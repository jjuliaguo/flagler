# Q1 Notes: No-Show Fee Calculator

## Clarifying questions a strong candidate asks
- Is the input sorted? *(No.)* Can the same appointment appear twice? *(Yes, with conflicting types.)*
- Waiver tie on the same date: which one is waived? *(The more expensive.)*
- Does the cap apply before or after the waiver? *(The waiver comes first and doesn't count toward the cap.)*
- Unknown `type` values? *(Not in the base problem. Good to mention you'd skip them and log.)*
- Money: whole dollars here. In real code, use integer cents.

## Approach
1. **Dedupe by `appt_id`**, keeping the max fee: O(n) with a dict.
2. **Sort** by `(patient, date, -fee)`, which groups each patient's appointments chronologically and puts the bigger fee first on a tie.
3. **One pass** with state: a set of `(patient, year)` already waived, and a dict of `(patient, month) → charged`.
4. Charge `min(fee, cap - charged_this_month)`.

**Complexity:** O(n log n) time (the sort), O(n) space.

## Common mistakes
- Applying rules in the wrong order (cap before dedupe, or waiver after cap).
- Waiving once *ever* instead of once per **year**.
- Comparing dates as strings is fine for `YYYY-MM-DD` (it sorts correctly). Say that out loud. With other formats you'd parse them.
- Forgetting the tie rule, so the waiver lands on the cheaper fee.
- Including patients who owe 0.

## Follow-ups
- "Return an itemized bill per patient." → keep a list of `(appt_id, charged, reason)`.
- "Policy differs per clinic." → pass a `policy` dict (fees, cap, waiver count) instead of constants.
- "Events stream in daily." → persist the waiver/cap state per patient instead of recomputing.
- "A patient disputes a charge." → itemization + an audit log of which rule applied.

## Strong answer sounds like
"I'll first collapse duplicates per appointment, since the EMR can send conflicting updates. Then I'll sort each patient's history so the rules that depend on order (first of the year, monthly cap) are simple to apply in one pass…"
