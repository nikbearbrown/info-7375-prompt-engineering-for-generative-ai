# Research review packet — 2026-09-06

Status: technical worked-example evidence prepared for human review; Gate 1 remains unsigned. No chapter manuscripts, generated figures, or EPUB are claimed.

## What actually ran

[Executable research](worked_examples.py) imports all fifteen course implementations and asserts the constructed examples below. [Exact output](worked-examples.json) records Python 3.14.6 and every result. All fixtures are offline; none are Claude responses, real stakeholder decisions, or field experiments. The script can be rerun from the repository with `PYTHONDONTWRITEBYTECODE=1 python3 research/worked_examples.py .`.

[Validation transcript](validation-final-20260906.md) records 90 lesson tests plus 13 integration tests passing, along with implementation hashes. Only this interpreter was tested. Passing tests do not prove security, truth, or instructional effectiveness.

## Chapter evidence

### 01

Constructed logits [1, 2, 3] give probabilities [0.0900305732, 0.2447284711, 0.6652409558] at temperature 1. With seed 7 and 1,000 draws, counts are [102, 268, 630]. Independent direct-exponential normalization agrees with the stabilized implementation. These are toy sampling results, not Claude logits or accuracy.

Evidence: JSON key `chapters.01`; matching lesson implementation and tests linked in the individual research note.

### 02

A response saying red while its cited fixture says blue passes the format validator. Two malformed/unknown-source cases fail. Format acceptance is 1/3 for these three deliberately constructed cases; it is not a truth score.

Evidence: JSON key `chapters.02`; matching lesson implementation and tests linked in the individual research note.

### 03

The reason/read/write capability exercise reports different missing capabilities by mode. Its names are a course-specific action-surface classifier, not Anthropic's workflow/agent taxonomy.

Evidence: JSON key `chapters.03`; matching lesson implementation and tests linked in the individual research note.

### 04

A lookup of blue followed by finish(red) ends with finished status. Repeated lookups exhaust a budget of two. Termination and factual correctness are separate properties.

Evidence: JSON key `chapters.04`; matching lesson implementation and tests linked in the individual research note.

### 05

An in-root read succeeds. Traversal, an outside-pointing symlink, and an unapproved write are rejected in disposable fixtures. This does not establish resistance to filesystem races or constitute a production sandbox.

Evidence: JSON key `chapters.05`; matching lesson implementation and tests linked in the individual research note.

### 06

For inputs [2, 5], the old x-1 function returns [1, 4], an incorrect constant patch returns [3, 3], and x+1 returns [3, 6]. A review without approval fails. Tests expose the illustrated regression; the fixture is not an actual Claude-authored patch or human approval.

Evidence: JSON key `chapters.06`; matching lesson implementation and tests linked in the individual research note.

### 07

Cosine similarity for 'office hours' and 'office hours appointment' is 2/sqrt(6), approximately 0.8164965809. A synonym pair has no token overlap and is not retrieved. Equal-score results retain deterministic ordering. Lexical similarity is not semantic understanding.

Evidence: JSON key `chapters.07`; matching lesson implementation and tests linked in the individual research note.

### 08

Tool listing before initialization is rejected. Initialization returns version 2025-11-25, the initialized notification has no response, and a missing lookup returns isError. A fixed supported-version fallback can be legal under MCP; the teaching implementation's limited parameter/capability coverage, not fallback alone, prevents claiming full conformance.

Evidence: JSON key `chapters.08`; matching lesson implementation and tests linked in the individual research note.

### 09

On four constructed separable training points, a 0.2 learning-rate step changes weight from 0 to 0.15 and loss from 0.6931471806 to 0.5876561461. The finite-difference weight gradient is approximately -0.75. After 200 steps, weight is 3.1669517461 and training loss 0.0215209850. Four separately specified held-out toy points classify correctly. This is neither a real-world generalization estimate nor Claude training.

Evidence: JSON key `chapters.09`; matching lesson implementation and tests linked in the individual research note.

### 10

The dependency order is inspect, build, verify; a cycle is rejected. A syntactically populated but semantically empty plan produces no missing-field findings. Structural validation cannot establish plan quality.

Evidence: JSON key `chapters.10`; matching lesson implementation and tests linked in the individual research note.

### 11

The local add tool returns 42 for 17+25 with matching call identifiers. Boolean arguments and duplicate IDs are rejected. An end_turn answer of 99 can still finish. An independent arithmetic check, not protocol termination, establishes this example's correct answer.

Evidence: JSON key `chapters.11`; matching lesson implementation and tests linked in the individual research note.

### 12

A fresh write of an unverified red value succeeds, while a stale expected-version write fails. Version checks address stale updates, not truth. This sequential fixture is not a concurrent stress test or evidence that several agents independently verified a claim.

Evidence: JSON key `chapters.12`; matching lesson implementation and tests linked in the individual research note.

### 13

A simulated reviewer's approval matches the original target hash but not changed content. This demonstrates content binding only: the fixture is not a real person's consent, and a digest does not authenticate identity.

Evidence: JSON key `chapters.13`; matching lesson implementation and tests linked in the individual research note.

### 14

A populated register can be marked ready for human review; external write requests require review; an empty register reports seven omissions. Readiness is a routing state, not ethical clearance or stakeholder consent.

Evidence: JSON key `chapters.14`; matching lesson implementation and tests linked in the individual research note.

### 15

An empty packet reports ten missing requirements. Ten files containing repeated x characters satisfy the structural checker. This counterexample establishes that length/presence checks cannot establish meaningful professional evidence.

Evidence: JSON key `chapters.15`; matching lesson implementation and tests linked in the individual research note.

## Scope decisions for drafting

- Preserve the one-to-one lesson mapping and the approved 5,000–8,000-word narrative specification. These notes are not a substitute for those manuscripts.
- Use the separate chapter 9 calculation for held-out results; do not claim the lesson demo already returns a training curve or held-out evaluation.
- Treat the chapter 8 server as a protocol teaching subset. A supported-version fallback is not inherently an error.
- Never promote finished, ready, structurally complete, or matching hash into truth, ethical approval, meaningful work, or authenticated consent.
- No live API runs were needed or purchased. All numerical examples must be labeled constructed.
- External source support is restricted to the claims in [sources](sources.md). Retrieved but unread material is not evidence.
- Companion manuscripts supply attributed supervisory practices, not automatically verified empirical findings. Use only a specifically read passage; omit an unsupported closing note. Do not invent human experiences or import broad claims of AI incapacity.
- Figures, authorial rewrite, external empirical anecdotes, and product-specific UI instructions are not approved by this packet.

## Remaining author decisions

Review this evidence and its exclusions at Gate 1 before narrative drafting under AI+1. The approved Blueprint is not reopened. Future added factual claims require their own sources; no agent has signed verification sidecars.

