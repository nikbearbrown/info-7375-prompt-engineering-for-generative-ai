# PROJECT-BRIEF — Readback
Aravind Ravi · INFO 7375 · Fall 2026 · Target role: AI Product Manager
*Hear how AI reads your instructions before it acts on them.*

## 1. What is it?
Readback will show a product manager which clause of their eval rubric an AI judge reads differently than they meant. When it's done, it will be a Python repository (readback-pm) with a command-line tool, a worked case study on public meeting data, and an evaluation log reporting judge agreement before and after rubric revision on a held-out set.

## 2. Why would anyone care?
A PM who owns an AI feature uses an eval rubric to decide whether the feature works. If the judge reads a clause differently than the PM meant, the scores look fine and the ship decision is wrong. I looked at two tools that already work on judge reliability. Maxim AI lets you run several models as judges, compare their verdicts, and measure judge–human agreement. orq.ai has a workflow that compares an evaluator against human labels and then rewrites the evaluator's prompt to close the gap. As far as I could find in their docs on 14 October 2026, neither tells the PM which clause of their rubric caused the disagreement. Readback will, and it will hand that clause back to the PM as a question instead of rewriting it, because the rubric is the PM's product decision. Specs (later module): for specs rather than rubrics, the comparison is GitHub Spec Kit's clarify step, which asks a model to imagine where a spec is unclear; Readback's PRD module will measure disagreement between independent readings instead.

## 3. Who opens it, and what do they do with it?
The reader is an AI PM hiring manager. In the first sixty seconds they will open the README and see one table: per-clause agreement between the judges and my labels, the clause that caused the most disagreement, the question Readback asked, my revision, and held-out agreement before and after. The end user is a PM, who will run the tool on their own rubric and labelled outputs.

## 4. What does it prove about me?
That I treat a rubric as a prompt contract; that I verify instead of trust, because my labels will be committed before any judge runs, provable from the git history; that I evaluate with per-clause agreement on a held-out split; and that I ground claims in sources, since one rubric clause checks that every recap claim traces to a transcript line. A reviewer could fairly conclude that I understand why LLM judges need a human anchor. They could not conclude that Readback works on every kind of AI feature, because I will test it on one.

## 5. What is in, what is out, what comes first?
In: the rubric module and a meeting-recap case study on a sample of the public AMI Meeting Corpus (CC BY 4.0), with a constructed PRD, system prompt and rubric. Out: Readback will never rewrite a rubric itself; it only asks the PM clarifying questions, and the PM decides. I also won't build a UI, and PRDs and system prompts are later modules. First: one rubric, three judges and my labelled recap outputs, producing an agreement table. You would know it ran because the report lists per-clause disagreement, and its commit comes after my labels' commit.

## 6. What could sink it?
Overfitting. If I revise the rubric until the judges agree on the examples I tuned it on, the improvement means nothing. I will freeze a held-out split before any revision and report only held-out numbers. A second risk is that judges share blind spots and agree for the wrong reasons; I will compare same-model role prompts against cross-model judges and report the difference, whichever way it comes out.

## 7. Why this project?
It's a mix. New to me: eval design, measuring judge–human agreement, and multi-model judging. Already mine: writing product requirements, which I did as a PM at LG Energy Solution Vertech, Tech4Dev (Dalgo) and KoineArth (ngageN). Those documents are internal, so I can't show them here. What I can show is the verification habit from this course: my Week 1 film verified every on-screen number (PR #8, open), and I held my Week 2 Reallocation Engine recipe at DRAFT because open TODOs blocked promotion (PR #23, open, not merged). I picked this project because evals are becoming core to AI PM work and I have no eval project yet.

## Exists today (14 October 2026)
- This brief and FRICTIONAL.md.
- The brutalist.art toolkit, pinned at cd4bf20 and installed.
- Evidence for existing skills: Week 1 film (PR #8, open) and Week 2 recipe (PR #23, open, not merged, DRAFT).
- AMI sample: 10 whole scenario meetings (transcripts + human abstractive summaries), downloaded 14 October 2026 from the AMI Meeting Corpus (CC BY 4.0). In `case-study/data/sample/`.
- Constructed case-study docs (CONSTRUCTED, 14 October 2026): recap PRD, recap system prompt, and rubric-v0 with five clauses. In `case-study/constructed/`.
- Feature outputs: the recap prompt run once on each of the 10 meetings with headless Claude Code (Claude Opus 5.5, `claude-opus-5-5`, Claude Code 2.1.283), 14 October 2026. In `case-study/outputs/feature-run/`.
- Not yet: the Readback tool itself, my labels, judge runs, agreement results.

## Will exist
- readback-pm: a Python CLI for rubric stress testing.
- A meeting-recap case study on an AMI sample, with constructed PRD, system prompt and rubric labelled CONSTRUCTED.
- My per-clause pass/fail labels, committed before any judge runs.
- Judge runs, a per-clause agreement table, and a frozen held-out split with before/after results.
- A same-model vs cross-model judge comparison.
- Later modules for PRDs and system prompts.
