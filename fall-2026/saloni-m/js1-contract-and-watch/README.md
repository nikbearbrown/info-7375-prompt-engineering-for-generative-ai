# Job-Search Agent 1 — The Contract and the Watch

Saloni M · INFO 7375 · Fall 2026 · built and run 2026-11-01 (after the Oct 31 due date).

One board (Greenhouse `anthropic`), one fictional résumé (Priya Nair, from the Reallocation
Engine's `search/examples/`), new postings only, and two labelled verdicts per new posting: a
**rule record** anyone can recompute, and a **Claude judgment** that must pass a strict validator.
The contract came first: [CONTRACT.md](CONTRACT.md), commit `f166f5d`, before any code.

## Language and toolchain

- **Python 3.13.5** (standard library only: `urllib`, `json`, `unittest`, `subprocess`). Any
  Python ≥ 3.9 should work but only 3.13.5 was run.
- **Claude Code CLI 2.0.20** (`claude -p`), used only for the Claude judge, sampling, experiment
  and action surfaces. It needs a logged-in CLI (`claude`, then `/login`). Set `CLAUDE_BIN` if
  `claude` is not on your PATH. Model pinned with `CLAUDE_MODEL`, default `claude-sonnet-5-5`.
- macOS (Darwin 25.5), zsh. No other dependencies, no virtualenv, no API key in any file.

## Exact commands (from a fresh clone)

```sh
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/saloni-m/js1-contract-and-watch

python3 -m unittest discover -s tests -t . -v          # 14 tests, no network, no Claude

python3 -m agent.watch --resume personas/priya-nair.resume.json            # live run vs committed state
python3 -m agent.watch --resume personas/priya-nair.resume.json --claude   # + Claude judgment (needs CLI)
sh scripts/run_seeded.sh                                                   # the SEEDED two-run demo

python3 scripts/score.py sampling      # recompute SAMPLING-REPORT table from saved calls
python3 scripts/score.py experiment    # recompute PROMPT-EXPERIMENT tables from saved calls

# re-asking Claude (appends new calls; costs ~$0.05 per call on API billing)
python3 scripts/ask_claude.py sampling --repeats 4
python3 scripts/ask_claude.py experiment --split dev --prompt prompts/v1_baseline.md
sh scripts/action_surfaces.sh
```

A live run against the committed `state/seen_ids.json` reports postings that are new since
2026-11-01 18:58 UTC, and it updates that state file.

## What ran (all 2026-11-01)

| What | Evidence | Result |
|---|---|---|
| Tests | `tests/test_contract.py` | 14/14 pass, including both wrong versions caught |
| **Run 1, live baseline** | `evidence/raw/anthropic-20261101T185817Z.json` (674 postings), `state/seen_ids.json`, `results/run1-live-baseline.txt` | 674 seen, **0 reported new** |
| **SEEDED run 1** | `evidence/seeded/anthropic-SEEDED-before-2026-10-29.json`, built by `scripts/make_seeded_snapshot.py` from the real response by dropping postings first published on or after Oct 29 | 654 seen, 0 new (baseline) |
| **SEEDED run 2** | the real run-1 response, against the seeded state, `state/seeded_seen_ids.json`, `results/seeded-run2.txt` | **20 new**, each with both verdicts: the rule says 1 relevant ("Data Engineer"); Claude says 0 relevant (it called "Data Engineer" not_relevant, citing 5+ years preferred and a GTM/Salesforce data stack); 0 rejected |
| Sampling | `SAMPLING-REPORT.md`, `results/sampling/calls.jsonl` | 5 postings × 4 fresh calls: 20/20 modal, 3/5 match hand label |
| Prompt experiment | `PROMPT-EXPERIMENT.md`, `labels/`, `prompts/`, `results/experiment/` | held-out: rule 8/10, v1 2/10, v2 3/10 |
| Action surfaces | `ACTION-SURFACES.md`, `results/action-surfaces/` | agent-written state held 84/674 ids |

The second run is **seeded, not a second calendar day.** Only one real fetch exists. The seeded
"earlier" response is the real one minus 20 postings. It cannot contain postings that closed
before Nov 1, so it is cleaner than a real day-earlier board would be.

Seeded run 2 was run again with `--claude` (19:36 UTC) after the experiment, so
`results/seeded-run2.txt` shows both judges side by side.
`results/seeded-run2-BEFORE-citation-fix.txt` is kept on purpose: it shows the citation gap that
led to the contract amendment.

## Design in one paragraph

`agent/watch.py` refuses any URL whose scheme isn't https or whose host isn't
`boards-api.greenhouse.io`. It makes one unauthenticated GET, saves the bytes before parsing them,
diffs ids against the state file (no state = baseline = nothing new), then judges each new posting.
`agent/rule.py` is the title + level rule from the contract. `agent/claude_judge.py` sends Claude
the posting and the résumé minus `personal` (no name, email or phone), in a fresh, tool-less CLI
conversation. It accepts only a bare JSON object with exactly four keys, whose cited résumé fields
must exist in the résumé. Anything else is stored as `rejected`, never as a verdict.

## Sign-off — Job-Search Agent 1

```text
Checked:      - the allow-list refuses other hosts, http, look-alike hosts, and the allowed host
                hidden in a query string (test_allow_list_refuses_other_hosts)
              - baseline reports none, the second run reports only unseen ids, and nothing is new
                twice (test_baseline_then_new_since_last, test_end_to_end_two_runs_from_files)
              - both wrong versions are caught (test_wrong_version_mispaired_labels,
                test_wrong_version_empty_justification)
              - the rule matches the contract's hand-worked examples; senior/staff never relevant
              - the validator rejects fences, prose, extra or missing keys, unknown verdicts,
                unknown fields; rejections are never verdicts
              - Claude never sees the persona's email or phone (test_prompt_hides_contact_details)
              - a non-@example.com or non-555 résumé is refused (test_refuses_non_fictional_resume)
              - every number in the three reports is recomputed by scripts/score.py from saved calls
How:          - the 20 hand labels: by hand (scripts/label.py), before any Claude verdict existed
              - the tests: written by Claude Code against CONTRACT.md, in the same session as the
                code (not before reading it)
              - the run-2 citation gap: found by reading seeded run 2's output, fixed, and pinned
                with test_no_keyword_always_cites_the_keyword_list
              - the tables: by recomputation (score.py)
Not checked:  - a real second calendar day: only one live fetch was made
              - Greenhouse pagination or partial responses: the code assumes one response holds
                every job (674 did here)
              - that Claude's 20 run-2 verdicts are right: they were validated, not hand-labelled
              - whether the hand labels follow the written labeling rule: about 7.5 s per label,
                and many disagree with it (PROMPT-EXPERIMENT.md)
              - any other board, persona, model, prompt beyond v1/v2, or day
              - Greenhouse's terms of use beyond the public API being documented for job boards
Not claiming: that any verdict says whether a job is worth Priya's time. The rule reads only
              titles; Claude's verdicts are judgments that disagreed with the hand labels 14/20
              (v1). v2 beating v1 is one posting per split, not evidence of a better prompt.
Signed or withheld: Signed: Saloni Mathure, 2026-11-01
```

## Driver's seat

| Part | Claude did | Saloni did | Why it stays hers | Where it shows |
|---|---|---|---|---|
| Scope | proposed the persona, rule, board and folder options | chose Priya Nair, "title + level", Greenhouse `anthropic`, `saloni-m` | the agent watches the jobs she decides to look at | session of 2026-11-01 (question answers); CONTRACT.md header |
| Contract | drafted keyword lists, wrong versions, failure sentence from her choices | the rule shape the contract is built on | the contract is what she will be held to | commit `f166f5d` (before any code) |
| Code, tests, runs, reports | wrote all of them and ran them | logged the CLI in so the Claude steps could run | — | commits JS1-2 … JS1-7 |
| Ground truth | built the label tool; did not label | labelled all 20 postings | only she can say what counts as relevant; a model grading itself proves nothing | `labels/hand_labels.csv`, timestamps 14:22:30–14:24:59 |
| Sign-off | drafted Checked / Not checked from the tests and runs | read it and signed ("sign it", 2026-11-01) | her name goes on it | the line above |
