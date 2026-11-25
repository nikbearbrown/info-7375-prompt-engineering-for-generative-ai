# SOURCES — DataSentry: Project Film

Ethan Gomes · INFO 7375 · 2026-11-23

## Prior work named in the film (part 2)

| Source | What the film uses from it | Read |
|---|---|---|
| R. A. DeMillo, R. J. Lipton, F. G. Sayward, "Hints on Test Data Selection: Help for the Practicing Programmer," *IEEE Computer* 11(4):34–41, April 1978, doi:10.1109/C-M.1978.218136 | Mutation testing: plant small faults in a program and grade a test suite by how many it catches (B02). | 2026-11-23 (bibliographic record and course notes summarising it) |
| S. Schelter et al., "Automating Large-Scale Data Quality Verification," *PVLDB* 11(12):1781–1794, 2018 — https://www.vldb.org/pvldb/vol11/p1781-schelter.pdf | Amazon's Deequ: declarative "unit tests for data", with automatic constraint suggestion (B03). Not run (it needs Apache Spark). | 2026-11-23 (abstract and AWS blog summary) |
| dbt docs, "Add data tests to your DAG" — https://docs.getdbt.com/docs/build/data-tests | dbt runs data tests on tables (B03). | 2026-10-14 |
| Great Expectations — https://greatexpectations.io/ ; GX blog, "2025 In Review" (2026-01-09) — https://greatexpectations.io/blog/2025-in-review-building-trust-into-your-data-work/ | GX Core runs expectations on tables; GX Cloud's paid ExpectAI "generates suggested Expectations you can review, refine, and approve" (B03, B04). ExpectAI not run. | 2026-10-14 |
| pandera — https://github.com/unionai-oss/pandera | Data-frame checks; the library the checks are written in (B03, B08). | 2026-10-14 |
| N. Alshahwan et al., "Automated Unit Test Improvement using Large Language Models at Meta," FSE 2024 Industry — https://arxiv.org/abs/2402.09171 | TestGen-LLM on Instagram Reels and Stories: 75% of test cases built correctly, 57% passed reliably (B04). | 2026-11-23 (abstract) |
| M. Foster et al., "Mutation-Guided LLM-based Test Generation at Meta," FSE 2025 Companion — https://arxiv.org/abs/2501.12862 ; Meta engineering blog (2025-02-05) | ACH generates tests aimed at planted faults (mutants); engineers accepted 73% of its generated tests in the test-a-thons (B04). | 2026-11-23 (abstract) |
| NYC TLC Trip Record Data — https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page | The public data (B06). | 2026-10-14 |

The comparison grid (B05) is **constructed** from these sources and labelled so on screen. "In what I found" means
in these sources; it is not a claim that no such tool exists anywhere.

## What I ran (recorded, 2026-10-25)

All numbers on the recorded panels (B03, B13) come from `first-run/results/2026-10-25/`, unedited:

- `run_all.sh` (06:16): one rule, `fare_amount >= 0`, in pandera 0.29.0, dbt-core 1.10.23 + dbt-duckdb 1.10.1, and
  GX Core 1.24.1, on a clean 10,000-row sample and a broken copy (25 negative fares, 25 drop-offs before pick-up).
- `score_round.sh 1` and `2` (17:25): the hand-written baseline and Claude's two rounds, on plantings seed 25 and 99.
- Claude's two replies: Claude desktop app, model Opus 5.5, effort High, 2026-10-25, saved verbatim in
  `first-run/claude-checks/` with the prompts that produced them.

## What I ran (recorded, 2026-11-23)

- `first-run/run_loop.sh` (18:24–18:25, run by me in my terminal): 13 tests OK, then the live loop — Claude Code
  2.1.330 headless, `claude-opus-5-5`, effort high, no tools — three rounds, stopped on "pass line met". Every prompt,
  raw reply (with model usage), checks file, score and decision is in `first-run/loop-runs/2026-11-23_182418/`. Each raw reply includes Claude Code's `total_cost_usd` estimate (about $0.49 for the three rounds, at API rates); on my subscription there is no per-call charge.
- After the run, Claude Code wrote and ran `first-run/heldout_clean.py` on each round's checks (unchanged): a second,
  disjoint 10,000-row clean copy (seed 2026). Results are next to each round (`round<N>/loop-round<N>-heldout-clean.*`).

## What I made

- `APPENDIX.md` — methods and evaluation in detail.
- `film/make_sheet.py` → `beat_sheet.json` — narration and visual plan, 18 beats in the assignment's four parts.
- `film/scenes_body.py` — the 18 drawn scenes (Manim).
- `first-run/` — copied from my pitch folder: the planter, scorer, checks, prompts, Claude's replies and recorded runs.
- The rendered film and its subtitles.

## What Claude contributed

- **Claude as the thing being tested**: wrote the two hand-run rounds of checks (Claude desktop app, Opus 5.5,
  2026-10-25) and the three loop rounds (Claude Code headless, `claude-opus-5-5`, 2026-11-23) scored in B13.
- **Claude as my build assistant** (Claude Code, Opus 5.5, 2026-11-23): searched for and summarised the prior work above
  (I chose what to include), drafted the narration, the beat sheet, the scene code, this file, `APPENDIX.md` and the
  build paperwork, and ran the toolkit's audio, render and quality gates. It also wrote `loop.py`, `run_loop.sh`, `tests/test_loop.py` (the tests first) and `heldout_clean.py`, ran
  the tests and one fixture replay, and made one two-word smoke-test call to check the headless flags. Earlier
  (2026-10-25) it wrote the other `first-run/` scripts and drafted the two prompts.
- I chose the project, the four-part content, the plan (three rounds, the pass line, the free subscription route), and
  I ran the first-run scripts, both scoring rounds and the live loop myself.

## Tools and assets (all free, all local)

| Asset | Use | Licence |
|---|---|---|
| Brutalist toolkit (github.com/nikbearbrown/brutalist.art, commit 519fcbb) | pipeline, gates, show-tell drawing kit, approved original isometric props | No LICENSE file found at that commit; used as the course directs |
| Kokoro-82M via kokoro-onnx, voice `am_michael` | narration (a stock synthetic voice reading my script) | Apache 2.0 |
| faster-whisper (`small.en`) | pronunciation check of each clip | MIT |
| Manim Community v0.20.1 | drawn scenes | MIT |
| EB Garamond, Menlo | on-screen type | SIL OFL 1.1; macOS system font |
| ffmpeg | encode, subtitles track | LGPL/GPL |
| pandas, pyarrow, pandera, duckdb, dbt-core, dbt-duckdb, great_expectations | `first-run/` | BSD-3, Apache 2.0, MIT, MIT, Apache 2.0, Apache 2.0, Apache 2.0 |
| NYC TLC trip record data | the data | NYC open data |

No paid generation, API keys, stock media, music, or third-party images were used.
