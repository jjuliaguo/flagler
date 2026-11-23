"""
Coding Q6 (DEBUG): Copay Reconciliation

Scenario
--------
At the end of the day, the front desk reconciles copays: for each visit, how
much is still owed? A teammate wrote the function below. It "works on my
machine," but the tests fail.

Your job (talk through it out loud):
  1. Explain what the function is SUPPOSED to do.
  2. Before running anything, predict what goes wrong with the test data.
  3. Find and fix the bugs. Rank them by how bad they'd be in production.

Requirements
------------
visits:   [{"visit_id": "V1", "patient_id": "P1", "copay_due": 30.30}, ...]
payments: [{"payment_id": "p1", "visit_id": "V1", "amount": 10.10}, ...]
  - a visit can have SEVERAL payments
  - the same payment can be delivered twice (same payment_id): count it once
  - a payment can reference an unknown visit: report it as unmatched
Return:
  {"balances":  {visit_id: amount still owed, never negative, rounded to cents},
   "overpaid":  [visit_ids where payments exceeded copay_due],
   "unmatched": [payment_ids referencing unknown visits]}
Every visit must appear in balances, even if it has no payments.
"""


def reconcile_copays(visits, payments):
    paid = {}
    unmatched = []
    for p in payments:
        if p["visit_id"] not in visits:
            unmatched.append(p["payment_id"])
        paid[p["visit_id"]] = p["amount"]

    balances = {}
    overpaid = []
    for v in visits:
        owed = v["copay_due"] - paid[v["visit_id"]]
        if owed < 0:
            overpaid.append(v["visit_id"])
        balances[v["visit_id"]] = owed

    return {"balances": balances, "overpaid": overpaid, "unmatched": unmatched}


# ---------------------------------------------------------------- tests
def run_tests(fn):
    visits = [
        {"visit_id": "V1", "patient_id": "P1", "copay_due": 30.30},
        {"visit_id": "V2", "patient_id": "P2", "copay_due": 25.00},
        {"visit_id": "V3", "patient_id": "P3", "copay_due": 40.00},
    ]
    payments = [
        {"payment_id": "p1", "visit_id": "V1", "amount": 10.10},
        {"payment_id": "p2", "visit_id": "V1", "amount": 20.20},
        {"payment_id": "p3", "visit_id": "V2", "amount": 30.00},
        {"payment_id": "p3", "visit_id": "V2", "amount": 30.00},  # duplicate delivery
        {"payment_id": "p4", "visit_id": "V9", "amount": 15.00},  # unknown visit
    ]
    result = fn(visits, payments)
    assert result == {
        "balances": {"V1": 0.0, "V2": 0.0, "V3": 40.0},
        "overpaid": ["V2"],
        "unmatched": ["p4"],
    }, result
    assert fn([], []) == {"balances": {}, "overpaid": [], "unmatched": []}
    print("Q6: all tests passed")


if __name__ == "__main__":
    run_tests(reconcile_copays)
