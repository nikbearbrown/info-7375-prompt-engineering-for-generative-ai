"""Tests written from CONTRACT.md before jsagent/ was implemented.

Rewritten for CONTRACT v2 (2026-10-31 16:55 ET) before the v2 code changes.
Expected verdicts below were computed by hand from rules R1-R5 against the
constructed fixture tests/fixtures/board_small.json and persona/evan-gordon.resume.json.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from jsagent import audit, fetch, resume, rule, state

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "board_small.json"
PERSONA = ROOT / "persona" / "evan-gordon.resume.json"

# Hand-computed (see comments) - the oracle for the rule judge.
T = True
F = False
EXPECTED = {
    "1001": ("relevant", [T, T, T, T, T]),       # Data Engineer, Remote - US, 4+ yrs, Python+Airflow
    "1002": ("not_relevant", [T, F, T, T, F]),   # "Staff"; 10+ yrs
    "1003": ("not_relevant", [T, T, F, T, T]),   # Remote - Canada: no US region
    "1004": ("relevant", [T, T, T, T, T]),       # Senior allowed; Boston; 4-5 yrs; dbt+SQL
    "1005": ("not_relevant", [T, T, T, T, F]),   # 6+ yrs
    "1006": ("not_relevant", [T, T, T, F, T]),   # only "Spark" (sql/python lowercase); "7 years" has no "experience" nearby
    "1007": ("not_relevant", [T, F, T, T, T]),   # "Intern"
    "1008": ("not_relevant", [F, T, T, T, T]),   # Product Designer
    "1009": ("relevant", [T, T, T, T, T]),       # v2.3: Remote - Seattle passes (Seattle is a listed US marker); first years phrase 4+
}


def load_fixture_postings():
    return fetch.parse_postings(FIXTURE.read_bytes())


class TestAllowList(unittest.TestCase):
    def setUp(self):
        self.allow = fetch.load_allowlist()

    def test_allowlist_is_exactly_the_gate_hosts(self):
        # JS2 (GATE.md v2.3 section 5) adds Lever. Was {"boards-api.greenhouse.io"} in JS1.
        self.assertEqual(self.allow, {"boards-api.greenhouse.io", "api.lever.co"})

    def test_board_url_is_on_allowlist(self):
        fetch.check_url(fetch.board_url("klaviyo"), self.allow)  # no raise

    def test_refuses_other_host(self):
        with self.assertRaises(fetch.HostNotAllowed):
            fetch.check_url("https://api.ashbyhq.com/posting-api/job-board/x", self.allow)  # JS2: Lever is allowed, Ashby is not

    def test_refuses_lookalike_host(self):
        with self.assertRaises(fetch.HostNotAllowed):
            fetch.check_url("https://boards-api.greenhouse.io.evil.example.com/v1", self.allow)

    def test_refuses_plain_http(self):
        with self.assertRaises(fetch.HostNotAllowed):
            fetch.check_url("http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs", self.allow)

    def test_refuses_bad_board_token(self):
        for bad in ["../x", "klaviyo/jobs", "Klaviyo", "a b", ""]:
            with self.assertRaises(ValueError):
                fetch.board_url(bad)

    def test_raw_files_never_overwritten(self):
        # Regression: two fetches in the same second used to share a filename, so the second overwrote the first.
        with tempfile.TemporaryDirectory() as d:
            first = Path(d) / "2026-10-31T173231_samsara_live.json"
            first.write_text("first")
            second = fetch.unused_path(first)
            self.assertNotEqual(second, first)
            second.write_text("second")
            self.assertNotIn(fetch.unused_path(first), (first, second))
            self.assertEqual(first.read_text(), "first")

    def test_board_list_config(self):
        # JS1 watched ONE board; JS2 moved that list to config/boards_js1.json (config/boards.json is now the JS2 plan).
        self.assertEqual(fetch.load_boards(), ["samsara"])
        self.assertEqual(fetch.BOARDS_PATH.name, "boards_js1.json")
        extension = fetch.load_boards(fetch.ROOT / "config" / "boards_all.json")
        self.assertGreaterEqual(len(extension), 100)
        self.assertEqual(len(extension), len(set(extension)))
        for b in extension:
            fetch.check_url(fetch.list_url(b), self.allow)  # every board URL is on the allow-list

    def test_v3_job_detail_url(self):
        fetch.check_url(fetch.job_url("samsara", "8141959"), self.allow)
        for bad in ["81419x", "", "../1", "1/2"]:
            with self.assertRaises(ValueError):
                fetch.job_url("samsara", bad)
        self.assertNotIn("content=true", fetch.list_url("samsara"))

    def test_redirect_off_allowlist_is_blocked(self):
        handler = fetch.AllowListRedirectHandler(self.allow)
        with self.assertRaises(fetch.HostNotAllowed):
            handler.redirect_request(None, None, 302, "Found", {}, "https://evil.example.com/")


class TestResume(unittest.TestCase):
    def test_persona_validates(self):
        r = resume.load_resume(PERSONA)
        self.assertEqual(r["personal"]["name"], "Evan Gordon")

    def test_persona_background_v2_5(self):
        r = resume.load_resume(PERSONA)
        self.assertEqual(r["search"]["years_experience"], 4)
        self.assertEqual(r["education"][0]["degree"], "MS, Information Systems")
        self.assertEqual(r["education"][1]["degree"], "BS, Computer Engineering")
        self.assertTrue(all("(fictional)" in job["company"] for job in r["experience"]))

    def test_refuses_non_example_email(self):
        r = json.loads(PERSONA.read_text())
        r["personal"]["email"] = "someone@gmail.com"
        self.assertTrue(resume.validate_resume(r))

    def test_refuses_real_looking_phone(self):
        r = json.loads(PERSONA.read_text())
        r["personal"]["phone"] = "(617) 373-2000"
        self.assertTrue(resume.validate_resume(r))

    def test_refuses_unmarked_resume(self):
        r = json.loads(PERSONA.read_text())
        r["_comment"] = "my resume"
        self.assertTrue(resume.validate_resume(r))

    def test_refuses_hidden_email_anywhere(self):
        r = json.loads(PERSONA.read_text())
        r["experience"][0]["bullets"].append("contact me at real.person@northeastern.edu")
        self.assertTrue(resume.validate_resume(r))

    def test_load_raises_on_invalid(self):
        r = json.loads(PERSONA.read_text())
        r["personal"]["email"] = "x@gmail.com"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.json"
            p.write_text(json.dumps(r))
            with self.assertRaises(resume.ResumeRefused):
                resume.load_resume(p)

    def test_resolve_paths(self):
        r = resume.load_resume(PERSONA)
        self.assertEqual(resume.resolve(r, "search.locations"), ["Boston, MA"])
        self.assertEqual(resume.resolve(r, "search.max_required_years"), 5)
        self.assertEqual(resume.resolve(r, "education[0].institution"), "Northeastern University")
        with self.assertRaises(KeyError):
            resume.resolve(r, "skills.nonexistent")

    def test_model_copy_has_no_contact_fields(self):
        r = resume.load_resume(PERSONA)
        red = resume.redact_for_model(r)
        text = json.dumps(red)
        for f in ["name", "email", "phone", "linkedin", "github"]:
            self.assertNotIn(r["personal"][f], text)
        self.assertIn("Boston, MA", text)  # location is kept: R3-style reasoning needs it


class TestRule(unittest.TestCase):
    def setUp(self):
        self.r = resume.load_resume(PERSONA)
        self.postings = load_fixture_postings()

    def check(self, p, name):
        return [c for c in rule.judge(p, self.r)["checks"] if c["check"] == name][0]

    def with_(self, **kw):
        p = copy.deepcopy(self.postings[0])
        for k, v in kw.items():
            if k == "location":
                p["location"]["name"] = v
            else:
                p[k] = v
        return p

    def test_parse_strips_html(self):
        p = {x["id"]: x for x in self.postings}["1001"]
        self.assertEqual(p["content"], "You have 4+ years of experience building pipelines in Python and Airflow.")
        self.assertEqual(p["location"]["name"], "Remote - US")

    def test_hand_computed_verdicts(self):
        for p in self.postings:
            v = rule.judge(p, self.r)
            want_verdict, want_checks = EXPECTED[p["id"]]
            self.assertEqual(v["verdict"], want_verdict, p["title"])
            self.assertEqual([c["check"] for c in v["checks"]], ["R1", "R2", "R3", "R4", "R5"])
            self.assertEqual([c["passed"] for c in v["checks"]], want_checks, p["title"])

    def test_verdict_is_labeled_record(self):
        v = rule.judge(self.postings[0], self.r)
        self.assertEqual(v["kind"], "record")
        self.assertEqual(v["posting_id"], "1001")

    def test_r1_data_analyst_added_in_v2_1(self):
        self.assertTrue(self.check(self.with_(title="Data Analyst II"), "R1")["passed"])
        self.assertTrue(self.check(self.with_(title="Senior Data Analyst, Growth"), "R1")["passed"])
        self.assertFalse(self.check(self.with_(title="Data Scientist"), "R1")["passed"])
        staff = rule.judge(self.with_(title="Staff Data Analyst"), self.r)
        self.assertEqual(staff["verdict"], "not_relevant")  # R2 still excludes Staff

    def test_r2_senior_allowed_intern_not_inside_internal(self):
        self.assertTrue(self.check(self.with_(title="Senior Data Engineer"), "R2")["passed"])
        self.assertTrue(self.check(self.with_(title="Data Engineer, Internal Tools"), "R2")["passed"])
        self.assertFalse(self.check(self.with_(title="Lead Data Engineer"), "R2")["passed"])

    def test_r3_locations(self):
        # v2.3: Boston (preferred), remote in the US, or on-site/hybrid anywhere in the US (relocation).
        cases = {"Remote - US": T, "Remote (U.S.)": T, "Remote - USA": T, "Remote, United States": T,
                 "Remote - MA": T, "Boston, MA": T, "Hybrid - Boston": T, "Remote - Seattle": T,
                 "Remote - SF Bay Area": T, "San Francisco Bay Area": T, "San Francisco, California, United States": T,
                 "Hybrid - New York, NY": T, "Mountain View, California (HQ)": T, "Washington, DC": T, "United States": T,
                 "Remote - Canada; Remote - US": T,
                 "Remote - Canada": F, "Remote - India": F, "London, UK": F, "Bengaluru, India": F,
                 "Toronto, Ontario, Canada": F, "Vancouver, British Columbia, Canada": F,
                 "São Paulo, São Paulo, Brazil": F, "Remote, Poland": F, "Remote - Boise": F}
        for loc, want in cases.items():
            self.assertEqual(self.check(self.with_(location=loc), "R3")["passed"], want, loc)

    def test_r3_boston_is_preferred_not_required(self):
        boston = self.check(self.with_(location="Boston, MA"), "R3")
        sf = self.check(self.with_(location="San Francisco, CA"), "R3")
        self.assertTrue(boston["preferred"])
        self.assertFalse(sf["preferred"])
        self.assertTrue(sf["passed"])
        self.assertEqual(rule.judge(self.with_(location="San Francisco, CA"), self.r)["verdict"], "relevant")

    def test_r3_respects_flags(self):
        r = copy.deepcopy(self.r)
        r["search"]["open_to_relocate"] = False
        self.assertFalse(rule.check_r3(self.with_(location="San Francisco, CA"), r)["passed"])
        self.assertTrue(rule.check_r3(self.with_(location="Remote - US"), r)["passed"])
        self.assertTrue(rule.check_r3(self.with_(location="Boston, MA"), r)["passed"])
        r["search"]["open_to_remote"] = False
        self.assertFalse(rule.check_r3(self.with_(location="Remote - US"), r)["passed"])

    def test_r4_case_sensitive_and_whole_word(self):
        p = {x["id"]: x for x in self.postings}["1006"]
        self.assertEqual(self.check(p, "R4")["posting"]["value"], ["Spark"])
        self.assertEqual(self.check(self.with_(content="Scalable systems in Python."), "R4")["posting"]["value"], ["Python"])

    def test_r4_counts_bi_tools_added_in_v2_2(self):
        c = self.check(self.with_(content="Dashboards in Tableau and Power BI."), "R4")
        self.assertEqual(c["posting"]["value"], ["Tableau", "Power BI"])
        self.assertTrue(c["passed"])
        self.assertEqual(self.check(self.with_(content="We use PowerBI."), "R4")["posting"]["value"], [])  # exact spelling only

    def test_r4_ignores_familiar_with_not_shipped(self):
        self.assertFalse(self.check(self.with_(content="Flink and Kubernetes and Python."), "R4")["passed"])

    def test_r5_years(self):
        cases = {
            "Requires 5 years of experience.": ("5 years", T),
            "Requires 6 years of experience.": ("6 years", F),
            "Experience: 3+ years in data roles.": ("3+ years", T),
            "2 to 4 years of relevant experience": ("2 to 4 years", T),
            "7–9 years experience": ("7–9 years", F),
            "Our company is 12 years old. No requirement listed.": ("", T),
        }
        for text, (value, want) in cases.items():
            c = self.check(self.with_(content=text), "R5")
            self.assertEqual((c["posting"]["value"], c["passed"]), (value, want), text)

    def test_r5_preferred_years_v2_4(self):
        # 0-4 preferred; exactly 5 still relevant but not preferred; >5 invalid; unknown not preferred.
        cases = {
            "0-1 years of experience": (T, T),
            "2+ years of experience": (T, T),
            "4-5 years of professional experience": (T, T),
            "5 years of experience": (T, F),
            "5+ years of experience": (T, F),
            "6+ years of experience": (F, F),
            "No requirement listed.": (T, F),
        }
        for text, want in cases.items():
            c = self.check(self.with_(content=text), "R5")
            self.assertEqual((c["passed"], c["preferred"]), want, text)

    def test_preferences_never_change_verdict(self):
        p = {x["id"]: x for x in self.postings}["1004"]  # Senior Analytics Engineer, Boston, 4-5 years
        v = rule.judge(p, self.r)
        self.assertEqual((v["verdict"], v["preferred_location"], v["preferred_years"]), ("relevant", T, T))
        five = rule.judge(self.with_(content="5+ years of experience with Python and Airflow.", location="Remote - US"), self.r)
        self.assertEqual((five["verdict"], five["preferred_location"], five["preferred_years"]), ("relevant", F, F))

    def test_r5_uses_first_phrase(self):
        p = {x["id"]: x for x in self.postings}["1009"]
        self.assertEqual(self.check(p, "R5")["posting"]["value"], "4+ years")

    def test_audit_accepts_correct_verdicts(self):
        verdicts = [rule.judge(p, self.r) for p in self.postings]
        self.assertEqual(audit.audit_verdicts(self.postings, self.r, verdicts), [])


class TestState(unittest.TestCase):
    def setUp(self):
        self.postings = load_fixture_postings()

    def test_baseline_reports_none_new(self):
        is_baseline, new = state.diff_new(None, self.postings)
        self.assertTrue(is_baseline)
        self.assertEqual(new, [])

    def test_second_run_reports_only_added_ids(self):
        first = self.postings[:4]
        st = state.update_state(None, first, {"run_id": "r1"})
        is_baseline, new = state.diff_new(st, self.postings)
        self.assertFalse(is_baseline)
        self.assertEqual(sorted(p["id"] for p in new), ["1005", "1006", "1007", "1008", "1009"])

    def test_changed_title_same_id_is_not_new(self):
        st = state.update_state(None, self.postings, {"run_id": "r1"})
        changed = copy.deepcopy(self.postings)
        changed[0]["title"] = "Renamed"
        self.assertEqual(state.diff_new(st, changed)[1], [])

    def test_removed_then_returned_is_not_new(self):
        st = state.update_state(None, self.postings, {"run_id": "r1"})
        st = state.update_state(st, self.postings[1:], {"run_id": "r2"})
        self.assertEqual(state.diff_new(st, self.postings)[1], [])

    def tag(self, board, postings):
        return [dict(p, board=board) for p in postings]

    def test_v3_new_board_is_baselined(self):
        a = self.tag("alpha", self.postings[:3])
        st = state.update_state(None, a, {"run_id": "r1"})
        b = self.tag("beta", copy.deepcopy(self.postings[3:]))
        is_baseline, new = state.diff_new(st, a + b)
        self.assertFalse(is_baseline)
        self.assertEqual(new, [])  # beta never seen before: baselined, nothing new
        self.assertEqual(state.new_boards(st, a + b), ["beta"])

    def test_v3_failed_board_loses_nothing(self):
        a, b = self.tag("alpha", self.postings[:3]), self.tag("beta", self.postings[3:])
        st = state.update_state(None, a + b, {"run_id": "r1"})
        st = state.update_state(st, a, {"run_id": "r2"})  # beta failed in r2
        self.assertEqual(state.diff_new(st, a + b)[1], [])  # beta back: nothing re-reported
        self.assertIn("beta", st["seen_boards"])

    def test_v3_empty_board_counts_as_seen(self):
        # Regression: seen_boards was built from postings, so a board with zero jobs was never recorded and its
        # first real postings would later be silently baselined instead of reported as new.
        a = self.tag("alpha", self.postings[:3])
        st = state.update_state(None, a, {"run_id": "r1"}, fetched_boards=["alpha", "empty"])
        self.assertIn("empty", st["seen_boards"])
        later = self.tag("empty", copy.deepcopy(self.postings[3:5]))
        self.assertEqual(sorted(p["id"] for p in state.diff_new(st, a + later)[1]), ["1004", "1005"])
        self.assertEqual(state.new_boards(st, a + later), [])

    def test_v3_duplicate_ids_across_boards_stop_the_run(self):
        a = self.tag("alpha", self.postings[:2])
        b = self.tag("beta", self.postings[:1])
        with self.assertRaises(ValueError):
            state.check_unique_ids(a + b)

    def test_state_roundtrip(self):
        st = state.update_state(None, self.postings, {"run_id": "r1"})
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            state.save_state(p, st)
            self.assertEqual(state.load_state(p), st)
            self.assertIsNone(state.load_state(Path(d) / "missing.json"))


if __name__ == "__main__":
    unittest.main()
