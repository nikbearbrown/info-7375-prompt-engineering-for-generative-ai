# FACTCHECK — "A Slogan Is a Division"

One row per claim that appears on screen or in narration. Every numeric claim is
reproducible offline; nothing here was estimated, remembered, or asked of a model.

**Reproduce everything in this table:**

```bash
cd <course repo>
python research/llm_scale.py          # every number in rows 3-9
```

Environment of record: Python 3.13.3, Windows 11, 2026-09-26.
The chapter's own saved run used Python 3.14.6; my figures match it exactly.

| # | Beat | Claim as stated | Status | Source / how verified |
|---|---|---|---|---|
| 1 | B00 | "It would take a person thousands of years to read everything GPT-3 was trained on" | **ATTRIBUTED, not asserted** | Presented as a circulating slogan, which is what the film then audits. Chapter 1, "Scale, in units you can check": "You have probably heard the reading comparison." I do not claim it as my own measurement. |
| 2 | B01 | The comparison is a division, not a measurement | **ARGUED** | This is the film's thesis, established by rows 3-7 rather than asserted. Chapter 1: "The headline figure is not a measurement. It is a division." |
| 3 | B02 | GPT-3: 175,000,000,000 parameters | **VERIFIED** | Brown et al. 2020, *Language Models are Few-Shot Learners*, arXiv:2005.14165. Echoed in `llm_scale.py` → `cited.gpt3_parameters`. Reported by the authors; not re-measured by me. |
| 4 | B02 | GPT-3: ~300,000,000,000 training tokens | **VERIFIED** | Same source → `cited.gpt3_train_tokens = 300000000000`. |
| 5 | B02 | GPT-3: 3.14 x 10^23 FLOPs training compute | **VERIFIED** | Same source → `cited.gpt3_train_flops = 3.14e+23`. |
| 6 | B03 | 300e9 tokens x 0.75 words/token = 225e9 words | **VERIFIED** | `assumptions.words_per_token = 0.75`; asserted at build time in `build_beats.py` (`assert abs(words - 225_000_000_000) < 1`). The 0.75 figure is the chapter's stated assumption, and the film says so. |
| 7 | B03 | 225e9 / (250 wpm x 525,960 min/yr) = 1,711.2 years | **VERIFIED** | `reading_years_by_rate["250"] = 1711.2`. Independently re-derived in `build_beats.py` and asserted to within 0.5 yr. 525,960 = `assumptions.seconds_per_year` (31,557,600) / 60. |
| 8 | B04 | 150→2851.9, 200→2138.9, 250→1711.2, 300→1426.0 years | **VERIFIED** | `reading_years_by_rate`, read live at build time. Values are not typed into the beat sheet by hand; `build_beats.py` inserts whatever the script prints. Chapter prose quotes three of these rounded (2,852 / 2,139 / 1,711); the 300 wpm row is in the script but not the prose. |
| 9 | B04 | The answer moves by more than 1,400 years | **VERIFIED** | 2851.9 − 1426.0 = **1,425.9**. Narration deliberately says "more than fourteen hundred", not a false-precision figure. Asserted at build time (`assert spread > 1400`). |
| 10 | B05 | GPT-3 compute = ~9.95 million years at 1e9 ops/sec | **VERIFIED** | `compute_years_at_one_billion_per_second = 9950059.57`. |
| 11 | B05 | "Over 100 million years" implies ~3.16e24 FLOPs, ~10x GPT-3 | **VERIFIED** | `flops_implied_by_one_hundred_million_years = 3.15576e+24`; 3.15576e24 / 3.14e23 = **10.05**. Asserted at build time (`assert 9 < ratio < 11`). |
| 12 | B06 | This does not establish the comparison is false or useless | **ARGUED — the stated boundary** | Required by the assignment. Chapter 1 agrees: "That does not make the comparison useless — every version of it says *more text than a person could read in many lifetimes*, which is the actual point." |
| 13 | B06 | None of this is evidence about the truthfulness of model output | **ARGUED** | Follows from the scope of the arithmetic: the division's inputs are token counts and reading rates. Correctness of generated text is never one of its arguments. |

## Constructed vs. real

- **No Claude transcript appears in this video.** Nothing was generated, screenshotted,
  or reconstructed from a model. The Claude-style composer frames in B00 and B07 are
  the toolkit's own `ClaudeComposerAsk` component rendering *my* typed question — they
  are a title device, not a claim that Claude was asked anything or answered.
- **No constructed distributions or illustrative fake data.** Every number on screen is
  printed by `research/llm_scale.py`.
- **Not re-measured by me:** the three published GPT-3 figures (rows 3-5). I take them
  from Brown et al. as reported, and the card says "Reported by the authors".

## What I did not check

- Whether 0.75 words/token is accurate for GPT-3's actual tokenizer. It is the chapter's
  stated assumption, used to keep my arithmetic comparable to the chapter's. If it is
  wrong, every years figure scales with it — which is itself an instance of the film's
  own point, and is the reason the film names the assumption out loud.
- Any figure for models after GPT-3. The film says these are "frequently undisclosed"
  and makes no claim about them.
