# FRICTIONAL — Prasad S, week-01 video
 
Process log for the week-01 explainer video (lesson 01, randomness and first prompts). Short dated entries, written during the session.
 
---
 
## Entries
 
### 2026-09-25 — brutalist.art setup: the ElevenLabs guard blocks its own toolkit
 
- **Date and what I was working on:** Setting up the external `brutalist.art` checkout (sibling of this course repo) per `prerequisites/brutalist-video.md`, so I can later build an ai-explainer reel. Toolkit revision: `6a8380ae169cca81e0633664a65c958f5c12ab4b`.
- **I tried / expected:** Ran `./setup --install` then `./setup` in a fresh venv. I expected the readiness table the prerequisite and HOW-TO describe, with some rows possibly blocked by missing system tools.
- **What happened:**
  - No table at all. Both runs exited 1 at the ElevenLabs guard, listing 10 files, all under the toolkit's own `youtube/brutalist/` example reels.
  - How the guard works (Claude Code read this in `setup`, lines 102–116, and reported it to me). Before any dependency check, it runs `grep -rqiE` over the whole checkout for four patterns: the ElevenLabs API-key env var name, the ElevenLabs domain, `"engine": "elevenlabs"` in JSON, and the `xi-api-key` header. Its own comment says *functional* ElevenLabs references are bugs and prose mentions are allowed. On any hit it prints the files and `exit 1`, so the readiness table is never reached.
  - The guard has no ignore or exclude mechanism. The only exclusions are hard-coded: `.git`, `node_modules`, `__pycache__`, `.claude`, `CHANGELOG*`, and `setup` itself. There's no flag, no ignore file, and no env var. `art` has nothing either.
  - Why these 10 are false positives with respect to the guard's intent:
    - 6 files are narration and prompts for the toolkit's own film *about* `setup`: `claude-liam-brutalist-command-setup/{SCRIPT.md, PROMPTS.md, beat_sheet.json, vertical/PROMPTS.md, vertical/beat_sheet.json}` and `shorts/claude-liam-brutalist-command-setup-short/PROMPTS.md`. They quote the guard's own pattern list and code on screen. That's documentation of the guard, and the guard matches its own description.
    - 4 files are demo fixtures holding legacy beat sheets with `"engine": "elevenlabs"`: `claude-liam-brutalist-runtime-brand-variant/demo/{canonical/beat_sheet.json, book-example/lectures/chap01-lecture/beat_sheet.json}` and `claude-liam-brutalist-skill-your-turn/demo/{fixture-beat_sheet.json, fixture-beat_sheet.applied.json}`. These are literal functional-looking config, but they are inputs to recorded demos, not live settings.
    - Reachability check (Claude Code ran this at my instruction; I reviewed the result rather than running the greps by hand): grepped `skills/make/ai-explainer/`, `runtime/scripts/`, `art`, and `setup` for every flagged folder and file name. **Zero hits.** A repo-wide grep found references only inside those same example reel folders (their README, build-state, CHECKS-REPORT, RUN-LOG) and the `youtube/brutalist/` index files (`WATCH.md`, `playlist.json`). No code path I use loads them.
- **What I did:**
  - First (Claude's attempt, which I later reviewed): it tried to run a scratch copy of `setup` with the guard block cut out, just to see the table. Claude Code's permission system refused that as weakening a safety check. We didn't try another workaround, and I agree with that call: it would have hidden the finding rather than dealt with it.
  - Then, on my instruction, Claude Code deleted exactly those 10 files from my local clone and **did not edit `setup`**. `git diff HEAD -- setup` is empty, and `git status` shows only the 10 `D` lines plus the untracked `.venv/`.
  - Why this keeps the guard's intent instead of weakening it: the pattern list, the grep scope, the exclusions, and `exit 1` are all unchanged. Any new functional ElevenLabs reference anywhere in the checkout, including my own reel if it lives inside the toolkit, still fails setup. Claude Code removed only inert example content that was matching its own documentation, at my direction — I set the boundary that detection logic in `setup` itself was not to be touched. Suppressing the check with an exclude or a patch would have blinded it for everything.
  - Rerun result: `./setup` now gets past the guard and prints the table. Fonts are ready. Everything else is blocked on real missing dependencies (ffmpeg, Node ≥ 20/npm, Python packages; see the next entry).
- **What Claude or another person contributed:** The approach here — root-cause the guard rather than patch around it, verify reachability before deleting anything, and hold the line at "don't touch detection logic" — was worked out first in a planning conversation with Claude (chat), before I gave the instruction to Claude Code. Claude Code (Opus 5.5) then read `setup`, ran the greps, sorted the hits into "quotes the guard" and "legacy fixture", and ran the deletion and reruns. I chose deletion over patching, set the boundary, and asked for the reachability grep before deleting anything. I accepted Claude's classification based on its report of the matched lines. 
- **What I understand now / still do not understand:**
  - Now: the guard is a repo-wide content scan, not a check on what the runtime actually uses. So it can't tell a film *about* the guard from a violation of it.
  - Still open:
    - Upstream still ships these files, so every fresh clone at this revision will fail the same way. This should go to the instructor rather than be fixed silently.
    - The deleted files leave those three example reels (and the one short) incomplete in my local copy.
    - The guard scans `.venv/` too (not excluded), and the prerequisite puts the venv inside the checkout. A third-party package that ever contained one of the patterns would trip it.
- **Evidence and next step:**
  - Evidence: `git -C ../brutalist.art status --short` (the 10 deletions). The first failing `./setup` output lists the same 10 paths, and the post-deletion readiness table is recorded in the next entry.
  - To restore the files: `git -C ../brutalist.art checkout -- youtube/brutalist`.
  - Next: install Python 3.11, Node 20, and ffmpeg, rebuild the venv, and get a green table.
### 2026-09-25 — Python 3.9 can't install the voice engine
 
- **Date and what I was working on:** Same session. Getting `./setup --install` to actually install the Python dependencies.
- **I tried / expected:** A venv from the default `python3`. I expected pip to install `requirements.txt`.
- **What happened:** The only Python on the machine is the macOS system 3.9.6. pip couldn't resolve `kokoro-onnx>=0.4`: every 0.4.x needs `onnxruntime>=1.20.1`, which doesn't install on 3.9. There was also no `npm`, `node`, `ffmpeg`, or Homebrew. `setup`'s own Python check is only `command -v python3`, so it would mark 3.9 as fine even though its hint says "3.10+". The course prerequisite says 3.11+.
- **What I did:** Approved Python 3.11 — identified, in a planning conversation with Claude, as satisfying both the 3.10+ and 3.11+ mentions — as the fix. The plan is Homebrew, then `brew install python@3.11 node@20 ffmpeg`, then rebuild `.venv` with `python3.11`. Homebrew's installer needs my macOS password (sudo), so I ran that step myself.
- **What Claude or another person contributed:** Claude Code found the version conflict in the pip output and pointed out that `setup`'s Python check doesn't enforce the version its own hint gives. The reconciliation — that 3.11 satisfies both documents' stated minimums — came out of a separate planning discussion with Claude (chat); I approved it and made the final call to proceed on that version.
- **What I understand now / still do not understand:** A readiness check that only tests "is it installed" can pass on a version that can't install the rest of the stack. I don't yet know whether `faster-whisper` and `manim<0.19` are fine on 3.11. The next `--install` run will show it.
- **Evidence and next step:** Readiness table after the guard fix, still on 3.9:
```text
  audio (Kokoro Bella/Onyx)    ❌ blocked   (ffmpeg, kokoro-onnx, Kokoro synth smoke test)
  captions + word clock        ❌ blocked   (ffmpeg, faster-whisper)
  Manim beats                  ❌ blocked   (ffmpeg, manim, Pillow)
  Manim equation beats         ❌ blocked   (ffmpeg, manim, LaTeX + dvisvgm)
  Remotion beats + bookends    ❌ blocked   (Node >= 20, npm install)
  slates / previz / compile    ❌ blocked   (ffmpeg, Pillow)
  fonts (EB Garamond + Oswald) ✅ ready
```
 
  Next: rerun `./setup --install` and `./setup` on 3.11 and record the table.
 
### 2026-09-25 — Rebuilt on Python 3.11: six of seven features ready
 
- **Date and what I was working on:** Same session. Installed the toolchain and rebuilt the toolkit venv on 3.11.
- **I tried / expected:** Installed Homebrew myself (it needs my password). Then had Claude Code run `brew install python@3.11 node@20 ffmpeg`, `rm -rf .venv && python3.11 -m venv .venv`, and `./setup --install`. I expected a green table apart from the LaTeX row.
- **What happened:**
  - Installed versions: Python 3.11.16, Node v20.20.2 (npm 10.8.2), ffmpeg 9.0.2. `node@20` is keg-only in Homebrew, so it isn't on PATH by default. The runs used `PATH=/opt/homebrew/opt/node@20/bin:$PATH`.
  - The first `--install` on 3.11 still failed pip. `pycairo` (pulled in by `manim<0.19`) couldn't build: `Did not find pkg-config` and `Dependency lookup for cairo ... failed`. The npm install for Remotion succeeded.
- **What I did:** Approved `brew install pkgconf cairo pango`, which Claude Code identified as the missing system libraries after reading the pycairo build failure. Neither the prerequisite nor HOW-TO lists these. On the rerun, pip installed everything. `npm install` rewrote the tracked `runtime/remotion/package-lock.json`; that's a local change I'm leaving uncommitted.
- **What Claude or another person contributed:** Claude Code ran the installs, read the pycairo meson log to find the missing `pkg-config` and cairo, and proposed `pkgconf cairo pango` as an extra step. I approved that step, approved the Homebrew install, and ran the Homebrew installer myself.
- **What I understand now / still do not understand:** "Python 3.10+, Node 20, ffmpeg" is not the full list of system prerequisites on a clean Mac. cairo, pango, and pkg-config are also needed for Manim. The ElevenLabs guard still passes with the new `.venv/` inside the checkout. I haven't checked whether `setup_smoke_kokoro.py` passing means a full reel renders. `./art smoke` is the documented proof, and I haven't run it yet.
- **Evidence and next step:** `./setup` on 3.11 (exit 1 only because of the equation row):
```text
  audio (Kokoro Bella/Onyx)    ✅ ready
  captions + word clock        ✅ ready
  Manim beats                  ✅ ready
  Manim equation beats         ❌ blocked   (LaTeX + dvisvgm — not used for this reel)
  Remotion beats + bookends    ✅ ready
  slates / previz / compile    ✅ ready
  fonts (EB Garamond + Oswald) ✅ ready
```
 
  Per the prerequisite, I'm recording the equation row honestly as blocked and not using equation beats in the first video. Next: draft the evidence packet for expected vs. observed counts.