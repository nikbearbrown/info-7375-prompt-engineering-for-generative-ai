"""
Tests written from CONTRACT.md BEFORE the implementation existed (commit order shows it).
Each test names the contract section it enforces. Offline: no network, no Claude call.

Run from the folder root:  python -m unittest discover -s tests -v
"""
import json
import os
import sys
import tempfile
import shutil
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from agent import persona, rule, watch, judge, report  # noqa: E402

RESUME = json.load(open(os.path.join(ROOT, "persona", "resume.json"), encoding="utf-8"))


def job(jid, title="Data Analyst", loc="San Francisco, CA, US", content="Use SQL and Python daily."):
    return {"id": jid, "title": title, "location": {"name": loc}, "content": content,
            "absolute_url": f"https://example.com/jobs/{jid}"}


def checks(result):
    return {r["check"]: r for r in result["reasons"]}


class PersonaTests(unittest.TestCase):          # Contract §1 In, §3 Refuses (2)
    def test_fictional_persona_validates(self):
        persona.validate_resume(RESUME)

    def test_real_looking_email_is_refused(self):
        bad = dict(RESUME, email="someone@gmail.com")
        with self.assertRaises(persona.PersonaError):
            persona.validate_resume(bad)

    def test_non_555_phone_is_refused(self):
        bad = dict(RESUME, phone="(617) 823-1234")
        with self.assertRaises(persona.PersonaError):
            persona.validate_resume(bad)

    def test_missing_field_is_refused(self):
        bad = {k: v for k, v in RESUME.items() if k != "skills"}
        with self.assertRaises(persona.PersonaError):
            persona.validate_resume(bad)


class WatchTests(unittest.TestCase):            # Contract §2 Out, §3 Refuses (1)(4), §6 failure
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_once(self, jobs):
        raw = json.dumps({"jobs": jobs}).encode("utf-8")
        return watch.run_watch("pinterest", self.tmp, ["boards-api.greenhouse.io"], fetcher=lambda url: raw,
                               stamp=f"t{len(os.listdir(self.tmp))}")

    def test_baseline_reports_nothing_new(self):           # failure (1)
        new = self.run_once([job(1), job(2)])
        self.assertEqual(new, [])
        state = json.load(open(os.path.join(self.tmp, "state", "seen_ids.json")))
        self.assertEqual(sorted(state["seen_ids"]), [1, 2])

    def test_second_run_reports_only_unseen(self):         # failure (2)
        self.run_once([job(1), job(2)])
        new = self.run_once([job(1), job(2), job(3)])
        self.assertEqual([j["id"] for j in new], [3])
        again = self.run_once([job(1), job(2), job(3)])
        self.assertEqual(again, [])

    def test_duplicate_id_in_one_response_reported_once(self):   # failure (2)
        self.run_once([job(1)])
        new = self.run_once([job(1), job(5), job(5)])
        self.assertEqual([j["id"] for j in new], [5])

    def test_only_postings_in_this_response(self):         # failure (3)
        self.run_once([job(1), job(2)])
        new = self.run_once([job(7)])                       # 1 and 2 disappeared; 7 is new
        self.assertEqual([j["id"] for j in new], [7])

    def test_raw_response_saved_unchanged(self):           # §2 evidence
        raw = json.dumps({"jobs": [job(1)]}).encode("utf-8")
        watch.run_watch("pinterest", self.tmp, ["boards-api.greenhouse.io"], fetcher=lambda url: raw, stamp="x")
        saved = [f for f in os.listdir(os.path.join(self.tmp, "evidence"))]
        self.assertEqual(len(saved), 1)
        with open(os.path.join(self.tmp, "evidence", saved[0]), "rb") as f:
            self.assertEqual(f.read(), raw)

    def test_same_second_runs_keep_both_evidence_files(self):   # found by the seeded run, 2026-10-30
        raw = json.dumps({"jobs": [job(1)]}).encode("utf-8")
        for _ in range(2):
            watch.run_watch("pinterest", self.tmp, ["boards-api.greenhouse.io"], fetcher=lambda url: raw, stamp="same")
        self.assertEqual(len(os.listdir(os.path.join(self.tmp, "evidence"))), 2)

    def test_host_not_on_allowlist_is_refused(self):       # §3 (1)
        called = []
        with self.assertRaises(watch.NotAllowed):
            watch.fetch("https://evil.example.org/jobs", ["boards-api.greenhouse.io"], fetcher=lambda u: called.append(u))
        self.assertEqual(called, [])


class RuleTests(unittest.TestCase):             # Contract §4
    def v(self, **kw):
        return rule.judge(job(1, **kw), RESUME)

    def test_relevant_posting(self):
        r = self.v(content="2+ years of SQL and Python. Tableau a plus.")
        self.assertEqual(r["verdict"], "relevant")
        self.assertEqual(r["label"], "record")

    def test_r1_title_family(self):
        self.assertEqual(checks(self.v(title="Software Engineer"))["R1"]["result"], "fail")

    def test_r2_senior_word(self):
        self.assertEqual(checks(self.v(title="Senior Data Analyst"))["R2"]["result"], "fail")
        self.assertEqual(checks(self.v(title="Data Analyst III"))["R2"]["result"], "fail")
        self.assertEqual(checks(self.v(title="Data Analyst, Leadership Team"))["R2"]["result"], "pass")   # whole words

    def test_r3_location(self):
        self.assertEqual(checks(self.v(loc="Remote"))["R3"]["result"], "fail")
        self.assertEqual(checks(self.v(loc="Toronto, ON, Canada"))["R3"]["result"], "fail")
        self.assertEqual(checks(self.v(loc="Remote, US"))["R3"]["result"], "pass")
        self.assertEqual(checks(self.v(loc="New York, NY"))["R3"]["result"], "pass")

    def test_r3_canada_revision(self):   # CONTRACT revision 2026-10-30
        self.assertEqual(checks(self.v(loc="Toronto, ON, CA"))["R3"]["result"], "fail")
        self.assertEqual(checks(self.v(loc="San Francisco, CA"))["R3"]["result"], "pass")
        self.assertEqual(checks(self.v(loc="San Francisco, CA, US; Toronto, ON, CA"))["R3"]["result"], "pass")

    def test_r4_experience(self):
        self.assertEqual(checks(self.v(content="3+ years of SQL and Python"))["R4"]["result"], "fail")
        self.assertEqual(checks(self.v(content="2-4 years of SQL and Python"))["R4"]["result"], "pass")
        self.assertEqual(checks(self.v(content="at least 5 years with SQL, Python"))["R4"]["result"], "fail")
        self.assertEqual(checks(self.v(content="SQL and Python"))["R4"]["result"], "pass")

    def test_r5_citizenship_and_boilerplate(self):
        self.assertEqual(checks(self.v(content="Must be a U.S. citizen. SQL, Python."))["R5"]["result"], "fail")
        eeo = "SQL, Python. We hire without regard to race, religion, or citizenship status."
        self.assertEqual(checks(self.v(content=eeo))["R5"]["result"], "pass")

    def test_r5_itar_is_a_whole_word(self):   # found 2026-10-30: 'ITAR' matched inside 'military'
        self.assertEqual(checks(self.v(content="Bachelor's degree, or equivalent military experience. SQL, Python."))["R5"]["result"], "pass")
        self.assertEqual(checks(self.v(content="This role is subject to ITAR. SQL, Python."))["R5"]["result"], "fail")

    def test_r6_sponsorship(self):
        self.assertEqual(checks(self.v(content="SQL, Python. We will not sponsor visas."))["R6"]["result"], "fail")

    def test_r7_phd(self):
        self.assertEqual(checks(self.v(content="PhD required. SQL, Python."))["R7"]["result"], "fail")
        self.assertEqual(checks(self.v(content="PhD preferred. SQL, Python."))["R7"]["result"], "pass")

    def test_r9_graduation_window(self):   # CONTRACT revision 2026-10-30 (R9); persona window 2027-05..2027-12
        by = "Complete your degree by August 2027 or earlier. SQL, Python."
        self.assertEqual(checks(self.v(content=by))["R9"]["result"], "pass")
        late = "Expectation of graduating in December 2027 or spring/summer 2028. SQL, Python."
        self.assertEqual(checks(self.v(content=late))["R9"]["result"], "pass")      # overlaps at 2027-12 (co-op)
        early = "Must complete your degree by December 2026. SQL, Python."
        self.assertEqual(checks(self.v(content=early))["R9"]["result"], "fail")
        self.assertEqual(checks(self.v(content="SQL, Python."))["R9"]["result"], "pass")

    def test_r8_skills_whole_words(self):
        self.assertEqual(checks(self.v(content="Python only."))["R8"]["result"], "fail")
        self.assertEqual(checks(self.v(content="Pythonic SQLite"))["R8"]["result"], "fail")

    def test_html_escaped_content_is_read(self):   # Greenhouse returns HTML-escaped content
        r = self.v(content="&lt;p&gt;Use &lt;strong&gt;SQL&lt;/strong&gt; and Python&lt;/p&gt;")
        self.assertEqual(checks(r)["R8"]["result"], "pass")

    def test_every_reason_names_both_fields(self):   # W2 for the rule
        for c in self.v()["reasons"]:
            self.assertTrue(c["posting_field"] and c["resume_field"], c)

    def test_check_not_applying_for_a_citizen(self):  # §4 "when a check applies"
        citizen = json.loads(json.dumps(RESUME)); citizen["work_authorization"]["us_citizen"] = True
        r = rule.judge(job(1, content="Must be a U.S. citizen. SQL, Python."), citizen)
        self.assertEqual(checks(r)["R5"]["result"], "pass")


class JudgeValidatorTests(unittest.TestCase):    # Contract §7, W2 for Claude
    good = {"verdict": "relevant", "resume_fields": ["skills"], "posting_fields": ["title", "content"],
            "justification": "skills SQL and Python appear in content; title matches target role."}

    def ok(self, obj):
        return judge.validate_answer(json.dumps(obj))

    def test_good_answer_passes_and_is_labelled(self):
        out = self.ok(self.good)
        self.assertEqual(out["label"], "model-judgment")

    def test_rejects_extra_text(self):
        with self.assertRaises(judge.InvalidAnswer):
            judge.validate_answer("Sure! " + json.dumps(self.good))

    def test_rejects_bad_verdict(self):
        with self.assertRaises(judge.InvalidAnswer):
            self.ok(dict(self.good, verdict="maybe"))

    def test_rejects_justification_citing_nothing(self):   # W2
        with self.assertRaises(judge.InvalidAnswer):
            self.ok(dict(self.good, resume_fields=[], justification="Seems like a good fit."))

    def test_rejects_unknown_field(self):
        with self.assertRaises(judge.InvalidAnswer):
            self.ok(dict(self.good, posting_fields=["salary"]))

    def test_rejects_long_justification(self):
        with self.assertRaises(judge.InvalidAnswer):
            self.ok(dict(self.good, justification="x" * 401))


class PromptTests(unittest.TestCase):            # found 2026-10-30: a 6,000-char cut hid Affirm's no-sponsorship line
    def test_prompt_keeps_the_end_of_a_long_description(self):
        long = "SQL and Python. " * 600 + "Please note that visa sponsorship is not available for this position."
        prompt = judge.build_prompt(job(1, content=long), RESUME)
        self.assertIn("visa sponsorship is not available", prompt)


class PairingTests(unittest.TestCase):           # W1
    def test_verdicts_join_by_id_not_position(self):
        jobs = [job(10, title="Data Analyst"), job(20, title="Software Engineer")]
        rule_by_id = {j["id"]: rule.judge(j, RESUME) for j in jobs}
        claude_by_id = {20: {"verdict": "not_relevant", "label": "model-judgment", "justification": "title Software Engineer"},
                        10: {"verdict": "relevant", "label": "model-judgment", "justification": "title Data Analyst"}}
        out = report.assemble(list(reversed(jobs)), rule_by_id, claude_by_id)
        for rec in out:
            r1 = next(c for c in rec["rule_reasons"] if c["check"] == "R1")
            self.assertIn(rec["title"], r1["evidence"])
            self.assertIn(rec["title"], rec["claude"]["justification"])


if __name__ == "__main__":
    unittest.main()
