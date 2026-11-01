# SOURCES — what was used, what Aditya wrote, what Claude contributed

## External sources and data

| Source | What we used it for | How it was used |
|---|---|---|
| Assignment PDF, *Job-Search Agent 1 — The Contract and the Watch* (INFO 7375, Canvas) | The specification | Read in full |
| [`ai-policy.md`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/ai-policy.md), [`frictional.md`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/frictional.md), [`github-submission.md`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/github-submission.md), [`relative-quartile.md`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/relative-quartile.md) | Course policies | Read on 2026-10-30. The AI-policy **video** was not watched by Claude. Aditya reports he watched it. |
| [The Reallocation Engine](https://github.com/nikbearbrown/the-reallocation-engine), `search/examples/priya-nair/resume.example.json` at commit `d08afddc` | The fictional persona résumé (Priya Nair: `@example.com` email, 555 phone) | Copied **unchanged** to `resume/priya-nair.resume.example.json` (SHA-256 `a4fdbc96…c1`) |
| Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true` | Live board data (a public, unauthenticated endpoint) | Snapshot taken 2026-10-30T20:39:00Z, plus live run 2 |
| Internet Archive capture `web.archive.org/web/20260922181913id_/https://boards-api.greenhouse.io/v1/boards/databricks/jobs` | Genuine earlier response used for the **seeded** baseline | Downloaded by hand once, bytes kept as served. The agent never fetches from the archive. |
| Claude Code CLI 2.1.310 (`claude -p`), model `claude-opus-5-5`, effort `medium` | Every model judgment, experiment and action-surface run | Fresh isolated session per call; temperature not controllable |
| Python 3.12.8 standard library; pytest 8.3.3 | Implementation and tests | — |

## Contributions

| Part | Aditya | Claude (Claude Code, Opus 5.5) |
|---|---|---|
| **CONTRACT.md** | Wrote the text; made decisions R1–R5 and the experiment design | Saved it verbatim. Before approval it found the conflicts: 5/903 relevant, "databricks" in every description, no Spark on the résumé. It proposed options, and Aditya chose and modified them. |
| Rule, validator, watch, state, judge code | Specified the behaviour in the contract | Wrote all the code |
| Tests and faulty variants | Named the two wrong versions and what must be caught (§5) | Wrote the tests, the faulty variants and the mutation check |
| Prompt contract v1 (`prompts/judge_v1.md`) | The rule it encodes | Wrote the prompt text and output schema |
| Prompt revision v2 | Accepted Claude's stated rationale (2026-10-30). He did not independently find the issue or review the diff. | Identified the unsupported-evidence failure in watch run 2, then proposed, wrote and ran the one change |
| Sample selection procedure | Chose the grouped design, targets, duplicate handling and sealing | Wrote the procedure and script, and fixed seed 7375 |
| **Hand labels** (20 postings) | **All labels and notes** (received 2026-10-31 14:33 EDT; commit `83c0b7e`, byte-for-byte) | Generated blank sheets without groups or verdicts. Later repaired CSV quoting only (`4d6322a`, no label changed). |
| Mode 1 chat demonstration | Performed it in claude.ai (2026-10-31); saved the reply unchanged; wrote the observations in `mode1_chat_notes.txt` | Prepared the paste file; re-validated the saved reply; added the result to ACTION_SURFACE.md |
| Modes 2 and 3 | — | Ran them and recorded the results |
| Reports (sampling, prompt experiment, action surface), README | Reviews them and verifies them with the checklist | Drafted from the saved results |
| FRICTIONAL.md | The `[Aditya]` entries | The `[process log]` entries |
| Sign-off | Signs or withholds | Drafted the wording only |
