"""Assembles film/reel/: beat_sheet.json (via make_sheet.py) and scenes.py.

The show-tell skill requires the toolkit's iso_kit.py to be pasted, not imported,
at the top of scenes.py (Gate A copies only scenes.py). This script does that
paste from a toolkit checkout, then appends film/scenes_body.py.

Run: python film/build_reel.py <path-to-brutalist.art>
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REEL = HERE / "reel"


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    toolkit = Path(sys.argv[1]).expanduser()
    kit = toolkit / "skills" / "make" / "show-tell" / "templates" / "iso_kit.py"
    if not kit.is_file():
        raise SystemExit(f"not found: {kit}")
    subprocess.run([sys.executable, str(HERE / "make_sheet.py"), "--final"], check=True)
    body = (HERE / "scenes_body.py").read_text(encoding="utf-8")
    with open(REEL / "scenes.py", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(kit.read_text(encoding="utf-8").rstrip() + "\n\n" + body)
    print(f"wrote {REEL / 'scenes.py'} (kit from {kit})")


if __name__ == "__main__":
    main()
