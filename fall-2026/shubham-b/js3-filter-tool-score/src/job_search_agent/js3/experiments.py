"""Chapter 9: one change to one object at a time, measured on held-out labels.

``experiment filter``  E1/E2: filter-file and threshold changes, deterministic, on
                       the JS1 held-out labels (and the tuning labels, reported apart).
``experiment context --condition {full,trunc1500}``  E3: the JS1 judge prompt v2 with
                       the posting content given whole or cut to its first 1,500
                       characters; one ``claude`` call per held-out posting, each
                       condition run once.

Labels are read from ``experiments/prompt/labels/`` and ``experiments/sampling/``; the
postings from the JS1 hand-check raw the labels were made on.
"""

from __future__ import annotations

import argparse
import dataclasses
import html
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from job_search_agent.js3.corpus import HANDCHECK_RAW, load_inputs
from job_search_agent.js3.filter import FilterSpec, load_filter, score
from job_search_agent.models import Posting
from job_search_agent.providers.greenhouse import GreenhouseProvider
from job_search_agent.resume import default_project_root
from job_search_agent.text import clean_html

TRUNCATE_CHARS = 1500
OUT = "data/js3/experiments"


def labels(root: Path) -> dict[str, dict[str, bool]]:
    """``{"heldout": {id: relevant}, "tuning": {...}}``; MATCH means relevant."""

    def read(rel: str) -> dict[str, bool]:
        doc = json.loads((root / rel).read_text(encoding="utf-8"))
        return {x["posting_id"]: x["hand_label"] == "MATCH" for x in doc["labels"]}

    tuning = read("experiments/prompt/labels/dev.labels.json")
    sampling = json.loads(
        (root / "experiments/sampling/hand_labels.json").read_text(encoding="utf-8")
    )
    tuning |= {pid: v["hand_label"] == "MATCH" for pid, v in sampling["labels"].items()}
    return {
        "heldout": read("experiments/prompt/labels/heldout.labels.json"),
        "tuning": tuning,
    }


def handcheck_postings(root: Path) -> dict[str, Posting]:
    """The postings exactly as labelled (the 2026-10-29 hand-check raw)."""
    return {
        p.posting_id: p
        for p in GreenhouseProvider()
        .parse((root / HANDCHECK_RAW).read_bytes())
        .postings
    }


def agreement(
    predict: Callable[[Posting], bool],
    gold: Mapping[str, bool],
    postings: Mapping[str, Posting],
) -> dict[str, Any]:
    """Agreement and the 2x2 table of one predictor against one label set."""
    rows = []
    for pid, truth in sorted(gold.items()):
        rows.append(
            {
                "posting_id": pid,
                "title": postings[pid].title,
                "label": truth,
                "predicted": predict(postings[pid]),
            }
        )
    agree = sum(r["label"] == r["predicted"] for r in rows)
    return {
        "agree": agree,
        "n": len(rows),
        "false_keep": [
            r["posting_id"] for r in rows if r["predicted"] and not r["label"]
        ],
        "false_reject": [
            r["posting_id"] for r in rows if r["label"] and not r["predicted"]
        ],
        "rows": rows,
    }


def cmd_filter(root: Path) -> dict[str, Any]:
    """E1 (filter file: v0.1→v0.2, v0.2→v0.3) and E2 (threshold 7→6 on v0.3)."""
    inputs = load_inputs(root)
    postings = handcheck_postings(root)
    gold = labels(root)
    files = {
        v: load_filter(root / f"experiments/js3/filters/FILTER.v{v}.md")
        for v in ("0.1", "0.2", "0.3")
    }
    variants: dict[str, FilterSpec] = {
        "v0.1": files["0.1"],
        "v0.2": files["0.2"],
        "v0.3": files["0.3"],
        "v0.3 threshold 6": dataclasses.replace(files["0.3"], threshold=6),
    }

    def kept(spec: FilterSpec) -> Callable[[Posting], bool]:
        return lambda p: score(p, p.posting_id, "greenhouse/stripe", spec, inputs).kept

    result: dict[str, Any] = {
        name: {
            set_name: agreement(kept(spec), g, postings) for set_name, g in gold.items()
        }
        for name, spec in variants.items()
    }
    result["_steps"] = [
        {
            "id": "E1a",
            "object": "filter file",
            "change": "cut 'api','apis' from R5",
            "from": "v0.1",
            "to": "v0.2",
        },
        {
            "id": "E1b",
            "object": "filter file",
            "change": "add R2 generic_blockers",
            "from": "v0.2",
            "to": "v0.3",
        },
        {
            "id": "E2",
            "object": "setting",
            "change": "threshold 7 -> 6",
            "from": "v0.3",
            "to": "v0.3 threshold 6",
        },
    ]
    return result


def truncated(p: Posting, chars: int = TRUNCATE_CHARS) -> Posting:
    """The posting with its content cut to the first ``chars`` cleaned characters."""
    cut = html.escape(clean_html(p.content_raw)[:chars])
    return dataclasses.replace(p, content_raw=cut, raw={**p.raw, "content": cut})


def cmd_context(root: Path, condition: str) -> dict[str, Any]:
    """E3: one first-reply ``claude`` call per held-out posting under one condition."""
    # builds the JS1 judge wiring
    from job_search_agent.experiments._wiring import Wiring

    out = root / OUT / f"e3-{condition}.json"
    if out.exists():
        raise SystemExit(f"{out.relative_to(root)} exists; each condition runs once")
    wiring = Wiring(root / "config" / "agent.toml")
    judge = wiring.judge_call()
    prompt = wiring.load_prompt("v2")
    postings = handcheck_postings(root)
    gold = labels(root)["heldout"]
    records = []
    for pid in sorted(gold):
        p = postings[pid] if condition == "full" else truncated(postings[pid])
        rec = judge(
            p, prompt, f"js3/experiments/e3-{condition}/calls/{pid}"
        ).model_dump(mode="json")
        rec["hand_label"] = "MATCH" if gold[pid] else "NO_MATCH"
        rec["content_chars"] = len(clean_html(p.content_raw))
        records.append(rec)
        print(pid, rec["label"], rec["hand_label"], flush=True)
    agree = sum(
        (r["label"] == "RELEVANT") == (r["hand_label"] == "MATCH")
        for r in records
        if r["first_reply_valid"]
    )
    return {
        "experiment": "E3",
        "object": "context given to Claude",
        "condition": condition,
        "truncate_chars": TRUNCATE_CHARS if condition != "full" else None,
        "prompt": prompt.prompt_id,
        "prompt_sha256": prompt.sha256,
        "valid": sum(r["first_reply_valid"] for r in records),
        "agree_with_hand_labels": agree,
        "n": len(records),
        "records": records,
    }


def main(argv: list[str] | None = None) -> int:
    """``python -m job_search_agent.js3 experiment {filter|context} ...``."""
    parser = argparse.ArgumentParser(prog="experiment")
    parser.add_argument("which", choices=["filter", "context"])
    parser.add_argument("--condition", choices=["full", "trunc1500"], default="full")
    args = parser.parse_args(argv)
    root = default_project_root()
    if args.which == "filter":
        doc, name = cmd_filter(root), "e1-e2-filter.json"
    else:
        doc, name = cmd_context(root, args.condition), f"e3-{args.condition}.json"
    path = root / OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {path.relative_to(root)}")
    return 0
