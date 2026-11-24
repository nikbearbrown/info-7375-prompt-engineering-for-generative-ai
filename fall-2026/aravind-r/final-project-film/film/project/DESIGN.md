# DESIGN — Readback project film (Phase 2 storyboard, 2026-11-23)

**Status:** the storyboard was approved on 2026-11-23 (Phase 2). The narration was voiced early (Kokoro `am_onyx`, from the approved script) only to time the scenes: 20 clips, 232.43 s with holds (3:52, cap 4:00).

**Phase 3 updates:**
- Real-evidence cards moved to the deeper kraft to pass Gate V's contrast check. The tool nodes are 0.4 shorter.
- The planned grid cells are dashed outlines only.
- Every static window got a meaningful change (see Motion). The storyboard images show the Phase 2 state.

**Positioning revision (23 Nov 2026, evening; Aravind's review of the cut):**
- **Readback is for any AI feature's acceptance criteria.** The AMI meeting-recap feature is only the test bench, so meetings, recaps, AMI and C4 appear only in Methods and Evaluation (gate: `gates/positioning-audit.md`).
- **No section bar** on any frame. A chapter card (large numeral + part title, about 1.5 s) opens each part, at B01 (where it is also the poster frame), B04, B09 and B16. It replaces the near-empty frames at the part changes, and narration runs under it, so there is no silent gap.
- **Corner tags** (top right, y 3.12) replace the full-sentence CONSTRUCTED/PLANNED captions on concept diagrams: "illustration", "planned", "vision", "test case". They are set in `#6B675C`, quieter than ink and still 4.9:1 on the stage. Real evidence keeps its full source and date label at the bottom.
- **The hero chip** is a generic "criterion" chip in the executive summary and the introduction. From B11 on it is C4, written in plain English in two lines: "C4 · Don't report open questions as decisions".
- **New beats:** B01–B03 (hook; three constructed vignettes; Readback, the vision and the status), B09 (the test bench), the real ES2010b example in B14, B15 in three columns (have / account, not yet wired / planned), and B20 (the close).
- **End card:** "Readback.", the value line, "Aravind Ravi · INFO 7375" and "read by a synthetic voice", in larger type (my outro patch's `tagline` and `credit`). The toolkit's compile also prints the channel title, "Aravind Ravi · INFO 7375", over the first beat, so the poster carries no name of its own.
- The beat-by-beat table below is the Phase 2 storyboard. The current beat list is in `SHOTLIST.md`, and the current frames are in `storyboard.png` and `gates/contact-*.png`.

**Files:**
- `scenes.py`: the 20 Manim beats.
- `storyboard.png`: the last frame of every beat.
- `style-frames/`: one frame per part.
- `overlap_check.py`: a frame-by-frame check that no text overlaps.
- `make_storyboard.py`: builds the contact sheet.

## One visual system

### Colour roles (the only colours in the film)

| Role | Colour | Used for | Never |
|---|---|---|---|
| Stage | `#F2F0E9` | The ground at every cut, the outro included | — |
| Ink | `#3D3929` | All type, and neutral actors: the PM figure, ticks, crosses, needles | — |
| **Real evidence** | Kraft `#C7AE86` fill (`#A8916B` for a model drawn on a card), grey outline. Ink on `#C7AE86` is 5.4:1. | AMI data, the real transcript line and recap, real models, the three tools as their docs describe them | Ink outlines around type (they fail Gate T) |
| **Constructed** | White paper, light rule `#B4AFA6`, dark band `#3A3530` | The rubric and the recap prompt, each labelled `CONSTRUCTED` | Type on the dark band |
| **Planned ("will")** | Dashed grey `#8B8F96` on `#D9D4C7`; values shown as "—" | Labels, judge runs, agreement, every scorecard result | Grey type (it fails 4.5:1, so planned items are written in ink inside a dashed box) |
| **The clause** | Terracotta `#D97757` | The C4 chip's outline, its halo, the trace line, the C4 bar and cell outlines | Type, or type set on it |

### Type, grid, motion

- **Type scale:**
  - 72: "Readback", "86 decisions".
  - 52: part and tool titles.
  - 40: big evidence lines and tile heads.
  - 36: body.
  - 32: labels and tags. This is the floor.
  - The face is EB Garamond, with PT Mono for meeting IDs.
  - κ is spelled out as "kappa", because EB Garamond's κ reads as ϰ.
- **Grid:**
  - 12 columns across ±6.2, with a text margin of ±6.05.
  - ~~The part rail at y 3.1~~ (removed 23 Nov 2026; chapter cards mark the parts).
  - The Methods pipeline strip sits at y 2.3.
  - Content runs from y −2.7 to 2.6.
  - Source and date labels sit bottom-left at y −3.05 (bottom-right for a file path); corner tags sit top right at y 3.12.
- **Motion:**
  - Entrances fade in with a 0.15 rise.
  - Exits finish before entrances start.
  - At each part change (B04, B09, B16) the previous frame clears to the part's chapter card, which clears to the part's first frame.
  - Emphasis is an ink flash or an in-place pulse; the chip never changes colour.
  - Every cue is a spoken word (`mp3/words.json`).
  - Nothing animates across a clip's midpoint, because Gates T and V sample it.
  - Every scene opens on the previous scene's last frame, so each cut is a match cut.
  - Every narration line that carries a beat gets a change big enough to register. A large card flashes in place, a group steps back and returns, or text moves. Small icon changes don't count: ffmpeg's freeze detector averages over all three colour planes, so even a 36-pt line of text fading in stays under its threshold.

## The hero object: the criterion chip, then C4

In the executive summary and the introduction the chip is a generic **criterion** (forms `crit` and `crit_c`): no test case appears there. From B11 on it is **C4** from the CONSTRUCTED `rubric-v0.md`, in plain English: **full** ("C4 · Don't report open" / "questions as decisions", two lines at the 32 floor), **compact** ("C4") and **mini** ("C4" in a grid header). The table below is the Phase 2 version (when C4 was the chip throughout).

| Beat | The chip |
|---|---|
| B02 | Lifts out of the rubric page as the C4 bar turns terracotta. Trace lines tie it to the judges' split and back to the page. |
| B03 | Moves to the top. Two copies show "what the PM meant ≠ how a judge reads it". The misgraded C4 cell traces back to it, and the PM holds it. |
| B04–B06 | Parked top right while each tool is shown. |
| B07 | Drops into an empty dashed slot: "names the clause behind a disagreement" (not found in their docs). |
| B08 | Lit in tile 2: "a clause → what to fix". |
| B11 | Becomes the C4 row of the rubric. |
| B12 | Parked bottom right. |
| B13 | The C4 column header of the judges' grid. |
| B14 | Lights up. The split traces to it, and the question to the PM comes from it. |
| B16 | The planted clause. Readback's ring lands on it, which is the pass case. |
| B18 | The flagged clause, revised. The revision is dashed because it is planned. |

## Storyboard, beat by beat

| Beat | s | On screen | Moves on these words | Label or source |
|---|---|---|---|---|
| B01 | 9.5 | Rubric page C1–C5 (constructed), the PM, three AI judges and a pass/fail track. The judges' scores pull apart, and a "?" fans back to every clause. | rubrics, judges, grade, disagree, which, rubric | CONSTRUCTED illustration · no judge has run yet |
| B02 | 13.7 | "Aravind Ravi · read by a synthetic voice", then the "Readback" title. C4 lights and the chip appears. Traces run split → chip → C4. "Did you mean …?" goes to the PM, with "never rewrites the rubric" underneath. | synthetic, project, find, clause, disagreement, PM, rewriting | Same tag |
| B03 | 16.8 | "A rubric is a product decision." The PM's meaning ≠ a judge's reading. C1–C5 all ✓ and the feature ships; the wrong grading goes unnoticed: C4 was "graded on the judge's reading". Readback stops it before it ships, and the PM "decides what C4 means". | rubric, If, differently, scores, feature, wrong, unnoticed, catch, before, charge, mean | Same tag |
| B04 | 12.5 | "What others have done", with three tool names. Maxim AI: several models as judges → compares their verdicts → agreement with human labels (agreement score). | tools, reliable, Maxim, several, compares, measures, labels | per their public docs · checked 14 Oct 2026 |
| B05 | 9.5 | orq.ai: an evaluator vs human labels → same answer twice? → then proposes a rewrite (rewritten prompt). | compares, checks, proposes, prompt | Same |
| B06 | 8.3 | GitHub Spec Kit: for specs, not rubrics → an optional clarify step → resolves ambiguity before planning (clearer spec). | specs, optional, resolves, planning | Same |
| B07 | 12.8 | "From the tools I checked": the three outputs, each marked "✗ not found in docs". The chip sits in the empty slot: "names the clause behind a disagreement". | agreement, rewritten, clearer, What, documentation, October, naming, disagreement | Same |
| B08 | 10.1 | "Why Readback matters": a score → something is wrong; a clause (lit chip) → what to fix; a question → the PM decides, not a rewrite. | Readback, score, clause, question, rewrite, decision | Readback is planned · nothing has run yet |
| B09 | 16.0 | The pipeline strip builds itself (AMI data · Recaps · Rubric · Labels · Judges · Readback). "AMI Meeting Corpus" with CC BY 4.0. Ten real meeting cards (ID, length, DECISIONS count). The title becomes "86 decisions". | order, data, public, Corpus, ten, twenty, role-play, project, annotators, eighty-six | AMI corpus · CC BY 4.0 · data: `case-study/data/sample/selection.csv` |
| B10 | 9.8 | Real ES2007a transcript line `[00:17:52] C (UI): … it can just have a lock function,` → CONSTRUCTED recap prompt → Claude (`claude-opus-5-5`) → the real recap line. Then a stack of 10 real recaps. | recap, prompt, Claude, ran, fourteenth, ten | Labels on the cards; real output · 14 Oct 2026 |
| B11 | 12.1 | The constructed rubric's five clauses, verbatim (C1 shortened with "…"). The chip becomes the C4 row. C1 is linked to the real ES2007a DECISIONS list (2 of 7 shown, ✓). | rubric, five, every, unresolved, decisions, anchored, list, answer | CONSTRUCTED · rubric-v0.md / AMI ES2007a · CC BY 4.0 |
| B12 | 10.1 | 86 empty dashed cells, one row per meeting with one cell per DECISIONS item. "My human labels": 86 decisions, marked by me; planned, not marked yet. Git order: labels committed → judges run. | mark, covers, human, commit, first, history | PLANNED · no labels exist yet |
| B13 | 13.9 | Three planned judges (Claude, a second provider's model, a local open-weight model) against empty C1–C5 cells. Agreement between judges: —. Judges vs my labels, decisions clause: —. | judges, every, Claude, second, local, clause, measure, human, decisions | PLANNED · no judge has run yet |
| B14 | 10.8 | Illustration: the C4 cells split ✓ ✗ ✓. The split traces to the C4 chip, which lights. "Did you mean this, or that?" goes to the PM, then "C4 · revised by the PM" (dashed). | split, trace, clause, question, mean, answers, revises | PLANNED · illustration of the method, no judge has run yet |
| B15 | 14.2 | Checklist, one row per resource (see below). A tick only for what is set up on this Mac today. | data, repository, Claude, subscription, credits, provider, wired, local, human, labels | a tick means set up on this Mac · status as of 23 Nov 2026 |
| B16 | 14.6 | Rail → Evaluation. Scorecard frame (Check · Pass if · Fail if · Result), row 1. Demo: C1–C5 with C4 planted (one variant per clause). Readback's ring lands on C4 ✓, then on C2 ✗, then scatters ✗ (noise). | Three, pass, fail, planted, clause, vague, advance, blames, another, noise | PLANNED · nothing has run yet (EVAL-PLAN.md) |
| B17 | 14.9 | Row 2. My human labels (86 decisions, marked by me) and each judge. Cohen's kappa, low → high, with the 0.6 bar (locked) and pass and fail zones. | decisions, judge, human, eighty-six, Cohen's, point, fix, Below, trusted | PLANNED · the 0.6 bar is fixed before any run |
| B18 | 12.1 | Row 3. C4 → "C4 · revised" (PM revises the clause). Held-out meetings, locked; the split's size isn't shown. Before — / after —, which must rise. | after, revises, re-measure, held, rise, help, say | PLANNED · every result is reported, pass or fail |
| B19 | 8.4 | The full scorecard fills the frame, with every result "—". "Result: will be measured · nothing has run as of 23 Nov 2026". | blank, measured, failed, scorecard | a failed check goes on the scorecard too |
| BOUT | 4.3 | Patched `ClaudeTitleOutro`: "Readback.", my handle, no mascot, light card on `#F2F0E9`. | — | — |

B15's checklist rows (resource | status):
- ✓ AMI data · 10 meetings | in my repository
- ✓ 10 real recaps | in my repository
- ✓ Claude (`claude -p`) | set up on this Mac · CLI 2.1.323
- ○ API credits | account, not yet wired
- ○ a second provider | account, not yet wired
- ○ local open-weight model | planned · Ollama installed 2026-11-23 (0.40.17), no model pulled, judge not wired
- ○ my human labels | planned · I mark the 86 decisions
- ✓ compute | this Mac

A tick appears only for what was checked as set up on this Mac on 23 Nov 2026: the `claude` CLI 2.1.323 is installed and no API key is configured. Ollama: installed 2026-11-23 (0.40.17), no model pulled, judge not wired. The 22:11 EST check found `ollama --version` 0.40.17, `/Applications/Ollama.app`, the Homebrew cask `ollama-app` and `ollama serve` running, with `ollama list` empty and no judge code in the repo, so the local model stays under planned.

## Every number on screen, and where it comes from

| On screen | Source |
|---|---|
| 10 meetings; their IDs, lengths (min s) and DECISIONS counts (12, 10, 9, 8, …, 7); 86 | `../../case-study/data/sample/selection.csv` (asserted in `scenes.py`) |
| 7 (ES2007a) | the same file; ES2007a's `summary.txt` lists 7 DECISIONS |
| `[00:17:52]` | `../../case-study/data/sample/ES2007a/transcript.txt` and `../../case-study/outputs/feature-run/ES2007a.json` (asserted) |
| `claude-opus-5-5`, 14 Oct 2026, 10 real recaps | `../../case-study/outputs/feature-run/*.json` (`models_reported`, `run_started_utc`; asserted) |
| C1–C5 | `../../case-study/constructed/rubric-v0.md` (clause texts asserted) |
| 14 Oct 2026 (docs checked) | `../../FRICTIONAL.md`, the alternative-check entries |
| 0.6, one variant per clause (C1–C5), the held-out split, 3 judges | `EVAL-PLAN.md` (plan settings, shown as plans) |
| 23 Nov 2026 | the status date of this storyboard |
| Every result | "—" (nothing has run) |

## Checks run in Phase 2

- **Gate A** (`static_scene_check.py`, per class): 19 of 19 clean, 0 warnings.
- **Frame-by-frame text overlap** (`overlap_check.py`, every frame at 24 fps): 19 of 19 scenes, 0 overlaps. The first pass flagged 99, and all were fixed.
- **Ground colour:** every scene's frame and the outro still sample `#F2F0E9`.
- **Not yet run:** Gates T, W, B and V, freezedetect, loudness and the full render. They come in Phases 3–4.
