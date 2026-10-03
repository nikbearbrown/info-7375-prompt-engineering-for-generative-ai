---
owner: AtharvaHambir
term: 2026fa
component: reallocation-engine
status: RUNNABLE-SAMPLE   # sample run logged in logs/runs/2026fa-atharvahambir-1.md; no live run
promoted_to: null
---

# Daily data-role checker (OPT ending in ~90 days, needs H-1B)

## Executive summary

This is a small program an international master's student runs each morning to find entry-level data jobs worth applying to before their work authorization runs out. It reads the job boards of the companies the student chose, keeps only new postings that fit (data analyst / BI / analytics / data engineer titles, not senior, in the US, 0–3 years of experience), checks each against the public record of which companies have sponsored work visas, and works out whether the hiring process could finish in time. Each posting comes back as Apply, Consider, Skip, or "needs you first", with every number labeled by where it came from. It never guesses: a company with no visa record, or an employer whose E-Verify status nobody checked, is held for the person instead of scored.

Read this to run it. It works offline on sample data out of the box, as a fictional persona ("Atharva", in the repo's personas folder — first name only, every detail invented). It reads the real sponsorship data shipped with the repo; the sample job postings are invented.

---

## Run it

**Sample (offline, one command, from the repo root):**

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py --sample
```

Writes `out/sample/2026-10-01/daily-check.md` (for the person) and `daily-check.json` (for an agent) inside this folder, plus the scorer's own `role-scores.{json,md}`. Needs Python 3.10+ (standard library only) and Node 20+ (for the existing scorer). No network.

**Tests (offline, from a fixture, no network):**

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/test_daily_check.py
```

**Break attempts (the tests must catch each deliberately broken version):**

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/break_attempts.py
```

The mutants are listed in `fixtures/BROKEN-mutants.json` (one exact edit each); each is built in a temporary copy, so `daily_check.py` itself is never modified.

**For a real search (live board APIs):**

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py --candidate <your candidate.json> --targets <your targets.json> --out-dir <a folder>
```

Keep your real `candidate.json`, `targets.json` and the output folder in the repo's gitignored `private/` folder — the reports name the companies you are targeting. Run it once a day; the state file in the output folder is what makes "new since yesterday" work.

| Flag | What it does |
|---|---|
| `--boards-dir DIR` | read saved board responses instead of fetching (offline) |
| `--today YYYY-MM-DD` | run as if it were that day (reproducible runs) |
| `--fresh-state` | ignore the previous run — everything open counts as new |
| `--dry-run` | write the reports but don't update the state file |

Exit codes: `0` ran · `2` stopped at the intake gate (a missing or impossible input) · `3` the scorer failed · `4` no board could be read.

## Inputs

**`candidate.json`** — see `search/examples/atharva/daily-check.candidate.json` (the fictional persona the sample runs as). Every field is *your-input* and has no default; a missing one stops the run.

| Field | Meaning |
|---|---|
| `authorization` | read by the scorer to decide sponsorship matters, e.g. `"F-1 OPT — needs H-1B sponsorship"` |
| `visa.opt_end_date` | last day of OPT |
| `visa.unemployment_days_used`, `visa.unemployment_days_as_of` | days used so far, and the date that count is from (the run adds the days since, assuming still unemployed) |
| `visa.unemployment_limit_days` | e.g. 90 on initial OPT — confirm with your DSO |
| `visa.needs_e_verify_employer` | `true` if the next job must support a STEM extension — a DSO question |
| `visa.buffer_days` | how many days of slack you want before the deadline |
| `search.titles[]` | `phrase`, your `fit` for it (0–1), and the occupation code (`soc`) it maps to |
| `search.exclude_title_words`, `search.flag_title_words` | words that drop a title / flag it for a look |
| `search.max_years_experience` | e.g. 3 |

**`targets.json`** — see `fixtures/targets.sample.json`. `defaults.hiring_weeks`, then per company: `name`, `board` (a Greenhouse or Ashby link), `e_verify` (`{"enrolled": true|false|null, "source": "...", "checked_on": "..."}`), optional `hiring_weeks`, optional `csv_name` (the legal name in the sponsorship data when it differs, e.g. `NOTION LABS INC`), optional `sponsorship_override` (`{"tier": "Proven|Likely|Avoid", "source": "..."}`).

## What it reuses (and does not copy)

| Piece | Where |
|---|---|
| Board fetcher — Greenhouse + Ashby, host allow-list, no redirects | `.claude/skills/greenhouse-watch/scripts/greenhouse_watch.py` (imported, not modified) |
| Sponsorship history | `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` |
| Occupation wages (shown only; role quality weighs 0 in the scorer) | `data/bls/compact/soc_occupation_compact.csv` |
| The decision | `scripts/score/role-scorer.mjs`, run as a subprocess on the `roles.json` this program writes |

Network hosts, only in live mode, only through the reused fetcher: `boards-api.greenhouse.io`, `api.ashbyhq.com`.

## What it cannot tell you

A listed posting is open on the board, not necessarily being filled. H-1B counts are past filings (years not documented, at most 5 titles per company). A company with no record is *unknown*, not a non-sponsor. E-Verify status, hiring time and every immigration rule are your inputs. The title, location and experience filters are fixed text rules, so the report lists every target-title posting it dropped and why. Funding is not used: the SEC Form D samples shipped with the repo match none of these companies. Full list: the recipe, `recipes/cases/2026fa/atharvahambir-reallocation-engine.md`.
