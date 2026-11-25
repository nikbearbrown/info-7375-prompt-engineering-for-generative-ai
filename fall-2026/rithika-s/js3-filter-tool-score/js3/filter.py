"""The FILTER.md v1.0 filter.

evaluate(posting, config) -> {
    "board", "id", "title", "config_version",
    "decision": "kept" | "rejected" | "abstain",
    "reason", "score", "rule_scores", "fired", "matches"
}

Every match records the rule, the configured word, the field searched, the
character offsets in that field and the exact matched span. Offsets in
body_text refer to the plain text produced by js3.corpus.html_to_text.

Order of decision:
1. R3 or R4 fired -> "rejected" (whatever the score).
2. Empty body_text -> "abstain", reason "no body" (R2 cannot be scored).
3. score >= threshold -> "kept", otherwise "rejected".
"""

import json
import re
from pathlib import Path

KEPT = "kept"
REJECTED = "rejected"
ABSTAIN = "abstain"
NO_BODY = "no body"

# A "word character" for whole-word matching: ASCII letters, digits and
# underscore. Anything else (space, punctuation, non-Latin script) is a
# boundary.
_WORD_CHAR = "0-9A-Za-z_"


def load_config(path):
    config = json.loads(Path(path).read_text("utf-8"))
    for key in ("version", "threshold", "rules"):
        if key not in config:
            raise ValueError(f"filter config {path} has no {key!r}")
    for rule_id in ("R1", "R2", "R3", "R4"):
        if rule_id not in config["rules"]:
            raise ValueError(f"filter config {path} has no rule {rule_id}")
    return config


def term_pattern(term, whole_word=True, case_sensitive=False):
    """Regex for one configured word or phrase.

    The words of a phrase may be separated by any run of whitespace.
    """
    body = r"\s+".join(re.escape(word) for word in term.split())
    if whole_word:
        body = rf"(?<![{_WORD_CHAR}]){body}(?![{_WORD_CHAR}])"
    return re.compile(body, 0 if case_sensitive else re.IGNORECASE)


class Filter:
    """v1.0 filter. tests/test_js3_mutants.py subclasses this to build W1-W5;
    each mutant overrides exactly one of the hooks below."""

    exclusion_case_sensitive = False

    def __init__(self, config):
        self.config = config
        self.rules = config["rules"]
        self.threshold = config["threshold"]

    # --- hooks -----------------------------------------------------------

    def pattern(self, term, mode, case_sensitive=False):
        return term_pattern(term, whole_word=(mode == "whole_word"),
                            case_sensitive=case_sensitive)

    def role_field(self):
        return self.rules["R1"]["field"]

    def topic_score(self, r2_matches):
        """+1 per distinct configured word, at most the cap."""
        rule = self.rules["R2"]
        distinct = {m["word"] for m in r2_matches}
        return min(len(distinct) * rule["weight_per_distinct_word"],
                   rule["cap"])

    def no_body_decision(self):
        return ABSTAIN, NO_BODY

    # --- matching --------------------------------------------------------

    def _find(self, rule_id, field, text, case_sensitive=False):
        rule = self.rules[rule_id]
        found = []
        for word in rule["words"]:
            regex = self.pattern(word, rule["match"], case_sensitive)
            for m in regex.finditer(text):
                found.append({"rule": rule_id, "word": word, "field": field,
                              "start": m.start(), "end": m.end(),
                              "span": m.group(0)})
        found.sort(key=lambda m: (m["field"], m["start"], m["word"]))
        return found

    def evaluate(self, posting):
        title = posting.get("title") or ""
        body = posting.get("body_text") or ""
        has_body = bool(body.strip())
        fields = {"title": title, "body_text": body}

        role_field = self.role_field()
        r1 = self._find("R1", role_field, fields[role_field])
        r2 = self._find("R2", "body_text", body) if has_body else []
        r3 = []
        for field in self.rules["R3"]["fields"]:
            r3 += self._find("R3", field, fields[field],
                             self.exclusion_case_sensitive)
        r4 = self._find("R4", self.rules["R4"]["field"],
                        fields[self.rules["R4"]["field"]],
                        self.exclusion_case_sensitive)

        rule_scores = {"R1": self.rules["R1"]["weight"] if r1 else 0,
                       "R2": self.topic_score(r2) if has_body else None}
        score = rule_scores["R1"] + (rule_scores["R2"] or 0)
        fired = [rid for rid, hits in
                 (("R1", r1), ("R2", r2), ("R3", r3), ("R4", r4)) if hits]

        excluded = [rid for rid in ("R3", "R4") if rid in fired]
        if excluded:
            decision = REJECTED
            reason = "excluded by " + ", ".join(excluded)
        elif not has_body:
            decision, reason = self.no_body_decision()
        elif score >= self.threshold:
            decision = KEPT
            reason = f"score {score} >= {self.threshold}"
        else:
            decision = REJECTED
            reason = f"score {score} < {self.threshold}"

        return {
            "board": posting.get("board"),
            "id": posting.get("id"),
            "title": title,
            "config_version": self.config["version"],
            "decision": decision,
            "reason": reason,
            "score": score,
            "rule_scores": rule_scores,
            "fired": fired,
            "matches": r1 + r2 + r3 + r4,
        }


def evaluate(posting, config):
    return Filter(config).evaluate(posting)
