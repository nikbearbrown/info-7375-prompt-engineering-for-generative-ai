# FRICTIONAL.md — Week 1 explainer video

Format: the entry prompts in the course's `prerequisites/frictional.md` (canonical), laid out per
`frictional/templates/FRICTIONAL-annotated.md`. Entries were first logged during the 2026-09-27
session and reorganized into this format the same day. Entries 1 to 16 were logged during the Claude Code session. Entry 0 is retrospective: it was written afterwards, on 2026-09-27, from my chat history.
The personal fields (I tried / expected, What I understand now, and some What I did lines) were drafted with a separate Claude chat from what I told it during the project. I reviewed each one and confirmed it is accurate.

---

## Entry 0

**Date and what I was working on:** 2026-09-27 — Before Claude Code: WSL attempt and Windows setup (retrospective).

**I tried / expected:** I thought WSL was required, so I started there and expected setup to be quick.

**What happened:** sudo rejected my password until I realized it wanted my Linux password, not my Windows one. pip install then crashed with an AssertionError, which was the old pip 22.0.2 that comes with Ubuntu 22.04; upgrading pip fixed it. I ran main.py in WSL under Python 3.10 and 3.11, and diff showed identical output. A classmate then told me he did the project on native Windows without WSL, so I switched to CMD and Claude Code. On Windows, winget was not recognized even though App Installer v1.29.380 was installed, because my user PATH was missing the WindowsApps folder. I added it.

**What Claude or another person contributed:** a Claude chat walked me through each fix; a classmate told me WSL was optional.

**What I understand now / still do not understand:** WSL is optional for this toolkit; what matters is running Claude Code where the project lives. Terminals only see PATH changes after they are reopened.

---

## Entry 1

**Date and what I was working on:** 2026-09-27 — reading the assignment brief before setup.

**I tried / expected:** I pasted the brief into Notepad and thought it had saved.

**What happened:** `C:\info7375\ASSIGNMENT.md` existed but was 0 bytes, so no assignment spec could be read.

**What I did:** Continued with setup from my own task list, then pasted the real brief into `ASSIGNMENT.md` later that day. It was read after setup finished.

**What Claude or another person contributed:** Claude found that the file was empty and flagged it instead of guessing at the requirements. I supplied the brief.

**What I understand now / still do not understand:** I did not check the file before handing it to Claude Code. Now I check that a file actually has content before a tool depends on it.

**Evidence and next step:** `ASSIGNMENT.md` (now filled in). The requirements it adds are reflected in later entries.

---

## Entry 2

**Date and what I was working on:** 2026-09-27 — cloning the course repo and brutalist.art, and running the Chapter 1 code.

**I tried / expected:** Ran `lessons/01-randomness-and-first-prompts/code/main.py` under Python 3.11. I expected a token 2 probability of `0.6652409557748218` and counts `{"1": 268, "2": 630, "0": 102}`.

**What happened:** No friction. Both clones succeeded. `main.py` (stdlib only, `random.Random(7)`, 1000 draws, logits `[1,2,3]`, temperature 1.0) ran on Python 3.11.9 with exit 0 and matched exactly. Derived: 1000 × 0.6652409557748218 = 665.2409557748218 ≈ 665.24 expected, vs 630 observed. Chapter 1 (§ at the counts table) frames this gap the same way.

**What I did:** Saved stdout unmodified with `cmd /c` so PowerShell wouldn't re-encode it.

**What Claude or another person contributed:** Claude read `main.py` before running it, ran it, and compared the output to my expected values. I supplied those values.

**What I understand now / still do not understand:** The same code with the same seed gave the same numbers in WSL and on Windows, so the numbers in my video come from a run anyone can repeat.

**Evidence and next step:** `main_output_2026-09-27.txt`. Course repo HEAD `b293224d5c6f078ce5f793c7ea0f73c9af3f19a0`. Commands are in `BUILD-PROMPT.md` Step 1–2.

---

## Entry 3

**Date and what I was working on:** 2026-09-27 — first run of `brutalist.art/setup --install` on native Windows (Git Bash).

**I tried / expected:** Ran `./setup --install` as documented and expected a readiness table. I expected ./setup --install to work in one go, since the README makes it one command.

**What happened:**
- `python3` in Git Bash resolved to the Microsoft Store stub (`…/WindowsApps/python3`, "Python was not found"). No Python deps could be installed.
- The script exited 1 **before printing any readiness table**. Its ElevenLabs guard (`setup` lines 102–115) greps the whole repo and found 10 hits in the toolkit's own `youtube/brutalist/` reels (e.g. `claude-liam-brutalist-command-setup/beat_sheet.json:558` → `xi-api-key`). The shipped repo fails its own guard. brutalist.art commit `cd4bf20` (2026-09-26).
- No `pdflatex` / `dvisvgm`, so "Manim equation beats" would be blocked.
- Fonts were copied to `~/.local/share/fonts`, a Linux path that Windows doesn't search. `fc-list` is also absent.
- `npm install` in `runtime/remotion` added 189 packages. `npm audit` reports 5 vulnerabilities (1 moderate, 4 high), and `source-map@0.8.0-beta.0` is deprecated. Not acted on.
- The Kokoro model downloaded fine (kokoro-v1.0.onnx 325,532,387 B + voices-v1.0.bin 28,214,398 B).
- Doc inconsistencies: HOW-TO.md says `cd books/brutalist` (the checkout is `brutalist.art`); HOW-TO.md says the Kokoro model "ships inside this toolkit" (it's downloaded; the course's `brutalist-video-sources.md` also calls this stale); HOW-TO.md says "three skills" while CLAUDE.md says 15.

**What I did:** Stopped before changing anything and asked for approval of fixes (Entry 4). I didn't edit the files that tripped the guard.

**What Claude or another person contributed:** Claude read `setup` in full before running it, probed which tools actually resolve in Git Bash, ran the script unmodified to get a real baseline, and diagnosed each failure. I decided which fixes to approve.

**What I understand now / still do not understand:** Windows has a fake python3 that only points to the Microsoft Store, and the toolkit's own safety check fails on the toolkit's own example files. I still do not know why the repo ships files that fail its own check.

**Evidence and next step:** `logs/setup_install_2026-09-27.log`. brutalist.art HEAD `cd4bf20904be4e7d63babd9622b17963c2361b27`.

---

## Entry 4

**Date and what I was working on:** 2026-09-27 — applying approved workarounds and re-running setup.

**I tried / expected:** Approved three fixes: a Python 3.11 venv with a `python3` alias, a minimal local patch to the ElevenLabs guard, and MiKTeX. I'm disabling the Windows Store `python.exe`/`python3.exe` aliases myself.

**What happened:**
- **Venv:** `py -3.11 -m venv C:\info7375\brutalist.art\.venv`, plus `python3.exe` as a copy of `python.exe` (Windows venvs don't create `python3`). After `source .venv/Scripts/activate`, `python3` is 3.11.9 with pip 24.0.
- **UPSTREAM WORKAROUND — ElevenLabs guard patched locally, NOT committed.** Added `--exclude-dir=youtube` to both `grep` calls in `setup` (lines 107, 112), 2 lines changed. After the patch, the guard has no hits outside `youtube/`. The real fix belongs upstream: scrub the 10 files or change the guard. Revert with `git -C C:\info7375\brutalist.art checkout -- setup`.
- **MiKTeX 25.12** installed per-user (`%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64`) and added to the user PATH. Shells already open, including Claude's, didn't see it and needed an explicit `export PATH=…`. pdfTeX 4.23 and dvisvgm 3.4.3 confirmed.
- **Re-run:** `./setup --install` exit 0, all 7 readiness rows ✅. Every pip package installed as a prebuilt cp311 Windows wheel (manim 0.18.1, ManimPango 0.5.0, pycairo 1.29.1, onnxruntime 1.30.0, faster-whisper 1.2.1, kokoro-onnx 0.6.1). No guard hits in `.venv` site-packages.
- **The font row was a false positive on Windows.** EB Garamond and Oswald existed only in `~/.local/share/fonts`. `have_font` passed on its filename scan of that folder.
- Side effects in the toolkit repo, left as is and not committed: `.venv/` isn't in `.gitignore` (it shows as untracked, and the guard greps it), and the first `npm install` modified `runtime/remotion/package-lock.json`.

**What I did:** Decided that all video work goes in `C:\info7375\week-01-video\`, not the course repo's `youtube/` (as the course AGENTS.md and prerequisite suggest) and not the toolkit folder.

**What Claude or another person contributed:** Claude created the venv, wrote the 2-line patch and saved its diff, installed MiKTeX, re-ran setup, and then checked the green font row against the actual Windows font folders instead of trusting it. I approved each change and chose the build location.

**What I understand now / still do not understand:** A venv keeps the right Python for this project without touching the rest of my machine, and saving each patch as a diff means I can undo it or show exactly what changed. I also learned again that terminals opened before an install do not see new PATH entries.

**Evidence and next step:** `brutalist-setup-local-patch.diff`, `logs/setup_install_2026-09-27_run2.log`, `BUILD-PROMPT.md` Step 3b.

---

## Entry 5

**Date and what I was working on:** 2026-09-27 — verifying fonts and running `./art smoke`.

**I tried / expected:** Installed EB Garamond and Oswald into Windows myself, then wanted smoke-test frames to confirm the fonts render. I expected that installing the fonts would make the smoke test pass.

**What happened:**
- **Fonts confirmed installed:** per-user in `%LOCALAPPDATA%\Microsoft\Windows\Fonts` (EBGaramond Regular/Medium/Italic, Oswald-Variable) and registered in HKCU. Windows also has Monotype **Garamond** (`GARA.TTF`), a lookalike that could hide a fallback.
- **`./art smoke` FAILED (exit 1) at GATE 0:** `[kokoro] REFUSED: metadata.slug must be a filename, not a path`. The fixture slug `_smoke` begins with `_`, which `build_safety.py:186` rejects (`[A-Za-z0-9][A-Za-z0-9._-]*`). **Upstream bug, any OS**: the toolkit's own smoke fixture fails its own safety check.
- Also found: `smoke_test.sh` deletes its work directory on exit, so it never leaves frames to inspect. Its slates load EB Garamond **by file path** (`compile.py:84-104`), so they can't test the Windows font install anyway.
- **Replica run** (same three steps and env flags, in a scratch copy with slug `smoke`, repo untouched): Kokoro narration succeeded for both beats, and the per-beat clips rendered. **Compile then FAILED with a Windows-specific bug.** `compile.py:789` puts a raw Windows path into ffmpeg's `drawtext=fontfile=C:\info7375\…ttf`. The `:` and `\` break filter parsing ("No option name near 'info7375brutalist.art…'"). Needs escaping (e.g. `C\:/info7375/...`). **Not patched, since it's unapproved.** This will block `./art run` for the real reel.
- **Manim font probe** (scratch scene, not part of the video): Pango lists `EB Garamond` and `Oswald`. The rendered still shows EB Garamond and Oswald distinctly, and a fake-family control falls back to a different sans, so there's no silent substitution. There's a visible gap in "Garam ond" (m→o), which is worth checking in frame QC (see the toolkit's `type_check.py` kerning notes).
- **Remotion fonts:** not verified. `tokens/claude.ts:32` uses the CSS family name (`"EB Garamond", Georgia, …`), so Chrome resolves it from Windows, with Georgia as the silent fallback.

**What I did:** I installed EB Garamond and Oswald by right-clicking the font files and choosing Install, then asked Claude Code to check that the renderers really used them.

**What Claude or another person contributed:** Claude read `smoke_test.sh` before running it, ran it unmodified, found both bugs, built the replica and the font probe, and read the frames. I installed the fonts.

**What I understand now / still do not understand:** A green check can be a false positive. The font row passed only because the files sat in a folder Windows never reads. The smoke test also had a bug in its own fixture name. I still do not fully understand how ffmpeg parses file paths inside its filters.

**Evidence and next step:** `logs/art_smoke_2026-09-27.log`, `logs/art_smoke_replica_2026-09-27.log`, `_font-check/smoke-B00.png`, `_font-check/smoke-B01.png`, `_font-check/font_probe.py`, `_font-check/media/images/font_probe/FontProbe_ManimCE_v0.18.1.png`. Next: decide whether to approve a local `compile.py` drawtext-escaping patch, and verify Remotion fonts with one still rendered through `remotion_scenes.py`.

---

## Entry 6

**Date and what I was working on:** 2026-09-27 — reading the course guides and checking the build constraints before planning beats.

**I tried / expected:** I expected to use the ai-explainer template as it is.

**What happened:**
- The guides are in the course repo's `prerequisites/`: `frictional.md`, `brutalist-video.md`, `brutalist-video-sources.md`. brutalist.art has none of them.
- `brutalist-video.md` says: *"For this first video, use existing chart/diagram components and avoid equation beats."* This conflicts with brutalist's MATH-TYPESETTING rule (structured math is required wherever math appears) now that LaTeX works.
- **Persona check:** no course document tells students to use the instructor's personas. `NEU-COURSELOOP.md` uses "Liam, in for Bear" but says *"These are instructor films, not a new student video requirement."* `brutalist-video.md`: *"Do not imply a synthetic narrator is me, Bear, or an official endorsement … disclose synthetic narration."* `brutalist-video-sources.md`: *"Historical channel/persona credits do not authorize a student to impersonate the instructor or claim endorsement."* The ai-explainer SKILL.md *defaults* to `claude-liam` (IN-FOR-BEAR LAW, `@NikBearBrown` chip, NBB logo bug, locked outro), so the student build has to depart from the skill's house laws.
- `bookend_check.py` (which enforces the Claude cold open / Your Turn / ClaudeTitleOutro) isn't called by `run.sh`, `compile.py`, or `art`, so dropping those bookends won't block a build.
- The course repo contains other students' `fall-2026/*/week-01-video/` submissions. I didn't read them.

**What I did:** I decided to remove every Claude interface beat and the instructor persona, and to keep only real or labelled numbers.

**What Claude or another person contributed:** Claude located and read the guides, the full ai-explainer SKILL.md, and Chapter 1's treatment of 665.24 vs 630, and checked the persona rules. I set the constraints: no mock Claude responses, no instructor personas, only real or labelled numbers.

**What I understand now / still do not understand:** The template's cold open shows a Claude answer I never actually got, and the assignment says any Claude response on screen must be real and dated. "Liam, in for Bear" is for the instructor's own films, not student work.

**Evidence and next step:** Next: review the draft beat plan and approve the narration at GATE P before any audio or render.

---

## Entry 7

**Date and what I was working on:** 2026-09-27 — build decisions and a second toolkit patch.

**I tried / expected:** Since LaTeX was installed, I expected to show the math as typeset equations.

**What happened / decisions made:**
- **DECISION: counters only, no equation beats.** The course guide `prerequisites/brutalist-video.md` ("For this first video, use existing chart/diagram components and avoid equation beats") **takes priority over** brutalist's `docs/MATH-TYPESETTING.md` / ai-explainer "Math" hard rule (structured math wherever math appears). 1000 × p is shown as a counter, not a typeset equation. MiKTeX stays installed but unused.
- **DECISION: no Claude interface and no instructor persona.** B00 ClaudeComposerAsk, the ask→result micro-beats, the verdict artifact page, the Your Turn composer, ClaudeTitleOutro, the NBB logo bug, the `@NikBearBrown` chip and "Liam, in for Bear" are all dropped. These are knowing departures from the ai-explainer SKILL.md house laws, not oversights.
- **UPSTREAM WORKAROUND — `compile.py` drawtext patched locally, NOT committed.** At `runtime/scripts/compile.py:789`, the review-cut timecode filter used the raw font path (`fontfile=C:\…ttf`), which ffmpeg's filter parser splits at `:` and `\`. The patch adds `ff_font = str(font).replace("\\", "/").replace(":", "\\:")` and quotes it (`fontfile='{ff_font}'`) — 4 lines added, 1 changed, used only in the ffmpeg filter (PIL still gets the raw path). Exact change: `brutalist-compile-local-patch.diff`. Revert with `git -C C:\info7375\brutalist.art checkout -- runtime/scripts/compile.py`.
- **Verified by the smoke replica:** after the patch, compile writes `smoke-slate.mp4` (927,362 B, video + audio streams, mean_volume −24.2 dB), which passes all three smoke_test.sh gates (size, type, audio).
- **New Windows friction: `'charmap' codec can't encode character '\u2192'`.** Python on Windows defaults to cp1252, and the toolkit prints `→`, so the build stamp step was "REFUSED". Fixed without code changes by exporting `PYTHONUTF8=1` before every toolkit command.
- **New friction: GATE V fails on the review cut's own timecode.** With drawtext working, `run.sh` exits 2: GATE V reports 4 × BLOCKER `edge-bleed` (right/top). The frame shows the only thing there is the burned-in timecode `00:00:04.000` at `x=w-text_w-16, y=16`, outside the title-safe inset. Unverified guess: upstream doesn't see this where ffmpeg lacks drawtext. **Unresolved: every `./art run` review cut here will fail GATE V until this is handled.** The slate label also shows `B00 ? SLATE`. **Correction (2026-09-27, Entry 9):** this was first logged as a missing glyph, which was wrong. The label is `f"{bid} {stype} {status}"` (`compile.py:744`), and `stype` is literally `?` because the smoke beats have no shot type (log: `motion histogram: ?:2`).

**What Claude or another person contributed:** I made both decisions and approved the compile.py patch. Claude wrote and tested the patch, found the UTF-8 and GATE V problems, and inspected the flagged frame.

**What I understand now / still do not understand:** The course guide says to avoid equation beats in the first video, and for this assignment the course guide comes before the toolkit's rules. I also learned that Python on Windows uses a different text encoding by default, which is why PYTHONUTF8=1 is needed.

**Evidence and next step:** `brutalist-compile-local-patch.diff`, `logs/art_smoke_replica_2026-09-27_run2.log` (charmap), `logs/art_smoke_replica_2026-09-27_run3.log` (GATE V), `_font-check/smoke-slate-t4.png`, `_font-check/gatev-contact_sheet.png`. Next: decide how to handle the GATE V timecode before the first `./art run` of the reel.

---

## Entry 8

**Date and what I was working on:** 2026-09-27 — producing the real evidence for B04 and B06, and a voice audition.

**I tried / expected:** Asked for the exact seed-7 sequence to be regenerated with the same call `sample()` makes, with its counts confirmed to match main.py (268, 630, 102) before use, and for a real B06 repeat run.

**What happened:**
- `evidence/seed7_sequence.py` imports `probabilities` and `sample` from the course's `main.py` and calls `random.Random(7).choices(range(3), probabilities([1, 2, 3], 1.0), k=1000)`. Counts are `{'1': 268, '2': 630, '0': 102}`, an **exact match**, also asserted against `sample()` itself. First 20 draws: `1, 1, 2, 0, 2, 2, 0, 2, 0, 2, 0, 1, 2, 2, 1, 1, 2, 2, 2, 2`.
- B06 repeat run: `main.py` re-run on Python 3.11.9 → `evidence/main_output_rerun_2026-09-27.txt`. `fc /b` reports no differences, SHA-256 `EC682946…EFB4A7` for both.
- **Checked assumption:** the course's repeatability test `test_04` checks `sample([1, 2])`, not `[1, 2, 3]`. So the narration must not claim the course test proves 630 repeats. B06 relies on the real re-run only.
- Voice audition (not reel audio): the same sentence in `af_bella` (9.34 s) and `am_onyx` (8.77 s), exit 0, cost $0.00.

**What Claude or another person contributed:** I specified the verification requirement. Claude wrote the script, ran it and the re-run, and read `test_main.py`.

**What I understand now / still do not understand:** A seed makes a run repeatable, and my byte-identical re-run proves that on my machine. The course's own test only checks [1, 2], so I cannot use it as proof that 630 repeats.

**Evidence and next step:** `evidence/seed7_sequence.py`, `evidence/seed7_sequence.json`, `evidence/main_output_rerun_2026-09-27.txt`, `_voice-test/mp3/beat-B00.mp3` (af_bella), `_voice-test/mp3/beat-B01.mp3` (am_onyx). Next: pick a voice, then review the narration at GATE P.

---

## Entry 9

**Date and what I was working on:** 2026-09-27 — narration edits, the GATE V timecode patch, and checking the B08 snippet.

**I tried / expected:** I sent my decisions to Claude Code but accidentally left the voice as a placeholder, so it did not pick one for me.

**What happened:**
- **Narration edits (proposed by a separate Claude chat, reviewed and approved by me), before GATE P:** B03 now says "the average number of token twos you would see across many runs of a thousand draws". B06 adds "on this machine". B07 ends with "A single run cannot give you that criterion. You have to decide it first." GATE P is **not yet signed**. I will sign it myself.
- **Voice not yet chosen.** My decision message left the voice as a placeholder.
- **UPSTREAM WORKAROUND — `compile.py` review timecode moved inside title-safe, NOT committed.** `x=w-text_w-16:y=16` became `x=w*0.95-text_w-8:y=h*0.05+8` (the 5% inset of `layout.ts` SAFE, box border included), 1 line changed plus 1 comment line. Incremental diff (on top of the drawtext patch): `brutalist-compile-timecode-local-patch.diff`. Both compile.py patches together: `brutalist-compile-local-patch-cumulative.diff`. Revert both with `git -C C:\info7375\brutalist.art checkout -- runtime/scripts/compile.py`.
- **Verified:** the smoke replica through `run.sh` now exits 0, with GATE V `BLOCKER=0 MAJOR=0`. In a 4K review frame the timecode box ends at about x≈3648, y≈106, at the safe edge. The bottom-left review beat label (`overlay=16:H-h-16`) is still outside title-safe. GATE V doesn't flag it, and it's review-only.
- **`./art final` does not burn in the timecode, confirmed from code only.** `art:139-141` calls `compile.py` without `--review`, the timecode is drawn only under `if a.review and drawtext` (`compile.py:788`), and the beat labels only under `if a.review` (`compile.py:741`) unless `metadata.keep_review_labels` is set. **Not confirmed on output yet.** `./art final` on the smoke copy was refused ("--allow-slates is review-only; a final cannot contain missing visuals"), which is by design, since the fixture is all slates. GATE T passed before the refusal. Next: check a frame of the first real final.
- **B08 snippet verified.** The exact on-screen code (`evidence/b08_your_turn_snippet.py`) was run the way a viewer would, from `lessons/01-randomness-and-first-prompts/code` via `py -3.11 -`. Exit 0, 20 well-formed `seed count` lines for seeds 1–20. **I didn't read or report the counts, and they must not appear in the video body** (my decision: the seed sweep is only a Your Turn suggestion). Output kept only as check evidence: `evidence/b08_snippet_check_2026-09-27.txt`. Decide whether to include it in the submission.
- **Submission workflow:** still unresolved (the course docs don't say fork/PR vs direct push, and use `fall-2025/` while ASSIGNMENT.md says `fall-2026/`). My decision: nothing gets pushed anywhere until it's worked out from the assignment instructions.

**What Claude or another person contributed:** I wrote the narration edits and approved the patch. Claude made and tested the patch, traced the review-only code paths, ran the snippet check, and corrected its own earlier missing-glyph claim.

**What I understand now / still do not understand:** Adding "on this machine" matters. Repeatability depends on the environment, so the narration should only claim what I actually checked.

**Evidence and next step:** `brutalist-compile-timecode-local-patch.diff`, `brutalist-compile-local-patch-cumulative.diff`, `logs/art_smoke_replica_2026-09-27_run4.log`, `_font-check/smoke-slate-t4-safe.png`, `logs/art_final_smoke_2026-09-27.log`, `evidence/b08_snippet_check_2026-09-27.txt`. Next: choose the voice and sign GATE P.

---

## Entry 10

**Date and what I was working on:** 2026-09-27 — GATE P, voice, and the first build (beat sheet, audio, scenes, review cut).

**I tried / expected:** I listened to both voices and picked af_bella because it sounded clearer to me. I reviewed the narration before signing GATE P, and I read it aloud afterwards to confirm my verdict.

**What happened / decisions made:**
- **DECISION: voice = `af_bella`** (after listening to both auditions).
- **DECISION: B07 cut.** "set in advance" removed, so the line reads "To call it broken, or normal, you need an acceptance criterion. A single run cannot give you that criterion. You have to decide it first."
- **DECISION: B08 card shows the folder path** `lessons/01-randomness-and-first-prompts/code`.
- **DECISION: GATE P — PASS.** Recorded in `PEDAGOGY.md` exactly as: "VERDICT: PASS — signed by Prathamesh P, 2026-09-27. When I first signed, I had reviewed the narration by reading it silently. I then read the full narration aloud on 2026-09-27 and confirm this verdict." I later read the full narration aloud and can defend every sentence. The signed narration's SHA-256 fingerprint is `8afc5b04…c358c` (full value in PEDAGOGY.md). Re-checked after audio generation: unchanged.
- **Reel audio:** `generate_audio_kokoro.py` exit 0, cost $0.00. B00–B09 = 12.05 / 13.97 / 14.70 / 18.24 / 16.81 / 18.39 / 13.78 / 17.79 / 15.66 / 7.94 s, **total 149.33 s ≈ 2:29** (target 2–3 min).
- **Toolkit behaviours found while authoring** (read from source, so scenes are built to fit them):
  - `compile.py` **slows** clips shorter than their audio and **center-cuts** longer ones (`compile.py:257-276`), so every scene reads its beat's `actual_duration_s` and ends exactly on it.
  - `BrutalistHesitantWriter` triggers match **single words only** (`buildActs`, whitespace tokens), so the B01 correction is three positional swaps (code→distribution, predicts→expects, 665→665.24) that rewrite the whole sentence.
  - PT Mono ships in `runtime/fonts` but isn't installed on Windows, so `scenes.py` registers PT Mono and EB Garamond from their bundled files (`manimpango.register_font`).
  - Terracotta `#D97757` is about 2.9:1 on the cream page, below GATE W's 3.0 floor for text, so it's used for shapes only and `#A44A32` for accent text.
  - `DecimalNumber` counters render through LaTeX, so the counters are `Text` redrawn per frame instead (no equation beats).
  - Library-first (`./art scenes`): hits for bars/code/title cards were Claude-skinned, the Codex palette, or another brand, so they're custom Manim scenes in `scenes.py`. No template misses were logged.
- **Friction:** the Microsoft Store `python3` alias is still active outside the venv (`python3 -c …` printed "Python was not found"). Harmless inside the venv. _(you said you'd turn the aliases off)_

**What Claude or another person contributed:** I chose the voice, made the B07/B08 edits, and signed GATE P. Claude wrote `beat_sheet.json`, `scenes.py`, `PEDAGOGY.md` (recording my verdict verbatim; Claude signed nothing), `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` and `CHECKS-REPORT.md`, generated the audio, and started the review build.

**What I understand now / still do not understand:** The narration audio is the clock for the whole video. Every scene is timed to the measured audio, which is why the audio is generated before the visuals.

**Evidence and next step:** `PEDAGOGY.md`, `beat_sheet.json`, `mp3/timings.json`, `logs/audio_2026-09-27.log`, `scenes.py`, `FACTCHECK.md`, `logs/art_run_2026-09-27_1.log`. Next: review cut, QC, then `./art final` with a frame check for burned-in timecode or labels.

---

## Entry 11

**Date and what I was working on:** 2026-09-27 — first `./art run` attempts (runs 1–4).

**I tried / expected:** I expected the first build to go through once the scenes were written.

**What happened:**
- **Run 1 — my scene bug:** "nothing to render". `run.sh` finds scenes with the regex `class ([A-Z][A-Za-z0-9]*_\w+)\(Scene\)` (`run.sh:104`), and Claude's scene classes subclassed a `Beat` helper, so zero were found. Fixed: every beat is `class Bxx_Name(Scene)`, with helpers attached by a `@beat` decorator. A comment in scenes.py that literally contained that class pattern would also have matched (phantom scene `Bxx_Name`), so the comment was reworded.
- **Run 2 — GATE A false positive on B04:** "shapes never change — 1 distinct shape-state… (repeated animation)". The static checker runs `construct()` against a stub that doesn't execute `always_redraw` updaters. Fixed with the same fidelity: B04 now draws the **exact real cumulative counts once per frame** (about 10 draws per frame at 24 fps). The final frame is draw 1000 = 102 / 268 / 630.
- **Run 3 — GATE B (strict) failed B03:** "label on a curve/line: `665.24`". The box around ".24" cut through the number's own text box. Fixed: ".24" is marked by colour (`#A44A32`) with "not an integer" above it, and nothing crosses the text. B06's line boxes were tightened (buff 0.06 → 0.03) for the same reason.
- **Run 4:** all 9 Manim beats pass GATE A (text-only warnings are non-blocking), GATE W (all clean) and GATE B (strict), and are slotted in `manim/`. Every clip is within ±0.04 s of its measured audio.
- **BLOCKER — B01 Remotion fails on Windows:** `[WinError 2] The system cannot find the file specified`. `remotion_scenes.py:90` runs `subprocess.run(["npx", "remotion", "render", …])`, and on Windows `subprocess` without a shell resolves only `npx.exe`, while npm installs `npx.cmd`. `remotion_scenes.py` has no skip switch and `run.sh` exits on the failure, so **no review cut can be compiled yet**. Not patched, since it's unapproved. The toolkit also says never hand-roll `npx remotion render` (CLAUDE.md rule 4), so that workaround was not used.
- Claude's own check of the Manim end-frames (`_qc/manim-preview/sheet.png`): B02's code excerpt renders small (about 26 px/em at 1080p) with dead space around it. Candidate for revision after watching.

**What Claude or another person contributed:** Claude wrote and fixed the scenes and diagnosed each gate failure from the toolkit source. I did not approve any toolkit change in this round; the fixes were all in our own scenes.py.

**What I understand now / still do not understand:** The toolkit finds scenes by matching class names, and its static checker cannot see animations that only happen through updaters. I now know the Remotion failure was npx.cmd versus npx.exe on Windows, but I do not fully understand why Python only finds one of them.

**Evidence and next step:** `logs/art_run_2026-09-27_1.log` … `logs/art_run_2026-09-27_4.log`, `layout_audit.md`, `manim/B00.mp4`…`manim/B09.mp4`, `_qc/manim-preview/sheet.png`. Next: decide on the `remotion_scenes.py` npx patch.

---

## Entry 12

**Date and what I was working on:** 2026-09-27 — unblocking B01 and building the review cut (run 5).

**I tried / expected:** I expected the review cut to pass once B01 rendered.

**What happened:**
- **DECISION:** approved the one-line npx patch (option 1), rather than rebuilding B01 in Manim.
- **UPSTREAM WORKAROUND — `remotion_scenes.py` npx lookup patched locally, NOT committed.** At `runtime/scripts/remotion_scenes.py:90`, `"npx"` became `shutil.which("npx") or "npx"` (1 line changed; `shutil` was already imported). On this machine it resolves to `C:\Program Files\nodejs\npx.CMD`. Exact change: `brutalist-remotion-npx-local-patch.diff`. Revert with `git -C C:\info7375\brutalist.art checkout -- runtime/scripts/remotion_scenes.py`.

- **Remotion downloaded headless Chrome** on the first render: `brutalist.art/runtime/remotion/node_modules/.remotion/chrome-headless-shell/` (270 MB on disk; absent before run 5). Free; inside the toolkit's ignored `node_modules`. No key or account needed.
- **Review cut compiled:** `week-01-expected-vs-observed-slate.mp4`, **149.5 s** (ffprobe), 10/10 slots filled (9 Manim + B01 Remotion). Also `qc-sheet.png` and `_qc/contact_sheet.png`.
- **GATE V FAILED (strict): 2 BLOCKER, 2 MAJOR** (`_qc/REPORT.md`):
  - B06 at 50% / 85%: BLOCKER `edge-bleed`, left/right. Claude's two output panels are 6.2 units wide at x = ±3.4, so their outer edges reach ±6.5, past title-safe.
  - B01 at 50% / 85%: MAJOR `underfill`, content fills 40% / 50% of the safe area (min 55%).
- Also seen on the contact sheet (not a gate result): B01's "CONSTRUCTED EXAMPLE" banner is tiny (fixed 18 px in the component) and in the review cut sits under the timecode. It's my required label, so it has to be legible in the final.
- **Expected SKIN LINT warnings:** B00 "COLD OPEN LAW wants ClaudeComposerAsk", B09 "OUTRO LAW wants ClaudeTitleOutro". These are my deliberate departures (Entries 6–7), not fixed.
- The GATE V contact sheet image shows B00–B07 only. B08/B09 frames were pulled from the cut by Claude into `_qc/contact_sheet_B08_B09.png`, and GATE V reported no defects there.
- **Not fixed yet, by my decision:** I will watch the review cut with sound before deciding on B02, B01, B06 or anything else.

**What Claude or another person contributed:** I approved the patch. Claude applied it, saved the diff, built the cut and read the QC output.

**What I understand now / still do not understand:** The visual check caught things I would have missed, like panels past the safe edge and a label too small to read. My "constructed example" label has to be readable, not just present.

**Evidence and next step:** `brutalist-remotion-npx-local-patch.diff`, `logs/art_run_2026-09-27_5.log`, `week-01-expected-vs-observed-slate.mp4`, `_qc/REPORT.md`, `_qc/contact_sheet.png`, `_qc/contact_sheet_B08_B09.png`. Next: watch the review cut with sound.

---

## Entry 13

**Date and what I was working on:** 2026-09-27 — reviewing the cut and approving three fixes.

**I tried / expected:** I watched the review cut with sound and it looked good to me.

**What happened:**
- **I watched the review cut (`week-01-expected-vs-observed-slate.mp4`, 149.5 s) with sound and found no issues beyond the three fixes below.**
- **DECISION: approved fixes, no narration changes (GATE P stays signed):**
  1. **B06:** panels narrowed to 5.6 units at x = ±3.1 (now spanning ±0.3 … ±5.9, inside title-safe), with the text inside capped at 5.0 units.
  2. **B01 (beat sheet props only, no narration or toolkit change):** same words and the same three corrections, now on three lines at `fontSize` 92 ("The code predicts / 665 of token 2. / One seeded run of 1,000 draws gave 630.", corrected to "The distribution expects / 665.24 of token 2. / …"). `contextTitle` "Constructed example" (60 px heading). `brandLabel` carries the synthetic-narration disclosure (28 px) that B01 was missing. The small `banner` is kept.
  3. **B02:** code block enlarged. It now gets a 9.4-unit column (was 7.6) at base size 24 with 0.52 line pitch, and the probability bars move to a compact right-hand column. The code text is unchanged (verbatim main.py lines).
- Narration fingerprint re-checked after the B01 prop edit: still `8afc5b04…c358c`, so GATE P is unaffected.
- To force the re-render, Claude deleted only the three regenerated clips (`media/B01.mp4`, `manim/B02.mp4`, `manim/B06.mp4`), because the toolkit skips existing outputs (`remotion_scenes.py:78`, `run.sh:113`).

- **Run 6 — GATE A error on B02:** "2 explicit coord(s) outside the frame, e.g. (0.0,-4.2) in move_to". Claude's `code_block` helper laid lines out at y = −i × pitch before centring, and the larger 0.52 pitch pushed raw coordinates past ±4.0. Nothing was rendered, so `_qc/REPORT.md` and the cut were still run 5's. Fixed by laying lines out centred from the start. B06 and B08 use the same helper but are re-centred afterwards, so their layout is unchanged.
- **Run 7 — GATE V clean (0 BLOCKER / 0 MAJOR), but Claude found a defect the gates missed:** in the enlarged B02 the bar labels touched ("token 0token 1token 2"), because the narrower bar column spaced them 0.8 units apart. That came from the B02 fix itself, so it was fixed within the same approval: code column 9.0 units (from 9.4), bars 1.0 apart.
- **Run 8 — GATE V clean: 0 BLOCKER / 0 MAJOR across 20 frames. Review cut 149.5 s, 1920×1080, 10/10 filled.** Full-res check of B02 (`_qc/B02_1080_full.png`): code readable at 1080p (caps about 22 px), labels separated.
- Still open, not a gate failure: EB Garamond word spacing looks tight in places (e.g. "input checks omitted", the disclosure line), the same Pango spacing seen in the Entry 5 font probe. GATE T (with its kerning check) runs at `./art final`.

**What Claude or another person contributed:** I watched the cut and chose the fixes. Claude implemented them, caught its own B02 label collision on the contact sheet, and rebuilt.

**What I understand now / still do not understand:** It looked fine to me, but the checks still found problems I had not noticed, so watching it myself is not enough on its own.

**Evidence and next step:** `logs/art_run_2026-09-27_6.log`, the new `_qc/REPORT.md` and `_qc/contact_sheet.png`. Next: check GATE V, then (only when I say so) `./art final`.

---

## Entry 14

**Date and what I was working on:** 2026-09-27 — `./art final`, SOURCES.md and README.md drafts.

**I tried / expected:** I rewatched the rebuilt review cut, found it good, and asked for `./art final --height 1080 --out final/`. I expected the final to render without problems, since the review cut had passed.

**What happened:**
- **`./art final` BLOCKED by GATE T (`TYPECHECK.md`, exit 2). No final master was written (`final/` does not exist).** 2 FAILs, both **min-size §8.1** (floor 41 px = 1.9% of the 2160 px clip frames): B05 "smallest text run 39px", B08 "36px". Everything else passed: **kerning §8.4: 9 beats checked, 0 FAIL**; overflow, contrast, contrast-local, bbox-overlap and card-clip all 0 FAIL; redundancy §8.10 advisory, skipped.
- **Root cause, found with GATE T's own functions** (`visible_text_mask` → `labeled_blobs` → `text_run_bboxes`) on the clip frames:
  - B05: the shortest runs were on the legend line. First the standalone `=` signs ("outline **=** expected", "filled **=** observed"), then, once those were gone, the fragment "rve" of "obse**rve**d". Pango's tight EB Garamond spacing splits the word, and the legend was shrunk to about size 21.6 by `fit()` because it's long.
  - B08: the note "suggestion — results not shown" at size 24.
  - The label bounding boxes are all ≥ 58 px. GATE T measures pixel runs, not labels.
- **Trial fix in a scratch copy (reel folder untouched), verified with GATE T's `check_min_size`:** B05 legend → "outline: expected (computed)   ·   filled: observed (main.py, seed 7)" at size 26 (no `=`, no shrink; "1000 × p" dropped from this legend only, since B03 shows it). B08 note size 24 → 28. Result: B05 PASS at 15/50/85/97% (41, 41, 46, 46 px, just at the floor). B08 PASS (53, 42, 43, 43 px). **Not applied: it changes on-screen text beyond the three fixes I approved. Waiting for my decision.**
- **SOURCES.md drafted.** Licences were read from local files and metadata only.
  - **licence not found** for: brutalist.art (no LICENSE in repo), the `BrutalistHesitantWriter` origin ("brik/base44 … Author unknown"), the Kokoro voices file, espeakng-loader, and Segoe UI (B01's banner font, a Windows system font).
  - The Kokoro model licence, "Apache 2.0", is as stated in kokoro-onnx's METADATA. No file ships with the model.
  - Oswald's OFL 1.1 was read from the font's own name table, since no licence file was downloaded. Oswald isn't used in the video.
  - The "separate Claude chat" contribution is left for me to describe.
- **README.md drafted.** "Why this concept" and the runtime are left blank: the reason is mine to write, and the runtime waits for the final master.

**What Claude or another person contributed:** Claude ran the final build, traced the GATE T failures to specific glyph runs, tested a fix in scratch, and drafted SOURCES.md and README.md. I chose to write the "why this concept" line and the Claude chat contribution myself rather than let Claude Code guess them.

**What I understand now / still do not understand:** The type check measures small runs of glyphs, not whole labels, so tight letter spacing can split a word into pieces that fail. For some assets, like brutalist.art, I could not find a licence, and it is better to say so than to guess.

**Evidence and next step:** `logs/art_final_2026-09-27.log`, `TYPECHECK.md`, `SOURCES.md`, `README.md`. Next: decide on the B05/B08 text-size fix, then re-run `./art final` and check the final frames for burn-ins.

---

## Entry 15

**Date and what I was working on:** 2026-09-27 — GATE T fix with margin, relative paths, log move, second `./art final`.

**I tried / expected:** I expected the final to pass once the text sizes were fixed.

**What happened / decisions made:**
- **DECISION: FRICTIONAL.md structure fixed.** Entry 14 had been inserted inside Entry 13. Entry 13's last two lines were moved back above Entry 14. No content changed.
- **DECISION: GATE T fix approved with more margin (≥ 45 px at every sampled point), no narration changes.** Applied:
  - B05 legend → "outline: expected (computed)   ·   filled: observed (main.py, seed 7)" at **size 32** (10.96 units, no `fit()` shrink).
  - B08 note → **size 30**.
  - Checked with GATE T's `check_min_size` at 11 points (2–98%) on fresh 4K renders before rebuilding: B05 45–46 px, B08 46–53 px.
  - Along the way: size 30 left B05 at 44 px (the legend's own lowercase letters). A trial raising B05's value labels to 26 made no difference, so it was reverted (value labels stay 24).
- **DECISION: scenes.py paths made relative.** Evidence files resolve from the reel folder, and fonts from the sibling `../brutalist.art/runtime/fonts` (a missing font now raises instead of silently falling back). No absolute paths remain.
  - **Verified no change to output:** B02, B04 and B06 stills rendered before and after are byte-identical (SHA-256).
  - **Friction:** GATE A runs an isolated copy of `scenes.py` in a temp folder (`run.sh:167-172`), where no reel-relative path can work. The old absolute fallback had hidden this. Solution: the copy finds the reel via the `WEEK01_REEL_DIR` environment variable, which is only used there; it fails with a clear message if unset. README step 6 updated.
- **Run 9 (review cut):** B05 and B08 re-rendered, GATE V 0 BLOCKER / 0 MAJOR, 149.5 s.
- **`./art final` (2nd attempt): GATE T PASS (0 FAILs, kerning 0)**, but the final frame check (`final_frame_check.py`, strict) **refused** the candidate master: **B09 MAJOR `underfill`, 44% of the safe area (min 55%)** at 50% and 85%. `final/` is empty.
  - Why the review cut passed: the review-only timecode (top-right) and beat label (bottom-left) are counted as content and inflate the bounding box. **The review-cut GATE V doesn't predict the final check for sparse beats.**
- **Trial B09 fix in scratch (reel folder untouched), positions only, same text and sizes:** title y 1.3 → 2.1, name 0.0 → 0.4, provenance −0.8 → −1.5, disclosure −1.35 → −2.2. `final_frame_check.analyze_frame` gives **66% coverage, no defects** at 50% and 85%. **Not applied, awaiting my decision.**
- **DECISION: logs moved into `logs/`** (20 files). FRICTIONAL.md (15 references) and BUILD-PROMPT.md (6) updated to `logs/…`.
- **DECISION: README note added:** `evidence/b08_snippet_check_2026-09-27.txt` records only that the snippet runs; its contents weren't reviewed or used in the video. `_voice-test/` and `_font-check/` are listed as cited evidence.

**What Claude or another person contributed:** I set the margin target and decided on paths, logs and the file list. Claude implemented and verified each change and diagnosed the final-check failure.

**What I understand now / still do not understand:** The review cut's check is not a reliable preview of the final check for sparse screens, because the review-only timecode and labels count as content. I still do not fully understand why the toolkit measures fill that way.

**Evidence and next step:** `TYPECHECK.md` (PASS), `logs/art_run_2026-09-27_9.log`, `logs/art_final_2026-09-27_2.log`, `_qc/REPORT.md` (now the final-check report, B09 underfill). Next: decide on the B09 layout fix, then `./art final` and the burn-in frame check.

---

## Entry 16

**Date and what I was working on:** 2026-09-27 — B09 fix, final master, burn-in check, consistency check.

**I tried / expected:** I expected the final to look the same as the review cut without the overlays.

**What happened:**
- **DECISION: B09 layout fix approved (positions only, same text and sizes).** Applied exactly as tested (diff against the scratch trial: identical). Title y 1.3 → 2.1, name 0.0 → 0.4, provenance −0.8 → −1.5, disclosure −1.35 → −2.2.
- **Run 10 (review cut):** B09 re-rendered, GATE V 0 BLOCKER / 0 MAJOR.
- **`./art final` (3rd attempt) SUCCEEDED:** GATE T PASS (0 FAILs, kerning 0), final frame check passed. `final/week-01-expected-vs-observed.mp4` + `final/week-01-expected-vs-observed.verified.json`. SKIN LINT warnings for B00/B09 (no Claude composer / ClaudeTitleOutro) are expected, per my decision.
- **Final master:** **149.5 s (2:29.5), 1920×1080, H.264 24 fps + AAC, 7,112,377 bytes** (ffprobe). README runtime filled in.
- **Burn-in check on the final master:** frames at 6.0 s (B00), 67.0 s and 75.5 s (B04), 145.5 s and 149.0 s (B09), saved in `_qc/final-check/`. **No timecode and no beat labels.** Checked two ways: by eye (`_qc/final-check/final_B00_B04_B09.png`), and by the darkest pixel in the timecode region (top-right) and beat-label region (bottom-left), compared with a review-cut control frame (97–98 with the overlays). B00 and B09 read 248 (plain cream) in both corners. B04's top-right read 32, and the crop (`_qc/final-check/B04_topright_crop.png`) shows it's the end of B04's own code line "…1.0), k=1000)", not an overlay.
- **Consistency check** (script in Claude's scratchpad): every file in README's contents table exists; every path cited in FRICTIONAL.md (98) and BUILD-PROMPT.md (84) resolves on disk. The only non-literal paths are shell expansions (`$b`, `{before,after}`), whose expanded files exist.
- **Open, for my decision:** FRICTIONAL.md cites some build outputs that the proposed submission list leaves out (`manim/B00–B09.mp4`, `media/B01.mp4`, `mp3/timings.json`, `layout_audit.md`, `qc-sheet.png`, the review cut `week-01-expected-vs-observed-slate.mp4`). They resolve now, but won't inside the zip unless included or noted.

**What Claude or another person contributed:** I approved the B09 fix. Claude applied it, built the final, checked the frames and ran the path checks.

**What I understand now / still do not understand:** Checking frames by pixel, not only by eye, is what confirmed the final has no burned-in timecode. The files my logs cite have to be in the zip, or those references lead nowhere.

**Evidence and next step:** `final/week-01-expected-vs-observed.mp4`, `final/week-01-expected-vs-observed.verified.json`, `TYPECHECK.md`, `logs/art_run_2026-09-27_10.log`, `logs/art_final_2026-09-27_3.log`, `_qc/final-check/`. Next: decide how to handle the omitted-but-cited build outputs, write my own FRICTIONAL fields, the Claude-chat contribution in SOURCES.md and "Why this concept" in README.md; then create the zip and post (both only on my instruction).

---

## Entry 17

**Date and what I was working on:** 2026-09-27 — correcting my name before submission.

**I tried / expected:** I expected my name in the files to be correct. I had not noticed that my middle name was being used as my last name until I checked.

**What happened:**
- **My name had been recorded wrongly:** my middle name had been used as my last name.
- The course repo's `fall-2026/README.md` (read at `origin/main` `3f3e09f` after `git fetch`; my working clone is still at `b293224`) says: "One folder per person … `first-name-last-initial`, kebab case. **No IDs and no full names are stored here.**" My folder is `prathamesh-p/`.
- **DECISION: the wrong name → "Prathamesh P" everywhere in this folder**, following that rule (full names are not written into these files). Files changed: `beat_sheet.json` (metadata `author`), `scenes.py` (B09 outro text), `PEDAGOGY.md`, `FRICTIONAL.md`, `README.md`, `SOURCES.md`, the toolkit-generated `todo.json` and `clips/_work/resolved-sheet.json`, and two build logs (`logs/art_run_2026-09-27_4.log`, `logs/art_run_2026-09-27_10.log`), where the name appeared only in Manim's progress lines echoing the B09 text. Those log edits are name-only; nothing else in them changed. The stale `__pycache__/` was deleted.
- **GATE P signature corrected, not re-signed.** In `PEDAGOGY.md` only the name in the verdict line changed ("signed by Prathamesh P"). The signature is unchanged in meaning: same verdict, same date, same narration. The narration fingerprint is still `8afc5b04…c358c`.
- The B09 outro card showed the wrong name on screen, so B09 was re-rendered and the review cut and final rebuilt. Run 11: GATE V 0 BLOCKER / 0 MAJOR. `./art final` (4th attempt): GATE T PASS, master written. **New final master: 149.5 s, 1920×1080, 7,094,875 bytes.** B09 now shows "Prathamesh P · INFO 7375, Week 1" (`_qc/final-check/final_B09_name.png`). Burn-in re-check on the new master (B00 6.0 s, B04 67.0/75.5 s, B09 145.5/149.0 s): no timecode or beat labels. Corner readings are identical to Entry 16 (B04's top-right dark pixels are its own code line). README byte count updated.
- Also noticed, not changed: `PEDAGOGY.md` line 9 still says "including the student's edits to B03, B06, B07", which conflicts with SOURCES.md's attribution of those edits to a separate Claude chat. _(awaiting my wording)_ **Resolved 2026-09-27:** line 9 reworded to my attribution text; narration fingerprint unchanged.
- **Friction: a byte scan can't see names inside images.** Three evidence images were made before the B09 name fix, and their B09 frames show the old full name on screen: `_qc/contact_sheet_B08_B09.png` (20:08), `_qc/manim-preview/sheet.png` (19:57) and `_qc/final-check/final_B00_B04_B09.png` (21:21, from the previous final master). The first one was also in the first zip, built before this was caught; that zip must not be uploaded. `qc-sheet.png` (21:44, after the fix) was checked by eye and shows "Prathamesh P". No new zip until I decide how to handle the three images.
- **DECISIONS on the three images:**
  - `_qc/final-check/final_B00_B04_B09.png`: **regenerated** from the current final master (same frames 6.0 / 67.0 / 149.0 s, same stacking and scale). Its B09 frame now shows "Prathamesh P".
  - `_qc/contact_sheet_B08_B09.png` and `_qc/manim-preview/sheet.png`: **redacted**. The name line in each B09 frame is covered by a labelled box reading "name redacted — corrected to Prathamesh P, see FRICTIONAL.md Entry 17". Nothing else in those images changed: the changed pixels are confined to the name line's rows (531–556 and 896–920), between the title and provenance lines. The unredacted originals are kept only in Claude's session scratchpad, not in this folder or the submission.
  - The old zip in `C:\info7375\submission\` (Canvas naming `LastName_FirstName_INFO7375_Week01_Video.zip`), which contained the unredacted contact sheet, is **deleted**.
- **Eye check of every other image that could contain a B09 frame:** `qc-sheet.png`, `_qc/final-check/final_t145.5.png`, `_qc/final-check/final_t149.0.png` / `_qc/final-check/final_B09_name.png` and the regenerated composite all show "Prathamesh P". `_qc/contact_sheet.png` has only B00–B07. The other images in the submission (smoke and font-probe frames in `_font-check/`, `_qc/B02_1080_full.png`, `_qc/final-check/B04_topright_crop.png`, final frames at 6.0 / 67.0 / 75.5 s) contain no B09 frame.

**What Claude or another person contributed:** I spotted the wrong name and set the rule-based choice. Claude read the repo rule, listed every match before changing anything, and made the replacement.

**What I understand now / still do not understand:** The course repo stores no full names, so my folder and files use my first name and last initial, while the Canvas zip still follows the assignment's LastName_FirstName naming rule. A GATE P signature can have its name corrected without re-signing, because the narration fingerprint proves the signed narration did not change.

**Evidence and next step:** `git show origin/main:fall-2026/README.md` (course repo); `PEDAGOGY.md` line 5. Next: rebuild with the corrected B09 and re-check the final frames.
