"""Reference solution for Q1. Run: py solution.py"""
from collections import defaultdict

from practice import run_tests

FEES = {"NO_SHOW": 50, "LATE_CANCEL": 25}
MONTHLY_CAP = 100


def compute_no_show_fees(events):
    # 1) one record per appointment, keeping the more expensive type
    by_appt = {}
    for e in events:
        fee = FEES[e["type"]]
        current = by_appt.get(e["appt_id"])
        if current is None or fee > current[2]:
            by_appt[e["appt_id"]] = (e["patient_id"], e["date"], fee)

    # 2) process each patient's appointments in date order.
    #    Same date -> more expensive first, so the waiver hits the bigger fee.
    ordered = sorted(by_appt.values(), key=lambda r: (r[0], r[1], -r[2]))

    waived_years = set()             # (patient, year)
    month_totals = defaultdict(int)  # (patient, "YYYY-MM") -> charged so far
    owed = defaultdict(int)
    for patient, date, fee in ordered:
        year, month = date[:4], date[:7]
        if (patient, year) not in waived_years:
            waived_years.add((patient, year))
            continue
        charge = min(fee, MONTHLY_CAP - month_totals[(patient, month)])
        if charge > 0:
            month_totals[(patient, month)] += charge
            owed[patient] += charge

    return {p: amt for p, amt in owed.items() if amt > 0}


if __name__ == "__main__":
    run_tests(compute_no_show_fees)
