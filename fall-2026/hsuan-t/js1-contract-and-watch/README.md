# Job-Search Agent 1: The Contract and the Watch

One board, one résumé, new postings only, every verdict justified. The agent watches Stripe's public Greenhouse job board, reports only postings that are new since its last run, and gives each new posting two verdicts: one from my written rule (a **record** anyone can recompute) and one from Claude under a prompt contract (a **judgment**, labeled as one). The spec is [`CONTRACT.md`](CONTRACT.md); when the code and the contract disagree, the contract wins.

## Language and toolchain

| | Version used |
|---|---|
| Language | Python 3.11 (tested on 3.11.10, macOS) |
| Agent dependencies | Python standard library only for the watch and the rule judge |
| Claude judge, default | [Claude Code](https://claude.com/claude-code) CLI `claude`, logged in (tested on 2.1.316); called as `claude -p`, uses your Claude subscription |
| Claude judge, optional | `anthropic==2.3.0` + `ANTHROPIC_API_KEY` (API credits), with `--claude-via api` |
| Tests | `pytest==8.4.2` |
| Board | Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` |

## Exact commands (fresh clone)

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/hsuan-t/js1-contract-and-watch
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt      # pytest + anthropic (anthropic is only for --claude-via api)

# Tests (fake board, fake Claude: no network, no cost, never touches state/ or runs/)
.venv/bin/python -m pytest

# Run 1: replay the saved 2026-10-29 snapshot as the baseline (a "seeded" run; reports 0 new)
.venv/bin/python -m job_agent --from-raw evidence/raw/2026-10-30T033237Z/stripe_content.json

# Run 2: fetch the board live; judges only what is new since Run 1
.venv/bin/python -m job_agent
```

Options: `--claude-via api` (Anthropic API instead of `claude -p`), `--prompt claude_judge.v2` (another prompt file in `prompts/`), `--resume` / `--profile` (other fictional persona files). To start over, delete `state/stripe.state.json`; the next run is a new baseline.

Each run writes `evidence/raw/<UTC>/` (the board's response, byte for byte), `runs/<UTC>/verdicts.json`, `runs/<UTC>/summary.md`, `runs/<UTC>/claude_raw.jsonl` (Claude's replies as received), and updates `state/stripe.state.json` last, after the verdicts are saved.

## What ran

| | Run 1 | Run 2 |
|---|---|---|
| Folder | `runs/2026-10-31T225859Z/` | `runs/2026-10-31T225910Z/` |
| Source | **seeded**: replay of `evidence/raw/2026-10-30T033237Z/` (fetched 2026-10-29 23:32 EDT) | **live**: `evidence/raw/2026-10-31T225910Z/` (2026-10-31) |
| Postings fetched | 737 | 745 |
| New since the last run | 0 (baseline) | **20** |
| Verdicts | `[]` | 20 rule + 20 Claude; all not_relevant from both judges, 0 disagreements, 0 validator rejections |

745 − 737 = 8, but 20 are new: 12 postings closed between the two dates (recomputed from the two raw files: 725 in both, 20 only in Run 2, 12 only in Run 1). The summary shows fetched and new only; showing "no longer listed" is the next layer's first item. `state/stripe.state.json` holds 757 ids, both runs together, so a posting that comes back later isn't reported as new again.

These are the second Run 1 / Run 2. The first pair (working-repo commit 7b63b89, see `evidence/git-history.txt`) ran before I changed check 2 so that a posting with no location passes; I re-ran both with the final rule. Run 2's 20 new postings got the same verdicts both times. The raw fetch from the first Run 2, `evidence/raw/2026-10-31T214118Z/`, is kept because the hand labels come from it.

## The three reports

| Report | Question | Result |
|---|---|---|
| [`reports/sampling_report.md`](reports/sampling_report.md) | 5 postings × 4 fresh conversations: does the verdict move? | Never moved; 4 of 5 match my label. Stable ≠ correct: the 5th was a stable 4-of-4 disagreement |
| [`reports/prompt_experiment.md`](reports/prompt_experiment.md) | Baseline vs one change, dev first, held-out last | v1 8/10 dev, 7/10 held-out; v2 9/10 dev, 9/10 held-out (after correcting one wrong label of mine; both scores shown) |
| [`reports/action_surface.md`](reports/action_surface.md) | Chat paste vs a file vs the agent | Same verdict all three ways; I chose the agent |

Labels: [`labels/LABELING_RULE.md`](labels/LABELING_RULE.md) (committed before any label; order in `evidence/git-history.txt`), [`labels/labels.csv`](labels/labels.csv), [`labels/split.json`](labels/split.json). Prompts: [`prompts/`](prompts/).

## Tests

`.venv/bin/python -m pytest` runs 106 test cases. They use a fake board and a fake Claude (`tests/fakes.py`), and `tests/conftest.py` removes `ANTHROPIC_API_KEY` and hides the `claude` CLI for every test, so no test can call the real Claude or write to the repo's `state/` and `runs/`. My own runs: `evidence/tests/`.

**The tests the CONTRACT names**

| CONTRACT item | Test |
|---|---|
| Wrong version 1: verdict on the wrong posting | `test_wrong_version_1_label_mixup.py::test_each_posting_id_gets_its_own_verdict` |
| Wrong version 2: empty or "good fit" justification | `test_wrong_version_2_justification.py::test_every_ok_verdict_has_a_justification_with_real_field_names`, `::test_empty_jd_is_an_error_not_relevant`, `::test_claude_answer_with_a_quote_not_in_the_posting_is_rejected` |
| Wrong version 3: state not saved or not read | `test_wrong_version_3_state.py::test_second_run_reports_only_the_3_new_of_5` |
| Wrong version 4: case or spacing | `test_wrong_version_4_splitter.py::test_contract_splitter_table` (the contract's 5 rows) |
| Wrong version 5: wrong judge label | `test_wrong_version_5_judge_label.py::test_every_verdict_in_a_run_carries_its_own_judges_label`, `::test_claude_cannot_label_itself` |
| Wrong version 6: visa phrase by plain word matching | `test_wrong_version_6_visa_phrase.py::test_posting_a_passes_check_5`, `::test_posting_b_fails_at_check_5` |
| Refuses: host off the allow-list | `test_refuses.py::test_refused_host_never_gets_a_request` |
| Refuses: real résumé | `test_refuses.py::test_non_example_email_stops_before_fetching` |
| Validator table, one row each | `test_claude_validator.py::test_each_contract_row_rejects_its_example` |

**Extra tests** cover rules the CONTRACT states elsewhere: a broken state file stops the run before any fetch, a junk board response or a crash while judging leaves the state untouched, the raw response is saved byte for byte, a posting with no location passes check 2, Claude errors (no CLI, refusal, cut-off answer) never stop the rule judge, and the `claude -p` call has no tools, no MCP, no saved session and no settings. Each extra test was also checked by planting the bug it guards against and watching it fail.

## Add a skill spelling

If the rule misses a skill because the posting spells it differently, add the spelling to your profile, not to the tool. In `personas/aarav-patel.profile.json`:

```json
"skill_aliases": {"PostgreSQL": ["pg"], "Kubernetes": ["kube"]}
```

These merge with the built-in list in `data/skill_aliases.json`. Check 3's justification shows which spelling matched, e.g. `found: PostgreSQL (as postgres)`. Every run's summary ends with the same reminder and the profile path it used.

## Repo layout

| Path | What |
|---|---|
| `CONTRACT.md` | The spec (English). `CONTRACT.zh.md` is the Chinese original I wrote |
| `job_agent/` | The agent. `common/` (errors, file paths, the allow-listed network door), `watch/` (board adapter, state, new-posting detection), `judges/` (rule checks, Claude judge, validator, the one verdict format), `pipeline.py` (the order of one run), `__main__.py` (command line) |
| `personas/`, `data/` | Fictional résumé + profile (Aarav Patel, `@example.com`); built-in skill aliases and no-sponsorship phrases |
| `prompts/` | Claude's prompt contract: v1 baseline, v2 revision |
| `tests/` | pytest suite |
| `labels/`, `reports/` | Hand labels and the three reports, with the scripts that produced their data |
| `evidence/`, `runs/`, `state/` | Raw board responses, my test runs and terminal output, run verdicts, the state file |
| `SOURCES.md`, `FRICTIONAL.md` | What I used and who wrote what; my working log |

## Sign-off

**Checked**
1. The agent reports only postings new since the last run, and the first run reports 0.
2. Both judges produce the CONTRACT's verdict format with field-level justifications, and Claude's answers only count after the validator accepts them.
3. My labels against Claude's answers, posting by posting, in the prompt experiment.
4. The rule's verdict for one Run 2 posting, recomputed by hand from CONTRACT "The rule".
5. Claude, run as the agent's judge, does not see my own Claude Code instructions or memory.

**How**
1. By recomputation, with Claude's help: the 20 new ids are exactly the ids in Run 2's raw file that are not in Run 1's; I asked why 745 − 737 = 8 when 20 were new (12 closed). Run 1's `verdicts.json` is `[]`.
2. By tests I ran myself (`evidence/tests/`: 54 passed + 2 skipped after Step 4, 96 passed after the Claude judge, and the final run of 106) and by reading Run 2's `verdicts.json`.
3. By hand: I labeled the postings with my own rule before any Claude run on them, then read v1's reasons on the misses. One of them showed my own label was wrong (the New Grad posting caps experience at 18 months; Aarav has about 25), and I corrected it openly.
4. By hand: posting 8336819 (Blockchain Security Engineer, Bridge): check 1a, no excluded word in the title; check 1b, no target phrase ("engineer" alone isn't one), so not_relevant at 1b. That matches the agent's two justification lines.
5. With Claude's help: the same question with and without the judge's flags: 608 input tokens and no trace of my instructions vs 2,819 tokens where it quoted my own instructions back.

**Not checked**
1. Which hosts `claude -p` itself contacts. My program checks every request it makes itself; with the CLI, the request to Claude is made by Claude Code, outside my allow-list.
2. Whether the isolation flags (`--setting-sources ""`, `--strict-mcp-config`, `--tools ""`) behave the same on Claude Code versions other than 2.1.316.
3. Whether the lenient prompt v2 lets clearly bad postings through: all four held-out not_relevant postings were easy ones.
4. Any board other than Stripe on Greenhouse, and any persona other than Aarav.
5. Claude's stability beyond the 5 sampled postings: every other posting was asked once.

**Not claiming**
- That Claude's verdicts are correct, or that a "relevant" posting is a good job for anyone.
- That the pass rates from 10 cases per set say anything general.
- That the rule's location check understands places: it matches words, so "Seattle, WA" fails it even though Seattle is in the US (CONTRACT, Known limits).
- That the agent is ready for a real résumé: it refuses any résumé whose email isn't `@example.com`.

**Signed:** Hsuan-Hung (Isaac) Tai, 2026-10-31

## Driver's seat

Commit ids below are from my working repo, where I built this step by step. The course repo has the whole folder as one commit, so those ids don't exist here; `evidence/git-history.txt` is the full log of the working repo (id, time, author, message, files changed), so the order of every step can still be checked.

| Part | Claude did | I did | Why it stays mine | Where it shows |
|---|---|---|---|---|
| Contract | Skeleton questions; unified field names; ran my rule on saved data to fill Examples; English translation | Wrote the In / Out / Refuses / rule / wrong versions and the dated failure sentence; added checks 4–6 | It's my definition of a good and a failed agent | `CONTRACT.md` committed in a0d895e, before any code (first `.py`: 587d361) |
| Code standard | Wrote all code; refactored Step 3 into modules | Required a company-standard structure before committing | I'll maintain it in later layers | FRICTIONAL "Code has to follow a company standard"; 58a93ee |
| Tests | Wrote the tests; planted bugs to check them | Ran them myself and saved the output | The brief: "Run your tests on what it returns, yourself" | `evidence/tests/`; fcc0376, ce9d196 |
| How Claude is reached | Tested `claude -p` and built it | Chose the CLI over buying API credits | It decides cost and who can reproduce it | "用這個 cli 的方式。因为现在多数人都是买桌面的这种订阅，不太会买 API" (FRICTIONAL "Claude judge through the Claude Code subscription"); ce9d196 |
| Missing location | Found the gap in both rules; offered to only document it | Decided a missing location passes, in my labels and in the rule, and re-ran | It's a rule about what's worth my time | "如果 location 没有写的话，我也一律判定为合格" … "contract 選 B. 重跑"; 7cca07d, cb2291e |
| Hand labels | Picked the 20 postings by a fixed-seed script; typed up my labeling rule from my list | Labeled them, and corrected my own wrong label after reading the posting | Labels are the answer key; a model can't grade itself | ab1e292 (rule before labels), 926f9e6, 74db17f |
| Prompt revision | Ran v1 on dev; offered two candidate changes; wrote v2 | Chose the change and its example ("relevant unless clearly a bad fit") | It encodes my own standard | "選Ｂ，我覺的只要不是明顯不適合就算relevant…" (FRICTIONAL "Prompt v2"); 74db17f |
| Least autonomy | Ran the three surfaces; drafted the table | Chose the agent and gave the reasons | Authority is mine to grant | "My decision" in `reports/action_surface.md`; 93abb22 |
| Sign-off | Drafted the wording | Checked, chose what to claim, signed | My name is on it | This section |
