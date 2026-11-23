# Full Mock 4: Solution Notes (Referrals and Patient Identity)
Code + tests: [solution.py](solution.py)

## Part A: Coding

### Clarifications a strong candidate asks
- What counts as the "same name"? **Ignore case, punctuation, extra spaces, and word order.** Middle names or initials? **Not handled in the base version** (good to raise).
- Output order? Groups in the order first seen; ids in input order.
- Part 2: are faxes sorted by time? **Yes.** Is the window inclusive? **Yes (`<=`).** Compare to the *first* copy or the *most recent* copy? **Most recent** (state it either way).

### Part 1: Group duplicates (LC 49)
- **Brute force:** compare every pair, O(n²).
- **Optimal:** build a **normalized key** for each record, group in a dict `key → [ids]`, and return the groups with size > 1.
  - Name key: lowercase → extract letter tokens → **sort the tokens** → join. Sorting the tokens is the "anagram" idea: different order, same key.
  - Full key: `(name_key, normalized_dob)`.
- **Complexity:** O(n · L log L), where L = tokens per name (tiny), so effectively O(n).
- **Follow-up (DOB formats):** normalize everything to `YYYY-MM-DD` before building the key.
- **Discussion points that impress:**
  - Exact keys miss typos ("Jane" vs "Jnae") and nicknames ("Bob" vs "Robert"). That needs fuzzy matching or scoring.
  - **This output is a list of candidates for a person to review. It never auto-merges.** Merging two different patients is a safety problem.

### Part 2: Re-sent faxes (LC 219)
- Dict `(sender, page_hash) → last received_at`. For each fax: if the key was seen and `now - last ≤ window`, it's a duplicate. Always update the last-seen time.
- **O(n) time, O(unique keys) space.**
- **Design choice to say out loud:** comparing to the most recent copy means a chain of resends every 20 min (window 30) are all duplicates. Comparing to the first copy behaves differently. Neither is wrong, so ask which the business wants.
- Real-world note: a re-scanned fax gives a different hash, so exact hashing misses it. Follow-ups could compare the extracted patient + referral content instead.

### Hint ladder
1. "If two records are the same person, what would they look like after cleaning?"
2. "How do you make 'Doe Jane' and 'Jane Doe' produce the same thing?" (sort the words)
3. Part 2: "What's the only earlier fax you need to remember for each sender + hash?"

---

## Part B: System design (patient matching / duplicate-record service)

### Clarifications (interviewer answers)
- **Sources:** 5 clinics' EMRs (different vendors), referral intake, call center. ~500k patient records total, ~2k new/updated per day.
- **Fields:** name, DOB, phone, address, insurance member ID, sometimes the last 4 of SSN. Lots of typos and missing values.
- **Goal:** each downstream feature should resolve to one "golden" patient ID. **A false merge (two different people combined) is much worse than a missed duplicate.**
- Staff need to be able to review, approve, and **undo** merges.

### Reference design
```
Source systems (EMRs, referrals, calls) --> Ingest/normalize (clean names, phones E.164, DOB ISO, addresses)
        --> source_records table (one row per record per source, never deleted)
        --> Matching worker (queue-driven, on new/updated record):
              1) blocking: find candidates cheaply (same DOB, or same phone, or same insurance ID) via indexes
              2) scoring: compare fields -> match score (rules or weighted)
              3) decide: score >= high -> auto-link | middle -> review queue | low -> new patient
        --> patients (golden record) + links(source_record -> patient_id)
Review UI: staff approve / reject / split; every action audited
Downstream services ask: GET /patients/resolve?source=&source_id= -> patient_id
```
- **Blocking** is the key scaling idea: comparing every new record against 500k is too slow, so first narrow to candidates that share an exact attribute (indexed), then score just those (Part A's grouping idea at scale).
- **Link, don't destroy:** keep every source record and map it to a golden patient ID. A merge is just changing links, so **undo is possible.**

### APIs
- `POST /records` (ingest from a source; idempotent on `(source, source_id, version)`)
- `GET /patients/resolve?source=&source_id=`
- `GET /match-reviews?status=PENDING` · `POST /match-reviews/{id}/approve|reject`
- `POST /patients/{id}/split` (undo a merge)

### Data
- `source_records(id, source, source_id, clinic_id, name_norm, dob, phone, member_id, raw, updated_at)`, `UNIQUE(source, source_id)`
- `patients(id, golden fields..., created_at)`
- `record_links(source_record_id, patient_id, linked_by[auto|user], score, created_at)`
- `match_reviews(id, record_a, record_b, score, reasons, status, reviewer_id)`
- `audit_log`
- Indexes: `dob`, `phone`, `member_id`, `(name_norm, dob)`

### Concepts to mention (and why)
| Concept | Why |
|---|---|
| Normalization before matching | "(555) 123-4567" vs "5551234567" otherwise looks different |
| Blocking + indexes | avoids O(n²) comparisons; only score plausible candidates |
| Scoring + thresholds | explainable; tune toward avoiding false merges |
| Human review for the middle band | identity mistakes are patient-safety and privacy incidents |
| Non-destructive links + undo | merges will sometimes be wrong; must be reversible |
| Idempotent ingest | sources re-send records |
| Queue-driven matching | ingestion stays fast; matching can be retried |
| Audit log + access control | who merged what; PHI; clinic-level permissions |

### Deep dives
1. **Twins** (same DOB, same address, similar names) → a classic false-merge risk. Require a strong differing-field check, then send to review.
2. **A source updates a record after it was linked** (phone changed) → re-run matching for that record; don't silently move links without review if the score drops.
3. **A bad auto-merge is discovered** → split: restore the links for that source record and notify downstream services (event) to re-resolve.

### Rubric
- **Strong:** normalize → block → score → threshold with human review; non-destructive links; undo; idempotent ingest; explains why false merges are worse.
- **Red flags:** auto-merging on name + DOB; deleting the "duplicate" record; comparing every record against every other.
