"""The one-change experiment (Chapter 9): does adding each claim's `statement` to the tool result change what Claude says?
Object changed: the tool result (variant A = as Claude Code first saw it, B = A plus `statement`). Nothing else changes:
same filter, same labeler, same model, same prompt, a fresh `claude -p` process (no memory) for every call.
Steps (run in order):
  python scripts/onechange.py sample   # seeded held-out pairs, excluding every posting used in an earlier sample
  python scripts/onechange.py run      # 20 pairs x 2 variants = 40 fresh Claude calls, 3 at a time
  python scripts/onechange.py sheet    # blind sheet: Vrajesh judges each sentence accurate / misleading, A/B hidden
Only Claude's final sentence is stored. Raw logs (session ids, local paths, hook output) are not kept."""
import csv
import json
import random
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from earlybird import boards  # noqa: E402

SEED = 7377
QUOTA = {"early_career": {"supported": 3, "insufficient": 3}, "stack_fit": {"supported": 2, "insufficient": 2},
         "sponsorship": {"insufficient": 3}, "no_clearance": {"insufficient": 3}, "ai_focus": {"supported": 2},
         "us_location": {"supported": 2}}
MODEL = "claude-sonnet-5-5"
PROMPT = ("Call score_posting for posting_id {id} on board {board}. Then answer in exactly ONE plain-English sentence, "
          "for a reader who has not seen the tool output: what does the posting's text say about the claim named "
          "'{claim}', and how sure can we be? Use only what the tool returned. If the label is insufficient, say "
          "'I cannot tell'.")
BROAD = {
    "early_career": r"years?|experience",
    "stack_fit": r"\b(python|golang|go|java|javascript|typescript|sql|react|next\.js|tailwind|postgres\w*|mongodb|redis|aws|gcp|docker|kubernetes|k8s|jenkins|terraform|protobuf|graphql|digitalocean)\b",
    "sponsorship": r"sponsor|visa|work authori[sz]ation|citizen|u\.?s\.? person",
    "no_clearance": r"clearance|citizen|u\.?s\.? person|top secret|ts/sci",
    "ai_focus": r"\bai\b|\bllm|agent|generative|machine learning",
    "us_location": r"\Z",
}
STATEMENTS = {"early_career": "The posting asks for fewer than 3 years of experience.", "sponsorship": "The employer will sponsor a visa.",
              "no_clearance": "No security clearance is required.", "us_location": "The role is in the US.",
              "stack_fit": "The posting names a technology from Rohan's documented shipped project (Go, PostgreSQL, Terraform, GraphQL, DigitalOcean).",
              "ai_focus": "The work involves building with LLMs or AI agents."}
P = ROOT / "results" / "onechange-pairs.json"
O = ROOT / "results" / "onechange-outputs.json"


def sample():
    used = set()
    for f in ("review/claim-check-key.json", "review/audit-key.json"):
        used |= {(k["board"], k["id"]) for k in json.loads((ROOT / f).read_text(encoding="utf-8"))}
    short = [s for s in json.loads((ROOT / "results/shortlist.json").read_text(encoding="utf-8"))
             if (s["board"], s["id"]) not in used]
    rng = random.Random(SEED)
    pairs = []
    for claim, byl in QUOTA.items():
        for label, n in byl.items():
            pool = [(s, c) for s in short for c in s["claims"] if c["claim"] == claim and c["label"] == label]
            for s, c in rng.sample(pool, min(n, len(pool))):
                pairs.append({"board": s["board"], "id": s["id"], "title": s["title"].strip(), "claim": claim,
                              "labeler_label": c["label"], "labeler_quote": c["quote"]})
    rng.shuffle(pairs)
    for i, p in enumerate(pairs, 1):
        p["i"] = i
    P.write_text(json.dumps(pairs, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(pairs), "held-out pairs from", len(short), "unused shortlisted postings, seed", SEED)


def one_call(job):
    pair, variant = job
    env_stmt = "1" if variant == "B" else "0"
    cfg = {"mcpServers": {"earlybird-score": {"command": "python", "args": ["-m", "earlybird.mcp_server"],
           "env": {"PYTHONPATH": str(ROOT), "PYTHONIOENCODING": "utf-8", "EARLYBIRD_INCLUDE_STATEMENT": env_stmt}}}}
    tmp = ROOT / "transcripts" / "private" / f"cfg-{variant}.json"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(cfg), encoding="utf-8")
    cmd = ["claude", "-p", PROMPT.format(**pair), "--mcp-config", str(tmp), "--strict-mcp-config",
           "--allowedTools", "mcp__earlybird-score__score_posting", "--disallowedTools", "Bash", "Edit", "Write", "Read",
           "WebFetch", "WebSearch", "--model", MODEL, "--max-turns", "4", "--output-format", "json"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=240)
    try:
        out = json.loads(r.stdout)
        return {"i": pair["i"], "variant": variant, "sentence": (out.get("result") or "").strip(), "is_error": out.get("is_error")}
    except json.JSONDecodeError:
        return {"i": pair["i"], "variant": variant, "sentence": "", "is_error": True, "stderr": r.stderr[-200:]}


def run():
    pairs = json.loads(P.read_text(encoding="utf-8"))
    jobs = [(p, v) for p in pairs for v in ("A", "B")]
    random.Random(SEED).shuffle(jobs)  # interleave so a drifting model or a busy hour does not line up with one variant
    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(one_call, jobs))
    O.write_text(json.dumps({"date": str(date.today()), "model": MODEL, "prompt": PROMPT, "results": results},
                            indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(results), "calls;", sum(1 for r in results if r["is_error"]), "errors")


def sheet():
    pairs = {p["i"]: p for p in json.loads(P.read_text(encoding="utf-8"))}
    outs = json.loads(O.read_text(encoding="utf-8"))["results"]
    posts = {}
    for f in sorted((ROOT / "data/snapshot-2026-11-01").glob("*.json")):
        for p in boards.parse(f.stem.split("_")[0], f.read_text(encoding="utf-8")):
            posts[(f.stem, p["id"])] = p
    rng = random.Random(SEED + 1)
    md = ["# One-change sheet (blind)\n",
          "For each posting, read the excerpts and the claim, then judge the two sentences X and Y that Claude wrote. "
          "**accurate** = a reader who sees only that sentence would understand correctly what the posting says about the claim "
          "(including 'I cannot tell' when the text is silent). **misleading** = the reader would draw a wrong or unsupported "
          "conclusion. Write `accurate` or `misleading` for X and Y in `onechange-labels.csv`. You do not know which sentence "
          "came from which variant.\n"]
    labels, key = [["pair", "X", "Y", "note"]], []
    for i in sorted(pairs):
        p = pairs[i]
        by = {o["variant"]: o["sentence"] for o in outs if o["i"] == i}
        order = ["A", "B"]
        rng.shuffle(order)
        t = posts[(p["board"], p["id"])]["descriptionPlain"]
        ex = []
        for m in re.finditer(BROAD[p["claim"]], t, re.I):
            a, b = max(0, m.start() - 80), min(len(t), m.end() + 80)
            if not ex or a > ex[-1][1]:
                ex.append([a, b])
            else:
                ex[-1][1] = b
        shown = " ... ".join(re.sub(r"\s+", " ", t[a:b]) for a, b in ex[:8]) or "(no matching words anywhere in the text)"
        loc = posts[(p["board"], p["id"])]["location"]
        md.append(f"\n## {i}. {p['title']} ({p['board']})\n- location: {loc}\n- **claim:** {STATEMENTS[p['claim']]}\n"
                  f"- excerpts: {shown[:1600]}\n- **X:** {by[order[0]]}\n- **Y:** {by[order[1]]}\n")
        labels.append([i, "", "", ""])
        key.append({"pair": i, "X": order[0], "Y": order[1], "claim": p["claim"], "labeler_label": p["labeler_label"]})
    (ROOT / "review/onechange-sheet.md").write_text("".join(md), encoding="utf-8")
    csv.writer(open(ROOT / "review/onechange-labels.csv", "w", newline="", encoding="utf-8")).writerows(labels)
    (ROOT / "review/onechange-key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    print("sheet for", len(pairs), "pairs")


{"sample": sample, "run": run, "sheet": sheet}[sys.argv[1]]()
