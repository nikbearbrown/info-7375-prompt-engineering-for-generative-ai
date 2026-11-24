# FRICTIONAL — Final Project Pitch Film

Riya Kapadnis · INFO 7375 · Fall 2026

> **Who wrote what (added 2026-10-21).** The five entries dated 2026-10-09 to 2026-10-14 were
> drafted by Claude from my decisions and the run outputs, as SOURCES.md says. They are kept
> unchanged as the record of the first submission (commit `42d8c48`). One correction: the
> 2026-10-14 entry says I confirmed "that I read the Vanna README myself". SOURCES.md said
> Claude read and summarised it. That entry was wrong: I only read Claude's summary of the Vanna README, not the README itself. On 2026-10-21 I ran Vanna myself (see the last entry). The entries from 2026-10-19
> on are written by me.

---

## Entry

**Date and what I was working on:** 2026-10-09: choosing the project and the target role.

**I tried / expected:** I had three candidates: extend my Reallocation Engine recipe, a
text-to-SQL evaluation harness, or a document-QA tool with grounded tests. I picked
text-to-SQL. I was unsure whether to frame it for AI Engineer or Data Analyst roles, and asked
Claude which would be more useful on a resume.

**What happened:** Claude recommended AI Engineer. Its reasoning: the artifact is evaluation and
verification work, which is what AI Engineer screens look for and what this course teaches,
and the business-question test set still reads well for analyst roles. Before committing,
Claude grepped every `fall-2026/*` folder for "text-to-SQL", "NL2SQL" and similar.
There were no hits. Only the instructor's `final-project-film` folder existed.

**What I did:** Went with text-to-SQL, framed for AI Engineer.

**What Claude or another person contributed:** The role recommendation and the overlap check.
The project choice was mine.

**What I understand now / still do not understand:** The project is only worth showing if it
finds failures a reader would not have spotted. An accuracy number alone would not be enough.
I don't yet know how often Claude will actually fail on a small, clean schema like Chinook. If
it almost never fails, the project has to move to harder questions or a messier schema, and I
would log that change here.

**Evidence and next step:** `PROJECT-BRIEF.md`. Next: build one real slice so the pitch has
something true to show.

---

## Entry

**Date and what I was working on:** 2026-10-09: building the first runnable slice.

**I tried / expected:** 8 questions over Chinook v1.4.5 (public, MIT), each with gold SQL, plus
9 hand-written variants: 3 that are different SQL with the same answer, and 6 plausible wrong
queries (join fan-out, COUNT vs COUNT DISTINCT, wrong join key, unit error, bad date filter,
wrong table). I expected the execution comparator to judge all 9 correctly on the first run.

**What happened:** It got 8 of 9. The miss was the Q08 "wrong" variant, which was judged PASS.
The comparator was right and my gold answer was wrong. I had asked for "revenue in 2023", but
Chinook's invoices run 2009-01-01 to 2013-12-22. The gold query returned `[(None,)]`, the
broken query also returned `[(None,)]`, and NULL equals NULL. My existing check only asserted
that the gold returned *rows*, and `[(None,)]` is a row.

A second, smaller problem: my first Q02 "wrong" variant changed two things at once (dropped
the tie-break *and* changed `LIMIT 5` to `LIMIT 4`), so its label described the wrong bug.

**What I did:** Kept the first run's output as `evidence/run_slice_output_v0_first_run.txt`
rather than overwrite it. Changed Q08 to 2013. Changed the runner so it rejects any gold
result that is empty or all NULL. Replaced Q02's variant with one that makes a single,
clearly labelled mistake (counting invoices instead of customers). Re-ran: 9/9, exit 0.

**What Claude or another person contributed:** Claude drafted `gold_set.json` and
`run_slice.py`, including the Q08 gold query with the bad year. Neither of us checked the date
range before writing the question. The run caught it. I want that on record, because the
point of the project is that a confident-looking answer needs checking.

**What I understand now / still do not understand:** A gold set is a claim too, and it needs
its own checks. Comparing the exact SQL text "agreed" with my labels on 6 of 9. That number
flatters it: it rejected every wrong query only because their text differed, and it also
rejected all 3 correct rewrites. Still open: Q04's gold answer is 59, which is every customer
in Chinook, so that question cannot tell "customers who bought Rock" apart from "all
customers". It needs replacing in the full set.

**Evidence and next step:** `evidence/run_slice_output_v0_first_run.txt`,
`evidence/run_slice_output.txt`, `evidence/gold_set.json` (note field records v0 → v1).

---

## Entry

**Date and what I was working on:** 2026-10-09: writing the narration and fitting it in 4 minutes.

**I tried / expected:** One beat per question from the assignment, plus a conclusion. I
expected about 3:30.

**What happened:** The first full voice pass measured **257.8 s (4:18)**, over the limit. Most
beats ran 18–24 s, and the show-tell skill flags anything over ~15 s as probably two ideas.

**What I did:** Cut wording, not content: every one of the seven answers is still there.
The second pass measured 233.1 s of narration (about 3:55 with the opening silence and the
outro tail).

**What Claude or another person contributed:** Claude wrote the first narration draft from the
brief and did the cuts. I need to check every line against what I would say myself (see the
open item below).

**What I understand now / still do not understand:** Two toolkit defaults conflict with this
assignment: the show-tell skill's default narrator is "Liam, in for Bear" with an
@NikBearBrown outro, and the assignment says not to use the instructor's name, persona or
credit line. I switched to the toolkit's other free voice (Kokoro `af_bella`), wrote the
narration in the first person as me, and set the outro handle to my name
(`metadata.channel_title`, which `bookend_check.py` reads). The voice is synthetic. It is not
my recorded voice, and README.md says so. The toolkit's CLAUDE.md lists show-tell as
"Advanced — Bear only". I used it because this assignment names it as the right format.

**Evidence and next step:** `beat_sheet.json` (`actual_duration_s` per beat), `make_sheet.py`.
Next: render, run the gates, watch the cut.

---

## Entry

**Date and what I was working on:** 2026-10-09 → 2026-10-10: rendering and running the toolkit's gates.

**I tried / expected:** `./art run` then `./art final`, fixing whatever the gates flagged.

**What happened, in order:**

1. **Gate F** refused to render: no `FACTCHECK.md`, `SHOTLIST.md` or `PROMPTS.md`. I wrote
   them first. The fact check turned out to be useful for the honesty rule anyway, because it
   forced a source for every spoken number.
2. The first render was in a fallback sans-serif font. Manim logged `Font EB Garamond not in`
   for every label: the toolkit ships the font but it was not installed on this Mac.
   I copied `runtime/fonts/EB_Garamond/static/*.ttf` to `~/Library/Fonts` and re-rendered.
3. **Gate V** (frame QC): one MAJOR defect, B02 at its midpoint, contrast 0.26 against a 0.30
   floor. That was a pale bar on a pale plinth. The skill's own advice is to set pale blocks on
   a dark plinth, which fixed it.
4. **GATE T** (type check) blocked `./art final` twice. First, B02's dark plinth ran off the
   bottom of the frame and counted as overflow, so I moved the chart up. Second, the terms card
   kept failing at 40px against a 41px floor. Shortening the definitions didn't help, and
   capitalising the footer didn't help either. I stopped guessing and ran the gate's own blob
   detector on the frame. The failing blobs were letter clusters with no tall letters: "ans"
   and "ers" in "answers", "rows", and "ons" in "questions". In EB Garamond at this size, a
   lowercase body measures exactly 40px. I tested new wording with a 4K Remotion still before
   re-rendering. "the right SQL, checked by hand" and "judge SQL by its output table" pass.
   The smallest run is now 46px.
5. Every gate then passed, and **watching the frames** found what none of them check:
   the outro card read **"@NikBearBrown"** with the Claude mascot, even though I had set the
   handle to my name. `ClaudeTitleOutro.tsx` hardcodes that handle ("no prop, no lookup, no
   override"). It belongs to the instructor's channel, and the assignment says not to use the
   instructor's credit line.

**What I did:** Did not edit the shared toolkit. I dropped the outro beat, so the film ends on
the conclusion (BCON). That is also the ending I prefer: a takeaway rather than a credit card.
Because the title had only appeared on the outro, I added it to the opening banner. As a
result, `bookend_check.py` now reports one failure, "no ClaudeTitleOutro beat". I am
submitting with that failure, deliberately, and its report is in `gate-reports/`. It is a
house-style check, not a render-integrity check. The render-integrity gates (Gate V, GATE T,
and the master's `verified.json` with status `ready`) all pass.

**What Claude or another person contributed:** Claude ran the pipeline, read each gate report,
made the fixes, and wrote the blob probe that found the real cause of the 40px failure. It
also caught the @NikBearBrown outro by pulling frames at 20%, 62% and 95% of every beat
instead of relying on the gates. The gates had passed that frame.

**What I understand now / still do not understand:** Exit codes did not catch a wrong
credit line. Only looking at the frames did, which is the same lesson as Week 1. Still open: I
don't know whether the instructor wants students to keep the bookend check green some other
way (for example, a student-handle outro component). If there is one, I didn't find it.

**Evidence and next step:** `gate-reports/` (Gate V REPORT.md, TYPECHECK.md, layout audit,
bookend check, fact-check, `verified.json`), `reel/_qc/contact_sheet.png`. Next: I watch the
full cut once with sound, confirm the open items in PROJECT-BRIEF §7 and SOURCES.md, then commit.

---

## Entry

**Date and what I was working on:** 2026-10-14: final review and assembling the folder.

**I tried / expected:** Watch the full cut with sound, then close every open item before committing.

**What happened:** I watched the full film with sound. Three things in the folder were still
open: the "Why this project?" answer in PROJECT-BRIEF §7 was a placeholder, SOURCES.md still
had my sign-off unconfirmed, and README.md had empty runtime and gate-summary slots. The folder
was also missing `beat_sheet.json`, `gate-reports/` and `reel/`, even though the README listed them.

**What I did:** Wrote §7 to match what the film's B10 narration says. Recorded my review in
SOURCES.md. Filled in the README: runtime 3:52 and a gate table. Copied in the beat sheet, the
gate reports and the film source. Shortened the home-directory paths in `verified.json` and
`final.log` to `<INFO7375>/`. Trimmed the brief's wording toward one page without dropping any
of the seven answers or any number.

**What Claude or another person contributed:** Claude did the copying, filled in the
placeholders, and did the trim. I watched the cut.

**What I understand now / still do not understand:** FACTCHECK.md waited on my sign-off.
Claude re-checked the numbers against the evidence (4,667.06 vs 523.06, a ratio of 8.92; 9/9;
invoices 2009–2013). I confirmed the two claims only I could: that I read the Vanna README
myself (claim 5), and that the TwinAI co-op skills are accurate (claim 10). Signed off 2026-10-14.

**Evidence and next step:** `gate-reports/`, `reel/`. Next: commit, zip, and submit to Canvas.

---

## Entry (written by me)

**Date and what I was working on:** 2026-10-19: redoing the film after the instructor's feedback.

**I tried / expected:** The problem I was trying to solve wasn't clear in the first film. It
also lacked animations and explanations. I expected the redo to fix that.

**What happened:** The new video shows examples and explains the problem I am trying to solve
more properly, which shows how my project will really help people.

**What I did:** I approved the new script and checked the numbers.

**What Claude or another person contributed:** I accepted Claude's narration, but there were a
few animations and scenes that I asked it to change.

**What I understand now / still do not understand:** It taught me that we can't just depend on
what the AI gives us. We should check it, question it, and ask it to make changes accordingly.

**Evidence and next step:** `reel/` (v2 source), `reel/SCRIPT-v2.md`, `gate-reports/`

---

## Entry (written by me)

**Date and what I was working on:** 2026-10-21: acting on the TA's feedback for the resubmission.

**I tried / expected:** Honestly, because of the low grade (38.5/50) I decided to resubmit. I
decided to fix the Vanna check and get a second check of my answers.

**What happened:** What surprised me most was that my Vanna claim was wrong. My old film said
Vanna had no way to check answers. It does have tests. I had only read a summary, so I had
stated something I never checked. When I ran it, its own test passed the answer that was nine
times too high, because it only checks that the right words are there. Claude passed 22 of 24
on my questions, and the two fails were my question's fault (a France/Brazil tie it never
settled). My classmate could not do the check, so I used a second method instead.

**What I did:** I ran Vanna on Chinook (`evidence/vanna_check_output_2026-10-21.txt`). I checked
the BIRD page myself (12,751 question-SQL pairs, 95 databases). I used a second-method check,
`evidence/cross_check.py`, which recomputes every gold answer in plain Python from the raw
tables. All 8 agreed, and it found 2 weak questions: Q02, whose top 5 has a tie the question
never says how to break, and Q04, whose answer (59) is every customer in the store, so it can't
tell "bought Rock" apart from "all customers". I feel good that I was able to check it myself
and found a few problems along the way.

**What Claude or another person contributed:** Claude wrote the Vanna check and the cross-check
scripts, ran the three Claude tests, and re-edited the film. I ran Vanna, checked BIRD, and
reviewed the results.

**What I understand now / still do not understand:** My questions are too easy: Claude got every
answer right. I also don't know yet how often Claude really fails. Next I will write harder
questions, fix Q02 and Q04, and move to a messier database if Claude still rarely fails.

**Evidence and next step:** `evidence/vanna_check.py`, `evidence/claude_runs/2026-10-21/`,
`evidence/cross_check_output_2026-10-21.txt`, `reel/FACTCHECK.md` (rows 11, 15, 17, 20, 21)


---

## Entry (written by me; evidence links added by Claude)

**Date and what I was working on:** 2026-11-22 to 2026-11-23: turning my pitch film into the
four-part final film (executive summary, introduction, methods, evaluation).

**What was hard:** It was difficult to divide all of them in 4 parts and explain each one of
them separately.

**What I decided:** I decided that I should use Claude Code instead of an API key, made some
graphic changes in the video and changed a few wordings in the videos which I thought would make
it easier to understand for the viewer.

**What I checked, and what Claude or another person contributed:** I watched the video myself
and checked it thoroughly. Whatever I didn't like, for example the wording or the graphics, I
asked Claude to change and it did that.

**Evidence and next step:** my two review notes on the first v4 cut were B05 (no line from
"AI data assistant" to the report card) and B20 (the jump from the recap to the closing line
felt off; now "In conclusion" / "So the takeaway is this"). Claude Code choice: B14 and
`APPENDIX.md` §3.3. Script as built: `reel/SCRIPT-v4-four-parts.md`; sign-off: `reel/FACTCHECK.md`.
