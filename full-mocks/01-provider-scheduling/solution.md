# Full Mock 1: Solution Notes (Provider Scheduling)
Code + tests: [solution.py](solution.py)

## Part A: Coding

### Clarifications a strong candidate asks
- Do touching blocks (`9:00–10:00` and `10:00–11:00`) merge? **Yes.** It's one continuous busy stretch.
- Is the input sorted? **No** (Part 1). **Yes, and already merged** (Part 2).
- Can a block sit entirely inside another? **Yes.**
- Empty input? Return `[]`. Can I mutate the input? Better not.

### Part 1: Merge (LC 56)
- **Brute force:** compare every pair until nothing changes. O(n²) or worse.
- **Optimal:** **sort by start**, then walk once. If the next block starts at or before the last merged end, extend the end with `max(...)`. Otherwise start a new block.
- **Complexity:** O(n log n) time (the sort), O(n) space.
- **Classic bugs:** forgetting `max()` (a contained block shrinks the end); `<` vs `<=` for touching blocks; not sorting.

### Part 2: Insert (LC 57)
- The input is sorted, so **don't re-sort.** One pass in 3 phases: add blocks ending before `new` → absorb overlapping blocks (widen start/end) → add the rest. **O(n).**
- Simple acceptable answer: append + call `merge_busy_blocks`, O(n log n). Ask: "Can we do better since it's already sorted?"

### Stretch: open slots
- Walk the merged schedule with a `cursor` starting at opening time. Each gap `block.start - cursor ≥ duration` is a slot. Clip blocks to clinic hours. Remember the gap at the end of the day.

### Hint ladder (if stuck)
1. "What if the blocks were sorted?"
2. "After sorting, when can block *i* overlap something other than the last merged block?" (It can't.)
3. "What should happen to the end time when one block is inside another?"

### Follow-ups
- Multiple providers? → Group by provider, then merge each one.
- Time zones / DST? → Store UTC, convert to the clinic's local time for display.
- A 1M-block calendar? → Still sort + one pass. Or keep it sorted on insert (bisect).

---

## Part B: System design (patient self-scheduling, no double-booking)

### Clarifications (interviewer answers)
- **Scale:** 100 clinics, ~5k self-bookings/day. Spikes when reminder texts go out.
- **Source of truth:** the EMR. Staff book in the EMR at the same time. The EMR API is slow (1–3s) and rate-limited.
- **Visit types** have durations and specific eligible providers (e.g. a new-patient eval takes 60 min, PTs only).
- A brief "this slot is held while you confirm" is fine. Patients may abandon.

### Reference design
```
Patient (SMS link web page / AI phone agent)
   -> Scheduling API (stateless, behind load balancer)
        GET availability  -> read local availability cache (synced from EMR) -> compute open slots (Part A code!)
        POST hold         -> create short-lived hold row (DB unique constraint prevents 2 holds on same slot)
        POST confirm      -> book in EMR (source of truth) -> on success: appointment CONFIRMED; on conflict: release + offer new times
   <- EMR webhooks / periodic sync keep local schedule fresh
Hold expiry job: release holds older than ~5 min
```

### APIs
- `GET /clinics/{id}/availability?visit_type=&provider_id=&from=&to=`
- `POST /holds {provider_id, start, end, patient_id}` → `201 {hold_id, expires_at}` or `409`
- `POST /holds/{id}/confirm` (idempotency key) → `200 {appointment_id}` or `409 slot taken`
- `DELETE /holds/{id}`

### Data
- `provider_schedule(provider_id, start, end, source[emr|hold|block], synced_at)`
- `holds(id, provider_id, start, end, patient_id, status[HELD|CONFIRMED|EXPIRED], expires_at)`, with a uniqueness rule so two active holds can't overlap (a simple version: a unique `(provider_id, start)` for fixed-size slots, or check-and-insert inside a transaction with a row lock on the provider)
- `appointments(id, emr_id, provider_id, patient_id, start, end, status)`

### Concepts to mention (and why)
| Concept | Why |
|---|---|
| Local copy of availability | the EMR is slow and rate-limited, so we can't hit it on every page view |
| Holds with expiry | prevents two patients picking the same slot during the 30s they spend confirming |
| DB constraint / transaction for holds | "check free, then insert" in two steps is a race; let the DB enforce it |
| Final check at the EMR | staff may have booked the slot in the EMR a second ago. The EMR is the truth, so handle the conflict nicely |
| Idempotency key on confirm | a patient double-taps, or the AI agent retries, so we must not book twice |
| Sync via webhooks + periodic reconcile | keeps the local copy fresh and catches missed events |
| Stateless API + LB | handles reminder-blast spikes |

### Deep dives
1. **Two patients, same slot, same second.** Only one hold insert succeeds (constraint). The other gets 409 → show the next options.
2. **EMR booking call times out.** Did it book? Retry with the same idempotency key, or look up the appointment in the EMR before retrying. Never blind-retry.
3. **Local cache is stale.** Availability might show a slot that's gone. That's OK because the confirm step catches it. Keep the sync lag small and monitor it.

### Rubric
- **Strong:** clarifies durations and the source of truth, separates read (availability) from write (booking), handles the race at the DB level, a final EMR check, idempotency, hold expiry.
- **Red flags:** query the EMR on every page load with no plan for its slowness; "check then insert" with no lock or constraint; ignoring staff booking in parallel.
