# Label sets and what each may be used for (Claude Code, 2026-11-25)

Drafted by Claude Code from Ashwin's instructions in chat on 2026-11-25. Kept here so the README and CHANGE.md can
state exactly which labels touched which decision.

## The label files

| File | Who made it | Use |
|---|---|---|
| `labels/heldout-sheet.csv` | Ashwin, blind (committed alone at `9757ee7b`: Y 7, N 19, ? 4). Ashwin confirmed in chat on 2026-11-25 that these are their own judgments | Held-out measurement of one frozen change; **potentially contaminated** (see below) |
| `labels/audit-sheet.csv` | Ashwin's personal verdicts for all 47 minimum-sample rows, confirmed in chat on 2026-11-25 after seeing the AI suggestions and filter results (not blind; recorded in `7e5c3d02`) | The only verdicts `--report` reads |
| `labels/audit-ai-draft.csv` | Codex, inferred from Ashwin's 30 held-out labels | Proposals only; not read by code |
| `labels/audit-ai-assisted.csv` | 47 Codex suggestions inferred from Ashwin's held-out labels, supplied by Ashwin in chat in batches 1–5 on 2026-11-25. Ashwin states they are not independent hand judgments. 46 match the draft; row 35 differs (draft Y, supplied ?) | Exploratory only: `python3 -m jobfilter.audit --exploratory` writes `audit/EXPLORATORY-v1.0-ai-assisted.md` |

## Correction of earlier commits

Commits `e5828b69`, `78fcdc42`, `f6e68c43`, `683e8cf0` and `7eb48860` wrote these 47 verdicts into
`labels/audit-sheet.csv`. Their subjects say "Ashwin's audit verdicts", and their notes say "Ashwin in chat … after the
review cards". `54cecbe8` then generated `audit/REPORT-v1.0.md` from them as hand verdicts.

Both are wrong. On 2026-11-25 Ashwin said in chat that all 47 were Codex suggestions based on the held-out labels.
The correcting commit moves the verdicts to `labels/audit-ai-assisted.csv`, blanks `audit-sheet.csv` again, and
replaces the report with the exploratory one. The earlier commits stay in history; this note is the correction.

## The human-audit requirement that is still unmet

The brief (Step 2.1, graded 12 points) asks for these to be judged by hand:

- at least 30 random rejects;
- the closest calls near the threshold;
- a sample of what was kept.

`jobfilter/audit_batches.py` takes those four strata unchanged from the saved selection (seed 20261126):
random_reject 30, close_below 6, close_at 5 and kept_random 6. That is 47 distinct postings, with blind review cards in
`labels/audit-review-cards.md`.

**Status, updated 2026-11-25 after `7e5c3d02`.** Ashwin confirmed a personal review of all 47 rows and kept the
suggested verdicts. That review came after Ashwin had seen Codex's suggestions and the filter's results, so it was
**not blind**. `audit/REPORT-v1.0.md` reports these verdicts, with that exposure recorded on every row.

Until then this section read "0 of 47 have an independent hand verdict". That was true when it was written: the
sheet was blank between `b03e6b29` and `7e5c3d02`.

The other two strata, `exclusion_check` (8) and `review` (7), are optional. If they stay unjudged, the FILTER.md
section 10 row "level-II and forward-deployed exclusions kept" stays **not measured**.

Ashwin's clearance rule: if a posting needs a clearance and Supriya's eligibility is unknown, the verdict is `?`.
Willingness to get a clearance is not eligibility. `data/supriya-sharma.resume.json` says nothing about citizenship
or clearance.

## Why the original 30-posting held-out comparison is potentially contaminated

- Codex's audit suggestions were inferred from the 30 held-out labels. Any rule change chosen from this audit
  therefore rests partly on held-out labels.
- Claude Code printed the 30 held-out labels in this session while validating the sheet (2026-11-25, before commit
  `9757ee7b`), so it has seen them. The held-out titles include a "Software Engineer - Mission Manager" posting.
  The title-rule fix under discussion would therefore be chosen by a session that knows a held-out label it would
  change.

If we tune from this audit, CHANGE.md must:

- call the 30-posting comparison **potentially contaminated**, not held out or untouched;
- say that the original held-out labels informed the AI-assisted verdicts behind the change;
- report it as a development-style check only.

## A genuinely unused evaluation sample

**Candidate:** `../js1-contract-and-watch/snapshots/cloudflare-2026-10-29T23-55-50Z.json`, a JS1 snapshot of the
Cloudflare board with 463 postings, plus its `.headers.txt` saved for provenance.

What has touched it so far:

- **The JS3 corpus:** no key overlaps the 805 postings (checked 2026-11-25).
- **JS1:** its README lists the snapshot as unused, and none of the five JS1 sampling postings come from it.
- **Claude Code, this session:** opened it only to count postings and compare IDs. It printed no titles, text or
  labels.
- **Filter v1.0, the Codex draft and every label sheet:** none has read it.
- **Ashwin and Codex:** Ashwin saw the board during JS1, before switching boards. On 2026-11-25 Ashwin relayed that
  Codex did not read the snapshot during this chat's work. Whether other chats read it is unverified.
- **Claude Code, for the Mission Manager question:** counted titles containing "mission manager" (0) and "manager"
  (70). It printed no titles. See `audit/FALSE-FRIENDS.md`.

What would make it a clean evaluation:

1. Freeze the one change first, as `filters/v1.1.json` with a commit.
2. Draw a random sample of the snapshot with a seed recorded before the draw, and seal the keys.
3. Ashwin labels it blind, by hand. AI-suggested labels would not give a clean human-labeled measurement.
4. Only then run v1.0 and the frozen v1.1 on it, once.

**Caveat:** it is a different employer, so it measures how the filter transfers, not how it does on the
development boards.

The other option is a fresh fetch of the same five boards, keeping only keys outside the 805. It would match the
development mix, but it needs a live fetch and the same blind hand labeling. The choice is Ashwin's.

**For the narrow Mission Manager fix specifically:** the Cloudflare sample cannot evaluate it. No Cloudflare title
contains the phrase, so both versions would make the same decision on every posting there.
