"""Reference solution for Q5. Run: py solution.py"""
from practice import run_tests

MAX_ATTEMPTS = 3
FIRST_OFFSET = 48
BACKOFF = [2, 6]  # hours after attempt 1, attempt 2
QUIET_START, QUIET_END = 21, 8


def next_allowed_time(t):
    hour = t % 24
    day_start = t - hour
    if hour >= QUIET_START:              # late evening -> tomorrow 08:00
        return day_start + 24 + QUIET_END
    if hour < QUIET_END:                 # after midnight -> today 08:00
        return day_start + QUIET_END
    return t


def plan_one(r, now):
    if r["status"] != "PENDING":
        return ("STOP", r["status"])
    attempts = r["attempts"]
    if len(attempts) >= MAX_ATTEMPTS:
        return ("STOP", "MAX_ATTEMPTS")

    if not attempts:
        next_time = r["appt_start"] - FIRST_OFFSET
    else:
        next_time = attempts[-1] + BACKOFF[len(attempts) - 1]
    next_time = next_allowed_time(next_time)

    if next_time >= r["appt_start"] - 1:  # check AFTER the quiet-hours shift
        return ("STOP", "TOO_LATE")
    return ("SEND", next_time) if next_time <= now else ("WAIT", next_time)


def plan_reminders(reminders, now):
    return {r["id"]: plan_one(r, now) for r in reminders}


if __name__ == "__main__":
    run_tests(plan_reminders)
