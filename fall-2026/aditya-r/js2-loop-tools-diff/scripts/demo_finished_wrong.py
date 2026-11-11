"""Finished-wrong-answer demonstration (GATE.md §6). Run from the JS2 folder:

    .venv/bin/python scripts/demo_finished_wrong.py

1. FAULTY VERSION (labeled): the inherited single-board agent/watch.py.
   - REPLAY: a baseline from the LIVE Figma response (144 postings).
   - SYNTHETIC: the next response is {"jobs": [], "meta": {"total": 0}}.
   It ends cleanly (exit 0, "COMPLETE: 0 new"), which is wrong.
2. The independent checker (scripts/check_run.py watch-pair), using the predeclared EXPECTATION.json,
   finds the contradiction from the raw evidence.
3. The same two inputs through the JS2 loop (a file-replay stand-in for the network): suspect-empty,
   exit 3, state unchanged; the checker finds no contradiction.
Outputs go to evidence/finished_wrong/ and are never overwritten.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "evidence/finished_wrong"
PRIOR = "out/runs/20261110T232115022Z_live/raw/02_greenhouse_figma_a1.json.gz"
EMPTY = "evidence/finished_wrong/inputs/empty_SYNTHETIC.json"
PY = sys.executable


def sh(argv, log):
    p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    text = (p.stdout + p.stderr).replace(str(ROOT), "<js2>")
    log.append(f"$ {' '.join(argv[1:] if argv[0] == PY else argv)}\n{text}[exit status: {p.returncode}]\n")
    return p.returncode


def main():
    for d in ("faulty_watch", "js2_loop"):
        if (OUT / d).exists():
            sys.exit(f"refusing to overwrite existing evidence {OUT / d}")
    log = []
    fw = "evidence/finished_wrong/faulty_watch"
    common = [PY, "-m", "agent.watch", "--board", "figma", "--resume", "resume/priya-nair.resume.example.json",
              "--state", f"{fw}/state.json", "--runs-dir", f"{fw}/runs"]
    log.append("## 1. FAULTY VERSION: inherited single-board agent/watch.py\n")
    c1 = sh(common + ["--label", "replay-baseline", "--from-file", PRIOR,
                      "--seeded-note", "REPLAY of the LIVE Figma response from run 20261110T232115022Z_live"], log)
    state_before = (ROOT / fw / "state.json").read_bytes()
    c2 = sh(common + ["--label", "synthetic-empty", "--from-file", EMPTY, "--seeded-note", "SYNTHETIC empty board"], log)
    (ROOT / fw / "exit_codes.json").write_text(json.dumps({"baseline": c1, "later": c2}) + "\n")
    runs = sorted((ROOT / fw / "runs").iterdir())
    log.append("## 2. Independent checker on the faulty runs (predeclared EXPECTATION.json)\n")
    k1 = sh([PY, "scripts/check_run.py", "watch-pair", str(runs[0].relative_to(ROOT)), str(runs[1].relative_to(ROOT)),
             f"{fw}/exit_codes.json", "evidence/finished_wrong/EXPECTATION.json"], log)

    log.append("## 3. Same inputs through the JS2 loop (file replay instead of the network)\n")
    from agent.loop import run_loop
    jroot = OUT / "js2_loop"
    (jroot / "config").mkdir(parents=True)
    (jroot / "resume").mkdir()
    (jroot / "config/boards.json").write_text(json.dumps({"boards": [{"provider": "greenhouse", "board": "figma"}]}))
    shutil.copy(ROOT / "resume/priya-nair.resume.example.json", jroot / "resume/")
    import gzip
    bodies = [gzip.decompress((ROOT / PRIOR).read_bytes()), (ROOT / EMPTY).read_bytes()]

    def replay(url, timeout, deadline):  # REPLAY/SYNTHETIC stand-in for the network
        return 200, {"content-type": "application/json"}, bodies.pop(0)

    codes = []
    for label in ("replay-baseline", "synthetic-empty"):
        code, run_dir = run_loop(jroot, label=label, transport=replay, judge_fn=lambda *a: None)
        codes.append(code)
        log.append(f"run_loop(label={label!r}) -> exit {code}; report {run_dir.relative_to(ROOT)}/report.md\n")
    later = sorted((jroot / "out/runs").iterdir())[-1]
    k2 = sh([PY, "scripts/check_run.py", "run", str(later.relative_to(ROOT))], log)
    summary = {"faulty_watch": {"baseline_exit": c1, "later_exit": c2,
                                "state_changed_by_empty_run": (ROOT / fw / "state.json").read_bytes() != state_before},
               "checker_on_faulty_exit": k1, "js2_loop": {"baseline_exit": codes[0], "later_exit": codes[1]},
               "checker_on_js2_loop_exit": k2}
    log.append("## Summary\n" + json.dumps(summary, indent=1) + "\n")
    (OUT / "DEMO_LOG.md").write_text("# Finished-wrong-answer demonstration — log\n\n"
                                     "Labels: REPLAY = LIVE Figma bytes re-read; SYNTHETIC = constructed empty board.\n\n"
                                     + "\n".join(f"```text\n{x}```" if x.startswith("$") else x for x in log))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
