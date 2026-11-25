"""The rules files match FILTER.md v1.2, the loader deduplicates correctly, and the
saved JS2 input is complete. The loader test uses CONSTRUCTED run folders; the
saved-data tests are skipped if the JS2 folder is not present."""
import json
import tempfile
import unittest
from pathlib import Path

from helpers import J, P, PERSONA_PATH, ROOT, rules

FILTER_MD = (ROOT / "FILTER.md").read_text(encoding="utf-8")


class RulesMatchFilterMd(unittest.TestCase):
    def test_hand_set_numbers(self):
        S = rules()["filter"]["scoring"]
        self.assertEqual(S["role_points"], {"target": 35, "related": 20, "special_review": 20})
        self.assertEqual(S["topic_points"], {"one": 10, "two_or_more": 20})
        self.assertEqual(S["skill_points"], {"one": 10, "two_or_more": 20})
        self.assertEqual((S["us_location_points"], S["experience_compatible_points"]), (15, 10))
        self.assertEqual((S["threshold"], S["near_threshold_range"]), (65, [55, 75]))
        self.assertEqual(rules()["filter"]["review_candidates"]["size"], 10)
        self.assertIn("**Version:** 1.2", FILTER_MD)
        self.assertIn("My initial threshold remains **65 points**.", FILTER_MD)

    @unittest.skipUnless(PERSONA_PATH.exists(), "JS2 persona file not present")
    def test_skills_come_from_the_resume_groups(self):
        real = J.counted_skills(json.loads(PERSONA_PATH.read_text(encoding="utf-8")), rules()["filter"])
        self.assertEqual(sorted(real), sorted(rules()["filter"]["skills"]["expected_counted"]))
        for s in ("Ray", "Kubeflow", "Databricks", "Unity Catalog"):
            self.assertNotIn(s, real)

    def test_standalone_ai_is_not_a_topic_phrase(self):
        phrases = [w.lower() for c, ws in rules()["filter"]["topics"].items() if not c.startswith("_") for w in ws]
        self.assertNotIn("ai", phrases)
        self.assertNotIn("artificial intelligence", phrases)


class Loader(unittest.TestCase):
    def make_run(self, root, name, greenhouse_ids, ashby_ids, title="T"):
        run = root / "runs" / name
        run.mkdir(parents=True)
        for board, ats, fname in P.BOARDS:
            ids = ashby_ids if ats == "ashby" else greenhouse_ids
            jobs = [{"id": i, "title": f"{title} {i}", "location": {"name": "Seattle, WA"}, "content": "&lt;p&gt;x&lt;/p&gt;"}
                    if ats == "greenhouse" else {"id": i, "title": f"{title} {i}", "location": "Seattle", "descriptionHtml": "<p>x</p>"}
                    for i in ids]
            (run / fname).write_text(json.dumps({"jobs": jobs}), encoding="utf-8")

    def test_dedupes_by_board_and_id_and_keeps_the_latest_run(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_run(root, "run-2026-01-01T000000Z", [1, 2], ["a"], title="old")
            self.make_run(root, "run-2026-01-02T000000Z", [2, 3], ["a"], title="new")
            ps, sources = P.load_saved_postings(root)
            keys = [(p["board"], p["id"]) for p in ps]
            self.assertEqual(len(keys), len(set(keys)))
            self.assertEqual(sum(p["board"] == "Databricks" for p in ps), 3)  # ids 1, 2, 3
            two = next(p for p in ps if p["board"] == "Databricks" and p["id"] == "2")
            self.assertEqual((two["title"], two["source_run"]), ("new 2", "run-2026-01-02T000000Z"))
            self.assertEqual(len(sources), 6)

    def test_missing_saved_response_is_an_error_not_zero_postings(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_run(root, "run-2026-01-01T000000Z", [1], ["a"])
            (root / "runs" / "run-2026-01-01T000000Z" / P.BOARDS[0][2]).unlink()
            with self.assertRaises(FileNotFoundError):
                P.load_saved_postings(root)


@unittest.skipUnless((P.DEFAULT_JS2 / "runs").exists(), "saved JS2 runs not present")
class SavedData(unittest.TestCase):
    def test_2418_unique_postings_with_the_expected_board_counts(self):
        ps, _ = P.load_saved_postings()
        exp = rules()["filter"]["expected_postings"]
        self.assertEqual(len(ps), exp["total"])
        for b in ("Databricks", "Anthropic", "OpenAI"):
            self.assertEqual(sum(p["board"] == b for p in ps), exp[b])
        self.assertEqual(len({(p["board"], p["id"]) for p in ps}), exp["total"])


if __name__ == "__main__":
    unittest.main()
