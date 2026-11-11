"""Build each GATE.md "wrong version" as a mutant copy of JS2 and confirm its named test fails.

Usage: .venv/bin/python tools/check_wrong_versions_js2.py
Each mutant is a copy of the project in a temp dir with textual edits; the real code is untouched.
A mutant whose anchor text is missing counts as NOT caught, so a refactor cannot make this pass silently.
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
JS2_TESTS = ["tests/test_js2_boundary.py", "tests/test_js2_loop.py", "tests/test_js2_independent_check.py"]

# (GATE.md wrong version, named test, [(file, old, new), ...])
MUTANTS = [
    ("1 empty Greenhouse board accepted", "test_empty_board_is_incomplete_never_no_new_jobs",
     [("jsloop/providers.py", 'if not data["jobs"]:\n        raise BoardInvalid(EMPTY)',
       'if False:\n        raise BoardInvalid(EMPTY)')]),
    ("1 empty Lever board accepted", "test_empty_board_is_incomplete_never_no_new_jobs",
     [("jsloop/providers.py", "if not data:\n        raise BoardInvalid(EMPTY)",
       "if False:\n        raise BoardInvalid(EMPTY)")]),
    ("2 failed board counted as zero", "test_failed_board_records_actual_error_never_zero",
     [("jsloop/loop.py", 'obs["outcome"], obs["error"] = "failed", failure',
       'obs["outcome"], obs["error"], obs["postings_in_response"], obs["new_count"] = "failed", failure, 0, 0')]),
    ("2 finished despite a failed board", "test_deliberate_404_is_labeled_first_recorded_and_kept",
     [("jsloop/loop.py",
       'status = "finished" if all(o["outcome"] == "ok" for o in trace["boards"]) else "incomplete"',
       'status = "finished"')]),
    ("3 time checked only after acting", "test_B16_request_not_started_with_under_10_seconds_left",
     [("jsloop/loop.py", "if remaining < budget.min_seconds_to_start_request:", "if remaining < 0:")]),
    ("3 request budget off by one", "test_request_budget_refused_before_sending",
     [("jsloop/loop.py", 'if trace["requests_made"] >= budget.max_requests:',
       'if trace["requests_made"] > budget.max_requests:')]),
    ("4 duplicate selection not refused", "test_duplicate_url_in_selection_is_preflight_error_with_no_request",
     [("jsloop/loop.py", "    if duplicates:\n", "    if False:\n")]),
    ("4 ledger lets a repeat through", "test_ledger_suppresses_a_repeated_action",
     [("jsloop/loop.py", "if key in self._taken:", "if False:")]),
    ("5 containment by string prefix", "test_B09_sibling_prefix_denied",
     [("jsloop/policy.py", "return path == root or path.is_relative_to(root)",
       "return str(path).startswith(str(root))")]),
    ("5 symlinks not resolved", "test_B10_symlink_escape_denied",
     [("jsloop/policy.py",
       "return pathlib.Path(os.path.realpath(path if path.is_absolute() else self.base / path))",
       "return pathlib.Path(os.path.abspath(path if path.is_absolute() else self.base / path))")]),
    ("6 fixture folder writable", "test_B12_write_to_seeded_fixture_denied",
     [("jsloop/policy.py", 'WRITE_DIRS = ("evidence/js2", "runs/js2")',
       'WRITE_DIRS = ("evidence/js2", "runs/js2", "fixtures/js2")')]),
    ("6 state write without approval", "test_B13_run_without_approval_observes_but_never_writes_state",
     [("jsloop/policy.py", "            if approve_state_write:\n                return real",
       "            if True:\n                return real"),
      ("jsloop/loop.py", 'wants_state = status == "finished" and trace["approve_state_write"]',
       'wants_state = status == "finished"')]),
    ("7 state advances after failure", "test_state_bytes_unchanged_after_incomplete_run_even_with_approval",
     [("jsloop/loop.py", 'wants_state = status == "finished" and trace["approve_state_write"]',
       'wants_state = trace["approve_state_write"]')]),
    ("7 observation-only run tries to write state", "test_state_bytes_unchanged_after_observation_only_run",
     [("jsloop/loop.py", 'wants_state = status == "finished" and trace["approve_state_write"]',
       'wants_state = status == "finished"')]),
    ("8 Lever parser unwraps a Greenhouse object", "test_lever_parser_rejects_greenhouse_shape",
     [("jsloop/providers.py", "    if not isinstance(data, list):\n        raise BoardInvalid(\"not a Lever",
       "    if isinstance(data, dict) and isinstance(data.get(\"jobs\"), list):\n        data = data[\"jobs\"]\n"
       "    if not isinstance(data, list):\n        raise BoardInvalid(\"not a Lever")]),
    ("B03a host matched by substring", "test_B03a_look_alike_host_denied",
     [("jsloop/policy.py", "if parts.hostname not in ALLOWED_HOSTS:",
       "if not any(h in (parts.hostname or '') for h in ALLOWED_HOSTS):")]),
    ("B15 demo-only board allowed in normal mode", "test_B15_deliberate_failure_board_needs_demo_mode",
     [("jsloop/policy.py", "if board.demo_only and not demo:", "if False:")]),
]

_FAILED = re.compile(r"^FAILED \S+::(\w+)")


def main():
    all_caught = True
    for name, test, edits in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "proj"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(
                ".venv", ".git", "__pycache__", ".pytest_cache", "evidence", "runs", "state", "experiment", "*.zip"))
            applied = True
            for rel, old, new in edits:
                target = copy / rel
                source = target.read_text()
                if source.count(old) != 1:
                    print(f"[{name}] MUTATION NOT APPLIED: anchor found {source.count(old)} times in {rel}")
                    applied = False
                    break
                target.write_text(source.replace(old, new, 1))
            if not applied:
                all_caught = False
                continue
            proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *JS2_TESTS],
                                  cwd=copy, capture_output=True, text=True)
            failed = sorted({m.group(1) for line in proc.stdout.splitlines() if (m := _FAILED.match(line))})
            caught = test in failed
            all_caught &= caught
            print(f"[{name}] named test {test}: {'FAILED (caught)' if caught else 'PASSED (NOT caught)'}"
                  f"; all failing tests: {', '.join(failed) or 'none'}")
    print(f"\n{len(MUTANTS)} mutants: " + ("all wrong versions caught" if all_caught
                                         else "SOME WRONG VERSION WAS NOT CAUGHT"))
    return 0 if all_caught else 1


if __name__ == "__main__":
    sys.exit(main())
