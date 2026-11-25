"""Ask real Claude (Claude Code CLI, headless) to score postings. One condition per run; every response is saved.

    python3 tools/claude_score.py --label B1 --split heldout                       # baseline
    python3 tools/claude_score.py --label E2-prompt-v2 --split heldout --prompt prompts/score-v2.md
    python3 tools/claude_score.py --label E3-title-only --split heldout --context title_location
    python3 tools/claude_score.py --label E4-with-tool --split heldout --with-tool
    python3 tools/claude_score.py --label E5-haiku --split heldout --model haiku

The five knobs are the Chapter 9 objects: --prompt (the prompt), --context (what Claude is shown), --with-tool (the tool
list), --model (a setting). The filter file is measured without Claude (tools/measure.py). Each run writes
runs/claude/<label>/<item>.json (the raw CLI JSON + the parsed verdict) and runs/claude/<label>/meta.json. Live.
"""

import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from js3 import corpus  # noqa: E402
from js3.text import plain_text  # noqa: E402

MAX_TEXT = 6000  # characters of posting text shown to Claude (hand-set; keeps each call small)
PERSONA = ("Arya Sahni, Boston MA. MS Information Systems (Northeastern, Dec 2025). About 1 year of experience: "
           "AI Engineer Co-op at Staples (Jan-Aug 2025): an LLM agent with LangGraph used by 120+ analysts, an inference "
           "pipeline with MLflow tracing, an A/B framework for LLM evaluation. Skills: Python, SQL, Power BI, LangGraph, "
           "MLflow, Mem0, Delta Lake, AWS.")


def build_prompt(template, p, context):
    text = plain_text(p.get("content", ""))
    if context == "title_location":
        text = "(not shown)"
    else:
        text = text[:MAX_TEXT] + (" […]" if len(text) > MAX_TEXT else "")
    persona = PERSONA if context != "no_persona" else "(not given)"
    return (template.replace("{{PERSONA}}", persona).replace("{{BOARD}}", p["board"])
            .replace("{{TITLE}}", p["title"]).replace("{{LOCATION}}", p["location"]["name"] or "(none)")
            .replace("{{EMPLOYMENT}}", p.get("employment") or "(board does not say)").replace("{{TEXT}}", text))


def parse_verdict(result_text):
    m = re.search(r"\{.*\}", result_text or "", re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except ValueError:
        return None
    return obj if obj.get("verdict") in ("show", "not", "cannot_tell") else None


def one(item, prompt, model, with_tool, outdir):
    cmd = ["claude", "-p", "--output-format", "json", "--strict-mcp-config"]
    tmp = tempfile.mkdtemp()
    if with_tool:
        cfg = {"mcpServers": {"js3": {"command": sys.executable, "args": ["-m", "js3.mcp_server"],
                                      "env": {"PYTHONPATH": str(ROOT)}}}}
        Path(tmp, "mcp.json").write_text(json.dumps(cfg))
        cmd += ["--tools", "", "--mcp-config", str(Path(tmp, "mcp.json")), "--allowedTools", "mcp__js3__score_posting"]
        prompt += (f"\n\nYou may call the score_posting tool (board={item['board']}, id={item['id']}) to see how Riya's "
                   "written filter scores this posting. The final verdict is yours.")
    else:
        cmd += ["--tools", ""]
    if model:
        cmd += ["--model", model]
    t0 = time.time()
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=tmp, timeout=300)
    try:
        raw = json.loads(p.stdout)
    except ValueError:
        raw = {"unparsed_stdout": p.stdout[-3000:], "stderr": p.stderr[-2000:]}
    verdict = parse_verdict(raw.get("result", "")) if isinstance(raw, dict) else None
    rec = {"item": item["item"], "board": item["board"], "id": item["id"], "title": item["title"],
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seconds": round(time.time() - t0, 1),
           "returncode": p.returncode, "parsed": verdict, "prompt_sent": prompt, "cli_json": raw}
    (outdir / f"item-{item['item']:02d}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    return item["item"], (verdict or {}).get("verdict")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--split", default="heldout", choices=["heldout", "audit"])
    ap.add_argument("--prompt", default="prompts/score-v1.md")
    ap.add_argument("--context", default="full", choices=["full", "title_location", "no_persona"])
    ap.add_argument("--model", default=None)
    ap.add_argument("--with-tool", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    sample = json.loads((ROOT / "audit" / "sample.json").read_text())["items"]
    items = [i for i in sample if i["split"] == a.split]
    posts = corpus.by_key(corpus.load())
    template = (ROOT / a.prompt).read_text()
    outdir = ROOT / "runs" / "claude" / a.label
    outdir.mkdir(parents=True, exist_ok=True)
    ver = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    meta = {"label": a.label, "split": a.split, "n": len(items), "prompt": a.prompt, "context": a.context,
            "model": a.model or "(CLI default)", "with_tool": a.with_tool, "claude_cli": ver,
            "max_text_chars": MAX_TEXT, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(one, it, build_prompt(template, posts[(it["board"], it["id"])], a.context), a.model,
                          a.with_tool, outdir) for it in items]
        got = dict(f.result() for f in futs)
    meta["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    meta["unparsed"] = [k for k, v in got.items() if v is None]
    (outdir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps({k: got[k] for k in sorted(got)}), "unparsed:", meta["unparsed"])


if __name__ == "__main__":
    main()
