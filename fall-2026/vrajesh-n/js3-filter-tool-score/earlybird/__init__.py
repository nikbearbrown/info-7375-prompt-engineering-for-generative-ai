"""Early Bird, JS2 slice: a bounded loop over many boards, with tools under a code-enforced policy."""


class Refused(Exception):
    """A permission or contract refusal (GATE.md). The loop stops the whole run on one: exit `error`."""
