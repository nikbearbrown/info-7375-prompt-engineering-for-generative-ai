# CLAIMS — Readback project film (four-part brief) · approved 2026-11-23, revised the same evening for positioning

**Rule:** every narration sentence and every on-screen number maps to an evidence path in this repo, or is marked **PLANNED**. Anything that maps to neither is cut.

**Paths** are relative to `fall-2026/aravind-r/final-project-film/`.

**Pronunciation:** in `beat_sheet.json` (the Kokoro input), Readback is spelled "Reed-back" so it is said "reed-back". The sentences below are the script as meant; on screen it is always "Readback".

**Positioning (my note, 2026-11-23):** Readback is application-agnostic. It is for any PM who writes acceptance criteria that an AI judge will grade a feature against, and it checks whether the judges read each criterion the way the PM meant it. The meeting-recap feature on AMI is only the test bench used to prove that; it is not the product. In the film, meetings, recaps, AMI and C4 appear only in Methods and Evaluation, under a "test case" tag (gate: `gates/positioning-audit.md`).

**Status values:**
- **EVIDENCE:** the file or files that show it.
- **POSITION:** my stated design position, recorded in `PROJECT-BRIEF.md` or my positioning note; an argument, not a measured fact.
- **PLANNED:** future work, defined in `film/project/EVAL-PLAN.md`; said with "will", or in the context of the plan.
- **VISION:** where Readback goes after this project (later modules); marked "vision" on screen.
- **NO CLAIM:** a question or transition.

## Narration (55 sentences, in film order; IDs match `beat_sheet.json` `claim_ids`)

| ID | Beat | Sentence | Status | Evidence / note |
|---|---|---|---|---|
| N01 | B01 | AI features ship against acceptance criteria a PM wrote. | POSITION | Framing; positioning note (Aravind, 2026-11-23, `FRICTIONAL.md`); `PROJECT-BRIEF.md` ("A PM who owns an AI feature uses an eval rubric to decide whether the feature works"). A general statement about AI features, not a count. Reworded 2026-11-23 (final fix pass) from "Every AI feature ships…", which overstated it |
| N02 | B01 | Those criteria become a rubric: the checklist an AI judge grades the output against. | POSITION | Definition of the term. `PROJECT-BRIEF.md` ("eval rubric"); judges grading against criteria: `FRICTIONAL.md`, Maxim AI and orq.ai checks (2026-10-14) |
| N03 | B01 | When a judge reads a criterion differently than the PM meant it, the eval passes, and the wrong behaviour ships. | POSITION | Conditional. `PROJECT-BRIEF.md` ("If the judge reads a clause differently than the PM meant, the scores look fine and the ship decision is wrong"). A hypothetical, not a reported case |
| N04 | B02 | Then teams act on wrong output, users lose trust, and the feature quietly dies. | POSITION | Argued consequence; positioning note (Aravind, 2026-11-23, `FRICTIONAL.md`). No statistics, no incidents |
| N05 | B02 | And where an eval is the launch gate, a misread criterion ships wrong behaviour at scale, with a passing score attached. | POSITION (conditional) | Conditional: it holds where an eval gates the launch; no claim about how many teams do this, and no trend claim. Positioning note (Aravind, 2026-11-23, `FRICTIONAL.md`). Reworded 2026-11-23 (final fix pass) from "And because evals are becoming the launch gate for AI features…", a trend claim with no source in this repo |
| N06 | B03 | Readback will find the criterion the judges read differently, and ask the PM what they meant, before anyone trusts the score. | PLANNED | `PROJECT-BRIEF.md` Q1, Q5; `film/project/EVAL-PLAN.md` |
| N07 | B03 | It's module one of a bigger vision: a copilot for what PMs write for AI. | VISION | `PROJECT-BRIEF.md`: the rubric module first, "PRDs and system prompts are later modules"; "copilot" from my positioning note (Aravind, 2026-11-23, `FRICTIONAL.md`). On screen: corner tag "vision"; tiles "criteria · module 1 · Readback", "system prompts · later", "PRDs · later" |
| N08 | B03 | Readback is planned; nothing has run yet. | EVIDENCE | Status: `film/project/EVAL-PLAN.md`; no judge output, labels or Readback output exist in the repo (`case-study/outputs/` holds only the feature-run recaps; checked 2026-11-23) |
| N09 | B04 | What have others done? | NO CLAIM | question |
| N10 | B04 | Some tools already work on making AI judges more reliable. | EVIDENCE | `FRICTIONAL.md`, Maxim AI and orq.ai checks (2026-10-14) |
| N11 | B04 | Maxim AI runs several models as judges, compares their verdicts, and measures how often they agree with human labels. | EVIDENCE | `FRICTIONAL.md` (2026-10-14): "multiple LLMs as judges with compared assessments; judge–human agreement via percent agreement, Cohen's kappa, Krippendorff's alpha; human annotation" |
| N12 | B05 | Ork dot AI compares an evaluator with human labels, checks whether it answers the same way twice, and then proposes a rewritten evaluator prompt. | EVIDENCE | `FRICTIONAL.md` (2026-10-14): "compares a pass/fail evaluator against human labels, measures self-consistency by re-running, then proposes a rewritten evaluator prompt". Spoken spelling for Kokoro; on screen it reads "orq.ai" |
| N13 | B06 | For specs rather than rubrics, GitHub's Spec Kit has an optional clarify step that resolves ambiguity before planning starts. | EVIDENCE | `FRICTIONAL.md` (2026-10-14): "an optional /speckit.clarify step that resolves ambiguity in a spec before planning. Applies to specs, not eval rubrics." |
| N14 | B07 | So the tools I checked give you an agreement score, a rewritten prompt, or a clearer spec. | EVIDENCE | Summary of N12–N14, same entries; scoped to the three tools I checked |
| N15 | B07 | What I couldn't find in their documentation, read on October fourteenth, is any of them naming the rubric clause behind a judge disagreement. | EVIDENCE | `FRICTIONAL.md` (2026-10-14) for all three; "any of them" = the three tools I checked. Braintrust and Confident AI aren't named (not checked) |
| N16 | B08 | That gap is why Readback matters on any AI feature. | POSITION | `PROJECT-BRIEF.md` Q2; positioning note (Aravind, 2026-11-23, `FRICTIONAL.md`) |
| N17 | B08 | A score tells you something is wrong. | POSITION | argument; `PROJECT-BRIEF.md` Q2 |
| N18 | B08 | The criterion tells you what to fix. | POSITION | argument; `PROJECT-BRIEF.md` Q2 (was "A clause tells you what to fix") |
| N19 | B08 | And a question, instead of a rewrite, keeps the fix a product decision. | POSITION | `PROJECT-BRIEF.md` Q2, Q5 |
| N20 | B09 | To test Readback, I need one real AI feature with public data and human ground truth. | POSITION | The method's requirement: `film/project/EVAL-PLAN.md` (labels checked against AMI's DECISIONS); `PROJECT-BRIEF.md` ("a meeting-recap case study") |
| N21 | B09 | I chose a meeting-recap feature on the AMI Meeting Corpus, because AMI ships human-written decision lists. | EVIDENCE | All 10 `case-study/data/sample/*/summary.txt` are headed "AMI abstractive summary (human-written)" and have a DECISIONS section (checked 2026-11-23); `case-study/data/sample/README.md`; `SOURCES.md` (CC BY 4.0, downloaded 2026-10-14) |
| N22 | B09 | It's my test case, not the product. | POSITION | positioning note (Aravind, 2026-11-23, `FRICTIONAL.md`); `PROJECT-BRIEF.md` calls it "a meeting-recap case study". On screen: "test case, not the product", then the corner tag "test case" on every Methods and Evaluation frame |
| N23 | B09 | I use ten of its meetings, which hold eighty-six decisions. | EVIDENCE | `case-study/data/sample/selection.csv`: 10 selected; sum of `decisions` over them = 86 (rechecked 2026-11-23) |
| N24 | B10 | The feature under test is a meeting recap: my own prompt, running on Claude. | EVIDENCE | `case-study/constructed/recap-system-prompt.md` (CONSTRUCTED); `case-study/run_feature.py` |
| N25 | B10 | I ran it on every meeting on October fourteenth, so ten real recaps already exist. | EVIDENCE | `case-study/outputs/feature-run/*.json`: 10 files, `run_started_utc` 2026-10-14, `claude-opus-5-5` |
| N26 | B11 | Next, a constructed rubric with five clauses, like 'every decision appears' and 'don't report open questions as decisions'. | EVIDENCE | `case-study/constructed/rubric-v0.md` (CONSTRUCTED): C1 and C4 in plain English. C4 there reads "Unresolved stays unresolved. Disagreements and open questions the team didn't settle are reported as unresolved, not as decisions." The plain version keeps open questions only (approved 2026-11-23). On screen: chip "C4 · Don't report open questions as decisions" |
| N27 | B11 | The decisions clause is anchored to AMI's list, so there's a right answer to check against. | EVIDENCE | `rubric-v0.md` C1 (reference: the meeting's `summary.txt` DECISIONS) |
| N28 | B12 | Before any judge runs, I'll mark which of AMI's decisions each recap covers. | PLANNED | `EVAL-PLAN.md` "Human labels", proposal A **(decided 2026-11-23)** |
| N29 | B12 | Those are the human labels, and I'll commit them first, so the history proves the order. | PLANNED | `EVAL-PLAN.md` |
| N30 | B13 | Then three judges score every recap: Claude, a second provider's model, and a local open-weight model. | PLANNED | `EVAL-PLAN.md` "Judges (3)". "each one going clause by clause" cut for time (2026-11-23); "Claude" and "clause" are never adjacent |
| N31 | B13 | I'll measure how often they agree with each other, and with my human labels on the decisions clause. | PLANNED | `EVAL-PLAN.md` "Agreement measures"; the human labels are my planned marks (proposal A) |
| N32 | B14 | Where the judges split, Readback will trace the split to its clause and ask the PM. | PLANNED | `PROJECT-BRIEF.md` Q1; `EVAL-PLAN.md` |
| N33 | B14 | In one real recap, two quick yeses became a decision. | EVIDENCE | ES2010b. Transcript `case-study/data/sample/ES2010b/transcript.txt`: [00:20:44] ID "Do we want this thing to be able to be found easily?", [00:20:49] PM "I think so.", [00:20:52] ME "Sure, yeah."; recap `case-study/outputs/feature-run/ES2010b.json` (claude-opus-5-5, run 2026-10-14) lists "The remote should be easy to find if lost [00:20:52]" under Decisions; AMI's DECISIONS (`ES2010b/summary.txt`): "The group will consider including speech recognition and a locator function in the functional design." All asserted in `scenes.py`. **Flag:** "two quick yeses" is my description of "I think so" and "Sure, yeah" (approved 2026-11-23). Shown as a line where C4 is hard to call, not as a recap error |
| N34 | B14 | Does a quick yes count? | PLANNED | Illustration of the kind of question Readback will ask about C4; not Readback output (nothing has run) |
| N35 | B14 | The PM answers, and revises the clause. | PLANNED | `PROJECT-BRIEF.md` Q5; `EVAL-PLAN.md` check 3 |
| N36 | B15 | Do I have what I need? | NO CLAIM | question |
| N37 | B15 | The data and the ten recaps are in my repository, and Claude runs here on my subscription. | EVIDENCE | `case-study/data/sample/` (10 meetings); `case-study/outputs/feature-run/` (10 recaps); `claude` CLI 2.1.323 installed on this Mac (checked 2026-11-23), the same CLI that produced the recaps on 2026-10-14 |
| N38 | B15 | My API credits and a second provider account aren't wired in yet. | EVIDENCE | The accounts are mine (stated by me, `FRICTIONAL.md` 2026-11-23 Phase 0); not wired in: no API key in this shell's environment (checked 2026-11-23). On screen: "account, not yet wired" |
| N39 | B15 | Still to come: the local model, and my human labels. | PLANNED | Ollama 0.40.17 installed later on 2026-11-23 (checked 22:11 EST: `ollama --version`, `/Applications/Ollama.app`, Homebrew cask `ollama-app`, `ollama serve` running; `ollama list` shows no model, and no judge code is in the repo), so the local model is not yet a judge; my human labels are planned (`EVAL-PLAN.md`, proposal A) and no labels file exists |
| N40 | B16 | Three checks on the test case, each with a pass and a fail. | PLANNED | `EVAL-PLAN.md` checks 1–3. "How will I know it worked?" cut for time (2026-11-23) |
| N41 | B16 | First, a planted ambiguity: I'll make one clause deliberately vague, so I know the right answer in advance. | PLANNED | `EVAL-PLAN.md` check 1 |
| N42 | B16 | It passes if Readback blames the clause I planted. | PLANNED | `EVAL-PLAN.md` check 1 (pass) |
| N43 | B16 | It fails if it blames another clause, or noise. | PLANNED | `EVAL-PLAN.md` check 1 (fail) |
| N44 | B17 | Second, agreement on the decisions clause: each judge against my human labels on all eighty-six decisions, measured with Cohen's kappa. | PLANNED | `EVAL-PLAN.md` check 2 (my planned marks, proposal A); 86 from `selection.csv` |
| N45 | B17 | It passes at point six or higher, a bar I'll fix before any run. | PLANNED | `EVAL-PLAN.md` check 2, κ ≥ 0.6 **(decided 2026-11-23)** |
| N46 | B17 | Below that, it fails. | PLANNED | `EVAL-PLAN.md` check 2 (fail). Was "Below that, the judges can't be trusted on this clause." |
| N47 | B18 | Third, before and after. | PLANNED | `EVAL-PLAN.md` check 3 |
| N48 | B18 | The PM revises the flagged clause, and I re-measure judge agreement on meetings held out from the revision. | PLANNED | `EVAL-PLAN.md` check 3 (held-out split **(decided 2026-11-23)**) |
| N49 | B18 | If agreement doesn't rise, Readback didn't help, and I'll say so. | PLANNED | `EVAL-PLAN.md` check 3 (fail) |
| N50 | B19 | None of these checks has run yet, so every result is blank, and a failed check goes on the scorecard too. | EVIDENCE | No judge outputs, labels or agreement results exist in the repo (checked 2026-11-23); the reporting rule is `EVAL-PLAN.md` "Reporting" |
| N51 | B20 | If these checks pass, a PM could trust a passing score to mean what they meant. | PLANNED | Conditional: what the three checks test (`EVAL-PLAN.md`). Shown on one test case only, so the next line states the rest as a goal |
| N52 | B20 | That's the goal for any AI feature. | POSITION | positioning note (Aravind, 2026-11-23, `FRICTIONAL.md`) |
| N53 | B20 | And Readback is module one of a copilot for what PMs write for AI. | VISION | As N07. On screen: corner tag "vision" |
| N54 | BOUT | Readback. | EVIDENCE | `PROJECT-BRIEF.md` |
| N55 | BOUT | A project film by Aravind Ravi, read by a synthetic voice. | EVIDENCE | Author (`README.md`); voice: `film/project/beat_sheet.json` metadata (Kokoro `am_onyx`, synthesized locally). End card: "Aravind Ravi · INFO 7375" and "read by a synthetic voice" |

## On-screen numbers (every frame; checked on the contact sheets)

| ID | Number on screen | Where | Status | Source |
|---|---|---|---|---|
| O01 | 10 meetings | Methods (B09; B15 checklist) | EVIDENCE | `case-study/data/sample/selection.csv` (`selected == True`) |
| O02 | 86 decisions | Methods (B09, B12, B15), Evaluation (B17) | EVIDENCE | `selection.csv`: sum of `decisions` over the selected rows |
| O03 | Per-meeting DECISIONS: IS1004d 12, ES2006d 10, IS1009d 9, ES2008c / ES2010b / ES2011b / ES2013d / IS1003c / IS1005c 8, ES2007a 7 | Methods (B09) | EVIDENCE | `selection.csv` (`decisions` column) |
| O04 | Meeting lengths 20 min 21 s … 34 min 58 s | Methods (B09) | EVIDENCE | `selection.csv` `duration_s` (1221–2098 s). No longer spoken (cut for time) |
| O05 | 10 recaps | Methods (B10, B15) | EVIDENCE | `case-study/outputs/feature-run/*.json` (10 files) |
| O06 | 14 Oct 2026 | recap labels (B10, B14); prior-work footer (B04–B07) | EVIDENCE | `feature-run/*.json` `run_started_utc`; `FRICTIONAL.md` checks dated 2026-10-14 |
| O07 | `claude-opus-5-5` | recap labels (B10, B14) | EVIDENCE | `feature-run/*.json` `models_reported` |
| O08 | 5 clauses, C1–C5; C4 | rubric (B11), grid (B13), demos (B16, B18) | EVIDENCE | `case-study/constructed/rubric-v0.md` |
| O09 | CC BY 4.0 | data labels (B09–B11, B14) | EVIDENCE | `SOURCES.md`; `case-study/data/sample/README.md` |
| O10 | [00:17:52] | B10 (transcript and recap lines) | EVIDENCE | `ES2007a/transcript.txt`; `feature-run/ES2007a.json` |
| O11 | [00:20:44], [00:20:52] | B14 (the ES2010b example) | EVIDENCE | `ES2010b/transcript.txt`; `feature-run/ES2010b.json` |
| O12 | 3 judges | Methods (B13) | PLANNED | `film/project/EVAL-PLAN.md` |
| O13 | 3 checks; "check 1 · pass" … "check 3 · pass" | Evaluation (B16–B19), the close (B20, drawn as planned) | PLANNED | `EVAL-PLAN.md` |
| O14 | κ ≥ 0.6 / < 0.6 | Evaluation scorecard | PLANNED | `EVAL-PLAN.md` check 2 **(decided 2026-11-23)** |
| O15 | Results: "—" in every cell | Evaluation scorecard | PLANNED | not run; drawn as empty grey cells |
| O16 | CLI 2.1.323; 23 Nov 2026 | B15 checklist | EVIDENCE | `FRICTIONAL.md` 2026-11-23 Phase 0 (`claude --version`, rechecked 15:50 EST) |
| O17 | the chapter numerals 1–4 | chapter cards | NO CLAIM | the film's own structure |
| O18 | "module 1" | B03 vision tiles, B20 | VISION | `PROJECT-BRIEF.md` (the rubric module first; later modules) |

## On-screen wording that changed with the positioning revision

- **The hero chip.** In the executive summary and the introduction it is a generic "criterion" chip. From Methods on it is C4, written in plain English as "C4 · Don't report open questions as decisions" (rubric-v0.md's C4 is "Unresolved stays unresolved. Disagreements and open questions the team didn't settle are reported as unresolved, not as decisions."). The plain version drops "disagreements"; approved 2026-11-23.
- **The three vignettes** in B02 are CONSTRUCTED illustrations, tagged "illustration": a support-reply bot ("Resolve the issue" · "See Settings for refunds."), a document summariser ("Cover the key points" · "Both sides agree on price."), a search answer ("Cite a source" · "Source: a forum post."). Each judge marks "pass". None is a real product, output or incident.
- **Corner tags** replace the full-sentence CONSTRUCTED/PLANNED captions on concept diagrams: "illustration", "planned", "vision", "test case". Real evidence keeps its full source and date label. Constructed artefacts keep "CONSTRUCTED" (the prompt card in B10, rubric-v0.md in B11).
- **The value line**, "Check that AI judges read your acceptance criteria the way you meant them.", is on the poster frame (tagged "planned") and on the end card. It states what Readback is for, not a result.
- **The synthetic-voice credit** moved from the 0:09 frame to the end card and its spoken line.

## Cut or reworded while drafting (they mapped to nothing)

- **"Nobody can tell which clause caused it"** (the prompt's wording) became "it's hard to tell". "Nobody" can't be evidenced; the checked tools not naming the clause can.
- **"Nobody notices"** (B03) became "the wrong grading goes unnoticed" (2026-11-23), so no line makes a "nobody" claim.
- **"The compute is my laptop"** was cut from the narration. Phase 0 verified that the *film* pipeline runs on this Mac; no local judge model has been tested on it. The checklist shows exactly that: "compute · this Mac" is under "have" (final fix pass, 2026-11-23), and the local judge stays under "planned" as "local open-weight model · Ollama installed, judge not wired".
- **Braintrust and Confident AI** stay out. They were never checked (`FRICTIONAL.md`, 2026-10-14).
- **Present-tense descriptions of what Readback does** became "will". Readback doesn't exist yet.
- **"I'm Aravind Ravi, and this film is read by a synthetic voice"** (old B02) moved to the end: the end card and its spoken line now say "A project film by Aravind Ravi, read by a synthetic voice" (2026-11-23 positioning revision).
- **"Here's how I'll build it, in the order it runs"** (old B09) was replaced by the test-bench sentence ("To test Readback, I need one real AI feature…").
- **"twenty to thirty-five minutes long, where teams role-play a product design project"** was cut from the narration for time; the lengths stay on screen (O04).
- **"each one going clause by clause"** (B13) and **"How will I know it worked?"** (B16) were cut for time.
- **"did you mean this, or that?"** (B14) became the real ES2010b example and its question, "Does a quick yes count?".
- **"Below that, the judges can't be trusted on this clause"** (B17) became "Below that, it fails."
- **Final fix pass (2026-11-23, my requests):** B01's first line became "AI features ship against acceptance criteria a PM wrote." (was "Every AI feature ships…"); B02's became "And where an eval is the launch gate, a misread criterion ships wrong behaviour at scale, with a passing score attached." (was "And because evals are becoming the launch gate for AI features, …", a trend claim). On screen, B07's "names the clause behind a disagreement" became "names the criterion behind a disagreement", and B15's compute moved from "planned" ("this Mac · local judge planned") to "have" ("this Mac").
- **B15's Ollama line (2026-11-23, 22:11 EST check):** "planned · Ollama not installed" (true at the 05:19 and 15:50 EST checks) became "Ollama installed, judge not wired" after I installed Ollama 0.40.17. The narration is unchanged: the local model is still to come as a judge.
