# Does a pandera schema inferred from one clean 2,000-row sample raise false alarms on other clean samples?
import os
from pathlib import Path
SANDBOX = Path(os.environ.get("SEEDED_FAULTS_SANDBOX", Path.home() / "Projects/seeded-faults-sandbox"))
import sys, pandas as pd, pandera.pandas as pa
sb = str(SANDBOX) + "/"
sample = pd.read_csv(sb + "trips_sample.csv")
full = pd.read_parquet(sb + "yellow_2024_01.parquet")
print("full rows", len(full))
head = full.head(2000).reset_index(drop=True)
print("sample == first 2000 parquet rows (passenger_count, fare):",
      (head.passenger_count.values == sample.passenger_count.values).all(),
      (head.fare_amount.values == sample.fare_amount.values).all())
schema = pa.infer_schema(sample)
# "clean" here = rows with no missing values at all, so a null is never counted as a false alarm
pool = full.iloc[2000:].dropna()
print("complete rows available", len(pool))
for seed in range(5):
    d = pool.sample(n=2000, random_state=seed).reset_index(drop=True)
    d = d.astype({c: sample[c].dtype for c in sample.columns if str(sample[c].dtype) in ("int64","float64")}, errors="ignore")
    for c in ("tpep_pickup_datetime", "tpep_dropoff_datetime", "store_and_fwd_flag"):
        d[c] = d[c].astype(str).astype(sample[c].dtype)
    try:
        schema.validate(d, lazy=True); print(f"seed {seed}: PASS")
    except pa.errors.SchemaErrors as e:
        fc = e.failure_cases
        rows = fc["index"].dropna().nunique()
        print(f"seed {seed}: FAIL, {rows} of 2000 rows flagged;", dict(fc.groupby("column").size()))
