"""Tests written from CONTRACT.md (commit 19bbfae) before the agent code.

Each test names the contract section it checks. The three "Wrong versions"
from the contract each have a test that fails on the buggy behaviour.
"""
import json
import tempfile
import unittest
from pathlib import Path

from agent import fetch, resume, rule, watch

ROOT = Path(__file__).resolve().parent.parent
PERSONA = ROOT / "examples" / "rohan-desai.resume.example.json"


def posting(pid, title, location, content=""):
    return {"id": pid, "title": title, "location": {"name": location},
            "content": content, "absolute_url": f"https://example.invalid/{pid}"}


SKILLED = "We use Python, PostgreSQL and Docker every day."


class TestRuleTitle(unittest.TestCase):
    """The rule, check 1: title."""

    def setUp(self):
        self.r = resume.load(PERSONA)

    def test_engineer_passes(self):
        v = rule.judge(posting(1, "Software Engineer", "Seattle, WA", SKILLED), self.r)
        self.assertTrue(v["checks"]["title"]["passed"])

    def test_developer_passes(self):
        v = rule.judge(posting(1, "Frontend Developer", "Seattle, WA", SKILLED), self.r)
        self.assertTrue(v["checks"]["title"]["passed"])

    def test_seniority_words_fail(self):
        for t in ["Senior Software Engineer", "Staff Engineer", "Principal Engineer",
                  "Lead Developer", "Engineering Manager", "Director, Engineering"]:
            v = rule.judge(posting(1, t, "Seattle, WA", SKILLED), self.r)
            self.assertFalse(v["checks"]["title"]["passed"], t)

    def test_non_engineering_title_fails(self):
        v = rule.judge(posting(1, "Abuse Investigator", "Seattle, WA", SKILLED), self.r)
        self.assertFalse(v["checks"]["title"]["passed"])


class TestRuleLocation(unittest.TestCase):
    """The rule, check 2: location (strings taken from Stripe's board, 2026-10-29)."""

    def setUp(self):
        self.r = resume.load(PERSONA)

    def loc(self, name):
        return rule.judge(posting(1, "Software Engineer", name, SKILLED), self.r)["checks"]["location"]["passed"]

    def test_us_places_pass(self):
        for name in ["Seattle, WA", "US", "United States", "San Francisco, NYC",
                     "US-NYC; US-SF; US-Chicago; US-Atlanta; US-Seattle; US-Remote",
                     "Seattle, San Francisco, or New York", "US - Remote", "Remote from the US"]:
            self.assertTrue(self.loc(name), name)

    def test_plain_remote_counts_as_us(self):
        self.assertTrue(self.loc("Remote"))

    def test_all_places_must_be_us(self):
        for name in ["US, Canada", "SEA, SF, NY, Toronto", "Toronto, CA",
                     "Toronto Canada, San Francisco, Remote in US, Remote in Canada"]:
            self.assertFalse(self.loc(name), name)

    def test_non_us_fails(self):
        for name in ["Dublin", "London", "Bengaluru, India", "Mexico City, MX"]:
            self.assertFalse(self.loc(name), name)

    def test_na_fails(self):
        for name in ["N/A", "na", ""]:
            self.assertFalse(self.loc(name), name)


class TestRuleSkills(unittest.TestCase):
    """The rule, check 3: at least 3 skills, whole word, any case."""

    def setUp(self):
        self.r = resume.load(PERSONA)

    def skills(self, content):
        return rule.judge(posting(1, "Software Engineer", "Seattle, WA", content), self.r)["checks"]["skills"]

    def test_three_skills_pass(self):
        s = self.skills(SKILLED)
        self.assertTrue(s["passed"])
        self.assertEqual(sorted(s["matched"]), ["Docker", "PostgreSQL", "Python"])

    def test_two_skills_fail(self):
        self.assertFalse(self.skills("Python and Docker.")["passed"])

    def test_any_case(self):
        self.assertTrue(self.skills("python, POSTGRESQL, docker")["passed"])

    def test_wrong_version_substring_go_good(self):
        """Wrong version 2: substring matching ('Go' matching 'good')."""
        s = self.skills("A good engineer with JavaScript and PostgreSQL.")
        self.assertNotIn("Go", s["matched"])
        self.assertNotIn("Java", s["matched"])
        self.assertNotIn("SQL", s["matched"])
        self.assertEqual(sorted(s["matched"]), ["JavaScript", "PostgreSQL"])
        self.assertFalse(s["passed"])

    def test_familiar_list_does_not_count(self):
        s = self.skills("GraphQL federation, Python, Docker.")
        self.assertNotIn("GraphQL federation", s["matched"])
        self.assertFalse(s["passed"])

    def test_html_in_content_is_read(self):
        # Greenhouse sends descriptions as escaped HTML.
        s = self.skills("&lt;li&gt;Python&lt;/li&gt;&lt;li&gt;Redis&lt;/li&gt;&lt;li&gt;AWS&lt;/li&gt;")
        self.assertTrue(s["passed"])


class TestOut(unittest.TestCase):
    """Out: verdict plus a justification that cites fields."""

    def setUp(self):
        self.r = resume.load(PERSONA)

    def test_relevant_justification_names_title_location_skills(self):
        v = rule.judge(posting(7, "Software Engineer", "Seattle, WA", SKILLED), self.r)
        self.assertEqual(v["verdict"], "relevant")
        j = v["justification"]
        self.assertIn("engineer", j)
        self.assertIn("Seattle, WA", j)
        for s in ["Python", "PostgreSQL", "Docker"]:
            self.assertIn(s, j)
        self.assertIn("posting.title", j)
        self.assertIn("posting.location.name", j)
        self.assertIn("resume.skills", j)

    def test_not_relevant_says_which_check_failed(self):
        v = rule.judge(posting(7, "Software Engineer", "Dublin", SKILLED), self.r)
        self.assertEqual(v["verdict"], "not relevant")
        self.assertEqual(v["failed_checks"], ["location"])
        self.assertIn("failed: location", v["justification"])

    def test_verdict_is_labeled_a_record(self):
        v = rule.judge(posting(7, "Software Engineer", "Seattle, WA", SKILLED), self.r)
        self.assertEqual(v["judge"], "rule")
        self.assertEqual(v["label"], "record")

    def test_wrong_version_verdicts_on_wrong_posting(self):
        """Wrong version 3: verdicts attached to the wrong posting."""
        ps = [posting(101, "Software Engineer", "Seattle, WA", SKILLED),
              posting(102, "Abuse Investigator", "Dublin", ""),
              posting(103, "Backend Developer", "US", "Go, Redis, Kubernetes")]
        out = rule.judge_all(list(reversed(ps)), self.r)
        by_id = {v["posting_id"]: v for v in out}
        self.assertEqual(by_id[101]["verdict"], "relevant")
        self.assertEqual(by_id[102]["verdict"], "not relevant")
        self.assertEqual(by_id[103]["verdict"], "relevant")
        for v in out:
            src = next(p for p in ps if p["id"] == v["posting_id"])
            self.assertEqual(v["posting_title"], src["title"])


class TestIn(unittest.TestCase):
    """In: résumé needs personal.location and skills; refuses a real résumé."""

    def write(self, data):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(data, f)
        f.close()
        return Path(f.name)

    def base(self):
        return json.loads(PERSONA.read_text())

    def test_persona_loads(self):
        self.assertEqual(resume.load(PERSONA)["personal"]["location"], "Boston, MA")

    def test_missing_location_is_rejected(self):
        d = self.base()
        del d["personal"]["location"]
        with self.assertRaises(resume.ResumeError):
            resume.load(self.write(d))

    def test_empty_skills_marks_everything_not_relevant(self):
        d = self.base()
        d["skills"] = {}
        r = resume.load(self.write(d))
        v = rule.judge(posting(1, "Software Engineer", "Seattle, WA", SKILLED), r)
        self.assertEqual(v["verdict"], "not relevant")
        self.assertIn("skills", v["failed_checks"])

    def test_real_looking_resume_is_refused(self):
        d = self.base()
        d["personal"]["email"] = "someone@gmail.com"
        with self.assertRaises(resume.ResumeError):
            resume.load(self.write(d))


class TestRefuses(unittest.TestCase):
    """Refuses: only boards-api.greenhouse.io is fetched."""

    def test_allowed_host(self):
        fetch.check_allowed("https://boards-api.greenhouse.io/v1/boards/stripe/jobs")

    def test_other_hosts_refused(self):
        for url in ["https://www.linkedin.com/jobs", "https://stripe.com/jobs",
                    "http://boards-api.greenhouse.io/v1/boards/stripe/jobs",
                    "https://boards-api.greenhouse.io.evil.example/x"]:
            with self.assertRaises(fetch.HostNotAllowed, msg=url):
                fetch.check_allowed(url)


class TestWatch(unittest.TestCase):
    """The watch: baseline reports none; later runs report only unseen ids."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.r = resume.load(PERSONA)

    def run_with(self, jobs, label):
        raw = json.dumps({"jobs": jobs}).encode()
        return watch.run_once(raw, self.r, self.dir, run_label=label)

    def test_baseline_reports_none_new(self):
        rep = self.run_with([posting(1, "Software Engineer", "US", SKILLED)], "t1")
        self.assertTrue(rep["baseline"])
        self.assertEqual(rep["new_postings"], [])

    def test_second_run_reports_only_new(self):
        self.run_with([posting(1, "Software Engineer", "US", SKILLED)], "t1")
        rep = self.run_with([posting(1, "Software Engineer", "US", SKILLED),
                             posting(2, "Backend Developer", "US", SKILLED)], "t2")
        self.assertFalse(rep["baseline"])
        self.assertEqual([v["posting_id"] for v in rep["new_postings"]], [2])

    def test_wrong_version_seen_posting_new_again(self):
        """Wrong version 1: a posting seen in an earlier run is reported as new again."""
        self.run_with([posting(1, "A Engineer", "US", SKILLED)], "t1")
        # Posting 1 drops off the board on run 2 and comes back on run 3.
        self.run_with([posting(2, "B Engineer", "US", SKILLED)], "t2")
        rep = self.run_with([posting(2, "B Engineer", "US", SKILLED), posting(1, "A Engineer", "US", SKILLED)], "t3")
        self.assertEqual(rep["new_postings"], [])

    def test_raw_response_saved_byte_for_byte(self):
        raw = json.dumps({"jobs": [posting(1, "X Engineer", "US")]}).encode()
        watch.run_once(raw, self.r, self.dir, run_label="t1")
        self.assertEqual((self.dir / "runs" / "t1" / "raw.json").read_bytes(), raw)

    def test_report_never_contains_resume_personal_details(self):
        rep = self.run_with([posting(1, "Software Engineer", "US", SKILLED)], "t1")
        rep = self.run_with([posting(1, "Software Engineer", "US", SKILLED),
                             posting(2, "Backend Developer", "US", SKILLED)], "t2")
        text = (self.dir / "runs" / "t2" / "report.json").read_text()
        for s in ["rohan.desai@example.com", "555-0127", "Rohan Desai"]:
            self.assertNotIn(s, text)


if __name__ == "__main__":
    unittest.main()
