"""FILTER.md section 7: plausible-but-wrong filters. Each one replaces exactly one behavior of the real one.

These are deliberately wrong. They exist so tests/test_wrong_versions.py can show that the tests
catch each one. W7 (a claim labeled supported because a negated quote is present) is in claims.py.
"""
from __future__ import annotations

import re

from .filter import KEEP, REJECT, Filter, norm


class W1Substring(Filter):
    """W1: substring matching: "java" inside "javascript", "sr" inside "sre"."""
    def find(self, phrase, text):
        return re.search(re.escape(norm(phrase)), text)


class W2CountOverridesRole(Filter):
    """W2: a high raw skill count overrides the role gate."""
    def classify(self, p):
        out = super().classify(p)
        if out["decision"] == REJECT and out.get("n_topic_groups", 0) >= 4 and out["location"]["status"] == "eligible":
            out.update(decision=KEEP, reasons=["W2: 4+ topic groups"])
        return out


class W3UnresolvedIsRemoteUS(Filter):
    """W3: missing location or Remote Global is treated as eligible US remote."""
    def classify_location_value(self, value):
        r = super().classify_location_value(value)
        return {"score": 2, "kind": "us-remote", "why": "W3 assumed"} if r["kind"] == "unresolved" else r

    def location(self, p):
        r = super().location(p)
        if r["status"] == "unresolved":
            return {"status": "eligible", "score": 2, "best": {"value": "(assumed remote US)", "score": 2},
                    "alternatives": r["alternatives"]}
        return r


class W4MissingContentRejects(Filter):
    """W4: a missing description silently becomes a rejection."""
    def missing_fields(self, p):
        return [m for m in super().missing_fields(p) if m != "content"]


class W5BoilerplateLocation(Filter):
    """W5: a mention of Boston anywhere in the description sets the job location."""
    def location(self, p):
        if self.find("boston", norm(p.get("content"))):
            best = {"field": "content", "value": "Boston (from description)", "score": 2, "kind": "boston-area"}
            return {"status": "eligible", "score": 2, "best": best, "alternatives": [best]}
        return super().location(p)


class W6AliasesInflate(Filter):
    """W6: every alias and repeated mention counts, so python + python3 scores twice."""
    def topics(self, p):
        text = norm(p.get("content"))
        found = []
        for group, aliases in self.c["topic_groups"].items():
            for alias in aliases:
                for _ in re.finditer(rf"(?<![a-z0-9]){re.escape(norm(alias))}(?![a-z0-9])", text):
                    found.append({"group": group, "alias": alias, "field": "content", "snippet": alias})
        return found


class W8NoForwardDeployedExclusion(Filter):
    """W8: "software engineer" admits Forward Deployed Software Engineer."""
    def gate(self, p):
        g = super().gate(p)
        g["reasons"] = [r for r in g["reasons"] if "forward deployed" not in r]
        g["passed"] = not g["reasons"]
        return g


WRONG_FILTERS = {"W1": W1Substring, "W2": W2CountOverridesRole, "W3": W3UnresolvedIsRemoteUS,
                 "W4": W4MissingContentRejects, "W5": W5BoilerplateLocation, "W6": W6AliasesInflate,
                 "W8": W8NoForwardDeployedExclusion}
