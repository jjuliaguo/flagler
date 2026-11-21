from datetime import datetime

REFERENCE_RANGES = {
    "glucose": (70, 99),
    "potassium": (3.5, 5.0),
    "hemoglobin": (12.0, 17.5),
}


def summarize_labs(results, flagged=[]):
    """
    results: list of dicts like
      {"patient_id": "P1", "test": "glucose", "value": 105,
       "taken_at": "2026-11-01T08:30:00"}

    Returns a dict keyed by patient_id with each patient's latest value per
    test, the tests that came back abnormal, and the average value per test.
    """
    summary = {}
    for r in results:
        pid = r["patient_id"]
        test = r["test"].lower()
        value = r["value"]
        taken_at = datetime.fromisoformat(r["taken_at"])

        if pid not in summary:
            summary[pid] = {"latest": {}, "abnormal": flagged, "totals": {}}
        patient = summary[pid]

        prev = patient["latest"].get(test)
        if prev is None or taken_at > prev[1]:
            patient["latest"][test] = (value, taken_at)

        low, high = REFERENCE_RANGES[test]
        if value < low or value > high:
            patient["abnormal"].append(test)

        patient["totals"][test] = patient["totals"].get(test, 0) + value

    for pid, patient in summary.items():
        count = len(patient["latest"])
        patient["averages"] = {
            t: total / count for t, total in patient["totals"].items()
        }
    return summary
