"""
Coding Q3: Out-of-Order EMR Appointment Events

Scenario
--------
A clinic's EMR sends us webhook events whenever an appointment changes. The
delivery is messy:
  - the same event can be delivered more than once (same event_id)
  - events can arrive out of order
Each event carries a per-appointment `version`. Higher means newer.
Build the final, correct state of every appointment.

Input
-----
events: list of dicts in DELIVERY order:
    {"event_id": "e1", "appt_id": "a1", "version": 1,
     "type": "CREATED" | "RESCHEDULED" | "CANCELED",
     "start": "2026-11-24T09:00" or None}

Rules
-----
1. Ignore an event whose event_id was already processed.
2. Ignore an event whose version is <= the version already applied for that
   appointment (stale or conflicting).
3. CREATED / RESCHEDULED -> status "BOOKED", start = event's start.
   CANCELED -> status "CANCELED"; keep the previous start if the event's
   start is None.
4. An appointment may be first seen via a RESCHEDULED or CANCELED event
   (its CREATED event is late). Handle it.

Output
------
{appt_id: {"status": ..., "start": ..., "version": ...}}
"""


def apply_events(events: list[dict]) -> dict[str, dict]:
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------- tests
def run_tests(fn):
    events = [
        {"event_id": "e1", "appt_id": "a1", "version": 1, "type": "CREATED", "start": "2026-11-24T09:00"},
        {"event_id": "e2", "appt_id": "a1", "version": 3, "type": "CANCELED", "start": None},
        {"event_id": "e3", "appt_id": "a1", "version": 2, "type": "RESCHEDULED", "start": "2026-11-24T10:00"},
        {"event_id": "e1", "appt_id": "a1", "version": 1, "type": "CREATED", "start": "2026-11-24T09:00"},
        {"event_id": "e4", "appt_id": "a2", "version": 2, "type": "RESCHEDULED", "start": "2026-11-24T11:00"},
        {"event_id": "e5", "appt_id": "a2", "version": 1, "type": "CREATED", "start": "2026-11-24T09:30"},
        {"event_id": "e6", "appt_id": "a3", "version": 1, "type": "CREATED", "start": "2026-11-24T13:00"},
        {"event_id": "e7", "appt_id": "a3", "version": 1, "type": "RESCHEDULED", "start": "2026-11-24T14:00"},
    ]
    expected = {
        # v1 booked 09:00 -> v3 canceled (keeps 09:00) -> v2 is stale, ignored
        "a1": {"status": "CANCELED", "start": "2026-11-24T09:00", "version": 3},
        # v2 arrives first; the late CREATED v1 is stale
        "a2": {"status": "BOOKED", "start": "2026-11-24T11:00", "version": 2},
        # same version, different event -> the second one is ignored
        "a3": {"status": "BOOKED", "start": "2026-11-24T13:00", "version": 1},
    }
    assert fn(events) == expected, fn(events)

    # cancel seen first with no start ever known
    only_cancel = [{"event_id": "x", "appt_id": "a9", "version": 5, "type": "CANCELED", "start": None}]
    assert fn(only_cancel) == {"a9": {"status": "CANCELED", "start": None, "version": 5}}

    assert fn([]) == {}
    print("Q3: all tests passed")


if __name__ == "__main__":
    run_tests(apply_events)
