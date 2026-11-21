# 9. (General) Webhook Ingestion Under Bursts (solution notes)
**Emphasis:** load balancing, horizontal scaling, buffering/backpressure, idempotency

## Answers to clarifying questions
- **Partner behavior:** retries if we don't return 2xx within 5s, up to 24h. Each event has a unique `event_id`. They sign requests (HMAC).
- **Burst:** ~50k events in ~3 minutes (~280/s) once per day; baseline ~5/s.
- **Processing per event:** ~200ms–2s (DB writes, a call to another service).
- **Current problem:** one server does receive + process inline, so requests time out, the partner retries, the load doubles, and the server dies.
- **Ordering:** mostly doesn't matter, except events for the same entity should apply in order (or be order-safe).

## Reference design
```
Partner --> Load balancer --> N stateless receiver instances
                                  | verify signature, minimal validation
                                  | write raw event to durable queue (or events table)
                                  | return 200 immediately (~10ms)
                                  v
                              Durable queue (buffer)
                                  v
                       Worker pool (autoscale on queue depth) --> process --> DB
                                  |
                              failures --> retry w/ backoff --> DLQ + alert
```
- **Key insight: separate receiving from processing.** Receiving is cheap and must be fast; processing can lag a few minutes during the burst and catch up. The queue is the shock absorber.
- **Receivers** are stateless, so you can scale horizontally behind a load balancer. **Workers** scale on queue depth.
- Protect the DB: cap worker concurrency so the burst doesn't exhaust DB connections (backpressure).

## APIs
- `POST /webhooks/partner` → `200` once enqueued (or `503` if the queue is unavailable, so the partner retries later; never lose it silently)
- Internal/admin: `GET /webhooks/stats` (lag, DLQ size) · `POST /webhooks/dlq/replay`

## Data
- `processed_events(event_id PRIMARY KEY, processed_at)` or a unique constraint on the business table
- Optional `raw_events` table/object storage for replay and audit

## Concepts to mention (and why)
| Concept | Why |
|---|---|
| Fast ack + async processing | avoid partner timeouts and the retry storm that amplifies load |
| Durable queue | the burst is absorbed; nothing is lost if a worker dies |
| Horizontal scaling + LB | no single point of failure; add receivers for throughput |
| Autoscaling workers on queue depth | pay for capacity only during the burst |
| Idempotency via `event_id` | partner retries and queue redeliveries are normal |
| Backpressure / concurrency limits | the DB is usually the real bottleneck; don't DDoS yourself |
| Vertical vs. horizontal | a bigger box is a quick fix, but it's still one point of failure and has a ceiling |
| Monitoring | queue lag, processing error rate, DLQ size, p95 ack latency |

## Failure modes / deep dives
1. **Queue down** → return 5xx so the partner retries (they keep events for 24h); alert.
2. **A bad event crashes the worker every time** → limited retries, then DLQ; don't block the rest.
3. **Out-of-order events for the same entity** → apply only if the event timestamp/version is newer; or partition by entity id so one worker handles that entity in order.
4. **Burst grows 10×** → more receivers/workers; the DB becomes the bottleneck, so batch writes, add indexes, and only then consider partitioning.

## Follow-ups
1. Why does the single server fall over? Explain the retry amplification.
2. Why not just get a bigger server?
3. What's the bottleneck after adding the queue?
4. How do you guarantee each event is processed once (effectively)?

## Rubric
- **Strong:** diagnoses the inline-processing problem, adds a queue + fast ack, idempotency, scales the right tier, names the DB as the next bottleneck.
- **Red flags:** "add more servers" without decoupling; ignoring duplicates; assuming exactly-once delivery from the queue.
