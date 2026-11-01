# Job-Search Agent 1 — The Contract and the Watch

**Course:** INFO 7375 Prompt Engineering & Agentic AI (Prof. Nik Bear Brown), Northeastern University
**Student:** Rithika Sankar Rajeswari · **Assignment:** JS1 · **Runs dated:** 2026-10-31
**License:** MIT (code and documentation in this folder)

An agent that watches one public job board, reports only postings new since the last
run, and gives each new posting two separately labeled verdicts: a **record**
(a written rule anyone can recompute) and a **judgment** (Claude under a prompt contract,
validated). The résumé is a **fictional persona** (Priya Nair, from the Reallocation
Engine examples). No real personal data is in this folder.

## Language and toolchain
- **Python 3.11+**, standard library only (ran on Python 3.14, python.org installer, macOS).
  No third-party packages; nothing to install.
- **Claude Code CLI** v2.1.316 (Northeastern Claude Enterprise login), used only by
  the optional Claude steps (`--claude`, `tools/claude_trials.py`).
- git. On macOS with python.org Python, run `Install Certificates.command` once,
  or the HTTPS fetch fails with `CERTIFICATE_VERIFY_FAILED` (this happened to me;
  the agent saved nothing and stopped).

## Contents
| Path | What it is |
|---|---|
| `CONTRACT.md` | In / Out / Refuses / the rule / wrong versions / failure sentence, written before any code |
| `agent/` | `fetch.py` (allow-list, raw save, SHA-256), `resume.py` (persona validation), `state.py`, `rule.py`, `claude_judge.py` (prompt contract + validator), `check.py`, `run.py` (CLI) |
| `tests/` | 42 offline unit tests; `mutants.py` holds the contract's two wrong versions; fixtures are **constructed** and labeled so |
| `data/resume.example.json`, `data/target.example.json` | Fictional persona and her target roles/exclusion |
| `data/raw/` | Raw board responses, saved unchanged |
| `data/state.json` | Seen posting ids from the real live runs |
| `data/seeded/`, `data/seeded_action_surface/` | **SEEDED** earlier responses (real response minus documented postings) and their separate state files; `SEEDED_manifest.json` lists what was removed |
| `reports/runs/` | One `.md` + `.json` report per run |
| `reports/sampling/` | Sampling report (Chapter 1) and raw trials |
| `reports/prompt_experiment/` | Labeling rule, labels, prompts, results, post-hoc label audit (Chapter 2) |
| `reports/action_surface/` | Action-surface comparison and the three runs' replies (Chapter 3) |
| `tools/` | Seeding, label-sheet, labeling, and Claude-trial scripts |
| `SOURCES.md`, `FRICTIONAL.md` | Contributions and my work log |

## Commands (run from this folder)
```bash
# Tests: offline, no network, no Claude
python3 -m unittest discover -s tests -v

# Live run against the one allow-listed board (no state file = baseline)
python3 -m agent.run --board scaleai            # add --claude for Claude verdicts

# Reproduce the seeded second run offline, into a throwaway state file
python3 -m agent.run --from-raw data/seeded/earlier_SEEDED.json --state /tmp/js1_state.json
sleep 1 && python3 -m agent.run --from-raw data/raw/20261031T143632Z_scaleai.json --state /tmp/js1_state.json
```
`sleep 1` is needed: report files are named by the second, and the agent refuses to
overwrite an existing report. `tools/claude_trials.py` also refuses to overwrite
existing results, so re-running it needs the old result files moved first.

## What actually ran (2026-10-31, UTC; reports in `reports/runs/`)
| Time | Run | Result |
|---|---|---|
| 14:36:32 | **Live baseline**, `scaleai` | 170 postings, 0 new (baseline); raw SHA-256 `e1f22b59…` |
| 14:52:23 | Baseline on **SEEDED** earlier response | 163 postings, 0 new |
| 14:53:26 | **SEEDED second run** with `--claude` | 7 new (exactly the 7 ids in the manifest), 2 relevant by rule; 7 Claude judgments, 0 rejected |
| 17:29:30 | **Live second run** with `--claude` | 170 postings, 0 new; raw SHA-256 identical to 14:36, so the board did not change in ~3 h (why the seeded run exists) |
| 17:29:37, 17:30:34 | SEEDED runs for the action-surface comparison | 1 new posting (4720573005) |

Also run: 42 unit tests (OK, run by me); 20 sampling calls and 40 prompt-experiment
calls to `claude -p` (raw replies with timestamps in the `.jsonl` files).

## Results in brief
- **Two judges disagree in instructive ways.** On *Senior/Staff ML Research Scientist,
  Agents*, the rule said relevant (title has "machine learning", 2 skills matched) and
  Claude said not relevant (research role, publications). The rule's title gate is too
  broad and it has no seniority check.
- **Sampling:** Claude's verdicts were identical across 4 fresh runs for all 5 postings,
  and matched my labels 16/20. Repeatability is not correctness.
- **Prompt experiment:** as pre-registered, the baseline scored 9/10 dev and 10/10 held-out;
  the one-change revision scored 9/10 and 8/10. A prompt always answering "not relevant"
  scores 9/10 and 8/10. A **post-hoc audit** found one labeling error and one rule gap in
  my labels, which I verified in the raw posting text. After correction both prompts tie,
  and neither beats "always not relevant". Ten cases show very little.
- **Action surface:** I give network and write authority to deterministic code and give
  Claude only text-in/JSON-out with no tools.

## Honesty labels
- **SEEDED** runs use a real saved response with documented postings removed; they are
  not a real earlier fetch. The real live second run showed no change.
- **Constructed** fixtures (ids 9001–9006) exist only in tests.
- Every Claude response shown is one I actually got on 2026-10-31; raw replies are saved.
- Post-hoc rescoring in the prompt experiment is labeled post-hoc and is not the
  pre-registered result.

## Sign-off — Job-Search Agent 1

**Checked**
- A fresh copy of only the committed files (`git archive` of this folder into `/tmp`)
  ran the README commands: 42 tests OK; the seeded runs reproduced 0 new, then
  7 new / 2 relevant by rule, with the same SHA-256 hashes.
- Allow-list refuses other hosts, `http://`, and off-host redirects before any network
  call: `tests/test_fetch.py`. Persona validation rejects non-`@example.com` emails and
  non-555 phones without echoing them: `tests/test_resume.py`.
- Baseline reports zero new; a later run reports only unseen ids:
  `tests/test_state_and_run.py`, plus the real runs above. The seeded run's 7 new ids
  equal the 7 in `SEEDED_manifest.json` (compared by hand).
- Both contract wrong versions (misaligned labels, empty justification) are caught:
  `tests/test_mutants.py` shows the checker passes on the real code and fails on each mutant.
- The raw response was not modified: I recomputed its SHA-256 with `shasum -a 256`, and it
  matches the hash in every report that used it.
- Claude replies are validated: 0 of 68 rejected (7 seeded-run, 20 sampling, 40 experiment, 1 action-surface agent call). Three claims in Claude's reasons
  (graduation window, "4+ years required", "Ideal: 3+ years") I checked myself against
  the raw text: `reports/prompt_experiment/label_audit_evidence.txt`.

**How**
- By tests Claude Code wrote against my contract; I ran all 42 myself. I did not write
  tests before reading Claude's code. What I wrote first was the contract and its two
  wrong versions, which the tests encode.
- By hand: hand labels (with a condition-by-condition tool), the manifest comparison,
  and the label audit.
- By recomputation: SHA-256.
- With Claude's help: drafting the contract wording, reports, and scripts (see `SOURCES.md`).

**Not checked**
- I did not hand-recompute the rule's verdicts on real postings. Rule correctness rests
  on unit tests over constructed fixtures.
- Report filenames collide when two runs start in the same second. Observed twice; the
  agent refuses to overwrite, but the collision is not fixed.
- The Claude validator checks field-name prefixes only. It accepted
  `target.title_keywords`, a field that does not exist.
- The agent's rule ignores location, sponsorship, seniority, required-vs-preferred
  experience, and graduation windows. Whole-word matching means "clearances" does
  not trigger the "clearance" exclusion.
- I did not test other boards, other days, or Greenhouse response-format changes.
- `claude -p` does not expose sampling settings, so I cannot say what produced the
  stability I saw. On one borderline posting the same prompt gave different verdicts
  on different occasions.
- The cause of a macOS "Data Access Blocked" notice during the Claude Code file run.

**Not claiming**
- That the agent finds good jobs, or that Claude's verdicts are correct in general.
- That the prompt revision is better or worse. Ten held-out cases with one or two
  relevant postings cannot show that.
- That anything here generalizes beyond one board, one fictional persona, and one day.

**Signed or withheld:** Rithika Sankar Rajeswari, 2026-10-31

## Driver's seat
| Part of the task | Claude did | I did | Why it stays mine | Where the split shows |
|---|---|---|---|---|
| The contract | Drafted the wording from my decisions | Chose the persona (Priya over Aarav, after comparing all four), the board (Scale AI over Databricks), and the separate target file; reviewed and committed it before any code | It defines what "relevant" means, and I answer for every verdict | Commit `19d72c7` (contract) precedes `aeb018b` (code) |
| Building the agent | Wrote `agent/` and 42 tests in Claude Code | Ran the tests myself; declined the external `AGENTS.md` import; switched off auto mode | Claude's "all tests pass" is a claim until I run them | `aeb018b`; FRICTIONAL entries |
| Touching the internet | Told not to make network requests | Ran every live fetch myself | Network actions need a human decision | Build prompt; reports at 14:36 and 17:29 UTC |
| Labeling rule and labels | Proposed a starting rule; flagged labels that contradicted my rule | Changed the rule (2 years allowed, sponsorship, data-science roles, US location); labeled all 20 myself; re-checked flagged postings | The labels are the standard Claude is scored against | `LABELING_RULE.md` and its amendment; labels in `2b7d3ce`, corrected in `cb39cee` before any prompt ran |
| Believing Claude | Gave reasons citing posting requirements | Checked those claims in the raw text before accepting any | Fluent reasons are not evidence | `label_audit_evidence.txt`; commit `64194b7` |
| Applying for a job | Nothing; the agent never applies, emails, or logs in | Every application decision | A day of a person's life is not a model's call | `CONTRACT.md` "Refuses" |
