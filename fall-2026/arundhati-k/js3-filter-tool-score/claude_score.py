"""Claude scorer runs on the 20 held-out postings. LIVE Claude calls through the Claude Code CLI (`claude -p`).

One object changes per run (Chapter 9):
  P1  prompt judge_v1 (inherited from my JS1 baseline), context = full posting body          (baseline)
  P2  prompt judge_v2 (my FILTER.md level/location rules), context = full body               (prompt change)
  C2  prompt judge_v1, context = required/responsibility lines only (FILTER.md rule D idea)  (context change)

python3 claude_score.py P1 [P2 C2 ...]   -> evidence/claude-runs/<run>.jsonl
Fresh, tool-less session per call, no settings, no MCP; default model; run from an empty temp dir.
"""
import concurrent.futures as cf
import csv
import datetime as dt
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from jsagent3.evidence import sections
from jsagent3.mcp_server import load_postings

HERE = Path(__file__).resolve().parent
SYSTEM = "You classify job postings for a fixed contract. Output only the JSON object the user asks for."
RUNS = {"P1": ("judge_v1.txt", "full"), "P2": ("judge_v2.txt", "full"), "C2": ("judge_v1.txt", "required")}


def resume_skills():
    r = json.loads((HERE / "persona" / "rohan-desai.resume.example.json").read_text())
    return json.dumps(r.get("skills", {}), indent=1)


def context(p, mode):
    if mode == "full":
        return p["body"]
    lines = [ln for k, ln in sections(p["body"]) if k == "required"]
    return "\n".join(lines) or "(no requirements section found)"


def build(template, p, mode):
    return template.format(resume_skills=resume_skills(), posting_id=p["id"], title=p["title"],
                           location=p["location"], content=context(p, mode))


def call(prompt):
    cmd = ["claude", "-p", "--output-format", "json", "--tools", "", "--setting-sources", "",
           "--strict-mcp-config", "--no-session-persistence", "--system-prompt", SYSTEM]
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=empty, timeout=300)
    return json.loads(proc.stdout)


def verdict(reply):
    m = re.search(r"\{.*\}", reply or "", re.S)
    try:
        v = json.loads(m.group(0))["verdict"] if m else None
    except (json.JSONDecodeError, KeyError):
        v = None
    return v if v in ("RELEVANT", "NOT RELEVANT") else None


def run(name):
    tmpl_file, mode = RUNS[name]
    template = (HERE / "prompts" / tmpl_file).read_text()
    posts = load_postings()
    rows = list(csv.DictReader((HERE / "labels" / "heldout.csv").open()))
    out = HERE / "evidence" / "claude-runs" / f"{name}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    def one(r):
        p = posts[r["id"]]
        asked = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        try:
            o = call(build(template, p, mode))
            reply, models, err = o.get("result", ""), sorted((o.get("modelUsage") or {}).keys()), None
        except Exception as e:
            reply, models, err = "", [], f"{type(e).__name__}: {e}"
        return {"run": name, "prompt": tmpl_file, "context": mode, "n": int(r["n"]), "posting_id": p["id"],
                "asked_at_utc": asked, "models": models, "reply": reply, "verdict": verdict(reply), "error": err}

    with cf.ThreadPoolExecutor(6) as ex:
        recs = sorted(ex.map(one, rows), key=lambda x: x["n"])
    with out.open("w") as f:
        for rec in recs:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(name, "valid", sum(r["verdict"] is not None for r in recs), "/", len(recs), "->", out)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        run(n)
