# Honesty audit — Readback v2 visuals

**My own check, not a toolkit gate.** Prepared 2026-10-14 by Claude Code against the submitted `aravind-r-readback-pitch.mp4` (v2 visuals, SHA-256 `4334b59e…568278eb`, 182.458 s; re-checked after the overlap fixes), checked on `gates/v2/frames/*.png` and `gates/v2/v2-contact-1frame-per-2s.png`. I (Aravind) decide every fix.

**Narration:** identical to v1. The decoded audio PCM hash is the same (`215332921a8d6b4c…`) and `beat_sheet.json` narration and durations are asserted equal. The 46 narration rows in `../honesty-audit.md` (second pass, all medium flags resolved) still apply unchanged.

**This file adds a row for every new on-screen claim, label and number in v2.**

## On-screen claims, labels and numbers (v2)

| Beat | On screen | claim_status | Evidence (path, date) or "will" | Flag |
|---|---|---|---|---|
| all | Progress rail: What · Why · Who · Proves · Scope · Risk · Why me | framing | maps to Q1–Q7 | — |
| all | Text overlaps | — | `gates/v2/overlap-check.txt`: 0 on every frame of all 9 Manim scenes; outro card and the toolkit's name line checked by eye | — |
| BIDEA | "Aravind Ravi" / "read by a synthetic voice" | exists | Kokoro `am_onyx`, local | — |
| BIDEA | rubric C1–C5, "my eval rubric", a recap card, 3 judges, stamps pass / pass / fail, C4 red, "Does the judge misread my rubric?"; tag "CONSTRUCTED — no judges have run yet" | constructed | labelled | — |
| BIDEA | small "Aravind Ravi · INFO 7375" at bottom centre | exists | Added by the toolkit's compiler (it was also in v1); my name only | **V1** (low): small toolkit text I didn't place; Gate T passed it |
| B01 | "Readback", rays to C4, "Did you mean…?", PM, grey repo / case study / eval log, `$ readback-pm check rubric.md`, before → after; tag "CONSTRUCTED · grey = planned" | will / constructed | labelled grey | — |
| B02 | Grid rows 1–5 × Maxim AI / orq.ai / Readback; ✓ only where logged; "not found" elsewhere (never ✗); Readback "planned" ×4 + "never"; "specs (later module): Spec Kit clarify"; footer "per their public docs, as of 14 Oct 2026 · names only" | exists (checks) / will | `FRICTIONAL.md` alternative checks, 2026-10-14; FACTCHECK rows 24–26 | — |
| B02 | "score: pass" / "ship decision: wrong" | framing | the narration's conditional ("If the judge misreads…") | **V2** (low): shown without "if"; the narration carries the condition |
| B03 | README table headers + "—" cells, "first 60 seconds", PM end user; tag "CONSTRUCTED mock-up — values will be measured" | constructed | labelled; no values | — |
| B04 | "it will show I can:", skill labels, grey labels → judge runs, "planned order", grey held-out box, anchor, "AI features" → "1 feature" | will / constructed | tag "CONSTRUCTED · grey = planned" | — |
| B04 | "AMI ES2007a [00:17:52] UI: “… it can just have a lock function,”" | exists | `case-study/data/sample/ES2007a/transcript.txt`, asserted in `scenes.py`; FACTCHECK row 28 | — |
| B04 | "recap · Claude Opus 5.5 · 14 Oct 2026 / “Include a lock function … [00:17:52]”" | exists | `case-study/outputs/feature-run/ES2007a.json`, asserted; FACTCHECK row 29 | — |
| B05 | DECISIONS bars 12, 10, 9, 8 ×6, 7 with the meeting IDs | exists | `case-study/data/sample/selection.csv`, asserted at render time; FACTCHECK row 30 | — |
| B05 | recap-word bars and "250" | exists | feature-run outputs (word counts asserted) and `recap-system-prompt.md`; FACTCHECK row 31 | — |
| B05 | "IS1004d: 12 decisions, 250-word cap" | exists (fact) | FACTCHECK row 32; no outcome claimed | — |
| B05 | rubric "CONSTRUCTED", "OUT · never rewrites the rubric", C4 → ? → PM, "first run · planned" checklist, labels → report; tag "AMI sample · CC BY 4.0 · downloaded 14 Oct 2026" | will / constructed / exists (data) | labelled | — |
| B06 | "overfitting", examples, dev / held-out, padlock, "held-out score: —", same-model / cross-model; tag "CONSTRUCTED — planned method" | constructed | labelled; no values | — |
| B07 | "a mix", "new to me:" bracket + three skills, "already mine:", role chips "LG Energy Solution Vertech · Tech4Dev · KoineArth", "internal — not shown", "PR #8 · open" ✓, "PR #23 · open · DRAFT", grey Readback; tag "PR status as of 14 Oct 2026 · roles internal, not shown" | exists / will | `PROJECT-BRIEF.md` Q7; PR checks 2026-10-14; FACTCHECK row 35 | F7 (v1, kept as disclosed): roles not shown |
| B08 | "exists · 14 Oct 2026": "AMI sample · 10 meetings", "constructed docs (3)", "“Include a lock function …”" with "ES2007a recap · Claude Opus 5.5", "10 real outputs", "brief · log"; "will exist" (grey): my labels, judge runs, agreement table, "held-out result: —", CLI · later modules; tag "real output · Claude Opus 5.5 · 14 Oct 2026 · grey = will" | exists / will | FACTCHECK row 36 | — |
| BOUT | "Readback.", "Aravind Ravi · INFO 7375", no mascot | exists | toolkit patch `hideMascot` | — |

## Checks across the whole film (v2)

- **Numbers on screen:** 12, 10, 9, 8, 7 (DECISIONS); 250; 10 (meetings, outputs); 3 (docs, judges planned); 60 s; 00:17:52; PR #8, #23; 14 Oct 2026; Opus 5.5; INFO 7375.
  - Every one is from a file, a date or a PR number, or is a labelled plan ("3 judges", "first 60 seconds").
  - Planned metrics appear only as "—" or empty, with no placeholder values.
- **Logos:** none; frames checked.
  - Maxim AI, orq.ai and Spec Kit appear as plain text only.
  - Google, Zoom and Microsoft don't appear at all.
  - Anthropic: "Claude Opus 5.5" appears only as the model the recap ran on, and the Claude mascot stays hidden.
- **Instructor:** no instructor name, persona or credit. The only matches for the handle are the owner name inside PR URLs, in metadata only.
- **Colour roles:**
  - red is used on C4 and its rays, the fail stamp and the "wrong" stamp (all disagreement or the clause in question), plus the OUT underline in B05 (see V3);
  - grey only for planned work;
  - all text ink.

## Flags (for my decision)

| Flag | Severity | Where | Possible fix (not applied) |
|---|---|---|---|
| V1 | low | BIDEA: small "Aravind Ravi · INFO 7375" line from the toolkit compiler | Leave it (it's my name and it was in v1), or find and switch off the overlay |
| V2 | low | B02: "score: pass / ship decision: wrong" shown without the narration's "if" | Add "if misread:" before it (re-render B02) |
| V3 | low | B05: the OUT underline uses the red accent, outside its "disagreement / clause" role | Make it an ink underline (re-render B05) |
