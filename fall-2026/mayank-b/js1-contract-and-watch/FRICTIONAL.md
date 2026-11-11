# FRICTIONAL: honest build log (Job-Search Agent 1)

Dates are local. Each entry: what I tried → what broke or surprised me → what I did instead. Write each entry the same day, right after the session (5 minutes), with the commit, prompt, or test that proves it.

<!-- Template structure from Claude (2026-10-24); every entry below is mine. Same format as my week-01-video FRICTIONAL.md. Grading (10 pts): specific attempts and outcomes; what I checked,
     changed, or learned, including what is still unresolved; what I accepted, modified, or rejected from Claude;
     traceability (commit hash, prompt file, test name). Never reconstruct entries later; never invent struggle. -->

## YYYY-MM-DD: <session topic>
- **Tried:** ...
  **Happened:** ... (evidence: commit `abc1234` / `tests/xyz.test.js` / `prompts/v1.md`)
  → **Did instead:** ...
- **From Claude:** accepted ... / changed ... because ... / rejected ... because ...
- **Unresolved:** ...

## 2026-10-29: labels, sampling, dev experiment, action surfaces
- **Tried:** `npm run experiment` (v1 and v2 on dev) and `npm run sample` from the guide.
  **Happened:** both failed before any Claude call: the labels file was missing (`labels/labels.json`; `scripts/experiment.js` stops with a usage error), and the guide gave the wrong run folder (`run-01-2026-10-28`; my run #1 is `runs/run-01-2026-10-29/`). I was confused initially.
  → **Did instead:** asked Claude to check what failed; it wrote `labels/labels.json` from my labels and re-ran with the right path: v1 dev 5/12, v2 dev 8/12 (`reports/experiment-judge-v1-dev-2026-10-29.json`, `reports/experiment-judge-v2-dev-2026-10-29.json`); sampling `reports/sampling-judge-v1-2026-10-29.json`.
- **Tried:** judging the same posting, Data Engineer, Product (5448481008), three ways: chat paste, file read (Claude Code in this folder), agent.
  **Happened:** the same job got three different answers depending on how I asked: chat said not relevant, file read and agent said relevant. That surprised me. (evidence: `notes/my-answers-2026-10-29.md`, `reports/sampling-judge-v1-2026-10-29.json`)
  → **Next time:** I would spend more time for human review of the result and writing labels/rules if i didnt have the time constraint.
- **From Claude:** accepted flipping 5 labels that broke my labeling rule (3 Applied AI roles to not relevant, Security Data Engineer to relevant); kept my own dev/held-out split (12 dev / 8 held-out) instead of rebalancing to 10/10; kept Option A as my labeling rule unchanged (my reason is in `notes/my-answers-2026-10-29.md`).
- **Unresolved:** held-out ran once with `--final` (v1 6/8, v2 6/8; `reports/experiment-judge-v1-heldout-2026-10-29.json`, `reports/experiment-judge-v2-heldout-2026-10-29.json`); the split is 12/8, not 10/10; Data Scientist, Product went 2-2 in sampling, so its v1-to-v2 change may be chance.
