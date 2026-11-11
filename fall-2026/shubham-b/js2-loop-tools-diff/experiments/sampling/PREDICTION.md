# Sampling prediction (written before the run)

Committed before `uv run jsa exp sampling run --n 4`; the commit timestamp is the evidence it came first.

> **Prediction (before running `jsa exp sampling run --n 4`):** Across 4 fresh `claude -p` (`judge.v1`) calls per posting, I predict high label repeatability on the clear rejections (`7543868`, `8175099`, `8127182`), systematic disagreement with my `MATCH` hand label on `8249901` (where Claude will repeatedly say `NOT_RELEVANT` due to the 3+ years and tier-0 infrastructure requirements that the deterministic rule does not gate on), potential label split or false-positive `RELEVANT` calls on `8234357` (where location is `"N/A"` and `judge.v1` does not state that unestablished locations must fail), and substantial call-to-call variation in the cited `evidence` JSONPath sets even when the binary label is unanimous.

— Shubham Bagwe, 2026-10-30
