"""Three applicant-tracking systems, one posting shape, provenance kept.

Each adapter is where a careless normalisation would invent a value, so each
test names the specific thing the adapter must *not* do.
"""

from __future__ import annotations

import pytest

from agent import providers
from agent.errors import SchemaFailure
from tests.conftest import ASHBY_OK, GREENHOUSE_OK, LEVER_OK


def test_three_providers_are_registered_one_per_system():
    assert set(providers.REGISTRY) == {"greenhouse", "lever", "ashby"}
    hosts = {p.host for p in providers.REGISTRY.values()}
    assert len(hosts) == 3, "three systems, three hosts"
    from agent.policy import ALLOWED_HOSTS

    assert hosts == set(ALLOWED_HOSTS), (
        "every provider's host must be on the allow-list and vice versa: "
        "a provider the policy forbids is dead code, and an allowed host no "
        "provider uses is a hole"
    )


def test_greenhouse_reads_job_family_out_of_metadata():
    out = providers.get("greenhouse").parse("greenhouse:x", GREENHOUSE_OK)
    assert [p.posting_id for p in out] == ["1001", "1002", "1003"]
    assert out[0].job_family == "Software Engineering"
    assert out[0].provider_field["job_family"] == "metadata[1].value"
    # the null-value case: 10 of 161 real postings on the JS1 board had this
    assert out[2].job_family is None
    assert out[2].provider_field["job_family"] == "metadata[0].name"


def test_lever_is_a_bare_array_and_the_title_lives_in_text():
    out = providers.get("lever").parse("lever:x", LEVER_OK)
    assert [p.title for p in out][0] == "Software Engineer, Platform"
    assert out[0].location == "New York City, NY"
    assert out[0].provider_field == {
        "title": "text",
        "location": "categories.location",
        "job_family": "categories.team",
    }


def test_lever_falls_back_to_department_then_to_none_never_to_a_guess():
    out = providers.get("lever").parse("lever:x", LEVER_OK)
    assert (out[1].job_family, out[1].provider_field["job_family"]) == (
        "Sales", "categories.department",
    )
    assert out[2].job_family is None, "no team and no department is None, not ''"
    assert out[2].provider_field["job_family"] == "categories"


def test_ashby_drops_unlisted_postings_and_counts_them():
    provider = providers.get("ashby")
    out = provider.parse("ashby:x", ASHBY_OK)
    assert [p.posting_id for p in out] == ["ash-111", "ash-222"]
    assert provider.dropped_unlisted == 1, (
        "a posting the adapter removed must be counted, or the cross-check "
        "sees it as a posting that vanished from the board"
    )


def test_identity_is_namespaced_by_provider():
    gh = providers.get("greenhouse").parse("greenhouse:x", GREENHOUSE_OK)
    lv = providers.get("lever").parse("lever:x", LEVER_OK)
    assert gh[0].identity == "greenhouse:1001"
    assert lv[0].identity == "lever:lev-aaa"
    assert len({p.identity for p in gh + lv}) == len(gh) + len(lv)


@pytest.mark.parametrize(
    "name,payload",
    [
        ("greenhouse", {"results": []}),
        ("greenhouse", []),
        ("lever", {"jobs": []}),
        ("ashby", [1, 2, 3]),
        ("ashby", {"jobs": [{"title": "no id"}]}),
    ],
)
def test_a_payload_of_the_wrong_shape_is_a_schema_failure_not_an_empty_board(name, payload):
    """The distinction the whole finished-wrong-answer section rests on."""
    with pytest.raises(SchemaFailure):
        providers.get(name).parse(f"{name}:x", payload)


def test_an_honestly_empty_board_parses_to_zero_postings():
    """And this one is NOT a schema failure, which is why it is dangerous."""
    out = providers.get("greenhouse").parse("greenhouse:x", {"jobs": [], "meta": {"total": 0}})
    assert out == []
