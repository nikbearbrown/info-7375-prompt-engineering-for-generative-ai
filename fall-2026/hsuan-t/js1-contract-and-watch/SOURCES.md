# Sources

## What I used

| Source | Used for |
|---|---|
| Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | The board; both raw responses are in `evidence/raw/` |
| JSON Resume schema, https://jsonresume.org/schema/ | Format of the fictional résumé; `personas/aarav-patel.resume.json` validates against it |
| Fictional persona Aarav Patel, from the course's Reallocation Engine examples (`search/examples/aarav-patel/resume.example.json`) | Converted by hand to JSON Resume; email `@example.com`, phone 555 |
| Claude Code CLI (`claude -p`), model `claude-sonnet-5-5` | The Claude judge, sampling report, prompt experiment, action-surface comparison |
| Anthropic Python SDK `anthropic` 2.3.0 | Optional `--claude-via api` path |
| pytest 8.4.2 | Tests |
| Python 3.11 standard library | Everything else |

## What I wrote

- `CONTRACT.zh.md`: the contract, written by me in Chinese before any code (In, Out, Refuses, the rule and its checks 1–6, the wrong versions, the dated failure sentence). Commit a0d895e in my working repo (see `evidence/git-history.txt`).
- The labeling rule's six steps, the nice-to-have rule and the missing-location rule (`labels/LABELING_RULE.zh.md`).
- The hand labels in `labels/labels.csv`, including the one I corrected after the held-out run.
- The decisions recorded in `FRICTIONAL.md` and in the README's driver's seat table: the architecture standard, the Claude CLI instead of API credits, a missing location passes check 2, the prompt revision (option B and its example), the choice of the agent as the least autonomy that suffices, and the sign-off.

## What Claude contributed

Claude (Claude Code, Claude Opus) contributed, at my request and checked by me:

- **Contract:** the skeleton of guiding questions; unified field names and filled gaps after reviewing my draft (paths, hosts, `status` / `error_message`, the run summary, the wrong-version tests); the Examples, by running my rule on the saved 2026-10-29 data; writing my checks 4–6, the phrase list and Known limits out as rules; later edits for the Claude CLI, the missing-location rule and two validator examples; the English translation (`CONTRACT.md`).
- **Code:** all of `job_agent/`, `tests/`, and the scripts in `labels/` and `reports/`.
- **Inputs:** the conversion of the persona to JSON Resume and the profile file; the built-in `data/` word lists.
- **Labels:** typed up my labeling rule from my spoken list; picked the 20 postings and the dev / held-out split by fixed-seed scripts; suggested the 6 clear rejects (title not engineering, or location outside the US), which I checked; the English translation of the labeling rule.
- **Prompts:** `prompts/claude_judge.v1.md`, and `v2` from the change I chose.
- **Reports:** ran every Claude call and drafted all three reports; the conclusions and decisions in them are mine.
- **README:** drafted, including the sign-off wording; I decided what is checked, not checked and claimed, and signed.
