# Full Mock 1: Provider Scheduling

## Part A: Live coding (~30 min)

### Context
A physical therapist's calendar is built from several sources: EMR appointments, blocked admin time, team meetings, and lunch. These blocks come in **unsorted** and often **overlap**. Before our AI scheduler can offer times to a patient, it needs a clean view of when the provider is busy.

Times are **minutes from midnight** (e.g. `540` = 9:00am). Each block is `(start, end)` with `start < end`.

### Part 1: Merge busy blocks
```python
def merge_busy_blocks(blocks: list[tuple[int, int]]) -> list[tuple[int, int]]:
    ...
```
Return the provider's busy time as a sorted list of non-overlapping blocks.

**Example**
```
Input:  [(600, 660), (540, 600), (720, 750), (630, 700)]
Output: [(540, 700), (720, 750)]
```

### Part 2: Add a new block
The schedule is now **already merged and sorted**. A front-desk user adds a new block (e.g. an appointment or blocked time). Return the updated schedule, still sorted and non-overlapping.
```python
def add_block(schedule: list[tuple[int, int]], new: tuple[int, int]) -> list[tuple[int, int]]:
    ...
```
**Example**
```
schedule = [(540, 600), (660, 720), (780, 840)]
new      = (590, 670)
Output:    [(540, 720), (780, 840)]
```

### Stretch (if time)
Given the merged schedule, the clinic's hours, and an appointment length, return every open gap long enough to book.
```python
def find_open_slots(schedule, day_start: int, day_end: int, duration: int) -> list[tuple[int, int]]:
    ...
```
```
find_open_slots([(540, 700), (720, 750)], 480, 1020, 30)
-> [(480, 540), (750, 1020)]
```

---

## Part B: System design (~20–25 min)

> Patients can now **book their own appointments**, either by tapping a link in a text message or by talking to our AI phone agent. They pick from open times for the right provider and visit type. The clinic's **EMR remains the source of truth** for the schedule, and staff are booking in the EMR at the same time. Design the backend that shows patients available times and books them, **without double-booking**.
