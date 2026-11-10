"""Plant each GATE.md §6 wrong version (W1–W12), plus the accepted meta-validation patch, into a temporary
copy of the real code, and confirm the test suite fails for each (MUTATION evidence).

    .venv/bin/python tests/mutation_check_js2.py      # exits 0 only if every mutant is CAUGHT
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MUTANTS = [
    ("W1 empty Greenhouse response accepted as zero new", "agent/providers.py",
     "        jobs = parse_jobs(decode_body(body))  # integer ids, duplicates, meta / meta.total checks\n        if not jobs:",
     "        jobs = parse_jobs(decode_body(body))  # integer ids, duplicates, meta / meta.total checks\n        if False:"),
    ("W1 count-inconsistent response accepted (meta.total check removed; review patch)", "agent/board.py",
     "        if total != observed:", "        if False:"),
    ("W1 non-object meta accepted (review revision removed)", "agent/board.py",
     'if "meta" in data and not isinstance(meta, dict):', "if False:"),
    ("W2 failed board omitted from the exit decision", "agent/loop.py",
     '        elif o["status"] in ("failed", "unattempted"):', "        elif False:"),
    ("W3 HTTP budget checked so that a ninth attempt is sent", "agent/loop.py",
     '        if budget.http_used >= budget.limits["http_attempts"]:\n            return _blocked(b, "http_attempts"',
     '        if budget.http_used > budget.limits["http_attempts"]:\n            return _blocked(b, "http_attempts"'),
    ("W3 model budget checked so that an eleventh call starts", "agent/loop.py",
     'if budget.model_used >= budget.limits["model_calls"]:', 'if budget.model_used > budget.limits["model_calls"]:'),
    ("W4 a 404 is retried", "agent/loop.py",
     "        if 500 <= status < 600 and attempt == 1:", "        if 400 <= status < 600 and attempt == 1:"),
    ("W4 retry attempts not counted", "agent/loop.py",
     "        budget.http_used += 1  # counted", "        budget.http_used += 1 if attempt == 1 else 0  # counted"),
    ("W5 string-prefix containment admits a sibling", "agent/policy.py",
     "    return path == base or base in path.parents", "    return str(path).startswith(str(base))"),
    # W6: removing resolve() alone was MASKED (2026-11-10) by the post-mkdir re-check in _prepare; the
    # plausible wrong version removes both symlink defenses.
    ("W6 containment ignores symlinks (both resolve() and the post-mkdir re-check removed)", "agent/policy.py",
     "        return (p if p.is_absolute() else self.root / p).resolve()  # follows symlinks and '..'\n",
     "        return Path(os.path.abspath(p if p.is_absolute() else self.root / p))\n",
     ("        if r2 != r or r.is_symlink():", "        if r.is_symlink():")),
    ("W7 substring host match admits a deceptive host", "agent/policy.py",
     '    host = (parts.hostname or "").lower()',
     '    host = next((h for h in ENDPOINTS if h in (parts.hostname or "").lower()), "")'),
    ("W8 redirect followed before policy enforcement", "agent/net.py",
     "        if 300 <= status < 400:  # never read on, never follow: the caller refuses it\n            return status, headers, b\"\"",
     "        if 300 <= status < 400:\n            import urllib.request\n"
     "            urllib.request.urlopen(headers['location'], timeout=timeout_s).read()\n            return status, headers, b\"\""),
    ("W9 state shared across boards", "agent/loop.py",
     '            entry = staged["boards"].get(o["key"])',
     '            entry = next(iter(staged["boards"].values()), None)'),
    ("W10 unvalidated judgment marked completed", "agent/loop.py",
     "                if ok:\n                    staged", "                if True:\n                    staged"),
    ("W10 failed board's state advanced (erased)", "agent/loop.py",
     "            if jobs is None:\n                o.update(",
     "            if jobs is None:\n                staged[\"boards\"][o[\"key\"]] = {\"ids\": {}}\n                o.update("),
    # W11: removing the approvals/ check alone was MASKED (2026-11-10): approvals/ is outside out/, so the
    # out-only confinement still refuses it. The plausible wrong version grants its own approval directly.
    ("W11 export grants its own approval (writes the record itself, bypassing policy)", "agent/loop.py",
     "    if not appr_path.exists():\n",
     "    if not appr_path.exists():\n        appr_path.parent.mkdir(parents=True, exist_ok=True)\n"
     "        appr_path.write_text(json.dumps({k: proposal[k] for k in ('run_id', 'operation', 'destination', 'sha256')}))\n"
     "    if not appr_path.exists():\n"),
    ("W11 approval bound only to the run id", "agent/loop.py",
     '    bound = ("run_id", "operation", "destination", "sha256")', '    bound = ("run_id",)'),
    ("W12 non-finished run exits 0", "agent/loop.py",
     "    report.update(status=status, exit_code=EXIT[status],",
     "    report.update(status=status, exit_code=0 if status != 'error' else 2,"),
]


def main():
    caught_all = True
    for name, rel, old, new, *extra in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            for d in ("agent", "tests", "resume", "prompts"):
                shutil.copytree(ROOT / d, Path(tmp) / d, ignore=shutil.ignore_patterns("__pycache__"))
            target = Path(tmp) / rel
            src = target.read_text()
            assert src.count(old) == 1, f"mutation anchor not found exactly once for {name}"
            src = src.replace(old, new)
            for o2, n2 in extra:
                assert src.count(o2) == 1, f"second anchor not found for {name}"
                src = src.replace(o2, n2)
            target.write_text(src)
            proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x", "--tb=no"],
                                  cwd=tmp, capture_output=True, text=True, timeout=300)
            failed = [line for line in proc.stdout.splitlines() if line.startswith("FAILED")]
            caught = proc.returncode != 0
            caught_all &= caught
            print(f"{'CAUGHT' if caught else 'MISSED'}: {name}")
            for line in failed[:2]:
                print("   ", line)
    sys.exit(0 if caught_all else 1)


if __name__ == "__main__":
    main()
