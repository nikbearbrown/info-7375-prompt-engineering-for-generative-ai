# Conducting AI: companion readings

These selective closing notes adapt *Conducting AI* to the existing INFO 7375 Python builds and Claude Code exercises. The main chapter sequence (1–15) was reviewed on 2026-09-06. The notes add supervisory practices, not a second course, new assessment weights, or required direct API spending.

## Locating the chapters

The companion manuscript is not bundled with this repository. In the instructor's workspace it lives at `../conducting-ai/`, relative to the course root. The filenames below are under its `chapters/` directory. With that checkout available, ask Claude Code to open the named chapter and section; otherwise consult the matching title in the instructor-supplied edition. The lesson notes are self-contained for public readers. No public book or instructor-film URL is assumed.

The book contains teaching frameworks, philosophical arguments, empirical claims, and editorial flags. These notes adapt its practical exercises without endorsing every broader claim or repeating unverified case statistics. In particular, deterministic code can be wrong, missing context may be supplied later, and a model's observed failure is not proof of an inherent inability. Human accountability is distinct from a system's ability to help detect errors.

Chapter 13 leaves section labels and alternative document structures for author confirmation; Chapters 14–15 discuss unresolved grading and auditor-calibration questions. Those choices remain in the source manuscript. INFO 7375 retains its existing artifacts and assessment policy. The supplemental themes and appendix are not assigned by this guide.

## Usage and supervision

Chapter 3, **Three Levels of AI Usage**.
File: `03-three-levels-of-ai-usage.md`.

Read the discussion of copy editor, research assistant, and supercollaborator, together with the usage-inventory exercises. Week 3 contrasts the author's supervision-demand framework with the course's capability classifier. The levels are not synonymous with chat, assistant, and agent, nor a validated product taxonomy.

## Audit before verification

Chapters 4–5, **Plausibility Auditing**.
Files: `04-plausibility-auditing-part-1.md` and `05-plausibility-auditing-part-2.md`.

Read Chapter 4's distinction between auditing and verification, then Chapter 5's “The Audit-First Protocol” and “The Honest Limit: Polanyi and the Edge of the Audit.” Week 6 records verdict, target, and mechanism before testing a patch, then compares that record with actual evidence. This is a diagnostic exercise, not a substitute for mandatory checks.

## Explicit handoffs

Chapter 9, **Tool Orchestration (Part 2: Every Handoff Explicit)**.
File: `09-tool-orchestration-part-2.md`.

Read “The Handoff as the Unit of Risk” and “The Laundering Failure.” Week 8 applies the documented trust decision to the server-to-host handoff in an MCP transcript. The added check is source correspondence, not just valid transport or a plausible tool description.

## Distinct reframings

Chapters 6–7, **Problem Formulation**.
Files: `06-problem-formulation-part-1.md` and `07-problem-formulation-part-2.md`.

Read Chapter 6's “Primary Generators: The Anchors You Don't Know You're Using” and Chapter 7's “The Distinctness Test,” “The Constraint Set as an Evaluation Instrument,” and “The Values Decision Inside Formulation.” Week 10 asks whether alternative objectives can disagree about success before a plan is generated. Claude may suggest or critique alternatives; the learner defends the selection rather than claiming models cannot generate reframings.

## Verifiability first

Chapter 8, **Tool Orchestration (Part 1: The Capability Stack)**.
File: `08-tool-orchestration-part-1.md`.

Read “Verifiability-First Engineering” and “Worked Example: One Task, Two Routings.” Week 11 makes the model/runtime division explicit and examines the independence of its arithmetic check. The author's capability stack and “easier to verify” value are teaching devices, not universal reliability rankings. A Python implementation must still be tested against its specification and inputs.

## Re-engagement

Chapters 12–13, **Executive Integration**.
Files: `12-executive-integration-part-1.md` and `13-executive-integration-part-2.md`.

Read “Integration Is Not Sequencing,” “The Re-engagement Trigger,” and “The Sequencing Trap Built Into the Structure Itself.” Week 12 records when a source change reopens an earlier plan decision, beyond merely retrying a stale write. The incident replay supplies evidence of the trigger and response; it does not assert that all components being individually correct guarantees a sound outcome.

## Interpretation and accountability

Chapters 10–11, **Interpretive Judgment**.
Files: `10-interpretive-judgment-part-1.md` and `11-interpretive-judgment-part-2.md`.

Read Chapter 10's “Three Kinds of Legitimacy” and Chapter 11's “The Memo A → Memo B Transformation” and “The Counterfeit That Looks Like Judgment.” Week 14 separates the model's proposal, checked evidence, contextual interpretation, and human recommendation. Applying Suchman's organizational framework to AI outputs is the book author's adaptation, not Suchman's own AI framework.

## Critique and the Gap Account

Chapters 14–15, **The Dress Rehearsal** and **The Plausibility Audit**.
Files: `14-the-dress-rehearsal.md` and `15-the-plausibility-audit.md`.

Read “Three Legitimate Responses to a Critique,” “Predicting the Auditor's Findings,” “Genuine Failure or False Positive,” “The Gap Account — The Whole Point,” and “Where This Leaves You — and the Honest Limit.” Week 15 keeps predictions and evidence-based responses inside the existing audit note. The course adaptation does not demand that a reviewer produce a false positive, import the book's grading weights, or require agreement with its philosophical claim of a permanent structural blind spot.

## Selection boundary

Notes appear in Weeks 3, 6, 8, 10, 11, 12, 14, and 15. Weeks 1, 2, 4, 5, 7, 9, and 13 have no added Conducting AI section: the possible connections mostly repeat existing predictions, tests, boundaries, source checks, or accountability notes. Add a future note only for a specific new contribution, not for chapter coverage.
