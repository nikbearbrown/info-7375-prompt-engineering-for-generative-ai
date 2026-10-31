# Early Bird — Job-Search Agent 1: The Contract and the Watch

Vrajesh N. · INFO 7375 Fall 2026 · Chapters 1–3

One public board (Ashby, Commure), one fictional resume (Rohan Desai, `@example.com`, 555 number), new postings only, and every verdict justified twice: once by my written rule (a **record**) and once by Claude (a **judgment**, labeled as one).

| File | What it is |
|---|---|
| [CONTRACT.md](CONTRACT.md) | In / Out / Refuses / Rule / Wrong versions / Failure. Written first (10-24, closed 10-31 before code) |
| [TEST-EXPECTATIONS.md](TEST-EXPECTATIONS.md) | "given X, expect Y" rows, written before the code |
| `earlybird/` | the agent: `fetch.py` (allow-list), `resume.py` (fictional-only), `rule.py` (R1–R4), `validate.py`, `claude_judge.py`, `watch.py` (seen ids), `__main__.py` |
| `tests/` | 21 tests, plus `wrong_versions.py` (the two wrong implementations the tests must catch) |
| `data/raw/` | raw responses: `2026-10-14/` and `2026-10-23/` (fetched by my pitch-film probe, same bytes as `final-project-film/evidence/`), `2026-10-31/` (fetched by this agent) |
| `data/state/seen.json` | state after runs 1–3 |
| `reports/` | one `.md` plus `.json` per run |
| [SAMPLING-REPORT.md](SAMPLING-REPORT.md) | Chapter 1: 5 postings × 4 fresh conversations |
| [PROMPT-EXPERIMENT.md](PROMPT-EXPERIMENT.md) | Chapter 2: 20 hand labels, baseline vs one change, dev then held-out |
| [ACTION-SURFACE.md](ACTION-SURFACE.md) | Chapter 3: chat paste vs file read vs agent, plus the autonomy choice |
| [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md) | who did what · my honest log |

## Language and toolchain
- **Python 3.13.3**, standard library only (no `pip install`).
- **Claude Code CLI 2.1.314** (`claude -p`), only for `--claude` and `experiments/`. Model: `claude-sonnet-5-5`. The rule, the watch and the tests run without it.
- Tested on Windows 11 (Git Bash and PowerShell). Commands below use forward slashes.

## Exact commands (from a fresh clone, inside this folder)
```bash
# 1. tests (no network, no Claude)
python -m unittest discover -s tests -v

# 2. replay the two-day watch into a fresh state file (no network; leaves the submitted state alone)
python -m earlybird run --snapshot data/raw/2026-10-14/ashby_commure.json --day 2026-10-14 --label repro-run1 --state data/state/repro.json
python -m earlybird run --snapshot data/raw/2026-10-23/ashby_commure.json --day 2026-10-23 --label repro-run2 --state data/state/repro.json
#    expected: "80 postings, 0 new" then "81 postings, 12 new (0 relevant by the rule)"

# 3. live run against the board, with Claude's labeled judgment (needs network and a logged-in `claude`)
python -m earlybird run --live --claude --label my-live-run --state data/state/repro.json

# 4. refusals
python -m earlybird run --snapshot data/raw/2026-10-23/ashby_commure.json --day 2026-10-23 --label x --resume tests/wrong_versions.py   # REFUSED: not a resume

# 5. experiments (need `claude`)
python experiments/sampling.py --n 4 <id> <id> <id> <id> <id>
python experiments/prompt_experiment.py baseline dev
python experiments/prompt_experiment.py revision dev
python experiments/prompt_experiment.py revision heldout --final
```

## What ran (all on 2026-10-31 unless noted)

| Run | Source | Postings | New | Relevant (rule) | Claude |
|---|---|---|---|---|---|
| run1 | 10-14 saved response, replayed: **baseline** | 80 | 0 | – | – |
| run2 | 10-23 saved response, replayed (a real second calendar day of the board) | 81 | 12 | 0 | 12/12 valid, 12/12 agree with the rule |
| run3 | **live fetch** by this agent | 84 | 7 | 0 | 7/7 valid, 7/7 agree with the rule |

- Runs 1 and 2 are **replays** of responses fetched live on 2026-10-14 and 2026-10-23 by `data/raw/probe.py`. They are not seeded or edited: the md5 hashes equal `final-project-film/evidence/`. Run 3 is the only fetch the agent itself made.
- Tests: 21/21 passed. Claude ran them while building, and I ran them myself afterwards (21 passed in 0.10s; see the sign-off).
- Failure check (CONTRACT.md): neither failure happened. Fetches returned 80/81/84 postings, and the second run reported 12 new.

## Sign-off — Job-Search Agent 1
> Drafted by Claude from what was actually run; read by me and signed with no changes to the text (signature typed by me).

- **Checked:**
  - baseline = 0 new and new-by-id on a real second day (`test_baseline_reports_zero_new`, `test_second_run_reports_only_new_ids`)
  - state is saved (`test_state_is_saved_and_repeat_run_is_zero`)
  - both wrong versions are caught (`test_tests_catch_wrong_version_1/2`)
  - off-allow-list host refused (`test_off_allowlist_host_refused`)
  - real resume refused (`test_real_resume_refused`)
  - validator rejects prose, code fences, extra keys, missing or invented citations, wrong posting id (`test_validator_*`)
  - each of R1–R4 (`test_rule_*`)
- **How:**
  - The test expectations were written by me before Claude wrote code (TEST-EXPECTATIONS.md). Claude wrote the code and the tests against them.
  - I ran the tests myself on 2026-10-31. My words: "All 21 tests passed in 0.10s. They cover the refusals, the relevance rule, the validator and the watch behavior."
  - The 20 hand labels are mine, done by hand.
  - The run counts can be recomputed from `data/raw/` with the replay commands above.
  - Claude drafted the reports from the result files.
- **Not checked:**
  1. Any board other than Commure, or any ATS other than Ashby.
  2. Whether the years regex is right on real text beyond the postings I looked at. It counts any "N years" in the description, so a line like "founded 5 years ago" would wrongly fail R2.
  3. R4 never fired on a real posting. No Commure posting said it won't sponsor, so the sponsorship blocker is tested only on a constructed posting.
  4. How often Claude flips on a posting. 4 samples can't show a 1-in-10 flip, and the prompt experiment ran each prompt once per posting.
  5. Whether my rule picks jobs that are actually worth applying to. It agreed with my labels 20/20, but I labeled with that same rule.
  6. Ashby's terms of use beyond reading the public posting API at about one request per run.
- **Not claiming:** that the revision prompt is better (one held-out posting flipped), that Claude's verdicts are correct, or that this generalizes beyond one company, one week and one fictional resume. The agent does not apply, email, message or log in anywhere.
- **Signed or withheld:** Signed: Vrajesh Nasit - 10/31/2026 - 10:14 AM

## Driver's seat

| Part | Claude did | I did | Why it stays mine | Where it shows |
|---|---|---|---|---|
| The contract | turned my OPEN items into multiple-choice questions; placed my answers | wrote the 10-24 words; chose every option on 10-31 | what "relevant" means for me is my call, not the model's | CONTRACT.md lines marked *(chosen 10-31)*; my 10-24 lines kept verbatim |
| Code and tests | wrote all of `earlybird/`, `tests/` and `experiments/` | wrote the expectations first; ran the tests myself | I have to be able to explain why a test exists | TEST-EXPECTATIONS.md; sign-off "How" |
| Hand labels | built the sheet, hid the rule's verdict | labeled all 20; changed #8 after a second look | the labels are the ground truth; a model can't grade itself | labels.csv `hand_note`: "5,16 yes other's No i guess", then "i also think it's yes" |
| The one prompt change | offered three options | picked "clarify sponsorship" | the prompt says what I mean, so I choose what to fix | PROMPT-EXPERIMENT.md "Prompts" |
| Chat-paste arm | wrote the question text | ran it in claude.ai and pasted the answer back | the assignment asks for a response I actually got | ACTION-SURFACE.md arm 1 |
| Sign-off | drafted it | read it and signed it | my name goes on it | the Sign-off section above |
