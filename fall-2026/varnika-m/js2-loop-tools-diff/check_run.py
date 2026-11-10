"""An independent check of one run (GATE.md section 7). It does not import the agent.

    python3 check_run.py jobs/runs/RUN_ID.json

It trusts nothing the loop concluded. It reads the run record, the trace, the saved raw
responses, the boards' state history and this folder's GATE.md, recomputes what it can
with its own parsing, and says whether the run's claim is supported.
Exit code 0 if every check passes, 1 if any fails.
"""

import collections
import gzip
import hashlib
import json
import math
import re
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
Check = collections.namedtuple("Check", "name passed detail")
SECONDS_SLACK = 5  # total time only: work after the last request (parsing, writing) is not inside any timeout
ROUNDING = 0.01  # the trace rounds times to 3 decimals


def gate_rules(gate_text):
    def number(name):
        return int(re.search(r"^\| %s \| ([0-9,]+)" % re.escape(name), gate_text, re.M).group(1).replace(",", ""))
    hosts = set(re.findall(r"^\| `([a-z.-]+\.[a-z]+)` \| `/", gate_text, re.M))
    return {"boards": number("Boards"), "requests": number("Requests"), "seconds": number("Seconds"),
            "seconds_per_request": number("Seconds per request"), "hosts": hosts}


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def ids_in(system, body):
    """Posting ids in a raw response, by this file's own reading of each system's shape."""
    data = json.loads(body.decode("utf-8"))
    jobs = data if system == "lever" else data["jobs"]
    return [str(job["id"]) for job in jobs]


def raw_body(root, relative):
    return gzip.decompress((root / relative).read_bytes())


def history_before(root, key, run_id):
    """This board's earlier good runs, from its state file: [(run_id, postings, raw_file)]."""
    path = root / "jobs" / "state" / ("%s.json" % key.replace("/", "-"))
    if not path.exists():
        return None
    runs = json.loads(path.read_text(encoding="utf-8")).get("runs", [])
    earlier = []
    for entry in runs:
        if entry.get("run_id") == run_id:
            return earlier
        earlier.append(entry)
    return None  # this run is not in the board's history


def boards_match_config(root, record, trace):
    config = json.loads((root / "config" / "boards.json").read_text(encoding="utf-8"))["boards"]
    keys = ["%s/%s" % (e["system"].lower(), e["board"].lower()) for e in config]
    problems = []
    listed = [b["key"] for b in record["boards"]] + list(record["not_attempted"])
    if record["exit"] != "error" and listed != keys:
        problems.append("the record lists %s, config/boards.json has %s" % (listed, keys))
    start = next((line for line in trace if line["action"] == "start"), None)
    if start is not None and start["boards"] != keys:
        problems.append("the trace started with %s, config/boards.json has %s" % (start["boards"], keys))
    fetched = {line["board"] for line in trace if line["action"] == "fetch"}
    earlier = set()
    for b in record["boards"]:
        if b["status"] == "skipped_repeat":
            if b["key"] not in earlier:
                problems.append("%s is labelled skipped_repeat, but no earlier entry is the same board" % b["key"])
        elif b["key"] not in fetched:
            problems.append("%s has status %s, but the trace has no fetch for it" % (b["key"], b["status"]))
        earlier.add(b["key"])
    return Check("boards_match_config", not problems, "; ".join(problems) or
                 "the record's boards are config/boards.json's, and each was fetched or truly a repeat")


def check(record_path, root=None):
    record_path = Path(record_path).resolve()
    root = Path(root).resolve() if root else record_path.parents[2]
    record = json.loads(record_path.read_text(encoding="utf-8"))
    trace = [json.loads(line) for line in (root / record["files"]["trace"]).read_text(encoding="utf-8").splitlines()]
    gate = gate_rules((HERE / "GATE.md").read_text(encoding="utf-8"))
    checks = []

    # 1. Every saved raw response is the one the trace recorded.
    traced = {line["result"]["raw_file"]: line["result"]["raw_sha256"] for line in trace
              if line["action"] == "fetch" and "raw_file" in line.get("result", {})}
    bad = []
    for b in record["boards"]:
        for attempt in b.get("attempts", []):
            if "raw_file" not in attempt:
                continue
            actual = hashlib.sha256(raw_body(root, attempt["raw_file"])).hexdigest()
            if not (actual == attempt["raw_sha256"] == traced.get(attempt["raw_file"])):
                bad.append(attempt["raw_file"])
    checks.append(Check("raw_sha256", not bad, "mismatch: %s" % bad if bad else
                        "%d raw responses match the trace" % len(traced)))

    # 2-5 look at the final answer of each board the loop called ok. A failed board's body
    # (HTML, an error document) is not a board, so it is not parsed.
    final = {}
    for b in record["boards"]:
        answered = [a for a in b.get("attempts", []) if a.get("http_status") == 200]
        if b["status"] == "ok" and answered:
            try:
                final[b["key"]] = ids_in(b["system"], raw_body(root, answered[-1]["raw_file"]))
            except (ValueError, KeyError, TypeError):
                final[b["key"]] = []

    wrong_counts = ["%s: loop %s, raw %d" % (b["key"], b["counts"]["postings"], len(set(final.get(b["key"], []))))
                    for b in record["boards"] if b["status"] == "ok"
                    and b["counts"]["postings"] != len(set(final.get(b["key"], [])))]
    checks.append(Check("independent_count", not wrong_counts, "; ".join(wrong_counts) or
                        "every ok board's count matches my own count of its raw response"))

    if record["exit"] == "finished":
        problems = ["%s is %s" % (b["key"], b["status"]) for b in record["boards"]
                    if b["status"] not in ("ok", "skipped_repeat")]
        problems += ["%s has 0 postings in its raw response" % b["key"] for b in record["boards"]
                     if b["status"] == "ok" and not final.get(b["key"])]
        checks.append(Check("finished_needs_postings_on_every_board", not problems,
                            "; ".join(problems) or "every board in this finished run had postings"))

    drops = []
    for b in record["boards"]:
        if b["status"] == "ok" and not final.get(b["key"]):
            earlier = history_before(root, b["key"], record["run_id"]) or []
            before = [e["postings"] for e in earlier if e.get("postings")]
            drops.append("%s reported ok with 0 postings (%s)" % (
                b["key"], ("last good run had %d" % before[-1]) if before else "no earlier run to compare"))
    checks.append(Check("no_drop_to_zero", not drops, "; ".join(drops) or "no ok board dropped to zero"))

    # 5. Recompute "new" from the earlier raw responses themselves, not from the loop's state.
    wrong_new, cannot = [], []
    for b in record["boards"]:
        if b["status"] != "ok":
            continue
        earlier = history_before(root, b["key"], record["run_id"])
        if earlier is None:
            cannot.append("%s: this run is not in the board's state history" % b["key"])
            continue
        reported = {p["job_id"] for p in b.get("new_postings", [])}
        if not earlier:
            expected = set()
        else:
            seen = set()
            for entry in earlier:
                path = (root / entry["raw_file"]).resolve()
                if not path.exists():
                    cannot.append("%s: earlier raw file %s is missing" % (b["key"], entry["raw_file"]))
                    break
                seen |= set(ids_in(b["system"], gzip.decompress(path.read_bytes())))
            expected = set(final.get(b["key"], [])) - seen
        if reported != expected:
            wrong_new.append("%s: loop %d new, recomputed %d" % (b["key"], len(reported), len(expected)))
    checks.append(Check("new_ids_recomputed", not wrong_new and not cannot, "; ".join(wrong_new + cannot) or
                        "every ok board's new ids match a recomputation from the earlier raw responses"))

    # 5b. Recompute "gone since the last good run" from that run's raw response.
    wrong_gone = []
    for b in record["boards"]:
        if b["status"] != "ok" or b["counts"].get("gone") is None:
            continue
        earlier = history_before(root, b["key"], record["run_id"])
        if not earlier:
            expected = 0
        else:
            path = (root / earlier[-1]["raw_file"]).resolve()
            if not path.exists():
                wrong_gone.append("%s: last raw file %s is missing" % (b["key"], earlier[-1]["raw_file"]))
                continue
            expected = len(set(ids_in(b["system"], gzip.decompress(path.read_bytes()))) - set(final.get(b["key"], [])))
        if b["counts"]["gone"] != expected:
            wrong_gone.append("%s: loop %d gone, recomputed %d" % (b["key"], b["counts"]["gone"], expected))
    checks.append(Check("gone_recomputed", not wrong_gone, "; ".join(wrong_gone) or
                        "every ok board's gone count matches its last good run's raw response (or is unknown)"))

    # 6. Budgets and hosts, from the trace, against GATE.md.
    fetches = [line for line in trace if line["action"] == "fetch"]
    problems = []
    used = record["budget"]["used"]["seconds"]
    if not finite(used):
        problems.append("the run's total time is %r, so the time budget cannot be verified" % (used,))
    elif used > gate["seconds"] + SECONDS_SLACK:
        problems.append("%.1f s used, GATE.md allows %d" % (used, gate["seconds"]))
    if len(fetches) != record["budget"]["used"]["requests"]:
        problems.append("trace has %d fetches, record says %d" % (len(fetches), record["budget"]["used"]["requests"]))
    if len(fetches) > gate["requests"]:
        problems.append("%d requests, GATE.md allows %d" % (len(fetches), gate["requests"]))
    if record["budget"]["used"]["boards"] > gate["boards"]:
        problems.append("%d boards, GATE.md allows %d" % (record["budget"]["used"]["boards"], gate["boards"]))
    for line in fetches:
        parts = urllib.parse.urlsplit(line["url"])
        if parts.scheme != "https" or parts.hostname not in gate["hosts"]:
            problems.append("request to %s" % line["url"])
        if line["timeout"] > gate["seconds_per_request"]:
            problems.append("timeout %s s > %d s" % (line["timeout"], gate["seconds_per_request"]))
        if "started_t" in line:  # GATE.md Decisions, 2026-11-10: the same budget as the agent, no slack
            started, allowance = line["started_t"], ROUNDING
        else:  # traces written before that decision do not record the start; estimate it
            started, allowance = (line["t"] - (line.get("seconds") or 0)) if finite(line["t"]) else None, SECONDS_SLACK
        if not finite(started) or not finite(line["timeout"]):
            problems.append("a request's start or timeout is not a number, so the time budget cannot be verified")
            continue
        if started >= gate["seconds"]:
            problems.append("a request started at %.1f s, after the %d s budget was spent" % (started, gate["seconds"]))
        elif started + line["timeout"] > gate["seconds"] + allowance:
            problems.append("a request started at %.1f s was given %s s, past the %d s budget"
                            % (started, line["timeout"], gate["seconds"]))
    checks.append(Check("budgets_and_hosts", not problems, "; ".join(problems) or
                        "%d requests, all to GATE.md hosts, within budget" % len(fetches)))

    # 7. The boards in the record are the boards in config/boards.json, and each one was really fetched.
    checks.append(boards_match_config(root, record, trace))

    # 8. The exit agrees with what happened to the boards.
    statuses = [b["status"] for b in record["boards"]]
    problems = []
    if trace[-1].get("action") != "exit" or trace[-1].get("exit") != record["exit"]:
        problems.append("the last trace line is not this exit")
    if record["exit"] == "finished" and (record["not_attempted"] or {"failed", "suspect"} & set(statuses)):
        problems.append("finished with a failed, suspect or unattempted board")
    if record["exit"] == "incomplete" and (record["not_attempted"] or not {"failed", "suspect"} & set(statuses)):
        problems.append("incomplete without a failed or suspect board, or with unattempted boards")
    if record["exit"] == "budget_exhausted" and not record["not_attempted"]:
        problems.append("budget_exhausted but every board was attempted")
    checks.append(Check("exit_consistent", not problems, "; ".join(problems) or
                        "exit %s agrees with the boards and the trace" % record["exit"]))
    return checks


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    record = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    checks = check(argv[0])
    print("Independent check of run %s (the loop said: %s)" % (record["run_id"], record["exit"]))
    for c in checks:
        print("  %s  %-40s %s" % ("PASS" if c.passed else "FAIL", c.name, c.detail))
    supported = all(c.passed for c in checks)
    print("Verdict: the run's claim is %s." % ("SUPPORTED" if supported else "NOT SUPPORTED"))
    return 0 if supported else 1


if __name__ == "__main__":
    sys.exit(main())
