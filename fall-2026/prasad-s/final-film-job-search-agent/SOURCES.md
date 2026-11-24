# SOURCES: WorthLoop final project film

## Outside sources
I read each of these on 2026-11-22 (FACTCHECK.md). Claude.ai checked them
first, on 2026-11-21 (OUTLINE.md, "Sources").
- Fortune, 2026-07-27, Orianna Rosa Royle, interviewing Greenhouse CEO
  Daniel Chait: job ads on Greenhouse draw about 254 applicants each, a
  figure from Greenhouse itself (B3).
- The Washington Post, 2026-03-01, Danielle Abril, republished by the
  Philadelphia Inquirer: employers say auto-apply tools put the wrong
  information in the wrong fields; Joseph Eitner, chief HR officer at Eaton
  Capital Management, called them snake oil (B4).
- The career-ops README, github.com/career-ops-hq/career-ops: 740 listings
  checked for its maker, 68 applications, 12 interviews, one offer; the
  person presses Submit; golden evals and a check that CV facts aren't made
  up (B5, B7).
- The AP2 specification v0.2, ap2-protocol.org: the Trusted Surface must be
  non-agentic (B6).
- The AsAsked README, github.com/ginjikurata/asasked (B6).
- The Mandate Shield README, github.com/LSUDOKO/Mandate-Shield: 15 of 15
  attacks blocked and 35 of 35 legitimate cases passed on its own
  benchmark, which it says shows internal consistency, not real-world
  proof (B6).

Also in OUTLINE.md's source list, not cited in the film:
- The New York Times (DealBook), 2025-06-21, Sarah Kessler, "A.I. Sludge
  Has Entered the Job Search". I read it on 2026-11-22, in The Star's
  syndicated copy.
- TIME, 2025-03-23, Michael B. Horn, an opinion piece on LazyApply and
  JobCopilot. Claude.ai checked it on 2026-11-21; I didn't read it.

## My own work the film draws on
- JS1, js1-contract-and-watch/: the contract and the watcher.
- JS2, js2-loop-tools-diff/: the loop, the tools and the diff.
- JS3, js3-filter-tool-score/: the filter, the scorer and its MCP server,
  the measurement and the sealed sets. The film cites MEASURE.md lines 32,
  39 and 46; FILTER.md lines 18, 19, 33, 34 and 104; GATE.md lines 12-16
  and 34-36; SEAL.md lines 39 and 65; resume_persona.json line 8;
  config.json; agent/run.py lines 30-34; agent/policy.py;
  tools/mcp_server.py, tools/filter_run.py and tools/measure.py.
- My pitch film, final-project-film/: the October pitch of the approval
  check for payments (B6).
- Assignment 1, week-01-video/: the "Prasad" phoneme swap in
  tools/kokoro_phoneme_override.py, copied into tools/voice_with_pauses.py.

## What I wrote and decided
- The narration, NARRATION.md, in my words.
- Every decision in README.md: the voice, the length, the appendix, the
  toolkit, and keeping the video out of git.
- The shot list's choices, SHOTLIST.md: what each beat shows, its labels
  and its part label. Claude Code drew the scenes to it.
- All the hand labels behind the numbers the film cites: "about one in
  thirty" is my labeling of JS3's 30-posting held-out set, 1 worth it after
  my re-check (js3-filter-tool-score/MEASURE.md line 32). The five traps'
  right answers and the pass/fail bar were written down by me before the
  test (OUTLINE.md, part 4).
- Alex Rivera is fictional; no real person's data is in the project.

## What Claude contributed
- Claude Code wrote make_sheet.py, tools/voice_with_pauses.py and scenes.py,
  and typed the build documents (FACTCHECK.md, SHOTLIST.md, PROMPTS.md,
  GATE-LOG.md, BUILD-PROMPT.md, SOURCES.md, APPENDIX.md and this README's
  updates) to my prompts, in sessions on 2026-11-21 and 2026-11-22. It ran
  the voicing, the builds, the gates and the checks, and made the commits.
- Claude.ai drafted the prompts with me, checked the sources on 2026-11-21,
  and reviewed my outline and narration.
- Claude.ai suggested narration wording that I accepted: B3 ("job ads on
  its platform", "It matters because hiring is flooded"), B6 ("One standard
  there"), B7 ("in the job tools"), B10 ("a standard plug"), B13 ("built to
  skip", and the order of the count sentence), and B15 ("too senior for
  Alex, who looks for roles asking three years or less").
- Claude.ai drafted the text of FACTCHECK.md and PROMPTS.md, the starting
  shot list that I edited, the OUTLINE.md file from my four lines
  (including edits I accepted), and the commit messages, which I approved.
- I made the decisions. I watched all three review cuts and the master. No
  Claude response is shown in the film.

## Tools and licenses
Read from the files on disk on 2026-11-22. Paths are inside the toolkit
checkout unless stated.
- Brutalist toolkit, github.com/nikbearbrown/brutalist.art, revision
  22264a332f6bf8825cdd639bcd33864563801f55 (2026-10-03). License: none. The
  checkout has no LICENSE, COPYING or NOTICE file for the toolkit as a
  whole; it has notices for parts of it only (runtime/fonts/*/OFL.txt,
  icons/NOTICE.md, runtime/remotion/src/vendor/LICENSE-roughjs, and
  skills/make/show-tell/assets/isocons-24/references/license-panel.txt). Of
  those parts, the film uses only the EB Garamond font. My local changes to
  the checkout are listed in BUILD-PROMPT.md.
- The show-tell drawing kit, skills/make/show-tell/templates/iso_kit.py,
  pasted into scenes.py unchanged except its cue helper. License: none of
  its own; the toolkit has none.
- kokoro-onnx 0.6.1: MIT, "Copyright (c) 2025 github.com/thewh1teagle"
  (.venv/lib/python3.11/site-packages/kokoro_onnx-0.6.1.dist-info/licenses/LICENSE).
- The Kokoro model files kokoro-v1.0.onnx and voices-v1.0.bin
  (runtime/models/kokoro/): no license file on disk. ./setup downloads them
  from the kokoro-onnx "model-files-v1.0" release on GitHub (setup, lines
  93-94). Voice used: am_onyx.
- onnxruntime 1.30.0: MIT (its package metadata; onnxruntime/LICENSE and
  onnxruntime/ThirdPartyNotices.txt in site-packages).
- phonemizer 3.4.0: GNU GPL v3 or later (its package metadata;
  phonemizer-3.4.0.dist-info/licenses/LICENSE).
- espeakng-loader 0.2.4: no license field and no license file in its
  package metadata. It bundles libespeak-ng 1.52.0 and espeak-ng-data.
- numpy 2.4.6: BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 (its
  package metadata).
- Manim 0.18.1: MIT (manim-0.18.1.dist-info/LICENSE and LICENSE.community).
  ManimPango 0.5.0: MIT. pycairo 1.29.1: LGPL-2.1-only OR MPL-1.1 (package
  metadata; no license file listed). SciPy 1.17.1: BSD (package metadata;
  scipy-1.17.1.dist-info/LICENSE.txt). Pillow 10.4.0: HPND (package
  metadata; pillow-10.4.0.dist-info/LICENSE).
- EB Garamond: SIL Open Font License 1.1, "Copyright 2017 The EB Garamond
  Project Authors" (runtime/fonts/EB_Garamond/OFL.txt, and the font file's
  own license field).
- Menlo (B11's fingerprint), the macOS system font
  /System/Library/Fonts/Menlo.ttc: its copyright field reads "Copyright ©
  2009 Apple Inc. Copyright © 2006 by Tavmjong Bah. Copyright © 2003 by
  Bitstream, Inc. All Rights Reserved." It has no license field; it ships
  with macOS.
- ffmpeg 9.0.2: GNU GPL v3 or later (ffmpeg -L; built with --enable-gpl,
  --enable-version3 and --enable-libx264).
- Node v20.20.2: installed for the toolkit, not used by this film (no
  Remotion beats). Its license was not read.

No images, music, stock footage or other media files were imported: images/
and pantry/ are empty, and every picture is drawn in code.

## Disclosures
- The narration voice is synthetic: Kokoro am_onyx, run locally on my
  laptop, reading my words. The film says so on its opening card: "Voice:
  synthetic (Kokoro) · Script: Prasad Shinde".
- All eleven commits for this film, FILM-CP1 to FILM-CP11, were made through
  Claude Code with commit messages I approved, without a Co-Authored-By
  trailer.
