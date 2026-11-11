"""Isaac's six checks from CONTRACT "The rule", one function each, listed in order in CHECKS.

One function per check (instead of one long judge) so each can be read and tested on its own,
and adding a check is one function plus one registry line. Every check returns a justification
line even when it passes, because the record must show each step a TA would redo by hand.
"""

from dataclasses import dataclass, field
from typing import Callable

from . import verdict
from ..common.posting import Posting
from .words import has_all_words, has_phrase, salaries_in, strip_html, words, years_in


@dataclass(frozen=True)
class Criteria:
    """The job seeker's side, built once per run and shared by every posting."""
    resume_keywords: list[str]
    profile: dict
    aliases: dict[str, list[str]]   # lowercased skill -> other spellings (built-in + profile, D9)
    phrases: list[str]              # "no sponsorship" phrases
    # The whole résumé, only for the Claude judge (CONTRACT: Claude sees the résumé); the rule's
    # checks read resume_keywords only. Defaulted so a Criteria built for the rule alone still works.
    resume: dict = field(default_factory=dict)


@dataclass(frozen=True)
class PostingText:
    """A posting turned into words once, so six checks don't each re-split the same JD."""
    title: set[str]
    location: set[str]
    location_words: list[str]   # ordered, to tell "N/A" or a bare "Remote" from a real place
    jd: str               # HTML removed
    jd_words: list[str]   # ordered, for whole-phrase matching
    jd_set: set[str]      # unordered, for word matching

    @classmethod
    def of(cls, posting: Posting) -> "PostingText":
        jd = strip_html(posting.content)
        jd_words = words(jd)
        loc = words(posting.location)
        return cls(set(words(posting.title)), set(loc), loc, jd, jd_words, set(jd_words))


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    line: dict


@dataclass(frozen=True)
class Check:
    id: str
    name: str
    run: Callable[[PostingText, Criteria], CheckResult]


def _matches(phrases: list[str], text_words: set[str]) -> str:
    return ", ".join(p for p in phrases if has_all_words(p, text_words))


def exclude_words(t: PostingText, c: Criteria) -> CheckResult:
    hit = _matches(c.profile["exclude_title_words"], t.title)
    return CheckResult(not hit, verdict.line("title", "profile.exclude_title_words[]", f"match: {hit}" if hit else "no match"))


def title(t: PostingText, c: Criteria) -> CheckResult:
    hit = _matches(c.profile["target_roles"], t.title)
    return CheckResult(bool(hit), verdict.line("title", "profile.target_roles[]", f"match: {hit}" if hit else "no match"))


# location.name values that say nothing about where the job is: "", "N/A" -> [n, a], "na", and a bare
# "Remote" with no country. Isaac: "no location written counts as a pass"; same lean as checks 4-6 (not written ->
# pass), so a posting is never cut on a field the board left blank. Compared as word lists (one splitter).
NO_LOCATION = ([], ["n", "a"], ["na"], ["remote"])


def location(t: PostingText, c: Criteria) -> CheckResult:
    field = ("location.name", "profile.locations[]")
    if t.location_words in NO_LOCATION:
        return CheckResult(True, verdict.line(*field, "skipped: no location in posting"))
    hit = _matches(c.profile["locations"], t.location)
    return CheckResult(bool(hit), verdict.line(*field, f"match: {hit}" if hit else "no match"))


def skills(t: PostingText, c: Criteria) -> CheckResult:
    found = []
    for kw in c.resume_keywords:
        # The keyword itself first, then its aliases; the result says which spelling hit (D9).
        for spelling in [kw] + c.aliases.get(kw.lower(), []):
            if has_all_words(spelling, t.jd_set):
                found.append(kw if spelling == kw else f"{kw} (as {spelling})")
                break
    result = f"{len(found)} found" + (f": {', '.join(found)}" if found else "")
    return CheckResult(bool(found), verdict.line("content", "resume.skills[].keywords[]", result))


def years(t: PostingText, c: Criteria) -> CheckResult:
    field = "profile.years_experience + profile.years_stretch"
    p = c.profile
    if "years_experience" not in p or "years_stretch" not in p:
        return CheckResult(True, verdict.line("content", field, "skipped: not set in profile"))
    found = years_in(t.jd)
    if not found:
        return CheckResult(True, verdict.line("content", field, "skipped: no years in posting"))
    limit = p["years_experience"] + p["years_stretch"]
    # Smallest number: leaning toward keeping a posting rather than cutting it on a misread number.
    ok = min(found) <= limit
    return CheckResult(ok, verdict.line("content", field, f"min {min(found)} years {'≤' if ok else '>'} {limit:g}"))


def visa(t: PostingText, c: Criteria) -> CheckResult:
    field = "data/no_sponsorship_phrases.json"
    if c.profile.get("needs_sponsorship") is not True:
        reason = "profile.needs_sponsorship is false" if "needs_sponsorship" in c.profile else "not set in profile"
        return CheckResult(True, verdict.line("content", field, f"skipped: {reason}"))
    hits = [ph for ph in c.phrases if has_phrase(ph, t.jd_words)]
    return CheckResult(not hits, verdict.line("content", field, f"found: {', '.join(hits)}" if hits else "no phrase found"))


def salary(t: PostingText, c: Criteria) -> CheckResult:
    field = "profile.min_salary"
    if "min_salary" not in c.profile:
        return CheckResult(True, verdict.line("content", field, "skipped: not set in profile"))
    pay = salaries_in(t.jd)
    if not pay:
        return CheckResult(True, verdict.line("content", field, "skipped: no salary in posting"))
    # Largest amount: the top of a posted range is what the posting could pay.
    ok = max(pay) >= c.profile["min_salary"]
    return CheckResult(ok, verdict.line("content", field, f"max ${max(pay):,} {'≥' if ok else '<'} ${c.profile['min_salary']:,.0f}"))


# CONTRACT order. The first failing check decides not_relevant.
CHECKS = [
    Check("1a", "exclude words", exclude_words),
    Check("1b", "title", title),
    Check("2", "location", location),
    Check("3", "skills", skills),
    Check("4", "years", years),
    Check("5", "visa", visa),
    Check("6", "salary", salary),
]
