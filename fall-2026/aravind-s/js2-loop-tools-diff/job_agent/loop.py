"""The loop (GATE.md): one run visits each board on the list once, in the listed order, under fixed budgets.

The order of a run:
1. Check every input before anything is fetched: the résumé, the board list, the prompt, each
   board's state, and any write that needs --approve (moving layer 1's state/seen.json).
2. Create runs/<run id>/ and its trace.
3. For each board in order: check the budgets, check the request, GET it (one retry for a transient
   failure), save every answer that arrived, read it, and compare it with the board's state. A
   board that fails is unverified: its state stays as it was and no value is filled in for it.
4. Judge: the rule judges every new posting; Claude judges postings still waiting from earlier runs
   first, then the new ones, until its budget runs out.
5. Write the report, then the state of each board that was read, then trace.md.
The exit follows from what happened (GATE.md, Exits).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import CONTRACT_VERSION, board_state, evidence, fetch, gate, loop_report, policy, providers
from . import resume as resume_mod
from .errors import BoardNoAnswer, BrokenInput, Redirected, Refused, Unverified
from .trace import Trace


class BudgetStop(Exception):
    """A budget ran out (GATE.md, Budgets). Not an error: the run goes on to its report."""

    def __init__(self, budget: str, message: str):
        super().__init__(message)
        self.budget = budget


@dataclass
class Board:
    system: str
    name: str
    url: str
    company: str = ""
    deliberate_failure: bool = False
    status: str = "not visited"  # read | unverified | not visited
    reason: str = ""
    attempts: list = field(default_factory=list)
    postings: list = None
    previous: dict = None  # the board's state before this run (layer 1's, converted, for OpenAI)
    on_disk: dict = None  # what is in this board's own state file, or None when there is none
    diff: board_state.Diff = None
    state_path: Path = None
    waiting_found: list = field(default_factory=list)  # postings that waited for Claude and are still listed
    waiting_gone: list = field(default_factory=list)  # ids that waited for Claude and are gone
    still_waiting: list = field(default_factory=list)  # ids that wait for Claude after this run

    @property
    def key(self) -> str:
        return f"{self.system}-{self.name}"


class Ledger:
    """The request budget and the repeat rule (GATE.md), both checked before a request is sent."""

    def __init__(self, limit: int):
        self.limit, self.used, self.sent = limit, 0, {}

    def send(self, get, url: str, retry: bool, announce):
        times = self.sent.get(("GET", url), 0)
        if times and not (retry and times == 1):
            raise Refused(f"refused: GET {url} was already sent in this run (GATE.md, Repeat rule)")
        if self.used >= self.limit:
            raise BudgetStop("requests", f"the request budget of {self.limit} was used up")
        self.used += 1
        self.sent[("GET", url)] = times + 1
        announce(self.used)
        return get(url, gate.REQUEST_TIMEOUT)


def run(*, boards_path, resume_path, state_root, runs_root, files: policy.Files, judges, budgets=None,
        approve=None, replay=None, get=fetch.get_board, now=None, monotonic=time.monotonic, sleep=time.sleep,
        say=print) -> dict:
    budgets = budgets or gate.Budgets()
    now = now or (lambda: datetime.now(timezone.utc))
    clock_start = monotonic()

    # 1. Inputs, before anything is fetched.
    resume = resume_mod.load(files.check_read(resume_path))
    boards, repeats, over = read_board_list(files.check_read(boards_path), budgets)
    files.check_read(judges.prompt)
    js1_path = Path(state_root) / board_state.JS1_FILE
    moving_js1 = False
    for board in boards + over:
        board.state_path = files.check_read(board_state.path_for(state_root, board.system, board.name))
        board.on_disk = board_state.load(board.state_path, board.system, board.name)
        board.previous = board.on_disk
        if (board.system, board.name) == board_state.JS1_BOARD and files.check_read(js1_path).exists() \
                and board in boards:
            if board.on_disk is not None:
                raise BrokenInput("there are two states for ashby/openai: state/seen.json (layer 1) and "
                                  f"{files.shown(board.state_path)}")
            board.previous = board_state.load_js1(js1_path)
            files.check_state_delete(js1_path, approve)  # NeedsApproval here, before anything is fetched
            moving_js1 = True
    if replay is not None:
        get = ReplayGet(files.check_read(replay), files)

    # 2. The run folder and its trace.
    started = now()
    run_id = evidence.run_id_for(started)
    run_dir = files.check_write(Path(runs_root) / run_id)
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        raise Refused(f"refused: {files.shown(run_dir)} already exists, and a saved run is never overwritten") from None
    trace = Trace(files.check_write(run_dir / "trace.jsonl"), now)
    source = "live" if replay is None else f"replay of the saved answers in {files.shown(replay)}, not a live run"
    context = {"run_id": run_id, "started_at": _iso(started), "source": source, "run_dir": run_dir,
               "budgets": budgets, "approve": approve, "moving_js1": moving_js1, "js1_path": js1_path}
    trace.add("run_start", run_id=run_id, source=source, gate_version=gate.GATE_VERSION,
              contract_version=CONTRACT_VERSION, budgets=budgets.as_dict(), resume=Path(resume_path).name,
              code_sha256=evidence.code_fingerprint(), git_head=evidence.git_head(),
              prompt=judges.describe())
    try:
        return _run(context, trace, files, boards, repeats, over, resume, judges, get, now, monotonic,
                    clock_start, sleep, say)
    except Exception as exc:
        code = gate.REFUSED_CODE if isinstance(exc, Refused) else gate.BROKEN_INPUT_CODE
        trace.add("exit", status=gate.ERROR, code=code, reason=str(exc), state="no state was changed")
        files.check_write(run_dir / "error.txt").write_text(
            f"The run stopped with an error and no state was changed: {exc}\n", encoding="utf-8")
        _write_trace_md(files, run_dir, trace, run_id)
        raise


def _run(context, trace, files, boards, repeats, over, resume, judges, get, now, monotonic, clock_start, sleep, say):
    budgets, run_dir, approve = context["budgets"], context["run_dir"], context["approve"]
    elapsed = lambda: monotonic() - clock_start  # noqa: E731
    stops = []
    trace.add("board_list", visiting=[b.key for b in boards], repeats=[b.key for b in repeats],
              not_visited_boards_budget=[b.key for b in over],
              deliberate_failure=[b.key for b in boards if b.deliberate_failure])
    if over:
        stops.append(f"boards budget: {len(boards) + len(over)} boards listed, {budgets.boards} allowed; "
                     f"not visited: {', '.join(b.key for b in over)}")
        trace.add("budget_stop", budget="boards", not_visited=[b.key for b in over])
    if approve:
        trace.add("approval", reason=approve, given_on_the_command_line=True,
                  needed_for=("moving state/seen.json (layer 1) into state/ashby-openai.json, then deleting it"
                              if context["moving_js1"] else "nothing in this run"))

    # 3. The boards, in order.
    ledger = Ledger(budgets.requests)
    stopped = None
    for board in boards:
        if stopped:
            board.reason = f"not visited: {stopped}"
            continue
        try:
            _visit(board, files, run_dir, ledger, get, trace, budgets, elapsed, sleep, monotonic, context["source"])
        except BudgetStop as stop:
            stopped = str(stop)
            board.reason = f"not visited: {stop}" if not board.attempts else f"stopped: {stop}"
            if board.attempts:
                board.status = "unverified"
            stops.append(f"{stop.budget} budget: {stop}")
            trace.add("budget_stop", budget=stop.budget, board=board.key, why=str(stop))
        if board.status == "read":
            board.diff = board_state.diff(board.previous, board.postings)
            trace.add("diff", board=board.key, baseline=board.diff.baseline, new=len(board.diff.new),
                      gone=len(board.diff.gone))

    # 4. Judging.
    verdicts = _judge(boards, resume, judges, run_dir, files, trace, budgets, elapsed, stops)

    # The exit, the report, then the states.
    status = exit_status(boards, stops)
    reasons = stops + [f"{b.key} unverified: {b.reason}" for b in boards if b.status == "unverified"]
    summary = loop_report.summary(context, boards, repeats, over, verdicts, status, reasons, ledger.used,
                                  sum(1 for v in verdicts.values() if "claude" in v), round(elapsed(), 1))
    loop_report.write(files, run_dir, summary)
    trace.add("report", files=["report.md", "report.json"], exit=status, reasons=reasons)
    for line in loop_report.screen_lines(summary):
        say(line)
    _save_states(boards, files, trace, approve, context)
    trace.add("exit", status=status, code=gate.EXIT_CODES[status], reasons=reasons)
    _write_trace_md(files, run_dir, trace, context["run_id"])
    return summary


def exit_status(boards, stops) -> str:
    """GATE.md, Exits: error is raised, never returned; then budget-exhausted, incomplete, finished."""
    if stops:
        return gate.BUDGET_EXHAUSTED
    if any(b.status == "unverified" for b in boards):
        return gate.INCOMPLETE
    return gate.FINISHED


def _visit(board, files, run_dir, ledger, get, trace, budgets, elapsed, sleep, monotonic, source):
    try:
        checked = policy.check_request("GET", board.url)
    except Refused as exc:
        trace.add("permission", board=board.key, url=board.url, allowed=False, why=str(exc))
        raise
    trace.add("permission", board=board.key, url=checked, allowed=True)
    folder = files.check_write(run_dir / "boards" / board.key)
    folder.mkdir(parents=True, exist_ok=True)
    attempt = 0
    while True:
        attempt += 1
        retry = attempt > 1
        if elapsed() >= budgets.seconds:
            raise BudgetStop("seconds", f"the {budgets.seconds}-second budget was used up")
        announce = lambda used: trace.add("request", board=board.key, attempt=attempt, retry=retry,  # noqa: E731
                                          method="GET", url=checked, requests_used=used)
        began = monotonic()
        try:
            response = ledger.send(get, checked, retry, announce)
        except BoardNoAnswer as exc:
            board.attempts.append({"attempt": attempt, "retry": retry, "no_answer": str(exc),
                                   "transient": exc.transient, "seconds": round(monotonic() - began, 2)})
            trace.add("no_answer", board=board.key, attempt=attempt, why=str(exc), transient=exc.transient)
            if exc.transient and not retry:
                _wait_for_retry(board, trace, budgets, elapsed, ledger, sleep, "a transient failure")
                continue
            return _unverified(board, trace, str(exc) + ("" if not retry else " (after one retry)"))
        except Redirected as exc:
            board.attempts.append({"attempt": attempt, "retry": retry, "no_answer": str(exc), "transient": False,
                                   "seconds": round(monotonic() - began, 2)})
            trace.add("no_answer", board=board.key, attempt=attempt, why=str(exc), transient=False)
            return _unverified(board, trace, str(exc))
        saved = _save_answer(files, folder, attempt, retry, response, source)
        board.attempts.append({"attempt": attempt, "retry": retry, "status": response.status,
                               "bytes": len(response.body), "sha256": saved["sha256"], "file": saved["file"],
                               "seconds": round(monotonic() - began, 2)})
        trace.add("answer", board=board.key, attempt=attempt, status=response.status, bytes=len(response.body),
                  sha256=saved["sha256"], file=files.shown(folder / saved["file"]),
                  seconds=round(monotonic() - began, 2))
        if response.status == 429 or 500 <= response.status <= 599:
            if not retry:
                _wait_for_retry(board, trace, budgets, elapsed, ledger, sleep, f"HTTP {response.status}")
                continue
            return _unverified(board, trace, f"the board answered HTTP {response.status} twice")
        try:
            board.postings = providers.read(board.system, response.status, response.body)
        except Unverified as exc:
            trace.add("decision", board=board.key, action="no retry",
                      why=f"{exc}; a retry cannot fix this answer (GATE.md, Error policy)")
            return _unverified(board, trace, str(exc))
        board.status = "read"
        trace.add("parse", board=board.key, postings=len(board.postings), mapped_from=board.system)
        return None


def _wait_for_retry(board, trace, budgets, elapsed, ledger, sleep, what):
    if ledger.used >= ledger.limit:
        raise BudgetStop("requests", f"the request budget of {ledger.limit} was used up before the retry")
    if elapsed() + gate.RETRY_WAIT >= budgets.seconds:
        raise BudgetStop("seconds", f"the {budgets.seconds}-second budget would run out before the retry")
    trace.add("decision", board=board.key, action="retry once",
              why=f"{what}: a GET changes nothing on the server, and this kind of failure often clears; "
                  f"waiting {gate.RETRY_WAIT} s (GATE.md, Error policy)")
    sleep(gate.RETRY_WAIT)


def _unverified(board, trace, why):
    board.status, board.reason = "unverified", why
    trace.add("decision", board=board.key, action="unverified",
              why=f"{why}. Its state stays as it was, nothing counts as new or gone, and it is escalated to you")
    return None


def _save_answer(files, folder, attempt, retry, response, source) -> dict:
    """Every answer that arrived, byte for byte (gzip-compressed), with its SHA-256 and where it came from."""
    name = f"attempt-{attempt}.json.gz"
    digest = hashlib.sha256(response.body).hexdigest()
    files.check_write(folder / name).write_bytes(gzip.compress(response.body, mtime=0))
    meta = {"url": response.url, "status": response.status, "received_at": response.received_at,
            "bytes": len(response.body), "sha256": digest, "headers": response.headers, "retry": retry,
            "source": source, "body_file": name, "note": "the SHA-256 is of the uncompressed answer"}
    files.check_write(folder / f"attempt-{attempt}.meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"file": name, "sha256": digest}


def _judge(boards, resume, judges, run_dir, files, trace, budgets, elapsed, stops) -> dict:
    """Both verdicts per posting, keyed by (board key, posting id). Claude only within its budget."""
    queue = []
    for board in boards:
        if board.status != "read":
            continue
        index = {p["id"]: p for p in board.postings}
        waiting = (board.previous or {}).get("pending_claude") or []
        board.waiting_found = [index[i] for i in waiting if i in index]
        board.waiting_gone = [i for i in waiting if i not in index]
        queue += [(board, p, "waited") for p in board.waiting_found]
    for board in boards:
        if board.status == "read":
            queue += [(board, p, "new") for p in board.diff.new]
    verdicts = {}
    for board, posting, why in queue:
        verdicts[(board.key, posting["id"])] = {"rule": judges.rule_verdict(posting, resume), "why": why}
    if queue:
        trace.add("judge_rule", postings=len(queue), relevant=sum(
            1 for v in verdicts.values() if v["rule"]["verdict"] == "relevant"))
    claude_dir = files.check_write(run_dir / "claude")
    calls, made, stopped = 0, set(), None
    for board, posting, why in queue:
        key = (board.key, posting["id"])
        if stopped is None and calls >= budgets.claude_calls:
            stopped = BudgetStop("claude_calls", f"the budget of {budgets.claude_calls} Claude calls was used up")
        if stopped is None and elapsed() >= budgets.seconds:
            stopped = BudgetStop("seconds", f"the {budgets.seconds}-second budget was used up before Claude's turn")
        if stopped is not None:
            board.still_waiting.append(posting["id"])
            continue
        call = (key, judges.describe()["sha256"], judges.model)
        if call in made:  # GATE.md, Repeat rule: the same Claude call is never made twice in a run
            continue
        made.add(call)
        verdict = judges.claude_verdict(posting, resume, claude_dir)
        calls += 1
        verdicts[key]["claude"] = verdict
        trace.add("claude_call", board=board.key, posting_id=posting["id"], why=why, valid=verdict.get("valid"),
                  verdict=verdict.get("verdict"), record=verdict.get("record"), calls_used=calls)
    if stopped is not None:
        waiting = sum(len(b.still_waiting) for b in boards)
        stops.append(f"{stopped.budget} budget: {stopped} ({waiting} postings wait for Claude's judgment)")
        trace.add("budget_stop", budget=stopped.budget, why=str(stopped), waiting_for_claude=waiting)
    return verdicts


def _save_states(boards, files, trace, approve, context):
    for board in boards:
        if board.status != "read":
            trace.add("state_write", board=board.key, path=files.shown(board.state_path), write="none",
                      why=f"the board was {board.status}, so its state stays exactly as it was")
            continue
        run = {"run_id": context["run_id"], "started_at": context["started_at"], "postings": len(board.postings),
               "new": len(board.diff.new), "gone": len(board.diff.gone),
               "answer_sha256": board.attempts[-1]["sha256"], "source": context["source"]}
        state = board_state.next_state(board.previous, board.system, board.name, board.url, board.postings, run,
                                       board.still_waiting)
        kind = files.check_state_write(board.state_path, board.on_disk, state, approve)
        files.check_write(board.state_path.with_name(board.state_path.name + ".tmp"))
        board_state.save(board.state_path, state)
        trace.add("state_write", board=board.key, path=files.shown(board.state_path), write=kind,
                  seen_ids=len(state["seen_ids"]), waiting_for_claude=len(state["pending_claude"]))
        if context["moving_js1"] and (board.system, board.name) == board_state.JS1_BOARD:
            js1 = context["js1_path"]
            kind = files.check_state_delete(js1, approve)
            os.remove(js1)
            trace.add("state_write", board=board.key, path=files.shown(js1), write=f"deleted ({kind})",
                      why="layer 1's state now lives in " + files.shown(board.state_path), approval=approve)


def read_board_list(path: Path, budgets) -> tuple:
    """(boards to visit, repeats skipped, boards over the boards budget). Broken input refuses the whole list."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise BrokenInput(f"the board list {Path(path).name} is unreadable ({type(exc).__name__})") from None
    entries = data.get("boards") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        raise BrokenInput(f"the board list {Path(path).name} has no boards")
    unique, repeats, seen = [], [], set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise BrokenInput(f"board {index} in the list is not an object")
        system, name = entry.get("system"), entry.get("name")
        url = providers.board_url(system, name)  # BrokenInput for an unknown system or a bad name
        if "url" in entry:
            raise BrokenInput(f"board {index} gives a URL; the list names a system and a board, never a URL")
        board = Board(system=system, name=name, url=url, company=str(entry.get("company") or ""),
                      deliberate_failure=entry.get("deliberate_failure") is True)
        key = (system, name.lower())
        if key in seen:
            repeats.append(board)
            continue
        seen.add(key)
        unique.append(board)
    return unique[: budgets.boards], repeats, unique[budgets.boards:]


class ReplayGet:
    """Hands out the answers saved in an earlier run folder, in order, instead of fetching (a labeled replay)."""

    def __init__(self, run_dir: Path, files: policy.Files):
        self.saved = {}
        for meta_path in sorted(Path(run_dir).glob("boards/*/attempt-*.meta.json"),
                                key=lambda p: (p.parent.name, int(p.name.split("-")[1].split(".")[0]))):
            meta = json.loads(files.check_read(meta_path).read_text(encoding="utf-8"))
            body = gzip.decompress(files.check_read(meta_path.parent / meta["body_file"]).read_bytes())
            self.saved.setdefault(meta["url"], []).append(
                fetch.Response(url=meta["url"], status=meta["status"], headers=meta.get("headers") or {},
                               body=body, received_at=meta.get("received_at") or ""))

    def __call__(self, url, timeout=None):
        answers = self.saved.get(url) or []
        if not answers:
            raise BoardNoAnswer("no saved answer for this request in the replayed run", transient=False)
        return answers.pop(0)


def _write_trace_md(files, run_dir, trace, run_id):
    files.check_write(run_dir / "trace.md").write_text(trace.markdown(f"Trace of run {run_id}"), encoding="utf-8")


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
