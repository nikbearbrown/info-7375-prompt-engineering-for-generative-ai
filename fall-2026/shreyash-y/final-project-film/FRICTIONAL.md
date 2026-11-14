# FRICTIONAL.md — Final Project Pitch Film

I worked on this pitch on two days: **2026-10-07** (choosing the project, the brief, the beat
sheet) and **2026-10-14**, the due date (building the film, running the checks, fixing what
failed, assembling the submission). The dates below come from the files themselves: the brief,
the beat sheet, the Dovetail test output, the build logs, and the git commits.

**Who wrote what.** Sections 1 to 8 are mine. The build log at the end was written by Claude
(Claude Code) during the build sessions, on my instructions; "I" in that log means Claude, not
me. I read it and kept it because it records each failure and fix with its date, but I did not
write it. (Added 2026-10-25, after grading: the first version of this file didn't say this.)

## 1. Choosing My Project — 2026-10-07

At first, I thought about continuing with the Reallocation Engine because I had already worked on it. But I decided to choose ClaimCheck instead. I wanted to work on something that I could build and test on my own without depending on someone else to approve my work.

I also wanted to make something related to AI verification because I think it is important to check whether AI-generated answers are actually supported by the documents.

## 2. Planning the Project — 2026-10-07

My first challenge was deciding how much I could realistically build. Initially, I thought about making a complete document-question-answering application, but that would be too much for this project.

I decided to focus on answering questions from insurance documents and checking whether the cited information actually exists in the source.

I also made sure to separate what I had already done from what I was planning to build.

## 3. Planning the Video — 2026-10-07

I wanted the video to be simple enough that someone could understand my project without knowing much about AI.

Instead of putting too much text on the screen, I decided to use diagrams showing how the question moves through the system and how the answer gets verified.

My main goal was to explain what makes ClaimCheck different from a normal document chatbot.

## 4. Problems During Video Production — 2026-10-14

Making the video was harder than I expected. I faced problems with rendering, text placement, and scene layouts. Some text was too small, and some elements were overlapping.

I had to make changes and check the output again. I realized that just because the code runs does not mean the video looks good.

I decided to focus on making the explanation clear rather than adding unnecessary animations.

## 5. Testing and Fixing Errors — 2026-10-14

I ran the quality checks and found issues that needed to be fixed. Some scenes passed the earlier checks but still had visual problems.

Instead of ignoring the errors, I corrected the layouts and reran the tests.

This helped me understand why checking the final output is just as important as writing the code.

## 6. What I Learned — 2026-10-14

This assignment taught me that explaining a project is different from actually building it.

I had to think about who would use ClaimCheck, why they would care about it, and how I could prove that it works.

I also learned that it is better to keep the project small and testable instead of promising too many features.

ClaimCheck is still a proposed project. My next step is to build a small working version using synthetic documents and test whether the citation-checking process works correctly.

## 7. Tools and Limitations — 2026-10-14

I used the Brutalist toolkit to create the film and Kokoro for narration. I also used AI assistance while preparing parts of the project and debugging (exactly what Claude contributed is listed in SOURCES.md).

I did not record the narration using my own voice, and ClaimCheck itself has not been implemented yet. I wanted to be clear about these limitations instead of presenting unfinished work as completed.

## 8. After Grading — 2026-10-25

My TA gave this log 3/5 and said the next step is to build the first piece of ClaimCheck. I
labelled the build log below as Claude's, because it was written in the first person and did
not say who wrote it. Then I built the first piece the film promised in B08: one synthetic
policy, 10 frozen questions, the citation checker, and a dated eval report. That work and its own
dated log are in `claimcheck/` inside this folder.

---

## Build log written by Claude (Claude Code), dated

"I" in this section means Claude. Written during the sessions on 2026-10-07 and 2026-10-14.

### 2026-10-07

**Project choice, then a change.** My first plan was to pitch the Reallocation Engine recipe I
had already built (`healthins-ai-opt`, draft PR #39 on `nikbearbrown/the-reallocation-engine`).
I changed my mind the same day. That recipe's future depends on a maintainer approving and
merging the PR, and I wanted a portfolio piece that stands on its own and matches the roles
I'm applying for. The new project is **ClaimCheck**, an insurance-claims Q&A tool with a
citation checker. The assignment allows this change; I'm logging it here as it asks.

**No `show-tell` skill.** `find brutalist.art -iname "*show-tell*"` returns nothing in my
checkout (commit `6a8380a`). I used `ai-explainer`, the same Claude-skin explainer as my Week 1
reel. I dropped its channel persona rules (the Liam-in-for-Bear line and the `@NikBearBrown`
chip) because the assignment says to narrate as myself and not use the instructor's name or
persona.

**Generic diagram components aren't renderable.** The ai-explainer skill names starter templates
(`SourceFlow`, `ChipGrid`, `LayerStack`, `PredictCard`). `./art scenes --check` reports all four
as NOT RENDERABLE (no `<Composition>` in `Root.tsx`). The other library hits were built for
specific films and have their content hard-coded. So the eight body beats are my own Manim
scenes (`scenes.py`).

**Checking claims before scripting them.**
- Dovetail's test count: `pytest --collect-only -q` → 47. I then ran the full suite:
  `47 passed in 0.62s`. Saved as `evidence/dovetail-pytest-2026-10-07.txt`.
- I confirmed I had actually tried both alternatives named in B05 (a chat assistant with a PDF
  upload; a LlamaIndex/LangChain RAG template). Nothing beyond what I saw is claimed.
- Left out: Dovetail's benchmark figures (not re-run for this pitch), any mention of my
  Cybersenz internship, and a classmate writing blind test questions (not arranged).

**Due date.** The first copy of the assignment I pasted said "Due Monday". The plan assumed
2026-10-12. Canvas shows Wednesday 2026-10-14, 11:59pm.

### 2026-10-14 (due date)

Days 3 to 5 of the five-day plan (build, gates, assemble) all happened today.

**Audio.** Kokoro `am_onyx`, 14 beats, 212.5 s of narration in total. Cost $0.

**Voice.** The narration is the toolkit's local Kokoro voice reading my script, the same
approach as my Week 1 reel. The script is in the first person and names me. Claude drafted
it from my decisions (see `SOURCES.md`). I'm noting this because "narrate as yourself"
could also mean recording my own voice. The beat sheet would work unchanged with recorded
audio.

**Low-resolution preview before the real build.** I rendered the last frame of every Manim
scene and looked at them. I found a footer running off both edges, the endorsement box
covering policy text (B02), the checker title overflowing its box (B03), the B08 column
headers colliding, and a padlock clipped at the left edge (B09). All fixed before the 4K build.

**Gate F stopped the first build.** No `FACTCHECK.md`, `SHOTLIST.md`, or `PROMPTS.md`. The
toolkit wants this paperwork before rendering. I wrote all three with real content. FACTCHECK
lists every claim in the narration and how it was checked.

**Gate A stopped the second build: every scene raised `NameError: BOLD`.** The gate runs
each scene against a stub of Manim that doesn't define the `BOLD` constant. Fixed by passing
`weight="BOLD"` as a string, which real Manim also accepts. Then B02 failed again: the stub
returns plain lists, so `(a + b) / 2` on two points raised a `TypeError`. I rewrote the
midpoint by hand. Two horizontal rules (B05, B08) were 0.2 units outside the safe area;
I shortened them.

**Gate B stopped the third build, and it was right.** The layout audit rejected the
strikethrough on "4(a) Fire and smoke" in B02 because a line crossed text. B08 used the same
strikes on its "out" items. I replaced them with an outline box (B02) and cross marks
beside the text (B08). It also warned that the footers sat below the safe area. I moved them
up and re-checked headings and two long labels. Before the fourth build, I ran the layout
audit on all eight scenes myself: 0 errors, 0 warnings.

**B01 would not render, and the error was mine.** The first failure looked like a timeout
(headless Chrome couldn't connect while several Remotion renders ran at once). It failed
again on its own, and that time the real error showed: a schema error. The `seed` prop of
`BrutalistHesitantWriter` must be a string, and I had given it the number 7375. Changed it to
`"claimcheck-7375"`.

**Gate V (frame-level visual QC on the compiled cut) found 4 MAJOR defects**, all
"underfill": at the 50% sample frame, B03 / B06 / B08 / B09 covered only 48% / 19% / 31% /
50% of the safe area (minimum 55%). The cause was that I'd timed their main content to late
narration words, so the frame was half-empty at its midpoint. I moved each scene's main
content earlier. I kept it at or just after the words it illustrates, not ahead of the voice.
B03's pipeline also moved lower to use the frame's height. Before re-rendering, I ran the
gate's own frame analyzer (`final_frame_check.analyze_frame`) on low-resolution midpoint
frames: 60% / 67% / 73% / 69%. The old renders were moved to `_superseded/`, not deleted.

**The toolkit's outro card shows the instructor's handle.** The contact sheet showed that
`ClaudeTitleOutro` renders "@NikBearBrown" under the title. It's hard-coded (`OUTRO-LOCK.md`),
and there's no prop to change it. The assignment says not to use the instructor's name or
credit line, so I replaced the outro with my own Manim card (`BOUT_Title`): the title, my
name, "INFO 7375 · Final project pitch · Fall 2026", and "ClaimCheck (working title) -
nothing built yet". The toolkit's static gate first rejected the new card because "shapes
never change" (it ignores text when checking whether frames differ). I added an underline
and an outline box that draw in at separate moments.

**Watching the cut found three things the gates passed.** After the build first came back
clean, I pulled frames from every beat and looked at them:
- **B01 never showed its correction.** The summary was still being typed at 95% of the beat,
  so the switch from "a smarter chatbot" to "a citation checker" never appeared. The screen
  ended on the framing the film rejects. I cut the on-screen text to two lines. It still
  didn't correct, because the component matches corrections **one word at a time**, and I
  had given it the phrase "a smarter chatbot". The ai-explainer skill doc says to put the
  whole phrase in `triggerWords`, but the component splits the text on spaces, so a phrase
  can never match. I used two word swaps instead (smarter→citation, chatbot→checker), which
  gives the same corrected sentence. Gate V then flagged B01 for underfill at its midpoint
  (48%, then 51%, because only line one is typed by then). Larger type, wider line spacing,
  and moving the block down got it to pass.
- **B04's contract was too small to read** (13 px code in a large white card). The component
  has a `largeText` option, which I turned on.
- **BVDT said "EXISTS (2026-10-07): … this film"**, but the film was made on 2026-10-14.
  It now reads "project brief (2026-10-07), beat sheet, this film (2026-10-14)". This was an
  honesty-rule slip in my own verdict card, and no gate could have caught it.

**Orphaned Chrome processes.** Four headless-Chrome processes from the first B01 attempt were
still running 50 minutes later, which probably caused the first "could not connect to the
browser" timeout. I killed them by PID.

**The Claude Code session crashed** during the B01/B04/BVDT re-render. Nothing was lost: the
beat-sheet edits were saved, and the build skips beats that are already rendered. I re-ran it.

**Gate T (type lock) blocked the first `art final` with 6 FAILs.** The review cut had passed
every earlier gate, so these only surfaced at the master export:
- **Terracotta read as text (B02, B03, B07, BOUT).** At 4K, my 4–6 px terracotta outlines,
  rules, and arrowheads form blobs the detector treats as accent-coloured text (2.74:1 on
  cream, below 4.5:1). The toolkit handles other reels with a per-reel allowlist inside
  `type_check.py`. I did **not** add one for my reel, because that would mean editing the
  gate to pass my film. My Week 1 reel passed with thin terracotta strokes, so I thinned
  mine to 2–2.4 px with smaller arrowheads. One flag was real: BOUT's terracotta period is
  actual text, so it is now the darker contrast-safe red (`#A44A32`).
- **B04:** the title must be a filename (the component repeats the title as the language
  badge), and the longest code line touched the card edge once `largeText` was on.
  The title is now `PROPOSED_answer_contract.json`, which keeps the "proposed" label on
  screen. The quote placeholder is shortened to `"<verbatim span>"`.
- **B06:** smallest text run 40 px against a 41 px floor. The step box auto-shrank
  "python -m claimcheck eval" to fit. I widened the box and enlarged the table header.

**Gate T, second pass: 4 FAILs left.** Thinner strokes fixed B03 and B06. B02, B07, and BOUT
still tripped the check, so I read the detector: any terracotta blob 1.5–15× wider than it is
tall counts as a word. The box around "4(a)", the endorsement box, the arrows, and the box
around "nothing built yet" all have that shape. I switched those marks to the darker,
contrast-safe terracotta (`#A44A32`) and kept the long flat rules in the bright accent. The
B04 card-clip turned out to be the "INFO 7375" brand label sitting flush with the card edge
below it, so I removed the label (my Week 1 code card didn't have one either).

**Gate F's content half.** The pipeline only checks that FACTCHECK.md exists. The toolkit
also has `factcheck_check.py`, which reads it, and I ran that myself. It failed, because my
table had no Verdict column. I rewrote it as one row per beat with a PASS / CORRECTED / EXEMPT
verdict and a source for each. Two rows are CORRECTED: B05 (narrowed to what I observed) and
BVDT (the date slip above).

**Final result (2026-10-14, ~03:10 EDT).** All gates pass: F, F-content, L, A, W, B, V
(0 blocker / 0 major), T, CONTENT, FRAME. The master decodes end to end with no errors.
The numbers for the final cut, after the Q1/Q2 fix below, are in `qc/EXTRA-CHECKS.txt`. I never set `ART_STRICT=0` and never edited the toolkit.
The reports are in `qc/`.

**Checking against the assignment, line by line (03:20).** Before pushing I went down
the brief again and found three gaps. The brief's "Exists today" list named a plan file I
hadn't submitted and left out the beat sheet and the film; fixed. And two of the seven
answers were only in the brief, not in the film: Q1 asks for the artifact's *form*, but the
narration said only "a Python tool on Claude"; Q2 asks for "it saves [a person] [a thing]",
but the narration never put it that way. I rewrote one line each. B03 now says "a public
GitHub repository holding a Python command-line tool on Claude, with its test set and eval
report", with a caption on screen. B05 now ends "ClaimCheck will save a claims examiner from
acting on a cited clause that nobody checked, which neither of those does". I regenerated the
audio (only B03 and B05 changed length), re-timed both scenes, checked their midpoint fill
with the gate's own analyzer before the 4K pass (B03 sat at exactly 55% at first, so I moved
the checker box in a little earlier), and rebuilt.

**Not done / still open:**
- The narration is the toolkit's TTS voice, not a recording of me (see the "Voice" entry above).
- ClaimCheck itself: nothing is built. The first piece (1 policy, 10 questions, the checker,
  a dated `eval_report.md`) is the next step after this pitch.
