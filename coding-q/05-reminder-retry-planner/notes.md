# Q5 Notes: Reminder Retry Planner

## Clarifying questions a strong candidate asks
- Is time in the patient's local time zone? *(Assume yes here. In real life, store UTC and convert per patient.)*
- Is 08:00 itself quiet? *(No: quiet is 21:00–07:59.)*
- Should "too late" be checked before or after the quiet-hours shift? *(After. The shift can push a send past the cutoff, as in R9.)*
- What if `next_time` is long past (the scheduler was down)? *(Still SEND now. Mention you might skip a reminder that's stale.)*

## Approach
- Split it into small functions: `next_allowed_time(t)` (quiet hours) and `plan_one(reminder, now)` (rules in order). Clean decomposition is part of the score.
- Constants for the policy (`MAX_ATTEMPTS`, `BACKOFF`, quiet hours) instead of magic numbers.
- Apply the rules in the given order; **early returns** keep it readable.

**Complexity:** O(n), O(1) per reminder.

## Common mistakes
- Checking "too late" before shifting for quiet hours.
- Off-by-one on the backoff index (`BACKOFF[len(attempts) - 1]`).
- Hour 21 not treated as quiet (`>` vs `>=`).
- Moving an after-midnight time to *tomorrow* 08:00 instead of *today* 08:00.

## Follow-ups
- "Two scheduler instances run at once. How do you avoid double-sending?" → claim the reminder atomically (`UPDATE ... SET status='SENDING' WHERE id=? AND status='PENDING'`), plus an idempotency key to the SMS provider.
- "Fall back to a phone call after the 2nd failed SMS." → add channel to the plan; a small state machine.
- "Time zones and DST." → store UTC, compute quiet hours in the patient's zone with `zoneinfo`.
- "Add jitter." → spread sends so 10k reminders don't hit the SMS provider at exactly 08:00.

## Strong answer sounds like
"I'll keep the policy as constants and write a helper for quiet hours, so each rule is one readable line. One subtlety: the too-late check has to happen after the quiet-hours shift, because pushing to 8am can move the send past the appointment."
