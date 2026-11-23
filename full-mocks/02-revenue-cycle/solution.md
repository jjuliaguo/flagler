# Full Mock 2: Solution Notes (Revenue Cycle)
Code + tests: [solution.py](solution.py)

## Part A: Coding

### Clarifications a strong candidate asks
- Ties? **Break alphabetically** (deterministic output). Fewer than k distinct codes? Return all of them.
- Same claim denied twice for the same code: count once or twice? *(Base: twice. Follow-up: once.)*
- Part 2: can amounts be negative? **Yes** (take-backs). Can a run be one day? **Yes.** Amounts in cents (integers, no float rounding issues).

### Part 1: Top K (LC 347)
- **Count** with a dict/`Counter` → **sort** by `(-count, code)` → take k. O(n + u log u).
- Mention alternatives: a **heap** of size k gives O(n + u log k); **bucket sort** by count gives O(n). Either is fine to *mention*. Sorting is fine to *code* at this scale (a few hundred distinct codes).
- **Follow-up (dedupe):** count unique `(claim_id, reason_code)` pairs. That's a good catch for real billing data, where resubmitted claims get re-denied.
- **Domain extension:** top reasons **per payer** → group by payer, then count. The real business value is the "fix the root cause" conversation.

### Part 2: Matching runs (LC 560)
- **Brute force:** every (start, end) pair with a running sum: O(n²). Say it first.
- **Trap:** a sliding window does **not** work because the negative values break the "shrink when too big" logic. Strong candidates notice this.
- **Optimal:** **prefix sums + hash map.** If `prefix[j] - prefix[i] == target`, then days `i+1..j` match. Keep `count of each prefix seen so far`, starting with `{0: 1}` (the empty prefix). O(n) time and space.
- **Classic bugs:** forgetting `{0: 1}` (misses runs starting at day 0); updating the map *before* the lookup (counts empty runs when target = 0).
- **Follow-up:** earliest-ending run → store the *first* index per prefix and return on the first hit.

### Hint ladder
1. "What's the sum of days i..j in terms of running totals?"
2. "If the running total now is 500 and the target is 300, what running total do you need to have seen earlier?"
3. "What data structure answers 'have I seen this value, and how many times?' in O(1)?"

---

## Part B: System design (claim submission and status tracking)

### Clarifications (interviewer answers)
- **Volume:** ~10k claims/day across clinics.
- **Clearinghouse:** accepts claim batches via API/SFTP and returns **acknowledgments** (accepted/rejected for formatting) within hours, then **remittances (ERA/835)** days to weeks later with paid/denied and amounts. Responses can be **duplicated or late**.
- **Users:** billing team needs a work list ("rejected", "denied", "no response in 30 days") and totals.
- Claims are created from **completed, coded visits** in the EMR.

### Reference design
```
EMR (visit completed + coded) --> Claim builder (validate required fields: scrubbing)
      --> claims table (status=READY) --> Submission worker (batches, idempotent) --> Clearinghouse
Clearinghouse acks / ERA files --> Ingest worker (parse, dedupe, match to claim) --> update status + payments
Scheduler: "no response in N days" -> follow-up task
Billing UI <- API <- claims, claim_events, payments (Postgres)
```
**Claim states:** `DRAFT → READY → SUBMITTED → ACCEPTED | REJECTED → PAID | PARTIALLY_PAID | DENIED → (corrected) RESUBMITTED…`

### APIs
- `GET /claims?status=&payer=&older_than_days=` (work list, paginated)
- `GET /claims/{id}` (with full event history)
- `POST /claims/{id}/resubmit` (idempotency key) · `POST /claims/{id}/notes`
- Internal: `POST /ingest/clearinghouse-responses`

### Data
- `claims(id, clinic_id, visit_id UNIQUE, patient_id, payer_id, billed_amount, status, control_number UNIQUE, submitted_at, version)`
- `claim_events(id, claim_id, type, raw_ref, created_at)` (append-only history)
- `payments(id, claim_id, amount, era_id, posted_at)`, `UNIQUE(era_id, claim_id)`
- Index `(clinic_id, status, submitted_at)`.

### Concepts to mention (and why)
| Concept | Why |
|---|---|
| Validate before submit ("scrubbing") | rejections are slow and costly, so catch missing fields up front |
| State machine + event history | billing needs to know exactly where each claim is and why; also an audit trail |
| Unique claim control number / `visit_id` | one visit must never be billed twice (duplicate billing is a compliance problem) |
| Async workers + queue | the clearinghouse is slow and batch-based, so the user doesn't wait |
| Idempotent response ingestion | duplicate ERA files must not double-post payments (`UNIQUE(era_id, claim_id)`) |
| Matching + "unmatched" bucket | some responses won't match a claim cleanly, so a human reviews them |
| Timeouts / "no response in N days" | silence is a failure mode too; create follow-up tasks |
| Money in integer cents | no float rounding errors |
| Audit + access control | PHI and financial data |

### Deep dives
1. **The same ERA file arrives twice.** Unique constraint → the second insert is a no-op → the payment is posted once.
2. **Submission call times out.** Was it received? Resubmit with the same control number (the clearinghouse dedupes), or check status first.
3. **A remittance references an unknown claim.** Park it in `UNMATCHED` and alert billing. Don't drop it.

### Rubric
- **Strong:** clear entities and states, async submission, idempotent ingest, reconciliation for silence, money handled in cents, a work list for humans.
- **Red flags:** synchronous submit-and-wait; no dedupe of payments; overwriting status with no history.
