# Coding Questions (Flagler-style practice)

Short backend coding exercises built around MSK clinic workflows. They're sized for the **25–35 minute coding slot** (Easy–Medium, usually 20–50 lines). The focus is practical business logic (grouping, rules, intervals, dedupe, state transitions), not LeetCode puzzles. All data is fictional and in memory.

> These are plausible practice problems, **not** Flagler's actual interview questions.

## Exercises

| # | Exercise | Type | Domain | Skills |
|---|----------|------|--------|--------|
| 1 | No-show fee calculator | Implement | Front desk / billing | business rules, grouping, caps, ties |
| 2 | PT visit authorization tracker | Implement | Prior auth / RCM | sorting, matching, picking the best option |
| 3 | Out-of-order EMR events | Implement | EMR integration | idempotency, versions, conflicting updates |
| 4 | Referral SLA report | Implement | Referrals / analytics | aggregation, missing data, ranking |
| 5 | Reminder retry planner | Implement | Patient engagement | state rules, backoff, quiet hours |
| 6 | Copay reconciliation | **Debug** | Billing | find and fix bugs in existing code |
| 7 | Waitlist backfill | **Debug** | Scheduling | find and fix bugs in existing code |

**Suggested order:** 3 → 1 → 6 → 4 → 7 → 2 → 5.

## Files in each folder
- `practice.py`: **start here.** It has the scenario, function signature, rules, examples, a `TODO` (or buggy code for the debug ones), and tests. Run it with `py practice.py`. The tests fail until your code is right.
- `solution.py`: reference solution. It runs the same tests: `py solution.py`. **Don't open it until you're done.**
- `notes.md`: interviewer notes: clarifying questions to ask, edge cases, complexity, follow-ups, and what a strong answer sounds like. **Open after.**

## How to practice (about 30 min)
1. **Read the scenario (2 min).** Restate it out loud in one sentence.
2. **Clarify (3 min).** List the edge cases you'd ask about *before* coding: ties, missing data, duplicates, unsorted input.
3. **Plan (3 min).** Say the approach and its complexity before typing.
4. **Code (12–15 min).** Talk while you code.
5. **Test (5 min).** Trace one example by hand, then run the tests.
6. **Discuss (2 min).** Complexity, what you'd change for production, follow-ups.

For the **debug** exercises: read the code first and explain what it's *supposed* to do. Then predict which tests fail *before* running them, and list the bugs ranked by severity.

You can also say *"Give me coding question #N in mock mode."* Claude will act as the interviewer and won't show the solution.
