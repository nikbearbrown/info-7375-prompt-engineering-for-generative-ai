# SOURCES — Job-Search Agent 1

## What I used
- **Assignment brief:** "Job-Search Agent 1 — The Contract and the Watch" (INFO 7375, Canvas).
- **Fictional persona:** Priya Nair, from Prof. Brown's Reallocation Engine,
  `search/examples/priya-nair/` (`resume.example.json` copied unchanged; target roles
  and the clearance exclusion copied from her fictional `profile.yml` into
  `data/target.example.json`).
- **Job board:** Scale AI's public Greenhouse Job Board API,
  `https://boards-api.greenhouse.io/v1/boards/scaleai/jobs?content=true`
  (public endpoint, read only; no login, no applying).
- **Python 3 standard library** only. **Claude Code CLI** v2.1.316 (Northeastern Claude Enterprise).
- No other students, starter code, or external code. No collaborators.

## What Claude contributed
**Claude (claude.ai chat, in my course Project)**
- Planned the assignment with me step by step and compared options. It recommended
  Aarav first, then Priya after seeing all four personas, and recommended Scale AI
  over Databricks. I made each choice.
- Drafted the wording of `CONTRACT.md` and `data/target.example.json` from my decisions.
- Wrote the build prompt I gave Claude Code.
- Wrote these scripts: `tools/make_seeded_earlier.py`, `tools/make_label_sheet.py`,
  `tools/make_label_sheet_v2.py`, `tools/label.py`, `tools/label_v2.py`,
  `tools/claude_trials.py`, and the one-off snippets that built the action-surface
  prompt, the seeded action-surface file, and `label_audit_evidence.txt`.
- Wrote both prompt templates in `reports/prompt_experiment/prompts/`.
- Proposed a starting labeling rule. Pointed out that my first random sample had a
  base-rate problem and suggested stratified re-sampling.
- Flagged hand labels that contradicted my own written rule (for example, a TS/SCI-required
  posting I had labeled relevant). Proposed the three post-hoc audit readings.
- Drafted `SAMPLING_REPORT.md`, `PROMPT_EXPERIMENT.md`, `ACTION_SURFACE.md`,
  `README.md`, and this file from my real runs and commits.
- Drafted my FRICTIONAL entries for 2026-10-30 and 2026-10-31 from each day's actual
  events, plus example reflections for 2026-10-31. I edited them and filled in my own reasons.

**Claude Code (v2.1.316, Opus 5.5)**
- Wrote all of `agent/` and `tests/` (42 tests, including `tests/mutants.py` for the
  contract's two wrong versions) from my `CONTRACT.md`, and chose the 11 interpretations
  it listed (e.g. double HTML unescaping, whole-word matching everywhere).
- In auto mode, before I switched it off, it created `tools/make_seeded_earlier.py`
  from text I pasted and ran one CLI check on its own.

**Claude as a judge (data, not authorship)**
- Every Claude verdict in `reports/` is model output from actual calls on 2026-10-31,
  labeled as a judgment. Raw replies are saved.

## What I did myself
- **Decisions:** persona (Priya), board (Scale AI), a separate target file instead of
  skills-only, and every permission choice: declined the external `AGENTS.md` import,
  declined trusting my home folder, switched auto mode off, and kept live fetches for myself.
- **Labeling rule changes:** at most 2 years of experience with internships counting,
  the sponsorship condition, data science/analytics roles, and the US-location amendment.
- **All 20 hand labels and their notes**, using the condition-by-condition tool, and the
  re-check of every label Claude flagged.
- **The label audit:** I checked Claude's three claims against the raw posting text
  and agreed with the proposed readings.
- **Ran everything:** all 42 tests, every live and seeded agent run, all Claude trials,
  the three action-surface runs, and the SHA-256 recomputation. Reviewed every file
  before committing it.
- **Signed** the sign-off, and reviewed and edited the drafted FRICTIONAL reflections
  so they match my own thoughts.
