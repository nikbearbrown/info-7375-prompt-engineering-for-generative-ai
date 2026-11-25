# Final Project Film — design

Drafted by Claude Code on 2026-11-21 from the conversation and the records named below. This is a working document, not
a deliverable. The student's words are quoted. Everything else is either a fact with its source or Claude's proposal,
marked as such.

## 1. What this is and why

A film of **at most five minutes** for INFO 7375's **Final Project Film** assignment. Canvas lists it at 25 points, due
**Monday 2026-11-23 by 11:30 pm**, and accepts a text entry, a website URL, a media recording, or a file upload. The
instructor's brief, pasted by the student on 2026-11-21, asks for four parts in this order:

1. **Executive summary.** What the project is and why anyone would care, in plain words, with no "how". Someone who
   watches only the first minute should know both.
2. **Introduction.** What already exists, who has tried something like it, and what they got. Then why yours matters,
   said again.
3. **Methods.** The plan: how it gets built, where the data comes from, what happens step by step, and whether the
   resources are in hand (token credits, accounts, access, compute). Detail belongs here and in "your appendix", never in
   the summary.
4. **Evaluation.** What will be measured or checked, and what result would say it worked, or that it didn't.

The brief's standard: "It needs to be crystal clear." The student's goal, in their words: "to make it impactful in
class. To score the best marks." The brief is saved verbatim in [ASSIGNMENT-BRIEF.md](ASSIGNMENT-BRIEF.md).

## 2. Decisions so far

| Decision | Choice | Who decided | When |
|---|---|---|---|
| The project the film describes | **Fine Print, built on jobwatch.** jobwatch (JS1–JS2) is the half that watches job boards, and it already runs. Fine Print's posting reader is built next, through JS3–JS5, toward the Final Project on Dec 20. | Claude recommended it when the student asked which option "will work best … to score the best marks". The student answered: "Yes, go with it". | 2026-11-21 |
| How the film is made | **A mix.** October's drawn style and voice tell the story; real jobwatch terminal clips appear in Part 3. | Claude's call, offered as "I'll go with C unless you say otherwise". The student raised no objection. | 2026-11-21 |
| How the model calls are paid for | "Only Claude Code". There are no Anthropic API credits. | The student | 2026-11-21 |

The first two decisions are Claude's recommendations. The student's Frictional log should say so (see §9).

## 3. Goals, non-goals, anti-goals

**Goals**
- The four parts appear in the brief's order, and a viewer can tell where each one starts.
- The first 60 seconds stand alone: what Fine Print is and why it matters, with no method.
- Real and planned look different on screen, using the stamps from October.
- Every factual sentence traces to a record (`FACTCHECK.md`).
- The student writes their own Frictional entries at four checkpoints (§9), in their own words, at the time.
- The film is finished by Monday afternoon, leaving a buffer before the 11:30 pm deadline. JS3 is due Wednesday Nov 25
  in Canvas. The repo's brief says Nov 23, but Canvas governs.

**Non-goals**
- It is not the Final Project demo. That one (Dec 20) is a recording of at most five minutes of the system running. This
  film is a plan.
- No new agent code is written for the film. The only runs are of jobwatch exactly as committed.
- It is not JS3. The film must not write the student's JS3 gate (`FILTER.md`: the filter and the evidence rules) for
  them. Part 3 names what JS3 requires in plain words and stops there. *Claude's call:* the film's wording about
  claims and evidence uses only the JS3 brief's own terms and the student's October pitch. If the student reviews the
  script (C2) before writing `FILTER.md`, their JS3 record should say so.

**Anti-goals.** Any of these makes the film a failure, even if it renders fine.
- Past tense for anything that has not run, or a planned piece shown as working.
- A first-person line that credits the student with work Claude did, or the reverse.
- "Hand labels" for labels that were not labelled by hand. JS1's 20 labels were computed by the student's script.
- A claim about another product or paper that was not checked on its own page, with a date.
- The instructor's handle, persona, portraits or credit line. October's `ClaudeTitleOutro` hard-codes `@NikBearBrown`.
- "How" content in Part 1, or a film longer than 5:00.
- Frictional entries written after the fact, or written by Claude.

## 4. Constraints

- **The course honesty rule** (Final Project brief). Use past tense only for what ran and can be shown. Label every
  mock-up, simulation and seeded run. Any Claude response shown must be real, with its date. No invented users, metrics,
  testimonials or results.
- **Privacy.** A fictional persona appears wherever a person does: Alex Morgan in jobwatch, Arjun Rao in A3. The
  student's own background appears only as the student chose in October: on F-1, about two and a half years at Amazon,
  six months at Vertex, and AgentOS. No résumé and no employer data.
- **Model access is the Claude Code login only.** JS1's judge already worked this way. On 2026-10-31 `claude -p` (Claude
  Code 2.1.291, `claude-opus-5-5`) judged 27 new postings. JS1's API route never made a real call because there was no
  key (JS1 README at `99a7443`).
- **Toolkit.** brutalist.art `show-tell` at `519fcbb`, already installed in `Assignment 4/brutalist.art/` (venv `.venv`,
  Python 3.12.7). October hit these traps:
  - `ClaudeTitleOutro` hard-codes the handle, so the outro must be a drawn beat.
  - The `ClaudeDefinitions` terms card fails GATE T at 4K.
  - Gate W skips classes that aren't named like `B07_Foo`.
  - `./setup --install` exits 1 at its own ElevenLabs guard.
  - Kokoro mispronounces the student's name. Use `Assignment 4/final-project-film/name_voice.py`, which the student
    approved by ear.
  - Check frames at about 85% of each beat, because the gates miss key visuals that land late.
- **Job boards.** Read-only HTTPS GET requests, only to the allow-listed endpoints in `jobwatch/boards.py`, with no
  retries, exactly as JS2 runs.
- **Student time is still limited**, because JS3 (100 points) is due two days later, on Wednesday Nov 25. Each
  checkpoint (§9) is kept short.

## 5. Approaches considered

| | How it's made | Good | Costs |
|---|---|---|---|
| A. Same as October | All drawn scenes, with the same synthesized voice reading the student's script | Fastest, and it matches what the class saw | Nothing on screen proves jobwatch runs; real and planned both look like drawings |
| B. Screen recording + own voice | Slides for Parts 1, 2 and 4, a real terminal recording for Part 3, and the student narrates | Most personal; everything shown is real | Most of the student's time, on the JS3 weekend; plainer look |
| **C. Mix (chosen)** | Drawn story, plus real terminal clips in Part 3 | The line between what runs and what's planned is visible, and Part 3's "do you have what you need?" is answered with evidence | One extra step: checking the clips for legibility and privacy |

## 6. The film, part by part

The target length is about 4:30, with a hard cap of 5:00. Beat IDs and exact timings are the builder's call (§12).

### Part 1 — What and why (≤ 60 s)

- **What Fine Print is, in one plain sentence:** an agent that reads new-grad ML job postings for an international
  student, shows the exact sentence behind every requirement that could rule them out, and waits for their approval
  before anything reaches their shortlist.
- **Why anyone should care:** the real A3 finding. Of eight postings that matched by title and sponsor record, six asked
  for 2 to 12+ years of experience or excluded new graduates (A3 `POSTING-REVIEW.md`; the review was for a fictional
  applicant, Arjun Rao). The cost is the time spent tailoring applications to postings that rule you out.
- **Where it stands, in one line:** the half that watches job boards runs today; the half that reads postings is next.
- **Stamp:** `real · from my A3 work` on the finding.
- **No method words in this part:** no loop, tool, gate or budget.

### Part 2 — What others have done (≈ 45–50 s)

- **The student's own A3 recipe:** a title plus a sponsor record could not tell whether a posting fit (6 of 8).
- **LinkedIn:** the student's own check on 2026-10-14 of two graduate ML postings (Qualcomm and TikTok). Both separate
  minimum and preferred qualifications; neither states sponsorship. Two examples support a narrow comparison only.
- **Two or three outside examples**, researched by Claude and each checked on its own page, with a date, before it
  enters the script. Candidates: sponsorship-history lookups built on public H-1B data (they show an employer's filing
  history), résumé-to-posting match scorers, and published research on extracting skills or requirements from job
  postings. Each line says what the thing produces and what it does not, only as far as its own page says.
- **Close:** what Fine Print adds. The exact sentence, checked by code; required, preferred and either-or kept apart;
  sponsorship marked "unknown" when the posting is silent; and a person's approval before the shortlist.
- **Voice:** "I" only for what the student did (A3 and LinkedIn). Outside examples are in neutral voice ("Tools like …
  show …").

### Part 3 — How (≈ 100–110 s)

Part 3 opens with one line, in the student's words from Frictional entry 1, on what changed since October. The pitch
planned to build the reader first. The course's JS assignments built the watcher first, so that is what runs today, and
the reader comes next.

1. **Data:** public job-board APIs (Greenhouse and Ashby) on an allow-list. Each raw response is saved with its SHA-256
   before it is read. The persona is fictional, and no real résumé is used.
2. **What runs today** (real clips, §7):
   - the tests passing on a fresh clone;
   - a live run today against the three boards, with the deliberate 404 control, ending `incomplete` with the state
     untouched;
   - the gate: without the student's approval the saved state is not replaced, and with the student's typed approval the
     run finishes.
3. **How it gets built:** the student writes the rules first (JS2's `GATE.md` was committed before any code, `b55d2a5`;
   JS1's `CONTRACT.md` likewise). Claude Code writes the code and most of the tests. The student signs off or withholds.
4. **Step by step to Dec 20** (stamped `constructed · not built`). Each line names what that assignment requires, in
   plain words. The specific filter and evidence rules are the student's to write in JS3 and are not invented here.
   - **JS3 (due Nov 25):** the reader. Every claim about a posting is labelled supported, contradicted or insufficient
     against the posting's own text, and the reader says "I cannot tell" when the text is insufficient. It is offered to
     Claude as a tool, and the rejects are audited by hand.
   - **JS4 (Dec 1):** each claim is checked by something that fails differently from what made it. The quote check:
     every quoted sentence must appear word for word in the saved raw posting. Memory across days gets a revision rule,
     shown with a two-day diff.
   - **JS5 (Dec 13):** the approval gate is bound to a fingerprint of the exact shortlist. A data register, and a
     supervised run with a controlled failure.
   - **Final Project (Dec 20):** the ten-document packet, the held-out evaluation, the stranger run, and the demo.
5. **Resources:**
   - No API credits. Model calls go through the student's Claude Code login, as JS1's judge did for 27 postings on
     2026-10-31.
   - No accounts are needed for public boards.
   - Compute is a laptop, with the Python standard library.
   - Known limits: a board can refuse automated reads (in A3, OpenAI's Ashby API returned 403), and those postings go to
     a person. Claude Code's usage limits cap how many postings can be read in a day, so reading has a budget.

### Part 4 — How I'll know it worked (≈ 60–70 s)

- **The test set:** real public postings, labelled by the student by hand, split into development and held-out before any
  tuning. None are labelled yet, and the film says so.
- **What gets measured:**
  1. Quote check: every quoted sentence is found word for word, and a test fails if one word changes.
  2. Misreads: required, preferred and either-or against the student's labels.
  3. Two error counts, kept apart: unsupported clearances (a requirement marked as met without support) and false
     exclusions (a posting ruled out wrongly).
  4. How often it says "I cannot tell".
- **At least five deliberate failure cases.** Examples: "5+ years preferred" read as required; an either-or pathway read
  as one rule; a quote with one word changed; a posting silent on sponsorship; a board that answers 404 or 403.
- **One controlled failure:** predicted first, triggered on purpose, caught by an independent check, and recovered with
  review. The prediction is October's named risk, "a true quote read the wrong way".
- **"Worked" and "didn't work":** the student's bar, in their own words, set at C2. Claude does not propose the numbers.
- **Honest limits:** what a sample this size can and cannot show.

### Close (≈ 5 s)

A drawn outro, "Fine Print · Suketh Reddy Produtoor", with no handle. One small on-screen line says the narration is the
student's script in a synthesized voice, and that the appendix holds the detail.

## 7. The real clips (Part 3)

- **Where the runs happen.** Everything runs in a fresh clone of the fork's `js2-loop-tools-diff` branch at `9c1db18`
  (JS2's final commit), placed in this folder's `work/`. JS2's committed evidence and `state/state.json` stay untouched.
  The clone's state is the Nov 8 baseline, so a live run counts the postings that are new since Nov 8. No live run so far
  has found a new posting, because all of them were within three hours of the baseline.
- **Claude runs:**
  - the tests;
  - a live failure-control run;
  - a normal run without approval. Expected: `incomplete`, approval missing, state unchanged, confirmed with `cmp`.
- **The student runs (about 5 minutes):** the normal run with their own `--approve-state RUN_ID:state/state.json`, typed
  in a Terminal panel tab that Claude opens in the clone. Claude never types that approval. If the student has no time,
  the fallback is the Nov 8 `2026-11-08-normal-1` run the student made, labelled with its date.
- **Capture.** Each session's exact text is saved under `evidence/` with its SHA-256. The clip replays that exact text in
  a terminal frame that is legible at film size. It is stamped `real · ran <date> · replay of the saved terminal log`.
  Nothing in a clip is retyped or edited. Trimming removes whole lines only, and each cut is noted in `SHOTLIST.md`.
- **Privacy scan of every clip:** no home-folder paths, usernames, tokens or unrelated windows. Any `~` substitution is
  recorded, as in JS1.
- **Numbers on screen** (counts, new postings since Nov 8) are whatever the run reports. The script does not predict them
  before the run.

## 8. Script, voice and appendix

- The script is in the first person, for the student to approve line by line. Claude drafts it from the records, and the
  student edits it.
- The voice is Kokoro `am_eric`, as in October (the student's choice then), with the student's name voiced by
  `name_voice.py`.
- Captions (`.srt`) are made from the final narration.
- **The appendix** (`APPENDIX.md` and a PDF) holds the detailed plan, the data sources, the resources, the evaluation
  design and links to the evidence. It is submitted with the film.

## 9. Checkpoints: what the student does, and when

| # | Target | The student | About |
|---|---|---|---|
| C1 | Sat 21, tonight | Approve this design. Write Frictional entry 1 in your own words: what changed since the October pitch and why (the pitch brief asks for project changes to be logged in `FRICTIONAL.md`), why this framing (it was Claude's recommendation, so say so and what you think of it), and what you expect to be hardest. If the Canvas assignment shows a rubric, paste it. | 10 min |
| C2 | Sun 22, by about 1 pm | Read the script line by line and fix anything untrue or not in your voice. Write your "worked / didn't work" bar. Frictional entry 2: what you changed and why. | 30–45 min |
| — | Sun 22, afternoon | Type the approval command for the film's normal run (optional; the fallback is in §7). | 5 min |
| C3 | Sun 22, about 9 pm | Watch the first full render and list what's wrong. Frictional entry 3. | 20 min |
| C4 | Mon 23, by about 3 pm | Watch the final version and approve it. Frictional entry 4. Upload to Canvas yourself. | 20 min |

Claude keeps its own work separate, as a factual timeline that uses only times it can prove. Each step starts as soon as
the checkpoint before it is done.

**Changed on 2026-11-21 at the student's request.** The student wrote: "make it the best that will be outstanding,
After everything you finished setting up let me know for approval". So C2 and C3 merge into one review of a complete
draft (the script and the rendered film together). The draft's narration is rendered from Claude's draft script and
labelled DRAFT. Nothing is final until the student approves the script, and changed lines are then re-voiced. C1's
Frictional entry is still asked for now, before building.

*Claude's call on late inputs:* no narration audio is made before the student approves the script at C2. The
"worked / didn't work" bar and the size of the test set are the student's, asked at C2. Part 4's bar beat is rendered
last, so the rest of the film doesn't wait for it. If the bar hasn't arrived by C3, Claude asks again. The film isn't
finished without it, because the brief requires it.

## 10. Deliverables (in this folder)

- The MP4 master and its captions (`.srt`).
- `APPENDIX.md` and its PDF.
- `SCRIPT.md`, `SHOTLIST.md` and `beat_sheet.json`.
- `FACTCHECK.md`: each claim and the record behind it.
- `SOURCES.md`: who did what (the student or Claude), the tools, the licenses, and the prior-art sources with dates.
- `FRICTIONAL.md`: the student's entries, verbatim, with Claude's timeline kept separate.
- `README.md`: what the film is, how it was made, what's real and what's constructed, and the MP4's filename and SHA-256.
- `evidence/`: the film's terminal logs with their hashes, and the prior-art page checks.
- `work/`: the clone, renders and scratch files. Not submitted.

**Submission.** The student uploads the MP4 and the appendix PDF to Canvas. The pasted brief doesn't mention GitHub.
*Claude's call:* prepare a GitHub-ready copy by default, in a new folder, because
`fall-2026/suketh-p/final-project-film` already holds October's film. The student decides at C4 whether to post it, and
opens the PR themselves.

## 11. Risks

- **Student time** (JS3 is due two days later). Mitigation: short checkpoints, and a fallback for the one optional
  student run.
- **Toolkit gates failing**, as they did in October. Mitigation: reuse October's fixes (§4), and disclose any gate that
  could not pass and why.
- **A live board failing at capture time.** The run then says `incomplete`, and the film shows that honestly. The Nov 8
  runs are the fallback.
- **Thin prior-art findings.** Part 2 then uses only what was verified, even if that is only the A3 recipe, LinkedIn and
  one outside example.
- **Claude-drafted first-person lines drifting from the record.** Mitigation: `FACTCHECK.md` before any audio is made,
  and the student's line-by-line review at C2.

## 12. Left to the builder

- The beat count, the order of beats within each part, and exact timings.
- Which October scenes to adapt (B00 recipe binder, B01 eight postings, B03 quote check, B04 misread, B06 loop, B07 gate,
  B08 alternatives, B10 evaluation, BOUT) and which to make new.
- How the terminal replay is rendered: its frame and font size.
- Render resolution and gate set: October's targets, unless a gate blocks for reasons unrelated to quality. Any skipped
  gate is disclosed.
- Which two or three outside prior-art examples make the cut, as long as each one is verified.
- Filenames.

## 13. Questions from the reviewer check (2026-11-21), and their answers

1. **Final Project Update 1 (due Nov 5).** This is a separate assignment from October's pitch film: "Final Project
   Update 1 — The First Working Slice", 50 points, one working slice plus a recording of 90 seconds or less.
   October's `FRICTIONAL.md` (line 119) promised that Update 1 would be the
   reader's first slice: read one allowed posting, extract requirements with verbatim quotes, verify the quotes, and stop
   at the gate. No Update 1 work was found in the fork, upstream, or on the Desktop, Documents or Downloads. Did it
   happen? The answer decides whether Part 1's "the reading half is next" is true and what the film says changed since
   October.
   **Answered:** the student's Canvas Assignments list (screenshots, 2026-11-21 18:34) has no Final Project Update 1. It
   was never assigned on Canvas, so nothing was missed. "The reading half is next" holds. Part 3 still says plainly what
   changed since October (see Part 3). The same list shows JS3 due **Wednesday Nov 25**, not Nov 23.
2. **The voice.** The pitch, Update 1 and Final Project briefs all say "Narrate as yourself"; the new brief says nothing
   about narration. In October the student chose Kokoro reading their first-person script, and disclosed it. What did
   October's film score, and did the feedback mention the voice? Kokoro again, or the student's own recorded voice?
   **Answered in part:** the student's Canvas screenshot (2026-11-21) shows "Final Project Pitch Film — Show What You
   Will Build" graded 49 out of 50. The TA's only comment is "nice work!!", with nothing about the voice. That pitch brief
   also says a project may change later if the change is logged in `FRICTIONAL.md`. *Claude's proposal:* keep Kokoro
   `am_eric` unless the student wants to record their own voice.
3. **GitHub.** Every earlier film and JS assignment graded a GitHub posting; this brief doesn't mention it. Post the
   film's folder too? Publishing needs the student's yes, and the student opens the PR, as before.
   **Settled as Claude's call:** a GitHub-ready copy is prepared by default, and the student decides at C4 (§10).
