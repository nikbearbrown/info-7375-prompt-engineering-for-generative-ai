"""Reproduce a defect found on 2026-11-09 in commit e270605 (written by Claude Code, not a test).

A request that is interrupted (Ctrl-C) while in flight has already been sent, but:
  - run.attempts_used does not count it (the budget undercounts), and
  - the board's report lists 0 attempts, although trace.jsonl records the attempt.
The independent checker flags both (C7, C2).

    python3 review-packet/reproduce_interrupt.py      # from the js2-loop-tools-diff folder
Exit 1 while the defect is present, 0 once it is fixed.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import independent_check  # noqa: E402
from jobloop import loop  # noqa: E402
from tests.helpers import FakeClock, FakeTransport, Project, url  # noqa: E402
from tests.test_loop import SEEN, THREE, happy_script  # noqa: E402


class InterruptOnBeta(FakeTransport):
    def __call__(self, u, t):
        if u == url("ashby", "beta"):
            self.calls.append((u, t))
            raise KeyboardInterrupt
        return super().__call__(u, t)


def main() -> int:
    clock = FakeClock()
    project = Project(THREE, SEEN)
    try:
        transport = InterruptOnBeta(clock, happy_script())
        report = loop.run(project.root, transport=transport, clock=clock, sleep=clock.sleep, wall=clock.wall)
        run_dir = project.root / report["run"]["run_dir"]
        trace = [json.loads(l) for l in (run_dir / "trace.jsonl").read_text().splitlines()]
        beta = report["boards"][1]
        print(f"requests sent: {len(transport.calls)}")
        print(f"report attempts_used: {report['run']['attempts_used']}")
        print(f"trace attempt events: {sum(e['event'] == 'attempt' for e in trace)}")
        print(f"ashby/beta attempts in report: {len(beta['attempts'])} (outcome {beta['outcome']})")
        findings = independent_check.check(run_dir, project.root)
        for f in findings:
            print(f"independent check [{f['invariant']}] {f['board'] or 'run'}: {f['message']}")
        defect = report["run"]["attempts_used"] != len(transport.calls) or len(beta["attempts"]) != 1 or findings
        print("DEFECT PRESENT" if defect else "defect not present")
        return 1 if defect else 0
    finally:
        project.cleanup()


if __name__ == "__main__":
    sys.exit(main())
