# System Design Mocks (Flagler Health prep)

Short (15–25 min) backend design mocks, sized for an early-career engineer. They're grounded in Flagler's business areas (MSK clinics: call center, RCM, referrals, patient engagement, EMR integration, analytics), plus two general ones. Everything is synthetic. Nothing here assumes Flagler's real architecture.

## Files
- **`PROMPTS.md`**: the only thing you see before a mock. One short prompt per mock.
- **One folder per case** (e.g. `01-efax-referral-intake/`), containing:
  - `solution.md`: the interviewer's notes: answers to clarifying questions, a reference design, APIs/data, failure modes, follow-ups, and a rubric. **Open it only after you've tried the mock.**
  - `my-answers.md` (once attempted): what I said during the mock, with a summary at the top of what went well, what I missed, and what to focus on.
- **`CONCEPTS.md`**: a cheat sheet of the core ideas (queues, idempotency, transactions, and so on), with *why* you'd use each one. Fine to read anytime.

## Mock bank

| # | Mock | Main emphasis |
|---|------|---------------|
| 1 | eFax referral intake | async processing, human-in-the-loop |
| 2 | Appointment reminders | scheduling jobs, idempotency, opt-outs |
| 3 | Insurance eligibility checks | slow external API, timeouts, caching |
| 4 | Denied-claims work queue | workflow/state machine, concurrency |
| 5 | EMR appointment sync | integrations, duplicate/out-of-order webhooks |
| 6 | Post-visit check-ins and escalation | care-management workflow, AI as assistant |
| 7 | Clinic analytics dashboard | read vs. write load, pre-aggregation, multi-tenancy |
| 8 | General: notification service | API design, fan-out, scaling workers |
| 9 | General: webhook ingestion endpoint | traffic spikes, load balancing, backpressure |

Suggested order for Nov 24 prep: **1 → 4 → 5 → 2 → 3** (most Flagler-flavored). Do the rest if you have time.

## How to run one (about 20 min)
1. **Clarify (2–4 min):** users, actions, scale, constraints. Write down your assumptions.
2. **High-level design (5–7 min):** boxes and arrows from the client to the DB. Start with the simplest thing that works.
3. **APIs and data (3–5 min):** 3–5 endpoints and the main tables/columns.
4. **Deep dive (5–7 min):** pick one failure from the solution file (or ask Claude to play the interviewer).
5. **Wrap-up (1–2 min):** why it fits, and what you'd add next.

> Tip: say *why* before *what*. "We need a queue **because** the OCR step takes about 30s and the fax provider's webhook times out in 5s" beats "add Kafka."

You can also ask Claude: *"Run system design mock #4 with me."* It will play the interviewer and won't reveal the solution.
