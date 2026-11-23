# Q7 Notes: Waitlist Backfill (Debug)

## Bugs, ranked by impact
| # | Bug | What happens | Fix |
|---|-----|--------------|-----|
| 1 | No `break` after assigning | The loop keeps going: one slot gets **overwritten** by later matches, and **several patients are removed** from the waitlist for one slot (they silently lose their place) | `break` after a match |
| 2 | `waitlist.remove(w)` **while iterating** over the same list | Python skips the element after the removed one, so some patients are never considered | Track an `assigned` set (or iterate over a copy) |
| 3 | `reverse=True` | The **newest** waitlist entry is served first, the opposite of fair | Sort ascending by `added_at` |
| 4 | `provider_id == slot["provider_id"]` | Patients who accept **any** provider (`None`) never match | `w["provider_id"] in (None, slot["provider_id"])` |
| 5 | Slots not sorted by start | Later slots can grab patients who should have gotten an earlier one | `sorted(open_slots, key=start)` |
| 6 | `earliest < start` | A patient available exactly at the slot start is skipped | `<=` |
| 7 | `.sort()` mutates the caller's list | A side effect: the caller's waitlist order changes, and `remove` deletes entries from the caller's data | `sorted()` copy |
| 8 | Unmatched slots missing from result | The caller gets a KeyError or can't tell "no match" from "not processed" | Initialize each slot to `None` |

## Tracing the buggy code on the test (what you'd say out loud)
- The sort puts W1 (added 5) first, so the newest patient is served first. ❌
- S2 is processed before S1 (input order).
- S2 (dr_a): W1 fails (None ≠ dr_a); W3 fails; W4 fails (earliest 650); W2 fails because `600 < 600` is false. → no assignment, and S2 isn't even in the result.
- S1 (dr_b): W3 matches → removed while iterating…

## What the interviewer is looking for
- **Trace before fixing.** Narrate the state as it changes.
- Spot the **mutation-while-iterating** bug. It's a classic Python trap.
- Notice the *fairness* impact (newest-first) and the *side effect* on the input. These are business and API-contract issues, not just code issues.

## Follow-ups
- "Complexity?" → O(S log S + W log W + S·W). Fine for one clinic's day. With a lot of data, index the waitlist by `(visit_type, provider)`.
- "Real system: two cancellations happen at once." → two workers could offer the same patient two slots; claim atomically in the DB.
- "The patient has to accept the offer by text." → offers become *pending* with a timeout, then move to the next patient (a state machine).
