# Job-Search Agent 1 — The Contract and the Watch

**Om Raut** · INFO 7375, Fall 2026 · Job-Search Agent 1 (Chapters 1–3) ·
GitHub folder: `fall-2026/om-r/js1-contract-and-watch/`

An agent that watches one public job board (GitLab's Greenhouse board),
reports only postings new since the last run, and gives each one two
separately labeled verdicts. One is a **RECORD** from a hand-computable rule.
The other is a **JUDGMENT** from Claude under a strict prompt contract. The
persona is fictional (Priya Nair, `resume.json`).

## Language and toolchain

- **Python 3.11** (tested on 3.11.15). Standard library only for the agent
  itself: `urllib` for the board fetch, `unittest` for the tests.
- **Anthropic Python SDK** `anthropic==0.39.0`, for the judgment step only
  (`requirements.txt`). The SDK uses `httpx` internally; the project does not
  import `httpx` or `requests` directly.
- No other dependencies.
- **Network hosts:** `boards-api.greenhouse.io` (allow-listed, the only host
  the agent fetches) and the Claude API (judgment calls).
- **Judgment model:** pinned to `claude-opus-5-5`, no fallback
  (CONTRACT.md, Toolchain).

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...      # only for the commands marked [key]
```

## Exact commands to reproduce everything, in order

These are the commands that produced this submission, in the order they
were run. Tags: **[offline]** no network and no key; **[live]** fetches the
board; **[key]** calls the Claude API (billed).

> **Run these in a scratch clone, not this folder.** Several commands
> write files: the watch writes evidence and state, the samplers add calls,
> and the worksheet generators overwrite the BLANK worksheets. Overwriting
> the BLANK worksheets resets the file timestamps that serve as timing
> evidence. Where a command would otherwise change committed state, a
> scratch path is shown.

**0. The contract (written first, by hand).** `CONTRACT.md`. No command.

**1. Test-first: the wrong-version tests fail against a deliberately wrong
stub, then pass against the real rule.** [offline]
```
JS1_IMPL=agent.wrong_stub python3 -m unittest -v tests.test_wrong_versions   # logs/01: FAILED (failures=3)
python3 -m unittest -v tests.test_wrong_versions tests.test_justification     # logs/02: OK
```

**2. Watch baseline against the live board.** [live] The original run used the
default state file; a fresh reproduction uses scratch paths so the
committed state is untouched:
```
python3 -m agent.watch --board gitlab --resume resume.json                     # original: logs/run1_baseline.txt
python3 -m agent.watch --board gitlab --resume resume.json \
  --state /tmp/js1_state.json --evidence-dir /tmp/js1_evidence                 # reproduction: BASELINE, 0 new
```

**3. Seeded second run (constructed input, clearly labeled).** [offline] See
`evidence/seeded-run-note.md`. To reproduce, replay against a copy of the
baseline state:
```
python3 scripts/make_seeded.py                                                 # rebuilds the identical SEEDED file
cp state/gitlab_seen.json /tmp/js1_seeded_state.json
python3 -m agent.watch --board gitlab --resume resume.json \
  --from-file evidence/gitlab_jobs_SEEDED_20261030T201528Z_plus-one-fake-posting.json \
  --state /tmp/js1_seeded_state.json                                           # logs/run2_SEEDED.txt: exactly 1 new, RECORD relevant
```

**4. The judge: validator wrong-version tests, then compare RECORD vs JUDGMENT.**
```
JS1_JUDGE_IMPL=agent.wrong_validator_stub python3 -m unittest -v tests.test_judge  # [offline] logs/07: FAILED
python3 -m unittest discover -v -s tests -t .                                       # [offline] logs/09: 53 tests, OK
python3 -m agent.compare                                                            # [key] logs/compare_20261030T203314Z.json
```

**5. Sampling Report: 5 postings × 4 independent calls.**
```
python3 scripts/make_sampling_worksheet.py     # [offline] the seeded draw; overwrites the BLANK worksheet
python3 scripts/sample_judge.py                # [key] 20 calls; re-running ADDS calls 5+, never overwrites
python3 scripts/summarize_sampling.py          # [offline] logs/sampling_summary.md
```

**6. Prompt Experiment, dev set.**
```
python3 scripts/make_experiment_worksheets.py                                  # [offline] the seeded draw; overwrites both BLANK worksheets
python3 scripts/run_experiment.py --set dev --prompt judge-dev-v0             # [key]
python3 scripts/run_experiment.py --set dev --prompt judge-dev-v1             # [key]
python3 scripts/score_experiment.py --set dev --prompt judge-dev-v0           # [offline] 9/10
python3 scripts/score_experiment.py --set dev --prompt judge-dev-v1           # [offline] 9/10
```

**7. Prompt Experiment, held-out set (only at the end).**
```
python3 scripts/run_experiment.py --set heldout --prompt judge-dev-v0 --final  # [key]
python3 scripts/run_experiment.py --set heldout --prompt judge-dev-v1 --final  # [key]
python3 scripts/score_experiment.py --set heldout --prompt judge-dev-v0       # [offline] 10/10
python3 scripts/score_experiment.py --set heldout --prompt judge-dev-v1       # [offline] 10/10
```
The runner makes one call per posting per prompt and skips postings that
already have a saved call. In this folder it is therefore a no-op; to make
new calls, move `logs/experiment_raw/` aside in a scratch clone. Scoring
from the saved calls is fully reproducible offline.

**8. Action-Surface Comparison: the same posting three ways.**
```
# 1. paste: copy action_surface/paste_into_chat.txt into a fresh claude.ai chat (manual, no command)
# 2. file-read: a fresh Claude Code subagent read action_surface/posting_8730125002.txt (manual, no command)
python3 scripts/agent_fetch_one.py             # 3. agent-fetch [live][key]; writes evidence/ and state/action_surface_seen.json
```

## What actually ran vs. what's proposed

Everything above actually ran, on 2026-10-30. The real output is saved in
`logs/` and `evidence/`, and nothing in this submission is a `[TODO]` stub.
Three things are deliberately not what they might look like, and each is
labeled where it appears:

- `agent/wrong_stub.py` and `agent/wrong_validator_stub.py` are
  **deliberately wrong implementations**, kept only so the tests can be
  shown failing. The agent never imports them.
- The second run with a real change is **seeded**: one constructed posting
  was added to a saved real response (`evidence/seeded-run-note.md`). A
  later live fetch (22:31:55Z, Action-Surface step) did see a real board
  change: one posting removed, 238 → 237. The watch reports only new ids,
  so it did not report that removal; the change was found by comparing
  evidence files by hand.
- The paste-into-chat reply's model and time were **not recorded**, and
  are left as unknown (ACTION-SURFACE.md).

## Files in this submission

| Path | What it is |
|---|---|
| `CONTRACT.md` | The spec, written before any code |
| `agent/` | `rule.py` (RECORD), `fetch.py` (allow-list), `watch.py`, `judge.py` (JUDGMENT), `compare.py`, and the two deliberately wrong stubs |
| `tests/` | 53 `unittest` tests |
| `scripts/` | The seeded-run builder, the samplers, the experiment runner/scorer, the agent-fetch script |
| `resume.json` | The fictional persona |
| `requirements.txt` | `anthropic==0.39.0` |
| `evidence/` | Raw board responses (baseline, re-run, seeded, later live fetch) and the seeded-run note |
| `state/` | Seen-id state files (live baseline, seeded copy, action-surface run) |
| `logs/` | Test runs, watch runs, compare runs, hand labels, every raw Claude call, scored results |
| `action_surface/` | The paste text and the posting file used in the comparison |
| `SAMPLING-REPORT.md` | Chapter 1 artifact |
| `PROMPT-EXPERIMENT.md` | Chapter 2 artifact |
| `ACTION-SURFACE.md` | Chapter 3 artifact |
| `FRICTIONAL.md` | The honest log, including corrections |
| `SOURCES.md` | What I used, what I wrote, what Claude contributed |

## Sign-off — Job-Search Agent 1

```text
Checked:      The relevance rule against the two deliberately wrong versions;
              refusal of board hosts outside the allow-list; baseline behavior
              and reporting only unseen IDs on the next run; and rejection
              of invalid judgment output. I also read the postings and wrote
              the hand labels, and reviewed the seeded posting used to test
              the second run.
How:          The code checks used tests Claude wrote before implementing
              the relevant behavior. I specified the contract's two wrong
              versions and required failing-then-passing evidence. I did
              not write the test files. The recorded runs show the tests
              failing against the wrong implementations and passing against
              the real ones; the recorded full suite reports 53 passing
              tests. The hand labels were my own reading and judgment.
              The second-run example used a seeded posting, so it checks
              that controlled case rather than a naturally occurring change.
              This sign-off's wording was drafted with ChatGPT's help; the
              checks, limits, and decision to sign are my own.
Not checked:  Concurrent runs writing to the same state file; restriction of
              the Claude API host if ANTHROPIC_BASE_URL is changed; detection
              of removed postings; and enforcement of the file-read boundary
              beyond the instructions given to the model. The paste reply's
              model and exact time were not recorded either.
Not claiming: This does not prove the agent finds every suitable job or that
              its judgments are correct just because they repeat. It does
              not establish broad prompt reliability from these small
              samples. The held-out leakage limits the experiment, and
              AI-work relevance is different from fit for Priya's résumé.
              I am not claiming a security audit or production readiness.
Signed or withheld: Signed — Om Raut, 2026-10-31, for the checks and limits
              stated above.
```

## Driver's seat

| Task | Claude did | Om did | Why that part stayed mine | Evidence |
|---|---|---|---|---|
| CONTRACT.md | Implemented against it. Added one dated line, the model pin, on my instruction. | Wrote the contract before any code: inputs, outputs, refusals, the rule, the two wrong versions, and the dated failure case. | I needed to decide what I was asking the agent to do before seeing an implementation. Otherwise, I could end up accepting behavior just because it was what Claude produced. | The session's first listing showed only CONTRACT.md at 16:11 EDT. The added line is marked 2026-10-30. Its timestamp changed with that edit. |
| The relevance rule | Implemented the whole-word rule with a threshold of at least two of six terms. Found the "LLMs" plural gap during the board-wide check. | Specified the rule and decided to leave it unchanged after the gap was found. | I wanted to test the rule I had actually chosen. Quietly changing it after seeing a miss would hide a useful failure. | agent/rule.py; FRICTIONAL.md, whole-word matching note. |
| Wrong-version tests | Wrote both tests and the deliberately wrong stub, test-first. | Specified the two wrong versions in the contract and required evidence that the tests failed on them before passing on the real rule. I did not write the test files. | I needed to decide which mistakes mattered. Claude could write the checks, but I still had to make sure they tested the failures I cared about. | tests/test_wrong_versions.py at 20:14:00Z; agent/wrong_stub.py at 20:14:07Z; logs/00-02. |
| The allow-list | Wrote the fetcher, redirect guard, token check, and tests. Found that the endpoint returned no content and proposed ?content=true. | Named the board and allowed host, then approved the query change needed to retrieve posting content. | The destination was my scope decision. A problem with the response was a reason to adjust the request, not give the agent unrestricted access. | agent/fetch.py; tests/test_watch.py::AllowList; FRICTIONAL.md, endpoint-content note. |
| Sampling Report finding | Built the draw, runner, and summary. Drafted the report and softened claims that went beyond the data. | Ran the 20 calls. Composed the five labels and the labeling rule in a chat conversation with Claude, used as a drafting and thinking tool (see SAMPLING-REPORT.md and FRICTIONAL.md's hand-label note) -- this is different from the Prompt Experiment's 20 labels, which I wrote entirely on my own, no AI help. I directed the framing of the disagreement. | I needed to decide what the disagreement meant without treating my label as unquestionable. Consistent answers can still miss something, and agreement does not settle correctness. | SAMPLING-REPORT.md; logs/sampling_raw/; the final sampling labels file. |
| Prompt experiment design | Implemented both prompts, the scorer, and the held-out guard. Checked that v1 differed from v0 by one sentence. Reported the scores and declined to claim leakage had no effect. | Set the scope, wrote the one-sentence revision, chose its target posting, labeled all 20 dev and held-out postings myself without AI help, and ran all 40 calls. | I needed to choose the change and what it was supposed to test. I also had to accept the limits of the result, including leakage, rather than explain away an inconvenient weakness. | PROMPT-EXPERIMENT.md; logs/experiment_*_labels.md; logs/experiment_raw/. |
| Labeling corrections | Preserved the original dev labels file, logged corrections, and flagged an unverifiable precedent claim. | Stated that the dev-set labels file's claim of ChatGPT assistance was incorrect -- no AI help was actually used for the 20 Prompt Experiment labels (dev or held-out) -- and ordered the correction and the later trim. This correction concerns only the Prompt Experiment's dev-label file header; it does not affect the Sampling Report's labels, which remain correctly documented elsewhere as composed with Claude's help in chat. | I needed to keep the record accurate about which labels were actually used and who wrote them. | FRICTIONAL.md, correction entry; logs/experiment_dev_labels.ORIGINAL_20261030T212343Z.md. |
| Action-surface comparison | Ran and validated the file-read surface, wrote agent_fetch_one.py and the comparison, and identified removal-detection and refusal-test gaps. | Chose the posting, ran the paste in claude.ai and the live agent fetch, noticed the count changing from 238 to 237, and left the unrecorded paste model and time unknown. | I needed to decide what was being compared and notice what the successful runs did not establish. Making up the missing model or time would make the comparison look stronger than it was. | ACTION-SURFACE.md; logs/action_surface/. |
| This sign-off | Drafted the skeleton and evidence hints. | Supplied my account of the work and used ChatGPT to help phrase this draft. The checks I stand behind, the limits I accept, and the decision to sign are mine. | My name is on it. I need to understand what the evidence supports and what it leaves open, even when someone else wrote the code or helped with the wording. | This file; my clarification in this chat; the final README. |
