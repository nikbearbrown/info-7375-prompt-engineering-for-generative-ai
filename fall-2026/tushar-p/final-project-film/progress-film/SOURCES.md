# SOURCES

## Tools used

| Tool | Version | Role | Licence (where it was checked) |
|---|---|---|---|
| Brutalist toolkit (`nikbearbrown/brutalist.art`, local checkout `Brutalist-latest`) | commit `3a6d397` | Reel pipeline, QC gates, compile | No licence file (as in the October pitch); used as directed by the INFO 7375 course. Its instructor-persona skills, bookends, portraits and outro were not used. |
| Manim Community | 0.20.1 (ManimPango 0.6.1) | All scene animation (`scenes.py`) | MIT (package metadata) |
| Kokoro TTS, voice `am_onyx` | Kokoro-82M v1.0 weights via kokoro-onnx 0.6.1, run locally | Narration (`sentence_audio.py`), the same local voice as the October pitch; 0.25 s between sentences in v2 | Weights Apache-2.0 and kokoro-onnx MIT, as checked for the October pitch (its SOURCES.md, 2026-10-14). The model files were copied from the October checkout, not re-downloaded (SHA-256 identical). |
| faster-whisper, model `small.en` | 1.2.1, run offline from the local cache | Pronunciation check only (`gates/whisper_check.txt`); nothing from it is in the film | MIT (package metadata) |
| ffmpeg | 9.0.1 | Audio joins, measurement, muxing, frame checks | Not separately checked |
| Python | 3.12.14 (toolkit `.venv`, rebuilt Nov 23 from `requirements.txt`) | Runs the toolkit | — |

Also used: the macOS system fonts Menlo and the default serif. No stock footage, music, images, logos or paid generation. No API keys and no API calls.

## Source material shown in the film

The film is v2 (Nov 23, 2026). v1 was superseded the same day (see BEAT-PLAN.md); its clips, audio and export are kept outside this folder, in the toolkit reel's `_superseded/v1/`.

The REAL beats (B09, B11) show text captured on 2026-11-23 from my repo `~/Documents/agent-proving-ground` (public at https://github.com/tushar-patel28/agent-proving-ground; confirmed public by Tushar on Nov 23, 2026), read-only, at HEAD `f40f3a1`. The exact commands and full output are in `evidence/<capture>.txt`; the script that ran them is `evidence/capture.sh`. The capture files keep their v1 names (B6.txt … B13.txt); the table maps them to the v2 beats. `B12-v2.txt` was added on Nov 23 for v2 B12's third item. Lines that don't fit are cut with "…"; nothing is reworded. Grey annotations such as "(result line recorded in PLAN.md)" are mine.

| v2 beat | Capture | Source in the APG repo | Source date |
|---|---|---|---|
| B09 frame 1 | `evidence/B6.txt` | PLAN.md:120 (the `apg run 001` result line); trace `evidence/traces/20261112T053055Z-92239eb0.json` and its step list | 2026-11-12 |
| B09 frame 2 | `evidence/B7.txt` | `apg show traces/20261118T034327Z-b54f5cd6.json`, step 4 (contract B, held-out, 008) | 2026-11-18 03:43Z (Nov 17 ET) |
| B09 frame 3 | `evidence/B9.txt` | evidence/isolation/20261117-isolation-d29.txt | 2026-11-17 |
| B09 strip | `evidence/B13.txt` | PLAN.md:457–462 (M0–M5) | Nov 3 – Nov 18 |
| B11 frame 1 | `evidence/B11.txt` | evidence/compare/20261118-t51-a-vs-b.txt (totals; costs not shown) | 2026-11-18 |
| B11 frame 2 | `evidence/B12.txt` | docs/07-evidence.md:415; FAILURES.md F2 | 2026-11-18 |

The CONSTRUCTED beats are drawn. Their facts come from the same captures and from my October PROJECT-BRIEF.md (`../PROJECT-BRIEF.md`):

| v2 beat | Facts from |
|---|---|
| B03, B13 | `evidence/B13.txt` (git remote: the public repo URL; B13 also docs/01-brief.md:47, "Not a model benchmark") |
| B04 | October PROJECT-BRIEF.md:14 ("first sixty seconds"); `evidence/B6.txt` (the result-line format shown in the mock-up) |
| B06 | October PROJECT-BRIEF.md:38 (Go and Kubernetes new to me) |
| B07 | `evidence/B6.txt` (model, tools, check), `B7.txt` (policy, gate), `B9.txt` (no network, not root) |
| B08 | `evidence/B8.txt` (16 tasks, 11 + 5, split membership, `26b5305`); `B9.txt` (spend limit) |
| B10 | `evidence/B8.txt`, `B10.txt` (two prompts, `6d7bafe`) |
| B12 | `evidence/B13.txt` (docs/01-brief.md:40–41; PLAN.md:6, Dec 18); `evidence/B12-v2.txt` (docs/03-action-surface-map.md:108–113 and docs/07-evidence.md:517–519, Honest limits point 4: `os._exit(0)`, the gap item 3 closes) |

`evidence/B10.txt` is used for facts only; no v2 frame shows it.

## Tools named in the film (B05)

| Item | Wording in the film | Basis |
|---|---|---|
| E2B | "provides sandboxes for running AI-generated code" | October PROJECT-BRIEF.md §2, word for word |
| Langfuse | "records LLM traces and scores" | October PROJECT-BRIEF.md §2, word for word |

"Each solves one piece well. But a sandbox doesn't tell you whether the work is right, and a trace doesn't stop an agent from doing what it shouldn't." is my own characterisation. It was not checked against either product's documentation in this build (no network).

The v1 beat plan also named Runtime, Raindrop, oh-my-pi and a Drupal project. The October SOURCES.md lists Raindrop, Runtime and oh-my-pi under "Alternatives looked at" (Oct 13, 2026). As in the October film, only E2B and Langfuse are named in this film.

## What I made vs. what Claude contributed

- **Me:** Agent Proving Ground itself, built through M5 with Claude Code writing the code while I reviewed every change (APG SOURCES.md). I wrote the v1 beat plan and then the v2 narration that replaced it (both Nov 23). I made the human gate approval, the predictions, the diff review and the executed check that the film describes (B07, B10, B11).
- **Claude Code (this build, Nov 23, 2026):**
  - checked every number in the v2 narration against the captures (NUMBER-CHECK.md)
  - captured the evidence (`evidence/`), read-only; v2 reuses those captures
  - wrote `beat_sheet.json` (via `make_sheet.py`), `scenes.py` and the copy of `sentence_audio.py`, and generated the audio
  - rendered the film, ran the gates and reviewed frames
  - drafted README.md, PROJECT-BRIEF.md, BUILD-PROMPT.md, this file, FACTCHECK.md, SHOTLIST.md and PROMPTS.md for my review
  - created FRICTIONAL.md with a header only. Its entries are mine.
- **Reused from the October pitch:** the scene chassis (palette, rail, text helpers, cue timing) and `sentence_audio.py` (in v2 with 0.25 s pauses).

## Third-party assets and licences

None in the picture beyond the software above. No images, footage, music, logos, portraits or mascots.
