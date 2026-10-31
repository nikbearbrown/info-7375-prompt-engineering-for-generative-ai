"""Exit codes from CONTRACT.md Interfaces, and the exception that ends a run with one."""

OK = 0
OTHER = 1
REFUSED = 2
NETWORK = 3
CORRUPT_STATE = 4
BAD_RULE_VERDICT = 5


class Stop(Exception):
    """Ends a run with `code`. The message must never contain a résumé value."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
