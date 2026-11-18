# Exam preparation guide: INFO 7375: Prompt Engineering for Generative AI

**Student-facing draft for instructor review.** Learn to communicate precise instructions to Claude and verify agent work through Python mechanisms and evidence. Use this guide for preparation, not as a prediction of examination questions. It follows the supplied guide’s six-part structure, with course-specific review, vocabulary and audit questions.

## Start here: format and scoring

The revised local format is **100 points: five cases × 10 = 50, plus ten multiple-answer questions × 5 = 50**. Every case asks five case-specific questions: justified defect (3), precise concept applied (2), evidence check (2), corrected instruction (2), and plain-language consequence (1). Give short numbered answers, not an open essay. Each multiple-answer item contains five independently true/false statements; any number from zero through five may be true. Use the [standalone practice prompt](EXAM-GENERATOR-PROMPT.md); its embedded starter knowledge requires no extra uploads. Historical papers/keys remain old-format exercises. The compact term list prioritizes prompting/agents/loops/tools but is still being narrowed, so confirm final scope with the instructor.

The current public rubric accepts a real defect other than the author’s intended one when it is justified from the case. Your evidence, fix and explanation must address your chosen defect. If no real defect with a reason is identified, the case is capped at 5/10; that is a ceiling, not an automatic score. Do not substitute a cosmetic nitpick for a consequential problem. See the [public rubric](README.md) for details.

Use the taught lesson sequence: sampling; prompt contracts; chat and agents; loops; permissions; diff review; retrieval; MCP; training/configuration; planning; tool verification; memory; evaluation/approval; governance; capstone. Check the instructor’s announced coverage rather than inferring topic frequencies from practice papers.

## 1. What the evidence says

The attached guide is the structural starting point for this plan. The broad study principles below are useful, but the exact schedule is advice, not an experimentally validated recipe for this examination. Numerical effect sizes and precise optimal spacing claims from the source draft are not repeated because they have not been rechecked here against the original papers.

| Technique | Evidence and limitation | Application |
|---|---|---|
| Retrieval practice | Broad support for attempting to recall and then receiving corrective feedback [1,3]. It is not proof that every practice design transfers. | Answer before opening the key; explain the reason after checking. |
| Spacing | Distributed practice is well supported; useful gaps depend on the material and retention interval [1,2]. | Revisit difficult concepts on several days rather than one long session. |
| Interleaving | Benefits depend on the material and similarity of categories [4]. | Mix confusable case types after learning their basic distinctions. |
| Comparing cases | Comparing examples can support abstraction [5]. | State the deciding rule between two similar concepts, not just two definitions. |
| Worked examples | Helpful scaffolding, especially early; support should fade with understanding [6]. | Study one public example, finish a partial answer, then solve independently. |
| Correcting confident errors | Feedback can correct high-confidence mistakes; correction may not persist without later retrieval [7]. | Record confidence and retest important errors after a delay. |
| Pretesting | A first attempt can direct later study [8]. | Try an unfamiliar public question before reading its explanation; low first scores are diagnostic. |
| Multiple true-false practice | Evaluates individual propositions and can reveal partial misconceptions [9]. | Judge each option by its meaning, not by the pattern of other answers. |
| Audit checklists | Results depend on the task and checklist; a checklist is not proof of correctness [10]. | Use the short course-specific questions below, then justify your conclusion. |
| Partner practice and timed writing | Practical advice rather than a validated treatment for this exam [11,12]. | Exchange answers and check against the public rubric; rehearse the announced medium. |
| Sleep | Sleep habits correlate with performance; the cited study does not establish a causal guarantee [13]. | Protect a sustainable sleep schedule across preparation. |
| Writing about worries | Evidence is mixed, and the supplied draft relied on secondary reporting [14]. | Optional; do not substitute it for practice or support you already find useful. |

Targeted rereading is useful when it repairs a gap. The recommendation is not “never reread,” but “do not mistake familiarity for being able to answer.” Begin untimed if the mechanism is new; add timing once you can explain it.

## 2. Study plans

### Set the budget and record what you learn

Use the instructor-announced exam duration and accommodations. After reserving reading/checking time, split the answering time equally between the two 50-point parts; this update does not announce a new duration.

Allocate time from the actual examination instructions, not from a universal formula. Keep some checking time. A missed case should not prevent attempts at the remaining questions. Practise on paper if that is the announced format; confirm permitted materials with the instructor.

Keep an **error log** with: item; your answer; confidence; corrected reasoning; the decisive fact or qualifier; a short rule; next retest date. Keep a **pair list** of terms you confuse. Do not write only the answer letter: record why it is correct.

### Fourteen-day plan

These are adjustable study sessions, not required workloads. Include breaks and adapt around other commitments.

| Day | Work | Suggested duration |
|---|---|---|
| 1 | Attempt public practice 01 cold; then check it and start both logs. | Exam-length sitting plus review |
| 2 | Review cluster 1 below; make two-direction term cards; explain a public worked answer. | 60–75 min |
| 3 | Review cluster 2; complete Q1 independently, then add Q2–Q4 without the key. | 60–75 min |
| 4 | Review cluster 3; answer two cases and ten individual T/F statements. | 60–75 min |
| 5 | Retest confident errors; rewrite vague evidence requests and next instructions. | 45–60 min |
| 6 | Review clusters 4–5; mix cases from different areas. | 60–75 min |
| 7 | Rest or brief spaced retrieval from the pair list. | 0–20 min |
| 8 | Attempt public practice 02 cold, then score every rubric row. | Exam-length sitting plus review |
| 9 | Revisit the oldest errors. Explain why the tempting alternative is not supported. | 45–60 min |
| 10 | Create two new scenarios from public lessons, each with one deliberate defect. Exchange with a peer. | 60–75 min |
| 11 | Practise individual T/F reasoning and two cases from the weakest clusters. | 60–75 min |
| 12 | Full rehearsal using unused public questions or your peer-created set; do not assume a third full case paper exists. | Exam-length sitting plus review |
| 13 | Retest the most consequential remaining errors and explain one mechanism aloud. | 30–45 min |
| 14 | Light retrieval, check logistics, and protect sleep. | 20–30 min |

Course-specific clusters:
1. Tokens, sampling and prompt contracts.
2. Agent loops, permissions and diff review.
3. Retrieval, mcp and configuration.
4. Planning, verification and retries.
5. Memory, evaluation, approval and governance.

When repeating a question, explain the reasoning before recalling the answer. A familiar score is not evidence that you can transfer the concept to a new case.

### Three-day version

| Day | Work |
|---|---|
| 1 | Diagnose with practice 01. Review the two weakest clusters and make cards only for important gaps. |
| 2 | Solve several mixed cases; inspect feedback; retest earlier mistakes after a break. Practise the full four-probe response. |
| 3 | Rehearse with practice 02, review remaining gaps, and stop intensive work early enough to rest. |

Short preparation cannot reproduce two weeks of spacing. Focus on accurate reasoning and targeted reading rather than memorizing complete answers.

## 3. Part A routine: audit the claim

1. Underline the requested action, constraints and decision the person must make.
2. Identify the output’s consequential claims. Distinguish observation, interpretation and recommendation.
3. Compare each claim with the supplied evidence. What is missing, contradictory or stronger than the evidence permits?
4. Choose a substantive defect supported by the case. Quote the relevant fact and name the mechanism. Do not invent unseen facts to make the diagnosis work.
5. Keep the check, next instruction and plain explanation aimed at that same defect.

### Course-specific audit questions

- **Contract:** What was requested, what was excluded, and what acceptance condition was defined?
- **Boundary:** Which files, tools and data are permitted? Is the limit enforced or merely described?
- **Output:** Are structure, source support and task completeness being checked separately?
- **Retrieval:** Does a result support the claim, and what does an unsuccessful lookup actually establish?
- **Evaluation:** What examples, repetitions, failure categories and denominators define the score?
- **Tool effects:** What system-of-record state proves the operation succeeded? What happens after interruption or retry?
- **Plan and memory:** Are prerequisites meaningful, and can a remembered claim be traced to independent evidence?
- **Approval:** What exact action and version did the real authorized person approve?

### Answer five case-specific questions

| Probe | What to write | Self-check |
|---|---|---|
| Q1: defect and reason (3) | “The claim … is not supported because … .” | Can a marker locate the fact and see why it matters? |
| Q2: precise concept (2) | Name the taught term and apply it to your chosen defect. | Is the concept accurate rather than a vague label? |
| Q3: evidence (2) | One concrete test, comparison or inspection and what result would support or defeat the claim. | Could this check reveal that the claim is wrong? |
| Q4: next instruction (2) | Tell the agent what to do, within which limits, and what to report. Ask for necessary clarification if proceeding would exceed authority. | Does it address your defect rather than offer generic advice? |
| Q5: plain explanation (1) | Tell the named person what they can rely on now, what remains uncertain, and why it matters. | Can a non-expert act on it without learning your jargon? |

A test needs an observable outcome, not necessarily a numerical threshold. An evidence request is not “ask the agent whether it is sure.” A correction is not “be more careful.” Short bullets are fine where the paper permits them.

**Practice prompt:** An agent says a Python export is complete because the output directory exists. Design one check that distinguishes a fully exported dataset from an empty directory, then give a bounded next instruction. This is a study prompt, not an exam answer.

### Short drills

- **Diagnosis drill:** From a public lesson, state one claim, its limit and the precise term in one minute.
- **Evidence drill:** Write a check that distinguishes a correct result from a convincing but wrong one.
- **Instruction drill:** Give one bounded, executable next step with a report requirement.
- **Translation drill:** Explain the same issue without jargon, without changing its meaning.

Course exercises assume Claude Code access through the university portal for enrolled students; public readers need their own Claude Code account. That is not the same as direct API credits. Practise Python mechanisms offline first; live API calls are optional and explicit. During a cold exam rehearsal, do not use Claude or reference code.

If a public key appears technically wrong, record the disputed wording and your reasoning, then ask the instructor. Do not memorize a contradiction simply because it is in a key. This guide does not replace grading policy.

## 4. Part B routine: use the terms precisely

For each pair, make a card with a definition, deciding question, original example and non-example. Practise both directions: term to explanation, and scenario to term. Start with these review distinctions, then extend them using the instructor’s glossary.

| Terms | Deciding distinction |
|---|---|
| Repeatability / correctness | Did the same answer come back each time, or was it compared with the true answer? |
| Temperature / evidence of truth | Does the setting change how concentrated the choices are, or does it supply evidence the answer is right? |
| Validator pass / entailment | Does the output have the required shape, or does the cited passage support the claim? |
| Development set / held-out set | Was it used to build or choose, or kept aside to test the final choice? |
| tool_use / tool_result | Is this the model asking for a tool call, or what the tool returned? |
| Association / intervention | What goes with what, or what happens if we act? |
| Capability / authority | What can the system do, or what is it allowed to do for this task? |
| Containment / string prefix | Is the resolved path inside the approved folder, or does it only start with the same letters? |
| Scope check / correctness | Did only the allowed files change, or does the change behave correctly? |
| Plan / result | What was meant to happen, or what did happen? |
| Version check / lock | Does it spot a stale write, or keep writers from interleaving? |
| Approval / fingerprint | Did someone say yes, or is that yes tied to the exact proposal? |

These are study aids, not a complete syllabus or a claim that these particular terms will appear. Prefer the course’s explicitly stated usage, but ask about a factual conflict or a term whose meaning varies across fields.

### Judge each statement independently

1. Identify the claim and its qualifiers.
2. Work out whether the stated conditions are enough. For a number, verify the denominator, units and assumptions.
3. Use a counterexample when evaluating a universal claim. “Always” is not automatically false, and a cautious-sounding sentence is not automatically true.
4. Mark the statement according to its meaning and the printed marking instructions, not a guessed answer pattern.
5. During review, explain why the nearest wrong alternative fails. Retest high-confidence errors later.

The published rules score each of the five statements separately: correctly checked true and correctly left-blank false statements each earn one point. Follow the actual examination’s instructions if revised.

## 5. Common mistakes and fixes

| Mistake | Better practice |
|---|---|
| Remembering the answer rather than the mechanism | Explain an unfamiliar example and a counterexample. |
| Giving only “bias,” “bug” or “unreliable” | State the specific defect, case evidence and precise term. |
| Inventing missing details | State what is unknown and what evidence would settle it. |
| Naming many shallow defects | Develop one consequential, defensible defect coherently. |
| Proposing an unrelated test | Ask whether your check could expose the defect you identified. |
| Treating completion as verification | Identify the observable result and the appropriate source of evidence. |
| Giving an unrestricted “fix everything” instruction | Bound the change and require a specific report or confirmation. |
| Writing technical jargon to a non-expert | Explain the practical consequence in ordinary language. |
| Using an AI answer as proof of understanding | Attempt cold first, then critique help against public sources. |
| Spending the whole sitting on early cases | Use the announced timing and return to difficult items. |
| Treating a study schedule as an exam rule | Check the instructor’s current announcements, accommodations and examination sheet. |

### Final self-check

Can you name a claim, give a reason it is unsupported, use a precise term, ask for discriminating evidence, and give a bounded next step? Can you explain a mistaken T/F choice without looking at its key? If not, return to the relevant lesson and practise that mechanism rather than rereading everything.

## 6. Sources and course resources

### Use the public course materials

- [Exam overview and rubric](README.md).
- [Practice exam 01](practice-exam-01.md) and [practice exam 02](practice-exam-02.md). Open each matching key only after attempting the student file.
- [Lessons](../lessons/), [setup](../docs/setup.md), and [NEU Claude Code access](../docs/neu-claude-access.md).
- The exam overview links the jargon glossary and an additional public multiple-answer bank as extra study resources; the exam itself uses only terms from the course text. Their legacy filenames may say “midterm”; this document is an **exam preparation guide**, not a new midterm specification.

This guide uses the public overview as inspected on 9 November 2026. It does not reproduce private examination questions, solutions, topic allocations or answer patterns. The instructor’s current examination sheet controls scope, duration and permitted materials.

### Research behind the preparation structure

These references come from the supplied study-guide draft. They support general study principles, not a guarantee of a score or the exact schedule above. The original papers and all links have not been independently revalidated in this adaptation; secondary-source limitations are retained. Quantitative claims from the draft have deliberately been omitted.

1. Dunlosky et al. (2013), *Improving Students’ Learning With Effective Learning Techniques*. DOI: [10.1177/1529100612453266](https://doi.org/10.1177/1529100612453266). Broad review of study strategies.
2. Cepeda et al. (2008), *Spacing effects in learning*. [PubMed](https://pubmed.ncbi.nlm.nih.gov/19076480/).
3. Pan & Rickard (2018), *Transfer of test-enhanced learning*. [Author PDF](https://sc-pan.github.io/pdf/PR_2018.pdf).
4. Brunmair & Richter (2019), *Similarity matters: a meta-analysis of interleaved learning*. [PubMed](https://pubmed.ncbi.nlm.nih.gov/31556629/).
5. Alfieri, Nokes-Malach & Schunn (2013), *Learning through case comparisons*. [Author PDF](https://www.lrdc.pitt.edu/Schunn/papers/ContrastingCasesMeta-AlfieriEtAl2013.pdf).
6. Salden et al. (2010), *The expertise reversal effect and worked examples in tutored problem solving*. [Research record](https://researchportal.hw.ac.uk/en/publications/the-expertise-reversal-effect-and-worked-examples-in-tutored-prob/).
7. Butterfield & Metcalfe (2006), *The correction of errors committed with high confidence*. [Article copy](https://core.ac.uk/download/357328401.pdf). Revisit corrections; immediate feedback is not permanent mastery.
8. Pan & Sana (2021), *Pretesting versus posttesting*. [Author PDF](https://sc-pan.github.io/pdf/PS_2021.pdf). The supplied draft relied on a summary rather than full-paper inspection.
9. Research comparing multiple-true-false and multiple-choice formats (2019), *International Journal of STEM Education*. [DOI](https://doi.org/10.1186/s40594-019-0169-0).
10. University of Maryland Experimental Software Engineering Group, [reading techniques for fault detection](https://www.cs.umd.edu/projects/SoftEng/ESEG/topics/rtfault2.html). Transfer to this exam is indirect.
11. Penn Career Services, [case interview guide](https://careerservices.upenn.edu/resources/case-interview-guide/). Practitioner guidance, not experimental evidence for this exam.
12. Kansas State Counseling Services, [suggestions for taking essay tests](https://www.k-state.edu/counseling/resources/self_help/suggestionsfortakingessaytests.html). Practitioner guidance.
13. Okano et al. (2019), *Sleep quality, duration, and consistency are associated with better academic performance in college students*. [MIT record](https://dspace.mit.edu/handle/1721.1/127257). Observational evidence.
14. Ramirez & Beilock (2011), expressive writing before tests, via [a research news summary](https://www.sciencedaily.com/releases/2011/01/110113141605.htm). The supplied draft also reports a replication concern through secondary material; no recommendation here depends on this finding.
