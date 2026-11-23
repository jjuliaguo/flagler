# Full Mock 2: Revenue Cycle (Claims and Denials)

## Part A: Live coding (~30 min)

### Part 1: Top denial reasons
Insurers send back denials with a **reason code** (e.g. `CO-16` = missing information, `CO-97` = bundled service). The billing manager wants to know which reasons come up most, so the team can fix the root cause.

```python
def top_denial_reasons(denials: list[dict], k: int) -> list[str]:
    """
    denials: [{"claim_id": "C1", "payer": "Aetna", "reason_code": "CO-16"}, ...]
    Return the k most frequent reason codes, most frequent first.
    """
```
**Example**
```
codes in denials: CO-16 x3, CO-97 x2, PR-1 x2, CO-50 x1
k = 2  ->  ["CO-16", "CO-97"]
```

### Part 2: Match a deposit to a run of days
The clinic's bank shows a lump-sum insurance deposit, and billing needs to figure out which payment days it covers. You have the **net amount posted per day** (in cents). Payments are positive. Adjustments and take-backs are **negative**.

Count how many **contiguous runs of days** add up to exactly the deposit amount.
```python
def count_matching_periods(daily_net: list[int], target: int) -> int:
    ...
```
**Example**
```
daily_net = [100, 200, -100, 300, 100], target = 300
Output: 3     # days [0..1], [3..3], [2..4]
```

### Follow-up (if time)
Return the `(start_day, end_day)` of the matching run that **ends earliest**, or `None`.

---

## Part B: System design (~20–25 min)

> After each visit, the clinic needs to bill the patient's insurance. Design a system that takes completed visits, **submits claims** to insurers through a clearinghouse, and **tracks each claim's status** (accepted, rejected, paid, denied) until it's resolved. The billing team needs to see where every claim is and which ones need attention.
