"""Brief Step 2.4, one change at a time, measured on the held-out set H (data/heldout, 30 postings).

  python tools/experiments.py run   [--variants B,P,C,T,S]   # Claude stage: saves every stdout, needs CLAUDE_BIN
  python tools/experiments.py score                         # needs Siddi's labels; filter variants run here

Claude variants (each differs from B in exactly one object; see experiments/PLAN.md):
  B  baseline: prompts/judge_v1.md (inherited from JS1), claude-sonnet-5-5, no tools
  P  prompt:   prompts/judge_v2.md (JS1's pre-registered one-sentence seniority rule)
  C  context:  prompts/judge_v1+labeling-context.md (one added candidate line: Siddi's LABELING.md answers)
  T  tools:    judge_v1 + the score_posting MCP tool, with one line naming the posting's board and id
  S  setting:  judge_v1 on claude-haiku-5-5"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_heldout  # noqa: E402
from js3 import claude_cli, judge, policy  # noqa: E402
from js3 import filter as flt  # noqa: E402

VARIANTS = {
    "B": {"prompt": "judge_v1", "model": claude_cli.MODEL, "tools": False, "changes": "nothing (baseline)"},
    "P": {"prompt": "judge_v2", "model": claude_cli.MODEL, "tools": False, "changes": "the prompt"},
    "C": {"prompt": "judge_v1+labeling-context", "model": claude_cli.MODEL, "tools": False,
          "changes": "the context given to Claude"},
    "T": {"prompt": "judge_v1", "model": claude_cli.MODEL, "tools": True, "changes": "the tool list"},
    "S": {"prompt": "judge_v1", "model": "claude-haiku-5-5", "tools": False, "changes": "a setting (model)"},
}
FILTERS = ["v1", "v1.1", "v1.2"]
OUT = policy.ROOT / "output" / "experiments"
TEXT_CFG = "config/filter.v1.json"              # every Claude variant reads the posting text prepared by filter v1


def run_one(name: str, v: dict, persona: dict, cfg: dict, template: str, p: dict) -> dict:
    tag = f"{p['board']}-{p['id']}"
    prompt = judge.fill(template, persona, p, judge.requirements_text(cfg, p), tool_line=v["tools"])
    extra, mcp = [], None
    if v["tools"]:
        mcp = claude_cli.js3_mcp_config(f"evidence/experiments/T/{tag}-server.jsonl", ["--postings", "data/heldout"])
        extra = ["--allowedTools", "mcp__js3__score_posting"]
    reasons, paths = [], []
    for attempt in ("", "_retry1"):
        _, out, err, code = claude_cli.run(prompt, extra, mcp_config=mcp, model=v["model"])
        path = OUT / "claude" / name / f"{tag}{attempt}.json"
        policy.write_bytes(path, out)
        paths.append(path.relative_to(policy.ROOT).as_posix())
        ans, why = judge.validate(out)
        if ans:
            return {"variant": name, "key": f"{p['board']}:{p['id']}", "title": p["title"], "status": "ok",
                    "verdict": ans["verdict"], "justification": ans["justification"], "raw": paths}
        reasons.append(why)
    return {"variant": name, "key": f"{p['board']}:{p['id']}", "title": p["title"], "status": "invalid_output",
            "verdict": None, "reasons": reasons, "raw": paths}


def cmd_run(names: list[str]) -> int:
    persona = json.loads(policy.check_read("data/persona_resume.json").read_text(encoding="utf-8"))
    cfg = json.loads(policy.check_read(TEXT_CFG).read_text(encoding="utf-8"))
    H = build_heldout.load()
    for name in names:
        v = VARIANTS[name]
        template = policy.check_read(f"prompts/{v['prompt']}.md").read_text(encoding="utf-8")
        with ThreadPoolExecutor(max_workers=4) as ex:
            rows = list(ex.map(lambda p: run_one(name, v, persona, cfg, template, p), H))
        policy.write_bytes(OUT / "claude" / f"{name}.jsonl",
                           "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8"))
        ok = sum(r["status"] == "ok" for r in rows)
        rel = sum(r["verdict"] == "relevant" for r in rows)
        print(f"{name} ({v['changes']}): {ok}/{len(rows)} valid, {rel} relevant")
    return 0


def hand_labels() -> dict:
    """{key: 'relevant'|'not_relevant'} for H: Siddi's sheet labels for the 20 sheet items, JS1 labels for 10."""
    labels = {}
    for line in policy.check_read("labels/hand_labels.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            x = json.loads(line)
            labels[x["key"]] = x["label"]
    for line in policy.check_read("labels/heldout_js1_labels.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            x = json.loads(line)
            labels[f"stripe:{x['posting_id']}"] = x["label"]
    return labels


def confusion(pairs) -> dict:
    """pairs of (predicted relevant: bool | None, hand label). None = no answer (cannot tell / invalid)."""
    c = {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "no_answer_rel": 0, "no_answer_not": 0}
    for pred, lab in pairs:
        rel = lab == "relevant"
        if pred is None:
            c["no_answer_rel" if rel else "no_answer_not"] += 1
        elif pred and rel:
            c["tp"] += 1
        elif pred:
            c["fp"] += 1
        elif rel:
            c["fn"] += 1
        else:
            c["tn"] += 1
    c["agree"] = c["tp"] + c["tn"]
    c["n"] = len(pairs)
    return c


def cmd_score() -> int:
    labels = hand_labels()
    H = build_heldout.load()
    keys = [f"{p['board']}:{p['id']}" for p in H]
    missing = [k for k in keys if k not in labels]
    if missing:
        raise SystemExit(f"no hand label for {missing}")
    table = {"held_out": {"n": len(keys), "relevant": sum(labels[k] == "relevant" for k in keys)}, "rows": []}
    per_item = {k: {"title": p["title"], "hand": labels[k]} for k, p in zip(keys, H)}
    for f in FILTERS:
        cfg = json.loads(policy.check_read(f"config/filter.{f}.json").read_text(encoding="utf-8"))
        preds = {}
        for p in H:
            r = flt.evaluate(cfg, p)
            preds[f"{p['board']}:{p['id']}"] = {"keep": True, "reject": False}.get(r["verdict"])
        for k in keys:
            per_item[k][f"filter {f}"] = preds[k]
        table["rows"].append({"object": "filter file", "variant": f, **confusion([(preds[k], labels[k]) for k in keys])})
    for name, v in VARIANTS.items():
        path = OUT / "claude" / f"{name}.jsonl"
        if not path.exists():
            continue
        rows = {r["key"]: r for r in map(json.loads, path.read_text(encoding="utf-8").splitlines())}
        preds = {k: (None if rows[k]["verdict"] is None else rows[k]["verdict"] == "relevant") for k in keys}
        for k in keys:
            per_item[k][f"claude {name}"] = preds[k]
        table["rows"].append({"object": v["changes"], "variant": name, **confusion([(preds[k], labels[k]) for k in keys])})
    table["per_item"] = per_item
    policy.write_bytes(OUT / "scores.json", (json.dumps(table, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"H: {table['held_out']}")
    for r in table["rows"]:
        print(f"{r['variant']:5} {r['object']:28} agree {r['agree']}/{r['n']}  tp {r['tp']} fp {r['fp']} fn {r['fn']} "
              f"tn {r['tn']}  no-answer {r['no_answer_rel'] + r['no_answer_not']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "score"])
    ap.add_argument("--variants", default="B,P,C,T,S")
    a = ap.parse_args()
    return cmd_run(a.variants.split(",")) if a.cmd == "run" else cmd_score()


if __name__ == "__main__":
    sys.exit(main())
