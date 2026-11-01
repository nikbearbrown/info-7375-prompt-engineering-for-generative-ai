# Sample selection procedure (fixed before the sample was generated)

Written 2026-10-30 (EDT), after contract approval (17:30 EDT) and **before** `experiments/select_sample.py` was run. The procedure and seed are committed before any of the files it produces.

This is a **deliberately selected diagnostic sample**, not a representative sample of the board. It was chosen using the deterministic rule's own RECORD, so that both verdict classes and near-miss cases appear. It can't estimate how common relevant postings are, and agreement between Claude and the hand labels on it can't be generalised to the board.

**Pool:** all 903 postings in `evidence/snapshots/databricks_20261030T203900Z.json` (SHA-256 `22745f51…5299`).

**Seed:** `7375`, used with Python `random.Random(7375)`. Every draw happens in the order listed below.

1. Compute the RECORD (`agent.rules.evaluate`) for every posting in the pool, using `resume/priya-nair.resume.example.json`.
2. Put each posting in exactly one group:
   - **R** — RECORD `relevant`.
   - **N** (near-miss) — condition A passes, but the RECORD is `not_relevant`, because B or C fails or a field is missing.
   - **O** (other) — condition A fails.
3. Treat postings whose normalized titles are identical as one cluster of duplicates (for example, the same role advertised in several cities). A cluster is never split across dev and held-out.
4. **R:** take all R postings. Of all the ways to give each R cluster to dev or held-out, keep those that put exactly 3 postings in dev and 2 in held-out. Sort them, then draw one with `rng.choice`. If none exists, take the split closest to 3/2 and record the adjustment.
5. **N:** remove any cluster already used. Sort the remaining N cluster keys, draw 7 with `rng.sample`, and take one posting from each with `rng.choice` over sorted ids. Shuffle those 7 with `rng.shuffle`: the first 3 go to dev and the other 4 to held-out.
6. **O:** do the same for 8 clusters from O. Shuffle them: the first 4 go to dev and the other 4 to held-out.
7. Shuffle each split's sheet order with `rng.shuffle`, so the order says nothing about the groups.
8. Write these outputs:
   - `experiments/sample/manifest.json` — ids, groups and hashes. **The labeler should not open it until labeling is finished.**
   - `experiments/sample/dev_postings.json` and `experiments/sample/heldout_postings.json` — the original posting objects, unchanged.
   - `labeling/dev_sheet.md`, `labeling/heldout_sheet.md`, `labeling/dev_labels.csv` and `labeling/heldout_labels.csv` — no groups, RECORDs or model output.

**Sealing:** held-out postings and held-out labels are not read during prompt development. Claude (the assistant building this project) does not display or inspect them. The prompt-evaluation script refuses `--split heldout` until `prompts/FROZEN.json` exists and its hashes match the prompt files. The held-out labels file is committed when received, and its SHA-256 hash is recorded. A content hash identifies a version of a file; it does not prove when that version existed. The git commit history is the timing evidence.

**Sampling experiment (Chapter 1):** five dev postings, chosen with `random.Random(7375 + 1)` from the dev split: 2 from R, 2 from N and 1 from O (fewer if a group has fewer).
