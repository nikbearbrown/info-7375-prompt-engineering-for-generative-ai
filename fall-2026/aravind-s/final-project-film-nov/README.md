# Final Project Film: Klaxon in four parts

- **Student:** Aravind Sundaravadivelu (`aravind-s`)
- **Course:** INFO 7375 Prompt Engineering for Generative AI, Fall 2026
- **Assignment:** Final Project Film (Canvas assignment 3551817, 25 points), Professor Nik Bear Brown's brief of
  2026-11-18, due Mon 2026-11-23, 11:30 PM ET
- **Project:** Klaxon, an AI on-call engineer for a payments system, his final project for INFO 7375 and CSYE 7374.
  Public repo: https://github.com/AravindKumar2504/klaxon (the film uses its `main` at `fef450b`)
- **Film:** `klaxon-final-project-film.mp4`, 4:34.6, 1920x1080 at 30 fps, H.264 and AAC, with soft English captions
  (their text is also in `captions.srt`)
- **Voice:** synthetic (Kokoro, voice `am_onyx`), disclosed in the film's first line

## The four parts, in the brief's order

The brief asks for four parts in this order: an executive summary (what the project is and why anybody should care,
with no "how"), an introduction (what others have done, what they got, and why this project still matters), the
methods (the plan step by step, the data source, and whether the token credits, accounts, access and compute are in
hand, with the detail there and in an appendix), and the evaluation (what is measured, and what result means it
worked or did not).

| Part | Starts | Beats | Where each question is answered |
|---|---|---|---|
| 1. Executive summary | 0:00 | B01 to B04 | What Klaxon is (0:07.9). Why it matters (0:21.6 and 0:37.0): in a real run, the other alert rules stayed quiet while the books were $461 ahead of the payment provider's, so an incident can look healthy while the money is wrong |
| 2. Introduction: what others have done | 0:47.8 | B05 to B08 | Who builds AI SREs and what they raised (0:47.8); what they got, a vendor's own count and a research benchmark (1:05.2); the open-source HolmesGPT (1:21.2); why Klaxon still matters: after a fix, code, not the model, checks the money (1:34.3) |
| 3. Methods | 1:46.1 | B09 to B15 | The data source: a synthetic payments system with six faults injected on purpose (1:46.1); the method step by step, on a real week 7 run (2:02.4, 2:15.2, 2:29.3); what is built and what is planned by Dec 4 (2:41.0); the resources: no API key and no token credits, the university Claude seat, compute (2:52.4); who did what (3:11.3) |
| 4. Evaluation | 3:20.1 | B16 to B20 | The eight test cases (3:20.1); the three things measured and how each is graded (3:30.5); the first results (3:47.3); what did not work yet (3:58.5); what result means it works or fails (4:13.6) |
| Appendix | 4:30.6 | B21 | A silent card with the sources and the AI use; the full detail is in this folder (SOURCES.md, FACTCHECK.md, build/) |

The film ends at 4:34.6. Every beat's start and length: `TIMINGS.md`.

## Real footage, cards, results and plans

- **Real footage:** Klaxon's own web panel (B02 to B04, B08, B10, B12, B17 to B19), one of the five screenshots the
  panel saved during the week 7 live run (B11), a terminal card set from the real output of `make eval-cases` (B16),
  and two public GitHub pages of the Klaxon repo, captured signed out (B13, B15). The panel was served from a copy of
  `fef450b`; it only reads saved runs.
- **Cards:** the title (B01), the prior work as plain text with its sources (B05 to B07), one flat diagram (B09), the
  resources (B14), works if / fails if (B20) and the sources (B21).
- **Results** come from Klaxon's records at `fef450b`: the week 7 live run and the week 5 evaluation (48 runs).
- **Plans are said as plans:** week 8 (a multi-agent version, the webhook receiver in Go, a 72-run comparison) and
  the week 9 safety pass are "planned by December 4th", because none of it was merged on `main` when the film was
  made (`fef450b`, and still on 2026-11-22 at the final render). Most of week 8 was merged on 2026-11-23 (`142f217`),
  after the film was finished; the film is left as approved. The missing held-out fault is stated as a limit (B19).

## His decisions

- The film's form, chosen on 2026-11-20: real footage of Klaxon, a few title cards and a synthetic voice that the
  first line discloses.
- How the film states his part (B15), at his answer on 2026-11-20: Claude Code wrote the code under his direction,
  while he made Klaxon's decisions, reviewed and accepted every week and typed every approval himself.
- The missing held-out fault stays a stated limit (B19) rather than a late addition to the plan.
- The film is posted in this repo, with a FRICTIONAL.md whose author entries come from his own notes, organized by
  Claude Code at his request.
- He approved the film with no changes on 2026-11-22; the final render only drops "(review cut)" from its title tag.

## AI use

Claude Code researched, wrote the script, captured the footage and built the film at his direction; the voice is
synthetic (Kokoro am_onyx), disclosed in the film's first seconds.

## Contents

| File | What it is |
|---|---|
| `klaxon-final-project-film.mp4` | The film: the final render of 2026-11-22, after Aravind approved the review cut with no changes (the same video, audio and caption streams; only the title tag dropped "(review cut)"); SHA-256 `7ee3328eed1d78cb7585eafe03d1f9dc1eeb5b79ac1aaacc155a0e90f7364ed8`. Force-added, since the repo ignores mp4 files |
| `captions.srt` | The text of the soft captions |
| `SCRIPT.md` | The script: 21 beats in the four parts, with the caption and spoken text of each |
| `FACTCHECK.md` | Every narrated claim (66), its verdict and its source |
| `SOURCES.md` | Klaxon's records and the prior work, each read on 2026-11-20 |
| `SHOTLIST.md` | The footage for each beat and how it was captured |
| `TIMINGS.md` | The measured start and length of every beat and part |
| `FRICTIONAL.md` | Claude Code's labeled build record, and the author's entries (his notes, organized by Claude Code) |
| `beats.py`, `beats.json` | The narration and caption text that the build reads (`beats.py` writes `beats.json`) |
| `build/scripts/` | The seven scripts that make the cut: `capture.py`, `measure.py`, `tts.py`, `stage.py`, `assemble.py`, `contact.py`, `make_script_md.py` |
| `build/capture/` | The captured footage: 11 PNGs (the panel's pages, the two GitHub pages, and the panel's five saved screenshots in `saved/`), the boxes of what the film crops and highlights, and the `make eval-cases` output |
| `build/audio/durations.json` | The narration lengths, so the frames rebuild without the voice model |
| `build/BUILD-NOTES.md` | The rebuild order and the environment variables it needs |

Left out on purpose: generated media and intermediates (the narration WAVs, the rendered cards, stills and frames,
the segment lists), which the scripts make again. Nothing from the course's video toolkit is included or copied.

## Rebuild

`build/BUILD-NOTES.md` has the steps. In short, from this folder, with `PW_PY` (a Python with Playwright), `TTS_PY`
(a Python with kokoro-onnx, numpy and Pillow) and `KOKORO_MODELS` (the Kokoro v1.0 model folder) set, and ffmpeg on
the PATH:

```bash
"$TTS_PY" build/scripts/tts.py        # the narration, one WAV per beat
"$PW_PY" build/scripts/stage.py       # every frame, from build/capture/
"$TTS_PY" build/scripts/assemble.py   # the film, its captions and TIMINGS, in build/out/
```

Checked on 2026-11-22 on a copy of this folder, after the final render: the three commands gave back the film byte
for byte (the same SHA-256 as above), with the same 20 narration WAVs, 51 frames, captions and timings, in 106
seconds. The frames alone need only
this folder (`stage.py` gave all 51 of them unchanged, without the voice model). The footage itself can be captured
again from Klaxon's public repo at `fef450b` (step 0 in BUILD-NOTES.md).

## Credits

- Project and film: Aravind Sundaravadivelu.
- Research, script, footage capture and build: Claude Code, at his direction.
- Voice: Kokoro v1.0 through kokoro-onnx 0.6.1, voice `am_onyx`.
- Tools: Playwright with headless Chromium (footage and cards), ffmpeg (the cut, with the captions as a soft track),
  Python with numpy and Pillow.
- Prior work cited in the film: TechCrunch, Goodwin, Dealroom, Traversal, Datadog, AWS, Microsoft, ITBench (Jha et
  al., ICML 2025), the CNCF blog and the HolmesGPT docs. The full list with links: `SOURCES.md`.
