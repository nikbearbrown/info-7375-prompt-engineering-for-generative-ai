"""The one capability offered as a tool: score_posting (read-only, frozen corpus, filter v1.0).

    python3 serve.py [--transcript transcripts/NAME.jsonl]

Held-out postings are refused (tool error) so that no client can read their sealed predictions
before the one-change comparison is frozen (FILTER.md section 8).
"""
from __future__ import annotations

import sys

from .corpus import load
from .filter import Filter, load_config
from .heldout import heldout_keys
from .mcp_server import FOLDER, Server, Tool, Transcript

VERSION = "v1.0"
SCHEMA = {"type": "object",
          "properties": {"key": {"type": "string",
                                 "description": "provider/board/id, e.g. greenhouse/klaviyo/8041054003"}},
          "required": ["key"], "additionalProperties": False}
DESCRIPTION = ("Score one job posting from a frozen snapshot (collected 2026-11-09, 805 postings from 5 public job "
               "boards) with filter " + VERSION + " (FILTER.md). Returns KEEP / REJECT / REVIEW, the score and its "
               "components, matched topic words with snippets, and the location reading. Read-only: it cannot "
               "fetch new postings, apply, email, message, log in, or write anything. A REVIEW means the filter "
               "cannot tell. A KEEP means worth reading, not qualified or likely to be hired. Held-out postings are refused.")


def make_handler():
    postings = {p["key"]: p for p in load()["postings"]}
    flt = Filter(load_config(VERSION))
    sealed = heldout_keys()

    def score_posting(args: dict) -> dict:
        key = args["key"].strip()
        if key in sealed:
            return {"_is_error": True, "error": "this posting is in the sealed held-out set; not scored by this tool"}
        p = postings.get(key)
        if p is None:
            return {"_is_error": True, "error": f"no posting with key {key!r} in the 2026-11-09 snapshot"}
        d = flt.classify(p)
        keep = ("key", "title", "url", "filter_version", "decision", "reasons", "score", "components",
                "score_is_diagnostic", "n_topic_groups", "disclosure")
        out = {k: d[k] for k in keep if k in d}
        out["topics"] = [{"group": t["group"], "matched": t["alias"], "snippet": t["snippet"]} for t in d.get("topics", [])]
        loc = d.get("location", {})
        out["location"] = {"status": loc.get("status"),
                           "best": (loc.get("best") or {}).get("value"),
                           "alternatives": [{"value": a["value"], "kind": a["kind"]} for a in loc.get("alternatives", [])]}
        out["entry_signals"] = d.get("gate", {}).get("entry_signals", [])
        out["snapshot"] = "2026-11-09T20:21:52Z; not proof the job is still open"
        return out

    return score_posting


def build_server(transcript_path=None) -> Server:
    return Server([Tool("score_posting", DESCRIPTION, SCHEMA, make_handler())], Transcript(transcript_path))


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = None
    if argv[:1] == ["--transcript"] and len(argv) == 2:
        path = FOLDER / argv[1] if not argv[1].startswith("/") else argv[1]
    elif argv:
        print("usage: python3 serve.py [--transcript transcripts/NAME.jsonl]", file=sys.stderr)
        return 2
    build_server(path).serve()
    return 0
