"""Reference solution for Q2. Run: py solution.py"""
from collections import defaultdict

from practice import run_tests


def apply_visits_to_auths(auths, visits):
    remaining = {a["auth_id"]: a["visits_allowed"] for a in auths}

    # group auths by patient, pre-sorted by (end, auth_id) -> first match is the best one
    by_patient = defaultdict(list)
    for a in sorted(auths, key=lambda a: (a["end"], a["auth_id"])):
        by_patient[a["patient_id"]].append(a)

    uncovered = []
    for v in sorted(visits, key=lambda v: (v["date"], v["visit_id"])):
        for a in by_patient[v["patient_id"]]:
            if a["start"] <= v["date"] <= a["end"] and remaining[a["auth_id"]] > 0:
                remaining[a["auth_id"]] -= 1
                break
        else:  # no break -> nothing qualified
            uncovered.append(v["visit_id"])

    return remaining, uncovered


if __name__ == "__main__":
    run_tests(apply_visits_to_auths)
