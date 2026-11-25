"""F3 after amendment A1: a denylist of non-engineering functions.

FILTER.md §7 A1. The inherited F3 required the family value to match
Greenhouse's `Job Family` vocabulary, so the same job passed or failed
depending on which applicant-tracking system the company bought. There is no
vocabulary the three systems share, so F3 stops requiring a positive match and
instead stops the case it was really there for: a posting filed under a
function that is not engineering.

Each entry asserts something true at any company, not something about one
company's org chart. A posting filed under Payroll is not a software
engineering job whatever its title says.

An absent or null family passes: absence is not denial (E3), and F2 has
already read the title.
"""

from __future__ import annotations

#: substrings of the lower-cased family value. One entry catches
#: "Advertising Sales - Enterprise" and "Advertising Business Marketing".
NON_ENGINEERING_FUNCTIONS: tuple[str, ...] = (
    "sales",
    "marketing",
    "legal",
    "finance",
    "accounting",
    "payroll",
    "tax",
    "human resources",
    "people & talent",
    "recruiting",
    "pr & communications",
    "government affairs",
    "business development",
    "deal desk",
    "customer experience",
    "advertising",
    "music business",
)

F3_VERSION = "F3-denylist (A1)"


def f3_rejects(job_family: str | None) -> str | None:
    """Return the denylist entry that rejects this family, or None to pass."""
    if not job_family:
        return None
    value = job_family.casefold()
    for entry in NON_ENGINEERING_FUNCTIONS:
        if entry in value:
            return entry
    return None
