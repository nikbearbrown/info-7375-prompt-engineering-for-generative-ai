"""Apply plausible-but-wrong variants of the removal patch to a scratch copy
and record which removal tests fail. The project tree is not modified."""
import argparse, re, shutil, subprocess, sys, tempfile
from pathlib import Path
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent.parent),
                help="project root (default: the project this script lives in)")
ROOT = Path(ap.parse_args().root).resolve()
SRC = (ROOT / "agent/loop.py").read_text()
VARIANTS = [
 ("A. field added, never detects anything (removed always [])",
  "        removed = sorted(previous - ids, key=str)\n", "        removed = []\n"),
 ("B. literal 'previously-seen state': compare against seen_ids, ignore last_fetch_ids",
  'previous = set(state.get("last_fetch_ids", state["seen_ids"]))', 'previous = set(state["seen_ids"])'),
 ("C. removals merged into 'new' instead of a separate list",
  "        removed = sorted(previous - ids, key=str)\n",
  "        removed = []\n        new = new + [{\"id\": i, \"title\": \"(removed)\", \"url\": None} for i in sorted(previous - ids, key=str)]\n"),
]
for name, old, new in VARIANTS:
    assert SRC.count(old) == 1, name
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        for d in ("agent", "tests"):
            shutil.copytree(ROOT / d, t / d, ignore=shutil.ignore_patterns("__pycache__"))
        (t / "agent/loop.py").write_text(SRC.replace(old, new))
        p = subprocess.run([sys.executable, "-m", "unittest", "-v", "tests.test_removal_detection"], cwd=t, capture_output=True, text=True)
        res = re.findall(r"^(test_\w+) .*\.\.\. (ok|FAIL|ERROR)$", p.stderr, re.M)
        print(f"\n{name}\n  - {old.strip()}\n  + {new.strip()}")
        for test, r in res:
            print(f"    {r:<5} {test}")
        print(f"  => {'CAUGHT' if p.returncode else 'SURVIVED'} ({p.stderr.strip().splitlines()[-1]})")
print(f"\nproject agent/loop.py unchanged: {(ROOT / 'agent/loop.py').read_text() == SRC}")
