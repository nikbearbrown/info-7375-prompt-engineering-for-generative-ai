"""Step 2 — the defect planter. Copies the clean sample and breaks it on purpose.

Two defect types, 25 rows each, on different rows (seeded, so the same rows every run):
  negative_fare           fare_amount becomes negative          (the one check covers this)
  dropoff_before_pickup   drop-off moved before the pick-up     (the one check does NOT cover this)
The answer key (which rows were broken, and how) is written to data/planted/ and is never read by any check.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CLEAN = HERE / "data" / "clean.parquet"
BROKEN = HERE / "data" / "broken.parquet"
KEY = HERE / "data" / "planted" / "answer_key.csv"
SEED = 25
PER_TYPE = 25


def main(out_dir):
    df = pd.read_parquet(CLEAN)
    rng = np.random.default_rng(SEED)
    rows = rng.choice(len(df), size=2 * PER_TYPE, replace=False)
    neg, early = sorted(rows[:PER_TYPE]), sorted(rows[PER_TYPE:])
    broken = df.copy()
    broken.loc[neg, "fare_amount"] = -(broken.loc[neg, "fare_amount"].abs() + 1.0)
    minutes = pd.to_timedelta(rng.integers(5, 60, size=PER_TYPE), unit="m")
    broken.loc[early, "tpep_dropoff_datetime"] = broken.loc[early, "tpep_pickup_datetime"].values - minutes.values
    broken.to_parquet(BROKEN, index=False)
    KEY.parent.mkdir(parents=True, exist_ok=True)
    key = pd.DataFrame({"row": list(neg) + list(early),
                        "defect": ["negative_fare"] * PER_TYPE + ["dropoff_before_pickup"] * PER_TYPE})
    key.to_csv(KEY, index=False)
    (Path(out_dir) / "planted.json").write_text(json.dumps(
        {"seed": SEED, "per_type": PER_TYPE, "types": ["negative_fare", "dropoff_before_pickup"]}, indent=2) + "\n")
    print(f"broken copy: {len(broken):,} rows, {PER_TYPE} negative fares + {PER_TYPE} drop-offs before pick-up planted")


if __name__ == "__main__":
    main(sys.argv[1])
