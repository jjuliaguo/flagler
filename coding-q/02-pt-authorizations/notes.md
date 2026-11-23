# Q2 Notes: PT Visit Authorization Tracker

## Clarifying questions a strong candidate asks
- Are start/end inclusive? *(Yes.)* Are visits sorted? *(No.)*
- Several auths cover a visit: which one? *(Ends soonest, then auth_id.)* Ask **why**: so the soon-to-expire one gets used before it's wasted.
- Can auths for the same patient overlap? *(Yes. That's the interesting case.)*
- A visit for a patient with no auths at all? *(Uncovered.)*

## Approach
1. `remaining = {auth_id: visits_allowed}`.
2. Group auths by patient, **pre-sorted by `(end, auth_id)`**. Then the first auth that qualifies is automatically the best choice.
3. Sort visits by `(date, visit_id)`. For each visit, scan that patient's auths and take the first one that covers the date and has visits remaining. Otherwise mark it uncovered.

**Complexity:** O(A log A + V log V + V·k), where k = auths per patient (small, usually 1–3).

## Common mistakes
- Processing visits in input order instead of date order (the greedy choice depends on order).
- Picking the *first auth in the input* instead of the one ending soonest.
- `<` instead of `<=` on the end date.
- Returning `remaining` only for auths that were used (the spec says every auth).
- Python's `for … else` is handy here; a `found` flag is fine too. Explain whichever you use.

## Follow-ups
- "Warn billing when an auth has ≤ 1 visit left or ends within 7 days." → a pass over `remaining` + end dates. This is the real business value: renew auths *before* visits go uncovered.
- "A visit gets canceled after being applied." → you need to know *which* auth each visit used (return a `visit → auth` mapping) so you can give the visit back.
- "Thousands of auths per patient?" → sort and binary search by date, or a heap of active auths.

## Strong answer sounds like
"Visits are applied greedily in date order, and when there's a choice I use the auth that expires first, so we don't waste visits that are about to expire. Pre-sorting each patient's auths by end date means the first match is the right one."
