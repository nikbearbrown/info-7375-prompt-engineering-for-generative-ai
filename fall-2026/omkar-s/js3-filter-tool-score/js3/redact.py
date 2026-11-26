"""Redact local paths from transcripts before they are committed.

    python3 -m js3.redact            # rewrites transcripts/* in place; prints what it changed

The only change: the home-directory prefix (e.g. /Users/<name>) and the matching
'-Users-<name>-' form Claude Code uses in folder names become <HOME>. Nothing else in a message is
touched, so the transcripts stay the real messages otherwise. Each run appends to transcripts/REDACTIONS.md.
"""
import datetime as dt
import glob
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def redact_text(s, home=os.path.expanduser("~")):
    user = os.path.basename(home)
    s = s.replace(home, "<HOME>")
    s = s.replace("-" + home.strip("/").replace("/", "-") + "-", "-<HOME>-")
    return re.sub(r"(?<![A-Za-z0-9])" + re.escape(user) + r"(?![A-Za-z0-9])", "<USER>", s) if user else s


def main():
    changed = []
    for p in sorted(glob.glob(os.path.join(BASE, "transcripts", "**", "*"), recursive=True)):
        if not os.path.isfile(p) or p.endswith("REDACTIONS.md"):
            continue
        with open(p, encoding="utf-8") as f:
            s = f.read()
        r = redact_text(s)
        if r != s:
            with open(p, "w", encoding="utf-8") as f:
                f.write(r)
            changed.append((os.path.relpath(p, os.path.join(BASE, "transcripts")), s.count(os.path.expanduser("~"))))
    if changed:
        with open(os.path.join(BASE, "transcripts", "REDACTIONS.md"), "a", encoding="utf-8") as f:
            f.write(f"- {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ}: home path → `<HOME>`, user name → `<USER>` in "
                    + ", ".join(f"`{n}` ({k} paths)" for n, k in changed) + "\n")
    for n, k in changed:
        print(f"redacted {n} ({k} home paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
