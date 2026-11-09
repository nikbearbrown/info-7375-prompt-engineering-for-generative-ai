"""Typed errors. Every permission denial is raised before the guarded operation starts."""


class AgentError(Exception):
    """Base class for errors the agent reports."""


class ConfigError(AgentError):
    """An unknown provider or a board token that fails the F7 token check."""


class PermissionDenied(AgentError):
    """A policy check refused an operation before it happened."""


class RequestDenied(PermissionDenied):
    """An outbound request was refused before any transport call."""


class ReadDenied(PermissionDenied):
    """A local read was refused before the file was opened."""


class WriteDenied(PermissionDenied):
    """A local write was refused before the destination was opened."""


class TransportError(AgentError):
    """The transport call failed before a complete HTTP response arrived."""


class TransportTimeout(TransportError):
    """The transport call timed out."""
