"""CONTRACT.md Refuses 1 and 4: fetch.py is the only module that can reach the network.

Reads every module's imports (without running them) and fails if any other module imports a
networking or messaging library, or if anything but the Claude judge can start a program.
"""

import ast
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent / "job_agent"
NETWORK = {"urllib.request", "urllib.error", "http", "http.client", "http.server", "socket", "ssl", "smtplib",
           "ftplib", "imaplib", "poplib", "telnetlib", "xmlrpc", "webbrowser", "asyncio", "requests", "httpx",
           "urllib3", "aiohttp"}
ALLOWED = {"fetch.py": {"urllib.request", "urllib.error", "http.client"}}  # http.client: to name a dropped answer
STARTS_PROGRAMS = {"subprocess", "os.system", "pty"}
MAY_START_PROGRAMS = {"claude_judge.py"}


def imports(path: Path) -> set:
    names = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


def matches(name: str, banned: set) -> bool:
    return any(name == b or name.startswith(b + ".") for b in banned)


class NetworkDoorTest(unittest.TestCase):
    def test_only_fetch_imports_networking(self):
        for path in sorted(PACKAGE.glob("*.py")):
            used = {n for n in imports(path) if matches(n, NETWORK)}
            with self.subTest(module=path.name):
                self.assertLessEqual(used, ALLOWED.get(path.name, set()))

    def test_only_the_claude_judge_may_start_a_program(self):
        for path in sorted(PACKAGE.glob("*.py")):
            if path.name in MAY_START_PROGRAMS:
                continue
            used = {n for n in imports(path) if matches(n, STARTS_PROGRAMS)}
            source = path.read_text(encoding="utf-8")
            with self.subTest(module=path.name):
                self.assertEqual(used, set())
                self.assertNotIn("os.system(", source)
                self.assertNotIn("os.popen(", source)


if __name__ == "__main__":
    unittest.main()
