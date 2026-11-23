"""Full Mock 5 reference solutions. Run: python solution.py"""


# Part 1 (LC 706 Design HashMap + TTL): separate chaining.
# Average O(1) put/get/remove; worst case O(n) if everything lands in one bucket.
class ConversationStore:
    LOAD_FACTOR = 0.75

    def __init__(self, ttl_sec, capacity=16):
        self.ttl = ttl_sec
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def _bucket(self, key):
        return self.buckets[hash(key) % len(self.buckets)]

    def put(self, key, state, now):
        bucket = self._bucket(key)
        for entry in bucket:
            if entry[0] == key:  # update existing (even if expired) and refresh TTL
                entry[1] = state
                entry[2] = now + self.ttl
                return
        bucket.append([key, state, now + self.ttl])  # [key, value, expires_at]
        self.size += 1
        if self.size > self.LOAD_FACTOR * len(self.buckets):
            self._resize()

    def get(self, key, now):
        bucket = self._bucket(key)
        for i, entry in enumerate(bucket):
            if entry[0] == key:
                if entry[2] <= now:  # lazy expiry: clean up when we touch it
                    bucket.pop(i)
                    self.size -= 1
                    return None
                return entry[1]
        return None

    def remove(self, key):
        bucket = self._bucket(key)
        for i, entry in enumerate(bucket):
            if entry[0] == key:
                bucket.pop(i)
                self.size -= 1
                return True
        return False

    def _resize(self):
        old = self.buckets
        self.buckets = [[] for _ in range(2 * len(old))]
        for bucket in old:
            for entry in bucket:
                self._bucket(entry[0]).append(entry)  # rehash: index depends on len


# Part 2 (LC 3 Longest Substring w/o Repeating): sliding window, O(n) time
def longest_varied_streak(days):
    last_index = {}
    start = 0  # left edge of the current window
    best = 0
    for i, exercise in enumerate(days):
        if exercise is None:  # follow-up: missed day breaks the streak
            start = i + 1
            continue
        if exercise in last_index and last_index[exercise] >= start:
            start = last_index[exercise] + 1  # jump past the earlier copy
        last_index[exercise] = i
        best = max(best, i - start + 1)
    return best


if __name__ == "__main__":
    s = ConversationStore(ttl_sec=600)
    s.put("+15551234", {"step": "ASK_DATE"}, now=0)
    assert s.get("+15551234", now=100) == {"step": "ASK_DATE"}
    s.put("+15551234", {"step": "CONFIRM"}, now=200)
    assert s.get("+15551234", now=700) == {"step": "CONFIRM"}
    assert s.get("+15551234", now=800) is None
    assert s.get("+10000000", now=0) is None

    small = ConversationStore(ttl_sec=100, capacity=2)
    for n in range(50):  # forces several resizes
        small.put(f"+1555{n:04d}", {"n": n}, now=0)
    assert all(small.get(f"+1555{n:04d}", now=1) == {"n": n} for n in range(50))
    assert len(small.buckets) >= 64
    assert small.remove("+15550007") is True and small.remove("+15550007") is False
    assert small.get("+15550007", now=1) is None

    assert longest_varied_streak(["squat", "bridge", "clam", "squat", "plank", "bridge"]) == 4
    assert longest_varied_streak([]) == 0
    assert longest_varied_streak(["a", "a", "a"]) == 1
    assert longest_varied_streak(["a", "b", "a", "c", "b"]) == 3  # trap: "a b a" must not reset to 0
    assert longest_varied_streak(["a", "b", "c", "a", "d", "b"]) == 4  # stale-index check
    assert longest_varied_streak(["a", "b", None, "c", "d", "e", "c"]) == 3
    print("mock 5: all tests passed")
