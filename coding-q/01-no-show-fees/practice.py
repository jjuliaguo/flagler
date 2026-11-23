"""
Coding Q1: No-Show Fee Calculator

Scenario
--------
A PT clinic charges patients for missed appointments. At the end of each
month the front desk needs to know how much each patient owes. Your job is to
apply the clinic's fee policy to a list of missed-appointment events.

Input
-----
events: list of dicts, in NO particular order:
    {"patient_id": "P1", "appt_id": "a1", "type": "NO_SHOW", "date": "2026-01-05"}
    type is "NO_SHOW" or "LATE_CANCEL". date is "YYYY-MM-DD".

Policy
------
1. Fees: NO_SHOW = $50, LATE_CANCEL = $25.
2. The EMR sometimes sends conflicting updates for the SAME appt_id
   (e.g. first LATE_CANCEL, then NO_SHOW). Count each appointment once,
   using the more expensive type.
3. Courtesy waiver: each patient's FIRST chargeable appointment in each
   calendar year is free. If two appointments tie on that first date,
   waive the more expensive one.
4. Monthly cap: a patient is never charged more than $100 in one calendar
   month. Charges apply in date order; once the cap is hit, later charges
   that month are reduced or dropped.

Output
------
dict {patient_id: total_dollars_owed}, including ONLY patients who owe > 0.

Example
-------
P1: no-show Jan 5 (waived, first of year), no-show Jan 10 ($50),
    late-cancel Jan 20 ($25), no-show Jan 25 ($25, cap reached), no-show Feb 2 ($50)
    -> P1 owes 150
"""


def compute_no_show_fees(events: list[dict]) -> dict[str, int]:
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------- tests
def run_tests(fn):
    events = [
        {"patient_id": "P1", "appt_id": "a4", "type": "NO_SHOW", "date": "2026-01-25"},
        {"patient_id": "P2", "appt_id": "b1", "type": "LATE_CANCEL", "date": "2026-03-01"},
        {"patient_id": "P1", "appt_id": "a1", "type": "NO_SHOW", "date": "2026-01-05"},
        {"patient_id": "P3", "appt_id": "c2", "type": "NO_SHOW", "date": "2026-01-02"},
        {"patient_id": "P1", "appt_id": "a5", "type": "NO_SHOW", "date": "2026-02-02"},
        {"patient_id": "P1", "appt_id": "a2", "type": "NO_SHOW", "date": "2026-01-10"},
        {"patient_id": "P2", "appt_id": "b1", "type": "NO_SHOW", "date": "2026-03-01"},
        {"patient_id": "P1", "appt_id": "a3", "type": "LATE_CANCEL", "date": "2026-01-20"},
        {"patient_id": "P3", "appt_id": "c1", "type": "NO_SHOW", "date": "2025-12-30"},
        {"patient_id": "P2", "appt_id": "b2", "type": "LATE_CANCEL", "date": "2026-03-05"},
    ]
    # P1: 0 + 50 + 25 + 25 (capped) + 50 = 150
    # P2: b1 counted once as NO_SHOW and waived; b2 = 25
    # P3: one waiver in 2025, one in 2026 -> owes nothing, not in output
    assert fn(events) == {"P1": 150, "P2": 25}, fn(events)

    # tie on the first date -> waive the more expensive one
    tie = [
        {"patient_id": "P4", "appt_id": "d1", "type": "LATE_CANCEL", "date": "2026-04-01"},
        {"patient_id": "P4", "appt_id": "d2", "type": "NO_SHOW", "date": "2026-04-01"},
    ]
    assert fn(tie) == {"P4": 25}, fn(tie)

    assert fn([]) == {}
    print("Q1: all tests passed")


if __name__ == "__main__":
    run_tests(compute_no_show_fees)
