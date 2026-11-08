"""The boards this agent may watch (GATE.md 'Exits' and 'Permission policy').

The list lives in code, not in a configuration file, because the policy lets the agent
read only the persona, the state and saved run evidence. A normal run checks the three
normal boards; a failure run adds the failure control, a Greenhouse name that does not
exist and should answer 404."""

from dataclasses import dataclass

GREENHOUSE = "greenhouse"
ASHBY = "ashby"
_ENDPOINTS = {
    GREENHOUSE: "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
    ASHBY: "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}


@dataclass(frozen=True)
class Board:
    ats: str
    slug: str
    role: str = "normal"  # "normal" or "failure-control"

    @property
    def name(self):
        return f"{self.ats}/{self.slug}"

    @property
    def url(self):
        return _ENDPOINTS[self.ats].format(slug=self.slug)


CONFIGURED = (
    Board(GREENHOUSE, "anthropic"),
    Board(GREENHOUSE, "databricks"),
    Board(ASHBY, "linear"),
    Board(GREENHOUSE, "jobwatch-no-such-board-js2", role="failure-control"),
)
NORMAL_RUN = tuple(b.name for b in CONFIGURED if b.role == "normal")
FAILURE_RUN = tuple(b.name for b in CONFIGURED)


def normalize_name(name):
    """GATE.md 'Repeat rule': trim whitespace and lowercase the ATS and the slug."""
    ats, _, slug = name.partition("/")
    return f"{ats.strip().lower()}/{slug.strip().lower()}"


def lookup(name, configured=CONFIGURED):
    wanted = normalize_name(name)
    for board in configured:
        if normalize_name(board.name) == wanted:
            return board
    return None


def approved_urls(configured=CONFIGURED):
    return frozenset(board.url for board in configured)
