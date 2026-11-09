"""Errors that carry a reason. The loop turns them into an exit status (jobwatch/loop.py);
an expected exit is a status, never an unhandled exception."""


class AgentError(Exception):
    """Base class."""


class InputError(AgentError):
    """The résumé or a board response broke its input contract."""


class StateError(AgentError):
    """The state file exists but is damaged. The agent will not start another baseline."""


class PolicyDenied(AgentError):
    """The permission policy refused a request or a file operation (GATE.md 'Permission
    policy'). `rule` names the check that fired."""

    def __init__(self, rule, detail):
        super().__init__(f"refused by the permission policy ({rule}): {detail}")
        self.rule = rule
        self.detail = detail
