# Full 60-Minute Mocks (live coding + system design)

Five full interview simulations. Each one has a **live coding** section built from a LeetCode pattern, reworded as a Flagler-style problem (MSK clinics: scheduling, RCM/claims, AI call center, referrals, patient engagement). The coding is followed by a **system design** discussion from the same area of the business.

> The real split between coding and design is unknown. These mocks assume about 30 minutes for coding and 20–25 for design. If the real one differs, adjust.

## Mocks

| # | Theme | Coding Part 1 | Coding Part 2 | System design |
|---|-------|---------------|---------------|---------------|
| 1 | Provider scheduling | Merge busy blocks *(LC 56)* | Insert a block + find open slots *(LC 57)* | Patient self-scheduling without double-booking |
| 2 | Revenue cycle (RCM) | Top K denial reasons *(LC 347)* | Match a deposit to a run of daily payments *(LC 560)* | Claim submission and status tracking pipeline |
| 3 | AI call center | Calls in the last 60s *(LC 933)* | Validate call event nesting *(LC 20)* | AI phone scheduling agent with human handoff |
| 4 | Referrals and patient identity | Group possible duplicate patients *(LC 49)* | Flag re-sent faxes within a window *(LC 219)* | Patient matching / duplicate-record service |
| 5 | Patient engagement | Conversation state store with TTL *(LC 706)* | Longest varied exercise streak *(LC 3)* | Two-way SMS assistant backend |

All 10 LeetCode problems from your list are covered. **Suggested order before Tuesday: 1 → 3 → 2 → 4 → 5.** Mock 1 is the most likely style for a scheduling-heavy company, and mock 3 lines up with your voice-agent project.

## Files in each mock folder
- `prompt.md`: **candidate-facing**. The coding problems, with signatures and examples, plus the design prompt. No hints.
- `solution.py`: reference Python solutions with tests. Run `py solution.py` (on Windows; `python solution.py` elsewhere). Open it only after you try.
- `solution.md`: interviewer notes: clarifications, hint ladder, complexity, edge cases, follow-ups, design reference (concepts + *why*), and a rubric.
- `my-answers.md`: added after you do the mock. It covers what you said, what went well, and what you missed.

## 60-minute run sheet
| Time | Section | What to do |
|------|---------|-----------|
| 0–3 | Intro | 30-second intro. Mention the voice agent / denied-claims project. |
| 3–8 | Coding: clarify | Restate the problem and ask about edge cases (empty input, ties, sorted or not?). Write 1–2 examples. |
| 8–30 | Coding: solve | Say the brute force first, then the better approach. Code it while talking. Trace an example by hand. State the time and space complexity. |
| 30–33 | Coding: follow-up | Handle the follow-up the interviewer gives you. |
| 33–55 | System design | Clarify → high-level design → APIs/data → deep dive → tradeoffs. |
| 55–60 | Your questions | Ask them something real (see below). |

## Coding habits that score points
1. **Restate the problem in your own words** and confirm the input/output format.
2. **Ask about edge cases out loud:** empty input, duplicates, ties, unsorted input, invalid data.
3. **Say the brute force and its complexity**, then improve it.
4. **Talk while you code.** Silence makes it hard for the interviewer to follow you.
5. **Test by hand** with your example *and* an edge case before saying "done."
6. **Connect it to the domain:** "In a real system I'd also handle time zones, or log the invalid record instead of crashing."

## Questions to ask them at the end
- "How does the team balance AI automation with human review for things like referrals or claims?"
- "What does a forward-deployed engineer's week look like? How much is customer-facing vs. building?"
- "What's the hardest part of integrating with clinics' EMRs?"

You can also say *"Run full mock #N."* Claude will act as the interviewer for the whole hour without showing the solutions.
