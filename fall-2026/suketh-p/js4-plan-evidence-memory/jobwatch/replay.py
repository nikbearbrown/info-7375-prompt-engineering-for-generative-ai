"""The SEEDED replay: PLAN.md v0.2 steps 1-7 over a saved capture, offline.

    python3 -m jobwatch.replay receipt [--state PATH]
    python3 -m jobwatch.replay init [--state PATH]
    python3 -m jobwatch.replay run --run-id ID --capture runs/CAPTURE [--earlier runs/EARLIER ...]
                                   [--approve RUN_ID:PATH:REVISION:SHA256] [--closure FIXTURE.json]
    python3 -m jobwatch.replay premortem --capture runs/CAPTURE --approve-anthropic TEXT
                                         --approve-databricks TEXT [--state PATH]
    python3 -m jobwatch.replay premortem-resume --capture runs/CAPTURE --watcher databricks
                                                --approve RUN_ID:PATH:REVISION:SHA256 [--state PATH]

A replay makes no HTTP request and no model call. It reads saved captures under runs/, the
fictional persona, the checker and labelled fixtures. It writes its own run folder under
replay/runs/, and it writes the replay state only with the student's approval for that exact run,
path, revision and SHA-256. Run it from the JS4 folder.

Claude Code wrote this on 2026-11-28 to pass tests/test_replay.py (0117cf0b). Where the plan leaves
room, the choices here are Claude Code's: the file names in a run folder, the JS3-format report that
lets checks/independent_check.py audit the replay, and checking the closure case in memory only."""

import argparse
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

from jobwatch import ats, memory, watchers
from jobwatch.errors import AgentError, InputError, StateError
from jobwatch.policy import PERSONA_FILE
from jobwatch.resume import validate_resume

LABEL = "SEEDED"
STATE_PATH = "replay/state/state.json"
RUNS = "replay/runs"
PREMORTEM_STATE = "replay/premortem/state.json"
CHECKER = "checks/independent_check.py"
PLANTED = "fixtures/count-42-planted-99"
PLANTED_FLAG = "results.json reports 99 jobs; its saved response has 42"
BUDGET_SECONDS = 30.0      # the JS2 ceiling, kept by PLAN.md v0.2
EXIT = {"finished": 0, "error": 1, "incomplete": 3, "budget-exhausted": 4}
_RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _dump(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else _dump(data), encoding="utf-8")


def init_state(root, rel=STATE_PATH):
    """Create an empty jobwatch-state/3 file at revision 0. It never replaces an existing file."""
    path = Path(root) / rel
    if path.exists():
        raise StateError(f"{rel} already exists; an existing state is never replaced by an empty one")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "xb") as handle:
        handle.write(memory.encode(memory.empty_state()))
    return memory.receipt(root, rel)


def _capture_folder(root, rel):
    given = PurePosixPath(rel)
    if given.is_absolute() or ".." in given.parts or len(given.parts) < 2 or given.parts[0] != "runs":
        raise InputError(f"{rel!r}: a capture must be a folder under runs/")
    folder = root / given
    if not (folder / "trace.json").is_file():
        raise InputError(f"{rel}: no trace.json, so this is not a saved capture")
    return folder


def _verify(root, capture):
    """Step 2: recompute each saved body's SHA-256 and parse its posting keys with the agent's parser.
    The independent recount is step 5's job (checks/independent_check.py)."""
    folder = _capture_folder(root, capture)
    trace = json.loads((folder / "trace.json").read_text(encoding="utf-8"))
    results = folder / "results.json"
    roles = {}
    if results.is_file():
        roles = {row.get("board"): row.get("role", "normal")
                 for row in json.loads(results.read_text(encoding="utf-8")).get("boards", [])}
    entries, captures, postings, events = [], {}, {}, []
    for event in trace.get("events", []):
        if event.get("event") != "request":
            continue
        board = event["board"]
        events.append(event)
        entry = {"board": board, "role": roles.get(board, "normal"), "captured_at": event.get("at"),
                 "capture_run_id": folder.name, "http": event.get("status"),
                 "raw": f"{capture}/{event['raw']}" if event.get("raw") else None,
                 "sha256_in_trace": event.get("sha256"), "sha256_recomputed": None, "jobs": None,
                 "outcome": "unusable", "reason": None}
        entries.append(entry)
        if not event.get("raw") or event.get("status") != 200:
            entry["reason"] = "no usable response was saved for this board"
            continue
        body = gzip.decompress((folder / event["raw"]).read_bytes())
        entry["sha256_recomputed"] = _sha(body)
        if entry["sha256_recomputed"] != event.get("sha256"):
            entry["reason"] = "the saved body does not match the sha256 in the capture's trace"
            continue
        try:
            found = ats.parse(board.split("/")[0], body)
        except (InputError, ValueError) as error:
            entry["reason"] = f"the saved body could not be parsed: {error}"
            continue
        keys = [posting.key for posting in found]
        entry.update(outcome="usable", jobs=len(keys))
        postings[board] = found
        captures[board] = memory.Capture(board=board, keys=keys, captured_at=event["at"],
                                         capture_run_id=folder.name, source_path=entry["raw"],
                                         source_sha256=entry["sha256_recomputed"],
                                         verification_ref=None)
    return folder, entries, captures, postings, events


def _with_ref(capture, ref):
    return memory.Capture(**{**capture.__dict__, "verification_ref": ref})


def _check(root, args):
    command = [sys.executable, "-I", str(root / CHECKER), *args]
    done = subprocess.run(command, capture_output=True, text=True, cwd=root, timeout=120)
    shown = ["python3", "-I", CHECKER, *[os.path.relpath(a, root) if os.path.isabs(a) else a for a in args]]
    return {"command": shown, "exit": done.returncode, "output": done.stdout + done.stderr}


def _stale_write_fixture(captures, run_id, clock):
    """PLAN.md v0.2 step 5: the stale-write case against a disposable fixture, in a temporary folder.
    Two updates from revision 0, with simulated approvals (not the student's)."""
    chosen = list(captures.values())[:2]
    if len(chosen) < 2:
        return {"refused": False, "bytes_unchanged": False, "note": "fewer than two usable boards to race"}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        rel = "state/state.json"
        (root / "state").mkdir()
        (root / rel).write_bytes(memory.encode(memory.empty_state()))
        sha0 = _sha((root / rel).read_bytes())
        state0 = memory.load(root / rel)
        first, second = (memory.propose(state0, f"{run_id}-fixture-{n}", [capture]) for n, capture in
                         (("a", chosen[0]), ("b", chosen[1])))
        memory.commit(root, rel, memory.WriteApproval(first.run_id, rel, 0, sha0), first, f"runs/{first.run_id}",
                      label="FIXTURE", clock=clock)
        after_first = (root / rel).read_bytes()
        try:
            memory.commit(root, rel, memory.WriteApproval(second.run_id, rel, 0, sha0), second,
                          f"runs/{second.run_id}", label="FIXTURE", clock=clock)
        except memory.StaleWrite as error:
            refused = {"expected": error.expected, "found": error.found}
        else:
            refused = None
        unchanged = (root / rel).read_bytes() == after_first
    return {"refused": refused is not None, "bytes_unchanged": unchanged, **(refused or {}),
            "boards": [c.board for c in chosen],
            "note": "a disposable fixture in a temporary folder, with simulated approvals; not the student's"}


def _closure_case(root, closure, state, proposal, base_sha, run_dir, clock):
    """The seeded closure case, computed in memory on the staged state. It is never written."""
    raw = (root / closure).read_bytes()
    data = json.loads(raw.decode("utf-8"))
    fixture = memory.Closure(board=data["board"], key=data["key"], closed_at=data["closed_at"],
                             fixture_id=data["fixture_id"], fixture_path=closure, fixture_sha256=_sha(raw),
                             label=data["label"], verification_ref=f"{run_dir}/checks.json#closure_case")
    staged = memory.apply(state, proposal, base_sha256=base_sha, label=LABEL, committed_at=clock())
    before = memory.liveness(staged, fixture.board, fixture.key)
    closing = memory.propose(staged, f"{proposal.run_id}-closure-check", closures=[fixture])
    after = memory.liveness(memory.apply(staged, closing, base_sha256="0" * 64, label="FIXTURE CHECK",
                                         committed_at=clock()), fixture.board, fixture.key)
    return {"fixture": closure, "fixture_sha256": fixture.fixture_sha256, "label": fixture.label,
            "board": fixture.board, "key": fixture.key,
            "before": {"statement": before["statement"], "as_of": before["as_of"]},
            "after": {"statement": after["statement"], "as_of": after["as_of"]},
            "shown": before["statement"] == memory.LISTED and after["statement"] == memory.CLOSED,
            "note": "computed in memory on the staged state; the closure is not written to the replay state"}


def _rows(entries, proposal):
    rows = []
    for entry in entries:
        summary = proposal.boards.get(entry["board"], {}) if proposal else {}
        rows.append({"board": entry["board"], "role": entry["role"], "outcome": entry["outcome"],
                     "jobs": entry["jobs"], "baseline": summary.get("baseline", False),
                     "new_keys": summary.get("new", []), "missing_keys": summary.get("missing", []),
                     "returned_keys": summary.get("returned", []), "reason": entry["reason"]})
    return rows


def _reports(folder, run_id, status, reason, advanced, rows, events, steps):
    """The JS3-format report, so checks/independent_check.py can audit the replay's own claims."""
    _write(folder / "results.json", {"run_id": run_id, "label": LABEL, "status": status, "reason": reason,
                                     "state_advanced": advanced, "boards": rows, "notes": "notes.json",
                                     "trace": "trace.json"})
    md = [f"# Replay `{run_id}` ({LABEL}): **{status}**", "", reason, "",
          "| Board | Role | Outcome | Jobs | Baseline | New | Missing | Reason |",
          "|---|---|---|---:|---|---:|---:|---|"]
    for row in rows:
        md.append(f"| {row['board']} | {row['role']} | {row['outcome']} | "
                  f"{row['jobs'] if row['jobs'] is not None else '—'} | {row['baseline']} | {len(row['new_keys'])} | "
                  f"{len(row['missing_keys'])} | {row['reason'] or '—'} |")
    _write(folder / "results.md", "\n".join(md) + "\n")
    _write(folder / "trace.json", {"run_id": run_id, "label": LABEL, "status": status, "reason": reason,
                                   "state_advanced": advanced, "events": events + steps})
    md = [f"# Trace of replay `{run_id}` ({LABEL}): **{status}**", "",
          "The request rows are the original capture's, read from its saved bodies; nothing was fetched.", "",
          "| # | At | Event | Board | HTTP | Bytes | Outcome | Jobs | Raw file |",
          "|---:|---|---|---|---:|---:|---|---:|---|"]
    for event in events:
        md.append(f"| {event['seq']} | {event.get('at')} | request | {event['board']} | {event.get('status')} | "
                  f"{event.get('bytes', '—')} | {event.get('outcome')} | {event.get('jobs')} | {event.get('raw')} |")
    md += ["", "| Step | At | What happened |", "|---|---|---|"]
    md += [f"| {step['event']} | {step['at']} | {step['detail']} |" for step in steps]
    _write(folder / "trace.md", "\n".join(md) + "\n")


def _result(run_id, status, reason, run_dir, advanced=False):
    return {"run_id": run_id, "status": status, "exit": EXIT[status], "reason": reason, "state_advanced": advanced,
            "run_dir": run_dir}


def run(root, run_id, capture, *, earlier=(), approval=None, closure=None, clock=None, monotonic=time.monotonic):
    """PLAN.md v0.2 steps 1-7. Returns {run_id, status, exit, reason, state_advanced, run_dir}."""
    root = Path(root).resolve()
    clock = clock or memory._utc_now
    started = monotonic()
    run_dir = f"{RUNS}/{run_id}"
    # Step 1: preflight. Nothing is written until the run ID, the inputs and the state are known good.
    if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
        return _result(run_id, "error", "a run ID is 1 to 64 letters, digits, dots, dashes or underscores", run_dir)
    folder = root / RUNS / run_id
    if folder.exists():
        return _result(run_id, "error", f"run ID {run_id} is already used ({run_dir} exists); "
                                        "a new run needs a new ID and its own approval", run_dir)
    try:
        for rel in earlier:
            _capture_folder(root, rel)
        verified_folder, entries, captures, postings, events = _verify(root, capture)
        state_bytes = (root / STATE_PATH).read_bytes()
        state = json.loads(state_bytes.decode("utf-8"))
        problem = memory.validate(state)
        if problem:
            raise StateError(f"{STATE_PATH} is damaged: {problem}")
        persona_bytes = (root / PERSONA_FILE).read_bytes()
        persona = json.loads(persona_bytes.decode("utf-8"))
        validate_resume(persona)
    except (AgentError, OSError, ValueError) as error:
        return _result(run_id, "error", f"preflight failed: {error}", run_dir)
    base = {"path": STATE_PATH, "revision": state["revision"], "sha256": _sha(state_bytes)}
    steps = []

    def step(name, detail):
        steps.append({"event": name, "at": clock(), "detail": detail})

    folder.mkdir(parents=True)
    (folder / "state-before.json").write_bytes(state_bytes)
    approval_note = None
    if approval is not None and (approval.run_id, approval.path, approval.revision, approval.sha256) != \
            (run_id, STATE_PATH, base["revision"], base["sha256"]):
        approval_note = "the approval does not name this run, this path and the state's current revision and hash"
    _write(folder / "preflight.json", {
        "run_id": run_id, "label": LABEL, "started_at": clock(), "capture": capture, "earlier": list(earlier),
        "target": base, "approval": str(approval) if approval else None, "approval_note": approval_note,
        "persona": {"path": PERSONA_FILE, "sha256": _sha(persona_bytes), "fictional": persona.get("fictional")},
        "http_requests": 0, "model_calls": 0, "budget_seconds": BUDGET_SECONDS,
        "writes": [run_dir, f"{STATE_PATH}, only with an approval for this run, path, revision and SHA-256"]})
    step("preflight", f"state {STATE_PATH} at revision {base['revision']} (sha256 {base['sha256'][:12]}…); "
                      f"approval: {'given' if approval else 'none'}")

    # Step 2: verify the capture.
    captures = {board: _with_ref(c, f"{run_dir}/verify.json#{board}") for board, c in captures.items()}
    _write(folder / "verify.json", {"capture": capture, "boards": entries})
    step("verify", "; ".join(f"{e['board']}: {e['outcome']}, {e['jobs']} jobs" for e in entries))
    raw_events = []
    for event in events:
        copied = dict(event)
        if copied.get("raw"):
            copied["raw"] = os.path.relpath(verified_folder / event["raw"], folder)
        raw_events.append(copied)

    def finish(status, reason, proposal=None, advanced=False):
        step("exit", f"{status}: {reason}")
        _reports(folder, run_id, status, reason, advanced, _rows(entries, proposal), raw_events, steps)
        return _result(run_id, status, reason, run_dir, advanced)

    # Step 3: the two watchers, each on its own board, from the same starting state.
    for watcher in watchers.ORDER:
        board = watchers.WATCHERS[watcher]
        if board in captures:
            contribution = watchers.watch(watcher, run_id=run_id, base=base, capture=captures[board],
                                          postings=postings[board],
                                          new_keys=memory.new_keys(state, board, captures[board].keys),
                                          persona=persona)
            watchers.write_contribution(folder, contribution)
            step(f"watcher {watcher}", f"{len(contribution['notes'])} note(s) on {board}")

    # Step 4: the coordinator merges the notes; stage the proposal and the two-day diff.
    verified = {board: {"keys": c.keys, "source_path": c.source_path, "source_sha256": c.source_sha256}
                for board, c in captures.items()}
    try:
        merged = watchers.merge(folder, run_id=run_id, base=base, verified=verified)
    except watchers.HandoffError as error:
        return finish("error", f"the coordinator stopped the merge: {error}")
    step("coordinator", "notes.json written: " + ", ".join(f"{c['watcher']} {len(c['notes'])}"
                                                           for c in merged["contributions"]))
    unusable = [e["board"] for e in entries if e["outcome"] != "usable"]
    proposal = memory.propose(state, run_id, list(captures.values()), unusable=unusable)
    counts = {}
    for fact in proposal.facts:
        counts[fact["fact_type"]] = counts.get(fact["fact_type"], 0) + 1
    _write(folder / "proposal.json", {"run_id": run_id, "base": base, "label": LABEL, "facts_by_type": counts,
                                      "boards": proposal.boards,
                                      "note": "the facts themselves are in state-after.json once committed"})
    diff = {"run_id": run_id, "label": LABEL, "capture": capture, "earlier": list(earlier),
            "base_revision": base["revision"], "base_sha256": base["sha256"], "revision": base["revision"] + 1,
            "boards": proposal.boards}
    _write(folder / "diff.json", diff)
    lines = [f"# Two-day diff: `{run_id}` ({LABEL})", "",
             f"Revision {base['revision']} → {base['revision'] + 1} if committed. Capture `{capture}`"
             + (f", compared with the memory built from `{', '.join(earlier)}`." if earlier else "."), "",
             "| Board | Outcome | Jobs | Baseline | New | Missing (liveness unresolved) | Returned |",
             "|---|---|---:|---|---:|---:|---:|"]
    for board, d in proposal.boards.items():
        lines.append(f"| {board} | {d['outcome']} | {d['jobs'] if d['jobs'] is not None else '—'} | {d['baseline']} | "
                     f"{len(d['new'])} | {len(d['missing'])} | {len(d['returned'])} |")
    _write(folder / "diff.md", "\n".join(lines) + "\n")
    _reports(folder, run_id, "staged", "staged for the checks; not published", False, _rows(entries, proposal),
             raw_events, steps)
    step("stage", f"proposal and diff staged: {counts}")

    # Step 5: check the evidence.
    independent = _check(root, [str(folder), *[a for rel in earlier for a in ("--earlier", str(root / rel))]])
    planted = _check(root, [str(root / PLANTED)])
    planted["rejected"] = planted["exit"] == 1 and PLANTED_FLAG in planted["output"]
    stale = _stale_write_fixture(captures, run_id, clock)
    case = _closure_case(root, closure, state, proposal, base["sha256"], run_dir, clock) if closure else None
    flagged = [list(pair) for pair in watchers.instruction_like_keys(merged)]
    problems = []
    if independent["exit"] != 0:
        problems.append("the independent check flagged the replay's report")
    if not planted["rejected"]:
        problems.append("the planted 42/99 fixture was not rejected")
    if not (stale["refused"] and stale["bytes_unchanged"]):
        problems.append("the stale-write fixture was not refused with its bytes unchanged")
    _write(folder / "checks.json", {"independent_check": independent, "planted_count": planted,
                                    "stale_write_fixture": stale, "closure_case": case, "instruction_like": flagged,
                                    "gate": {"passed": not problems, "problems": problems}})
    md = [f"# Checks for replay `{run_id}`", "",
          f"- Independent check (`{' '.join(independent['command'])}`): exit {independent['exit']}",
          f"- Planted 42/99 fixture: exit {planted['exit']}, rejected: {planted['rejected']}",
          f"- Stale-write fixture: refused {stale['refused']}, bytes unchanged {stale['bytes_unchanged']}"]
    if case:
        md.append(f"- Closure case on {case['board']} {case['key']}: before \"{case['before']['statement']}\" "
                  f"({case['before']['as_of']}); after \"{case['after']['statement']}\" ({case['after']['as_of']}); "
                  f"fresh is not true shown: {case['shown']}")
    md.append(f"- Instruction-like posting text kept as data: {flagged or 'none'}")
    md += ["", "## Independent check output", "", "```text", independent["output"].rstrip(), "```"]
    _write(folder / "checks.md", "\n".join(md) + "\n")
    step("checks", "passed" if not problems else "; ".join(problems))
    if problems:
        return finish("error", "evidence conflicts: " + "; ".join(problems), proposal)

    # Step 6: publish the revision, only with the student's approval.
    if monotonic() - started > BUDGET_SECONDS:
        return finish("budget-exhausted", f"budget: the {BUDGET_SECONDS:.0f}-second limit was reached before "
                                          "publication; the state was not changed", proposal)
    if any(e["role"] == "normal" and e["outcome"] != "usable" for e in entries):
        return finish("incomplete", "not every board could be verified; the state was not changed and the "
                                    "results are provisional", proposal)
    if approval is None:
        return finish("incomplete", "no approval was given for this run; the state was not changed and the "
                                    "results are provisional", proposal)
    try:
        receipt = memory.commit(root, STATE_PATH, approval, proposal, run_dir, label=LABEL, clock=clock)
    except memory.StaleWrite as error:
        step("write-refused", str(error))
        return finish("error", str(error), proposal)
    except (memory.ApprovalVoid, StateError) as error:
        status = "incomplete" if isinstance(error, memory.ApprovalProblem) else "error"
        return finish(status, f"the state was not changed: {error}", proposal)
    after = (root / STATE_PATH).read_bytes()
    (folder / "state-after.json").write_bytes(after)
    _write(folder / "publish.json", {"receipt": receipt._asdict(), "base": base, "approval": str(approval),
                                     "state_after_matches": _sha(after) == receipt.sha256})
    step("publish", f"revision {base['revision']} → {receipt.revision} (sha256 {receipt.sha256[:12]}…)")

    # Step 7: close the run.
    return finish("finished", f"every board was usable, both watchers' notes merged, the checks passed and "
                              f"revision {receipt.revision} was committed", proposal, advanced=True)


def premortem(root, state_rel, capture, approvals, *, clock=None):
    """PREMORTEM.md line 2: two updates with different posting keys from the same revision, each with
    its own run ID and approval. Anthropic commits first; then Databricks submits its original revision
    and hash. Writes record.json and record.md next to the disposable state."""
    root = Path(root).resolve()
    clock = clock or memory._utc_now
    _, _, captures, _, _ = _verify(root, capture)
    home = PurePosixPath(state_rel).parent
    before = (root / state_rel).read_bytes()
    state0 = json.loads(before.decode("utf-8"))
    attempts = {}
    for watcher in watchers.ORDER:
        approval, board = approvals[watcher], watchers.WATCHERS[watcher]
        cap = _with_ref(captures[board], f"{home}/record.json#{watcher}")
        proposal = memory.propose(state0, approval.run_id, [cap])
        try:
            receipt = memory.commit(root, state_rel, approval, proposal, f"{home}/runs/{approval.run_id}",
                                    label="PREMORTEM", clock=clock)
            attempts[watcher] = {"run_id": approval.run_id, "approval": str(approval), "status": "committed",
                                 "receipt": receipt._asdict(), "at": clock()}
        except memory.StaleWrite as error:
            attempts[watcher] = {"run_id": approval.run_id, "approval": str(approval), "status": "refused",
                                 "expected": error.expected, "found": error.found, "message": str(error),
                                 "refusal_record": f"{home}/runs/{approval.run_id}/{memory.REFUSAL_FILE}",
                                 "at": clock()}
        except StateError as error:
            attempts[watcher] = {"run_id": approval.run_id, "approval": str(approval), "status": "not attempted",
                                 "message": str(error), "at": clock()}
        if watcher == watchers.ORDER[0]:
            after_first = (root / state_rel).read_bytes()
    after = (root / state_rel).read_bytes()
    final = json.loads(after.decode("utf-8"))
    record = {"label": "PREMORTEM TRIGGER (PREMORTEM.md lines 2-4), offline, on a disposable state file",
              "state": state_rel, "capture": capture,
              "started_from": {"revision": state0["revision"], "sha256": _sha(before)},
              "first": attempts[watchers.ORDER[0]], "second": attempts[watchers.ORDER[1]],
              "after_first_sha256": _sha(after_first), "after_refusal_sha256": _sha(after),
              "bytes_unchanged_by_refusal": after == after_first, "revision_after": final["revision"],
              "boards_after": sorted(final["boards"])}
    _write(root / home / "record.json", record)
    second = record["second"]
    lines = ["# Premortem trigger", "", record["label"] + ".", "",
             f"- Started from revision {record['started_from']['revision']} "
             f"(sha256 {record['started_from']['sha256'][:12]}…).",
             f"- First, `{record['first']['run_id']}`: {record['first']['status']}.",
             f"- Second, `{second['run_id']}`: {second['status']}"
             + (f" (expected revision {second['expected']['revision']}, found revision {second['found']['revision']})."
                if second["status"] == "refused" else "."),
             f"- The refusal left the file's bytes unchanged: {record['bytes_unchanged_by_refusal']} "
             f"(sha256 {record['after_first_sha256'][:12]}… before and {record['after_refusal_sha256'][:12]}… after).",
             f"- The state is at revision {record['revision_after']} with the boards {record['boards_after']}."]
    _write(root / home / "record.md", "\n".join(lines) + "\n")
    return record


def premortem_resume(root, state_rel, capture, watcher, approval, *, clock=None):
    """PREMORTEM.md line 5, after the plan owner's decision: reread the latest state, rebuild the refused
    watcher's update on it, and commit it under a new run ID and approval. Writes resume-<RUN_ID>.json
    and .md next to the disposable state, whatever the outcome."""
    root = Path(root).resolve()
    clock = clock or memory._utc_now
    _, _, captures, _, _ = _verify(root, capture)
    home = PurePosixPath(state_rel).parent
    board = watchers.WATCHERS[watcher]
    raw = (root / state_rel).read_bytes()
    state = json.loads(raw.decode("utf-8"))
    problem = memory.validate(state)
    if problem:
        raise StateError(f"{state_rel} is damaged: {problem}")
    cap = _with_ref(captures[board], f"{home}/resume-{approval.run_id}.json#{watcher}")
    proposal = memory.propose(state, approval.run_id, [cap])
    try:
        receipt = memory.commit(root, state_rel, approval, proposal, f"{home}/runs/{approval.run_id}",
                                label="PREMORTEM RESUME", clock=clock)
        outcome = {"status": "committed", "receipt": receipt._asdict()}
    except memory.StaleWrite as error:
        outcome = {"status": "refused", "expected": error.expected, "found": error.found, "message": str(error)}
    except StateError as error:
        outcome = {"status": "not committed", "message": str(error)}
    after_raw = (root / state_rel).read_bytes()
    after = json.loads(after_raw.decode("utf-8"))
    record = {"label": "PREMORTEM RESUME (PREMORTEM.md line 5), offline, on the disposable state file",
              "state": state_rel, "capture": capture, "watcher": watcher, "board": board, "run_id": approval.run_id,
              "approval": str(approval),
              "reread": {"revision": state["revision"], "sha256": _sha(raw), "boards": sorted(state["boards"])},
              **outcome,
              "earlier_facts_kept": after["facts"][:len(state["facts"])] == state["facts"],
              "revision_after": after["revision"], "sha256_after": _sha(after_raw),
              "boards_after": sorted(after["boards"]), "facts_after": len(after["facts"]), "at": clock()}
    _write(root / home / f"resume-{approval.run_id}.json", record)
    lines = ["# Premortem resume", "", record["label"] + ".", "",
             f"- Reread `{state_rel}`: revision {record['reread']['revision']} "
             f"(sha256 {record['reread']['sha256'][:12]}…), boards {record['reread']['boards']}.",
             f"- Rebuilt the {watcher} update ({board}) on that revision, as run `{approval.run_id}`: {record['status']}."]
    if record["status"] != "committed":
        lines.append(f"- {record['message']}")
    lines += [f"- Every earlier fact kept unchanged: {record['earlier_facts_kept']}.",
              f"- The state is at revision {record['revision_after']} (sha256 {record['sha256_after'][:12]}…) with "
              f"the boards {record['boards_after']} and {record['facts_after']} facts."]
    _write(root / home / f"resume-{approval.run_id}.md", "\n".join(lines) + "\n")
    return record


def _parser():
    parser = argparse.ArgumentParser(prog="python3 -m jobwatch.replay", description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    for name, text in (("receipt", "print the revision and SHA-256 an approval must name"),
                       ("init", "create an empty revision 0 state (never replaces one)")):
        command = commands.add_parser(name, help=text)
        command.add_argument("--state", default=STATE_PATH)
    run_command = commands.add_parser("run", help="one SEEDED replay of a saved capture")
    run_command.add_argument("--run-id", required=True)
    run_command.add_argument("--capture", required=True, metavar="runs/CAPTURE")
    run_command.add_argument("--earlier", action="append", default=[], metavar="runs/EARLIER")
    run_command.add_argument("--approve", type=memory.WriteApproval.parse, metavar="RUN_ID:PATH:REVISION:SHA256")
    run_command.add_argument("--closure", metavar="FIXTURE.json")
    trigger = commands.add_parser("premortem", help="trigger the premortem's stale write on a disposable state")
    trigger.add_argument("--capture", required=True, metavar="runs/CAPTURE")
    trigger.add_argument("--state", default=PREMORTEM_STATE)
    for watcher in watchers.ORDER:
        trigger.add_argument(f"--approve-{watcher}", required=True, type=memory.WriteApproval.parse,
                             metavar="RUN_ID:PATH:REVISION:SHA256")
    resume = commands.add_parser("premortem-resume",
                                 help="rebuild a refused premortem update on the latest revision (PREMORTEM.md line 5)")
    resume.add_argument("--capture", required=True, metavar="runs/CAPTURE")
    resume.add_argument("--watcher", required=True, choices=watchers.ORDER)
    resume.add_argument("--state", default=PREMORTEM_STATE)
    resume.add_argument("--approve", required=True, type=memory.WriteApproval.parse,
                        metavar="RUN_ID:PATH:REVISION:SHA256")
    return parser


def main(argv=None, *, root=None):
    args = _parser().parse_args(argv)
    root = Path(root) if root is not None else Path(__file__).resolve().parent.parent
    if args.command == "receipt":
        receipt = memory.receipt(root, args.state)
        print(f"{receipt.path}: revision {receipt.revision}, sha256 {receipt.sha256}")
        print(f"An approval for the next write names: RUN_ID:{receipt.path}:{receipt.revision}:{receipt.sha256}")
        return 0
    if args.command == "init":
        try:
            receipt = init_state(root, args.state)
        except StateError as error:
            print(error, file=sys.stderr)
            return 1
        print(f"created {receipt.path}: revision {receipt.revision}, sha256 {receipt.sha256}")
        return 0
    if args.command == "run":
        result = run(root, args.run_id, args.capture, earlier=args.earlier, approval=args.approve,
                     closure=args.closure)
        print(f"{result['run_id']}: {result['status']} (exit {result['exit']}). {result['reason']}")
        print(f"Evidence: {result['run_dir']}/")
        return result["exit"]
    if args.command == "premortem-resume":
        record = premortem_resume(root, args.state, args.capture, args.watcher, args.approve)
        print((root / PurePosixPath(args.state).parent / f"resume-{args.approve.run_id}.md").read_text(encoding="utf-8"),
              end="")
        return 0 if record["status"] == "committed" else 1
    record = premortem(root, args.state, args.capture,
                       {watcher: getattr(args, f"approve_{watcher}") for watcher in watchers.ORDER})
    print((root / PurePosixPath(args.state).parent / "record.md").read_text(encoding="utf-8"), end="")
    held = record["second"]["status"] == "refused" and record["bytes_unchanged_by_refusal"]
    return 0 if held else 1


if __name__ == "__main__":
    sys.exit(main())
