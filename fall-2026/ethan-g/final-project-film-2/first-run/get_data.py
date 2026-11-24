"""Step 1 — get the public data and make a clean 10,000-row sample.

Source: NYC TLC yellow taxi trip records, January 2025 (public, no account).
The clean copy keeps only rows that already pass the two sanity rules we test later
(fare is not negative; drop-off is not before pick-up), so the clean copy is a fair control.
It also reports how many rows in the REAL month already break those rules.
"""
import hashlib, json, sys, urllib.request
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw" / "yellow_tripdata_2025-01.parquet"
URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet"
CLEAN = HERE / "data" / "clean.parquet"
COLS = ["tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "fare_amount"]
SEED = 7375          # the course number, so the sample is the same every run
N = 10_000


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(out_dir):
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if not RAW.exists():
        print(f"downloading {URL}")
        urllib.request.urlretrieve(URL, RAW)
    month = pd.read_parquet(RAW, columns=COLS)
    real = {
        "rows_in_month": int(len(month)),
        "negative_fare_rows": int((month.fare_amount < 0).sum()),
        "dropoff_before_pickup_rows": int((month.tpep_dropoff_datetime < month.tpep_pickup_datetime).sum()),
        "rows_with_a_missing_value": int(month.isna().any(axis=1).sum()),
    }
    ok = month.dropna()
    ok = ok[(ok.fare_amount >= 0) & (ok.tpep_dropoff_datetime >= ok.tpep_pickup_datetime)]
    clean = ok.sample(n=N, random_state=SEED).reset_index(drop=True)
    clean["passenger_count"] = clean["passenger_count"].astype("int64")
    CLEAN.parent.mkdir(parents=True, exist_ok=True)
    clean.to_parquet(CLEAN, index=False)
    info = {"source_url": URL, "raw_file": RAW.name, "raw_sha256": sha256(RAW), "raw_bytes": RAW.stat().st_size,
            "sample_seed": SEED, "sample_rows": N, "clean_sha256": sha256(CLEAN), "real_month_findings": real}
    (Path(out_dir) / "data.json").write_text(json.dumps(info, indent=2) + "\n")
    print(f"raw month: {real['rows_in_month']:,} rows | negative fares: {real['negative_fare_rows']:,} | "
          f"drop-off before pick-up: {real['dropoff_before_pickup_rows']:,} | rows with a missing value: "
          f"{real['rows_with_a_missing_value']:,}")
    print(f"clean sample: {len(clean):,} rows (seed {SEED}) -> {CLEAN.relative_to(HERE)}")


if __name__ == "__main__":
    main(sys.argv[1])
