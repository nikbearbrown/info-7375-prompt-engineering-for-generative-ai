# Sources and contributions

## What was used

- **The assignment brief:** `assignments/assignment-js1-the-contract-and-the-watch.md` in this repository, read 2026-10-28.
- **Course guides:** `prerequisites/frictional.md` and `prerequisites/github-submission.md` in this repository, read 2026-10-31.
- **The board:** Oscar Health's public Greenhouse board API, `https://boards-api.greenhouse.io/v1/boards/oscar/jobs?content=true`. It was fetched by the agent on 2026-10-28 and 2026-10-30, and by the way-C test agent on 2026-10-31. The responses are saved unchanged in `runs/raw/` and `experiments/action-surface/way-C-attempt2/written-outside-its-folder/`.
- **Experiment 2 board:** Klaviyo's public Greenhouse board, `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true`, fetched once through `jsagent/fetch.py` on 2026-10-31 and saved in `experiments/experiment-2/raw/`. Before that, Claude Code fetched 20 Greenhouse boards through the same code just to count rule-positives per board. Only the counts were looked at, and nothing was saved.
- **One extra fetch before the contract:** Claude Code fetched the same URL once with `curl` on 2026-10-28, before the contract existed, to see which fields the postings have. That response was not saved here and was not used for any run, label or result.
- **Tools:** Python 3.14.6 standard library; Claude Code CLI 2.1.312 with model `claude-opus-5-5`.
- **Persona:** fictional. Alex Morgan is defined in CONTRACT.md, with an `example.com` email and a 555 phone. No real résumé is in this folder.
- **Not used:** no code was copied from other students' folders. One classmate's JS1 folder was visible in the repository listing on 2026-10-28; only its file names were seen.

## What Shreyash wrote

| Part | Where |
|---|---|
| The contract (In, Out, Refuses, the rule, wrong versions, the failure sentence, the persona). Pasted into the session on 2026-10-28; Claude changed formatting only. | `CONTRACT.md` (commit `7c8f9e5`) |
| The labeling rule and the 20 hand labels, pasted 2026-10-31. Shreyash: "i read the 20 ads myself". | `labels/LABELING-RULE.md`, `labels/hand-labels.csv` (commit `b3faea5`) |
| The 20 Klaviyo labels for experiment 2 (verdict, failed conditions, reason), committed before any Claude call on them, and the labeling-review note | `experiments/experiment-2/hand-labels.csv` (commit `8e2c92b`), `FRICTIONAL.md` |
| The per-posting evidence notes, the review of the five disputed postings, and the two rule decisions, all after the experiment on 2026-10-31 | `labels/hand-labels.csv` `note` column, `labels/DISPUTED-POSTINGS-REVIEW.md` |
| Choices: Oscar as the board, Opus as the judge model, the interview route for the contract, and when to do run 2 | the session record; see the README driver's seat |
| The sign-off signature | `README.md` |

## What Claude Code contributed

| Part | Notes |
|---|---|
| `INTERPRETATIONS.md` | Claude's reading of the contract, with its choices marked. Shreyash decided the two open choices on 2026-10-31, after the experiment. |
| All code in `jsagent/`, `experiments/` and `labels/make_label_sheet.py` | written by Claude Code |
| All tests in `tests/`, including the wrong-version implementations | written by Claude Code from the contract, before the implementation |
| The persona JSON | transcribed from CONTRACT.md section 1 |
| Both prompt contracts | `baseline-v1` puts the contract's rule in verbatim; Claude wrote the frame and the output format. Claude chose the one change in `revision-1`. |
| Running everything | the live runs, all 73 judge calls and the 4 action-surface sessions, at Shreyash's request |
| Reports and docs | `README.md`, `experiments/*.md` and Claude's section of `FRICTIONAL.md` |
| Evidence clean-up | trimmed the CLI's local environment listing from the four `events.jsonl` files (each says so) |

## Claude output shown in this folder

Every Claude answer quoted in this folder is one Claude actually returned, on the date in its file. The full CLI output of every call is saved in `runs/claude-calls/`, `experiments/*/calls/` or `experiments/action-surface/*/events.jsonl`.
