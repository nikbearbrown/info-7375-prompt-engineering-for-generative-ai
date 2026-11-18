# How to prepare for the Fall 2026 exam

> **Draft, not signed off.** This guide summarises published studies on how people learn and prepare for tests. The sources are listed at the end, but the figures have not yet been checked against the original papers, and no study covers an exam exactly like this one. The plans are suggestions built on that research, not a proven schedule. Where your course glossary differs from the example terms below, **the glossary wins**: on a vocabulary exam, the course's definition is the answer.


The exam: fully on paper (no laptop, no phone; pen or pencil on the printed exam). Part A (50 points): five case questions, 10 points each: a scenario, an instruction given to an AI agent, and the agent's confident output with at least one real flaw; the student finds a real defect and gives a reason a grader can check, names it with the exact term, says what check would turn the claim into evidence, writes the correction to the agent, and explains it to a non-expert in plain words. Part B (50 points): ten multiple-answer questions, five statements each, each true or false on its own, 1 point per statement.

Each new case prints five tailored questions: defect/reason (3), concept (2), evidence check (2), correction (2), and plain consequence (1). Use short numbered answers. Any number of the five multiple-answer statements can be true, from zero to five.

Use [EXAM-GENERATOR-PROMPT.md](EXAM-GENERATOR-PROMPT.md) in a Claude Project for new-format practice. The existing papers/keys below are historical 7+6 exercises, not the current-format template. Final topic coverage and duration remain subject to the instructor announcement.

## Two ways to use each practice exam
Each practice exam has two files.
| Option | File | Use it when |
|---|---|---|
| The exam | `practice-exam-NN.md` | **This is the one to practise from.** You answer cold, on paper, in 100 minutes, with no answers in sight. |
| The key, with the questions shown | `practice-exam-NN-KEY.md` | You have finished the exam and now mark yourself. Every case and every multiple-answer question is printed in full with its answer right under it, so you can read them together. |

Every entry in the key ends with a **Covered in:** line pointing to the chapter and section of this course that teaches it. If the course does not teach an idea, the line says so.

## 1. What the evidence says

| Technique | What the research found | Strength | What it means for this exam |
|---|---|---|---|
| Practice testing (self-quizzing) | One of only two techniques rated "high utility" in a major review of ten study techniques. Works best with corrective feedback. Rereading, highlighting and summarizing were rated low. [1] | Strong | Do practice exams and cards. Stop rereading notes. Check against the key right after each attempt. |
| Spaced practice | The other "high utility" technique [1]. For a test one week away, the best gap between study sessions was about 20-40% of that week; a gap that is too short hurts more than one that is too long. [2] | Strong (mostly facts, less tested on case skills) | Revisit each topic every 3-5 days across 14 days (the guide's extrapolation from [2]). Cramming throws this away. |
| Transfer from practice tests | Practice testing transfers to new questions (average d about 0.40), mainly when practice and exam answers overlap, practice involves elaboration, and you got most practice items right. Transfer is weakest when cue and answer are swapped (practise term -> definition, get tested definition -> term). [3] | Moderate | Practise in the exam's own format. Drill terms in both directions. Get accurate first, then fast. |
| Interleaving (mixing problem types) | Moderate average benefit (g = 0.42), larger when the categories look alike. For word-based materials, blocking actually won (g = -0.39). [4] | Moderate, conditional | Mix cases whose defects are easy to confuse. Do not expect shuffling a bare word list to help: interleave by applying terms to scenarios. |
| Comparing cases side by side | Comparison activities beat other case formats (d about 0.50). Stating the principle after the comparison helped. [5] | Moderate | Study look-alike terms as pairs, then write the rule that separates them. Caveat: the strongest condition in that review was finding similarities, so evidence for contrasting confusable terms is indirect. |
| Worked examples | Help beginners; the advantage fades or reverses as skill grows (expertise reversal). Removing worked steps gradually works better than fixed examples. [6] | Strong for early learning | Study keyed answers in the first days only. Then attempt cold and use the key to check. |
| Learning from errors | Errors made with high confidence are corrected more readily after feedback (hypercorrection). Feedback must show the correct answer. Some confident errors come back after a delay. [7] | Moderate-strong (mostly lab, general-knowledge questions) | Rate your confidence on every practice answer. Re-test confident errors 2-3 days later. |
| Pretesting | Attempting questions before studying can help as much as testing after. [8] | Promising, not settled | Try a case cold before reading the key or the chapter. |
| Multiple true-false format | This format exposes "mixed" understanding: students who accept the correct statement and also a wrong one. Single-answer multiple choice hides this. [9] | Moderate (assessment research) | Judge each statement on its own. There is no fixed number of true statements. |
| Checklists for finding defects (code/document inspection) | Mixed. One controlled study found a generic checklist no better than unguided reading, while reading aimed at specific defect classes found 35% more. Other small studies favour checklists or find no difference. [10] | Weak / mixed | Use a short checklist of defect classes, phrased as questions. Not a long generic list. |
| Case interview prep | Career-centre guidance: practise with partners to find weaknesses, then drill those weaknesses. [11] | Practitioner advice, not research | Swap cases with a classmate and mark each other with the rubric. |
| Timed handwritten exams | Teaching-centre guidance: budget time by points, read all questions first, move on when time is up. A partial answer beats a blank. [12] | Practitioner advice | Fix a per-case time limit and practise it by hand. |
| Sleep | In one course (88 students, wearable trackers), sleep over the prior week and month correlated with grades; sleep on the single night before a test did not. [13] | Correlational, one course | Protect sleep across all 14 days. Do not trade sleep for study. |
| Writing about worries before the exam | A 2011 study found benefits for anxious students. A later large replication reported no effect (confirmed only through a secondary source). [14] | Mixed | Optional. Do not rely on it. |

Where the evidence is weak. Most of this research uses facts, word lists, maths problems or general-knowledge questions. No studies were found of exams like this one (audit an AI agent's output, then write five specific parts). The checklist evidence is mixed and comes from small studies. Case interview and timed-exam advice is practitioner guidance, not experiments. The plan is well founded on how to practise and less certain on exam-specific tactics.

## 2. Study plans

Set your time budget first.
- Minutes per case = (exam minutes - 10) x 0.50 / 5
- Minutes per Part B question = (exam minutes - 10) x 0.50 / 10
- Example: a 90-minute exam gives 8 minutes per case and 4 minutes per Part B question, with 10 minutes spare.
Use your numbers in every timed drill.

Keep two logs from Day 1.
- Error log: question, your answer, your confidence (sure / unsure / guess), correct answer, the word or fact that decided it, one-line rule.
- Pair list: every pair of terms you confused, plus pairs that sit near each other in the chapters.

### 14-day plan (Day 14 = day before the exam)
| Day | What to do | Time | Why |
|---|---|---|---|
| 1 | One practice exam, cold, by hand, timed. Mark it with the key and rubric. Start both logs. | 2 h | Pretest; shows your gaps; sets a baseline. |
| 2 | Build term cards from the chapters and pair list. Study 3 keyed Part A answers: for each line, say why it earns credit. | 75 min | Worked examples while the format is new. |
| 3 | Cards in both directions (25 min). Two cases "faded": write parts 1-2, check the key, then write parts 3-5, check. | 75 min | Moving from examples to solo work. |
| 4 | Three cases cold under your time limit, marked against the rubric. Two Part B questions. | 75 min | Retrieval in exam format. |
| 5 | Re-attempt every confident error from Days 1-4. Rewrite five of your part-4 corrections until an agent could run them without asking a question. | 60 min | Hypercorrection; fixes the most commonly weak part. |
| 6 | Mixed set: four cases from different lessons, shuffled. Shuffle cards within clusters of similar terms. | 75 min | Interleaving where categories are easy to confuse. |
| 7 | Rest, or 20 minutes of cards. | 0-20 min | Spacing gap. |
| 8 | Second practice exam, full, timed, by hand. Mark it. | 2 h | Spaced retrieval; measures progress. |
| 9 | Work the error log: for each miss, write why the wrong answer tempted you and the rule that would have stopped you. Re-test Day 1 confident errors. | 60 min | Delayed re-test; confident errors can return. |
| 10 | Write two cases of your own: take a sound agent output and plant one defect. Swap with a classmate if you can and mark each other. Say part 5 aloud. | 75 min | Thinking like the exam author; partner feedback. (The guide's suggestion; not directly tested.) |
| 11 | Part B block: all remaining multiple-answer questions, interleaved, timed. Then two cases. | 75 min | Speed on Part B once accuracy is solid. |
| 12 | Third practice exam, or a mixed set of 7 cases + 6 Part B questions, under exact timing. | 2 h | Full rehearsal. |
| 13 | Cards only for terms missed twice. Re-attempt your two worst cases. | 45 min | Targeted and light. |
| 14 | One case and ten cards. Pack pens and pencils. Sleep. Nothing new. | 30 min | Protect sleep; avoid late confusion. |
If you have fewer than three practice exams, build sets from leftover questions or your Day 10 cases. Avoid reusing a practice exam within 4 days, or you will be recognizing answers rather than retrieving them.

### 3-day crash version
You lose most of the spacing benefit. Make up for it by testing, never by rereading.
| Day | What to do | Time | Why |
|---|---|---|---|
| 1 | Practice exam, timed, by hand. Mark it. Build a pair list from misses only; make cards in both directions. Study two keyed cases closely for the defect types you missed. | 3 h | Diagnose, then worked examples on your gaps only. |
| 2 | Cards (30 min). Five cases cold under your time limit, marked. Two Part B questions per cluster of confusable terms. In the evening, re-attempt Day 1 confident errors. | 3 h | Retrieval with feedback; a same-day gap. |
| 3 | Second practice exam, timed. Review only confident errors and your weakest answer part. Memorize the checklist (section 3). Stop by early evening and sleep. | 2.5 h | Final rehearsal; protect sleep. |
| Exam morning | Ten cards, one case. | 15 min | Warm-up only. |

## 3. Part A routine

### Read as an auditor: claim, then evidence
1. Underline what was asked. Mark the verbs and limits in the instruction ("train", "on X", "report Y", "don't Z").
2. Box every claim in the output. Every number, and every "done", "all", "fixed", "passed", "means", "ready", "safe", "fair".
3. For each boxed claim, ask three things. What evidence is shown? Is it the right kind of evidence for this claim? Is the sentence stronger than the evidence?
4. Pick one defect you can prove from the page. Any real defect with a checkable reason earns credit, so take the one you can argue best, not the most interesting one.

### Defect checklist (ask as questions)
- Scope: Did the agent do what was asked, on the right data, within the limits? Did it quietly drop, swap or add anything?
- Done vs verified: Is "done / passed / fixed" backed by checking the final state, or only by the agent's own report or log?
- Numbers: Does the arithmetic hold? Is there a baseline? What is the denominator? What is the base rate?
- Data and retrieval: Where did the facts come from? Is each claim backed by a source that was actually retrieved, or was it invented?
- Testing: Do the tests exercise the real behaviour and the risky inputs, or only a trivial case? Did anyone check the final state?
- Tools and permissions: Did the agent use a tool, or touch a file, it was not given or told to avoid?
- Evaluation: Was it scored on the same examples used to build it? One run, one prompt, one sample?
- Confidence words: Do "always", "proves", "guarantees", "ready to deploy" match the evidence?
- Handoffs and approvals: Is there a condition someone can actually check? Does the approval cover this action?
- Replication: One run, one try, one sample? Would it hold if you ran it again?

### Writing the five parts by hand
Aim for one or two lines each. Grammar earns nothing; precision earns everything.
| Part | Frame | Common failure |
|---|---|---|
| 1. Defect + reason | "The claim '[8 words or fewer from the output]' is unsupported because [fact from the case: a number, a line, a step]." | A reason the grader cannot check ("seems off"). |
| 2. Term | One term. If two fit, pick the narrower one. | Listing three terms to hedge. |
| 3. Check | "[Test] on [data]; the claim stands only if [pass condition]." | "Review it carefully" (not a test). |
| 4. Correction | An instruction the agent can run: do X on Y, report Z, do not claim W until V. | A complaint ("you were wrong") instead of an instruction. |
| 5. Plain words | Two sentences, no jargon: what is wrong and what could happen because of it. | Jargon, or no consequence. |

### Drills for each part
- Term sprint: 10 cases, 60 seconds each, parts 1-2 only.
- Check sprint: for 10 claims, write only the test and its pass condition.
- Correction test: reread your part 4 and ask, "Could an agent do this without asking me a question?" If not, rewrite it.
- Plain-words test: say part 5 aloud to someone outside the field, or imagine one. If they would ask "what does that mean?", rewrite it.
- Always by hand, always timed. Typing hides how long handwriting takes.

## 4. Part B routine

### Learn look-alike terms in pairs
For each pair, make one card with: each term's one-line definition, in the wording of the chapter that teaches it; the deciding question: the one thing that tells them apart; one example of each; one prompt to an AI tool that uses the wrong term.

Example pairs, taken only from terms the course chapters use (the chapter wins if it differs):
| Pair | Deciding question |
|---|---|
| Repeatability / correctness | Did the same answer come back each time, or was it compared with the true answer? (chapter 1) |
| Temperature / evidence of truth | Does the setting change how concentrated the choices are, or does it supply any evidence the answer is right? (chapter 1) |
| Validator pass / entailment | Does the output have the required shape, or does the cited passage actually support the claim? (chapters 2 and 7) |
| Development set / held-out set | Was it used to build or choose the prompt or model, or kept aside to test the final choice? (chapters 2 and 9) |
| tool_use / tool_result | Is this the model asking to call a tool, or what the tool returned? (chapter 11) |
| Association / intervention | Does it say what goes with what, or what happens if we do something? (chapter 9) |
| Capability / authority | What can the system technically do, or what is it allowed to do for this task? (chapters 3 and 5) |
| Containment / string prefix | Is the resolved path inside the approved folder, or does it only start with the same letters? (chapter 5) |
| Scope check / correctness | Did only the allowed files change, or does the change behave correctly? (chapter 6) |
| Plan / result | Is it what was meant to happen, or a record of what did? (chapter 10) |
| Version check / lock | Does it spot a stale write, or keep two writers from interleaving? (chapter 12) |
| Approval / fingerprint | Did someone say yes, or is that yes tied to the exact proposal? (chapter 13) |

Make cards in both directions: definition -> term, and term -> "which description fits?" Practice in one direction transfers poorly to the other [3]. Shuffle within a cluster of similar terms, not across unrelated ones [4].

### Judge each statement alone
1. Cover the other four statements.
2. Find the word that carries the meaning: usually the technical term or a qualifier ("always", "only", "guarantees", "never").
3. Ask: is this term the correct name for exactly what is described? Common traps are the right term with the wrong condition, a near-synonym swapped in, and a qualifier that makes the statement too strong.
4. Mark it and move on. Do not count how many you have marked true; there is no quota.
5. For "spot the wrong word in this prompt", first write in the margin what the person meant, then check whether the word matches.

### Review wrong answers
For every missed statement, log the deciding word and a one-line rule (for example, "'precision' uses flagged cases as the denominator"). Star the confident errors and re-test them 2-3 days later [7]. Always review with the correct answer in front of you; practice with corrective feedback works best [1].

## 5. Common mistakes and fixes
| Mistake | Fix |
|---|---|
| Rereading notes and highlighting as the main study method. | Replace with practice tests and cards [1]. |
| A vague label ("bias", "hallucination", "bad data") where an exact term exists. | Use the narrowest term the evidence in the case supports. |
| A reason that points at nothing in the case. | Quote or cite the number or line that shows the defect. |
| Listing several terms to hedge. | Commit to one. |
| A "check" that is not a test. | Name the test, the data, and the pass condition. |
| A correction that scolds or says "be more careful". | Write an instruction an agent could run. |
| A plain-words answer full of jargon. | Two sentences a manager could repeat to their own boss. |
| Writing up four shallow defects instead of one solid one. | One well-proven defect earns credit; add a second only if time allows. |
| Overrunning on the first cases and leaving blanks. | Hard per-case limit; a partial answer beats a blank [12]. |
| Part B: assuming one true statement per question, or judging statements against each other. | Judge each alone; no quota [9]. |
| Practising only on screen. | Every timed drill on paper. |
| Trading sleep for late study. | Keep sleep steady across the two weeks [13]. |

## 6. Sources
Numbers match the citations above. Where the guide relied on a summary rather than the paper itself, it says so.
1. Dunlosky, Rawson, Marsh, Nathan & Willingham (2013). Improving students' learning with effective learning techniques. Psychological Science in the Public Interest, 14(1). DOI 10.1177/1529100612453266. Read via the APS press release and a summary table (texasldcenter.org/?p=346).
2. Cepeda, Vul, Rohrer, Wixted & Pashler (2008). Spacing effects in learning: a temporal ridgeline of optimal retention. Psychological Science, 19(11). https://pubmed.ncbi.nlm.nih.gov/19076480/ . The "too short is worse than too long" point comes from York University's press release.
3. Pan & Rickard (2018). Transfer of test-enhanced learning: meta-analytic review and synthesis. Psychological Bulletin, 144(7). https://sc-pan.github.io/pdf/PR_2018.pdf
4. Brunmair & Richter (2019). Similarity matters: a meta-analysis of interleaved learning and its moderators. Psychological Bulletin, 145(11). https://pubmed.ncbi.nlm.nih.gov/31556629/
5. Alfieri, Nokes-Malach & Schunn (2013). Learning through case comparisons: a meta-analytic review. Educational Psychologist, 48(2).
6. Kalyuga, "Expertise reversal effect and its instructional implications" (Chartered College of Teaching). Salden, Aleven, Schwonke & Renkl (2010), The expertise reversal effect and worked examples in tutored problem solving, Instructional Science.
7. Butterfield & Metcalfe (2006). The correction of errors committed with high confidence. Metacognition and Learning. Review of learning from errors, Psychonomic Bulletin & Review (2021). Griffiths & Higham, "Beyond hypercorrection".
8. Pan & Sana (2021). Pretesting versus posttesting. Journal of Experimental Psychology: Applied. (The guide saw the pretesting result in a database summary, not in the full paper; provisional.)
9. Multiple-true-false vs multiple-choice questions (2019), International Journal of STEM Education. https://dx.doi.org/10.1186/s40594-019-0169-0
10. University of Maryland Experimental Software Engineering Group, reading techniques for fault detection. Akinola & Osofisan (2009), arXiv 0909.4260. Oladele & Adedayo, LAUJET.
11. Boston University Questrom, consulting case resources. Penn Career Services, case interview guide.
12. University of Texas at Austin learning center, "Written Tests". Kansas State Counseling Services, "Suggestions for Taking Essay Tests".
13. Okano, Kaczmarzyk, Dave, Gabrieli & Grossman (2019). Sleep quality, duration, and consistency are associated with better academic performance in college students. npj Science of Learning.
14. Ramirez & Beilock (2011), Science. The failed replication (Camerer et al., 2018) was seen only in lecture slides. Check the original before relying on it.
