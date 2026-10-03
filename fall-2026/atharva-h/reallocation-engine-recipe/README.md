# The Reallocation Engine — Recipe Design Assignment (Atharva H)

## Executive summary

This folder is my submission for the INFO 7375 assignment to design a recipe for *The Reallocation Engine*, plus a working prototype. The recipe is a **daily job-board check for an international master's student hunting entry-level data roles on post-completion OPT, with about 90 days left and an H-1B sponsor needed**. Each morning it reads the student's chosen companies' Greenhouse and Ashby boards. It keeps the new postings that fit, then checks whether each employer has a public visa-sponsorship record and meets the student's E-Verify requirement, and whether hiring could finish before either visa clock runs out. It returns Apply, Consider, Skip or "Needs you", with every number labeled by its source. It never guesses: missing evidence is handed back to the person.

**Claimed stage: RUNNABLE-SAMPLE.** The prototype runs on a fresh clone. One live run against a real board has been done; nothing is claimed beyond that.

---

## Layout

The folder mirrors the assignment's "Where your work goes" table. Every path inside is relative to the root of `nikbearbrown/the-reallocation-engine`.

| What | Path |
|---|---|
| Recipe + card | `recipes/cases/2026fa/atharvahambir-reallocation-engine.md`, `….card.md` |
| Prototype, tests, fixtures, break mutants | `scripts/contrib/2026fa/atharvahambir-reallocation-engine/` |
| Run-log entries | `logs/runs/2026fa-atharvahambir-1.md` (sample run), `logs/runs/2026fa-atharvahambir-2.md` (live worked run) |
| Change brief, justification, worked run, test report, sources, frictional log, saved output | `course/2026fa/submissions/atharvahambir/` |
| Fictional persona used by the sample and worked run | `search/examples/atharva/` (first name only; every detail invented) |

Start with: the [recipe](recipes/cases/2026fa/atharvahambir-reallocation-engine.md), the [card](recipes/cases/2026fa/atharvahambir-reallocation-engine.card.md), the [worked run](course/2026fa/submissions/atharvahambir/WORKED-RUN.md), the [test report](course/2026fa/submissions/atharvahambir/TEST-REPORT.md), the [domain justification](course/2026fa/submissions/atharvahambir/DOMAIN-JUSTIFICATION.md), [FRICTIONAL](course/2026fa/submissions/atharvahambir/FRICTIONAL.md), [SOURCES](course/2026fa/submissions/atharvahambir/SOURCES.md), and the [index of saved terminal output](course/2026fa/submissions/atharvahambir/runs/INDEX.md).

The same files are on branch `contrib/2026fa-atharvahambir-reallocation-engine` of my fork, `AtharvaHambir/the-reallocation-engine`, for the pull request to the engine repo; that PR commit is my commit of record.

## Run it

The prototype reads the engine's data and calls the engine's scorer, so it runs inside a clone of the engine at the commit it was built on (`015843d`). Needs Python 3.10+ and Node 20+. The sample and tests make no network calls.

```bash
git clone https://github.com/nikbearbrown/the-reallocation-engine.git
cd the-reallocation-engine
git checkout 015843d
cp -R <this folder>/recipes <this folder>/scripts <this folder>/logs <this folder>/course <this folder>/search .
npm install
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py --sample
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/test_daily_check.py
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/break_attempts.py
```

The sample should print `Apply 6 · Consider 1 · Skip 2 · Held for you 4`; the tests `OK` (18); the break attempts `all 4 mutants caught`. `npm run verify` additionally needs PyYAML for the engine's own manifest check (a fresh-clone issue in the engine, documented in the test report).
