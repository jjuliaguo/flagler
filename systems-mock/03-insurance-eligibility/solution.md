# 3. Insurance Eligibility Checks (solution notes)
**Emphasis:** slow/unreliable external systems, timeouts, caching, background pre-fetch

## Answers to clarifying questions
- **Users:** front-desk staff. They need the result *before* check-in.
- **External:** payer APIs (or a clearinghouse). Latency is 2–30s, sometimes down for hours, with per-payer rate limits.
- **Scale:** ~20k appointments/day across clinics, plus ad-hoc checks for walk-ins.
- **Freshness:** coverage rarely changes day to day; a result from the last ~24–72h is usually fine. Re-check when insurance info is edited.
- **Output:** active/inactive, copay, deductible remaining, whether PT visits need prior auth, plus the raw response for audit.

## Reference design
```
Nightly/rolling job: appointments in next 2 days --> enqueue check(patient, insurance)
On-demand: staff clicks "Re-check" ------------------^
                                    |
                                 Queue --> Eligibility workers --(timeout, retries, per-payer rate limit)--> Clearinghouse/Payer
                                               |
                                               v
                                   eligibility_checks table (latest result + raw response)
                                               |
Front-desk UI <-- GET /appointments/{id}/eligibility (reads DB only, always fast)
```
- **Pre-fetch asynchronously** so staff never wait on the payer. The UI reads the stored result and shows *when* it was checked.
- On-demand re-check: `POST` returns `202 Accepted` + check id; the UI polls (or gets a push) for completion.

## APIs
- `GET /appointments/{id}/eligibility` → latest result + `checked_at` + status
- `POST /patients/{id}/eligibility-checks` → `202 {check_id}`
- `GET /eligibility-checks/{check_id}`

## Data
- `eligibility_checks(id, clinic_id, patient_id, insurance_policy_id, status[QUEUED|RUNNING|DONE|FAILED], result_json, raw_response_ref, checked_at, error)`
- Index `(patient_id, insurance_policy_id, checked_at DESC)`.

## Concepts to mention (and why)
| Concept | Why |
|---|---|
| Async + 202 pattern | don't hold an HTTP request open for 30s, and don't tie up web servers |
| Timeouts | without them a hung payer call blocks a worker forever |
| Retries with exponential backoff + jitter | handle transient failures without hammering a struggling payer |
| Per-payer rate limiting / concurrency caps | payers throttle or ban noisy clients |
| Circuit breaker (simple version) | if payer X fails repeatedly, pause calls to it for a few minutes and show "payer unavailable" |
| Caching = the stored result with a TTL | avoid duplicate checks for the same patient within 24h; it's just a DB lookup, no Redis needed |
| Dedupe in-flight checks | 3 staff click re-check, so only 1 payer call happens |
| Stale-but-labeled data | showing "Active (checked 2 days ago)" is better than a spinner during an outage |

## Failure modes / deep dives
1. **Payer down for 4 hours** → retries back off, the circuit opens, the UI shows the last known result + a warning, and the check auto-retries when the payer recovers. Staff can fall back to a phone call.
2. **Response is ambiguous/partial** → mark `NEEDS_REVIEW`; don't guess coverage.
3. **Insurance edited after the check** → invalidate (new policy id) and enqueue a new check.

## Follow-ups
1. Why not just call the payer when the staff opens the page?
2. What timeout would you set and what happens when it's hit?
3. A payer starts returning 429s. What do you do?
4. Do you need Redis here? (Probably not. The DB row is the cache. Add it only if reads become a bottleneck.)

## Rubric
- **Strong:** pre-fetch + async, timeouts/retries/backoff, rate limiting, shows staleness, dedupe, raw-response audit.
- **Red flags:** synchronous call in the request path with no timeout; adding a cache without explaining what is cached or for how long.
