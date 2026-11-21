"""Privacy scan for files before they are committed (transcripts, run outputs).

Standard library only. Run from the js3-filter-tool-score directory:

    python3 tool/privacy_scan.py tool/transcripts/*.jsonl
    python3 tool/privacy_scan.py --term <extra word> ... <files>

Blocking checks (any hit means: do not commit, report first):
  - the home-directory prefix and other home-path forms, and the current
    user's actual home directory;
  - email addresses, phone numbers, LinkedIn profile links;
  - credential- and token-like strings;
  - identity terms: the local account name, the git user name and email,
    the owners named in the git remotes, the persona's personal fields
    (persona/*.resume.example.json), and any --term given.

Identity terms are read at run time and never printed, so this file holds
no personal value itself. Informational output (not blocking) lists long
unbroken strings, URLs and Claude Code tool-use ids, for a human to review.

For .jsonl files, every line must also parse as JSON.
Exit code: 0 if no blocking hit, 1 otherwise.
"""

import argparse
import getpass
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HOME_PREFIX = "/" + "Users" + "/"  # built in two parts so this file does not match its own check
BLOCKING = {
    "home-directory prefix": re.compile(re.escape(HOME_PREFIX)),
    "other home path": re.compile(r"/home/\w|C:\\\\Users|~/"),
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "phone": re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)"),
    "linkedin profile": re.compile(r"linkedin\.com/in/"),
    "token-like": re.compile(r"sk-[A-Za-z0-9_-]{10,}|sk-ant-|ghp_[A-Za-z0-9]{20,}|github_pat_|AKIA[0-9A-Z]{16}|xox[bap]-"
                             r"|(?i:bearer\s+[A-Za-z0-9._-]{10,})|(?i:api[_-]?key|secret|password|authorization)"),
}
INFO = {
    "long unbroken string (not a sha256)": re.compile(r"\b(?![0-9a-f]{64}\b)[A-Za-z0-9+/=_-]{40,}\b"),
    "url": re.compile(r"https?://[^\"\\ ]+"),
    "Claude Code tool-use id": re.compile(r"toolu_[A-Za-z0-9]+"),
}


def git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=False).stdout
    except OSError:
        return ""


def identity_terms(extra):
    terms = set(extra)
    terms.add(getpass.getuser())
    terms.add(os.path.expanduser("~"))
    terms.add(git("config", "user.name").strip())
    email = git("config", "user.email").strip()
    terms |= {email, email.split("@")[0]}
    for url in git("remote", "-v").split():
        m = re.search(r"github\.com[/:]([^/]+)/", url)
        if m:
            terms.add(m.group(1))
    for f in Path("persona").glob("*.resume.example.json"):
        personal = json.loads(f.read_text(encoding="utf-8")).get("personal", {})
        for value in personal.values():
            if isinstance(value, str):
                terms.add(value)
                terms |= set(value.split()) if " " in value and "," not in value else set()
    return sorted(t for t in terms if len(t) >= 3)


def scan(path, terms):
    text = Path(path).read_text(encoding="utf-8")
    blocking = 0
    print(f"{path}")
    if path.endswith(".jsonl"):
        lines = text.splitlines()
        bad = [n for n, line in enumerate(lines, 1) if not _is_json(line)]
        print(f"  entries: {len(lines)}, invalid JSON lines: {len(bad)}")
        blocking += len(bad)
    for name, rx in BLOCKING.items():
        hits = sorted({m.group() for m in rx.finditer(text)})
        blocking += len(hits)
        print(f"  {name}: {len(hits)}" + (f" {hits[:10]}" if hits else ""))
    lowered = text.lower()
    found = [t for t in terms if t.lower() in lowered]
    blocking += len(found)
    print(f"  identity terms ({len(terms)} checked, values not shown): {len(found)}"
          + (f" {found}" if found else ""))
    for name, rx in INFO.items():
        hits = sorted({m.group() for m in rx.finditer(text)})
        print(f"  [info] {name}: {len(hits)}" + "".join(f"\n      {h}" for h in hits))
    return blocking


def _is_json(line):
    try:
        json.loads(line)
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--term", action="append", default=[], help="an extra identity term to search for")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    terms = identity_terms(args.term)
    total = sum(scan(f, terms) for f in args.files)
    print(f"BLOCKING HITS: {total}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
