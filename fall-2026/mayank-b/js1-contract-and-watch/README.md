# Job-Search Agent 1: The Contract and the Watch

Mayank Bhadrasen · INFO 7375 · Fall 2026

One board (Anthropic on Greenhouse), one fictional persona résumé (Priya Nair), new postings only, and two labeled verdicts per new posting: a **record** from my written rule, which anyone can recompute, and a **judgment** from Claude under a fixed output format and a validator. The contract came first: [CONTRACT.md](CONTRACT.md), commit `e936060`, before any code existed.

## Toolchain

| | |
|---|---|
| Language | JavaScript (ES modules) on Node.js 22 or later; built and tested on Node 24.8.0, npm 11.6.0, macOS |
| Dependency | `@anthropic-ai/sdk` 1.3.0 (the only one) |
| Tests | Node's built-in test runner (`node:test`), no test framework |
| Claude model | `claude-haiku-5-5`, effort `low`, one fresh API call per verdict |
| Board | `GET https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` (public, no login) |

## Setup and commands (from a fresh clone)

```bash
cd fall-2026/mayank-b/js1-contract-and-watch
npm install
cp .env.example .env            # then put your own ANTHROPIC_API_KEY in .env (git-ignored)

npm test                        # 21 tests; no network, no API key needed
node scripts/wrong-versions.js  # plants W1, W2, W5 into a temp copy and shows the tests catch each one
npm run check-persona           # validates the persona résumé
npm run watch                   # one run of the watch: live fetch, raw response saved, new postings judged
node src/cli.js rule <posting_id> --raw runs/<run>/raw-response.json   # recompute one rule verdict
```

The baseline run needs no API key (it reports nothing as new, so nothing is judged). Without a key, later runs still give the rule's verdict and record Claude's as `no_verdict`.

Seeded run, only if a live second run shows no change: `npm run watch -- --seeded-from runs/<earlier-run>/raw-response.json`. Its folder and report are labeled `seeded`.

Step 4 scripts (each Claude call is fresh; they read saved raw responses and never fetch the board):

```bash
npm run sample -- --raw runs/<run>/raw-response.json --ids <5 ids, comma-separated> --n 4
npm run experiment -- --prompt prompts/judge-v1.md --set dev
npm run experiment -- --prompt prompts/judge-v2.md --set heldout --final   # only at the very end
```

## Layout

| Path | What it is |
|---|---|
| `CONTRACT.md` | In, Out, Refuses, the rule, wrong versions, the dated failure sentence |
| `notes/contract-questions-with-my-answers.md` | Claude's guided questions with my original answers (evidence for how the contract was written) |
| `persona/priya-nair.resume.json` | fictional persona with my `search` block (the rule's control panel) |
| `src/allowlist.js` | every request passes the host allow-list check first |
| `src/persona.js` | persona validator (`@example.com`, `555`), runs before any fetch |
| `src/rule.js` | the rule (record) |
| `src/claude.js`, `prompts/judge-v1.md` | the Claude judge (judgment), its prompt contract and validator |
| `src/watch.js`, `src/cli.js` | the watch: fetch, save raw, new-by-id, dedupe, state |
| `tests/` | the tests, including W1, W2, W5 and the failure sentence; `tests/fixtures/` holds constructed (not real) postings |
| `scripts/wrong-versions.js` | proves each wrong version is caught |
| `scripts/sample.js`, `scripts/experiment.js` | sampling report and prompt experiment |
| `state/seen-ids.json` | every posting id seen so far |
| `runs/run-NN-YYYY-MM-DD/` | `raw-response.json` (exactly as received) and `report.json` for each run |
| `labels/` | my hand labels (`labels.example.json` is the template) |
| `reports/` | sampling and experiment results |

## What ran

Past tense only for what ran and can be shown.

- 2026-10-28, during the build (run by Claude Code): `npm test` passed 21 of 21; `node scripts/wrong-versions.js` caught W1, W2 and W5; one live Claude call on posting 5448481008 ("Data Engineer, Product") returned a reply the validator accepted (verdict `relevant`, 2.5 s). That call was a development check and is not part of any report.
- I re-ran the tests myself (2026-10-30): `npm test` passed 21 of 21, 0 failed.
- Run 1 (baseline), 2026-10-29 01:40 Boston time: fetched 680 postings, 0 duplicate ids, 0 reported new (baseline), every id saved to `state/seen-ids.json` (`runs/run-01-2026-10-29/`).
- Run 2 (second calendar day, live, not seeded), 2026-10-30 05:18 Boston time: fetched 670 postings, 0 duplicate ids, 12 new. None of the 12 ids is in run 1's raw response, and 22 postings from run 1 were gone. Rule and Claude agreed on all 12 (all `not_relevant`); state now holds 692 ids (`runs/run-02-2026-10-30/`).

## Sampling report (Chapter 1)

Judge v1, 4 fresh Claude calls per posting on 5 dev postings (`reports/sampling-judge-v1-2026-10-29.json`):

| Posting | Verdicts over 4 calls |
|---|---|
| Data Engineer, Product | 4 of 4 relevant |
| Data Scientist, Product | 2 relevant, 2 not relevant |
| Applied AI Architect, International Policy | 4 of 4 relevant |
| Applied AI Demo Engineer | 4 of 4 relevant |
| Anthropic Fellows Program | 4 of 4 relevant |

Data Scientist, Product split 2-2, so a single call on it is a coin flip.

## Prompt experiment (Chapter 2)

Labels: `labels/labels.json` (my labels, labeling rule Option A, role first; 12 dev, 8 held-out). One change from v1 to v2: judge the role, not the keyword match (`prompts/CHANGES.md`, commit `927e44b`). My reason: I believe the role matters more and skills can be learned.

| Prompt | Dev (12) | Held-out (8), run once with `--final` |
|---|---|---|
| v1 | 5 / 12 | 6 / 8 |
| v2 | 8 / 12 | 6 / 8 |

- Dev, gained under v2: Data Scientist, Product; Applied AI Architect; Software Engineer, Beneficial Deployments. Still wrong under both: Applied AI Engineer (Enterprise), Applied AI Demo Engineer, Applied AI Engineer (Startups), Software Engineer, Education.
- Held-out: both prompts gave the same verdict on every posting; both called Cyber Evaluations Engineer and Research Engineer, Machine Learning (Reinforcement Learning) relevant where my label is not relevant. Held-out has one relevant posting (Security Data Engineer); both got it right.
- Size: with 12 and 8 postings, one posting moves the score by 8 to 12 points.

Reports: `reports/experiment-judge-v{1,2}-{dev,heldout}-2026-10-29.json`.

## Action-surface comparison (Chapter 3)

My answers, typed in chat on 2026-10-29 and copied verbatim (`notes/my-answers-2026-10-29.md`).

#### Surface 1, chat paste (claude.ai), posting "Data Engineer, Product"
- What Claude answered: Not relevant. It's a data engineering role, not the AI/ML engineer role Priya is targeting, even though the SF/NYC locations and her SQL/Databricks skills fit.
- How it compared: Faster, I didnt have to type her details

#### Surface 2, file read (Claude Code in this folder), posting 5448481008
- What it answered (pasted from the session):

> Relevant. It's a Data Engineer, Product role at Anthropic, and Priya's day-to-day stack is the data side of that job: SQL, Python, Databricks, Delta Lake and Unity Catalog. "Data Engineer" is one of her target titles, and the posting is in SF / NYC / Seattle, on-site. She's open to relocating to SF and NYC.
>
> The raw response only has metadata for this posting. There's no content field anywhere in the file, so I couldn't see the job description, the seniority level or the years of experience they want. The title has none of her excluded words (Senior, Staff and so on), but Anthropic's data roles often ask for more than her 8-month co-op. If you're labelling this as the ground truth for the held-out run, mark it "relevant, seniority unverified." It's also missing from report.json, because run 1 was the baseline with 0 new postings.
>
> Separately, today's JSA1 held-out run and the action-surface comparison are due today, and the submission deadline is Sat 11:30am.

- What it opened: it opened these three files:
  - Bash List persona files and extract posting 5448481008
  - Bash Read Priya's résumé
  - Bash Check report entry and whether descriptions exist
- How it compared: i can trust this as this way it checked the details/files that were mentioned to give a calculated answer, chat paste just gave an answer acc to the instructions in the prompt and checked no files for evidence

#### The three ways side by side (table drafted by Claude Code on 2026-10-31 from what each setup ran with; my verdicts and my choice are above)

| | Chat paste (claude.ai) | File read (Claude Code in this folder) | Agent (`npm run watch` / `npm run sample`) |
|---|---|---|---|
| Verdict on Data Engineer, Product | not relevant | relevant | relevant, 4 of 4 calls (`reports/sampling-judge-v1-2026-10-29.json`) |
| Can read | only what I paste | any file in the folder it is allowed to open, including `.env` | the board (allow-listed host only), the persona's listed fields, `state/` |
| Can write | nothing | files in the folder, if I approve | only `state/` and `runs/` (other writes refused, tested) |
| Can send | nothing | nothing beyond the Claude session | one GET to the allow-listed host; one Claude API call per verdict |
| Authority needed | none | folder access granted at launch | an API key in `.env` and network access |
| What could go wrong | it judges without the résumé, from my summary | reads secrets in the folder; a confident wrong answer | wrong or partial board data saved as state; a confident wrong verdict recorded |

#### Choice and defense (first answer)
- Which way for the judging step, and why: letting the agent read the file, this way the probability of getting a right answer is more
- Worst realistic failure: even if the probability of a right answer is high, worst thing would be even after an agent reads the files and still gives a wrong answer as AI can be wrong

#### Choice and defense (revised answer, replaces the first)
- Which way, and why: i meant the file read (Claude Code reading the saved file), it has access to those files
- Worst realistic failure: File read: it can open anything in the folder, including .env (your API key).
- How I'd limit it: When we launch Claude Code, we have that permission to give access to a certain folder. So we can give the access to that folder where no confidential data or ENV is present.

## Sign-off: Job-Search Agent 1

- Checked: `npm test` (21 tests in `tests/`, including W1, W2, W5 and the failure sentence), re-run by me on 2026-10-30, 21 of 21 passed; run 2 reported 12 new ids, none of them in run 1's raw response.
- How: by hand (3 rule verdicts recomputed) / by running the tests / with Claude's help: Claude Code wrote the code and the tests against my CONTRACT.md (SOURCES.md).
- Not checked (my 3 picks):
  - The validator checks that Claude names the right fields, not that what it quotes from them is true.
  - No check that the board API returns every posting the website shows.
  - A job reposted under a new id gets reported as new.
- Not claiming: Im not claiming that the Claude's verdicts are correct.
- Checked by hand: I recomputed 3 rule verdicts by hand from the rule's text (1 of 3 matched at first; the other 2 were my own judgment, not the rule's) and reviewed all 12 dev rule verdicts against their titles.
  - My hand answers (2026-10-29): A Data Scientist, Product: relevant; B Applied AI Architect, International Policy: relevant; C Anthropic Fellows Program, ML Systems & RL: relevant. Rule (reports/sampling-judge-v1-2026-10-29.json): A not_relevant, B relevant, C not_relevant.

- Signed or withheld: ____________ (name, date)

## Driver's seat

- "I did" column: no correction to Claude's summary (Contract: answered the questions, my answers became CONTRACT.md; Code: ran npm test and the watch; Labels: labelled 20 postings, chose the dev/held-out split, flipped the 5; Prompt: chose v2; Not checked: picked 3, recomputed 3 rule verdicts by hand).
- Why it stays mine:
  - contract: I went through all questions and answered them to the best of my knowledge
  - code: observing the tests and giving claude the response was critical for further development
  - labels: i labelled the jobs with option A (reason listed below)
  - prompt change: I believe the role matters more and skills can be learned
  - not checked: due to the time constraint i picked 3
- Labeling rule: I chose Option A (Role first) as its the deciding factor of a person's work, what they want to be or work as in a company, skills vary from company to company and they can be learned, but the role stays with you until you get promoted or switch jobs
