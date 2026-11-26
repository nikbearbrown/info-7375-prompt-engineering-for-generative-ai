"""The FILTER.md score. All numbers come from filters/<version>.json; this file holds no weights.

score = R (role, title) + S (level, title) + T (topic groups, capped) + E (early career) + Y (years)
verdict: keep if score >= threshold; cannot_tell if title or description is empty after normalization.

The small functions below (phrase_in, topic_phrase_allowed, level_fields, topic_points,
missing_fields) are the seams tests/mutation_check.py replaces to plant wrong versions W1-W5.
"""
import json
import re
from pathlib import Path

from inherited.rules import contains_phrase, normalize

from .text import quote_for, readable, segments

ROOT = Path(__file__).resolve().parent.parent
FIELD = {"title": "posting.title", "description": "posting.description"}


def load_filter(version):
    return json.loads((ROOT / "filters" / f"{version}.json").read_text(encoding="utf-8"))


def phrase_in(norm_text, phrase):                      # W1 seam
    return contains_phrase(norm_text, phrase)


def topic_phrase_allowed(phrase, board, cfg):         # W2 seam
    if not cfg["topic"].get("ignore_employer_words_on_own_board"):
        return True
    return not (set(phrase.split()) & set(normalize(board).split()))


def level_fields(cfg):                                 # W5 seam
    return cfg["level"]["fields"]


def topic_points(groups, cfg):                         # W3 seam
    uncapped = len(groups) * cfg["topic"]["points_per_group"]
    return min(uncapped, cfg["topic"]["cap"]), uncapped


def load_boilerplate_segments():                       # W6 seam (v1.1 false-friend fix)
    from .boilerplate import load
    return load()


def missing_fields(norm):                              # W4 seam
    return [FIELD[f] for f in ("title", "description") if not norm[f]]


def _first(fields, phrases, texts, norm):
    """First (phrase, field, quote) for any phrase in any of the fields, or None."""
    for phrase in phrases:
        for f in fields:
            if phrase_in(norm[f], phrase):
                return {"phrase": phrase, "field": FIELD[f], "quote": quote_for(texts[f], phrase)}
    return None


def score_posting(posting, cfg):
    texts = {"title": " ".join((posting.get("title") or "").split()),
             "description": readable(posting.get("text"))}
    norm = {f: normalize(t) for f, t in texts.items()}
    missing = missing_fields(norm)
    out = {"kind": "JS3 FILTER SCORE", "key": posting.get("key"), "filter_version": cfg["version"],
           "threshold": cfg["threshold"], "missing": missing}
    if FIELD["title"] in missing:
        return {**out, "verdict": "cannot_tell", "score": None, "parts": None,
                "reason": "posting.title is empty after normalization: role and level cannot be read"}

    # R: highest tier only
    r = {"points": 0, "tier": None, "match": None}
    for tier in cfg["role"]["tiers"]:
        m = _first(cfg["role"]["fields"], tier["phrases"], texts, norm)
        if m:
            r = {"points": tier["points"], "tier": tier["name"], "match": m}
            break

    # S: level words
    m = _first(level_fields(cfg), cfg["level"]["phrases"], texts, norm)
    s = {"points": cfg["level"]["points"] if m else 0, "match": m}

    # T: distinct groups, capped. Optionally (v1.1 candidate C-a) on the description with board boilerplate removed.
    t_texts, t_norm = texts, norm
    if cfg["topic"].get("ignore_boilerplate_segments"):
        boiler = load_boilerplate_segments().get(posting.get("board") or "", set())
        kept = "\n".join(sg for sg in segments(texts["description"]) if normalize(sg) not in boiler)
        t_texts = {**texts, "description": kept}
        t_norm = {**norm, "description": normalize(kept)}
    groups = []
    for name, phrases in cfg["topic"]["groups"].items():
        allowed = [p for p in phrases if topic_phrase_allowed(p, posting.get("board") or "", cfg)]
        m = _first(cfg["topic"]["fields"], allowed, t_texts, t_norm)
        if m:
            groups.append({"group": name, **m})
    t_points, t_uncapped = topic_points(groups, cfg)
    t = {"points": t_points, "uncapped": t_uncapped, "cap": cfg["topic"]["cap"], "groups": groups}

    # E: early-career phrase
    m = _first(cfg["early_career"]["fields"], cfg["early_career"]["phrases"], texts, norm)
    e = {"points": cfg["early_career"]["points"] if m else 0, "match": m}

    # Y: smallest first-number of every "N years" phrase in the normalized description
    rx = re.compile(cfg["years"]["regex_on_normalized"])
    hits = [(int(mt.group(1)), mt.group(0)) for mt in rx.finditer(norm["description"])]
    n = min((h[0] for h in hits), default=None)
    y_points = 0
    if n is not None:
        for band in cfg["years"]["bands"]:
            if n >= band["min_n"]:
                y_points = band["points"]
                break
    y = {"points": y_points, "N": n,
         "matches": [{"normalized": h[1], "quote": quote_for(texts["description"], h[1])} for h in hits]}

    total = r["points"] + s["points"] + t["points"] + e["points"] + y["points"]
    if missing:
        verdict = "cannot_tell"
    else:
        verdict = "keep" if total >= cfg["threshold"] else "reject"
    return {**out, "verdict": verdict, "score": total,
            "arithmetic": f"R {r['points']} + S {s['points']} + T {t['points']} + E {e['points']} + Y {y['points']} = {total}",
            "parts": {"R": r, "S": s, "T": t, "E": e, "Y": y}}
