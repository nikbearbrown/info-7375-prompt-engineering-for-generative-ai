# Job-Search Agent 1 — The Contract and the Watch

INFO7375 · Revan Somshekhar Chonnad · contract in [CONTRACT.md](CONTRACT.md)

Watches one public job board (Klaviyo on Greenhouse), remembers the posting ids it has seen,
and reports only new postings. Each new posting gets two separately labeled verdicts:
a **rule verdict** (a record anyone can recompute from CONTRACT.md) and a **Claude verdict**
(a JUDGMENT, validated for format and citations, never for correctness).
The persona is fictional (`@example.com`, `555` phone).

Commit hashes cited in these documents (such as `2edbefa`) come from this project's own git history, which
was developed in a separate local repository. [COMMIT_LOG.md](COMMIT_LOG.md) lists every one of those commits
with its date, author, and full message, so each citation can be traced in this folder.

## Toolchain

- Python 3.14.5 (macOS, Homebrew). Standard library `urllib` for the fetch.
- `anthropic==2.3.0` (Claude judge), `jsonschema==4.26.0` (résumé schema), `pytest==9.2.0`.
- Claude judge defaults: model `claude-opus-5-5`, effort `medium`, `max_tokens` 8000,
  server-side refusal fallback enabled (the served model is recorded per call as `claude_model_served`).
  No temperature is sent: current Claude models reject sampling parameters. CONTRACT.md asks for the temperature
  to be recorded with each experiment; the record for every call is therefore "none sent", and the model's own
  default sampling applies. Repeat calls are not deterministic, which the sampling report measures.

## Setup from a fresh clone

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

The Claude judge reads `ANTHROPIC_API_KEY` from your environment. It is never written to any file.
Everything except the Claude judge works without it (use `--no-claude`).

## Commands

Run the tests:

```bash
.venv/bin/python -m pytest -v
```

Confirm each CONTRACT.md "wrong version" is caught by its named test (builds mutant copies in a temp dir):

```bash
.venv/bin/python tools/check_wrong_versions.py
```

One watch run (live fetch, both judges):

```bash
.venv/bin/python -m jsagent run --board klaviyo --resume resumes/aarav-patel.json
```

Useful flags: `--seeded-response PATH` (use a saved response instead of fetching; the run is labeled `seeded`),
`--no-claude`, `--state`, `--runs-dir`, `--evidence-dir`, `--model`, `--effort`, `--prompt`, `--json`.
Exit codes: `2` refused fetch or slug, `3` refused résumé, `4` invalid board response (state not advanced),
`5` no Claude credentials (checked first, before anything else, unless `--no-claude` is given).

The run above writes to the committed `state/`, `runs/`, and `evidence/`. To try the agent without changing that
record, and without an API key, point it at a scratch directory:

```bash
.venv/bin/python -m jsagent run --board klaviyo --resume resumes/aarav-patel.json --no-claude --state /tmp/js1/seen_ids.json --runs-dir /tmp/js1/runs --evidence-dir /tmp/js1/evidence
```

The first such run is a baseline (0 new). To see a refusal (exit 2), pass `--no-claude` so the credential check does not answer first:

```bash
.venv/bin/python -m jsagent run --board greenhouse --resume resumes/aarav-patel.json --no-claude
```

## Sampling report and prompt experiment

The labeling rule is [experiment/LABELING_RULE.md](experiment/LABELING_RULE.md). Steps, in order:

1. Create the label sheet. By default it holds every snapshot posting whose title contains a `target_titles` phrase; `--ids` overrides that. It never shows a verdict and refuses to overwrite.

```bash
.venv/bin/python -m experiment.make_label_sheet
```

2. Fill in every row of `experiment/labels.csv` by hand.
3. Split once into 10 dev and 10 held-out postings, stratified by hand label. It refuses to re-split.

```bash
.venv/bin/python -m experiment.split --seed <your seed>
```

4. Sampling: run 5 dev postings with 4 or more fresh calls each. Held-out ids are refused.

```bash
.venv/bin/python -m experiment.sample --ids <five dev ids> --n 4
```

5. Run each prompt on the dev set:

```bash
.venv/bin/python -m experiment.run_experiment --set dev --prompt prompts/baseline.txt
```

```bash
.venv/bin/python -m experiment.run_experiment --set dev --prompt prompts/revision-1.txt
```

6. Run the held-out set last. This needs `--final`, a committed and unedited prompt, and an earlier dev run of that exact prompt.

```bash
.venv/bin/python -m experiment.run_experiment --set heldout --prompt prompts/baseline.txt --final
```

```bash
.venv/bin/python -m experiment.run_experiment --set heldout --prompt prompts/revision-1.txt --final
```

Each invocation writes a new folder under `experiment/sampling/` or `experiment/results/`. The folder holds every raw response, with its date, model, request id, and token usage, plus `summary.json` and `summary.md`. An invalid or unavailable output counts as a fail. Pass rates are reported with a 95% Wilson interval, because ten cases show very little.

## What a run writes

| Path | Contents |
|---|---|
| `evidence/klaviyo_<UTC>.json` | Raw live response, saved before parsing |
| `runs/<UTC>_<mode>.json` | Run mode, source path, baseline flag, one record per new posting |
| `state/seen_ids.json` | Every id seen so far; written last, only if everything before it succeeded |

## Layout

| Path | Role |
|---|---|
| `jsagent/fetch.py` | Allow-list (`boards-api.greenhouse.io`, slug `klaviyo`, one endpoint); redirects held to the same check |
| `jsagent/resume.py`, `resume.schema.json` | Résumé validation and the fictional-persona guard |
| `jsagent/text.py` | HTML stripping and the normalization shared by rule and validator |
| `jsagent/rule.py` | The five-condition rule |
| `jsagent/validator.py` | Rejects any Claude output that breaks the prompt contract |
| `jsagent/claude_judge.py`, `prompts/baseline.txt` | Claude judge and its baseline prompt |
| `jsagent/run.py`, `jsagent/__main__.py` | One run, and the CLI |
| `tests/test_contract.py` | Tests from CONTRACT.md v2, committed before any implementation existed |
| `tests/test_claude_judge.py` | Claude-judge plumbing with a fake client; written after the implementation |
| `tests/test_review_fixes.py` | From the author's review: rule evidence is true (fixtures and all 156 snapshot postings), scalar types, write failure; written after the implementation |
| `tools/check_wrong_versions.py` | Mutation check for the contract's wrong versions |
| `experiment/` | Labeling rule, label sheet, split, sampling, and experiment runner |
| `prompts/revision-1.txt` | The experiment's one change: baseline plus one sentence on preferred qualifications |
| `tests/test_experiment.py` | Experiment tooling with a fake judge; written after the code |

## Implementation choices the contract leaves open

These were made by Claude Code while implementing and are open to the author's review:

- **Skills evidence.** One `skills` entry per posting whose `resume_field`, `resume_value`, and `posting_value`
  are parallel lists: item *i* of each is one matched skill's exact path (e.g. `skills.devops_cicd`), its
  résumé value, and the text as written in the posting. Empty lists mean no skill matched.
  (Modified after author review: the first version put all four category names in one string.)
- **Seniority and role-type evidence.** On a failure, `posting_value` lists the offending words as written
  in the title (for example `["Mobile", "Android"]`); on a pass it is the whole title.
- **Duplicate ids** within one response stop the run, because verdicts are keyed by id.
- **Validator strictness.** A cited list value must be one exact element, matched case-sensitively; a scalar
  must also match the résumé value's JSON type (`2` passes; `"2"`, `2.0`, `true` fail — tightened after author
  review). `posting_value` must appear in the cited field as a complete word sequence after the rule's
  normalization, so case and punctuation are ignored; the prompt says so instead of asking for "verbatim".
- **Failure handling.** A failed run-file or state write is reported as a stopped run (exit 4); the state
  file is only replaced after the run file is written.
- **Privacy.** The Claude prompt receives only the eight allowed résumé paths, never name, email, or phone.
- **Run file names** carry the mode: `runs/<UTC>_seeded.json` and `runs/<UTC>_live.json`.

## Status

What has run so far, on 2026-10-31:

- `pytest`: 28 passed at commit `1397a6f`; 33 passed after the review changes. The 5 new review tests
  were also run against the pre-review code, and all 5 failed there. 41 passed after adding the experiment tooling.
- `tools/check_wrong_versions.py`: all six mutants (five wrong versions, the second split in two) failed their named test.
- CLI smoke runs, all with `--no-claude` and all writing to a scratch directory outside this repo (not kept as evidence):
  a seeded baseline of 156 postings, a live run with 0 new, a refused `--board greenhouse` (exit 2),
  and a rehearsal of the seeded plan that reported exactly ids 8041054003 (relevant) and 7792539003 (not relevant, role type).

Then, on 2026-10-31, run by Revan in a terminal (all committed):

- **Watch run 1** (`runs/2026-10-31T05-37-48Z_seeded.json`): SEEDED baseline, 154 postings, 0 new.
- **Watch run 2** (`runs/2026-10-31T05-51-09Z_live.json`): LIVE, 156 postings, 2 new. 8041054003 came out
  rule `relevant` / Claude `relevant`. 7792539003 came out rule `not_relevant` (role type) / Claude `not_relevant`.
  The live board was byte-identical to the 04:26Z snapshot, so the change between the runs is the seeded removal.
  An earlier attempt at 05:47Z crashed with no API key visible; see FRICTIONAL.md.
- **Sampling, prompt experiment, and the mechanical rule:** results and limits are in
  [SAMPLING_REPORT.md](experiment/SAMPLING_REPORT.md) and [EXPERIMENT_REPORT.md](experiment/EXPERIMENT_REPORT.md).
  Of 60 Claude calls, 56 produced valid outputs, and all 56 matched the hand labels.
- **Action surfaces:** [ACTION_SURFACES.md](experiment/ACTION_SURFACES.md). All three surfaces ran on 2026-10-31.
  The chat paste returned valid JSON; both file-upload runs on claude.ai returned prose, and the first,
  with memory on, used real projects of mine that were not in the input.

Also: [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md) · [evidence/PROVENANCE.md](evidence/PROVENANCE.md)

## Sign-off — Job-Search Agent 1

> **Draft by Claude Code.** Revan: verify every line and change what you would not put your name to.
> The signature line is yours alone.

**Checked**

- **The allow-list and refusals.** Covered by `test_only_klaviyo_on_allowed_host`, `test_cross_host_redirect_refused`, `test_cli_refuses_other_slug`, and `test_real_looking_resume_refused`.
- **New-since-last by id, with a zero-new baseline.** Covered by `test_baseline_reports_zero` and `test_second_run_reports_only_unseen_ids`, and shown by watch runs 1 and 2.
- **State never advances on failure.** Covered by `test_invalid_board_response_does_not_advance_state`, `test_output_write_failure_leaves_state_unchanged`, and `test_cli_refuses_missing_credentials_before_fetching`.
- **Verdicts keyed by id, true rule evidence, and the five conditions.** Covered by `test_verdicts_keyed_by_id`, `test_rule_evidence_is_true_on_real_snapshot` (all 156 postings), and `test_contract_hand_check_examples`.
- **The validator rejects empty or fake citations, wrong types, and prose.** Covered by `test_validator_rejects_empty_or_fake_evidence`, `test_validator_rejects_format_violations`, and `test_validator_requires_same_type_for_scalars`.
- **The authorization flag ignores "work authorized".** Covered by `test_work_authorized_still_needs_sponsorship`.
- **Each contract wrong version is caught by its test.** Shown by `tools/check_wrong_versions.py`, with all 6 mutants caught.

**How**

- **Tests written before the implementation.** The contract tests were written by Claude from my contract, before any implementation existed (`5cef19a`). I ran them but did not read their assertions closely or edit them.
- **Tests from my review.** These came from my own review findings and were written by Claude after the code (`87f68dd`).
- **By hand.** An AI assistant drafted the initial CSV rows; I read all 20 full postings, checked each label against my rule, and adopted them. I checked that `"2"` passed the old validator.
- **By recomputation.** The rule against my labels agrees on 19 of 20, and anyone can recompute it from CONTRACT.md.
- **With Claude's help.** Claude ran a consistency check of my labels against the objective parts of my rule, and drafted the reports.

**Not checked**

- **Prompt injection.** No posting containing instructions to the model was tested.
- **A real board change across days.** Run 2's "new" postings came from my seeded removal; the live board never changed between runs.
- **Repeatability of the chat surfaces.** Surface 1 ran once and surface 2 twice, on one posting.
- **Whether Claude's justifications make sense.** The validator checks only that cited values and phrases exist. One passing citation paired the target title "backend engineer" with the content phrase "This is a backend-heavy role".
- **A live redirect.** Redirect handling was tested only as a function; no real redirect was ever observed.
- **Other personas, boards, models, or efforts.**

**Not claiming**

- **That the Claude judge is accurate in general.** 56 of 56 agreement on 20 mostly easy postings, with 3 relevant, says little.
- **That revision 1 helps or hurts.**
- **That any posting's employer sponsors visas or participates in E-Verify.**
- **That the hand labels are correct.** They are my reviewed judgment under a rule I revised from an AI-assisted first draft.

**Signed or withheld:** Revan Somshekhar Chonnad , 31 oct 2026

## Driver's seat

| Part of the task | What Claude did | What I did | Why that part stays mine | Evidence |
|---|---|---|---|---|
| The contract | Checked v1 against live data and pointed out the problems | Wrote v1 and v2 and made every rule decision | The rule defines "relevant" for my search, and a TA must be able to predict it from my words | `2091127`, `021999d` |
| The code | Wrote the implementation and tests | Reviewed them; accepted, modified, and rejected specific choices | I answer for how it behaves | `87f68dd`; FRICTIONAL.md §3 |
| Hand labels | Checked consistency only; changed no label; a separate AI assistant drafted the initial CSV rows | Read all 20 full postings, checked each label, and adopted the rows | The experiment compares Claude against my reviewed judgment | `2edbefa`, `335d280`; SOURCES.md |
| Prompt revision | Built the tooling and froze the order | Chose the one change before any call | Choosing after seeing results would bias the test | `ba3a9b8` |
| Runs | Built the guards that refuse unsafe runs | Ran the seeded and live runs, the sampling, and the experiment in my terminal, with my key | The key, the spending, and the record are mine | `37d77e4`, `5fc0b68`, `30e722c` |
| Conclusions | Drafted the reports | Reviewed the results and adopted the reports with corrections and stated limits | What the results mean is a claim under my name | SAMPLING_REPORT.md, EXPERIMENT_REPORT.md, ACTION_SURFACES.md; the commit that adds this line |
