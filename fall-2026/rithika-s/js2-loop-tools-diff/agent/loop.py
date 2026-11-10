"""Job-Search Agent 2: the bounded loop, as specified in GATE.md.

    python3 -m agent.loop                 live run (network, allow-list only)
    python3 -m agent.loop --replay DIR    SEEDED run from saved responses
    python3 -m agent.loop --boards FILE   boards from FILE instead of
                                          config/boards.json (same checks)

Each step of the loop is observe -> decide -> act -> record, and the loop
stops on one of four exits (GATE section 1):

    finished 0 | incomplete 1 | budget_exhausted 2 | error 3

Budgets are checked before every request (section 2), the repeat rule is
applied before every request (section 3), and failures follow the error
policy (section 4). Every network call and file read/write goes through
agent/policy.py. No Claude calls are made (max_claude_calls is 0).

Outputs (only inside out/):
    out/runs/<run_id>/trace.jsonl         one line per loop event
    out/runs/<run_id>/summary.json        machine-readable result
    out/runs/<run_id>/report.md           "Needs your attention" first
    out/runs/<run_id>/replay.json         lets --replay serve this run again
    out/runs/<run_id>/state_before/       state files as they were at start
    out/raw/<run_id>_<board>_a<n>.json    response bodies, unchanged
    out/state/<board>.json                seen ids, for boards that succeeded

A run that ends in `error` writes nothing except its trace.
"""

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from agent import adapters, policy
from agent import resume as resume_mod
from agent import transport as transport_mod

FINISHED = "finished"
INCOMPLETE = "incomplete"
BUDGET_EXHAUSTED = "budget_exhausted"
ERROR = "error"
EXIT_CODES = {FINISHED: 0, INCOMPLETE: 1, BUDGET_EXHAUSTED: 2, ERROR: 3}

BUDGET_KEYS = ("max_boards", "max_requests", "max_run_seconds",
               "max_request_seconds", "max_claude_calls")
RETRY_DELAY_SECONDS = 2
MAX_ATTEMPTS = 2
MAX_REDIRECTS = 3
LIVE = "LIVE"
SEEDED = "SEEDED"
OWN_REPORT_NOTE = ("This is the agent's own report, not an independent "
                   "check.")

BOARDS_CONFIG = Path("config") / "boards.json"
BUDGETS_CONFIG = Path("config") / "budgets.json"
RESUME_PATH = Path("data") / "resume.example.json"
STATE_DIR = Path("out") / "state"
# A replayed run keeps its own state so a SEEDED run can never change what
# a later LIVE run treats as already seen.
SEEDED_STATE_DIR = Path("out") / "state" / "seeded"
RAW_DIR = Path("out") / "raw"
RUNS_DIR = Path("out") / "runs"

BOARD_NAME = re.compile(r"[a-z0-9][a-z0-9_-]*")
REQUEST_HEADERS = {"User-Agent": transport_mod.USER_AGENT,
                   "Accept": "application/json"}

RETRYABLE_KINDS = frozenset({"timeout", "connection", "server_error"})


class RunError(Exception):
    """The run cannot proceed safely; it stops with exit `error`."""

    def __init__(self, reason, detail=""):
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}" if detail else reason)


# --- small decision rules, kept separate so each can be tested -------------

def failed_board_new():
    """New-job count for a failed board: unknown (None), never 0."""
    return None


def is_retryable(outcome):
    """Timeout, connection error and 5xx get one retry; nothing else does."""
    return bool(outcome) and outcome.get("kind") in RETRYABLE_KINDS


def decide_exit(boards, budget_limit):
    """Pick the exit for a run that did not end in `error`."""
    if budget_limit:
        return BUDGET_EXHAUSTED
    if any(b["status"] != "ok" for b in boards):
        return INCOMPLETE
    return FINISHED


def dedupe(postings, on_duplicate):
    """Keep the first posting for each id; report every repeat."""
    seen, unique = set(), []
    for posting in postings:
        if posting["id"] in seen:
            on_duplicate(posting["id"])
            continue
        seen.add(posting["id"])
        unique.append(posting)
    return unique


def action_key(method, url):
    """Same action = same method + host + full URL (path and query)."""
    parts = urllib.parse.urlsplit(url)
    return (method, (parts.hostname or "").lower(),
            urllib.parse.urlunsplit(("", "", parts.path, parts.query, "")))


def utc_run_id(mode):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{SEEDED}" if mode == SEEDED else stamp


# --- trace ---------------------------------------------------------------

class Trace:
    """Append-only JSON-lines trace, one line per event."""

    def __init__(self, handle, run_id, mode, elapsed):
        self.handle = handle
        self.run_id = run_id
        self.mode = mode
        self.elapsed = elapsed
        self.seq = 0

    def write(self, kind, **fields):
        self.seq += 1
        line = {"seq": self.seq, "t": round(self.elapsed(), 3),
                "run_id": self.run_id, "mode": self.mode, "kind": kind}
        line.update(fields)
        self.handle.write(json.dumps(line, ensure_ascii=False) + "\n")
        self.handle.flush()

    def close(self):
        self.handle.close()


# --- the loop ------------------------------------------------------------

class Runner:
    """One run of the bounded loop."""

    def __init__(self, root=policy.ROOT, transport=None, replay_dir=None,
                 clock=time.monotonic, sleep=time.sleep, run_id=None,
                 mode=None, boards_file=BOARDS_CONFIG):
        self.root = Path(root)
        self.transport = transport
        self.replay_dir = replay_dir
        self.boards_file = Path(boards_file)
        self.mode = mode or (SEEDED if replay_dir is not None else LIVE)
        self.clock = clock
        self.sleep = sleep
        self.run_id = run_id or utc_run_id(self.mode)
        self.start = clock()
        self.run_dir = RUNS_DIR / self.run_id
        self.state_dir = SEEDED_STATE_DIR if self.mode == SEEDED else STATE_DIR
        self.trace = None
        self.budgets = {}
        self.boards = []
        self.contacts = []
        self.pending = []          # actions not yet taken, in order
        self.requests_sent = 0
        self.boards_started = set()
        self.sent = {}             # action key -> times sent
        self.last_outcome = {}     # action key -> last outcome
        self.budget_limit = None
        self.raw_buffer = []       # (path, bytes), written at the end
        self.replay_entries = {}   # url -> [manifest entries]
        self.exit = None
        self.error = None

    # -- helpers --

    def elapsed(self):
        return self.clock() - self.start

    def _rel(self, path):
        try:
            return str(Path(path).resolve().relative_to(
                self.root.resolve()))
        except ValueError:
            return str(path)

    def _read_json(self, path, what):
        try:
            return json.loads(policy.read_bytes(path, self.root))
        except FileNotFoundError:
            raise RunError(f"{what}_missing", str(path)) from None
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RunError(f"{what}_invalid",
                           f"{path}: {exc.__class__.__name__}") from None

    def _board(self, name):
        return next(b for b in self.boards if b["name"] == name)

    # -- startup --

    def _load_budgets(self):
        data = self._read_json(BUDGETS_CONFIG, "budgets")
        if not isinstance(data, dict) or set(data) != set(BUDGET_KEYS):
            raise RunError("budgets_invalid",
                           f"keys must be exactly {list(BUDGET_KEYS)}")
        for key in BUDGET_KEYS:
            value = data[key]
            if isinstance(value, bool) or not isinstance(value, int) \
                    or value < 0:
                raise RunError("budgets_invalid",
                               f"{key} must be a non-negative integer")
        self.budgets = data

    def _load_boards(self):
        # Read through the policy: outside data/, config/, out/ is refused.
        data = self._read_json(self.boards_file, "config")
        boards = data.get("boards") if isinstance(data, dict) else None
        if not isinstance(boards, list) or not boards:
            raise RunError("config_invalid",
                           "'boards' must be a non-empty list")
        if len(boards) > self.budgets["max_boards"]:
            raise RunError("config_too_many_boards",
                           f"{len(boards)} boards in config, max_boards is "
                           f"{self.budgets['max_boards']}")
        names, keys = set(), set()
        for entry in boards:
            if not isinstance(entry, dict):
                raise RunError("config_invalid",
                               "board entry is not an object")
            name, ats, url = (entry.get("name"), entry.get("ats"),
                              entry.get("url"))
            if not isinstance(name, str) or not BOARD_NAME.fullmatch(name):
                raise RunError("config_invalid", f"bad board name {name!r}")
            if ats not in adapters.PARSERS:
                raise RunError("config_invalid",
                               f"{name}: unknown ats {ats!r}")
            if not isinstance(url, str):
                raise RunError("config_invalid", f"{name}: url missing")
            policy.check_request("GET", url, REQUEST_HEADERS)
            key = action_key("GET", url)
            if name in names or key in keys:
                raise RunError("config_duplicate_board",
                               f"{name} appears twice in config")
            names.add(name)
            keys.add(key)
            self.boards.append({
                "name": name, "ats": ats, "url": url, "status": "not_tried",
                "http_status": None, "reason": None, "attempts": 0,
                "postings_seen": None, "duplicates": [], "new": None,
                "new_ids": None, "new_postings": [], "baseline": None,
                "previously_seen": None, "raw_files": [],
                "state_updated": False, "_ids": [], "_seen": None,
                "_state_bytes": None,
            })

    def _load_resume(self):
        try:
            data = json.loads(policy.read_bytes(RESUME_PATH, self.root))
            resume = resume_mod.validate_resume(data)
        except FileNotFoundError:
            raise RunError("resume_missing", str(RESUME_PATH)) from None
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise RunError("resume_invalid", "not valid JSON") from None
        except resume_mod.ResumeInvalid as exc:
            raise RunError("resume_invalid", str(exc)) from None
        self.contacts = resume_mod.contact_values(resume)

    def _load_states(self):
        for board in self.boards:
            path = self.state_dir / f"{board['name']}.json"
            resolved = policy.check_read(path, self.root)
            if not resolved.exists():
                continue
            raw = policy.read_bytes(path, self.root)
            try:
                data = json.loads(raw)
                ids = data["seen_ids"]
                if not isinstance(ids, list) or not all(
                        isinstance(i, str) for i in ids):
                    raise TypeError("seen_ids must be a list of strings")
                if data.get("board", board["name"]) != board["name"]:
                    raise ValueError("state belongs to another board")
            except (json.JSONDecodeError, UnicodeDecodeError, KeyError,
                    TypeError, ValueError, AttributeError) as exc:
                raise RunError("state_unreadable",
                               f"{path}: {exc.__class__.__name__}") from None
            board["_seen"] = set(ids)
            board["_state_bytes"] = raw

    def _startup(self):
        self._load_budgets()
        self._load_boards()
        self._load_resume()
        self._load_states()
        if self.replay_dir is not None:
            try:
                self.transport = transport_mod.ReplayTransport(
                    self.replay_dir,
                    {b["url"]: b["name"] for b in self.boards}, self.root)
            except (ValueError, AttributeError) as exc:  # bad replay.json
                raise RunError("replay_invalid",
                               f"{exc.__class__.__name__}") from None
        if self.transport is None:
            raise RunError("no_transport")
        self.trace.write("startup", boards_file=str(self.boards_file),
                         budgets=self.budgets,
                         boards=[b["name"] for b in self.boards],
                         state_dir=str(self.state_dir),
                         replay_dir=None if self.replay_dir is None
                         else str(self.replay_dir))
        self.pending = [{"board": b["name"], "url": b["url"], "attempt": 1,
                         "hop": 0, "retry": False} for b in self.boards]

    # -- observe / decide / act / record --

    def _observe(self):
        obs = {
            "next": dict(self.pending[0]) if self.pending else None,
            "pending": len(self.pending),
            "requests_sent": self.requests_sent,
            "boards_started": len(self.boards_started),
            "elapsed_seconds": round(self.elapsed(), 3),
            "claude_calls": 0,
        }
        self.trace.write("observation", **obs)
        return obs

    def _budget_block(self, action):
        """Return the budget a request would exceed, or None. Before acting."""
        b = self.budgets
        if action["board"] not in self.boards_started \
                and len(self.boards_started) >= b["max_boards"]:
            return "max_boards"
        if self.requests_sent >= b["max_requests"]:
            return "max_requests"
        wait = RETRY_DELAY_SECONDS if action["retry"] else 0
        if self.elapsed() + wait + b["max_request_seconds"] \
                > b["max_run_seconds"]:
            return "max_run_seconds"
        return None

    def _is_allowed_retry(self, action, key):
        """The one repeat the error policy allows: attempt 2 of 2."""
        return (action["retry"] and action["attempt"] == MAX_ATTEMPTS
                and self.sent.get(key) == 1
                and is_retryable(self.last_outcome.get(key)))

    def _decide(self, obs):
        if not self.pending:
            decision = {"do": "stop", "reason": "every planned board tried"}
            self.trace.write("decision", **decision)
            return decision
        action = self.pending[0]
        key = action_key("GET", action["url"])
        if key in self.sent and not self._is_allowed_retry(action, key):
            decision = {"do": "block", "reason": "repeat_blocked",
                        "board": action["board"], "url": action["url"]}
            self.trace.write("decision", **decision)
            return decision
        limit = self._budget_block(action)
        if limit:
            decision = {"do": "stop", "reason": BUDGET_EXHAUSTED,
                        "limit": limit, "board": action["board"],
                        "budgets": self.budgets,
                        "requests_sent": self.requests_sent,
                        "elapsed_seconds": round(self.elapsed(), 3)}
            self.trace.write("decision", **decision)
            return decision
        decision = {"do": "fetch", "board": action["board"],
                    "url": action["url"],
                    "attempt": f"attempt {action['attempt']} of "
                               f"{MAX_ATTEMPTS}",
                    "retry": action["retry"], "hop": action["hop"],
                    "budget_check": "ok"}
        self.trace.write("decision", **decision)
        return decision

    def _act(self, action):
        if action["retry"]:
            self.trace.write("wait", board=action["board"],
                             seconds=RETRY_DELAY_SECONDS)
            self.sleep(RETRY_DELAY_SECONDS)
        url = policy.check_request("GET", action["url"], REQUEST_HEADERS)
        key = action_key("GET", url)
        self.requests_sent += 1
        self.boards_started.add(action["board"])
        self.sent[key] = self.sent.get(key, 0) + 1
        board = self._board(action["board"])
        board["attempts"] = max(board["attempts"], action["attempt"])
        self.trace.write("action", board=action["board"], method="GET",
                         url=url, attempt=f"attempt {action['attempt']} of "
                                          f"{MAX_ATTEMPTS}",
                         hop=action["hop"],
                         timeout_seconds=self.budgets["max_request_seconds"],
                         request_number=self.requests_sent)
        try:
            response = self.transport("GET", url, dict(REQUEST_HEADERS),
                                      self.budgets["max_request_seconds"])
        except transport_mod.TransportTimeout as exc:
            outcome = {"kind": "timeout", "status": None, "detail": str(exc)}
        except transport_mod.TransportConnectionError as exc:
            outcome = {"kind": "connection", "status": None,
                       "detail": str(exc)}
        except transport_mod.ReplayMissing as exc:
            outcome = {"kind": "replay_missing", "status": None,
                       "detail": str(exc)}
        else:
            outcome = self._classify(response)
        self.last_outcome[key] = outcome
        return outcome

    @staticmethod
    def _classify(response):
        status = response.status
        outcome = {"status": status, "body": response.body,
                   "headers": response.headers}
        if 200 <= status < 300:
            outcome["kind"] = "ok"
        elif 300 <= status < 400 and response.headers.get("location"):
            outcome["kind"] = "redirect"
        elif status == 429:
            outcome["kind"] = "rate_limited"
        elif 400 <= status < 500:
            outcome["kind"] = "client_error"
        elif 500 <= status < 600:
            outcome["kind"] = "server_error"
        else:
            outcome["kind"] = "unexpected_status"
        return outcome

    def _save_raw(self, action, outcome):
        """Buffer the body unchanged; it is written when the run ends."""
        board = self._board(action["board"])
        entry = {"status": outcome["status"]}
        if outcome["headers"].get("location"):
            entry["headers"] = {"location": outcome["headers"]["location"]}
        # Redirect hops within one attempt get a _r<hop> suffix so no file
        # is ever written twice.
        hop = f"_r{action['hop']}" if action["hop"] else ""
        name = (f"{self.run_id}_{board['name']}_a{action['attempt']}"
                f"{hop}.json")
        path = RAW_DIR / name
        self.raw_buffer.append((path, outcome["body"]))
        board["raw_files"].append(str(path))
        entry["file"] = f"../../raw/{name}"
        self.replay_entries.setdefault(action["url"], []).append(entry)
        return str(path)

    def _fail(self, board, reason, status=None):
        board["status"] = "failed"
        board["reason"] = reason
        board["http_status"] = status
        board["new"] = failed_board_new()
        board["new_ids"] = None
        board["postings_seen"] = None
        self.trace.write("board_failed", board=board["name"], reason=reason,
                         http_status=status, new="unknown",
                         state="not updated")

    def _succeed(self, board, body):
        postings = adapters.PARSERS[board["ats"]](body)

        def on_duplicate(pid):
            board["duplicates"].append(pid)
            self.trace.write("duplicate_posting", board=board["name"], id=pid,
                             counted="once")

        unique = dedupe(postings, on_duplicate)
        ids = [p["id"] for p in unique]
        board["status"] = "ok"
        board["http_status"] = 200
        board["postings_seen"] = len(unique)
        board["_ids"] = ids
        seen = board["_seen"]
        board["baseline"] = seen is None
        board["previously_seen"] = 0 if seen is None else len(seen)
        if seen is None:
            board["new"], board["new_ids"] = 0, []
        else:
            new = [p for p in unique if p["id"] not in seen]
            board["new"] = len(new)
            board["new_ids"] = [p["id"] for p in new]
            board["new_postings"] = [
                {k: p[k] for k in ("id", "title", "location", "url")}
                for p in new]
        self.trace.write("board_ok", board=board["name"],
                         postings_seen=board["postings_seen"],
                         duplicates=len(board["duplicates"]),
                         new=board["new"], baseline=board["baseline"])

    def _record(self, action, outcome):
        self.pending.pop(0)
        board = self._board(action["board"])
        result = {"board": board["name"], "url": action["url"],
                  "attempt": f"attempt {action['attempt']} of "
                             f"{MAX_ATTEMPTS}",
                  "outcome": outcome["kind"], "status": outcome["status"]}
        if "body" in outcome:
            body = outcome["body"]
            result["bytes"] = len(body)
            result["sha256"] = hashlib.sha256(body).hexdigest()
            result["raw_file"] = self._save_raw(action, outcome)
        else:
            result["detail"] = outcome.get("detail", "")
            if outcome["kind"] in ("timeout", "connection"):
                self.replay_entries.setdefault(action["url"], []).append(
                    {"error": outcome["kind"]})
        self.trace.write("result", **result)

        kind = outcome["kind"]
        if kind == "ok":
            try:
                self._succeed(board, outcome["body"])
            except adapters.MalformedResponse as exc:
                self.trace.write("malformed_response", board=board["name"],
                                 detail=exc.detail)
                self._fail(board, adapters.MALFORMED_RESPONSE, 200)
        elif kind == "redirect":
            target = policy.check_redirect(action["url"],
                                           outcome["headers"]["location"],
                                           REQUEST_HEADERS)
            if action["hop"] >= MAX_REDIRECTS:
                self._fail(board, "too_many_redirects", outcome["status"])
            else:
                self.trace.write("redirect", board=board["name"],
                                 status=outcome["status"], target=target,
                                 policy="allowed")
                self.pending.insert(0, dict(action, url=target,
                                            hop=action["hop"] + 1,
                                            retry=False))
        elif is_retryable(outcome) and action["attempt"] < MAX_ATTEMPTS:
            self.trace.write("retry_scheduled", board=board["name"],
                             after_seconds=RETRY_DELAY_SECONDS,
                             next_attempt=f"attempt {action['attempt'] + 1} "
                                          f"of {MAX_ATTEMPTS}")
            self.pending.insert(0, dict(action, attempt=action["attempt"] + 1,
                                        hop=0, retry=True))
        elif kind == "rate_limited":
            self._fail(board, "rate_limited", 429)
        elif kind in ("client_error", "server_error", "unexpected_status"):
            self._fail(board, f"http_{outcome['status']}", outcome["status"])
        else:
            self._fail(board, kind, None)

    def _block_repeat(self, decision):
        action = self.pending.pop(0)
        board = self._board(action["board"])
        self.trace.write("repeat_blocked", board=board["name"],
                         url=action["url"], sent="no")
        self._fail(board, "repeat_blocked", None)

    def _stop_on_budget(self, decision):
        self.budget_limit = decision["limit"]
        for action in self.pending:
            board = self._board(action["board"])
            if board["status"] == "not_tried" and board["attempts"] > 0:
                self._fail(board, f"budget_exhausted:{decision['limit']}",
                           None)
        self.pending = []

    # -- finish --

    def _boards_to_save(self):
        return [b for b in self.boards if b["status"] == "ok"]

    def _summary(self):
        boards = []
        for b in self.boards:
            boards.append({k: v for k, v in b.items()
                           if not k.startswith("_")})
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "exit": self.exit,
            "exit_code": EXIT_CODES[self.exit],
            "note": OWN_REPORT_NOTE,
            "budget_limit_hit": self.budget_limit,
            "budgets": self.budgets,
            "usage": {"requests": self.requests_sent,
                      "boards_started": len(self.boards_started),
                      "elapsed_seconds": round(self.elapsed(), 3),
                      "claude_calls": 0},
            "boards_file": str(self.boards_file),
            "state_dir": str(self.state_dir),
            "replay_dir": None if self.replay_dir is None
            else str(self.replay_dir),
            "boards_succeeded": [b["name"] for b in self.boards
                                 if b["status"] == "ok"],
            "boards_failed": [b["name"] for b in self.boards
                              if b["status"] == "failed"],
            "boards_not_tried": [b["name"] for b in self.boards
                                 if b["status"] == "not_tried"],
            "boards": boards,
        }

    def _write_state(self, board):
        seen = (board["_seen"] or set()) | set(board["_ids"])
        data = json.dumps({"board": board["name"], "updated": self.run_id,
                           "mode": self.mode, "seen_ids": sorted(seen)},
                          indent=2) + "\n"
        path = self.state_dir / f"{board['name']}.json"
        policy.replace_state(path, data.encode("utf-8"), self.run_id,
                             self.root)
        board["state_updated"] = True
        self.trace.write("state_saved", board=board["name"], path=str(path),
                         seen_ids=len(seen))

    def _check_no_contact(self, texts):
        for text in texts:
            lowered = text.lower()
            for value in self.contacts:
                if value.lower() in lowered:
                    raise RunError("contact_field_in_output",
                                   "output would contain a résumé contact "
                                   "field")

    def _finish(self):
        for path, body in self.raw_buffer:
            policy.write_new(path, body, self.root)
            self.trace.write("raw_saved", path=str(path), bytes=len(body))
        for board in self.boards:
            if board["_state_bytes"] is not None:
                policy.write_new(self.run_dir / "state_before"
                                 / f"{board['name']}.json",
                                 board["_state_bytes"], self.root)
        manifest = {"_comment": f"Responses seen by run {self.run_id}; "
                                f"replay with --replay {self.run_dir}",
                    "mode": self.mode, "responses": self.replay_entries}
        to_save = self._boards_to_save()
        for board in to_save:
            board["state_updated"] = True  # recorded before writing below
        summary = self._summary()
        summary_text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
        report_text = render_report(summary)
        self._check_no_contact([summary_text, report_text])
        policy.write_new(self.run_dir / "replay.json",
                         (json.dumps(manifest, indent=2) + "\n").encode(),
                         self.root)
        policy.write_new(self.run_dir / "summary.json",
                         summary_text.encode("utf-8"), self.root)
        policy.write_new(self.run_dir / "report.md",
                         report_text.encode("utf-8"), self.root)
        # State is saved last, so a failed report never hides postings.
        for board in to_save:
            self._write_state(board)

    def run(self):
        """Run the loop. Returns the exit name; see EXIT_CODES."""
        try:
            handle = policy.open_new_text(self.run_dir / "trace.jsonl",
                                          self.root)
        except (policy.PolicyRefusal, OSError) as exc:
            self.exit, self.error = ERROR, f"trace_unwritable: {exc}"
            return self.exit
        self.trace = Trace(handle, self.run_id, self.mode, self.elapsed)
        self.trace.write("run_start", mode=self.mode,
                         boards_file=str(self.boards_file))
        try:
            self._startup()
            while True:
                obs = self._observe()
                decision = self._decide(obs)
                if decision["do"] == "stop":
                    if decision["reason"] == BUDGET_EXHAUSTED:
                        self._stop_on_budget(decision)
                    break
                if decision["do"] == "block":
                    self._block_repeat(decision)
                    continue
                action = self.pending[0]
                outcome = self._act(action)
                self._record(action, outcome)
            self.exit = decide_exit(self.boards, self.budget_limit)
            self._finish()
        except policy.PolicyRefusal as exc:
            self.exit, self.error = ERROR, f"permission_violation: {exc}"
        except RunError as exc:
            self.exit, self.error = ERROR, str(exc)
        except OSError as exc:
            self.exit, self.error = ERROR, f"io_error: {exc}"
        if self.exit == ERROR:
            self.trace.write("run_end", exit=ERROR,
                             exit_code=EXIT_CODES[ERROR], reason=self.error,
                             written="trace only")
        else:
            self.trace.write("run_end", exit=self.exit,
                             exit_code=EXIT_CODES[self.exit],
                             budget_limit=self.budget_limit)
        self.trace.close()
        return self.exit


# --- report --------------------------------------------------------------

def _new_text(board):
    return "unknown" if board["new"] is None else str(board["new"])


def render_report(summary):
    mode = summary["mode"]
    lines = [f"# Job-search run {summary['run_id']} ({mode})", ""]
    if mode == SEEDED:
        lines += [f"**SEEDED**: responses were replayed from "
                  f"`{summary['replay_dir']}`. No network request was made. "
                  f"State used: `{summary['state_dir']}`.", ""]

    attention = []
    for b in summary["boards"]:
        if b["status"] == "failed":
            status = b["http_status"] if b["http_status"] is not None \
                else "no HTTP status"
            what = "rate limited by the site" if b["reason"] == \
                "rate_limited" else f"failed: `{b['reason']}`"
            raw = ", ".join(f"`{r}`" for r in b["raw_files"]) or "none"
            attention.append(
                f"- **{b['name']}** {what} (HTTP {status}). New jobs: "
                f"**unknown**. State file not updated. Raw: {raw}")
    if summary["budget_limit_hit"]:
        never = ", ".join(summary["boards_not_tried"]) or "none"
        attention.append(
            f"- Run stopped: budget `{summary['budget_limit_hit']}` reached "
            f"before the next action. Never tried: {never}.")
    lines += ["## Needs your attention", ""]
    lines += attention or ["Nothing needs your attention."]
    lines += [""]

    lines += ["## Result", "",
              f"- Exit: **{summary['exit']}** (code {summary['exit_code']})",
              f"- Boards file: `{summary['boards_file']}`",
              f"- {OWN_REPORT_NOTE} Independent check: "
              f"`python3 -m checks.independent_check "
              f"out/runs/{summary['run_id']}`",
              f"- Succeeded: "
              f"{', '.join(summary['boards_succeeded']) or 'none'}",
              f"- Failed: {', '.join(summary['boards_failed']) or 'none'}",
              f"- Never tried: "
              f"{', '.join(summary['boards_not_tried']) or 'none'}",
              ""]

    lines += ["## Boards", "",
              "| board | ATS | status | HTTP | attempts | postings seen | "
              "duplicates | new |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for b in summary["boards"]:
        seen = "unknown" if b["postings_seen"] is None else b["postings_seen"]
        new = _new_text(b) + (" (baseline)" if b["baseline"] else "")
        lines.append(f"| {b['name']} | {b['ats']} | {b['status']} | "
                     f"{b['http_status'] if b['http_status'] else '-'} | "
                     f"{b['attempts']} | {seen} | {len(b['duplicates'])} | "
                     f"{new} |")
    lines += [""]

    lines += ["## New postings", ""]
    any_new = False
    for b in summary["boards"]:
        if b["baseline"]:
            lines += [f"- {b['name']}: baseline run; every current id was "
                      f"recorded and none is reported as new."]
        for p in b["new_postings"]:
            any_new = True
            title = " ".join(p["title"].split())
            lines.append(f"- {b['name']} `{p['id']}`: {title} "
                         f"({p['location'] or 'no location'}) {p['url']}")
    if not any_new:
        lines.append("- No new postings on any board that succeeded.")
    lines += [""]

    u, bud = summary["usage"], summary["budgets"]
    lines += ["## Budget use", "",
              f"- Requests: {u['requests']} of {bud['max_requests']}",
              f"- Boards started: {u['boards_started']} of "
              f"{bud['max_boards']}",
              f"- Elapsed: {u['elapsed_seconds']} s of "
              f"{bud['max_run_seconds']} s "
              f"(per request: {bud['max_request_seconds']} s)",
              f"- Claude calls: {u['claude_calls']} of "
              f"{bud['max_claude_calls']}",
              "",
              "## Notes", "",
              "- A 200 with zero postings is accepted as a valid empty board "
              "(known limit, GATE.md section 4).",
              ""]
    return "\n".join(lines)


# --- CLI -----------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(prog="python3 -m agent.loop",
                                     description=__doc__.splitlines()[0])
    parser.add_argument("--replay", metavar="DIR", type=Path,
                        help="serve saved responses from DIR instead of the "
                             "network; the run is labeled SEEDED")
    parser.add_argument("--boards", metavar="FILE", type=Path,
                        default=BOARDS_CONFIG,
                        help="boards config to use (default: "
                             "config/boards.json); read through the policy "
                             "and validated exactly like the default")
    return parser


def main(argv=None, root=policy.ROOT, transport=None, clock=time.monotonic,
         sleep=time.sleep, run_id=None):
    args = build_parser().parse_args(argv)
    if args.replay is None and transport is None:
        transport = transport_mod.UrllibTransport()
    runner = Runner(root=root, transport=transport, replay_dir=args.replay,
                    clock=clock, sleep=sleep, run_id=run_id,
                    boards_file=args.boards)
    exit_name = runner.run()
    code = EXIT_CODES[exit_name]
    if exit_name == ERROR:
        print(f"error ({code}): {runner.error}", file=sys.stderr)
        print(f"trace: {RUNS_DIR / runner.run_id / 'trace.jsonl'}",
              file=sys.stderr)
        return code
    print(f"[{runner.mode}] exit: {exit_name} ({code})")
    for board in runner.boards:
        seen = "unknown" if board["postings_seen"] is None \
            else board["postings_seen"]
        print(f"  {board['name']}: {board['status']}"
              f"{' (' + board['reason'] + ')' if board['reason'] else ''}, "
              f"postings {seen}, new {_new_text(board)}")
    print(f"report: {RUNS_DIR / runner.run_id / 'report.md'}")
    return code


if __name__ == "__main__":
    sys.exit(main())
