# Where filter v1.0 had to interpret FILTER.md (Claude Code, 2026-11-25)

FILTER.md v1.0 (`a3a7a2af`) did not settle these points. Claude Code chose the readings below while
implementing `jobfilter/filter.py` and `filters/v1.0.json`. These are not decisions by Ashwin until marked so.
Ashwin reviewed them retrospectively on 2026-11-25; see the section at the end.

| # | Gap in FILTER.md | Reading in v1.0 | Effect in the corpus (`runs/v1.0/location-coverage.md`) |
|---|---|---|---|
| I1 | One Greenhouse field lists several cities: `Boston, MA; Denver, CO` | Each `;` part is a separate alternative | 6 Klaviyo values |
| I2 | `Flex - Dublin, Ireland`, `Office - Bengaluru, India` | The `Flex -` / `Office -` prefix is a workplace label and is ignored | 99 values |
| I3 | Greenhouse repeats the city as a bare office (`London, UK` + `London`) | A bare office equal to another alternative's city is the same place | Without this, every non-US Klaviyo posting would be REVIEW instead of REJECT |
| I4 | `Remote, Bay Area, CA, US` | Remote within a named US area = **US location (1)**, not US-remote (2) | 7 Supabase values |
| I5 | §3 says to read structured remote fields | Ashby `isRemote`/`workplaceType` and Lever `workplaceType`/`country` are saved and shown by the tool, **not scored**. Notion reports `isRemote: true` together with `workplaceType: Hybrid` for San Francisco jobs, so the flag alone did not settle remote status | Displayed only |
| I6 | "Explicitly outside the US" needs a word list | Non-US countries and regions listed in `filters/v1.0.json`. `Remote, AMER`, `North America` and `Remote, Global` are **unresolved** (REVIEW) | 55 unresolved values |
| I7 | "City plus US state" with 2-letter codes | Read literally, so **`Munich, DE` = Delaware, US (1)**. Left unfixed as a false-friend candidate for the audit | 1 value |
| I8 | "Known to be truncated" | No truncation signal exists in these feeds, so only empty content becomes REVIEW | 0 postings had empty content |
| I9 | §8: do not inspect held-out predictions | The tool server refuses all 30 held-out keys, and their decisions are in a sealed file | — |

One implementation bug was found and fixed **before** the v1.0 run was committed. `Washington, D.C.` (66 postings) at
first read as unresolved, because "Washington" was matched as a state name before the city-alias check ran.
FILTER.md lists that city alias, so the check order was fixed.

## Ashwin's retrospective review (2026-11-25, after implementation)

Ashwin gave these decisions in chat on 2026-11-25, **after** filter v1.0 and v1.1 had been implemented and run.
They did not guide the implementation.

- **No change to code or results.** The code, the committed runs and every reported number stay as they were.
- **Disagreements are not fixed.** They are recorded as unresolved limitations.

| # | Ashwin's decision | Status |
|---|---|---|
| I1, I2, I3 | Agree with the normalization, provided genuinely different or ambiguous locations remain distinguishable | Agreed, with that condition. No check of the condition was added |
| I4 | Agree. Region-restricted remote work should not imply remote work from anywhere in the US | Agreed |
| I5 | **Disagree** with ignoring structured remote fields in scoring. Conflicting fields should lead to REVIEW under the gate | **Unresolved limitation.** Not implemented; v1.0 and v1.1 still ignore structured fields when scoring |
| I6 | Agree. Broad regions that do not establish US eligibility stay unresolved | Agreed |
| I7 | **Disagree.** `Munich, DE` must not be read as Delaware | **Known unresolved parsing defect.** Not fixed. It did not change that posting's final decision, which is REJECT because the title has no qualifying role phrase |
| I8 | Accepted **only as an implementation limitation**, not as full compliance with the truncation rule. Non-empty text can still be incomplete | Limitation |
| I9 | Agree, as a workflow safeguard, not a security boundary | Agreed. The held-out comparison stays labeled potentially contaminated |
