"""The JS3 corpus: every posting in every saved raw response of the FILTER.md §3 boards.

A posting seen in several raws counts once, from its newest raw (raws sort by their
run-folder timestamp; the JS1 hand-check file is the oldest Stripe raw). Nothing here
touches the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from job_search_agent.config import load_config
from job_search_agent.errors import AgentError
from job_search_agent.models import Posting
from job_search_agent.providers import get_provider
from job_search_agent.resume import load_verified_resume
from job_search_agent.rule.verdict import RuleInputs, rule_inputs

EXPECTED_BOARDS: tuple[str, ...] = (
    "greenhouse/stripe",
    "greenhouse/figma",
    "ashby/ramp",
    "ashby/linear",
)
"""FILTER.md §3 expected sources, in report order."""

EXCLUDED_BOARDS: dict[str, str] = {
    "ashby/linearapp": "deliberate 404 in JS2 (GATE §5); not a real board",
    "greenhouse/ramp": (
        "stale wrong board in JS2 (FINISHED_WRONG.md); Ramp hires on Ashby"
    ),
}

HANDCHECK_RAW = "evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json"


@dataclass(frozen=True, slots=True)
class Entry:
    """One corpus posting and where it came from."""

    key: str  # "<provider>/<token>/<posting_id>"
    board: str
    posting: Posting
    raw_rel: str  # repo-relative raw file it was read from

    @property
    def url(self) -> str:
        """The public posting page."""
        provider, token = self.board.split("/")
        if provider == "ashby":
            return f"https://jobs.ashbyhq.com/{token}/{self.posting.posting_id}"
        url = self.posting.raw.get("absolute_url")
        return url if isinstance(url, str) else ""


@dataclass(frozen=True, slots=True)
class Corpus:
    """The loaded corpus and the sources behind it."""

    entries: tuple[Entry, ...]
    raws: dict[str, tuple[str, ...]]  # board -> raw files read, oldest first
    missing: dict[str, str]  # board -> reason (FILTER.md §3 MISSING_SOURCE)

    def by_key(self) -> dict[str, Entry]:
        """Entries keyed by ``key``."""
        return {e.key: e for e in self.entries}


def _raw_files(root: Path, board: str) -> list[Path]:
    provider, token = board.split("/")
    files = sorted(
        root.glob(
            f"data/watch/boards/{provider}-{token}/live/runs/*/raw/{provider}-{token}.json"
        )
    )
    if board == "greenhouse/stripe":
        js1 = sorted(root.glob("data/live/runs/*/raw/greenhouse-stripe.json"))
        files = [root / HANDCHECK_RAW, *js1, *files]
    return [f for f in files if f.is_file()]


def load_corpus(root: Path, boards: tuple[str, ...] = EXPECTED_BOARDS) -> Corpus:
    """Reads every saved raw of ``boards``; newest raw wins per posting ID."""
    entries: dict[str, Entry] = {}
    raws: dict[str, tuple[str, ...]] = {}
    missing: dict[str, str] = {}
    for board in boards:
        provider = get_provider(board.split("/")[0])
        read: list[str] = []
        for path in _raw_files(root, board):
            rel = path.relative_to(root).as_posix()
            try:
                parsed = provider.parse(path.read_bytes())
            except (AgentError, OSError) as exc:
                missing.setdefault(board, f"{rel}: {type(exc).__name__}")
                continue
            read.append(rel)
            for posting in parsed.postings:
                key = f"{board}/{posting.posting_id}"
                entries[key] = Entry(key, board, posting, rel)
        raws[board] = tuple(read)
        if not read:
            missing[board] = missing.get(board, "no saved raw response")
        else:
            missing.pop(board, None)
    ordered = sorted(
        entries.values(),
        key=lambda e: (
            EXPECTED_BOARDS.index(e.board) if e.board in EXPECTED_BOARDS else 99,
            e.posting.posting_id,
        ),
    )
    return Corpus(tuple(ordered), raws, missing)


def load_inputs(root: Path) -> RuleInputs:
    """The persona's roles and skills.

    Read through the pinned-hash résumé gate (CONTRACT §12).
    """
    config = load_config(root / "config" / "agent.toml")
    resume = load_verified_resume(
        config.resume_path, config.resume.pinned_sha256, project_root=root
    )
    return rule_inputs(resume.to_dict())
