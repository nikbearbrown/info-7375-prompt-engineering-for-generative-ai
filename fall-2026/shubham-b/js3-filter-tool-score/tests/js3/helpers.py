"""Shared JS3 test helpers: a posting builder and the persona's rule inputs."""

from __future__ import annotations

from functools import cache
from html import escape

from job_search_agent.js3.corpus import load_inputs
from job_search_agent.js3.filter import FilterSpec, Scored, load_filter, score
from job_search_agent.models import Posting
from job_search_agent.rule.verdict import RuleInputs
from tests.conftest import REPO_ROOT


@cache
def inputs() -> RuleInputs:
    return load_inputs(REPO_ROOT)


@cache
def spec() -> FilterSpec:
    return load_filter(REPO_ROOT / "FILTER.md")


def posting(
    title: str,
    content: str = "",
    location: str | None = "Seattle, WA",
    departments: tuple[str, ...] = (),
) -> Posting:
    """A Greenhouse-shaped posting.

    ``content`` is plain text, escaped like the API does.
    """
    raw: dict[str, object] = {
        "id": 1,
        "title": title,
        "content": escape(f"<p>{content}</p>"),
    }
    if location is not None:
        raw["location"] = {"name": location}
    return Posting(
        posting_id="1",
        index=0,
        raw=raw,
        title=title,
        location_name=location,
        updated_at=None,
        content_raw=str(raw["content"]),
        department_names=departments,
    )


def scored(p: Posting, s: FilterSpec | None = None) -> Scored:
    return score(p, "greenhouse/test/1", "greenhouse/test", s or spec(), inputs())


FILLER = (
    " We build reliable systems for millions of users"
    " and care about craft, testing and clear writing." * 3
)
