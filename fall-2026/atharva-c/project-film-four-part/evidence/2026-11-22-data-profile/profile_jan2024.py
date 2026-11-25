# Base rates of candidate "faults" that already exist in the real NYC TLC yellow-taxi data, January 2024.
import os
from pathlib import Path
SANDBOX = Path(os.environ.get("SEEDED_FAULTS_SANDBOX", Path.home() / "Projects/seeded-faults-sandbox"))
import pandas as pd
d = pd.read_parquet(SANDBOX / "yellow_2024_01.parquet")
n = len(d); p = lambda m: f"{int(m.sum()):>8} ({m.mean()*100:.2f}%)"
print("rows", n)
print("nulls per col:"); nn = d.isna().sum(); print(nn[nn > 0].to_string())
nullblock = d[["passenger_count","RatecodeID","store_and_fwd_flag","congestion_surcharge","Airport_fee"]].isna().all(axis=1)
print("rows where all 5 of those are null together", p(nullblock), "| of those, payment_type==0:", int((d.payment_type[nullblock]==0).sum()))
pu, do = d.tpep_pickup_datetime, d.tpep_dropoff_datetime
print("dropoff < pickup", p(do < pu)); print("dropoff == pickup", p(do == pu))
print("pickup outside Jan 2024", p((pu < "2024-01-01") | (pu >= "2024-02-01")))
print("trip > 24h", p((do - pu) > pd.Timedelta(hours=24)))
for c in ["fare_amount","total_amount","tip_amount","trip_distance","extra","tolls_amount"]: print(f"{c} < 0", p(d[c] < 0))
print("trip_distance == 0", p(d.trip_distance == 0)); print("trip_distance > 100", p(d.trip_distance > 100))
print("passenger_count == 0", p(d.passenger_count == 0)); print("passenger_count > 6", p(d.passenger_count > 6))
print("VendorID values", sorted(int(v) for v in d.VendorID.unique()))
print("RatecodeID values", d.RatecodeID.value_counts(dropna=False).to_dict())
print("payment_type values", d.payment_type.value_counts().to_dict())
print("PULocationID range", d.PULocationID.min(), d.PULocationID.max(), "| DOLocationID range", d.DOLocationID.min(), d.DOLocationID.max())
comp = ["fare_amount","extra","mta_tax","tip_amount","tolls_amount","improvement_surcharge","congestion_surcharge","Airport_fee"]
print("total_amount != sum of these parts (>0.01)", p((d[comp].fillna(0).sum(axis=1) - d.total_amount).abs() > 0.01))
key = ["VendorID","tpep_pickup_datetime","tpep_dropoff_datetime","PULocationID","DOLocationID","fare_amount","total_amount"]
print("exact duplicate rows", p(d.duplicated())); print("duplicates on trip key", p(d.duplicated(subset=key)))
