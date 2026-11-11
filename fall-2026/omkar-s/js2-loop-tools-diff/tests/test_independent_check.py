"""The independent check must catch what the agent's own report would not (offline, constructed)."""
import json
import os
import unittest

from tests.helpers import FakeNet, TempBase, fixture_bytes, ok, rd, wr
from tests.test_loop import B_GH, run
from verify import independent_check as ic

B_EMPTY = {"ats": "greenhouse", "slug": "webflowx"}
SCRIPT = {"/boards/alpha/": [ok(fixture_bytes("greenhouse-2.json"))],
          "/boards/webflowx/": [ok(fixture_bytes("greenhouse-empty.json"))]}


def refs(tb, rows):
    wr(tb.path("config", "reference-counts.json"), json.dumps({"references": rows}))


class IndependentCheck(unittest.TestCase):
    def test_empty_board_contradicted_by_other_ats(self):
        with TempBase() as tb:
            refs(tb, [])
            res, _, _, r = run(tb, [B_GH, B_EMPTY], SCRIPT)
            probe = FakeNet({"job-board/webflowx": [ok(fixture_bytes("ashby-2.json"))],
                             "boards/webflowx/": [ok(fixture_bytes("greenhouse-empty.json"))]})
            _, findings = ic.check(r.run_dir, base=tb.dir, get=probe)
            c3 = [f for f in findings if f["check"] == "C3"]
            self.assertEqual(len(c3), 1)
            self.assertEqual(c3[0]["result"], "CONTRADICTED")
            self.assertIn("ashby has 3 postings", c3[0]["detail"])  # raw recount: 3 entries incl. the unlisted one

    def test_empty_board_contradicted_by_reference_alone(self):
        with TempBase() as tb:
            refs(tb, [{"key": "greenhouse:webflowx", "postings": 27, "date": "2026-09-26", "source": "test"}])
            _, _, _, r = run(tb, [B_EMPTY], SCRIPT)
            _, findings = ic.check(r.run_dir, base=tb.dir, probe=False)
            self.assertEqual([f["result"] for f in findings if f["check"] == "C3"], ["CONTRADICTED"])

    def test_empty_board_with_no_evidence_is_unconfirmed_not_ok(self):
        with TempBase() as tb:
            refs(tb, [])
            _, _, _, r = run(tb, [B_EMPTY], SCRIPT)
            _, findings = ic.check(r.run_dir, base=tb.dir, probe=False)
            self.assertEqual([f["result"] for f in findings if f["check"] == "C3"], ["UNCONFIRMED"])

    def test_tampered_raw_file_is_caught(self):
        with TempBase() as tb:
            refs(tb, [])
            _, _, _, r = run(tb, [B_GH], SCRIPT)
            p = os.path.join(r.raw_dir, "greenhouse-alpha-a1.json")
            wr(p, rd(p).replace("101", "999"))
            _, findings = ic.check(r.run_dir, base=tb.dir, probe=False)
            self.assertIn("CONTRADICTED", [f["result"] for f in findings if f["check"] == "C1"])

    def test_report_count_that_disagrees_with_raw_is_caught(self):
        with TempBase() as tb:
            refs(tb, [])
            res, _, _, r = run(tb, [B_GH], SCRIPT)
            p = os.path.join(r.run_dir, "report.json")
            rep = json.loads(rd(p))
            rep["boards"][0]["postings"] = 5
            wr(p, json.dumps(rep))
            _, findings = ic.check(r.run_dir, base=tb.dir, probe=False)
            self.assertEqual([f["result"] for f in findings if f["check"] == "C2"], ["CONTRADICTED"])

    def test_check_does_not_import_the_loop(self):
        imports = [l.strip() for l in rd(ic.__file__).splitlines() if l.startswith(("import ", "from "))]
        self.assertIn("from agent import policy, store, transport", imports)
        self.assertFalse([l for l in imports if "loop" in l or "ats" in l.split()], imports)


if __name__ == "__main__":
    unittest.main()
