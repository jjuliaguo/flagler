# Q3 Notes: Out-of-Order EMR Events

## Clarifying questions a strong candidate asks
- Is `version` per appointment or global? *(Per appointment.)*
- Same version, different event_id: which wins? *(The first applied. The later one is ignored as a conflict.)* Say you'd **log it**, because it signals an upstream bug.
- Canceled with no start: what start do we show? *(Keep the previous one, or None if unknown.)*
- Can a CANCELED appointment be un-canceled by a newer RESCHEDULED? *(Yes, the higher version wins. Worth asking.)*

## Approach
- `seen_event_ids` set → exact duplicates (**idempotency**).
- `state[appt_id]` holds the latest applied version → **ignore stale or out-of-order events** (`<=`).
- Apply the event by type. A CANCELED event with no start inherits the previous start.

**Complexity:** O(n) time, O(n) space.

## Why two different checks?
- `event_id` catches the **same event delivered twice** (a webhook retry).
- `version` catches **different events arriving in the wrong order**.
They solve different problems, and strong candidates explain both.

## Common mistakes
- Only deduping on event_id → the late v2 overwrites v3, so a canceled appointment shows as booked (a patient might show up for a canceled visit).
- `<` instead of `<=` → a same-version conflict overwrites.
- Overwriting `start` with None on cancel.
- Assuming CREATED always arrives first → KeyError when a RESCHEDULED event comes first.

## Follow-ups
- "Memory: `seen_event_ids` grows forever." → store it in the DB with a unique constraint, or expire IDs older than the provider's retry window (e.g. 3 days). The version check alone already makes reapplying safe.
- "Run this across 5 workers." → in-memory state breaks, so put the state in the DB: `UPDATE appointments SET ... WHERE appt_id = ? AND version < ?` (an atomic conditional update).
- "What if the EMR doesn't send versions?" → use `updated_at` timestamps (watch for clock skew), or re-fetch the record from the EMR API on every event.
- "Return a count of ignored events by reason." → good for monitoring integration health.

## Strong answer sounds like
"Webhooks are at-least-once and unordered, so I need two guards: event_id dedupe for exact repeats, and a version check so stale updates can't overwrite newer state. In production that version check becomes a conditional UPDATE in the database."
