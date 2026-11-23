# Full Mock 3: Solution Notes (AI Call Center)
Code + tests: [solution.py](solution.py)

## Part A: Coding

### Clarifications a strong candidate asks
- Is the window inclusive? **Yes:** `[ts - 60, ts]`. Can two calls share a timestamp? **Yes.**
- Are timestamps always increasing? **Non-decreasing** for Part 1. (Out-of-order is a great follow-up to raise yourself.)
- Part 2: can calls appear back-to-back in one log? **Yes.** Can holds nest inside transfers? **Yes, as long as they nest properly.** Unknown/point events are allowed only inside a call.

### Part 1: Recent calls (LC 933)
- **Brute force:** keep a list of all calls and count the ones in the window each time. O(n) per call, and memory grows forever.
- **Optimal:** a **queue (deque)**. Append the new call, then pop from the front while it's older than `ts - 60`. Each call is added and removed once, so it's **amortized O(1)**, and memory is bounded by the window size.
- **Classic bugs:** using `list.pop(0)` (O(n)); `<` vs `<=` at the window edge.
- **Follow-ups:**
  - **Per clinic:** a dict of `clinic_id → deque`.
  - **Out-of-order timestamps:** a sorted structure + bisect, or buckets per second.
  - **Huge volume:** count per-second buckets in a fixed ring of 60 slots, O(1) memory.
  - **Multiple servers:** in-memory state doesn't work, so use a shared store (e.g. Redis sorted set / counters).

### Part 2: Event nesting (LC 20)
- A **stack**: push on `*_START`, and on `*_END` check that the top of the stack is the matching start, then pop. At the end, the stack must be empty.
- Extra rules on top of plain parentheses: no `CALL_START` while the stack is non-empty; any other start or point event requires a non-empty stack.
- **Complexity:** O(n) time, O(n) space.
- **Classic bugs:** forgetting the final "stack not empty" check (returns valid for an unclosed hold); popping an empty stack.

### Hint ladder
1. Part 1: "Once a call is older than 60 seconds, will it ever count again?"
2. Part 2: "When you see `HOLD_END`, which start event must it match?" → "What data structure gives you the most recent unmatched item?"

---

## Part B: System design (AI phone agent with human handoff)

### Clarifications (interviewer answers)
- **Scale:** 100 clinics, ~10k calls/day, peaking Monday mornings. Typical concurrency is ~50–200 calls.
- **Telephony:** a provider like Twilio handles the phone network and calls our webhooks; we stream audio to speech-to-text / text-to-speech / an LLM.
- **Actions:** look up the patient, find slots, book/reschedule/cancel **in the EMR**.
- **Handoff:** to a clinic staff phone queue during business hours; otherwise voicemail/callback task.
- **Constraints:** latency (the patient is waiting on the line), PHI, verify the caller's identity before discussing appointments.

### Reference design
```
Patient phone --> Telephony provider --webhook/media stream--> Call Orchestrator (stateless workers)
                                                                |  conversation state machine:
                                                                |  GREET -> VERIFY_IDENTITY -> INTENT -> (SCHEDULE | RESCHEDULE | CANCEL | FAQ) -> CONFIRM -> END
                                                                |                                         \-> HANDOFF
                                         STT / LLM / TTS  <-----+
                                         Tools layer ----------> Scheduling service --> EMR
                                         Call state store (Redis/DB, keyed by call_id)
                                         Transcripts + action log (DB / object storage)
Handoff --> warm transfer to clinic queue + summary on staff screen, OR create callback task
```
- **The LLM handles the language. Deterministic code handles the actions.** The LLM chooses an intent and fills slots, but **booking happens through validated tool calls** (e.g. `book(slot_id, patient_id)`) that check permissions and availability. The LLM never writes to the EMR directly.
- **The state machine** limits what can happen at each step. For example, nothing about appointments is discussed before identity is verified.

### APIs
- `POST /telephony/calls/incoming` · `POST /telephony/calls/{id}/events` (webhooks)
- `POST /calls/{id}/handoff` · `GET /clinics/{id}/calls?date=` (staff view: transcript, outcome)
- Internal tools: `GET /patients/search`, `GET /availability`, `POST /appointments` (idempotency key = call_id + action)

### Data
- `calls(id, clinic_id, from_number, patient_id NULL, state, outcome, started_at, ended_at)`
- `call_events(call_id, seq, type, payload, ts)` (the Part 2 event log)
- `transcripts(call_id, storage_ref)`, `actions(call_id, type, appointment_id, status)`
- `handoffs(call_id, reason, summary, assigned_to, status)`

### Concepts to mention (and why)
| Concept | Why |
|---|---|
| Explicit state machine | predictable, testable flow; enforces "verify before disclose" |
| LLM proposes, code executes (tool calls with validation) | prevents hallucinated bookings, wrong-patient actions |
| Confidence / escalation rules → handoff | AI isn't authoritative; frustrated patients, clinical questions, and repeated misunderstandings go to a human |
| External call state store | any worker can handle the next webhook for a call; survives a worker crash |
| Idempotent booking | webhook retries or LLM retries must not book twice |
| Timeouts + fallbacks | the EMR or LLM is slow, so say "one moment" or offer a callback; never leave dead air or hang up |
| Audit log + transcripts | the clinic can see exactly what the AI did; compliance |
| PHI handling | identity verification, encryption, retention policy, minimal data sent to third-party models |
| Monitoring | containment rate, handoff rate, booking errors, latency per turn |

### Deep dives
1. **EMR is down mid-call.** Don't pretend to book. Tell the patient someone will call back, create a callback task with the details, and alert.
2. **Webhook retried / duplicate event.** Dedupe on `(call_id, seq)`; booking uses an idempotency key.
3. **Caller asks a clinical question ("Is this swelling normal?").** That's an immediate handoff or a nurse callback, plus emergency guidance. The AI does not answer it.

### Rubric
- **Strong:** a state machine, tool layer with validation, a clear handoff path with context, idempotency, failure fallbacks, PHI/identity awareness. Can tie it to their own voice-agent project.
- **Red flags:** the LLM directly modifies records; no handoff; call state kept in a single server's memory.
