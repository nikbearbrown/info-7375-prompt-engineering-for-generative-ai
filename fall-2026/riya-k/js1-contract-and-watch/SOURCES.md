# SOURCES

## What I used

| Source | Used for | Date |
|---|---|---|
| Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true` (public, no login) | The board: 2 live fetches by `jsagent/watch.py` | 2026-10-31 23:32 and 2026-11-01 00:05 UTC |
| Classmate **yash-s**'s saved raw Databricks response, `fall-2026/yash-s/js1-contract-and-watch/runs/raw-databricks-2026-10-29T005656Z.json` in the course repo | The "earlier response" for the **seeded** two-day run, copied unchanged to `snapshots/databricks-2026-10-29T005656Z-from-yash-s.json` | captured 2026-10-29 00:56 UTC by yash-s |
| The Reallocation Engine, `search/examples/priya-nair/resume.example.json` (fictional example persona) | The persona résumé. I renamed it to **Arya Sahni** and changed the email, LinkedIn and GitHub handles; the skills, experience and education are unchanged | read 2026-10-31 |
| Professor Bear's `fall-2026/nik-bear-brown/greenhouse-watch-demo/README.md` | Read for the expected shape of a watch demo (baseline then second run, raw saved). No code copied | 2026-10-31 |
| Course `prerequisites/frictional.md` | FRICTIONAL.md format | 2026-10-31 |
| Python 3.13 standard library; `certifi` (only its CA bundle path, for the macOS SSL fix) | Everything in `jsagent/`, `tests/`, `experiments/` | |

## What I did (Riya)

- **Contract decisions:** the persona and board choice, title words (I added ML after Claude pointed out Arya's ML-infra target),
  the 2-skill minimum, not counting Databricks, Ray or Kubeflow, the seniority words, US-or-Remote, the refusals, which wrong versions to test,
  the labeling rule and the failure sentence. I gave these as answers in the Claude Code chat on 2026-10-31. All rules and decisions are
  mine; Claude formatted them into CONTRACT.md.
- **Amendment 1** (don't count Unity Catalog): my decision, after Claude showed it appears in 901 of 901 postings.
- **All 20 hand labels**, including the blanket "non-US = not relevant" rule, chosen from options showing each posting's facts.
- **The one change for prompt v2** (add my labeling criteria).
- **Keeping my #4 label** after learning Claude was right.
- **The persona name** (Arya Sahni).
- **The FRICTIONAL entries:** I chose which real events to record, from options Claude listed, and Claude wrote them up.
- **The hand check** of posting 6866538002 (`labels/handcheck/`), and my verdict on it.
- **The "[Riya, own words]" paragraph** in FRICTIONAL.md (Claude suggested spelling fixes and one phrase change, which I accepted).
- **Keeping v1** after the prompt experiment.
- **The sign-off** and its signature.

## What Claude contributed

Claude Code (Claude Opus 5.5) in one session on 2026-10-31:

- **All code:** `jsagent/` (watcher, rule implementation, Claude judge, validators), `tests/test_agent.py`, `experiments/*.py`, `tools/check_wrong_versions.py`.
- **Running everything:** the live and seeded watches, tests, sampling, prompt experiment, and action-surface runs.
- **Prompt drafts** `v1_baseline.md` and `v2_criteria.md`. v2's added paragraph is my labeling rule.
- **Drafts of README.md, SAMPLING.md, PROMPT_EXPERIMENT.md, ACTION_SURFACE.md, this file and FRICTIONAL.md**, written from
  the saved results and my answers.
- **Finding problems I then decided on:** the "Databricks" and "Unity Catalog" free matches, the missing ML title words, the macOS
  certificate error, the evidence-overwrite bug (found by a test), the first labeling draw being almost all senior or non-US postings, and the
  graduation-date reason that made my #4 label wrong.

The Claude **judge** in the agent and experiments is a separate model, `claude-sonnet-5-5`, called through `claude -p`.
Its outputs are judgments and are labeled that way everywhere.
