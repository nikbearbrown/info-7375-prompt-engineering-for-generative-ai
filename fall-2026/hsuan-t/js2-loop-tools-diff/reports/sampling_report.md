# Sampling report (Chapter 1)

**Question:** if I ask Claude my prompt contract about the same posting several times, in fresh conversations, how much does the verdict move, and does a stable verdict mean a correct one?

## Setup

| | |
|---|---|
| Postings | 5, all from the **dev** set (`labels/split.json`), so the held-out set stays unseen for the prompt experiment |
| How they were chosen | Fixed rule, not by hand: every dev posting where the CONTRACT rule disagrees with my hand label (4), plus the one dev posting with an engineering title that I labeled not_relevant (1) |
| Tries | 4 per posting = 20 calls, each its own `claude -p` process (no saved session = a fresh conversation) |
| Judge | Same as the agent: prompt `prompts/claude_judge.v1.md`, model `claude-sonnet-5-5`, same validator |
| Postings' text | `evidence/raw/2026-10-31T214118Z/stripe_content.json` (Run 2 fetch, the one the labels came from) |
| Data | Every verdict: `reports/sampling/results.json`. Every reply as received: `reports/sampling/raw.jsonl`. Script: `reports/sampling.py` |

## Every verdict

| posting_id | Title | My hand label | CONTRACT rule | Claude try 1 | try 2 | try 3 | try 4 |
|---|---|---|---|---|---|---|---|
| 7235875 | Backend Engineer, Privy | relevant | not_relevant (check 2: "NYC-Privy") | relevant | relevant | relevant | relevant |
| 8131144 | Backend Engineer, Link | relevant | not_relevant (check 2: "NYC, Sea, SF, Tor") | relevant | relevant | relevant | relevant |
| 8301253 | Backend / API Engineer, Radar | relevant | not_relevant (check 2: "San Francisco, Seattle, New York") | relevant | relevant | relevant | relevant |
| 8072257 | Solutions Architect, Metronome (Startups) | relevant | not_relevant (check 1b: title) | not_relevant | not_relevant | not_relevant | not_relevant |
| 7913700 | Backend Engineer, Data | not_relevant (Canada) | not_relevant (check 2) | not_relevant | not_relevant | not_relevant | not_relevant |

All 20 replies passed the validator (0 rejected, 0 errors). Each call took 3.5–6.9 s.

## How much they vary

- **Verdict: no variation.** 5 of 5 postings got the same verdict in all 4 tries.
- **Justification: small variation.** The number of lines moved between 3 and 4 (7235875 try 3 left out the years line; 7913700 try 1 left out the skills line), and the order of lines changed between tries. The deciding reason did not change. For example, all 4 tries on 8072257 said "Solutions Architect is a customer-facing pre-sales role, not one of the target engineering roles", and all 4 on 7913700 cut it for Canada.

## Compared with my hand labels

| | Postings |
|---|---|
| Claude agrees with my label, 4 of 4 tries | 4 (7235875, 8131144, 8301253, 7913700) |
| Claude disagrees with my label, 4 of 4 tries | 1 (8072257) |
| The rule agrees with my label | 1 of 5 (7913700) |

## What I can conclude

- On these 5 postings, with prompt v1, Claude's verdict is **repeatable**: asking again did not change it.
- Where the rule and I disagreed because of location (3 postings in NYC / Seattle / SF), Claude read the location the way I do (those cities are in the US) and agreed with me every time. This is the rule's known limit (it matches words, not places), not chance.
- **Repeating is not being right.** 8072257 got the same verdict 4 times, and it is the opposite of my label. Asking more times would only have made a disagreement look more certain.

## What I cannot conclude

- That Claude is correct in general: 5 postings is very few, and they were picked on purpose to be the hard ones, not at random.
- Who is right on 8072257. My rule's step 1 says "engineer-related"; I counted a Solutions Architect as engineer-related, Claude reads it as a pre-sales role. That is a difference in judging the title, not a mistake one of us can be proven wrong about from the posting alone.
- That the verdict never flips. If a posting flipped 1 time in 10, four identical answers in a row would still happen about 66% of the time (0.9⁴ ≈ 0.66). Four tries can show instability; they can't prove stability.
- Anything about other models, other days, or a changed prompt: all 20 calls were the same model, the same prompt and the same evening (2026-10-31).
