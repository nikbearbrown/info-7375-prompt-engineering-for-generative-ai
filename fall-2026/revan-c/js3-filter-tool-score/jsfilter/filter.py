"""The filter in FILTER.md v1: rules R1-R6, the score, the threshold, and the audit view.

Every number here is hand-set in FILTER.md v1; none is fitted. This module reads files and never writes them.
"""
import hashlib
import json
import pathlib

from jsagent.text import find_original, normalize, strip_html, contains_sequence

FILTER_VERSION = "v1"

# R1 and the role weight. The phrases are the persona's target_titles; FILTER.md weights two of them higher.
ROLE_WEIGHT = {"backend engineer": 3, "platform engineer": 3,
               "software engineer": 2, "devops engineer": 2, "site reliability engineer": 2}
SENIORITY_WORDS = ("senior", "sr", "principal", "staff", "lead", "director", "manager")       # R2
ROLE_TYPE_WORDS = ("frontend", "front end", "mobile", "ios", "android")                      # R3
TOPIC_PHRASES = ("backend", "back end", "platform", "infrastructure", "api", "distributed systems",
                 "cloud", "devops", "site reliability", "kubernetes")                        # R5
SKILL_CATEGORIES = ("languages", "backend_automation", "database_cloud", "devops_cicd")      # R6
MIN_SKILLS = 2
TOPIC_CAP = 2
SKILL_CAP = 3
THRESHOLD = 6

FATES = ("kept", "below_threshold", "hard_rule_reject", "unscorable")
REJECT_FATES = ("hard_rule_reject", "below_threshold")

# FILTER.md section 3: the dated snapshot and where each board's raw body is.
SNAPSHOT_TRACE = "runs/js2/2026-11-10T06-33-08Z_normal.json"
SNAPSHOT = (
    ("klaviyo", "greenhouse", "evidence/js2/2026-11-10T06-33-08Z_klaviyo.body"),
    ("duolingo", "greenhouse", "evidence/js2/2026-11-10T06-33-08Z_duolingo.body"),
    ("patchmypc", "lever", "evidence/js2/2026-11-10T06-33-08Z_patchmypc.body"),
)
EXPECTED_COUNTS = {"klaviyo": 149, "duolingo": 61, "patchmypc": 5}


# ---- Loading ------------------------------------------------------------------------------

def _str(value):
    return value if isinstance(value, str) and value.strip() else None


def _greenhouse_posting(job):
    location = job.get("location") if isinstance(job.get("location"), dict) else {}
    pid = job.get("id")
    return {
        "id": str(pid) if isinstance(pid, (int, str)) and not isinstance(pid, bool) and str(pid) else None,
        "title": _str(job.get("title")),
        "location": _str(location.get("name")),
        "workplace_type": None,
        "description": strip_html(job["content"]) if _str(job.get("content")) else None,
        "url": _str(job.get("absolute_url")),
        "fields": {"title": "title", "location": "location.name", "description": "content"},
    }


def _lever_posting(item):
    parts = [item.get("description")]
    parts += [e.get("content") for e in item.get("lists") or [] if isinstance(e, dict)]
    parts.append(item.get("additional"))
    parts = [p for p in parts if _str(p)]
    categories = item.get("categories") if isinstance(item.get("categories"), dict) else {}
    return {
        "id": _str(item.get("id")),
        "title": _str(item.get("text")),
        "location": _str(categories.get("location")),
        "workplace_type": _str(item.get("workplaceType")),
        "description": strip_html(" \n".join(parts)) if _str(item.get("description")) else None,
        "url": _str(item.get("hostedUrl")),
        "fields": {"title": "text", "location": "categories.location + workplaceType",
                   "description": "description + lists[].content + additional"},
    }


def load_board(board, ats, raw, source_path):
    """One board's postings, or status `unknown` with the reason. Never an empty `ok` (FILTER.md 3, W4)."""
    base = {"board": board, "ats": ats, "source_path": source_path}
    if raw is None:
        return {**base, "status": "unknown", "error": "board body missing", "postings": []}
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        return {**base, "status": "unknown", "error": f"not JSON: {exc.__class__.__name__}", "postings": []}
    items = data.get("jobs") if ats == "greenhouse" and isinstance(data, dict) else data
    if not isinstance(items, list):
        return {**base, "status": "unknown", "error": f"not a {ats} postings list", "postings": []}
    if not items:
        return {**base, "status": "unknown", "error": "empty postings list", "postings": []}
    build = _greenhouse_posting if ats == "greenhouse" else _lever_posting
    postings = []
    for i, item in enumerate(items):
        p = build(item if isinstance(item, dict) else {})
        p.update(board=board, source_path=source_path, index=i)
        p["missing"] = [f for f in ("id", "title", "location", "description", "url") if p[f] is None]
        if p["id"] is None:
            p["id"] = f"<missing id at index {i}>"
        postings.append(p)
    return {**base, "status": "ok", "error": None, "postings": postings}


def load_snapshot(root):
    root = pathlib.Path(root)
    boards = []
    for board, ats, rel in SNAPSHOT:
        path = root / rel
        raw = path.read_bytes() if path.is_file() else None
        boards.append(load_board(board, ats, raw, rel))
    return boards


# ---- Rules --------------------------------------------------------------------------------

def _phrases_in(text_norm, phrases):
    return [p for p in phrases if contains_sequence(text_norm, normalize(p))]


def _quote(text, phrase, width=90):
    """The phrase as written, with surrounding words, for the audit and the shortlist."""
    found = find_original(text, phrase)
    if not found:
        return None
    at = text.find(found)
    start, end = max(0, at - width), min(len(text), at + len(found) + width)
    return ("…" if start else "") + " ".join(text[start:end].split()) + ("…" if end < len(text) else "")


def score_posting(resume, posting):
    """One audit-view row: every rule result, the score components, the total, and the fate."""
    row = {"board": posting["board"], "id": posting["id"], "title": posting["title"],
           "location": posting["location"], "workplace_type": posting["workplace_type"],
           "url": posting["url"], "source_path": posting["source_path"], "index": posting["index"],
           "source_fields": posting["fields"], "missing": list(posting["missing"]),
           "filter_version": FILTER_VERSION}
    if posting["missing"]:
        return {**row, "rules": {}, "components": None, "total": None, "failed_rules": [],
                "zero_topic": None, "zero_skill": None, "fate": "unscorable", "evidence": {}}

    title_n = normalize(posting["title"])
    desc = posting["description"]
    desc_n = normalize(desc)

    roles = _phrases_in(title_n, ROLE_WEIGHT)
    seniority = _phrases_in(title_n, SENIORITY_WORDS)
    role_type = _phrases_in(title_n, ROLE_TYPE_WORDS)
    loc_n = normalize(posting["location"])
    city = normalize(resume["personal"]["location"].split(",")[0])
    remote_loc = contains_sequence(loc_n, "remote")
    remote_wpt = posting["workplace_type"] is not None and normalize(posting["workplace_type"]) == "remote"
    location_ok = contains_sequence(loc_n, city) or remote_loc or remote_wpt
    topics = _phrases_in(desc_n, TOPIC_PHRASES)

    skills, seen = [], set()
    for category in SKILL_CATEGORIES:
        for skill in resume["skills"][category]:
            key = normalize(skill)
            if key not in seen and contains_sequence(desc_n, key):
                seen.add(key)
                skills.append(skill)

    rules = {
        "R1": {"passed": bool(roles), "matched": roles, "field": posting["fields"]["title"]},
        "R2": {"passed": not seniority, "matched": seniority, "field": posting["fields"]["title"]},
        "R3": {"passed": not role_type, "matched": role_type, "field": posting["fields"]["title"]},
        "R4": {"passed": location_ok, "matched": [w for w, hit in
                                                  ((city, contains_sequence(loc_n, city)),
                                                   ("remote (location)", remote_loc),
                                                   ("remote (workplaceType)", remote_wpt)) if hit],
               "field": posting["fields"]["location"]},
        "R5": {"passed": bool(topics), "matched": topics, "field": posting["fields"]["description"]},
        "R6": {"passed": len(skills) >= MIN_SKILLS, "matched": skills,
               "field": posting["fields"]["description"]},
    }
    components = {"role": max((ROLE_WEIGHT[r] for r in roles), default=0),
                  "topic": min(len(topics), TOPIC_CAP),
                  "skill": min(len(skills), SKILL_CAP)}
    total = sum(components.values())
    failed = [k for k, v in rules.items() if not v["passed"]]
    fate = "hard_rule_reject" if failed else ("kept" if total >= THRESHOLD else "below_threshold")
    evidence = {p: _quote(desc, p) for p in topics + skills}
    return {**row, "rules": rules, "components": components, "total": total, "failed_rules": failed,
            "zero_topic": not topics, "zero_skill": not skills, "fate": fate, "evidence": evidence}


# ---- Whole run ----------------------------------------------------------------------------

def run_filter(resume, boards):
    rows, summary = [], {}
    for b in boards:
        if b["status"] != "ok":
            summary[b["board"]] = {"status": "unknown", "error": b["error"], "source_path": b["source_path"],
                                   "scored": "unknown", "kept": "unknown"}
            continue
        board_rows = [score_posting(resume, p) for p in b["postings"]]
        rows += board_rows
        counts = {f: sum(r["fate"] == f for r in board_rows) for f in FATES}
        summary[b["board"]] = {"status": "ok", "error": None, "source_path": b["source_path"],
                               "scored": len(board_rows), **counts}
    return {"filter_version": FILTER_VERSION, "boards": summary, "rows": rows, "kept": rank(rows)}


def rank(rows):
    """Kept postings: total descending, then board and id ascending (FILTER.md 1; W3)."""
    return sorted((r for r in rows if r["fate"] == "kept"), key=lambda r: (-r["total"], r["board"], r["id"]))


def closest_calls(rows):
    """FILTER.md 1: all hard rules pass with total THRESHOLD-1, or total >= THRESHOLD with one failed rule."""
    picked = [r for r in rows if r["fate"] != "unscorable" and (
        (not r["failed_rules"] and r["total"] == THRESHOLD - 1)
        or (r["total"] >= THRESHOLD and len(r["failed_rules"]) == 1))]
    return sorted(picked, key=lambda r: (r["board"], r["id"]))


def _seeded_order(rows, seed):
    # A hash of (seed, board, id) gives an order that depends only on the seed and the keys,
    # never on input order or Python's per-process hash salt.
    return sorted(rows, key=lambda r: hashlib.sha256(f"{seed}|{r['board']}|{r['id']}".encode()).hexdigest())


def sample_rejects(rows, n, seed):
    rejects = [r for r in rows if r["fate"] in REJECT_FATES]
    if len(rejects) < n:
        raise ValueError(f"only {len(rejects)} rejects; cannot sample {n}")
    return _seeded_order(rejects, seed)[:n]


def sample_kept(rows, n, seed):
    return _seeded_order([r for r in rows if r["fate"] == "kept"], seed)[:n]
