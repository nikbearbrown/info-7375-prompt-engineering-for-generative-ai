"""FILTER.md version 1.1 (2026-11-22): added below version 1.0, which is never edited.

The newest Section 7 is what the filter command reads; the v1.0 run, its kits and the MCP server name version 1.0.
"""

import copy
import shutil
import subprocess
import unittest

from job_agent import filter as flt
from job_agent import mcp_server
from job_agent.errors import BrokenInput

from .loop_helpers import REPO
from .test_filter import posting

V10, V11 = flt.load_rules(version="1.0"), flt.load_rules()
JANE = flt.load_profile()


def differences(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += differences(a.get(k), b.get(k), f"{path}.{k}")
        return out
    return [] if a == b else [path]


class VersionsTest(unittest.TestCase):
    def test_the_newest_is_1_1_and_1_0_can_still_be_named(self):
        self.assertEqual((V11["version"], V11["date"]), ("1.1", "2026-11-22"))
        self.assertEqual(V10["version"], "1.0")
        with self.assertRaises(BrokenInput):
            flt.load_rules(version="9.9")

    def test_1_1_differs_from_1_0_only_where_the_document_says(self):
        self.assertEqual(differences(V10, V11),
                         [".date", ".ranking.caution_penalty", ".ranking.shortlist_min", ".splitter_keeps",
                          ".topic_groups.Developer tools", ".version", ".years_company_words"])
        self.assertEqual(V11["ranking"]["shortlist_min"], 50)
        self.assertEqual(V11["ranking"]["caution_penalty"], -10)
        self.assertEqual(V11["years_company_words"], ["grew", "grown", "founded", "history"])
        self.assertNotIn("build systems", V11["topic_groups"]["Developer tools"])
        self.assertEqual(V11["splitter_keeps"], ["U.S.", "e.g.", "i.e."])

    @unittest.skipUnless(shutil.which("git"), "git is not available")
    def test_version_1_0_text_is_unchanged(self):
        old = subprocess.run(["git", "-C", str(REPO), "show", "66e26d9:FILTER.md"], capture_output=True, text=True)
        if old.returncode:
            self.skipTest("this copy has no history for commit 66e26d9")
        now = (REPO / "FILTER.md").read_text(encoding="utf-8")
        self.assertEqual(now.split("## Version 1.1")[0], old.stdout.split("## Changelog")[0])

    def test_the_mcp_server_stays_on_the_version_it_was_evaluated_with(self):
        self.assertEqual(mcp_server.SERVED_FILTER_VERSION, "1.0")


class BehaviorTest(unittest.TestCase):
    def test_an_export_control_line_costs_ten_points_and_never_rejects(self):
        p = posting(description="We build APIs and design SQL schemas. To comply with U.S. export control laws, "
                                "candidates may need to meet legal status requirements.")
        old, new = flt.judge(p, JANE, V10), flt.judge(p, JANE, V11)
        self.assertEqual((old["fate"], new["fate"]), ("kept", "kept"))
        self.assertEqual(new["score"], old["score"] - 10)

    def test_build_systems_no_longer_earns_developer_tools(self):
        p = posting(description="You will build systems that consume ML-based signals.")
        self.assertIn("Developer tools", flt.judge(p, JANE, V10)["topics"])
        self.assertNotIn("Developer tools", flt.judge(p, JANE, V11)["topics"])

    def test_the_cutoff_is_50(self):
        records = [dict(fate="kept", score=s, board="b", title=f"Software Engineer {s}", id=str(s),
                        publishedAt="2026-11-01T00:00:00+00:00") for s in (50, 55, 60)]
        self.assertEqual(flt.shortlist(copy.deepcopy(records), V10)["eligible"], 1)
        self.assertEqual(flt.shortlist(copy.deepcopy(records), V11)["eligible"], 3)

    def test_a_us_citizen_line_is_quoted_whole(self):
        p = posting(description="To comply with a U.S. government contract, applicants must be U.S. citizens with "
                                "an active clearance. We build APIs.")
        old = next(r for r in flt.judge(p, JANE, V10)["rules"] if r["rule"] == "R5")
        new = next(r for r in flt.judge(p, JANE, V11)["rules"] if r["rule"] == "R5")
        self.assertEqual((old["result"], new["result"]), ("reject", "reject"))
        self.assertIn("applicants must be U.S. citizens with an active clearance", new["quote"])
        self.assertNotIn("applicants must be U.S. citizens with an active clearance", old["quote"])

    def test_growth_no_longer_hides_a_years_requirement(self):
        p = posting(description="Have 8+ years of experience, ideally within high-growth startups. We build APIs.")
        old = next(r for r in flt.judge(p, JANE, V10)["rules"] if r["rule"] == "R7")
        new = next(r for r in flt.judge(p, JANE, V11)["rules"] if r["rule"] == "R7")
        self.assertEqual((old["result"], new["result"]), ("cannot_tell", "reject"))


if __name__ == "__main__":
    unittest.main()
