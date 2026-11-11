"""Build each CONTRACT.md "wrong version" as a mutant copy and confirm its named test fails.

Usage: .venv/bin/python tools/check_wrong_versions.py
Each mutant is a copy of the project in a temp dir with one textual edit; the real code is untouched.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent

MUTANTS = [
    ("1 shifted labels", "test_verdicts_keyed_by_id", "jsagent/rule.py",
     'return {posting["id"]: judge_posting(resume, posting) for posting in postings}',
     'ids = [p["id"] for p in postings]\n'
     '    return dict(zip(ids[1:] + ids[:1], [judge_posting(resume, p) for p in postings]))'),
    ("2 empty or fake justification", "test_validator_rejects_empty_or_fake_evidence", "jsagent/validator.py",
     "if not isinstance(justification, list) or not justification:",
     "if not isinstance(justification, list):"),
    ("2b fake citations accepted", "test_validator_rejects_empty_or_fake_evidence", "jsagent/validator.py",
     "for i, entry in enumerate(justification):",
     "for i, entry in enumerate([]):"),
    ("3 baseline leak", "test_baseline_reports_zero", "jsagent/run.py",
     'new = [] if baseline else [p for p in postings if p["id"] not in seen]',
     'new = [p for p in postings if p["id"] not in (seen or set())]'),
    ("4 authorization trap", "test_work_authorized_still_needs_sponsorship", "jsagent/authorization.py",
     'if resume["visa"]["type"].strip().upper() == "F-1":',
     'if "work authorized" in resume["visa"]["current_status"].lower():\n'
     '        return "AUTHORIZED"\n'
     '    if resume["visa"]["type"].strip().upper() == "F-1":'),
    ("5 ignored exclusions", "test_seniority_and_mobile_exclusions", "jsagent/rule.py",
     'verdict = "relevant" if all(e["passed"] for e in entries) else "not_relevant"',
     'verdict = "relevant" if all(e["passed"] for e in entries[:3]) else "not_relevant"'),
]


def main():
    all_caught = True
    for name, test, rel, old, new in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "proj"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".venv", ".git", "__pycache__", ".pytest_cache"))
            target = copy / rel
            source = target.read_text()
            if old not in source:
                print(f"[{name}] MUTATION NOT APPLIED: anchor text not found in {rel}")
                all_caught = False
                continue
            target.write_text(source.replace(old, new, 1))
            proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                                  cwd=copy, capture_output=True, text=True)
            failed = sorted({line.split("::")[1].split()[0] for line in proc.stdout.splitlines()
                             if line.startswith("FAILED")})
            caught = test in failed
            all_caught &= caught
            print(f"[{name}] named test {test}: {'FAILED (caught)' if caught else 'PASSED (NOT caught)'}"
                  f"; all failing tests: {', '.join(failed) or 'none'}")
    print("\nall wrong versions caught" if all_caught else "\nSOME WRONG VERSION WAS NOT CAUGHT")
    return 0 if all_caught else 1


if __name__ == "__main__":
    sys.exit(main())
