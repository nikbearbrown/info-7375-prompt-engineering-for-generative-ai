"""The JS3 corpus: every posting in one jobwatch run's saved raw bodies, read the way FILTER.md
'The expected sources' says: Greenhouse id, title, location.name and content; Ashby jobUrl,
title, location and descriptionHtml; each with its board name and capture time.

Each body is checked against the sha256 recorded in the run's trace before it is read."""

import gzip
import hashlib
import json
from pathlib import Path

from jobwatch import ats
from jobwatch.screen import Item

# FILTER.md 'The expected sources', the fields each ATS is read for.
LISTED_FIELDS = {
    "greenhouse": ("id", "title", "location", "content"),
    "ashby": ("jobUrl", "title", "location", "descriptionHtml"),
}


class CorpusError(Exception):
    pass


def _body(run_dir, event):
    raw = gzip.decompress((run_dir / event["raw"]).read_bytes())
    if hashlib.sha256(raw).hexdigest() != event["sha256"]:
        raise CorpusError(f"{event['raw']} does not match the sha256 in trace.json")
    return raw


def load(run_dir):
    """-> (items, boards). A board whose request was not usable has count None and names its failure."""
    run_dir = Path(run_dir)
    trace = json.loads((run_dir / "trace.json").read_text(encoding="utf-8"))
    items, boards = [], []
    for event in trace["events"]:
        if event.get("event") != "request":
            continue
        name = event["board"]
        if event.get("outcome") != "usable" or not event.get("raw"):
            boards.append({"board": name, "count": None,
                           "failure": event.get("reason") or event.get("outcome") or "no saved body"})
            continue
        postings = ats.parse(name.split("/")[0], _body(run_dir, event))
        for posting in postings:
            items.append(Item(board=name, key=posting.key, title=posting.title,
                              location=posting.location_name, description=posting.content,
                              captured_at=event["at"]))
        boards.append({"board": name, "count": len(postings), "failure": None,
                       "captured_at": event["at"], "sha256": event["sha256"], "raw": event["raw"]})
    return items, boards


def raw_jobs(run_dir, board):
    """The board's job objects exactly as saved, for the field inventory."""
    run_dir = Path(run_dir)
    trace = json.loads((run_dir / "trace.json").read_text(encoding="utf-8"))
    for event in trace["events"]:
        if event.get("event") == "request" and event["board"] == board and event.get("raw"):
            return json.loads(_body(run_dir, event))["jobs"]
    return None
