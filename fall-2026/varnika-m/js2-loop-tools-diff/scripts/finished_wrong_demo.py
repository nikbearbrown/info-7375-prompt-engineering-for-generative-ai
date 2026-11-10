"""The finished-wrong-answer demonstration (FINISHED-WRONG.md). SEEDED runs only: no network.

    python3 scripts/finished_wrong_demo.py

Builds finished-wrong/ (its own config, persona, fixtures and jobs/), then runs, in order:

  A  the real agent, seeded with live run 2026-11-10T212848Z's saved responses (baseline);
  C  the real agent, with Linear's response replaced by a CONSTRUCTED empty one;
  B  wrong version W5 (GATE.md section 6), on exactly the same responses as C.

C runs before B so both start from the same state: C leaves Linear's state alone.
After each run, check_run.py checks it from the outside and its output is saved.
"""

import gzip
import json
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from agent import loop  # noqa: E402

LIVE = "2026-11-10T212848Z"
DEMO = HERE / "finished-wrong"
BOARDS = [{"system": "greenhouse", "board": "anthropic", "company": "Anthropic"},
          {"system": "lever", "board": "palantir", "company": "Palantir"},
          {"system": "ashby", "board": "linear", "company": "Linear"}]
REAL = {"greenhouse/anthropic": "fixtures/anthropic-live-%s.body.gz" % LIVE,
        "lever/palantir": "fixtures/palantir-live-%s.body.gz" % LIVE,
        "ashby/linear": "fixtures/linear-live-%s.body.gz" % LIVE}
EMPTY_LINEAR = "fixtures/linear-CONSTRUCTED-empty.json"
REAL_CLASSIFY = loop.classify


def w5_empty_is_ok(system, http_status, body):
    """WRONG VERSION W5, on purpose: an empty board is a good board with nothing new."""
    status, reason, postings = REAL_CLASSIFY(system, http_status, body)
    return ("ok", None, []) if (status, reason) == ("suspect", "empty") else (status, reason, postings)


def build():
    if DEMO.exists():
        print("refused: %s exists; delete it first to rebuild the demonstration" % DEMO.relative_to(HERE))
        sys.exit(1)
    for folder in ("config", "persona", "fixtures", "jobs"):
        (DEMO / folder).mkdir(parents=True)
    (DEMO / "config" / "boards.json").write_text(json.dumps({"boards": BOARDS}, indent=2) + "\n", encoding="utf-8")
    shutil.copy(HERE / "persona" / "aarav-patel.resume.example.json", DEMO / "persona")
    for key, target in REAL.items():
        shutil.copy(HERE / "jobs" / "raw" / ("%s--%s--r%d.body.gz" % (LIVE, key.replace("/", "-"),
                                                                     {"greenhouse/anthropic": 1, "lever/palantir": 2,
                                                                      "ashby/linear": 3}[key])), DEMO / target)
    # CONSTRUCTED: Linear's real live response with its jobs list emptied; every other key kept as it was.
    linear = json.loads(gzip.decompress((DEMO / REAL["ashby/linear"]).read_bytes()))
    linear["jobs"] = []
    (DEMO / EMPTY_LINEAR).write_text(json.dumps(linear), encoding="utf-8")


def run_and_check(run_id, fixtures, note, wrong=False):
    if wrong:
        with mock.patch.object(loop, "classify", w5_empty_is_ok):
            record = loop.run(DEMO, fixtures=fixtures, note=note, run_id=run_id)
    else:
        record = loop.run(DEMO, fixtures=fixtures, note=note, run_id=run_id)
    result = subprocess.run([sys.executable, str(HERE / "check_run.py"), str(DEMO / record["files"]["record"])],
                            capture_output=True, text=True)
    (DEMO / "jobs" / "runs" / (run_id + ".check.txt")).write_text(result.stdout, encoding="utf-8")
    print("== %s: loop exit %s; check_run exit %d" % (run_id, record["exit"], result.returncode))
    for b in record["boards"]:
        c = b.get("counts")
        print("   %-22s %-16s %s" % (b["key"], b["status"] + (":" + b["reason"] if b.get("reason") else ""),
                                     "%d postings, %d new" % (c["postings"], c["new"]) if c else "no counts"))
    print("   " + result.stdout.strip().replace("\n", "\n   "))


def main():
    build()
    run_and_check("demo-A-baseline", REAL, "SEEDED: live run %s's saved responses, replayed" % LIVE)
    empty = dict(REAL, **{"ashby/linear": EMPTY_LINEAR})
    run_and_check("demo-C-real-agent-linear-empty", empty,
                  "SEEDED; Linear's response is CONSTRUCTED (the real one with an empty jobs list). The real agent.")
    run_and_check("demo-B-WRONG-VERSION-W5-linear-empty", empty,
                  "SEEDED; Linear's response is CONSTRUCTED (the real one with an empty jobs list). "
                  "WRONG VERSION W5, run on purpose: an empty board is treated as a good board.", wrong=True)


if __name__ == "__main__":
    main()
