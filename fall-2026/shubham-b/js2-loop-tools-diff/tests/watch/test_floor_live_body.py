"""Revision of the GATE A2 floor (Shubham's review decision: revise).

The floor applies to the live response the loop fetched, identified by its bytes, not
to "the first parse" in a run, so it no longer depends on the order in which
``pipeline.run_once`` parses responses. Written by Claude before the revision.
"""

from __future__ import annotations

import pytest

from job_search_agent.errors import InvalidResponse
from job_search_agent.providers import get_provider
from job_search_agent.watch import FlooredProvider
from tests.watch.harness import ashby_body

IDS = [f"00000000-0000-4000-8000-{i:012d}" for i in range(4)]


def test_an_old_raw_parsed_first_is_not_floored_and_the_live_one_still_is() -> None:
    live = ashby_body(*IDS[:2])
    old = ashby_body(*IDS[:3])
    provider = FlooredProvider(get_provider("ashby"), 5, live_body=lambda: live)
    assert provider.parse(old).fetched_count == 3
    assert not provider.below_floor
    with pytest.raises(InvalidResponse) as caught:
        provider.parse(live)
    assert caught.value.code == "below_floor"
    assert provider.below_floor


def test_no_live_body_means_no_floor() -> None:
    provider = FlooredProvider(get_provider("ashby"), 5, live_body=lambda: None)
    assert provider.parse(ashby_body(*IDS[:1])).fetched_count == 1
