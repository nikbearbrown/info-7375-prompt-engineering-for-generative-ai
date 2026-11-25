"""The corpus: everything the agent collected (FILTER.md section 5).

Reads every run record in out/runs/, takes the boards whose outcome was `ok`, parses the
saved raw response named in the trace, and merges postings by id. The newer run's copy of
a posting wins. Boards that failed are listed as missing, never as empty (FILTER.md A3).

    python -B -m agent3.corpus          # print the summary and write out/corpus/manifest.json
"""
import hashlib
import json
import sys
from pathlib import Path

from agent3 import policy, providers

RUNS = policy.OUT / "runs"


def load(runs_dir: Path = RUNS) -> dict:
    """Return {"postings": {id: posting}, "sources": [...], "missing": [...]}.

    Each posting gains "board" (e.g. "ashby:snowflake"), "first_seen_run" and "last_seen_run".
    """
    postings, sources, missing = {}, [], []
    for rec in sorted((json.loads(p.read_text(encoding="utf-8")) for p in Path(runs_dir).glob("*.json")),
                      key=lambda r: r["run_id"]):
        raw_by_board = {e["board"]: e["raw"] for e in rec["trace"] if e["event"] == "request" and e.get("raw")}
        for board_key, outcome in rec["boards"].items():
            if outcome["outcome"] != "ok":
                missing.append({"run_id": rec["run_id"], "board": board_key, "outcome": outcome["outcome"],
                                "detail": outcome["detail"]})
                continue
            raw_path = policy.check_read(raw_by_board[board_key])
            body = raw_path.read_bytes()
            ats, board = board_key.split(":", 1)
            parsed = providers.parse(ats, json.loads(body), board)
            sources.append({"run_id": rec["run_id"], "board": board_key, "raw": raw_by_board[board_key],
                            "sha256": hashlib.sha256(body).hexdigest(), "postings": len(parsed)})
            for p in parsed:
                first = postings.get(p["id"], {}).get("first_seen_run", rec["run_id"])
                postings[p["id"]] = {**p, "board": board_key, "first_seen_run": first, "last_seen_run": rec["run_id"]}
    return {"postings": postings, "sources": sources, "missing": missing}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    c = load()
    by_board = {}
    for p in c["postings"].values():
        by_board[p["board"]] = by_board.get(p["board"], 0) + 1
    latest = max(s["run_id"] for s in c["sources"])
    still_listed = sum(1 for p in c["postings"].values() if p["last_seen_run"] == latest)
    print(f"corpus: {len(c['postings'])} distinct postings; per board {by_board}")
    print(f"still listed in the latest run ({latest}): {still_listed}; seen only earlier: {len(c['postings']) - still_listed}")
    for s in c["sources"]:
        print(f"  source {s['run_id']} {s['board']}: {s['postings']} postings  sha256 {s['sha256'][:16]}…  {s['raw']}")
    for m in c["missing"]:
        print(f"  MISSING {m['run_id']} {m['board']}: {m['outcome']} ({m['detail']}) -> no data: I cannot tell")
    manifest = {"sources": c["sources"], "missing": c["missing"],
                "postings": {pid: {k: p[k] for k in ("board", "title", "first_seen_run", "last_seen_run")}
                             for pid, p in sorted(c["postings"].items())}}
    policy.write_bytes(policy.OUT / "corpus" / "manifest.json",
                       (json.dumps(manifest, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
