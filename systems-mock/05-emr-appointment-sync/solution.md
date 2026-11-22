# 5. EMR Appointment Sync (solution notes)
**Emphasis:** integrations, duplicate and out-of-order webhooks, reconciliation, multi-tenancy

## Answers to clarifying questions
- **EMR behavior:** sends webhooks `appointment.created/updated/canceled` with an appointment id + `updated_at`. Webhooks are **at-least-once** (duplicates happen), **not ordered**, and are sometimes dropped. The REST API has rate limits (e.g. 10 req/s per clinic).
- **Scale:** 100 clinics, ~20k appointment changes/day.
- **Freshness:** within a few minutes is fine.
- **Direction:** mainly EMR → us. Some write-backs (confirmations from reminders).
- **Multiple EMR vendors?** Start with one, but don't hard-code it everywhere.

## Reference design
```
EMR --webhook--> Webhook API (verify signature, store raw event, 200 fast) --> Queue
                                                                               |
                                                               Sync worker: fetch latest from EMR API (or use payload)
                                                                               |
                                                     upsert appointments WHERE incoming.updated_at > stored.updated_at
                                                                               |
                                                            emit internal "appointment changed" event --> reminders, analytics...
Reconciliation job (every N min / nightly): list EMR appointments changed since last cursor --> same upsert path
```
- **Adapter layer** per EMR vendor maps their format to *our* appointment model, so the rest of the platform doesn't care which EMR it is.
- **Webhook = "something changed" hint; the EMR API = truth.** Re-fetching the record avoids acting on stale payloads.
- **Reconciliation** catches dropped webhooks. Webhooks are for speed, polling is for correctness.

## APIs
- `POST /integrations/{clinic_id}/emr/webhooks`
- Internal: `GET /appointments?clinic_id=&from=&to=`
- Admin: `POST /integrations/{clinic_id}/resync?since=` · `GET /integrations/{clinic_id}/health` (last sync time, error count)

## Data
- `webhook_events(id, clinic_id, external_event_id UNIQUE, payload, received_at, processed_at, error)`
- `appointments(id, clinic_id, emr_appointment_id, patient_id, provider_id, start_at, status, emr_updated_at)`, `UNIQUE(clinic_id, emr_appointment_id)`
- `integration_state(clinic_id, last_reconciled_cursor, credentials_ref)` (secrets in a vault, not the DB)
- Patient mapping: `patients(id, clinic_id, emr_patient_id)`

## Concepts to mention (and why)
| Concept | Why |
|---|---|
| At-least-once + idempotent processing | the same event processed twice gives the same result (upsert on the unique key) |
| Ordering via `updated_at`/version check | an old "rescheduled to 2pm" must not overwrite a newer "canceled" |
| Store raw events | debugging, replay after a bug fix, audit |
| Reconciliation job | webhooks get lost; periodic diff fixes drift |
| Rate limiting the EMR API | per-clinic token bucket in workers; queue absorbs backlog |
| Adapter pattern | multiple EMR vendors later without rewriting everything |
| Tenant isolation | `clinic_id` scoping; per-clinic credentials |
| Monitoring | "no webhooks from clinic X in 6 hours" is probably a broken integration, so alert |

## Failure modes / deep dives
1. **Duplicate webhook** → unique `external_event_id` and/or idempotent upsert.
2. **Out-of-order: cancel arrives before the create** → upsert creates the row as canceled; later create with an older `updated_at` is ignored.
3. **EMR down for 2 hours** → events sit in the queue/retry; reconciliation catches up after; downstream (reminders) re-check before acting.
4. **Bad data** (appointment for an unknown patient) → fetch the patient, or park the event in an error state + alert, rather than crash the worker.

## Follow-ups
1. The same webhook arrives twice. What happens?
2. "Update" arrives before "create." What happens?
3. How would you know if you silently missed events?
4. A second clinic uses a different EMR. What changes?

## Rubric
- **Strong:** fast ack + queue, idempotent upsert, ordering guard, reconciliation, rate limits, per-clinic health monitoring.
- **Red flags:** trusting webhooks as complete and ordered; blind overwrite; processing inline in the webhook request.
