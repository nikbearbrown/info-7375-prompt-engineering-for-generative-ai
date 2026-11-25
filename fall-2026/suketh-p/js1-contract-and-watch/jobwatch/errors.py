"""Every way a run can stop. A run that raises one of these leaves the state file as it was."""


class AgentError(Exception):
    """Base class: the run stopped without advancing the state."""


class InputError(AgentError):
    """The résumé or the board response broke the input contract."""


class StateError(AgentError):
    """The state file exists but is damaged. The agent will not start another baseline."""


class FetchError(AgentError):
    """The board could not be fetched."""


class RefusedError(AgentError):
    """A request the allow-list does not permit."""


class JudgeError(AgentError):
    """The model call failed, or its reply broke the output contract."""

    def __init__(self, message, reply=None):
        super().__init__(message)
        self.reply = reply
