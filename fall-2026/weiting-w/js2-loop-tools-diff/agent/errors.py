"""Every refusal and every failure the gate names, as one class each.

GATE.md §4 classifies a failure before acting on it, so the class of the
exception *is* the classification. Nothing in this package decides what to do
about a failure by reading an error message.
"""


class AgentError(Exception):
    """Base class. Carries the classification the error policy switches on."""

    #: one of GATE.md §4: transient | permanent | schema | policy | budget
    classification = "permanent"
    exit_code = 2


# --- GATE.md §5: permission policy. Classification `policy` aborts the run. ---

class PolicyRefusal(AgentError):
    classification = "policy"


class DisallowedHost(PolicyRefusal):
    """R5.1: host is not on the allow-list."""


class DisallowedScheme(PolicyRefusal):
    """R5.1: scheme is not https."""


class DisallowedPort(PolicyRefusal):
    """R5.1: port is neither absent nor 443."""


class MethodNotAllowed(PolicyRefusal):
    """R5.1: only GET exists in this package."""


class PathEscapes(PolicyRefusal):
    """R5.2: the resolved real path is not inside the permitted root."""


class RefusedRealResume(PolicyRefusal):
    """R5.2: a path matching *.real.json. Carried over from JS1 R2."""


class NeedsApproval(PolicyRefusal):
    """R5.3: an overwrite of saved raw evidence, without --approve-overwrite."""


# --- GATE.md §3: the repeat rule. Also classification `policy`. ---

class RepeatedAction(PolicyRefusal):
    """The same (method, url) twice in one run."""


# --- GATE.md §4: faults in the world, not in the plan. ---

class TransientFailure(AgentError):
    classification = "transient"


class PermanentFailure(AgentError):
    classification = "permanent"


class SchemaFailure(AgentError):
    classification = "schema"


class BudgetExhausted(AgentError):
    classification = "budget"


# --- Carried over from JS1 unchanged in meaning. ---

class NonPersonaResume(AgentError):
    """The resume given is not a validated fictional persona."""


class ValidatorRejected(AgentError):
    """A model's output did not meet the prompt contract's output format."""
