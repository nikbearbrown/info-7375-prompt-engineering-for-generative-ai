"""Plumbing shared by the sampling report and the prompt experiment: load the run-1
postings, ask the judge once per fresh conversation, and keep every call on disk.

Each call is a separate `claude -p --no-session-persistence` process (or a separate API
request), so no call can see another call's conversation."""

import datetime as dt
import gzip
import json
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jobwatch import board, judge, rule, transports  # noqa: E402
from jobwatch.errors import JudgeError  # noqa: E402
from jobwatch.resume import validate_resume  # noqa: E402

SELECTION = ROOT / "experiments" / "selection.json"
HAND_LABELS = ROOT / "labels" / "hand_labels.csv"


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def selection():
    return json.loads(SELECTION.read_text(encoding="utf-8"))


def persona():
    return validate_resume(json.loads((ROOT / "persona" / "alex_morgan.json").read_text(encoding="utf-8")))


def baseline_postings():
    raw = gzip.decompress((ROOT / selection()["source_run"] / "raw_response.json.gz").read_bytes())
    return {p.id: p for p in board.parse_board(raw)}


def rule_verdicts(resume, postings, ids):
    return {i: rule.rule_verdict(resume, postings[i])["verdict"] for i in ids}


def git_state():
    def git(*args):
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True).stdout.strip()
    return {"head": git("rev-parse", "--short", "HEAD"), "dirty_paths": git("status", "--porcelain", "--", ".").splitlines()}


def one_call(resume, posting, prompt, send, index):
    record = {"posting_id": posting.id, "title": posting.title, "prompt": prompt, "call_index": index, "started_at": now()}
    try:
        out = judge.judge_posting(resume, judge.posting_input(posting), send, prompt=prompt)
        record.update(valid=True, verdict=out["verdict"], error=None, justification=out["justification"],
                      resume_evidence=out["resume_evidence"], posting_evidence=out["posting_evidence"],
                      call=out["call"], reply=out["raw_reply"])
    except JudgeError as error:
        reply = error.reply
        record.update(valid=False, verdict=None, error=str(error), justification=None, resume_evidence=None,
                      posting_evidence=None, call=getattr(reply, "meta", None), reply=None if reply is None else str(reply))
    record["finished_at"] = now()
    return record


def run_calls(jobs, *, judge_name, model, workers, out_path):
    """jobs: list of (posting, prompt, call_index). Appends one JSON line per call as it finishes."""
    send = transports.get(judge_name, model)
    resume = persona()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    records = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(one_call, resume, posting, prompt, send, index) for posting, prompt, index in jobs]
        for future in as_completed(futures):
            record = future.result()
            with lock, open(out_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            records.append(record)
            status = record["verdict"] if record["valid"] else f"REJECTED ({record['error']})"
            print(f"  {record['finished_at']} {record['posting_id']} {record['prompt']} #{record['call_index']}: {status}", flush=True)
    return records


def read_calls(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
