# Computational Skepticism: companion readings

The closing lesson notes draw on Nik Bear Brown's *Computational Skepticism for AI*, using the local manuscript reviewed on 2026-09-06. Each note points to a specific argument and adapts it to the lesson's existing Python artifact. These are selective readings, not an additional required exercise in every week.

## Locating the chapters

The companion book is not bundled with this course. In the instructor's workspace it is the sibling directory `../computational-skepticism-for-ai/`, relative to the course root. Each source below names the file under that directory's `chapters/` folder and the section to read. Ask Claude Code to open that named file when you have the companion checkout; otherwise use the corresponding title in the instructor-supplied edition. The lesson notes remain self-contained for public readers without the book. No public book or film URL is assumed.

The introduction specifies a 13-chapter sequence. The folder also contains older numbered versions of Data Validation, Delegation, and Accountability. This guide uses the explicitly chapterized files numbered 03, 09, and 12, which match that introduction. Some manuscript files contain unresolved merge markers and verification flags. The notes use identifiable prose sections, not competing figure references or unverified empirical case statistics; this task does not edit or resolve the manuscript.

## Probability and confidence

Source: Chapter 2, **Probability, Uncertainty, and the Confidence Illusion**.

File: `02-probability-uncertainty-and-the-confidence-illusion.md`.

Read “Calibration — the most operationally important diagnostic in this chapter” and “Glimmer 2.4 — Calibration curves you can trust and ones you cannot (BUILD).” The course connection is the distinction between a distribution's confidence and observed outcomes. Week 1 uses this to distinguish sampling temperature from fitted calibration on labeled examples.

## Prompt sensitivity

Source: Chapter 4, **Robustness: What Understanding Means When a Pixel Can Break the Model**.

File: `04-robustness-what-understanding-means-when-a-pixel-can-break-the-model.md`.

Read “Cross-domain transfer — the same structure in different clothes” and “Prompt sensitivity — the LLM-specific version of this problem.” Week 2 adapts the meaning-preserving perturbation question to its held-out prompt tests. The chapter itself distinguishes a shared diagnostic question from identical attack mechanisms across domains.

## Agent outcomes

Source: Chapter 8, **Validating Agentic AI: When Autonomous Systems Misbehave**.

File: `08-validating-agentic-ai-when-autonomous-systems-misbehave.md`.

Read “From prediction to action” and the discussion of completion claims in “A taxonomy of how agents go wrong.” Week 4 tests whether a finish action establishes anything beyond controller termination. The independent outcome check is the added skeptical move.

## Claims and evidence

Source: Chapter 11, **Communicating Uncertainty: Calibrating Claims to Evidence**.

File: `11-communicating-uncertainty-calibrating-claims-to-evidence.md`.

Read “The verb taxonomy,” “Saying you do not know in writing,” and “Why solitary review does not work — and the peer critique protocol.” Week 6 uses the author's wording discipline to audit a patch report against the tests actually performed. Treat the proposed verb ordering as the author's editorial instrument, not a universal measurement scale.

## Data and retrieval

Source: Chapter 3, **Data Validation: Reconstructing the Epistemic Frame Behind a Dataset**.

File: `03-data-validation-reconstructing-the-epistemic-frame-behind-a-dataset.md`.

Read “Hidden assumptions that hide in plain sight” and “Reconstructing the epistemic frame — a working procedure.” Week 7 applies the chapter's missing-data and provenance questions to corpus construction and retrieval. Trace what was excluded before treating a retrieved passage as sufficient evidence.

## Delegation and handoffs

Source: Chapter 9, **Delegation, Trust, and the Supervisory Role**.

File: `09-delegation-trust-and-the-supervisory-role.md`.

Read “The handoff condition: the contract, not the partition” and “The full delegation map structure.” Week 10 adds a testable evidence boundary to a dependency edge. The book distinguishes a reviewable delegation document from proof that the underlying decisions are good; retain that distinction.

## Explanation and verification

Source: Chapter 5, **Model Explainability: Distinguishing Explanation from the Appearance of Explanation**.

File: `05-model-explainability-distinguishing-explanation-from-the-appearance-of-explanation.md`.

Read “Back to Ash” and “Glimmer 5.1 — Technically accurate, practically misleading.” Week 11 takes the distinction between local operations and the reader's interpretation into its tool evidence matrix. The exercise uses the course fixture, not an assertion that the historical narrative has been independently fact-checked here.

## Shared state and provenance

Source: Chapter 8, **Validating Agentic AI: When Autonomous Systems Misbehave**.

File: `08-validating-agentic-ai-when-autonomous-systems-misbehave.md`.

Read “When agents talk to each other,” especially cascading errors and authority laundering. Week 12 distinguishes an update that is valid under concurrency control from information that deserves belief. Validate the handoff and source, not just each worker in isolation.

## Attestation and review

Source: Chapter 12, **Accountability: Who Is Responsible When the System Fails?**

File: `12-accountability-who-is-responsible-when-the-system-fails.md`.

Read “The gate: the attestation you sign” and “What the attestation regime optimizes for — and what it sacrifices.” Weeks 13 and 15 apply the declaration of tested and untested scope, named human decisions, and the ability to withhold sign-off. This supplements the course gate and packet; it does not authenticate a signature or provide a legal compliance determination.

## Values and accountability

Sources: Chapter 7, **Fairness Metrics: Choosing a Definition and Defending It**, and Chapter 12, **Accountability: Who Is Responsible When the System Fails?**

Files: `07-fairness-metrics-choosing-a-definition-and-defending-it.md` and `12-accountability-who-is-responsible-when-the-system-fails.md`.

Read “Each metric is a values claim,” “The defense as deliverable,” and the accountability chapter's discussion of recourse. Week 14 asks who owns the tradeoff and how an affected person can contest a result. Formal fairness metrics apply only where the task supports them; do not invent demographic measurements for unrelated workflows.

## The casebook

Source: Chapter 1, **The Skeptic's Toolkit**.

File: `01-the-skeptics-toolkit.md`.

Read “The fluency trap” and the “Agentic Red-Team Casebook” exercise. Week 15 adapts its prediction-before-observation record and comparison of reported versus actual outcomes. Keep the record in the existing capstone evidence packet and use Claude Code; other interfaces mentioned by the book do not change the course stack.

## Selection boundary

Notes are included in Weeks 1, 2, 4, 6, 7, and 10–15. Weeks 3, 5, 8, and 9 retain their existing explanations and references: this pass did not find a sufficiently distinct addition beyond the outcome, boundary, or validation questions already assigned elsewhere. Future notes should identify a new, specific connection rather than repeat general cautions.
