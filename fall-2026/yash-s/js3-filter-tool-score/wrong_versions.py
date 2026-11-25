"""Plant each wrong version from FILTER.md section 9 and check that the tests catch it.

    python3 wrong_versions.py

For each wrong version, this copies the code, rules and tests into a temporary
folder, changes job_filter.py in exactly the way described, runs the whole test
suite there, and reports which tests failed. A wrong version counts as caught
only if at least one test fails. The real project files are never changed.
A baseline run with no change comes first and must pass.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

WRONG_VERSIONS = [
    ("WV1", "Substring matching: 'AI' matches inside 'email'",
     [('    return phrase_re(phrase).search(text or "") is not None',
       '    return (phrase or "").lower() in (text or "").lower()')]),
    ("WV2a", "Counting boilerplate: approved company sentences are not removed",
     [('    job = [s for s in sents if s["text"] not in approved]',
       '    job = list(sents)')]),
    ("WV2b", "Counting boilerplate: Databricks and Unity Catalog count as skills",
     [('            if skill not in sk["excluded"] and skill not in out:',
       '            if skill not in out:')]),
    ("WV2c", "Counting boilerplate: standalone 'AI' earns topic points",
     [('    return out\n\n\ndef skills(',
       '    if has("AI", job_text) or has("artificial intelligence", job_text):\n'
       '        out.setdefault("AI (standalone)", "AI")\n    return out\n\n\ndef skills(')]),
    ("WV3", "US location: a city-only US location is treated as outside the US",
     [('    if p.lower() in {c.lower() for c in L["us_cities"]["names"]}:\n        return "us"',
       '    if p.lower() in {c.lower() for c in L["us_cities"]["names"]}:\n        return "non_us"')]),
    ("WV4", "Missing experience treated as eligible",
     [('        return {"status": "unknown", "decisive_min": None, "reason": "no mandatory year count", **detail}',
       '        return {"status": "compatible", "decisive_min": 0, "reason": "no mandatory year count", **detail}')]),
]


def copy_project(dest):
    """Copy every project .py file, FILTER.md, rules/, tests/ and the registered experiment
    candidates (not runs/, audit/, shortlist/ or mcp/)."""
    for f in sorted(HERE.glob("*.py")):
        if f.name != Path(__file__).name:
            shutil.copy2(f, dest / f.name)
    shutil.copy2(HERE / "FILTER.md", dest / "FILTER.md")
    shutil.copytree(HERE / "rules", dest / "rules")
    shutil.copytree(HERE / "tests", dest / "tests", ignore=shutil.ignore_patterns("__pycache__"))
    (dest / "experiments").mkdir()
    shutil.copy2(HERE / "experiments" / "candidates.json", dest / "experiments" / "candidates.json")


def link_js2(tmp):
    """The tests look for the JS2 folder next to the project. Give the temporary copies a
    link to the real one, so the persona and saved-data tests run instead of being skipped.
    The tests only read it."""
    real = HERE.parent / "js2-loop-tools-diff"
    if real.is_dir():
        (Path(tmp) / "js2-loop-tools-diff").symlink_to(real, target_is_directory=True)


def run_tests(folder):
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                          cwd=folder, capture_output=True, text=True,
                          env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
    out = proc.stdout + proc.stderr
    failed = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(([^)]+)\)", out, re.MULTILINE)))
    ran = re.search(r"Ran (\d+) tests?", out)
    skipped = re.search(r"skipped=(\d+)", out)
    if skipped:
        print(f"  note: {skipped.group(1)} test(s) skipped in {Path(folder).name}")
    names = []
    for test, where in failed:
        names.append(where if where.endswith("." + test) else f"{where}.{test}")
    return proc.returncode, int(ran.group(1)) if ran else 0, names, out


def main():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        link_js2(tmp)
        base = Path(tmp) / "baseline"
        base.mkdir()
        copy_project(base)
        code, ran, failed, out = run_tests(base)
        print(f"baseline (no change): {ran} tests, {'all pass' if code == 0 else f'{len(failed)} FAILED'}")
        if code != 0:
            print(out)
            print("The baseline must pass before wrong versions mean anything.")
            return 1
        for key, label, edits in WRONG_VERSIONS:
            folder = Path(tmp) / key
            folder.mkdir()
            copy_project(folder)
            src = (folder / "job_filter.py").read_text(encoding="utf-8")
            for old, new in edits:
                if src.count(old) != 1:
                    print(f"{key}: could not plant (expected text found {src.count(old)} times)")
                    return 1
                src = src.replace(old, new)
            (folder / "job_filter.py").write_text(src, encoding="utf-8")
            code, ran, failed, _ = run_tests(folder)
            caught = code != 0 and bool(failed)
            results.append((key, caught))
            print(f"\n{key}: {label}\n  {'CAUGHT' if caught else 'NOT CAUGHT'} - {len(failed)} of {ran} tests failed")
            for name in failed:
                print(f"    {name}")
    caught = sum(c for _, c in results)
    print(f"\n{caught} of {len(results)} wrong versions caught")
    return 0 if caught == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
