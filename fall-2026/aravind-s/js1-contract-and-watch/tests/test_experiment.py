"""The sampling and experiment reports rebuild from the saved calls alone, and the held-out set waits its turn."""

import importlib.util
import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from .helpers import REPO

spec = importlib.util.spec_from_file_location("experiment_tool", REPO / "tools" / "experiment.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class ExperimentToolTest(unittest.TestCase):
    def test_wilson_intervals(self):
        self.assertEqual([round(x, 3) for x in tool.wilson(7, 10)], [0.397, 0.892])
        self.assertEqual([round(x, 3) for x in tool.wilson(10, 10)], [0.722, 1.0])
        self.assertEqual([round(x, 3) for x in tool.wilson(0, 10)], [0.0, 0.278])

    def test_the_committed_reports_are_what_the_saved_calls_give(self):
        jobs, labels, jane = tool.load()
        for name, build in (("SAMPLING.md", tool.sampling_report), ("EXPERIMENT.md", tool.experiment_report)):
            path = REPO / "experiment" / name
            if path.exists():
                with self.subTest(name):
                    self.assertEqual(path.read_text(encoding="utf-8"), build(jobs, labels, jane))

    def test_the_held_out_set_is_refused_until_both_development_runs_exist_and_runs_once(self):
        saved = tool.EXPERIMENT
        temp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temp)
        tool.EXPERIMENT = temp
        self.addCleanup(setattr, tool, "EXPERIMENT", saved)
        (temp / "baseline-development").mkdir()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(tool.run(REPO / "prompts" / "baseline.txt", "held_out", "m"), 3)
            (temp / "revision-development").mkdir()
            (temp / "baseline-held_out").mkdir()
            self.assertEqual(tool.run(REPO / "prompts" / "baseline.txt", "held_out", "m"), 3)  # already ran once
            self.assertEqual(tool.run(REPO / "prompts" / "other.txt", "held_out", "m"), 3)  # not a developed prompt
            self.assertEqual(tool.run(REPO / "prompts" / "baseline.txt", "development", "m"), 3)  # never re-run


if __name__ == "__main__":
    unittest.main()
