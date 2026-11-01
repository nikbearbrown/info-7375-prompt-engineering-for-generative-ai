# Job-Search Agent 1 — The Contract and the Watch

Arundhati K · INFO 7375 · Fall 2026 · contract: [CONTRACT.md](CONTRACT.md) (committed first, `122d4f1`, before any code)

One board (Stripe on Greenhouse), one fictional résumé (Rohan Desai), new postings only, every verdict justified,
two judges kept apart: a **record** from the written rule and a **model judgment** from Claude.

Commit hashes in these docs are the ones on GitHub. Before pushing, my commits were rebased onto classmates' newer
commits, which changed the hashes (author dates unchanged): contract e6008c3→`122d4f1`, code 0c55047→`bb8984b`,
labeling rule 41a33a4→`a496500`, dev results 55376c3→`dd89511`, held-out 684dad2→`9bf8c91`. Commit messages may
still quote the old hashes.

## Language and toolchain

- Python 3 standard library only (developed on Python 3.15.0, macOS). No packages to install.
- Claude Code CLI (`claude`, 2.1.283) for the Claude judge — optional; everything else runs offline or with
  one public GET. The judge calls `claude -p` with no tools, no settings, no MCP servers, from an empty temp dir.
- Network: only `boards-api.greenhouse.io` (allow-list in `jsagent/fetch.py`).

## Exact commands (from this folder)

```bash
python3 -m unittest discover -s tests -t .        # 45 tests, offline
python3 seed.py --published-before 2026-10-29     # live fetch + build the SEEDED earlier response
python3 run.py --from-file evidence/seeded/earlier-response-before-2026-10-29.json.gz   # run 1: baseline (seeded)
python3 run.py                                    # run 2: live fetch, reports postings new since run 1
python3 run.py --claude                           # same, plus a labeled Claude judgment per new posting
python3 experiments.py sample                     # sampling calls (needs `claude` logged in)
python3 experiments.py run --prompt prompts/revision.txt --set dev   # prompt experiment (see PROMPT-EXPERIMENT.md)
python3 experiments.py score                      # rebuild experiments/RESULTS.md from logs + labels
```

To re-run the watch from scratch, delete `state/seen_ids.json` first (the state file is what makes run 1 a baseline).

## What ran (2026-10-31)

| run | when (UTC) | source | postings | new | rule RELEVANT |
|---|---|---|---|---|---|
| seed source | 06:16:29 | live fetch → `evidence/raw/20261031T061629Z-live-seed-source.json.gz` | 746 | — | — |
| 1 — baseline, **SEEDED** | 06:16:32 | `evidence/seeded/earlier-response-before-2026-10-29.json.gz` (live response minus the 32 postings first published on/after 2026-10-29) | 714 | 0 (baseline) | — |
| 2 — live | 06:16:36 | live fetch → `evidence/raw/20261031T061636Z-live.json.gz` | 746 | 32 | 0 of 32 |
| 1′ — baseline, **SEEDED** (separate state file) | 06:36:07 | same seeded file | 714 | 0 (baseline) | — |
| 2′ — live **with `--claude`** | 06:36:08 | live fetch → `evidence/raw/20261031T063608Z-live.json.gz` | 746 | 32 | rule 0/32 · Claude 0/32 · agree 32/32 |

Reports: [`reports/`](reports/) · state files: [`state/seen_ids.json`](state/seen_ids.json) (runs 1–2),
[`state/seen_ids-with-claude.json`](state/seen_ids-with-claude.json) (runs 1′–2′, repeated with the Claude judge after I
logged in; same seeded baseline, a second live fetch). Claude's 32 replies: `reports/20261031T063608Z-claude-calls.jsonl`
— all passed the validator; none was rejected, so the validator's rejection path is tested only on constructed replies.
**Run 1 is seeded, not a second calendar day.** The 32 "new" postings are new relative to a constructed earlier
board, not relative to a board I observed earlier. Postings that closed before today are missing from the seeded
file too, so it only approximates the board as it was before 2026-10-29.

## How the rule reads a posting (CONTRACT §5 interpretations)

| condition | posting field | reading |
|---|---|---|
| role | `title` | whole words "software engineer", "software developer", "backend/back-end engineer", "full-stack/full stack/fullstack engineer" |
| level | `title` only | whole words "intern", "internship", "co-op", "new grad", "new graduate". "Internal" ≠ intern. **"Early Career" is not on the contract's list, so it fails.** |
| US location | `location.name` | whole-word US markers: US, USA, U.S., United States, San Francisco/SF, Seattle/SEA, New York/NYC, Chicago/CHI, Atlanta, WA/CA/NY/IL. "Remote", "AMER", "N/A" alone fail (cannot be verified). |
| skills | `content` (HTML removed) | ≥ 2 of the 10 contract skills, whole words, anywhere in the text; no required/preferred distinction. Aliases: Golang, Postgres, k8s, Amazon Web Services. "Go" counts only capitalised and not starting a sentence. |

A skill is cited only if Rohan's résumé lists it; each citation names the résumé field (`skills.languages[2]`)
and quotes the posting's `content`.

## Tests (CONTRACT §10 → test file)

| contract requirement | test |
|---|---|
| first-run baseline; new ids; no duplicate reports | `tests/test_watch.py` (`NewSinceLastTests`, `EndToEndTests`) |
| verdict ↔ posting id (wrong version 1) | `tests/test_wrong_versions.py::WrongVersion1MisPairing` — rotated verdicts, relabelled ids, missing/duplicated records |
| evidence-based justification (wrong version 2) | `tests/test_wrong_versions.py::WrongVersion2NoEvidence` — generic, one citation, invented quote, wrong résumé field, repeated skill |
| invalid Claude output rejected | `tests/test_claude_validator.py` — 13 constructed bad replies (constructed strings, not Claude output) |
| host allow-list; redirects | `tests/test_fetch.py` |
| judges kept separate and labeled | `tests/test_watch.py::EndToEndTests` |
| fictional résumé only | `tests/test_resume.py` |

Last run: `Ran 45 tests … OK` (2026-10-31).

## Sampling report · Prompt experiment · Action surfaces

- Sampling (Chapter 1): [SAMPLING-REPORT.md](SAMPLING-REPORT.md) — 20 calls; 4 of 5 postings 4/4 stable, the one
  US new-grad posting split 3 RELEVANT / 1 NOT.
- Prompt experiment (Chapter 2): [PROMPT-EXPERIMENT.md](PROMPT-EXPERIMENT.md) — baseline 9/10 dev, 7/10 held-out;
  revision 10/10 dev, 6/10 held-out.
- Action-surface comparison (Chapter 3): [ACTION-SURFACES.md](ACTION-SURFACES.md)
- [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md)

## Sign-off — Job-Search Agent 1

- **Checked:** I ran all 45 tests myself on October 31, and they passed. I also reviewed my 20 labels against the labeling rules and checked the decisions for consistency.
- **How:** Claude helped write the tests, but I ran them myself. I assigned the labels manually, and the pass rates were calculated using `experiments.py score`.
- **Not checked:**
  - I have not reviewed every available Stripe engineering posting.
  - I have not independently verified every classification against a human-reviewed answer.
  - I have not tested the workflow on a large dataset.
  - I have not established that the classifier works consistently across different job platforms.
  - I haven't tested the validator against an actual invalid Claude response. All 62 real responses passed, so the rejection behavior was only tested using sample inputs.
  - I haven't tested the workflow across two actual calendar days. The second run used an earlier seeded board to check whether previously processed postings were handled correctly.
  - Each held-out posting received only one Claude call per prompt, so the results may change if the same postings are tested again.
- **Not claiming:** I am not claiming that the classifier is completely accurate or production-ready based on the limited testing completed so far.
- **Signed or withheld:** Arundhati Kandelkar, October 31, 2026

### Driver's seat

| Claude handled | I handled |
|---|---|
| Generated classifications from the supplied job-posting text. | Defined the candidate profile and project requirements. |
| Returned results across the different testing surfaces. | Created the labeling rules and assigned reference labels. |
| Provided outputs for repeated sampling. | Reviewed results and identified inconsistencies. |
| Provided suggestions and feedback on the project. | Decided which suggestions to accept, modify or reject. |
| Helped identify issues in the classification process. | Made the final decisions and documented the results. |

_Added by Claude for the record (from the git history and SOURCES.md):_ Claude Code wrote all of the code and tests
(`jsagent/`, `run.py`, `seed.py`, `make_labeling_set.py`, `experiments.py`, `tests/`) in commit `bb8984b`, after the
contract was committed in `122d4f1`. The labeling rule (`a496500`) was committed before any label; held-out labels and
scores are in `9bf8c91`.
