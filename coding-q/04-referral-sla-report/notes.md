# Q4 Notes: Referral SLA Report

## Clarifying questions a strong candidate asks
- Is exactly 48h a breach? *(No: strictly greater.)*
- Should the average include unscheduled referrals? *(No, only scheduled ones. Otherwise the metric changes every hour.)*
- What about bad data (scheduled before received)? *(Skip it. In real life, log it or count it.)*
- Is `avg_hours` None or 0 when nothing is scheduled? *(None: 0 would look like great performance.)*
- Sort order on ties? *(Clinic name A–Z.)*

## Approach
- **One pass** grouping by clinic into running totals: `total`, `scheduled`, `hours_sum`, `breaches`. Store the **sum and count, not a running average.** You compute the average at the end.
- Breach check: `wait = scheduled - received` if scheduled, else `now - received`; breach if `> sla`.
- Build rows, then sort by `(-breaches, clinic)`.

**Complexity:** O(n + c log c), where c = clinics.

## Common mistakes
- Dividing by `total` instead of `scheduled` (or dividing by zero).
- Counting invalid rows in `total`.
- Using `>=` for the SLA.
- Sorting with `reverse=True` on a tuple: that reverses the name tiebreak too. Negate the number instead.

## Follow-ups
- "Report the median instead of the average." → keep a list of waits per clinic; the median is robust to one referral that took 30 days.
- "Exclude weekends from the SLA clock." → business-hours calculation; ask how holidays work.
- "This is a dashboard over millions of referrals." → do the aggregation in SQL (`GROUP BY clinic`) or pre-aggregate daily (see system design mock #7).
- "Which referrals should staff work on first?" → list unscheduled referrals sorted by hours waiting, descending.

## Strong answer sounds like
"I'll group in one pass, keeping sums and counts rather than averages so the math stays correct. A clinic with no scheduled referrals gets None, not 0, because 0 would look like perfect performance."
