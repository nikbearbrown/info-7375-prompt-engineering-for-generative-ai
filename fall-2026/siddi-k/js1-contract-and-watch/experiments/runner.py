"""Experiment runner (CONTRACT.md, Experiment runner). Runs Claude on stored postings from a raw/ board with the same
isolated invocation as the agent. Reads raw/, labels/, config/, prompts/ and experiments/output/label_selection.json;
never reads or writes state/ or output/; writes only to experiments/output/.

    python -m experiments.runner sample --ids 111,222,333,444,555 --repeats 4 [--prompt judge_v1]
    python -m experiments.runner score --prompt judge_v1 --split dev
    python -m experiments.runner score --prompt judge_v2 --split held_out     (refuses a second held-out scoring)

Every call is a fresh `claude -p` process, i.e. a fresh conversation. There is no retry here: an output that fails
the validator is recorded as invalid_output and scored as a miss, because the variation is what is being measured.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import claude_judge, config, persona as persona_mod, textprep

OUT = Path("experiments") / "output"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def _append(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_board(root: Path) -> tuple[str, dict]:
    sel = json.loads((root / OUT / "label_selection.json").read_text(encoding="utf-8"))
    board = json.loads((root / sel["board"]).read_bytes())
    return sel["board"], {int(j["id"]): j for j in board["jobs"]}


def ask(root: Path, cfg, persona: dict, job: dict, raw_rel: str) -> dict:
    """One fresh Claude call on one stored posting; raw stdout saved unmodified to experiments/output/."""
    sentences = textprep.requirements_sentences(job.get("content"), cfg.cut_headings, cfg.drop_phrases)
    if not sentences:
        return {"status": "skipped_empty_requirements", "verdict": None, "raw_path": None}
    prompt = claude_judge.fill_prompt(cfg.prompt_template, persona, job["title"],
                                      (job.get("location") or {}).get("name", ""),
                                      textprep.requirements_text(sentences))
    out, note = claude_judge.run_claude(cfg.claude_argv, prompt)
    raw = root / raw_rel
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_bytes(out)
    answer, reason = claude_judge.validate_output(out)
    return {"status": "ok" if answer else "invalid_output", "verdict": answer["verdict"] if answer else None,
            "justification": answer["justification"] if answer else None,
            "reason": None if answer else reason + (f" ({note})" if note else ""), "raw_path": raw_rel}


def sample(root: Path, ids: list[int], repeats: int, prompt_version: str, log=print) -> list[dict]:
    cfg = config.load(root, prompt_version)
    persona = persona_mod.load(root / "data" / "persona_resume.json", cfg.vocab)
    board_path, jobs = load_board(root)
    recs = []
    for i in ids:
        for k in range(1, repeats + 1):
            res = ask(root, cfg, persona, jobs[i], (OUT / "sampling" / prompt_version / f"{i}_{k}.json").as_posix())
            rec = {"posting_id": i, "title": jobs[i]["title"], "repeat": k, "prompt_version": prompt_version,
                   "claude_model": cfg.claude_model, "board": board_path, "ran_at": _now(), **res}
            _append(root / OUT / "sampling.jsonl", rec)
            recs.append(rec)
            log(f"  {i} #{k}: {res['verdict'] or res['status']}")
    return recs


def score(root: Path, prompt_version: str, split: str, log=print) -> dict:
    out_path = root / OUT / f"experiment_{prompt_version}_{split}.jsonl"
    if split == "held_out" and out_path.exists():
        raise SystemExit(f"{out_path.name} exists: held_out is scored once, after the final prompt is frozen")
    cfg = config.load(root, prompt_version)
    persona = persona_mod.load(root / "data" / "persona_resume.json", cfg.vocab)
    board_path, jobs = load_board(root)
    labels = [r for r in _jsonl(root / "labels" / "hand_labels.jsonl") if r["split"] == split]
    if len(labels) != 10 or any(r.get("label") not in ("relevant", "not_relevant") for r in labels):
        raise SystemExit(f"labels/hand_labels.jsonl must hold 10 labelled {split} postings")
    if out_path.exists():
        out_path.unlink()          # a dev rerun replaces the earlier dev scoring of the same prompt
    hits = 0
    for r in labels:
        i = int(r["posting_id"])
        res = ask(root, cfg, persona, jobs[i], (OUT / "experiment" / prompt_version / split / f"{i}.json").as_posix())
        match = res["verdict"] == r["label"]
        hits += match
        _append(out_path, {"posting_id": i, "title": jobs[i]["title"], "split": split, "hand_label": r["label"],
                           "prompt_version": prompt_version, "claude_model": cfg.claude_model, "board": board_path,
                           "ran_at": _now(), "match": match, **res})
        log(f"  {i}: hand {r['label']:12} claude {res['verdict'] or res['status']:14} {'PASS' if match else 'miss'}")
    summary = {"prompt_version": prompt_version, "split": split, "passed": hits, "total": len(labels)}
    log(f"{prompt_version} on {split}: {hits}/{len(labels)} agree with the hand labels")
    return summary


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="python -m experiments.runner")
    ap.add_argument("--root", type=Path, default=config.ROOT, help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--ids", required=True)
    s.add_argument("--repeats", type=int, default=4)
    s.add_argument("--prompt", default=config.PROMPT_VERSION)
    c = sub.add_parser("score")
    c.add_argument("--prompt", required=True)
    c.add_argument("--split", choices=("dev", "held_out"), required=True)
    a = ap.parse_args(argv)
    root = a.root.resolve()
    if a.cmd == "sample":
        sample(root, [int(x) for x in a.ids.split(",")], a.repeats, a.prompt)
    else:
        score(root, a.prompt, a.split)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
