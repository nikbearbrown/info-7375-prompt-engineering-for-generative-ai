# Sources

## What I used

| Source | Used for |
|---|---|
| Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/<board>/jobs?content=true` | Boards `stripe`, `cloudflare`, and `striqe` (misspelled on purpose: 404). Responses in `evidence/raw/` |
| Ashby Posting API, `https://api.ashbyhq.com/posting-api/job-board/openai` | Board `openai`, the second applicant-tracking system. Responses in `evidence/raw/` |
| My Job-Search Agent 1, course folder `fall-2026/hsuan-t/js1-contract-and-watch/` | The starting point: contract, Stripe watch, rule judge, Claude judge, persona, tests |
| JSON Resume schema, https://jsonresume.org/schema/ | Format of the fictional résumé (JS1) |
| Fictional persona Aarav Patel, from the course's Reallocation Engine examples | The résumé and profile every run judges against (JS1; `@example.com`) |
| Claude Code CLI (`claude -p`, tested on 2.1.319), model `claude-sonnet-5-5` | The optional Claude judge (`--claude`) |
| Anthropic Python SDK `anthropic` 2.3.0 | Optional `--claude-via api` path |
| pytest 8.4.2 | Tests |
| Python 3.11 standard library | Everything else |

## What I wrote

**Job-Search Agent 2**
- `GATE.md`: exits, budgets and who may change them, the repeat rule, the error policy, the permission policy with the ten boundary rows and their expected outcomes, and the wrong versions. My draft is commit 9722ada; the final, after Claude's review and my choices, is 614afb8, before any JS2 code (see `evidence/git-history.txt`). Later changes to it are dated, each from a decision of mine.
- The decisions in `FRICTIONAL.md` and the README's driver's seat: the failure cases the loop must survive; `finished` only when every board is `ok`; leaving the `meta.total` gap out of GATE so it could be the finished-wrong demo and the review-packet fix; JS2 may change JS1's rules; Claude off by default, and when on, every new posting until 30 calls or 300 s; the rule's misses as a documented known limit; the expected behaviour of the `meta.total` check; accepting the patch.
- The review in `REVIEW_PACKET.md` §4–7: my reading of the diff, the scope call, the commands I ran, the decision.
- The sign-off: what is checked, not checked and claimed, and the signature.

**Job-Search Agent 1** (unchanged): the contract, the labeling rule and the hand labels, the prompt revision choice, the action-surface decision.

## What Claude contributed

Claude (Claude Code, Claude Opus) contributed, at my request and checked by me:

- **GATE:** the skeleton of guiding questions; a review of my draft that found three problems (when `finished` applies, a boundary-test folder, two missing wrong versions); typing the edits I chose.
- **Code:** all of `job_agent/` changes for JS2 (Ashby adapter, board list, permission policy, the loop, error codes, the Claude budget, the `meta.total` check), `checks/total_check.py`, `demo/finished_wrong/run_demo.py`.
- **Tests:** all test code, including `tests/test_meta_total.py`, whose expected outcomes I chose and which I ran red and committed before the patch. Claude also checked the tests by planting bugs.
- **Analysis:** live checks of candidate boards; recounting both real runs from the raw responses and the trace; measuring what a JS1 rule change would do on saved data.
- **Documents:** drafts of `README.md`, `ERROR_CODES.md`, `REVIEW_PACKET.md`, the demo README, dated notes in `CONTRACT.md`, and this file.
