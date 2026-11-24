# SOURCES — Readback pitch film

Pitch-film sections are as of 2026-10-14; the project-film section is as of 2026-11-23.

## Used

### Toolkit and components

| Component | Version | Licence | Used for |
|---|---|---|---|
| brutalist.art toolkit (https://github.com/nikbearbrown/brutalist.art) | commit `cd4bf20904be4e7d63babd9622b17963c2361b27` | No licence file in the repository at this commit (GitHub's licence API returns "Not Found"); course-provided toolkit, not redistributed here | The `show-tell` skill, its iso drawing kit (pasted into `scenes.py`, as the skill requires), the pipeline scripts (`generate_audio_kokoro.py`, `align.py`, `art run`, `art final`) and the gates (A, W, B, V, T, bookend, factcheck) |
| Toolkit patch (mine, `toolkit-patches/ClaudeTitleOutro-handle-hideMascot.patch`) | against `cd4bf20` | — | Outro shows my handle ("Aravind Ravi · INFO 7375") and no mascot |
| kokoro-onnx | 0.6.1 | MIT (repository licence, checked 2026-10-14) | Local narration engine |
| Kokoro-82M voice model (`kokoro-v1.0.onnx`, `voices-v1.0.bin`), voice `am_onyx` | v1.0 | Apache-2.0 (model card, checked 2026-10-14) | Narration voice |
| espeak-ng (Homebrew) | 1.52.0 | GPL-3.0 | Phonemizer backend for Kokoro |
| Manim Community | 0.18.1 | MIT | Body beats B01–B08 |
| Remotion | 4.0.486 | Remotion License (free for individuals) | Bookends BIDEA (`BrutalistHesitantWriter`) and BOUT (`ClaudeTitleOutro`) |
| faster-whisper | 1.2.1 | MIT (repository licence, checked 2026-10-14) | Forced alignment (`align.py`) and my pronunciation checks (`base.en`, `small.en`) |
| FFmpeg | 9.0.2 | LGPL/GPL | Holds, frame extraction, encoding |
| Claude Code (headless `claude -p`, my subscription) | 2.1.283, model `claude-opus-5-5` | Anthropic consumer terms | The recap feature run in `case-study/outputs/feature-run/` |
| Claude Code | 2.1.323 | Anthropic consumer terms | Project film build (2026-11-23) |

### AMI Meeting Corpus — manual annotations (CC BY 4.0)

- **What:** AMI manual annotations, file `ami_public_manual_1.6.2.zip`. The download page labels it v1.6.2 (10-Apr-2017); its `00README_MANUAL.txt` calls itself release 1.7 (16 June 2014).
  - Source: https://groups.inf.ed.ac.uk/ami/download/
  - Direct URL: https://groups.inf.ed.ac.uk/ami/AMICorpusAnnotations/ami_public_manual_1.6.2.zip
- **Downloaded:** 2026-10-14, 13:52 EDT. 22,887,865 bytes; SHA-256 `b56e5babb2496b8795deeeda7e71178d7fbc9963f94276cf2a3f4b56ebbc9f9d`.
- **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
- **Coverage of the summaries (checked 2026-10-14):**
  - The licence page (https://groups.inf.ed.ac.uk/ami/corpus/license.shtml) and the zip's own `LICENCE.txt` both say: "The AMI corpus and its annotations are released under the Creative Commons Attribution 4.0 … (CC BY 4.0)."
  - The download page lists this zip as "license altered to CC BY 4.0".
  - The annotation documentation (https://groups.inf.ed.ac.uk/ami/corpus/annotation.shtml) lists "Abstractive and Extractive Summaries" as one of the corpus annotations. They ship inside this zip under `abstractive/` (142 `*.abssumm.xml` files) and `extractive/`.
  - The summaries are therefore covered.
- **Attribution:** AMI Meeting Corpus, AMI Consortium. Distributed by the University of Edinburgh at https://groups.inf.ed.ac.uk/ami/, under CC BY 4.0. The corpus site introduces it with Carletta, J. (2006), "Announcing the AMI Meeting Corpus", *The ELRA Newsletter* 11(1), pp. 3–5.
- **Changes made:**
  - 10 whole scenario meetings were selected; the rule is in `case-study/data/sample/README.md`.
  - Their NXT XML was converted to speaker-labelled plain text, plus the matching abstractive summaries.
  - Nothing was reworded.
  - The full raw download stays local and is not redistributed: it is git-ignored under `case-study/data/raw/`.

### Alternatives looked at (for Q2)

- **Maxim AI:** the getmaxim.ai FAQ "What is LLM-as-a-Judge evaluation" and the Maxim article "LLM as a Judge: a practical, reliable path…".
- **orq.ai:** the docs.orq.ai cookbook "Align an Evaluator with Human Judgement".
- **GitHub Spec Kit:** https://github.com/github/spec-kit.
- All three were checked 2026-10-14; details are in `FRICTIONAL.md`.

## Third-party assets in the film

| Asset | Licence | Where |
|---|---|---|
| EB Garamond font (Google Fonts) | SIL Open Font License 1.1 (`runtime/fonts/EB_Garamond/OFL.txt` in the toolkit) | All on-screen text: Manim `Text` and the Remotion serif fallback (Tiempos Text isn't installed) |
| show-tell palette and iso drawing primitives | part of the toolkit (see above) | Body beats |
| AMI excerpt: none on screen. The B08 excerpt is from Claude's recap output, not from AMI text | — | B08 |

No stock footage, images, music, sound effects, logos or generated imagery are used.

## Made by me (Aravind)

- **Project and brief:**
  - The project choice, title (Readback) and target role.
  - All seven answers in `PROJECT-BRIEF.md`; the final text was drafted by Claude from my inputs, and I reviewed it.
  - The Q5 "out" item, in my words.
  - Removing Braintrust and Confident AI because I hadn't checked them.
- **Alternatives:** opening the Maxim AI, orq.ai and Spec Kit pages myself on 2026-10-14 and confirming Claude's summaries.
- **Case-study decisions:**
  - The whole-meeting selection rule (10 meetings, under 35 minutes, non-empty DECISIONS).
  - C1's wording, C5's wording, the leakage rule, and keeping the 250-word cap.
  - The phase-scope cap: no labels or judges before this deadline.
- **Film decisions:**
  - Approving the narration as written, and the `am_onyx` voice.
  - No pull of the toolkit.
  - The outro, greeting and persona decision: my handle, no instructor persona.
  - Every honesty-audit fix: F3, F5, F8 and F9 fixed; F7 kept as disclosed.
- **Earlier work reused:**
  - `add_holds.py` and the original outro `handle` patch, from my Week 1 folder.
  - The Week 1 and Week 2 work cited as evidence: PR #8 and PR #23.

## Contributed by Claude

Claude Code (Opus 5.5) in this project's session, at my direction:

- **Drafts:**
  - `PROJECT-BRIEF.md`: first draft from my appendix answers, then the final text from my inputs.
  - The narration and visual plan in `make_sheet.py` / `beat_sheet.json`, which I approved line by line.
  - The constructed `recap-prd.md`, `recap-system-prompt.md` and `rubric-v0.md` (C2–C4 and the system prompt text are Claude's, kept by me).
  - `FACTCHECK.md`, `SHOTLIST.md` and `PROMPTS.md`.
  - `gates/honesty-audit.md`.
  - The entries in `FRICTIONAL.md`, which I reviewed, with decisions marked (Aravind).
  - `README.md` and this file.
- **Code:**
  - `case-study/scripts/select_ami_sample.py` and `case-study/run_feature.py`.
  - `make_sheet.py`.
  - `scenes.py`: the eight scenes and helpers; the iso kit itself is the toolkit's.
  - The `hideMascot` extension to my toolkit patch.
- **Checks:**
  - The AMI licence check.
  - The PR #23 head-commit match.
  - The `readback` name check on PyPI and GitHub.
  - The pronunciation tests (Kokoro with whisper).
  - Running every gate and diagnosing each failure.
- **Summaries:** found and summarized the Maxim AI, orq.ai and Spec Kit pages, which I then opened and confirmed.
- **Recap outputs:** the 10 recaps in `case-study/outputs/feature-run/` are Claude Opus 5.5 (`claude-opus-5-5`) responses to my constructed prompt, received 2026-10-14. They are the feature under test, not authored by me.

## v2 visuals (built 2026-10-14; approved by me and submitted)

- **Used:** the same toolkit, components and licences as above.
  - The narration clips are reused byte for byte; no new audio was generated.
  - Fonts: EB Garamond (OFL) for all text, plus PT Mono for the one CLI line in B01. PT Mono is a macOS system font (ParaType, SIL OFL), rendered locally and not redistributed.
- **Made by me (Aravind):**
  - The decision to upgrade the visuals and the full v2 brief: diagnosis, design system, beat-by-beat visuals, the timebox and the hard rules.
  - Approving the plan (including the two adjustments and "never" in the grid) and approving the B05 probe.
  - Requiring that no text overlap anything on any frame, and approving v2 for submission.
- **Contributed by Claude (Claude Code, Opus 5.5):**
  - `gates/v2-visual-plan.md`.
  - The v2 `scenes.py`: colour roles, progress rail, the recurring `Rubric` page, judge tokens and stamps, the midpoint guard, word-clock cue timing, and the nine Manim scenes (BIDEA, B01–B08).
  - The render-time assertions tying every on-screen number and excerpt to its source file.
  - The v2 `beat_sheet.json` edits: BIDEA moved to the Manim lane, the v2 labels and the v2 slug, with narration and durations asserted unchanged.
  - `FACTCHECK.md` rows 21–36 and the v2 `SHOTLIST.md`.
  - `gates/v2/honesty-audit-v2.md` and `gates/v2/GATES.md`.
  - `overlap_check.py`, the frame-by-frame text-overlap check, and the fixes it drove.
  - The freezedetect, contact-sheet and frame checks.
  - The top-level rebuild that proved the submitted file reproduces byte for byte.
  - Diagnosing each gate failure.

## Project film (four-part brief; built 2026-11-23, approved by me)

The file is `film/project/aravind-r-readback-project-film.mp4`. The build and its records are in `film/project/`.

Final file: film/project/aravind-r-readback-project-film.mp4, 3:56.8, SHA-256 535fe61b…, commit 8424a49

- **Used:**
  - The same toolkit, components and licences as above: brutalist.art at `cd4bf20`, kokoro-onnx with the Kokoro-82M `am_onyx` voice, Manim Community 0.18.1, Remotion, faster-whisper and FFmpeg. No paid services.
  - My outro patch, extended twice:
    - `toolkit-patches/ClaudeTitleOutro-handle-hideMascot-polarity-bg.patch` adds a pinned light polarity and the stage-colour ground (Phase 3).
    - `toolkit-patches/ClaudeTitleOutro-handle-hideMascot-polarity-bg-tagline.patch` also adds the `tagline` and `credit` lines on the end card (positioning revision). The second patch contains the first.
  - Fonts: EB Garamond (OFL) for all text, and PT Mono (macOS system font, SIL OFL, rendered locally) for the meeting IDs.
  - Real material already in this repo:
    - The AMI sample.
    - The ten feature-run recaps from 2026-10-14.
    - On screen: ES2007a's transcript line and recap output (B10), ES2007a's DECISIONS list (B11), and ES2010b's transcript lines [00:20:44]–[00:20:52], its recap's Decisions line and its DECISIONS summary (B14).
    - The three prior-work tools as checked on 2026-10-14 (above).
  - faster-whisper `small.en` for the speech-to-text checks (`film/project/stt_check.py`).
  - Ollama 0.40.17 (Homebrew cask ollama-app), installed 2026-11-23; not yet used by any judge
  - No stock footage, images, music, sound effects, logos or generated imagery. The three B02 vignettes (a support-reply bot, a document summariser, a search answer) are constructed illustrations, not real products or outputs.
- **Made by me (Aravind):**
  - The four-part brief: requested and directed by me; the Claude Code prompt 'Readback project film (four-part brief)' was drafted in Claude chat from my request, and I sent it.
  - Approving the narration (Phase 1), the storyboard (Phase 2), Phase 3, the revised narration ("OK, go") and the final cut ("Approve cut").
  - My review requests before Phase 5 (B15's checklist, my human labels, prior work scoped to the tools I checked, B13, the Readback respelling) and the four checks after them.
  - The positioning feedback on the review cut: Readback for any AI feature's acceptance criteria with the AMI recap feature as the test bench, the P0/P1 list and the positioning-audit gate.
  - Kept the flagged lines in the drafts; softened both in the final fix pass.
  - The submission route: a new branch from `2cad8ba`, pushed to my fork, no PR yet.
  - Judgment calls: see FRICTIONAL.md, 2026-11-23, 'my judgment calls'.
- **Contributed by Claude (Claude Code, Opus 5.5), at my direction:**
  - Claude Code 2.1.323 for the project film.
  - **Drafts:**
    - the narration in `film/project/make_sheet.py`, which I approved;
    - `film/project/CLAIMS.md`, `EVAL-PLAN.md`, `DESIGN.md`, `FACTCHECK.md`, `SHOTLIST.md` and `PROMPTS.md`;
    - `film/project/gates/GATES.md` and `positioning-audit.md`;
    - this section, and the `FRICTIONAL.md` entries, which I reviewed, with decisions marked (Aravind).
  - **Code:**
    - `film/project/scenes.py` (the 20 Manim scenes);
    - `add_holds.py`: edge trimming added to my Week 1 hold script;
    - `normalize_audio.py`, `qc_film.py`, `overlap_check.py`, `strings_dump.py`, `positioning_check.py`, `stt_check.py` and `make_storyboard.py`;
    - the `polarity`, `background`, `tagline` and `credit` extensions to my outro patch.
  - **Checks:**
    - the real-evidence search across the ten recaps (ES2010b used; IS1005c and IS1009d ruled out);
    - the environment checks behind B15;
    - the speech-to-text and pronunciation checks;
    - running every gate and diagnosing each failure.
- Claude (chat), Claude.ai in my project, at my direction: the film-subject recommendation; the four-part Claude Code prompt; reviews of each Claude Code report, with the honesty flags; frame-by-frame reviews of both review cuts from contact sheets and ffmpeg freeze/silence detection; the P0/P1 revision prompts, the positioning-audit gate and the final fix-pass prompt; the paperwork gap list and this prompt. It made no changes to the repo. Details: FRICTIONAL.md, 2026-11-23.
