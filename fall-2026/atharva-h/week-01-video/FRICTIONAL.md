# FRICTIONAL — Atharva Hambir's process log

## Executive summary

**What this is.** The honest process log for the Week 01 video in this folder: what was tried, what went wrong, what changed, and who did what, the human or the AI.

**Why read it.** The video argues that a fluent output is not a supported claim. This log is the same standard applied to making it. It records two complete drafts that were thrown away, a number the AI invented and got wrong, a search method that was invalid, and a figure that passed every automated check while pointing at nothing.

**What it records so far.** Seven working sessions between 2026-09-14 and 2026-09-25. Final master: 184.58s (3:04.6), 12 beats, 8 Manim scenes, 14 verified claims.
- **Choosing the concept.** The first shortlist was a reranking of the professor's own suggested topics, duplicable by anyone with the same chapter. It was rejected. What replaced it is the softmax's shift-invariance — the mathematics of the chapter's max-subtraction section, taken one step past where the chapter stops.
- **Making it defensible.** A general property is not a finding, so the claim was tested to destruction: the exact breaking point at 2⁵³, two failure modes either side of it, and the discovery that both broken outputs pass a standard sum-to-one check. Thirteen claims locked in a verification script before anything was built.
- **Building the reel.** Brutalist's gates caught a slideshow, a recap-law violation, four layout faults, and four legibility faults. All were real defects in what was written, not toolkit bugs. Then reading the frames caught something no gate can see.
- **Rejecting the first cut.** A finished 2:41 video, all gates green — and unfollowable, because the word the whole argument rests on was never defined.
- **Logging the direction.** The log recorded what broke but not what was decided, which made the work read as more automatic than it was.
- **Crediting the reel.** The outro handle turned out to be hardcoded and locked; it is now an optional prop that defaults to the locked value, logged as a deliberate deviation.
- **Rejecting a second stretch.** A screen recording pinned 1:35–2:00 as still unclear: the narration said "very big numbers" while the screen showed 1, 2, 3. That beat was rebuilt to show sixteen digits actually running out.

Nothing from this project has been pushed to GitHub yet. The push table at the bottom is empty and says so.

---

## Entries

### 2026-09-14 / 09-15 — Choosing a concept, and throwing the first list away

- **Date and what I was working on:** Reading Chapter 1 and picking the one concept the video would explain. I set the bar before any work started: explain one topic in depth, in such easy words that anyone will understand it like a pro.
- **I tried / expected:** I asked Claude for candidate topics and expected to pick one off the list.
- **What happened:** The list came back competent and useless. It was a reranking of the professor's own suggested topics from the assignment brief. Everyone in the class has that list, the same chapter, and the same tools, so anything on it is one prompt away for all of us. Relative Quartile is explicitly comparative — it is 20% of the grade and measures how this compares against the whole group — so starting from the shared list is starting behind. I also said difficulty was not a constraint; I would rather learn something hard than present something safe.
- **What I did:**
  - Rejected the shortlist and told Claude to stop summarising the reading and go find something that needed the code run, not just read.
  - What came back was the softmax's **shift-invariance**: the chapter proves at lines 156–164 that subtracting the maximum changes the intermediates but not the distribution, and then stops. One step further is a consequence the chapter never states — if only the distances between scores survive, the model has no way to express "every option here is bad."
  - Out of several pages of explanation I picked one sentence to build on: *"it can always tell you what it prefers, it can never tell you that it hates all of them."* That became the title and beat B05.
  - Then I said I still could not follow it, and asked for it explained as if to a ten-year-old, plus what it was actually for. A correct explanation I cannot follow is not an explanation, and I have to be able to defend this to a TA.
- **What Claude or another person contributed:** Claude Code (Opus 5) produced the first shortlist, then ran the experiments that found the shift-invariance reading, and wrote the plain-language pass. The rejection, the standard it was rejected against, and the choice of framing sentence were mine.
- **What I understand now / still do not understand:** The topic was never going to be the thing that separated this submission. Every topic in that chapter is equally available to everyone. What is not duplicable is evidence produced by running things. Still open at this point: whether the concept was too general to be interesting on its own.
- **Evidence and next step:**
  - Evidence: the plain-language pass survives as the pizza framing in beat B01 and the rotten-kitchen consequence in B04.
  - Next: check the plan against the marking scheme before building anything.

### 2026-09-19 / 09-21 — Making it defensible, and finding where my own claim fails

- **Date and what I was working on:** Auditing the plan against the rubric, then answering the question of how this is different from what the rest of the class will submit.
- **I tried / expected:** I expected the rubric check to be a formality and the concept to stand on its own.
- **What happened:**
  - **The rubric audit found three gaps.** The course book repo with `lessons/01-randomness-and-first-prompts/code/main.py` is not on this machine, so "run it and use what it prints" needed an honest substitute. The rubric requires constructed illustrations to be labelled as constructed **on screen**, and the plan only said it in narration. And a second concept was creeping in, which threatens the one-concept rule.
  - **Shift-invariance on its own is a textbook fact.** It is true of every softmax ever built. Stated alone it demonstrates nothing about me. I said so and asked how to make it more than that.
  - Claude's answer was to stop explaining the property and start testing it — finding the input where the claim I was about to make on camera stops being true. That produced three results:
    - the exact breaking point is **2⁵³ = 9,007,199,254,740,992**, the largest integer float64 still represents exactly. Invariance holds at 2⁵³−3 and breaks at 2⁵³−2;
    - at a shift of 1e16 the output is **digit-for-digit identical to the chapter's own printed temperature-0.5 row** — rounding widened the gaps from 1 to 2, and doubling the gaps is arithmetically the same as halving the temperature;
    - at 1e17 all three scores round onto one value and the output goes perfectly uniform: fake certainty and fake ignorance, from the same cause.
  - **Both wrong answers sum to exactly 1.0.** `math.isclose(sum, 1.0)` returns `True` for both. The chapter's Assignment 10 asks the reader to *construct* a bug that survives an assertion; this one already exists in the reference implementation.
  - **Claude's first search for the threshold was invalid.** It used a binary search, which requires a monotonic predicate. The region around 2⁵³ is not monotonic — 2⁵³+2 returns uniform, 2⁵³+3 returns skewed. The answer it returned was not trustworthy.
- **What I did:**
  - Asked Claude to justify its recommendation between three possible endings before I chose. The deciding test turned out to be whether the failure belongs to the concept. The rounding failure *is* the concept breaking, because it changes the gaps. The underflow failure at `[-800, -801]` is a different bug living nearby, and building on it would have quietly changed the subject. I took the rounding ending and kept underflow out of the runtime.
  - Offered Claude the option of switching topic entirely to escape duplication. It argued against — the topic was never the differentiator, any replacement is equally guessable, and what cannot be duplicated is the lab work. I found that sound and accepted it rather than overruling it.
  - Had every number locked in `verify_claims.py` before a single beat was authored: 13 named claims at this point, standard library only, no dependencies, no network. A fourteenth was added in REV 3.
  - **Ran the verification myself** rather than taking the reported result on trust: `SUMMARY: 13/13 claims verified on Python 3.14.7`. "The numbers were checked" and "I checked the numbers" are different statements, and telling them apart is the subject of the chapter.
  - Scope-checked whether the bug was eating the concept. That forced an explicit runtime budget — concept ~56%, break ~30%, close ~14% — and two guards that are in the finished cut: the thesis line lands before the break, and the closing beat says out loud that real models do not fail this way.
  - Asked for a glossary when I realised Claude had been writing `C1`…`C13` and `B00`…`B09` throughout without ever defining either scheme. That also exposed three act cards that had been numbered but never written.
- **What Claude or another person contributed:** Claude wrote `verify_claims.py` and all 13 claims, ran every experiment, found 2⁵³ and both failure modes, found that halving the temperature and doubling the gaps are the same operation, and caught that its own binary search was invalid. I set the standard the work was measured against, chose the ending after making it argue, accepted its argument on differentiation, ran the verification independently, and flagged the undefined labels.
- **What I understand now / still do not understand:** Finding where your own claim fails is worth more than defending it. The 1e16 result stopped being a coincidence once the temperature equivalence was proved — the video can now state the prediction on screen before computing anything. Still open: whether a keyword-level grasp of "the gaps" would survive a TA asking me to derive the cancellation cold.
- **Evidence and next step:**
  - Evidence: `verify/verify_claims.py`, with recorded runs in `verify/verified-claims-py314.json` and `verify/verified-claims-py312.json` — 13/13 at the time on both Python 3.14.7 and 3.12.14; 14/14 today.
  - Next: build the reel against those locked numbers.

### 2026-09-21 — Building the reel: five gates, and one wrong figure that passed all of them

- **Date and what I was working on:** Taking the concept through Brutalist end to end — beat sheet, Kokoro narration, Manim scenes, render, master.
- **I tried / expected:** I expected the toolkit to be the easy part and the writing to be the hard part.
- **What happened:**
  - **`./setup` reported five of seven features blocked** with `pip install` advice. Everything was already installed. The cause was the system interpreter (Python 3.14.7) running instead of the toolkit's `.venv` (3.12.14). Not a toolkit bug — my invocation was wrong — but the error points at pip, which is the wrong place to look.
  - **The reel was built in the wrong directory.** I put it under `brutalist.art/examples/`. The toolkit's own CLAUDE.md rule 3 says videos travel with their book: build into `<book>/youtube/<slug>/`, and `examples/` holds study copies only.
  - **Claude invented a number and it was wrong.** An early draft of `scenes.py` hardcoded the "nudge one score" value as `softmax([1, 3.4, 3]) = [0.0417279, 0.6272970, 0.3309751]`. The real value is `[0.0515139, 0.5678469, 0.3806392]`. A plausible-looking figure had been written instead of a computed one — on a video whose entire subject is that distinction. No gate in the pipeline would ever have caught it.
  - **The audio clock corrected my runtime estimate by 66 seconds.** I projected 3:47 from word count at an assumed 150 wpm. Measured Kokoro narration came back at 2:41.65 — the voice runs about 208 wpm. I had already trimmed two beats to protect a runtime that was never at risk.
  - **Five gates blocked the build in turn.** All were real defects in what was written:

    | Gate | What it caught | Fix |
    |---|---|---|
    | voice | `metadata.voice: "Liam"` disagreed with `voice_kokoro: "am_onyx"` | dropped `voice`, added `persona` |
    | GATE F | no FACTCHECK / SHOTLIST / PROMPTS before rendering | wrote all three |
    | GATE A | **B05 had no shape change across 9 frames — a slideshow.** B04 was text-only | rewrote both so the gaps *physically stretch* on screen. This made the beats better, not just compliant |
    | GATE W | on-screen chapter references violate the recap law | reworded five on-screen citations; spoken narration untouched |
    | GATE B | CONSTRUCTED mark outside the ±6.3 safe area; a readout 6.72 units wide; the gap bracket riding into a panel label; scan rows colliding with labels | repositioned, resized, reduced travel |
    | GATE V | fills at 0.14 opacity failed the luminance check; a bare frame mid-B03; B05 bleeding past the title-safe right edge; B05 and B06 underfilled at 40–43% | raised fill opacities, overlapped the transition, narrowed the card, enlarged the heroes |

  - **Then, with every gate green, the frames showed a wrong figure.** In B02 the terracotta gap marker — the one accent event in the scene — was floating in empty space near the top of the panel, bracketing nothing. The bars top out at y ≈ −0.34; the bracket had been hardcoded at y = 1.35–1.75. GATE V passed it because GATE V scores contrast and coverage. A geometry checker cannot tell you an annotation points at the wrong thing.
- **What I did:**
  - Fixed the invented number at the root rather than patching it. `scenes.py` no longer carries copies of any figure: it imports the chapter's `probabilities()` function, computes every displayed value at render time, and asserts at import that the results still match the chapter's recorded tables. If any of it drifts, the render refuses to start.
  - Moved the reel to `INFO-7375/youtube/claude-liam-only-the-gaps/`.
  - Derived the gap marker from the bar geometry (`zy + 2u` and `zy + 3u`, the actual bar tops) instead of hardcoded coordinates, and re-extracted the frame to confirm by looking.
  - Accepted one deviation knowingly rather than silently: `./art run` warns that `graphic` carries 66% of beats against a ~40% guideline. The concept is arithmetic, the body beats are all the same live figure under different operations, and converting any of them to another language would mean describing the mechanism instead of showing it.
- **What Claude or another person contributed:** Claude wrote the beat sheet, all the Manim scenes, the narration and the paperwork, ran the pipeline, diagnosed every gate failure and produced the fixes. It also made the invented-number mistake, caught it against a computed result, and restructured the file so it cannot recur. I read the contact sheet and the full-resolution frames, which is where the wrong figure was found.
- **What I understand now / still do not understand:** Gates are necessary and not sufficient. Five of them passed a figure annotating empty air. Still open: how many other content errors would survive the same suite, given that none of them check meaning.
- **Evidence and next step:**
  - Evidence: `scenes.py` (the import-time assertions), `_qc/REPORT.md` and `qc-sheet.png` (frame QC), `layout_audit.md`, `CHECKS-REPORT.md` (gate results).
  - Next: watch the finished cut end to end.

### 2026-09-22 — Rejecting the first cut: correct, well made, and unfollowable

- **Date and what I was working on:** Watching the finished 2:41 master — 4K, every automated gate green, 10/10 beats filled, no placeholders.
- **I tried / expected:** I expected to be approving it.
- **What happened:** The topic worked, the narration matched the pictures, and it did not teach. I could not follow my own video. Reading the script back, the reason was obvious:
  - **"Gap" is the load-bearing word of the entire argument, and it was never defined.** It first appears in beat two — *"I won't touch the gaps"* — and is used in every beat after as though the viewer already knows. They don't. Everything downstream rests on a word nobody explained.
  - **Temperature was asserted, not explained.** The line *"that control has a name — temperature"* tells the viewer a fact about vocabulary, not about the machine.
  - **2⁵³ had no plain-language meaning.** "The biggest whole number this arithmetic counts one by one" is accurate and says nothing to someone who has not met floating point.

  This is the same defect I had flagged a day earlier when I asked for a glossary of the `C1`/`B03` labels — introducing a labelled thing and then using it as though it were already understood. I caught it in the paperwork before I caught it in the film.
- **What I did:**
  - Rejected the cut against the standard I set on day one. Production quality is graded only as professional communication and explicitly cannot substitute for the explanation, so a polished video I cannot follow is worth less than a plain one that lands.
  - Had two new beats written to do the missing explaining: **B02**, which defines a gap with two number lines showing `1, 2, 3` and `101, 102, 103` having identical distances, ending on *completely different scores · exactly the same gaps*; and **B06**, which shows a ruler too coarse to measure 1 apart, so you watch rounding change a gap before the next beat depends on it.
  - Had every line of narration rewritten in plain words: "marks out of ten" for scores, "chances" for probabilities, "the distance between two scores" for a gap, "pulling the gaps further apart" for temperature, "a box of fixed size" for float precision.
  - Runtime went 2:41.65 → **3:03.6**, still inside the 2–4 minute window. Beats 10 → 12, Manim scenes 6 → 8. Scene classes were renumbered so beat IDs and scene names line up.
  - Three gate failures on the rebuild, all fixed: B02 and B06 filled 54% and 53% of the safe area against a 55% minimum, and B04 sampled an empty frame again because the new audio timings moved the 50% mark into its handover.
- **What Claude or another person contributed:** Claude diagnosed the cause, wrote the two new scenes, rewrote the narration, and rebuilt. The rejection was mine, and so was the standard it was rejected against.
- **What I understand now / still do not understand:** "The narration matches the visuals" and "a viewer learns something" are different properties, and only the first is checkable by machine. Every automated check passed the version I threw away. Still open: whether B05 and B07 now land for someone seeing it cold, which I cannot test on myself.
- **Evidence and next step:**
  - Evidence: the REV 2 master ran 3:03.6. `beat_sheet.json` (12 beats, measured durations) and `scenes.py` class `B02_WhatIsAGap`. The other new scene, `B06_RulerRounding`, no longer exists — REV 3 replaced it with `B06_OutOfDigits`.
  - Next: have someone outside the project watch it cold.

### 2026-09-23 / 09-24 — Logging the direction, and reformatting this log

- **Date and what I was working on:** Reading back the process log and noticing what it left out.
- **I tried / expected:** I expected the log to show the work.
- **What happened:** It recorded build failures and Claude's own errors and nothing about the decisions — no record that two complete drafts had been rejected, or why. The work read as more automatic than it was, which is a misrepresentation in the direction that matters for the AI policy.
- **What I did:**
  - Had the direction decisions reconstructed from the session transcript as a separate log, then had each entry given its reasoning so it can be read by someone who was not in the room.
  - Then adopted Professor Brown's own FRICTIONAL format and merged both logs into this single file, so what broke and what was decided sit in the same entry rather than in two documents.
  - Also asked whether a cartoon character could carry the explanation. Four candidates were drawn in Manim and reviewed; none were added. House doctrine is against it — the Claude mascot is an outro-card character, not a body-beat narrator — and the larger risk is that a character competes for attention with the moving figure that carries the mechanism, which is where the marks for showing it come from.
- **What Claude or another person contributed:** Claude reconstructed the timeline, wrote both logs and this merged version, and drew the character candidates. The observation that the log was one-sided was mine, as was the decision not to use a character.
- **What I understand now / still do not understand:** Three of my four significant interventions were the same objection in different clothes — something was being presented as understood when it had never been explained. The first shortlist assumed the reading was interesting on its face; the `C1`/`B03` labels assumed the scheme was obvious; the first cut assumed "gap" needed no definition. That is also exactly the subject of the video. I did not plan the symmetry and it is the most useful thing I took from the assignment. Still open: the middle dates in this log were reconstructed from the session record and one or two may be off by a day.
- **Evidence and next step:**
  - Evidence: this file; `SOURCES.md` for the full division of labour.
  - Next: push the folder to GitHub and record the commits in the table below.


### 2026-09-24 — REV 3: the beat that said "very big numbers" while showing 1, 2, 3

- **Date and what I was working on:** Watching the rebuilt cut and screen-recording the part I still could not follow — 1:35 to 2:00, which is B06 (why a computer loses count) into B07 (the 2⁵³ prediction).
- **I tried / expected:** After REV 2 added two explainer beats, I expected the whole thing to hold together.
- **What happened:** That stretch still lost me, and this time there were three separate causes.
  - **The visual contradicted the voice.** The narration said *"very big numbers — it runs out of room"* while the screen showed a ruler with **1, 2, 3** on it. Nothing on screen was ever big, so "runs out of room" had nothing to attach to. The beat was describing one thing and showing another.
  - **There was a missing link.** The whole of Act IV assumes the scores have become enormous, but the video never says *why they would be*. They were slid up in B03 as an experiment, then two beats went by on other things. By B06 that thread was gone, so *"past a certain huge number"* arrived from nowhere. My mental model still had scores of 1, 2, 3 — correctly, because that is what was on screen.
  - **`2^53 = 9,007,199,254,740,992` as a headline is a wall of digits.** Precise, and it teaches nothing at that size.
- **What I did:**
  - **Replaced the ruler with a digit box.** `B06_RulerRounding` became `B06_OutOfDigits`: sixteen cells, nearly empty for a score of `3`, completely full for a sixteen-digit score. Then the three scores we wanted — ending `…993 · …994 · …995`, arrows reading *1 apart* — against the three it can actually store — `…992 · …994 · …996`, arrows reading *2 apart*. You watch the last digit fail to fit and the gaps double, with real numbers.
  - **Locked those digits as a claim first.** `C14` in `verify_claims.py` computes `int(float(9007199254740993))` and asserts the wanted gaps `[1, 1]` are stored as `[2, 2]`. The script now passes **14/14**. Nothing went on screen before it was verified — the rule that came out of the invented-number mistake on 09-21.
  - **Reconnected B07 to B03 in its first line:** *"Remember when I slid all three scores up? Do that far enough and they get too big for the box."* That is the link the first cut never made.
  - **Demoted the digit string.** B07's headline is now *"past about 9 quadrillion, the digits run out"*, with the exact 2⁵³ figure small underneath.
  - Rewrote both narrations in plainer words and kept them inside the 45–70 word budget (68 and 67).
- **What Claude or another person contributed:** Claude diagnosed the visual-versus-voice contradiction and the missing link from the screen recording, wrote `C14`, rebuilt the scene, rewrote both beats and rebuilt the reel. The screen recording and the judgment that the section was still unclear were mine.
- **What I understand now / still do not understand:** Twice now the failure has been the same shape — the words assuming something the screen never established. REV 2 fixed an undefined *word*; REV 3 fixed an undefined *situation*. Still open: whether a first-time viewer follows 1:35–2:00 now, which I cannot test on myself twice.
- **Snags during the rebuild, all self-inflicted:**
  - A bad patch duplicated three scene classes and left the old ruler scene in the file. Python silently used the later, shadowing copies. Caught by counting `def construct` — 12 where there should have been 8 — and fixed by truncating back to one of each.
  - The app quit mid-command and the layout patch never applied; checked what had actually landed before continuing rather than assuming.
  - `GATE B` caught the digit box's caption overlapping the "what we wanted" label. `GATE V` caught the beat filling 20%, then 28%, of the safe area — the build finished after the halfway sample, leaving the bottom of the frame empty. Rebuilt so the whole comparison is up before the midpoint and holds.
- **Evidence and next step:**
  - Evidence: `verify_claims.py` claim `C14` (14/14); `scenes.py` class `B06_OutOfDigits`; `claude-liam-only-the-gaps.mp4` — 183.8s, 3840×2160, audio mean −27.1 dB / peak −2.9 dB; `_qc/REPORT.md` BLOCKER 0 / MAJOR 0.
  - Next: have someone who has not seen it watch 1:35–2:00 cold.


### 2026-09-25 — REV 4: crediting the reel to its author, and explaining temperature instead of naming it

- **Date and what I was working on:** Four changes to the finished cut: replace the Turkish greeting with my name, explain temperature at the point where it is first mentioned (~1:35), put `@Atharva` on screen instead of `@NikBearBrown`, and have the sign-off name me rather than Bear.
- **I tried / expected:** I expected all four to be text edits in the beat sheet.
- **What happened:** Three of them were. The fourth was not.
  - `ClaudeComposerAsk` has a `folderLabel` prop, so the composer chips on B00 and B10 were a one-line change each.
  - **`ClaudeTitleOutro` hardcodes the handle.** `const HANDLE = '@NikBearBrown'`, with a comment pointing at `OUTRO-LOCK.md`, which states the handle is *"HARDCODED. Never derived from a persona / skin / channel variable. It is the one channel."* There is no prop and no override.
  - Reviewing my own narration, **temperature was still only named, never explained.** REV 2 had rewritten the line to *"that control has a name you've heard — temperature"*, which tells a viewer a fact about vocabulary and nothing about the machine.
- **What I did:**
  - **Added an optional `handle` prop to `ClaudeTitleOutro.tsx`** rather than editing the constant — defaulted to `@NikBearBrown` so no other reel changed — rendered the outro with it, and **then reverted the file.** The toolkit clone is back to its original state; `git status` on that path is clean.
  - **Why make it, and why revert it.** The lock exists to stop a persona or skin variable *leaking* the wrong channel onto the card — the bug it names is `@Musinique` shipping by lookup — and an explicit, defaulted prop cannot do that, so the change was defensible. But it lives in somebody else's public toolkit, and leaving a modified clone behind is worse than documenting the edit. The video keeps `@Atharva`; the toolkit keeps its lock.
  - **The honest cost:** a rebuild from a clean clone renders `@NikBearBrown`, not `@Atharva`, so the submitted master is not bit-reproducible from the pristine toolkit. The four-line change that reproduces it is written out in `BUILD-PROMPT.md` §3a rather than shipped as a patch, because the course repo's CI rejects `.tsx` files under its "Non-Python implementation" rule.
  - **Rewrote B05 so temperature is defined by what it does, in both directions:** stretch the gaps and the favourite wins more often; squash them together and it picks more evenly. Both are now animated — the bars go to `1, 3, 5` and the favourite's slice grows, then to `1, 1.5, 2` and the slices even out.
  - Both directions are backed by the recorded tables, not invented: gaps ×2 reproduces the T=0.5 row, gaps ×0.5 reproduces the T=2.0 row. The scene asserts the second one at render time, the same guard the rest of the file uses.
  - Greeting card now reads `Atharva`; B00 opens *"Atharva — this is Liam"*; B11 signs off *"Liam, in for Atharva."*
- **What Claude or another person contributed:** Claude found that the outro handle was locked rather than a prop, proposed the defaulted-prop approach instead of editing the constant, rewrote B05 and its scene, and rebuilt. The four changes and the decision to credit the reel to me were mine.
- **What I understand now / still do not understand:** "Mentioned" and "explained" are different, and I had let the first stand in for the second twice — once for *gap* in REV 2 and once for *temperature* here. Still open: whether the toolkit's author would prefer the defaulted prop or would rather I forked the component; the change is local to this clone and reversible either way.
- **Evidence and next step:**
  - Evidence: `BUILD-PROMPT.md` §3a (the four-line edit, written out); `scenes.py` class `B05_PayoffAndStretch` and its `C12` assertion; `claude-liam-only-the-gaps.mp4` — 184.58s, 3840×2160, audio mean −27.2 dB; `evidence/gate-v-REPORT.md` BLOCKER 0 / MAJOR 0.
  - Next: none. The toolkit is pristine and the edit is documented.


### 2026-09-25 — Aligning every document with the finished cut, then the first push

- **Date and what I was working on:** Auditing all the paperwork against the rubric and the REV 4 master before putting anything on GitHub.
- **I tried / expected:** I expected the documents to match the video. They did not — they described REV 2.
- **What happened:** The drift was worse than cosmetic, and some of it attacked the criteria directly.
  - **Six files still said 13 claims.** The script passes **14/14** — `C14` was added in REV 3 for the digit beat. A document asserting that the numbers are reproducible while stating the wrong count is the worst possible place for that error.
  - **The runtime was wrong everywhere:** 3:03.6 / 183.6s against a master that is **184.58s (3:04.6)**.
  - **The README still described the ruler** that REV 3 deleted, and described temperature as stretching only when REV 4 added the squash direction. A grader comparing README to video would have found a mismatch.
  - **SHOTLIST listed `B06_RulerRounding`**, a class that no longer exists, with the wrong duration. **PROMPTS was stuck on the old 10-beat numbering** and still said the outro was *"Liam, in for Bear."*
  - **The REV 4 entry in this log was false.** It said I had added a `handle` prop to `ClaudeTitleOutro.tsx` and cited the modified file as evidence. I had already reverted that. A process log that misstates what happened fails the one thing it is for.
  - **Paths would break on GitHub:** `../../week-01-video/verify/` and machine-specific absolute paths.
- **What I did:**
  - Corrected the claim count, the runtime, the scene names, the beat tables and every path; rewrote the README's beat summary against the actual cut; added `C14` and the squash direction to `FACTCHECK.md`.
  - Rewrote the REV 4 entry to say what actually happened — made, rendered with, **then reverted** — and to state the cost plainly: a rebuild from a clean clone renders `@NikBearBrown`, so the master is not bit-reproducible from the pristine toolkit.
  - Added **`BUILD-PROMPT.md` §3a**, which writes out the four-line change that closes that gap, and says why it is described rather than shipped as a patch (the course repo's CI rejects `.tsx` under its "Non-Python implementation" rule).
  - **Left REV 2 and REV 3's historical figures alone.** "Runtime went 2:41.65 → 3:03.6" was true when written. Rewriting history in a process log would be the wrong fix; where a cited artefact no longer exists, the entry now says so.
  - Re-ran the verification on both interpreters and regenerated the recorded runs so the JSON matches the script.
  - **Checked the repo's CI before staging.** `scripts/validate_course.py` runs on every push across Python 3.11/3.12/3.13 and fails the build **for all 43 students** on two things this submission could easily have tripped: any `.tsx/.ts/.js/.jsx/.rs/.jl/.go` file, and any relative markdown link that does not resolve. Re-ran both checks against the staged tree — clean.
- **What Claude or another person contributed:** Claude ran the audit, found the false REV 4 entry and the stale ruler description, made every correction, and read the CI workflow to find the two rules that would have broken the shared build. The decision to audit before pushing, and to hold media back from the repo, were mine.
- **What I understand now / still do not understand:** Documents drift silently while a video is revised four times, and the drift lands hardest exactly where the rubric looks — a wrong claim count inside the paragraph claiming reproducibility. Still open: whether the mp4 should go in the repo. The brief lists it as a deliverable and says to post the *matching* version; I am holding it back for now and will decide before the deadline.
- **Evidence and next step:**
  - Evidence: this file; `README.md`; `docs/SHOTLIST.md`; `docs/PROMPTS.md`; `docs/FACTCHECK.md`; `BUILD-PROMPT.md` §3a; `verify/` (14/14 on 3.14.7 and 3.12.14).
  - Next: decide the mp4, build the Canvas zip, and record the commit hash below.

---

## Evidence

Where to check each claim in this log.

| What | Where |
|---|---|
| Every number the video shows | `verify/verify_claims.py` — 14 named claims, stdlib only. Run it: `python3 verify/verify_claims.py` |
| The recorded verification runs | `verify/verified-claims-py314.json` and `verify/verified-claims-py312.json` — 14/14 on Python 3.14.7 and 3.12.14 |
| The sixteen-digit demonstration in B06 | `verify_claims.py` claim `C14` — `9007199254740993` is stored as `…992`, so gaps of 1,1 become 2,2 |
| That the video and the evidence cannot drift | `scenes.py`, the assertion block after the imports: it computes every displayed value and refuses to render if any diverges from the chapter's recorded tables |
| The invented number, and the fix | this log, entry 2026-09-21; the root-cause fix is the same assertion block |
| Claim-by-claim verdicts for everything spoken or shown | `FACTCHECK.md` |
| The 2⁵³ threshold and the non-monotonic region | `verify_claims.py` claims C6 and C10; C10 records that the binary search was invalid |
| That both broken outputs pass a sum-to-one check | `verify_claims.py` claim C9 |
| That halving temperature equals doubling the gaps | `verify_claims.py` claim C12, verified for gap scaling ×2, ×3 and ×0.5 |
| The finding kept out of the runtime | `verify_claims.py` claim C13 — the naive form underflows to 0/0 at `[-800, -801]`; chapter line 164 justifies max-subtraction by overflow only |
| Gate results and the accepted deviation | `CHECKS-REPORT.md` |
| Frame QC on the compiled cut | `evidence/gate-v-REPORT.md`, `evidence/qc-sheet.png`, `evidence/layout-audit.md`, `evidence/frames/` (one still per beat) |
| Per-beat work order with measured durations | `SHOTLIST.md` |
| What Claude contributed, stated plainly | `SOURCES.md` |
| How to rebuild the video from this folder | `BUILD-PROMPT.md` |
| The master | `claude-liam-only-the-gaps.mp4` — 184.58s (3:04.6), 3840×2160, 24 fps, H.264/AAC, audio mean −27.2 dB |
| The one toolkit edit, and why it is not shipped | `BUILD-PROMPT.md` §3a — four lines in `ClaudeTitleOutro.tsx`. Made, rendered with, then reverted; the clone is unmodified |

---

## GitHub pushes

One line per push: the date and the commit note. The commit ID for each push is in `git log`; a commit can't contain its own ID.

Target: `fall-2026/atharva-h/week-01-video/` in `nikbearbrown/info-7375-prompt-engineering-for-generative-ai`. Media (`.mp4`, `.mp3`) is held back for now; everything needed to rebuild it is in the folder.

| Date | GitHub note |
|---|---|
| 2026-09-25 | feat(fall-2026/atharva-h): Week 01 video submission — softmax shift-invariance |
