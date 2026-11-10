"""Permission-policy boundary cases B01-B18 (policy/BOUNDARY-TABLE.md) and wrong versions 11, 12, 14, 15.

Written by Claude Code on 2026-11-10, after the predictions were committed (6c1c5b3).
Each expected outcome below comes from GATE.md section 5, not from the predictions; the table
compares the two. `python3 -m tests.test_boundaries --table` prints the Actual column.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import unittest
import uuid

from jobloop import loop, policy, providers
from tests.helpers import TMP, FakeClock, FakeTransport, Project, gh_body, ok, state_for, url
from wrong_versions import applied

KLAVIYO = providers.endpoint("greenhouse", "klaviyo")
ALLOWED = {KLAVIYO}
GH = "https://boards-api.greenhouse.io"


class Sandbox:
    """A throwaway project root under tests/tmp/, plus a folder outside it for the symlink case."""

    def __init__(self):
        self.root = TMP / f"bound-{uuid.uuid4().hex[:10]}"
        self.outside = TMP / f"outside-{uuid.uuid4().hex[:10]}"
        for d in ("config", "runs", "state"):
            (self.root / d).mkdir(parents=True)
        self.outside.mkdir(parents=True)
        (self.root / "config" / "boards.json").write_text('{"schema_version": 1, "boards": []}')
        os.symlink(self.outside, self.root / "runs" / "link")

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)
        shutil.rmtree(self.outside, ignore_errors=True)


def b18_config_grants_approval() -> str:
    """The whole loop: a config key trying to grant approval, run WITHOUT the flag."""
    clock = FakeClock()
    project = Project([("greenhouse", "alpha", "watch")], state_for({"greenhouse/alpha": [1]}))
    try:
        cfg = json.loads((project.root / "config" / "boards.json").read_text())
        cfg["approve_state_write"] = True
        (project.root / "config" / "boards.json").write_text(json.dumps(cfg))
        before = project.state_bytes()
        transport = FakeTransport(clock, {url("greenhouse", "alpha"): [ok(gh_body([1, 2]))]})
        report = loop.run(project.root, transport=transport, clock=clock, sleep=clock.sleep, wall=clock.wall)
        if report["run"]["status"] == loop.ERROR and not transport.calls and project.state_bytes() == before:
            return "run error"
        return f"status {report['run']['status']}, {len(transport.calls)} request(s), state changed: {project.state_bytes() != before}"
    finally:
        project.cleanup()


def cases(sb: Sandbox):
    req = lambda m, u: policy.check_request(m, u, ALLOWED).outcome          # noqa: E731
    write = lambda p, **kw: policy.check_write(p, root=sb.root, **kw).outcome  # noqa: E731
    read = lambda p: policy.check_read(p, root=sb.root).outcome             # noqa: E731
    return [
        ("B01", policy.ALLOW, lambda: req("GET", KLAVIYO)),
        ("B02", policy.DENY, lambda: req("GET", "https://evil.example/v1/boards/klaviyo/jobs?content=true")),
        ("B03", policy.DENY, lambda: req("GET", "https://boards-api.greenhouse.io.evil.example/v1/boards/klaviyo/jobs?content=true")),
        ("B04", policy.DENY, lambda: req("POST", KLAVIYO)),
        ("B05", policy.DENY, lambda: req("GET", f"{GH}/v1/boards/stripe/jobs?content=true")),
        ("B06", policy.DENY, lambda: req("GET", "http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true")),
        ("B07", policy.DENY, lambda: req("GET", "https://boards-api.greenhouse.io:8443/v1/boards/klaviyo/jobs?content=true")),
        ("B08", policy.ALLOW, lambda: write("runs/2026-11-09T00-00-00Z-live/report.json")),
        ("B09", policy.DENY, lambda: write("runs/../state/seen.json")),
        ("B10", policy.DENY, lambda: write("runs-evil/report.json")),
        ("B11", policy.DENY, lambda: write("runs/link/x.json")),
        ("B12", policy.ALLOW, lambda: read("config/boards.json")),
        ("B13", policy.DENY, lambda: write("config/boards.json")),
        ("B14", policy.APPROVAL_REQUIRED, lambda: write("state/seen.json", approve_state_write=False, run_status="finished")),
        ("B15", policy.ALLOW, lambda: write("state/seen.json", approve_state_write=True, run_status="finished")),
        ("B16", policy.DENY, lambda: write("state/seen.json", approve_state_write=True, run_status="incomplete")),
        ("B17", policy.DENY, lambda: read("/etc/passwd")),
        ("B18", "run error", b18_config_grants_approval),
    ]


class TestBoundaryDecisions(unittest.TestCase):
    def setUp(self):
        self.sb = Sandbox()

    def tearDown(self):
        self.sb.cleanup()

    def test_each_case_gets_the_outcome_gate_section_5_requires(self):
        table = cases(self.sb)
        self.assertGreaterEqual(len(table), 10)
        for case_id, expected, actual in table:
            with self.subTest(case=case_id):
                self.assertEqual(actual(), expected)


class TestBoundaryEffects(unittest.TestCase):
    """The decision is not enough: the real file operations must agree with it."""

    def setUp(self):
        self.sb = Sandbox()

    def tearDown(self):
        self.sb.cleanup()

    def test_b08_new_run_file_is_written_once_and_never_overwritten(self):
        path = "runs/2026-11-09T00-00-00Z-live/report.json"
        policy.write_new_file(path, b"first", root=self.sb.root)
        with self.assertRaises(FileExistsError):
            policy.write_new_file(path, b"second", root=self.sb.root)
        self.assertEqual((self.sb.root / path).read_bytes(), b"first")

    def test_b09_b10_b13_denied_writes_raise_and_create_nothing(self):
        for path in ("runs/../state/seen.json", "runs-evil/report.json", "config/boards.json"):
            with self.subTest(path=path), self.assertRaises(policy.PolicyViolation):
                policy.write_new_file(path, b"x", root=self.sb.root)
        self.assertFalse((self.sb.root / "runs-evil").exists())
        self.assertFalse((self.sb.root / "state" / "seen.json").exists())

    def test_b11_symlink_write_is_refused_and_nothing_lands_outside(self):
        with self.assertRaises(policy.PolicyViolation):
            policy.write_new_file("runs/link/x.json", b"x", root=self.sb.root)
        self.assertEqual(list(self.sb.outside.iterdir()), [])

    def test_b11_even_without_the_check_the_os_refuses_to_follow_the_link(self):
        # A symlink swapped in after a check: the O_NOFOLLOW directory walk still refuses it.
        with self.assertRaises(OSError):
            policy._open_dir(self.sb.root, ("runs", "link"), create=False)

    def test_b12_read_works_and_b17_read_outside_raises(self):
        self.assertIn(b"schema_version", policy.read_bytes("config/boards.json", root=self.sb.root))
        with self.assertRaises(policy.PolicyViolation):
            policy.read_bytes("/etc/passwd", root=self.sb.root)

    def test_b14_b16_state_is_not_written_and_b15_writes_it_atomically(self):
        with self.assertRaises(policy.PolicyViolation):
            policy.replace_state(b"{}", approve_state_write=False, run_status="finished", root=self.sb.root)
        with self.assertRaises(policy.PolicyViolation):
            policy.replace_state(b"{}", approve_state_write=True, run_status="incomplete", root=self.sb.root)
        self.assertFalse((self.sb.root / "state" / "seen.json").exists())
        policy.replace_state(b'{"ok": 1}', approve_state_write=True, run_status="finished", root=self.sb.root)
        self.assertEqual((self.sb.root / "state" / "seen.json").read_bytes(), b'{"ok": 1}')
        self.assertEqual([p.name for p in (self.sb.root / "state").iterdir()], ["seen.json"])   # no temp left


class TestPolicyWrongVersionsAreCaught(unittest.TestCase):
    """GATE.md section 6, wrong versions 11, 12, 14, 15: each flips a boundary case."""

    def setUp(self):
        self.sb = Sandbox()

    def tearDown(self):
        self.sb.cleanup()

    def test_each_wrong_version_changes_its_boundary_outcome(self):
        catches = {11: ("B10", policy.DENY), 12: ("B03", policy.DENY), 14: ("B04", policy.DENY),
                   15: ("B14", policy.APPROVAL_REQUIRED)}
        table = {cid: fn for cid, _, fn in cases(self.sb)}
        for n, (case_id, expected) in catches.items():
            with self.subTest(wrong_version=n, case=case_id):
                self.assertEqual(table[case_id](), expected)          # real code
                with applied(n):
                    self.assertNotEqual(table[case_id](), expected, f"wrong version {n} was NOT caught")


def print_table() -> None:
    sb = Sandbox()
    try:
        for case_id, expected, actual in cases(sb):
            got = actual()
            print(f"{case_id}\t{got}\t(GATE requires {expected}){'' if got == expected else '  MISMATCH'}")
    finally:
        sb.cleanup()


if __name__ == "__main__":
    if "--table" in sys.argv:
        print_table()
    else:
        unittest.main()
