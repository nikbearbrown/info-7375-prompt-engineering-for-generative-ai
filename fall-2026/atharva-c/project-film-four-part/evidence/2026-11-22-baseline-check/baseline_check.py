# Apply the Option A filters from the FAULT-CATALOGUE draft (2026-11-22) and check each planted fault is absent from clean data.
import os
from pathlib import Path
SANDBOX = Path(os.environ.get("SEEDED_FAULTS_SANDBOX", Path.home() / "Projects/seeded-faults-sandbox"))
import pandas as pd
d = pd.read_parquet(SANDBOX / "yellow_2024_01.parquet")
pu, do = d.tpep_pickup_datetime, d.tpep_dropoff_datetime
print("raw rows", len(d), "| raw dropoff <= pickup:", int((do <= pu).sum()))
rules = {
 "payment_type != 0": d.payment_type != 0,
 "fare_amount > 0": d.fare_amount > 0,
 "0 < trip_distance <= 500": (d.trip_distance > 0) & (d.trip_distance <= 500),
 "1 <= passenger_count <= 6": d.passenger_count.between(1, 6),
 "dropoff > pickup": do > pu,
 "pickup in Jan 2024": (pu >= "2024-01-01") & (pu < "2024-02-01"),
 "RatecodeID in 1..6": d.RatecodeID.isin([1, 2, 3, 4, 5, 6]),
 "total_amount >= fare_amount": d.total_amount >= d.fare_amount,
}
keep = pd.Series(True, index=d.index)
for k, m in rules.items():
    print(f"  {k:30} removes {int((keep & ~m).sum()):>8} more rows")
    keep &= m
c = d[keep]
print("POST-FILTER CLEAN ROWS", len(c))
s = c.sample(n=10_000, random_state=42)
print("10k holdout (seed 42): rows with fare > 20:", int((s.fare_amount > 20).sum()), "| rows with distance > 1:", int((s.trip_distance > 1).sum()))
print("planted values already present in clean data (should all be 0):")
for k, m in {
 "VendorID == 99": c.VendorID == 99, "RatecodeID == 7": c.RatecodeID == 7,
 "store_and_fwd == 'X'": c.store_and_fwd_flag == "X", "passenger_count == 10 or -1": c.passenger_count.isin([10, -1]),
 "trip_distance == 1200": c.trip_distance == 1200, "tip_amount < 0": c.tip_amount < 0,
 "pickup year 2008": c.tpep_pickup_datetime.dt.year == 2008, "nulls in faulted columns": c[["tpep_pickup_datetime","PULocationID","fare_amount","payment_type"]].isna().any(axis=1),
 "exact duplicates": c.duplicated(),
}.items(): print(f"  {k:30} {int(m.sum())}")
print("VendorID values left", sorted(int(v) for v in c.VendorID.unique()), "| store_and_fwd values left", sorted(c.store_and_fwd_flag.unique()))
