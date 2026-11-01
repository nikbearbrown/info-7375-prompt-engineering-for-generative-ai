# Prompt experiment procedure (pre-registered)

Written by Claude (WS4 coding agent) on 2026-10-29 from PLAN.md §6.2, before
`jsa exp prompt select` has run. `select` refuses to run until this file is committed,
and it records this file's SHA-256 in `data/experiments/prompt/selection.json`.

## Question

How often do Claude's first replies agree with the student's hand labels under prompt
v1, and does changing exactly one section of the prompt (v2) change that? Agreement is
with the written rule (CONTRACT.md §16: `RELEVANT` = `MATCH`, `NOT_RELEVANT` =
`NO_MATCH`), not with whether a job is desirable.

## Source

- The committed hand-check raw file
  `evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json`, SHA-256
  `74e20e05ef2261864f89b8d95ab8673454c38cbbf16860d8e9f524f7f31082fd`. `select` refuses
  a file with any other digest.
- The five CONTRACT.md §13 postings (8249901, 7543868, 8175099, 8127182, 8234357) are
  excluded because they are the sampling set.

## Strata and quotas

Each remaining posting is evaluated by the built rule at the commit recorded in
`selection.json` and placed in at most one stratum:

| Stratum | Definition | Quota |
|---|---|---|
| M | rule verdict MATCH | 8 |
| N1 | title pass, at least 2 skills, location label not US_BASED | 4 |
| N2 | title pass, fewer than 2 skills | 4 |
| N3 | title fail, at least 2 skills, location label US_BASED | 4 |

Postings in no stratum are not sampled. If any stratum has fewer candidates than its
quota, `select` fails loudly and nothing is written.

## Draw and split

1. One `random.Random(20261029)` is used for the whole draw, in this order.
2. For each stratum in the order M, N1, N2, N3: sort the candidates by numeric ID,
   draw the quota with `rng.sample`, shuffle the draw with `rng.shuffle`, and put the
   first half in dev and the second half in held-out.
3. Shuffle the dev IDs, then the held-out IDs, with the same generator. That is the
   worksheet order.
4. Dev and held-out each get 4 M + 2 N1 + 2 N2 + 2 N3 = 10 postings.

## What `select` writes (under `data/experiments/prompt/`)

- `selection.json`: the IDs of each set, the seed, this file's digest, the raw file's
  digest, the code commit and the digest of `strata.json`. It contains no strata and
  no verdicts.
- `strata.json`: each selected posting's stratum and the rule's verdict and failed
  gates. **Do not open it until `score`.** A self-run study cannot truly blind the
  person running it; this is a stated limitation.
- `worksheets/{dev,heldout}.md`: ID, title, `location.name`, departments, URL and
  cleaned content, with blank fields to fill. No verdict and no stratum is shown.
- `label-templates/{dev,heldout}.labels.json`: blank label files with the IDs filled
  in. Copy each over `experiments/prompt/labels/<set>.labels.json` and fill it in.

Do not run `jsa rule` on any experiment posting before `seal`.

## Hand labels

Label every posting with the CONTRACT.md §6 rule exactly as written (§16). Each entry
records `hand_label` (`MATCH`/`NO_MATCH`), `title_pass`, the matched `skills` (term,
résumé path, posting path), the `exclusion_phrase` found (or `null`), the
`location_label` and `notes`. `labeled_by` names the labeler. `seal` rejects a file
whose `hand_label` does not follow from its own recorded gates under §6.5.

## Command order

Each step is checked against git (tracked and unchanged since commit):

1. `uv run jsa exp prompt select` — once; refuses if a selection exists.
2. The student fills both label files by hand.
3. `uv run jsa exp prompt seal` — validates all 20 labels and writes `SEAL.json`
   (SHA-256 of both label files and `selection.json`). **Commit the labels and
   `SEAL.json` before any model call.** The commit time is the seal.
4. `uv run jsa exp prompt run --prompt v1 --set dev` — refuses unless SEAL is
   committed and its hashes match. Runs once.
5. The student reads the v1 dev results, picks one of the candidates pre-registered in
   `prompts/CHANGELOG.md`, writes `prompts/judge.v2.md` and records the choice there.
6. `uv run jsa exp prompt freeze` — needs the v1 dev results and a v2 that differs
   from v1 in exactly one marked section; checks that v1 is the file used by the v1
   dev run and by the sampling report. Writes `FREEZE.json`. **Commit it.**
7. `uv run jsa exp prompt run --prompt v2 --set dev` — refuses unless FREEZE is
   committed and both prompt digests equal FREEZE. There is no iteration on v2.
8. `uv run jsa exp prompt run --prompt v1 --set heldout`, then
   `uv run jsa exp prompt run --prompt v2 --set heldout` — each refuses unless FREEZE
   is committed, the prompt digests equal FREEZE, both dev cells exist and that cell
   has not run.
9. `uv run jsa exp prompt score` — re-verifies the SEAL hashes, reveals the strata and
   writes `metrics.json` and `PROMPT_EXPERIMENT.tables.md`.

Each (prompt, set) cell runs once: a `STARTED.json` marker is written before the first
call, so a crashed cell is not silently re-run.

## Calls

One call per posting per cell, prompt on stdin, a fresh `claude` process per call
(PLAN amendment R1 argv), and **no retry**: the first reply is the one scored. Each
call's raw envelope is logged under `results/<prompt>-<set>/calls/<id>/attempt-1.json`.

## Metrics (first reply only, n = 10 per cell)

- Format acceptance: validator pass rate, k/10. Never called accuracy.
- Agreement with the hand label: k/10 with an invalid reply counted as a
  disagreement, and separately k/valid.
- Evidence-path validity: the fraction of evidence entries in parseable replies whose
  two paths both exist, and the number of replies with at least one bad path.
- A 2×2 confusion matrix (hand × Claude), with invalid replies counted separately.
- A Wilson 95% interval for every k/n.
- v1-vs-v2 discordant postings, listed by ID and stratum.
- A rule-vs-hand audit: every posting where the hand label differs from the code's
  verdict. Each is either a labeling slip or a rule bug; the student decides which.

## Limits

- One posting moves a rate by 10 points.
- One call per cell ignores the sampling variance measured in the sampling report.
- Both sets come from one board on one day.
- The stratified mix is not the board's base rate.
