"""The written rule, R-v2a — carried over from JS1, reading a normalised view.

**What changed from JS1's R-v2 and what did not.** The four gates, their order,
their comparisons and their verdicts are unchanged, character for character in
intent. What changed is only *where* G3 and G4 read from: JS1's rule reached
into a Greenhouse-shaped dict (`metadata[i].value`, `location.name`), and this
layer watches three applicant-tracking systems that have no such paths. So the
rule now reads `providers.base.Posting.for_rule()`, and every justification
carries **two** field names: the normalised one it compared, and
`provider_field`, the provider-native path that value came from. The provenance
CONTRACT.md O2 demanded in JS1 does not get to lapse because there are now
three providers.

That is amendment A1 in GATE.md §8, and it is a rule *letter* bump rather than
a number bump because it is not supposed to change any verdict. That claim is
testable and is tested: `tests/test_rule_carried_over.py` recomputes R-v2a over
the 163 real Greenhouse postings JS1 captured on 2026-10-31 and asserts the
verdict and the failing gate match what JS1's R-v2 produced for all 163.

**R-v3 (2026-11-09).** G4 no longer treats "remote" as a location. `remote_ok`
became a filter instead of a bypass: a remote posting is rejected outright when
the persona cannot work remotely, and every posting — remote or not — must
match `locations_ok` to pass. This changes verdicts, so it is a number bump,
and `review/review-packet.md` is the record of how the change was reviewed.
`tests/test_rule_carried_over.py` pins exactly which of JS1's 163 verdicts
moved and asserts no others did.

The *other* defect JS1 documented is still here, on purpose: G1 reads seniority
out of the title while the boards state it outright in a `Management Level`
field. One change per version.
"""

from __future__ import annotations

from .fieldpath import whole_word

RULE_VERSION = "R-v3"

GATE_ORDER = ("G1_title_block", "G2_discipline", "G3_job_family", "G4_location")


def _cite(resume_field, resume_value, posting_field, evidence, provider_field=None):
    citation = {
        "resume_field": resume_field,
        "resume_value": resume_value,
        "posting_field": posting_field,
        "evidence": evidence,
    }
    if provider_field:
        citation["provider_field"] = provider_field
    return citation


def _verdict(verdict, gate_failed, justification):
    return {
        "kind": "record",
        "rule_version": RULE_VERSION,
        "verdict": verdict,
        "gate_failed": gate_failed,
        "justification": justification,
    }


def judge(posting: dict, resume: dict) -> dict:
    """Return the rule verdict for one normalised posting.

    `posting` is what `Posting.for_rule()` returns. Gates are evaluated in
    order and the first failure decides, which is what makes `gate_failed`
    meaningful.
    """
    title = posting.get("title") or ""
    title_cf = title.casefold()
    loc = posting.get("location") or {}
    location = loc.get("name") if isinstance(loc, dict) else ""
    location_cf = (location or "").casefold()
    family = posting.get("job_family")
    family_cf = family.casefold() if isinstance(family, str) else None
    pf = posting.get("provider_field") or {}

    passed = []

    # --- G1 title_block ----------------------------------------------------
    for i, token in enumerate(resume["title_block"]):
        if whole_word(token, title_cf):
            return _verdict(
                "not_relevant",
                "G1_title_block",
                [_cite(f"title_block[{i}]", token, "title", token, pf.get("title"))],
            )
    passed.append(
        _cite("title_block", "no blocked token matched", "title", title_cf, pf.get("title"))
    )

    # --- G2 discipline -----------------------------------------------------
    hit = None
    for i, phrase in enumerate(resume["target_title_phrases"]):
        if phrase in title_cf:
            hit = (i, phrase)
            break
    if hit is None:
        return _verdict(
            "not_relevant",
            "G2_discipline",
            [
                _cite(
                    "target_title_phrases",
                    "no target phrase occurs in this title",
                    "title",
                    title_cf,
                    pf.get("title"),
                )
            ],
        )
    passed.append(
        _cite(f"target_title_phrases[{hit[0]}]", hit[1], "title", hit[1], pf.get("title"))
    )

    # --- G3 job_family -----------------------------------------------------
    if family_cf is None:
        return _verdict(
            "not_relevant",
            "G3_job_family",
            [
                _cite(
                    "target_job_families",
                    "the posting carries no job family value",
                    "job_family",
                    "null",
                    pf.get("job_family"),
                )
            ],
        )
    family_hit = None
    for j, phrase in enumerate(resume["target_job_families"]):
        if phrase in family_cf:
            family_hit = (j, phrase)
            break
    if family_hit is None:
        return _verdict(
            "not_relevant",
            "G3_job_family",
            [
                _cite(
                    "target_job_families",
                    "no target job family occurs in this posting's job family",
                    "job_family",
                    family_cf,
                    pf.get("job_family"),
                )
            ],
        )
    passed.append(
        _cite(
            f"target_job_families[{family_hit[0]}]",
            family_hit[1],
            "job_family",
            family_hit[1],
            pf.get("job_family"),
        )
    )

    # --- G4 location (R-v3) ------------------------------------------------
    # `remote_ok` is a filter, not a bypass. In R-v2/R-v2a it only ever widened
    # the gate: any location containing "remote" passed, which admitted
    # "Remote - Ontario, Canada". A posting is now in an allowed location only
    # if `locations_ok` says so, and remote work is separately permitted or not.
    is_remote = "remote" in location_cf
    if is_remote and not resume["remote_ok"]:
        return _verdict(
            "not_relevant",
            "G4_location",
            [
                _cite(
                    "remote_ok",
                    False,
                    "location.name",
                    "remote",
                    pf.get("location"),
                )
            ],
        )
    loc_hit = None
    for i, phrase in enumerate(resume["locations_ok"]):
        if phrase in location_cf:
            loc_hit = _cite(
                f"locations_ok[{i}]", phrase, "location.name", phrase, pf.get("location")
            )
            break
    if loc_hit is None:
        return _verdict(
            "not_relevant",
            "G4_location",
            [
                _cite(
                    "locations_ok",
                    "no allowed location phrase occurs in this location; "
                    "being remote is not itself a location",
                    "location.name",
                    location_cf,
                    pf.get("location"),
                )
            ],
        )
    passed.append(loc_hit)

    return _verdict("relevant", None, passed)
