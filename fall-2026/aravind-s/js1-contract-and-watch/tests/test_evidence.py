"""Evidence helpers: the code fingerprint and the git commit a report names."""

import shutil
import tempfile
import unittest
from pathlib import Path

from job_agent import evidence


class EvidenceTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)

    def test_the_fingerprint_changes_when_any_source_file_changes(self):
        package = self.dir / "pkg"
        package.mkdir()
        (package / "a.py").write_text("x = 1\n", encoding="utf-8")
        (package / "b.py").write_text("y = 2\n", encoding="utf-8")
        before = evidence.code_fingerprint(package)
        self.assertEqual(before, evidence.code_fingerprint(package))
        (package / "b.py").write_text("y = 3\n", encoding="utf-8")
        self.assertNotEqual(before, evidence.code_fingerprint(package))

    def test_git_head_reads_a_loose_ref_a_packed_ref_or_nothing(self):
        git = self.dir / ".git"
        (git / "refs" / "heads").mkdir(parents=True)
        (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        self.assertIsNone(evidence.git_head(self.dir))
        (git / "packed-refs").write_text("# pack-refs\n" + "a" * 40 + " refs/heads/main\n", encoding="utf-8")
        self.assertEqual(evidence.git_head(self.dir), "a" * 40)
        (git / "refs" / "heads" / "main").write_text("b" * 40 + "\n", encoding="utf-8")
        self.assertEqual(evidence.git_head(self.dir), "b" * 40)
        self.assertIsNone(evidence.git_head(self.dir / "no-such-repo"))


if __name__ == "__main__":
    unittest.main()
