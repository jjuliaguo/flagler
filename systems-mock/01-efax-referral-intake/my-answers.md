# My Answers: Mock #1, eFax Referral Intake
*Attempt 1, Nov 21, 2026*

## Summary

### ✅ What I did well
- **Changed my design when I got new facts.** Once I heard the scale (50 clinics, US only), I dropped the CDN myself.
- **Thought about duplicate patients.** I planned to check whether a patient already exists in the DB/EMR before creating one. That's a real concern and it's in the reference solution.
- **Got to queue + workers** ("the rail is the queue, the cooks are the independent servers").
- **Asked when I didn't understand** ("can u explain…", "what is the reply") instead of guessing.
- **Asked good clarifying questions** once prompted: volume, location, whether it connects to other clinics' or doctors' software.

### ❌ What I missed
- **Started designing before clarifying.** I jumped into components before asking about scale and users.
- **Added tools that didn't fit the problem:** CDN (for latency we didn't need), caching (for something that has to be durable), and horizontal scaling (to fix how slow *one* request is, which it can't).
- **Put slow work inside the webhook request.** I had parsing plus EMR checks running before replying, so the provider times out and retries.
- **Didn't know how the PDF gets read:** OCR, then AI/rules extraction, then **confidence scores**.
- **Didn't say who catches extraction mistakes.** The answer is a **person reviewing** low-confidence fields. SSN isn't on referrals, and a new patient has nothing to compare against.
- **Misread what the retry does.** The first request doesn't stop. The retry runs **in parallel**, which can create **duplicate referrals or patients**. The fix is **idempotency** (a unique `fax_id`).
- **Not reached:**
  - status tracking in the DB (`RECEIVED → NEEDS_REVIEW → APPROVED → SCHEDULED`)
  - keeping each clinic's data separate (`clinic_id` on every query)
  - privacy (encryption, no patient info in logs, audit log)
  - EMR outage plus retries
  - monitoring

### 🎯 What to focus on
1. **Webhook pattern:** check the signature → dedupe → save the file and a DB row → enqueue → reply `200` fast → a worker does the slow work.
2. **Idempotency:** webhooks and queues deliver duplicates. Use a unique ID plus "if seen, do nothing."
3. **Justify every component:** "I'm adding X **because** Y." If there's no Y, leave it out.
4. **Cache vs. durable storage:** a cache is for speeding up reads and can lose data. Anything you can't lose goes in the DB or file storage.
5. **Human-in-the-loop for AI:** AI suggests, a person confirms anything low-confidence or high-stakes.
6. **Healthcare checklist** to mention every time: clinic data separation, PHI privacy, audit log.

---

## What I said (in order)

**Q: Design a system that receives referral faxes, extracts the info, and gets the patient scheduled.**
> first, when the info comes in there can be a cdn system based on location of where the msk clinic is and thus, it can also store files/images/etc of patient information - the database can store things like patient id, dob, and other structured information that is required for most/all patients in a referral -> it would be stored into the database using the api. another api (get) would be used to get the important information - then it could be scheduled accordingly using another api that accesses calendar for whichever treatment they require. Api will be used to get the patient's phone number then do the calling and updating the info after the call. Things can be cached include: the clinic that the patient will be scheduled with (cached by type of treatment they provide)

*Feedback:* The flow and the structured DB data are reasonable. The CDN and cache weren't justified, and there's no step that actually reads the fax.

**Q: Anything you'd want to know first? And what is the CDN solving?**
> i would want to know how many patients is it expecting to schedule, where are they located (condensed geogrpahic region or across the world), is this a standalone system just used by the front desk staff or does it connect with multiple different clinics/doctors software as well

*Feedback:* Good questions. Ask these **first** next time.

**Q: (After hearing ~5k faxes/day, US only, eFax webhook, clinics use an EMR.) What is the CDN doing?**
> originally my thought was because of the geographic proximity and breadth, it would be good to use the cdn... However, because there are only about 50 clinics and max 200 patients, i dont think that is necessary for the current scale. Since we don't want duplicates, we can use an api to check if the patient already exists in the EMR.

*Feedback:* Good self-correction, and checking for existing patients is good. (Also, a CDN is for serving static content to users quickly. It isn't a store for incoming patient files.)

**Q: Walk through webhook → ready to schedule. How do we get the fields out of the PDF?**
> the moment that the efax provider calls our webhook, we would parse through the fax for key patient information such as name, patient id, etc. and check if it already exists in the database/emr. if it's not in there, the api creates a new entry and stores the value there... Then another api is used to schedule the patient

*Feedback:* Everything happens inside the webhook request, which is too slow. "Parse" was vague (it needs OCR + extraction).

**Q: What reads the image, and how do we know it's right? What if extraction takes 30s, the provider waits 5s, and then it retries?**
> im not too sure -- what we could do to check if it's right is if the patient already exists there should be some primary key that uniquely identifies the patient and as a result we can match things like dob, name, etc. (a unique thing would be like ssn) -> in terms of timing: it causes redundant calling of the webhook - it would stop the current process (even if it's not done and restart it) this means that if there were more faxes coming it would take a long time

*Feedback:* Referrals rarely include an SSN, and new patients can't be matched. A retry runs **in parallel** with the first request (it doesn't restart it), so you get duplicates.

**Q: How would you restructure so we reply in ~2s but still do the slow work?**
> we could partition the work - horizontally scale by adding more servers taht can check for respective infromation and the other creates the patient for example

*Feedback:* More servers handle *more faxes at once*, but **one** fax still takes 30s. Wrong tool for this problem.

**Q: (Restaurant hint.) What's the ticket, the rail, the cooks?**
> ok so we can use caching essentially for the patient info? the rail is the queue the cooks are the independent servers

*Feedback:* ✅ The queue and workers are correct. ❌ The "ticket" needs **durable** storage, not a cache.

**Q: Before replying 200, where do you save the PDF and the "received" record?**
> the pdf file in the database/disk and the record in the queue

*Feedback:* Close. Put the PDF in **file/object storage** (e.g. S3), and put a **DB row with a status** plus a **queue message**. The DB row is how staff and the system track every referral.

---

## Reference flow (to memorize)
```
POST /webhooks/efax
  verify signature -> dedupe on fax_id -> save PDF to S3 -> insert referrals(status=RECEIVED) -> enqueue -> 200 OK
Worker: OCR -> AI extract fields + confidence -> NEEDS_REVIEW or READY
Staff review UI: confirm/fix fields + patient match -> APPROVED
Send to EMR (retry w/ backoff if down) -> schedule/call patient
Always: clinic_id scoping, encryption, audit log, alert on stuck referrals
```
Full notes: [solution.md](solution.md)
