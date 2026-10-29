# Job-Search Agent 1 — The Contract and the Watch (nishant-u)

> Draft for Nishant to edit. Drafted by Claude Code on 2026-10-29 from the commit history and the
> files in this folder. Sections marked **TODO-NISHANT** are yours to write.

<!-- data/resume.example.json is copied unchanged from the Reallocation Engine,
     search/examples/priya-nair/resume.example.json (repo commit d08afddc, 2026-08-17).
     sha256 a4fdbc960457ba911b9d3b8593400d17ea77f35a33ce2a508128c1694c4493c1.
     Priya Nair is a FICTIONAL persona (@example.com, 555 phone). -->

## What this is

A watch over one public job board, Faire on Greenhouse (`boards-api.greenhouse.io`, the only allowed
host), for one fictional résumé, Priya Nair. Each run saves the raw board response and its sha256,
compares posting ids with `state/seen_ids.json`, and reports only postings new since the last run;
the first run is a baseline that reports none as new. Each new posting gets a rule verdict labeled
**record**, which anyone can recompute from the rule in `CONTRACT.md`, and, with `--claude`, a Claude
verdict labeled **judgment**, checked by a validator, with every quote checked against the field it
cites. The contract came first: see `CONTRACT.md` and its commit. The agent never applies, emails,
messages or logs in anywhere.

## Language and toolchain

- **Python 3.12, standard library only.** Nothing to install. Tested on Python 3.12.10.
- **Tests:** `unittest`.
- **Optional:** the Claude Code CLI (`claude`), logged in, for `--claude` and the experiment scripts that
  call the judge. Without it, the Claude judge records "not run" and everything else still works. No API
  key is used; the judge calls ran on my Claude Code login.
- **Tested on:** Windows 11 with Git Bash. In Git Bash both `python3` and `python` ran Python 3.12.10.
  On Windows, use `python` (on this machine the `py` launcher failed to start, so it isn't used here).
- **macOS:** with a python.org install, HTTPS may fail with a certificate error until you run the bundled
  "Install Certificates.command" in the Python folder. This only matters for live runs. It hasn't been
  tested here.
- **Windows clone:** other folders in this course repository have paths longer than Windows' default
  limit. Clone with `git clone -c core.longpaths=true ...`, or checkout fails before this folder is
  reached. This folder itself has no long paths.

## Commands for a fresh clone

Run everything from this folder (`fall-2026/nishant-u/js1-contract-and-watch/`). The commands below use
`python3`; on Windows, use `python`.

**Tests (offline, no Claude):**

```bash
python3 -m unittest discover -s tests -t . -v
```

**Replay the baseline response (no network, no Claude).** Point `--state` and `--runs` at a scratch
folder, so the committed state file and runs are left alone:

```bash
python3 -m agent.run --replay runs/2026-10-29-1/raw.json --state /tmp/js1-replay/seen_ids.json --runs /tmp/js1-replay/runs
```

Expected: `68 postings, baseline`, and a report under `/tmp/js1-replay/runs/<date>-1/` whose
`meta.json` has sha256 `3c10b536e3805bb5a4fca46800ac5caf4c521fa84c9beec30a8ab0beb995c2b7`. Running the
same command again reports `68 postings, 0 new`. The printed line says `report in runs/...`; the
report is in the `--runs` folder you gave. In PowerShell, use a Windows path such as
`$env:TEMP\js1-replay\...` instead of `/tmp`.

**A seeded run** (an edited response, labeled seeded in its report):

```bash
python3 -m agent.run --replay <edited.json> --seeded --state /tmp/js1-replay/seen_ids.json --runs /tmp/js1-replay/runs
```

**Live watch** (network GET to the Faire board; updates `state/seen_ids.json` and adds `runs/<date>-<n>/`):

```bash
python3 -m agent.run
```

**Live watch with the Claude judge** (also needs `claude` logged in; one fresh `claude -p` call per new
posting, run with `--tools ""` in an empty temporary folder):

```bash
python3 -m agent.run --claude
```

**Experiment scripts.** These read only saved files, need no network and no Claude, and reproduce the
tables in the reports:

```bash
python3 experiment/report_dev.py sampling            # SAMPLING-REPORT.md tables
python3 experiment/report_dev.py baseline-dev        # BASELINE-DEV.md table
python3 experiment/report_dev.py revision1-dev       # PROMPT-EXPERIMENT.md dev tables
python3 experiment/report_dev.py baseline-heldout    # held-out tables
python3 experiment/report_dev.py revision1-heldout
python3 experiment/rule_vs_hand.py                   # rewrites experiment/rule_vs_hand.md
python3 experiment/action-surface/check_surface_replies.py   # prints the action-surface check
```

These call Claude and were each run once. They are listed for the record, not for a TA to re-run:

```bash
python3 experiment/make_split.py                 # the sealed 20-posting split (no Claude call)
python3 experiment/claude_dev.py sampling        # 5 dev postings x 4 fresh calls
python3 experiment/claude_dev.py baseline-dev    # 10 dev postings, baseline prompt
python3 experiment/claude_dev.py revision1-dev   # 10 dev postings, revision-1 prompt
python3 experiment/claude_dev.py heldout         # held-out, once only; refuses a second run
```

### Fresh-clone check, 2026-10-29

Claude Code cloned this local repository into a temporary folder outside the repo (with
`core.longpaths=true`), checked out `nishant-u-js1` at `3d397ae`, and ran the commands above from this
folder in Git Bash on Windows 11:

| Command | Exit | Result |
|---|---|---|
| `python3 --version` / `python --version` | 0 / 0 | Python 3.12.10 / Python 3.12.10 |
| `python3 -m unittest discover -s tests -t . -v` | 0 | Ran 56 tests, OK |
| replay of `runs/2026-10-29-1/raw.json` into a scratch folder | 0 | 68 postings, baseline; sha256 matched the live run |
| the same replay again | 0 | 68 postings, 0 new |
| `report_dev.py` (all five modes), `rule_vs_hand.py`, `check_surface_replies.py` | 0 | ran; the action-surface output matched `check-output.txt` |

After the runs, the clone's only change was `experiment/rule_vs_hand.md`, with line endings only: Git
checked it out with CRLF, and the script writes LF. No content changed. The live commands and the
scripts that call Claude were not run in this check. The temporary clone was then deleted.

## What actually ran

All on 2026-10-29 (Eastern time) unless marked.

| Step | Commit | What it shows |
|---|---|---|
| Contract, before any code | `3deb719` | `CONTRACT.md`: in, out, refusals, rule R1–R4, Claude schema, three wrong versions |
| Tests first | `771bb15` | tests and constructed fixtures written from the contract; all errored before implementation |
| Implementation | `4b9e88e` | `agent/` |
| Baseline run | `f0bddac` | `runs/2026-10-29-1/`: live fetch, 68 postings, all ids saved, 0 reported as new |
| Hand labels | `8e2fa73` | my 20 labels, blind, before any Claude judge call |
| Freeze | `37fd62f` | both prompts frozen by sha256 before the held-out evaluation |
| Held-out evaluation | `8a53c80` | run once: baseline and revision 1, 10/10 pass each |
| Safety tests | `3d397ae` | redirect refusal, atomic state write, `--tools ""` |
| Second watch run | pending 2026-10-30 | to be `runs/2026-10-30-<n>/`, run by Claude Code with `--claude` (the agent surface in `ACTION-SURFACE.md`) |

The full list of commits is in `git log -- .`.

## Where each required artifact is

| Required artifact | Where |
|---|---|
| Contract | `CONTRACT.md` (amendments at the end); labeling rule in `LABELING-RULE.md` |
| Code | `agent/`: `watch` (allow-listed fetch, state), `rules` (record), `claude_judge` (judgment), `validator`, `resume`, `run` |
| Tests | `tests/`; constructed fixtures in `tests/fixtures/` (see its `README.md`); the three wrong versions in `tests/mutants.py` |
| Raw responses and state | `runs/2026-10-29-1/` (`raw.json` verbatim, `meta.json` with time and sha256, `report.md`, `report.json`); `state/seen_ids.json`. The second run: pending 2026-10-30 |
| Sampling report | `experiment/SAMPLING-REPORT.md`; replies in `experiment/sampling/` |
| Prompt experiment | `experiment/PROMPT-EXPERIMENT.md` (with `BASELINE-DEV.md`, `SPLIT.md`, `rule_vs_hand.md`); prompts in `prompts/`; labels in `experiment/labeling/labels.csv`; replies and results in `experiment/runs/` |
| Action-surface comparison | `experiment/ACTION-SURFACE.md`; kit, prompts, saved replies and check output in `experiment/action-surface/` |
| Sources | `SOURCES.md` |
| Frictional | `FRICTIONAL.md` |

## Sign-off

**TODO-NISHANT:** write this yourself, in the assignment's template. "Not checked" needs at least three
real items. Candidates from the record, for you to keep, change or drop: `, DC` and other non-state
locations aren't counted by R3; the second run hasn't happened yet; the live commands weren't run in
the fresh-clone check; macOS wasn't tested; the undecided choices in `FRICTIONAL.md` (absence citations,
the judge's empty folder).

```text
Sign-off — Job-Search Agent 1
Checked:      TODO-NISHANT
How:          TODO-NISHANT
Not checked:  TODO-NISHANT
Not claiming: TODO-NISHANT
Signed or withheld: TODO-NISHANT (name, date)
```

## Driver's seat

**TODO-NISHANT:** fill in each row, and link the commit, file or transcript line that shows the split.

| Task | What Claude did | What I did | Why that part stays mine | Evidence |
|---|---|---|---|---|
| TODO-NISHANT | | | | |
| TODO-NISHANT | | | | |
| TODO-NISHANT | | | | |
