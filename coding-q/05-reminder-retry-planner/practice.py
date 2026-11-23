"""
Coding Q5: Reminder Retry Planner

Scenario
--------
We text patients an appointment reminder and retry if they don't confirm.
A scheduler runs periodically and asks: "for each reminder, what should we do
right now?" Implement the decision logic.

Time is in whole HOURS since some epoch (int). Hour of day = t % 24.

Input
-----
reminders: [{"id": "R1", "appt_start": 1100,
             "status": "PENDING" | "CONFIRMED" | "OPTED_OUT" | "CANCELED",
             "attempts": [990, 992]},   # times we already sent, ascending
            ...]
now: int

Rules (apply in this order)
---------------------------
1. status != "PENDING"         -> ("STOP", status)
2. 3 or more attempts already  -> ("STOP", "MAX_ATTEMPTS")
3. Next send time:
     no attempts yet -> appt_start - 48
     after 1 attempt -> last attempt + 2
     after 2 attempts-> last attempt + 6
4. Quiet hours: never send between 21:00 and 08:00 (hour 21..23 or 0..7).
   If the next send time falls in quiet hours, move it to 08:00 of the
   next morning (same day if it's already past midnight).
5. If the (possibly moved) next send time >= appt_start - 1
                               -> ("STOP", "TOO_LATE")
6. If next send time <= now     -> ("SEND", next_time)
   otherwise                    -> ("WAIT", next_time)

Output
------
{reminder_id: (action, value)}
"""


def plan_reminders(reminders: list[dict], now: int) -> dict[str, tuple]:
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------- tests
def run_tests(fn):
    now = 1000  # hour of day = 16
    reminders = [
        {"id": "R1", "appt_start": 1100, "status": "PENDING", "attempts": []},            # first at 1052 (20:00)
        {"id": "R2", "appt_start": 1030, "status": "PENDING", "attempts": [990]},         # 992 (08:00) -> due
        {"id": "R3", "appt_start": 1100, "status": "PENDING", "attempts": [900, 902]},    # 908 -> due
        {"id": "R4", "appt_start": 1100, "status": "PENDING", "attempts": [1, 2, 3]},
        {"id": "R5", "appt_start": 1100, "status": "CONFIRMED", "attempts": [990]},
        {"id": "R6", "appt_start": 1054, "status": "PENDING", "attempts": []},            # 1006 = 22:00 -> next day 08:00 = 1016
        {"id": "R7", "appt_start": 1059, "status": "PENDING", "attempts": []},            # 1011 = 03:00 -> same day 08:00 = 1016
        {"id": "R8", "appt_start": 1043, "status": "PENDING", "attempts": [1040]},        # 1042 >= 1042 -> too late
        {"id": "R9", "appt_start": 1035, "status": "PENDING", "attempts": [1027]},        # 1029 = 21:00 -> 1040 -> too late
    ]
    expected = {
        "R1": ("WAIT", 1052),
        "R2": ("SEND", 992),
        "R3": ("SEND", 908),
        "R4": ("STOP", "MAX_ATTEMPTS"),
        "R5": ("STOP", "CONFIRMED"),
        "R6": ("WAIT", 1016),
        "R7": ("WAIT", 1016),
        "R8": ("STOP", "TOO_LATE"),
        "R9": ("STOP", "TOO_LATE"),
    }
    result = fn(reminders, now)
    for rid, exp in expected.items():
        assert result.get(rid) == exp, (rid, result.get(rid), exp)

    assert fn([], now) == {}
    print("Q5: all tests passed")


if __name__ == "__main__":
    run_tests(plan_reminders)
