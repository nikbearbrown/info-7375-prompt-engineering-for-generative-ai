# Job-Search Agent 1: The Contract and the Watch

**Student:** Shreyash Yadav (`shreyash-y`) · INFO 7375 Prompt Engineering & Agentic AI, Fall 2026 · Professor Nik Bear Brown
**Assignment:** JS1, Chapters 1–3 · due 2026-10-31

One board (Oscar Health on Greenhouse), one fictional résumé (Alex Morgan), new postings only, and every verdict justified twice: once by a written rule (a **record**) and once by Claude under a prompt contract (a **judgment**).

*This README was drafted by Claude Code on 2026-10-31. The contract, the labeling rule, the labels and the sign-off are Shreyash's; SOURCES.md says who made what.*

## Language and toolchain

- **Python 3**, standard library only, with no packages to install. Tested only on Python 3.14.6 (macOS); the code uses 3.9+ syntax.
- **Tests:** `unittest` (standard library).
- **Claude judge:** the Claude Code CLI (`claude`, tested on 2.1.312), called as `claude -p --model opus --tools "" --no-session-persistence --strict-mcp-config --setting-sources ""` from an empty temporary folder. It runs on a Claude Code login, not an API key. Everything except the `--claude-prompt` option and the `experiments/run_claude.py` and `experiments/action_surface.py` scripts runs without it.
- **Network:** only `https://boards-api.greenhouse.io`, and only in a live `run`.

## Commands, from a fresh clone

```bash
git clone -b shreyash-y/js1-contract-and-watch https://github.com/shreyashyadav1/info-7375-prompt-engineering-for-generative-ai.git
```

```bash
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/shreyash-y/js1-contract-and-watch
```

Tests, offline (65 tests):

```bash
python3 -m unittest discover -s tests -t . -v
```

Check that the résumé is a valid fictional persona:

```bash
python3 -m jsagent check-persona persona/alex_morgan.json
```

**Seeded** replay of the two saved live responses, offline. The first call is the baseline (0 new); the second reports the 12 new postings of live run 2:

```bash
python3 -m jsagent run --board oscar --runs-dir /tmp/js1-replay --from-raw runs/raw/oscar-20261029T031015Z.json --seeded-label "replay of run 1"
```

```bash
python3 -m jsagent run --board oscar --runs-dir /tmp/js1-replay --from-raw runs/raw/oscar-20261030T230217Z.json --seeded-label "replay of run 2"
```

A live run into fresh state (the first run against a new `--runs-dir` is always a baseline):

```bash
python3 -m jsagent run --board oscar --runs-dir /tmp/js1-live
```

A live run with the Claude judge as well. This needs a logged-in `claude` CLI and costs about $0.03 per new posting:

```bash
python3 -m jsagent run --board oscar --runs-dir /tmp/js1-live --claude-prompt prompts/baseline-v1.md
```

Re-score the prompt experiment from the saved calls, offline:

```bash
PYTHONPATH=. python3 experiments/score.py --set held_out --summary experiments/prompt-experiment/heldout-baseline/hobase-summary.jsonl experiments/prompt-experiment/heldout-revision1/horev-summary.jsonl
```

## What ran

All runs below happened as described. Times are Eastern.

| When | What | Result | Evidence |
|---|---|---|---|
| 2026-10-28 23:07 | Tests run before any implementation existed | all 5 test modules fail to import | `evidence/tests-before-implementation-2026-10-28.txt` |
| 2026-10-28 23:10 | **Run 1, live baseline** | 220 fetched, 0 reported new (baseline) | `runs/raw/oscar-20261029T031015Z.json`, `runs/report-oscar-20261029T031015Z.*`, `evidence/run1-terminal-2026-10-28.txt` |
| 2026-10-30 19:02 | **Run 2, live, second calendar day, both judges** | 214 fetched, **12 new**, 18 gone; rule and Claude both Not Relevant on all 12, with the same failed conditions on 11 | `runs/raw/oscar-20261030T230217Z.json`, `runs/report-oscar-20261030T230217Z.*`, `runs/state.json`, `runs/claude-calls/` |
| 2026-10-30 | Independent recount of run 2 from the two raw files | matches the agent's new and gone lists | `evidence/run2-recount-2026-10-30.txt` |
| 2026-10-31 | Sampling: 5 postings × 4 fresh Claude calls | 20/20 identical verdicts and failed conditions | [experiments/SAMPLING-REPORT.md](experiments/SAMPLING-REPORT.md) |
| 2026-10-31 | Prompt experiment: baseline vs one change, 10 development then 10 held-out | 10/10 on the hand labels everywhere; the revision's quotes are word for word 112/112 | [experiments/PROMPT-EXPERIMENT.md](experiments/PROMPT-EXPERIMENT.md) |
| 2026-10-31 | Action surface: chat paste, file read, agent with tools | way C needed curl to any host before it could work, wrote outside its folder, and misreported a count | [experiments/ACTION-SURFACE.md](experiments/ACTION-SURFACE.md) |
| 2026-10-31 | Seeded replay of runs 1 and 2 (`runs-replay/`) | identical to live run 2 (ids, verdicts, failed conditions, justification text) | `evidence/replay-terminal-2026-10-31.txt` |

Wrong version 1 appeared in live data. Run 2's new postings include "Senior Product Manager, Marketplace" three times (Boston, LA and SF, three ids) and "Strategic Insights Associate, Data Analytics" four times. All seven were reported and judged separately.

Claude use, all `claude-opus-5-5`: 73 judge calls ($2.29, including one smoke test on a constructed posting) and 4 action-surface sessions ($0.41).

## How it works

- **[CONTRACT.md](CONTRACT.md):** Shreyash's contract (In, Out, Refuses, the rule, two wrong versions, the dated failure sentence), committed first and alone (`7c8f9e5`).
- **[INTERPRETATIONS.md](INTERPRETATIONS.md):** how each phrase of the rule was made computable, and the rule defects found later. Committed with the tests, before the code (`1ab74ec`).
- **`jsagent/`:**
  - `fetch.py`: HTTPS GET to the allow-listed host only. Every redirect is checked against the list.
  - `watch.py`: saves the raw bytes first, keeps seen ids per board, makes the first run a baseline, and reports only ids never seen before.
  - `posting.py`, `rule.py`: the six conditions. Each verdict carries one line per condition naming the `resume.` and `posting.` fields it read.
  - `persona.py`: refuses a résumé that is not marked fictional or has a non-`example.com` email or a non-555 phone.
  - `claude_judge.py` and `validator.py`: the Claude step and its fixed JSON format. Anything else is rejected, never repaired.
- **`tests/`:** `wrong_versions.py` implements both wrong versions from the contract, plus a shifted-labels version, and `test_wrong_versions.py` shows the checks fail on them. `test_rule.py` has one test per interpretation, `test_fetch.py` covers the allow-list, `test_persona.py` checks the persona and scans this folder for real contact details, and `test_validator.py` covers the output format. Every posting in `tests/` is constructed and labeled as such.
- **The two judges in the output.** Every report line says `rule (record)` or `Claude (judgment)`. The Markdown reports call the Claude verdict "a model's judgment, not a fact".

## Known defects (found, not fixed)

The rule's record disagreed with Claude on condition 3 or 5 five times across run 2 and the experiment. Each time, the ad's own words, checked in the saved raw response, sided with Claude:

- **Condition 5 (experience) undercounts** when the word "experience" is missing or more than 60 characters after the number (8083703, 8319419).
- **Condition 3 (location) trusts an office tag.** A "Remote" tag wins over an ad that says hybrid (6555819, 8250366), and remote limited to states that exclude Massachusetts still passes (8172223).

None of the five changed a verdict, because every one of those postings fails other conditions. They were left unfixed in this layer so that the record of what ran stays what ran. Fixing them is the first item for the next layer.

## Sign-off — Job-Search Agent 1

```text
Checked:      - New-since-last by id, baseline first, and no title dedup: tests/test_wrong_versions.py
                (wrong versions 1-3 implemented and caught), plus a recount of live run 2 from the
                two raw files by a script that does not import the agent
                (evidence/run2-recount-2026-10-30.txt).
              - Justifications cite real resume and posting fields: test_wrong_versions.py
                WrongVersion2GenericJustification; Claude's format: tests/test_validator.py, and
                112/112 revision quotes found word for word in the saved postings.
              - Allow-list and redirects: tests/test_fetch.py; persona and no real contacts in the
                folder: tests/test_persona.py.
              - The 20 hand labels: Shreyash labeled all 20 Not Relevant "using the rule above and
                the 20 Oscar job descriptions" (labels/LABELING-RULE.md, labels/hand-labels.csv).
How:          Tests were written by Claude Code from CONTRACT.md and committed before the
              implementation (1ab74ec before 6d74630); they were not written by Shreyash. The run 2
              recount and the seeded replay are recomputations. The labels are by hand (Shreyash).
              Reading the ads where the two judges disagreed was done by Claude Code, which also
              checked the quotes against the raw files; Shreyash has not re-read those five ads.
Not checked:  - No real posting passed all six conditions, so the Relevant path has only been
                exercised on constructed postings in tests, never on a real one.
              - The three rule defects above are known and unfixed, and the two interpretation
                choices (experience = largest N; state-limited remote passes) were never confirmed
                by Shreyash.
              - Redirect refusal was tested against a constructed redirect only; no live redirect
                was seen.
              - The Claude judge's resistance to instructions hidden in a posting was not tested.
              - The React/RAG whole-word false positive was not measured on real postings.
              - Only Python 3.14.6 and one model on one day were tried.
Not claiming: That this agent finds good jobs, that Claude's verdicts are accurate (only that they
              were repeatable and matched 20 all-negative labels), that the rule's record is ground
              truth (it is wrong in five places), or that it works on any board but Oscar's.
Signed or withheld: ____________ (name, date)
```

## Driver's seat

| Part of the task | Claude should | Shreyash should | Why that part stays Shreyash's | Where the split shows |
|---|---|---|---|---|
| The contract | turn the words into code and point out ambiguous phrases | decide what counts as relevant, and write it first | it is the decision about which jobs are worth a day; a model can state a rule but has no stake in it | `7c8f9e5` contains only CONTRACT.md. The session record shows Shreyash choosing "Interview me" on 2026-10-28 and pasting the contract text. The ambiguities went to INTERPRETATIONS.md (`1ab74ec`), not into the contract. |
| Ground truth | build a label sheet that shows no verdicts | label the postings with a rule written first | labels made by the system being tested would only measure it against itself | `20041e3` (sheet, no verdicts) before `b3faea5` (Shreyash's rule and labels), before any Claude call on those postings |
| Code, tests, prompts, runs | write them, run them, save everything | choose the board, the persona and the model, and say when to run | the run order and scope are Shreyash's calls; the code can be checked by the tests | Shreyash picked Oscar, Opus and the persona (2026-10-28) and asked for run 2 on 2026-10-30 ("lets do run 2"); commits `6d74630` to `a021d9c` |
| Who was right when the judges disagreed | find the disagreements, quote the ad, check the quote is real | read the ad and decide | a verdict about a job is the one thing the assignment says Claude cannot own | **Not fully done.** Claude did the reading. Shreyash has not re-read the five ads (Not checked). |
| The one prompt change | propose options from the development results | pick one | — | **Not done as intended.** Claude picked revision-1 (PROMPT-EXPERIMENT.md says so). |
| The sign-off | draft the lines | check them, decide what is not checked, sign or withhold | only the person who signs knows what they did not test | the signature line above |
