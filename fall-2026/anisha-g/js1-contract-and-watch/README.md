# Job-Search Agent 1 — The Contract and the Watch

**Anisha Gaikar · INFO7375 · Language: Python 3.10+ (standard library only) · Toolchain: python3, Claude Code CLI (`claude -p`), git**

Watches one public Greenhouse board (Klaviyo), reports only postings new since the last run, and judges each one twice: by my written rule (a RECORD) and by Claude under a prompt contract (a JUDGMENT). Contract: [CONTRACT.md](CONTRACT.md).

## Commands (from a fresh clone, inside this folder)
```bash
python3 -m unittest discover -s tests -v                 # tests written from the contract
python3 agent.py run --board klaviyo                     # run 1: baseline (reports none as new)
python3 agent.py run --board klaviyo                     # run 2: later / next day: reports new postings only
# if the board has not changed, a SEEDED second run (clearly labelled):
python3 agent.py seed runs/<run1>-raw.json --drop 3 --out runs/seeded-earlier.json
cp state/seen.json /tmp/seen-live.json && rm state/seen.json && python3 agent.py run --from-file runs/seeded-earlier.json && python3 agent.py run --from-file runs/<run1>-raw.json && mv state/seen.json state/seen-seeded.json && cp /tmp/seen-live.json state/seen.json   # keeps the live state
python3 agent.py labels runs/<run1>-raw.json --analytics-only   # 20 postings for hand labels -> labels/labels.csv
python3 agent.py experiment runs/<run1>-raw.json --split dev     # baseline vs revised prompt on 10 dev postings
python3 agent.py experiment runs/<run1>-raw.json --split heldout # only at the end
python3 agent.py sample runs/<run1>-raw.json --n 4               # 5 postings x 4 fresh claude -p calls
```

## What ran
All on 2026-10-31.
- **Tests:** `python3 -m unittest discover -s tests -v` → `Ran 9 tests … OK` (my Mac). After I added the runtime persona check (`load_resume` refuses a résumé without an @example.com email and a 555 phone): `Ran 10 tests … OK`.
- **Run 1 (live, baseline):** `runs/2026-10-31T173836-live-raw.json` — 156 postings on Klaviyo's board, 0 reported as new (baseline), ids saved in `state/seen.json` (my Mac).
- **Run 2 (SEEDED, clearly constructed):** the board did not change within the evening, so I used the assignment's "saved earlier response" option. `runs/seeded-earlier.json` = run 1's real response minus its 3 highest ids. Baseline on it: `2026-10-31T175858-SEEDED` → 153 postings, 0 new. Replay of the real response: `2026-10-31T175859-from-saved` → **3 new** (Associate Growth Specialist German-Speaker; Lead Product Data Scientist, Agents; Lead Product Data Scientist, Forecasting). Rule and Claude both said `not_relevant` for all three; all three Claude replies passed the validator. State: `state/seen-seeded.json`. This seeded run was executed by Claude in its workspace, on my run-1 raw response, because it included Claude judgments.
- **Run 2b (live, second real run, ~6:26 pm):** `2026-10-31T182630-live: 156 on board, baseline=False, new=0 -> runs/2026-10-31T182630-live-report.json`. Result: no postings were new since run 1. Judged by the written rule only (`--no-claude`), because my Claude Code was still at its spend limit.
- **Note:** `runs/2026-10-31T173836-live-report.json` is empty (0 bytes) and I don't know why. The evidence for run 1 is its raw response (`runs/2026-10-31T173836-live-raw.json`, 156 postings) and `state/seen.json`, which recorded 156 ids with `last_run` `2026-10-31T173836-live` before run 2b.
- **Run 1 reproduction:** `runs/*-run1-REPRODUCED-report.json` re-runs run 1's saved raw response on an empty state: baseline, 156 postings, 0 new. It is labelled as a reproduction and is not the original file.
- **Claude calls:** my own Claude Code hit its spend limit (`You've hit your individual spend limit`, exit 1) at ~5:56 pm, so my first experiment run produced 60 empty replies, all correctly rejected as `INVALID`. The real runs (dev, held-out, sampling, and run 2's three judgments) were made with `claude -p` in Claude's workspace at ~6:00 pm on the same code, raw response and labels. At ~6:17 pm, dev, held-out and sampling were rerun so that every raw reply is saved with its time (`raw_reply`, `at` in `reports/*.json`); the 6:00 pm verdict-only files are in `reports/first-run-1800-verdicts-only/`. Nothing in the prompts changed between the dev and held-out runs. See FRICTIONAL.md.

## Files
`agent.py` (fetch, watch, rule judge, Claude judge + validator, reports) · `tests/` (10 tests) · `reports/action-surfaces/` (the real chat and file runs) · `persona/resume.json` (fictional) · `prompts/baseline.txt`, `prompts/revised.txt` (one change: the revised prompt states the three-part rule) · `runs/` raw responses and reports · `state/seen.json` · `labels/labels.csv` (my hand labels) · `label.py` (the helper I labelled with) · `reports/SAMPLING.md`, `reports/EXPERIMENT-dev.md`, `reports/EXPERIMENT-heldout.md` · [ACTION-SURFACES.md](ACTION-SURFACES.md) · [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md)

## Sampling report — conclusion
`reports/SAMPLING.md`: 5 postings × 4 fresh `claude -p` conversations (revised prompt). **Zero variation:** every posting got the same verdict 4/4, and all 20 replies passed the validator. On 4 of 5 that verdict matched my hand label. On the 5th — *Senior CS Compensation Analyst*, the only posting I labelled `relevant` — Claude said `not_relevant` **4 times out of 4**. That is the point of this report: Claude was perfectly repeatable and still disagreed with me, so repeatability is not correctness. I also cannot conclude Claude is "wrong" there: the posting asks for "3–5 years", my rule takes the top of the range (5 > 3) and also says `not_relevant`; I read it as reachable at 3. Four tries per posting also can't show rare flips.

## Prompt experiment — conclusion
One change only: `prompts/revised.txt` adds my three-part rule; nothing else differs. The revision was chosen before any results, not tuned on the dev set. Both prompts were fixed before either split ran, so the held-out set could not influence them. In the 6:17 pm rerun, the two splits ran at the same time. "Pass" = a reply that passes the validator AND matches my hand label.

| set | baseline | revised | written rule |
|---|---|---|---|
| dev (10) | 8/10 (2 INVALID) | 10/10 | 10/10 |
| held-out (10; prompts fixed before it ran) | 6/10 (3 INVALID, 1 wrong); first run 5/10 (4 INVALID) | 9/10 | 9/10 |

What it shows: most of the baseline's failures were **format**, not judgment — in the first run, 4 replies cited `resume_fields` the contract doesn't allow, and 2 quoted the location line (`"San Francisco, CA"`), which my validator rejects because it only checks the posting's title and body (a strictness in my validator, not an invention by Claude). With the rule stated, every reply was valid. The single held-out miss is the same *Senior CS Compensation Analyst* posting, where the rule itself disagrees with me. What it can't show: 19 of my 20 labels are `not_relevant`, so "always say not_relevant" would score 19/20 — ten cases per split cannot separate a good judge from a lazy one, and one disagreement is one posting, not a rate.

## Sign-off — Job-Search Agent 1
- **Checked:** allow-list refusal, slug refusal, real-looking résumé refused at load time, baseline-then-new-by-id, rule verdicts on 4 constructed postings in the tests (one relevant, three not), both wrong versions, validator rejections — by `tests/test_agent.py` (written from CONTRACT.md); the runs by reading the terminal output and the saved `runs/` files (run 1's report file is empty, so for run 1 I relied on the raw response and `state/seen.json`).
- **How:** tests drafted with Claude's help from my contract, then I ran them myself; rule verdicts compared with my hand labels by recomputation: the `experiment` command scores the rule against my labels (19/20 agree). I did not recompute the rule by hand. Claude explained the one disagreement: the posting says "3–5 years" and the rule reads it as 5.
- **Not checked:** (1) whether the years regex reads every way a posting states experience (e.g. "three years", ranges in prose); (2) whether Claude's quotes *support* its verdict (the validator only checks they exist); (3) any board other than Klaviyo, or Greenhouse API changes; (4) whether the rule should read the bottom or the top of a years range ("3–5 years") — my label and the rule disagree on exactly this; (5) a real change on the live board: my live second run (run 2b) was the same evening and found 0 new, so the only run that shows new postings is the seeded one; (6) my labels against the full postings: my labeling rule says to read the whole posting, but `label.py` showed me only the title, location, link and up to 8 lines that mention years, skills or a degree, and I did not open every link, so a label could change on a full read.
- **Not claiming:** that the agent finds good jobs; that 20 hand labels make a valid benchmark; that Claude's verdicts are correct.
- **Signed or withheld:** Signed — Anisha Gaikar, 2026-10-31
## Driver's seat
| Part | Claude | Me | Why it stays mine |
|---|---|---|---|
| Contract and rule | Drafted wording | Chose rule, refusals, approved the failure sentence Claude drafted| Only I decide what "worth my time" means |
| Code and tests | Wrote `agent.py` and tests against the contract | Ran the tests and both live runs on my Mac (the seeded run and every Claude call ran in Claude's workspace) | I sign what ran, not what was written |
| Hand labels | Copied my labels, unchanged, into its workspace run (my Claude Code hit its spend limit) | Labelled all 20 by reading | Labels are the ground truth; Claude can't grade itself |
| Verdict on a posting | Gives a JUDGMENT | Decides whether to apply | My time, my name |
Evidence of the split: commit `509e6ca` (contract committed before any run); `labels/labels.csv` filled by me one posting at a time with `label.py` (my reasons are in the `my_reason` column, e.g. "director, 10 yrs PM"); my Claude Code spend-limit error and the decision to run the judge calls in Claude's workspace are logged in FRICTIONAL.md.

- **Run 2c (live, ~7:09 pm, rule only):** `2026-10-31T190953-live: 156 on board, baseline=False, new=0`. The board still had not changed.
