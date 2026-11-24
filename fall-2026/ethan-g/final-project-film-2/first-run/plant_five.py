"""The five-defect planter. One broken copy PER defect type, so each type is scored on its own
and one defect can't hide or crash the check for another.

  negative_fare          25 fares made negative
  dropoff_before_pickup  25 drop-offs moved 5-59 minutes before their pick-up
  missing_value          25 trip distances blanked (NaN)
  duplicate_rows         25 existing trips appended again (exact copies)
  wrong_type             fare_amount arrives as text, like a bad import

Seeded (default 25; pass another seed for a held-out set). The answer key goes to data/planted/<seed>/
and is never shown to any check writer.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CLEAN = HERE / "data" / "clean.parquet"
PER_TYPE = 25
TYPES = ["negative_fare", "dropoff_before_pickup", "missing_value", "duplicate_rows", "wrong_type"]


def main(seed=25):
    seed = int(seed)
    out = HERE / "data" / "planted" / str(seed)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(CLEAN)
    rng = np.random.default_rng(seed)
    key = {}

    rows = sorted(int(r) for r in rng.choice(len(df), PER_TYPE, replace=False))
    b = df.copy(); b.loc[rows, "fare_amount"] = -(b.loc[rows, "fare_amount"].abs() + 1.0)
    b.to_parquet(out / "negative_fare.parquet", index=False); key["negative_fare"] = rows

    rows = sorted(int(r) for r in rng.choice(len(df), PER_TYPE, replace=False))
    b = df.copy(); mins = pd.to_timedelta(rng.integers(5, 60, size=PER_TYPE), unit="m")
    b.loc[rows, "tpep_dropoff_datetime"] = b.loc[rows, "tpep_pickup_datetime"].values - mins.values
    b.to_parquet(out / "dropoff_before_pickup.parquet", index=False); key["dropoff_before_pickup"] = rows

    rows = sorted(int(r) for r in rng.choice(len(df), PER_TYPE, replace=False))
    b = df.copy(); b.loc[rows, "trip_distance"] = np.nan
    b.to_parquet(out / "missing_value.parquet", index=False); key["missing_value"] = rows

    src = sorted(int(r) for r in rng.choice(len(df), PER_TYPE, replace=False))
    b = pd.concat([df, df.loc[src]], ignore_index=True)          # copies land at rows len(df) .. len(df)+24
    b.to_parquet(out / "duplicate_rows.parquet", index=False)
    key["duplicate_rows"] = {"copies": list(range(len(df), len(df) + PER_TYPE)), "originals": src}

    b = df.copy(); b["fare_amount"] = b["fare_amount"].map(lambda v: f"{v:.2f}")
    b.to_parquet(out / "wrong_type.parquet", index=False); key["wrong_type"] = {"column": "fare_amount", "rows": "whole column"}

    (out / "answer_key.json").write_text(json.dumps({"seed": seed, "per_type": PER_TYPE, "key": key}, indent=1) + "\n")
    print(f"planted 5 defect types (seed {seed}) -> data/planted/{seed}/ : " + ", ".join(TYPES))


if __name__ == "__main__":
    main(*(sys.argv[1:2] or [25]))
