"""The frozen corpus: every posting in the one collection run that FILTER.md says all of JS3 measures.

    python3 corpus.py              print per-board counts of the frozen corpus

config/corpus.json names the run folder. Postings are parsed from that folder's saved raw
responses (raw/*.json.gz), never fetched again. Each posting gets "board" ("system/token") and
"key" ("system/token/id"), a stable id used by labels, audits, and the tool server.
"""
import gzip
import json
import sys

import adapters
from policy import Policy
from tools import Tools

CONFIG = "config/corpus.json"


def load(tools=None, config=CONFIG):
    tools = tools or Tools(Policy())
    run = json.loads(tools.read_text(config))["run"]
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
            postings.append(dict(p, board=board, key=f"{board}/{p['id']}"))
    return run, postings


def main():
    run, postings = load()
    counts = {}
    for p in postings:
        counts[p["board"]] = counts.get(p["board"], 0) + 1
    print(f"corpus: {run}, {len(postings)} postings")
    for board, n in counts.items():
        print(f"  {board}: {n}")
    missing = sum(1 for p in postings if not p["text"])
    print(f"  postings with no description text: {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
