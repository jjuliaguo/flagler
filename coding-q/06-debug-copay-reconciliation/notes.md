# Q6 Notes: Copay Reconciliation (Debug)

## Bugs, ranked by production impact
| # | Bug | What happens | Fix |
|---|-----|--------------|-----|
| 1 | `p["visit_id"] not in visits`: `visits` is a **list of dicts**, so a string is never "in" it | **Every** payment is reported as unmatched | Build `due = {visit_id: ...}` and check membership against that |
| 2 | `paid[...] = amount` **overwrites** | A visit with 2 payments only counts the last one, so patients get billed again for money they already paid | `+=` (with `defaultdict(int)`) |
| 3 | No `continue` after unmatched | An unknown visit's payment still lands in `paid` | `continue` |
| 4 | No dedupe on `payment_id` | A duplicate webhook double-counts the payment, so the patient looks paid when they aren't | `seen_payments` set |
| 5 | `paid[v["visit_id"]]` → **KeyError** for a visit with no payments | Crashes the whole end-of-day report | `defaultdict(int)` or `.get(id, 0)` |
| 6 | Floats for money: `30.30 - (10.10 + 20.20)` = `3.5e-15`, not 0 | A visit shows a tiny balance and isn't treated as paid | Integer cents (or `Decimal`) |
| 7 | Negative balance not clamped | An overpaid visit shows "owes −5.00" | `max(owed, 0)`, and report the overpayment separately |

## What the interviewer is looking for
- **Read before running:** explain the intent, then *predict* the failures (bug 1 is visible by reading alone).
- **Prioritize:** wrong money and crashes come before cosmetic issues.
- **Explain the float issue simply:** "Binary floats can't represent 0.10 exactly, so sums drift. Money should be integer cents."
- **Healthcare/billing awareness:** double-billing patients and losing payment records are compliance and trust problems.

## Follow-ups
- "Where should an overpayment go?" → refund workflow or credit balance; never silently drop it.
- "Payments arrive throughout the day from a card terminal webhook." → idempotency key = `payment_id`, a unique constraint in the DB.
- "Complexity?" → O(V + P).
