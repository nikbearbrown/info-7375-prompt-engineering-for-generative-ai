"""Safe probes of the UNCHANGED JS1 baseline, for Aditya to run and interpret.

Written by Claude Code (2026-11-10). This script only prints what happens. It does not say what is
right or wrong; comparing it with GATE.md is Aditya's job.

Safety:
- Every probe runs inside a fresh temporary directory, which is deleted at the end.
- All postings and boards are SYNTHETIC (tests/fixtures.py), and the persona is the synthetic test copy.
- There is no network access: every run uses --from-file replay. No model is called; a counting
  stand-in judge returns fixed text.
- Nothing is read or written outside the temporary directory.

    .venv/bin/python review/probes/investigate_baseline.py            # all probes
    .venv/bin/python review/probes/investigate_baseline.py P1 P3      # selected probes
"""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agent.watch import run  # noqa: E402  (the unchanged JS1 baseline)
from tests.fixtures import NOT_RELEVANT, PERSONA, RELEVANT, board, posting, valid_response  # noqa: E402


def make_args(root, board_file, label, runs_dir=None):
    persona = root / "persona.json"
    persona.write_text(json.dumps(PERSONA))
    return argparse.Namespace(board="synthetic", resume=str(persona), state=str(root / "state.json"),
                              runs_dir=str(runs_dir or root / "runs"), label=label, from_file=str(board_file),
                              seeded_note="SYNTHETIC probe", resume_run=None, workers=1, prompt_version="test")


def write(root, name, data):
    p = root / name
    p.write_bytes(data if isinstance(data, bytes) else json.dumps(data).encode())
    return p


class CountingJudge:
    """Stand-in judge (no model). Returns `text_for(posting)` and counts invocations."""

    def __init__(self, text_for):
        self.calls, self.text_for = 0, text_for

    def __call__(self, p, resume):
        self.calls += 1
        return {"response_text": self.text_for(p), "models_used": ["SYNTHETIC"], "session_id": None,
                "prompt_version": "test", "prompt_sha256": "test"}


def show(root, label, code):
    print(f"  exit code: {code}")
    runs = sorted((root / "runs").glob(f"*_{label}")) if (root / "runs").exists() else []
    if runs:
        rep = runs[0] / "report.json"
        if rep.exists():
            r = json.loads(rep.read_text())["run"]
            print("  report run entry:", {k: r.get(k) for k in ("kind", "postings_in_response", "new", "completed", "pending")})
    if (root / "state.json").exists():
        ids = json.loads((root / "state.json").read_text())["ids"]
        print(f"  state ids after run: {len(ids)} -> {dict(list(ids.items())[:4])}{' …' if len(ids) > 4 else ''}")


def p1(root):
    """Baseline with two postings, then a later response whose jobs array is empty."""
    run(make_args(root, write(root, "b0.json", board(RELEVANT, NOT_RELEVANT)), "base"), judge_fn=CountingJudge(str))
    code = run(make_args(root, write(root, "b1.json", {"jobs": [], "meta": {"total": 0}}), "later"),
               judge_fn=CountingJudge(str))
    show(root, "later", code)


def p2(root):
    """Baseline, then a Greenhouse-shaped response whose meta.total disagrees with the list length."""
    run(make_args(root, write(root, "b0.json", board(RELEVANT)), "base"), judge_fn=CountingJudge(str))
    data = {"jobs": [RELEVANT], "meta": {"total": 40}}
    code = run(make_args(root, write(root, "b1.json", data), "later"), judge_fn=CountingJudge(str))
    show(root, "later", code)


def p3(root):
    """A first run on an Ashby-shaped response (string UUID ids, as observed in pre-gate recon)."""
    jobs = [{"id": "00000000-0000-4000-8000-00000000000%d" % i, "title": "Software Engineer",
             "descriptionHtml": "<p>Python and SQL</p>", "jobUrl": "https://example.invalid/j"} for i in (1, 2)]
    code = run(make_args(root, write(root, "ashby.json", {"apiVersion": "1", "jobs": jobs}), "first"),
               judge_fn=CountingJudge(str))
    show(root, "first", code)


def p4(root):
    """Where do run files land when the label contains path components? (Contained in a sandbox.)"""
    sandbox = root / "a" / "b" / "c"
    runs_dir = sandbox / "runs"
    code = run(make_args(root, write(root, "b0.json", board(RELEVANT)), "/../../outside-runs", runs_dir=runs_dir),
               judge_fn=CountingJudge(str))
    print(f"  exit code: {code}; --runs-dir was {runs_dir.relative_to(root)}")
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f == "report.md":
                print("  report.md written at:", (Path(dirpath) / f).relative_to(root))


def p5(root):
    """Baseline with one posting, then 12 new postings whose judge responses are all invalid."""
    run(make_args(root, write(root, "b0.json", board(RELEVANT)), "base"), judge_fn=CountingJudge(str))
    new = [posting(1000 + i, f"Data Engineer {i}", "<p>Python and SQL</p>") for i in range(12)]
    judge = CountingJudge(lambda p: "not json")
    code = run(make_args(root, write(root, "b1.json", board(RELEVANT, *new)), "later"), judge_fn=judge)
    show(root, "later", code)
    print(f"  judge invocations in this one run: {judge.calls}")


def p6(root):
    """Baseline, then a valid new posting: a control probe for comparison."""
    run(make_args(root, write(root, "b0.json", board(RELEVANT)), "base"), judge_fn=CountingJudge(str))
    judge = CountingJudge(valid_response)
    code = run(make_args(root, write(root, "b1.json", board(RELEVANT, NOT_RELEVANT)), "later"), judge_fn=judge)
    show(root, "later", code)
    print(f"  judge invocations: {judge.calls}")


PROBES = {"P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6}

if __name__ == "__main__":
    chosen = sys.argv[1:] or list(PROBES)
    for name in chosen:
        fn = PROBES[name]
        print(f"\n{name}: {fn.__doc__}")
        with tempfile.TemporaryDirectory(prefix=f"js2-probe-{name}-") as tmp:
            try:
                fn(Path(tmp))
            except Exception as e:  # an exception is an observation too
                print(f"  raised {type(e).__name__}: {e}")
