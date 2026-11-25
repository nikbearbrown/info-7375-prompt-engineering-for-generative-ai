"""GATE.md, Boards and "Postings from three systems": the URL each board is read from, and how each
system's answer is read into the fields the rule reads. Real answers are excerpts (tests/fixtures/js2)."""

import json
import unittest
from pathlib import Path

from job_agent import providers, resume, rule
from job_agent.errors import BrokenInput, Unverified

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "js2"
JANE = resume.load(Path(__file__).resolve().parent.parent / "persona" / "jane-doe.json")


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def by_title(postings, title):
    return next(p for p in postings if p["title"] == title)


class BoardUrlTest(unittest.TestCase):
    def test_each_system_has_one_url_template(self):
        self.assertEqual(providers.board_url("ashby", "openai"), "https://api.ashbyhq.com/posting-api/job-board/openai")
        self.assertEqual(providers.board_url("greenhouse", "verkada"),
                         "https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true")
        self.assertEqual(providers.board_url("lever", "palantir"), "https://api.lever.co/v0/postings/palantir?mode=json")

    def test_a_name_outside_the_pattern_is_broken_input(self):
        for name in ("OpenAI", "", "-x", "a/b", "a?x=1", "a" * 65, "evil.example", None):
            with self.subTest(name=name):
                with self.assertRaises(BrokenInput):
                    providers.board_url("greenhouse", name)

    def test_an_unknown_system_is_broken_input(self):
        with self.assertRaises(BrokenInput):
            providers.board_url("workday", "acme")


class BrokenAnswerTest(unittest.TestCase):
    def test_the_real_404_answers_of_all_three_systems_are_unverified(self):
        for system, name in (("greenhouse", "greenhouse-404.json"), ("lever", "lever-404.json"),
                             ("ashby", "ashby-404.txt")):
            with self.subTest(system=system):
                with self.assertRaises(Unverified) as caught:
                    providers.read(system, 404, fixture(name))
                self.assertIn("HTTP 404", str(caught.exception))

    def test_an_empty_jobs_list_is_unverified_not_zero_postings(self):
        # Wrong version 1b: an empty jobs list read as zero postings.
        for system, body in (("ashby", b'{"jobs": []}'), ("greenhouse", b'{"jobs": [], "meta": {"total": 0}}'),
                             ("lever", b"[]")):
            with self.subTest(system=system):
                with self.assertRaises(Unverified) as caught:
                    providers.read(system, 200, body)
                self.assertIn("empty", str(caught.exception))

    def test_other_broken_answers_are_unverified(self):
        cases = [("ashby", b"not json"), ("greenhouse", b'{"no_jobs": 1}'), ("lever", b'{"ok": false}'),
                 ("greenhouse", b'{"jobs": [{"id": 1}]}'), ("lever", b'[{"id": "x"}]'), ("ashby", b'{"jobs": [3]}')]
        for system, body in cases:
            with self.subTest(system=system, body=body):
                with self.assertRaises(Unverified):
                    providers.read(system, 200, body)


class GreenhouseTest(unittest.TestCase):
    def setUp(self):
        self.postings = providers.read("greenhouse", 200, fixture("greenhouse-verkada-excerpt.json"))

    def test_fields_are_mapped_by_the_gate_table(self):
        grad = by_title(self.postings, "Backend Software Engineer - University Graduate 2027")
        self.assertEqual(grad["id"], "5280545007")  # Greenhouse ids are numbers; the agent keeps text
        self.assertEqual(grad["employmentType"], "FullTime")  # metadata "Employment Type": "Full-Time"
        self.assertEqual(grad["location"], "San Mateo, CA United States")
        self.assertEqual(grad["address"]["postalAddress"],
                         {"addressCountry": "United States", "addressRegion": "California", "addressLocality": "San Mateo"})
        self.assertTrue(grad["jobUrl"].startswith("https://"))
        self.assertNotIn("<", grad["descriptionPlain"])
        self.assertNotIn("&lt;", grad["descriptionPlain"])
        self.assertIn("\n", grad["descriptionPlain"])  # block tags become line breaks, so sentences split

    def test_an_unlisted_employment_value_is_kept_as_written(self):
        intern = by_title(self.postings, "Backend Software Engineering Intern 2027")
        self.assertEqual(intern["employmentType"], "Intern/Co-op")

    def test_new_york_city_counts_as_new_york_and_london_is_not_american(self):
        nyc = by_title(self.postings, "Account Executive, Select, New York City (Mid-Market)")
        self.assertEqual(nyc["address"]["postalAddress"]["addressLocality"], "New York")
        london = by_title(self.postings, "Account Executive, Benelux")
        self.assertEqual(london["address"], {})

    def test_the_rule_judges_the_mapped_postings(self):
        verdicts = {p["title"]: rule.judge(p, JANE) for p in self.postings}
        self.assertEqual(verdicts["Backend Software Engineer - University Graduate 2027"]["verdict"], "relevant")
        self.assertEqual(verdicts["Backend Software Engineering Intern 2027"]["deciding_check"], 1)
        self.assertEqual(verdicts["Account Executive, Benelux"]["deciding_check"], 2)

    def test_no_employment_type_is_not_stated(self):
        raw = json.loads(fixture("greenhouse-verkada-excerpt.json"))
        job = dict(raw["jobs"][0])
        job["metadata"] = []
        mapped = providers.read("greenhouse", 200, json.dumps({"jobs": [job]}).encode())[0]
        self.assertIsNone(mapped["employmentType"])
        self.assertTrue(rule.check_employment_type(mapped, JANE)["passed"])  # GATE.md: not stated passes


class LeverTest(unittest.TestCase):
    def setUp(self):
        self.postings = providers.read("lever", 200, fixture("lever-palantir-excerpt.json"))

    def test_fields_are_mapped_by_the_gate_table(self):
        apollo = by_title(self.postings, "Software Engineer - Apollo Platform")
        self.assertEqual(apollo["employmentType"], "FullTime")  # categories.commitment "Full-time"
        self.assertEqual(apollo["address"]["postalAddress"]["addressRegion"], "New York")
        self.assertEqual(apollo["workplaceType"], "hybrid")
        self.assertTrue(apollo["jobUrl"].startswith("https://jobs.lever.co/palantir/"))

    def test_the_requirements_in_lists_are_read(self):
        # GATE.md: Lever's requirements sit in `lists`, not in descriptionPlain.
        raw = json.loads(fixture("lever-palantir-excerpt.json"))
        apollo_raw = next(p for p in raw if p["text"] == "Software Engineer - Apollo Platform")
        heading = apollo_raw["lists"][-1]["text"]
        self.assertNotIn(heading, apollo_raw["descriptionPlain"])
        apollo = by_title(self.postings, "Software Engineer - Apollo Platform")
        self.assertIn(heading, apollo["descriptionPlain"])
        self.assertIn(apollo_raw["additionalPlain"].strip()[:60], apollo["descriptionPlain"])

    def test_internship_maps_to_intern(self):
        self.assertEqual(by_title(self.postings, "Deployment Strategist, Internship")["employmentType"], "Intern")

    def test_a_remote_us_posting_fits_as_us_remote(self):
        remote = next(p for p in self.postings if p["workplaceType"] == "remote")
        self.assertTrue(remote["_us_remote"])
        self.assertTrue(rule.check_location(remote, JANE)["passed"])
        self.assertFalse(by_title(self.postings, "Software Engineer - Apollo Platform")["_us_remote"])

    def test_the_status_check_reads_the_us_government_role(self):
        gov = by_title(self.postings, "Deployment Strategist, New Grad - Intel, US Government")
        self.assertEqual(gov["address"]["postalAddress"]["addressRegion"], "District of Columbia")
        self.assertEqual(rule.judge(gov, JANE)["verdict"], "not_relevant")


class AshbyTest(unittest.TestCase):
    def test_ashby_jobs_keep_their_own_fields(self):
        raw = json.loads(fixture("ashby-openai-excerpt.json"))
        postings = providers.read("ashby", 200, fixture("ashby-openai-excerpt.json"))
        self.assertEqual([p["id"] for p in postings], [j["id"] for j in raw["jobs"]])
        for mapped, original in zip(postings, raw["jobs"]):
            self.assertEqual({k: v for k, v in mapped.items() if k != "_system"}, original)


class PlaceTest(unittest.TestCase):
    def test_city_then_state_code(self):
        self.assertEqual(providers.postal("Palo Alto, CA")["postalAddress"]["addressRegion"], "California")
        self.assertEqual(providers.postal("Austin, TX United States")["postalAddress"]["addressLocality"], "Austin")

    def test_nothing_is_guessed(self):
        for text in ("London", "Remote - US", "United States", "Toronto, ON", "Paris, France", None):
            with self.subTest(text=text):
                self.assertEqual(providers.postal(text), {})


if __name__ == "__main__":
    unittest.main()
