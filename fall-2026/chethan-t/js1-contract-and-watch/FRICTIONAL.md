# FRICTIONAL — Job-Search Agent 1

An honest log of what I tried, what happened, and what I changed.

## 2026-10-31 — First contract draft, then restart

**What I tried.** I wrote a first `CONTRACT.md` by answering questions from
Claude (claude.ai chat) one section at a time: In, Out, Refuses, the rule,
wrong versions, and a failure sentence. Claude offered multiple-choice
options; I picked or wrote my own answers, and Claude turned them into
contract wording.

**What I accepted, modified, or rejected from Claude.**
- Rejected Claude's sample persona (Rohan Desai, a new grad) because I have
  about 3 years of experience and wanted a persona closer to how I judge
  jobs. Accepted Claude's draft of a fictional persona (Arjun Mehta) instead.
- Wrote my own role-title list instead of choosing Claude's options.
- Wrote my own condition for Senior/Lead titles (allowed only if required
  experience is 3 years or less).
- First chose a three-value verdict (relevant / not relevant / unsure);
  dropped "unsure" after checking the assignment only asks for two values.
- Claude added "as a whole word" to the US location check when assembling
  the contract, so the rule matches my Brussels wrong-version test.

**What happened.** After reading the assembled contract, I felt the first
version fell short. I had answered the questions quickly and hadn't thought
enough about each one.

**What I changed.** I'm restarting contract-first. The first draft is kept
for reference as `CONTRACT_v1.md`, and I'm revising my answers before any
code is written.

**Unresolved.** Which answers will change in the revision.

**Trace.** Revised contract (v2): `046b749` (2026-10-31 17:07). v1 draft
added for reference in `b938a14` (2026-10-31 17:18). Git shows v1 committed
after v2 because I only saved v1 as a reference copy after deciding to restart.

## 2026-10-31 — Rebalanced the labels

**What happened.** After labeling, 19 of 20 postings were `not_relevant`,
too few positives to measure anything. **What I changed.** Replaced 3
non-engineering rows with entry/mid-level US software roles before any
Claude run; only 3 distinct such roles existed on the board, so 1 went to
dev and 2 to held-out (`7617ffe`). Old set kept as
`experiment/labels_v2_unbalanced.csv`. Labeled the 3 new rows (`0531149`).

## 2026-10-31 — Predicted failure happened: rule 18/20

**What happened.** The rule agreed with my labels on 18 of 20 (dev 10/10,
held-out 8/10). Both misses were held-out postings the rule marked
`relevant` and I marked `not_relevant`: 7727703003 (Full Stack Software
Engineer - People Systems) and 7792539003 (Mobile Developer -
Android/Kotlin). My labeling rule includes skill overlap; the contract's
rule has no skills check. **Unresolved.** Whether to add a skills check.

## 2026-10-31 — Fenced Claude replies

**What happened.** 3 of 40 baseline-prompt calls (1 in sampling, 2 on
held-out) wrapped the JSON in a ```json fence and were rejected as
"no Claude verdict"; the verdict inside matched my label each time.
The same happened in 1 of 3 calls in the SEEDED run and in the way 2 reply.
**What I kept.** Fenced replies stay rejected (strict contract).

## 2026-10-31 — Revision prompt result

**What I tried.** One change: "Do not use markdown or code fences. Start
your reply with { and end with }." (`54d1a26`). **What happened.** Dev
10/10, 0 invalid (`fa48df0`); held-out revision 10/10 vs baseline 8/10,
both baseline failures fenced (`7d8a647`). **Unresolved.** With 1 relevant
held-out posting and 3 fenced replies in 40, I can't claim it is reliably
better. The agent still uses `prompts/baseline.txt`.

## 2026-10-31 — Seeded second run

**What happened.** A second calendar day was not available before the
deadline. **What I did.** Replayed the saved baseline response with 3 ids
removed from a copy of the seen file (`--replay`, `9d65674`); the agent
reported exactly those 3 as new (`396a46e`). Labeled SEEDED everywhere;
see `seeded_run/SEEDED.md`.
