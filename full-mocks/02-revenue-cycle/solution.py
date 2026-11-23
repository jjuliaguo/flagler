"""Full Mock 2 reference solutions. Run: python solution.py"""
from collections import Counter
import heapq


# Part 1 (LC 347 Top K Frequent): count, then sort. O(n + u log u), u = distinct codes
def top_denial_reasons(denials, k):
    counts = Counter(d["reason_code"] for d in denials)
    # tie-break alphabetically so output is deterministic
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [code for code, _ in ranked[:k]]


# Alternative: heap, O(n + u log k). Worth mentioning when u is large and k is small.
def top_denial_reasons_heap(denials, k):
    counts = Counter(d["reason_code"] for d in denials)
    return [code for code, _ in heapq.nsmallest(k, counts.items(), key=lambda it: (-it[1], it[0]))]


# Follow-up the interviewer may add: the same claim re-denied for the same reason
# (e.g. resubmitted and denied again) should count once.
def top_denial_reasons_dedup(denials, k):
    unique = {(d["claim_id"], d["reason_code"]) for d in denials}
    counts = Counter(code for _, code in unique)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [code for code, _ in ranked[:k]]


# Part 2 (LC 560 Subarray Sum Equals K): prefix sums + hash map, O(n) time and space.
# A sliding window does NOT work, because negative numbers (take-backs) break it.
def count_matching_periods(daily_net, target):
    seen = {0: 1}  # prefix sum -> how many times we've seen it (empty prefix = 0)
    running = 0
    total = 0
    for amount in daily_net:
        running += amount
        # a run ending today sums to target  <=>  some earlier prefix == running - target
        total += seen.get(running - target, 0)
        seen[running] = seen.get(running, 0) + 1
    return total


# Follow-up: (start, end) of the matching run that ends earliest
def first_matching_period(daily_net, target):
    first_index = {0: -1}  # prefix sum -> first index where it occurred
    running = 0
    for i, amount in enumerate(daily_net):
        running += amount
        if running - target in first_index:
            return (first_index[running - target] + 1, i)
        first_index.setdefault(running, i)
    return None


if __name__ == "__main__":
    denials = (
        [{"claim_id": f"C{i}", "payer": "Aetna", "reason_code": "CO-16"} for i in range(3)]
        + [{"claim_id": f"D{i}", "payer": "BCBS", "reason_code": "CO-97"} for i in range(2)]
        + [{"claim_id": f"E{i}", "payer": "UHC", "reason_code": "PR-1"} for i in range(2)]
        + [{"claim_id": "F0", "payer": "UHC", "reason_code": "CO-50"}]
    )
    assert top_denial_reasons(denials, 2) == ["CO-16", "CO-97"]
    assert top_denial_reasons_heap(denials, 2) == ["CO-16", "CO-97"]
    assert top_denial_reasons([], 3) == []
    assert top_denial_reasons(denials, 10) == ["CO-16", "CO-97", "PR-1", "CO-50"]
    dup = denials + [{"claim_id": "F0", "payer": "UHC", "reason_code": "CO-50"}] * 5
    assert top_denial_reasons(dup, 1) == ["CO-50"]
    assert top_denial_reasons_dedup(dup, 1) == ["CO-16"]

    assert count_matching_periods([100, 200, -100, 300, 100], 300) == 3
    assert count_matching_periods([], 300) == 0
    assert count_matching_periods([0, 0], 0) == 3
    assert count_matching_periods([100, -100, 100], 100) == 3
    assert first_matching_period([100, 200, -100, 300, 100], 300) == (0, 1)
    assert first_matching_period([50, 50], 300) is None
    print("mock 2: all tests passed")
