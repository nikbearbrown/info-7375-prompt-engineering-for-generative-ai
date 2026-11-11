"""The defect under review: G4 treats "remote" as a location.

Written **before** the patch, and committed while it still fails, so the review
packet has a real before-and-after rather than a story about code that was
already fixed. `review/review-packet.md` quotes the failure output from this
file verbatim.

The defect, stated as a property I want: **a posting the persona cannot
legally take must not be judged relevant.** R-v2 and R-v2a both violate it,
because G4 passes any location containing the substring "remote" whenever the
résumé says `remote_ok`, without ever asking *remote where*.

This was pre-registered in JS1 CONTRACT.md §4.2 item 3 on 2026-10-21, before I
had seen any real data, and then confirmed by the real board: JS1's live
capture of 2026-10-31 carries 24 non-US remote postings.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent import providers
from agent import rule as rule_judge

ROOT = Path(__file__).resolve().parents[1]
RESPONSE = ROOT / "evidence" / "fixtures" / "js1-greenhouse-reddit-20261031.json"


def posting(title, job_family, location):
    """A constructed posting, Greenhouse-shaped, for the unit cases."""
    return providers.get("greenhouse").parse(
        "greenhouse:constructed",
        {
            "jobs": [
                {
                    "id": 9001,
                    "title": title,
                    "location": {"name": location},
                    "metadata": [{"name": "Job Family", "value": job_family}],
                    "absolute_url": "https://example.com/9001",
                }
            ]
        },
    )[0]


@pytest.fixture(scope="module")
def real_postings():
    payload = json.loads(RESPONSE.read_text(encoding="utf-8"))
    return providers.get("greenhouse").parse("greenhouse:reddit", payload)


# --- the property, on real data ------------------------------------------------

def test_no_posting_outside_the_personas_locations_is_relevant(real_postings, persona):
    """The defect, reproduced on the real board.

    This is the assertion that fails before the patch. It names the postings it
    fails on, so the failure output is itself the reproduction.
    """
    allowed = persona["locations_ok"]
    offenders = []
    for p in real_postings:
        verdict = rule_judge.judge(p.for_rule(), persona)
        if verdict["verdict"] != "relevant":
            continue
        loc = p.location.casefold()
        if not any(phrase in loc for phrase in allowed):
            offenders.append((p.identity, p.title, p.location))
    assert offenders == [], (
        f"{len(offenders)} posting(s) judged relevant in a location the persona "
        f"cannot take: {offenders}"
    )


def test_the_board_really_does_carry_non_us_remote_postings(real_postings):
    """Guards the test above: if this is empty, the test above proves nothing."""
    non_us_remote = [
        p for p in real_postings
        if "remote" in p.location.casefold()
        and "united states" not in p.location.casefold()
    ]
    assert len(non_us_remote) >= 10, (
        f"only {len(non_us_remote)} non-US remote postings in the fixture"
    )


# --- the unit cases -----------------------------------------------------------

@pytest.mark.parametrize(
    "location",
    [
        "Remote - Ontario, Canada",
        "Remote - British Columbia, Canada",
        "Remote - United Kingdom",
        "Remote - The Netherlands",
        "Remote - Ireland",
        "Remote - Germany",
    ],
)
def test_remote_outside_the_allowed_locations_fails_g4(location, persona):
    verdict = rule_judge.judge(
        posting("Software Engineer, Core", "Software Engineering", location).for_rule(),
        persona,
    )
    assert verdict["verdict"] == "not_relevant"
    assert verdict["gate_failed"] == "G4_location"


# --- what must NOT change ------------------------------------------------------

def test_remote_inside_the_allowed_locations_still_passes(persona):
    verdict = rule_judge.judge(
        posting(
            "Software Engineer, Core", "Software Engineering", "Remote - United States"
        ).for_rule(),
        persona,
    )
    assert verdict["verdict"] == "relevant"


def test_an_on_site_allowed_location_still_passes(persona):
    verdict = rule_judge.judge(
        posting(
            "Software Engineer, Core", "Software Engineering", "New York City, NY"
        ).for_rule(),
        persona,
    )
    assert verdict["verdict"] == "relevant"


def test_remote_in_an_allowed_location_is_unaffected_by_the_remote_flag(persona):
    """The flag now cuts both ways, so check the direction that must not move."""
    verdict = rule_judge.judge(
        posting(
            "Software Engineer, Core", "Software Engineering", "Chicago, IL"
        ).for_rule(),
        persona,
    )
    assert verdict["verdict"] == "relevant"


def test_a_persona_that_cannot_work_remotely_rejects_a_remote_posting(persona):
    """`remote_ok` should be a filter, not a bypass.

    In R-v2a `remote_ok` only ever *widened* the gate, so a persona with
    `remote_ok: false` was indistinguishable from one with it true for any
    posting whose location also matched `locations_ok`. If the flag is going to
    exist it should mean something in both directions.
    """
    import copy

    homebound = copy.deepcopy(persona)
    homebound["remote_ok"] = False
    verdict = rule_judge.judge(
        posting(
            "Software Engineer, Core", "Software Engineering", "Remote - United States"
        ).for_rule(),
        homebound,
    )
    assert verdict["verdict"] == "not_relevant"
    assert verdict["gate_failed"] == "G4_location"


# --- what this file still does NOT catch ---------------------------------------
#
# Found while reviewing the R-v3 diff, not while writing it, and written down
# here rather than only in prose because a defect recorded as a test is the
# only kind that argues back later. See review/review-packet.md section 7.
#
# The property test at the top of this file asks: "is every relevant posting in
# a location `locations_ok` allows?" — and it answers using
# `any(phrase in loc for phrase in allowed)`, which is *the same substring
# comparison G4 itself performs*. Oracle and implementation share a criterion,
# so the test can only ever confirm that G4 agrees with G4. If the criterion is
# itself wrong, both are wrong together and the suite stays green.
#
# It is wrong in the same way the bug A2 just fixed was wrong: a substring of a
# location string is being treated as the identity of a place.

@pytest.mark.xfail(
    strict=True,
    reason="Known, unfixed defect recorded by A2's review (review-packet.md §7): "
           "`locations_ok` is matched as a substring, so a place name that occurs "
           "inside a location the persona cannot take still passes G4. Not fixed "
           "in R-v3 on purpose — one change per version, and the fix is a change "
           "of comparison rather than of control flow. strict=True so that "
           "whoever does fix it is forced to come back and update this record.",
)
@pytest.mark.parametrize(
    "location,why",
    [
        ("Boston, Lincolnshire, United Kingdom",
         "Boston is also a town in England; 'boston' is in locations_ok"),
        ("Remote - anywhere outside the United States",
         "a negation that contains the allowed phrase it negates"),
    ],
)
def test_substring_matching_still_admits_places_the_persona_cannot_take(
    location, why, persona
):
    verdict = rule_judge.judge(
        posting("Software Engineer, Core", "Software Engineering", location).for_rule(),
        persona,
    )
    assert verdict["verdict"] == "not_relevant", why
