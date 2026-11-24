# Frictional — Final Project Film (four-part)

Varnika M · INFO 7375 · *A Job-Search Agent You Can Check*

Entries are dated on the day they happened. Claude Code (NEU-provisioned) organized these notes
from the session. The "What I understand now" lines and the final reflection are mine, in my own
words.

---

### 2026-11-23 — New assignment, or a redo?

- **What I was working on:** Professor Bear's email "What your project film needs to show" and the
  Canvas assignment "Final Project Film" (25 points, due tonight, 11:30 pm).
- **What happened:** the email does not say "new film" or "reuse your old film". It only asks for a
  film about my project in four parts, in order. My October pitch film (*Terraform Docs, Quoted*)
  follows a different order and has almost no evaluation part. Several classmates posted
  four-part re-cuts of their pitch films the same day.
- **What I decided:** to make a new four-part film. I also changed the project, from the Terraform
  docs tool to my job-search agent (below).
- **What I understand now:** *I learned that when an assignment is unclear, I should compare the instructions with my previous work before deciding whether to reuse or start over. In this case, making a new film helped me follow the required four-part structure.*

### 2026-11-23 — Changing the project to the job-search agent

- **What happened:** Claude Code suggested three ideas: my job-search agent, an agentic version of
  Terraform Docs Quoted, and a new Terraform plan reviewer. The final project brief requires a
  loop, tools with a permission policy, memory or state, a stop condition and a human gate. It also
  allows "the job-search agent you built across the course". My JS1 and JS2 already have the loop,
  the permission policy, the state and an independent checker. My October Terraform idea was a
  question-answering tool, not yet an agent.
- **What I decided:** the job-search agent.
- **Evidence:** `../../js1-contract-and-watch/`, `../../js2-loop-tools-diff/`.
- **What I understand now:** *I learned that choosing a project that already has working parts makes it easier to build on existing work. My job-search agent was a better fit because it already had most of the features required for the final project.*

### 2026-11-23 — Part 2: one claim I almost made was wrong

- **What happened:** the plan was to say "no other tool has a person in the loop". The research
  found Simplify's Copilot mode, where you "click the employer’s final Submit button yourself". So
  a human step does exist, for one application form at a time.
- **What changed:** the film says what the pages show. Finding and applying are automated, and none
  of these pages mentions rules you can recheck, a separate run checker, or a person approving a
  whole shortlist. LinkedIn's Premium "how you match" page returned 404, so it was left out.
- **Evidence:** `evidence/others-2026-11-23/README.md`.
- **What I understand now:** *I learned that I should not make broad claims without checking the evidence first. Even if a competitor has a different approach, I need to describe it accurately and explain what makes my project different.*

### 2026-11-23 — The pass line for check 2 was worded wrong in the choice I was given

- **What happened:** I chose the "strict" pass line. Its option text said the agent "skips at least
  half of a 'should skip' test list (the course rule)". The JS5 rule is different. It says a
  healthy run skips at least half of **everything it evaluates**. Skipping only half of a list of
  postings that must all be skipped would be a weak test.
- **What changed:** Claude Code wrote check 2 as "every must-skip posting is skipped, **and** the run
  skips at least half of what it evaluates". The film (B14) says "If even one gets through, that's
  a fail."
- **What I decided:** on 2026-11-23, after an explanation with a 4-posting example, I confirmed the
  strict wording: "yes".
- **What I understand now:** *I learned that small differences in evaluation wording can change what a test actually checks. I need to understand the exact pass condition instead of choosing an option just because it sounds strict.*

### 2026-11-23 — The computer voice: two lines could be misheard

- **What happened:** a speech-to-text check of every narration clip heard "every failure I plant"
  as "every failure I planned", and "any one fails" as "anyone fails".
- **What changed:** reworded to "every planted failure" and "if even one check fails", re-voiced,
  and re-checked (both transcribed correctly). Other transcriber slips, such as "cloud code" for
  Claude Code, were the transcriber's spelling, not the voice.
- **What I understand now:** *I learned that a voiceover can sound correct to me but still be misunderstood by speech-to-text tools. I should use clear wording, listen carefully, and check the transcription before finalizing the narration.*

### 2026-11-23 — Toolkit gates that failed, and the fixes

- **Gate F:** refused to render before `FACTCHECK.md`, `SHOTLIST.md` and `PROMPTS.md` existed. They
  were written, and every claim was checked against my JS1 and JS2 files and the saved pages.
- **Gate A:** B16, then B17, failed "shapes never change", because their changes were mostly colour
  and line changes. Added a "new fingerprint" tag and a cross (B16), and a banner and a red outline
  on the failed box (B17).
- **Gate B:** B01's "job boards" label sat under passing cards. Moved it down. The part label and
  corner tags sat just outside the safe area, so they were moved in.
- **Gate B, again:** B06's "applied" and "no review" stamps sat on the cards' text lines, and B16's
  cross sat on its "approved" stamp. The outro title was too wide. Stamps moved above the cards, the
  cross was replaced by a "no longer counts" tag, and the title was made smaller. To stop finding
  these one at a time, the same audit was run on every remaining scene in parallel before the next
  render.
- **Gate V (whole cut):** low contrast in B02 (light grey dots) and B11 (pale steps, grey labels).
  The dots are now ink, and the steps are white with ink labels.
- **Gate T (before the final export):** every scene failed WCAG contrast, because the part labels,
  stamps and highlights used the brand accent `#D97757`, only 2.74:1 on cream (4.5:1 needed). All
  accents were switched to a darker rust, `#A3472A` (5.27:1), and all 18 scenes were re-rendered.
- **After the gates, by eye:** frames from the final cut showed four reveals landing in the last
  second of their beat: "1 match" (B02), "not yet" (B03), the fifth rule card (B09) and the JS2
  "caught" tag (B15). They were moved a few words earlier. B02 also got a 1-second silent tail, so
  "1 match", the film's key number, stays on screen for about 2 seconds. Re-rendered and
  re-exported, with all gates passing again.
- **Before the gates, by eye:** a contact sheet of every scene's last frame showed overlaps in B03,
  B04, B08, B12 and B14. In B10, `add_tip()` stretched the loop to about 1.4 times its size, so the
  tip is now drawn by hand.

---

### Final reflection

I learned that I need to check the actual implementation before describing it and make claims only when I have evidence to support them. I also learned that passing automated checks is not enough. I need to review the final film for timing, readability and accessibility.
