# Full Mock 3: AI Call Center

## Part A: Live coding (~30 min)

### Part 1: Call volume monitor
The AI phone line sends us an event every time a patient call comes in. To decide when to route overflow to backup human staff, we need to know **how many calls arrived in the last 60 seconds**.

```python
class CallVolumeMonitor:
    def __init__(self, window_sec: int = 60): ...
    def record(self, ts: int) -> int:
        """Record a call at time ts (seconds). Return the number of calls
        in the window [ts - window_sec, ts], inclusive."""
```
Timestamps passed to `record` are **non-decreasing**.

**Example**
```
m = CallVolumeMonitor(60)
m.record(1)  -> 1
m.record(30) -> 2
m.record(61) -> 3
m.record(62) -> 3
```

### Part 2: Validate a call's event log
Each call produces a log of events. Some events come in START/END pairs:
`CALL_START/CALL_END`, `HOLD_START/HOLD_END`, `TRANSFER_START/TRANSFER_END`.
Other events (like `DTMF`, `INTENT_DETECTED`) are single points in time.

A valid log:
- Every pair is **properly nested** and closed (you can't end a hold while a transfer started inside it is still open).
- Everything happens **inside a call**. Calls can't be nested inside each other, but one log can hold several calls in a row.

Return the **index of the first invalid event**: the event that breaks a rule, or `len(events)` if the log ends with something still open. Return `-1` if the log is valid.
```python
def first_invalid_event(events: list[str]) -> int:
    ...
```
**Examples**
```
["CALL_START", "HOLD_START", "HOLD_END", "CALL_END"]                -> -1
["CALL_START", "HOLD_START", "TRANSFER_START", "HOLD_END"]           -> 3
["HOLD_START"]                                                      -> 0
["CALL_START", "DTMF", "HOLD_START"]                                -> 3
```

### Follow-up (if time)
Volume is now tracked **per clinic**: `record(clinic_id, ts)`. What changes?

---

## Part B: System design (~20–25 min)

> Design the backend for an **AI phone agent** that answers a clinic's calls and can **schedule, reschedule, or cancel** appointments. When the AI can't handle something (an upset patient, a clinical question, low confidence), it should **hand the call off to a human** at the clinic with context. Clinics want transcripts and a record of what the AI did.
