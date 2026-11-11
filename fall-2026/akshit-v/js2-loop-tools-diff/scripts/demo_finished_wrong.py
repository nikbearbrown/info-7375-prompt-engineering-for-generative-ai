"""SEEDED demonstration: a run that ends cleanly and is wrong, caught by the independent check.

Setup (all SEEDED, written under out/demo_finished_wrong/):
  - state: a copy of the real state after a live run (figma had jobs last time);
  - responses: the real saved lever:spotify and ashby:snowflake responses from that live run,
    plus a SEEDED empty job list for greenhouse:figma (simulating the board returning nothing);
  - boards: the three real boards only (the deliberate 404 board would make every run
    'incomplete' and hide the point).
Then it runs the wrong version W-a (empty accepted as "no new jobs") and the real version,
and runs scripts/check_run.py on both.

    python -B scripts/demo_finished_wrong.py out/runs/<live_run_id>.json
"""
import functools
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent2 import loop, policy, run  # noqa: E402
from agent2.config import BOARDS  # noqa: E402
from tests import wrong_versions  # noqa: E402

DEMO = policy.OUT / "demo_finished_wrong"
REAL_BOARDS = [b for b in BOARDS if b.board != "no-such-board-js2"]


def prepare(sub: str, live: dict) -> Path:
    d = DEMO / sub
    policy.write_bytes(d / "state" / "seen_ids.json", (policy.OUT / "state" / "seen_ids.json").read_bytes())
    manifest = {}
    for e in (e for e in live["trace"] if e["event"] == "request"):
        b = next((b for b in REAL_BOARDS if b.key == e["board"]), None)
        if b is None:
            continue
        if b.board == "figma":
            body, name = b'{"jobs": []}', "SEEDED_empty_greenhouse_figma.json"
        else:
            body, name = (ROOT / e["raw"]).read_bytes(), "REAL_" + Path(e["raw"]).name
        policy.write_bytes(d / "replay" / name, body)
        manifest[b.url] = {"file": name, "status": 200}
    policy.write_bytes(d / "replay" / "manifest.json", json.dumps(manifest, indent=2).encode())
    return d


def run_variant(d: Path, label: str, classify) -> Path:
    original = loop.run_loop
    run.BOARDS[:] = []
    run.BOARDS.extend(REAL_BOARDS)
    loop.run_loop = functools.partial(original, classify=classify)
    try:
        run.main(["--resume", "data/resume_jack_spencer.json", "--replay", str(d / "replay" / "manifest.json"),
                  "--label", label, "--out", str(d)])
    finally:
        loop.run_loop = original
    return sorted((d / "runs").glob("*.json"))[-1]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    live = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for sub, label, classify in (("wrong", "SEEDED + WRONG VERSION W-a", wrong_versions.wa_classify),
                                 ("real", "SEEDED", loop.classify)):
        print(f"\n######## {label} ########")
        rec = run_variant(prepare(sub, live), label, classify)
        print(f"-- independent check ({rec.relative_to(ROOT).as_posix()}):")
        subprocess.run([sys.executable, "-I", "-B", str(ROOT / "scripts" / "check_run.py"), str(rec)], cwd=ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
