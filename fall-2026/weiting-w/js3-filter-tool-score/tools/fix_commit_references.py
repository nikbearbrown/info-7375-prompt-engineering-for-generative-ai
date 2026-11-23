"""Rewrite the commit hashes in README.md and FRICTIONAL.md to the real ones.

    python3 tools/fix_commit_references.py            # report only
    python3 tools/fix_commit_references.py --write    # rewrite

**Why this exists.** The JS3 commits were authored in one repository and
replayed into the course repository with `git am`, which gives every commit a
new hash because its parent differs. Hashes written into the documents while
the commits were being made are therefore stale in the repository a reader
actually clones.

That is precisely the defect JS2 shipped — `FRICTIONAL.md` §0 — where the
README told a TA to run `git show --stat ce94b1f` and that commit had never
reached GitHub. Catching it here cost one script; catching it there cost the
credibility of every ordering claim in the submission.

The script matches each commit by its **subject line**, which survives the
replay, and substitutes the hash the commit has in *this* repository. It
refuses to invent one: a subject with no match is reported and left alone.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = "fall-2026/weiting-w/js3-filter-tool-score"

#: stale hash -> a distinctive fragment of that commit's subject line
KNOWN = {
    "ee698f2": "freeze FILTER.md before any filter code",
    "ed9d7d1": "F-v1 implemented exactly as frozen, and the me",
    "12ad9e8": "amendment A1 to FILTER.md -- F3 inverts to a d",
    "2e47c65": "amendment A2 -- three false friends cut from t",
    "b9ff488": "apply A1 and A2 to the code, with both predict",
    "5335b7b": "the tool server, written from scratch, and two",
    "adff571": "the source-grounded shortlist -- 7 entries, 29",
    "79b4573": "amendment A3 -- the experience wall was a list",
    "5eb1bc0": "apply A3, and fix the bug A3's own consistency",
    "e86eaa6": "what moves the score -- four objects changed o",
    "8b7a5bc": "SOURCES.md, FRICTIONAL.md, and the audit analy",
    "1e49fb4": "README with the toolchain, the commands, the s",
    "82ed301": "a script to stop this submission repeating JS2",
    "0a25bd2": "the reject audit, everything in it that does n",
    "bef72d8": "amendment A4 -- weight a span by the section i",
    "c48c2cd": "amendment A5 -- reinstate `infrastructure` (S-",
}

DOCS = ("README.md", "FRICTIONAL.md", "SOURCES.md", "FILTER.md")


def log_subjects(repo: Path) -> list[tuple[str, str]]:
    out = subprocess.run(
        ["git", "log", "--format=%h%x00%s", "--", FOLDER],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout
    rows = []
    for line in out.splitlines():
        if "\x00" in line:
            h, s = line.split("\x00", 1)
            rows.append((h, s))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--repo", default=None, help="defaults to the enclosing repo")
    args = ap.parse_args(argv)

    repo = Path(args.repo) if args.repo else ROOT
    while not (repo / ".git").exists() and repo != repo.parent:
        repo = repo.parent
    if not (repo / ".git").exists():
        print("no git repository found above this folder", file=sys.stderr)
        return 2

    subjects = log_subjects(repo)
    mapping, unmatched = {}, []
    for stale, fragment in KNOWN.items():
        hits = [h for h, s in subjects if fragment in s]
        if len(hits) == 1:
            mapping[stale] = hits[0]
        else:
            unmatched.append((stale, fragment, len(hits)))

    for stale, fragment, n in unmatched:
        print(f"  UNMATCHED {stale}: {n} commits match {fragment!r}", file=sys.stderr)

    changed = 0
    for name in DOCS:
        path = ROOT / name
        if not path.exists():
            continue
        text = original = path.read_text(encoding="utf-8")
        for stale, fresh in mapping.items():
            if stale == fresh:
                continue
            text = re.sub(rf"(?<![0-9a-f]){stale}(?![0-9a-f])", fresh, text)
        if text != original:
            changed += 1
            if args.write:
                path.write_text(text, encoding="utf-8")
            print(f"  {'rewrote' if args.write else 'would rewrite'} {name}")

    stale_same = sum(1 for s, f in mapping.items() if s == f)
    print(f"\n{len(mapping)} commits matched by subject, {stale_same} already correct, "
          f"{len(unmatched)} unmatched, {changed} file(s) "
          f"{'rewritten' if args.write else 'needing rewrite'}")
    if unmatched:
        print("An unmatched subject means a hash in the documents points at nothing. "
              "That is the JS2 defect; fix it before pushing.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
