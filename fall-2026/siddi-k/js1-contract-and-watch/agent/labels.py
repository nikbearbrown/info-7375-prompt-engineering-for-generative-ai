"""Hand-label set (CONTRACT.md, Hand-label set): the contract's seed-42 selection of 20 postings and the base-rate
count. Writes only to experiments/output/; prints the rule-relevant COUNT, never per-posting verdicts."""
from __future__ import annotations

import html
import json
import random
import re
from pathlib import Path

from . import rule, textprep


def _posting(job: dict) -> dict:
    return {"id": int(job["id"]), "title": job["title"], "location": (job.get("location") or {}).get("name", "")}


def select(board: dict, persona: dict, cfg) -> dict:
    jobs = {int(j["id"]): j for j in board["jobs"]}

    def sentences(i):
        return textprep.requirements_sentences(jobs[i].get("content"), cfg.cut_headings, cfg.drop_phrases)

    def passes_title(i):
        return rule.title_check(jobs[i]["title"], persona)["passed"]

    def passes_seniority(i):
        return rule.seniority_check(jobs[i]["title"], sentences(i), persona)["passed"]

    # The contract's selection, line for line.
    rng = random.Random(42)
    all_ids = sorted(int(j["id"]) for j in board["jobs"])            # ascending
    candidates = [i for i in all_ids if passes_title(i) and passes_seniority(i)]
    A = rng.sample(candidates, k=min(10, len(candidates)))
    B = rng.sample(sorted(set(all_ids) - set(A)), k=20 - len(A))
    labels = A + B                                                    # in sample order
    dev, held_out = labels[0::2], labels[1::2]                        # 10 and 10

    relevant = sum(1 for i in labels if sentences(i)
                   and rule.judge(_posting(jobs[i]), sentences(i), persona, cfg.vocab)["rule_verdict"] == "relevant")
    return {"seed": 42, "board_postings": len(all_ids), "candidates": len(candidates), "A": A, "B": B,
            "labels": labels, "dev": dev, "held_out": held_out, "rule_relevant_count": relevant}


def display_text(content: str | None) -> str:
    """The whole description for a human labeller: tags removed, case kept, nothing cut."""
    p = textprep._Lines()
    p.feed(html.unescape(content or ""))
    p.close()
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in "".join(p.parts).split("\n")]
    return "\n".join(ln for ln in lines if ln)


def write_sheet(board: dict, sel: dict, board_path: str, out_dir: Path) -> None:
    jobs = {int(j["id"]): j for j in board["jobs"]}
    out_dir.mkdir(parents=True, exist_ok=True)
    split = {i: "dev" for i in sel["dev"]} | {i: "held_out" for i in sel["held_out"]}
    record = {k: sel[k] for k in ("seed", "board_postings", "candidates", "labels", "dev", "held_out")}
    record["board"] = board_path
    (out_dir / "label_selection.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    with (out_dir / "hand_labels.template.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for i in sorted(sel["labels"]):
            f.write(json.dumps({"posting_id": i, "split": split[i], "title": jobs[i]["title"], "label": None,
                                "reason": None}, ensure_ascii=False) + "\n")
    md = [f"# The 20 postings to hand-label", "",
          f"Selected from `{board_path}` by `python -m agent select-labels` (CONTRACT.md, Hand-label set, seed 42). "
          "Listed by posting id, not by split. Each description is the posting's own text with HTML tags removed; "
          "nothing is cut or summarised. Copy `hand_labels.template.jsonl` to `labels/hand_labels.jsonl` and fill "
          "`label` (relevant / not_relevant) and `reason` using LABELING.md.", ""]
    for n, i in enumerate(sorted(sel["labels"]), 1):
        j = jobs[i]
        md += [f"## {n}. {j['title']}", "", f"- posting_id: `{i}`",
               f"- location.name: {(j.get('location') or {}).get('name', '')}",
               f"- departments: {'; '.join(d.get('name', '') for d in j.get('departments') or [])}",
               f"- absolute_url (recorded, never fetched by the agent): {j.get('absolute_url')}", "",
               display_text(j.get("content")), "", "---", ""]
    (out_dir / "to_label.md").write_text("\n".join(md), encoding="utf-8")
