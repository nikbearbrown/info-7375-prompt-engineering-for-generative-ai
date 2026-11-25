# SOURCES — Final Project Film (plan)

## 1. What I wrote (Swathi)

- The project, its plan and every decision in it: `PLAN-APPENDIX.md` (authored by
  me; its header says "Drafted with Claude Chat, revised 2026-11-22 after review
  with ChatGPT; decisions recorded 2026-11-22").
- The requirements for the film's structure, narration and on-screen labels,
  and the final revision and approval of `NARRATION.md` and `beat_sheet.json`
  (drafted by Claude Chat; see section 2).
- The completed JS1–JS3 work shown in B05 (filter rules, collection, audit
  judgments, v1.1), recorded in my JS3 folder and commits.
- The Phase 2/3 decisions for this build (voice `af_heart`; output filename; grey
  `#8A8A90`; runtime ceiling 300 s; B11 label through the sign-off; no git;
  GATE MASTER + Gate V for "render integrity").
- `FRICTIONAL.md` (written by me; not drafted by Claude Code).
- Claude Chat drafted a reference version of FRICTIONAL.md from the session record; I rewrote it and approved the final text.

## 2. What Claude Chat and ChatGPT contributed

- **Claude Chat:** drafted `PLAN-APPENDIX.md` with me, and checked its references
  on 2026-11-22 (verification status recorded in its section 9).
- **ChatGPT:** reviewed the plan with me before the 2026-11-22 revision. In JS3,
  audit rows 5–48 were judged by me after I saw a ChatGPT-assisted draft
  (recorded in `audit/HUMAN_AUDIT.csv`, `how_judged`).
- **`NARRATION.md` and `beat_sheet.json`:** drafted by Claude Chat from my
  requirements, reviewed with ChatGPT, and revised and approved by me.

## 3. What Claude Code did (this session, Opus 5.5)

- **Inventory (Phase 1):** checksummed the pitch folder, checked the beat sheet
  schema, narration and labels, and planned the build.
- **Pipeline copy:** copied the pitch film's scripts and adapted them for this film:
  - `build_mux.py`: filename; runtime ceiling 240 → 300 s.
  - `make_srt.py`: caption forms, plus a check that captions equal `NARRATION.md`.
  - `check_facts.py`: lists numbers shown but not spoken.
  - `run_upstream_gates.sh`: no git; gates read from the local `519fcbb` copy.
  - `build.sh`: added the label gate and `PYTHONDONTWRITEBYTECODE`.
- **New code:**
  - `scene.py`: 11 new scenes. It reuses the pitch's `Beat` helper and checks,
    logs every drawn string, and skips sub-frame waits.
  - `check_labels.py`: the new label gate.
  - `data/facts.json`: every displayed number with its source and spoken form.
- **Beat sheet edits** (approved): voice → `af_heart`; `#6B6B70` → `#8A8A90` in
  B03, B05 and B11. The Kokoro script also wrote back `actual_duration_s` and
  `audio_file`. No narration, label or number was changed.
- **Gates and checks:** ran every local and upstream gate and saved the reports.
  Verified the B05 figures read-only against my JS3 files. Wrote these drafts.

## 4. Facts on screen

| Beat | Facts | Source |
|---|---|---|
| B03 | USCIS H-1B Employer Data Hub (FY2009+), DOL OFLC disclosure files, MyVisaJobs, H1BGrader, Interstride | `PLAN-APPENDIX.md` section 9 (footer on screen) |
| B05 | 1,832 postings (Databricks 901, Stripe 789, Plaid 142), Nov 17; v1 shortlisted 4; 0 of 30 (up to ~10%); v1.1 changed 7, shortlist 4; commits `0f689b8`, `d4a3b94`, `beb8a26`, `815064e`, `7672a21`, final `c2e624e` | JS3 artifacts; each figure matched a JS3 file (see the build report). Not confirmed to be at commit `c2e624e`, because git was not used |
| B06 | LCA → H-1B petition; VISA_CLASS and CASE_STATUS rules | 20 CFR 655 Subpart H; DOL LCA record layout (footer on screen) |
| B09–B11 | 60 / 20 / 40, ≥25, ≥10, ≥5, 0, ≤ 2 | `PLAN-APPENDIX.md` sections 6–7: planned, and proposed targets, not results |

## 5. Tools and licences

| Tool | Version | Licence | Role |
|------|---------|---------|------|
| Brutalist toolkit (local copy) | commit `29ba0e8` (2026-09-15) | no `LICENSE` file at its root | `generate_audio_kokoro.py` unmodified; Gates A, W, B, V from `runtime/qc/` |
| Brutalist toolkit (upstream gates) | scripts from commit `519fcbb` (2026-10-12), local copy | as above | LOUDNESS, MASTER, T, SRT, SHARPNESS, unmodified |
| [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) | weights v1.0 | Apache-2.0 | narration voice `af_heart` |
| [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) | 0.6.1 | MIT | ONNX wrapper for Kokoro |
| onnxruntime | 1.30.0 | MIT | Kokoro inference |
| [eSpeak NG](https://github.com/espeak-ng/espeak-ng) | 1.52.0 | GPL-3.0 | phonemizer backend |
| [Manim Community](https://www.manim.community/) | v0.18.1 | MIT | visuals |
| [FFmpeg](https://ffmpeg.org/) | 9.0.1 | LGPL-2.1+ | mux, concat, loudness, verification |
| NumPy / Pillow / SciPy | 2.2.6 / 10.4.0 / 1.18.1 | BSD-3 / MIT-CMU / BSD-3 | scenes, contact sheet, gates |
| Menlo | macOS system font | Apple | on-screen type |

No logos, screenshots, company-branded images or personal data appear on screen.
Company names appear only as plain text.
