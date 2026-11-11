"""The bounded loop over the board list (JS2 Step 5): one board after another, under the budgets,
with GATE's retry, repeat and error rules, and a trace row for everything it observes.

Why a separate module from the pipeline: the pipeline is the order of a run (inputs -> boards ->
judges -> report -> state); this is what happens *inside* "boards", where every decision (try
again? skip? stop?) comes from GATE §2-§4 and must be testable without writing a report.
"""

import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..common import net
from ..common.errors import CountMismatchError, FetchError, WatchError
from ..common.paths import Paths
from ..common.policy import Policy, PolicyError
from ..judges.checks import Criteria
from ..judges import rule
from ..watch import watcher
from ..watch.board_list import Board
from . import codes
from .budget import Budget
from .results import FAILED, OK, SKIPPED, BoardResult
from .trace import Trace

MAX_ATTEMPTS = 3   # GATE §3: the initial request plus at most two retries


class RunStopped(Exception):
    """A shared failure (GATE §4: e.g. the run record can't be written): the rest of the run
    depends on the same resource, so the loop stops and the run ends with exit `error`."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass
class Context:
    """What every board in one run shares."""
    paths: Paths
    policy: Policy
    criteria: Criteria
    now: datetime
    raw_folder: Path
    budget: Budget
    trace: Trace
    fetcher: object = None          # tests inject a fake; None = the real network through net.http_get
    from_raw: Path | None = None    # replay a saved response instead of fetching (one board only)
    clock: object = time.monotonic


def run_boards(boards: list[Board], ctx: Context) -> tuple[list[BoardResult], str | None]:
    """(a result for every board in list order, the shared failure that stopped the run or None).

    Ctrl-C marks the board in progress and the rest `skipped` (GATE §1: interrupted by the user)
    instead of losing the boards already done. A shared failure fails the board it happened on,
    skips the rest, and is returned so the exit becomes `error` (GATE §4)."""
    results: list[BoardResult] = []
    requested: set[str] = set()
    shared = None

    def end(*ended: BoardResult) -> None:
        # Traced the moment a board ends, so the trace reads in the order things happened.
        for r in ended:
            results.append(r)
            ctx.trace.board_end(r.row())

    for i, board in enumerate(boards):
        try:
            end(_one_board(board, ctx, requested))
        except KeyboardInterrupt:
            end(*[BoardResult(b.name, b.ats, SKIPPED, reason="interrupted by the user") for b in boards[i:]])
            break
        except RunStopped as e:
            shared = f"{codes.describe(e.code)}: {e}"
            end(BoardResult(board.name, board.ats, FAILED, e.code, str(e)),
                *[BoardResult(b.name, b.ats, SKIPPED, reason="run stopped by a shared failure") for b in boards[i + 1:]])
            break
    return results, shared


def _one_board(board: Board, ctx: Context, requested: set[str]) -> BoardResult:
    stop = ctx.budget.stops_board()
    if stop:
        return BoardResult(board.name, board.ats, SKIPPED, reason=f"{stop} budget used up", budget=stop)
    ctx.budget.start_board()

    try:
        previous = watcher.load_previous(ctx.paths.state(board.name), board.name, board.adapter.ID_TYPE, ctx.policy)
    except PolicyError as e:
        return BoardResult(board.name, board.ats, FAILED, "105", str(e))
    except WatchError as e:
        # Board scope (GATE §4, JS2 D8): one board's broken state must not stop the others, and
        # the file is left as it is so nobody's history is silently replaced by a new baseline.
        return BoardResult(board.name, board.ats, FAILED, "003", str(e))

    if ctx.from_raw is not None:
        body, attempts, source = ctx.policy.check_read(ctx.from_raw).read_bytes(), 0, "seeded"
        raw_path = ctx.from_raw
    else:
        url = board.adapter.board_url(board.slug)
        if url in requested:
            # GATE §3; the board list already refuses two entries for one board, so this guards
            # against the loop itself being changed to visit a board twice.
            ctx.trace.repeat(board.name, "url", url)
            return BoardResult(board.name, board.ats, SKIPPED, reason=f"repeat of an earlier request: {url}")
        requested.add(url)
        got = _fetch(board, url, ctx)
        if isinstance(got, BoardResult):
            return got
        body, headers, attempts = got
        source = "live"
        try:
            raw_path = watcher.save_raw(ctx.raw_folder, board.name, body, headers, ctx.policy)
        except (PolicyError, OSError) as e:
            raise RunStopped("401", f"could not save the raw response: {e}") from e

    try:
        postings = board.adapter.parse(body)
    except CountMismatchError as e:
        # JS2 D21: before WatchError, which it subclasses, so it is not reported as a wrong shape.
        return BoardResult(board.name, board.ats, FAILED, "203", str(e), attempts=attempts)
    except WatchError as e:
        return BoardResult(board.name, board.ats, FAILED, "202", str(e), attempts=attempts)
    if not postings:
        # GATE WV3: an empty list is not "0 jobs", it is a response we can't trust.
        return BoardResult(board.name, board.ats, FAILED, "201", "the job list is empty", attempts=attempts)

    postings = _drop_repeats(board, postings, ctx.trace)
    w = watcher.observe(board.name, postings, previous, raw_path, source, ctx.now)
    rule_results = [rule.judge(p, ctx.criteria) for p in w.new]
    return BoardResult(board.name, board.ats, OK, attempts=attempts, watch=w, rule_results=rule_results)


def _fetch(board: Board, url: str, ctx: Context):
    """(body, headers, attempts) or the board's failed/skipped result.

    GATE §3-§4: a code that can't clear by waiting (404, refused, 403) ends the board at once.
    A retryable one is tried again; if the retry fails the same way, stop; if it fails with a
    different retryable code, one final try. Retryability is checked before comparing codes, so
    timeout -> 404 ends the board immediately."""
    last: str | None = None
    attempt = 0
    while True:
        stop = ctx.budget.stops_request()
        if stop:
            if attempt == 0:
                return BoardResult(board.name, board.ats, SKIPPED, reason=f"{stop} budget used up", budget=stop)
            return BoardResult(board.name, board.ats, FAILED, last, f"retry not attempted: {stop} budget used up",
                               budget=stop, attempts=attempt)
        attempt += 1
        timeout = ctx.budget.start_request()
        started = ctx.clock()
        try:
            ctx.policy.check_url(url)      # also for an injected fetcher, which skips net.http_get
            body, headers = ctx.fetcher(url) if ctx.fetcher else net.http_get(url, ctx.policy, timeout)
        except (FetchError, PolicyError) as e:
            code = codes.for_fetch(e)
            ctx.trace.request(board.name, url, attempt, getattr(e, "status", None), code,
                              ctx.clock() - started, len(getattr(e, "body", b"")), ctx.budget.snapshot())
            if getattr(e, "body", b""):
                try:
                    watcher.save_failed_attempt(ctx.raw_folder, board.name, attempt, e.body, ctx.policy)
                except (PolicyError, OSError) as err:
                    raise RunStopped("401", f"could not save the failed response: {err}") from err
            same_again = attempt >= 2 and code == last
            if not codes.CODES[code].retryable or same_again or attempt >= MAX_ATTEMPTS:
                return BoardResult(board.name, board.ats, FAILED, code, str(e), attempts=attempt)
            last = code
            continue
        ctx.trace.request(board.name, url, attempt, _status(headers), None,
                          ctx.clock() - started, len(body), ctx.budget.snapshot())
        return body, headers, attempt


def _status(headers: str) -> int | None:
    """The HTTP status from net.http_get's first header line ("HTTP 200"); fakes may send none."""
    first = headers.split("\n", 1)[0].split()
    return int(first[1]) if len(first) == 2 and first[0] == "HTTP" and first[1].isdigit() else None


def _drop_repeats(board: Board, postings: list, trace: Trace) -> list:
    """GATE §3: a posting is (source, board, job id); one listed twice in a response is processed
    once. The board is part of the key, so the same id on two boards is two postings (GATE WV1)."""
    seen, kept = set(), []
    for p in postings:
        key = (board.ats, board.name, p.id)
        if key in seen:
            trace.repeat(board.name, "posting", "/".join(map(str, key)))
            continue
        seen.add(key)
        kept.append(p)
    return kept
