# GATES — Readback project film · Phase 4, re-run after the pre-Phase-5 revisions (measured 2026-11-23 16:08 EST; full re-run 16:14 EST on the same master, identical results — `gate-rerun.txt`)

**The file:** `../aravind-r-readback-project-film.mp4`. It's byte-identical to the toolkit master `../exports/landscape/aravind-r-readback-project-film.mp4`.
- **Verified record:** status `ready`, SHA-256 `79aa3ec669cd4652f4e4c639a95956e30886c69ba24fbe88b5196af58914d8ca`, matching the file.
- **Format:** 1920×1080, 24 fps, H.264, AAC 48 kHz stereo, 235.38 s.
- **Measurements:** `../qc_film.py`, whose raw output is `QC.json`.

**What changed since the first Phase 4 table:**
- B15's resource checklist: ticks only for what is set up on this Mac.
- "my human labels" on screen and in the narration.
- Prior work scoped to "the tools I checked".
- B13 reworded.
- "Readback" respelled "Reed-back" in the Kokoro input. Eleven beats were re-voiced; `stt-revoiced-beats.txt` has their speech-to-text.
- The storyboard and style frames were regenerated from this master.

## Phase 4 gates (my brief)

| Gate | Pass condition | Measured | Result |
|---|---|---|---|
| Freeze | `freezedetect=n=0.003:d=3` total under 15 % of runtime, and every hold listed in `SHOTLIST.md` | **10.87 s = 4.6 %**: three spans, 171.71–174.83 s, 200.08–203.83 s and 231.38–235.38 s. At `d=2.5` there are five holds, all listed in `SHOTLIST.md` with the line each lands on. | **PASS** |
| Black | no unintended black frames (`blackdetect=d=0.1:pix_th=0.10`) | none | **PASS** |
| Loudness | −16 LUFS ±1 integrated; true peak ≤ −1 dBTP | **−16.1 LUFS · −1.2 dBTP** (ebur128) | **PASS** |
| Dead air | no silence over 1.2 s between beats (`silencedetect=noise=-50dB:d=1.2`) | none | **PASS** |
| Runtime | within the 4:00 cap | **3:55.4** (235.38 s) | **PASS** |
| Contact sheet | `fps=1/4,tile=6x8` | `contact-01.png`, `contact-02.png` (59 frames) | done |
| Section boundaries | a frame grab at every part boundary | `boundaries/`: each boundary ±0.05 s (identical pairs, because every cut is a match cut), 1.5 s into each part, and the last frame | done |
| Ground at every cut | the same colour on both sides of every cut | 19 cuts × 2 sides × 4 corner points = 152 samples, **all RGB (241, 240, 233)**, which is `#F2F0E9` after H.264 | **PASS** |
| Labels | constructed material says `CONSTRUCTED`; real material carries its source and date | audit below | **PASS** |
| Numbers | every on-screen number comes from a repo file, with its path cited | audit below | **PASS** |
| First minute | the first 60 s says what Readback is and why it matters | quoted below | **PASS** |
| Brands and persona | prior work as plain text only, no logos or marks, no instructor name, persona or credit, mascot hidden | audit below | **PASS** |

## Toolkit gates (brutalist.art @ `cd4bf20` with my outro patch)

| Gate | Result | Where |
|---|---|---|
| F — paperwork exists | PASS | `../FACTCHECK.md`, `../SHOTLIST.md`, `../PROMPTS.md` |
| factcheck (content of F) | clean: 72 rows, 20 of 20 beats covered | `factcheck_check.txt` |
| L — beat-mix lint | clean | `art-run-8.log`, `gate-rerun.txt` |
| A — static pre-flight | clean, 0 warnings, all 19 scenes | `gates-AWB-final.txt` (final code, all 19) |
| W — WCAG contrast, margins, text overlap | clean, all 19 scenes | `gates-AWB-final.txt` |
| B — layout audit (`--curve-strict`) | CLEAN, all 19 scenes | `gates-AWB-final.txt` |
| V — frame-level visual QC | 0 BLOCKER, 0 MAJOR (40 frames), on the review cut and again on the clean master (`--mp4`) | `gate-v-REPORT.md` (clean master) |
| T — typography (size, overflow, contrast, kerning) | PASS, 20 of 20 beats | `TYPECHECK.md` (re-run 16:14) |
| Bookends (outro handle = `channel_title`) | PASS | `bookend_check.txt` |
| Verified master | `ready`, SHA-256 matches | `../exports/landscape/*.verified.json` |
| My frame-by-frame text-overlap check (every frame, 24 fps) | 19 of 19 scenes, 0 overlaps | `overlap-check.txt` |

## Label audit

**Constructed material:**
- B01–B03: `CONSTRUCTED illustration · no judge has run yet`.
- B10: `CONSTRUCTED · my recap prompt`.
- B11: `CONSTRUCTED · rubric-v0.md`.

**Real material, with source and date:**
- B04–B07: `per their public docs · checked 14 Oct 2026`, and B07's title reads "From the tools I checked".
- B09: `AMI corpus · CC BY 4.0 · data: case-study/data/sample/selection.csv`.
- B10:
  - `AMI ES2007a transcript · CC BY 4.0`;
  - `Claude · claude-opus-5-5`;
  - `real output · claude-opus-5-5 · 14 Oct 2026`, then `10 real recaps · claude-opus-5-5 · 14 Oct 2026`.
- B11: `AMI ES2007a · CC BY 4.0`. AMI's DECISIONS list is shown as the reference answer, not as labels.
- B15: `a tick means set up on this Mac · status as of 23 Nov 2026`.
  - Ticked: AMI data, the 10 recaps, `claude -p` (CLI 2.1.323).
  - Open circles: API credits and a second provider (each "account, not yet wired"), the local model ("planned · Ollama not installed"), my human labels ("planned · I mark the 86 decisions"), compute ("this Mac · local judge planned").

**Planned material:** drawn in the dashed grey "will" style, with every value shown as "—". The human labels always read as mine and planned: B12 "my human labels · 86 decisions, marked by me · planned · not marked yet"; B13 "judges vs my labels"; B17 "my human labels · 86 decisions, marked by me"; the scorecard "vs my human labels". The tags read:
- `PLANNED · no labels exist yet` (B12);
- `PLANNED · no judge has run yet` (B13);
- `PLANNED · illustration of the method, no judge has run yet` (B14);
- `PLANNED · nothing has run yet (EVAL-PLAN.md)` (B16);
- `PLANNED · the 0.6 bar is fixed before any run` (B17);
- `PLANNED · every result is reported, pass or fail` (B18);
- `Result: will be measured · nothing has run as of 23 Nov 2026` (B19);
- `Readback is planned · nothing has run yet` (B08).

Checked on `contact-01.png`, `contact-02.png` and `../storyboard.png`.

## Numbers audit (everything on screen that contains a digit)

| On screen | Source |
|---|---|
| 10 meetings; IDs; lengths (20 min 21 s … 34 min 58 s); DECISIONS counts (12, 10, 9, 8 ×6, 7); 86 decisions | `../../../case-study/data/sample/selection.csv` (the tag cites it; asserted in `scenes.py`) |
| … 7 in this meeting | the same file, plus `ES2007a/summary.txt` (7 DECISIONS) |
| [00:17:52] | `ES2007a/transcript.txt`, `case-study/outputs/feature-run/ES2007a.json` (asserted) |
| 10 real recaps, claude-opus-5-5, 14 Oct 2026 | `case-study/outputs/feature-run/*.json` (`models_reported`, `run_started_utc`; asserted) |
| CLI 2.1.323 | `FRICTIONAL.md` 2026-11-23 Phase 0 (`claude --version`, rechecked 2026-11-23 15:50 EST) |
| C1–C5, C4, rubric-v0.md | `case-study/constructed/rubric-v0.md` |
| checked 14 Oct 2026 | `FRICTIONAL.md`, alternative checks dated 2026-10-14 |
| 0.6, kappa ≥ 0.6 / < 0.6; one variant per clause, C1–C5; checks 1–3 | `../EVAL-PLAN.md` (plan settings, shown as plans) |
| 23 Nov 2026 | the status date (`FRICTIONAL.md`, 2026-11-23 entries) |
| CC BY 4.0 | `case-study/data/sample/README.md`, `SOURCES.md` |
| INFO 7375 | my course (outro handle) |
| Results | "—" everywhere; nothing has run |

## First-minute test (0:00–1:00, as voiced)

> "Product managers now write rubrics that AI judges grade against. When those judges disagree, it's hard to tell which line of the rubric caused it. I'm Aravind Ravi, and this film is read by a synthetic voice. My project is called Readback. It will find the clause behind a disagreement, and ask the PM a clarifying question about it, instead of rewriting the rubric for them. Why should anyone care? Because a rubric is a product decision. If a judge reads one clause differently than the PM meant, the scores can still look fine, the feature ships, and the wrong grading goes unnoticed. Readback will catch that misreading before it ships, and keep the PM in charge of what their words mean."

That's the executive summary, 0:00–0:40. What it is lands by 0:23, and why it matters by 0:40. From 0:40 to 1:00 the introduction starts on prior work: Maxim AI, then orq.ai. **PASS.**

## Brand and persona audit

- **Prior work:** Maxim AI, orq.ai and GitHub Spec Kit are plain text in EB Garamond. `scenes.py` has no image, SVG or logo objects (grep: no `ImageMobject` or `SVGMobject`). On-screen claims are limited to the 2026-10-14 checks in `FRICTIONAL.md`, and the "not found" claims are scoped to the tools I checked.
- **Other brands:** no marks for Google, Zoom, Microsoft or Anthropic. "Claude" appears only as a model name, in text.
- **Persona:** no instructor name, persona or credit in the scenes, the beat sheet or the outro props (grep clean). The outro shows "Readback." and "Aravind Ravi · INFO 7375", and the mascot is hidden (`hideMascot`, my patch). Checked on `boundaries/last-frame.png`.
- **Cold open:** the toolkit's skin lint asks for a Claude composer cold open. This film has none, by design, which the beat sheet records in `bookend_exempt`.

## Unchanged narration clips

The 9 clips that were not re-voiced (B01, B04, B05, B06, B09, B10, B11, B12, B19) match the pre-revoice backup byte for byte: **9 of 9 SHA-256 match** (`unchanged-clips-sha256.txt`). The 11 re-voiced clips differ, as they should.

## Speech-to-text on the full film

`../stt_check.py` transcribes the whole delivered soundtrack (faster-whisper small.en). It compares the result with the script in one diff, after normalising formatting only: numbers, hyphens, punctuation, quote marks, word spacing (Spec Kit / Speckit, re-measure / remeasure), and the spoken spellings "Reed-back" and "Ork dot AI". The script has 697 words, and 697 were heard. **4 of 20 beats differ** (`stt-full-master.txt`). For each of them, the beat's own clip was also transcribed alone with the same model:

| Beat | Film time | Script | Heard in the full film | Heard on its own clip |
|---|---|---|---|---|
| B02 | 0:09.8 | "I'm **Aravind** Ravi" | "I'm **Eravind** Ravi" | "I'm **Eravind** Ravi" |
| B06 | 1:04.0 | "**GitHub's** Spec Kit" | "**GitHub** spec kit" | "GitHub's Speckit" (matches) |
| B19 | 3:45.1 | "every result on **this** scorecard" | "every result on **the** scorecard" | matches |
| BOUT | 3:52.8 | "by **Aravind** Ravi" | "by **Eravind** Ravi" | matches |

Only B02's "Aravind" differs on both passes. The other three differences come from transcribing the film in one pass. B06 and B19 are among the 9 clips that weren't re-voiced.

B13 matches the script: in the full film its "Claude" is heard as "Claude", though the clip alone gave "clawed" earlier. No "Readback" differs either. On their own clips, all seven beats that say the name give "read back" or "readback" (`stt-revoiced-beats.txt`).
