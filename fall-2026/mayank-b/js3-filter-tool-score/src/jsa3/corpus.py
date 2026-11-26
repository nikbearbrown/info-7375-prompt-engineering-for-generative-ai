"""The corpus: every posting in one fetch run's saved raw responses, read back from disk.

Reads only `runs/<fetch-run>/report.json` and the raw files it names, and checks each file's SHA-256
against the trace before parsing, so the filter never sees bytes the loop did not record.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsa import boards


class CorpusError(Exception):
    pass


def load(run_dir: str | Path) -> dict:
    """-> {"run": <run id>, "boards": {board: {"postings": n, "sha256": ..., "raw": ...} | {"error": ...}},
           "postings": [posting + {"board"}]} (de-duplicated by board + id, first occurrence kept)."""
    run_dir = Path(run_dir)
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    out, seen, info = [], set(), {}
    for res in report["results"]:
        board = res["board"]
        if res["result"] != "ok":
            info[board] = {"error": f"{res.get('error_kind')}: {res.get('error')}"}
            continue
        att = next(a for a in reversed(res["attempts"]) if a["kind"] == "ok")
        data = (run_dir / att["raw"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != att["sha256"]:
            raise CorpusError(f"{att['raw']}: SHA-256 does not match the trace")
        jobs = boards.parse(res["ats"], data)
        info[board] = {"postings": len(jobs), "sha256": att["sha256"], "raw": att["raw"],
                       "with_text": sum(1 for j in jobs if j["text"])}
        for j in jobs:
            key = (board, j["id"])
            if key in seen:
                continue
            seen.add(key)
            out.append(dict(j, board=board))
    return {"run": report["run_id"], "boards": info, "postings": out}


def by_id(corpus: dict) -> dict:
    """posting id -> posting. Ids are unique per board; across boards a clash is reported, not guessed."""
    idx, clash = {}, set()
    for p in corpus["postings"]:
        if p["id"] in idx:
            clash.add(p["id"])
        idx[p["id"]] = p
    for c in clash:
        idx.pop(c, None)
    return idx
