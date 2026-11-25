"""BOUNDARY-TESTS.md row 22, added 2026-11-10 after a second review. Predicted and committed before
it was run. A chain of two symlinks: runs/hop1 -> runs/hop2 -> a folder outside runs/. A check that
looked at only the first link would see a path inside runs/; the policy resolves the whole chain."""
import os
import pathlib
import tempfile
import unittest

from jsagent import policy


class NestedSymlinks(unittest.TestCase):
    def test_22_chain_of_links_leading_outside_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp).resolve()
            project, outside = base / "proj", base / "outside"
            runs = project / "runs"
            runs.mkdir(parents=True)
            outside.mkdir()
            os.symlink(outside, runs / "hop2")
            os.symlink(runs / "hop2", runs / "hop1")
            with self.assertRaises(policy.PolicyViolation) as cm:
                policy.Files(project, runs).write(runs / "hop1" / "x.json", b"{}")
            self.assertEqual(cm.exception.kind, "outside-runs")
            self.assertEqual(list(outside.iterdir()), [], "nothing may appear outside runs/")


if __name__ == "__main__":
    unittest.main()
