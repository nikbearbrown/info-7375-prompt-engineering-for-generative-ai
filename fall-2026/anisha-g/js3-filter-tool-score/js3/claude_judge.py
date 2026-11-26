"""Run the Claude judge experiments in runs/experiments.json on the held-out set, through the Claude Code CLI
(`claude -p`, headless). Every raw reply is saved to runs/<exp>/<id>.json with the date; nothing is parsed by hand.
Run:  python3 -m js3.claude_judge B B2 E1 E2 E3 E4      (second held-out set: python3 -m js3.claude_judge --h2 B B2 E1 E2 E4)"""
import json, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from js3.filter import load_corpus

ROOT = Path(__file__).resolve().parent.parent
EXPS = json.loads((ROOT / "runs/experiments.json").read_text())
RESUME = (ROOT / "persona/resume.json").read_text()
CORPUS = None

def build(exp, p):
    e = EXPS[exp]
    text = p["text"] if e["context"] == "full" else p["text"][:600]
    posting = json.dumps({"title": p["title"], "location": p.get("location"), "text": text}, ensure_ascii=False)
    prompt = (ROOT / e["prompt"]).read_text().replace("{resume}", RESUME).replace("{posting}", posting)
    if e["tools"] == "score_posting":
        prompt += "\n" + (ROOT / "prompts/tool_addendum.txt").read_text().replace("{id}", p["id"])
    return prompt

SETDIR = ""
def one(exp, pid):
    out = ROOT / "runs" / SETDIR / exp / (pid.replace(":", "_") + ".json")
    if out.exists(): return json.loads(out.read_text())
    e = EXPS[exp]; p = CORPUS[pid]
    cmd = ["claude", "-p", build(exp, p), "--model", e["model"], "--output-format", "json", "--strict-mcp-config"]
    if e["tools"] == "score_posting":
        cmd += ["--mcp-config", str(ROOT / "toolserver/configs/claude-mcp.json"), "--allowedTools", "mcp__js3__score_posting", "--tools", ""]
    else:
        cmd += ["--tools", ""]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=300)
    try: res = json.loads(r.stdout)
    except json.JSONDecodeError: res = {"raw_stdout": r.stdout, "stderr": r.stderr[-500:]}
    m = re.search(r'"verdict"\s*:\s*"(relevant|not_relevant)"', res.get("result", "") or "")
    rec = {"exp": exp, "id": pid, "date": datetime.now().isoformat(timespec="seconds"), "seconds": round(time.time() - t0, 1),
           "model_flag": e["model"], "verdict": m.group(1) if m else None, "result_text": res.get("result"),
           "cost_usd": res.get("total_cost_usd"), "num_turns": res.get("num_turns"), "is_error": res.get("is_error")}
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(rec, indent=1, ensure_ascii=False))
    return rec

def main(exps):
    global CORPUS, SETDIR
    CORPUS = {p["id"]: p for p in load_corpus(ROOT / "data/corpus.jsonl.gz")}
    if exps and exps[0] == "--h2":                     # second held-out set (audit/sets_h2.json) -> runs/H2/<exp>/
        SETDIR = "H2"; exps = exps[1:]; H = json.loads((ROOT / "audit/sets_h2.json").read_text())["H2_heldout"]
    else:
        H = json.loads((ROOT / "audit/sets.json").read_text())["H_heldout"]
    jobs = [(x, pid) for x in exps for pid in H]
    with ThreadPoolExecutor(6) as ex:
        for rec in ex.map(lambda j: one(*j), jobs):
            print(rec["exp"], rec["id"], rec["verdict"], rec.get("cost_usd"), flush=True)

if __name__ == "__main__": main(sys.argv[1:])
