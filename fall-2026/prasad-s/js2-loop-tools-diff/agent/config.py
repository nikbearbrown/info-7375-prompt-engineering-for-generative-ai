"""Config file (CONTRACT.md v0.5 items 1, 2, 5; v0.6 item 1; GATE.md §0, §2, §5).

The board list comes from here; no board is wired into the code. Shape
problems are a RunError (GATE.md §1: error, invalid config). An allow-list
that differs from GATE.md §5's is a Refusal (GATE.md §1: refused).
"""

import json
from dataclasses import dataclass

from .errors import Refusal, RunError
from .policy import ALLOWED_HOSTS

# v0.5 item 1: the two fetch URL forms, one per ATS.
ATS_HOSTS = {"greenhouse": "boards-api.greenhouse.io", "ashby": "api.ashbyhq.com"}
URL_FORMS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{name}/jobs?content=true",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{name}?includeCompensation=true",
}
PATH_KEYS = ("resume_path", "state_dir", "evidence_dir", "output_dir")
CONFIG_KEYS = ("boards", "allow_list") + PATH_KEYS
BOARD_KEYS = ("ats", "name")


@dataclass(frozen=True)
class Board:
    ats: str
    name: str

    @property
    def key(self):
        """v0.5 item 4: the board key is the ATS plus the name, e.g. greenhouse:stripe."""
        return f"{self.ats}:{self.name}"

    @property
    def host(self):
        return ATS_HOSTS[self.ats]

    @property
    def url(self):
        return URL_FORMS[self.ats].format(name=self.name)


@dataclass(frozen=True)
class Config:
    boards: tuple
    allow_list: tuple
    resume_path: str
    state_dir: str
    evidence_dir: str
    output_dir: str

    @property
    def board_pairs(self):
        """(host, name) pairs for Policy (v0.6 item 3)."""
        return [(board.host, board.name) for board in self.boards]


def parse_config(raw, label="config.json"):
    """Parse config bytes. Paths stay relative to the project folder, as written."""
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise RunError(f"invalid config {label}: not JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RunError(f"invalid config {label}: not a JSON object")
    missing = [key for key in CONFIG_KEYS if key not in data]
    if missing:
        raise RunError(f"invalid config {label}: missing {', '.join(missing)}")
    # Decision 2026-11-06: any key outside the v0.5 shape is invalid, which is
    # how GATE.md §5's "the config holds no budget values" is enforced.
    unknown = sorted(set(data) - set(CONFIG_KEYS))
    if unknown:
        raise RunError(f"invalid config {label}: unknown key(s) {', '.join(unknown)} "
                       "(GATE.md §5: budgets live in GATE.md §2, never in the config)")
    for key in PATH_KEYS:
        if not isinstance(data[key], str) or not data[key]:
            raise RunError(f"invalid config {label}: {key} must be a non-empty path string")

    boards = data["boards"]
    if not isinstance(boards, list) or not boards:
        raise RunError(f"invalid config {label}: boards must be a non-empty list")
    parsed, seen = [], set()
    for index, entry in enumerate(boards):
        if not isinstance(entry, dict) or sorted(entry) != sorted(BOARD_KEYS):
            raise RunError(f"invalid config {label}: board #{index} must have exactly {', '.join(BOARD_KEYS)}")
        ats, name = entry["ats"], entry["name"]
        if ats not in ATS_HOSTS:
            raise RunError(f"invalid config {label}: board #{index} ats {ats!r} is not one of {', '.join(ATS_HOSTS)}")
        if not isinstance(name, str) or not name:
            raise RunError(f"invalid config {label}: board #{index} name must be a non-empty string")
        board = Board(ats, name)
        # Decision 2026-11-06 (Prasad, CP5b): a board listed twice is an invalid config.
        if board.key in seen:
            raise RunError(f"invalid config {label}: board {board.key} is listed twice")
        seen.add(board.key)
        parsed.append(board)

    allow_list = data["allow_list"]
    if not isinstance(allow_list, list) or not all(isinstance(host, str) for host in allow_list):
        raise RunError(f"invalid config {label}: allow_list must be a list of host names")
    if sorted(allow_list) != sorted(ALLOWED_HOSTS):
        raise Refusal(f"allow_list must be exactly {list(ALLOWED_HOSTS)} (GATE.md §5), not {allow_list}")
    return Config(
        boards=tuple(parsed),
        allow_list=tuple(allow_list),
        resume_path=data["resume_path"],
        state_dir=data["state_dir"],
        evidence_dir=data["evidence_dir"],
        output_dir=data["output_dir"],
    )
