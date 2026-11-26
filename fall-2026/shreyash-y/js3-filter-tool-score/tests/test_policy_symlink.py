"""BOUNDARY-TESTS.md row 21, added 2026-11-10 after review. The mutation check showed that deleting
the explicit no-symlink line in Files._writable left every test green: row 11's symlink points
outside runs/, so the real-path check alone refuses it. Here the link and its target are both
inside runs/ and the target does not exist yet, so neither the real-path check nor the
overwrite-approval guard can stop the write. Only the no-symlink rule can."""
import os
import pathlib
import tempfile
import unittest

from jsagent import policy


class SymlinkInsideRuns(unittest.TestCase):
    def test_21_symlink_to_new_file_inside_runs_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = pathlib.Path(tmp).resolve() / "proj"
            runs = project / "runs"
            (runs / "r1").mkdir(parents=True)
            target = runs / "r1" / "target.json"
            os.symlink(target, runs / "alias.json")
            with self.assertRaises(policy.PolicyViolation) as cm:
                policy.Files(project, runs).write(runs / "alias.json", b"{}")
            self.assertIn("symlink", str(cm.exception))
            self.assertFalse(target.exists(), "nothing may be written through the link")
            # Added 2026-11-10 at review: the link itself must be left as it was, too.
            self.assertTrue((runs / "alias.json").is_symlink())
            self.assertEqual(os.readlink(runs / "alias.json"), str(target))


if __name__ == "__main__":
    unittest.main()
