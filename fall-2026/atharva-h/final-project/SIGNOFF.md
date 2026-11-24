# Sign-off — SIGNED : narrow

**Status:** signed by Atharva Hambir on 2026-11-23; decision: narrow. Ticked boxes are checks Atharva did personally on 2026-11-23. An earlier AI-assisted pass the same day is recorded separately in [evidence/assisted-checks-2026-11-23.md](evidence/assisted-checks-2026-11-23.md); a box beginning “I” is ticked only for what Atharva did personally.

## What I checked, and how — owner checklist

- [x] I read `CONTRACT.md` and `pre-mortem.md` and agree with them as written. 
- [x] I ran `python3 -m unittest discover -s tests -t .` myself and saw 43 tests pass.
- [x] I ran a question on the real database with a **recorded Claude reply** (`--adapter recorded --gate interactive`) and made my own approve / refuse / defer decision. Run id: `20261124T031329Z-4d8997` (D2, Boston): I **approved** the answer 40 after seeing the SQL and matching rows; the system stopped `approved_and_exported`. Saved copies: [evidence/owner-gate-approve-2026-11-23.json](evidence/owner-gate-approve-2026-11-23.json) (paths made relative) and [evidence/owner-gate-approve-2026-11-23-report.md](evidence/owner-gate-approve-2026-11-23-report.md).
- [x] I read the development and held-out results in `evals/results/` and compared at least 2 answers (D2 and H1) with their matching rows.
- [x] I reviewed `evals/PROMPT-CONTRACT-v2.md` against v1 and **accept / revise / reject** it: accept
- [x] I chose Q4's annual-wage meaning and Q6's BI-title meaning, or deliberately kept the existing definitions.
- [x] I independently recounted at least one answer from the workbook in Excel. Question, method, and result: D2 (Boston), a `COUNTIFS` formula on Certified, H-1B, titles containing "Data Analyst", Boston, MA: 40, matching SponsorSQL.

## Earlier AI-assisted pass (before my own checks)

| Check | Observed result | Scope |
|---|---|---|
| Contract and pre-mortem read | Read; no edits made | Technical reading, not owner agreement |
| Test suite | **43 tests passed** in 0.715 s | Ran in this assisted session, not a personal owner test run |
| Live CLI attempt | Run `20261124T024108Z-454e7c` stopped `budget_exhausted`: `claude CLI not found`; shell exit was 0 | Did not reach an answer view or human gate; the process exit alone does not show success |
| Recorded-reply gate exercise | Run `20261124T024133Z-f17861` displayed answer 40 and 40 matching rows, then `d` was entered; no report written | The program labels the stop `deferred_by_human`, but this was an assisted replay, not Atharva's personal gate decision |
| Results checked | D2: answer 40, 40 matching rows, all case numbers equal the independent key. H1: answer 564, 564 matching rows; first two rows inspected. | Two saved results; not all 15 |
| Excel check | Temporary `COUNTIFS` formula returned **40** for Boston; workbook closed without saving and checksum unchanged | Formula entered in this assisted session, not an owner hand recount |
| Contract v2 technical review | Whole-phrase title rule and explicit wage/title limits address several v1 failures; D8, H3 false `MISMATCH`, missing `value`/refusal types, and prior scoring before owner approval remain | **Recommend revise** before final acceptance; this is not Atharva's accept/reject decision |

The checklist's quoted command with a positional question failed because the CLI requires `--question`; a live model call also requires `--adapter claude-cli`. The corrected live attempt is recorded above.

## Not checked

- A working, authenticated **live Claude CLI** path and a live model answer reaching the gate.
- A recount of any answer other than Boston. Atharva's Excel recount covers only D2 and uses a substring title criterion.
- A new held-out set frozen **after** owner review of the contract. The current five held-out questions were already scored on v2 before owner approval.
- A stranger run by someone outside the build. The recorded clean-checkout run is not a stranger run.
- Whether these answers hold for a newer DOL release, for second worksites absent from the main file, or for every one of the 1,114 employer names in D6.
- A live-model attempt to issue unsafe SQL. Policy enforcement was checked with tests and scripted failure cases.

## What I am not claiming

- That SponsorSQL is accurate on arbitrary questions. The evaluation covers 10 development and 5 held-out questions on one file, using recorded Claude replies replayed through the system.
- That an LCA count says anything about a particular person's visa or an employer's present willingness to sponsor.
- That the assisted session's replayed gate deferral was my own gate decision.

## Decision — owner only

- [x] Signed — ship / narrow / defer / stop (circle one): narrow

Name: Atharva Hambir · Date: 11/23/2026
