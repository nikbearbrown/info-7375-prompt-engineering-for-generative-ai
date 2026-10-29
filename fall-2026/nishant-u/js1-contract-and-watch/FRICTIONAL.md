# FRICTIONAL — Job-Search Agent 1 (nishant-u)

An honest log of what I tried and what happened. Entries were drafted with Claude Code from the
session record on the dates shown; I review and edit them before submitting.

## 2026-10-29 — Board choice: Faire, not the retailers in my pitch

**Tried.** My pitch named retail and e-commerce companies. I sent GET requests (no login) to the public
JSON endpoints of Greenhouse, Lever and Ashby for ten names: wayfair, chewy, etsy, warbyparker,
instacart, faire, stitchfix, thredup, glossier, peloton.

**Happened.** Lever and Ashby returned 404 for all ten. Greenhouse returned postings for five: instacart
(93 postings, 13 data-like titles), faire (68, 25), peloton (58, 4), glossier (19, 0), stitchfix
(14, 0). **Wayfair, Chewy, Etsy, Warby Parker and thredUp had no public board on any of the three
systems** under those names. "Data-like" was a title keyword count, not a label.

**Decided.** Faire on `boards-api.greenhouse.io`, with Instacart as the backup: enough postings, and a
real mix of data and non-data roles. Faire is a wholesale marketplace (B2B e-commerce), not a classic
retailer, so this departs from my pitch.

**Unresolved.** I didn't look for other board tokens or other applicant systems for the five missing
companies. Greenhouse's Job Board API docs say GET endpoints need no authentication; I found no rate
limit or terms of use for public API readers there, and I have not yet read Faire's own careers-site
terms.

## 2026-10-29 — Persona mismatch: Priya Nair is ML-infra, not data analytics

I remembered Priya Nair as a data-analytics persona. Her `profile.yml` actually targets "LLM-platform
and ML-infrastructure roles; Databricks/LangGraph stack." I kept her as the fictional résumé. The
rule's title terms (data, analytics, analyst, scientist, machine learning, ML) cover both readings,
but the mismatch with my pitch is still there and I need to address it in the write-up.

## 2026-10-29 — A read-only check that was wrong: agent_note split into letters

**Happened.** On 2026-10-29, before the contract was written, Claude Code ran a read-only check of how
many of Priya's skills appear in Faire postings. Claude Code wrote that script; I didn't. Its first
version took every value under `skills` and iterated it. `skills.agent_note` is a string ("No
certification claims - none exist for this persona."), so it was read letter by letter, and single
letters such as `a` and `s` counted as matched skills. Every posting appeared to match 16–28 skills.

**Caught by.** Claude Code itself, in the same check. The numbers were implausible (a non-data posting "matched" as many skills as a data
one), and the printed match list was mostly single characters and spaces. The rerun, using only the
list-valued fields, gave 0–4 skills per posting.

**Changed.** I made this wrong version 3 in my contract, `CONTRACT.md`, and the mutant `string_skills` in
`tests/mutants.py`, caught by `test_3_skills_read_from_string_is_caught`.

## 2026-10-29 — Allowing Senior and Staff titles

On Faire's board (live, 2026-10-29), every data, analytics or scientist title that is not a manager,
director, head, lead or intern role is Senior or Staff. Excluding seniority would leave no relevant
postings at all, so relevance would be trivially all-no. The contract says it outright: "Seniority fit
is **not** judged." That is a limit of this rule, not a claim that Priya is a fit for Staff roles.

## 2026-10-29 — Failures and surprises while building

- **Tests before implementation failed as expected.** At commit A, all 35 tests errored with
  `ModuleNotFoundError: No module named 'agent'`, because nothing was implemented yet.
- **A tool check was blocked.** Checking whether `ANTHROPIC_API_KEY` was set, the first command used
  `${ANTHROPIC_API_KEY:-no}`, which would have printed the key's value if one existed. Claude Code's
  safety check blocked it; the rewritten command printed only "set" or "unset". It was unset, and
  `claude -p` ran on my login.
- **`python -I -m agent.run` failed** with `No module named 'agent'`: isolated mode leaves the current
  folder off `sys.path`. The tests had passed only because `unittest discover -t .` adds that folder.
  The documented command, `python3 -m agent.run` from this folder, works.
- **Line endings.** Git on this machine converts line endings, which would change the bytes of saved
  responses and break their sha256. `.gitattributes` marks `runs/**/raw.json` and Claude replies as
  `-text` so they are stored exactly.

## 2026-10-29 — Hand-labeling the 20 postings

2026-10-29: I hand-labeled all 20 postings in Excel by applying R1–R4 in order (title, title, location, then Ctrl+F for the 10 shipped skills in the .txt files). While labeling I asked Claude (claude.ai) how the rule reads on word forms (e.g. that 'AI/ML' contains ML, that 'Leader' is not 'lead', that 'ML models' in the text is not a skill for R4). I shared the 20 titles and locations with claude.ai, including the held-out ones; Claude explained rule wording and did not label any posting.

## 2026-10-29 — Tests added after the implementation for three safety claims

The draft of `experiment/ACTION-SURFACE.md` said the watch and state were "handled by tested code".
Claude Code pointed out that the claim was broader than the tests: only the host allow-list had a
test. The redirect re-check, the atomic state write and `--tools ""` were in the code but untested. I
had `tests/test_safety.py` added after the implementation:
- a redirect to a non-allow-listed host is refused before any request to it;
- a state write that fails after the temp file is written, or partway through writing, leaves the old
  `seen_ids.json` unchanged;
- the judge's command always includes `--tools ""`, and the judge runs in an empty folder.

Each test failed against a deliberately broken version before passing against the real code.

## 2026-10-29 — Sampling-report conclusion: a wrong claim caught before commit

My sampling-report conclusion (drafted with Claude in claude.ai) said the not-relevant calls were decided by title or location; Claude Code checked it against results.json and found none were decided by location (three by title, one by R4). Corrected before commit.

## Open: implementation choices I have not reviewed yet

Claude Code made these choices while implementing my contract. They are listed so I can accept,
change or reject each one; none had been reviewed when this list was written. My decisions are below it.

- R3 markers: entries starting with `, ` must end a location part; `Remote - US` must equal it. Only
  the 50 state codes are listed: `, DC` is not.
- Rule citations for R1–R3 have `resume_field: null`, because those checks don't read the résumé.
- Absence is cited with `quote: null` plus `absent_terms`, and the support check re-verifies the
  absence.
- The validator accepts an empty string as `quote`, and the support check would mark it supported,
  since `""` is a substring of every field. The contract doesn't rule this out.
- The Claude judge runs with `--tools ""` in an empty temporary folder, so this repository's
  CLAUDE.md is not in its context.

### My decisions, 2026-10-29

- R3 markers: keep the 50-state list. `, DC` is not counted; it goes under "Not checked" in the sign-off.
- `resume_field: null` for R1–R3: keep.
- Empty quotes: fixed by the 2026-10-29 contract amendment (`CONTRACT.md`, Amendments). The validator
  now rejects an empty or blank quote, and the support check marks it not supported.
- Not decided yet: absence cited with `quote: null` plus `absent_terms`; the judge running with
  `--tools ""` in an empty temporary folder.
