# Concepts Cheat Sheet: what it is, *why* you'd use it

Interviewers reward the **why**. Each line answers "why would I add this?"

## Core flow
- **Client → API → service → DB.** Start every design here, then add pieces only when a requirement forces you to.
- **REST endpoints:** nouns + verbs (`POST /referrals/{id}/approve`), paginate lists, return `202 Accepted` for async work.
- **Request validation:** reject bad input at the edge so garbage never reaches the DB or downstream systems.
- **Relational DB (e.g. Postgres):** default choice for structured, related data with transactions (patients, appointments, claims). Pick something else only with a reason.
- **Indexes:** match the `WHERE`/`ORDER BY` of your hot queries (e.g. `(clinic_id, status, created_at)`). The trade-off is slightly slower writes.
- **Transactions:** multiple writes that must happen together (status change + audit row). All or nothing.

## Reliability
- **Queue + workers:** use one when work is **slow, bursty, or depends on an unreliable external system**. You ack the user fast, process later, and scale workers separately. *Don't* add one for a 5ms DB write.
- **Timeouts:** every external call needs one. Without it, a hung dependency ties up your threads/workers forever.
- **Retries + exponential backoff + jitter:** retry transient failures (timeouts, 5xx, 429) with growing waits (1s, 2s, 4s…), plus randomness so clients don't retry in sync. Don't retry 4xx validation errors.
- **Dead-letter queue (DLQ):** after N failures, park the message and alert, so one bad message doesn't block or loop forever.
- **Idempotency:** doing an operation twice has the same effect as once. Needed because **webhooks, queues, and client retries all deliver duplicates.** Tools: unique constraint on an external id, idempotency-key header, upsert.
- **At-least-once vs. exactly-once:** queues/webhooks give at-least-once. You get "effectively once" by making the processing idempotent.
- **Status/state machine:** persist where each item is (`RECEIVED → PROCESSED → …`) so you can resume after crashes, find stuck items, and report.
- **Partial failure:** "step 1 succeeded, step 2 failed." Persist progress, make steps retryable, and reconcile later.
- **Reconciliation job:** periodic "compare with source of truth and fix drift." It catches lost webhooks and missed updates.
- **Circuit breaker:** stop calling a dependency that keeps failing for a short while; fail fast and show a fallback.
- **Monitoring/alerting:** queue depth/lag, error rate, p95 latency, "items stuck in status X," "no data from clinic Y in 6h."

## Concurrency
- **Race condition:** "check then act" in two steps is a race. Two users both see "unassigned" and both take it.
- **Fix at the DB:** conditional update (`UPDATE ... WHERE assignee IS NULL` and check rows affected), `SELECT ... FOR UPDATE SKIP LOCKED` for job queues, unique constraints.
- **Optimistic locking:** a `version` column; the update succeeds only if the version is unchanged, otherwise return 409 and the client refreshes. Good when conflicts are rare (editing a record).

## Scaling (only when the requirements need it)
- **Vertical scaling:** bigger machine. Easy, but there's a ceiling and it's still a single point of failure.
- **Horizontal scaling:** more machines behind a **load balancer**. This requires **stateless** servers (keep sessions/state in the DB/cache, not memory).
- **Find the bottleneck first:** usually the DB or an external API, not the web servers.
- **Caching:** use it when reads are frequent, data changes rarely, and slightly stale is OK. Always say the **key, the TTL, and how it's invalidated**. Often "the DB row with a timestamp" *is* the cache.
- **Read replicas / separate analytics store:** keep heavy reporting queries away from the production DB.
- **Pre-aggregation:** compute rollups on a schedule so dashboards read small tables.
- **Partitioning/sharding:** split data by key (e.g. `clinic_id`) once one DB can't handle it. Rarely needed at startup scale; mention it as "later."
- **CDN:** static assets/files close to users. Usually not central in backend healthcare workflows.

## Healthcare-specific
- **PHI privacy (HIPAA):** encrypt at rest and in transit, minimum necessary data, no PHI in logs or SMS bodies, short-lived signed URLs for documents.
- **Access control (RBAC) + multi-tenancy:** `clinic_id`/`org_id` on every row, every query scoped server-side, roles for what each user can do.
- **Audit logs:** append-only record of who viewed or changed what, and when. Required for trust and compliance.
- **EMR integration:** EMRs are slow, rate-limited, inconsistent, and sometimes down. Use adapters, webhooks + polling, idempotent upserts, and reconcile.
- **Human-in-the-loop:** AI *suggests*, humans *confirm* for high-stakes or low-confidence output (patient identity, clinical concerns, money). AI output is not clinical judgment. Prefer false-positive escalations over missed ones.

## Phrases that show good judgment
- "Let me start with the simplest version that works, then harden it."
- "I'd add a queue here **because** ___."
- "This can be delivered twice, so I'll make it idempotent by ___."
- "What happens if this external system is down? ___."
- "For a startup at this scale, one Postgres is plenty. I'd revisit if ___."
- "A human should confirm this because the cost of being wrong is ___."
