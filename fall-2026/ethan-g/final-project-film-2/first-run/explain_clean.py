"""Which rules flag rows of the CLEAN copy (false alarms), and how many rows each.

  python explain_clean.py <checks.py> <label> <out_dir>

Only the clean copy is used, so this says nothing about the planted defects. It is the feedback a check writer
may see between rounds.
"""
import importlib.util, json, sys
from pathlib import Path
import pandas as pd
from pandera.errors import SchemaErrors

HERE = Path(__file__).resolve().parent


def main(checks, label, out_dir):
    spec = importlib.util.spec_from_file_location("checks_under_test", checks)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    clean = pd.read_parquet(HERE / "data" / "clean.parquet")
    try:
        mod.schema.validate(clean, lazy=True)
        per = {}
    except SchemaErrors as e:
        fc = e.failure_cases
        fc = fc[fc["index"].notna()]
        # table-level rules are reported once per column by pandera; count each rule once
        per = (fc.groupby("check")["index"].nunique().sort_values(ascending=False).to_dict())
    total = 0
    lines = [f"{label}: rules that flag the clean copy ({len(clean):,} rows)"]
    try:
        mod.schema.validate(clean, lazy=True); total = 0
    except SchemaErrors as e:
        total = int(e.failure_cases["index"].dropna().nunique())
    lines.append(f"  {total} distinct clean rows flagged in all")
    crashed = []
    try:
        mod.schema.validate(clean, lazy=True)
    except SchemaErrors as e:
        col = e.failure_cases[e.failure_cases["index"].isna()]
        crashed = [(str(r["column"]), str(r["check"]), str(r["failure_case"])) for _, r in col.iterrows()]
    for c, k, x in crashed:
        lines.append(f"  column-level failure: '{k}' on {c}: {x}")
    if not per and not crashed:
        lines.append("  none — the clean copy passes")
    for chk, n in per.items():
        lines.append(f"  {n:>4} rows   {chk}")
    text = "\n".join(lines)
    print(text)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / f"{label}-clean-flags.txt").write_text(text + "\n")
    (out / f"{label}-clean-flags.json").write_text(json.dumps(
        {"distinct_rows": total, "per_rule": [{"check": str(k), "rows": int(n)} for k, n in per.items()],
         "column_level": [{"column": c, "check": k, "failure": x} for c, k, x in crashed]}, indent=1) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:4])
