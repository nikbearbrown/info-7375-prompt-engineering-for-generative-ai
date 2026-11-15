"""Turn a run's saved raw responses into postings: board, id, title, location, country, text, url.

Fields are the ones FILTER.md section 4 names. A missing field stays empty; nothing is guessed.
A posting without an id or title is listed as unreadable, not judged.
"""
import json
import os

from filter import plain_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _greenhouse(board, body):
    for j in body.get("jobs", []):
        yield {"board": board, "id": str(j.get("id") or ""), "title": j.get("title"),
               "location": (j.get("location") or {}).get("name"), "country": None,
               "text": plain_text(j.get("content")), "url": j.get("absolute_url")}


def _lever(board, body):
    for j in body:
        parts = [j.get("descriptionPlain") or ""]
        for lst in j.get("lists") or []:
            parts.append((lst.get("text") or "") + "\n" + plain_text(lst.get("content")))
        parts.append(j.get("additionalPlain") or "")
        yield {"board": board, "id": str(j.get("id") or ""), "title": j.get("text"),
               "location": (j.get("categories") or {}).get("location"), "country": j.get("country"),
               "text": "\n".join(p.strip() for p in parts if p and p.strip()), "url": j.get("hostedUrl")}


def _ashby(board, body):
    for j in body.get("jobs", []):
        if j.get("isListed") is False:
            continue
        addr = ((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry")
        yield {"board": board, "id": str(j.get("id") or ""), "title": j.get("title"),
               "location": j.get("location"), "country": addr,
               "text": (j.get("descriptionPlain") or "").strip(), "url": j.get("jobUrl")}


PARSERS = {"greenhouse": _greenhouse, "lever": _lever, "ashby": _ashby}


def load_run(run_id):
    """-> (postings, unreadable, manifest)"""
    run_dir = os.path.join(ROOT, "runs", run_id)
    with open(os.path.join(run_dir, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    postings, unreadable = [], []
    for b in manifest["boards"]:
        if b["status"] != "collected":
            continue
        with open(os.path.join(run_dir, b["raw"]), encoding="utf-8") as f:
            body = json.load(f)
        for p in PARSERS[b["ats"]](b["board"], body):
            (postings if p["id"] and p["title"] else unreadable).append(p)
    return postings, unreadable, manifest
