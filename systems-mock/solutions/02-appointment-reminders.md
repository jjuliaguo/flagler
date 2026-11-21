# 2. Appointment Reminders (solution notes)
**Emphasis:** scheduled jobs, idempotency, external providers, patient preferences

## Answers to clarifying questions
- **Channels:** SMS first, automated voice call as a fallback. Email is optional.
- **When:** 48h and 2h before the appointment (configurable per clinic).
- **Scale:** about 100 clinics, ~20k appointments/day, so about 40k reminders/day, clustered at certain hours.
- **Replies:** "C" to confirm, "X" to cancel, "R" to reschedule. Free text goes to staff or a voice agent.
- **Constraints:** respect opt-outs (STOP), quiet hours in the *patient's* time zone, and minimal PHI in an SMS (no diagnosis).
- **Appointments come from the EMR**, and they can be rescheduled or canceled after a reminder is scheduled.

## Reference design
```
EMR sync --> appointments table
                 |
Scheduler (runs every minute): find reminders due now ----> Queue ----> Send workers ---> SMS/Voice provider (e.g. Twilio)
                                                                              |
Provider status webhooks + patient replies ---> Webhook API ---> update reminder / appointment ---> notify EMR / staff
```
- Store **`reminders` as rows** created when an appointment is created (one per offset). The scheduler polls `WHERE send_at <= now() AND status='PENDING'`. This is simpler and more inspectable than in-memory timers.
- **Right before sending, re-check** that the appointment is still active and at the same time, and that the patient hasn't opted out.
- Reply handling: map the inbound number to the most recent active reminder → update the appointment status → write back to the EMR (async).

## APIs
- `POST /appointments/{id}/reminders` (internal; usually auto-created)
- `POST /webhooks/sms/inbound` (patient reply) · `POST /webhooks/sms/status` (delivered/failed)
- `GET /clinics/{id}/reminders?date=` (staff view) · `PUT /clinics/{id}/reminder-settings`
- `POST /patients/{id}/opt-out`

## Data
- `appointments(id, clinic_id, patient_id, provider_id, start_at, status, emr_id)`
- `reminders(id, appointment_id, channel, send_at, status[PENDING|SENDING|SENT|FAILED|CANCELED], provider_message_id, attempts)`, `UNIQUE(appointment_id, channel, offset)`
- `patient_contact_prefs(patient_id, phone, timezone, sms_opt_out, quiet_hours)`
- Index: `(status, send_at)` for the scheduler.

## Concepts to mention (and why)
| Concept | Why |
|---|---|
| DB-backed schedule + poller | survives restarts, is easy to cancel/reschedule (update the row), and easy to debug |
| Claim before send (`UPDATE ... SET status='SENDING' WHERE id=? AND status='PENDING'`) | if 2 scheduler instances run, only one sends, so no double texts |
| Idempotency key to the provider | a retry after a timeout shouldn't send the SMS twice |
| Re-validate at send time | the appointment may have moved or been canceled since the reminder was created |
| Retry/backoff, then fallback channel | SMS fails → retry → voice call |
| Time zones | store UTC, render and apply quiet hours in the patient's local time |
| Compliance | STOP/opt-out honored immediately; minimal PHI in the message body |

## Failure modes / deep dives
1. **Appointment rescheduled after reminder is queued** → cancel/re-create reminder rows on change, *and* re-check at send time.
2. **SMS provider outage** → messages stay `PENDING`/`FAILED`, retry with backoff; alert; switch to the fallback provider/channel if critical.
3. **Patient replies to an old reminder / has 2 upcoming appointments** → match to the nearest upcoming one; if ambiguous, ask a follow-up or route to staff.
4. **8am burst** → the queue absorbs it; workers scale horizontally; respect the provider's rate limits.

## Follow-ups
1. How exactly does the 48h reminder get triggered?
2. You run two scheduler instances for availability. How do you avoid sending twice?
3. Patient cancels by text. Walk me through everything that happens.
4. How do you know reminders are actually working? (delivery rate, confirm rate, no-show rate metrics)

## Rubric
- **Strong:** reminder rows + poller/queue, de-dup/claim, re-check at send, inbound reply flow, opt-out/time zones, write-back to EMR.
- **Red flags:** `sleep()`/cron-per-appointment in memory; no handling of reschedules; PHI in SMS text.
