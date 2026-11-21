# 4. Denied-Claims Work Queue (solution notes)
**Emphasis:** workflow/state machine, data modeling, concurrency (two people grabbing the same item)

## Answers to clarifying questions
- **Source:** denials arrive from the clearinghouse as remittance files/events (ERA/835) with a denial reason code.
- **Users:** ~20 billing specialists across a clinic group, plus managers who watch the backlog.
- **Scale:** ~5k open denials, ~300 new/day. Small data, so correctness matters more than scale.
- **Priority:** deadline to appeal (payers give N days), dollar amount, denial reason.
- **Actions:** claim a denial, add notes, request documents, correct and resubmit, appeal, write off (needs manager approval).
- **Automation:** some denials (e.g. a wrong patient ID) could be auto-fixed or AI-suggested, but a human approves resubmission.

## Reference design
```
Clearinghouse --> Ingest job --> denials table (status=NEW, priority computed)
                                      |
Specialist UI --> API --> "Get next" (claims highest priority unassigned) / list / update status
                              |
                         Postgres (single source of truth) + audit log
                              |
                     Resubmission worker --> Clearinghouse (async, retried)
Scheduler: deadline approaching & untouched --> alert manager / bump priority
```
**State machine:**
`NEW → ASSIGNED → IN_PROGRESS → (WAITING_ON_INFO) → RESUBMITTED | APPEALED → RESOLVED_PAID | RESOLVED_WRITTEN_OFF`. Only allowed transitions are accepted (enforced in the service layer).

## APIs
- `POST /denials/next` → atomically assigns the top item to the caller
- `GET /denials?status=&assignee=&sort=priority` (paginated)
- `GET /denials/{id}` (claim details, history, notes)
- `POST /denials/{id}/transitions {to: "RESUBMITTED", note, version}`
- `POST /denials/{id}/notes`

## Data
- `claims(id, clinic_id, patient_id, payer_id, amount, service_date, ...)`
- `denials(id, claim_id, reason_code, status, assignee_id NULL, priority, appeal_deadline, version, created_at)`
- `denial_events(id, denial_id, actor_id, from_status, to_status, note, created_at)` (history + audit)
- Indexes: `(status, priority DESC)` for "next", `(assignee_id, status)` for "my queue", `(appeal_deadline)` for the alert job.

## Concepts to mention (and why)
| Concept | Why |
|---|---|
| Explicit state machine | prevents illegal jumps (e.g. NEW → PAID), and makes reporting easy |
| Atomic claim | two specialists click "next" at once; both must not get the same denial |
| `SELECT ... FOR UPDATE SKIP LOCKED` **or** conditional update `UPDATE denials SET assignee=? WHERE id=? AND assignee IS NULL` (check rows affected) | DB-level guarantee, no app-level race |
| Optimistic locking (`version`) | two people editing the same denial; the second write fails with 409 and has to refresh |
| Transactions | the status change + event row are written together or not at all |
| Append-only event/audit table | money and PHI: who changed what, when (also gives you history for free) |
| Lease/timeout on assignment | a specialist goes on vacation, so unworked items return to the pool after N days |
| Idempotent resubmission | a retry after a timeout must not submit the claim twice to the payer |

## Failure modes / deep dives
1. **Race on "get next"** → walk through `SKIP LOCKED` or the conditional update. What does the loser get? (The next item.)
2. **Resubmission call times out** → mark `RESUBMISSION_PENDING`, retry with the same claim control number / idempotency key, and reconcile with the clearinghouse status later.
3. **Same denial ingested twice** → unique `(claim_id, remittance_id)`.
4. **Deadline missed** → scheduled job flags items N days out; manager dashboard.

## Follow-ups
1. Draw the states. What transitions are allowed?
2. Two specialists hit "next" at the exact same moment. What happens in your design?
3. How do you prioritize? (Deadline proximity × amount; keep the formula simple and tunable.)
4. Where could AI help, and where should a human stay in the loop?

## Rubric
- **Strong:** clear entities, state machine, atomic assignment at the DB level, audit history, deadline handling, simple stack (one relational DB is enough).
- **Red flags:** "check if unassigned, then assign" as two separate steps; no history; jumping to microservices/Kafka for 300 items/day.
