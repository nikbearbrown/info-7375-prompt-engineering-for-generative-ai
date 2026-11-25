"""The frozen corpus: every posting in the one collection run that FILTER.md says all of JS3 measures.

    python3 corpus.py              print per-board counts of the frozen corpus

config/corpus.json names the v1.0 run folder ("run") and, from FILTER.md v1.1, the supplement run folders
("supplement"). Postings are parsed from that folder's saved raw
responses (raw/*.json.gz), never fetched again. Each posting gets "board" ("system/token") and
"key" ("system/token/id"), a stable id used by labels, audits, and the tool server, and "corpus" ("v1.0" or
"v1.1 supplement"), so every number can be reported for each part and for both together.
"""
import gzip
import json
import sys

import adapters
from policy import Policy
from tools import Tools

CONFIG = "config/corpus.json"


def load(tools=None, config=CONFIG):
    """Return (the v1.0 run folder, every posting in the v1.0 run and the supplement runs)."""
    tools = tools or Tools(Policy())
    cfg = json.loads(tools.read_text(config))
    postings = _load_run(tools, cfg["run"], "v1.0")
    for run in cfg.get("supplement", []):
        postings += _load_run(tools, run, "v1.1 supplement")
    return cfg["run"], postings


def _load_run(tools, run, part):
    boards = json.loads(tools.read_text(f"{run}/run.json"))["results"]
    postings = []
    for name in tools.list_dir(f"{run}/raw"):
        if not name.endswith(".json.gz") or name.endswith("_board.json.gz"):
            continue
        system, token = name[: -len(".json.gz")].split("_", 1)
        board = f"{system}/{token}"
        if boards.get(board, {}).get("status") != "ok":
            continue  # a failed board is absent from the corpus, never "no postings"
        for p in adapters.parse({"system": system}, gzip.decompress(tools.read_bytes(f"{run}/raw/{name}"))):
            postings.append(dict(p, board=board, key=f"{board}/{p['id']}", corpus=part))
    return postings


def main():
    run, postings = load()
    counts = {}
    for p in postings:
        counts[(p["corpus"], p["board"])] = counts.get((p["corpus"], p["board"]), 0) + 1
    print(f"corpus: {run} plus supplement, {len(postings)} postings")
    for (part, board), n in counts.items():
        print(f"  {part:16} {board}: {n}")
    missing = sum(1 for p in postings if not p["text"])
    print(f"  postings with no description text: {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
