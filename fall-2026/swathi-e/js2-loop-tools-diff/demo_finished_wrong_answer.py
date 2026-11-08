"""SIMULATED demonstration of the finished wrong answer (GATE.md wrong version 1).

    python3 demo_finished_wrong_answer.py

1. The naive JS1 watch (watch.py, copied unchanged) replays the REAL Nov 5 live
   Databricks response, then a SIMULATED empty response (200, {"jobs": []}).
   It ends without error and reports "0 new": a wrong answer.
2. The independent check reads only the two raw files and flags the empty one.
3. The JS2 loop gets the same SIMULATED response through a fake transport and
   reports "empty, unverified", exit incomplete.

watch.py and the loop run in temporary folders outside the repo, so the real
state/ is never read for writing or changed. Everything kept is written once,
through policy.write_evidence, into runs/simulated-2026-11-05-finished-wrong-answer/.
No network request is made. Written by Claude Code (approved 2026-11-05).
"""
from contextlib import redirect_stdout
from datetime import datetime
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time

import independent_check
import loop
import policy as policy_module
import watch

HERE = Path(__file__).resolve().parent
DEMO = Path("runs") / "simulated-2026-11-05-finished-wrong-answer"
REAL_NOV5 = Path("runs") / "2026-11-05T23-11-48-228373-0500" / "001-databricks-request.json"
SIMULATED_NAME = "SIMULATED-databricks-empty-200.json"
SIMULATED_BODY = b'{"jobs":[],"meta":{"total":0}}'
BANNER = "=== SIMULATED: the Databricks response below is constructed, not fetched ==="

LABEL = f"""# SIMULATED: the finished wrong answer

Everything in this folder comes from a SIMULATED demonstration, not a live run.

- `{SIMULATED_NAME}` is SIMULATED: a constructed Greenhouse response, HTTP 200
  with zero postings. No board returned it.
- The one REAL input is `{REAL_NOV5.as_posix()}`, the Nov 5
  live Databricks response, used by path (not copied).
- `js1-watch-output.txt`, `js1-watch-report.json`, `js1-watch-state-before.json`,
  `js1-watch-state-after.json`: the naive JS1 watch (watch.py, unchanged) replaying
  the real response and then the SIMULATED one. watch.py prints "SEEDED RUN"
  because all it knows is that it replayed a file; the second file is SIMULATED.
- `independent-check-output.txt`: independent_check.py on the two raw files.
- `js2-loop-result.json`: the JS2 loop's trace for the same SIMULATED response,
  served by a fake transport.

Reproduce: `python3 demo_finished_wrong_answer.py` (refuses if this folder exists).
"""


def main():
    os.chdir(HERE)
    pol = policy_module.Policy(HERE)
    if pol.check_write(DEMO).exists():
        sys.exit(f"{DEMO.as_posix()} already exists; evidence is never overwritten")
    started = datetime.now().astimezone()
    print(BANNER)
    print(f"demo run at {started:%Y-%m-%d %H:%M:%S %Z} (no network)")
    pol.write_evidence(DEMO / "SIMULATED.md", LABEL.encode())
    simulated = pol.write_evidence(DEMO / SIMULATED_NAME, SIMULATED_BODY)
    sim_rel = Path(os.path.relpath(simulated, HERE))

    # 1. The naive JS1 watch, in a temporary folder.
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        paths = {"state_path": tmp / "state.json", "raw_dir": tmp / "raw", "report_dir": tmp / "reports"}
        with redirect_stdout(io.StringIO()):
            watch.run(from_file=str(REAL_NOV5), **paths)
        state_before = paths["state_path"].read_bytes()
        time.sleep(1.1)  # watch.py names reports by the second
        summary = watch.run(from_file=str(sim_rel), **paths)
        state_after = paths["state_path"].read_bytes()
        report = (paths["report_dir"] / Path(summary["report_path"]).name).read_bytes()
        out = io.StringIO()
        watch.print_summary(summary, out)
        js1_text = BANNER + "\n" + out.getvalue().replace(str(tmp), "<temporary folder>")
    pol.write_evidence(DEMO / "js1-watch-output.txt", js1_text.encode())
    pol.write_evidence(DEMO / "js1-watch-report.json", report.replace(str(tmp).encode(), b"<temporary folder>"))
    pol.write_evidence(DEMO / "js1-watch-state-before.json", state_before)
    pol.write_evidence(DEMO / "js1-watch-state-after.json", state_after)

    # 2. The independent check: raw files only.
    out = io.StringIO()
    check_code = independent_check.main([str(REAL_NOV5), str(sim_rel)], out=out)
    check_text = BANNER + f"\n$ python3 independent_check.py {REAL_NOV5.as_posix()} {sim_rel.as_posix()}\n" \
        + out.getvalue() + f"exit code {check_code}\n"
    pol.write_evidence(DEMO / "independent-check-output.txt", check_text.encode())

    # 3. The JS2 loop, same SIMULATED bytes, in a temporary copy of the JS2 folder.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "js2"
        shutil.copytree(HERE / "persona", root / "persona")
        (root / "state").mkdir(parents=True)
        shutil.copy(HERE / "state" / "seen_ids.json", root / "state" / "seen_ids.json")
        board = loop.BOARDS[0]
        url = loop.board_url(board)

        def simulated_transport(requested, timeout):
            assert requested == url, requested
            return 200, SIMULATED_BODY

        def no_sleep(seconds):
            raise AssertionError("no retry is expected for an empty response")

        result = loop.run_loop((board,), loop.BUDGETS, policy=policy_module.Policy(root),
                               transport=simulated_transport, clock=time.monotonic, sleep=no_sleep,
                               run_id="SIMULATED-empty-databricks")
        trace = json.loads((root / result.run_dir / "trace.json").read_text(encoding="utf-8"))
        kept = len(json.loads((root / "state" / "seen_ids.json").read_text(encoding="utf-8"))["boards"]["databricks"])
    trace["label"] = "SIMULATED: the JS2 loop given the SIMULATED empty Databricks response by a fake transport"
    trace["databricks_ids_kept_in_state"] = kept
    pol.write_evidence(DEMO / "js2-loop-result.json", json.dumps(trace, indent=2).encode())

    db = result.boards[board["name"]]
    print("\n--- 1. naive JS1 watch (SIMULATED empty response) ---")
    print(js1_text.split("\n", 1)[1].rstrip())
    print(f"state ids before: {len(json.loads(state_before)['seen_ids'])}, after: {len(json.loads(state_after)['seen_ids'])}")
    print("\n--- 2. independent check (raw files only) ---")
    print(check_text.split("\n", 1)[1].rstrip())
    print("\n--- 3. JS2 loop (same SIMULATED response) ---")
    print(f"exit: {result.exit}; databricks: {db['status']} ({db['reason']}); new_ids: {db['new_ids']}; "
          f"requests: {result.budgets['requests_used']}; databricks ids kept in state: {kept}")
    print(f"\nevidence: {DEMO.as_posix()}/")


if __name__ == "__main__":
    main()
