# SOURCES

## Tools used

| Tool | Version | Role | Licence (where it was checked) |
|---|---|---|---|
| Brutalist toolkit (`nikbearbrown/brutalist.art`, local checkout `Brutalist-latest`) | commit `3a6d397` | Reel pipeline, QC gates, compile | No licence file (as in the October pitch); used as directed by the INFO 7375 course. Its instructor-persona skills, bookends, portraits and outro were not used. |
| Manim Community | 0.20.1 (ManimPango 0.6.1) | All scene animation (`scenes.py`) | MIT (package metadata) |
| Kokoro TTS, voice `am_onyx` | Kokoro-82M v1.0 weights via kokoro-onnx 0.6.1, run locally | Narration (`sentence_audio.py`), the same local voice as the October pitch | Weights Apache-2.0 and kokoro-onnx MIT, as checked for the October pitch (its SOURCES.md, 2026-10-14). The model files were copied from the October checkout, not re-downloaded (SHA-256 identical). |
| faster-whisper, model `small.en` | 1.2.1, run offline from the local cache | Pronunciation check only (`gates/whisper_check.txt`); nothing from it is in the film | MIT (package metadata) |
| ffmpeg | 9.0.1 | Audio joins, measurement, muxing, frame checks | Not separately checked |
| Python | 3.12.14 (toolkit `.venv`, rebuilt Nov 23 from `requirements.txt`) | Runs the toolkit | — |

Also used: the macOS system fonts Menlo and the default serif. No stock footage, music, images, logos or paid generation. No API keys and no API calls.

## Source material shown in the film

Every REAL beat (B06–B12) shows text captured on 2026-11-23 from my repo `~/Documents/agent-proving-ground` (public at https://github.com/tushar-patel28/agent-proving-ground), read-only, at HEAD `f40f3a1`. The exact commands and full output are in `evidence/<beat>.txt`; the script that ran them is `evidence/capture.sh`. Lines that don't fit are cut with "…"; nothing is reworded. Grey annotations such as "(result line recorded in PLAN.md)" and "(computed: b / a = 1.409)" are mine.

| Beat | Source in the APG repo | Source date |
|---|---|---|
| B06 | PLAN.md:120 (the `apg run 001` result line); `apg show evidence/traces/20261112T053055Z-92239eb0.json`; that trace's step list | 2026-11-12 |
| B07 | `apg show traces/20261118T034327Z-b54f5cd6.json` step 4 (contract B, held-out, 008); gate section of `evidence/traces/20261113T224740Z-a9a2c258.json`; docs/trace-schema.md:47, :193 | 2026-11-18 03:43Z (Nov 17 ET); 2026-11-13 |
| B08 | tasks/README.md; `git log -1 753612d`; `git show --stat 26b5305` | 2026-11-13 |
| B09 | evidence/isolation/20261117-isolation-d29.txt; docs/01-brief.md:27 | 2026-11-17 |
| B10 | `wc -c contracts/*-system.txt`; docs/t5-predictions.md:1; `git log -1 6d7bafe`; first held-out eval in results/eval-log.jsonl | 2026-11-17 |
| B11 | evidence/compare/20261118-t51-a-vs-b.txt | 2026-11-18 |
| B12 | docs/07-evidence.md:415, :480; FAILURES.md F2 | 2026-11-18 |
| B13 | PLAN.md (M0–M5, target submit Dec 18); docs/01-brief.md:40–41; git remote | — |

## Tools named in the film (B04)

| Item | Link | Wording in the film | Basis |
|---|---|---|---|
| E2B | — | "provides sandboxes for running AI-generated code" | October PROJECT-BRIEF.md §2, word for word |
| Langfuse | — | "records LLM traces and scores" | October PROJECT-BRIEF.md §2, word for word |
| AI Proving Ground (Drupal) | https://www.drupal.org/project/ai_proving_ground | "grades what an agent actually saved instead of what it reports, but only for Drupal sites" | My line, new in this film. The page was not fetched during this build (no network beyond pip), so I confirm the wording against it myself |

The approved beat plan also named Runtime, Raindrop and oh-my-pi in B04. The October brief doesn't name them, so they were taken out (B4 [VERIFY], Nov 23; see README.md).

## What I made vs. what Claude contributed

- **Me:** Agent Proving Ground itself, built through M5 with Claude Code writing the code while I reviewed every change (APG SOURCES.md). I wrote and approved the BEAT-PLAN narration (Nov 23) and chose the B4 wording ("brief only"). I made the human gate approval, the predictions, the diff review and the executed check shown in B07, B10 and B12.
- **Claude Code (this build, Nov 23, 2026):**
  - checked the narration against the repo (NUMBER-CHECK.md) and B4 against the October brief
  - captured the evidence (`evidence/`), read-only
  - wrote `beat_sheet.json` (via `make_sheet.py`), `scenes.py` and the copy of `sentence_audio.py`, and generated the audio
  - rendered the film, ran the gates and reviewed frames
  - drafted README.md, PROJECT-BRIEF.md, BUILD-PROMPT.md, this file, FACTCHECK.md, SHOTLIST.md and PROMPTS.md for my review
  - created FRICTIONAL.md with a header only. Its entries are mine.
- **Reused from the October pitch:** the scene chassis (palette, rail, text helpers, cue timing) and `sentence_audio.py`.

## Third-party assets and licences

None in the picture beyond the software above. No images, footage, music, logos, portraits or mascots.
