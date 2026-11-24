"""A second clean copy the loop never saw: false alarms on 10,000 good trips that were never fed back.

  python heldout_clean.py <checks.py> <label> <out_dir>

The loop's feedback comes from data/clean.parquet, so "0 good trips flagged" there is measured on the copy the
checks were tuned on. This draws a DISJOINT 10,000-row sample from the same month, cleaned by the same two rules
(get_data.py), with a different seed (2026), and reports how many of its good trips the checks flag.
Writes <label>-heldout-clean.txt / .json. Builds data/clean-heldout.parquet on first use.
"""
import json, sys
from pathlib import Path
import pandas as pd
from get_data import RAW, COLS, SEED, N
from score_checks import load_schema, run

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "clean-heldout.parquet"
SEED2 = 2026


def build():
    month = pd.read_parquet(RAW, columns=COLS)
    ok = month.dropna()
    ok = ok[(ok.fare_amount >= 0) & (ok.tpep_dropoff_datetime >= ok.tpep_pickup_datetime)]
    used = ok.sample(n=N, random_state=SEED).index                 # the rows in data/clean.parquet
    rest = ok.drop(index=used)
    h = rest.sample(n=N, random_state=SEED2).reset_index(drop=True)
    h["passenger_count"] = h["passenger_count"].astype("int64")
    h.to_parquet(OUT, index=False)
    return len(set(used) & set(rest.index))


def main(checks, label, out_dir):
    overlap = build() if not OUT.exists() else 0
    df = pd.read_parquet(OUT)
    rows, cols, crashed, err = run(load_schema(checks), df)
    res = {"checks": Path(checks).name, "sample": "clean-heldout", "seed": SEED2, "rows": len(df),
           "overlap_with_clean_sample": overlap, "flagged_rows": len(rows), "column_failures": cols,
           "crashed_checks": crashed, "error": err}
    text = (f"{label}: {Path(checks).name} on a second clean copy ({len(df):,} good trips, seed {SEED2}, disjoint "
            f"from the feedback copy)\n  good trips flagged: {len(rows)}"
            + (f"\n  column-level failures: {cols}" if cols else "")
            + (f"\n  crashing checks: {crashed}" if crashed else "") + (f"\n  error: {err}" if err else ""))
    print(text)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / f"{label}-heldout-clean.txt").write_text(text + "\n")
    (out / f"{label}-heldout-clean.json").write_text(json.dumps(res, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:4])
