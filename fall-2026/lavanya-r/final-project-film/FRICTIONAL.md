# FRICTIONAL — Final Project Pitch Film

Dated log of what I tried, what broke, and what I did instead.

## 2026-10-12: Planning
- Read the assignment and planned the work with Claude.
- Changed the plan: I have two working days, not five, because the film is due Wed 2026-10-14 at 11:59pm. I kept every required piece and compressed the schedule.
- Considered several topics: a Reallocation Engine recipe, a photo-grouping tool, and a DevOps workflow. I wanted a general software-engineering project, so I dropped those and chose the **README Checker**. It is easy for a stranger to verify, because a setup step either runs or it doesn't.

## 2026-10-13: Toolkit setup
- My `brutalist.art` clone was 48 commits behind and did not include the `show-tell` skill the assignment recommends. I stashed my old local edits (they are not deleted) and pulled. `show-tell` is now present (commit `519fcbb`).
- `./setup --install` exited with code 1. Its "ElevenLabs guard" flags example films inside the toolkit's own `youtube/` folder, so it stops before the readiness report runs. This is not a problem with my machine.
- **What I did instead:** ran the readiness checks by hand:
  - Node v22.11.0, Manim 0.20.1 and Remotion node_modules are present.
  - The Kokoro voice smoke test passed (mean volume −21.8 dB).
  - The EB Garamond and Oswald fonts are installed.
  - LaTeX is missing, but it is only needed for equation beats, which this film does not use.
- Found a conflict between the toolkit and the assignment. `show-tell`'s default bookends narrate as "Liam, in for Bear" and end with "@NikBearBrown", but the assignment says to narrate as myself with no instructor name, persona or credit line. Plan: rewrite the greeting and outro under my own name.

## 2026-10-13: Checking the alternative by hand
- To answer "real alternatives I actually looked at," I followed my own public `webapp` README step by step in a fresh clone (`~/Desktop/readme-test`), without fixing anything.
- Result: I could not get a working setup in about 5 minutes.
  - There are two placeholders: `<repository-url>` and `<container-name>`.
  - `db:migrate` failed on a missing `config/config.json`.
  - The DBeaver step needs a GUI app I don't have.
  - `node app.js` hit a database SSL error, because the code expects AWS RDS and the README doesn't say so.
  - `/healthz` returned 503.
- My first `git clone` failed because an old `webapp` folder already existed in my home directory. I cloned into a new folder instead, so the test would not use my old `.env` or installed packages.
- This changed my pitch. I had assumed the problem was other people's READMEs, but my own README has it too.
- Ran a second manual test on an open-source README, so the pitch would not rest only on my own repo: `heroku/node-js-getting-started` ("Running Locally" section), cloned fresh into `~/Desktop/readme-test-2`.
  - **It worked.** `npm start` printed `Listening on 5006`, and `curl localhost:5006` returned `200 OK` at 6:16pm.
  - The README says the Heroku CLI is required. I don't have it (`command not found`), and the app ran anyway.
  - `npm install` warned that the project wants npm 12, while I have 10.9.0.
  - The README's clone URL (`nodejs-getting-started`) doesn't match the repo name. GitHub redirected it.
- What this changed: a working README with small warnings showed me the tool must not call everything "broken." I added **pass / warning / fail** levels, and a false-alarm count on working READMEs, to the brief.
- Checked my evidence before claiming skills. My `webapp` repo proves CI/CD (3 GitHub Actions workflows) and Cloud (Packer, CloudWatch). It does **not** contain Docker work I wrote, so the brief says Docker has "no public proof yet."

## 2026-10-13: Beat sheet and script
- First draft of the narration came to about 5 minutes (811 words), over the 2–4 minute limit. I tightened every beat to 541 words and cut the show-tell "Your Turn" beat, which the assignment doesn't require. The measured audio is **3 min 20 s**.
- Fixed a bug before rendering. The opening animation's word swap ("fix" → "find") would never have fired, because the trigger phrase spanned a line break.
- Removed old local files before building, so this film starts clean:
  - deleted the stash of toolkit edits from my previous assignment
  - moved my old week-01 render files (`youtube/claude-hai-seed-repeatable/`, which git ignores) to the Trash
- Checked the toolkit against GitHub: my `brutalist.art` is identical to `origin/main` (`519fcbb`).

## 2026-10-13: Narrating as myself
- The show-tell outro, `ClaudeTitleOutro`, **hard-codes** `@NikBearBrown` in its source, and the toolkit's outro rule (OUTRO-LOCK.md) says it can't be overridden. The assignment forbids the instructor's credit line, so I didn't use that card. I drew my own outro (B14) with my name. The toolkit's `bookend_check.py` may flag the missing locked outro. That is expected, and this entry explains why.
- On the other bookends I set `folderLabel` to my name instead of the default `@NikBearBrown`. The greeting is mine ("Hi, I'm Lavanya Rajesh"), not "Liam, in for Bear."
- Voice: I chose the toolkit's free local Kokoro voice `af_bella` reading my first-person script, because of time. SOURCES.md says it is synthetic.
- Transcribed the audio with faster-whisper to check pronunciation. My name, "503", "AWS", "GCP" and "npm" all came out correctly.

## 2026-10-13: Drawings
- Rendered low-quality stills of all 15 drawn beats first. Two scenes crashed on dashed "ghost" outlines (Manim's `DashedVMobject` can't take a whole group), so I dashed each face separately. I also removed a stray decorative dot in B01 that meant nothing.
- Pre-checks: Gate A static check and the layout audit were clean on all 15 scenes (0 errors, 0 warnings).
- I accidentally started `art run` by passing `--help`, which it doesn't support. I stopped it, then ran the real render.

## 2026-10-13: Quality gates failed, then fixed
- **First `art run` (4K): Gate V FAILED.** Beat B09 ("five course skills") had 2 MAJOR `low-contrast` defects: ink/background separation 0.29, below the 0.30 floor, from pale cardboard on cream. **Fix:** set the box on a dark plinth, as the show-tell skill advises. I moved the old clip to `_superseded/` and re-rendered B09 only. **Re-run: Gate V clean** (34 frames, 0 BLOCKER, 0 MAJOR).
- The run also printed two "SKIN LINT" advisories, which are expected. BIDEA uses the hesitant writer, which the show-tell skill calls normal. B14 is my own outro instead of the locked `@NikBearBrown` card (see "Narrating as myself").
- **First `art final`: Gate T FAILED** on 1 beat. On the BDEFS terms card, my name label ("Lavanya Rajesh", drawn at the component's fixed 32 px) measured 40 px against the 41 px floor. The default "@NikBearBrown" passes because its letters measure taller. **Fix:** I wrote the label in capitals ("LAVANYA RAJESH") instead of editing the toolkit, re-rendered the card, and re-ran `art final`.
- **Re-run: Gate T still FAILED**, even after capitalizing my name. I measured the frame myself and found the real cause: Gate T measures letter groups, and the card's fixed 48 px definition text contains groups with only small letters, like the "ow" in "how", which always measure 40 px. Rewording couldn't fix that, and I didn't want to edit the toolkit. I also tried delaying the third term past the midpoint, which didn't help. **Fix:** I redrew the terms card myself in Manim (`BDEFS_Terms`) with the same content. **Result: Gate T PASS**, Gate V clean, and the master rendered (3 min 20 s, 3840×2160).

## 2026-10-13: My review of cut 1, and cut 2
I watched the first master and found three problems:
1. **My name was mispronounced**, and I want only my first name. I generated six spellings with the same Kokoro voice and picked "Luh-vun-ya" (sample 4). The narration now says "Hi, I'm Lavanya" and "A pitch by Lavanya", with no last name.
2. **The fix → find animation came too early.** It played over my greeting. I split the opening into its own beat (BHELLO) and made the typing slower, so the correction lands when the voice says "fix" and "find".
3. **The pictures were too abstract.** It was mostly boxes and grey lines, with almost no readable text. Show-tell's default is minimal text, but my pitch needs its evidence on screen. For cut 2 I added:
   - a question header on every beat (which of the seven questions it answers)
   - readable README steps with a result beside each
   - **my real terminal output** from both runs, copied exactly, with long paths shortened to "…" and labelled "real output · Oct 13, 2026"
   - a detailed report mock-up using real README line numbers (27, 34, 40, 48), stamped "CONSTRUCTED MOCK-UP · not built yet"
   - one key sentence per beat

   Each real run now gets two beats, steps and then terminal, because the full-width terminal text doesn't fit beside the steps. The new length is 3 min 30 s.
- Pre-checks on cut 2 found three problems:
  - Two scenes added only text after their first frame, which Gate A rejects as "shapes never change". I added a dot to each.
  - Three labels ran past the safe edge. I shortened or moved them.
  - Three layouts overlapped (CI header, a command overflowing its window, report text overflowing its panel). I fixed them from preview stills before the 4K render.

## 2026-10-14: Cut 2 gates
- Cut 2's first `art run` (2026-10-13, late): **Gate V FAILED** with 2 MAJOR `empty-frame` defects on BIDEA, the typing beat. Gate T passed. The beat wasn't blank; the typing was too slow (150 ms per letter). In its 4.6 s it only reached "How do I find", in small text. `art final` also stopped at `final_frame_check`.
- **Fix, in two tries:**
  - 90 ms per letter at a larger size passed Gate V. Looking at the frames, it still never finished typing "README".
  - One line at 60 ms per letter: it types "How do I fix", corrects it to "find", and finishes "How do I find a broken README" before the beat ends.
- **Result:** Gate V clean (40 frames, 0 BLOCKER, 0 MAJOR), Gate T PASS, `art final` wrote the master. It is 3 min 31 s at 3840×2160, has audio, and decodes with no errors.

## 2026-10-14: My review of cut 2, and cut 3
- When I watched cut 2, it had **too much on screen**: full README commands, seven-line terminal dumps, and report rows with line numbers. Viewers saw what was inside the READMEs instead of the point. Cut 1 had too little. For cut 3 I aimed for the middle:
  - README pages are grey lines again, with ✓ / ⚠ / ✗ marks and only three short results ("placeholder", "missing file", "503")
  - each terminal beat shows **two real lines only**: the error and the 503, then the npm warning and the 200 OK
  - the report mock-up has three short rows, without commands or line numbers, and is still stamped CONSTRUCTED MOCK-UP
  - the CI beat shows two simple panels instead of real YAML lines
  - question headers and key sentences stay
- I removed "a pitch by Lavanya" from the ending, from both the screen and the voice. My name still appears at the start and on the terms card. I re-voiced B14 only and padded the 1 s tail again. The film is now 3 min 29 s.
- Preview stills showed "never run by CI" sitting on the page edge and crowding the key sentence, so I moved it before the 4K render. Pre-checks on the 8 changed scenes: Gate A and layout audit clean.
- **Cut 3 gates:** Gate V clean (40 frames, 0 BLOCKER, 0 MAJOR) and Gate T PASS, both on the first try. The master is 3 min 29 s at 3840×2160, has audio, and decodes with no errors.

## 2026-10-14: Sign-off and assembly
- I watched cut 3 and approved it, together with BUILD-PROMPT.md. I rewrote BUILD-PROMPT.md as a rebuild contract (the steps and rules an agent follows), not a record of my requests to Claude.
- I added my sign-off (`Status:` line) to FACTCHECK.md. `factcheck_check.py` is now clean: 21 rows, every claim-bearing beat covered. `bookend_check.py` still reports the missing `ClaudeTitleOutro`. That is intentional, and its output is saved in `gate-reports/BOOKEND-CHECK.txt`.
- The layout audit file kept only the last scene it checked, so I re-ran the audit on all 19 Manim scenes and saved one combined report: all CLEAN.
- I scanned the submission folder for private data (passwords, keys, emails, local paths) and for the instructor's name or persona. No private data. The instructor references are only sentences explaining why the defaults were removed. None appear in the film.
- I fixed a stale description in `beat_sheet.json` ("box, title, my name" → "box and title").
- Left out of the submission: caches, rendered intermediate clips, audio files, the `_superseded/` archive, and the Kokoro model. The `build/` folder plus Brutalist rebuild everything.

## 2026-10-14: GitHub posting
- Before posting, I noticed the professor's convention for the public class repo: first name plus last initial ("Lavanya R"). I changed my full name to "Lavanya R" in README, PROJECT-BRIEF, the FACTCHECK sign-off, beat_sheet.json and the build files. The film only ever shows "Lavanya", so it didn't need a re-render. The Canvas zip keeps the full-name filename the assignment requires.
- I pulled the course repo first (fast-forward, classmates' folders only), then pushed my folder to `main` as commit `405d2eb`.
- **The film was missing from that commit.** The repo's `.gitignore` ignores `*.mp4`, and `git add` skipped it silently. I caught it because only 16 files were staged instead of 17. Other final-project folders contain force-added films, so I did the same (`git add -f`) and pushed it as commit `66094dc`. I confirmed through the GitHub API that the 17.7 MB `readme-checker-film.mp4` is on the remote.
- My first commit had only a title line, while several classmates' commits have a full description. I decided **not** to rewrite that commit: it was already on the shared `main`, and changing it would mean a force-push that could erase classmates' work. Instead, this commit carries the full description.

## 2026-11-23: Cut 4, re-ordered into four parts
- New guidance for the project film asks for four parts, in order: an executive summary (what and why, with no "how"), an introduction (what others have done), methods, and evaluation, with the detail kept in an appendix. I checked cut 3 against it:
  - What I'm building first appeared at 1:16, not inside the first minute, and the terms card put "how" detail into the opening.
  - "What exists" covered only my two runs by hand and CI. It named no existing tools or research.
  - Methods didn't say where the data comes from, what order I'll build in, or whether I have the resources.
  - Evaluation named the two metrics but not the result that would mean it worked or didn't.
- **What I changed for cut 4** (21 beats, 3 min 51 s):
  - **Part 1** now says what the tool will do at 0:22, and uses my own failed README as the reason it matters. It ends at 0:49. The terms card is gone.
  - **Part 2** adds Runme and Doc Detective, plus two published AI agents that set up projects: ExecutionAgent (33 of 50 projects, ISSTA 2025) and Installamatic (21 of 40 Python projects, SANER 2025). It ends on a comparison table showing why mine is still worth building. I checked each number against the paper's own abstract (SOURCES.md).
  - **Part 3** adds three beats: the data (about ten sample projects I'll make, five broken and five working, with an answer key), a four-step build order, and the resources I have. For resources I ran `docker --version` (29.1.2) and confirmed I already use Claude Code on my university login for my JS1 agent.
  - **Part 4** adds the targets: it worked if it catches at least 4 of 5 planted problems at the right line, with at most 1 false alarm, and every verdict comes from a command that ran.
  - Cut to fit under 4 minutes: the terms card, the Heroku README-marks beat, who opens it, course skills, why this project, and exists vs. will exist. That content is now in the new APPENDIX.md.
- The first draft of the new script was 744 words, estimated at about 4 min 30 s, over the limit. I tightened it to 646 words. The measured audio is 3 min 51 s.
- **Environment problems:**
  - The first audio run stopped with "pip install kokoro-onnx", because the shell's default `python3` is the system Python.
  - The first `art run` then failed with `manim: command not found` (exit 127). Manim 0.20.1, the version cut 3 used, is only in my Anaconda environment. I rendered with that environment first on `PATH`.
- **Gates that stopped the run, and the fixes:**
  - **Gate A:** in the build-order beat, a dot was placed past the right edge of the frame; I removed it. On the doc-tools card, a warning mark sat near the safe edge; I gave it a fixed position.
  - **Gate W** skipped six of the new beats, because it only analyses classes named like `B07_Foo`, and I had named them `BWHAT`, `BGAP` and so on. I renamed all eight new beats to digit-style IDs (B00A, B06A–B06C, B05A–B05C, B08A) and re-voiced. The durations came out identical.
  - **Gate B** (layout, strict) stopped twice. The answer-key text in B05A ran past its panel, so I widened the panel and shortened the lines. A subtitle in B08 crossed the safe area, so I shortened it and moved the score block left.
- **Cut 4 gates:** Gate V clean (42 frames, 0 BLOCKER, 0 MAJOR), Gate T PASS, the strict layout audit CLEAN on all 20 Manim scenes, and `factcheck_check.py` clean (31 rows). `bookend_check.py` still reports the missing `ClaudeTitleOutro`, as intended.
- I looked at the last frame of every new beat myself: no overflow, and every planned item is labelled ("(planned)", "CONSTRUCTED MOCK-UP", "targets set now, before anything is built", "These numbers don't exist yet").
- I watched cut 4 and approved it, together with the new FACTCHECK rows 22–31: the evaluation targets, the sample-set plan and the Claude Code resource line. Cut 3 stays in this repo's history and in my local `_superseded/cut3-final/` archive.
