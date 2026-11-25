"""Phase 2d: the dataset of one collection run (FILTER.md sections 1, 3 and 5).

    build(tools, run_dir) -> (lines, meta)
    python -m jobwatch dataset --run runs/<run-id>

Reads runs/<run-id>/summary.json and manifest.json and each OK board's raw body through
tools.read_file, parses the bytes with the same providers the loop used, and writes
    data/postings-<run-id>.jsonl       one line per posting
    data/postings-<run-id>.meta.json   the run, the boards (failed ones included), counts
through tools.write_file. Nothing is fetched.

A line holds: key ("<system>:<slug>:<posting id>"), board, posting_id, url, title and location
(each normalized as one field; location null when the field is missing), text (the joined
section 5 text fields), fields (each field's span in text), sentences (each sentence's field,
start, end and boilerplate flag) and raw_file.

Boilerplate (FILTER.md section 3): a normalized sentence of the posting text that appears in at
least 50% of one board's postings in this run. A posting counts once however often the sentence
appears in it. Title and location are not posting-body sentences and carry no flag.
"""
import json

from jobwatch import providers
from jobwatch.text import join_fields, normalize_single
from jobwatch.tools import FetchResult

BOILERPLATE_SHARE = 0.5  # FILTER.md section 3, hand-set


class DatasetError(Exception):
    pass


def _json(tools, path):
    return json.loads(tools.read_file(path).decode("utf-8"))


def posting_key(board, posting_id):
    return f"{board}:{posting_id}"


def build(tools, run_dir):
    run_dir = run_dir.rstrip("/")
    summary = _json(tools, f"{run_dir}/summary.json")
    manifest = _json(tools, f"{run_dir}/manifest.json")
    content_types = {m["path"]: m.get("content_type") for m in manifest.get("files", manifest)
                     if isinstance(m, dict) and "path" in m}
    lines, boards_meta = [], []
    for b in summary["boards"]:
        entry = {"board": b["key"], "status": b["status"], "http_status": b.get("http_status"),
                 "reason": b.get("reason"), "url": b.get("url")}
        boards_meta.append(entry)
        if b["status"] != "OK":
            continue
        raw_rel = b["raw_file"]
        body = tools.read_file(f"{run_dir}/{raw_rel}")
        result = FetchResult(b.get("url") or "", b.get("http_status"),
                             {"content-type": content_types.get(raw_rel)}, body)
        parsed = providers.get(b["system"]).parse(result, b["key"])
        if isinstance(parsed, providers.BoardError):
            raise DatasetError(f"{b['key']}: saved body no longer parses: {parsed.kind} {parsed.detail}")
        board_lines = []
        for p in parsed:
            text, sentences, spans = join_fields(p.text_fields)
            board_lines.append({
                "key": posting_key(b["key"], p.id), "board": b["key"], "posting_id": p.id, "url": p.url,
                "title": normalize_single(p.title), "location": normalize_single(p.location),
                "text": text, "fields": spans,
                "sentences": [{"field": s["field"], "start": s["start"], "end": s["end"]} for s in sentences],
                "raw_file": f"{run_dir}/{raw_rel}",
            })
        _flag_boilerplate(board_lines)
        entry["postings"] = len(board_lines)
        lines.extend(board_lines)
    keys = [ln["key"] for ln in lines]
    if len(set(keys)) != len(keys):
        raise DatasetError("duplicate posting keys in the run")
    lines.sort(key=lambda ln: (ln["board"], ln["posting_id"]))
    meta = {"run_id": summary["run_id"], "run_exit": summary["exit"], "run_exit_code": summary["exit_code"],
            "run_label": summary.get("label"), "boilerplate_share": BOILERPLATE_SHARE,
            "postings": len(lines), "boards": boards_meta,
            "failed_boards": [e["board"] for e in boards_meta if e["status"] != "OK"]}
    return lines, meta


def _flag_boilerplate(board_lines):
    """Mark each sentence that appears in >= 50% of this board's postings (FILTER.md section 3)."""
    n = len(board_lines)
    counts = {}
    for ln in board_lines:
        for s in {ln["text"][x["start"]:x["end"]] for x in ln["sentences"]}:
            counts[s] = counts.get(s, 0) + 1
    for ln in board_lines:
        for x in ln["sentences"]:
            x["boilerplate"] = n > 0 and counts[ln["text"][x["start"]:x["end"]]] >= BOILERPLATE_SHARE * n


def write(tools, lines, meta, out_dir="data"):
    run_id = meta["run_id"]
    body = "".join(json.dumps(ln, ensure_ascii=False, sort_keys=True) + "\n" for ln in lines)
    tools.write_file(f"{out_dir}/postings-{run_id}.jsonl", body.encode("utf-8"))
    tools.write_file(f"{out_dir}/postings-{run_id}.meta.json",
                     (json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return f"{out_dir}/postings-{run_id}.jsonl"


def load(tools, path):
    """Read a dataset .jsonl through tools.read_file."""
    return [json.loads(line) for line in tools.read_file(path).decode("utf-8").splitlines() if line.strip()]
