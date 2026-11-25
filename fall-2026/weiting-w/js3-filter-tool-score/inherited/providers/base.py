"""One posting shape across three applicant-tracking systems.

JS1's rule read Greenhouse-shaped dicts directly: `title`,
`location.name`, and the `metadata` entry named "Job Family". Lever and Ashby
have none of those paths, so this layer normalises. The normalisation is the
subject of GATE.md §8 amendment A1 and of the `R-v2a` rule version: the gates
and their decisions are unchanged, they just read a provider-independent view.

Every normalised field keeps **where it came from**. `provider_field` is the
provider-native path, so a justification can still name the posting field it
rests on — which was CONTRACT.md O2 in JS1 and does not get to lapse because
there are now three providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Posting:
    """A posting, provider-independent, with provenance for every field."""

    board: str              # plan entry id, e.g. "greenhouse:reddit"
    provider: str           # "greenhouse" | "lever" | "ashby"
    posting_id: str         # provider-native id, as a string
    title: str
    location: str
    job_family: str | None
    url: str
    #: normalised field name -> provider-native path it was read from
    provider_field: dict[str, str] = field(default_factory=dict)
    #: the provider's own object, untouched, so nothing is lost
    raw: dict = field(default_factory=dict)

    @property
    def identity(self) -> str:
        """Global identity across providers.

        A Greenhouse id and a Lever id can collide as integers, so the key the
        state file uses is namespaced by provider. Nothing else is identity:
        not the title, not a timestamp.
        """
        return f"{self.provider}:{self.posting_id}"

    def for_rule(self) -> dict:
        """The view the carried-over rule judges, with provenance attached."""
        return {
            "id": self.identity,
            "title": self.title,
            "location": {"name": self.location},
            "job_family": self.job_family,
            "provider_field": dict(self.provider_field),
        }

    def summary(self) -> dict:
        return {
            "identity": self.identity,
            "board": self.board,
            "provider": self.provider,
            "posting_id": self.posting_id,
            "title": self.title,
            "location": self.location,
            "job_family": self.job_family,
            "url": self.url,
            "provider_field": dict(self.provider_field),
        }


class Provider:
    """Base class. A provider turns one board token into a URL and a parse."""

    name = "base"
    #: the single host this provider is permitted to reach
    host = ""

    def url_for(self, token: str) -> str:  # pragma: no cover - abstract
        raise NotImplementedError

    def parse(self, board: str, payload) -> list[Posting]:  # pragma: no cover
        raise NotImplementedError

    @staticmethod
    def _text(value) -> str:
        return value if isinstance(value, str) else ""
