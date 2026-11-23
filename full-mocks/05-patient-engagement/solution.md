# Full Mock 5: Solution Notes (Patient Engagement)
Code + tests: [solution.py](solution.py)

## Part A: Coding

### Clarifications a strong candidate asks
- Does `get` refresh the expiry? **No.** Only `put` does (a new message from the patient).
- Expired exactly at `now == expires_at`? **Expired** (state the choice).
- Can I use Python lists? **Yes**, just not `dict`/`set`. Is `hash()` allowed? **Yes.**
- Part 2: is a day with no entry possible? **Follow-up: `None` = missed day.**

### Part 1: Hash map with TTL (LC 706)
- **Separate chaining:** an array of buckets; each bucket is a list of `[key, value, expires_at]`. Index = `hash(key) % capacity`.
- `put`: if the key is in the bucket, update the value and expiry; otherwise append.
- `get`: find the key; if it's expired, delete it and return `None` (**lazy expiry**).
- **Resize** when `size / capacity > 0.75`: double the array and **rehash everything** (the index depends on capacity).
- **Complexity:** average O(1), worst O(n) (all keys collide).
- **Classic bugs:** not rehashing on resize (looking in the wrong bucket); forgetting to update existing keys (duplicates in a bucket); not decrementing `size`.
- **Discussion:** lazy expiry means expired-but-never-read entries waste memory. Fix with a periodic sweep, or a min-heap of expiry times. In production, this is **Redis with a TTL** shared across servers, not in-process memory.

### Part 2: Longest varied streak (LC 3)
- **Brute force:** check every window with a set, O(n²).
- **Optimal:** a **sliding window** with `last_index[exercise]`. When you see a repeat *inside the current window* (`last_index >= start`), move `start` to `last_index + 1`. Track the best length. **O(n) time.**
- **Classic bug:** moving `start` backward for a repeat that's already outside the window. That's why the `last_index >= start` check is there (test: `a b c a d b`).
- **Follow-up (`None`):** reset `start = i + 1`.

### Hint ladder
1. Part 1: "How do you turn a phone number into an array index?" → "What if two numbers land on the same index?"
2. Part 2: "When you hit a repeat, which days can't be in any valid window that ends today?"

---

## Part B: System design (two-way SMS assistant)

### Clarifications (interviewer answers)
- **Scale:** ~200k active patients, ~30k inbound texts/day, bursts right after reminder blasts.
- **Flows:** reschedule (multi-step), cancel (with confirmation), FAQs (address, hours, parking). Anything else, or anything clinical, goes to staff.
- **Patients reply hours later**, or with something unrelated ("thanks!") mid-flow.
- **Constraints:** SMS provider webhooks (at-least-once delivery), STOP/opt-out, PHI minimization in texts, EMR is the source of truth.

### Reference design
```
Patient SMS --> SMS provider --webhook--> Inbound API (verify signature, dedupe message_id, enqueue, 200)
                                              v
                                    Queue (partitioned by phone number -> per-conversation ordering)
                                              v
                    Conversation worker:
                      load state (Redis w/ TTL, backed by DB)  <- Part A idea, but shared + durable
                      classify intent (rules first; LLM for free text, with a confidence threshold)
                      run state machine step: IDLE -> RESCHEDULE_ASK_DATE -> ASK_TIME -> CONFIRM -> DONE
                      call tools: availability / book / cancel (Scheduling service -> EMR)
                      save state + message log; send reply via SMS provider (idempotency key)
                                              v
                    Low confidence / clinical / angry / "talk to a person" -> staff inbox (with conversation history)
```

### APIs
- `POST /webhooks/sms/inbound` · `POST /webhooks/sms/status`
- `GET /clinics/{id}/inbox?status=NEEDS_STAFF` · `POST /conversations/{id}/reply` (staff) · `POST /conversations/{id}/resolve`
- `GET /conversations/{id}` (full thread + state + actions)

### Data
- `conversations(id, clinic_id, patient_id, phone, state, context_json, expires_at, assigned_to NULL, status)`
- `messages(id, conversation_id, direction, provider_message_id UNIQUE, body, created_at)`
- `actions(id, conversation_id, type, appointment_id, status)`
- `opt_outs(phone, created_at)`

### Concepts to mention (and why)
| Concept | Why |
|---|---|
| Fast ack + queue | the provider retries slow webhooks; the LLM/EMR calls are slow |
| Dedupe on `provider_message_id` | at-least-once webhooks, so we must not process "CONFIRM" twice |
| Per-conversation ordering (partition by phone) | two quick texts ("Tuesday" / "actually Wednesday") must be processed in order |
| Shared state store with TTL (Redis/DB) | any worker can continue the conversation; abandoned flows expire (the Part A concept, productionized) |
| State machine + rules before LLM | predictable flows; the LLM only helps interpret free text |
| Confirm before destructive actions | "Reply YES to cancel Tue 3pm" |
| Human handoff with context | staff see the full thread; AI isn't authoritative on clinical questions |
| Opt-out + PHI minimization | compliance: honor STOP immediately; no diagnoses in texts |
| Idempotent outbound sends + booking | retries must not double-text or double-book |

### Deep dives
1. **Patient replies "2" after the state expired.** The context is gone. Re-ask ("Want to reschedule your appointment on…?") rather than guess.
2. **Two messages arrive out of order or concurrently.** Partitioning by phone (or a per-conversation lock) gives one worker at a time per conversation.
3. **EMR booking fails after the patient said "yes."** Tell them, keep the state at `CONFIRM_PENDING`, retry, then hand off to staff if it still fails. Never text "You're booked!" before the EMR confirms.

### Rubric
- **Strong:** webhook → queue → worker, dedupe, shared state with TTL, a state machine, ordering per conversation, a handoff inbox, opt-out/PHI.
- **Red flags:** conversation state held in one server's memory; LLM free-for-all with direct EMR writes; no plan for late or duplicate messages.
