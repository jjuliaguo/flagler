# Full Mock 5: Patient Engagement

## Part A: Live coding (~30 min)

### Part 1: Conversation state store (no built-in dict)
Our SMS assistant has multi-step conversations ("Which day works? → Which time? → Confirm?"). For each phone number we need to remember **where the conversation is**. Abandoned conversations should **expire after `ttl_sec` seconds** with no new message.

Implement it **without using Python's `dict` or `set`**. Build the hash table yourself.
```python
class ConversationStore:
    def __init__(self, ttl_sec: int, capacity: int = 16): ...
    def put(self, phone: str, state: dict, now: int) -> None:
        """Insert or update. Resets the expiry to now + ttl_sec."""
    def get(self, phone: str, now: int) -> dict | None:
        """Return the state, or None if missing or expired."""
    def remove(self, phone: str) -> bool:
        """Delete. Return True if it existed."""
```
**Example**
```
s = ConversationStore(ttl_sec=600)
s.put("+15551234", {"step": "ASK_DATE"}, now=0)
s.get("+15551234", now=100)  -> {"step": "ASK_DATE"}
s.put("+15551234", {"step": "CONFIRM"}, now=200)
s.get("+15551234", now=700)  -> {"step": "CONFIRM"}
s.get("+15551234", now=800)  -> None
```

### Part 2: Longest varied exercise streak
Physical therapists want patients to rotate through their home exercises. Each day the patient logs the one exercise they did. Find the **longest run of consecutive days with no exercise repeated**.
```python
def longest_varied_streak(days: list[str]) -> int:
    ...
```
**Example**
```
["squat", "bridge", "clam", "squat", "plank", "bridge"]  ->  4
# "bridge, clam, squat, plank" or "clam, squat, plank, bridge"
```
**Follow-up:** a `None` entry means the patient **missed** that day, which breaks the streak.

---

## Part B: System design (~20–25 min)

> Design the backend for a **two-way SMS assistant** that patients can text to **reschedule or cancel** appointments or ask simple questions ("What's the clinic address?"). Conversations take several messages, patients may reply hours later, and anything the assistant can't handle should go to clinic staff.
