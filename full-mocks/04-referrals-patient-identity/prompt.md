# Full Mock 4: Referrals and Patient Identity

## Part A: Live coding (~30 min)

### Part 1: Group possible duplicate patients
Patient records come in from faxes, phone calls, and the EMR. The same person often shows up in different formats, like `"Jane Doe"`, `"DOE, JANE"`, and `"jane  doe"`. Group records that are **likely the same person** so a staff member can review them.

Two records are a possible match if they have the **same date of birth** and the **same name once you ignore case, punctuation, extra spaces, and word order**.

```python
def group_possible_duplicates(patients: list[dict]) -> list[list[int]]:
    """
    patients: [{"id": 1, "name": "Jane Doe", "dob": "1985-03-14"}, ...]
    Return groups (lists of ids) with MORE than one record.
    """
```
**Example**
```
[{"id": 1, "name": "Jane Doe",  "dob": "1985-03-14"},
 {"id": 2, "name": "DOE, JANE", "dob": "1985-03-14"},
 {"id": 3, "name": "John Doe",  "dob": "1985-03-14"},
 {"id": 4, "name": "jane  doe", "dob": "1985-03-14"},
 {"id": 5, "name": "Jane Doe",  "dob": "1990-01-01"}]
-> [[1, 2, 4]]
```
**Follow-up:** some DOBs come in as `"03/14/1985"` (MM/DD/YYYY). Handle both formats.

### Part 2: Flag re-sent faxes
Doctors' offices often re-send the same referral fax when they don't hear back. A fax counts as a **duplicate** if an earlier fax with the **same sender number and same page hash** arrived **within `window_min` minutes** of it.

```python
def find_duplicate_faxes(faxes: list[dict], window_min: int) -> list[str]:
    """
    faxes are sorted by received_at (minutes):
      [{"id": "A", "sender": "+15550001", "page_hash": "h1", "received_at": 0}, ...]
    Return the ids of duplicate faxes, in order.
    """
```
**Example**
```
A: sender s1, hash h1, t=0
B: sender s1, hash h1, t=5    <- duplicate of A
C: sender s2, hash h1, t=10
D: sender s1, hash h1, t=50
E: sender s1, hash h1, t=70   <- duplicate of D
window_min = 30  ->  ["B", "E"]
```

---

## Part B: System design (~20–25 min)

> A clinic group has patients spread across several clinics, each with its own EMR, plus records created by our referral and call-center tools. The same patient often exists **several times with slightly different data**. Design a service that **finds and resolves duplicate patient records**, so every downstream feature (scheduling, billing, outreach) uses the right person.
