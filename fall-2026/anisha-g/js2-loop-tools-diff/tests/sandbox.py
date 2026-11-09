"""Shared fixtures: a throwaway project root with reports/job-watch/ (the only writable folder), a sibling reports/job-watch-evil/, and a symlink that points outside."""
import os, tempfile
from pathlib import Path

def make_sandbox():
    tmp = Path(tempfile.mkdtemp(prefix="js2-")).resolve()
    root = tmp / "proj"; out = root / "reports" / "job-watch"
    for d in ("config", "persona", "reports/job-watch/runs/r1", "reports/job-watch-evil", "outside"):
        (root / d).mkdir(parents=True)
    (root / "persona/resume.json").write_text((Path(__file__).resolve().parent.parent / "persona/resume.json").read_text())
    (root / "config/budgets.json").write_text("{}"); (root / "agent.py").write_text("# source\n")
    (out / "runs/r1/trace.jsonl").write_text("{}\n"); (out / "run-2.json").write_text("{}")
    (root / "outside/target.txt").write_text("secret")
    os.symlink(root / "outside", out / "link")
    return {"tmp": tmp, "ROOT": root, "OUT": out, "SIB": root / "reports/job-watch-evil", "LINK": out / "link"}

def expand(s, sb):
    for k in ("ROOT", "OUT", "SIB", "LINK"):
        s = s.replace("{%s}" % k, str(sb[k]))
    return s
