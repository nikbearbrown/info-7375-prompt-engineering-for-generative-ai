"""REVIEW PACKET test, written BEFORE the patch (2026-11-10), from my rule of 2026-11-09 ~3:38 pm:
"Keep the IDs. A valid empty list tells me the board has zero postings right now. It doesn't erase what the agent saw
before. If job 123 was already seen, disappears during an empty run, and comes back tomorrow, I'd treat it as a returning
posting. A job ID the agent has never seen would count as new. The empty run should still report success, zero current
postings, and zero new jobs."
Defect (found by Claude Code reviewing stage B): watch.py REPLACES a board's seen ids with the current ids, so an empty
list wipes them and the next run reports every job as new."""
import json, tempfile, unittest
from pathlib import Path
import watch
from watcher.fetch import Response

def gh(*ids): return Response(200, json.dumps({"jobs": [{"id": i, "title": f"Job {i}"} for i in ids]}).encode())

class EmptyListKeepsSeenIds(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()); (self.tmp / "reports/job-watch").mkdir(parents=True)
        (self.tmp / "boards.json").write_text(json.dumps({"boards": [{"ats": "greenhouse", "slug": "klaviyo"}]}))
        self.old = (watch.HERE, watch.make_fetch); watch.HERE = self.tmp
    def tearDown(self): watch.HERE, watch.make_fetch = self.old
    def run_with(self, response):
        watch.make_fetch = lambda policy: (lambda board, url, timeout: response)
        watch.cmd_run(watch.argparse.Namespace(boards="boards.json", wrong=None))
        runs = sorted((self.tmp / "reports/job-watch/runs").glob("*/trace.json"))
        return json.loads(runs[-1].read_text())
    def test_returning_jobs_after_an_empty_run_are_not_new(self):
        import time
        self.run_with(gh(1, 2, 3)); time.sleep(1.1)              # run 1: baseline, ids 1 2 3 seen
        empty = self.run_with(gh()); time.sleep(1.1)             # run 2: valid empty list
        b = empty["boards"][0]
        self.assertEqual((b["status"], b["jobs"], b["new"]), ("ok", 0, []))   # success, 0 current, 0 new
        back = self.run_with(gh(1, 2, 3))                        # run 3: the same 3 jobs come back
        self.assertEqual(back["boards"][0]["new"], [], "returning jobs were reported as new: the empty run wiped the seen ids")
    def test_a_never_seen_id_is_still_new(self):
        import time
        self.run_with(gh(1, 2)); time.sleep(1.1); self.run_with(gh()); time.sleep(1.1)
        r = self.run_with(gh(1, 2, 9))
        self.assertEqual([j["id"] for j in r["boards"][0]["new"]], ["9"])

if __name__ == "__main__": unittest.main()
