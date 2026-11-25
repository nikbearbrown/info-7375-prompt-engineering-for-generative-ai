# Fault catalogue: CANDIDATES (not the locked catalogue)

**Drafted by Claude Code on 2026-11-22. These are suggestions, not decisions.**
Your TA's next step is to write the catalogue (15–20 types) and commit it, dated, before any test is generated. The locked file should be `FAULT-CATALOGUE.md`, with **your** choices and **your** one-line reason for each. Use this list as raw material: cut, merge, rename, or add your own. Credit it in SOURCES.md as "Claude proposed candidates; I chose and wrote the catalogue."

The base rates come from `evidence/2026-11-22-data-profile/output.txt`, a profile of all 2,964,624 rows of NYC TLC yellow taxi data for January 2024 (run by Claude).

## Decide this first: what counts as "clean"?

Several of these faults **already occur in the real data**. If you plant a negative fare into a table that already has 37,448 of them, a test that flags negative fares will "fail" on your clean copy too. Choose one option and write it at the top of `FAULT-CATALOGUE.md`:

- **A. Filtered clean baseline:** clean = rows that pass a written list of rules (for example fare ≥ 0, distance > 0, no null block). Simple, but you are defining clean yourself.
- **B. Keep the data as it is:** score faults by the *increase* in flagged rows over the unmodified sample. More realistic, but harder to explain.
- **C. Drop the faults that already occur** from the catalogue and keep only ones with a ~0% base rate.

The pitch didn't face this. It belongs in the Methods part of the film.

## Candidates

Base rate = how often this already happens in the real January 2024 data.

| # | Fault | How it would be planted | Base rate in real data | Notes |
|---|---|---|---|---|
| 1 | Missing `passenger_count` | blank N random rows | 4.73% (as part of the null block) | The October fault. The real nulls come as a block (see #2). |
| 2 | Null block | blank 5 columns together and set `payment_type=0` | 140,162 rows (4.73%), all with `payment_type=0` | A real pattern. Possibly a data-source quirk worth reading about first. |
| 3 | Missing pick-up time | blank `tpep_pickup_datetime` | 0 | Breaks every time-based check |
| 4 | Drop-off before pick-up | swap the two timestamps | 56 rows | |
| 5 | Zero-length trip | set drop-off = pick-up | 814 rows | |
| 6 | Trip longer than 24 h | push drop-off forward by days | 16 rows | |
| 7 | Pick-up outside the file's month | shift the date to 2023 or March | 18 rows | Good "wrong partition" fault |
| 8 | Negative fare | flip the sign of `fare_amount` | **37,448 (1.26%)** | Needs the clean-baseline decision |
| 9 | Negative tip | flip the sign of `tip_amount` | 102 rows | |
| 10 | Zero distance with a fare | set `trip_distance=0` | **60,371 (2.04%)** | Needs the clean-baseline decision |
| 11 | Absurd distance | set `trip_distance` to 500+ | 59 rows over 100 | |
| 12 | Zero passengers | set `passenger_count=0` | **31,465 (1.06%)** | Needs the clean-baseline decision |
| 13 | Too many passengers | set `passenger_count` to 9 | 60 rows over 6 | |
| 14 | Unknown vendor | set `VendorID` to 5 | real values seen: 1, 2, 6 | Check what 6 means in the TLC data dictionary before deciding what's "valid" |
| 15 | Invalid rate code | set `RatecodeID` to 7 | 1–6 and 99 seen | Check what 99 means in the dictionary |
| 16 | Invalid payment type | set `payment_type` to 9 | 0–4 seen | 0 appears only in the null block |
| 17 | Location ID out of zone range | set `PULocationID` to 300 | 0 (range 1–265) | Referential: needs the zone lookup table |
| 18 | Exact duplicate trip | copy N rows | 0 | Clean on this one, so it's a sharp test |
| 19 | Near-duplicate trip | copy rows and change one cent | 0 on the trip key | Tests whether the key is defined well |
| 20 | Unit error | multiply `trip_distance` by 1.609 (km) | n/a | A subtle distribution shift. Many tests will miss it, which is the point. |
| 21 | Column swap | swap `fare_amount` and `tip_amount` | n/a | A subtle fault |
| 22 | Truncated load | delete 30% of rows | n/a | Only a row-count or freshness test catches it |

**Left out on purpose:** "total_amount ≠ sum of parts". My profile found 761,838 rows (25.7%) where the sum doesn't match, which more likely means my formula is missing a fee than that a quarter of the data is wrong. Don't use it until you've read the TLC data dictionary and understood the formula.

## Before you lock it
- Pick 15–20 and write *why* each one is in, in your own words.
- Write the clean-baseline choice (A, B or C).
- Commit it **before** Claude generates any test. The commit date is the proof your TA asked for.
