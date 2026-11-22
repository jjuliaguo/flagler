# 7. Clinic Analytics Dashboard (solution notes)
**Emphasis:** read vs. write workloads, pre-aggregation, caching (when justified), multi-tenancy, scaling

## Answers to clarifying questions
- **Users:** clinic owners/managers. ~500 dashboard users, mostly opened in the morning.
- **Metrics:** appointments/day, no-show rate, referral → scheduled time, denial rate, by location/provider, over days/weeks/months.
- **Freshness:** hourly or daily is fine. Not real-time.
- **Data volume:** millions of appointment/claim rows over years.
- **Access:** an owner sees all their locations; a location manager sees only theirs. Never other organizations.

## Reference design
```
Operational DB (Postgres: appointments, referrals, claims)
          |  (replica or nightly/hourly ETL job)
          v
Aggregation job --> daily_metrics table (clinic_id, location_id, provider_id, date, metric values)
          |
Dashboard API --(auth: org/location scoping)--> reads daily_metrics (fast, small) --> Web UI (charts)
                    |
               optional cache (per clinic + date range, TTL ~ until next aggregation)
```
- **Don't run heavy analytics queries on the production DB** that the call center and scheduling depend on. Use a **read replica** or a separate analytics store.
- **Pre-aggregate** into daily rollups: the dashboard reads hundreds of rows instead of scanning millions. Week/month = sum of days.
- Rates are stored as numerator + denominator (no-shows, total appts), so they combine correctly across days/locations (you can't average averages).

## APIs
- `GET /orgs/{org_id}/metrics?metric=no_show_rate&from=&to=&group_by=location|provider|day`
- `GET /orgs/{org_id}/metrics/summary?period=last_30d`
- (Optional) `GET /orgs/{org_id}/exports?...` → async CSV export job

## Data
- `daily_metrics(org_id, clinic_id, location_id, provider_id, date, appts_total, appts_no_show, referrals_received, referrals_scheduled, referral_to_sched_hours_sum, claims_total, claims_denied)`
- PK/index `(org_id, date, location_id, provider_id)`
- `user_access(user_id, org_id, location_id NULL)` for scoping

## Concepts to mention (and why)
| Concept | Why |
|---|---|
| Separate read path (replica/warehouse) | analytics shouldn't slow down patient-facing operations |
| Pre-aggregation / rollups | turns slow big scans into fast small reads; fits the "hourly is fine" freshness |
| Indexes on filter columns | `org_id`, `date` drive every query |
| Caching, justified | many managers open the same dashboard at 8am, and data only changes hourly, so caching is safe. Say *what* the key and TTL are |
| Idempotent ETL | re-running a day's job overwrites that day's row (upsert), with no double counting |
| Row-level authorization | every query is filtered by the user's org/locations, enforced server-side |
| Minimize PHI | aggregates don't need patient names; reduces exposure |

## Failure modes / deep dives
1. **ETL job fails overnight** → dashboard shows "data as of yesterday 6am" + alert; job is re-runnable.
2. **Late-arriving data** (a no-show marked 2 days later) → recompute a rolling window (last 7 days) each run.
3. **One giant clinic group** → partition rollups by org or date if needed; still small after aggregation.
4. **Metric definitions disagree** with the clinic's own reports → document definitions; a single source of truth for metric logic.

## Follow-ups
1. Why not just query the appointments table directly?
2. Where would you add a cache, and when would it be wrong to?
3. How do you make sure a location manager can't see another location?
4. If they want real-time numbers later, what changes? (Streaming/incremental counters, but question whether it's really needed.)

## Rubric
- **Strong:** separates OLTP vs. analytics, pre-aggregation, correct rate math, auth scoping, a re-runnable job, a justified cache.
- **Red flags:** giant `GROUP BY` on prod for every page load; cache everything "for speed" with no invalidation thought.
