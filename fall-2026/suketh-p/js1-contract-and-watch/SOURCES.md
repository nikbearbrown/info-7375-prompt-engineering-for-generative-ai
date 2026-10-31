# SOURCES — what I used, what I wrote, what Claude contributed

## What I used

- **The assignment brief:** `assignments/assignment-js1-the-contract-and-the-watch.md` in the course repo, the same as the Canvas text.
- **The board:** the Greenhouse Job Board API, public endpoint `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` (no login). Two live GETs: 2026-10-28 and 2026-10-31.
- **Claude Code 2.1.291** (`claude -p`) with my NEU Claude Code login, as the agent's judge and for the sampling and experiment calls. Model `claude-opus-5-5`.
- **claude.ai** (Opus 5.5, effort Max, as the chat showed) for action surface 1.
- **Python 3.12.7 standard library only.** No third-party packages or code.
- **The Anthropic API reference** for the optional `api` route: the request shape, `anthropic-version: 2026-10-21`, and server-side fallbacks. Claude Code read it from its built-in API reference. That route never made a real call.
- **Other students' JS1 folders were not used.** They are on the course repo's `main`; Claude Code deliberately did not open them.

## What I wrote myself

| What | Where | Evidence |
|---|---|---|
| The contract: purpose, in, out, refusals, the rule, the wrong versions, and the dated failure sentence. **I wrote it myself.** | [CONTRACT.md](CONTRACT.md) | `29b3a26`, committed before any code. A word-for-word check of my pasted text against the Markdown: 1,634/1,634 tokens identical |
| The Oct 31 amendment (a new dated failure sentence) | [CONTRACT.md](CONTRACT.md), "Amendment" | `7752e69` |
| The persona Alex Morgan (fictional: @example.com, 555 number) | inside CONTRACT.md; copied to `persona/alex_morgan.json` | `29b3a26`, `d945f28` |
| The labeling rule | [labels/LABELING-RULE.md](labels/LABELING-RULE.md) | `7752e69` |
| All 20 hand labels and my reasons | [labels/hand-labels-as-sent.txt](labels/hand-labels-as-sent.txt), [hand_labels.csv](labels/hand_labels.csv) | `0f312fb`, before any sampling or experiment call |
| The choice of judge route (my Claude Code login) | README, FRICTIONAL | chat, 2026-10-30 |
| The surface-1 chat: I pasted the text and copied back the reply | [action-surface/1-chat/](action-surface/1-chat/README.md) | `0f3b4af` |
| My Frictional entries | [FRICTIONAL.md](FRICTIONAL.md) | dated |
| The one change for prompt v2 (A: the justification names the exact résumé and posting fields), and why | [reports/PROMPT-EXPERIMENT.md](reports/PROMPT-EXPERIMENT.md), FRICTIONAL | `b0d2a88` |
| The least-autonomy choice and defense | PENDING | PENDING |
| The sign-off | README | PENDING |

## What Claude (Claude Code, Opus 5.5) contributed

- **Formatting:** converted my pasted contract to Markdown (headings, lists, two tables, code fences) without changing words.
- **All code and tests:** `jobwatch/`, `tests/` (including the wrong versions as code), `experiments/`, and the action-surface script. Tests were written first from my contract and committed failing (`d945f28`) before the implementation (`546fd7a`).
- **Prompt text:** `prompts/judge_v1.md`, drafted from my contract's rule and output contract. `prompts/judge_v2.md` is v1 plus one inserted paragraph that implements the change I chose; Claude Code proposed options A and B after measuring v1.
- **Design calls where my contract was silent:** listed in the README section "Calls Claude Code made where the contract was silent". This includes the stricter persona checks, the quote-matching rule, no retries, `.gz` storage, and the sample selection (stratified, seed 20261028).
- **Running things:** run 1, run 2, the seeded demo, surface 2, sampling, and the experiment.
- **Drafts:** README, the reports, and the factual timeline in FRICTIONAL.md. My own entries there are mine.
- **Claude's verdicts in this repo are model output.** Each is labeled a model judgment and saved verbatim with its date.
