# PROMPTS — Readback project film

No generative media: no image, video or voice-cloning prompts. The narration is the free local Kokoro voice `am_onyx`, synthesized from the script I approved (Phase 1 on 2026-11-23, and the revised narration that evening). Every visual is a deterministic Manim or Remotion render. The three B02 vignettes are constructed illustrations drawn in Manim; they are not generated images or real product outputs.

## Prompts behind real material shown in the film

**Recap feature (the B10 excerpt from ES2007a, and the B14 excerpt from ES2010b).** The system prompt is `../../case-study/constructed/recap-system-prompt.md` (everything below its `---` line). `../../case-study/run_feature.py` sent it with `claude -p --system-prompt … --tools "" --output-format json`, with each meeting's `transcript.txt` as the input. The outputs, with their date, Claude Code version and model, are in `../../case-study/outputs/feature-run/`.

No other Claude response appears on screen.

## How the film was made

These are the prompts I sent to Claude Code, in order. The four-part prompt, the revision prompts and the final fix-pass prompts were drafted in Claude chat at my direction, from my feedback; I sent each one (see ../../SOURCES.md and FRICTIONAL.md, 2026-11-23). The log, with each decision, is `../../FRICTIONAL.md`.

1. **"Readback project film (four-part brief)" (2026-11-23).** It set the four parts (executive summary, introduction, methods, evaluation), the hard rules (honesty, labels, prior work as plain text, no instructor persona, the pitch films untouched, a free local pipeline, commits without attribution trailers) and the phases with stop points.
2. **Phase approvals:** Phase 1 (narration and claims), Phase 2 (storyboard), then "Approve, go to Phase 3".
3. **My review requests before Phase 5:**
   - B15's checklist only ticks what is set up on this Mac;
   - the human labels read as mine and planned;
   - prior work is scoped to "the tools I checked";
   - B13 is reworded and Readback respelled for the voice;
   - the storyboard is regenerated and every gate re-run;
   - the submission options, then my choice of route, and four checks (clip hashes, full-film speech-to-text, the B15 wording, a full gate re-run).
4. **My feedback on the review cut:**
   - the positioning (Readback is for any AI feature's acceptance criteria; the AMI meeting-recap feature is only the test bench);
   - P0 items 1–7 and P1 items 8–13;
   - a new positioning-audit gate;
   - text before voicing.
5. **Approvals:** "OK, go" for the revised narration and build, then "Approve cut".
6. **After the approval:** the final fix pass, the paperwork pass, the PR #54 entry, the Canvas zip, and this documentation fix pass with its appendix. Their full texts are under "Prompt texts" below.

For each step, Claude Code drafted the narration, the claims ledger (`CLAIMS.md`), the evaluation plan (`EVAL-PLAN.md`), the design system (`DESIGN.md`), the scenes and the gate reports. I approved each phase before the next.

## Prompt texts

The full text of each prompt, copied verbatim from the Claude Code session, in the order I sent them. Prompts only: no replies or transcripts, the same rule as the pitch film's `../../BUILD-PROMPT.md`. Times are EST on the session's clock.

### 1. The four-part prompt (2026-11-23, 04:45 EST)

Sent in one message after the line "New Assignment:" and the instructor's email with the brief. The email isn't reproduced here: it is the course's text, not my prompt, and the prompt quotes the brief.

````text
Claude Code prompt: Readback project film (four-part brief)
Paste everything below the line into the Final Project session.
We're making a new film for Readback. It's not a re-cut of the pitch film. The pitch film answered seven fixed questions. This one follows a new brief from the instructor, and the brief's structure replaces the old one completely. Retire the seven-question beat order, the "Q1 · what it is" style headers and any pitch-film narration. Reuse the visual system, the toolkit setup and the real evidence.
The brief (governs structure; quoted from the instructor's email)
Four parts, in this order:

1. Executive summary. What I'm doing and why anybody would care, in plain words. No "how." Someone who watches only the first minute should know what this is and why it's worth doing.
2. Introduction. What others have done, who has tried this or something like it, and what they got. Then why anybody should care about mine.
3. Methods. How I'll build it, where the data comes from, the steps, and whether I have what I need (token credits, accounts, access, compute). The detail lives here and in the appendix, never in the executive summary.
4. Evaluation. How I'll know it did a good job: what gets measured or checked, and what result means it worked versus didn't.

Hard rules (non-negotiable)

1. Honesty. Show no invented numbers, results, users or testimonials. A number appears on screen only if it comes from a file that exists in this repo, and you cite the path. Show every planned metric as "—" or "will be measured," drawn in the grey "will" style, never as a placeholder value. If anything in Evaluation has actually been run, the real result goes on screen with its date. Otherwise it's a plan, and the narration says so.
2. Labels. Constructed material (the PRD, system prompt, rubric) carries `CONSTRUCTED`. Real material carries its source and date, for example `AMI ES2007a · CC BY 4.0` or `real output · <model> · <date>`.
3. Prior work is plain text. Maxim AI, orq.ai and GitHub Spec Kit appear by name only. No logos, no screenshots of their sites, no brand marks for Google, Zoom, Microsoft or Anthropic. State what each one does only as far as FRICTIONAL.md already records what I verified. If you'd need a claim I haven't verified, stop and ask me.
4. No instructor name, persona or credit anywhere in the film. The Claude mascot stays hidden in the outro, via my existing patch.
5. Don't touch the pitch films. v1 (31005a1) and v2 stay as they are. Render the new film to `aravind-r-readback-project-film.mp4`.
6. Free local pipeline only: Kokoro, Manim, Remotion, ffmpeg. No paid services.
7. Commits. Never add a `Co-Authored-By` or "Generated with Claude Code" trailer. Check `.claude/settings.json` (project and user level) before the first commit. After every commit, verify with `git log -1 --format=%B`. If a trailer slipped in, amend it out before pushing.
8. Stop points are real. At each STOP, report and wait. Don't start the next phase on your own.

Phase 0: Orient (then STOP)

* Run `pwd`, `git branch --show-current`, `git status` and `git log --oneline -5`. Confirm we're on `final-project-film-aravind-r` in the Brutalist fork.
* Inventory what we can reuse, with paths: Kokoro voice config, Remotion components, Manim scenes, the v2 colour and type tokens, AMI selection CSV, real recap outputs, the constructed PRD, system prompt and rubric, FRICTIONAL.md and the prior-work notes.
* Ask me three things: the submission deadline, the runtime cap for this film, and what resources I actually have for Methods (which judge models, claude -p on my subscription or API credits, any second-provider access). Don't assume any of these.
* Set a hard stop 90 minutes before the deadline. If the film isn't fully gated by then, we submit the best gated cut and log it in FRICTIONAL.md.

Phase 1: Script and claims ledger (then STOP)
Write `film/project/beat_sheet.json` and `film/project/CLAIMS.md`.
Pacing. Derive words-per-minute from the existing Kokoro clips rather than guessing, and budget each part from the runtime cap. Rough split: summary 20%, intro 20%, methods 35%, evaluation 25%.
Executive summary. Open on the problem in under 10 seconds, with no title card first. PMs now write rubrics that AI judges grade against. When judges disagree, nobody can tell which clause caused it. Readback finds the clause and asks the PM a clarifying question instead of rewriting it. Say why it matters, and leave all mechanism out.
Introduction. Cover what exists: multi-judge agreement tools and spec clarify steps. Then name the gap I actually verified, clause-level attribution of disagreement. Close by restating why that gap matters.
Methods. Lay out the pipeline in the order it runs. The data is the AMI Meeting Corpus (CC BY 4.0) and the 10 selected meetings. The feature under test is the constructed meeting recap. Then the rubric, then multiple judges scoring the recaps, then agreement measured judge-vs-judge and judge-vs-human, with the human labels being AMI's decisions annotations for the anchored clause. Then disagreement traced to clauses, then the clarifying question to the PM. Finish with a "what I have" checklist on screen showing data, accounts, credits and compute. Show only what I confirmed in Phase 0, and mark anything missing as missing.
Evaluation. Use three checks, each with an explicit pass/fail condition said out loud:

1. Planted-ambiguity test. Seed known ambiguities into specific clauses. It passes if Readback attributes disagreement to the seeded clause, and fails if it blames another clause or noise.
2. Anchored-clause agreement. Measure judge-vs-human agreement on the decisions clause against AMI labels. Name the statistic, for example Cohen's kappa. Show no value unless one has been run.
3. Before/after. Revise the flagged clause from the PM's answer, then re-measure judge agreement. If agreement doesn't rise, Readback didn't help. Say that outright.

CLAIMS.md lists every sentence of narration and every on-screen number. Each one maps to an evidence path or is marked PLANNED. Any claim that maps to neither gets cut.
STOP. Show me the narration as plain text with per-part word counts and estimated runtime, plus the claims ledger.
Phase 2: Design system and storyboard (then STOP)
The bar is that the film should look designed, not assembled. Concretely:

* One visual system across all four parts. Use a fixed palette with named colour roles: real evidence, constructed material, planned/"will" grey, and a single accent for "the clause." Use one type scale and one grid. Section transitions should share the same motion language.
* A persistent hero object. The rubric clause is a physical "chip" that the viewer follows the whole way through. It's introduced in the summary, sits among existing tools in the intro, travels through the pipeline in Methods, and gets tested in Evaluation. Motion should enact the idea. Disagreement is judges' scores pulling apart, and attribution is the line tracing back to one clause lighting up.
* The evidence is big. Real AMI transcript lines, real recap outputs and real counts appear at full legibility, filling the frame when they're the point. Don't tuck them into corners.
* Use the whole frame. No layouts that leave half the canvas empty.
* The Methods pipeline builds itself as narration names each stage, rather than appearing whole.
* The Evaluation criteria render as a pass/fail scorecard. Planned cells stay visibly empty.

Deliver one rendered style frame per part plus a storyboard contact sheet (one still per beat) at `film/project/storyboard.png`.
STOP for my review before any full render.
Phase 3: Build

* Generate narration with the same Kokoro voice and settings as the pitch film, then normalise.
* Make every beat move. Static holds longer than 2.5 s are allowed only where the narration lands a key line, and each one gets listed in SHOTLIST.md with a reason.
* Keep background colours identical across every cut.
* Render a review cut and continue straight to Phase 4.

Phase 4: QC gates (then STOP)
Run these and report a pass/fail table with the measured values:

* `freezedetect=n=0.003:d=3`. Total frozen time must be under 15% of runtime, and every hold must be one listed in SHOTLIST.md.
* `blackdetect`: no unintended black frames.
* Loudness: integrated −16 LUFS ±1, true peak ≤ −1 dBTP.
* Silence: no dead air over 1.2 s between beats.
* Runtime is within the cap.
* A contact sheet (`fps=1/4,tile=6x8`) and a frame grab at every section boundary.
* Background colour sampled at every cut: identical.
* Label audit: every constructed item says CONSTRUCTED, and every real item has a source and date.
* Numbers audit: every on-screen number matches its source file.
* First-minute test: someone who watches only 0:00–1:00 knows what Readback is and why it matters, with no "how." Quote the narration that proves it.
* Brand and persona audit: no logos, no instructor name, mascot hidden.

STOP. Send me the review cut path, the contact sheet and the gate table. Fix before enhance: resolve every failed gate before polishing anything else.
Phase 5: Paperwork and commit (only after I approve the cut)

* Update FACTCHECK.md, SHOTLIST.md, PROMPTS.md, SOURCES.md and FRICTIONAL.md for this film. Attribute accurately between Claude Code, Claude (chat) and me. Leave the judgment-call entries for me to write.
* Commit, verify there are no trailers with `git log -1 --format=%B`, and push to my fork.
* Don't open or update a PR until I say so.
````

### 2. Requests before Phase 5 (2026-11-23, 15:47 EST)

````text
Not approved yet. Before Phase 5:

1. Show me the exact B15 narration and on-screen resource checklist. Only show "have" for what is set up on this machine today (claude -p; anything else you verified). Credits or second-provider access that exist but aren't configured here: label "account, not yet wired". Ollama: planned. No claim of access you didn't verify.
2. Quote every line that mentions human labels or judge-vs-human agreement. They must say the human marking of the 86 AMI decisions is planned and done by me. Don't call AMI's DECISIONS list a label set.
3. Quote every prior-work line. Scope any "nobody/no tool" claim to "the tools I checked" (Maxim AI, orq.ai, Spec Kit).
4. Reword the B13 line so "Claude" and "clause" never sit next to each other, then re-voice B13 only. In the Kokoro input, spell Readback phonetically wherever it's spoken and re-voice those beats. Re-run speech-to-text on all changed beats and show me the transcript.
5. Regenerate the storyboard and style frames from the final code, or add a note to SHOTLIST.md saying they show Phase 2.
6. Re-run every gate on the new master and update GATES.md.
7. PR #18 is merged. Tell me the options for submitting (new branch + PR vs new PR from this branch) and wait for my choice.

Stop after 6 and 7. I'll watch the new cut, with sound and without, before approving.
````

### 3. Item 7: my choice of route, and the checks (2026-11-23, 16:13 EST)

````text
Item 7: new branch from the current head (2cad8ba), named project-film-aravind-r. Do not merge or rebase origin/main. Commit only the project-film work, push to my fork, and don't open the PR until I say so.

Before Phase 5, also:
- SHA-256 of the 9 unchanged clips vs the pre-revoice backup; they must match.
- Speech-to-text on the full master, not just changed beats; show me any line that differs from the script.
- Confirm the B15 checklist wording verbatim once more.
- Full gate table re-run on the new master.

Then stop. I'll watch it with and without sound before approving.
````

### 4. The positioning revision: feedback on the review cut (2026-11-23, 16:57 EST)

````text
Feedback on the review cut. Revise, re-gate, stop for review. Hard stop stays 22:29 ET.

POSITIONING (governs every change below)
Readback is application-agnostic. It is for any PM who writes acceptance criteria that an AI judge will grade a feature against. It checks whether the judges read each criterion the way the PM meant it. The meeting-recap feature on AMI is only the test bench I use to prove that. It is not the product and not part of the product. No line or frame may imply otherwise.

P0 — structure and message
1. Remove the four-part section bar from every frame. Add four 1.5 s chapter cards at the part boundaries (large numeral + title), replacing the near-empty frames at ~1:33 and ~3:00.

2. Executive summary: application-agnostic, consequence first, no meeting recap anywhere in it.
   - Hook (0–10 s): every AI feature ships against acceptance criteria a PM wrote, and AI judges now grade the feature against them. When a judge reads a criterion differently than the PM meant it, the eval passes and the wrong behaviour ships.
   - Show breadth visually: 3 quick constructed vignettes from different kinds of AI features (e.g. a support-reply bot, a document summariser, a search answer). Each has one plausible ambiguous criterion and a judge marking it pass. Label them as illustrations. Keep them brief and visual. Do not narrate each one.
   - The cost, stated generally: teams act on wrong output, users lose trust and the feature quietly dies. Because evals are becoming the launch gate for AI features, a misread criterion ships wrong behaviour at scale with a passing score attached. No invented stats or incidents.
   - Readback in one or two lines: it finds the criterion the judges read differently and asks the PM what they meant, before anyone trusts the score.
   - Vision: Readback is module 1 of a PM copilot for what PMs write for AI (criteria, system prompts, PRDs). Mark it as vision.
   - End the part with one disclosure line: Readback is planned; nothing has run yet.
   - The clause chip stays the hero object. In this part it is a generic "criterion" chip, not C4. It becomes C4 only when the test case begins in Methods.

3. Introduction: keep the prior-work beats as verified (scoped to "the tools I checked"). Restate why anybody should care in application-agnostic terms.

4. Methods opens by introducing the test bench as a test bench, in one beat:
   - To test Readback, I need one real AI feature with public data and human ground truth. I chose a meeting-recap feature on the AMI Meeting Corpus, because AMI ships human-written decision lists.
   - On screen: an explicit "test case, not the product" tag. Every later frame showing AMI data, recaps, the recap prompt or rubric-v0 carries a small "test case" corner tag alongside its existing source label.
   - Optional, if the time fits: a one-line closing beat that the same steps run on any feature's criteria.
   - Real evidence: search the 10 real recaps in case-study/outputs/feature-run/ against AMI's DECISIONS lists for a case where an open question or discussion was reported as a decision. If one exists, show it in Methods or Evaluation as a real example of the failure Readback targets, labelled real with source and date. Do not use it as the film's hook; the hook stays application-agnostic.

5. Terminology. Introduce "acceptance criteria" first. Define rubric once: "for an AI feature, those criteria become a rubric: the checklist an AI judge grades the output against." Then use rubric. Rewrite C4's displayed text into plain English (e.g. "Don't report open questions as decisions") wherever it appears in the test case, and update CLAIMS.md so the film and repo agree.

6. Labels. On concept diagrams, replace the full-sentence CONSTRUCTED/PLANNED captions with a small corner tag ("illustration", "planned") at reduced opacity. Keep full source+date labels on real evidence. Every item must still be tagged; the label audit stays a gate.

7. Add a ~10 s close after the final scorecard: what a pass would let a PM trust for any AI feature, then the vision line, then the end card.

P1 — production
8. Tighten inter-beat gaps from ~1.15 s to 0.4–0.6 s and vary them; use the time freed for the new narration. Runtime stays ≤ 4:00.
9. Methods and Evaluation: scale content ~1.3–1.4× and recenter; no lower-right dead zones; type floor ~34 px at 1080p.
10. 1:51–1:57: give the real transcript line and the real recap output a hero-size beat.
11. 2:48: regroup the resources checklist into three columns: have / account, not wired / planned. Wording stays as verified.
12. Frame 0 must be a strong poster frame, not the empty rubric box. Move the "read by a synthetic voice" credit off the 0:09 frame and onto the end card.
13. End card: Readback, a one-line application-agnostic value proposition (along the lines of "check that AI judges read your acceptance criteria the way you meant them"), credit line. Replace the tiny centered text.

NEW GATE: positioning audit
- Quote every narration line and on-screen string that mentions meetings, recaps, AMI or C4. Each must sit in Methods or Evaluation and be framed as the test case.
- The executive summary must contain zero meeting-recap references.
- A viewer who watches only 0:00–1:00 must come away believing Readback is for any AI feature's acceptance criteria. Quote the lines that establish that.
- Add the results to GATES.md.

Process
- Show me the new executive summary, the Methods test-bench beat and the closing narration as plain text, plus their CLAIMS.md rows, BEFORE voicing. Stop and wait for my OK.
- After my OK: voice only the changed beats, re-run every gate (including the positioning audit) on the new master, run speech-to-text on the full master, update GATES.md, SHOTLIST.md, FACTCHECK.md and CLAIMS.md, and log the changes in FRICTIONAL.md.
- Stop with the new review cut and a contact sheet. No commits until I approve.
````

### 5. The final fix pass (2026-11-23, 20:47 EST)

````text
Final fix pass. Time-box: done, gated and pushed by 22:45 ET, or stop and keep 6aadb5a.

1. B15 resources checklist: add "compute: this Mac" under "have". Add "my human labels: I mark the 86 decisions" under "planned", beside the open-weight model. Wording must stay verified as of today.
2. B01: change "Every AI feature ships against acceptance criteria a PM wrote." to "AI features ship against acceptance criteria a PM wrote."
   B02: change "And because evals are becoming the launch gate for AI features, a misread criterion..." to "And where an eval is the launch gate, a misread criterion ships wrong behaviour at scale, with a passing score attached."
   Update CLAIMS N01 and N05 to match; N05 becomes a conditional POSITION with no trend claim.
3. If "evals" in B02 needs it, respell it for the voice the same way as "Reed-back". Re-voice B01 and B02 only.
4. 1:21: change "names the clause behind a disagreement" to "names the criterion behind a disagreement".
5. Re-render the changed scenes, re-run every gate (including positioning, label and numbers audits, plus speech-to-text on the full master), and update GATES.md, FACTCHECK.md, CLAIMS.md, SHOTLIST.md.
6. Commit on project-film-aravind-r with no trailers, verify with git log -1 --format=%B, and push to my fork. Don't open the PR.

Leave the FRICTIONAL judgment-call TODOs and the SOURCES chat line for me. Stop and report the gate table and the new SHA.
````

### 6. The paperwork pass (2026-11-23, 22:11 EST)

````text
Final paperwork pass, plus one conditional scene fix. Time-box: everything committed and pushed by 23:20 ET. Do the paperwork (part 2) first, then part 1 only if time allows.

PART 1 — B15 Ollama line (conditional; skip it if it can't be gated and pushed by 23:10 ET)
- Verify first: run `ollama --version` and `ls /Applications | grep -i ollama`. I installed Ollama 0.40.17 with Homebrew (brew install --cask ollama-app), and it's running. If the check doesn't confirm that, stop and tell me; don't change B15.
- If it confirms: in B15's "planned" column, change "local open-weight model · Ollama not installed" to "local open-weight model · Ollama installed, judge not wired". Narration unchanged, so no re-voicing. Re-render B15 and B16, rebuild the master, re-run every gate (freeze, black, dead air, loudness, runtime, ground colour, F, factcheck, L, A, W, B, V, T, bookends, overlap, positioning, labels/numbers), and update GATES.md, FACTCHECK.md, CLAIMS.md and SHOTLIST.md.
- If you skip Part 1, record in FRICTIONAL (part 2, entry A) that the film's B15 line reflects the 15:50 check and Ollama was installed afterwards.

PART 2 — FRICTIONAL.md and SOURCES.md
My entries go in word for word as written below. Don't reword them.

FRICTIONAL.md

A. Replace the "Judgment calls (TODO, Aravind)" block in the positioning-revision entry with this new entry:

## 2026-11-23 — Project film, my judgment calls (Aravind, my words)
1. Film subject: Readback is the final project, so that's why the video was created for that.
2. Application-agnostic positioning: I didn't want people to mistake that Readback is applicable just for a meeting note taker application. So to emphasize that, I positioned it for any AI feature's acceptance criteria and kept the AMI meeting-recap feature as the test bench only.
3. PM vocabulary first: PM vocabulary would make the project easily relatable for PMs, who are the target audience for the project. I didn't want to make it sound too technical. I believe if you really understand something, or if you want people to understand your concepts, it's important to share it in a simpler language, which makes it relatable and understandable. I focussed on that aspect.
4. Cutting the section bar and full-sentence labels: I made sure only relevant and necessary information was kept on every page.
5. Consequences before mechanism: Before jumping into how it's built, it's very important to communicate the relevance, or the why, of the project. That's why I decided to focus on that first before getting into the solutioning and mechanism.
6. ES2010b as the real example: Using a real example from the test data was the right approach, rather than a synthetic one.
7. Softening the two flagged claims in the final pass: "Every AI feature" overgeneralised and the "launch gate" trend had no source in the repo. I didn't want unverifiable claims in the opening, which gets the most scrutiny, in a course that grades fact-checking.
8. Skipping P1 item 9 and B15's tight spacing: The video was looking good without that, and I didn't want to spend time on unnecessary fluff.
9. Listening checks: While listening to an earlier cut, I found the discrepancies and decided to fix them. The mispronunciations flagged on the first review cut (B13's "Claude"/"clause" line and "Readback") were reworded and re-voiced. The speech-to-text slips logged on the final cut were left as logged.

Resources: I hold Anthropic and OpenAI API credits from other projects. I'll create project-specific keys at implementation time, which is why the film shows them as "account, not yet wired". OpenAI is the second provider. Ollama: Claude Code's checks at 05:19 and 15:50 EST found it not installed. I then installed Ollama 0.40.17 with Homebrew (brew install --cask ollama-app), and it's running. [Write the outcome of Part 1 here: either the B15 line updated and re-gated, with the new master SHA, or the B15 line left as it was at the 15:50 check.]

B. Add this entry:

## 2026-11-23 — Project film: what Claude (chat) contributed (Aravind)
I used Claude.ai chat in my "Prompt Engineering & Agentic AI" project alongside Claude Code. It:
- recommended Readback as the film's subject over the job-search agent, mapped to the four-part brief;
- drafted the Claude Code prompt "Readback project film (four-part brief)" from my request;
- reviewed Claude Code's Phase 4 report and flagged honesty risks before Phase 5: B15 claiming resources not set up, human labels reading as AMI's, prior work not scoped to the tools I checked, the B13 "Claude"/"clause" adjacency, the Readback pronunciation, and the merged PR #18; it recommended the new branch from 2cad8ba;
- reviewed the first review cut and the revised cut frame by frame, from timestamped contact sheets plus ffmpeg freeze and silence detection, and listed the production issues by timestamp: the empty poster frame, the 0:09 credit, uniform ~1.15 s gaps, small type and dead zones in Methods and Evaluation, near-empty boundary frames, the small evidence beats, the B15 checklist, the end card;
- turned my feedback (removing the section bar, rubric vocabulary, cutting the clutter labels, consequences and long-term impact, application-agnostic positioning) into the P0/P1 revision prompts, and proposed the positioning-audit gate;
- on the revised cut, caught the missing compute line and the two unsourced opening claims, and drafted the final fix-pass prompt;
- listed what FRICTIONAL.md and SOURCES.md still needed, and drafted this prompt from my answers.
The decisions are mine. Claude chat never touched the repo; everything it drafted reached Claude Code through me.

C. In the positioning-revision entry, replace "My feedback on the review cut (Aravind):" and its bullets with:
- My feedback on the review cut (Aravind): remove the four-part section bar; rubric isn't PM vocabulary, so define it or use a PM term; remove the "CONSTRUCTED illustration · no judge has run yet" clutter from the opening; lead with why Readback matters and its long-term impact (the real consequence of a wrong ship decision) rather than the mechanism; position Readback as application-agnostic, with the AMI meeting-recap feature as the test case only.
- Claude (chat) turned that into the P0/P1 list, added the frame-by-frame production items and proposed the positioning-audit gate. Claude Code made the changes.

D. Factual fixes:
- Phase 0 entry, "Resources for Methods (Aravind)": make the list read "claude -p on my subscription; Anthropic API credits and OpenAI API credits (accounts held, project keys not yet created); local open-weight models via Ollama (installed later on 2026-11-23, after Claude Code's checks; see my judgment-calls entry)".
- Header: change the title to "FRICTIONAL — Readback: pitch film and project film". Add "Project film (2026-11-23): Claude Code 2.1.323."
- Final fix pass entry: add "Committed as d3b87e9 on project-film-aravind-r and pushed to my fork; master SHA-256 4d790803…".
- Remove the stale bullet about keeping "Every AI feature…" and "evals are becoming the launch gate" as written; entry A replaces it.

SOURCES.md
- "Made by me", the four-part brief line becomes: "The four-part brief: requested and directed by me; the Claude Code prompt 'Readback project film (four-part brief)' was drafted in Claude chat from my request, and I sent it."
- "Keeping the flagged lines as written" becomes: "Kept the flagged lines in the drafts; softened both in the final fix pass."
- "Judgment calls: TODO (Aravind)" becomes: "Judgment calls: see FRICTIONAL.md, 2026-11-23, 'my judgment calls'."
- Replace the "Claude (chat): TODO" line with: "Claude (chat), Claude.ai in my project, at my direction: the film-subject recommendation; the four-part Claude Code prompt; reviews of each Claude Code report, with the honesty flags; frame-by-frame reviews of both review cuts from contact sheets and ffmpeg freeze/silence detection; the P0/P1 revision prompts, the positioning-audit gate and the final fix-pass prompt; the paperwork gap list and this prompt. It made no changes to the repo. Details: FRICTIONAL.md, 2026-11-23."
- Under the project film's "Contributed by Claude (Claude Code, Opus 5.5)", add: "Claude Code 2.1.323 for the project film."
- Opening line: "Pitch-film sections are as of 2026-10-14; the project-film section is as of 2026-11-23."
- Components table: add a row, "Claude Code | 2.1.323 | Anthropic consumer terms | Project film build (2026-11-23)".
- Project-film section, add "Final file: film/project/aravind-r-readback-project-film.mp4, 3:56.8, SHA-256 4d790803…, commit d3b87e9". If Part 1 ran, use the new SHA, duration and commit instead.
- Project-film "Used" list: add "Ollama 0.40.17 (Homebrew cask ollama-app), installed 2026-11-23; not yet used by any judge".

PART 3 — commit and push
- Commit with no trailers, verify with git log -1 --format=%B, push to my fork. No PR.
- Report the commit SHA, the final master SHA, and whether Part 1 ran.
- After I open the PR, add a FRICTIONAL entry with its URL ("PR opened by me"), commit, and push again.
````

### 7. The PR #54 entry (2026-11-23, 23:02 EST)

````text
PR opened by me: https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/pull/54

Add a FRICTIONAL entry:

## 2026-11-23 — Project film PR #54 opened (Aravind)
- I opened PR #54 myself: aravindravi7:project-film-aravind-r into nikbearbrown:main.
- Head at opening: 8fb0730. Final master SHA-256 535fe61b…, 3:56.8, built in commit 8424a49.
- Record the commit count, file count and opening time from `gh pr view 54` or the compare against 2cad8ba. Don't guess them.
- CI: record what the PR shows. If it's waiting on maintainer approval for a fork workflow, say so, and run scripts/validate_course.py locally and record the result.
- This entry goes in its own commit; PR #54 picks it up automatically.

Commit with no trailers, verify with git log -1 --format=%B, push to my fork. Then confirm that PR #54's head matches the new commit and that every changed file is under fall-2026/aravind-r/final-project-film/.
````

### 8. The Canvas zip (2026-11-23, 23:21 and 23:23 EST)

Two short prompts, sent one after the other.

````text
share the zip url here, so I can submit

share the zip file here for download
````

### 9. This documentation fix pass and appendix (2026-11-23, 23:30 EST)

````text
Documentation fix pass for the project film, plus an appendix. Stop points are real. Nothing gets committed until I approve Part 3's drafts.

PART 1 — factual fixes (no review needed)
1. README.md
   - Title: "Readback — Final Project Films".
   - New top section "Project film (four-part brief, 2026-11-23)": file film/project/aravind-r-readback-project-film.mp4, 3:56.8, 1920×1080, 24 fps, SHA-256 535fe61b3ba67484f88d8beb9859b9d3de5c010748f4765a57457b420aba6752, PR https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/pull/54. One paragraph on what it is (the four parts; Readback for any AI feature's acceptance criteria, with the AMI meeting-recap feature as the test case only; everything Readback does is planned).
   - A "What's in film/project/" table covering: the film, beat_sheet.json, make_sheet.py, scenes.py, add_holds.py, normalize_audio.py, the check scripts (qc_film.py, overlap_check.py, strings_dump.py, positioning_check.py, stt_check.py, make_storyboard.py), CLAIMS.md, EVAL-PLAN.md, DESIGN.md, FACTCHECK.md, SHOTLIST.md, PROMPTS.md, TYPECHECK.md, gates/ (GATES.md as the summary; review-cut-1/ as history), storyboard.png, style-frames/, and the appendix from Part 3.
   - "Rebuild the project film": the exact commands you actually ran, in order: toolkit checkout at cd4bf20, applying toolkit-patches/ClaudeTitleOutro-handle-hideMascot-polarity-bg-tagline.patch, make_sheet.py, Kokoro, add_holds.py, align.py, art run, normalize_audio.py, art final --audio, then the checks. Use the real flags from your logs. Don't invent any.
   - Relabel the existing content "Pitch film (2026-10-14)" and keep it below, unchanged apart from the heading.
2. film/project/PROMPTS.md: replace "These are my prompts to Claude Code, in order." with "These are the prompts I sent to Claude Code, in order. The four-part prompt, the revision prompts and the final fix-pass prompts were drafted in Claude chat at my direction, from my feedback; I sent each one (see ../../SOURCES.md and FRICTIONAL.md, 2026-11-23)." Then add a section "Prompt texts" holding the full text of each prompt I sent this session, copied verbatim from this conversation, in order: the four-part prompt, the pre-Phase-5 requests, the item-7 choice and checks, the positioning revision, the final fix pass, the paperwork pass, the PR-entry prompt, the Canvas-zip prompt and this prompt. Prompts only, no replies or transcripts, the same rule as the pitch film's BUILD-PROMPT.md.
3. film/project/DESIGN.md: every "Ollama not installed" or "Ollama isn't installed" line becomes "installed 2026-11-23 (0.40.17), no model pulled, judge not wired", and the line-118 sentence matches the 22:11 EST check.
4. SOURCES.md title: "# SOURCES — Readback pitch film and project film".
5. FRICTIONAL.md
   - Header machine line: add "Project film: macOS Darwin 27.2."
   - Judgment call #9, replace it with exactly: "9. Listening checks: Whisper flagged B13's "Claude"/"clause" line and "Readback" on the first review cut; I listened, confirmed them and approved rewording and re-voicing. The speech-to-text slips logged on the final cut I left as logged."
   - Phase 5 entry, the line "The judgment-call entries, and anything drafted in Claude chat, are marked TODO for me to write.": append " (written later the same evening; see the entries at the end of this log)."
   - Ordering: move the two entries "Project film, my judgment calls (Aravind, my words)" and "Project film: what Claude (chat) contributed (Aravind)" to the end of the log, after the PR #54 entry, unchanged, with a one-line note under each heading: "Written 2026-11-23 evening, after the final fix pass; moved here so the log reads in order."
   - Don't change any other wording in my entries.
6. Grep the whole folder for any remaining "Ollama not installed", "Every AI feature", "becoming the launch gate", "TODO (Aravind)" or "pitch film" used to mean the project film. Fix live documents; leave dated history and review-cut-1/ as they are. Report what you changed and what you left, with reasons.

PART 2 — checks
- Re-run factcheck_check.py and positioning_check.py; both must still pass (no film files change).
- Confirm the film's SHA-256 is still 535fe61b…

PART 3 — appendix: film/project/APPENDIX-METHODS-EVAL.md (draft, STOP for my review)
Header: "PLANNED · drafted by Claude Code from the repo, reviewed by Aravind on 2026-11-23. Nothing here has run." Every number is either measured from the repo (cite the path) or marked as a plan setting. No invented results.
A. How Readback traces a disagreement to a criterion, step by step. Inputs: rubric clauses, judge verdicts per clause per recap, each judge's stated reason. Then: flag clauses where judges split or a judge diverges from my labels; group the split cases; extract the reading each judge applied; write the clarifying question to the PM as a choice between those readings, never a rewrite; the PM's answer revises the clause; re-run. Use ES2010b as the worked example (real transcript and recap lines, already sourced).
B. Cost and compute. Token counts measured from case-study/data/sample transcripts and the 10 recaps, times 3 judges × 5 clauses, plus the re-runs in check 3. Dollar cost only if you can fetch the current official Anthropic and OpenAI pricing pages and cite them with the date; otherwise give tokens only and say pricing wasn't checked. The local judge is a cost of zero on this Mac; note its runtime is unmeasured.
C. Statistical limits, stated plainly: kappa on 10 recaps per clause is unstable; give the 95% interval width you'd expect for n=10 versus n=86, computed, not guessed. Explain why check 2 uses the 86 decision items and that per-clause judge-vs-judge results are descriptive only. Name the held-out split's size from EVAL-PLAN.md and its limit.
D. Generality. The film claims Readback is for any AI feature, but every check runs on one test case. State this as a known gap and give the plan: a second test feature with a different output type, chosen from a public dataset with human ground truth. Propose two candidates with their licence and source URL, only ones you can verify by fetching the page, and mark the choice as mine to make.
E. Link the appendix from README.md, EVAL-PLAN.md and CLAIMS.md (one line each).
STOP: show me the full appendix. I approve or edit before anything is committed.

PART 4 — commit, push, zip (after my OK)
- One commit, no trailers, verified with git log -1 --format=%B; push to my fork. Confirm PR #54's head updates and every changed file is under fall-2026/aravind-r/final-project-film/.
- Add one FRICTIONAL line to this entry first: "Documentation fix pass and appendix (Aravind's requests; Claude Code made the changes; appendix reviewed by me)."
- Rebuild ~/Desktop/Ravi_Aravind_INFO7375_ProjectFilm.zip from git ls-files at the new HEAD, diff the listing, and print the zip path, size, file count, full commit hash and the film SHA.

PART 5 — optional, only after Part 4 is pushed: B15 spacing
- Re-lay out B15 so "this Mac" under compute clears the footer by at least the gap the other rows use, "local open-weight model" stays on one line (shrink the column's type a step only if it stays at or above the current smallest size in the film), and the "have" column's row spacing is even. No wording changes.
- Re-render B15 and B16, rebuild the master, and re-run every gate. If any gate fails or a value changes other than the SHA, discard Part 5 and keep 535fe61b.
- If it passes: update GATES, SHOTLIST, FACTCHECK, the README SHA, SOURCES "Final file" and a FRICTIONAL line; then commit, push, rebuild the zip and print as in Part 4.
````
