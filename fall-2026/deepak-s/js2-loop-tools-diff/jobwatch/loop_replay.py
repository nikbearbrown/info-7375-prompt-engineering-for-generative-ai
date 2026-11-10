"""`python -m jobwatch replay runs/<run-id>` for a JS2 loop run: offline, writes nothing.

Re-parses each board's saved raw bytes with the same providers, re-derives count, new ids and
baseline from state_before.json, recomputes the exit, and compares with summary.json.
Exit 0 when everything matches, 1 on any difference.

Taken from summary.json as given, because no saved file records them: boards that failed with
no HTTP response (timeout, connection), the budget record, and the error record. This is a
consistency check on the loop's own files; the independent check is verify (GATE.md section 7).
"""
import hashlib
import json

from jobwatch import providers
from jobwatch.loop import EXIT_CODES, decide_exit, validate_state
from jobwatch.policy import Policy
from jobwatch.tools import FetchResult, Tools


def replay_loop_run(run_dir, root="."):
    tools = Tools(Policy(root))
    diffs = []

    def read_json(name):
        return json.loads(tools.read_file(f"{run_dir}/{name}"))

    summary, manifest = read_json("summary.json"), read_json("manifest.json")
    try:
        state_raw = tools.read_file(f"{run_dir}/state_before.json")
    except FileNotFoundError:
        state_raw = None
    if (hashlib.sha256(state_raw).hexdigest() if state_raw is not None else None) != summary.get("state_before_sha256"):
        diffs.append("state_before.json sha256 differs from summary.json")
    known = validate_state(state_raw)["boards"] if state_raw is not None else {}

    results = []
    for b in summary["boards"]:
        if b["status"] == "UNVISITED":
            continue
        files = [f for f in manifest["files"] if f["board"] == b["key"]]
        for f in files:
            if hashlib.sha256(tools.read_file(f"{run_dir}/{f['path']}")).hexdigest() != f["sha256"]:
                diffs.append(f"sha256 mismatch: {f['path']}")
        if not files:
            results.append(b)  # no response saved: taken as given
            continue
        final = max(files, key=lambda f: f["attempt"])
        body = tools.read_file(f"{run_dir}/{final['path']}")
        res = FetchResult(b["url"], final["http_status"], {"content-type": final["content_type"]}, body)
        parsed = providers.get(b["system"]).parse(res, b["key"])
        if isinstance(parsed, providers.BoardError):
            got = {"status": "FAILED", "count": None, "new_ids": None, "baseline": None, "reason": parsed.kind}
            if b["reason"] in ("budget", "repeat"):
                got["reason"] = b["reason"]
        else:
            ids = [p.id for p in parsed]
            prior = known.get(b["key"])
            new = [] if prior is None else [i for i in ids if i not in set(prior["seen_ids"])]
            got = {"status": "OK", "count": len(ids), "new_ids": new, "baseline": prior is None, "reason": None}
        for k, v in got.items():
            if b.get(k) != v:
                diffs.append(f"{b['key']}.{k}: summary.json {b.get(k)!r}, replay {v!r}")
        results.append({**b, **got})

    status = decide_exit(results, summary.get("budget_exhausted"), summary.get("error"))
    if status != summary["exit"] or EXIT_CODES[status] != summary["exit_code"]:
        diffs.append(f"exit: summary.json {summary['exit']}, replay {status}")
    return diffs, summary


def main(run_dir):
    diffs, summary = replay_loop_run(run_dir)
    print(f"replay {run_dir} (offline; JS2 loop run, label {summary.get('label')})")
    for d in diffs:
        print(f"  DIFF {d}")
    print(f"  exit {summary['exit']} ({summary['exit_code']}); "
          f"{'matches' if not diffs else str(len(diffs)) + ' difference(s)'}")
    return 0 if not diffs else 1
