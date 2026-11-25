"""The tools/ scripts must start the way a person naturally runs them.

Regression for a real failure Om hit: `python3 tools/replay_from_file.py ...`
raised ModuleNotFoundError: No module named 'agent', because in script mode
Python puts tools/ (not the project root) first on sys.path. Claude Code had
only ever run it as `python3 -m tools.replay_from_file`, which puts the
current directory first, so its own logs never showed the failure.

Each tool is started with --help in a subprocess, in script mode and -m mode,
from the project root and from an unrelated temp directory, with PYTHONPATH
removed from the environment. --help is parsed after all imports, so exit 0
plus a usage line proves the imports resolved. No network, no state needed.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ["replay_from_file", "count_drift_check", "weak_patch_check"]


def _env():
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    return env


class ToolInvocation(unittest.TestCase):
    def _assert_starts(self, argv, cwd):
        p = subprocess.run(argv, cwd=cwd, env=_env(), capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, f"{' '.join(argv)} (cwd={cwd}) failed:\n{p.stderr}")
        self.assertIn("usage:", p.stdout)
        self.assertNotIn("ModuleNotFoundError", p.stderr)

    def test_script_mode_from_project_root(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self._assert_starts([sys.executable, f"tools/{tool}.py", "--help"], ROOT)

    def test_script_mode_from_another_directory(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            for tool in TOOLS:
                with self.subTest(tool=tool):
                    self._assert_starts([sys.executable, str(ROOT / "tools" / f"{tool}.py"), "--help"], elsewhere)

    def test_module_mode_from_project_root(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self._assert_starts([sys.executable, "-m", f"tools.{tool}", "--help"], ROOT)


if __name__ == "__main__":
    unittest.main()
