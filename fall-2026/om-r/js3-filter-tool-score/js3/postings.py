"""Turn a JS2 run report (logs/run_<stamp>.json) back into filterable
postings, reading the raw evidence files that run saved.

JS2's boards.parse_page normalizes postings to {id, title, url} and drops the
body text, so content is read here from the raw responses, exactly as
received:

  Greenhouse (gitlab, stripe): id, title, content (HTML-escaped HTML), absolute_url
  Lever (palantir):            id, text, descriptionPlain, hostedUrl

FILTER.md "Expected sources" names Lever's descriptionPlain as the content
field, so that is what "content" is for palantir. Lever's separate `lists`
(e.g. "What We Require") and `additionalPlain` are NOT folded in; they are
kept as `lever_extra` so the effect of that spec choice can be measured
without changing the filter.

Duplicate ids within a board are collapsed first-one-wins (JS2's repeat
rule), and the per-board count is checked against the run report's
postings_in_response so this reader can't silently disagree with the loop.
"""
import json
from pathlib import Path

ATS = {"gitlab": "greenhouse", "stripe": "greenhouse", "palantir": "lever"}


class CountMismatch(ValueError):
    pass


def _lever_extra(it):
    parts = []
    for lst in it.get("lists") or []:
        parts.append(lst.get("text") or "")
        parts.append(lst.get("content") or "")  # HTML <li> items
    parts.append(it.get("additionalPlain") or "")
    return "\n".join(p for p in parts if p)


def _normalize(board, it):
    if ATS[board] == "greenhouse":
        return {"board": board, "id": it.get("id"), "title": it.get("title"),
                "content": it.get("content"), "url": it.get("absolute_url")}
    return {"board": board, "id": it.get("id"), "title": it.get("text"),
            "content": it.get("descriptionPlain"), "url": it.get("hostedUrl"),
            "lever_extra": _lever_extra(it)}


def load_run(report_path, root):
    root = Path(root)
    report = json.loads(Path(report_path).read_text())
    postings, per_board = [], {}
    for board, entry in report["boards"].items():
        if entry.get("board_status") != "ok":
            per_board[board] = {"status": entry.get("board_status"), "error": entry.get("error"), "postings": 0}
            continue
        seen, items = set(), []
        for rel in entry["evidence_files"]:
            data = json.loads((root / rel).read_bytes())
            raw_items = data["jobs"] if ATS[board] == "greenhouse" else data
            for it in raw_items:
                p = _normalize(board, it)
                if p["id"] not in seen:
                    seen.add(p["id"])
                    items.append(p)
        if len(items) != entry["postings_in_response"]:
            raise CountMismatch(f"{board}: read {len(items)} postings from evidence, "
                                f"run report says {entry['postings_in_response']}")
        per_board[board] = {"status": "ok", "postings": len(items), "evidence_files": entry["evidence_files"]}
        postings.extend(items)
    return report, postings, per_board
