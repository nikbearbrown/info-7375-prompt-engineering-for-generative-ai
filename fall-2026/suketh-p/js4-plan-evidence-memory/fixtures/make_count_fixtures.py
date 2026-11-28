"""Write the count-check fixtures that PLAN.md v0.2 names. They are FIXTURES, not board responses.

PLAN.md v0.2, "Evidence on the edges": "The count fixture will contain exactly 42 unique keys,
numbered 1 through 42. I'll first check that the recount returns 42. I'll then put 99 in the
summary and require rejection before publication."

  count-42/             a run folder in the loop's format: one Greenhouse-format body holding the
                        keys 1 to 42, and a trace and a summary that both say 42
  count-42-planted-99/  the same raw body and the same trace, but the summary (results.json and
                        results.md) says 99: the planted "42 in the trace, 99 in the claim" error

Claude Code wrote this on 2026-11-25. Nothing it writes was fetched from a board. Standard
library only, and nothing from jobwatch, so the fixtures do not change if the loop's report code
does. Usage, from the JS4 folder:

  python3 -I fixtures/make_count_fixtures.py [OUT_DIR]

OUT_DIR defaults to this folder. Files there are rewritten. The same input always gives the same
JSON and Markdown files and the same decompressed raw body. The gzip container bytes may differ
between machines, and no check compares them."""

import gzip
import hashlib
import json
import sys
from pathlib import Path

BOARD = "greenhouse/fixture-count-42"
RUN_ID = "FIXTURE-count-42"
RAW = "raw/greenhouse-fixture-count-42.body.gz"
KEYS = list(range(1, 43))  # the plan: "exactly 42 unique keys, numbered 1 through 42"
REASON = "FIXTURE: no request was sent"
LABEL = ("FIXTURE: constructed by Claude Code on 2026-11-25 for the count check in PLAN.md v0.2. "
         "Not a board response; nothing here was fetched.")
PLANTED_LABEL = ("FIXTURE with a PLANTED ERROR: this summary claims 99 jobs, but the trace and the raw body "
                 "hold 42 (the keys 1 to 42). The count check must reject it. Constructed by Claude Code on "
                 "2026-11-25; nothing here was fetched.")


def raw_body():
    jobs = [{"id": n, "title": f"FIXTURE posting {n}"} for n in KEYS]
    return json.dumps({"jobs": jobs, "meta": {"total": len(KEYS)}}, separators=(",", ":")).encode("utf-8")


def _json(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def trace_record(body):
    request = {"seq": 1, "at": None, "event": "request", "board": BOARD, "url": None, "elapsed_s": None,
               "status": 200, "content_type": "application/json", "bytes": len(body),
               "sha256": hashlib.sha256(body).hexdigest(), "raw": RAW, "outcome": "usable",
               "jobs": len(KEYS), "reason": None}
    exit_event = {"seq": 2, "at": None, "event": "exit", "status": "finished", "reason": REASON}
    return {"run_id": RUN_ID, "label": LABEL, "status": "finished", "reason": REASON, "state_advanced": False,
            "events": [request, exit_event]}


def results_record(summary_jobs, label):
    row = {"board": BOARD, "role": "normal", "url": None, "outcome": "usable", "jobs": summary_jobs,
           "baseline": True, "new_keys": [], "new_postings": [], "reason": None, "provisional": True}
    return {"run_id": RUN_ID, "label": label, "status": "finished", "reason": REASON, "state_advanced": False,
            "boards": [row], "trace": "trace.json"}


def trace_md(trace):
    request = trace["events"][0]
    return "\n".join([
        f"# Trace of run `{RUN_ID}`: **finished**",
        "",
        trace["label"],
        "",
        "| # | At | Event | Board | HTTP | Elapsed s | Bytes | Outcome | Jobs | Raw file | Reason |",
        "|---:|---|---|---|---:|---:|---:|---|---:|---|---|",
        f"| 1 | — | request | {BOARD} | 200 | — | {request['bytes']} | usable | {request['jobs']} | {RAW} | — |",
        f"| 2 | — | exit | — | — | — | — | finished | — | — | {REASON} |",
        "",
    ])


def results_md(results):
    row = results["boards"][0]
    return "\n".join([
        f"# Run `{RUN_ID}`: **finished**",
        "",
        results["label"],
        "",
        "| Board | Role | Outcome | Jobs | Baseline | New | Reason |",
        "|---|---|---|---:|---|---:|---|",
        f"| {BOARD} | normal | usable | {row['jobs']} | True | 0 | — |",
        "",
    ])


def write_run(folder, summary_jobs, label):
    folder = Path(folder)
    (folder / "raw").mkdir(parents=True, exist_ok=True)
    body = raw_body()
    (folder / RAW).write_bytes(gzip.compress(body, mtime=0))
    trace = trace_record(body)
    results = results_record(summary_jobs, label)
    (folder / "trace.json").write_text(_json(trace), encoding="utf-8")
    (folder / "results.json").write_text(_json(results), encoding="utf-8")
    (folder / "trace.md").write_text(trace_md(trace), encoding="utf-8")
    (folder / "results.md").write_text(results_md(results), encoding="utf-8")
    return folder


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = Path(argv[0]) if argv else Path(__file__).resolve().parent
    for folder in (write_run(out / "count-42", len(KEYS), LABEL),
                   write_run(out / "count-42-planted-99", 99, PLANTED_LABEL)):
        print(f"wrote {folder}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
