# Job-Search Agent 1: The Contract and the Watch

**Student:** Ashwin Thankachan · INFO 7375, Fall 2026 · Assignment JS1 (due 2026-10-31)

A watch on one public job board (Klaviyo on Greenhouse) for one **fictional** job seeker, Supriya Sharma
(`data/supriya-sharma.resume.json`, `@example.com` address, 555 phone number). Each run fetches the board
from one allow-listed URL and saves the raw response. It reports only postings whose id is new since the
last successful run, and gives each new posting two labeled verdicts:

- a **RULE RECORD**: the deterministic rule in `CONTRACT.md`, which anyone can recompute;
- an **AI JUDGMENT**: Claude under a prompt contract, accepted only if it passes a strict validator.

The agent never applies, emails, messages or logs in anywhere.

## Language and toolchain

| | |
|---|---|
| Language | Python 3, **standard library only** (no `pip install`) |
| Tested with | Python 3.12.15 (Homebrew) and Python 3.9.6 (macOS `/usr/bin/python3`) |
| Claude | Claude Code CLI 2.1.285, called headless as `claude -p`; model reported `claude-opus-5-5` |
| Board | `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` (public, no key) |

Claude is needed only for `--judge claude` and the `jobwatch.lab sample/experiment` commands.
Everything else, including all tests, runs offline without Claude or a network connection.

## Run it

All commands run from this folder.

```bash
python3 -m unittest discover -s tests -t .
```

65 tests: the contract's two wrong versions, the rule, inputs, the watch, the validator, the
worked example on real saved data, and the lab tools. They use fixtures and fake Claude replies, never the network.

Replay the two saved runs offline into a scratch state file. This does not touch the committed state:

```bash
python3 -m jobwatch --fixture runs/2026-10-30T23-25-13Z/raw-response.json --collected-at 2026-10-30T23:25:13Z --state /tmp/js1-state.json --runs /tmp/js1-runs
```

```bash
python3 -m jobwatch --fixture runs/2026-10-31T16-09-43Z/raw-response.json --collected-at 2026-10-31T16:09:43Z --state /tmp/js1-state.json --runs /tmp/js1-runs
```

A live run, with Claude judging each new posting. This fetches the board and **updates `state/seen_ids.json`**:

```bash
python3 -m jobwatch --judge claude
```

**Which prompt the watch uses:** by default `prompts/baseline-v1.md` (the `--prompt` default in
`jobwatch/watch.py`). Run 2 used that default, but it made no Claude call because nothing was new.
`revision-v2` did better in the experiment (see `experiment/REPORT.md`). To use it:

```bash
python3 -m jobwatch --judge claude --prompt prompts/revision-v2.md
```

The default was not changed after the experiment. `experiment/REPORT.md` explains why one flipped posting is weak evidence.

Re-print the experiment's pass-rate table from the saved results:

```bash
python3 -m jobwatch.lab summary
```

The commands that made the Chapter artifacts: `jobwatch.lab select --seed 2608`, `label`, `supplement`,
`label --supplement`, `sample`, `experiment --prompt P --set dev|heldout [--final]`, and
`python3 action-surfaces/file_read.py`. `python3 -m jobwatch.lab --help` lists them. Rerunning them
would make new Claude calls and new result folders. `select` and `supplement` refuse to overwrite their files.

## What ran

| When (UTC) | What | Who ran it | Result | Evidence |
|---|---|---|---|---|
| 2026-10-30 | Test suite, before any live run | Ashwin | 48/48 OK | My terminal output; not saved as a file |
| 2026-10-30 23:25:13 | **Run 1**, live baseline: `python3 -m jobwatch` (no Claude) | Ashwin | 156 postings, 0 reported new (baseline) | `runs/2026-10-30T23-25-13Z/` |
| 2026-10-31 16:09:43 | **Run 2**, live, second calendar day: `python3 -m jobwatch --judge claude` (default prompt `baseline-v1`) | Ashwin | 156 postings, same ids, **0 new**, so no Claude call. 8 postings changed `updated_at` and were correctly not treated as new | `runs/2026-10-31T16-09-43Z/` |
| 2026-10-31 17:56 | Sampling: 5 postings × 4 fresh calls | Claude Code | 20/20 valid, all unanimous, 16/20 agree with my labels | `sampling/REPORT.md` |
| 2026-10-31 17:57–18:00 | Prompt experiment: baseline and one revision, dev then held-out | Claude Code | **Original 20:** both prompts 10/10 on dev and 10/10 on held-out, so no difference. **Supplement 4 (exploratory, added after labeling):** 1/2 → 2/2 on dev and 1/2 → 2/2 on held-out; the held-out gain is one already-familiar posting. Not clean evidence of generalization | `experiment/REPORT.md` |
| 2026-10-31 | Action surfaces: chat paste and file read, `revision-v2` rules | Ashwin (chat), Claude Code (file read) | Both RELEVANT and valid. The watch made no Claude call (0 new) | `action-surfaces/COMPARISON.md` |
| 2026-10-31 | Review of the drafts; reran 64 tests on 3.9.6 and 3.12.15, checked the saved hashes, 0 new ids and 8 changed timestamps | Codex, used by Ashwin | Found a validator crash and four documentation problems | FRICTIONAL.md; fix in `c42f2c6` |
| 2026-10-31 18:44:21 | **Seeded replay** through the real watch: run 2's unmodified response, scratch state with 7855793003 removed, `--prompt prompts/revision-v2.md` | Claude Code | 1 new; RULE RECORD RELEVANT, AI JUDGMENT RELEVANT (one real call, valid); scratch state 155 → 156 ids; committed state and live runs unchanged | `action-surfaces/3-watch-seeded/NOTES.md` |
| 2026-10-31 | Test suite after the fixes | Claude Code | 65/65 OK on 3.12.15 and 3.9.6 | — |
| 2026-10-31 | `python3 scripts/validate_course.py` from the repository root | Codex, then Claude Code | **Exits with failure** (exit code 1). Every listed failure is outside this folder: other students' `.ts`/`.tsx` files and broken links elsewhere in the shared course repository. None names `js1-contract-and-watch` | — |

**No new posting appeared between runs 1 and 2,** so the live runs show the baseline, the new-by-id
check and the state update, but no live Claude verdict on a new posting. The full path, from new posting
to rule, Claude, validator, report and state, is shown by `tests/test_watch.py` on constructed fixtures and
by the **seeded** replay on real posting text (`action-surfaces/3-watch-seeded/`). That is not the same as
a posting appearing live. Claude's other verdicts on real postings are in `sampling/` and `experiment/`.

## Contents

| Path | What it is |
|---|---|
| `CONTRACT.md` | In, Out, Refuses, the rule, the worked example, two wrong versions, the failure sentence. Committed (`470fae3`) before any code |
| `jobwatch/` | The watch: `board` (allow-list, fetch), `persona`, `rule`, `state`, `judge` (prompt, `claude -p`, validator), `report`, `watch` (CLI) and `lab` (sampling and experiment tools) |
| `wrong_versions/` | The contract's two wrong versions, kept so the tests can prove they catch them |
| `tests/` | 65 unittest tests; `fixtures/klaviyo-7855798003.json` is one real posting copied from run 1 |
| `prompts/` | `baseline-v1.md` and `revision-v2.md`, which adds one sentence |
| `data/supriya-sharma.resume.json` | The fictional persona. It is validated before every run |
| `runs/`, `state/seen_ids.json` | The two live runs (raw response, SHA-256, report) and the state after run 2 |
| `sampling/` | The Chapter 1 report and its 20 saved replies |
| `experiment/` | The split, my protocol and labels, the supplement, the Chapter 2 report and every result |
| `action-surfaces/` | The Chapter 3 comparison and the records from each surface |
| `snapshots/` | A Cloudflare snapshot from 2026-10-29, before I switched boards. Unused; see FRICTIONAL.md |
| `SOURCES.md`, `FRICTIONAL.md` | Who wrote what, and my log |

Nothing here contains a real résumé, credentials or caches (`.gitignore` excludes `__pycache__/`).

## Sign-off — Job-Search Agent 1

```text
Sign-off — Job-Search Agent 1
Checked:      - The two wrong versions are caught: test_wrong_version_1_positional_verdicts_is_caught,
                test_wrong_version_2_substring_skills_is_caught (tests/test_contract.py).
              - The rule matches my hand evaluation of the worked example on the real saved posting:
                test_hand_evaluation_in_the_contract_matches_the_rule (tests/test_worked_example.py).
              - Baseline reports none as new; new-since-last is by id; a failed fetch, a bad response or
                a failed report write does not move state (tests/test_watch.py).
              - Only the exact allow-listed URL is fetched and redirects are refused (tests/test_inputs.py).
              - Claude replies with a wrong id, a fabricated quote, an unsupported skill, extra text or
                wrong JSON types are rejected (tests/test_judge.py).
              - Run 2 reported 0 new against run 1: recomputed from the two raw responses' id sets
                (by Claude Code and by Codex, not by me).
              Claude Code wrote these tests against my contract.
How:          I ran the original 48 tests and both live runs. Claude Code wrote the implementation and
              tests and ran the final suite. Codex independently reran all 64 tests on Python 3.9.6 and
              3.12.15, checked the saved response hashes, and confirmed 0 new IDs and 8 changed
              timestamps. Those later checks were AI-assisted, not checks I personally performed.
Not checked:  1. No new posting appeared during the live runs, so the full new-posting-to-Claude-to-report
                 path was not demonstrated live.
              2. The held-out evaluation was not entirely blind because one posting was already my
                 worked example.
              3. The results do not establish accuracy on other boards, model versions, or future postings.
              4. The matching GitHub and Canvas submission has not been verified.
Not claiming: I am not claiming the agent identifies every suitable job, establishes hiring
              eligibility, or runs daily without someone starting it.
Signed or withheld: Signed: Ashwin Thankachan, 2026-10-31
```

## Driver's seat

| Part of the task | Claude did | I did | Why this part stays mine | Evidence |
|---|---|---|---|---|
| The contract and the rule | Ran checks on my drafts and applied the edits I directed | Wrote `CONTRACT.md`, chose the board, the rule and the wrong versions | I choose the screening criteria and need to explain why each one belongs. | `470fae3`; edits listed in SOURCES.md |
| Code and tests | Wrote `jobwatch/`, the wrong versions and the tests against the contract | Ran the suite (48/48) and both live runs | Claude can implement and test, but I need to understand the behavior before signing off. | `15d6b3f`, `d093ecf`, `26bf8fe` |
| What counts as "relevant" for Supriya | Nothing | Wrote the labeling protocol and all 24 hand labels | The labels represent my interpretation of the fictional candidate's fit. | `20b01fb`, `6773f06`, `f9bd958` |
| The experiment design | Found that the labels were all one class and proposed the supplement | Chose the seed, chose to add the supplement, chose the one change | I own the choices about the split, supplement, and what the results support. | `9ed2e88`, `04bcea5`, `d932e3b` |
| The autonomy choice | Ran the file-read surface and drafted the comparison table | Ran the chat paste and wrote the decision | I decide which actions the workflow needs and what access to give it. | `a13d3ca` |
| The sign-off | Claude Code drafted the "Checked" list from the tests. Codex drafted the "How", "Not checked" and "Not claiming" wording and these driver's-seat reasons | Confirmed the facts in them, decided what is listed as not checked, and signed after my review | Only I can confirm what I personally checked and what remains unverified. | this README |
