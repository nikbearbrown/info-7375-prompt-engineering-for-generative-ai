# Fault Catalogue & Pre-Build Evaluation Thresholds — Seeded Faults

**Dataset:** NYC TLC Yellow Taxi Trip Records (January 2024; 2,964,624 raw rows)  
**Evaluation Holdout Slice:** 10,000-row random slice drawn from the 2,696,560 filtered rows via `pandas .sample(n=10000, random_state=42)` (never shown to Claude)  
**Prompt Sample Slice:** Separate 1,000-row sample drawn from the remaining 2,686,560 filtered rows excluding the holdout indices (`pandas .sample(n=1000, random_state=99)`), so generated bounds cannot overfit to the holdout rows used to measure false alarms  
**Injection Config:** 50 mutated rows per fault injected into isolated copies of the 10,000-row holdout slice (`random_state=42`)  
**Status:** Locked

---

## 1. Clean-Baseline Definition

- **Chosen Baseline Option:** Option A
- **Filter Rules Applied to Raw Parquet (in order):**
  1. `payment_type != 0` — removes the `140,162` raw rows where five columns are simultaneously null
  2. `fare_amount > 0` — removes `36,225` remaining rows with negative or `$0.00` fares
  3. `trip_distance > 0 AND trip_distance <= 500` — removes `33,777` remaining rows with zero distance or extreme multi-thousand-mile outliers
  4. `passenger_count >= 1 AND passenger_count <= 6` — removes `30,703` remaining rows with zero passengers or counts above 6 (my upper cutoff so valid rows aren't flagged as false alarms)
  5. `tpep_dropoff_datetime > tpep_pickup_datetime` — removes `55` remaining inverted or zero-duration rows (`870` raw rows total: `56` inverted plus `814` zero-duration, including the `23` zero-duration trips with `trip_distance > 1`)
  6. `tpep_pickup_datetime >= '2024-01-01 00:00:00' AND tpep_pickup_datetime < '2024-02-01 00:00:00'` — removes `17` remaining out-of-month pickup rows
  7. `RatecodeID IN (1, 2, 3, 4, 5, 6)` — removes `27,125` remaining rows (excluding code `99`, which is outside the 1–6 codes I'm treating as valid, so standard domain tests don't trigger baseline false alarms)
  8. `total_amount >= fare_amount` — a guard; removes `0` rows in this data
- **Post-Filter Clean Row Count:** `2,696,560`
- **Why I Chose Option A:** Stripping pre-existing dirty rows out first prevents a test from scoring a "hit" on background anomalies already sitting in the raw file, keeping the 50-row planted catch rate readable. Removing known outliers up front also gives a cleaner baseline for measuring false alarms on the unmutated holdout, though a poorly calibrated test can still flag valid rows.

---

## 2. Locked Fault List (18 Types)

Each fault below is injected into its own copy of the 10,000-row clean holdout slice (`50` rows mutated per copy, `random_state = 42`):

### Null & Missingness Faults
1. **Null `tpep_pickup_datetime` (set 50 rows to `NULL`):** Core event timestamp required for partitioning, deduplication, and trip-duration checks.
2. **Null `PULocationID` (set 50 rows to `NULL`):** Required pickup taxi-zone foreign key; missing values break spatial joins and borough aggregations.
3. **Null `fare_amount` (set 50 rows to `NULL`):** Primary revenue metric; silent nulls corrupt daily fare totals and downstream billing models.
4. **Null `payment_type` (set 50 rows to `NULL`):** Required categorical field needed to distinguish card vs. cash trips and tip-reporting behavior.

### Sign & Range Faults
5. **Negative `fare_amount` (set 50 rows to `-15.50`):** Simulates uncleaned void/refund adjustments leaking into active trip records.
6. **Zero `trip_distance` with high fare (set `trip_distance = 0.0` on 50 rows where `fare_amount > 20.00`):** Catches broken odometer/GPS logging on high-value rides (including metered and flat-rate trips) where distance failed to increment.
7. **Extreme `trip_distance` outlier (set 50 rows to `1200.0` miles):** Simulates unit-conversion or decimal-shift bugs (e.g., feet or tenths recorded as miles) that skew distance averages.
8. **Negative `passenger_count` (set 50 rows to `-1`):** Tests whether generated constraints reject a plausible negative sentinel value in an integer count column.
9. **Extreme `passenger_count` outlier (set 50 rows to `10`):** Exceeds my `1–6` baseline cutoff (`passenger_count <= 6`) to test upper-bound enforcement on group size.
10. **Negative `tip_amount` (set 50 rows to `-5.00`):** Tips cannot be negative; catches missing lower-bound checks on non-fare monetary components.

### Temporal & Ordering Faults
11. **Inverted timestamps (swap `tpep_pickup_datetime` and `tpep_dropoff_datetime` on 50 rows so drop-off precedes pick-up):** Simulates clock skew or column-mapping swaps where a trip ends before it begins.
12. **Zero-second trip duration on long ride (set `tpep_dropoff_datetime = tpep_pickup_datetime` on 50 rows where `trip_distance > 1.0`):** Physical impossibility (distance greater than 1 mile traveled in 0 seconds) caused by frozen end-of-trip timestamps.
13. **Out-of-month pickup timestamp (shift `tpep_pickup_datetime` year to `2008` on 50 rows):** Simulates uninitialized device clocks or stale records leaking into the January 2024 partition.

### Categorical & Domain-Code Faults
14. **Invalid `VendorID` (set 50 rows to `99`):** `1` and `2` are the only `VendorID` codes left in my filtered baseline; `99` tests whether generated domain tests catch an unrecognized vendor code.
15. **Invalid `RatecodeID` (set 50 rows to `7`):** Outside the `1–6` codes I'm treating as valid in the clean baseline; tests strict enum/accepted-values validation.
16. **Invalid `store_and_fwd_flag` (set 50 rows to `'X'`):** Binary flag should only contain `'Y'` or `'N'`; tests strict two-value categorical enforcement.

### Relational & Cross-Column Faults
17. **Exact duplicate trip rows (duplicate 50 existing rows verbatim into the slice):** Simulates retry/double-ingestion bugs in batch loading where identical records appear twice.
18. **`total_amount < fare_amount` mismatch (set `total_amount = fare_amount - 5.00` on 50 rows):** Violates basic accounting consistency (`total_amount` must at least cover `fare_amount` before surcharges/tips).

---

## 3. Pre-Build Evaluation Pass/Fail Thresholds

Locked **before** writing hand-written baseline tests or running Claude to generate any `dbt` tests:

- **Hand-Written Baseline Order:** I will write and commit my hand-written `dbt` test suite *before* prompting Claude to generate its tests, ensuring my baseline is unaffected by Claude's output.
- **Catch Rate (per fault type):** `>= 80%` (at least 15 of the 18 faulted dataset copies caught, where *caught* = at least one generated `dbt` test fails on that faulted copy), **and** Claude's suite must catch at least as many fault types as my hand-written baseline suite.
- **False-Alarm Rate (clean holdout):** `<= 5%` of generated `dbt` tests failing when run against the unmutated 10,000-row holdout slice (`random_state=42`).
- **Resource / Generation Cap:** Claude Code CLI (Opus 5.5, `claude-opus-5-5`), max **3 prompt turns** (1 initial schema-plus-sample prompt using the 1,000-row `random_state=99` non-holdout sample + up to 2 syntax/compile-fix turns; no iterative tuning against fault scores).
