"""FILTER.md v1.1: Shreyash's decisions A1, A2, A4 and B4 (pasted 2026-11-25 ~18:07 EST, commit 61e0d4c0),
as tests. Written by Claude Code BEFORE filter-v1.1.json and the v1.1 code existed. Each decision is one
entry in filter-v1.1.json; v1 is kept unchanged for comparison. Constructed postings are marked by the
P() helper; the others are REAL postings from data/corpus.jsonl."""
import json
import pathlib
import unittest

from js3 import claims, corpus, filtering
from tests.test_js3_filter import GOOD_LINES, P, PERSONA, outcome

HERE = pathlib.Path(__file__).resolve().parent.parent
V1 = filtering.load_config(HERE / "filter-v1.json")
V11 = filtering.load_config(HERE / "filter-v1.1.json")
POSTS = {p["key"]: p for p in corpus.load()}
LINEAR_PE = "linear:0c7c2e26-0a98-42cf-a47c-9a3999fb513b"
RECOMMENDATIONS = "klaviyo:7855798003"
OSCAR_DALLAS = "oscar:8157655"
ANDROID = "klaviyo:7792539003"
CONVERSATIONAL = "klaviyo:8041054003"


def ev(p, cfg):
    return filtering.evaluate(p, PERSONA, cfg)


class OnlyWhatShreyashDecided(unittest.TestCase):
    def test_v11_differs_from_v1_only_in_the_adopted_entries(self):
        diff = {k for k in set(V1) | set(V11) if V1.get(k) != V11.get(k)}
        self.assertEqual(diff, {"version", "document", "rule1_title_phrases", "rule4_skill_aliases",
                                "rule3_single_state_residence", "evidence_full_time_not_stated_exception"})
        self.assertEqual(V11["version"], "v1.1")
        self.assertEqual(V11["rule1_title_phrases"], V1["rule1_title_phrases"] + ["Product Engineer"])
        self.assertEqual(V11["rule4_skill_aliases"], {"SQL": ["MySQL", "PostgreSQL", "Postgres"]})

    def test_rejected_changes_are_not_in_v11(self):
        self.assertEqual(V11["rule4_min_skills"], 2, "A5 rejected: keep at least two skills")
        self.assertEqual(V11["rule4_ignore_sections"], ["perk"], "A3 rejected: tech lists still count")


class A1ProductEngineer(unittest.TestCase):
    def test_product_engineer_passes_rule_1_in_v11_only(self):
        p = P(title="Product Engineer")
        self.assertEqual(outcome(ev(p, V1), 1), "fail")
        self.assertEqual(outcome(ev(p, V11), 1), "pass")

    def test_the_real_linear_product_engineer_is_kept(self):
        self.assertEqual(ev(POSTS[LINEAR_PE], V1)["verdict"], "Not Relevant")
        self.assertEqual(ev(POSTS[LINEAR_PE], V11)["verdict"], "Relevant")


class A2SqlFamily(unittest.TestCase):
    def test_mysql_postgresql_postgres_count_as_sql(self):
        for db in ("MySQL", "PostgreSQL", "Postgres"):
            p = P(lines=("Requirements:", f"You know Python and {db}."))
            self.assertEqual(outcome(ev(p, V1), 4), "fail", db)
            self.assertEqual(outcome(ev(p, V11), 4), "pass", db)

    def test_nosql_is_not_sql(self):
        p = P(lines=("Requirements:", "You know Python and NoSQL stores."))
        self.assertEqual(outcome(ev(p, V11), 4), "fail")

    def test_sql_counts_once(self):
        line = ev(P(lines=("Requirements:", "You know SQL, MySQL and PostgreSQL.")), V11)["rules"][3]
        self.assertEqual(line["outcome"], "fail", "one skill (SQL), however many databases are named")

    def test_the_real_recommendations_posting_is_kept_and_its_quotes_are_real(self):
        p = POSTS[RECOMMENDATIONS]
        rec = ev(p, V11)
        self.assertEqual(ev(p, V1)["verdict"], "Not Relevant")
        self.assertEqual(rec["verdict"], "Relevant")
        self.assertEqual(filtering.verify_quotes(rec, p), [])


class A4OneStateResidence(unittest.TestCase):
    def test_the_real_oscar_dallas_posting_fails_location_instead_of_cannot_tell(self):
        p = POSTS[OSCAR_DALLAS]
        self.assertIn("reside in: Dallas, Texas", p["content"])
        self.assertEqual(outcome(ev(p, V1), 3), "cannot tell")
        self.assertEqual(outcome(ev(p, V11), 3), "fail")

    def test_constructed_one_state_line(self):
        p = P(location="Dallas, Texas, United States", offices=["Dallas"], lines=GOOD_LINES + (
            "This is a remote position, open to candidates who reside in: Dallas, Texas.",))
        self.assertEqual(outcome(ev(p, V11), 3), "fail")

    def test_one_state_that_is_massachusetts_passes(self):
        p = P(location="Remote", offices=["Remote"], lines=GOOD_LINES + (
            "This is a remote position, open to candidates who reside in Massachusetts.",))
        self.assertEqual(outcome(ev(p, V11), 3), "pass")

    def test_located_is_not_a_residence_rule(self):
        p = P(location="Remote", offices=["Remote"], lines=GOOD_LINES + (
            "Our headquarters is located in New York.", "This role is remote anywhere in the United States."))
        self.assertEqual(outcome(ev(p, V11), 3), "pass")

    def test_the_physician_reviewer_is_still_cannot_tell(self):
        fx = json.loads((HERE / "tests" / "fixtures" / "physician_reviewer.json").read_text())
        self.assertEqual(outcome(ev(filtering.from_raw("greenhouse", "oscar", fx["job"]), V11), 3), "cannot tell")


class B4FullTimeNotStated(unittest.TestCase):
    def test_a_kept_posting_no_longer_abstains_for_full_time(self):
        p = POSTS[CONVERSATIONAL]
        j1 = claims.justify(p, ev(p, V1), PERSONA, V1)
        j11 = claims.justify(p, ev(p, V11), PERSONA, V11)
        self.assertEqual(j1["answer"], "I cannot tell")
        self.assertEqual(j11["answer"], "reaches Alex")
        ft = [c for c in j11["claims"] if c["id"] == "full_time"][0]
        self.assertEqual(ft["label"], "insufficient", "the label stays honest: the ad does not say it")
        self.assertIn("not stated", ft["exception"])

    def test_a_part_time_ad_is_still_rejected(self):
        p = P(lines=GOOD_LINES + ("This is a part-time position.",))
        self.assertEqual(outcome(ev(p, V11), 6), "fail")


class KnownFalsePositive(unittest.TestCase):
    def test_the_android_job_is_still_kept_because_a3_was_rejected(self):
        """Shreyash labeled it no (item 39). A3 would have removed it, and two held-out jobs he wants with
        it, so he rejected A3. This test records that the known false positive is still there."""
        self.assertEqual(ev(POSTS[ANDROID], V11)["verdict"], "Relevant")


if __name__ == "__main__":
    unittest.main()
