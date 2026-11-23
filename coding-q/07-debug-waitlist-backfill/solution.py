"""Fixed version of Q7. Run: py solution.py"""
from practice import run_tests


def backfill(open_slots, waitlist):
    # FIX: sorted() copy, oldest first (not reverse); caller's list untouched
    candidates = sorted(waitlist, key=lambda w: w["added_at"])
    assigned = set()
    result = {}
    for slot in sorted(open_slots, key=lambda s: s["start"]):  # FIX: earliest slot first
        result[slot["slot_id"]] = None  # FIX: every slot appears in the output
        for w in candidates:
            if w["patient_id"] in assigned:
                continue
            if (w["visit_type"] == slot["visit_type"]
                    and w["provider_id"] in (None, slot["provider_id"])  # FIX: None = any provider
                    and w["earliest"] <= slot["start"]):  # FIX: <= (can come exactly at start)
                result[slot["slot_id"]] = w["patient_id"]
                assigned.add(w["patient_id"])  # FIX: no list.remove() while iterating
                break  # FIX: one patient per slot
    return result


if __name__ == "__main__":
    run_tests(backfill)
