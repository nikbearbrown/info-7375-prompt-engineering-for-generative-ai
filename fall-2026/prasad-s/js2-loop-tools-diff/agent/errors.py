"""The two ways a run stops early.

A Refusal is an output (§3): the agent stops, logs the reason, and produces
no substitute verdict. A RunError is a failed run (bad file, network error).
Neither one writes state.json (§1 item 3).
"""


class Refusal(Exception):
    """The contract forbids this run or this fetch (§3)."""


class RunError(Exception):
    """The run could not finish; nothing is judged and state is not written."""
