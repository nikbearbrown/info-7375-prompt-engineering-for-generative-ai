"""Where every file of a run lives, defined once.

Pipeline, CLI and tests all ask this object for paths, so tests can point a whole run at a temp
folder (keeping the submitted state/, runs/, evidence/ untouched) and a layout change is one edit.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# job_agent/common/paths.py -> repo root is three levels up.
REPO = Path(__file__).resolve().parents[2]


def stamp(now: datetime) -> str:
    """Folder name for one run. Same style as the 10/29 snapshot (2026-10-30T033237Z): no colons, safe on every OS."""
    return now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


@dataclass(frozen=True)
class Paths:
    out: Path = REPO   # where a run writes: state/, runs/, evidence/raw/
    repo: Path = REPO  # where shipped inputs live: data/, personas/

    def state(self, board: str) -> Path:
        return self.out / "state" / f"{board}.state.json"

    def raw(self, stamp: str) -> Path:
        return self.out / "evidence" / "raw" / stamp

    def run(self, stamp: str) -> Path:
        return self.out / "runs" / stamp

    @property
    def skill_aliases(self) -> Path:
        return self.repo / "data" / "skill_aliases.json"

    @property
    def no_sponsorship_phrases(self) -> Path:
        return self.repo / "data" / "no_sponsorship_phrases.json"

    @property
    def default_resume(self) -> Path:
        return self.repo / "personas" / "aarav-patel.resume.json"

    @property
    def default_profile(self) -> Path:
        return self.repo / "personas" / "aarav-patel.profile.json"

    def prompt(self, name: str) -> Path:
        """Prompt files are versioned by name (claude_judge.v1, .v2 ...) for the Step 9 experiment."""
        return self.repo / "prompts" / f"{name}.md"

    def show(self, path: Path) -> str:
        """Repo-relative when possible, so output never prints a home-folder path; temp paths stay absolute."""
        path = path.resolve()
        return str(path.relative_to(self.repo)) if path.is_relative_to(self.repo) else str(path)
