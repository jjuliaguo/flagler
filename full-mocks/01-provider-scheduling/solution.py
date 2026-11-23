"""Full Mock 1 reference solutions. Run: python solution.py"""


# Part 1 (LC 56 Merge Intervals): O(n log n) time, O(n) space
def merge_busy_blocks(blocks):
    if not blocks:
        return []
    blocks = sorted(blocks)  # sort by start; don't mutate the caller's list
    merged = [list(blocks[0])]
    for start, end in blocks[1:]:
        last = merged[-1]
        if start <= last[1]:  # overlap or touching -> one continuous busy block
            last[1] = max(last[1], end)  # max() handles a block fully inside another
        else:
            merged.append([start, end])
    return [tuple(b) for b in merged]


# Part 2 (LC 57 Insert Interval): O(n) time, schedule is already sorted + merged
def add_block(schedule, new):
    start, end = new
    result = []
    i, n = 0, len(schedule)
    # 1) blocks that end before the new one starts
    while i < n and schedule[i][1] < start:
        result.append(schedule[i])
        i += 1
    # 2) blocks that overlap/touch the new one -> absorb them
    while i < n and schedule[i][0] <= end:
        start = min(start, schedule[i][0])
        end = max(end, schedule[i][1])
        i += 1
    result.append((start, end))
    # 3) everything after
    result.extend(schedule[i:])
    return result


# Stretch: open gaps inside clinic hours, O(n)
def find_open_slots(schedule, day_start, day_end, duration):
    slots = []
    cursor = day_start
    for start, end in schedule:
        # clip each block to clinic hours
        start = min(max(start, day_start), day_end)
        end = min(max(end, day_start), day_end)
        if start - cursor >= duration:
            slots.append((cursor, start))
        cursor = max(cursor, end)
    if day_end - cursor >= duration:
        slots.append((cursor, day_end))
    return slots


if __name__ == "__main__":
    assert merge_busy_blocks([(600, 660), (540, 600), (720, 750), (630, 700)]) == [(540, 700), (720, 750)]
    assert merge_busy_blocks([]) == []
    assert merge_busy_blocks([(540, 720), (600, 630)]) == [(540, 720)]  # contained
    assert merge_busy_blocks([(540, 600), (600, 660)]) == [(540, 660)]  # touching

    assert add_block([(540, 600), (660, 720), (780, 840)], (590, 670)) == [(540, 720), (780, 840)]
    assert add_block([], (1, 2)) == [(1, 2)]
    assert add_block([(10, 20)], (30, 40)) == [(10, 20), (30, 40)]
    assert add_block([(30, 40)], (10, 20)) == [(10, 20), (30, 40)]
    assert add_block([(10, 20)], (20, 30)) == [(10, 30)]
    assert add_block([(10, 20), (30, 40)], (0, 100)) == [(0, 100)]

    assert find_open_slots([(540, 700), (720, 750)], 480, 1020, 30) == [(480, 540), (750, 1020)]
    assert find_open_slots([], 480, 1020, 30) == [(480, 1020)]
    assert find_open_slots([(400, 1100)], 480, 1020, 30) == []
    assert find_open_slots([(1030, 1100)], 480, 1020, 30) == [(480, 1020)]  # block after hours
    print("mock 1: all tests passed")
