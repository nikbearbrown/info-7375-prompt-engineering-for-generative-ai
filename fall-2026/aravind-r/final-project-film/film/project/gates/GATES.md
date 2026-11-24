# GATES — Readback project film · positioning revision (measured 2026-11-23, 19:32–19:38 EST)

**The file:** `../aravind-r-readback-project-film.mp4`. It's byte-identical to the toolkit master `../exports/landscape/aravind-r-readback-project-film.mp4`.
- **Verified record:** status `ready`, SHA-256 `8ed1366af25017b19515fa9dc7618c6238532026e3bdfe7e6d90673c7b808b2b`, matching the file.
- **Format:** 1920×1080, 24 fps, H.264, AAC 48 kHz stereo, 238.46 s.
- **Measurements:** `../qc_film.py`, whose raw output is `QC.json`.

**What changed in this revision** (my feedback on the review cut, 2026-11-23):
- Readback is positioned for any AI feature's acceptance criteria. The AMI meeting-recap feature is the test bench and appears only in Methods and Evaluation, tagged "test case". There is a new gate for this: the positioning audit below.
- A new executive summary (B01–B03) and close (B20). B08 was restated. B09 is now the test bench. B14 has the real ES2010b example. B15 is in three columns.
- No section bar. Chapter cards open each part, and card 1 is the poster frame. Corner tags replace the full-sentence captions on concept diagrams.
- C4 is in plain English. The gaps between beats are 0.35–0.55 s. B10 has a hero-size transcript and recap beat. The end card is larger and adds the value line and the voice credit.
- 13 beats were re-voiced (B01–B03, B08, B09, B11, B13, B14, B16, B17, B19, B20, BOUT). The other 8 keep their speech, with only the edge silence trimmed.

## Phase 4 gates (my brief)

| Gate | Pass condition | Measured | Result |
|---|---|---|---|
| Freeze | `freezedetect=n=0.003:d=3` total under 15 % of runtime, and every hold listed in `SHOTLIST.md` | **5.08 s = 2.1 %**: only the end card (233.38–238.46 s). At `d=2.5` there are five holds, all listed in `SHOTLIST.md` with the line spoken over each. The first measure of this revision was 47.62 s (20.0 %, a fail); flashes on large cards and soft bands, each on a spoken word, fixed it. | **PASS** |
| Black | no unintended black frames (`blackdetect=d=0.1:pix_th=0.10`) | none | **PASS** |
| Loudness | −16 LUFS ±1 integrated; true peak ≤ −1 dBTP | **−16.1 LUFS · −1.2 dBTP** (ebur128) | **PASS** |
| Dead air | no silence over 1.2 s (`silencedetect=noise=-50dB:d=1.2`) | none; the gaps between beats are 0.35–0.55 s, and the chapter cards run over narration | **PASS** |
| Runtime | within the 4:00 cap | **3:58.5** (238.46 s) | **PASS** |
| Contact sheet | `fps=1/4,tile=6x8` | `contact-01.png`, `contact-02.png` | done |
| Section boundaries | a frame grab at every part boundary | `boundaries/`: each boundary ±0.05 s, 1.5 s into each part (the chapter cards), and the last frame | done |
| Ground at every cut | the same colour on both sides of every cut | 20 cuts × 2 sides × 4 corner points = 160 samples, **all RGB (241, 240, 233)**, which is `#F2F0E9` after H.264 | **PASS** |
| Labels | constructed material says `CONSTRUCTED`; real material carries its source and date; concept diagrams carry a corner tag | audit below | **PASS** |
| Numbers | every on-screen number comes from a repo file, with its path cited | audit below (`../CLAIMS.md`, on-screen numbers O01–O18) | **PASS** |
| First minute | the first 60 s says what Readback is and why it matters, for any AI feature | quoted below (positioning audit §4) | **PASS** |
| Brands and persona | prior work as plain text only, no logos or marks, no instructor name, persona or credit, mascot hidden | audit below | **PASS** |
| **Positioning (new)** | every mention of meetings, recaps, AMI (or an AMI meeting ID) or C4 sits in Methods or Evaluation, in a scene tagged "test case"; the executive summary has none | **110 of 110 mentions OK** (10 spoken, 100 on screen across 12 scenes, B09–B20); summary: **0**. `positioning-audit.md` quotes every one | **PASS** |

## Toolkit gates (brutalist.art @ `cd4bf20` with my outro patch)

| Gate | Result | Where |
|---|---|---|
| F — paperwork exists | PASS | `../FACTCHECK.md`, `../SHOTLIST.md`, `../PROMPTS.md` |
| factcheck (content of F) | clean: 81 rows, 21 of 21 beats covered | `factcheck_check.txt` |
| L — beat-mix lint | clean | `art-run-18.log` |
| A — static pre-flight | clean, 0 warnings, all 20 scenes | `gates-AWB-final.txt` |
| W — WCAG contrast, margins, text overlap | clean, all 20 scenes | `gates-AWB-final.txt` |
| B — layout audit (`--curve-strict`) | CLEAN, all 20 scenes | `gates-AWB-final.txt` |
| V — frame-level visual QC | 0 BLOCKER, 0 MAJOR (42 frames), on the review cut and again on the clean master (`--mp4`) | `gate-v-REPORT.md` (clean master) |
| T — typography (size, overflow, contrast, kerning) | PASS, 21 of 21 beats | `TYPECHECK.md` |
| Bookends (outro handle = `channel_title`, no subline) | PASS | `bookend_check.txt` |
| Verified master | `ready`, SHA-256 matches | `master.verified.json` (a copy of the toolkit's `exports/landscape/*.verified.json`) |
| My frame-by-frame text-overlap check (every frame, 24 fps) | 20 of 20 scenes, 0 overlaps | `overlap-check.txt` |

## Positioning audit (new gate)

`../positioning_check.py` reads every narration sentence from `../beat_sheet.json` and every string visible on any frame of any scene (`../strings_dump.py`, 24 fps). It writes `positioning-audit.md`, which quotes each mention with its beat, part, time and verdict.
- **Narration:** 10 sentences mention the test case; all are in Methods or Evaluation.
- **On screen:** 100 strings mention it; all sit in B09–B20, and each of those scenes carries the "test case" tag.
- **Executive summary (B01–B03):** 0 references, spoken or on screen.
- **First minute:** what Readback is for, heard by 0:40:
  - 0:00 "Every AI feature ships against acceptance criteria a PM wrote."
  - 0:04 "Those criteria become a rubric: the checklist an AI judge grades the output against."
  - 0:09 "When a judge reads a criterion differently than the PM meant it, the eval passes, and the wrong behaviour ships."
  - 0:18 "And because evals are becoming the launch gate for AI features, a misread criterion ships wrong behaviour at scale, with a passing score attached."
  - 0:29 "Readback will find the criterion the judges read differently, and ask the PM what they meant, before anyone trusts the score."
  - 0:35 "It's module one of a bigger vision: a copilot for what PMs write for AI."
  - 0:39 "Readback is planned; nothing has run yet."

  The three vignettes (a support-reply bot, a document summariser, a search answer) are on screen from 0:15 to 0:28.

## Label audit

**Corner tags (top right, `#6B675C`, 4.9:1 on the stage):**
- "planned": the poster, B03, B08.
- "illustration": B01, B02.
- "planned · vision": B03's vision, B20.
- "test case": B09–B11, B15.
- "planned · test case": B12–B14, B16–B19.

**Constructed material:**
- B10: `CONSTRUCTED · my recap prompt`.
- B11: `CONSTRUCTED · rubric-v0.md`, with C4 in plain English (mapped in `../CLAIMS.md`).
- The B02 vignettes are CONSTRUCTED illustrations, tagged "illustration".

**Real material, with source and date:**
- B04–B07: `per their public docs · checked 14 Oct 2026`, under the title "From the tools I checked".
- B09: `AMI corpus · CC BY 4.0` and `data: case-study/data/sample/selection.csv`.
- B10: `AMI ES2007a transcript · CC BY 4.0`, `Claude · claude-opus-5-5`, then `real output · claude-opus-5-5 · 14 Oct 2026` and `10 real recaps · claude-opus-5-5 · 14 Oct 2026`.
- B11: `AMI ES2007a · CC BY 4.0`. AMI's DECISIONS list is the reference answer, not labels.
- B14: `ES2010b · AMI · CC BY 4.0`; `real recap · claude-opus-5-5 · 14 Oct 2026`; "AMI's DECISIONS list: “will consider including … a locator function”".
- B15: `a tick means set up on this Mac · status as of 23 Nov 2026`. The three columns keep the verified wording.

**Planned material:**
- Drawn dashed grey, with every value shown as "—". My human labels always read as mine and planned.
- B19: "Result: will be measured · nothing has run as of 23 Nov 2026" and "a failed check goes on the scorecard too".
- B03: the status line "Readback is planned · nothing has run yet".

Checked on `contact-01.png`, `contact-02.png` and `../storyboard.png`.

## Numbers audit

Every on-screen number is listed with its source in `../CLAIMS.md` (O01–O18). The new ones:
- the ES2010b timestamps [00:20:44] and [00:20:52] (`ES2010b/transcript.txt`, `feature-run/ES2010b.json`);
- "check 1–3" (`../EVAL-PLAN.md`; drawn as planned);
- "module 1" (`PROJECT-BRIEF.md`, later modules; vision).

The vignettes carry no numbers.

## Brand and persona audit

- **Prior work:** Maxim AI, orq.ai and GitHub Spec Kit are plain text. `scenes.py` has no image, SVG or logo objects (no `ImageMobject` or `SVGMobject`). The "not found" claims are scoped to the tools I checked.
- **Other brands:** no marks for Google, Zoom, Microsoft or Anthropic. "Claude" appears only as a model name, in text.
- **Persona:** no instructor name, persona or credit anywhere.
- **End card:** "Readback.", "Check that AI judges read your acceptance criteria / the way you meant them.", "Aravind Ravi · INFO 7375" and "read by a synthetic voice". The mascot is hidden. The value line and credit come from new `tagline` and `credit` props in my outro patch (`../../../toolkit-patches/ClaudeTitleOutro-handle-hideMascot-polarity-bg-tagline.patch`). `subline` stays empty, so the bookend gate's rule still holds.
- **First beat:** the toolkit's compile step prints the channel title ("Aravind Ravi · INFO 7375") centred at the bottom for the whole first beat, poster frame included. That is the only place my name appears before the end card, and the synthetic-voice credit is no longer on the opening frames.
- **Cold open:** none, by design (recorded in `bookend_exempt`).

## Speech-to-text on the full film

`../stt_check.py` (faster-whisper small.en) transcribes the whole soundtrack and compares it with the script in one diff. It normalises formatting only: numbers, hyphens, punctuation, quote marks, spacing and spelling (Spec Kit / Speckit, re-measure / remeasure, co-pilot / copilot, behavior / behaviour), and the spoken spellings "Reed-back" and "Ork dot AI". It also transcribes every beat's own clip alone. Results (`stt-full-master.txt`, 732 script words, 732 heard):

| Beat | Film time | Script | Full film | Its own clip, alone |
|---|---|---|---|---|
| B06 | 1:04.6 | "**GitHub's** Spec Kit" | "**GitHub** spec kit" | matches |
| B02 | 0:20.8 | "because **evals** are becoming the launch gate" | matches | "because **the valves** are becoming…" |
| B13 | 2:23.0 | "every recap: **Claude**, a second provider's model" | matches | "every recap, **clawed**, …" |

Every "Readback" is heard as "read back" or "readback", and "Aravind" (end card) is heard correctly.

## Not done in this revision

- **P1 item 9 (Methods and Evaluation content scaled ~1.3–1.4×, type floor ~34 px):** not done. Most Methods and Evaluation frames already span the full width (the method strip, ten meeting cards, the scorecard), so a 1.3× scale needs a per-scene re-layout. That didn't fit before the stop.
- **What did change for item 9:** the section bar is gone, B10's transcript and recap are hero-size (52 pt), B15 is regrouped into three columns, and Gate V's fill check passes on every sampled frame.
