"""The ways a run stops on purpose. The command line turns them into exit codes 3, 1 and 2."""


class Refused(Exception):
    """Something CONTRACT.md refuses (Refuses 1 and 2). Raised before any connection opens."""


class NoAnswer(Exception):
    """The board gave no answer at all (DNS, TLS, timeout). Nothing was saved and the state is unchanged."""


class BrokenInput(Exception):
    """An input the run cannot use (CONTRACT.md, In: "Broken input stops the run and changes no state")."""
