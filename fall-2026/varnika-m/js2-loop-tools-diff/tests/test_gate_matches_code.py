"""The code's limits and allow-list are the ones written in GATE.md, and nothing else.

A budget changes only by a written decision: if someone edits a number in the
code without editing GATE.md (or the other way round), these tests fail.
"""

import ast
import re
import unittest
from pathlib import Path

from agent import loop, policy

FOLDER = Path(__file__).resolve().parent.parent
GATE = (FOLDER / "GATE.md").read_text(encoding="utf-8")


def gate_budget(name):
    match = re.search(r"^\| %s \| ([0-9,]+)" % re.escape(name), GATE, re.M)
    return int(match.group(1).replace(",", ""))


class GateMatchesCode(unittest.TestCase):
    def test_budgets(self):
        self.assertEqual(loop.LIMITS, {
            "boards": gate_budget("Boards"),
            "requests": gate_budget("Requests"),
            "seconds": gate_budget("Seconds"),
            "seconds_per_request": gate_budget("Seconds per request"),
            "bytes_per_response": gate_budget("Bytes per response"),
        })

    def test_retry_policy(self):
        self.assertIn("at most 2 retries**, after waiting 2 s, then 4 s", GATE)
        self.assertEqual(loop.RETRY_WAITS, [2, 4])
        self.assertIn("longer than 10 s is not retried", GATE)
        self.assertEqual(loop.MAX_RETRY_AFTER, 10)
        self.assertIn("3 refused repeats", GATE)
        self.assertEqual(loop.REPEAT_LIMIT, 3)

    def test_allowed_hosts(self):
        hosts = re.findall(r"^\| `([a-z.-]+\.[a-z]+)` \| `(/[^`]+)` \|", GATE, re.M)
        self.assertEqual(len(hosts), 3)
        self.assertEqual(sorted(policy.ALLOWED_PATHS), sorted(h for h, _ in hosts))

    def test_no_code_outside_tools_touches_the_network_or_writes_files(self):
        """The policy is the only way out: the network and every file read or write are in tools.py only."""
        for path in sorted((FOLDER / "agent").glob("*.py")):
            if path.name == "tools.py":
                continue
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                        for alias in node.names}
            imported |= {node.module.split(".")[0] for node in ast.walk(tree)
                         if isinstance(node, ast.ImportFrom) and node.module}
            for banned in ("urllib", "http", "socket", "subprocess", "smtplib", "shutil"):
                self.assertNotIn(banned, imported, "%s imports %s" % (path.name, banned))
            for call in ("write_text(", "write_bytes(", "read_text(", "read_bytes(", "os.replace(", "os.remove(",
                         "unlink(", "open("):
                self.assertNotIn(call, source, "%s calls %s" % (path.name, call))


if __name__ == "__main__":
    unittest.main()
