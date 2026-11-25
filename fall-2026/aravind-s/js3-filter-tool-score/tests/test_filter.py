"""JS3's filter (FILTER.md v1.0): the document's lists, each rule, the ranking, and wrong versions W1 to W7.

Every posting here is a CONSTRUCTED fixture, except where a test says it reads a real saved sentence. The profile is
Jane Doe's unless a test says otherwise (FILTER.md Section 6, item 8: person facts come from the profile).
"""

import copy
import random
import re
import unittest

from job_agent import filter as flt
from job_agent import providers
from job_agent.errors import BrokenInput

from .loop_helpers import REPO

RULES = flt.load_rules(version="1.0")
JANE = flt.load_profile()
SECTION_1 = flt.FILTER_MD.read_text(encoding="utf-8").split("## Section 1")[1].split("## Section 2")[0]
SECTION_6 = flt.FILTER_MD.read_text(encoding="utf-8").split("## Section 6")[1].split("## Section 7")[0]
SF = {"postalAddress": {"addressCountry": "United States", "addressRegion": "California",
                        "addressLocality": "San Francisco"}}


def posting(i="p-1", title="Software Engineer, Example Team", description="We build APIs and design SQL schemas.",
            **extra):
    data = {"id": i, "title": title, "employmentType": "FullTime", "location": "San Francisco", "address": SF,
            "secondaryLocations": [], "descriptionPlain": description, "publishedAt": "2026-11-01T00:00:00+00:00",
            "jobUrl": f"https://example.com/{i}"}
    data.update(extra)
    return data


def rule(record, name):
    return next(r for r in record["rules"] if r["rule"] == name)


def listed(text):
    """Items of an English list: "a, b, c and d" -> [a, b, c, d]."""
    return [p.strip() for p in re.split(r",\s*|\s+and\s+|\s+or\s+", text.strip().rstrip(".")) if p.strip()]


class DocumentTest(unittest.TestCase):
    """Section 7 (what the program reads) must hold exactly the lists Aravind wrote in Section 1."""

    def test_r1_keeps_only_the_listed_type(self):
        self.assertEqual(RULES["employment_type_keep"], re.findall(r"Keep only `([^`]+)`", SECTION_1))

    def test_r3_level_words(self):
        words = re.search(r"these 15 exact words: (.*?)\. ", SECTION_1).group(1)
        self.assertEqual(RULES["level_words"], listed(words))
        self.assertEqual(len(RULES["level_words"]), 15)

    def test_r4_included_and_excluded_phrases(self):
        def block(head):
            part = SECTION_1.split(head)[1]
            items = []
            for line in part.splitlines()[1:]:
                if re.match(r"\d+\. ", line.strip()):
                    items.append(line.strip().split(". ", 1)[1])
                elif items and line.strip():
                    break
            return items
        self.assertEqual(RULES["role_includes"], block("Included phrases (12):"))
        self.assertEqual(RULES["role_excludes"], block("Excluded phrases (17):"))

    def test_r6_start_phrases(self):
        sentence = re.search(r"these exact phrases: (.*?)\. Keep", SECTION_1).group(1)
        self.assertEqual(RULES["start_phrases"], re.findall(r'"([^"]+)"', sentence))

    def test_r7_optional_phrases(self):
        sentence = re.search(r"Only clear optional phrases excuse it: (.*?)\.\s", SECTION_1).group(1)
        self.assertEqual(RULES["years_optional_phrases"], re.findall(r'"([^"]+)"', sentence))

    def test_action_words(self):
        line = re.search(r"Exact action words: (.*)", SECTION_1).group(1)
        self.assertEqual(RULES["action_words"], listed(line.rstrip(".").replace(" ", "").replace(",", ", ")))

    def test_topic_groups(self):
        groups = {}
        for match in re.finditer(r"^\* ([^:]+): (.*)$", SECTION_1, re.M):
            name, rest = match.group(1), match.group(2)
            if name in RULES["topic_groups"]:
                groups[name] = [t.strip() for t in rest.split(". ")[0].split(",")]
        self.assertEqual(groups, RULES["topic_groups"])

    def test_r8_titles_and_phrases(self):
        titles = re.search(r"these exact phrases: (AI Trainer.*?)\. ", SECTION_1).group(1)
        self.assertEqual(RULES["annotation_titles"], listed(titles))
        sentence = re.search(r"main-responsibility phrase such as (.*?)\. Reject", SECTION_1).group(1)
        duties, tasks = sentence.split("together with tasks such as")
        self.assertEqual(RULES["annotation_responsibility_phrases"], re.findall(r'"([^"]+)"', duties))
        self.assertEqual(RULES["annotation_task_phrases"], re.findall(r'"([^"]+)"', tasks))

    def test_ranking_numbers(self):
        rank = RULES["ranking"]
        self.assertIn(f"starts with {rank['start']} points", SECTION_1)
        self.assertIn(f"Add {rank['per_topic_group']} points for each", SECTION_1)
        self.assertIn(f"capped at {rank['topic_cap']}", SECTION_1)
        self.assertIn(f"Subtract {-rank['other_us_location']} points for US locations outside", SECTION_1)
        for words, key in (("for a missing or unclear location", "location_cannot_tell"),
                           ("for a missing employment type", "employment_type_cannot_tell"),
                           ("when the start date", "start_cannot_tell"), ("when the years", "years_cannot_tell")):
            self.assertIn(f"Subtract {-rank[key]} points {words}", SECTION_1)
        self.assertIn(f"minimum shortlist score is {rank['shortlist_min']} points", SECTION_1)
        self.assertIn(f"top {rank['shortlist_size']} distinct postings", SECTION_1)

    def test_section_6_company_words(self):
        line = re.search(r"when it contains one of: (.*?)\. Such", SECTION_6, re.S).group(1)
        self.assertEqual(RULES["years_company_words"], listed(" ".join(line.split())))

    def test_years_max_is_janes_experience(self):
        # Section 7's years_max is a person fact; the engine reads the profile, and for Jane the two agree.
        self.assertEqual(RULES["years_max"], JANE["experience"]["full_time_years"])

    def test_a_missing_section_7_key_is_broken_input(self):
        text = flt.FILTER_MD.read_text(encoding="utf-8").replace('"years_max": 3,', "")
        path = REPO / "tests" / "_tmp_filter.md"
        path.write_text(text, encoding="utf-8")
        self.addCleanup(path.unlink)
        with self.assertRaises(BrokenInput) as caught:
            flt.load_rules(path)
        self.assertIn("years_max", str(caught.exception))


class RuleTest(unittest.TestCase):
    def judge(self, p, profile=None):
        return flt.judge(p, profile or JANE, RULES, board="ashby-test")

    def test_r1_employment_type(self):
        self.assertEqual(rule(self.judge(posting()), "R1")["result"], "pass")
        self.assertEqual(self.judge(posting(employmentType="Intern"))["deciding_rule"], "R1")
        self.assertEqual(self.judge(posting(employmentType="Full Time - Fixed Term Employment"))["fate"], "rejected")
        record = self.judge(posting(employmentType=None))
        self.assertEqual((record["fate"], rule(record, "R1")["result"]), ("kept", "cannot_tell"))
        self.assertIn(("R1: the employment type is missing", -10), record["score_terms"])

    def test_r2_preferred_other_us_outside_and_unclear(self):
        self.assertEqual(self.judge(posting())["location_category"], "preferred")
        dc = posting(location="Washington, D.C.", address=providers.postal("Washington, D.C."))
        record = self.judge(dc)
        # W7: a US place outside Jane's areas is kept with 15 points off, not rejected.
        self.assertEqual((record["fate"], record["location_category"]), ("kept", "other_us"))
        self.assertIn(-15, [p for _, p in record["score_terms"]])
        london = posting(location="London, United Kingdom",
                         address={"postalAddress": {"addressCountry": "United Kingdom"}})
        self.assertEqual(self.judge(london)["deciding_rule"], "R2")
        both = posting(location="London, United Kingdom", address={"postalAddress": {"addressCountry": "United Kingdom"}},
                       secondaryLocations=[{"location": "New York, NY", "address": providers.postal("New York, NY")}])
        self.assertEqual(self.judge(both)["location_category"], "preferred")  # one matching location is enough
        bare = self.judge(posting(location="Remote", address={}))
        self.assertEqual((bare["location_category"], bare["fate"]), ("unclear", "kept"))
        self.assertEqual(self.judge(posting(location="Remote - US", address={}))["location_category"], "preferred")
        # Section 6, item 5 as written: a US remote spelling that is not one of Jane's phrases is "other US".
        self.assertEqual(self.judge(posting(location="Remote (United States)", address={}))["location_category"],
                         "other_us")

    def test_r3_level_words_are_whole_words(self):
        self.assertEqual(self.judge(posting(title="Senior Software Engineer"))["deciding_rule"], "R3")
        self.assertEqual(rule(self.judge(posting(title="Software Engineer, Seniority Platform")), "R3")["result"],
                         "pass")

    def test_r4_role_phrases_are_whole_phrases(self):
        # W1: "Data Engineer" must not match inside "Data Engineering".
        self.assertEqual(rule(self.judge(posting(title="Data Engineering, Platform")), "R4")["result"], "reject")
        for title in ("Software Engineer II", "Machine Learning Engineer", "ML Engineer, Search",
                      "Software Engineer, Frontend", "Software Engineer | Mobile", "Full-Stack Engineer"):
            with self.subTest(title=title):
                self.assertEqual(rule(self.judge(posting(title=title)), "R4")["result"], "pass")
        for title in ("Frontend Engineer", "Security Engineer", "Product Designer"):
            with self.subTest(title=title):
                self.assertEqual(rule(self.judge(posting(title=title)), "R4")["result"], "reject")

    def test_r5_status_and_caution(self):
        self.assertEqual(self.judge(posting(description="Must be a US citizen. We build APIs."))["deciding_rule"], "R5")
        self.assertEqual(self.judge(posting(description="We do not sponsor visas."))["deciding_rule"], "R5")
        record = self.judge(posting(description="This role may be subject to U.S. export control rules. We build APIs."))
        self.assertEqual(rule(record, "R5")["result"], "pass")
        self.assertTrue(record["cautions"])

    def test_r6_start(self):
        self.assertEqual(self.judge(posting(description="Please start immediately."))["deciding_rule"], "R6")
        # Section 6, item 1: "Dec. 2026" stays one date, so the start before May 2027 is seen.
        record = self.judge(posting(description="You will start in Dec. 2026 with the team."))
        self.assertEqual(record["deciding_rule"], "R6")
        self.assertEqual(len(record["section6"]["dec_merges"]), 1)
        unclear = self.judge(posting(description="Start date: Spring 2027. We build APIs and SQL tooling."))
        self.assertEqual((unclear["fate"], rule(unclear, "R6")["result"]), ("kept", "cannot_tell"))
        self.assertEqual(rule(self.judge(posting(description="Start in Summer 2027.")), "R6")["result"], "pass")
        self.assertEqual(rule(self.judge(posting(description="An early 2027 start.")), "R6")["result"], "cannot_tell")
        # As v1.0 is written, a season before the earliest start is "cannot tell" (FILTER-CHANGES-PENDING.md).
        self.assertEqual(rule(self.judge(posting(description="Start in Fall 2026.")), "R6")["result"], "cannot_tell")
        self.assertEqual(rule(self.judge(posting(description="Start in June 2027.")), "R6")["result"], "pass")

    def test_r7_years(self):
        reject = self.judge(posting(description="5+ years of software engineering experience."))
        self.assertEqual(reject["deciding_rule"], "R7")
        # W2: the real sentence of posting 19 (OpenAI, 2026-10-30) has no "experience" and still rejects.
        p19 = "- 5+ years in one or more of: ML systems, performance engineering, distributed systems, or HPC."
        self.assertEqual(self.judge(posting(description=p19))["deciding_rule"], "R7")
        # W3: optional years do not reject.
        self.assertEqual(rule(self.judge(posting(description="5+ years of Go is a plus.")), "R7")["result"], "pass")
        for text in ("3-5 years of experience.", "3+ years of experience.", "We were founded 15 years ago.",
                     "We will double over the next 5 years.", "1 year of Python."):
            with self.subTest(text=text):
                self.assertEqual(rule(self.judge(posting(description=text)), "R7")["result"], "pass")
        company = self.judge(posting(description="The company grew 10x in 5 years. We build APIs."))
        self.assertEqual((company["fate"], rule(company, "R7")["result"]), ("kept", "cannot_tell"))
        self.assertEqual(company["section6"]["company_words"][0]["word"], "grew")
        self.assertEqual(self.judge(posting(description="4 years required."))["deciding_rule"], "R7")

    def test_r8_annotation(self):
        self.assertEqual(flt.r8_annotation("AI Trainer", [], RULES)["result"], "reject")
        sentences = ["Your primary responsibility is to label data for our models."]
        self.assertEqual(flt.r8_annotation("Software Engineer", sentences, RULES)["result"], "reject")
        self.assertEqual(flt.r8_annotation("Machine Learning Engineer", ["You will build training pipelines."],
                                           RULES)["result"], "pass")

    def test_topics_need_an_action_word_in_the_same_sentence(self):
        self.assertEqual(flt.topic_groups(["Experience with Kafka and SQL."], RULES), {})
        found = flt.topic_groups(["We build RESTful APIs.", "You design SQL schemas."], RULES)
        self.assertEqual(sorted(found), ["APIs", "Databases"])

    def test_w6_rest_counts_only_in_uppercase(self):
        self.assertEqual(flt.topic_groups(["We build the rest of the platform."], RULES), {})
        self.assertIn("APIs", flt.topic_groups(["We build REST services."], RULES))

    def test_posting_level_cannot_tell(self):
        for p, why in ((posting(title=""), "no title"), (posting(description=""), "no description"),
                       (posting(_cannot_tell="the posting has no title"), "no title")):
            with self.subTest(why=why):
                record = self.judge(p)
                self.assertEqual(record["fate"], "cannot_tell")
                self.assertIn(why, record["cannot_tell"])

    def test_score_terms(self):
        two = self.judge(posting(description="We build APIs. You design SQL schemas."))
        self.assertEqual(two["score"], 60)
        many = self.judge(posting(description="We build APIs, SQL stores, Kafka queues, AWS stacks, microservices, "
                                              "SDK tools and backend code."))
        self.assertEqual(many["score"], 75)  # 7 groups, capped at 25
        dc = posting(location="Washington, D.C.", address=providers.postal("Washington, D.C."),
                     description="We build APIs. You design SQL schemas.")
        self.assertEqual(self.judge(dc)["score"], 45)


class RankingTest(unittest.TestCase):
    def records(self):
        rows = [("a", "Software Engineer", 70, "2026-11-10T00:00:00+00:00"),
                ("b", "Backend Engineer", 70, "2026-11-12T00:00:00+00:00"),
                ("c", "Platform Engineer", 70, "2026-11-12T00:00:00+00:00"),
                ("d", "Data Engineer", 70, None),
                ("e", "software  engineer", 65, "2026-11-15T00:00:00+00:00"),  # duplicate of "a" (case, spaces)
                ("f", "Infrastructure Engineer", 55, "2026-11-20T00:00:00+00:00")]
        rows += [(f"z{i:02}", f"Engineer {i}", 60, f"2026-10-{i + 1:02}T00:00:00+00:00") for i in range(10)]
        return [{"board": "ashby-test", "id": i, "title": t, "fate": "kept", "score": s, "publishedAt": d}
                for i, t, s, d in rows]

    def test_cutoff_duplicates_order_and_size(self):
        result = flt.shortlist(self.records(), RULES)
        top = [r["id"] for r in result["top"]]
        # b and c tie at 70 on score and date, so the id decides; d has no date, so it is last of the 70s;
        # the newer duplicate e (65) replaces a; f is under 60.
        self.assertEqual(top[:5], ["b", "c", "d", "e", "z09"])
        self.assertEqual(len(top), 10)
        self.assertNotIn("a", [r["id"] for r in result["ordered"]])
        self.assertNotIn("f", [r["id"] for r in result["ordered"]])
        self.assertEqual([r["id"] for r in result["duplicates_removed"]], ["a"])

    def test_w5_the_order_does_not_depend_on_the_input_order(self):
        records = self.records()
        first = [r["id"] for r in flt.shortlist(records, RULES)["top"]]
        for seed in range(5):
            shuffled = records[:]
            random.Random(seed).shuffle(shuffled)
            self.assertEqual([r["id"] for r in flt.shortlist(shuffled, RULES)["top"]], first)


class ProfileTest(unittest.TestCase):
    """The engine reads person facts from the profile it is given, so another profile can be used unchanged."""

    def test_person_facts_come_from_the_profile(self):
        other = copy.deepcopy(JANE)
        other["experience"]["full_time_years"] = 5
        other["availability"]["earliest_full_time_start"] = "2026-01"
        other["work_authorization"]["us_person"] = True
        other["preferences"]["cities"] = ["Chicago"]
        chicago = posting(location="Chicago, IL", address=providers.postal("Chicago, IL"),
                          description="5+ years of experience. You will start in Dec. 2026. Must be a US citizen.")
        self.assertEqual(flt.judge(chicago, JANE, RULES)["fate"], "rejected")
        record = flt.judge(chicago, other, RULES)
        self.assertEqual(record["failed_rules"], [])
        self.assertEqual(record["location_category"], "preferred")

    def test_a_profile_missing_a_fact_is_broken_input(self):
        broken = copy.deepcopy(JANE)
        del broken["availability"]
        with self.assertRaises(BrokenInput):
            flt.check_profile(broken)


if __name__ == "__main__":
    unittest.main()
