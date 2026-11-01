"""LIMITED privacy scan of the files intended for publication (git-tracked files only).

    .venv/bin/python scripts/privacy_scan.py

It flags:
  1. email addresses whose domain is not example.com (except a short allow-list of known
     public, non-personal addresses);
  2. US-style phone numbers whose exchange is not 555;
  3. any line containing a term listed in local/private_terms.txt. That file is optional and
     gitignored; you create it yourself, one term per line, e.g. your real email or phone digits.
     Terms are never printed: matches show as "private term #N".

This is a pattern search, not proof that no personal data exists. Names, addresses and free
text can only be found by reading. Board snapshots contain public company postings, and any
contact addresses in them are reported for review rather than treated as the persona's data.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
PHONE = re.compile(r"(?<!\d)\(?(\d{3})\)?[ .-](\d{3})[ .-](\d{4})(?!\d)")
ALLOWED_EMAILS = {"noreply@anthropic.com"}


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.split("\0") if p]


def main():
    terms_file = ROOT / "local/private_terms.txt"
    terms = [t.strip().lower() for t in terms_file.read_text().splitlines() if t.strip()] if terms_file.exists() else []
    findings = []
    files = tracked_files()
    for path in files:
        if path.suffix == ".gz":
            continue  # gzip bytes; the decompressed archive capture has no description text
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        rel = path.relative_to(ROOT)
        for n, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            for m in EMAIL.finditer(line):
                if m.group(1).lower() != "example.com" and m.group(0).lower() not in ALLOWED_EMAILS:
                    findings.append(f"{rel}:{n}: email {m.group(0)}")
            for m in PHONE.finditer(line):
                if m.group(2) != "555":
                    findings.append(f"{rel}:{n}: phone-like number {m.group(0)}")
            for i, t in enumerate(terms, 1):
                if t in low:
                    findings.append(f"{rel}:{n}: private term #{i}")
    print(f"Scanned {len(files)} tracked files; private terms file: {'used (' + str(len(terms)) + ' terms)' if terms else 'not present'}")
    for f in findings:
        print("  ", f)
    print(f"{len(findings)} finding(s) for review. A clean result is not proof that no personal data exists.")


if __name__ == "__main__":
    main()
