# FACTCHECK — Expected 665.24, Observed 630

Every factual claim in the narration or on screen, with its source. "Computed" means arithmetic on main.py's printed values, done in `scenes.py` at render time.

| Beat | Claim | Verdict | Source |
|---|---|---|---|
| B00, B03 | Token 2 probability is 0.6652409557748218 | OK | `main_output_2026-09-27.txt` (main.py, Python 3.11.9, course repo b293224) |
| B00, B03, B09 | Expected count 665.24 = 1000 × 0.6652409557748218 | OK, computed | same; Chapter 1 line 249 ("about `665.24`, an expected count under the distribution") |
| B00, B04, B09 | Observed count for token 2 is 630 | OK | `main_output_2026-09-27.txt`; Chapter 1 line 249/256 |
| B01 | "The code predicts 665…" is a misconception, corrected on screen | OK, **constructed example** (labelled) | Chapter 1 line 249 ("the program is not instructed to return the nearest integer… It samples.") |
| B02 | Scores 1, 2, 3 become probabilities 0.0900 / 0.2447 / 0.6652 | OK | `main_output_2026-09-27.txt`; code excerpt is main.py lines 9, 14–17, 19, 22–24 verbatim |
| B02 | "about sixty-six and a half percent" | OK (0.6652 → 66.5%) | same |
| B02 | Generator seeded with seven makes a thousand weighted draws | OK | main.py `sample(logits, count=1000, seed=7…)`, `random.Random(seed)`, `rng.choices(…, k=count)` |
| B03 | Expected count = average number of token twos across many runs of 1000 draws | OK | definition of expected value of a count; Chapter 1 line 249 |
| B03 | 665.24 isn't an integer, so no single run can land on it | OK | Chapter 1 line 249 ("It cannot be a literal observed count because a count is an integer.") |
| B03 | Other expected counts 90.03 / 244.73 | OK, computed | 1000 × 0.09003057317038046, 1000 × 0.24472847105479764 |
| B04 | The draws shown are the real seed-7 sequence | OK | `evidence/seed7_sequence.json` via `evidence/seed7_sequence.py` (same call as `sample()`; counts asserted equal to main.py and to `sample()`) |
| B04 | First draw is token 1; token 2 first appears on draw 3 | OK | `seed7_sequence.json`: first 20 = 1, 1, 2, 0, … |
| B04 | Nothing reserves a quota; each draw weighted and independent | OK | Chapter 1 line 247 ("does not allocate a fixed quota… performs weighted selections") |
| B04 | Final counts 102 / 268 / 630 | OK | main.py output; asserted in `scenes.py` against the sequence |
| B05 | Gaps +11.97 / +23.27 / −35.24; "about twelve / twenty-three / thirty-five" | OK, computed | counts − expected; spoken values are rounded, exact values on screen |
| B05 | Gaps cancel because both rows total 1000 | OK, computed | 90.03 + 244.73 + 665.24 = 1000 = 102 + 268 + 630 |
| B05 | Assigned p 0.6652 vs observed share 0.630 | OK | Chapter 1 line 259 |
| B06 | Re-run with seed 7 on this machine gives 630 again, byte for byte | OK | `evidence/main_output_rerun_2026-09-27.txt`; `fc /b` no differences; SHA-256 computed live in `scenes.py` from both files |
| B06 | The course's own test is **not** cited | Checked | `test_04` tests `sample([1, 2])`, not `[1, 2, 3]` (FRICTIONAL.md Entry 8) |
| B07 | One seed-7 run can't show whether a 35.24 gap is typical; a criterion must be decided first | OK | Chapter 1 line 261 ("You first need an acceptance criterion appropriate to the experiment.") |
| B07 | Axis, its ±60 extent and the empty slots | **constructed** (labelled on screen) | no data; only the −35.24 point is real |
| B08 | The snippet runs as shown, from `lessons/01-randomness-and-first-prompts/code` | OK | `evidence/b08_your_turn_snippet.py`, exit 0, 20 well-formed lines; output **not** shown (`evidence/b08_snippet_check_2026-09-27.txt`) |
| B09 | Course repo b293224, run 2026-09-27; narration is synthetic | OK | `BUILD-PROMPT.md` Step 2; Kokoro af_bella |
