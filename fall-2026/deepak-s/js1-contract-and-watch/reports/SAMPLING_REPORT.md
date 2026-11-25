# Sampling report (Chapter 1)

Model: claude-sonnet-5-5, through the Claude Code CLI 2.1.314 (`--judge claude-cli`, Amendment A14) · temperature: not set, because the CLI has no temperature flag · prompt: prompts/v1.md @ commit 7e76329 (sha256 24ea4522…) · dates run: 2026-10-30, 19:41:41Z to 19:42:33Z (15:41–15:42 ET)
"Fresh conversation" means each call was its own `claude -p` subprocess:
- with no prior messages and `--no-session-persistence`;
- started from a new empty temporary directory;
- with the System section as the whole system prompt, and no tools.

Drafted by Claude Code from saved results on 2026-10-30. Every verdict and count below comes from evidence/sampling/20261030T194141Z/results.json. Each call's request, raw stdout, meta and validator result are in evidence/sampling/20261030T194141Z/claude/<id>.<k>.*. Command: `python -m jobwatch sample --run evidence/runs/20261030T025837Z_stripe --posting-id 7983456 8144196 8174963 8175828 8191708 --resume examples/persona_resume.json --prompt prompts/v1.md --n 4 --judge claude-cli`, committed in 230cb5e. The smoke call in evidence/sampling/20261030T184652Z/ (posting 8172487, not among the 20) is not part of this report.

## About the hand labels
The 20 labels were made quickly by me. At least 7 of them contradict labels/LABELING_RULE.md as committed:
- 8174963, Staff Security Engineer, Abuse Control: relevant (Level: Staff)
- 8194283, PhD Data Scientist, Intern: relevant (Level: interns, PhD-required)
- 8148653, Staff Machine Learning Engineer, Financial Connections: relevant (Level: Staff)
- 8022713, ML Engineer Manager, AI Conversation Platform: relevant (Level: people managers)
- 7747640, Forward Deployed AI Accelerator, Marketing: relevant (Work: marketing)
- 8175661, Partner Marketing Manager, Online & Regional Events: relevant (Work: marketing, partnerships; Level: manager)
- 8198323, Solutions Engineer, AI Build Team: relevant (Level: a stated 7+ years, above the rule's 5)

Two more contradict it on location or stated years: 8144196 (Chicago) and 8197886 (6+ years). Every note is "work" except 7962437 ("location"). So the "agree with hand label" column below measures agreement with these labels, not correctness. Two of the five sampled postings (8174963 and 8144196) are on this list.

## Postings chosen and why
Selection rule, fixed before any sampling call:
1. Take the 10 development ids in labels/split.json.
2. Order them by note in labels/labels.csv: `unsure` first, then `level`, then `location`, then `work`.
3. Within each group, sort by id.
4. Take the first 5.

Every development note is `work`, so the rule picked the 5 lowest development ids.

| # | posting_id | title | why chosen (e.g. borderline) | my hand label |
|---|---|---|---|---|
| 1 | 7983456 | Machine Learning Engineer, Radar | selection rule (note `work`, lowest ids) | relevant |
| 2 | 8144196 | AI Engineer | selection rule (note `work`, lowest ids) | relevant |
| 3 | 8174963 | Staff Security Engineer, Abuse Control | selection rule (note `work`, lowest ids) | relevant |
| 4 | 8175828 | Account Executive, Product Sales - Currency Management | selection rule (note `work`, lowest ids) | not_relevant |
| 5 | 8191708 | Account Executive, Product Sales - Open Issuance | selection rule (note `work`, lowest ids) | not_relevant |

## Every verdict
All 20 calls were accepted by the validator. None was rejected, none errored, and every call exited 0 in 1 turn.

| posting_id | call 1 | call 2 | call 3 | call 4 | (more) | rejected by validator | agree with hand label |
|---|---|---|---|---|---|---|---|
| 7983456 | not_relevant | not_relevant | not_relevant | not_relevant | — | 0 of 4 | 0 of 4 |
| 8144196 | not_relevant | not_relevant | not_relevant | not_relevant | — | 0 of 4 | 0 of 4 |
| 8174963 | not_relevant | not_relevant | not_relevant | not_relevant | — | 0 of 4 | 0 of 4 |
| 8175828 | not_relevant | not_relevant | not_relevant | not_relevant | — | 0 of 4 | 4 of 4 |
| 8191708 | not_relevant | not_relevant | not_relevant | not_relevant | — | 0 of 4 | 4 of 4 |

## Spread
- **Verdicts:** no spread. Each posting got the same verdict on all 4 calls (4 of 4), with no flips.
- **Grounds:** they were stable too:
  - 7983456: every call cited the stated "5+ years" against the persona's 3.
  - 8144196: every call cited Chicago, outside the target locations.
  - 8174963: every call cited the Staff exclusion and 10+ years.
- **Citations changed even when the verdict did not.** Counting each call's exact citation list (source, path, value):

  | posting_id | distinct citation lists in 4 calls |
  |---|---|
  | 7983456 | 4 |
  | 8144196 | 2 |
  | 8174963 | 1 |
  | 8175828 | 3 |
  | 8191708 | 4 |

  For example, 7983456 cited `/targets/roles/0` in 2 calls and `/title` in 3. 8191708 cited `/work/0/highlights/0` once and `/years_experience` twice.
- **Reason wording** differed on every call, with the same grounds.

## What I can conclude / what I cannot
- **Can:** through this CLI, with a temperature that cannot be set, on 2026-10-30, v1 gave the same verdict 4 times out of 4 on each of these 5 postings. Every output passed the validator. The evidence behind a verdict varied more than the verdict did.
- **Cannot:** that the verdicts are right. Repeatability is not correctness. 8174963 got not_relevant 4 of 4 times, the opposite of my label. My label there contradicts my own rule (Staff), so in that case the repeated verdict matches the rule better than my label does. 7983456 got not_relevant 4 of 4 times even though my rule says a stated 5-year minimum fits. Being consistent did not make it agree with the rule.
- **Cannot:** generalise past n = 4 calls per posting, 5 postings, one model, one date and one prompt. The temperature cannot be set through the CLI, so I don't know what sampling setting produced this spread.
- **Cannot, from run 2:** run 2's 17 of 17 agreement between rule and judge (evidence/runs/20261030T195122Z_stripe/report.json) shows agreement on easy cases only. All 20 new postings were clear negatives under the rule:
  - 12 titles matched no target role;
  - 8 matched an excluded term (4 Manager, 4 Intern).

  The 17 accepted judgments all agreed with the rule, and the other 3 were rejected.
