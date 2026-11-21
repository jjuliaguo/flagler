# Answer Key (SPOILERS: open this only after you've tried each exercise)

Each exercise has interviewer questions in order. Try answering out loud first, then check.

---

## Exercise 1: `summarize_labs` (healthcare / dicts / state)

**Q1. Explain:** What does this function take in and return? Walk me through the loop.
- Input: a list of lab result dicts. Output: `{patient_id: {"latest", "abnormal", "totals", "averages"}}`.
- For each result: normalize the test name, parse the timestamp, create the patient bucket if needed, keep the most recent `(value, taken_at)` per test, flag the test if it's out of range, and add to a running total. A second pass computes averages.

**Q2. Trace:** What does this return?
```python
summarize_labs([
    {"patient_id": "P1", "test": "glucose",   "value": 110, "taken_at": "2026-11-01T08:00:00"},
    {"patient_id": "P1", "test": "glucose",   "value": 90,  "taken_at": "2026-11-02T08:00:00"},
    {"patient_id": "P2", "test": "Potassium", "value": 5.0, "taken_at": "2026-11-01T09:00:00"},
])
```
- P1 latest glucose = `(90, 11-02)`. 110 > 99, so `"glucose"` gets appended to `abnormal`.
- P2 potassium 5.0 is **not** > 5.0, so it's normal (the range check is inclusive).
- **P2's `abnormal` is `["glucose"]`** even though P2 never had a glucose test. Every patient's `"abnormal"` points to the *same* `flagged` list object.
- P1 average glucose = 200 / **1** = **200.0** (expected 100). P2 average = 5.0.

**Q3. Debug:** What's wrong?
1. **Mutable default argument `flagged=[]`.** The default list is created once, so it's shared (a) across all patients in one call and (b) across *every call* of the function. Abnormal flags leak between patients, which is a patient-safety bug. Fix: `"abnormal": []`.
2. **Wrong average denominator.** `count = len(patient["latest"])` is the number of *distinct tests*, not the number of readings for that test. Track a per-test count.
3. **`REFERENCE_RANGES[test]` raises KeyError** for an unknown test (e.g. "sodium"), which crashes the whole batch. Use `.get()` and skip or log.
4. **Abnormal is historical, not current,** and it can contain duplicates: two high readings means `["glucose", "glucose"]`, and a test stays flagged even after the latest reading is normal. Decide which one you want (a set, or check only the latest value).
5. Edge cases: `value` is None or a string (TypeError on `<`); a malformed `taken_at`; mixing timezone-aware and naive timestamps (TypeError on `>`); an equal timestamp keeps the first reading.

**Q4. Evaluate:** Complexity and improvements.
- O(n) time, O(p · t) space. Fine.
- Improvements: no mutable default; per-test `count`; validate input/skip bad rows with logging instead of crashing; maybe a dataclass instead of nested dicts; units (glucose in mg/dL vs mmol/L would silently mis-flag).

---

## Exercise 2: `process_claims` (backend reliability / retries / idempotency)

**Q1. Explain:** What is this supposed to guarantee? Walk me through one claim.
- Intent: submit each claim once, retry transient failures with exponential backoff, and skip anything already processed.

**Q2. Trace:** A claim `C1` times out on all 3 attempts. What happens? Then we call `process_claims([C1])` again. What happens?
- Attempt 1 fails, sleep 2s. Attempt 2 fails, sleep 4s. Attempt 3 fails, sleep 8s. That's about 14s total, and the last 8s sleep is wasted because nothing runs after it.
- The loop exits and C1 is **not** in `results`, with no error and no log.
- C1 **is** in `processed_ids` (it was added *before* the call succeeded), so the second call **skips it forever**. The claim is silently lost, which means lost revenue.

**Q3. Debug:** What else could go wrong?
1. **Marked processed before success.** Move `processed_ids.add` after a successful response.
2. **Infinite loop on a non-transient error.** The `except Exception` branch doesn't `break` or increment `attempt`, so a deterministic error (e.g. a bad payload) loops and prints forever.
3. **`claim["id"]` outside the try** raises KeyError on a malformed claim, which crashes the whole batch.
4. **Failures are invisible.** Callers can't tell failed claims from successful ones. Return failures as well, or push them to a dead-letter queue.
5. **Timeout does not mean "didn't happen."** The payer may have accepted the claim and the response timed out, so a retry can **double-submit**. You need an idempotency key sent to the payer (e.g. the claim id).
6. **The in-memory global set** is lost on restart and isn't shared across workers/processes. Two workers can both pass the `in` check and both submit (check-then-act race). Fix: a DB unique constraint, or an atomic "claim/lock" row with a status (`pending → submitted → accepted/failed`).
7. Backoff has no jitter, so many clients retry in sync (thundering herd). `time.sleep` blocks the whole batch; a slow claim delays the others.

**Q4. Reason:** Why exponential backoff? Why might someone have put `add` before the call?
- Backoff gives a struggling dependency time to recover. Adding first was probably meant to prevent concurrent duplicates ("reserve" the id), but without a status or rollback on failure it causes loss instead. The right pattern is a status field that is set to `failed` / re-queued on failure.

---

## Exercise 3: `findConflicts` (TypeScript / dates / algorithm)

**Q1. Explain:** Walk me through the algorithm.
- Group by provider, sort each group by start time, and compare each appointment with the next one. If the current one ends after the next starts, record the pair.

**Q2. Trace:** Provider X has A at 9:00 for 60 min and B at 9:30 for 30 min. Output?
- `curEnd = 9:00 + 60*60` **milliseconds** = 9:00:03.6. That isn't > 9:30, so it returns **`[]`**. Expected `[["A","B"]]`.

**Q3. Debug:**
1. **Unit bug:** `getTime()` is in ms, so you need `durationMin * 60 * 1000`. As written, almost no conflicts are ever detected.
2. **Only adjacent pairs are compared.** A at 9:00 for 120 min, B at 9:30 for 15 min, C at 10:00 for 30 min: A–C overlap is missed even after the unit fix. Track a running `maxEnd` (and the id of the appointment that owns it), or compare against all active appointments.
3. Boundary: `>` correctly treats back-to-back (10:00 end, 10:00 start) as no conflict. Ask whether buffer time is needed.
4. `.sort` mutates the grouped array in place (harmless here, but it's a habit to watch). The comparator never returns 0, so equal starts aren't handled cleanly; `a.start.getTime() - b.start.getTime()` is cleaner.
5. Edge cases: an invalid Date (`NaN` comparisons are always false, so conflicts are silently missed), timezones/DST if `start` came from strings, and a negative or 0 duration.

**Q4. Complexity:** O(n log n) because of the sort. The "compare against all" fix is O(n²) worst case. A sweep with `maxEnd` keeps it O(n log n) for detecting conflicts, though listing *all* overlapping pairs can be O(n²) output.

---

## Self-grading rubric
- **Accuracy:** Did your trace match exactly (e.g. 200.0, `[]`, the P2 glucose leak)?
- **Prioritization:** Did you lead with the most severe bug (data leakage, lost claims, missed conflicts) before nits?
- **Communication:** Did you state assumptions, think out loud, and propose concrete fixes?
- **Healthcare awareness:** Patient-safety and billing impact, PHI in logs (`print` of claim data), auditability.
