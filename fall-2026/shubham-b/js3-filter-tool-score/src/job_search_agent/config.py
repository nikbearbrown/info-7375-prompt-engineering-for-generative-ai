"""Loading and validating ``config/agent.toml``.

Relative paths in the file resolve against the *project root*: by default the
parent of the directory holding the config file (``config/agent.toml`` -> the
repository root). The data directory must lie inside the project root, and both
state files must lie inside the data directory (CONTRACT §3); anything else is a
``ConfigError`` before any work starts.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    model_validator,
)

from job_search_agent.errors import ConfigError, PathRejected
from job_search_agent.fsio import relative_within

DEFAULT_CONFIG_PATH = Path("config/agent.toml")
"""Default config location, relative to the current directory."""

ModelBackendKind = Literal["claude-cli", "none"]

_HostName = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$"
    ),
]
_NonEmpty = Annotated[str, StringConstraints(min_length=1)]


class _Section(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DataSettings(_Section):
    """``[data]``: the only write root and the state files inside it.

    Attributes:
        dir: Data directory, relative to the project root.
        state_file: Live state file, relative to ``dir``.
        seeded_state_file: Seeded (replay) state file, relative to ``dir``.
    """

    dir: _NonEmpty = "data"
    state_file: _NonEmpty = "live/state.json"
    seeded_state_file: _NonEmpty = "seeded/state.json"


class BoardSettings(_Section):
    """``[board]``: which provider and board to watch."""

    provider: _NonEmpty
    token: _NonEmpty


class HttpSettings(_Section):
    """``[http]``: allow-list and limits for the agent's own requests (CONTRACT §11)."""

    allowed_hosts: list[_HostName] = Field(min_length=1)
    timeout_s: float = Field(gt=0)
    max_bytes: int = Field(gt=0)
    max_redirects: int = Field(ge=0)
    user_agent: _NonEmpty


class ResumeSettings(_Section):
    """``[resume]``: fixture path and its pinned digest.

    Attributes:
        path: Fixture path, relative to the project root.
        pinned_sha256: Expected digest, or ``None`` when not set. A missing pin is not
            a config error: the résumé gate refuses with ``PIN_NOT_SET`` (§12).
    """

    path: _NonEmpty
    pinned_sha256: (
        Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None
    ) = None


class ModelSettings(_Section):
    """``[model]``: the judge backend."""

    backend: ModelBackendKind
    executable: _NonEmpty
    model_id: _NonEmpty
    timeout_s: float = Field(gt=0)
    prompt_version: Annotated[str, StringConstraints(pattern=r"^v[0-9]+$")]


@dataclass(frozen=True, slots=True)
class ConfigOverrides:
    """CLI overrides applied on top of the file before validation.

    Attributes:
        data_dir: Replaces ``[data].dir`` (``--data-dir``).
        model_backend: Replaces ``[model].backend`` (``--model-backend``).
    """

    data_dir: str | None = None
    model_backend: ModelBackendKind | None = None


class AgentConfig(_Section):
    """Validated configuration with resolved absolute paths.

    The absolute paths (``data_dir``, ``state_path``, ...) are for opening files only;
    anything written to outputs must use the relative strings from the sections.

    Raises:
        pydantic.ValidationError: If a path escapes its root (``load_config`` turns this
            into ``ConfigError``).
    """

    project_root: Path
    data: DataSettings = Field(default_factory=DataSettings)
    board: BoardSettings
    http: HttpSettings
    resume: ResumeSettings
    model: ModelSettings

    @property
    def data_dir(self) -> Path:
        """Absolute, resolved data directory."""
        return (self.project_root / self.data.dir).resolve()

    @property
    def state_path(self) -> Path:
        """Absolute, resolved live state file."""
        return (self.data_dir / self.data.state_file).resolve()

    @property
    def seeded_state_path(self) -> Path:
        """Absolute, resolved seeded state file."""
        return (self.data_dir / self.data.seeded_state_file).resolve()

    @property
    def resume_path(self) -> Path:
        """Absolute path of the résumé fixture (not resolved through symlinks)."""
        return self.project_root / self.resume.path

    def state_rel(self, *, seeded: bool) -> str:
        """Returns the state file path relative to the data dir (an ``OutputRoot`` rel).

        Computed lexically (symlinks are not followed), so a symlinked state file is
        later refused by ``OutputRoot`` instead of being resolved here.

        Args:
            seeded: Return the seeded state file instead of the live one.

        Returns:
            A POSIX path such as ``"live/state.json"``.
        """
        name = self.data.seeded_state_file if seeded else self.data.state_file
        return relative_within(name, self.data_dir, follow_symlinks=False)

    def repo_rel(self, data_rel: str) -> str:
        """Converts a data-dir-relative path to a repo-root-relative one.

        Args:
            data_rel: Path relative to the data dir, e.g. ``"live/runs/x/report.json"``.

        Returns:
            The repo-relative POSIX path, e.g. ``"data/live/runs/x/report.json"``.
        """
        data_dir_rel = self.data_dir.relative_to(self.project_root).as_posix()
        return (PurePosixPath(data_dir_rel) / data_rel).as_posix()

    @model_validator(mode="after")
    def _check_paths(self) -> Self:
        if not self.project_root.is_absolute():
            raise ValueError("project_root must be absolute")
        try:
            relative_within(self.data_dir, self.project_root)
        except PathRejected:
            raise ValueError(
                "data.dir must be a directory inside the project root"
            ) from None
        for name, path in (
            ("data.state_file", self.state_path),
            ("data.seeded_state_file", self.seeded_state_path),
        ):
            try:
                relative_within(path, self.data_dir)
            except PathRejected:
                raise ValueError(f"{name} must resolve inside data.dir") from None
        if self.state_path == self.seeded_state_path:
            raise ValueError("live and seeded state files must differ")
        return self


def _format_validation_error(exc: ValidationError) -> str:
    """Summarises a pydantic error as ``loc: message`` pairs (no input values)."""
    parts = []
    for err in exc.errors(include_input=False, include_url=False):
        loc = ".".join(str(p) for p in err["loc"]) or "<root>"
        parts.append(f"{loc}: {err['msg']}")
    return "; ".join(parts)


def load_config(
    path: Path = DEFAULT_CONFIG_PATH,
    *,
    project_root: Path | None = None,
    overrides: ConfigOverrides | None = None,
) -> AgentConfig:
    """Reads, overrides and validates the agent configuration.

    Args:
        path: The TOML file.
        project_root: Base for relative paths; defaults to the parent of the
            directory containing ``path``.
        overrides: Values that replace file values before validation.

    Returns:
        The validated configuration.

    Raises:
        ConfigError: If the file is missing or not TOML, a key is unknown or
            mistyped, or a path escapes its root (e.g. the state file outside the data
            directory).
    """
    try:
        with path.open("rb") as handle:
            raw = tomllib.load(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"config file not found: {path.name}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"config file is not valid TOML: {exc}") from exc

    root = (project_root or path.resolve().parent.parent).resolve()
    sections = {
        key: dict(value) for key, value in raw.items() if isinstance(value, dict)
    }
    scalars = sorted(key for key, value in raw.items() if not isinstance(value, dict))
    if scalars:
        raise ConfigError(f"unexpected top-level keys: {', '.join(scalars)}")

    if overrides is not None:
        _apply(sections, "data", "dir", overrides.data_dir)
        _apply(sections, "model", "backend", overrides.model_backend)

    try:
        return AgentConfig.model_validate({"project_root": root, **sections})
    except ValidationError as exc:
        raise ConfigError(f"invalid config: {_format_validation_error(exc)}") from exc


def _apply(
    sections: dict[str, dict[str, object]], section: str, key: str, value: str | None
) -> None:
    """Sets ``sections[section][key] = value`` when ``value`` is not ``None``."""
    if value is not None:
        sections.setdefault(section, {})[key] = value
