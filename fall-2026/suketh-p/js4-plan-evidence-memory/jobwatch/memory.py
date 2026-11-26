"""The JS4 memory: jobwatch-state/3, the seen-postings state with a revision rule.

It follows the student's memory gate (MEMORY-GATE.md, aa5d3f62) and premortem (PREMORTEM.md,
9a8f1cc3), under PLAN.md v0.2:

- Every remembered fact carries the gate's twelve fields, so each one says where it came from.
- One revision covers the whole file. The writer takes a lock, rereads the file, and compares its
  revision and SHA-256 with the student's approval. Only on a match does it replace the file
  atomically, advancing the revision once. A mismatch refuses the write and leaves the file's bytes as
  they were. It also writes a refusal record in the run's folder, which voids that run's approval for
  good.
- The memory makes only dated statements about a posting: listed as of a capture time; missing from
  a later list, status unknown; closed in a labelled seeded fixture; or "I cannot tell".

Claude Code wrote this on 2026-11-25 to pass tests/test_memory.py (42cf9333). Where the gate leaves
room, the choices made here are marked "Claude Code's choice". Standard library only. JS3's
jobwatch/state.py (jobwatch-state/2, the live loop's state) is unchanged."""

import copy
import fcntl
import hashlib
import json
import os
import re
import secrets
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import NamedTuple

from jobwatch.errors import StateError
from jobwatch.policy import _inside, _symlink_in_path
from jobwatch.state import _problem as _state2_problem

SCHEMA = "jobwatch-state/3"
FACT_FIELDS = ("board", "posting_key", "fact_type", "value", "captured_at", "capture_run_id",
               "recorded_by_run_id", "source_kind", "source_path", "source_sha256", "source_locator",
               "verification_ref")
FIRST_SEEN, LISTED_FACT, MISSING_FACT, CLOSED_FACT = "first seen", "listed", "missing from the list", "closed"
FACT_TYPES = (FIRST_SEEN, LISTED_FACT, MISSING_FACT, CLOSED_FACT)
SAVED_CAPTURE, SEEDED_FIXTURE, LEGACY_IMPORT = "saved capture", "seeded fixture", "legacy import"
SOURCE_KINDS = (SAVED_CAPTURE, SEEDED_FIXTURE, LEGACY_IMPORT)

# What memory may say about whether a posting is still open: MEMORY-GATE.md A2, word for word.
LISTED = "Listed as of the capture time"
MISSING = "Missing from this list. Status unknown."
CLOSED = "Closed in the seeded fixture as of the stated time"
CANNOT_TELL = "I cannot tell"
VALUES = {LISTED_FACT: LISTED, MISSING_FACT: MISSING, CLOSED_FACT: CLOSED}
# Claude Code's choice: the gate names no statement for a first sighting, so this wording is ours.
FIRST_SEEN_VALUE = "First seen as of the capture time"

REFUSAL_FILE = "write-refused.json"
RESUME = ("The plan owner rereads the latest state, reconciles the proposal and approves a new run ID "
          "against the new revision and hash (MEMORY-GATE.md, trigger 1).")

_SHA = re.compile(r"[0-9a-f]{64}")
_TIME = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")
_REVISION_TEXT = re.compile(r"0|[1-9][0-9]*")
_TOP = ("schema", "revision", "imported_from", "boards", "runs", "facts")
_BOARD_FIELDS = {"ats", "slug", "baseline_run"}
_RUN_FIELDS = {"run_id", "label", "base_revision", "base_sha256", "revision", "committed_at", "boards"}
_RUN_BOARD_FIELDS = {"outcome", "jobs", "baseline", "new", "missing", "returned"}
_IMPORT_FIELDS = {"path", "sha256", "schema", "migrated_by", "runs"}


class StaleWrite(StateError):
    """The file is not at the revision and SHA-256 the approval names (MEMORY-GATE.md C, trigger 1)."""

    def __init__(self, message, expected, found):
        super().__init__(message)
        self.expected, self.found = expected, found


class ApprovalVoid(StateError):
    """This run's approval was voided by an earlier refused write; a new run ID needs a new approval."""


class ApprovalProblem(StateError):
    """The approval or the proposal does not fit this write."""


@dataclass(frozen=True)
class WriteApproval:
    """The student's approval for one state write: the run ID, the target path, the starting
    revision and the SHA-256 of the file at that revision (PLAN.md v0.2, Approval). As text:
    RUN_ID:PATH:REVISION:SHA256. In tests it is a simulated fixture."""

    run_id: str
    path: str
    revision: int
    sha256: str

    @classmethod
    def parse(cls, text):
        parts = text.split(":")
        if len(parts) != 4:
            raise ValueError("an approval must look like RUN_ID:PATH:REVISION:SHA256")
        run_id, path, revision, sha = parts
        if not run_id.strip() or not path.strip():
            raise ValueError("an approval must name the run and the path")
        if not _REVISION_TEXT.fullmatch(revision):
            raise ValueError(f"the revision must be a whole number with no sign or leading zero, not {revision!r}")
        if not _SHA.fullmatch(sha):
            raise ValueError("the SHA-256 must be 64 lowercase hexadecimal characters")
        return cls(run_id, path, int(revision), sha)

    def __str__(self):
        return f"{self.run_id}:{self.path}:{self.revision}:{self.sha256}"


class Receipt(NamedTuple):
    """A read-only description of the state file: the values an approval must name."""

    path: str
    revision: int
    sha256: str


@dataclass(frozen=True)
class Capture:
    """One board's verified key set from one saved response (PLAN.md v0.2, step 2)."""

    board: str
    keys: list
    captured_at: str
    capture_run_id: str
    source_path: str
    source_sha256: str
    verification_ref: str
    source_kind: str = SAVED_CAPTURE


@dataclass(frozen=True)
class Closure:
    """An explicitly labelled seeded fixture that says a remembered posting closed at a stated time."""

    board: str
    key: str
    closed_at: str
    fixture_id: str
    fixture_path: str
    fixture_sha256: str
    label: str
    verification_ref: str


@dataclass(frozen=True)
class Proposal:
    """A run's proposed update, built on one revision. It changes nothing until commit()."""

    run_id: str
    base_revision: int
    facts: tuple
    boards: dict


# The state --------------------------------------------------------------------------------------

def empty_state():
    return {"schema": SCHEMA, "revision": 0, "imported_from": None, "boards": {}, "runs": [], "facts": []}


def _text(value):
    return isinstance(value, str) and value.strip() != ""


def _keys_list(value):
    return isinstance(value, list) and all(_text(item) for item in value)


def _run_problem(index, run):
    where = f"runs[{index}]"
    if not isinstance(run, dict) or set(run) != _RUN_FIELDS:
        return f"{where} must have exactly the fields {sorted(_RUN_FIELDS)}"
    if not (_text(run["run_id"]) and _text(run["label"])):
        return f"{where} needs a run ID and a label"
    if type(run["revision"]) is not int or run["revision"] != index + 1:
        return f"{where}.revision must be {index + 1}"
    if type(run["base_revision"]) is not int or run["base_revision"] != index:
        return f"{where}.base_revision must be {index}"
    if not (isinstance(run["base_sha256"], str) and _SHA.fullmatch(run["base_sha256"])):
        return f"{where}.base_sha256 must be a SHA-256"
    if not (isinstance(run["committed_at"], str) and _TIME.fullmatch(run["committed_at"])):
        return f"{where}.committed_at must be a UTC time like 2026-11-25T12:00:00Z"
    if not isinstance(run["boards"], dict):
        return f"{where}.boards must be an object"
    for name, entry in run["boards"].items():
        if not isinstance(entry, dict) or set(entry) != _RUN_BOARD_FIELDS:
            return f"{where}.boards[{name!r}] must have exactly the fields {sorted(_RUN_BOARD_FIELDS)}"
        if entry["outcome"] not in ("usable", "unusable"):
            return f"{where}.boards[{name!r}].outcome must be usable or unusable"
        usable = entry["outcome"] == "usable"
        jobs_ok = (type(entry["jobs"]) is int and entry["jobs"] >= 0) if usable else entry["jobs"] is None
        if not jobs_ok or not isinstance(entry["baseline"], bool):
            return f"{where}.boards[{name!r}] has a wrong jobs count or baseline flag"
        if not all(_keys_list(entry[field]) for field in ("new", "missing", "returned")):
            return f"{where}.boards[{name!r}] new, missing and returned must be lists of posting keys"
    return None


def _fact_problem(index, fact, boards, recorders):
    where = f"facts[{index}]"
    if not isinstance(fact, dict) or set(fact) != set(FACT_FIELDS):
        return f"{where} must have exactly the fields {list(FACT_FIELDS)}"
    for field in FACT_FIELDS:
        if not _text(fact[field]):
            return f"{where}.{field} must be non-empty text: every fact says where it came from"
    if fact["fact_type"] not in FACT_TYPES:
        return f"{where}.fact_type must be one of {list(FACT_TYPES)}"
    if fact["source_kind"] not in SOURCE_KINDS:
        return f"{where}.source_kind must be one of {list(SOURCE_KINDS)}"
    if not _SHA.fullmatch(fact["source_sha256"]):
        return f"{where}.source_sha256 must be a SHA-256"
    if not _TIME.fullmatch(fact["captured_at"]):
        return f"{where}.captured_at must be a UTC time like 2026-11-25T12:00:00Z"
    if fact["fact_type"] in VALUES and fact["value"] != VALUES[fact["fact_type"]]:
        return f"{where}.value must be {VALUES[fact['fact_type']]!r} for a {fact['fact_type']!r} fact"
    if fact["board"] not in boards:
        return f"{where}.board {fact['board']!r} has no baseline in this state"
    if fact["recorded_by_run_id"] not in recorders:
        return f"{where}.recorded_by_run_id {fact['recorded_by_run_id']!r} is not a committed run of this state"
    return None


def validate(state):
    """None if the state is a well-formed jobwatch-state/3 record; otherwise what is wrong."""
    if not isinstance(state, dict) or set(state) != set(_TOP):
        return f"expected exactly the fields {list(_TOP)}"
    if state["schema"] != SCHEMA:
        return f"schema must be {SCHEMA!r}"
    revision, runs = state["revision"], state["runs"]
    if type(revision) is not int or revision < 0:
        return "revision must be a whole number, 0 or more"
    if not isinstance(runs, list):
        return "runs must be a list"
    if revision != len(runs):
        return f"revision {revision} does not match the {len(runs)} committed run(s)"
    for index, run in enumerate(runs):
        problem = _run_problem(index, run)
        if problem:
            return problem
    committed = [run["run_id"] for run in runs]
    if len(set(committed)) != len(committed):
        return "a run ID appears twice in runs"
    imported, legacy_runs, recorders = state["imported_from"], set(), set(committed)
    if imported is not None:
        if not isinstance(imported, dict) or set(imported) != _IMPORT_FIELDS:
            return f"imported_from must be null or have exactly the fields {sorted(_IMPORT_FIELDS)}"
        if not (_text(imported["path"]) and _text(imported["migrated_by"])
                and isinstance(imported["sha256"], str) and _SHA.fullmatch(imported["sha256"])
                and imported["schema"] == "jobwatch-state/2" and isinstance(imported["runs"], list)
                and all(isinstance(run, dict) and _text(run.get("run_id")) for run in imported["runs"])):
            return "imported_from must name the jobwatch-state/2 file, its SHA-256, the migration and its runs"
        legacy_runs = {run["run_id"] for run in imported["runs"]}
        recorders.add(imported["migrated_by"])
    if not isinstance(state["boards"], dict):
        return "boards must be an object"
    for name, entry in state["boards"].items():
        if not isinstance(entry, dict) or set(entry) != _BOARD_FIELDS:
            return f"boards[{name!r}] must have exactly the fields {sorted(_BOARD_FIELDS)}"
        if not all(_text(entry[field]) for field in _BOARD_FIELDS) or name != f"{entry['ats']}/{entry['slug']}":
            return f"boards[{name!r}] must match its ats and slug"
        if entry["baseline_run"] not in set(committed) | legacy_runs:
            return f"boards[{name!r}].baseline_run {entry['baseline_run']!r} is not a run of this state"
    if not isinstance(state["facts"], list):
        return "facts must be a list"
    for index, fact in enumerate(state["facts"]):
        problem = _fact_problem(index, fact, state["boards"], recorders)
        if problem:
            return problem
    return None


def encode(state):
    """The file's bytes: readable JSON with one remembered fact per line, fields in the gate's order."""
    parts = []
    for name in _TOP[:-1]:
        parts.append(f"  {json.dumps(name)}: " + json.dumps(state[name], indent=2, ensure_ascii=False)
                     .replace("\n", "\n  "))
    facts = state["facts"]
    if facts:
        rows = []
        for fact in facts:
            ordered = {field: fact[field] for field in FACT_FIELDS} if set(fact) == set(FACT_FIELDS) else fact
            rows.append("    " + json.dumps(ordered, ensure_ascii=False))
        parts.append('  "facts": [\n' + ",\n".join(rows) + "\n  ]")
    else:
        parts.append('  "facts": []')
    return ("{\n" + ",\n".join(parts) + "\n}\n").encode("utf-8")


def _parse(raw, where):
    try:
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise StateError(f"{where} is damaged: {error}") from None
    problem = validate(data)
    if problem:
        raise StateError(f"{where} is damaged: {problem}")
    return data


def load(path):
    """Read and check the state. Each call returns a new copy; changing it never changes the file."""
    path = Path(path)
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        raise StateError(f"{path} does not exist; the replay starts from an empty revision 0 file") from None
    return _parse(raw, path)


def _target(root, rel):
    """The file a relative path names, refused if it would leave the workspace or pass a symlink."""
    given = PurePosixPath(rel)
    if not given.parts or given.is_absolute() or ".." in given.parts:
        raise ApprovalProblem(f"{rel!r}: the path must be relative and stay inside the workspace")
    full = root / given
    link = _symlink_in_path(root, full)
    if link is not None:
        raise ApprovalProblem(f"{rel}: {link.relative_to(root)} is a symlink")
    if not _inside(full.resolve(), root):
        raise ApprovalProblem(f"{rel} resolves outside the workspace")
    return full


def receipt(root, rel):
    """The revision and SHA-256 an approval for the next write must name. Reads only."""
    raw = _target(Path(root).resolve(), rel).read_bytes()
    return Receipt(rel, _parse(raw, rel)["revision"], hashlib.sha256(raw).hexdigest())


# Deciding what a run adds -------------------------------------------------------------------------

def _unique(keys):
    return list(dict.fromkeys(keys))


def _key_field(board):
    return "jobUrl" if board.startswith("ashby/") else "id"


def _seen(state, board):
    """The board's remembered keys, in first-seen order, each with its first-seen fact."""
    seen = {}
    for fact in state["facts"]:
        if fact["board"] == board and fact["fact_type"] == FIRST_SEEN:
            seen.setdefault(fact["posting_key"], fact)
    return seen


def _last_observations(state, board):
    """Each remembered key's newest dated observation (listed, missing or closed), in one pass."""
    latest = {}
    for index, fact in enumerate(state["facts"]):
        if fact["board"] == board and fact["fact_type"] != FIRST_SEEN:
            key = fact["posting_key"]
            if key not in latest or (fact["captured_at"], index) >= (latest[key][1]["captured_at"], latest[key][0]):
                latest[key] = (index, fact)
    return {key: fact for key, (_, fact) in latest.items()}


def new_keys(state, board, keys):
    """MEMORY-GATE.md B4 'Is this new?': None when the board has no usable capture yet (this one is its
    baseline); otherwise the keys the board's full seen-key history does not hold, in the order given."""
    if board not in state["boards"]:
        return None
    seen = _seen(state, board)
    return [key for key in _unique(keys) if key not in seen]


def _fact(board, key, fact_type, value, captured_at, capture_run_id, run_id, source_kind, source_path,
          source_sha256, source_locator, verification_ref):
    return dict(zip(FACT_FIELDS, (board, key, fact_type, value, captured_at, capture_run_id, run_id, source_kind,
                                  source_path, source_sha256, source_locator, verification_ref)))


def _capture_facts(state, run_id, capture):
    board, keys = capture.board, _unique(capture.keys)
    if not _keys_list(keys):
        raise StateError(f"{board}: posting keys must be non-empty text")
    baseline = board not in state["boards"]
    seen = {} if baseline else _seen(state, board)
    last = {} if baseline else _last_observations(state, board)
    field = _key_field(board)
    source = (capture.captured_at, capture.capture_run_id, run_id, capture.source_kind, capture.source_path,
              capture.source_sha256)
    facts, new, returned = [], [], []
    for key in keys:
        if key not in seen:
            facts.append(_fact(board, key, FIRST_SEEN, FIRST_SEEN_VALUE, *source, f"jobs[].{field} = {key}",
                               capture.verification_ref))
            if not baseline:
                new.append(key)
        else:
            # Claude Code's choice: a key "returns" when its newest observation was missing or closed.
            if key in last and last[key]["fact_type"] in (MISSING_FACT, CLOSED_FACT):
                returned.append(key)
        facts.append(_fact(board, key, LISTED_FACT, LISTED, *source, f"jobs[].{field} = {key}",
                           capture.verification_ref))
    listed = set(keys)
    missing = [key for key in seen if key not in listed]
    for key in missing:
        facts.append(_fact(board, key, MISSING_FACT, MISSING, *source, f"all jobs[].{field}",
                           capture.verification_ref))
    summary = {"outcome": "usable", "jobs": len(keys), "baseline": baseline, "new": new, "missing": missing,
               "returned": returned}
    return facts, summary


def _closure_fact(state, run_id, closure):
    if not (isinstance(closure.label, str) and "FIXTURE" in closure.label):
        raise StateError(f"a closure must come from an explicitly labelled fixture, not {closure.label!r}")
    if closure.board not in state["boards"] or closure.key not in _seen(state, closure.board):
        raise StateError(f"the closure names {closure.board} {closure.key!r}, which this memory does not remember")
    # Claude Code's choice: for a fixture, capture_run_id holds the fixture's own ID.
    return _fact(closure.board, closure.key, CLOSED_FACT, CLOSED, closure.closed_at, closure.fixture_id, run_id,
                 SEEDED_FIXTURE, closure.fixture_path, closure.fixture_sha256,
                 f"closures[] board = {closure.board}, key = {closure.key}", closure.verification_ref)


def propose(state, run_id, captures=(), *, unusable=(), closures=()):
    """The facts one run would add, built on the state's current revision. Pure: nothing changes."""
    problem = validate(state)
    if problem:
        raise StateError(f"the state is damaged: {problem}")
    if not _text(run_id):
        raise StateError("a proposal needs a run ID")
    named = [capture.board for capture in captures] + list(unusable)
    if len(named) != len(set(named)):
        raise StateError("a board may appear only once in a run")
    facts, boards = [], {}
    for capture in captures:
        board_facts, boards[capture.board] = _capture_facts(state, run_id, capture)
        facts.extend(board_facts)
    for board in unusable:
        boards[board] = {"outcome": "unusable", "jobs": None, "baseline": False, "new": [], "missing": [],
                         "returned": []}
    for closure in closures:
        facts.append(_closure_fact(state, run_id, closure))
    return Proposal(run_id, state["revision"], tuple(facts), boards)


def apply(state, proposal, *, base_sha256, label, committed_at):
    """The state after the proposal, one revision later. The input is not changed."""
    if proposal.base_revision != state["revision"]:
        raise ApprovalProblem(f"the proposal was built on revision {proposal.base_revision}, but the state is at "
                              f"revision {state['revision']}; build it again from the current state")
    for run in state["runs"]:
        if run["run_id"] == proposal.run_id:
            raise ApprovalProblem(f"run {proposal.run_id} already committed revision {run['revision']}; "
                                  "a new write needs a new run ID")
    after = copy.deepcopy(state)
    for name, summary in proposal.boards.items():
        if summary["outcome"] == "usable" and name not in after["boards"]:
            ats, _, slug = name.partition("/")
            after["boards"][name] = {"ats": ats, "slug": slug, "baseline_run": proposal.run_id}
    after["facts"].extend(copy.deepcopy(list(proposal.facts)))
    after["revision"] = state["revision"] + 1
    after["runs"].append({"run_id": proposal.run_id, "label": label, "base_revision": state["revision"],
                          "base_sha256": base_sha256, "revision": after["revision"], "committed_at": committed_at,
                          "boards": copy.deepcopy(proposal.boards)})
    problem = validate(after)
    if problem:
        raise StateError(f"refusing to build a damaged state: {problem}")
    return after


# Writing ----------------------------------------------------------------------------------------

def _utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@contextmanager
def _exclusive(lock_path):
    """An exclusive lock on a separate lock file that is never replaced (Claude Code's choice). Not
    the state file itself: the atomic replace gives the state a new inode, so a lock held on the old
    one would not stop a writer that opened the new one. flock() locks belong to each open file
    description, so two threads that open the lock file separately also exclude each other."""
    handle = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(handle, fcntl.LOCK_UN)
        os.close(handle)


def _write_atomic(target, data):
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.{secrets.token_hex(6)}.tmp")
    try:
        with open(temp, "xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, target)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise
    folder = os.open(target.parent, os.O_RDONLY)
    try:
        os.fsync(folder)
    finally:
        os.close(folder)


def _revision_or_none(raw):
    try:
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    revision = data.get("revision") if isinstance(data, dict) else None
    return revision if type(revision) is int else None


def commit(root, path, approval, proposal, run_dir, *, label, clock=None, before_write=None):
    """MEMORY-GATE.md B3: hold the lock while rereading the file, compare the approved starting
    revision and SHA-256, and replace the state atomically, advancing the revision once. A mismatch
    voids the run's approval, records the refusal in run_dir and leaves the state's bytes unchanged.
    before_write is a test hook, called inside the lock after the compare."""
    clock = clock or _utc_now
    if not isinstance(approval, WriteApproval):
        raise ApprovalProblem("a state write needs an approval naming the run, the path, the revision and the SHA-256")
    if approval.run_id != proposal.run_id:
        raise ApprovalProblem(f"the approval names run {approval.run_id!r}, not this run ({proposal.run_id!r})")
    if approval.path != path:
        raise ApprovalProblem(f"the approval names {approval.path!r}, not {path!r}")
    if proposal.base_revision != approval.revision:
        raise ApprovalProblem(f"the proposal was built on revision {proposal.base_revision}, but the approval names "
                              f"revision {approval.revision}; build the proposal again from the approved revision")
    root = Path(root).resolve()
    target = _target(root, path)
    refusal_rel = (PurePosixPath(run_dir) / REFUSAL_FILE).as_posix()
    refusal = _target(root, refusal_rel)
    if not target.is_file():
        raise StateError(f"{path} does not exist; the replay starts from an empty revision 0 file")
    with _exclusive(target.with_name(f".{target.name}.lock")):
        if refusal.exists():
            raise ApprovalVoid(f"run {proposal.run_id}'s approval was voided by an earlier refused write "
                               f"({refusal_rel}); a new run ID needs a new approval")
        raw = target.read_bytes()
        found_sha = hashlib.sha256(raw).hexdigest()
        current = None
        if found_sha == approval.sha256:
            current = _parse(raw, path)          # the approved bytes themselves are damaged: an error
        found_revision = current["revision"] if current is not None else _revision_or_none(raw)
        if current is None or found_revision != approval.revision:
            expected = {"revision": approval.revision, "sha256": approval.sha256}
            found = {"revision": found_revision, "sha256": found_sha}
            _write_atomic(refusal, (json.dumps({
                "event": "stale write refused", "run_id": proposal.run_id, "path": path, "approval": str(approval),
                "expected": expected, "found": found, "at": clock(), "state_changed": False,
                "approval_void": True, "next": RESUME}, indent=2) + "\n").encode("utf-8"))
            raise StaleWrite(f"stale write refused for run {proposal.run_id}: the approval expected revision "
                             f"{approval.revision} (sha256 {approval.sha256[:12]}…) and found revision "
                             f"{found_revision} (sha256 {found_sha[:12]}…). The state was not changed, and this "
                             f"run's approval is now void. {RESUME}", expected, found)
        after = apply(current, proposal, base_sha256=found_sha, label=label, committed_at=clock())
        data = encode(after)
        if before_write is not None:
            before_write()
        _write_atomic(target, data)
    return Receipt(path, after["revision"], hashlib.sha256(data).hexdigest())


# Reading what memory may say ------------------------------------------------------------------------

def _last_attempt(state, board):
    """The newest committed run that tried this board, as (run_id, its entry), or None."""
    found = None
    for run in state["runs"]:
        if board in run["boards"]:
            found = (run["run_id"], run["boards"][board])
    return found


def liveness(state, board, key):
    """MEMORY-GATE.md A2. Every statement is dated: the memory never says a posting is open now
    (Claude Code's choice, since no age limit for a present-tense answer has been set). Conflicting
    evidence, an unusable latest capture of the board, or no verified observation gives "I cannot
    tell", and the last verified observation stays in the answer."""
    said = {"board": board, "key": key, "statement": CANNOT_TELL, "as_of": None, "reason": None,
            "first_seen": None, "last_listed": None, "latest": None}
    if board not in state["boards"]:
        said["reason"] = "this memory has no usable capture of the board"
        return said
    history = [(index, fact) for index, fact in enumerate(state["facts"])
               if fact["board"] == board and fact["posting_key"] == key]

    def newest(fact_type):
        found = [(fact["captured_at"], index, fact) for index, fact in history if fact["fact_type"] == fact_type]
        return max(found, key=lambda item: item[:2]) if found else None

    first = [fact for _, fact in history if fact["fact_type"] == FIRST_SEEN]
    listed, missing, closed = newest(LISTED_FACT), newest(MISSING_FACT), newest(CLOSED_FACT)
    said["first_seen"] = copy.deepcopy(first[0]) if first else None
    said["last_listed"] = copy.deepcopy(listed[2]) if listed else None
    if not (listed or missing or closed):
        said["reason"] = "no verified observation of this key on this board"
        return said
    attempt = _last_attempt(state, board)
    if attempt is not None and attempt[1]["outcome"] == "unusable":
        said["reason"] = (f"the board's latest capture (run {attempt[0]}) was unusable; "
                          "the last verified observation stays in history")
        return said
    if closed and (listed is None or closed[0] > listed[0]):
        said.update(statement=CLOSED, as_of=closed[0], latest=copy.deepcopy(closed[2]))
        return said
    if closed and any(fact["fact_type"] == CLOSED_FACT and index > listed[1] for index, fact in history):
        said["reason"] = ("the evidence conflicts: a closure fixture recorded after the last listing "
                          f"states an earlier or equal time ({closed[0]}) than that listing ({listed[0]})")
        said["latest"] = copy.deepcopy(closed[2])
        return said
    if missing and (listed is None or missing[0] > listed[0]):
        said.update(statement=MISSING, as_of=missing[0], latest=copy.deepcopy(missing[2]))
        return said
    said.update(statement=LISTED, as_of=listed[0], latest=copy.deepcopy(listed[2]))
    return said


def run_diff(state, run_id):
    """MEMORY-GATE.md B4 'What changed between the two days?': one committed run's changes per board and
    the revisions it links."""
    for run in state["runs"]:
        if run["run_id"] == run_id:
            return {"run_id": run_id, "base_revision": run["base_revision"], "base_sha256": run["base_sha256"],
                    "revision": run["revision"], "boards": copy.deepcopy(run["boards"])}
    raise StateError(f"no committed run {run_id!r} in this state")


# The migration fixture ----------------------------------------------------------------------------

def migrate_v2(raw, *, source_path, run_id, verification_ref):
    """PLAN.md v0.2: copy a jobwatch-state/2 record into revision 0, keep its seen keys (as legacy
    first-seen facts) and its run history, and record the original file's SHA-256. Liveness starts
    unknown: a legacy record holds no listing observation."""
    try:
        old = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise StateError(f"{source_path} is damaged: {error}") from None
    problem = _state2_problem(old)
    if problem:
        raise StateError(f"{source_path} is not a valid jobwatch-state/2 record: {problem}")
    sha = hashlib.sha256(raw).hexdigest()
    finished = {run.get("run_id"): run.get("finished_at") for run in old["runs"] if isinstance(run, dict)}
    state = empty_state()
    state["imported_from"] = {"path": source_path, "sha256": sha, "schema": "jobwatch-state/2",
                              "migrated_by": run_id, "runs": copy.deepcopy(old["runs"])}
    for name, entry in old["boards"].items():
        state["boards"][name] = {"ats": entry["ats"], "slug": entry["slug"], "baseline_run": entry["first_snapshot_run"]}
        for key, seen_run in entry["seen"].items():
            at = finished.get(seen_run)
            if not (isinstance(at, str) and _TIME.fullmatch(at)):
                raise StateError(f"{source_path}: run {seen_run!r} has no finish time to date {name} {key!r}")
            state["facts"].append(_fact(
                name, key, FIRST_SEEN, f"First seen by run {seen_run} (legacy record: the time is that run's finish time)",
                at, seen_run, run_id, LEGACY_IMPORT, source_path, sha,
                f"boards[{json.dumps(name)}].seen[{json.dumps(key)}]", verification_ref))
    problem = validate(state)
    if problem:
        raise StateError(f"the migrated state would be damaged: {problem}")
    return state
