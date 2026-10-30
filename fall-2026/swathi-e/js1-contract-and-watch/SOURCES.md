# SOURCES — Job-Search Agent 1

Drafted by Claude Code from the committed records and my instructions;
reviewed by Swathi.

## What I used

- **Greenhouse public Job Board API, Databricks board.**
  `https://boards-api.greenhouse.io/v1/boards/databricks/jobs` (list) and
  `.../jobs/<id>` (one posting). Public GET endpoints, no login. Usage notes
  from Greenhouse's Job Board API documentation,
  `https://developers.greenhouse.io/job-board.html`, read 2026-10-25.
  Saved responses: `runs/raw/`, `runs/postings/`.
- **Priya Nair, a fictional persona** from the Reallocation Engine's
  `search/examples/priya-nair/` (`resume.example.json`, last changed in
  commit `d08afdd`, 2026-08-17). The résumé is copied byte for byte to
  `persona/priya-nair.resume.example.json`. `persona/priya-nair.targets.json`
  transcribes `target_role`, `geography` and two `visa` fields unchanged from
  the same persona's `profile.yml`, because the résumé JSON has no
  target-role or location-preference fields. No real résumé is used anywhere.
- **Claude Code** 2.1.308 (desktop app session, and the `claude` CLI from
  Homebrew for `claude -p` judge calls), model `claude-opus-5-5`.
  Setup and permission behavior from Claude Code's documentation,
  `https://code.claude.com/docs/en/setup` (read 2026-10-25) and
  `https://code.claude.com/docs/en/permissions` (read 2026-10-26).
- **Claude chat** (claude.ai), separately from the Claude Code session, and
  once as the chat action surface (Claude Opus 5.5 as shown in the chat,
  2026-10-26 23:07 ET).

## What I wrote myself

- `CONTRACT.md` and its Revisions 1(b) and 2.
- The decisions in `JUDGE-CONTRACT.md`, and its rule 4 revision.
- `LABELING-RULE.md`.
- The inputs and expected verdicts of my 12 hand-fixed test cases.
- The 20 hand labels and reasons in `labels/LABELS.csv`.
- `EXPERIMENT-PLAN.md` (from Claude chat's suggestions, which I reviewed and approved).
- `experiments/action_surface/AUTONOMY-CHOICE.md`.
- `FRICTIONAL.md`.
- The closing paragraph of `SIGNOFF.md` and the sign-off decisions.
- Every decision recorded in the driver's seat table in `SIGNOFF.md`, and the
  prompt choice in `experiments/prompt_choice.json` (recorded in my words).

## What Claude Code wrote

- All code: `watch.py`, `rule.py`, `persona.py`, `judge.py`,
  `experiments/*.py`, `labels/*.py`.
- All tests, including `tests/test_rule_cases.py` (my 12 cases written into
  the test file), `tests/test_agent.py` and `tests/test_judge.py`.
- The prompts: `prompts/judge-baseline.txt` (its four rules copied from my
  judge contract) and `prompts/judge-revision.txt` (the baseline plus the one
  sentence from my experiment plan).
- `persona/priya-nair.targets.json` (the transcription from `profile.yml`).
- The selection of the 20 labeling postings and the development/held-out
  split (`labels/select_postings.py`, `labels/selection.json`), using the
  method and seeds recorded there; the split rule (already-read postings go to
  development) was my choice among options Claude Code offered.
- The reading files in `labels/read/`, `experiments/action_surface/chat_paste.txt`,
  and `experiments/action_surface/comparison.md`.
- The scorer for measures A and B (`experiments/score_experiment.py`).
- This file and the `README.md` draft, including its Known limits entry.
- Review notes on my drafts of `FRICTIONAL.md` and `SIGNOFF.md`: Claude Code
  checked them against the records and suggested corrections. Some of my
  final wording follows its suggestions (for example the two corrected
  `SIGNOFF.md` lines about cases 9-12 and `tests/test_judge.py`).
- All commit messages for code and run records; the commits of my own files
  use my wording.

## What Claude chat helped with (as I report it; not part of the Claude Code session)

- Phrasing my contracts and plans from my decisions (`CONTRACT.md`,
  `JUDGE-CONTRACT.md`, `LABELING-RULE.md`, `EXPERIMENT-PLAN.md`).
- The experiment plan's suggestions: the sampling postings, the one prompt
  change, and measures A and B.
- For most of my 20 labels, Claude chat laid out the facts of each posting against my four checks; I made every label myself.
- For FRICTIONAL.md, Claude chat gave me a list of what happened to write from, and made five factual corrections I approved; the entries are in my words.
- For AUTONOMY-CHOICE.md, Claude chat asked guiding questions; both paragraphs are my words.
- Claude chat drafted the SIGNOFF.md tables and lists from our session records and corrected lines after Claude Code's checks; the closing paragraph is my words.
