"""Independent recomputation of filter v1.0's committed development decisions.

Written by a Claude Code subagent on 2026-11-25 as an independent recomputation from FILTER.md (v1.0 rules,
sections 2-4) and filters/v1.0.json, without importing jobfilter.filter or reusing any of its scoring,
matching or location functions. The only project code used is jobfilter.corpus.load (to read the frozen
postings); text normalization and whole-word matching are re-implemented here from the written rule.

What is re-derived from the posting text and the written rule, for all 775 development decisions in
runs/v1.0/decisions-dev.json:
  - the title gate (role phrase, "forward deployed", seniority terms, attached level suffixes);
  - the distinct topic groups found in the description, and that every evidence snippet exists in it;
  - the score arithmetic (title 3, topic 1 capped at 4, location 2/1/0) and the KEEP/REVIEW/REJECT rule.

What is NOT re-derived, and is stated as such rather than hidden:
  - Location value classification is recomputed only for the 64 postings that pass the title gate (13
    distinct values). For the 711 gate-rejected postings location cannot change the decision (FILTER.md
    section 3: title/seniority exclusions take precedence), so their per-value kinds are taken as committed.
    The known Munich, DE -> Delaware defect (drafting/IMPLEMENTATION-NOTES.md, I7) sits in that group.
  - 106 postings have a bare office city that is not cited as an alternative (implementation reading I3:
    a bare office equal to another alternative's city is the same place). FILTER.md itself does not state
    this; the test checks that it is the only kind of omission and that it changes no gate-passing score.
  - Structured remote fields (Ashby isRemote/workplaceType, Lever workplaceType/country) are not scored by
    v1.0 (IMPLEMENTATION-NOTES.md I5, an unresolved limitation Ashwin disagreed with). Deciding whether those
    fields "explicitly conflict" is a judgment, not a mechanical rule, so this file does not re-derive it.
  - The missing-required-field REVIEW branch is not exercised: no development posting has an empty key,
    title or description (asserted below), so 0 decisions are excluded on that ground.

A passing run means the committed file is consistent with the written rule as recomputed here. It does not
mean the rule is right, that a KEEP suits Supriya, or that the snippets mean what a claim would need.
"""
import html
import json
import re
import unittest
from collections import Counter
from pathlib import Path

from jobfilter.corpus import load

HERE = Path(__file__).resolve().parent.parent
CONFIG = json.loads((HERE / "filters" / "v1.0.json").read_text())
DECISIONS = json.loads((HERE / "runs" / "v1.0" / "decisions-dev.json").read_text())
POSTINGS = {p["key"]: p for p in load()["postings"]}
W = CONFIG["weights"]

_TAG = re.compile(r"<[^>]+>")
_HYPHEN = re.compile("[\\-‐-―−]")
_SPACE = re.compile(r"\s+")


def norm(value):
    """FILTER.md section 2: normalize case, HTML entities, whitespace and hyphens (hyphen -> space)."""
    t = html.unescape(value or "")
    t = html.unescape(_TAG.sub(" ", t))
    t = _HYPHEN.sub(" ", t.lower())
    return _SPACE.sub(" ", t).strip()


def has(phrase, text):
    """Whole words or complete phrases only (FILTER.md section 2): letters/digits may not touch either end."""
    body = r"\s+".join(re.escape(w) for w in norm(phrase).split())
    return re.search(rf"(?<![a-z0-9]){body}(?![a-z0-9])", text) is not None


def recompute_gate(title):
    """(role phrases found, exclusion reasons) for a title, from FILTER.md section 2 and the json lists."""
    t = norm(title)
    roles = [r for r in CONFIG["role_phrases"] if has(r, t)]
    excluded = [("phrase", x) for x in CONFIG["excluded_title_phrases"] if has(x, t)]
    excluded += [("seniority", x) for x in CONFIG["seniority_terms"] if has(x, t)]
    excluded += [("level", lv) for r in roles for lv in CONFIG["level_suffixes"] if has(f"{r} {lv}", t)]
    return roles, excluded


def recompute_groups(content):
    text = norm(content)
    return {g for g, aliases in CONFIG["topic_groups"].items() if any(has(a, text) for a in aliases)}


def classify_location(value):
    """FILTER.md section 3 for one structured location value: (kind, score). Deliberately small: it is only
    asked about the values of gate-passing postings, and anything it does not recognise is 'unresolved'."""
    loc = CONFIG["location"]
    v = _SPACE.sub(" ", re.sub(r"[^a-z0-9]+", " ", norm(value))).strip()
    parts = [_SPACE.sub(" ", re.sub(r"[^a-z0-9]+", " ", p.lower())).strip() for p in (value or "").split(",")]
    us_words = set(loc["us_country_words"])
    if any(has(b, v) for b in loc["boston_area"]):
        return "boston-area", W["location_preferred"]
    if has("remote", v):
        if any(has(u, v) for u in us_words):
            return "us-remote", W["location_preferred"]
        return "unresolved", W["location_unresolved"]
    if any(p in loc["non_us_countries"] or p in loc["non_us_regions"] for p in parts[1:]):
        return "outside-us", None
    if v in loc["us_city_aliases"] or parts[-1] in us_words:
        return "us-location", W["location_us_other"]
    states = set(loc["us_states"]) | set(loc["us_states"].values())
    if len(parts) >= 2 and parts[-1] in states:
        return "us-location", W["location_us_other"]
    return "unresolved", W["location_unresolved"]


def structured_values(p):
    """Section 3 sources: structured primary location and offices, each split on ';'."""
    def parts(values):
        return {s.strip() for v in values for s in (v or "").split(";") if s.strip()}

    return {"location.name": parts([(p.get("location") or {}).get("name")]),
            "offices[].name": parts([o.get("name") for o in p.get("offices") or []])}


def recompute_status(alternatives):
    """Section 3: highest applicable score; no eligible alternative + any ambiguous one -> unresolved."""
    best = max([a["score"] for a in alternatives if a["score"] is not None] or [0])
    if best > 0:
        return "eligible", best
    if not alternatives or any(a["kind"] == "unresolved" for a in alternatives):
        return "unresolved", 0
    return "outside-us", 0


def recompute_decision(d):
    """Section 3/4: hard exclusions first; then unresolved -> REVIEW; outside -> REJECT; else score rule."""
    if not d["gate"]["passed"]:
        return "REJECT"
    status, _ = recompute_status(d["location"]["alternatives"])
    if status == "unresolved":
        return "REVIEW"
    if status == "outside-us":
        return "REJECT"
    ok = d["score"] >= W["threshold"] and d["n_topic_groups"] >= W["min_topic_groups"]
    return "KEEP" if ok else "REJECT"


class CommittedTotals(unittest.TestCase):
    def test_counts_and_keys(self):
        self.assertEqual(len(DECISIONS), 775)
        self.assertEqual(len({d["key"] for d in DECISIONS}), 775)
        self.assertEqual(Counter(d["decision"] for d in DECISIONS), {"KEEP": 18, "REVIEW": 7, "REJECT": 750})
        self.assertEqual([d["key"] for d in DECISIONS if d["key"] not in POSTINGS], [])
        self.assertEqual({d["filter_version"] for d in DECISIONS}, {"v1.0"})

    def test_weights_read_are_the_approved_ones(self):
        self.assertEqual(W, {"title": 3, "topic": 1, "topic_cap": 4, "location_preferred": 2,
                             "location_us_other": 1, "location_unresolved": 0, "min_topic_groups": 2,
                             "threshold": 7})

    def test_no_required_field_is_missing(self):
        """So the 'missing field -> REVIEW' branch excludes 0 decisions from the recomputation below."""
        missing = [d["key"] for d in DECISIONS
                   if not (POSTINGS[d["key"]]["title"] or "").strip() or not norm(POSTINGS[d["key"]]["content"])]
        self.assertEqual(missing, [])


class ScoreArithmetic(unittest.TestCase):
    def test_components_sum_to_score_with_written_weights(self):
        for d in DECISIONS:
            with self.subTest(d["key"]):
                c = d["components"]
                self.assertEqual(c["title"] + c["topics"] + c["location"], d["score"])
                self.assertEqual(c["topics"], min(d["n_topic_groups"] * W["topic"], W["topic_cap"]))
                matched = d["gate"]["role_matched"]
                self.assertEqual(c["title"], W["title"] if matched else 0)
                if matched:
                    self.assertIn(matched, CONFIG["role_phrases"])
                self.assertEqual(c["location"], d["location"]["score"])
                self.assertIn(c["location"], (0, 1, 2))
                self.assertEqual(d["score_is_diagnostic"], not d["gate"]["passed"])
                self.assertLessEqual(d["score"], 9)

    def test_n_topic_groups_is_distinct_groups_and_aliases_belong(self):
        for d in DECISIONS:
            with self.subTest(d["key"]):
                groups = [t["group"] for t in d["topics"]]
                self.assertEqual(len(groups), len(set(groups)), "a group was counted twice")
                self.assertEqual(d["n_topic_groups"], len(set(groups)))
                for t in d["topics"]:
                    self.assertIn(t["alias"], CONFIG["topic_groups"][t["group"]])


class RecomputedFromPostingText(unittest.TestCase):
    def test_title_gate(self):
        mismatches = []
        for d in DECISIONS:
            roles, excluded = recompute_gate(POSTINGS[d["key"]]["title"])
            passed = bool(roles) and not excluded
            if passed != d["gate"]["passed"] or bool(roles) != bool(d["gate"]["role_matched"]):
                mismatches.append(d["key"])
            elif roles and d["gate"]["role_matched"] not in roles:
                mismatches.append(d["key"])
            elif roles and excluded:
                committed = " | ".join(d["gate"]["reasons"])
                if not all(f'"{term}"' in committed for _, term in excluded):
                    mismatches.append(d["key"])
        self.assertEqual(mismatches, [])
        self.assertEqual(sum(d["gate"]["passed"] for d in DECISIONS), 64)

    def test_topic_groups_from_description(self):
        mismatches = [d["key"] for d in DECISIONS
                      if recompute_groups(POSTINGS[d["key"]]["content"]) != {t["group"] for t in d["topics"]}]
        self.assertEqual(mismatches, [])

    def test_topic_evidence_snippets_exist_in_the_posting(self):
        """Evidence is not invented: each snippet occurs in the normalized description, and its alias occurs
        as a whole word inside the snippet. Topics are scored from the description only (section 2)."""
        n = 0
        for d in DECISIONS:
            text = norm(POSTINGS[d["key"]]["content"])
            for t in d["topics"]:
                n += 1
                with self.subTest(d["key"], group=t["group"]):
                    self.assertEqual(t["field"], "content")
                    self.assertIn(norm(t["snippet"]), text)
                    self.assertTrue(has(t["alias"], norm(t["snippet"])))
        self.assertEqual(n, 636)


class Location(unittest.TestCase):
    def test_cited_values_exist_and_status_follows_alternatives(self):
        """No alternative is invented: each is a structured value (location.name split on ';', or an office).
        Description text is never a location source (section 3, W5). Status/score follow the alternatives."""
        for d in DECISIONS:
            p, loc = POSTINGS[d["key"]], d["location"]
            with self.subTest(d["key"]):
                for field, values in structured_values(p).items():
                    cited = {a["value"].strip() for a in loc["alternatives"] if a["field"] == field}
                    self.assertLessEqual(cited, values, field)
                self.assertEqual(recompute_status(loc["alternatives"]), (loc["status"], loc["score"]))

    def test_uncited_values_are_only_repeated_bare_office_cities(self):
        """Not every structured value is cited. FILTER.md does not say to drop any; the implementation
        reading I3 (drafting/IMPLEMENTATION-NOTES.md, agreed by Ashwin) treats a bare office equal to another
        alternative's city as the same place. Checked here: that is the ONLY kind of omission, and among
        gate-passing postings it touches 2 keys, where the bare 'Boston' scores the same as 'Boston, MA'."""
        affected, gate_passed = [], []
        for d in DECISIONS:
            p = POSTINGS[d["key"]]
            values = structured_values(p)
            cited = {a["value"].strip() for a in d["location"]["alternatives"]}
            uncited = (values["location.name"] | values["offices[].name"]) - cited
            if not uncited:
                continue
            affected.append(d["key"])
            cities = {c.split(",")[0].strip().lower() for c in cited if "," in c}
            for u in uncited:
                with self.subTest(d["key"], value=u):
                    self.assertIn(u, values["offices[].name"])
                    self.assertNotIn(",", u)
                    self.assertIn(u.lower(), cities)
            if d["gate"]["passed"]:
                gate_passed.append(d["key"])
                for u in uncited:  # including it would not change the best score
                    self.assertLessEqual(classify_location(u)[1] or 0, d["location"]["score"])
        self.assertEqual(len(affected), 106)
        self.assertEqual(sorted(gate_passed), ["greenhouse/klaviyo/7727703003", "greenhouse/klaviyo/8041054003"])

    def test_values_recomputed_where_location_can_change_the_decision(self):
        passed = [d for d in DECISIONS if d["gate"]["passed"]]
        self.assertEqual((len(passed), len(DECISIONS) - len(passed)), (64, 711))  # 711 not recomputed here
        values, mismatches = set(), []
        for d in passed:
            for a in d["location"]["alternatives"]:
                values.add(a["value"])
                if classify_location(a["value"]) != (a["kind"], a["score"]):
                    mismatches.append((d["key"], a["value"]))
        self.assertEqual(len(values), 13)
        self.assertEqual(mismatches, [])


class DecisionRule(unittest.TestCase):
    def test_every_decision_recomputed_from_the_written_rule(self):
        mismatches = [(d["key"], d["decision"], recompute_decision(d)) for d in DECISIONS
                      if recompute_decision(d) != d["decision"]]
        self.assertEqual(mismatches, [])

    def test_review_only_for_unresolved_location_after_the_gate(self):
        for d in DECISIONS:
            if d["decision"] == "REVIEW":
                self.assertTrue(d["gate"]["passed"])
                self.assertEqual(d["location"]["status"], "unresolved")
                self.assertTrue(d["reasons"][0].startswith("I cannot tell"))

    def test_keep_boundary(self):
        keeps = [d for d in DECISIONS if d["decision"] == "KEEP"]
        for d in keeps:
            self.assertTrue(d["gate"]["passed"])
            self.assertGreaterEqual(d["score"], 7)
            self.assertGreaterEqual(d["n_topic_groups"], 2)
            self.assertEqual(d["location"]["status"], "eligible")
        self.assertEqual(sum(d["score"] == 7 for d in keeps), 7)  # exactly at the threshold
        # Conversely: passed gate, score >= 7, >= 2 groups, eligible location -> KEEP, with no exception.
        should_keep = [d["key"] for d in DECISIONS if d["gate"]["passed"] and d["score"] >= 7
                       and d["n_topic_groups"] >= 2 and d["location"]["status"] == "eligible"]
        self.assertEqual(sorted(should_keep), sorted(d["key"] for d in keeps))
        # Score 7 + >= 2 groups is not enough on its own: "location is resolved and eligible" also binds.
        # These four have score 7 only through 4-5 topic groups and every location outside the US.
        not_kept = sorted(d["key"] for d in DECISIONS if d["gate"]["passed"] and d["score"] >= 7
                          and d["n_topic_groups"] >= 2 and d["decision"] == "REJECT")
        self.assertEqual(not_kept, sorted([
            "lever/palantir/10dfc8bc-99ad-4ca2-ab76-853cb90a92c2",
            "lever/palantir/aaee4d20-7f1b-48b1-ad23-d52ffbf42a49",
            "lever/palantir/f70cdff7-c62f-4b73-a136-909e5e3d1891",
            "lever/palantir/f75cb0d2-6608-450b-848e-0f27937c930d",
        ]))

    def test_one_point_below_threshold_rejects(self):
        below = [d for d in DECISIONS if d["gate"]["passed"] and d["score"] == 6
                 and d["n_topic_groups"] >= 2 and d["location"]["status"] == "eligible"]
        self.assertEqual(len(below), 11)
        self.assertEqual({d["decision"] for d in below}, {"REJECT"})
        self.assertTrue(all("score 6 below threshold 7" in d["reasons"] for d in below))


if __name__ == "__main__":
    unittest.main()
