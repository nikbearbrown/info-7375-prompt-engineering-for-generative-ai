# Final Project Film — A Supervised Job-Search Agent with Sponsorship Evidence

**Swathi Baba Eswarappa** · INFO 7375 Prompt Engineering and Generative AI · Final Project Film

A narrated explainer of my final project in the four required parts, in order:
executive summary (B01–B02), introduction (B03–B04), methods (B05–B08) and
evaluation (B09–B11). B05 is completed JS1–JS3 work, labelled **COMPLETED · JS3**,
with commit ids. Everything else is planned and labelled **PLANNED**. The
evaluation thresholds are labelled **PROPOSED TARGETS — NOT RESULTS**. The
student persona, Priya Nair, is fictional and labelled **FICTIONAL**.

| | |
|---|---|
| File | `BabaEswarappa_Swathi_INFO7375_FinalProjectPlanFilm.mp4` (+ `.srt` captions) |
| Runtime | **4:05.78 (245.78 s)**; Part 1 ends at 0:38.5 |
| Format | H.264 3840×2160, 24 fps, yuv420p; AAC 48 kHz stereo; −19.0 LUFS integrated, true peak −1.5 dBTP |
| SHA-256 (mp4) | `f702ec08fdc8c73ab5d29fd1a8981a181d56bc121da09e00d634a33338db849d` |
| Voice | Kokoro `af_heart`, matching my pitch film's final cut |
| Pipeline | Brutalist: Kokoro narration, Manim CE visuals, FFmpeg; free and local |

## Status

| Gate | Result | Report |
|---|---|---|
| Facts (every on-screen number from `data/facts.json`) | PASS | `qc_reports/facts_check.txt` |
| Labels (every drawn string word for word from `beat_sheet.json`) | PASS | `qc_reports/label_check.txt` |
| Toolkit Gate A (static scene check) | PASS, 11 clean | `qc_reports/gateA_static_scene_check.txt` |
| Toolkit Gate W (WCAG, margins) | PASS, 11 clean | `qc_reports/gateW_wcag_margin_check.txt` |
| Toolkit Gate B (layout audit) | 0 errors; 4 warnings, reviewed: three intended strike-throughs (B06, B07) and B03's two-line footer near the safe-area edge | `qc_reports/gateB/` |
| Week 1 frame-safety sweep (16 px) | PASS | `qc_reports/week1_qc_frames.txt` |
| Runtime gate (120–300 s) | PASS | `qc_reports/week1_build_mux.txt` |
| Toolkit Gate V (final frames) | PASS, 0 BLOCKER, 0 MAJOR | `qc_reports/gateV_final_frame_check_REPORT.md` |
| Upstream LOUDNESS | PASS | `qc_reports/upstream/LOUDNESS.md` |
| Upstream MASTER | PASS | `qc_reports/upstream/MASTERCHECK.md` |
| Upstream SRT | PASS, 83 cues | `qc_reports/upstream/SRTCHECK.md` |
| Upstream SHARPNESS | PASS | `qc_reports/upstream/SHARPNESS.md` |
| Upstream T (type) | PASS, 11 beats, 0 FAILs | `qc_reports/upstream/TYPECHECK.md` |

GATE MASTER plus Gate V stand in for "render integrity", as in my pitch film:
no gate with that name exists in the toolkit.

**Upstream gates:** the five upstream gate scripts were run from a local copy
taken from toolkit commit `519fcbb` (2026-10-12), with no git command. Gates
added upstream after 2026-10-12 were not run. GATE MASTER skips its duration
check because `clock_check.py` is not in that copy, as happened in my pitch film.

## Rebuild

```bash
./build.sh                    # facts -> narration -> Gate A/W -> scenes -> labels -> Gate B -> frames -> mux -> Gate V
./build.sh --mux-only         # skip narration and render; re-run every local gate and re-mux
build/run_upstream_gates.sh   # upstream LOUDNESS, MASTER, SRT, SHARPNESS, T -> qc_reports/upstream/
```

Exact commands and flags are in `BUILD-PROMPT.md`.

## Files

| Path | What |
|---|---|
| `beat_sheet.json` | 11 beats: narration (voice spellings) and on-screen spec |
| `NARRATION.md` | readable narration; the captions match it word for word |
| `PLAN-APPENDIX.md` | the plan the film summarises, with references |
| `data/facts.json` | every number shown on screen, with its source and spoken form |
| `scene.py` | 11 Manim scenes built on the `Beat` helper |
| `check_facts.py`, `check_labels.py` | the facts and label gates |
| `build.sh`, `build_mux.py`, `make_srt.py`, `qc_frames.py`, `build/*.sh` | build and gates |
| `qc_reports/` | every gate report, the master verification and the 6-second contact sheet |

## Media and git

The course repo's `.gitignore` ignores only `.mp4` and `.mp3` files, by
extension (`*.[mM][pP]4`, `*.[mM][pP]3`; checked with `git check-ignore -v`).
`build/` and `media/` are **not** ignored, so they were not copied into the repo.
The exceptions are the `build/` files that are part of the build or the evidence:
`build/render_all.sh`, `build/run_upstream_gates.sh`, `build/beat_sheet.orig.json`
and the label gate's inputs in `build/onscreen/`. The mp4 and the narration mp3s
stay local; submit the mp4 separately. `mp3/timings.json` is included because
`scene.py` reads it.

Left out of the repo copy for privacy:

- The 11 raw Gate B logs (`qc_reports/gateB/*.log`) contain my home-directory
  path. The `qc_reports/gateB/*.md` and `*.json` reports beside them carry the
  same results.
- In `qc_reports/upstream/MASTERCHECK.md`, my home-directory path in the
  "clock_check skipped" note is replaced with `~`. Nothing else in it changed.
