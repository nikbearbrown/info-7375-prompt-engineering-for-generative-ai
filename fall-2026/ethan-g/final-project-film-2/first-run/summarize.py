"""Step 6 — put the three tools side by side, and record the environment.

Reads the saved outputs from this run (pandera, dbt's run_results.json, GX) and the answer key,
and writes compare.txt + environment.json into the dated results folder.
"""
import json, platform, sys
from datetime import datetime
from importlib import metadata
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent


def main(out_dir):
    out = Path(out_dir)
    fp = json.loads((out / "first_piece.json").read_text())
    gx = json.loads((out / "gx.json").read_text())
    rr = json.loads((HERE / "dbt_compare" / "target" / "run_results.json").read_text())
    dbt = {}
    for r in rr["results"]:
        if r["unique_id"].startswith("test."):
            which = "clean" if "trips_clean" in r["unique_id"] else "broken"
            dbt[which] = {"status": r["status"], "failures": r.get("failures") or 0}
    key = pd.read_csv(HERE / "data" / "planted" / "answer_key.csv")
    n = key.defect.value_counts().to_dict()
    data = json.loads((out / "data.json").read_text())

    def cell(passed, bad):
        return "PASS" if passed else f"FAIL {bad} rows"
    rows = [("pandera", cell(fp["clean_pass"], 0), cell(False, fp["broken_flagged"])),
            ("dbt", cell(dbt["clean"]["status"] == "pass", dbt["clean"]["failures"]),
             cell(dbt["broken"]["status"] == "pass", dbt["broken"]["failures"])),
            ("GX Core", cell(gx["clean"]["success"], gx["clean"]["unexpected_count"]),
             cell(gx["broken"]["success"], gx["broken"]["unexpected_count"]))]
    s = fp["score"]
    lines = [f"Same rule (fare_amount >= 0) in three tools. Recorded {datetime.now():%Y-%m-%d %H:%M} (local).",
             f"Data: NYC TLC yellow taxi, January 2025; clean sample {data['sample_rows']:,} rows (seed {data['sample_seed']}).",
             f"Broken copy: {n.get('negative_fare', 0)} negative fares + {n.get('dropoff_before_pickup', 0)} drop-offs before pick-up, planted.",
             "",
             f"{'tool':<10}{'clean copy':<14}{'broken copy':<16}",
             *[f"{t:<10}{c:<14}{b:<16}" for t, c, b in rows],
             "",
             f"Against the answer key: negative fares {s['negative_fare']['caught']}/{s['negative_fare']['planted']} "
             f"{s['negative_fare']['verdict']}; drop-off before pick-up {s['dropoff_before_pickup']['caught']}/"
             f"{s['dropoff_before_pickup']['planted']} {s['dropoff_before_pickup']['verdict']}.",
             "All three report rows that break the rule they were given. None of them can say what the rule missed;",
             "only the planted answer key shows the drop-offs before pick-up got through.",
             "",
             f"In the real January 2025 file: {data['real_month_findings']['negative_fare_rows']:,} negative fares and "
             f"{data['real_month_findings']['dropoff_before_pickup_rows']:,} drop-offs before pick-up, out of "
             f"{data['real_month_findings']['rows_in_month']:,} rows."]
    text = "\n".join(lines)
    print(text)
    (out / "compare.txt").write_text(text + "\n")
    pkgs = {p: metadata.version(p) for p in ["pandas", "pyarrow", "pandera", "duckdb", "dbt-core", "dbt-duckdb",
                                             "great_expectations"]}
    (out / "environment.json").write_text(json.dumps(
        {"recorded_at": datetime.now().isoformat(timespec="seconds"), "python": platform.python_version(),
         "platform": platform.platform(), "packages": pkgs}, indent=2) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
