"""Mutation check: put each GATE.md §6 wrong version into the code and confirm its own test fails. Run: python tests/mutants.py"""
from __future__ import annotations

import contextlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_wrong_versions as t  # noqa: E402

from agent2 import loop, providers  # noqa: E402


@contextlib.contextmanager
def patched(obj, name, value):
    saved = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, saved)


def _failures_as_zero():
    real = loop._Run.board

    def board(self, b):
        out = real(self, b)
        if out["status"] == "failed":
            out.update(status="success", postings=0)
        return out
    return patched(loop._Run, "board", board)


def _any_200_is_valid():
    real = providers.parse

    def parse(provider, body):
        try:
            return real(provider, body)
        except providers.Malformed:
            return [], None
    return patched(providers, "parse", parse)


def _always_finished():
    real = loop.run

    def run(*a, **k):
        s = real(*a, **k)
        if s["exit"] in ("incomplete", "budget-exhausted"):
            s["exit"] = "finished"
        return s
    return patched(loop, "run", run)


MUTANTS = {
    "test_wv_1_failures_never_become_zero": _failures_as_zero,
    "test_wv_2_retries_bounded": lambda: patched(loop, "MAX_ATTEMPTS", 10),
    "test_wv_3_repeat_is_not_new_work": lambda: patched(loop, "action_key", lambda method, url: object()),
    "test_wv_4_a_200_is_not_automatically_a_valid_board": _any_200_is_valid,
    "test_wv_5_finished_only_when_everything_succeeded": _always_finished,
}

if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    missed = []
    for name, mutant in MUTANTS.items():
        try:
            with mutant():
                getattr(t, name)()
            missed.append(name)
            print(f"MISSED {name}: still passed with the wrong version in place")
        except Exception as e:
            print(f"caught {name}: {type(e).__name__}")
    print(f"{len(MUTANTS) - len(missed)}/{len(MUTANTS)} GATE wrong versions caught by their own test")
    sys.exit(1 if missed else 0)
