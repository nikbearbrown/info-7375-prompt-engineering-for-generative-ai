# Seeded Faults: project film (four-part), LOCKED SCRIPT

**Status:** v2 drafted by Claude Code on 2026-11-22. All placeholders are now filled from decisions Atharva locked in `FAULT-CATALOGUE.md` (commit `e5aac1c`, 2026-11-22 17:09). Locked by Atharva on 2026-11-22 ("Locked, build it"); I3, M3, M4, V1 and V3 were revised afterwards at Atharva's request (see Length). This is the narration as rendered in `seeded-faults-project.mp4`.
**Structure:** Professor Bear's email. Executive summary → Introduction (prior work) → Methods → Evaluation.
**Length:** 593 words; rendered film 3:57 (237.2 s). v1 was about 870 words, roughly 6 minutes. I3, M4 and V1 were reworded on 2026-11-22 to meet the email's requirements (prior work's results and why it matters; plan and credits; checking the tool itself), M3 got back its run-and-score step, and E2, I3, M4 and V3 were trimmed to stay under 4 minutes.

## Wording notes
- **I2 says "Pandera's schema inference, run on my data".** It was rendered before Atharva's rerun, so it avoids "I ran". Atharva reran both pandera scripts on 2026-11-22 with identical results, so the line is accurate either way.
- **I1 says "a hand-written check".** In October, Claude wrote the sandbox scripts and you ran them (SOURCES.md of the pitch says so). So the film says "hand-written" (not tool-suggested), not "my check".
- Every number below is in an evidence file. The fact-check table is at the bottom.

---

## Script

### PART 1: EXECUTIVE SUMMARY (~45 s, no "how")

**E1:** *Picture: one table icon, a row of green checkmarks; one turns into a question mark.*
> Hi, I'm Atharva. My final project is Seeded Faults: a tool that checks whether the data-quality tests on a table would actually catch bad data, or just pass.

**E2:** *Picture: green "all tests passed" badge with a crack running through it.*
> That matters because a test that has never failed hasn't proven anything. And now that AI can write tests in seconds, it's easy to ship tests that look complete and that nobody has checked.

**E3:** *Picture: scoreboard with fault rows and CAUGHT / MISSED columns, rows empty. Label: CONSTRUCTED, no results yet.*
> Seeded Faults will score a test suite: from a fixed list of problems, what it caught and what it missed. It'll be a public repository anyone can rerun with one command. It isn't built yet. This film is the plan.

### PART 2: INTRODUCTION, WHAT OTHERS HAVE DONE (~65 s)

**I1:** *Picture: two tool boxes (Great Expectations, dbt), each with a hand-written checklist; "50 / 50" beneath.*
> First, what already exists. In October I tried Great Expectations and dbt. I planted fifty missing values in real New York taxi data, and a hand-written check caught all fifty. But neither tool told me what my checks would miss.

**I2:** *Picture: three boxes labelled "drafts checks for you": Deequ, older Great Expectations, pandera. The pandera box opens to a real excerpt of `output_holdout.txt`, labelled "real output, 2026-11-22".*
> Some tools draft the checks for you: Amazon's Deequ, older versions of Great Expectations, and pandera. Pandera's schema inference, run on my data, caught the same fifty. But on five fresh, clean samples from the same month, it flagged thirteen to twenty-five rows every time. I haven't checked yet whether those rows are really bad.

**I3:** *Picture: a code file with red "mutant" marks → a data table with the same marks → a paper card "IBM Research, arXiv, 2025".*
> Planting bugs on purpose is an old idea: mutation testing goes back to 1978. And a 2025 IBM Research paper already has AI write data checks, then measures how many injected errors those checks catch. So my part is narrower: the dbt tests data teams actually ship, faults specific to one real table, and false alarms counted alongside catches. That matters because those tests guard real pipelines, and a score tells you which to trust.

### PART 3: METHODS, HOW I'LL BUILD IT (~75 s)

**M1:** *Picture: taxi icon → table labelled "NYC TLC Yellow Trips, Jan 2024 (public)"; a laptop.*
> Here's the plan. The data is public: New York's yellow taxi trips for January 2024. Everything runs locally on my laptop, with DuckDB and dbt.

**M2A:** *Picture: a bar of ~3 million trips with slivers marked "negative fare 1.3%" and "zero distance 2.0%", then filtered down to "2.7 M clean". Real numbers from `evidence/2026-11-22-data-profile/` and `baseline-check/`.*
> Step one was deciding what clean means. When I profiled the month, about three million trips, some of my faults were already there: over one percent of fares are negative, and two percent of trips have zero distance. So I filtered those out first, leaving about two point seven million clean rows.

**M2B:** *Picture: the real `FAULT-CATALOGUE.md` with `e5aac1c · 2026-11-22` on screen and a padlock.*
> Step two: lock the faults. I wrote eighteen fault types, with my pass-fail line, and committed them on November twenty-second, before any test was written, so anyone can check the list came first.

**M3:** *Picture: a stamp planting 50 marks into each of 18 copies of a table labelled "10,000-row holdout"; three test files (mine, Claude's, pandera) aimed at the copies. Label: CONSTRUCTED, planned.*
> Next, I'll build a script that plants each fault, fifty rows at a time, into its own copy of a ten-thousand-row holdout. I'll write my own dbt tests first. Then Claude Code writes its tests from a separate sample, so it never sees the holdout. Then every suite runs against every copy, and gets scored.

**M4:** *Picture: checklist: public data ✓ downloaded · DuckDB + dbt ✓ free, local · Claude Code ✓ Opus 5.5, max 3 prompts.*
> The data's free, the tools are free, and Claude Code runs on my Claude Pro plan with Opus 5.5, capped at three prompts so I can't keep tuning it. No other accounts or paid compute are needed.

### PART 4: EVALUATION, HOW I'LL KNOW IT WORKED (~50 s)

**V1:** *Picture: a balance: "faults caught" on one side, "false alarms" on the other.*
> How will I know it worked? First, I'll check the tool itself: every faulted copy must have exactly fifty bad rows, and a test written for each fault must catch it. Then two numbers. Catch rate: how many of the eighteen faults a suite flags. And false alarms: how many of its tests fail on clean data.

**V2:** *Picture: a line across a chart labelled "set 2026-11-22, before building": ≥ 15 / 18 caught · ≥ my suite · ≤ 5% false alarms.*
> I set the line before building. Claude's tests pass if they catch at least fifteen of the eighteen, at least as many as mine, and no more than five percent of them fail on clean data. If they fall short, that isn't the project failing. That's the finding.

**V3:** *Picture: the cracked badge from E2 beside the empty scoreboard; "next: fault-injection script".*
> So that's Seeded Faults: tests for your data, tested. Next up: the fault-injection script.

---

## Fact check (every number or claim in the narration)

| Beat | Claim | Source |
|---|---|---|
| I1 | 50 planted nulls, 50 caught, GX and dbt, October | `../final-project-film/evidence/2026-10-09-first-planted-fault/` |
| I2 | Deequ suggests constraints | PRIOR-WORK-CHECK.md (AWS blog, PyDeequ docs) |
| I2 | Older GX drafted expectations | PRIOR-WORK-CHECK.md (GX 0.15/0.16 legacy docs) |
| I2 | pandera caught 50; flagged 13–25 rows on 5 fresh samples | `evidence/2026-11-22-pandera-infer-schema/` (rerun by Atharva 2026-11-22 ✓) |
| I3 | Mutation testing dates to 1978 | DeMillo, Lipton, Sayward, IEEE Computer 11(4), 1978 |
| I3 | 2025 IBM Research paper scores LLM-written checks vs injected errors | arXiv 2509.10572 |
| M2A | ~3 M trips; 1.26% negative fares; 2.04% zero distance | `evidence/2026-11-22-data-profile/output.txt` (rerun by Atharva 2026-11-22 ✓) |
| M2A | ~2.7 M clean rows (2,696,560) | `evidence/2026-11-22-baseline-check/output.txt` (rerun by Atharva 2026-11-22 ✓) |
| M2B | 18 faults committed 2026-11-22 before any test | git commit `e5aac1c` |
| M3, M4, V2 | 10,000-row holdout, 50 rows/fault, separate sample, Opus 5.5, 3 prompts, ≥15/18, ≤5% | `FAULT-CATALOGUE.md` |

## Honesty check
- Past tense only for: the October hand test, the pandera run (after your rerun), the profile, the filtering, and the catalogue commit. Everything else is "will".
- E3 and M3 pictures are labelled CONSTRUCTED. M2B and I2 show real files and output, dated.
