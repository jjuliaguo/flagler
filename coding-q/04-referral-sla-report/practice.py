"""
Coding Q4: Referral SLA Report

Scenario
--------
Clinics promise to schedule referred patients within 48 hours (the "SLA").
Operations wants a per-clinic report to see who's falling behind.

Input
-----
referrals: [{"id": "r1", "clinic": "Ortho East",
             "received_at": 10,            # hours (int)
             "scheduled_at": 30 or None},  # None = not scheduled yet
            ...]
now: current time in hours (int)
sla_hours: default 48

Rules
-----
1. Skip invalid records where scheduled_at < received_at (bad data).
2. A referral BREACHES the SLA if:
     - it was scheduled more than sla_hours after it was received, or
     - it is still unscheduled and more than sla_hours have passed (now - received_at).
   Exactly sla_hours is NOT a breach.
3. Per clinic compute:
     total       - number of valid referrals
     scheduled   - number with scheduled_at
     avg_hours   - average hours from received to scheduled, over scheduled
                   referrals only, rounded to 1 decimal; None if none scheduled
     breaches    - number of SLA breaches

Output
------
List of dicts, one per clinic:
  {"clinic", "total", "scheduled", "avg_hours", "breaches"}
sorted by breaches (most first), then clinic name (A-Z).
"""


def referral_sla_report(referrals: list[dict], now: int, sla_hours: int = 48) -> list[dict]:
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------- tests
def run_tests(fn):
    referrals = [
        {"id": "r1", "clinic": "Ortho East", "received_at": 0, "scheduled_at": 24},
        {"id": "r2", "clinic": "Ortho East", "received_at": 10, "scheduled_at": 70},   # 60h -> breach
        {"id": "r3", "clinic": "Ortho East", "received_at": 40, "scheduled_at": None}, # 60h waiting -> breach
        {"id": "r4", "clinic": "Ortho East", "received_at": 90, "scheduled_at": None}, # 10h waiting -> fine
        {"id": "r5", "clinic": "Spine West", "received_at": 0, "scheduled_at": 12},
        {"id": "r6", "clinic": "Spine West", "received_at": 20, "scheduled_at": 10},   # invalid -> skip
        {"id": "r7", "clinic": "Ankle North", "received_at": 50, "scheduled_at": None},# 50h -> breach
        {"id": "r8", "clinic": "Ankle North", "received_at": 51, "scheduled_at": None},# 49h -> breach
        {"id": "r9", "clinic": "Spine West", "received_at": 52, "scheduled_at": None}, # exactly 48h -> fine
    ]
    expected = [
        {"clinic": "Ankle North", "total": 2, "scheduled": 0, "avg_hours": None, "breaches": 2},
        {"clinic": "Ortho East", "total": 4, "scheduled": 2, "avg_hours": 42.0, "breaches": 2},
        {"clinic": "Spine West", "total": 2, "scheduled": 1, "avg_hours": 12.0, "breaches": 0},
    ]
    result = fn(referrals, now=100)
    assert result == expected, result

    assert fn([], now=0) == []
    print("Q4: all tests passed")


if __name__ == "__main__":
    run_tests(referral_sla_report)
