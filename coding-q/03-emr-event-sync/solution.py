"""Reference solution for Q3. Run: py solution.py"""
from practice import run_tests


def apply_events(events):
    seen_event_ids = set()
    state = {}
    for e in events:
        if e["event_id"] in seen_event_ids:  # rule 1: exact duplicate delivery
            continue
        seen_event_ids.add(e["event_id"])

        current = state.get(e["appt_id"])
        if current is not None and e["version"] <= current["version"]:  # rule 2: stale
            continue

        if e["type"] == "CANCELED":
            prev_start = current["start"] if current else None
            start = e["start"] if e["start"] is not None else prev_start
            status = "CANCELED"
        else:  # CREATED / RESCHEDULED
            start = e["start"]
            status = "BOOKED"

        state[e["appt_id"]] = {"status": status, "start": start, "version": e["version"]}
    return state


if __name__ == "__main__":
    run_tests(apply_events)
