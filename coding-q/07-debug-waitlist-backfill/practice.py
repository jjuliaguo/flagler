"""
Coding Q7 (DEBUG): Waitlist Backfill

Scenario
--------
When an appointment is canceled, the open slot should be offered to someone on
the waitlist. A teammate wrote the function below, and it's assigning the
wrong patients.

Your job (talk through it out loud):
  1. Explain what the function is SUPPOSED to do.
  2. Trace the test data by hand and find where the output goes wrong.
  3. Find and fix the bugs. Rank them by severity.

Requirements
------------
open_slots: [{"slot_id": "S1", "provider_id": "dr_b", "start": 540, "visit_type": "PT"}, ...]
            (start = minutes from midnight; NOT necessarily sorted)
waitlist:   [{"patient_id": "W1", "visit_type": "PT",
              "provider_id": "dr_a" or None,   # None = any provider is fine
              "added_at": 5,                   # smaller = waiting longer
              "earliest": 0}, ...]             # can't come before this minute
Rules:
  - Fill slots in order of start time (earliest slot first).
  - For each slot, pick the patient who has waited LONGEST among those whose
    visit_type matches, whose provider matches (or who accepts any provider),
    and whose earliest <= slot start.
  - Each patient gets at most one slot.
  - Don't modify the caller's waitlist.
Return {slot_id: patient_id or None} for EVERY slot.
"""


def backfill(open_slots, waitlist):
    waitlist.sort(key=lambda w: w["added_at"], reverse=True)
    result = {}
    for slot in open_slots:
        for w in waitlist:
            if (w["visit_type"] == slot["visit_type"]
                    and w["provider_id"] == slot["provider_id"]
                    and w["earliest"] < slot["start"]):
                result[slot["slot_id"]] = w["patient_id"]
                waitlist.remove(w)
    return result


# ---------------------------------------------------------------- tests
def run_tests(fn):
    slots = [
        {"slot_id": "S2", "provider_id": "dr_a", "start": 600, "visit_type": "PT"},
        {"slot_id": "S1", "provider_id": "dr_b", "start": 540, "visit_type": "PT"},
        {"slot_id": "S3", "provider_id": "dr_a", "start": 700, "visit_type": "EVAL"},
    ]
    waitlist = [
        {"patient_id": "W1", "visit_type": "PT", "provider_id": None, "added_at": 5, "earliest": 0},
        {"patient_id": "W2", "visit_type": "PT", "provider_id": "dr_a", "added_at": 1, "earliest": 600},
        {"patient_id": "W3", "visit_type": "PT", "provider_id": "dr_b", "added_at": 3, "earliest": 0},
        {"patient_id": "W4", "visit_type": "PT", "provider_id": "dr_a", "added_at": 2, "earliest": 650},
    ]
    original = [dict(w) for w in waitlist]
    result = fn(slots, waitlist)
    # S1 (540, dr_b): W2/W4 want dr_a; W3 (added 3) beats W1 (added 5) -> W3
    # S2 (600, dr_a): W2 waited longest and earliest 600 <= 600 -> W2
    # S3 (EVAL): nobody -> None
    assert result == {"S1": "W3", "S2": "W2", "S3": None}, result
    assert waitlist == original, "input waitlist was modified"

    # a patient who accepts any provider gets matched
    r = fn([{"slot_id": "S4", "provider_id": "dr_c", "start": 800, "visit_type": "PT"}],
           [{"patient_id": "W1", "visit_type": "PT", "provider_id": None, "added_at": 5, "earliest": 0}])
    assert r == {"S4": "W1"}, r

    assert fn([], []) == {}
    print("Q7: all tests passed")


if __name__ == "__main__":
    run_tests(backfill)
