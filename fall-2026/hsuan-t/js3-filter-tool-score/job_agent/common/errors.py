"""One error family for every CONTRACT "report the error and stop" case.

The CLI catches AgentError once instead of listing each module's error type, so a new module
(e.g. the Claude judge in Step 5) adds a subclass without touching the CLI.
"""


class AgentError(Exception):
    """Base: the run stops and the message is shown to the user."""


class InputError(AgentError):
    """A résumé, profile or built-in data file is malformed (GATE code 002)."""


class MissingInputError(InputError):
    """A required input file does not exist (GATE code 001). A subclass, so code that only cares
    "the inputs are bad" still catches InputError, while the loop can report the exact code."""


class WatchError(AgentError):
    """Fetching the board, reading the state, or a board response of the wrong shape."""


class CountMismatchError(WatchError):
    """The board's job list is well-formed but its length differs from the board's own count
    (Greenhouse meta.total), JS2 D21. A subclass so the loop can give it its own code (203)
    instead of 202: the shape is right, the content can't be trusted. Without it, a list missing
    postings ends `ok` and "0 new" (Step 7 demo)."""


class FetchError(WatchError):
    """One board request failed. kind ("http" / "timeout" / "connection") and status (the HTTP
    status, if any) are kept as data, not only in the message, because the loop's retry rule and
    error code depend on them (GATE §3-§4) and parsing them back out of text would be fragile.
    body is what the server sent with an HTTP error, saved as evidence (a 404 page, a 503 note)."""

    def __init__(self, message: str, kind: str, status: int | None = None, body: bytes = b""):
        super().__init__(message)
        self.kind, self.status, self.body = kind, status, body


class ClaudeCallError(Exception):
    """One Claude request failed (network, rate limit, refusal, no API key).

    Deliberately NOT an AgentError: CONTRACT In says a missing key or a failed Claude call makes the
    Claude judge report an error while the rule judge carries on, so it becomes that posting's
    status "error" verdict instead of stopping the run.

    timed_out separates "took longer than its 300 s" (GATE code 301) from every other failure
    (302), because GATE §2 budgets time per call and the trace must say which one happened.
    """

    def __init__(self, message: str, timed_out: bool = False):
        super().__init__(message)
        self.timed_out = timed_out
