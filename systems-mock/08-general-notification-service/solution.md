# 8. (General) Notification Service (solution notes)
**Emphasis:** API design, async fan-out, provider abstraction, scaling workers

## Answers to clarifying questions
- **Callers:** internal services (billing, scheduling, care team).
- **Channels:** SMS, email, push. One request may go to multiple channels.
- **Scale:** ~1M notifications/day, with peaks of 500/s (batch jobs).
- **Guarantees:** at-least-once delivery attempt; never send the same notification twice if the caller retries; respect user preferences/opt-outs.
- **Priority:** some are urgent (2FA code, escalation), most are not (newsletter).

## Reference design
```
Internal service --> POST /notifications (idempotency key) --> Notification API (stateless, behind load balancer)
                                                                   | validate, check prefs, save row, enqueue
                                                                   v
                                         Queues: high-priority  |  normal
                                                                   v
                                         Channel workers (SMS / Email / Push) --> provider adapters (Twilio, SES, FCM...)
                                                                   |
                                         status updates (+ provider delivery webhooks) --> notifications table
```
- The API is **stateless**, so you can add servers behind a **load balancer** (horizontal scaling).
- **Separate queues per priority** (and/or channel) so a 1M-email batch doesn't delay 2FA codes.
- **Templates** live in the service; callers pass a `template_id` + variables (consistent formatting, no PHI sprawl).

## APIs
- `POST /notifications {idempotency_key, recipient_id, channels[], template_id, vars, priority}` → `202 {notification_id}`
- `GET /notifications/{id}` (status per channel)
- `PUT /users/{id}/notification-preferences`
- `POST /webhooks/{provider}/status`

## Data
- `notifications(id, idempotency_key UNIQUE, caller, recipient_id, template_id, priority, created_at)`
- `deliveries(id, notification_id, channel, status, provider, provider_msg_id, attempts, last_error)`
- `preferences(user_id, channel, enabled, quiet_hours)`

## Concepts to mention (and why)
| Concept | Why |
|---|---|
| Idempotency key | a caller retry after a timeout shouldn't double-send |
| Queue + workers | providers are slow/rate-limited; absorb bursts; scale workers per channel |
| Priority queues | urgent messages aren't stuck behind bulk ones |
| Retries + backoff + DLQ | transient provider failures; poison messages are isolated |
| Provider abstraction / failover | switch providers in an outage without touching callers |
| Rate limiting | per provider limits, and per user (don't spam someone 50×) |
| Stateless API + LB | horizontal scaling; any server can handle any request |
| Observability | per-channel success rate, latency, queue depth |

## Failure modes / deep dives
1. **SMS provider outage** → retries back off; fail over to a secondary provider; urgent ones alert on-call.
2. **Caller retries same request** → idempotency key returns the existing `notification_id`.
3. **Worker crashes after the provider accepted but before marking SENT** → redelivery could double-send; mitigate with a provider-side idempotency key or a check of `provider_msg_id` before resend. Exactly-once is hard; say so.

## Follow-ups
1. Why return `202` instead of `200`?
2. How do you scale from 1M to 50M/day? (more workers, partitioned queues, DB write volume, maybe batch status writes)
3. How do you stop a bug in one caller from spamming every user?

## Rubric
- **Strong:** async API with an idempotency key, queues by priority, provider abstraction, retries/DLQ, prefs, honesty about at-least-once vs. exactly-once.
- **Red flags:** synchronous send in the API request; no dedupe.
