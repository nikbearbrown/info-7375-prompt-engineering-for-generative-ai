"""The JS3 corpus: every posting in one live run's saved raw responses,
read into one shape. Nothing is fetched here; the raw bytes are the source.

Each posting is a dict:
    key        "<ats>/<board>/<id>"   (unique across boards)
    ats, board, id
    title      the posting's own title
    locations  every location the posting names (list of strings)
    text       the posting's own description as plain text ("" if none)
    url        the public posting URL
    fields     which raw fields `text` was built from (for the evidence rules)

python3 -B -m agent.corpus runs/<stamp>-live      # prints counts per board
"""

import gzip
import hashlib
import html
import json
import pathlib
import re
import sys

RAW_NAME = re.compile(r"^(greenhouse|lever|ashby)-(.+)-attempt\d+-http200"
                      r"\.body\.gz$")


def strip_html(s):
    """HTML (possibly escaped once, as Greenhouse sends it) to plain text."""
    raw = html.unescape(s or "")
    raw = re.sub(r"(?i)<br\s*/?>|</(p|li|div|h\d)>", "\n", raw)
    no_tags = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(no_tags).replace("\xa0", " ")
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _greenhouse(board, data):
    for j in data["jobs"]:
        locs = [(j.get("location") or {}).get("name")]
        locs += [o.get("name") for o in j.get("offices") or []]
        yield {"id": str(j["id"]), "title": j.get("title") or "",
               "locations": locs, "text": strip_html(j.get("content")),
               "url": j.get("absolute_url"), "fields": ["content"]}


def _lever(board, data):
    for j in data:
        cats = j.get("categories") or {}
        locs = [cats.get("location")] + list(cats.get("allLocations") or [])
        parts, fields = [], []
        # descriptionPlain is Lever's opening + body; fall back to the parts.
        if j.get("descriptionPlain"):
            parts.append(j["descriptionPlain"]); fields.append("descriptionPlain")
        else:
            for f in ("openingPlain", "descriptionBodyPlain"):
                if j.get(f):
                    parts.append(j[f]); fields.append(f)
        for lst in j.get("lists") or []:
            parts.append(lst.get("text", "") + "\n" +
                         strip_html(lst.get("content")))
            fields.append("lists")
        if j.get("additionalPlain"):
            parts.append(j["additionalPlain"]); fields.append("additionalPlain")
        yield {"id": str(j["id"]), "title": j.get("text") or "",
               "locations": locs, "text": "\n".join(parts).strip(),
               "url": j.get("hostedUrl"), "fields": sorted(set(fields)),
               "country": j.get("country")}


def _ashby(board, data):
    for j in data["jobs"]:
        locs = [j.get("location")]
        locs += [s.get("location") for s in j.get("secondaryLocations") or []]
        yield {"id": str(j["id"]), "title": j.get("title") or "",
               "locations": locs, "text": (j.get("descriptionPlain") or "")
               .strip(), "url": j.get("jobUrl"),
               "fields": ["descriptionPlain"],
               "is_remote": j.get("isRemote")}


READERS = {"greenhouse": _greenhouse, "lever": _lever, "ashby": _ashby}


def load(run_dir):
    """All postings from a run folder's raw/*.http200.body.gz, sorted by key."""
    out = []
    for f in sorted(pathlib.Path(run_dir, "raw").glob("*.body.gz")):
        m = RAW_NAME.match(f.name)
        if not m:
            continue  # 404s and other non-200 bodies are not postings
        ats, board = m.groups()
        data = json.loads(gzip.decompress(f.read_bytes()))
        for p in READERS[ats](board, data):
            p["locations"] = [l for l in dict.fromkeys(p["locations"]) if l]
            p.update(ats=ats, board=board, key=f"{ats}/{board}/{p['id']}")
            out.append(p)
    out.sort(key=lambda p: p["key"])
    keys = [p["key"] for p in out]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate posting keys in corpus")
    return out


def raw_hashes(run_dir):
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(pathlib.Path(run_dir, "raw").glob("*.body.gz"))}


def main(argv=None):
    run_dir = (argv or sys.argv[1:])[0]
    posts = load(run_dir)
    by = {}
    for p in posts:
        by.setdefault(f"{p['ats']}/{p['board']}", []).append(p)
    for k, v in sorted(by.items()):
        empty = sum(1 for p in v if not p["text"])
        print(f"{k:25} {len(v):5} postings, {empty} with no text")
    print(f"{'total':25} {len(posts):5}")


if __name__ == "__main__":
    main()
