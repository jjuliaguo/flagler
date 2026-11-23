"""Fixed version of Q6. Run: py solution.py"""
from collections import defaultdict

from practice import run_tests


def to_cents(dollars):
    return round(dollars * 100)  # FIX: integer cents, no float drift


def reconcile_copays(visits, payments):
    due = {v["visit_id"]: to_cents(v["copay_due"]) for v in visits}  # FIX: lookup by id, not list membership

    paid = defaultdict(int)  # FIX: unpaid visits default to 0 (no KeyError)
    seen_payments = set()
    unmatched = []
    for p in payments:
        if p["payment_id"] in seen_payments:  # FIX: duplicate delivery counted once
            continue
        seen_payments.add(p["payment_id"])
        if p["visit_id"] not in due:
            unmatched.append(p["payment_id"])
            continue  # FIX: don't also record it as paid
        paid[p["visit_id"]] += to_cents(p["amount"])  # FIX: accumulate, don't overwrite

    balances = {}
    overpaid = []
    for visit_id, due_cents in due.items():
        owed = due_cents - paid[visit_id]
        if owed < 0:
            overpaid.append(visit_id)
        balances[visit_id] = max(owed, 0) / 100  # FIX: never negative
    return {"balances": balances, "overpaid": overpaid, "unmatched": unmatched}


if __name__ == "__main__":
    run_tests(reconcile_copays)
