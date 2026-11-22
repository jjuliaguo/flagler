# 1. eFax Referral Intake (solution notes)
**Emphasis:** async processing, human-in-the-loop, integrations

## Answers to clarifying questions
- **Users:** clinic intake staff (review and route), schedulers. The patient is contacted afterward.
- **Scale:** about 50 clinics, each getting 20–200 faxes/day, which is roughly 5k/day total. Bursty in business hours.
- **Input:** an eFax provider sends a **webhook** with a link to a PDF. Faxes can be blurry, multi-page, or contain several patients or junk (marketing faxes).
- **Extract:** patient name, DOB, phone, insurance, referring provider, diagnosis/body part, urgency.
- **Goal:** time from fax to scheduled matters (a slow referral means a lost patient). Nothing can be lost.
- **Constraints:** PHI (HIPAA). Each clinic can only see its own referrals. Final data goes to the clinic's EMR.

## Reference design
```
eFax provider --webhook--> Ingest API --(store PDF)--> Object storage (encrypted)
                               |  insert referral(status=RECEIVED), return 200 fast
                               v
                            Queue --> Extraction worker (OCR + AI extraction)
                                          | writes fields + confidence per field
                                          v
                                    DB: referrals  (status=NEEDS_REVIEW / READY)
                                          |
             Staff review UI <------------+   (human confirms low-confidence fields)
                    |
                    v
          Routing (clinic/location/provider rules) --> EMR integration --> schedule outreach
```
- **Ack fast, work later:** the webhook handler only stores the file and enqueues. OCR/AI is slow (seconds to minutes) and the provider will retry if we're slow.
- **Human review** for low-confidence or high-stakes fields (DOB, name, insurance ID). The AI suggests and a human confirms. Optionally auto-approve only above a high confidence threshold.
- **Patient matching:** look up an existing patient by name+DOB+phone. On an ambiguous match, send it to review. Never auto-merge.

## APIs
- `POST /webhooks/efax` → verify signature, dedupe on `provider_fax_id`, store, enqueue, `200`
- `GET /referrals?clinic_id=&status=NEEDS_REVIEW` (paginated)
- `GET /referrals/{id}` (fields, confidence, PDF link via short-lived signed URL)
- `PATCH /referrals/{id}` (staff corrections) · `POST /referrals/{id}/approve` · `POST /referrals/{id}/route`

## Data
- `referrals(id, clinic_id, provider_fax_id UNIQUE, pdf_key, status, received_at, assigned_location_id, patient_id NULL, version)`
- `referral_fields(referral_id, name, value, confidence, source[ai|human])`
- `audit_log(actor, action, entity, entity_id, timestamp, diff)`
- Indexes: `(clinic_id, status, received_at)` for the review queue.

## Concepts to mention (and why)
| Concept | Why |
|---|---|
| Queue + workers | OCR is slow and bursty; decouples ingestion from processing; scale workers separately |
| Idempotency on `provider_fax_id` | webhook providers retry, so the same fax must not create 2 referrals |
| Status state machine | RECEIVED → EXTRACTED → NEEDS_REVIEW → APPROVED → ROUTED → SCHEDULED; shows progress and lets you resume after failures |
| Retries + dead-letter queue | transient OCR/EMR failures retry with backoff; poison messages go to a DLQ and alert, not loop forever |
| Human-in-the-loop | AI extraction is error-prone and a wrong DOB means the wrong patient. AI isn't authoritative |
| Tenant isolation + RBAC | `clinic_id` on every row and every query is scoped by it; staff only see their clinic |
| Encryption + signed URLs + audit log | PHI at rest and in transit; track who viewed or changed what |
| Monitoring | alert on queue depth and on "referrals stuck in status X > N hours" |

## Failure modes / deep dives
1. **Duplicate webhook** → unique constraint on `provider_fax_id`; on conflict, return 200 and do nothing.
2. **Worker crashes mid-extraction** → message isn't acked, so it gets redelivered. The step must be idempotent (upsert fields keyed by referral).
3. **EMR is down when routing** → keep status `APPROVED`, retry with backoff; the referral is still visible to staff so nothing is lost.
4. **Two staff edit the same referral** → optimistic locking (`version` column) or assign/claim the referral.
5. **Fax contains 2 patients / junk** → reviewer can split or mark as not-a-referral.

## Follow-ups (in order)
1. Why not process the fax inside the webhook request?
2. The provider sends the same fax twice. What happens?
3. How do you decide what needs human review?
4. How does a clinic make sure it never sees another clinic's referrals?
5. Volume grows 10× next month. What breaks first? (Workers/OCR, so scale workers horizontally; the DB is fine.)

## Rubric
- **Strong:** fast-ack + queue, dedupe key, explicit statuses, human review with confidence, tenant scoping, PHI handling, mentions monitoring of stuck items.
- **OK:** working sync pipeline with some reliability added when prompted.
- **Red flags:** AI output written straight into the EMR with no review; no plan for duplicates; PHI in logs; no clinic separation.
