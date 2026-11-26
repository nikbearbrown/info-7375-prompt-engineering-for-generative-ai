# What moves the score (brief Step 2.4)

The plan was committed before any variant was scored: [experiments/PLAN.md](experiments/PLAN.md), commit `77827f07`. Scores: [output/experiments/scores.json](output/experiments/scores.json), with a per-posting breakdown.

## Where every number came from

| Number | Value | Origin |
|---|---|---|
| G1 title exclusions | 15 words | **inherited**: JS1 CONTRACT.md Appendix A (Siddi) |
| G2 seniority words | 9 words | **inherited**: JS1 |
| G3 years cap | 4 (= 2 years + 2) | **inherited** from JS1, reconfirmed by **Siddi's decision** 2026-11-25 |
| G3 years regex, 25-character degree window | — | **inherited**: JS1 |
| R1 role words | 7 phrases | **inherited**: JS1 `target_title_keywords` |
| R1 weight | +3 | **hand-set** (Claude's draft, approved by Siddi) |
| R2 skills and aliases | 12 skills | **inherited**: JS1 persona and vocab |
| R2 weight and cap | +1 each, at most 4 | **hand-set** |
| R3 topic words | 10 words | **hand-set** ("ai" turned out to be a false friend; AUDIT.md) |
| R3 weight | +1 once | **hand-set** |
| `keep_threshold` | 4 | **hand-set**, then **fitted** on the 13 audit postings that reached scoring. The best value was 4 with 3 errors, the same as hand-set (`output/experiments/fitted_threshold.json`). |
| v1.1 `us_place_names` | 14 names | **hand-set** from the collection's location strings, no labels used. **Adopted after** measuring on held-out labels. |
| Stripe boilerplate | 1 cut heading, 1 dropped sentence | **inherited**: JS1 boilerplate v2 |
| Shortlist size | 10 | **hand-set** |
| Collection budget | 30 requests, 120 s | **Siddi's decision**, 2026-11-25 |
| Per-request timeout, retries | 20 s, at most 3 attempts | **inherited**: JS2 GATE |
| Claude judge prompt | `judge_v1` | **inherited**: byte-identical to JS1 (sha256 `9d54e729…`) |
| Judge text limit | 6,000 characters | **inherited**: JS1 |
| Model | `claude-sonnet-5-5` | **inherited**: JS1's pinned model |
| Claim prompts | `justify_v1`, `label_claims_v1` | **hand-written** by Claude for JS3; not tuned on any labels |
| Claims per posting; claim text limit | 4–7; 12,000 characters | **hand-set** |
| Sample seeds; sample sizes | 7375, 7376; 30 rejects, 12 + 8 held-out | **hand-set** (30 is the brief's minimum) |

Only one number was fitted on labels, and the fit returned the value it already had.

## One change at a time, on held-out labels

H is 29 unique postings, and Siddi labelled 15 of them relevant:
- 19 come from the blind sheet's held-out groups. These labels are from 2026-11-25 and were never used to choose a change.
- 10 are JS1's held-out postings, labelled 2026-10-31.
- One posting was in both groups. It is scored once, with its JS1 copy and label. This was found after the run.

| Object changed | Variant | Agrees with Siddi | Kept and relevant | Kept, not relevant | Missed relevant | Correctly left out |
|---|---|---|---|---|---|---|
| (filter baseline) | filter v1 | 15/29 | 1 | 0 | 14 | 14 |
| the filter file | **v1.1** (US place names) | **17/29** | 3 | 0 | 12 | 14 |
| the filter file | v1.2 (drop Notion blurb) | 15/29 | 1 | 0 | 14 | 14 |
| (Claude baseline) | B: judge_v1, sonnet, no tools | 15/29 | 1 | 0 | 14 | 14 |
| the prompt | P: judge_v2 (JS1's seniority sentence) | 15/29 | 1 | 0 | 14 | 14 |
| the context | C: plus Siddi's LABELING.md answers | 15/29 | 1 | 0 | 14 | 14 |
| the tool list | T: plus `score_posting` | 15/29 | 1 | 0 | 14 | 14 |
| a setting | S: `claude-haiku-5-5` | 15/29 | 1 | 0 | 14 | 14 |

All 150 Claude calls returned valid output on the first try (2026-11-26; reported cost $2.12 in total). **Every Claude variant gave the same verdict on every posting.**

## What the numbers do and do not show

- **v1.1 fixed exactly the two misses it was built for:** "AI Engineer | Chicago" and "Machine Learning Engineer, Radar | Seattle". It added no false keep. That is 2 postings, and it is the whole case for adopting it.
- **12 of the 15 relevant postings in H can't be reached by any change tested here.** They are sales, solutions or manager titles, are outside the US, or have no usable location ("Payments Analyst | LOCATION"). FILTER.md and Jordan's persona exclude all of these by design (AUDIT.md, "two standards"). So no variant could agree on more than 17 of 29, and v1.1 reached that.
- **No Claude change moved a verdict, but some changed the reasons:**
  - **Context (C):** justifications that mention "preferred" cities dropped from 14 of 30 (B) to 5 of 30. C's justification for the Chicago AI Engineer says "Chicago is not a preferred city, though USA is OK". The verdict stayed "not relevant" because of "4+ years". C also read Siddi's "2+years" literally, as a stricter limit than FILTER.md's 4.
  - **Tool list (T):** Claude called the tool in 7 of 30 judgments (counted from the 29 server transcripts in `evidence/experiments/T/`; the duplicated posting shares one transcript file). In 1 justification (ML Engineer, Radar) it wrote that the filter's location rejection "looks wrong". The tool's record did not pull Claude toward the filter.
  - **Setting (S):** Haiku agreed with Sonnet on all 30.
- **Read with care.** H is small, and most of it is decided by titles and locations, so these variants were tested on easy postings. "No verdict changed on H" does not show the changes do nothing on borderline postings; H had almost none.

## What persistence is not proof of

- Every Claude call above started in a new, empty temporary directory, with `--no-session-persistence`, `--setting-sources project` and built-in tools off. No call could see another's output.
- When a variant behaved differently, the difference came from what was **sent** with that call: the prompt, the context, the tool list, or the model setting.
- Nothing was trained: no weights changed, and nothing was learned between calls.
- If a behaviour seems to "stick" across sessions, the honest explanation is something we sent again, such as a file, a prompt, a `CLAUDE.md`, or a tool result. A repeated behaviour across sessions shows a repeated input, not training.
