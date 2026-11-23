"""Reference solution for Q4. Run: py solution.py"""
from practice import run_tests


def referral_sla_report(referrals, now, sla_hours=48):
    stats = {}  # clinic -> running totals
    for r in referrals:
        received, scheduled = r["received_at"], r["scheduled_at"]
        if scheduled is not None and scheduled < received:
            continue  # bad data; in production: log it

        s = stats.setdefault(r["clinic"], {"total": 0, "scheduled": 0, "hours_sum": 0, "breaches": 0})
        s["total"] += 1
        if scheduled is not None:
            wait = scheduled - received
            s["scheduled"] += 1
            s["hours_sum"] += wait
        else:
            wait = now - received
        if wait > sla_hours:
            s["breaches"] += 1

    report = []
    for clinic, s in stats.items():
        avg = round(s["hours_sum"] / s["scheduled"], 1) if s["scheduled"] else None
        report.append({"clinic": clinic, "total": s["total"], "scheduled": s["scheduled"],
                       "avg_hours": avg, "breaches": s["breaches"]})
    report.sort(key=lambda row: (-row["breaches"], row["clinic"]))
    return report


if __name__ == "__main__":
    run_tests(referral_sla_report)
