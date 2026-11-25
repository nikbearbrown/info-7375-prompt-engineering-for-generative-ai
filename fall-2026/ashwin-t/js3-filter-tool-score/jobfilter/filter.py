"""The JS3 filter: FILTER.md, executed. Every word, weight and threshold comes from filters/<version>.json.

Decisions: KEEP, REJECT or REVIEW. REVIEW means "I cannot tell" (FILTER.md sections 3 and 4). It is neither
a rejection nor a shortlist place. Each behavior is one method so that a wrong version
(wrong_versions.py) can replace exactly one and the tests can show which one they catch.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Optional

from .text import normalize as _html_normalize

FILTERS = Path(__file__).resolve().parent.parent / "filters"
KEEP, REJECT, REVIEW = "KEEP", "REJECT", "REVIEW"
_DASHES = re.compile(r"[-‐-―]")
_SPACE = re.compile(r"\s+")
_W = "a-z0-9"


def load_config(version: str = "v1.0") -> dict:
    return json.loads((FILTERS / f"{version}.json").read_text())


def norm(text: Optional[str]) -> str:
    """FILTER.md section 2: case, HTML entities, whitespace and hyphens normalized (hyphen -> space)."""
    t = _html_normalize(text)
    t = _DASHES.sub(" ", t)
    return _SPACE.sub(" ", t).strip()


def find_word(phrase: str, text: str) -> Optional[re.Match]:
    """Whole-word / whole-phrase match in already-normalized text."""
    words = norm(phrase).split()
    body = r"\s+".join(re.escape(w) for w in words)
    return re.search(rf"(?<![{_W}]){body}(?![{_W}])", text)


def _loc_norm(value: str) -> str:
    v = unicodedata.normalize("NFKD", value)
    v = "".join(ch for ch in v if not unicodedata.combining(ch)).lower()
    return _SPACE.sub(" ", v).strip()


def _words(part: str) -> str:
    return _SPACE.sub(" ", re.sub(r"[^a-z0-9]+", " ", part)).strip()


def snippet(text: str, m: re.Match, width: int = 60) -> str:
    return text[max(0, m.start() - width): min(len(text), m.end() + width)].strip()


class Filter:
    def __init__(self, config: dict):
        self.c = config
        self.w = config["weights"]
        self.version = config["version"]

    # -- matching -------------------------------------------------------------------
    def find(self, phrase: str, text: str) -> Optional[re.Match]:
        return find_word(phrase, text)

    # -- required fields --------------------------------------------------------------
    def missing_fields(self, p: dict) -> list:
        missing = []
        if not str(p.get("key") or "").count("/") == 2:
            missing.append("key")
        if not (p.get("title") or "").strip():
            missing.append("title")
        if not norm(p.get("content")):
            missing.append("content")
        return missing

    # -- role and seniority gates -------------------------------------------------------
    def gate(self, p: dict) -> dict:
        t = norm(p["title"])
        roles = [r for r in self.c["role_phrases"] if self.find(r, t)]
        reasons = []
        if not roles:
            reasons.append("title has no qualifying role phrase")
        for x in self.c["excluded_title_phrases"]:
            if self.find(x, t):
                reasons.append(f'title contains excluded phrase "{x}"')
        # v1.1: a seniority term inside a listed product name (e.g. "manager" in "Mission Manager") does not count,
        # but only in a title that already has a role phrase, and only where that phrase is the term's sole occurrence.
        exceptions, applied = self.c.get("seniority_exceptions", {}), []
        for s in self.c["seniority_terms"]:
            t_s = t
            if roles:
                for phrase in exceptions.get(s, []):
                    m = find_word(phrase, t_s)
                    while m:
                        t_s = t_s[:m.start()] + " | " + t_s[m.end():]
                        applied.append(phrase)
                        m = find_word(phrase, t_s)
            if self.find(s, t_s):
                reasons.append(f'title contains excluded seniority term "{s}"')
        for r in roles:
            for lvl in self.c["level_suffixes"]:
                if self.find(f"{r} {lvl}", t):
                    reasons.append(f'title level "{lvl}" attached to "{r}"')
        signals = [s for s in self.c["entry_signals"] if self.find(s, t)]
        g = {"role_matched": roles[0] if roles else None, "passed": not reasons,
             "reasons": reasons, "entry_signals": signals}
        if applied:
            g["seniority_exceptions_applied"] = applied
        return g

    # -- topics -------------------------------------------------------------------
    def topics(self, p: dict) -> list:
        """Distinct topic groups in the description only; a group counts once whatever the alias."""
        text = norm(p.get("content"))
        found = []
        for group, aliases in self.c["topic_groups"].items():
            for alias in aliases:
                m = self.find(alias, text)
                if m:
                    found.append({"group": group, "alias": alias, "field": "content", "snippet": snippet(text, m)})
                    break
        return found

    # -- location -----------------------------------------------------------------
    def location_values(self, p: dict) -> list:
        vals = []
        if (p.get("location") or {}).get("name"):
            vals.append(("location.name", p["location"]["name"]))
        for o in p.get("offices") or []:
            if o.get("name"):
                vals.append(("offices[].name", o["name"]))
        alts = []
        for field, value in vals:
            for piece in value.split(";"):
                if piece.strip():
                    alts.append((field, piece.strip()))
        # A bare office equal to the city part of another alternative is the same place, not an alternative.
        firsts = {_words(_loc_norm(v).split(",")[0]) for _, v in alts if "," in v}
        return [(f, v) for f, v in alts if "," in v or _words(_loc_norm(v)) not in firsts]

    def classify_location_value(self, value: str) -> dict:
        L = self.c["location"]
        s = _loc_norm(value)
        for pre in L["workplace_prefixes"]:
            s = re.sub(rf"^{pre}\s*-\s*", "", s)
        remote = bool(re.search(r"(?<![a-z])remote(?![a-z])", s))
        s = re.sub(r"(?<![a-z])remote(?![a-z])", ",", s)
        parts = [_words(x) for x in re.split(r",| - ", s)]
        parts = [x for x in parts if x]
        states = L["us_states"]
        raw_joined = " ".join(parts)
        if raw_joined in L["us_city_aliases"] and not remote:  # exact bare-city alias, before state names
            return {"score": self.w["location_us_other"], "kind": "us-location", "why": f"alias {raw_joined}"}
        names_to_abbr = {v: k for k, v in states.items()}
        parts = [names_to_abbr.get(x, x) for x in parts]
        joined = " ".join(parts)

        def has(phrases):
            return [ph for ph in phrases if self.find(ph, joined)]

        if not parts:
            return {"score": 0, "kind": "unresolved", "why": "remote with no region" if remote else "empty"}
        if has(L["boston_area"]):
            return {"score": self.w["location_preferred"], "kind": "boston-area", "why": has(L["boston_area"])[0]}
        us_words = [x for x in parts if x in L["us_country_words"]]
        non_us = has(L["non_us_countries"]) + has(L["non_us_regions"])
        if non_us and not us_words:
            return {"score": None, "kind": "outside-us", "why": non_us[0]}
        us_place = [x for x in parts[1:] if x in states] or ([raw_joined] if raw_joined in L["us_city_aliases"] else [])
        if remote:
            if us_words and len(us_words) == len(parts):
                return {"score": self.w["location_preferred"], "kind": "us-remote", "why": us_words[0]}
            if us_place or us_words:
                return {"score": self.w["location_us_other"], "kind": "us-location",
                        "why": "remote within a named US area: " + joined}
            return {"score": 0, "kind": "unresolved", "why": f"remote, region not US-specific: {joined}"}
        if us_words or us_place:
            return {"score": self.w["location_us_other"], "kind": "us-location",
                    "why": (us_words or us_place)[0]}
        return {"score": 0, "kind": "unresolved", "why": f"not a recognized US or non-US location: {joined}"}

    def location(self, p: dict) -> dict:
        alts = [dict(field=f, value=v, **self.classify_location_value(v)) for f, v in self.location_values(p)]
        if not alts:
            return {"status": "unresolved", "score": 0, "best": None, "alternatives": [],
                    "why": "no structured location"}
        eligible = [a for a in alts if a["score"]]
        if eligible:
            best = max(eligible, key=lambda a: a["score"])
            return {"status": "eligible", "score": best["score"], "best": best, "alternatives": alts}
        if all(a["kind"] == "outside-us" for a in alts):
            return {"status": "outside-us", "score": 0, "best": None, "alternatives": alts}
        return {"status": "unresolved", "score": 0, "best": None, "alternatives": alts,
                "why": "no US-eligible alternative, and at least one alternative is ambiguous"}

    # -- decision -----------------------------------------------------------------
    def classify(self, p: dict) -> dict:
        out = {"key": p.get("key"), "title": p.get("title"), "filter_version": self.version,
               "url": p.get("absolute_url"), "structured": p.get("structured", {})}
        missing = self.missing_fields(p)
        if missing:
            out.update(decision=REVIEW, reasons=[f"I cannot tell: missing {', '.join(missing)}"], score=None,
                       missing=missing)
            return out
        g, topics, loc = self.gate(p), self.topics(p), self.location(p)
        n = min(len(topics), self.w["topic_cap"]) * self.w["topic"]
        title_pts = self.w["title"] if g["role_matched"] else 0
        score = title_pts + n + loc["score"]
        out.update(gate=g, topics=topics, n_topic_groups=len(topics), location=loc,
                   components={"title": title_pts, "topics": n, "location": loc["score"]}, score=score)
        if not out["url"]:
            out["disclosure"] = "no application URL in the source; none invented"
        if not g["passed"]:
            out.update(decision=REJECT, reasons=g["reasons"], score_is_diagnostic=True)
            return out
        out["score_is_diagnostic"] = False
        if loc["status"] == "outside-us":
            out.update(decision=REJECT, reasons=["every location alternative is outside the US"])
        elif loc["status"] == "unresolved":
            out.update(decision=REVIEW, reasons=[f"I cannot tell: location ({loc.get('why')})"])
        elif len(topics) < self.w["min_topic_groups"]:
            out.update(decision=REJECT, reasons=[f"{len(topics)} topic group(s); {self.w['min_topic_groups']} required"])
        elif score < self.w["threshold"]:
            out.update(decision=REJECT, reasons=[f"score {score} below threshold {self.w['threshold']}"])
        else:
            out.update(decision=KEEP, reasons=[f"score {score} >= threshold {self.w['threshold']}"])
        return out

    def run(self, postings: list) -> list:
        return [self.classify(p) for p in postings]


def rank(decisions: list) -> list:
    """FILTER.md section 4: score desc, location score desc, key asc. Kept postings only."""
    kept = [d for d in decisions if d["decision"] == KEEP]
    return sorted(kept, key=lambda d: (-d["score"], -d["components"]["location"], d["key"]))
