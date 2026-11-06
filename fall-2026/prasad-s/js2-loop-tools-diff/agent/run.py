"""One run of the agent and its run report (CONTRACT.md §1, §2, §6)."""

import json
from datetime import datetime, timezone
from pathlib import Path

from . import CONTRACT_VERSION
from .config import fetch_url_for, load_config, require_fetch_url
from .fetch import fetch_live, load_seed, save_evidence
from .persona import check_persona, load_persona
from .replies import CLAUDE_LABEL, claude_judgment, load_metadata
from .rule import judge
from .state import compute_watch, load_state, parse_board_response, write_state

NOT_STATED = "not stated"


def build_record(posting, persona, outputs_dir, metadata, metadata_error):
    """One §2 record: both judges side by side for the same posting_id."""
    posting_id = posting["posting_id"]
    rule_verdict, rule_justification = judge(posting, persona)
    claude_verdict, claude_justification = claude_judgment(
        posting_id, posting, persona, outputs_dir, metadata, metadata_error
    )
    location = posting.get("location")
    location_name = location.get("name") if isinstance(location, dict) else None
    return {
        "posting_id": posting_id,
        "title": posting.get("title"),
        "absolute_url": posting.get("absolute_url"),
        "location.name": location_name if isinstance(location_name, str) else NOT_STATED,
        "rule_verdict": rule_verdict,
        "rule_justification": rule_justification,
        "claude_verdict_label": CLAUDE_LABEL,
        "claude_verdict": claude_verdict,
        "claude_justification": claude_justification,
    }


def run(config_path, seed_path=None, report_path=None):
    """Live run when seed_path is None, otherwise a seeded run. Returns the report.

    Every check that can refuse happens before the fetch. state.json is written
    last, only after the report is written (§1 item 3).
    """
    config = load_config(config_path)
    persona = load_persona(config["resume_path"])
    check_persona(persona)
    state_before = load_state(config["state_path"])

    if seed_path is None:
        mode = "live"
        url = fetch_url_for(config["board_token"])
        require_fetch_url(url, config["allow_list"])
        raw, fetched_at = fetch_live(url, config["allow_list"])
        source = save_evidence(raw, url, fetched_at, config["evidence_dir"])
    else:
        # Decision 2026-10-27: a seeded run updates state.json but saves no new evidence.
        mode = "seeded"
        raw, source = load_seed(seed_path, config["evidence_dir"])

    postings = parse_board_response(raw)
    by_id = {}
    for posting in postings:
        by_id.setdefault(posting["posting_id"], posting)
    watch = compute_watch(state_before, [posting["posting_id"] for posting in postings])

    metadata, metadata_error = {}, None
    if watch.new_ids:
        metadata, metadata_error = load_metadata(config["claude_outputs_dir"])
    records = [
        build_record(by_id[posting_id], persona, config["claude_outputs_dir"], metadata, metadata_error)
        for posting_id in watch.new_ids
    ]

    if watch.baseline:
        message = f"baseline run: {len(watch.state_after)} ids saved, 0 postings reported as new"
    elif not records:
        message = "no new postings"
    else:
        message = f"{len(records)} new postings"
    report = {
        "contract_version": CONTRACT_VERSION,
        "summary": {
            "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "mode": mode,
            "baseline": watch.baseline,
            "total_fetched": len(postings),
            "new_count": len(records),
            "new_ids": list(watch.new_ids),
            "message": message,
            "source": source,
        },
        "new_postings": records,
    }

    report_path = Path(report_path) if report_path else Path(config_path).resolve().parent / "run_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_state(config["state_path"], watch.state_after)
    return report
