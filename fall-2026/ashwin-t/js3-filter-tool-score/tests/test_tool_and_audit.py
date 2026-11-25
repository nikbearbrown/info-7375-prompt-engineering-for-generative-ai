"""The real score_posting tool and the audit sampling (offline)."""
import json
import unittest

from jobfilter.audit import LABELS, SELECTION, strata, tally, wilson
from jobfilter.audit_batches import MINIMUM_STRATA, minimum_keys, write_batches
from jobfilter.corpus import HERE
from jobfilter.heldout import heldout_keys
from jobfilter.serve_tool import build_server
from jobfilter.sheets import read_verdicts


def call(server, args, name="score_posting"):
    line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}})
    return json.loads(server.handle_line(line))


class Tool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = build_server()

    def test_scores_a_development_posting(self):
        r = call(self.s, {"key": "greenhouse/klaviyo/8041054003"})["result"]
        body = json.loads(r["content"][0]["text"])
        self.assertFalse(r["isError"])
        self.assertEqual((body["decision"], body["score"], body["filter_version"]), ("KEEP", 8, "v1.0"))

    def test_refuses_every_held_out_posting(self):
        for key in heldout_keys():
            r = call(self.s, {"key": key})["result"]
            self.assertTrue(r["isError"], key)
            self.assertIn("sealed", r["content"][0]["text"])

    def test_unknown_key_is_a_tool_error(self):
        self.assertTrue(call(self.s, {"key": "../../etc/passwd"})["result"]["isError"])


class Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = json.loads((HERE / "runs" / "v1.0" / "decisions-dev.json").read_text())
        cls.sel = json.loads(SELECTION.read_text())

    def test_saved_selection_is_reproducible(self):
        s = strata(self.dev, self.sel["seed"])
        self.assertEqual({k: v["selected"] for k, v in s.items()},
                         {k: v["selected"] for k, v in self.sel["strata"].items()})

    def test_no_held_out_key_in_any_stratum(self):
        held = heldout_keys()
        for v in self.sel["strata"].values():
            self.assertFalse(held & set(v["population"]))

    def test_random_reject_sample_is_30_distinct_rejects(self):
        st = self.sel["strata"]["random_reject"]
        decisions = {d["key"]: d["decision"] for d in self.dev}
        self.assertEqual(len(set(st["selected"])), 30)
        self.assertTrue(all(decisions[k] == "REJECT" for k in st["selected"]))

    def test_wilson_interval(self):
        lo, hi = wilson(0, 30)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.1135, places=3)   # zero errors in 30 is still consistent with ~11%
        lo, hi = wilson(3, 30)
        self.assertAlmostEqual(lo, 0.0346, places=3)
        self.assertAlmostEqual(hi, 0.2562, places=3)
        self.assertEqual(wilson(0, 0), (None, None))


class MinimumSample(unittest.TestCase):
    """The brief's minimum: the saved random rejects, closest calls and kept sample, nothing redrawn."""

    @classmethod
    def setUpClass(cls):
        cls.sel = json.loads(SELECTION.read_text())

    def test_minimum_keeps_every_original_random_reject(self):
        keys = minimum_keys(self.sel)
        self.assertTrue(set(self.sel["strata"]["random_reject"]["selected"]) <= keys)
        self.assertEqual(len(keys), 47)
        self.assertNotIn("exclusion_check", MINIMUM_STRATA)

    def test_batches_are_blind(self):
        write_batches()
        text = (LABELS / "audit-minimum-batches.md").read_text()
        for leak in ("random_reject", "close_below", "close_at", "kept_random", "exclusion_check", "KEEP", "REJECT", "REVIEW"):
            self.assertNotIn(leak, text)
        self.assertEqual(text.count("\n| "), 47 + 5)   # one row per posting plus one header per batch

    def test_blank_rows_are_not_judged_not_verdicts(self):
        tmp = HERE / "tests" / "tmp"
        tmp.mkdir(exist_ok=True)
        f = tmp / "partial.csv"
        f.write_text("n,key,title,verdict,note\n1,a,A,Y,\n2,b,B,,\n")
        self.assertEqual(set(read_verdicts(f, allow_blank=True)), {"a"})
        with self.assertRaises(ValueError):
            read_verdicts(f)
        t = tally({"strata": {"s": {"selected": ["a", "b"], "population_size": 9}}},
                  read_verdicts(f, allow_blank=True), {"a": {"decision": "REJECT"}, "b": {"decision": "REJECT"}})
        self.assertEqual((t["s"]["Y"], t["s"]["not_judged"], t["s"]["selected"]), (1, 1, 2))


if __name__ == "__main__":
    unittest.main()
