# SponsorSQL — a supervised agent for public H-1B filing data

**Atharva Hambir · INFO 7375 Final Project · Fall 2026**
Language: **Python 3** (standard library only) · Database: **SQLite** (bundled with Python) · Model: **Claude** (Claude Code)

## What it is

You ask a plain-English question about the U.S. Department of Labor's public **LCA** (Labor Condition Application) disclosure file, for example *"How many certified H-1B Data Analyst cases have a recorded worksite in Boston, MA?"* SponsorSQL then:
1. refuses questions it must never answer: contact details, immigration predictions, requests to change data
2. asks Claude for one SQL query plus a second query that lists the rows behind the answer
3. checks both against a read-only permission policy enforced in code, and runs them under time budgets
4. shows you the answer, the SQL, and the matching public rows, so you can see how the number was produced, and check it
5. stops at a **human gate**: you approve, refuse or defer. Only an approval bound to the exact view you saw writes a report.

An LCA filing is not a job offer, a visa approval, or a promise of sponsorship. SponsorSQL never says otherwise.

**Changed since the October pitch:** SQLite instead of DuckDB (no downloads); an automated independent answer key instead of a hand count; a working agent loop with an enforced policy and a human gate. Details in [brief.md](brief.md).

## Results (2026-11-21)

| Evaluation | Result |
|---|---|
| Development, contract v1 | 4/10, failing as predicted in [pre-mortem.md](pre-mortem.md) |
| Development, contract v2 | **9/10** |
| Held-out (frozen first, scored once) | **5/5** |
| Unsafe SQL executed | 0. No model reply attempted unsafe SQL, so this number isn't evidence by itself; the policy is evidenced by tests and failure cases F1–F4. |
| Deliberate failure cases | **10/10** behaved as predicted |
| Controlled failure | A replication of the October draft's failure: triggered on purpose, caught by the independent key, recovered (owner review pending) |
| Independent review | 18 findings, none judged a false positive. 9 led to code changes (some only partial), and 9 are acknowledged in the docs. Re-scoring with stricter comparators left 4/10, 9/10 and 5/5 unchanged. [audit-note.md](audit-note.md) |

**Important limits:**
- **Contract v2 was used for scoring before the owner reviewed it**, so the held-out set is spent on an unapproved contract.
- The answer keys share their definitions with the system, so the scores measure how well Claude turns the stated rules into SQL, not correctness against an outside source.
- The model replies were real Claude output from separate Claude Code subagents, saved word for word and **replayed**. The live `claude -p` path was not run (CLI not logged in). Full detail, including what this can't show: [evidence.md](evidence.md) and [evals/FAILURE-LOG.md](evals/FAILURE-LOG.md).

## Run it

```bash
cd fall-2026/atharva-h/final-project
python3 -m unittest discover -s tests -t .          # 43 tests, no data needed
```

With the real data (a 252 MB public download, then about 70 s to load):

```bash
curl -L -o data/LCA_Disclosure_Data_FY2026_Q3.xlsx "https://www.dol.gov//media/LCA_Disclosure_Data_FY2026_Q3.xlsx"
shasum -a 256 data/LCA_Disclosure_Data_FY2026_Q3.xlsx   # f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3
python3 -m sponsorsql load data/LCA_Disclosure_Data_FY2026_Q3.xlsx data/fy2026q3.sqlite
python3 -m sponsorsql evaluate --db data/fy2026q3.sqlite --set evals/heldout-questions.json \
  --responses evals/proposals/heldout-responses.json --contract evals/PROMPT-CONTRACT-v2.md --out /tmp/heldout.json
python3 -m sponsorsql failures --db data/fy2026q3.sqlite --out /tmp/failures.json
```

### See the human gate

```bash
python3 -m sponsorsql ask --db data/fy2026q3.sqlite --qid D2 \
  --question "How many certified H-1B Data Analyst cases have a recorded worksite in Boston, MA?" \
  --responses evals/proposals/round2-dev-responses.json --gate interactive
```

You'll see the answer (40), the SQL, the matching rows and the view's SHA-256, then `Approve, refuse, or defer this answer? [a/r/d]`.

Every command, the toolchain, and where each agentic part lives in the code: [artifact.md](artifact.md).

## The packet (ten documents, in order)

1. [brief.md](brief.md): the need, owner, success, what it is not for
2. [data-boundary.md](data-boundary.md): every source, labelled, with retention
3. [action-surface-map.md](action-surface-map.md): read, write, send, and the authority each needs
4. [plan.md](plan.md): steps, evidence on each edge, stop and refusal paths
5. [gates.md](gates.md): human approvals bound to what the approver saw
6. [pre-mortem.md](pre-mortem.md): the predicted failure, written before the code
7. [evidence.md](evidence.md): commands and results, by kind of evidence
8. [artifact.md](artifact.md): the system and how to run it
9. [audit-note.md](audit-note.md): predictions, reviewer findings, failed cases, Gap Account
10. [transfer-reflection.md](transfer-reflection.md): the decision (owner)

Course devices: [CONTRACT.md](CONTRACT.md) (the gate: contract and tests before code) · [SIGNOFF.md](SIGNOFF.md) (the sign-off, **not signed yet**) · [DRIVERS-SEAT.md](DRIVERS-SEAT.md) (the driver's seat) · [STRANGER-RUN.md](STRANGER-RUN.md) · [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md)

## What ran, and what did not

- **Ran:**
  - the tests
  - the load
  - both answer keys
  - three evaluation runs on recorded Claude replies
  - ten deliberate failure cases
  - the controlled failure
  - a clean-checkout run (see [STRANGER-RUN.md](STRANGER-RUN.md))
- **Did not run:**
  - a live `claude -p` call from inside the loop
  - a real human gate decision
  - a stranger run by another person
  - a hand recount of the keys from the workbook

## The demo

- **File:** `atharva-sponsorsql-final.mp4`, 3 min 54 s
- **SHA-256:** `1112de3c041398fc540cc719420a37ea24813b400cb40b37faf25a40d87e143e`
- **Link:** *to be added by the owner after uploading*

The film follows the four parts in order (executive summary, introduction, methods, evaluation). It shows real output, including a real run and the human gate prompt. Its sources, per-claim fact check and quality-gate reports are in [film/](film/README.md). MP4s are kept out of GitHub.

## Folder map

`sponsorsql/` the agent · `tests/` 43 tests · `evals/` questions, keys, contracts, recorded replies, results · `evidence/` raw command output · `data/` local data (not committed)
