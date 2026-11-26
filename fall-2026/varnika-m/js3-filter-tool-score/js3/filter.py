"""The filter of FILTER.md section 1: score 0-5, an outcome, one job per group, and a ranking."""

import hashlib
import html
import re

from js3 import rule

KEEP, CLOSE = 5, 4  # FILTER.md: keep at 5 of 5 (JS1); a close call is one rule short
VERSION = "v1.1"
# v1.1 A: R3 also accepts "D.C." after a comma (JS1's rule knew only "DC").
DC = re.compile(r",\s*D\.C\.?(?![A-Za-z0-9])")
# v1.1 B: R2 fails "must be graduating" in December 2026 or later; he finished his degree in May 2026.
GRADUATING = re.compile(r"(?i)must be (?:planning on )?graduating[^.;\n]{0,80}")
LATER = re.compile(r"(?i)\b(?:20(?:2[7-9]|[3-9]\d))\b|\b(?:dec(?:ember)?|winter|fall)\.? *2026\b")
PREFERRED = re.compile(r"(?i)\b(preferred|nice[- ]to[- ]haves?|bonus|(?:is |are |be )?a plus|strong candidates may also"
                       r"|you might also|not required|extra credit|ideally)\b")
HEADING = re.compile(r"(?is)(<h[1-6][^>]*>.*?</h[1-6]>|<(?:strong|b)>[^<]{3,160}</(?:strong|b)>)")


def text_of(markup):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup))).strip()


def must_have_markup(content):
    """M1 (FILTER.md section 5): the description without preferred / nice-to-have parts.

    A heading that names preferred qualifications drops everything up to the next heading,
    and any single line that says "preferred", "nice to have", "a plus"... is dropped too.
    """
    markup = html.unescape(content or "")
    kept, skipping = [], False
    for part in HEADING.split(markup):
        if HEADING.fullmatch(part or ""):
            skipping = bool(PREFERRED.search(text_of(part)))
            if not skipping:
                kept.append(part)
            continue
        if skipping:
            continue
        lines = re.split(r"(?i)</li>|</p>|<br\s*/?>|\n", part)
        kept.extend(line for line in lines if not PREFERRED.search(text_of(line)))
    return html.escape(" ".join(kept))


def missing_fields(posting):
    missing = [name for name, value in (("title", posting.get("title")),
                                        ("location", (posting.get("location") or {}).get("name")),
                                        ("description", posting.get("content"))) if not (value or "").strip()]
    return missing


def apply_v1_1(posting, checks):
    """The two rules added in FILTER.md v1.1, on top of JS1's checks (which stay byte-identical in rule.py)."""
    r2, r3 = checks[1], checks[2]
    places = [part.strip() for part in re.split(r"[|;]", r3["posting_value"] or "")]
    dc = [part for part in places if DC.search(part)]
    if dc and not r3["passed"]:
        r3.update(passed=True, us_locations=dc, explanation="US location(s): %s (v1.1: D.C.)" % "; ".join(dc))
    text = text_of(html.unescape(posting.get("content") or ""))
    later = [m.group(0) for m in GRADUATING.finditer(text) if LATER.search(m.group(0))]
    if later and r2["passed"]:
        r2.update(passed=False, graduation=later[0],
                  explanation='v1.1: "%s"; he finished his degree in May 2026' % later[0].strip())
    return checks


def evaluate(posting, resume, must_haves_only=False, keep_at=KEEP, version=VERSION):
    """One posting: the JS1 record, its score, and its outcome (keep, close call, reject, cannot tell)."""
    missing = missing_fields(posting)
    if missing:
        return {"key": posting.get("key"), "score": None, "outcome": "cannot_tell", "missing": missing,
                "checks": [], "skills": []}
    scored = dict(posting, content=must_have_markup(posting["content"])) if must_haves_only else posting
    verdict = rule.judge(scored, resume)
    if must_haves_only:  # only R4 reads the must-have text; R5 still reads the whole description
        full = rule.judge(posting, resume)
        verdict["checks"] = [c if c["rule"] == "R4" else f for c, f in zip(verdict["checks"], full["checks"])]
    if version == "v1.1":
        apply_v1_1(posting, verdict["checks"])
    score = sum(c["passed"] for c in verdict["checks"])
    outcome = "keep" if score >= keep_at else "close_call" if score == keep_at - 1 else "reject"
    skills = next(c for c in verdict["checks"] if c["rule"] == "R5")["matches"]
    return {"key": posting.get("key"), "version": version, "score": score, "outcome": outcome, "missing": [],
            "checks": verdict["checks"], "skills": [m["skill"] for m in skills],
            "failed": [c["rule"] for c in verdict["checks"] if not c["passed"]]}


def group_key(posting):
    """One job, many ids: same company, same title, same description (FILTER.md section 1, WF5)."""
    digest = hashlib.sha256((posting.get("content") or "").encode("utf-8")).hexdigest()[:16]
    return "%s | %s | %s" % (posting.get("company_name"), (posting.get("title") or "").strip().lower(), digest)


def rank_key(posting, result):
    """Different skills matched, highest first, then title (FILTER.md section 1, WF3)."""
    return (-len(set(s.lower() for s in result["skills"])), (posting.get("title") or "").lower())


def run_filter(postings, resume, **options):
    results = {p["key"]: evaluate(p, resume, **options) for p in postings}
    groups = {}
    for p in postings:
        if results[p["key"]]["outcome"] == "keep":
            groups.setdefault(group_key(p), []).append(p)
    shortlist = []
    for members in groups.values():
        first = members[0]
        shortlist.append({"posting": first, "result": results[first["key"]],
                          "ids": [m["key"] for m in members],
                          "locations": [(m.get("location") or {}).get("name") for m in members]})
    shortlist.sort(key=lambda item: rank_key(item["posting"], item["result"]))
    return results, shortlist
