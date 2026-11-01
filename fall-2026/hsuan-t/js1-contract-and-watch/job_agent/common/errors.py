"""One error family for every CONTRACT "report the error and stop" case.

The CLI catches AgentError once instead of listing each module's error type, so a new module
(e.g. the Claude judge in Step 5) adds a subclass without touching the CLI.
"""


class AgentError(Exception):
    """Base: the run stops and the message is shown to the user."""


class InputError(AgentError):
    """A résumé, profile or built-in data file is missing or malformed."""


class WatchError(AgentError):
    """Fetching the board, reading the state, or a refused host."""


class ClaudeCallError(Exception):
    """One Claude request failed (network, rate limit, refusal, no API key).

    Deliberately NOT an AgentError: CONTRACT In says a missing key or a failed Claude call makes the
    Claude judge report an error while the rule judge carries on, so it becomes that posting's
    status "error" verdict instead of stopping the run.
    """
