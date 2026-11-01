# Job-Search Agent 1: The Contract and the Watch

INFO 7375 Prompt Engineering for Generative AI, Fall 2026 · Pavithra Prasad (`pavithra-p`) · Assignment JS1

A small agent that watches one public job board (Pinterest, on Greenhouse), keeps only the postings that are new since its last run, and judges each new posting for a fictional candidate, Rohan Mehta. Every new posting gets two verdicts. One comes from the written rule in `CONTRACT.md`, a record that anyone can recompute. The other comes from Claude, a judgment that is labelled as one and checked by a validator. The agent never applies, emails, messages anyone or logs in.

## Contents

| Path | What it is |
|---|---|
| `CONTRACT.md` | In / Out / Refuses, the relevance rule, the two wrong versions, the failure sentence. Written first (`586c296` my draft, `9aed486` the reviewed version, both before any code) |
| `agent/` | the code: `fetch.py` (allow-listed GET), `resume.py` (fictional résumé check), `watch.py` (raw response, state, new-since-last), `rule.py` (the rule judge), `wrong_versions.py`, `claude_judge.py` (prompt contract and validator), `freeze.py`, `experiments.py`, `surfaces.py`, `__main__.py` (commands) |
| `tests/` | 46 offline tests (list below). All fixtures are labelled CONSTRUCTED |
| `data/rohan-mehta.resume.json` | the fictional persona (`@example.com`, 555 phone) |
| `evidence/raw/` | every raw board response, saved before parsing |
| `evidence/runs/` | the report of each watch run |
| `state/seen_ids.json` | the state file: every job ID seen, and a log of the runs |
| `evidence/claude/` | every Claude reply, saved as it came back (sampling, experiment, watch) |
| `SAMPLING-REPORT.md` | Chapter 1: 5 postings × 4 fresh conversations |
| `experiment/`, `PROMPT-EXPERIMENT.md` | Chapter 2: the 20 frozen postings, my hand labels, both prompts, the results, and the label audit (`experiment/label-audit.md`) |
| `experiment-2/` | experiment 2: 20 new postings from seven more boards, frozen and labelled before any Claude answer, my labels and the one revision. Results in `PROMPT-EXPERIMENT.md` |
| `ACTION-SURFACES.md`, `action-surfaces/` | Chapter 3: chat vs file vs agent, and the least-autonomy choice |
| `SOURCES.md`, `FRICTIONAL.md` | what I used and what Claude contributed; my dated log |

## Toolchain

* Python 3.13.1, standard library only. Nothing to install for the code and the tests.
* Claude judgments use Claude Code's command line, `claude -p` (version 2.1.294, model `claude-sonnet-5-5`), with no tools, from an empty temporary folder, so each call is a fresh conversation. No API key is used. `--no-claude` skips Claude, and the rule still runs.
* Tested on macOS (Darwin 25.5).

## Commands

Run everything from this folder.

```bash
python3 -m unittest discover -s tests
```

```bash
python3 -m agent watch
```

`watch` fetches `https://boards-api.greenhouse.io/v1/boards/pinterest/jobs?content=true`, saves the raw response, compares the job IDs with `state/seen_ids.json`, and judges each new job with both judges. The first run is a baseline and reports 0 new.

| Command | What it does |
|---|---|
| `python3 -m agent watch --no-claude` | same, with the rule judge only |
| `python3 -m agent watch --from-file PATH` | uses a saved response instead of fetching. The run is labelled SEEDED and uses its own state file |
| `python3 -m agent snapshot figma` / `twilio` | saves one experiment board's raw response (no state, no verdicts) |
| `python3 -m agent freeze RAW...` | freezes the 20 postings and the dev/held-out split |
| `python3 -m agent sample` | sampling report: 5 dev postings × 4 fresh Claude conversations |
| `python3 -m agent experiment experiment/prompts/baseline.md --split dev` | one prompt on one split (`dev` or `held-out`) |
| `python3 -m agent surfaces 7832348` | action surfaces: writes the chat text, then lets Claude Code read the two files |
| `python3 -m agent audit` | label audit: scores the saved experiment replies against my labels and against the written rule. No Claude call |
| `python3 -m agent freeze --set 2 RAW...` | experiment 2: freezes 20 new postings in `experiment-2/` (the exact command is in `experiment-2/README.md`) |
| `python3 -m agent experiment PROMPT --split dev --set 2` | one prompt on one split of experiment 2 |

## What ran

All times are UTC. Each line points to the saved output.

| When | What | Result | Evidence |
|---|---|---|---|
| 2026-10-30 12:18:08 | Run 1 (baseline), in my own terminal | 165 jobs, 0 new | `evidence/runs/run-20261030T121808Z.md`, commit `d6a3a4b` |
| 2026-10-30 13:21 | Figma and Twilio snapshots, then the freeze (20 postings, 10 dev / 10 held-out) | before any label or Claude answer | `experiment/postings.json`, `c16b311` |
| 2026-10-30 | My 20 hand labels | 11 Relevant, 9 Not Relevant | `experiment/labels.csv`, `7327ccd` |
| 2026-10-30 14:05–14:07 | Sampling | 20/20 valid, the same verdict 4/4 on every posting | `SAMPLING-REPORT.md`, `evidence/claude/sampling/` |
| 2026-10-31 00:27–16:38 | Prompt experiment, 4 runs | against my labels: dev 3/10 → 7/10, held-out 4/10 → 8/10; 0 invalid | `PROMPT-EXPERIMENT.md`, `evidence/claude/experiment/` |
| 2026-10-31 17:39:02 | Run 2 (a real second day), in my own terminal | 170 jobs, 8 new. The rule: 8 Not Relevant. Claude: 6 Not Relevant, 2 invalid (empty `resume_fields`), saved and not repaired | `evidence/runs/run-20261031T173902Z.md`, `evidence/claude/watch/`, `15e9d2a` |
| 2026-10-31 17:39:16 | Run 3, the same command again 14 seconds later | 170 jobs, 0 new (nothing is reported twice) | `evidence/runs/run-20261031T173916Z.md` |
| 2026-10-31 17:42–17:45 | Action surfaces on job 7832348 | chat, file and agent all Not Relevant | `ACTION-SURFACES.md`, `5a9bd79` |
| 2026-10-31 21:44:48 | Label audit, in my own terminal | my labels agree with the written rule on 7/20. Against the rule: baseline 10/10 on both sets, revision 6/10 on both | `experiment/label-audit.md`, `PROMPT-EXPERIMENT.md` |
| 2026-10-31 22:04–22:38 | Experiment 2: seven boards saved, 20 new postings frozen at 22:38:41Z. An earlier freeze was deleted by mistake and redone with the same rule; the same 20 IDs came back | 10 dev / 10 held-out, before any label or Claude answer | `experiment-2/README.md` |
| 2026-10-31 | My 20 labels for experiment 2 | 8 Relevant, 12 Not Relevant | `experiment-2/my-labels.txt`, `experiment-2/labels.csv` |
| 2026-10-31 22:57 | Record fix: "1.5+ years" was read as 5 | experiment 1 and both Pinterest runs unchanged; experiment 2's 8003020003 now Relevant | `agent/rule.py`, `test_experience_reads_decimal_years_whole` |
| 2026-10-31 22:46–22:51 | Experiment 2, 4 runs, held-out last | baseline and revision both 8/10 on dev and 8/10 on held-out; 0 invalid | `PROMPT-EXPERIMENT.md`, `evidence/claude/experiment-2/` |

No seeded run was needed, because run 2 found real new jobs.

## Tests (46, offline)

* `test_fetch.py` (4): refuses other hosts and plain http, sends only GET, refuses a redirect to another host.
* `test_resume.py` (4): the persona passes; refuses a résumé without an `@example.com` email, without a 555 phone, or missing a skill list.
* `test_watch.py` (11): first run reports 0 new; the second run reports only unseen IDs; duplicates reported once; the raw response is saved before the state changes; the report lists only IDs from the raw response; a failed fetch leaves the state unchanged; a refused résumé stops before any fetch; a seeded run is labelled; both judges are shown and labelled; `--no-claude`; the live baseline through the command line.
* `test_rule.py` (13): each of the four rule parts, including the "CA" (Canada) location trap and decimal years like "1.5+ years"; all four are needed; the verdict is labelled a record; wrong version 1 (verdicts paired with the wrong job ID) and wrong version 2 (a reason that cites nothing) are both caught.
* `test_claude_judge.py` (7): the validator accepts only the exact format; Claude's opinion is labelled a judgment; invalid replies are saved and never repaired; each call is fresh, with no tools and no project folder; the prompt carries no email or phone; a command-line failure is recorded as invalid.
* `test_freeze.py` (4): keeps only non-senior US engineering roles; the order and the alternating split; 10/10; experiment 2's selection.
* `test_audit.py` (1): each prompt is scored against my labels and against the written rule, and the labels are never changed.
* `test_surfaces.py` (2): the chat text has no email or phone; the file way gives Claude only the Read tool.

## Credits

The persona is adapted from the Reallocation Engine example `search/examples/aarav-patel/` (commit `d08afdd`). Only the name, email, LinkedIn and GitHub were changed. Claude Code wrote most of the code, the tests and the first drafts of these documents. `SOURCES.md` says exactly what came from where.

## Sign-off — Job-Search Agent 1

```text
Checked:      1. New since last run: I recomputed run 2's new IDs from the two raw responses
                 (evidence/raw/pinterest-20261030T121808Z.json and ...20261031T173902Z.json)
                 and got the same 8 as the run report. Run 3, 14 seconds later, reported 0 new.
              2. My labels against my contract: the label audit shows they agree with the
                 written rule on 7 of 20. The baseline agrees with the rule on 20 of 20, the
                 revision on 12 of 20 (experiment/label-audit.md).
              3. Three saved postings in experiment/postings/: 8009057 asks for "4+ years"
                 (line 35); 7838591 asks for no years, only a degree by June 2027 (line 27),
                 and names Python, Java and TypeScript (line 32); 8213988 asks for "Minimum of
                 2 years" (line 28) and names SQL and Python (line 29). On these three the
                 rule's verdict holds, and my label differs from it. 7661919 line 33 says
                 "Minimum 2-3+ years", the quote Claude used in the sampling report.
              4. The 44 offline tests passed in my terminal, including test_first_run_reports_zero_new,
                 test_second_run_reports_only_unseen_ids, test_fetch_refuses_other_hosts,
                 test_location_rejects_toronto_ca, test_invalid_reply_is_saved_and_never_repaired,
                 test_pairing_check_catches_wrong_version_1, test_reason_check_catches_wrong_version_2
                 and test_each_prompt_is_scored_against_my_labels_and_against_the_rule.
                 Two more tests (experiment 2's selection, decimal years) were added after.
How:          By recomputation (1 and 2), by hand (3), and with Claude's help: Claude Code wrote
              all 46 tests, the audit command and the one-line set difference. I ran them in my
              own terminal on 2026-10-31.
Not checked:  1. Whether the Read tool in the file way would really read a file outside its folder.
              2. Whether the revised prompt is repeatable: it ran once per posting. Only the
                 baseline was sampled 4 times.
              3. Most of the quotes in Claude's 40 experiment reasons. Only a few were checked
                 against the saved postings (SAMPLING-REPORT.md), not all of them.
              4. Watching more than one board, or for more than two days. The other boards were
                 only snapshots for the two experiments.
              5. Whether whole-word matching counts a skill used in another sense, for example
                 "Java" inside a sentence about coffee. No test covers that.
              6. Whether my labels are right for Rohan. In experiment 1 they differ from my
                 written rule on 13 of 20, in experiment 2 on 4 of 20 (fewer than two skills).
              7. How a range of years should be read. The record reads "2–12+ years" as 12
                 (two experiment 2 postings) where Claude read 2; my contract does not say.
                 Its "1.5+ years" misreading was fixed, with a test.
Not claiming: that a Relevant verdict means Rohan should apply; that the agent finds every
              relevant job (one board only); that Claude's judgment is a fact; that pass rates
              on 10 postings say anything general; that the revised prompt is better (it matches
              my labels more and my contract less); that the experiment 2 revision changed
              anything (8/10 before and after, on both sets).
Signed or withheld: Signed, Pavithra Prasad, 2026-10-31
```

## Driver's seat

| Task | What Claude did | What I did | Why that part stays mine | Evidence |
|---|---|---|---|---|
| The contract | Claude Code sharpened my draft: exact rule words, the "CA" trap, the refuses list | I wrote the draft, kept the rule and cut the long version back to six sections | The rule decides which jobs reach me | `586c296` (my draft) → `9aed486` |
| The 20 postings | Claude Code wrote the selection and froze the first 20 | I rejected the first freeze (mostly senior roles) and asked for non-senior roles | The test set has to look like the jobs I would actually see | `5b130b8` → `c16b311` |
| Hand labels | nothing | I labelled all 20 before any Claude answer and decided my labelling rule | Claude is scored against the labels, so it cannot write them | `7327ccd`, `experiment/README.md` |
| Sampling conclusion | Claude Code ran the 20 conversations and made the table | I wrote the conclusion | What the numbers mean is my call | `SAMPLING-REPORT.md` "My conclusion", `aa3e1ab` |
| The one prompt change | Claude Code showed two options with predictions | I chose "drop the years check", from the dev results only | Choosing the change is the experiment | `287eefe` → `30e32c3` |
| The two real runs | Claude Code wrote the watcher | I ran run 1 and run 2 in my own terminal | A real second run has to be a real day, not a replay | `d6a3a4b`, `15e9d2a` |
| The chat surface | Claude Code wrote the text to paste | I pasted it into claude.ai and brought the reply back | Only I can use my claude.ai account | `action-surfaces/1-chat/reply-7832348.json` |
| Label audit | a ChatGPT cross-check found the gap; Claude Code wrote the audit command and its test | I ran the audit, kept my labels unchanged and re-read three postings myself | Changing the labels after seeing Claude's answers would hide the gap | `experiment/label-audit.md` |
| Experiment 2 | Claude Code froze 20 new postings, listed each one's years lines and skills by text search, ran the 40 calls, and chose the one change when I asked it to | I decided all 20 labels (3+ years Not Relevant, the others Relevant) and accepted the change, with my reason in `PROMPT-EXPERIMENT.md` | The labels are the yardstick | `experiment-2/my-labels.txt`, `experiment-2/README.md` |
| Whether a job is worth applying to | gives a labelled judgment | decides | Claude can apply my rule; it cannot know what a job is worth to me | `evidence/runs/` |
