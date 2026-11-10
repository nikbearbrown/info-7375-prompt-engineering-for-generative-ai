# SOURCES — what was used, what Aditya did, what Claude contributed

## External sources and data

| Source | Used for | How (dates are 2026-11-10 unless noted) |
|---|---|---|
| Assignment PDF *Job-Search Agent 2 — The Loop, the Tools, and the Diff* (Canvas) | The specification, the rubric and the `fall-2026/...` path | Read in full |
| [`ai-policy.md`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/ai-policy.md), [`frictional.md`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/frictional.md), [`github-submission.md`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/github-submission.md), [`relative-quartile.md`](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/relative-quartile.md) | Course policy | Read by Claude. `github-submission.md` still says `fall-2025/`; the JS2 PDF path was used instead. Claude did not watch the policy video; Aditya reports he watched it. |
| Aditya's **JS1** submission (local commit `819f2e9`; posted `693b7d3`) | Starting point (see `BASELINE.md`) | Imported unchanged; its inherited checks were re-run |
| [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html) | `GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`, public, no auth | Official doc read; boards `databricks` and `figma` |
| [Ashby public job posting API](https://developers.ashbyhq.com/docs/public-job-posting-api) | `GET https://api.ashbyhq.com/posting-api/job-board/{name}` | Official doc read. The doc **lists no `id` field**; the `id` field the agent relies on was observed in live responses (pre-gate recon) |
| [Lever postings API](https://github.com/lever/postings-api) | Considered and not used | Doc read only |
| The Reallocation Engine (local checkout) | A cross-check that these endpoint formats are the course's | URL patterns grepped only; no code used |
| Python 3.12.8 standard library; pytest 8.3.3; Claude Code CLI 2.1.310 (`claude-opus-5-5`, effort medium) | Implementation, tests and the JUDGMENT calls | — |

## Contributions

| Part | Aditya | Claude (Claude Code, Opus 5.5) |
|---|---|---|
| `GATE.md` and `GATE_ADDENDUM_1.md` | **Wrote both** (all decisions on exits, budgets, repeat rule, errors, permissions, wrong versions, the failure prediction and the six clarifications) | Prepared a decision worksheet with suggested options; checked the gate for contradictions; raised the six questions; saved the addendum verbatim |
| Board choice and limits | Chose them (4 boards, 8 attempts, 180 s, 10 model calls, 20 s timeouts, 10 s reserve) | Suggested them, with timings from recon and JS1 |
| JS1 baseline import, probes, provenance | Chose the guided P2 route | Imported the baseline and recorded hashes; wrote the six probes; flagged P2 (sealed observation, 2026-11-10) |
| **Review packet** | **Ran P2; wrote `INVESTIGATION.md`, `tests/test_aditya_total_mismatch.py` and `CHANGE_REQUEST.md`; captured the pre-patch failure; ran the post-patch and final checks; decided REVISE (non-object `meta`) and then ACCEPT; wrote the scope assessment and the missed case** | Wrote the patch (`0007bbd`), the focused tests, the revision tests (committed failing) and the revision (`d58682c`); reran checks; drafted the factual sections of `REVIEW.md` |
| Loop, policy, adapters, HTTP client, export path | Specified the behavior (gate and addendum) | Wrote all of it |
| Tests, mutants, checker, finished-wrong demo | Specified the wrong versions W1–W12 | Wrote them; drafted the boundary predictions from the gate before the code existed; found and fixed 3 mutation gaps |
| LIVE run | — | Ran it (18:21 EST) on Aditya's Claude Code login |
| README, SOURCES, `[process log]` entries in FRICTIONAL | Reviews them | Drafted them from the record |
| FRICTIONAL `[Aditya]` entries, sign-off, "why it stays mine", export approval | **His alone** | Nothing (left blank) |
