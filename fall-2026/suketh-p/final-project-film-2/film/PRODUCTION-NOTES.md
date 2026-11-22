# PRODUCTION-NOTES — Fine Print (final project film), DRAFT build

Written by Claude Code (a build subagent) on 2026-11-21, 18:54–22:30 EST. The narration is the main session's script
("NARRATION FINAL", 19:16), approved by the student as a draft; B17 is the student's own bar, added after that
approval. Nothing was published or uploaded, and no git commands were run.

## 1. Result

- Master: `exports/landscape/fine-print-film.mp4` (3840×2160, 24 fps). Captions: `exports/landscape/fine-print-film.srt`.
  It replaces the 19:36 draft master (233.75 s: no B17, before the pronunciation fix and the review fixes in §1b).
- **Runtime:** narration 254.05 s measured; the master timeline is **254.46 s** (each beat rounded up to whole frames,
  as `compile.py` does). Limit 300 s: met.
- **Part 1 ends at 47.08 s** (end of B03; narration-only sum 47.05 s). Limit 60 s: met. **B17 starts at 226.08 s.**
- `qc-sheet.png`: one frame at 85 % of each beat of the master, labelled (made by `make_qc_sheet.py`). The toolkit's
  own midpoint sheet from the first review cut is kept as `gate-reports/qc-sheet-review-midpoints.png`.

| Beat | Part | Narration (s) | Frame-rounded (s) | Starts at (s) | Ends at (s) |
|---|---|---:|---:|---:|---:|
| BIDEA | 1 · What and why | 11.083 | 11.083 | 0.00 | 11.08 |
| B01 | 1 · What and why | 14.123 | 14.125 | 11.08 | 25.21 |
| B02 | 1 · What and why | 10.411 | 10.417 | 25.21 | 35.62 |
| B03 | 1 · What and why | 11.435 | 11.458 | 35.62 | **47.08** |
| B04 | 2 · What exists | 13.653 | 13.667 | 47.08 | 60.75 |
| B05 | 2 · What exists | 18.923 | 18.958 | 60.75 | 79.71 |
| B06 | 2 · What exists | 14.699 | 14.708 | 79.71 | 94.42 |
| B07 | 3 · How | 14.805 | 14.833 | 94.42 | 109.25 |
| B08 | 3 · How | 12.821 | 12.833 | 109.25 | 122.08 |
| B09 | 3 · How | 10.261 | 10.292 | 122.08 | 132.37 |
| B10 | 3 · How | 11.307 | 11.333 | 132.37 | 143.71 |
| B11 | 3 · How | 12.096 | 12.125 | 143.71 | 155.83 |
| B12 | 3 · How | 17.045 | 17.083 | 155.83 | 172.92 |
| B13 | 3 · How | 15.339 | 15.375 | 172.92 | 188.29 |
| B14 | 4 · Did it work? | 9.835 | 9.875 | 188.29 | 198.17 |
| B15 | 4 · Did it work? | 13.611 | 13.625 | 198.17 | 211.79 |
| B16 | 4 · Did it work? | 14.251 | 14.292 | 211.79 | 226.08 |
| B17 | 4 · Did it work? | 19.456 | 19.458 | **226.08** | 245.54 |
| B18 | 4 · Did it work? | 5.483 | 5.500 | 245.54 | 251.04 |
| BOUT | outro | 3.411 | 3.417 | 251.04 | 254.46 |

## 1a. After the draft: pronunciation fix and B17

- **Pronunciation.** The first build's Whisper transcript (`gate-reports/whisper-check.txt`) heard "Jobscan" as
  "Jobskin" (B05), "Anthropic" as "and thropic" (B08) and "an either-or rule" as "in either a rule" (B16).
  `fix_pronunciation.py` re-voices only those beats, handing the voice a respelling ("Job-scan", "Ann-throppick",
  "either or") through the toolkit's own engine, normaliser and mp3 writer; `narration_text`, captions and screen keep
  the real words. Each respelling was chosen by voicing candidates in the full sentence and transcribing them.
  The toolkit's lexicon (`runtime/pronunciation/*.json`) lives inside the toolkit, which this reel does not modify, so
  the override is reel-local, like `name_voice.py`. `build_audio.sh` runs it after `name_voice.py`. Check: Whisper
  now hears **Jobscan, Anthropic and "either or"** (`gate-reports/whisper-check-pronunciation.txt`: PASS ×3). A full
  `bash build_audio.sh` in a scratch copy reproduced all 19 then-existing mp3s **byte for byte** (name fix included).
  B05 grew 0.02 s; B08 and B16 kept their length. B05, B08 and B16 were re-rendered (old clips in
  `_superseded/pron-fix/`) and passed Gates A, W and B again (`art-run-4-pronunciation.log`).
- **B17 (the student's bar).** `scene_b17_bar.py` is pasted into `scenes.py` only when the sheet has B17, so no
  wordless B17 could ever be rendered and slotted. Every word comes from the beat's `bar_lines` (copied by
  `make_scene_data.py`; the build stops if a field is missing): a measuring bar with ticks (no numbers on it) and two
  zones, a "worked if" column with ink checks, a "didn't work if" column with ink crosses, and the footer. Lines too
  long for a column are set on two rows at a word boundary; no word is changed. Stamp `my bar · set Nov 21`, part tag
  `4 · Did it work?` (the stamp is now `plan · my bar, set Nov 21`). Voiced as written (`generate_audio_kokoro.py --only
  B17`); Whisper heard it word for word.

## 1b. Review fixes (independent review of the 19:38 draft), all made before this master

1. **B07, B09:** the reader (inspection lamp) is not built, so it is drawn faint (40 % opacity, as in B03) with a small
   grey `plan` tag in both beats, though their stamps say `real`.
2. **B03:** `172 new` became `172` / `not seen on Nov 8` (two rows). **B08:** narration now ends "…one hundred
   seventy-two postings it hadn't seen on November eighth" (main session's edit); B08 was re-voiced (with the Anthropic
   fix) and re-timed, and its label is `172 not seen on Nov 8`. The terminal's own `new=83` etc. are verbatim.
3. **B11:** two sign-off sheets, one per agent: `JS1: withheld` / `→ signed` and `JS2: withheld` / `→ signed`.
4. **B16:** the second scanner is gone (a true quote passes the code quote check). The predicted failure is caught by
   the student's own hand label: a label card written by the quill, `my label: preferred`, and an ink cross on the predicted slip.
5. **B17:** stamp `plan · my bar, set Nov 21` (from the sheet).
6. **BOUT:** credit line, read from BOUT's `visual_intent` by `make_scene_data.py` and set on two rows after its first
   " · ": "Script and pictures by Claude Code from my records, approved by me · synthesized voice (Kokoro am_eric) ·
   detail: the appendix".
7. **Terminal font:** **PT Mono** (SIL Open Font License 1.1; shipped with the toolkit, `runtime/fonts/PT_Mono/OFL.txt`)
   replaces Menlo in B08, B09 and B10. PT Mono is wider for its x-height, so a window now holds 63 columns at a 43.0 px
   x-height (GATE T floor 41 px). Re-rendered: B03, B07, B08, B09, B10, B11, B16, B17, BOUT (old clips in
   `_superseded/review2/`).

## 2. Pipeline (October's, from `../../Assignment 4/final-project-film/BUILD-PROMPT.md`)

- `../brutalist.art` is a symlink to `../Assignment 4/brutalist.art` (toolkit at `519fcbb`, venv `.venv`, Python 3.12.7).
- Copied from October unchanged except docstrings/comments: `build_audio.sh`, `finish_audio.py`, `name_voice.py`,
  `make_srt.py` (all read the slug from the sheet). `build_scenes.py` also runs `make_scene_data.py` and pastes its
  `scene_data.py` into `scenes.py` (Gate A copies only `scenes.py`), as the brief asked.
- New: `make_scene_data.py` (stamps, part tags and terminal rows from the sheet and the saved logs),
  `scenes_body.py` (18 drawn scenes), `make_qc_sheet.py`, `SHOTLIST.md`, `PROMPTS.md`, `FACTCHECK.md` (symlink to
  `../FACTCHECK.md`, for Gate F and `factcheck_check`), `terminal_replay_record.json` (what each replay kept/dropped).
- Commands, in order: `python3 make_sheet.py`; `bash build_audio.sh` (full voice, 18:58); after each narration update,
  `generate_audio_kokoro.py . --only <changed beats>` then `finish_audio.py` (logs `gate-reports/build-audio-*.log`);
  `python3 build_scenes.py`; `../brutalist.art/art run . --height 2160` (three runs, see §5);
  `../brutalist.art/art final . --height 2160 --out exports/landscape`; `python3 make_srt.py`; the checks in §5.
- Audio: Kokoro `am_eric`; BIDEA and BOUT re-voiced by `name_voice.py` (the student's Devanagari guide) and padded by
  `finish_audio.py` (0.8 s lead, 1.0 s tail).

## 3. What was built, per beat

Every drawn beat except BOUT shows its stamp (top left; ink dot for `real · …`, terracotta dot for the plan) and its part
tag (top right), copied from `beat_sheet.json` by `make_scene_data.py`. Props are the toolkit's approved 25 originals
plus kit primitives (paper, slips, quill, Iso boxes, checks, crosses). Full table: `SHOTLIST.md`. Each beat's
`visual_intent` and `show` in `make_sheet.py` were rewritten to describe what is drawn (narration, stamps and part tags
untouched; checked by an AST comparison).

- **BIDEA**: the toolkit's Remotion hesitant writer, unchanged ("Will this company sponsor me" → "posting rule me out").
- **B01**: eight posting pages; title lines draw; a reading lens sweeps; six get an ink cross over a darkened line, two
  stay; "8 real postings", "6 of 8", "2–12+ yrs or no new grads". No sponsor ticks.
- **B02**: inspection lamp ("Fine Print") lowers; a sentence slip ("exact sentence"); approval stamp stays raised
  ("my approval").
- **B03**: three open crates fill (two tall stacks, one page) with "83 · 88 · 1"; "172" / "not seen on Nov 8";
  "watcher: runs"; the lamp drawn faint with "reader: next".
- **B04**: A3 binder with "?"; two LinkedIn pages ("Qualcomm · TikTok") split into "minimum" / "preferred" blocks;
  empty "sponsorship" slots.
- **B05**: four cards, 2 × 2, labels exactly as requested: "H-1B approvals · denials · per employer", "match score ·
  missing keywords", "experience, education: required or preferred?", "skill found · exact wording missed". No logos.
- **B06**: scanner checks a sentence slip; "required" / "preferred" trays; "sponsorship: unknown" tag; stamp raised.
- **B07**: the lamp (reader; faint, grey `plan` tag) lands on three crates ("jobwatch", three terracotta lights); gate ("allow-list") passes three
  feed slips and stops a fourth; parcel closes with a terracotta seal ("fingerprint"); "fictional applicant" card.
- **B08 / B09 / B10**: terminal replays (§4). B08 adds "172 not seen on Nov 8" under the run window; B09 adds the "rejected"
  crate, the empty "kept" tray, a "?" and the arriving lamp (faint, `plan` tag); B10 is the two windows only.
- **B11**: quill writes the rules page ("rules first"); workstation ("Claude Code"); the stamp beside two sign-off
  sheets: "JS1: withheld → signed", "JS2: withheld → signed".
- **B12**: four dated stations ("Nov 25", "Dec 1", "Dec 13", "Dec 20") filled at their dates by the lamp, scanner,
  stamp and experiment bench; an ink line and terracotta dot advance along a rail.
- **B13**: "no API credits" tag; plug into socket ("Claude Code login"); page stack with a check ("27 judged · Oct 31");
  workstation ("no accounts · laptop"); budget slots with a grey "plan" tag ("daily budget"), a token lifting to an
  ink cap line.
- **B14**: three pages marked by the quill; two pulled from the "rejected" crate; two locked into the "held out" vault;
  the rest to "development".
- **B15**: four stations: "quote found", "misreads", "two errors" (crates "unsupported clearance" / "false exclusion"),
  "?" with "I cannot tell".
- **B16**: five slips cracked one per named case ("at least 5"); a slip set apart ("predicted", "'5 years preferred'" /
  "→ read as required") caught by the student's hand label ("my label: preferred"), not by a scanner.
- **B17**: the student's bar (§1a).
- **B18**: a small iso stack ("my set") and a towering one ("every posting").
- **BOUT**: lamp, "Fine Print", "Suketh Reddy Produtoor", and the exact line "Script and pictures by Claude Code from
  my records, approved by me · synthesized voice (Kokoro am_eric) · detail: the appendix", set on two lines (broken
  after "me ·"; no character changed). No handle, instructor name, persona or portrait anywhere.

## 4. Terminal replays (B08, B09, B10): sources and every change

Built only by `make_scene_data.py`: it checks each source against `../evidence/terminal/SHA256SUMS`, checks each
`.json` line by line against its `.txt`, applies the changes below, then refuses to build if any row contains `/Users`,
the user name, `Desktop`, `Prompt Engineering`, `fork/fall-2026` or `suketh-p`, or if a quoted number is missing.
Prompt lines for the Nov 21 logs are `js2-loop-tools-diff % <command>` (the `.json`'s `cwd_shown` and `command`, the
same as the first line of each `.txt`). Font: **PT Mono** (OFL 1.1, from the toolkit), x-height **43.0 px** at 2160p, 63 columns per window. (The 19:38 draft
used Menlo at 43.5 px and 69 columns; Menlo is not OFL-licensed.)

- **B08**, window 1, `tests-2026-11-21.json` (SHA-256 `8d296e78…`): (a) shows the prompt, `Ran 164 tests in 4.180s`,
  the blank line and `OK`; drops the 164-dot progress line and the dashed rule (both wider than the window).
- **B08**, window 2, `film-normal-noapproval-2026-11-21.json` (`7184769a…`): (a) shows the prompt and the three board
  lines; drops the status line and the `used 3 boards…` line (both shown in B10) and the `evidence:` line. (b) the
  three board lines' space runs collapsed to two spaces (`  greenhouse/anthropic  usable  jobs=635 new=83`, `…jobs=895
  new=88`, `…jobs=32 new=1`). (w) the prompt (88 characters) wraps after 63.
- **B09**, `film-rule-count-2026-11-21.json` (`0b5a503f…`): every line shown (prompt, `172`). (w) the prompt (92
  characters) wraps after 63.
- **B10**, window 1, `film-normal-noapproval-2026-11-21.json` (`7184769a…`): (a) shows the prompt, the status line
  (`run film-normal-noapproval-2026-11-21: incomplete — the state was not saved: no approval was given for this run;
  results are provisional`) and `used 3 boards, 3 requests, 1.644 s; state advanced: False`; drops the three board
  lines (shown in B08) and the `evidence:` line. (w) the prompt (2 rows) and the status line (136 characters, 3 rows) wrap every 63.
- **B10**, window 2, `2026-11-08-normal-1-run-by-student.txt` (`63aa9b83…`; this log has no `.json`, so its session
  lines after the `---` header are read from the `.txt`): (a) shows the command line, `run 2026-11-08-normal-1:
  finished — every board was usable` and `used 3 boards, 3 requests, 1.948 s; state advanced: True`; drops the header
  note, the three board lines and the `evidence:` line. (c) `cd "/Users/…/js2-loop-tools-diff"` shown as
  `cd ~/…/js2-loop-tools-diff`. The prompt stays `$`, as in the log. (w) the command line (137 characters after (c))
  wraps every 63 (3 rows).

(w) is a hard wrap at the window's width, the way a 63-column terminal shows a long line: no character is added, removed
or changed. **It is not in the brief's list (a)–(c); see §6.** Numbers on screen, all from the logs: 164 tests; jobs
635 / 895 / 32; new 83 / 88 / 1; 172 (`not_relevant` count); `state advanced: False` (Nov 21) and `True` (Nov 8). "172"
in B03 and B08 is the sum 83 + 88 + 1, labelled "not seen on Nov 8" (what jobwatch's "new" means). Full kept/dropped record:
`terminal_replay_record.json`.

## 5. Gates and checks

Logs and reports are in `gate-reports/` (and `TYPECHECK.md`, `MASTERCHECK.md`, `LOUDNESS.md`, `SRTCHECK.md`,
`_qc/REPORT.md` in this folder). Nothing was skipped, waived or run with `ART_QC=0` / `ART_STRICT=0`.

| Gate / check | Result | Where |
|---|---|---|
| Gate F (paperwork: FACTCHECK.md, SHOTLIST.md, PROMPTS.md present) | PASS | `art-run-1…3.log` |
| Gate L (beat-mix lint), Gate SHAPE | PASS (clean; not a finance reel) | `art-run-*.log` |
| Gate A (static pre-flight, all 18 scenes, from a folder holding only `scenes.py`) | PASS, 0 warnings | `art-run-*.log` |
| Gate W (WCAG/margins/overlap, static) | PASS, all B-classes clean; BOUT by hand as `B19_Outro`: clean | `art-run-*.log` |
| Gate B (post-render layout, strict) | PASS for all 18 after two fixes: run 1 stopped B11 ("withheld" box reached x 6.40 > 6.30), run 2 stopped B18 ("every posting" reached 6.35); both labels moved left and re-rendered | `gateB-run1-B11-warning.md`, `gateB-run2-B18-warning.md`, `art-run-3.log` |
| B16 re-render before the final | GATE T's own checks, previewed on the slotted clips, found B16's ink crack inside an ink-edged slip read as two overlapping labels (§8.6b). The slips got grey edges; B16 was re-rendered with the same `manim -qk --fps 24 -r 3840,2160` command `run.sh` uses, then Gates A, W and B were run on it by hand: clean | `b16-rerender-*.log`, `gateB-B16-rerender.md` |
| Gate V (review cut, 38 frames at 50 % and 85 %) | PASS, 0 blocker / 0 major | `gateV-review-run3/` |
| **GATE T** (art final) | **PASS**, 19/19 beats, 0 FAILs; smallest text run 50–61 px (floor 41) | `TYPECHECK-art-final-1.md`, `art-final-1.log` |
| Gate V (final candidate) | PASS, 0 blocker / 0 major | `gateV-final-REPORT.md` |
| Master check | PASS: 3840×2160, 24 fps, yuv420p, h264, audio, 233.75 s = sheet | `MASTERCHECK.md` |
| Loudness | PASS: −22.00 LUFS, true peak −7.57 dBTP, no silent beat | `LOUDNESS.md` |
| Sharpness | PASS: 19 beats, median LV 285.5 (run on a scratch folder named after the slug holding only the master, because the check otherwise picks the review cut) | `SHARPNESS.md` |
| SRT check | PASS: 84 cues, 0 errors | `SRTCHECK.md` |
| **factcheck_check** | **FAIL (FC-1)**: "no claims table found … needs a markdown table with a Beat column and a Verdict column". `../FACTCHECK.md` has Beat / Claim / Record / **Tense** columns, no Verdict. Not fixable by a visual change, and PROJECT docs are outside this build's write scope | `postchecks-1.log` |
| Frames at 85 % (`qc-sheet.png`) | Every beat's key picture is on screen at 85 %; no home path or user name in any frame | `qc-sheet.png` |

Master SHA-256: `bcf27cd16a6243d67c81bb7b2a27d9cc89e32730eaf53e1cd04b98068a2297a9` (233.75 s, 24.3 MB);
captions SHA-256: `f76771591d6dc3dd72c49518b2fdf91a27b74b3ce272aad09aa792d7d744c76b`. The review cut
`fine-print-film-slate.mp4` predates the B16 fix. Advisory lines printed by `art`: SKIN LINT on BIDEA (cold open is
the hesitant writer) and BOUT (not `ClaudeTitleOutro`), both expected under `bookend_exempt`.

## 6. Deviations and decisions for the student

1. **Terminal wrap (w).** Four lines are longer than any window that keeps GATE T's 41 px floor (88–137 characters;
   in PT Mono at 43.0 px x-height, 63 fit). They are hard-wrapped at the window edge. The alternative within (a)–(c) is to drop
   them, which would remove both run commands, the grep command and the Nov 21 status line. Decide: keep the wrap, or
   drop those lines.
2. **Nov 8 prompt kept as `$`.** The brief's prompt form `js2-loop-tools-diff % …` would be a prompt the log never
   showed (the student replaced theirs with `$`). Decide whether that is acceptable.
3. **BIDEA shows no part tag** (and no stamp; the sheet has none). It is the toolkit's Remotion bookend; its only text
   slot (`banner`) is an 18-px, 62 %-opacity chip that would fail GATE T. Adding a tag needs a toolkit change. BOUT has
   no stamp or tag in the sheet, so none is drawn.
4. **B01 crosses are ink, not terracotta** (house rule: terracotta never marks or text; GATE T reads it as accent text).
5. **More labels than the skill's "two or three"** in B03, B04, B05, B12, B13, B15: the sheet and the main session asked
   for those words (counts 83 · 88 · 1, the four tool labels, the dates, the resources).
6. **B09 "kept: 0"** is drawn as an empty tray, not as text: the 0 comes from `film-rule-relevant-2026-11-21`, which B09
   does not replay.
7. **Whisper check** (`gate-reports/whisper-check.txt`, local faster-whisper small.en): words match except names, and a
   few places worth hearing before approval: "Jobscan" heard as "Jobskin" (B05), "Anthropic" as "and thropic" (B08),
   "an either-or rule" as "in either a rule" (B16), "it ended incomplete, state unchanged" as "in complete state" (B10),
   "misreads" as "Ms. Reed's" (B15). Narration was not changed. The first three are now fixed (§1a); the last two
   were left as voiced.
8. **Not labelled DRAFT on screen**; the sheet's metadata says `draft: true`.
9. **Gate W reads only `Text()` calls written inside a scene class**, so it saw few of this film's labels (they come from
   helpers); Gate B (post-render, every label's real box) is the check that covered them. Gate W skips `BOUT_Outro` by
   its name filter; it was run by hand on a copy renamed `B19_Outro`: clean.
10. Runtime 233.75 s, about 36 s under PLAN's ~270 s target (still under the 300 s cap).
