# 6. Post-Visit Check-ins and Escalation (solution notes)
**Emphasis:** workflow scheduling, response tracking, escalation, human-in-the-loop, AI as an assistant only

## Answers to clarifying questions
- **Cadence:** e.g. day 2, day 7, and weekly until discharge. Configurable per care plan (post-surgery vs. PT).
- **Channel:** SMS with structured questions ("Reply 0–10"), maybe voice. Free-text replies are possible.
- **Escalation triggers:** pain ≥ 8, a big jump from the last score, keywords (fever, swelling, fall, chest pain), or no response after N attempts.
- **Who responds:** a nurse/care coordinator queue per clinic, during business hours. **Emergencies: the message tells the patient to call 911 / go to the ER**; the system is not an emergency service.
- **Scale:** ~50k active patients, so a few thousand messages/day.

## Reference design
```
Care plan assigned (from EMR visit / staff) --> checkin_schedule rows
Scheduler --> Queue --> Send worker --> SMS/voice provider
Patient reply --> Webhook API --> Response processor:
       1) parse structured answer (rules)   2) optional AI classify free text (assist only)
       3) store response   4) evaluate escalation rules
                                    |
                     escalations table --> Care team queue UI (+ page/notify for urgent)
                                    |
                          Nurse reviews, contacts patient, resolves (audit logged)
Analytics/trends: pain over time per patient, shown in the care team UI
```
- **Rules first, AI second.** Deterministic rules catch clear red flags. AI can *flag* free text ("sounds like a fall"), but it can only escalate or prioritize, never auto-dismiss or give medical advice.
- Bias toward false positives: an unnecessary escalation costs a nurse 2 minutes; a missed one can hurt a patient.

## APIs
- `POST /patients/{id}/care-plans` (assign check-in program)
- `POST /webhooks/sms/inbound`
- `GET /clinics/{id}/escalations?status=OPEN&severity=` · `POST /escalations/{id}/assign` · `POST /escalations/{id}/resolve {outcome, note}`
- `GET /patients/{id}/checkins` (timeline/trend)

## Data
- `care_plans(id, patient_id, clinic_id, template_id, start_date, status)`
- `checkins(id, care_plan_id, scheduled_at, sent_at, status)`
- `checkin_responses(id, checkin_id, raw_text, pain_score NULL, parsed_by[rule|ai|human], ai_flags, received_at)`
- `escalations(id, patient_id, clinic_id, response_id, severity, reason, status[OPEN|ASSIGNED|RESOLVED], assignee_id, created_at, resolved_at)`
- `audit_log`

## Concepts to mention (and why)
| Concept | Why |
|---|---|
| Rules engine + AI assist | predictable, explainable safety rules; AI isn't authoritative clinical judgment |
| Human review queue with SLA | escalations must be seen; alert if an urgent one is OPEN > 30 min |
| Store raw responses | audit, and re-evaluate if rules change |
| Idempotent reply handling | provider retries the inbound webhook, so you mustn't create 2 escalations |
| Non-response as a signal | escalate after N missed check-ins |
| Access control + audit | PHI; only the patient's clinic care team sees it |
| After-hours behavior | the auto-reply includes emergency instructions; queue is visible next morning; maybe on-call paging |

## Failure modes / deep dives
1. **SMS provider down** → check-ins delayed; retry; don't count as "patient didn't respond."
2. **Ambiguous reply ("it's bad")** → can't parse a score; ask a follow-up or escalate at low severity.
3. **Nobody works the queue** → SLA timers + escalate to manager; dashboard of open escalations.
4. **Patient replies "STOP"** → opt-out honored; care team notified that monitoring stopped.

## Follow-ups
1. How do you decide what gets escalated?
2. Where would you use an LLM, and what guardrails would you put on it?
3. A patient texts "I fell and can't feel my leg" at 11pm. What happens?
4. How do you prove an escalation was handled? (audit trail, resolve outcome)

## Rubric
- **Strong:** clear flow, deterministic rules + optional AI flagging, human queue with SLAs, emergency messaging, auditability, privacy.
- **Red flags:** LLM decides if a patient is fine with no human; no plan for after-hours or ignored escalations.
