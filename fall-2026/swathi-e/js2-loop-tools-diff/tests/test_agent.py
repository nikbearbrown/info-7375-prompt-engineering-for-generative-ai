"""Tests for the watch, the allow-list, the persona, and the two wrong versions.

Written by Claude Code on 2026-10-25 against CONTRACT.md. Postings below are
CONSTRUCTED test fixtures, not real Databricks postings.
"""
from datetime import datetime, timedelta, timezone
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import persona  # noqa: E402
import rule  # noqa: E402
import watch  # noqa: E402

_, TARGETS = persona.load_persona()
ET = timezone(timedelta(hours=-4))


def body(*jobs):
    return json.dumps({"jobs": [{"id": i, "title": t, "location": {"name": loc},
                                 "absolute_url": f"https://example.invalid/{i}",
                                 "first_published": None, "updated_at": None}
                                for i, t, loc in jobs]}).encode()


POSTINGS = watch.parse_postings(body(
    (101, "Data Engineer", "San Francisco, California"),
    (102, "Senior Data Scientist", "Remote - US"),
    (103, "New Grad Software Engineer", "Mountain View, California"),
    (104, "Analytics Engineer", "Remote - Germany"),
))


class PersonaValidation(unittest.TestCase):
    def setUp(self):
        self.resume, self.targets = persona.load_persona()

    def test_shipped_persona_validates(self):
        self.assertEqual(self.resume["personal"]["name"], "Priya Nair")
        self.assertEqual(self.targets["target_role"]["secondary"], "Data Engineer")

    def test_rejects_non_example_email(self):
        bad = copy.deepcopy(self.resume)
        bad["personal"]["email"] = "priya@gmail.com"
        with self.assertRaises(persona.PersonaError):
            persona.validate_resume(bad)

    def test_rejects_resume_not_marked_fictional(self):
        bad = copy.deepcopy(self.resume)
        bad["_comment"] = "my resume"
        with self.assertRaises(persona.PersonaError):
            persona.validate_resume(bad)

    def test_rejects_targets_for_another_persona(self):
        bad = copy.deepcopy(self.targets)
        bad["persona"] = "Someone Else"
        with self.assertRaises(persona.PersonaError):
            persona.validate_targets(bad, self.resume)


class AllowList(unittest.TestCase):
    def test_board_url_is_allowed(self):
        self.assertEqual(watch.check_allowed(watch.BOARD_URL), watch.BOARD_URL)

    def test_refuses_other_hosts_and_lookalikes(self):
        for url in ("https://api.lever.co/v0/postings/plaid",
                    "https://boards-api.greenhouse.io.evil.example/v1/boards/databricks/jobs",
                    "http://boards-api.greenhouse.io/v1/boards/databricks/jobs"):
            with self.subTest(url=url), self.assertRaises(watch.HostNotAllowed):
                watch.check_allowed(url)

    def test_refuses_redirect_off_allow_list(self):
        handler = watch._AllowListRedirects()
        with self.assertRaises(watch.HostNotAllowed):
            handler.redirect_request(None, None, 302, "Found", {}, "https://example.com/jobs")


class RuleBoundaries(unittest.TestCase):
    def verdict(self, title, location="San Francisco, California"):
        return rule.judge(title, location, TARGETS)["verdict"]

    def test_contract_examples_for_1b(self):
        self.assertEqual(self.verdict("Software Engineer"), rule.NOT_RELEVANT)
        self.assertEqual(self.verdict("New Grad Marketing"), rule.NOT_RELEVANT)

    def test_whole_words_only(self):
        self.assertEqual(self.verdict("HTML Email Developer"), rule.NOT_RELEVANT)
        self.assertEqual(self.verdict("AI/ML Engineer"), rule.RELEVANT)

    def test_sr_with_period_is_senior(self):
        self.assertEqual(self.verdict("Sr. Data Engineer"), rule.NOT_RELEVANT)

    def test_remote_naming_non_us_country_fails(self):
        self.assertEqual(self.verdict("ML Engineer", "Remote - India"), rule.NOT_RELEVANT)
        self.assertEqual(self.verdict("ML Engineer", "Remote"), rule.RELEVANT)

    def test_intern_fails_on_check_2_not_check_1(self):
        # Hand-fixed case 11 passed before Revision 2 only because check 1 failed.
        checks = rule.judge("Data Science Intern", "Mountain View, California", TARGETS)["checks"]
        self.assertEqual((checks["role"], checks["not_too_senior"]), (True, False))

    def test_early_career_signal_is_noted(self):
        text = rule.judge("New Grad Software Engineer", "Seattle, Washington", TARGETS)["justification"]
        self.assertIn("Early-career signal", text)


class WrongVersionShiftedLabels(unittest.TestCase):
    def setUp(self):
        self.report = watch.build_report(POSTINGS, TARGETS)

    def test_correct_report_passes(self):
        self.assertEqual(watch.pairing_errors(POSTINGS, self.report, TARGETS), [])

    def test_labels_shifted_by_one_are_caught(self):
        shifted = copy.deepcopy(self.report)
        rules = [entry["rule"] for entry in shifted]
        for entry, moved in zip(shifted, rules[1:] + rules[:1]):
            entry["rule"] = moved
        self.assertTrue(watch.pairing_errors(POSTINGS, shifted, TARGETS))

    def test_labels_shuffled_are_caught(self):
        shuffled = copy.deepcopy(self.report)
        shuffled[0]["rule"], shuffled[2]["rule"] = shuffled[2]["rule"], shuffled[0]["rule"]
        self.assertTrue(watch.pairing_errors(POSTINGS, shuffled, TARGETS))

    def test_ids_paired_with_wrong_postings_are_caught(self):
        swapped = copy.deepcopy(self.report)
        swapped[0]["posting_id"], swapped[1]["posting_id"] = swapped[1]["posting_id"], swapped[0]["posting_id"]
        self.assertTrue(watch.pairing_errors(POSTINGS, swapped, TARGETS))


class WrongVersionJustificationCitesNothing(unittest.TestCase):
    def setUp(self):
        self.result = rule.judge("Data Engineer", "San Francisco, California", TARGETS)

    def test_real_justification_names_both_kinds_of_field(self):
        self.assertEqual(rule.justification_errors(self.result), [])

    def test_bare_verdict_is_caught(self):
        bare = dict(self.result, justification="RELEVANT.")
        self.assertEqual(len(rule.justification_errors(bare)), 2)

    def test_resume_fields_missing_is_caught_even_with_correct_verdict(self):
        posting_only = dict(self.result, justification="RELEVANT. posting.title matches a role term.")
        self.assertEqual(rule.justification_errors(posting_only), ["justification names no résumé field"])

    def test_empty_citation_lists_are_caught(self):
        uncited = dict(self.result, cited_posting_fields=[], cited_resume_fields=[])
        self.assertEqual(len(rule.justification_errors(uncited)), 2)


class Watch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.paths = {"state_path": root / "state.json", "raw_dir": root / "raw", "report_dir": root / "reports"}
        self.first, self.second = root / "first.json", root / "second.json"
        self.first.write_bytes(body((1, "Data Engineer", "Texas"), (2, "Recruiter", "London, United Kingdom")))
        self.second.write_bytes(body((1, "Data Engineer", "Texas"), (3, "ML Engineer", "Remote - US")))

    def tearDown(self):
        self.tmp.cleanup()

    def run_file(self, path, day):
        return watch.run(from_file=path, now=datetime(2026, 10, day, 9, tzinfo=ET), **self.paths)

    def test_first_run_is_baseline_with_nothing_new(self):
        summary = self.run_file(self.first, 25)
        self.assertEqual((summary["run_label"], summary["new_postings"]), ("baseline", 0))
        self.assertEqual(json.loads(self.paths["state_path"].read_text())["seen_ids"], [1, 2])

    def test_second_run_reports_only_new_ids_and_is_labelled_seeded(self):
        self.run_file(self.first, 25)
        summary = self.run_file(self.second, 26)
        self.assertTrue(summary["seeded"])
        self.assertEqual([r["posting_id"] for r in summary["report"]], [3])
        self.assertEqual(summary["report"][0]["rule"]["verdict"], rule.RELEVANT)
        self.assertEqual(summary["claude_judge"], "not_run")
        self.assertEqual(summary["report"][0]["claude_judge"]["status"], "not_run")

    def test_same_response_twice_reports_nothing_new(self):
        self.run_file(self.first, 25)
        self.assertEqual(self.run_file(self.first, 26)["new_postings"], 0)

    def test_duplicate_ids_are_refused(self):
        with self.assertRaises(ValueError):
            watch.parse_postings(body((1, "A", "Texas"), (1, "B", "Texas")))


if __name__ == "__main__":
    unittest.main()
