# Prompts (candidate-facing, no spoilers)

Read one prompt, start a timer, and drive the conversation. Ask clarifying questions before you design.

---

### 1. Referral intake from eFax
> MSK clinics receive patient referrals from primary-care doctors, mostly by **fax**. Today, front-desk staff read each fax, type the patient's info into the EMR, and call the patient to schedule. Design a system that receives these faxes, pulls out the important information, and gets each referral to the right place so the patient gets scheduled quickly.

---

### 2. Appointment reminders
> Patients often miss physical-therapy and ortho appointments. Design a system that sends patients reminders (text and/or automated call) before their appointments and lets them confirm, cancel, or ask to reschedule.

---

### 3. Insurance eligibility checks
> Before a visit, the clinic needs to know whether the patient's insurance is active and what it covers. Checking requires calling insurance-payer systems, which are **slow and sometimes down**. Design a service that makes eligibility results available to front-desk staff before patients arrive.

---

### 4. Denied-claims work queue
> When an insurer denies a claim, a billing specialist has to investigate, fix, and resubmit or appeal it, often with deadlines. A clinic group has a team of billing specialists and thousands of open denials. Design the system that tracks denials and assigns and moves them through to resolution.

---

### 5. EMR appointment sync
> Clinics already use an EMR (electronic medical record) system and don't want another portal. Our platform needs an up-to-date copy of each clinic's appointments (created, rescheduled, canceled) so our other features can act on them. The EMR can send us webhooks and also has a REST API. Design the sync.

---

### 6. Post-visit check-ins and escalation
> Between visits, we want to check in with patients (e.g. "How's your pain on a scale of 0–10? Are you doing your exercises?"), track their responses over time, and make sure concerning responses get to the care team. Design it.

---

### 7. Clinic analytics dashboard
> Clinic owners want a dashboard showing things like appointments per day, no-show rate, referral-to-scheduled time, and claim denial rate, per location and per provider. Design the backend that powers it.

---

### 8. (General) Notification service
> Several internal services need to send users notifications: SMS, email, and push. Design a shared notification service they can all call.

---

### 9. (General) Webhook ingestion endpoint
> A third-party partner sends us webhook events. Usually it's a few per second, but at the end of each day they send a burst of about 50,000 within a few minutes. Our current single server falls over. Design a system that reliably receives and processes all of them.
