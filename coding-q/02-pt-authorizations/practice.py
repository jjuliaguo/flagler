"""
Coding Q2: PT Visit Authorization Tracker

Scenario
--------
Insurers often approve a limited number of physical-therapy visits within a
date range (a "prior authorization"). A visit not covered by an authorization
may not get paid. Billing wants to know how many visits are left on each
authorization, and which visits aren't covered.

Input
-----
auths:  [{"auth_id": "A1", "patient_id": "P1",
          "start": "2026-01-01", "end": "2026-01-31", "visits_allowed": 2}, ...]
        start/end are inclusive dates "YYYY-MM-DD".
visits: [{"visit_id": "v1", "patient_id": "P1", "date": "2026-01-10"}, ...]
        in NO particular order.

Rules
-----
1. Process visits in date order (ties: by visit_id).
2. A visit can use an authorization for the SAME patient whose date range
   includes the visit date and which still has visits remaining.
3. If several authorizations qualify, use the one that ENDS soonest
   (use it before it expires). Ties: smallest auth_id.
4. If none qualify, the visit is uncovered.

Output
------
(remaining, uncovered)
  remaining: {auth_id: visits_left} for EVERY auth
  uncovered: list of visit_ids not covered, in processing order
"""


def apply_visits_to_auths(auths: list[dict], visits: list[dict]) -> tuple[dict, list]:
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------- tests
def run_tests(fn):
    auths = [
        {"auth_id": "A1", "patient_id": "P1", "start": "2026-01-01", "end": "2026-01-31", "visits_allowed": 2},
        {"auth_id": "A2", "patient_id": "P1", "start": "2026-01-15", "end": "2026-03-31", "visits_allowed": 3},
        {"auth_id": "A3", "patient_id": "P2", "start": "2026-02-01", "end": "2026-02-28", "visits_allowed": 1},
    ]
    visits = [
        {"visit_id": "v4", "patient_id": "P1", "date": "2026-02-05"},
        {"visit_id": "v1", "patient_id": "P1", "date": "2026-01-10"},
        {"visit_id": "v7", "patient_id": "P2", "date": "2026-02-11"},
        {"visit_id": "v3", "patient_id": "P1", "date": "2026-01-25"},
        {"visit_id": "v8", "patient_id": "P3", "date": "2026-02-01"},
        {"visit_id": "v2", "patient_id": "P1", "date": "2026-01-20"},
        {"visit_id": "v5", "patient_id": "P1", "date": "2026-04-01"},
        {"visit_id": "v6", "patient_id": "P2", "date": "2026-02-10"},
    ]
    # v1 -> A1; v2 -> A1 (both cover, A1 ends sooner); v3 -> A2 (A1 used up)
    # v8 -> uncovered (no auth for P3); v4 -> A2; v6 -> A3; v7 -> uncovered (A3 used up)
    # v5 -> uncovered (after A2 ends)
    remaining, uncovered = fn(auths, visits)
    assert remaining == {"A1": 0, "A2": 1, "A3": 0}, remaining
    assert uncovered == ["v8", "v7", "v5"], uncovered

    # boundary: visit exactly on the end date is covered
    r, u = fn([{"auth_id": "X", "patient_id": "P", "start": "2026-05-01", "end": "2026-05-31", "visits_allowed": 1}],
              [{"visit_id": "e", "patient_id": "P", "date": "2026-05-31"}])
    assert r == {"X": 0} and u == [], (r, u)

    assert fn([], []) == ({}, [])
    print("Q2: all tests passed")


if __name__ == "__main__":
    run_tests(apply_visits_to_auths)
