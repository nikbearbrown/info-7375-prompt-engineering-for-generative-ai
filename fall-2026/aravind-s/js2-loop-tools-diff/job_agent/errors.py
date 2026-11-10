"""The ways a run stops on purpose. The command line turns them into exit codes 3, 1 and 2."""


class Refused(Exception):
    """Something CONTRACT.md refuses (Refuses 1 and 2). Raised before any connection opens."""


class NoAnswer(Exception):
    """The board gave no answer at all (DNS, TLS, timeout). Nothing was saved and the state is unchanged."""


class BrokenInput(Exception):
    """An input the run cannot use (CONTRACT.md, In: "Broken input stops the run and changes no state")."""


# Layer 2 (GATE.md). A refused request or write stops the run with exit 3; an unverified board does not.

class NeedsApproval(Refused):
    """A write GATE.md allows only with --approve: replacing or deleting an existing board's state."""


class Unverified(Exception):
    """A board answer the loop cannot read (GATE.md, Error policy). The board's state stays as it was."""


class Redirected(Exception):
    """A board answered with a redirect. It is not followed, and the board is unverified."""


class BoardNoAnswer(NoAnswer):
    """No answer from one board (DNS, connection, timeout). `transient` says whether GATE.md allows a retry."""

    def __init__(self, message: str, transient: bool):
        super().__init__(message)
        self.transient = transient
