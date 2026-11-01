"""Shared enums, records and value types (changes are additive only).

Conventions used throughout this module:

* **Persisted documents are pydantic models** (``FrozenModel``: ``extra="forbid"``,
  immutable). They round-trip through ``model_dump_json`` / ``model_validate_json``.
  Enum fields serialise to their string values.
* **In-memory port values are frozen dataclasses** (``Posting``, ``FetchResult``,
  ``SourceResult``, ``ParsedBoard``, ``Availability``, ``BackendReply``,
  ``CompletedCommand``, ``JudgmentOutcome``). They may hold bytes or raw JSON and are
  never written to disk as-is.
* **Paths stored in persisted documents are repo-root-relative POSIX strings**
  (``RepoPath``), e.g.
  ``"data/live/runs/2026-10-30T02-11-07Z/raw/greenhouse-stripe.json"``
  or ``"evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json"``. They are never
  absolute, so outputs never leak a home directory. Paths handed to
  ``fsio.OutputRoot`` are relative to the data directory instead; the two kinds are
  kept apart by name (``*_ref`` / ``path`` here, ``rel`` in ``fsio``).
* **Posting IDs are canonical decimal strings** of a positive JSON integer (A31).
* **Timestamps are timezone-aware.** ``*_utc`` fields are UTC; ``*_et`` fields are the
  same instant in America/New_York (A22).
* Models record facts; they do not enforce rule semantics. For example a
  ``RuleVerdict`` with ``MATCH`` and a non-US location can be constructed, because the
  evidence validator must be able to see and reject it. The only invariants
  enforced here are structural ones that no correct or deliberately wrong rule needs
  to violate (status/label consistency of a judgment, state-file integrity).
"""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Any, Literal, Self, final

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

# --- enums ------------------------------------------------------------------


class LocationLabel(StrEnum):
    """Result of the CONTRACT §6.4 US-based location check."""

    US_BASED = "US_BASED"
    NON_US = "NON_US"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


class VerdictLabel(StrEnum):
    """Deterministic rule verdict (CONTRACT §6.5)."""

    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"


class Gate(StrEnum):
    """The four §6.5 conditions, in contract order; failed ones are all recorded."""

    TITLE = "TITLE"
    SKILLS = "SKILLS"
    EXCLUSION = "EXCLUSION"
    LOCATION = "LOCATION"


class JudgmentStatus(StrEnum):
    """Outcome of a Claude judgment (CONTRACT §8).

    ``UNAVAILABLE`` means no call was attempted; ``ERROR`` means a call was attempted
    and failed; ``INVALID_OUTPUT`` means two replies both failed validation.
    """

    VALID = "VALID"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    ERROR = "ERROR"
    UNAVAILABLE = "UNAVAILABLE"


class RunStatus(StrEnum):
    """The seven run statuses of CONTRACT §9; precedence is PLAN §1.4."""

    BASELINE = "BASELINE"
    SUCCESS_WITH_NEW = "SUCCESS_WITH_NEW"
    SUCCESS_NO_NEW = "SUCCESS_NO_NEW"
    FETCH_FAILED = "FETCH_FAILED"
    EMPTY_RESPONSE = "EMPTY_RESPONSE"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    PARTIAL_FAILURE = "PARTIAL_FAILURE"


class FetchKind(StrEnum):
    """Coarse outcome of obtaining and parsing the board (``status.explain_status``)."""

    OK = "OK"
    FAILED = "FAILED"
    EMPTY = "EMPTY"
    INVALID = "INVALID"


class FetchErrorKind(StrEnum):
    """Why obtaining the raw response failed. Every kind maps to ``FETCH_FAILED``."""

    TRANSPORT = "TRANSPORT"
    """Connection, DNS or TLS failure."""
    TIMEOUT = "TIMEOUT"
    HTTP_STATUS = "HTTP_STATUS"
    """A non-2xx status, including 429 (never retried)."""
    HOST_REJECTED = "HOST_REJECTED"
    """The allow-list transport refused the URL (scheme, host, port or userinfo)."""
    REDIRECT_REJECTED = "REDIRECT_REJECTED"
    """A redirect pointed outside the allow-list."""
    TOO_MANY_REDIRECTS = "TOO_MANY_REDIRECTS"
    SIZE_CAP = "SIZE_CAP"
    """The body exceeded ``http.max_bytes``."""
    REPLAY_UNREADABLE = "REPLAY_UNREADABLE"
    """Replay: the saved raw file or its meta could not be read under ``ReadPolicy``."""
    REPLAY_DIGEST_MISMATCH = "REPLAY_DIGEST_MISMATCH"
    """Replay: the saved raw file's sha256 differs from its ``.meta.json``."""


class SourceKind(StrEnum):
    """Where a raw response came from; written as ``source`` in raw meta files."""

    NETWORK = "network"
    REPLAY = "replay"


class RunMode(StrEnum):
    """Run mode as written in ``report.json``. A replay run is always seeded."""

    LIVE = "live"
    REPLAY = "replay"


class DataQualityCode(StrEnum):
    """Per-posting problems found while parsing a structurally valid board."""

    MISSING_ID = "MISSING_ID"
    INVALID_ID = "INVALID_ID"
    """Present but not a positive JSON integer (bools and strings included, A31)."""
    DUPLICATE_ID = "DUPLICATE_ID"
    NOT_AN_OBJECT = "NOT_AN_OBJECT"
    """A ``jobs`` entry that is not a JSON object."""
    WRONG_FIELD_TYPE = "WRONG_FIELD_TYPE"
    """An optional field of the wrong type; it contributes an empty value."""
    MISSING_LOCATION = "MISSING_LOCATION"
    """``$.location.name`` absent (A30); the location label is NOT_ESTABLISHED."""
    TOTAL_MISMATCH = "TOTAL_MISMATCH"
    """``meta.total`` differs from ``len(jobs)`` (A21, warning only)."""


class Severity(StrEnum):
    """Severity of a data-quality issue.

    ``ERROR`` issues make a non-baseline run ``PARTIAL_FAILURE`` (A19); ``WARNING``
    issues are reported only.
    """

    ERROR = "ERROR"
    WARNING = "WARNING"


class RefusalCode(StrEnum):
    """Reasons the résumé gate refuses a fixture (§12); messages carry codes only."""

    PIN_NOT_SET = "PIN_NOT_SET"
    UNREADABLE = "UNREADABLE"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    NOT_JSON = "NOT_JSON"
    NOT_FICTIONAL = "NOT_FICTIONAL"
    """``$.fictional`` missing or not exactly JSON ``true``."""
    EMAIL_DOMAIN = "EMAIL_DOMAIN"
    PHONE_PATTERN = "PHONE_PATTERN"
    MISSING_FIELD = "MISSING_FIELD"
    """A required persona or résumé field is absent or has the wrong type (A13)."""
    PERSONA_MISMATCH = "PERSONA_MISMATCH"
    """``$.personal.name`` is present but is not the approved persona."""


class BackendErrorKind(StrEnum):
    """Why a model call failed.

    ``CLI_NOT_FOUND`` and ``WORKDIR_FAILED`` (``PRE_SPAWN_ERRORS``) mean no process
    was started, so the judgment is ``UNAVAILABLE`` (CONTRACT §8: "If no model call
    can be made, the status is UNAVAILABLE"). Every other kind is a call that was
    attempted and failed, so the judgment is ``ERROR``.
    """

    CLI_NOT_FOUND = "CLI_NOT_FOUND"
    """The executable was not on ``PATH`` at call time (no process started)."""
    WORKDIR_FAILED = "WORKDIR_FAILED"
    """The per-call empty working directory could not be made (no process started)."""
    SPAWN_FAILED = "SPAWN_FAILED"
    TIMEOUT = "TIMEOUT"
    NONZERO_EXIT = "NONZERO_EXIT"
    ENVELOPE_NOT_JSON = "ENVELOPE_NOT_JSON"
    ENVELOPE_SHAPE = "ENVELOPE_SHAPE"
    """The CLI's JSON envelope lacks the expected fields."""
    IS_ERROR = "IS_ERROR"
    """The envelope reports ``is_error: true``."""


PRE_SPAWN_ERRORS: frozenset[BackendErrorKind] = frozenset(
    {BackendErrorKind.CLI_NOT_FOUND, BackendErrorKind.WORKDIR_FAILED}
)
"""Backend errors raised before any process started: the judgment is UNAVAILABLE."""


class ExitCode(IntEnum):
    """Process exit codes of ``jsa`` (PLAN §1.4).

    ``EXPERIMENT_REFUSED`` (6) is ``jsa exp ...`` refusing at an ordering gate or
    input check. ``LOCKED`` (7) means another ``jsa`` process holds the data lock
    for the same mode (``data/<live|seeded>/.lock``), or a run with the same
    one-second run ID already exists; nothing was fetched or written, so the command
    can simply be retried.
    """

    OK = 0
    PARTIAL_FAILURE = 1
    FETCH_OR_RESPONSE = 2
    RESUME_REFUSED = 3
    STATE_CORRUPT = 4
    CONFIG_ERROR = 5
    EXPERIMENT_REFUSED = 6
    LOCKED = 7


_STATUS_EXIT_CODES: Mapping[RunStatus, ExitCode] = {
    RunStatus.BASELINE: ExitCode.OK,
    RunStatus.SUCCESS_WITH_NEW: ExitCode.OK,
    RunStatus.SUCCESS_NO_NEW: ExitCode.OK,
    RunStatus.PARTIAL_FAILURE: ExitCode.PARTIAL_FAILURE,
    RunStatus.FETCH_FAILED: ExitCode.FETCH_OR_RESPONSE,
    RunStatus.EMPTY_RESPONSE: ExitCode.FETCH_OR_RESPONSE,
    RunStatus.INVALID_RESPONSE: ExitCode.FETCH_OR_RESPONSE,
}


def exit_code_for_status(status: RunStatus) -> ExitCode:
    """Maps a run status to the process exit code.

    Args:
        status: The decided run status.

    Returns:
        ``OK`` for BASELINE and SUCCESS_*, ``PARTIAL_FAILURE`` for PARTIAL_FAILURE and
        ``FETCH_OR_RESPONSE`` for FETCH_FAILED, EMPTY_RESPONSE and INVALID_RESPONSE.
    """
    return _STATUS_EXIT_CODES[status]


# --- scalar types -----------------------------------------------------------

ModelLabel = Literal["RELEVANT", "NOT_RELEVANT"]
"""Claude's two allowed labels (CONTRACT §8). RELEVANT corresponds to MATCH (§16).

A ``Literal`` rather than an enum so that ``JudgmentReply.model_validate(obj,
strict=True)`` accepts the plain JSON string.
"""

Sha256Hex = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
"""Lowercase hexadecimal SHA-256 digest."""

PostingId = Annotated[str, StringConstraints(pattern=r"^[1-9][0-9]*$")]
"""Canonical decimal string of a positive integer posting ID."""

RUN_ID_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z(-SEEDED)?$"
"""``YYYY-MM-DDTHH-MM-SSZ`` in UTC, with ``-SEEDED`` appended for replay runs."""

RunId = Annotated[str, StringConstraints(pattern=RUN_ID_PATTERN)]

_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


def _check_repo_path(value: str) -> str:
    """Validates a repo-root-relative POSIX path.

    Args:
        value: Candidate path string.

    Returns:
        The unchanged value.

    Raises:
        ValueError: If the path is empty, absolute, contains ``..``, a backslash, a NUL
            byte or a drive letter, or is not in canonical form (``./a``, ``a//b``).
    """
    if not value or "\x00" in value or "\\" in value or value.startswith("~"):
        raise ValueError("path must be a non-empty relative POSIX path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or _WINDOWS_DRIVE.match(value):
        raise ValueError("path must be relative to the repository root")
    if ".." in pure.parts:
        raise ValueError("path must not contain '..'")
    if str(pure) != value:
        raise ValueError("path must be in canonical form")
    return value


RepoPath = Annotated[str, AfterValidator(_check_repo_path)]
"""Repo-root-relative POSIX path; never absolute, never escaping the repository."""

NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]


class FrozenModel(BaseModel):
    """Base for persisted documents: unknown keys rejected, instances immutable."""

    model_config = ConfigDict(extra="forbid", frozen=True)


# --- inputs -----------------------------------------------------------------


@final
class VerifiedResume:
    """Opaque proof that a résumé passed every CONTRACT §12 check.

    Only ``resume.load_verified_resume`` may construct one; every other module
    receives it. This is enforced: the constructor requires ``token``, a
    module-private sentinel owned by ``resume`` (``resume._GATE_TOKEN``), so a direct
    ``VerifiedResume(...)`` raises ``TypeError`` (review fix 6). The judge accepts
    nothing else (it also checks the type at runtime), so unverified résumé content
    cannot reach a model. The parsed JSON is held privately and handed out only as a
    deep copy, and ``repr`` shows no résumé content, so a stray log line or traceback
    cannot print it (§12).

    Args:
        data: The parsed résumé JSON object. It is deep-copied.
        sha256: The verified digest of the exact fixture bytes.
        source_path: Repo-relative path of the fixture that was verified.
        token: The résumé gate's private sentinel.

    Raises:
        TypeError: If ``token`` is not the résumé gate's sentinel.
        ValueError: If ``sha256`` is not a lowercase hex digest or ``source_path`` is
            not a repo-relative path.
    """

    __slots__ = ("_data", "_sha256", "_source_path")

    def __init__(
        self,
        data: Mapping[str, Any],
        *,
        sha256: str,
        source_path: str,
        token: object = None,
    ) -> None:
        # Imported here: ``resume`` imports this module, and owns the sentinel.
        from job_search_agent.resume import _GATE_TOKEN  # noqa: PLC0415

        if token is not _GATE_TOKEN:
            raise TypeError(
                "a VerifiedResume is built only by resume.load_verified_resume"
            )
        if not re.fullmatch(r"[0-9a-f]{64}", sha256):
            raise ValueError("sha256 must be a lowercase hex digest")
        self._source_path: str = _check_repo_path(source_path)
        self._sha256: str = sha256
        self._data: dict[str, Any] = copy.deepcopy(dict(data))

    @property
    def sha256(self) -> str:
        """The verified SHA-256 of the fixture bytes."""
        return self._sha256

    @property
    def source_path(self) -> str:
        """Repo-relative path of the verified fixture."""
        return self._source_path

    def to_dict(self) -> dict[str, Any]:
        """Returns a deep copy of the parsed résumé JSON.

        Returns:
            A fresh, independently mutable copy; changing it never changes this object.
        """
        return copy.deepcopy(self._data)

    def __repr__(self) -> str:
        """Returns a content-free representation (digest prefix and path only)."""
        return (
            f"VerifiedResume(sha256={self._sha256[:16]}..., path={self._source_path})"
        )


@dataclass(frozen=True, slots=True)
class Posting:
    """Normalised view of one posting; ``raw`` is kept for JSONPath resolution.

    Missing optional fields contribute empty values (CONTRACT §5).

    Attributes:
        posting_id: Canonical decimal ID string.
        index: Position in the raw response's ``$.jobs`` array.
        raw: The posting object exactly as parsed. Record paths such as ``$.content``
            resolve against this object (§5, §7).
        title: ``$.title`` or ``""``.
        location_name: ``$.location.name``, or ``None`` when that path does not exist
            (A30), so callers can tell "absent" from an empty string and never cite a
            path that does not exist. Matching treats ``None`` as ``""``.
        updated_at: ``$.updated_at`` if it is a string, else ``None`` (metadata only).
        content_raw: ``$.content`` exactly as given (entity-escaped HTML) or ``""``.
        department_names: ``$.departments[i].name`` in order; a missing or non-string
            name contributes ``""`` so indices stay aligned with the raw array.
    """

    posting_id: str
    index: int
    raw: Mapping[str, Any] = field(repr=False, hash=False)
    title: str
    location_name: str | None
    updated_at: str | None
    content_raw: str = field(repr=False)
    department_names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SkillEntry:
    """One countable résumé skill and its path.

    Example: ``SkillEntry("GraphQL", "$.skills.backend[4]")``.
    """

    term: str
    resume_path: str


# --- rule results -----------------------------------------------------------


class SkillEvidence(FrozenModel):
    """One distinct matched skill: which résumé value was found in which field."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    term: NonEmptyStr
    resume_path: NonEmptyStr
    """Path into the résumé, e.g. ``$.skills.languages[2]``."""
    posting_path: NonEmptyStr
    """Path relative to the posting object: ``$.title``, ``$.content`` or
    ``$.departments[i].name`` (first field in that order containing the term, A29)."""


class LocationCheck(FrozenModel):
    """The §6.4 location label with at least one source path and a short reason."""

    label: LocationLabel
    evidence: list[NonEmptyStr] = Field(min_length=1)
    """Posting-relative paths, e.g. ``["$.location.name"]`` or ``["$.content"]``."""
    reason: NonEmptyStr


class TitleCheck(FrozenModel):
    """Result of the §6.1 title check.

    Attributes:
        matched_roles: Entries of ``$.target.roles`` whose family phrase the title
            contains (empty when no family phrase is present).
        excluded_markers: Every excluded marker found, lowercased (all are recorded).
        reason: Short human-readable explanation.
    """

    matched_roles: list[str]
    excluded_markers: list[str]
    reason: NonEmptyStr

    @property
    def passed(self) -> bool:
        """True when a role family matched and no excluded marker is present."""
        return bool(self.matched_roles) and not self.excluded_markers


class RuleVerdict(FrozenModel):
    """The deterministic verdict for one posting (CONTRACT §6.5, §7).

    Key order follows §7 (``label``, ``location_check``, ``evidence``, ``reason``);
    ``failed_gates`` is an additive key placed last (A28). A ``NO_MATCH`` still lists
    every matched skill. Consistency between ``label``, ``failed_gates`` and
    ``location_check`` is checked by the evidence validator, not here.
    """

    label: VerdictLabel
    location_check: LocationCheck
    evidence: list[SkillEvidence]
    reason: NonEmptyStr
    failed_gates: list[Gate]
    """Every failed gate in ``Gate`` order; empty exactly when the label is MATCH."""


# --- model judgment ---------------------------------------------------------


class ModelEvidence(FrozenModel):
    """One evidence entry of Claude's reply (§8); paths are checked separately."""

    resume_path: str
    posting_path: str
    reason: NonEmptyStr


class JudgmentReply(FrozenModel):
    """The exact §8 reply schema: these four keys and no others.

    The judge's validator parses the reply text itself (fences, prose, duplicate keys)
    and then calls ``JudgmentReply.model_validate(obj, strict=True)``; path existence is
    checked against the payloads afterwards. At least one evidence entry is required
    (A16).
    """

    label: ModelLabel
    summary: str
    evidence: list[ModelEvidence] = Field(min_length=1)
    uncertainties: list[str]


class AttemptSummary(FrozenModel):
    """Pointer to one model call's raw-reply log, plus its validation result.

    The raw reply text itself lives only in the log file (``raw_log_ref``), never in a
    record (§8: raw text must not overwrite structured output).
    """

    attempt: int = Field(ge=1, le=2)
    raw_log_ref: RepoPath
    first_reply: bool
    """True for attempt 1, the reply that sampling and experiments score."""
    validation_passed: bool | None
    """``None`` when the call itself failed and there was no reply to validate."""
    validation_codes: list[str] = Field(default_factory=list)
    """Rejection reason codes from the validator; empty when it passed."""
    session_id: str | None = None
    backend_error: BackendErrorKind | None = None


class JudgmentDiagnostic(FrozenModel):
    """Bookkeeping that explains a judgment without carrying any raw reply text."""

    prompt_id: str | None = None
    """E.g. ``"judge.v1"``; ``None`` when UNAVAILABLE before any prompt was rendered."""
    prompt_sha256: Sha256Hex | None = None
    model_requested: str | None = None
    attempts: list[AttemptSummary] = Field(default_factory=list, max_length=2)
    unavailable_reason: str | None = None
    """Short code such as ``"backend_none"`` or ``"cli_not_found"``; never stderr."""
    error_reason: str | None = Field(default=None, exclude_if=lambda v: v is None)
    """Short value-free code for an ``ERROR`` the judge itself raised, e.g.
    ``"judge_raised:PathRejected"`` (review fix 1). Omitted from JSON when unset, so
    ordinary records keep their exact shape."""


class ModelJudgment(FrozenModel):
    """Claude's opinion as stored in a record (CONTRACT §7, §8).

    Only a ``VALID`` judgment carries ``label``, ``summary``, ``evidence`` and
    ``uncertainties``; every other status has ``None``/empty values there, so an
    invalid raw reply can never fill the structured fields.

    Raises:
        pydantic.ValidationError: If the fields are inconsistent with ``status``.
    """

    status: JudgmentStatus
    label: ModelLabel | None = None
    summary: str | None = None
    evidence: list[ModelEvidence] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    diagnostic: JudgmentDiagnostic = Field(default_factory=JudgmentDiagnostic)

    @model_validator(mode="after")
    def _check_status_fields(self) -> Self:
        if self.status is JudgmentStatus.VALID:
            if self.label is None or self.summary is None or not self.evidence:
                raise ValueError("a VALID judgment needs label, summary and evidence")
        elif (
            self.label is not None
            or self.summary is not None
            or self.evidence
            or self.uncertainties
        ):
            raise ValueError(
                "only a VALID judgment may carry label, summary, evidence or "
                "uncertainties"
            )
        return self


@dataclass(frozen=True, slots=True)
class JudgmentOutcome:
    """What a ``Judge`` returns for one posting; drives the pending list (§10)."""

    posting_id: str
    judgment: ModelJudgment

    @property
    def status(self) -> JudgmentStatus:
        """Shortcut for ``judgment.status``."""
        return self.judgment.status

    @property
    def is_valid(self) -> bool:
        """True only for ``VALID``; anything else keeps the posting pending."""
        return self.judgment.status is JudgmentStatus.VALID


# --- records ----------------------------------------------------------------


class OutputRecord(FrozenModel):
    """One record per new or retried posting, in CONTRACT §7 key order.

    ``rule_evidence_errors`` is additive and last: a non-empty list means the rule's
    own evidence failed the §7 validator, which is a bug, and the run becomes
    ``PARTIAL_FAILURE``.
    """

    posting_id: PostingId
    title: str
    location: str | None
    """``$.location.name``, or ``None`` when absent."""
    updated_at: str | None
    rule_verdict: RuleVerdict
    model_judgment: ModelJudgment
    rule_evidence_errors: list[str] = Field(default_factory=list)


class RawRef(FrozenModel):
    """A pointer to saved raw response bytes, with the digest that pins them.

    Attributes:
        path: Repo-relative path of the raw response file.
        sha256: Digest of the file's exact bytes.
        index: Position of one posting in ``$.jobs``; set when the reference identifies
            a single posting (pending judgments, A26), ``None`` for a whole response.
    """

    path: RepoPath
    sha256: Sha256Hex
    index: int | None = Field(default=None, ge=0)


class DataQualityIssue(FrozenModel):
    """One per-posting data-quality finding (CONTRACT §5)."""

    code: DataQualityCode
    severity: Severity
    index: int | None = Field(default=None, ge=0)
    """Position in ``$.jobs``, when the issue concerns one entry."""
    posting_id: PostingId | None = None
    """Set only when the entry had a valid ID; an invalid ID is never echoed as one."""
    detail: str = ""
    """Short factual description; never contains posting HTML or résumé text."""


# --- state ------------------------------------------------------------------


class PendingJudgment(FrozenModel):
    """A posting whose rule result is saved but whose judgment is not VALID (§10)."""

    posting_id: PostingId
    last_status: JudgmentStatus
    queued_run_id: RunId
    last_attempt_run_id: RunId
    attempts: int = Field(ge=1)
    """Number of runs that tried to judge this posting."""
    source: RawRef
    """Where to re-read the posting if it leaves the board (A26); ``index`` required."""

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.last_status is JudgmentStatus.VALID:
            raise ValueError("a VALID judgment is never pending")
        if self.source.index is None:
            raise ValueError("a pending source must identify one posting (index)")
        return self


class AbandonedJudgment(FrozenModel):
    """A pending ID dropped by an explicit, documented ``jsa pending drop`` decision."""

    posting_id: PostingId
    last_status: JudgmentStatus
    queued_run_id: RunId
    dropped_at_utc: AwareDatetime
    reason: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SeenState(FrozenModel):
    """The state file (CONTRACT §10). Live and seeded runs keep separate files.

    Integrity checks run on load, so a hand-edited or truncated file fails validation
    (``state.parse_state`` maps that to ``StateCorrupt``) instead of silently becoming a
    new baseline.

    Raises:
        pydantic.ValidationError: On duplicate IDs, or pending/abandoned IDs that are
            not in ``seen_ids`` or appear in both lists.
    """

    schema_version: Literal[1]
    provider: NonEmptyStr
    board: NonEmptyStr
    seeded: bool
    seen_ids: list[PostingId]
    """Cumulative: an ID is never removed once seen (§9, §10)."""
    last_successful_fetch_utc: AwareDatetime
    """When the raw response was fetched; for a replay, the original fetch time."""
    last_successful_run_id: RunId
    run_started_at_utc: AwareDatetime
    """When the run that wrote this state started (differs from the fetch on replay)."""
    pending: list[PendingJudgment] = Field(default_factory=list)
    abandoned: list[AbandonedJudgment] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_integrity(self) -> Self:
        seen = set(self.seen_ids)
        if len(seen) != len(self.seen_ids):
            raise ValueError("seen_ids contains duplicates")
        pending = [p.posting_id for p in self.pending]
        abandoned = [a.posting_id for a in self.abandoned]
        for name, ids in (("pending", pending), ("abandoned", abandoned)):
            if len(set(ids)) != len(ids):
                raise ValueError(f"{name} contains duplicate posting IDs")
            if not seen.issuperset(ids):
                raise ValueError(f"{name} IDs must also be in seen_ids")
        if set(pending) & set(abandoned):
            raise ValueError("an ID cannot be both pending and abandoned")
        return self


# --- report -----------------------------------------------------------------


class RunReport(FrozenModel):
    """``report.json`` for one run; the source for ``report.md`` and ``docs/RUNS.md``.

    ``fetched_count`` and ``unique_valid_ids`` are ``None`` when nothing was parsed
    (FETCH_FAILED, INVALID_RESPONSE). ``raw_evidence`` points to the saved raw bytes
    (for a replay, the replayed file) and is ``None`` only when no body existed.

    Raises:
        pydantic.ValidationError: If ``new_count`` differs from ``len(new_ids)``.
    """

    run_id: RunId
    mode: RunMode
    seeded: bool
    provider: str
    board: str
    code_commit: str | None
    code_dirty: bool | None
    started_at_utc: AwareDatetime
    started_at_et: AwareDatetime
    finished_at_utc: AwareDatetime
    finished_at_et: AwareDatetime
    status: RunStatus
    fetched_count: int | None = Field(ge=0)
    unique_valid_ids: int | None = Field(ge=0)
    new_count: int = Field(ge=0)
    new_ids: list[PostingId] = Field(default_factory=list)
    retried_pending_ids: list[PostingId] = Field(default_factory=list)
    unresolved_pending_ids: list[PostingId] = Field(default_factory=list)
    """Pending after this run (still failing, or not retried because unavailable)."""
    judgment_counts: dict[JudgmentStatus, int] = Field(default_factory=dict)
    data_quality_issues: list[DataQualityIssue] = Field(default_factory=list)
    """All issues, both severities; only ERROR ones affect the status."""
    records_saved: bool
    state_saved: bool
    raw_evidence: RawRef | None = None
    original_fetched_at_utc: AwareDatetime | None = None
    """Replay only: when the replayed response was originally fetched."""
    fetch_error: FetchErrorKind | None = None
    http_status: int | None = None
    model_backend: str
    """``"claude-cli"`` or ``"none"``."""
    model_id: str | None = None
    prompt_version: str | None = None
    notes: list[str] = Field(default_factory=list)
    """Short machine-readable notes, e.g. ``"baseline_state_not_saved"`` (A19)."""

    @model_validator(mode="after")
    def _check_counts(self) -> Self:
        if self.new_count != len(self.new_ids):
            raise ValueError("new_count must equal len(new_ids)")
        return self


# --- port values ------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FetchResult:
    """Result of one ``HttpFetcher.get``. Expected failures are values, not exceptions.

    Attributes:
        requested_url: The URL asked for.
        final_url: URL of the last response, after allowed redirects.
        redirect_chain: Every URL visited before ``final_url``, in order.
        status_code: Final HTTP status, or ``None`` if no response arrived.
        headers: Selected response headers with lowercase names (content-type, etag,
            date, ...). Never contains request credentials.
        body: Exact response bytes when a body was received (also on non-2xx), else
            ``None``.
        error: Why the fetch failed, or ``None`` on a 2xx response within limits.
        error_detail: Short, credential-free explanation for logs.
        elapsed_ms: Wall time of the whole exchange.
    """

    requested_url: str
    final_url: str | None
    redirect_chain: tuple[str, ...]
    status_code: int | None
    headers: Mapping[str, str] = field(hash=False)
    body: bytes | None = field(repr=False)
    error: FetchErrorKind | None
    error_detail: str | None = None
    elapsed_ms: int | None = None

    @property
    def ok(self) -> bool:
        """True when there was no error and a body was received."""
        return self.error is None and self.body is not None


@dataclass(frozen=True, slots=True)
class SourceResult:
    """Raw response from a ``RawSource`` (live network or seeded replay).

    Attributes:
        kind: ``NETWORK`` or ``REPLAY``.
        body: The raw bytes, or ``None`` if none were obtained.
        sha256: Digest of ``body`` when present.
        error: Why the response could not be obtained, or ``None``.
        error_detail: Short, credential-free explanation.
        fetch: Live only: the underlying fetch, for meta files and events.
        replayed_from: Replay only: the saved file that was replayed.
        original_fetched_at_utc: Replay only: original fetch time from its meta file.
    """

    kind: SourceKind
    body: bytes | None = field(repr=False)
    sha256: str | None
    error: FetchErrorKind | None
    error_detail: str | None = None
    fetch: FetchResult | None = None
    replayed_from: RawRef | None = None
    original_fetched_at_utc: datetime | None = None

    @property
    def ok(self) -> bool:
        """True when there was no error and a body was obtained."""
        return self.error is None and self.body is not None


@dataclass(frozen=True, slots=True)
class ParsedBoard:
    """A structurally valid board response (``BoardProvider.parse``).

    An empty ``jobs`` array parses to ``fetched_count == 0`` (``is_empty``), which the
    pipeline reports as ``EMPTY_RESPONSE``. A non-empty array with zero valid IDs is
    ``InvalidResponse`` and never reaches this type.

    Attributes:
        postings: Postings with valid, unique IDs, in board order.
        fetched_count: ``len(jobs)`` as received, valid or not.
        meta_total: ``meta.total`` as received.
        data_quality: Every per-posting issue found.
    """

    postings: tuple[Posting, ...]
    fetched_count: int
    meta_total: int
    data_quality: tuple[DataQualityIssue, ...] = ()

    @property
    def is_empty(self) -> bool:
        """True when the response's ``jobs`` array was empty."""
        return self.fetched_count == 0

    @property
    def valid_ids(self) -> tuple[str, ...]:
        """Valid unique posting IDs in board order."""
        return tuple(p.posting_id for p in self.postings)

    @property
    def error_count(self) -> int:
        """Number of ``ERROR``-severity data-quality issues."""
        return sum(1 for i in self.data_quality if i.severity is Severity.ERROR)


@dataclass(frozen=True, slots=True)
class Availability:
    """Whether a model backend can be called at all, checked before any call.

    Attributes:
        available: False means every judgment is ``UNAVAILABLE`` and no call is made.
        reason: Short code when unavailable, e.g. ``"backend_none"``,
            ``"cli_not_found"``.
        version: Version string reported by the backend, when known.
    """

    available: bool
    reason: str | None = None
    version: str | None = None


@dataclass(frozen=True, slots=True)
class BackendReply:
    """One attempted model call. Failures are values (``error``), not exceptions.

    Attributes:
        argv: The command line used, without the prompt (which goes on stdin).
        started_at_utc: When the call started.
        duration_ms: Wall time of the call.
        exit_code: Process exit status, ``None`` on timeout or spawn failure.
        raw_stdout: Verbatim CLI stdout (the JSON envelope), for the raw-reply log.
        stderr: CLI stderr, already replaced by ``"[withheld: credential pattern]"``
            if it looked like it contained a credential.
        result_text: The envelope's ``result`` (Claude's reply text), if parsed.
        is_error: The envelope's ``is_error`` flag.
        session_id: The envelope's ``session_id``, if any.
        model_served: Served model labels (keys of the envelope's ``modelUsage``).
        total_cost_usd: The envelope's ``total_cost_usd``, if any.
        error: Why the call failed, or ``None`` when ``result_text`` is usable.
    """

    argv: tuple[str, ...]
    started_at_utc: datetime
    duration_ms: int
    exit_code: int | None
    raw_stdout: str = field(repr=False)
    stderr: str = field(repr=False)
    result_text: str | None = field(repr=False)
    is_error: bool
    session_id: str | None
    model_served: tuple[str, ...]
    total_cost_usd: float | None
    error: BackendErrorKind | None

    @property
    def ok(self) -> bool:
        """True when the call succeeded and produced reply text to validate."""
        return self.error is None and self.result_text is not None


@dataclass(frozen=True, slots=True)
class CompletedCommand:
    """Result of ``CommandRunner.run``.

    Attributes:
        argv: The command line that was run.
        returncode: Exit status, or ``None`` if the process was killed on timeout.
        stdout: Captured stdout, decoded as UTF-8 with replacement.
        stderr: Captured stderr, decoded as UTF-8 with replacement.
        timed_out: True when the timeout expired and the process was killed.
        duration_ms: Wall time.
    """

    argv: tuple[str, ...]
    returncode: int | None
    stdout: str = field(repr=False)
    stderr: str = field(repr=False)
    timed_out: bool
    duration_ms: int
