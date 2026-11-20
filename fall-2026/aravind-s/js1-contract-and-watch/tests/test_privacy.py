"""CONTRACT.md Refuses 2: no real contact details anywhere in the repo.

Scans every file git would commit (or every file, in a copy without .git, such as the Canvas zip)
and fails on an email address that does not end in @example.com (GitHub noreply addresses aside)
or a phone number outside 555-0100 to 555-0199.
"""

import os
import re
import subprocess
import unittest
from pathlib import Path

from job_agent.resume import _fictional_phone

REPO = Path(__file__).resolve().parent.parent
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\d-])(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]?\d{3}[ .-]\d{4}(?![\d-])")
ALLOWED_EMAIL_ENDINGS = ("@example.com", "@users.noreply.github.com")
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "scratch", "tmp"}


def repo_files():
    try:
        listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=REPO,
                                capture_output=True, check=True, timeout=60).stdout.decode("utf-8").split("\0")
        return [REPO / name for name in listed if name and (REPO / name).is_file()]
    except (OSError, subprocess.SubprocessError):
        files = []
        for root, dirs, names in os.walk(REPO):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            files += [Path(root) / n for n in names]
        return files


class PrivacyScanTest(unittest.TestCase):
    def test_no_real_email_or_phone_in_any_file(self):
        found = []
        for path in repo_files():
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            rel = path.relative_to(REPO)
            for address in EMAIL.findall(text):
                if not address.lower().endswith(ALLOWED_EMAIL_ENDINGS):
                    found.append(f"{rel}: an email address not on example.com")
            for number in PHONE.findall(text):
                if not _fictional_phone(number.strip()):
                    found.append(f"{rel}: a phone number outside 555-0100 to 555-0199")
        self.assertEqual(found, [], "\n".join(sorted(set(found))))

    def test_no_file_names_this_machines_home_folder(self):
        # Records write the home folder as ~ (the account name stays off GitHub).
        home = str(Path.home())
        found = []
        for path in repo_files():
            try:
                if home in path.read_text(encoding="utf-8"):
                    found.append(str(path.relative_to(REPO)))
            except (UnicodeDecodeError, OSError):
                continue
        self.assertEqual(found, [], "files naming the home folder: " + ", ".join(found))

    def test_the_scan_would_catch_a_real_email_and_phone(self):
        sample = "Reach me at jane.doe" + "@" + "gmail.com or (617) 432-" + "0142."
        self.assertEqual(EMAIL.findall(sample), ["jane.doe" + "@" + "gmail.com"])
        self.assertEqual([_fictional_phone(n) for n in PHONE.findall(sample)], [False])
        self.assertEqual([_fictional_phone(n) for n in PHONE.findall("call (555) 555-0142")], [True])


if __name__ == "__main__":
    unittest.main()
