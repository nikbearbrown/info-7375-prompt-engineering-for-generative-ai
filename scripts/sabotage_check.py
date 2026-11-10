"""Prove the wrong-version tests can fail (GATE.md section 6).

For each wrong version W1-W19: copy the project to a temporary folder, plant that wrong version with an exact text
substitution, run its test(s), and expect them to FAIL. The real files are never touched. JS1's audit sabotage
(its W1/W2) runs first.

    python3 scripts/sabotage_check.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COPY = ["jsagent", "scripts", "tests", "config", "baseline", "persona", "prompts", "GATE.md", "CONTRACT.md"]
T = "tests.test_js2_wrong_versions."

WRONG = [
    ("W1", "path check by string prefix", [("jsagent/policy.py",
        "return path == folder or path.is_relative_to(folder)  # path components, never a string prefix",
        "return str(path).startswith(str(folder))")], [T + "TestFileWrongVersions.test_W1_prefix_trick_out_evil"]),
    ("W2", "path checked before symlinks are resolved", [("jsagent/policy.py",
        "return p.resolve()  # follows",
        "return Path(__import__('os').path.abspath(p))  # follows")], [T + "TestFileWrongVersions.test_W2_symlink_escape"]),
    ("W3", "host check by suffix", [("jsagent/fetch.py",
        "    if parts.hostname not in allow:",
        "    if not any((parts.hostname or '').endswith(h) for h in allow):")], [T + "TestNetworkWrongVersions.test_W3_lookalike_host"]),
    ("W4", "only the hostname compared (JS1's behavior)", [("jsagent/fetch.py", 'if "@" in parts.netloc:', "if False:"),
        ("jsagent/fetch.py", "if port not in (None, 443):", "if False:")],
        [T + "TestNetworkWrongVersions.test_W4_port_refused", T + "TestNetworkWrongVersions.test_W4_userinfo_refused"]),
    ("W5", "redirect hops checked but not counted", [("jsagent/net.py", "        self.on_hop(newurl)\n", "        pass\n")],
        [T + "TestNetworkWrongVersions.test_W5_redirect_hops_count"]),
    ("W6", "failed board recorded as 0", [("jsagent/loop.py",
        '        rec.update(status="failed", reason=reason)\n        return',
        '        rec.update(status="failed", reason=reason, count=0)\n        return')],
        [T + "TestLoopWrongVersions.test_W6_failed_board_count_null"]),
    ("W7", "a failed board still exits finished", [("jsagent/loop.py",
        'partial = any(r["status"] != "ok" or r.get("new_unjudged")', 'partial = any(r.get("new_unjudged")')],
        [T + "TestLoopWrongVersions.test_W7_failed_board_incomplete"]),
    ("W8", "retries not charged to the request budget", [("jsagent/loop.py",
        "        ctx.budget.charge_request(url)\n", "        ctx.budget.charge_request(url) if attempt == 1 else None\n")],
        [T + "TestLoopWrongVersions.test_W8_retries_consume_budget"]),
    ("W9", "a 404 retried like a timeout", [("jsagent/loop.py", '    return "failed", None, 0', '    return "failed", 2, backoff')],
        [T + "TestLoopWrongVersions.test_W9_no_retry_on_404"]),
    ("W10", "repeat check without URL normalization", [("jsagent/loop.py",
        "key = (method.upper(), policy.normalize_url(url))", "key = (method.upper(), url)")],
        [T + "TestLoopWrongVersions.test_W10_trailing_slash_is_repeat"]),
    ("W11", "writes allowed anywhere in the project", [("jsagent/policy.py", "if not _inside(rp, self.out):", "if not _inside(rp, self.root):"),
        ("jsagent/policy.py", 'raise PolicyViolation("files.write", f"write into the protected folder {name}/: {path}")', "pass")],
        [T + "TestFileWrongVersions.test_W11_write_config_denied"]),
    ("W12", "existing evidence overwritten without approval", [("jsagent/policy.py",
        'if kind in ("overwrite", "delete") or rp.exists():', 'if kind in ("overwrite", "delete"):'),
        ("jsagent/policy.py", 'with open(rp, "xb") as f:', 'with open(rp, "wb") as f:')],
        [T + "TestFileWrongVersions.test_W12_overwrite_needs_approval"]),
    ("W13", "state updated for a failed board", [("jsagent/loop.py",
        '        rec.update(status="failed", reason=reason)\n        return',
        '        rec.update(status="failed", reason=reason)\n        ctx.observed[key] = {"ids": [], "unjudged": set(), "prev": set()}\n        return')],
        [T + "TestLoopWrongVersions.test_W13_failed_board_state_unchanged"]),
    ("W14", "ids marked seen before they are reported", [("jsagent/loop.py",
        'seen = set(obs["prev"]) | (set(obs["ids"]) - obs["unjudged"])', 'seen = set(obs["prev"]) | set(obs["ids"])')],
        [T + "TestLoopWrongVersions.test_W14_unjudged_stay_new"]),
    ("W15", "verifier trusts the report's count", [("scripts/verify_run.py",
        'check(len(ids) == rec["count"],', "check(True,")], [T + "TestLoopWrongVersions.test_W15_verifier_ignores_report_counts"]),
    ("W16", "output root inside a protected folder accepted", [("jsagent/policy.py",
        "        if _inside(out, (root / name).resolve()):", "        if False:")],
        [T + "TestFileWrongVersions.test_W16_out_root_in_protected_folder"]),
    ("W17", "allow-list drifts from the gate", [("config/allowlist.json",
        '"api.lever.co"', '"api.lever.co", "api.ashbyhq.com"')], [T + "TestConfigMatchesGate.test_W17_allowlist_matches_gate"]),
    ("W18", "a budget drifts from the gate", [("config/budgets.json", '"max_requests": 100', '"max_requests": 150')],
        [T + "TestConfigMatchesGate.test_W18_budgets_match_gate"]),
    ("W19", "verifier passes an empty board with no history", [("scripts/verify_run.py",
        "check(len(ids) > 0,", "check(True,")], [T + "TestLoopWrongVersions.test_W19_empty_board_fails_verification"]),
]


def fresh_copy(tmp):
    dst = Path(tmp) / "proj"
    dst.mkdir()
    for name in COPY:
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, dst / name, symlinks=True, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(src, dst / name)
    return dst


def run_tests(proj, test_ids):
    return subprocess.run([sys.executable, "-m", "unittest", *test_ids], cwd=proj, capture_output=True, text=True)


def js1_audit_sabotage():
    code = ("import unittest\nimport jsagent.audit as audit\naudit.audit_verdicts = lambda *a: []\n"
            "s = unittest.defaultTestLoader.loadTestsFromName('tests.test_wrong_versions')\n"
            "r = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w')).run(s)\n"
            "print(len(r.failures), r.testsRun)\n")
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True).stdout.split()
    failures, total = int(out[0]), int(out[1])
    print(f"JS1 audit sabotage: {failures} of {total} JS1 wrong-version tests failed (expected 9)")
    return failures == 9


def main():
    ok = js1_audit_sabotage()
    all_tests = [t for w in WRONG for t in w[3]]
    with tempfile.TemporaryDirectory() as tmp:
        clean = run_tests(fresh_copy(tmp), all_tests)
        print(f"unplanted copy: the W1-W19 tests {'pass' if clean.returncode == 0 else 'FAIL (fix this first)'}")
        ok &= clean.returncode == 0
    for wid, what, subs, tests in WRONG:
        with tempfile.TemporaryDirectory() as tmp:
            proj = fresh_copy(tmp)
            planted = True
            for rel, old, new in subs:
                path = proj / rel
                text = path.read_text()
                if text.count(old) != 1:
                    print(f"{wid:4} CANNOT PLANT: expected the text exactly once in {rel}: {old[:60]!r}")
                    ok = planted = False
                    break
                path.write_text(text.replace(old, new))
            if planted:
                red = run_tests(proj, tests).returncode != 0
                ok &= red
                print(f"{wid:4} {'RED (caught)' if red else 'GREEN (NOT caught)':20} {what}")
    print("every wrong version was caught" if ok else "SOME WRONG VERSION WAS NOT CAUGHT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
