"""Full Mock 3 reference solutions. Run: python solution.py"""
from collections import defaultdict, deque


# Part 1 (LC 933 Number of Recent Calls): queue, amortized O(1) per call
class CallVolumeMonitor:
    def __init__(self, window_sec=60):
        self.window = window_sec
        self.calls = deque()

    def record(self, ts):
        self.calls.append(ts)
        # drop calls that fell out of [ts - window, ts]
        while self.calls[0] < ts - self.window:
            self.calls.popleft()
        return len(self.calls)


# Follow-up: per clinic, one deque per clinic
class ClinicCallVolumeMonitor:
    def __init__(self, window_sec=60):
        self.window = window_sec
        self.calls = defaultdict(deque)

    def record(self, clinic_id, ts):
        q = self.calls[clinic_id]
        q.append(ts)
        while q[0] < ts - self.window:
            q.popleft()
        return len(q)


# Part 2 (LC 20 Valid Parentheses): stack, O(n) time and space
CLOSES = {"CALL_END": "CALL_START", "HOLD_END": "HOLD_START", "TRANSFER_END": "TRANSFER_START"}


def first_invalid_event(events):
    stack = []
    for i, event in enumerate(events):
        if event == "CALL_START":
            if stack:  # calls can't be nested
                return i
            stack.append(event)
        elif event.endswith("_START"):
            if not stack:  # must be inside a call
                return i
            stack.append(event)
        elif event in CLOSES:
            if not stack or stack[-1] != CLOSES[event]:
                return i
            stack.pop()
        else:  # point event (DTMF, INTENT_DETECTED, ...)
            if not stack:
                return i
    return len(events) if stack else -1


if __name__ == "__main__":
    m = CallVolumeMonitor(60)
    assert [m.record(t) for t in (1, 30, 61, 62)] == [1, 2, 3, 3]
    m2 = CallVolumeMonitor(60)
    assert [m2.record(t) for t in (5, 5, 5)] == [1, 2, 3]  # same-second calls
    c = ClinicCallVolumeMonitor(60)
    assert c.record("A", 1) == 1 and c.record("B", 2) == 1 and c.record("A", 50) == 2

    assert first_invalid_event(["CALL_START", "HOLD_START", "HOLD_END", "CALL_END"]) == -1
    assert first_invalid_event(["CALL_START", "HOLD_START", "TRANSFER_START", "HOLD_END"]) == 3
    assert first_invalid_event(["HOLD_START"]) == 0
    assert first_invalid_event(["CALL_START", "DTMF", "HOLD_START"]) == 3
    assert first_invalid_event(["CALL_START", "CALL_START"]) == 1
    assert first_invalid_event(["CALL_END"]) == 0
    assert first_invalid_event([]) == -1
    assert first_invalid_event(["CALL_START", "CALL_END", "CALL_START", "CALL_END"]) == -1
    assert first_invalid_event(["CALL_START", "CALL_END", "DTMF"]) == 2
    print("mock 3: all tests passed")
