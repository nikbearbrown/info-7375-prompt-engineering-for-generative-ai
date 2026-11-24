"""Step 3 — the first piece: one check, run on the clean copy and on the broken copy.

Expected: PASS on clean. On broken, the check flags some rows; only then is the answer key opened,
to score which planted defect types were CAUGHT and which were MISSED.
"""
import json, sys
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "checks"))
from fare_check import RULE, schema  # noqa: E402

from pandera.errors import SchemaErrors  # noqa: E402


def flagged_rows(df):
    try:
        schema.validate(df, lazy=True)
        return set()
    except SchemaErrors as e:
        idx = e.failure_cases["index"].dropna()
        return set(int(i) for i in idx)


def main(out_dir):
    clean = pd.read_parquet(HERE / "data" / "clean.parquet")
    broken = pd.read_parquet(HERE / "data" / "broken.parquet")
    clean_flags = flagged_rows(clean)
    broken_flags = flagged_rows(broken)
    key = pd.read_csv(HERE / "data" / "planted" / "answer_key.csv")      # opened only to score
    lines = [f"check: {RULE}   (pandera)",
             f"clean copy  ({len(clean):,} rows): {'PASS' if not clean_flags else f'FAIL {len(clean_flags)} rows'}",
             f"broken copy ({len(broken):,} rows): flagged {len(broken_flags)} rows"]
    score = {}
    for defect, rows in key.groupby("defect")["row"]:
        planted = set(int(r) for r in rows)
        caught = len(planted & broken_flags)
        verdict = "CAUGHT" if caught == len(planted) else ("MISSED" if caught == 0 else "PARTLY CAUGHT")
        score[defect] = {"planted": len(planted), "caught": caught, "verdict": verdict}
    for defect in ["negative_fare", "dropoff_before_pickup"]:
        s = score[defect]
        lines.append(f"  {defect:<22} planted {s['planted']:>2}  caught {s['caught']:>2}   {s['verdict']}")
    false_alarms = len(broken_flags - set(int(r) for r in key.row))
    lines.append(f"  false alarms on unbroken rows: {false_alarms}")
    text = "\n".join(lines)
    print(text)
    (Path(out_dir) / "first_piece.txt").write_text(text + "\n")
    (Path(out_dir) / "first_piece.json").write_text(json.dumps(
        {"rule": RULE, "clean_pass": not clean_flags, "broken_flagged": len(broken_flags),
         "score": score, "false_alarms": false_alarms}, indent=2) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
