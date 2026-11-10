"""The independent check (GATE.md, Evidence and review choices). Separate code: it imports nothing from jsagent.

It reads the raw files, the trace, the board file, the baseline raw response and earlier runs' raw files, and treats the
loop's report only as the thing being checked. It recomputes counts and new ids from the raw bytes.

    python3 scripts/verify_run.py out/runs/<run id>

FAIL if: a recount differs from the report; a Greenhouse job count differs from meta.total; recomputed new ids differ;
a board returned 0 postings (empty, needs review); a board dropped by more than half since its previous observation;
a planned board has no record; a failed board's count is not null; a raw file's sha256 does not match the trace.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_RAW = {"greenhouse:samsara": ROOT / "baseline" / "2026-10-31" / "samsara.json"}


def raw_ids(provider, body):
    """(ids, meta_total or None), parsed here, independently of the loop's adapters."""
    d = json.loads(body)
    if provider == "greenhouse":
        return [str(j["id"]) for j in d["jobs"]], (d.get("meta") or {}).get("total")
    return [str(j["id"]) for j in d], None


def read_trace(run_dir):
    path = run_dir / "trace.jsonl"
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []


def list_raw(run_dir, trace, key):
    """The raw list response the loop accepted for this board: the last 200 list attempt in the trace."""
    hits = [t for t in trace if t.get("action") == "list" and t.get("board") == key and t.get("http_status") == 200
            and t.get("raw_path")]
    return run_dir / hits[-1]["raw_path"] if hits else None


def earlier_observations(run_dir, key, provider):
    """Every earlier run in the same output root that observed this board: [(run name, ids, unjudged ids)], oldest first."""
    found = []
    for other in sorted(p for p in run_dir.parent.iterdir() if p.is_dir() and p.name < run_dir.name):
        report_path = other / "report.json"
        if not report_path.exists():
            continue
        report = json.loads(report_path.read_text())
        rec = next((b for b in report.get("boards", []) if b.get("key") == key and b.get("status") == "ok"), None)
        raw = list_raw(other, read_trace(other), key) if rec else None
        if rec and raw and raw.exists():
            ids, _ = raw_ids(provider, raw.read_bytes())
            found.append((other.name, ids, set(rec.get("new_unjudged") or [])))
    return found


def verify(run_dir, root=ROOT, baseline_raw=None):
    run_dir = Path(run_dir).resolve()
    baseline_raw = BASELINE_RAW if baseline_raw is None else baseline_raw
    report = json.loads((run_dir / "report.json").read_text())
    trace = read_trace(run_dir)
    lines, fails, no_history = [], [], []

    def check(ok, msg):
        lines.append(("[ok]   " if ok else "[FAIL] ") + msg)
        if not ok:
            fails.append(msg)

    boards_file = Path(report["boards_file"])
    boards_file = boards_file if boards_file.is_absolute() else Path(root) / boards_file
    planned = [f"{b['provider']}:{b['board'].lower()}" for b in json.loads(boards_file.read_text())["boards"]]
    records = {b["key"]: b for b in report["boards"]}
    for key in dict.fromkeys(planned):
        check(key in records, f"{key}: planned board has a record")

    for key, rec in records.items():
        provider = rec["provider"]
        if rec["status"] != "ok":
            check(rec["count"] is None, f"{key}: {rec['status']} board's count is null (unknown, not zero)")
            continue
        raw = list_raw(run_dir, trace, key)
        if raw is None or not raw.exists():
            check(False, f"{key}: no saved raw list response for an 'ok' board")
            continue
        ids, total = raw_ids(provider, raw.read_bytes())
        check(len(ids) == rec["count"], f"{key}: recount from raw {len(ids)} = report count {rec['count']}")
        if provider == "greenhouse":
            check(total == len(ids), f"{key}: meta.total {total} = jobs in the list {len(ids)}")
        check(len(ids) > 0, f"{key}: {len(ids)} postings" + ("" if ids else " (empty, needs review)"))

        earlier = earlier_observations(run_dir, key, provider)
        base = baseline_raw.get(key)
        seen, prev_count, prev_name = set(), None, None
        if base and Path(base).exists():
            base_ids, _ = raw_ids(provider, Path(base).read_bytes())
            seen |= set(base_ids)
            prev_count, prev_name = len(base_ids), f"baseline {Path(base).parent.name}"
        for name, e_ids, e_unjudged in earlier:
            seen |= set(e_ids) - e_unjudged
            prev_count, prev_name = len(e_ids), name
        has_history = bool(earlier) or bool(base and Path(base).exists())
        expected_new = sorted(set(ids) - seen) if has_history else []
        check(sorted(rec["new_ids"]) == expected_new,
              f"{key}: new ids recomputed {len(expected_new)} = reported {len(rec['new_ids'])}")
        if prev_count is None:
            if ids:
                no_history.append(key)
        else:
            check(len(ids) * 2 >= prev_count, f"{key}: {len(ids)} now vs {prev_count} in {prev_name} (drop check: not more than half)")

    for t in trace:
        if t.get("raw_path"):
            path = run_dir / t["raw_path"]
            good = path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == t.get("raw_sha256")
            if not good:
                check(False, f"sha256 of {t['raw_path']} does not match the trace")
    n_raw = sum(1 for t in trace if t.get("raw_path"))
    if not any("sha256" in f for f in fails):
        lines.append(f"[ok]   sha256 of {n_raw} raw file(s) match the trace")

    note = f" (drop check not applicable: {', '.join(no_history)} — no history)" if no_history else ""
    if fails:
        lines.append(f"verifier: FAIL ({'; '.join(fails)}){note}")
    else:
        lines.append(f"verifier: PASS{note}")
    return not fails, lines


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    good, lines = verify(Path(argv[0]))
    print("\n".join(lines))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
