# v2 visual plan — Readback (visuals only; narration and durations locked)

**Timebox:** the deadline is 2026-10-14 23:59 EDT, so the **hard stop is 22:44 EDT**. If v2 isn't fully gated by then, I submit v1 (`31005a1`). The plan was written at 15:15 EDT.
**v1 baseline:** `freezedetect n=0.003 d=3` on the clean master finds 23 holds of ≥3 s, totalling 163.7 s of 182.46 s (**89.7 %** frozen). The slate copy measures 90.6 %.
**v2 targets:**
- Holds of ≥3 s cover ≤25 % of the runtime.
- No hold is longer than 4 s, except BOUT.
- Runtime is 182.46 s ± 1 s, from the same 10 mp3 clips.

**Beat IDs:** your B01–B10 map onto the sheet's BIDEA, B01–B08 and BOUT.
**BIDEA changes from the Remotion hesitant writer to a Manim scene.** Its audio and duration don't change. The cold-open exemption already covers it.

## Colour roles (defined once in `scenes.py`)

| Role | Colour | Used only for |
|---|---|---|
| Readback / the PM's instruction | ink `#3D3929` | the rubric page outline, the PM, Readback's own items, all text |
| Existing tools and evidence | kraft `#C7AE86`, `#DCC9AA` | Maxim AI and orq.ai cells, real AMI cards, real recap cards, my PR chips |
| Disagreement / the clause in question | red accent `#D97757` | C4 (or C5) marks, the fail stamp, the disputed-clause connector, the OUT stamp outline |
| Planned / will exist | grey outline `#8B8F96`, dashed | every future object |

**Adjustment 1 (Gates T/W):** text is always ink. The red accent and the grey are never used for type: red-on-cream is 2.7:1 and grey-on-cream about 3:1, both under the 4.5:1 floor. So "planned" is written in ink beside a grey-outlined object.

## Grid, type and rail

- **Grid:** 12 columns across the ±6.2 safe width, each about 1.03 units. The main graphic spans at least 8 columns (≥ 65 %).
- **Type:**
  - Body labels: Manim `font_size` ≥ 36 (about 55 px text-run height at 1080p, against Gate T's 41 px floor).
  - Titles: 64.
  - At most about 8 words on screen, apart from real excerpts.
- **Progress rail:** a slim strip along the top (y = 3.1) with seven marks: What · Why · Who · Proves · Scope · Risk · Why me. The current mark is filled ink; the others are open circles. It replaces the "Q1 · what it is" headers. BIDEA, B08 and BOUT show the rail with no mark filled.
- **Honesty tag:** bottom-left (y = −3.05), same as v1.

## The rubric page (recurring character)

- One page object: a card with five clause bars labelled C1–C5. The red accent always sits on **C4** ("unresolved stays unresolved").
- **Continuity:** every scene opens with the page exactly where the previous scene left it, so the cuts are match-cuts.
  - BIDEA: centre, large; C1→C5 draw in. **Ends** at the left third.
  - B01: left third. **Ends** small, top-left of the content.
  - B02: grid header icon over the Readback column.
  - B03: slides into the README as the source of its table.
  - B04: becomes the "prompt contract" chip.
  - B05: right side, where the OUT stamp lands.
  - B06: beside the held-out lock.
  - B07: on the timeline as "Readback", in grey.
  - B08: in the "exists" column as the constructed rubric, then shrinks to the centre in the last second, where the outro's "Readback." title appears.

## Cue list (seconds from the start of each beat, from `mp3/words.json`; no gap > 2.6 s)

| Beat | Cues: word@time → change |
|---|---|
| **BIDEA** 15.08 | 0.3/0.9/1.5/2.1/2.7 C1–C5 draw · 4.9 "AI feature" a recap card slides in · 6.0 "judge" 3 judge tokens enter · 6.5/7.0/7.5 stamps pass, pass, **fail** · 8.4 "question" C4 Indicate · 10.0 "passes" Circumscribe C4 · 11.0–13.3 "judge reads my rubric" writes **"Does the judge misread my rubric?"** · 13.6 page slides to the left third. Tag: `CONSTRUCTED — no judges have run yet` |
| **B01** 17.21 | 0.7 "Readback" title · 2.5 "clause" 3 lines from the judges converge on C4 · 4.8 "reads differently" C4 turns red · 6.0 "meant" a "Did you mean…?" bubble rises toward the PM · 8.5 "repository" grey repo folder · 9.8 "command-line" types `readback-pm check rubric.md` · 10.9 "case study" grey folder · 13.1 "log" grey log sheet · 15.2 "revision" a before→after arrow draws. Tags: `CONSTRUCTED`, `planned` |
| **B02** 23.46 | 0.9 "misreads" C4 flash · 2.5 "look fine" a score chip says "pass" · 4.0 "wrong" the chip flips to red-outlined · 5.0 "two tools" grid columns Maxim AI · orq.ai · Readback · 6.5–8.7 rows 1–2 fill for Maxim · 10.0–12.8 rows 2–3 fill for orq.ai · 14.5 "docs" footer `per their public docs, as of 14 Oct 2026` · 16.5 "clause" row 4 · 18.2 "Readback will" grey "planned" column fills · 20.1 row 5 · 21.7 Spec Kit row "specs (later module)" |
| **B03** 17.79 | 0.6 "hiring manager" a reader figure · 2.4 a role chip "AI PM" · 4.2 "open" README window opens · 5.2 "one table" cursor scrolls to it · 6.0–13.0 the 5 headers type in on their spoken words (per-clause 6.0, disagreed 8.2, question 9.3, revision 10.9, held-out 11.9), with "—" cells · 13.8 "end user" a PM chip · 14.5–16.5 the stopwatch arc sweeps "first 60 s". Tag `CONSTRUCTED mock-up — values will be measured` |
| **B04** 20.54 | 1.8 "prompt contract" chip 1 · 2.7 "verify" chip 2 · 4.4 "labels" git commit "labels" (grey) · 5.8 "judge runs" commit 2 (grey) · 7.2 "proves the order" an order arrow · 8.6 "evaluate" chip 3 · 10.6 "ground claims" chip 4 · 11.5 "transcript lines" **real pair**: AMI ES2007a `[00:17:52] C (UI): … it can just have a lock function,` → recap line `Include a lock function … [00:17:52]` · 15.5 "human anchor" an anchor joins the labels commit · 17.5 "every feature" 1 feature box · 18.6 "one" box ticks |
| **B05** 19.35 | 2.0 "ten" 10 cards fan out with real IDs (staggered 0.12 s) · 3.0–5.0 they re-flow into a bar chart; ValueTracker bars grow to the **real DECISIONS counts** (IS1004d 12, ES2006d 10, IS1009d 9, ES2008c / ES2010b / ES2011b / ES2013d / IS1003c / IS1005c 8, ES2007a 7) · 5.8 "Out" the OUT stamp on the rubric + "never rewrites the rubric" · 7.6 "rubric" C4 Indicate · 8.7 "asks" a "?" chip · 10.5 "First" grey checklist line 1 · 11.6 line 2 · 12.5 line 3 · 13.6 "agreement table" a grey table · 15.8 "commit" two commit dots in order. **Adjustment 2:** the 250-word cap isn't a DECISIONS-scale quantity, so it sits on a second small axis: real recap word counts 224–276 with a 250 line, and the IS1004d bar called out "12 decisions · 250-word cap" as a sourced fact. Bars move ≥ every 2.5 s |
| **B06** 17.3 | 0.8 "Overfitting" the deck appears · 1.8 a revise arrow loops · 4.0 "examples" cards fan · 6.0 "freeze" the deck splits dev / held-out · 6.5 the padlock snaps shut · 8.5 "held-out numbers" an empty "—" cell · 10.8 "blind spots" 2 overlapping circles (same model) · 13.6 "cross-model" separate circles · 14.6 "report it either way" a two-cell "—" report. Tag `CONSTRUCTED — planned method` |
| **B07** 29.22 | 1.8 "new to me" bracket opens · 2.4/3.2/4.8 three ink chips · 6.2 "Already mine" a timeline draws · 9.5/11.3/12.1 three tan chips (LG Energy Solution Vertech · Tech4Dev · KoineArth) · 13.7 "internal" a "internal — not shown" tag · 15.3 "course" a course segment · 16.3 "week one film" PR #8 · open · 18.6 the "verified" tick · 19.6 "recipe" PR #23 · open · DRAFT · 21.0 "to-do" a TODO tag · 23.1 "e-vals" grey Readback chip · 26.6 "eval project" the bracket links the new skills to Readback |
| **B08** 18.55 | 0.1 "exists" the left column slides in · 1.9 "ten AMI" sample card (10 meetings) · 3.3 "constructed" CONSTRUCTED docs card · 5.1 "recap feature" a real recap excerpt card (model, date) · 9.5 "Ten real outputs" a 10-dot strip · 10.9 "will exist" the right column slides in (grey) · 11.8/12.4/13.0 labels / judge runs / agreement table · 14.3 "numbers" "—" cells · 15.8 "measured" CLI + later-modules outlines · 17.0 the rubric shrinks to the centre (match-cut to BOUT) |
| **BOUT** 3.73 | Patched `ClaudeTitleOutro`: "Readback.", my handle, `hideMascot`. Static by design (exempt from the 4 s rule). Plain text, no logo |

**B02 grid cells, only from `FRICTIONAL.md` (2026-10-14):**

| Row | Maxim AI | orq.ai | Readback |
|---|---|---|---|
| 1. Compares several judges | ✓ | not found in docs | planned |
| 2. Measures judge–human agreement | ✓ | ✓ | planned |
| 3. Rewrites the judge prompt | not found in docs | ✓ | never |
| 4. Names the clause behind a disagreement | not found in docs | not found in docs | planned |
| 5. Asks the PM instead of rewriting | not found in docs | not found in docs | planned |

The Readback cell in row 3 is "never" (Q5 out item), not "planned". Is that OK?

## How I'll measure

1. `freezedetect` on the B05 probe, then on the full v2.
2. Every toolkit gate, strict.
3. A contact sheet at 1 frame every 2 s.
4. A full-resolution frame per beat, which I check myself.
5. Runtime diffed against v1.
