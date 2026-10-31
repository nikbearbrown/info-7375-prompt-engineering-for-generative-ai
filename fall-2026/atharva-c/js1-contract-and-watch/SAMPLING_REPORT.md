# Sampling report (Chapter 1)

*Drafted by Claude Code from the committed evidence. Review by Atharva C.:
PENDING. Every number below comes from `logs/sampling.jsonl` (commit
13e0832).*

## What ran

On 2026-10-30, between 07:46:34 and 07:48:00 UTC, I asked Claude
(`claude-sonnet-5-5`) the baseline prompt contract (`prompts/baseline.txt`)
about 5 postings, 4 times each: 20 calls. Each call was a separate,
tool-less `claude -p` session run from an empty folder. The log shows 20
distinct session ids. Command:

```bash
python3 -m tools.sample --ids 7776179 7557899 8241260 8175647 8197135 --times 4
```

The 5 postings were chosen because they looked most likely to make a model
waver: my one "relevant" label, a mixed Toronto + US location, the
high-school internship, a plain "Remote" location, and one I labeled
"unsure".

## Every verdict

| posting | title | my label | Claude, 4 fresh calls | agree with me |
|---|---|---|---|---|
| 7776179 | Security Engineer, Bridge | relevant | not, not, not, not | 0/4 |
| 7557899 | Backend Engineer, Developer SDKs | not relevant | not, *invalid*, not, not | 3/4 |
| 8241260 | High School Internship, Software Engineering | not relevant | not, not, not, not | 4/4 |
| 8175647 | Integration Engineer (Metronome) | not relevant | not, *invalid*, not, not | 3/4 |
| 8197135 | Software Engineer, High Availability and DR | not relevant | not, not, *invalid*, not | 3/4 |

*invalid* = the validator rejected the output. All 3 rejections had the same
cause: Claude cited `resume.work_experience_years`, a field that doesn't
exist. The raw verdict inside each rejected output was also "not relevant".

## How much they varied

- **Verdict: no variation.** 20 of 20 raw verdicts said "not relevant".
- **Format: some variation.** 3 of 20 outputs (15%) broke the contract by
  inventing a field. Counting the prompt experiment's 20 baseline calls as
  well, the baseline prompt invented a field 5 times in 40 calls.

## What I can conclude

- On these 5 postings, on this model, on this day, Claude's verdict was
  repeatable.
- Repeatable is not correct. On 7776179 Claude disagreed with my hand label
  4 times out of 4, each time for the same stated reason: the posting asks
  for 8+ years. My labeling rule ignores required years. That's a real
  difference between my rule and Claude's judgment, not noise.
- The 4/4 and 3/4 "agreements" only show that Claude and I both said no.

## What I cannot conclude

- How Claude behaves on true borderline cases. By Claude's own reasons, all
  5 postings were clear "no" cases (years required, high school only), so
  there was nothing to waver on.
- Anything about other models, other days, or more than 4 samples per
  posting. Four identical answers is consistent with a model that would
  flip one time in ten.
- That the validator catches every bad output. It checks that cited fields
  exist, not that they are the fields the reason actually depends on.
