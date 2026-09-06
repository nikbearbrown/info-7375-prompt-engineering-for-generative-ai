"""Validate the curriculum contract and run all offline Python labs."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ("Learning Objectives", "The Problem", "The Concept", "Build It",
            "Use It", "Ship It", "Verify It", "Capstone Connection")


def validate():
    failures = []
    manifest = json.loads((ROOT / "course.json").read_text())
    weeks = manifest["weeks"]
    if [w["week"] for w in weeks] != list(range(1, 16)):
        failures.append("Expected 15 ordered weeks")
    if manifest.get("language") != "Python" or manifest.get("provider") != "Claude":
        failures.append("Course stack must remain Python and Claude")
    for path in ROOT.rglob("*"):
        if any(p in {".git", ".venv", "learning-artifacts", "__pycache__"} for p in path.parts):
            continue
        if path.suffix in {".js", ".ts", ".tsx", ".jsx", ".rs", ".jl", ".go"}:
            failures.append(f"Non-Python implementation: {path.relative_to(ROOT)}")
        if path.suffix == ".py":
            ast.parse(path.read_text(), filename=str(path))
        if path.suffix == ".md":
            text = path.read_text()
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if "://" in target or target.startswith("#"):
                    continue
                target = target.split("#")[0]
                if target and not (path.parent / target).exists():
                    failures.append(f"Broken local link in {path.relative_to(ROOT)}: {target}")
    test_count = 0
    for week in weeks:
        folder = ROOT / week["path"]
        doc = (folder / "docs/en.md").read_text()
        for section in SECTIONS:
            if f"## {section}\n" not in doc:
                failures.append(f"{week['path']}: missing {section}")
        if "**Languages:** Python" not in doc:
            failures.append(f"{week['path']}: language mismatch")
        if not list((folder / "outputs").glob("*")):
            failures.append(f"{week['path']}: missing artifact")
        questions = json.loads((folder / "quiz.json").read_text())["questions"]
        if [q["stage"] for q in questions] != ["pre", "check", "check", "check", "post", "post"]:
            failures.append(f"{week['path']}: quiz stages")
        for q in questions:
            if len(q["options"]) != 4 or type(q["correct"]) is not int or not 0 <= q["correct"] < 4 or not q["explanation"]:
                failures.append(f"{week['path']}: invalid quiz")
        tree = ast.parse((folder / "code/tests/test_main.py").read_text())
        count = sum(isinstance(n, ast.FunctionDef) and n.name.startswith("test_") for n in ast.walk(tree))
        test_count += count
        if count < 5:
            failures.append(f"{week['path']}: fewer than five tests")
        commands = [[sys.executable, str(folder / "code/main.py")],
                    [sys.executable, "-m", "unittest", "discover", "-s", str(folder / "code/tests"), "-v"]]
        for command in commands:
            try:
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=20)
                if result.returncode:
                    failures.append(f"{week['path']}: {result.stdout}{result.stderr}")
            except subprocess.TimeoutExpired:
                failures.append(f"{week['path']}: command timed out")
        print(f"Week {week['week']:02}: demo and {count} tests checked")
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    print(result.stderr.strip())
    if result.returncode:
        failures.append("Integration tests failed")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"PASS: {len(weeks)} lessons, {test_count} lesson tests, integration suite, Python-only structure, and local links")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate())
