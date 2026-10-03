# Daily data-role check — human card

**Audience:** the student who decides where their application hours go. Specifically: an international master's student targeting entry-level data roles, on OPT with about 90 days left, STEM degree, needing an H-1B sponsor that is also enrolled in E-Verify.
**Agent twin:** `recipes/cases/2026fa/atharvahambir-reallocation-engine.md`
**Chapters:** 7 (who sponsors), 8 (is the job real), 10 (the visa clock), 11 (the scorer that combines them).

## Purpose

Every morning, answer one question for the companies you picked: *which postings opened today that are worth tailoring an application for, and which aren't?* The answer must come from the companies' own job boards, the public sponsorship record, and your own dates. It must not come from a model's opinion. When the evidence isn't there, the tool says "needs you" instead of guessing.

## What it can verify

- A posting is **listed on the company's own board today**, and which postings have left the board since your last run.
- What the **public sponsorship data says** about a company: approvals, denials, approval rate, up to five sponsored titles. The company is matched by exact name, never a fuzzy guess.
- That the **timeline factor follows from your dates**. It names both clocks, your OPT end date and your unemployment allowance, and uses whichever runs out first.
- That the **existing scorer** made each Apply / Consider / Skip call, with its arithmetic saved.
- That **nothing without sponsorship evidence was scored**.

## What it cannot verify

- That a listed posting is **really being filled**. Listed ≠ hiring.
- That a sponsor on record will sponsor **this role, now**. The counts are past filings with undocumented years, and at most 5 titles per company.
- Anything about a company **with no record**. That is *unknown*, not "doesn't sponsor". Only about 1 in 20 companies in the data has H-1B history at all.
- That an exact name match is **the right company**. "Chime" matches CHIME INC (2 approvals), not CHIME FINANCIAL INC (580). The tool flags similar names; you decide.
- **E-Verify status, real hiring times, immigration rules.** Those are your inputs, and the rules are questions for your DSO.
- **Unusual wording** in titles, locations or experience requirements. The fixed text rules can misread it, so every target-title posting they dropped is listed with the reason.

## Dependencies

- Python 3.10+ (standard library only) and Node 20+ (for the existing scorer). No `.venv`, no network for the sample.
- Data shipped with the repo: `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`, `data/bls/compact/soc_occupation_compact.csv`.
- Reused code: the `greenhouse-watch` skill's fetcher and `scripts/score/role-scorer.mjs`.
- Your files: `candidate.json` (dates, limits, title phrases, fit values) and `targets.json` (companies, board links, E-Verify, hiring weeks). Keep the real ones in the gitignored `private/` folder.

## Annotated commands

Sample, offline. It runs as a fictional persona with made-up postings and the real sponsorship data. Expected: 6 Apply · 1 Consider · 2 Skip · 4 Needs you.

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py --sample
```

Tests (expected `OK`, 18 tests), then break attempts (expected: all 4 deliberately broken versions caught):

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/test_daily_check.py
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/break_attempts.py
```

Your real daily run. It reads the live boards. If a date or number you haven't filled in is missing, it stops with "fill it in; there is no default":

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py --candidate private/daily-check/candidate.json --targets private/daily-check/targets.json --out-dir private/daily-check/runs
```

## What it produces

- **`daily-check.md` — read this.** A short summary and your clock, then:
  - **Apply today**;
  - **Consider**;
  - **Needs you** (each row says exactly what to look up);
  - **Skipped**, with the reason;
  - **Network, don't apply**: sponsors with nothing open for you;
  - **Closed since last check**;
  - companies it couldn't check;
  - every posting it filtered out, so you can check the filters;
  - what it cannot tell you.

  Every value is tagged *(record)* or *(your-input)*. Nothing is tagged *(model-judgment)*, because no AI model is called.
- `daily-check.json` — the same run for an agent. The scorer's own `role-scores.md` shows the arithmetic behind each decision.

## Where it fits the 3-3-2 day

It takes over the *finding and first-pass research* inside the two research-and-apply hours. Apply rows go straight to tailoring. "Network, don't apply" rows go to the three networking hours. The project itself, tests and honest limits included, is evidence for the three credibility hours.

## Named failure modes (and who would miss them)

1. **Wrong company, confidently.** A company's everyday name matches a different legal entity in the data (CHIME INC instead of CHIME FINANCIAL INC), and the tier comes out wrong. *Hardest to catch for:* a student who sees a familiar name and a tier and stops reading. *Guard:* similar-name warning; set `csv_name`.
2. **"Unknown" read as "doesn't sponsor."** Most companies have no H-1B fields in the data, so treating silence as a no would drop real sponsors (Coinbase's row has no H-1B history). *Hardest to catch for:* anyone skimming a Skip list. *Guard:* those rows are held as "Needs you", never scored.
3. **The wrong clock.** The unemployment allowance can run out months before the OPT end date. The sample persona's runs out on 2026-12-17; their OPT ends 2027-03-15. *Hardest to catch for:* a student who only remembers their OPT date. *Guard:* both clocks named; the earlier one is the deadline.
4. **Sponsor, but no E-Verify.** An employer can sponsor H-1B yet be unable to support the STEM extension. *Hardest to catch for:* a student who checks only sponsorship. *Guard:* your E-Verify constraint is a gate; unchecked employers are held.
5. **A ghost on the board.** A posting can stay listed after the role is filled. *Hardest to catch for:* everyone, since the board looks identical. *Guard:* postings open more than 60 days are flagged; ask a contact.
6. **Experience misread.** "Bachelor's + 5 years or Master's + 3 years" contains both numbers. *Hardest to catch for:* a student who trusts the filter blindly. *Guard:* mixed statements are kept and flagged, and every drop shows the sentence that caused it.
