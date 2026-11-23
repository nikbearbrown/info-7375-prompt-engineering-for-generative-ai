"""One run of the watch (CONTRACT.md, In, Out and Refuses 6).

The order is the contract's: validate the résumé and read the state before anything else, fetch,
save the raw response, compare with the state, judge what is new, write the report, and only then
save the new state. A run that stops anywhere before the last step leaves the state as it was.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import CONTRACT_VERSION, board, evidence, fetch, report
from . import resume as resume_mod
from . import state as state_mod
from .allowlist import BOARD_URL
from .errors import BrokenInput, NoAnswer

REPO = Path(__file__).resolve().parent.parent


def run(*, resume_path: Path, state_path: Path, runs_root: Path, judge=None, replay: Path = None,
        get=fetch.get, now=None, say=print) -> dict:
    resume = resume_mod.load(resume_path)  # Refused: nothing has run yet
    previous = state_mod.load(state_path)  # None: this run is the baseline
    if previous is not None and judge is None:
        raise BrokenInput("this run would need to judge new postings, and no judge was given")
    started = now() if now else datetime.now(timezone.utc)
    run_id = evidence.run_id_for(started)
    if replay is None:
        try:
            response, source = get(BOARD_URL), "live fetch"
        except OSError as exc:
            raise NoAnswer(f"no answer from the board ({type(exc).__name__}: {exc})") from None
    else:
        response, source = _replayed(Path(replay)), f"replay of a saved response ({_shown_path(replay)}), not a live run"
    run_dir = evidence.new_run_dir(runs_root, run_id)
    digest = evidence.save_response(run_dir, response, source)  # kept even when the answer is broken
    try:
        return _finish(run_dir, run_id, started, source, digest, response, resume, previous,
                       state_path, resume_path, judge, say)
    except Exception as exc:
        (run_dir / "error.txt").write_text(f"The run stopped and the state was not changed: {exc}\n", encoding="utf-8")
        raise


def _finish(run_dir, run_id, started, source, digest, response, resume, previous, state_path, resume_path, judge, say):
    jobs = board.parse(response.status, response.body)
    postings = len({job["id"] for job in jobs})
    record = {
        "run_id": run_id,
        "started_at": started.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "response_sha256": digest,
        "postings": postings,
        "source": source,
        "code_sha256": evidence.code_fingerprint(),
        "git_head": evidence.git_head(),
    }
    found = state_mod.diff(previous, jobs)
    record.update(new=len(found.new), gone=len(found.gone))
    verdicts = {job["id"]: judge(job, resume, run_dir) for job in found.new}
    c = report.counts(found, verdicts)
    line = report.counts_line(run_id, postings, c, found.baseline)
    summary = {
        "run_id": run_id,
        "started_at": record["started_at"],
        "source": source,
        "board_url": BOARD_URL,
        "response_sha256": digest,
        "response_bytes": len(response.body),
        "resume": Path(resume_path).name,
        "contract_version": CONTRACT_VERSION,
        "code_sha256": record["code_sha256"],
        "git_head": record["git_head"],
        "baseline": found.baseline,
        "postings": postings,
        "counts": c,
        "counts_line": line,
    }
    report.write(run_dir, summary, found, verdicts)
    say(line)  # before the state is saved, so that a screen that fails cannot leave a saved state behind an error
    for text in report.screen_lines(found, verdicts):
        say(text)
    state_mod.save(state_path, state_mod.next_state(previous, jobs, record))  # the last step of a run
    return summary


def _shown_path(path) -> str:
    """A path as the evidence names it: relative to the repo when inside it, else only its file name."""
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(REPO))
    except ValueError:
        return resolved.name


def _replayed(path: Path) -> fetch.Response:
    """A saved response, read back for a labeled replay (the brief's "seeded" second run)."""
    body = path.read_bytes()
    received = ""
    meta = path.with_name("response.meta.json")
    if meta.exists():
        received = json.loads(meta.read_text(encoding="utf-8")).get("received_at", "")
    return fetch.Response(url=BOARD_URL, status=200, headers={}, body=body, received_at=received)
