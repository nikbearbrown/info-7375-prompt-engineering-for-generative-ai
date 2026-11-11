"""The watch (CONTRACT.md, In + State + Out): one run = fetch or replay the board, save it, judge new postings only."""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from . import claude_judge, config, fetch, lines, persona as persona_mod, rule, state, textprep


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_run_id(root: Path) -> str:
    while True:
        rid = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        if not (root / "raw" / rid).exists():
            return rid
        time.sleep(1)


def _append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def run(root: Path, mode: str, seeded_from: str | None = None, log=print) -> dict:
    cfg = config.load(root)
    persona = persona_mod.load(root / "data" / "persona_resume.json", cfg.vocab)   # before anything is fetched
    if mode == "seeded":
        if not seeded_from:
            raise SystemExit("--mode seeded needs --seeded-from <saved board file>")
        src = (root / seeded_from).resolve()
        seeded_from = src.relative_to(root.resolve()).as_posix() if src.is_relative_to(root.resolve()) else str(src)
        body = src.read_bytes()                                   # a seeded run never touches the network
    elif mode != "live":
        raise SystemExit("--mode must be live or seeded")

    st_path = state.path_for(root, mode)
    st = state.load(st_path)
    baseline = state.is_baseline(st)
    if st is None:
        st = {"seen_ids": [], "baseline_run_id": None, "runs": []}
    run_rec = {"run_id": new_run_id(root), "run_mode": mode, "seeded_from": seeded_from if mode == "seeded" else None,
               "started_at": _now(), "completed_at": None}
    st["runs"].append(run_rec)
    state.save(st_path, st)

    run_dir = root / "raw" / run_rec["run_id"]
    run_dir.mkdir(parents=True)
    if mode == "live":
        body, meta = fetch.fetch_board()
    else:
        meta = {"seeded_from": seeded_from, "copied_at": _now(), "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest()}
    (run_dir / "board.json").write_bytes(body)
    (run_dir / "source.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    jobs = sorted(json.loads(body)["jobs"], key=lambda j: int(j["id"]))
    ids = [int(j["id"]) for j in jobs]
    tag = (f"[SEEDED from {seeded_from}] run {run_rec['run_id']}" if mode == "seeded"
           else f"[live {config.BOARD_URL}] run {run_rec['run_id']}")

    new = []
    if baseline:
        st["baseline_run_id"] = run_rec["run_id"]
        log(f"{tag}: baseline, {len(ids)} postings recorded, 0 reported as new")
    else:
        seen = set(st["seen_ids"])
        new = [j for j in jobs if int(j["id"]) not in seen]
        log(f"{tag}: {len(ids)} postings on the board, {len(new)} new since the last run")
        boards = lines.BoardCache(root)
        for j in new:
            posting = {"id": int(j["id"]), "title": j["title"], "location": (j.get("location") or {}).get("name", "")}
            sentences = textprep.requirements_sentences(j.get("content"), cfg.cut_headings, cfg.drop_phrases)
            if not sentences:
                _append(root / "output" / "skipped.jsonl", {"posting_id": posting["id"], "run_id": run_rec["run_id"],
                        "reason": "requirements text is empty after text preparation"})
                log(f"  {posting['id']}  SKIPPED (empty requirements text)  {posting['title']}")
                continue
            rule_out = rule.judge(posting, sentences, persona, cfg.vocab)
            claude_out, failure = claude_judge.judge(cfg, persona, posting, textprep.requirements_text(sentences),
                                                     run_dir, root)
            line = lines.build(run_rec, cfg, posting, rule_out, claude_out)
            errors = lines.check(line, root, cfg, persona, boards)
            if errors:     # a bug, not a judgment: stop here so the run stays incomplete and is redone next time
                raise RuntimeError(f"write-time validator rejected the line for {posting['id']}: {errors}")
            _append(root / "output" / "verdicts.jsonl", line)
            if failure:
                _append(root / "output" / "claude_failures.jsonl",
                        {"posting_id": posting["id"], "run_id": run_rec["run_id"], **failure})
            log(f"  {posting['id']}  rule (record): {rule_out['rule_verdict']:12}  claude (judgment): "
                f"{claude_out['claude_verdict'] or claude_out['claude_status']:12}  {posting['title']}")

    st["seen_ids"] = sorted(set(st["seen_ids"]) | set(ids))
    run_rec["completed_at"] = _now()
    st["runs"][-1] = run_rec
    state.save(st_path, st)
    return {"run_id": run_rec["run_id"], "baseline": baseline, "postings": len(ids), "new": len(new)}
