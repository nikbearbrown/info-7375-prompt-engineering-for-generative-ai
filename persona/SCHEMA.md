# Résumé JSON schema (what `jsagent/resume.py` validates)

The agent refuses to load a résumé that breaks any of these rules.

| Path | Type | Rule |
|---|---|---|
| `_comment` | string | must contain `FICTIONAL` |
| `personal.name`, `personal.location` | string | required |
| `personal.email` | string | must end in `@example.com` |
| `personal.phone` | string | must contain a `555-dddd` number |
| `education`, `experience` | list | required |
| `skills` | object of string lists | at least one non-empty list. R4 counts every list except `familiar_with_not_shipped` |
| `search.target_titles` | non-empty list of strings | R1 |
| `search.excluded_title_terms` | list of strings | R2 |
| `search.locations` | non-empty list of `"City, ST"` strings | R3 |
| `search.open_to_remote` | boolean | R3 |
| `search.open_to_relocate` | boolean | R3 (on-site/hybrid outside Boston) |
| `search.us_location_markers` | non-empty list of strings | R3 (whole word, case-sensitive): US/USA/United States, state names and codes, listed metros |
| `search.relocation_scope` | string | informational |
| `search.max_required_years` | integer | R5 pass/fail (5) |
| `search.preferred_max_years` | integer | R5 preferred-years flag (4) |
| `search.years_experience` | integer | informational (sent to Claude, not used by the rule) |

Also: every string anywhere in the file that looks like an email must end in `@example.com`.

`evan-gordon.resume.json` is a **fictional** persona invented for this assignment on 2026-10-31, created as "Jordan Okafor" and renamed in v2.4 (v2.1 added `data analyst` to `search.target_titles`; v2.2 added `skills.bi_tools`: Tableau, Power BI; v2.3 replaced `remote_regions` with `open_to_relocate` + `us_location_markers`): a data
engineer with about 4 years of experience (Data Engineer 2021–2023 + co-op Jan–Jul 2026; MS Information Systems 2024–2026, BS Computer Engineering; kept realistic for a ~4-year data engineer, v2.5), employers marked "(fictional)", an @example.com address, and a 555 phone number.
The v1 persona (Rohan Desai, copied from The Reallocation Engine's `search/examples/`) was used in v1 only
(its files were removed before submission). A real résumé must never go in this folder. `.gitignore` blocks `resume.json`
and `*.real.json`.
