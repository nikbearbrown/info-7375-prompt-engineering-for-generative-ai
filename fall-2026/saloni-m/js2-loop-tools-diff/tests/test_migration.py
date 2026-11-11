"""Patch v2 (Saloni's REVISE decision, review/08-saloni-decision-v1.md).

Written BEFORE the v2 code (commit JS2-8) and expected to FAIL on patch v1, which re-baselined
old (schema 1) history and so hid a real new OpenAI job in live run 2.

Real data, copied into a temp folder (nothing under out/ is written):
  - out/state/seen_ids.json          : live run 1's saved history (schema 1, bare ids)
  - out/runs/<run1>/raw/*            : live run 1's raw responses
  - out/runs/<run2>/raw/*            : live run 2's raw responses, replayed as the "current" boards
Expected: exactly one new job, ashby:openai:76084eee-... "Account Director, Mid-Market | Korea".
"""
import glob
import gzip
import json
import os
import shutil
import unittest

from jsagent.fetch import FetchResult
from jsagent.loop import Loop
from jsagent.providers import PROVIDERS
from tests.helpers import AS, GH, ok, workspace

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN1 = "20261111T004140Z-live"
RUN2 = "20261111T005039Z-live"
KOREA = "ashby:openai:76084eee-9186-4897-ae12-3445307e61be"


def replay_table(run_dir, boards):
    t = {}
    for s, b in boards:
        [p] = glob.glob(os.path.join(run_dir, "raw", f"{s}-{b}-a1.json.gz"))
        with open(p, "rb") as f:
            t[PROVIDERS[s].url(b)] = FetchResult(200, gzip.decompress(f.read()), None)
    return t


class TestSchema1Migration(unittest.TestCase):
    def test_real_run1_history_migrated_reports_only_the_real_new_job(self):
        root, out, pol = workspace()
        shutil.copytree(os.path.join(HERE, "out", "runs", RUN1, "raw"), os.path.join(out, "runs", RUN1, "raw"))
        with open(os.path.join(HERE, "out", "state", "seen_ids.json")) as f:
            old = json.load(f)
        self.assertEqual(old["schema"], 1)  # the real saved history is the old format
        boards = [("greenhouse", "anthropic"), ("greenhouse", "figma"), ("ashby", "openai")]
        table = replay_table(os.path.join(HERE, "out", "runs", RUN2), boards)
        cfg = {"budgets": {"max_boards": 5, "max_requests": 10, "max_seconds": 60, "request_timeout_seconds": 10},
               "allowed_hosts": ["boards-api.greenhouse.io", "api.ashbyhq.com"],
               "boards": [{"system": s, "board": b} for s, b in boards]}
        loop = Loop(cfg, pol, lambda u, t: table[u], out, "migr", "test")
        report, new_state = loop.run(old)
        new = [n["key"] for b in report["boards"] for n in (b["new"] or [])]
        self.assertEqual(new, [KOREA])
        self.assertFalse(any(b["baseline"] for b in report["boards"]))
        self.assertEqual(new_state["schema"], 2)
        self.assertEqual(len(new_state["seen"]), 679 + 144 + 827)

    def test_board_whose_old_raw_is_missing_is_rebaselined_alone_and_logged(self):
        root, out, pol = workspace()
        os.makedirs(os.path.join(out, "runs", "old", "raw"))
        with open(os.path.join(out, "runs", "old", "raw", "greenhouse-a-a1.json.gz"), "wb") as f:
            f.write(gzip.compress(json.dumps({"jobs": [{"id": 1, "title": "x"}]}).encode()))
        old = {"schema": 1, "seen": ["1", "u-3"], "runs": [{"run_id": "old"}],
               "boards": {"greenhouse:a": {"last_ok_run": "old"}, "ashby:c": {"last_ok_run": "old"}}}
        cfg = {"budgets": {"max_boards": 5, "max_requests": 10, "max_seconds": 60, "request_timeout_seconds": 10},
               "allowed_hosts": ["boards-api.greenhouse.io", "api.ashbyhq.com"],
               "boards": [{"system": "greenhouse", "board": "a"}, {"system": "ashby", "board": "c"}]}
        table = {GH.format("a"): ok((1, "x"), (2, "new one")), AS.format("c"): ok(("u-3", "y"))}
        loop = Loop(cfg, pol, lambda u, t: table[u], out, "r2", "test")
        report, _ = loop.run(old)
        a, c = report["boards"]
        self.assertEqual([n["key"] for n in a["new"]], ["greenhouse:a:2"])
        self.assertTrue(c["baseline"])  # no raw for ashby:c, so it is re-baselined, not all-new
        self.assertEqual(c["new"], [])
        ev = [e for e in loop.trace if e["event"] == "state_migrated"]
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["rebaselined_boards"], ["ashby:c"])


if __name__ == "__main__":
    unittest.main()
