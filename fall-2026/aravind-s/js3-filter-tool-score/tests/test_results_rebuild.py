"""The committed results rebuild byte for byte from committed files.

- js3/audit/<run>/RESULTS.md, by tools/score_audit.py's score() and write_results();
- js3/claims/<run>/RESULTS.md, by tools/score_claims.py's score() and write_results();
- js3/score/EXPERIMENTS.md, by tools/heldout_experiments.py's report path (report_from_saved()) from the saved runs:
  nothing is measured again, and the one-touch guard (preflight(), on the measuring path only) is never reached;
- js3/checks/BASELINES.md, BOILERPLATE.md and CARD-REBUILD.md, by their tools' render().

The three older tools only write in place, so each runs on a copy of its folder in a temporary directory, under the
same folder name (their reports name it); no committed tool is changed for this. Every test also checks that the
committed files it rebuilds are unchanged afterwards.
"""

import contextlib
import importlib.util
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from .loop_helpers import REPO

RUN_ID = "2026-11-21T044414Z"
AUDIT = REPO / "js3" / "audit" / RUN_ID
CLAIMS = REPO / "js3" / "claims" / RUN_ID
SCORE = REPO / "js3" / "score"
FILTER_RUN = REPO / "js3" / "filter-run" / RUN_ID
CHECKS = REPO / "js3" / "checks"
FIRST_LINE = "Computed by Claude Code on 2026-11-24 from committed files, after the fact. Not a new measurement."


def tool(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot(*folders) -> dict:
    return {p: p.read_bytes() for folder in folders for p in sorted(Path(folder).rglob("*")) if p.is_file()}


@unittest.skipUnless(AUDIT.exists() and CLAIMS.exists() and (SCORE / "runs").exists() and FILTER_RUN.exists(),
                     "the committed JS3 results are not in this copy of the repo")
class CommittedResultsRebuildTest(unittest.TestCase):
    def test_the_audit_results_rebuild_from_the_verdicts_and_the_sealed_answers(self):
        score_audit = tool("score_audit")
        before = snapshot(AUDIT)
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / RUN_ID
            shutil.copytree(AUDIT, copy)
            text = score_audit.write_results(copy, FILTER_RUN, score_audit.score(copy, FILTER_RUN))
        self.assertEqual(text.encode("utf-8"), (AUDIT / "RESULTS.md").read_bytes())
        self.assertEqual(snapshot(AUDIT), before)

    def test_the_claims_results_rebuild_from_the_labels_and_the_sealed_checker(self):
        score_claims = tool("score_claims")
        before = snapshot(CLAIMS)
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / RUN_ID
            shutil.copytree(CLAIMS, copy)
            text = score_claims.write_results(copy, score_claims.score(copy))
        self.assertEqual(text.encode("utf-8"), (CLAIMS / "RESULTS.md").read_bytes())
        self.assertEqual(snapshot(CLAIMS), before)

    def test_the_experiments_report_rebuilds_from_the_saved_runs_without_a_new_touch(self):
        hx = tool("heldout_experiments")  # a module object of this test's own, so the patch below stays here
        before = snapshot(SCORE)
        runs = sorted(p.name for p in (SCORE / "runs").iterdir())
        self.assertEqual(len(runs), 1)  # the one measurement
        with tempfile.TemporaryDirectory() as tmp:
            score = Path(tmp) / "score"
            shutil.copytree(SCORE / "runs", score / "runs")
            saved = snapshot(score / "runs")
            original = hx.SCORE
            hx.SCORE = score  # report_from_saved() reads SCORE / "runs"; write_report() writes SCORE / "EXPERIMENTS.md"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(hx.report_from_saved(), 0)
            finally:
                hx.SCORE = original
            rebuilt = (score / "EXPERIMENTS.md").read_bytes()
            self.assertEqual(sorted(p.name for p in (score / "runs").iterdir()), runs)  # no new run folder
            self.assertEqual({p.name: b for p, b in snapshot(score / "runs").items()},
                             {p.name: b for p, b in saved.items()})  # the saved runs, whole-run.json too, untouched
        self.assertEqual(rebuilt, (SCORE / "EXPERIMENTS.md").read_bytes())
        self.assertEqual(snapshot(SCORE), before)


@unittest.skipUnless(CHECKS.exists() and FILTER_RUN.exists(),
                     "the committed JS3 checks are not in this copy of the repo")
class CommittedChecksRebuildTest(unittest.TestCase):
    """The three diagnostics of 2026-11-24 are what their tools compute from the committed files today."""

    def rebuilds(self, name: str, report: str, *watched):
        before = snapshot(CHECKS, *watched)
        module = tool(name)
        text = module.render()  # render() writes nothing
        committed = (CHECKS / report).read_text(encoding="utf-8")
        self.assertTrue(committed.startswith(FIRST_LINE + f" Rebuild: `python3 tools/{name}.py`"), report)
        self.assertEqual(text.encode("utf-8"), (CHECKS / report).read_bytes(), report)
        self.assertEqual(snapshot(CHECKS, *watched), before)

    def test_baselines(self):
        self.rebuilds("baselines", "BASELINES.md", REPO / "js3" / "audit", REPO / "js3" / "heldout")

    def test_boilerplate(self):
        self.rebuilds("boilerplate_check", "BOILERPLATE.md")

    def test_card_rebuild(self):
        self.rebuilds("card_rebuild_check", "CARD-REBUILD.md", REPO / "js3" / "audit", REPO / "js3" / "heldout")


if __name__ == "__main__":
    unittest.main()
