"""Verdict lines (CONTRACT.md, Out): build one line per new posting and validate it at write time and read time."""
from __future__ import annotations

import json
import math
from pathlib import Path

from . import state
from .claude_judge import VERDICTS
from .config import CONTRACT_VERSION, DISCLAIMER, POSTING_FIELDS, RESUME_FIELDS

CHECKS = ("title_match", "seniority_ok", "location_ok", "skill_overlap")


def build(run: dict, cfg, posting: dict, rule_out: dict, claude_out: dict) -> dict:
    return {"run_id": run["run_id"], "run_mode": run["run_mode"], "seeded_from": run["seeded_from"],
            "contract_version": CONTRACT_VERSION, "vocab_version": cfg.vocab_version,
            "boilerplate_version": cfg.boilerplate_version, "prompt_version": cfg.prompt_version,
            "claude_model": cfg.claude_model, "posting_id": posting["id"], "posting_title": posting["title"],
            "posting_location": posting["location"], **rule_out, **claude_out, "disclaimer": DISCLAIMER}


class BoardCache:
    """Titles by posting id for raw/<run_id>/board.json, loaded once per run."""

    def __init__(self, root: Path):
        self.root, self.boards = root, {}

    def titles(self, run_id: str):
        if run_id not in self.boards:
            p = self.root / "raw" / run_id / "board.json"
            self.boards[run_id] = ({int(j["id"]): j["title"] for j in json.loads(p.read_bytes())["jobs"]}
                                   if p.exists() else None)
        return self.boards[run_id]


def check(line: dict, root: Path, cfg, persona: dict, boards: BoardCache, completed=None) -> list[str]:
    """Write-time checks; pass `completed` (run ids by mode) to add the read-time check."""
    e = []
    mode, seeded_from = line.get("run_mode"), line.get("seeded_from")
    if mode not in ("live", "seeded") or (seeded_from is not None) != (mode == "seeded"):
        e.append("run_mode/seeded_from mismatch")
    if line.get("rule_verdict") not in VERDICTS or line.get("rule_label") != "record":
        e.append("rule_verdict/rule_label invalid")
    checks = line.get("rule_checks") or {}
    if set(checks) != set(CHECKS):
        e.append("rule_checks must have exactly the four checks")
    elif (line.get("rule_verdict") == "relevant") != all(checks[c].get("passed") is True for c in CHECKS):
        e.append("rule_verdict disagrees with the four rule_checks")
    sk = checks.get("skill_overlap") or {}
    found, matched = sk.get("posting_skills") or [], sk.get("matched") or []
    n = sk.get("matched_count")
    exact = n / len(found) if found and isinstance(n, int) else 0.0
    if sk.get("passed") != (bool(found) and isinstance(n, int) and n >= 3 and exact >= 0.40):
        e.append("skill_overlap.passed disagrees with matched_count/ratio")
    if n != len(matched) or not math.isclose(sk.get("ratio", -1), round(exact, 4), abs_tol=1e-4):
        e.append("skill_overlap counts are inconsistent")
    if not set(matched) <= set(found) <= set(cfg.vocab):
        e.append("skill_overlap: matched must be within posting_skills, posting_skills within the vocab")
    if not set(matched) <= set(persona["skills"]):
        e.append("skill_overlap.matched names a skill not in persona skills")
    titles = boards.titles(line.get("run_id", ""))
    if titles is None:
        e.append("raw/<run_id>/board.json is missing")
    elif titles.get(line.get("posting_id")) != line.get("posting_title") or line.get("posting_id") not in titles:
        e.append("posting_id/posting_title do not match that posting in raw/<run_id>/board.json")
    if line.get("claude_model") != cfg.claude_model:
        e.append("claude_model is not the model pinned in config/claude_cmd.txt")
    status = line.get("claude_status")
    if status not in ("ok", "invalid_output") or line.get("claude_label") != "judgment":
        e.append("claude_status/claude_label invalid")
    cited = (line.get("claude_cited_resume_fields"), line.get("claude_cited_posting_fields"))
    if status == "ok":
        if line.get("claude_verdict") not in VERDICTS or not line.get("claude_justification"):
            e.append("ok line needs a claude_verdict in the enum and a non-empty justification")
        for lst, allowed in zip(cited, (RESUME_FIELDS, POSTING_FIELDS)):
            if not isinstance(lst, list) or not lst or not all(x in allowed for x in lst):
                e.append("ok line needs non-empty cited-field lists from the allowed names")
    elif status == "invalid_output":
        if any(v is not None for v in (line.get("claude_verdict"), line.get("claude_justification"), *cited)):
            e.append("invalid_output line must have null verdict, justification and cited lists")
    raw_paths = line.get("claude_raw_paths")
    if not isinstance(raw_paths, list) or not raw_paths or not all((root / p).exists() for p in raw_paths):
        e.append("a claude_raw_paths file is missing")
    if mode == "seeded" and titles is not None:
        src = root / str(seeded_from)
        board = root / "raw" / line["run_id"] / "board.json"
        if not src.exists() or src.read_bytes() != board.read_bytes():
            e.append("seeded board.json is not a byte-for-byte copy of seeded_from")
    if completed is not None and line.get("run_id") not in completed.get(mode, set()):
        e.append("run never completed (ignored at read time)")
    return e


def completed_by_mode(root: Path) -> dict:
    out = {}
    for mode in ("live", "seeded"):
        st = state.load(state.path_for(root, mode)) or {}
        out[mode] = {r["run_id"] for r in st.get("runs", []) if r.get("completed_at")}
    return out


def read_valid(root: Path, cfg, persona: dict):
    """Read-time stage: (lines that pass every check, [(line number, errors)] for the rest)."""
    path = root / "output" / "verdicts.jsonl"
    if not path.exists():
        return [], []
    completed, boards, good, bad = completed_by_mode(root), BoardCache(root), [], []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        line = json.loads(raw)
        errors = check(line, root, cfg, persona, boards, completed)
        (bad.append((i, errors)) if errors else good.append(line))
    return good, bad
