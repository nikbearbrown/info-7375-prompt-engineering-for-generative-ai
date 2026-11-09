"""The one table of app error codes (GATE §1, JS2 D17): code -> stage, meaning, retry or not.

Why a table in code: GATE says failures are recorded as three-character codes and resolved to
messages "through one shared mapping when reporting". The loop records only the code; the summary,
the trace and ERROR_CODES.md (kept equal to this table by tests/test_loop.py) all read from here,
so a code can never mean two things in two places.

First digit = the stage where the failure happened (Isaac, JS2 D4): 0 inputs, 1 fetch, 2 validate,
3 judge (Claude, Step 5b), 4 output.
"""

from dataclasses import dataclass

from ..common.errors import AgentError, FetchError, InputError, MissingInputError
from ..common.policy import PolicyError

STAGES = {"0": "inputs", "1": "fetch", "2": "validate", "3": "judge", "4": "output"}


@dataclass(frozen=True)
class Code:
    code: str
    meaning: str
    retryable: bool    # GATE §4: only temporary failures may clear between attempts
    scope: str         # "run": the whole run stops with exit `error`; "board": only that board fails;
                       # "posting": only that posting's Claude verdict is an error, its rule verdict stands

    @property
    def stage(self) -> str:
        return STAGES[self.code[0]]


CODES = {c.code: c for c in [
    Code("001", "a required input file is missing", False, "run"),
    Code("002", "an input file is invalid", False, "run"),
    Code("003", "the board's state file is broken", False, "board"),
    Code("004", "an input or output was refused by the permission policy", False, "run"),
    Code("101", "board not found (HTTP 404)", False, "board"),
    Code("102", "the request timed out", True, "board"),
    Code("103", "could not connect", True, "board"),
    Code("104", "the board had a temporary failure (HTTP 5xx or 429)", True, "board"),
    Code("105", "the request was refused by the permission policy", False, "board"),
    Code("106", "the board refused the request (HTTP 4xx other than 404 and 429)", False, "board"),
    Code("201", "the board returned an empty job list", False, "board"),
    Code("202", "the board response has the wrong shape", False, "board"),
    Code("203", "the job list's length differs from the board's own total (meta.total)", False, "board"),
    Code("301", "the Claude call timed out", False, "posting"),
    Code("302", "the Claude judge could not run (no CLI or key, API error, empty job description)", False, "posting"),
    Code("303", "Claude's reply was rejected (validator, refusal, or cut off)", False, "posting"),
    Code("304", "the posting was not sent to Claude: the Claude budget (30 calls or 300 s) was used up", False, "posting"),
    Code("401", "the run record could not be written", False, "run"),
]}


def describe(code: str) -> str:
    """'101 fetch: board not found (HTTP 404)', the form every report uses."""
    c = CODES[code]
    return f"{c.code} {c.stage}: {c.meaning}"


def for_fetch(exc: Exception) -> str:
    """The code of one failed board request. Anything else raised while fetching is a bug and is
    not given a code, so it surfaces instead of being reported as an ordinary board failure."""
    if isinstance(exc, PolicyError):
        return "105"
    if isinstance(exc, FetchError):
        if exc.kind == "timeout":
            return "102"
        if exc.kind == "connection":
            return "103"
        if exc.status == 404:
            return "101"
        if exc.status == 429 or (exc.status or 0) >= 500:
            return "104"
        return "106"
    raise exc


def for_setup(exc: AgentError) -> str:
    """The code of a failure before the loop starts (inputs, board list, run folders)."""
    if isinstance(exc, MissingInputError):
        return "001"
    if isinstance(exc, InputError):
        return "002"
    if isinstance(exc, PolicyError):
        return "004"
    return "401"


def for_claude(failure: str) -> str:
    """The code of a failed Claude evaluation, from judges.claude's failure word."""
    return {"timeout": "301", "call": "302", "empty": "302", "rejected": "303"}[failure]
