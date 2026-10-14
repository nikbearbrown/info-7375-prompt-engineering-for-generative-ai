# Honesty audit — Readback pitch film

**My own check, not a toolkit gate.** Prepared 2026-10-14 by Claude Code. I (Aravind) decide every fix.

- **First pass:** master SHA-256 `4ed0aba1…f8e60e`, 181.92 s. It raised 10 flags.
- **Second pass, current:** master SHA-256 `18f0d50c…581c131c`, 182.46 s. Re-checked after my fixes for F3, F5, F8 and F9 (see "Resolution" at the end).

**Rule:** use past tense only for things that exist and can be shown; everything else is "will". Every number needs a source file. Every constructed item needs its label. Nothing may imply an affiliation with Google, Zoom, Microsoft or Anthropic.

**Status values:**
- `exists`: real and shown, with evidence.
- `will`: planned.
- `constructed`: illustration or mock-up.
- `framing`: a general statement, not a claim about this project.

## Narration (every sentence)

| ID | Sentence | Tense | claim_status | Evidence (path, date) or "will" | Flag |
|---|---|---|---|---|---|
| BIDEA.1 | Hi, I'm Aravind Ravi, and this pitch is read by a synthetic voice. | present | exists | `beat_sheet.json` voice `am_onyx` (Kokoro, local), 2026-10-14 | — |
| BIDEA.2 | When you own an AI feature, a judge model scores it against your rubric. | present | framing | none (general statement) | **F1** (low): unsourced generalization |
| BIDEA.3 | So the question isn't only whether my feature passes. | present | framing | — | — |
| BIDEA.4 | It's whether the judge reads my rubric the way I meant it. | present | framing | — | — |
| B01.1 | It's called Readback. | present | exists | `PROJECT-BRIEF.md` (working title) | — |
| B01.2 | It will show a product manager which clause … an AI judge reads differently than they meant. | future | will | will | — |
| B01.3 | When it's done, it will be a Python repository with a command-line tool, a case study …, and a log of judge agreement … | future | will | will | — |
| B02.1 | Why care? | question | — | — | — |
| B02.2 | If the judge misreads a clause, the scores look fine and the ship decision is wrong. | present (conditional) | framing | none | **F2** (low): unsourced generalization |
| B02.3 | I looked at two tools. | past | exists | `FRICTIONAL.md` alternative checks, 2026-10-14 | — |
| B02.4 | Maxim AI measures how well several judges agree with humans. | present (third party) | exists | `FRICTIONAL.md` Maxim AI entry, 2026-10-14 | — |
| B02.5 | Ork dot AI compares an evaluator with human labels, then rewrites its prompt. | present (third party) | exists | `FRICTIONAL.md` orq.ai entry, 2026-10-14 | — |
| B02.6 | As far as I could find in their docs on October fourteenth, neither says which clause caused the disagreement. | past / present, hedged | exists | `FRICTIONAL.md`, 2026-10-14 | — |
| B02.7 | Readback will, and it will ask the PM about that clause instead of rewriting it. | future | will | will | — |
| B03.1 | The reader is a hiring manager for AI product roles. | present | framing (target) | `PROJECT-BRIEF.md` Q3 | — |
| B03.2 | In the first minute, they'll open the README and see one table: … the question Readback will ask, my revision, and held-out agreement before and after. | future | will | will | F3 resolved (was "asked") |
| B03.3 | The end user is a PM with their own rubric. | present | framing (target) | `PROJECT-BRIEF.md` Q3 | — |
| B04.1 | What does it prove? | question | — | — | — |
| B04.2 | That I treat a rubric as a prompt contract, and verify instead of trust: my labels will be committed before any judge runs, so the git history proves the order. | present + future | will | will (labels not yet made; out of scope for this deadline) | **F4** (low): present "treat / verify / proves" frames a planned proof |
| B04.3 | That I'll evaluate per clause on held-out data, and ground claims in transcript lines. | future | will | will. The grounding clause exists: `case-study/constructed/rubric-v0.md` C2, 2026-10-14 | F5 resolved (was "I evaluate") |
| B04.4 | A reviewer could conclude I understand why judges need a human anchor. | conditional | will | — | — |
| B04.5 | Not that it works for every feature. | — | will | — | — |
| B04.6 | I'll test one. | future | will | will | — |
| B05.1 | In: the rubric module, and a case study on ten public AMI meetings, where teams role-play product design. | present | exists (sample) / will (module) | `case-study/data/sample/` (10 meetings, downloaded 2026-10-14) | — |
| B05.2 | Out: Readback will never rewrite a rubric itself. | future | will | will | — |
| B05.3 | It asks, and the PM decides. | present | will | will | **F6** (low): present tense for planned product behaviour |
| B05.4 | First: one rubric, three judges, and my labels, producing an agreement table. | — | will | will | — |
| B05.5 | You'll know it ran because its commit comes after my labels' commit. | future | will | will | — |
| B06.1 | What could sink it? | question | — | — | — |
| B06.2 | Overfitting: revising the rubric until the judges agree on the examples I tuned it on. | — | will | — | — |
| B06.3 | So I'll freeze a held-out set first, and report only held-out numbers. | future | will | will | — |
| B06.4 | And because judges can share blind spots, I'll compare same-model and cross-model judges, and report it either way. | future | will | will | — |
| B07.1 | Why this project? | question | — | — | — |
| B07.2 | It's a mix. | present | framing | — | — |
| B07.3 | New to me: eval design, judge and human agreement, and multi-model judging. | present | framing (self-assessment) | `PROJECT-BRIEF.md` Q7 | — |
| B07.4 | Already mine: writing product requirements, as a PM at LG Energy Solution Vertech, Tech for Dev and Koine Arth, though those documents are internal. | past (work history) | exists, **not shown** | none in the repo (internal, as stated) | **F7** (medium): the only existing-skill claim with no evidence a reviewer can open. Disclosed honestly; the brief's TODO about public Dalgo issues/specs is still open |
| B07.5 | From this course: my week one film verified every on-screen number, and I held my week two recipe at draft while to-do items were open. | past | exists | Week 1 `verify_numbers.py` + `FACTCHECK.md` (PR #8, open); Week 2 PR #23 body "Lifecycle stage: DRAFT … 3 typed TODOs are open" (open, not merged), checked 2026-10-14 | — |
| B07.6 | I think e-vals are becoming core to AI PM work, and I don't have an eval project yet. | present (opinion) | framing | none needed: stated as my view | F8 resolved (now my opinion, not a market claim) |
| B08.1 | What exists today, October fourteenth: ten AMI meetings, a constructed five-clause rubric, and the recap feature, my prompt, run once on each meeting with Claude Opus five point five. | present / past | exists | `case-study/data/sample/`; `case-study/constructed/rubric-v0.md`; `case-study/outputs/feature-run/*.json` (`claude-opus-5-5`, Claude Code 2.1.283, 2026-10-14) | — |
| B08.2 | Ten real outputs. | — | exists | `case-study/outputs/feature-run/` (10 files) | — |
| B08.3 | What will exist: my labels, the judges, and the agreement table. | future | will | will | — |
| B08.4 | Those numbers don't exist yet. | present (negative) | will | — | — |
| B08.5 | They will be measured. | future | will | will | — |
| BOUT.1 | Readback. | — | exists | — | — |
| BOUT.2 | A pitch by Aravind Ravi. | — | exists | — | — |

## On-screen claims and labels (checked on `gates/frames/*.png`, one frame per beat from the master)

| Beat | On screen | claim_status | Evidence or "will" | Flag |
|---|---|---|---|---|
| BIDEA | "Does the judge misread my rubric"; "Aravind Ravi · INFO 7375" | framing | — | — |
| B01 | rubric · AI judge · clause · repo; tag "CONSTRUCTED · illustration" | constructed | labelled | — |
| B02 | "Maxim AI" → "agreement"; "orq.ai" → "rewritten prompt"; Readback page + "?"; tag "names only, no logos · as far as I could find in their docs, 14 Oct 2026" | exists (checks) / will (Readback) | `FRICTIONAL.md`, 2026-10-14 | — |
| B03 | README window, table with **empty** cells, "per clause", "?", "PM"; tag "CONSTRUCTED mock-up · values will be measured" | constructed | labelled; no numbers shown | — |
| B04 | "prompt contract", "labels" → "judges" commit dots, anchor, "one feature"; tag "CONSTRUCTED · planned commit order" | constructed | labelled | — |
| B05 | "10 AMI meetings" (pages); rubric page with "CONSTRUCTED"; pen with strike; "3 judges · planned"; "planned" before the labels → report commit line; tag "AMI data · CC BY 4.0 · downloaded 14 Oct 2026" | exists (pages) / will (judges, commits) | `case-study/data/sample/` | F9 resolved: both plan elements now carry "planned" on screen (`gates/frames/B05.png`) |
| B06 | examples, held-out stack + padlock, "same model", "cross-model"; tag "CONSTRUCTED · planned method" | constructed | labelled | — |
| B07 | "new to me" (3 empty jars); "already mine": "internal", "PR #8 open", "PR #23 open, not merged"; tag "PR status as of 14 Oct 2026" | exists | PR #8 / PR #23, checked 2026-10-14 | — |
| B08 | "exists": 10 pages, rubric, excerpt card "Include a lock function so buttons can't be pressed by accident" · ES2007a recap; "will": grey outlines "labels · judges · table"; tag "real output · Claude Opus 5.5 · 14 Oct 2026 · grey = will" | exists / will | Excerpt is a verbatim substring of `case-study/outputs/feature-run/ES2007a.json` (asserted in `scenes.py`); model `claude-opus-5-5` | — |
| BOUT | "Readback." "Aravind Ravi · INFO 7375" (no mascot) | exists | — | — |

## Checks across the whole film

- **Numbers:** every number has a source file.
  - "ten" / "10" meetings: `case-study/data/sample/`.
  - "five-clause": `rubric-v0.md`.
  - "PR #8" / "PR #23": the PR links.
  - "14 Oct 2026": the dates of my checks and runs.
  - "Opus 5.5": the output JSON.
  - "3 judges" is a plan, labelled "planned" on screen.
  - No metric, score, user count or result appears anywhere.
- **Constructed items:** every constructed visual carries a CONSTRUCTED, "planned" or "will" label.
- **Affiliation:**
  - Google, Zoom and Microsoft: never named or shown.
  - Anthropic: the narration names "Claude Opus 5.5" only as the model the recap prompt ran on. No logo appears, and the Claude mascot was removed from the outro (toolkit patch). No Claude interface is shown: the composer and verdict cards are exempt.
  - **F10** (low): the toolkit's show-tell palette (cream stage, warm ink, terracotta) is Claude's brand palette. It isn't a logo, but it's your call whether that reads as house style or as association.
- **Instructor:** no instructor name, persona or credit in the narration, frames, outro, file metadata (ffprobe tags: encoder only) or sheet metadata. The only matches for the instructor's handle in the folder are the GitHub owner inside the PR URLs.

## Flags (for my decision)

| Flag | Severity | Where | Possible fix (not applied) |
|---|---|---|---|
| F3 | medium | B03.2 "the question Readback asked" | "the question Readback will ask" (re-voice B03) |
| F5 | medium | B04.3 "That I evaluate … and ground claims" | "That I'll evaluate … and ground claims …" (re-voice B04) |
| F7 | medium | B07.4 PM work history, no evidence | Link a public Dalgo issue/spec if one exists; otherwise keep the disclosure |
| F8 | medium | B07.6 "E-vals are becoming core to AI PM work" | Source it, or reword as my own reason ("I think evals are becoming…") |
| F9 | medium | B05 "3 judges" + commit line unlabelled as plan | Add a "plan" or "will" tag to that part of the frame (re-render B05) |
| F4, F6 | low | B04.2, B05.3 present-tense framing of planned behaviour | Optional: "will" |
| F1, F2 | low | BIDEA.2, B02.2 general statements | Optional: keep as framing |
| F10 | low | Claude-palette style | Keep, or say in the README that it's the toolkit's house style |

## Resolution (Aravind, 2026-10-14)

| Flag | Decision | Done |
|---|---|---|
| F3 | Fix as suggested | B03 re-voiced: "the question Readback will ask" |
| F5 | Fix as suggested | B04 re-voiced: "That I'll evaluate per clause …" |
| F8 | Reword as my own view | B07 re-voiced: "I think e-vals are becoming core to AI PM work …" |
| F9 | Add a plan tag | B05 re-rendered: "3 judges · planned" and "planned" before the commit line |
| F7 | Keep as disclosed | Unchanged. The narration says the documents are internal. |
| F1, F2, F4, F6, F10 | No decision requested (low) | Unchanged |

**Re-check after the fixes:**
- Whisper (`small.en`) hears all three re-voiced lines as written.
- Only B03, B04 and B07 changed length: 17.62 → 17.79 s, 20.46 → 20.54 s, 28.90 → 29.22 s.
- B03, B04, B05 and B07 were re-rendered; the old clips are in `_superseded/`.
- Every gate is clean again:
  - Gate A and Gate W: all 8 scenes (`gates/gateA-gateW-all-scenes.txt`).
  - Gate B: 0 errors, 0 warnings.
  - Gate V: 0 BLOCKER, 0 MAJOR.
  - Gate T: PASS.
  - Bookend check: PASS.
  - Factcheck: clean.
- Runtime: 182.46 s (3:02).
