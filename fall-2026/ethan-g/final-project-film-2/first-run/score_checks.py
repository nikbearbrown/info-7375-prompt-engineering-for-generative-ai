"""The scorer. Grades any pandera checks file against the five planted defect types.

  python score_checks.py <checks.py> <label> <out_dir> [seed]

For each copy it runs the checks (lazy, so every failure is collected), then opens the answer key:
  clean copy           any flag here is a FALSE ALARM (the check is too strict, or wrong)
  each defect copy     CAUGHT (all planted rows flagged) · PARTLY CAUGHT · MISSED
                       wrong_type is caught if the column-level type check fails
A check file that crashes is reported as ERROR, not hidden. Writes <label>.txt and <label>.json.
"""
import importlib.util, json, sys, traceback
from pathlib import Path
import pandas as pd
from pandera.errors import SchemaErrors, SchemaError

HERE = Path(__file__).resolve().parent
TYPES = ["negative_fare", "dropoff_before_pickup", "missing_value", "duplicate_rows", "wrong_type"]


def load_schema(path):
    spec = importlib.util.spec_from_file_location("checks_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.schema


EXC = ("Error(", "Exception(", "NotImplemented")


def _is_crash(failure_case):
    """A check that raised (pandera records the exception as the failure case) is a CHECK ERROR, not a detection."""
    return any(x in str(failure_case) for x in EXC)


def run(schema, df):
    """-> (flagged row indexes, column-level failures [(column, check)], crashed checks [(column, check, exc)], error)"""
    try:
        schema.validate(df, lazy=True)
        return set(), [], [], None
    except SchemaErrors as e:
        fc = e.failure_cases
        rows = set(int(i) for i in fc["index"].dropna())
        col = fc[fc["index"].isna()]
        crashed = [(str(r["column"]), str(r["check"]), str(r["failure_case"])) for _, r in col.iterrows() if _is_crash(r["failure_case"])]
        col_level = [(str(r["column"]), str(r["check"])) for _, r in col.iterrows() if not _is_crash(r["failure_case"])]
        return rows, col_level, crashed, None
    except SchemaError as e:
        return set(), [("?", str(e)[:120])], [], None
    except Exception as e:  # a check file that crashes outright is a result too
        return set(), [], [], f"{type(e).__name__}: {str(e)[:160]}"


def main(checks, label, out_dir, seed=25):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    pdir = HERE / "data" / "planted" / str(seed)
    key = json.loads((pdir / "answer_key.json").read_text())["key"]
    schema = load_schema(checks)
    clean = pd.read_parquet(HERE / "data" / "clean.parquet")
    c_rows, c_cols, c_crash, c_err = run(schema, clean)
    res = {"checks": str(Path(checks).name), "seed": int(seed),
           "clean": {"flagged_rows": len(c_rows), "column_failures": c_cols, "crashed_checks": c_crash, "error": c_err},
           "types": {}}
    for t in TYPES:
        df = pd.read_parquet(pdir / f"{t}.parquet")
        rows, cols, crash, err = run(schema, df)
        if t == "wrong_type":   # caught only by a real (non-crashing) column-level failure on fare_amount
            hit = any(c == "fare_amount" for c, _ in cols)
            planted, caught = 1, int(hit)
        elif t == "duplicate_rows":
            pairs = list(zip(key[t]["copies"], key[t]["originals"]))
            planted, caught = len(pairs), sum(1 for c, o in pairs if c in rows or o in rows)
        else:
            planted, caught = len(key[t]), len(set(key[t]) & rows)
        verdict = "ERROR" if err else ("CAUGHT" if caught == planted else ("MISSED" if caught == 0 else "PARTLY CAUGHT"))
        res["types"][t] = {"planted": planted, "caught": caught, "verdict": verdict, "error": err}
    n_caught = sum(1 for t in TYPES if res["types"][t]["verdict"] == "CAUGHT")
    res["types_caught"] = n_caught
    if c_err:
        clean_line = "ERROR " + c_err
    elif not c_rows and not c_cols and not c_crash:
        clean_line = "PASS"
    else:
        parts = []
        if c_rows: parts.append(f"FALSE ALARM: {len(c_rows)} rows flagged")
        if c_cols: parts.append(f"FALSE ALARM (column-level): {c_cols}")
        if c_crash: parts.append("CHECK ERROR: " + "; ".join(f"'{k}' on {c} raised {x}" for c, k, x in c_crash))
        clean_line = "FAIL — " + " · ".join(parts)
    lines = [f"{label}: {res['checks']}   (planted seed {seed})", "clean copy: " + clean_line]
    for t in TYPES:
        r = res["types"][t]
        cnt = "column" if t == "wrong_type" else f"{r['caught']}/{r['planted']}"
        lines.append(f"  {t:<22} {cnt:>7}   {r['verdict']}" + (f"   ({r['error']})" if r["error"] else ""))
    lines.append(f"defect types fully caught: {n_caught} of {len(TYPES)}")
    text = "\n".join(lines)
    print(text)
    (out / f"{label}.txt").write_text(text + "\n")
    (out / f"{label}.json").write_text(json.dumps(res, indent=1, default=str) + "\n")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2], *(a[3:4] or [25]))
