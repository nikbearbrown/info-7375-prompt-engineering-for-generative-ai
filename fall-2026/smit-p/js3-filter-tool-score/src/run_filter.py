"""Run the filter on every posting a run collected.

    python3 src/run_filter.py --run-id live-20261114

Writes runs/<run-id>/verdicts-v<filter version>.json and prints the counts. Offline.
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filter as flt  # noqa: E402
from postings import ROOT, load_run  # noqa: E402


def load_skills():
    with open(os.path.join(ROOT, "persona", "aarav-patel.resume.json"), encoding="utf-8") as f:
        return flt.resume_skills(json.load(f))


def run(run_id, config=None):
    config = config or flt.CURRENT
    version = config["version"]
    postings, unreadable, manifest = load_run(run_id)
    skills = load_skills()
    verdicts = [flt.judge(p, skills, config) for p in postings]
    out = {"run_id": run_id, "filter_version": version,
           "boards": {b["board"]: b["status"] for b in manifest["boards"]},
           "unreadable": [{"board": p["board"], "id": p["id"]} for p in unreadable],
           "verdicts": verdicts}
    path = os.path.join(ROOT, "runs", run_id, f"verdicts-v{version}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    return out, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--version", choices=["1.0", "1.1"], default=flt.FILTER_VERSION)
    a = ap.parse_args()
    out, path = run(a.run_id, flt.V1_0 if a.version == "1.0" else flt.V1_1)
    v = out["verdicts"]
    print(f"{len(v)} postings judged, {len(out['unreadable'])} unreadable -> {os.path.relpath(path, ROOT)}")
    print("verdicts:", dict(collections.Counter(x["verdict"] for x in v)))
    print("by rule: ", dict(sorted(collections.Counter(f"{x['verdict']}:{x['rule']}" for x in v).items())))
    print("by board:", dict(collections.Counter(f"{x['board']}:{x['verdict']}" for x in v)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
