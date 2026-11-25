"""JS3 step 2.2: source-grounded claims for each keep (FILTER.md "Evidence rules").

CLI (run from js3-filter-tool-score/):
    python -m agent.claims run --live          # LIVE Claude API calls on every v0.2 keep
    python -m agent.claims sheet               # blind claim sheet from evidence/claims/claims-v1.jsonl

`run` is a real, billed API call and refuses to start without --live. ANTHROPIC_API_KEY is
read from the environment only and is never printed or saved. The base URL is pinned to
https://api.anthropic.com (ANTHROPIC_BASE_URL is ignored), as in JS1.

For one posting Claude returns ONLY a JSON object (prompts/claims-v1.txt). The reply is
validated strictly (schema, enums, 3–6 claims, the four required kinds, empty quote ⇒
insufficient). Every non-empty quote must be an exact substring of the normalized posting
text; a quote that is not is flagged quote_not_found and is never silently accepted. An
invalid reply gets one retry with the same request, then the posting is recorded as failed.
"""

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from . import PROJECT_DIR
from . import filter as flt
from .postings import load_run

PROMPT_PATH = PROJECT_DIR / "prompts" / "claims-v1.txt"
# Inherited from JS1: ../js1-contract-and-watch/config.json "model" and "max_tokens".
MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 16000
BASE_URL = "https://api.anthropic.com"
# USD per million tokens for claude-sonnet-5-5 (claude-api skill model table, cached 2026-11-03).
PRICE_INPUT_PER_MTOK = 2.00
PRICE_OUTPUT_PER_MTOK = 10.00

RUN = PROJECT_DIR / "evidence" / "runs" / "live-text-1"
OUT_DIR = PROJECT_DIR / "evidence" / "claims"
RULES_MODE = "v0.2"
LIVE_LABEL = "REAL Claude API output (live call), not a fixture"

KINDS = ("role", "seniority", "location", "experience", "sponsorship", "skill")
REQUIRED_KINDS = ("role", "location", "experience", "sponsorship")
LABELS = ("supported", "contradicted", "insufficient")
MIN_CLAIMS, MAX_CLAIMS = 3, 6
MAX_ATTEMPTS = 2  # one try plus one retry

CLAIM_KEYS = ("kind", "claim", "quote", "proposed_label")
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "posting_id": {"type": "string"},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": list(KINDS)},
                    "claim": {"type": "string"},
                    "quote": {"type": "string"},
                    "proposed_label": {"type": "string", "enum": list(LABELS)},
                },
                "required": list(CLAIM_KEYS),
                "additionalProperties": False,
            },
        },
    },
    "required": ["posting_id", "claims"],
    "additionalProperties": False,
}

SHEET_COLUMNS = ("row", "posting_id", "title", "kind", "claim", "quote", "quote_found", "my_label", "note")
TEXT_DIR = "claims-texts"
TEXT_MARKER = "--- posting text ---"


class ClaimsValidationError(Exception):
    """The reply breaks the prompt contract."""


# ---------------------------------------------------------------- prompt and request

def load_prompt(path: Path = PROMPT_PATH) -> tuple[str, str]:
    data = Path(path).read_bytes()
    return data.decode("utf-8"), hashlib.sha256(data).hexdigest()


def build_request(posting: dict, persona: dict, system_prompt: str) -> dict:
    """Keyword arguments for messages.create. Contains no credentials."""
    payload = {
        "posting_id": str(posting["id"]),
        "title": posting.get("title"),
        "locations": posting.get("locations"),
        "posting_text": posting["text"],
        "cole": {k: persona[k] for k in ("target_titles", "years_experience", "needs_sponsorship",
                                         "work_country", "skills")},
    }
    return {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)}],
        "output_config": {"format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
    }


# ---------------------------------------------------------------- validation

def validate_reply(text, posting_id: str) -> dict:
    """The parsed reply if it keeps the contract; otherwise ClaimsValidationError."""
    if not isinstance(text, str) or not text.strip():
        raise ClaimsValidationError("no text in the reply")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise ClaimsValidationError(f"reply is not only JSON: {err.msg}") from None
    if not isinstance(data, dict):
        raise ClaimsValidationError("reply is not a JSON object")
    if set(data) != {"posting_id", "claims"}:
        raise ClaimsValidationError(f"top-level keys must be posting_id and claims, got {sorted(data)}")
    if not isinstance(data["posting_id"], str):
        raise ClaimsValidationError("posting_id is not a string")
    if data["posting_id"] != posting_id:
        raise ClaimsValidationError(f"posting_id {data['posting_id']!r} is not {posting_id!r}")
    claims = data["claims"]
    if not isinstance(claims, list):
        raise ClaimsValidationError("claims is not a list")
    if not MIN_CLAIMS <= len(claims) <= MAX_CLAIMS:
        raise ClaimsValidationError(f"{len(claims)} claims; must be {MIN_CLAIMS} to {MAX_CLAIMS}")
    for i, c in enumerate(claims):
        if not isinstance(c, dict):
            raise ClaimsValidationError(f"claim {i} is not an object")
        if set(c) != set(CLAIM_KEYS):
            raise ClaimsValidationError(f"claim {i} keys must be {list(CLAIM_KEYS)}, got {sorted(c)}")
        if c["kind"] not in KINDS:
            raise ClaimsValidationError(f"claim {i} kind {c['kind']!r} is not one of {list(KINDS)}")
        if c["proposed_label"] not in LABELS:
            raise ClaimsValidationError(f"claim {i} proposed_label {c['proposed_label']!r} is not one of {list(LABELS)}")
        if not isinstance(c["claim"], str) or not c["claim"].strip():
            raise ClaimsValidationError(f"claim {i} has an empty claim")
        if not isinstance(c["quote"], str):
            raise ClaimsValidationError(f"claim {i} quote is not a string")
        if c["quote"] == "" and c["proposed_label"] != "insufficient":
            raise ClaimsValidationError(f"claim {i} has an empty quote but label {c['proposed_label']!r}")
    missing = [k for k in REQUIRED_KINDS if not any(c["kind"] == k for c in claims)]
    if missing:
        raise ClaimsValidationError(f"no claim of kind {missing}")
    return data


def check_quotes(claims: list[dict], posting_text: str) -> list[dict]:
    """Each claim plus quote_found (True/False, None for an empty quote) and its flags."""
    out = []
    for c in claims:
        if c["quote"] == "":
            out.append({**c, "quote_found": None, "flags": []})
        elif c["quote"] in posting_text:
            out.append({**c, "quote_found": True, "flags": []})
        else:
            out.append({**c, "quote_found": False, "flags": ["quote_not_found"]})
    return out


# ---------------------------------------------------------------- the live run

def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _slug(posting: dict) -> str:
    return f"{posting['board'].replace('/', '-')}-{posting['id']}"


def _usage(response) -> dict:
    u = getattr(response, "usage", None)
    keys = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    return {k: (getattr(u, k, None) or 0) for k in keys}


def _dump(response) -> dict:
    return response.model_dump(mode="json") if hasattr(response, "model_dump") else {"repr": repr(response)}


def ask_once(client, request: dict, posting: dict, attempt: int, raw_dir: Path, meta: dict, now=_now) -> dict:
    """One API call: save the raw request and response, validate, check quotes."""
    slug, pid = _slug(posting), str(posting["id"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    sent_at = now()
    (raw_dir / f"{slug}-attempt{attempt}-request.json").write_text(
        json.dumps({**meta, "sent_at": sent_at, "request": request}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    result = {"attempt": attempt, "sent_at": sent_at, "usage": dict.fromkeys(
        ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"), 0)}
    try:
        response = client.messages.create(**request)
    except Exception as err:  # any API or network failure: nothing to validate
        status = getattr(err, "status_code", None)
        reason = f"API call failed: {type(err).__name__}" + (f" (HTTP {status})" if status else "")
        (raw_dir / f"{slug}-attempt{attempt}-response.json").write_text(
            json.dumps({"received_at": now(), "error": reason}, indent=2) + "\n", encoding="utf-8")
        if status == 401:
            raise RuntimeError("Claude API rejected the API key (HTTP 401); run stopped") from None
        return {**result, "ok": False, "reason": reason}
    received_at = now()
    (raw_dir / f"{slug}-attempt{attempt}-response.json").write_text(
        json.dumps({"received_at": received_at, "response": _dump(response)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    result.update(received_at=received_at, usage=_usage(response), model=getattr(response, "model", None),
                  stop_reason=getattr(response, "stop_reason", None))
    if result["stop_reason"] in ("refusal", "max_tokens"):
        return {**result, "ok": False, "reason": f"stop_reason {result['stop_reason']}"}
    text = "".join(b.text for b in (response.content or []) if getattr(b, "type", None) == "text")
    try:
        data = validate_reply(text, pid)
    except ClaimsValidationError as err:
        return {**result, "ok": False, "reason": str(err)}
    return {**result, "ok": True, "claims": check_quotes(data["claims"], posting["text"])}


def claims_for(client, posting: dict, persona: dict, prompt: str, raw_dir: Path, meta: dict, now=_now) -> dict:
    """Up to MAX_ATTEMPTS calls with the same request; the record for claims-v1.jsonl."""
    request = build_request(posting, persona, prompt)
    attempts = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        res = ask_once(client, request, posting, attempt, raw_dir, meta, now)
        attempts.append({k: v for k, v in res.items() if k != "claims"})
        if res["ok"]:
            break
    last = attempts[-1]
    usage = {k: sum(a["usage"][k] for a in attempts) for k in attempts[0]["usage"]}
    record = {"board": posting["board"], "posting_id": str(posting["id"]), "title": posting["title"],
              "status": "ok" if last["ok"] else "failed", "attempts": attempts, "usage": usage,
              "model": last.get("model"), **meta}
    if last["ok"]:
        record["claims"] = res["claims"]
    else:
        record["failure"] = last["reason"]
    return record


def cost_usd(usage: dict) -> float:
    inp = usage["input_tokens"] + usage["cache_creation_input_tokens"] * 1.25 + usage["cache_read_input_tokens"] * 0.1
    return inp * PRICE_INPUT_PER_MTOK / 1e6 + usage["output_tokens"] * PRICE_OUTPUT_PER_MTOK / 1e6


def keeps(run_dir: Path = RUN, mode: str = RULES_MODE) -> tuple[list[dict], dict]:
    postings, failures = load_run(run_dir, with_blocks=True)
    if failures:
        raise RuntimeError(f"board failures in {run_dir}: {failures}")
    persona = flt.load_persona(flt.DEFAULT_PERSONA)
    rules = flt.RULE_MODES[mode]
    return [p for p in postings if flt.evaluate(p, persona, rules)["verdict"] == "keep"], persona


def make_client():
    """Anthropic client with the key from ANTHROPIC_API_KEY and the base URL pinned."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set in the environment")
    import anthropic  # imported only for the live run

    return anthropic.Anthropic(api_key=key, base_url=BASE_URL)


def run(client, out_dir: Path = OUT_DIR, run_dir: Path = RUN, now=_now) -> dict:
    postings, persona = keeps(run_dir)
    prompt, sha = load_prompt()
    started = now()
    meta = {"label": LIVE_LABEL, "run_started": started, "prompt_file": "prompts/claims-v1.txt",
            "prompt_sha256": sha, "requested_model": MODEL, "rules_mode": RULES_MODE}
    records = [claims_for(client, p, persona, prompt, out_dir / "raw", meta, now) for p in postings]
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "claims-v1.jsonl", "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    usage = {k: sum(r["usage"][k] for r in records) for k in records[0]["usage"]} if records else {}
    claims = [c for r in records for c in r.get("claims", [])]
    summary = {
        **meta, "run_finished": now(), "postings": len(records),
        "ok": sum(r["status"] == "ok" for r in records), "failed": [r["posting_id"] for r in records if r["status"] != "ok"],
        "retried": [r["posting_id"] for r in records if len(r["attempts"]) > 1],
        "models_returned": sorted({a.get("model") for r in records for a in r["attempts"] if a.get("model")}),
        "claims": len(claims), "quote_not_found": sum(c["quote_found"] is False for c in claims),
        "empty_quotes": sum(c["quote_found"] is None for c in claims),
        "usage": usage, "estimated_cost_usd": round(cost_usd(usage), 4) if usage else 0.0,
        "pricing": f"${PRICE_INPUT_PER_MTOK}/MTok input, ${PRICE_OUTPUT_PER_MTOK}/MTok output "
                   "(claude-api skill model table, cached 2026-11-03); thinking tokens bill as output",
    }
    (out_dir / "run-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


# ---------------------------------------------------------------- blind claim sheet

def _quote_found_cell(value) -> str:
    return "empty" if value is None else ("yes" if value else "no")


def posting_text_file(posting: dict) -> str:
    """Header, marker, then one block per paragraph (blank line between), as the labeler reads it."""
    blocks = posting.get("blocks") or [posting["text"]]
    head = [f"posting_id: {posting['id']}", f"board: {posting['board']}", f"title: {posting['title']}",
            f"locations: {' | '.join(posting['locations'] or [])}", f"url: {posting.get('url')}", "", TEXT_MARKER, ""]
    return "\n".join(head) + "\n\n".join(blocks) + "\n"


def build_sheet(records: list[dict], postings: dict, root: Path = PROJECT_DIR,
                key_path: Path | None = None, force: bool = False) -> dict:
    """labels/claims-sheet.csv (no proposed_label) + labels/claims-texts/ + the key under out/."""
    sheet = root / "labels" / "claims-sheet.csv"
    key_path = key_path or root / "out" / "claims-key.json"
    if sheet.exists() and not force:
        raise FileExistsError(f"{sheet} exists; refusing to overwrite labels (use --force only before labeling)")
    texts = root / "labels" / TEXT_DIR
    texts.mkdir(parents=True, exist_ok=True)
    rows, key_rows = [], []
    for rec in records:
        if rec["status"] != "ok":
            continue
        p = postings[(rec["board"], rec["posting_id"])]
        (texts / f"{rec['posting_id']}.txt").write_text(posting_text_file(p), encoding="utf-8")
        for i, c in enumerate(rec["claims"]):
            n = len(rows) + 1
            rows.append([n, rec["posting_id"], rec["title"], c["kind"], c["claim"], c["quote"],
                         _quote_found_cell(c["quote_found"]), "", ""])
            key_rows.append({"row": n, "board": rec["board"], "posting_id": rec["posting_id"], "claim_index": i,
                             "proposed_label": c["proposed_label"], "flags": c["flags"]})
    sheet.parent.mkdir(parents=True, exist_ok=True)
    with open(sheet, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(SHEET_COLUMNS)
        writer.writerows(rows)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(json.dumps({"sheet_sha256": hashlib.sha256(sheet.read_bytes()).hexdigest(),
                                    "rows": key_rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"rows": len(rows), "postings": len({r[1] for r in rows}), "sheet": sheet, "key": key_path}


def load_records(path: Path = OUT_DIR / "claims-v1.jsonl") -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m agent.claims", description="JS3 claims (live Claude API).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="LIVE API calls on every v0.2 keep")
    r.add_argument("--live", action="store_true", help="required: confirms this is a real, billed API run")
    s = sub.add_parser("sheet", help="blind claim sheet from evidence/claims/claims-v1.jsonl")
    s.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd == "run":
        if not args.live:
            print("refusing: `run` makes real, billed Claude API calls; pass --live to confirm")
            return 2
        try:
            summary = run(make_client())
        except RuntimeError as err:
            print(f"error: {err}")
            return 2
        print(json.dumps({k: summary[k] for k in ("label", "requested_model", "models_returned", "prompt_sha256",
                                                  "postings", "ok", "failed", "retried", "claims", "quote_not_found",
                                                  "empty_quotes", "usage", "estimated_cost_usd")}, indent=2))
        return 0
    postings, _ = load_run(RUN, with_blocks=True)
    by_key = {(p["board"], str(p["id"])): p for p in postings}
    try:
        info = build_sheet(load_records(), by_key, force=args.force)
    except FileExistsError as err:
        print(f"error: {err}")
        return 2
    print(f"{info['rows']} claim rows from {info['postings']} postings -> {info['sheet']}")
    print(f"proposed-label key (do not open before labeling): {info['key']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
