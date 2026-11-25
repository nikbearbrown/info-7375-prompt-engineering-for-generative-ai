"""The optional Claude step (GATE §2, D1, D20): after every board is fetched, send every new posting
to Claude, in board order, until a Claude budget (30 calls, 300 s in total) runs out.

Why it is in the loop and not in judges/: the judge knows how to ask about one posting; *which*
postings, *how many* and *whether there is time* are budget decisions, recorded in the trace like
every board request. Why every new posting and not only the rule's relevant ones (D20, replacing
5b's filter): JS1's two judges exist to be compared on the same postings. If the rule picks what
Claude sees, Claude can never catch a posting the rule wrongly cut (D19). The budget is what limits
token use, not the rule.
"""

from dataclasses import dataclass, field

from ..common.errors import ClaudeCallError
from ..judges import claude, verdict
from ..judges.checks import Criteria
from . import codes
from .budget import Budget
from .results import BoardResult
from .trace import Trace


@dataclass
class ClaudeOutcome:
    by_board: dict[str, list[dict]] = field(default_factory=dict)   # board -> Claude verdicts
    raw: list[dict] = field(default_factory=list)                   # replies as received (claude_raw.jsonl)
    budget_stop: str | None = None                                  # set when a new posting was not sent


def selected(ok_boards: list[BoardResult]) -> list[tuple[BoardResult, object]]:
    """(board, posting) pairs to send: every new posting, in board-list order and then posting order,
    whatever the rule said (D20). Deterministic, so a rerun on the same raw responses sends the same
    postings first; the budget, not this list, decides where sending stops."""
    return [(b, posting) for b in ok_boards for posting in b.watch.new]


def run_claude(ok_boards: list[BoardResult], criteria: Criteria, make_ask, prompt: claude.Prompt,
               budget: Budget, trace: Trace) -> ClaudeOutcome:
    """make_ask(timeout_s) builds the real Claude call (or a test's fake). It is built per call,
    because each call's timeout is the Claude time left (D20), and only when there is a new posting,
    so a run with nothing new never needs Claude installed."""
    out = ClaudeOutcome()
    cannot_run = ""
    for b, posting in selected(ok_boards):
        stop = budget.stops_claude()
        if stop:
            # GATE §2: report every new posting not sent because a Claude budget ran out; the rule verdict stands.
            out.budget_stop = stop
            _record(out, trace, b, verdict.error(claude.JUDGE, posting.id, f"not sent: {stop} budget used up"),
                    {"posting_id": posting.id, "error": "not sent"}, "304", 0.0)
            continue
        if not cannot_run:
            try:
                ask = make_ask(budget.claude_seconds_left())
            except ClaudeCallError as e:
                cannot_run = str(e)
            except ImportError:
                cannot_run = "the anthropic package is not installed (pip install -r requirements.txt)"
        if cannot_run:
            # Not counted as a call: nothing reached Claude, so no tokens or Claude time were spent.
            _record(out, trace, b, verdict.error(claude.JUDGE, posting.id, cannot_run),
                    {"posting_id": posting.id, "error": cannot_run}, "302", 0.0)
            continue
        budget.start_claude()
        started = budget.clock()
        result = claude.judge(posting, criteria, ask, prompt)
        spent = budget.clock() - started
        budget.end_claude(spent)
        code = codes.for_claude(result.failure) if result.failure else None
        _record(out, trace, b, result.verdict, result.raw, code, spent)
    return out


def _record(out: ClaudeOutcome, trace: Trace, b: BoardResult, v: dict, raw: dict, code: str | None,
            seconds: float) -> None:
    if code:
        v = {**v, "error_code": code}    # the same three-digit code the boards use (GATE §1)
    out.by_board.setdefault(b.board, []).append(v)
    out.raw.append({**raw, "board": b.board})
    trace.claude_call(b.board, v["posting_id"], code, seconds)
