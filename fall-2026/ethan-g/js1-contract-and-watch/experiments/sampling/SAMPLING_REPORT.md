# Sampling report (Chapter 1)


**Setup.** Five postings: the first 5 of the dev split from `experiments/common.py` (seeded, not picked by hand).
Prompt: `prompts/judge_v1_baseline.txt`. Model: `claude-sonnet-5-5`. Persona: Evan Gordon (fictional). Each call is
a separate `claude -p` process with `--no-session-persistence` and no tools, so there is no shared conversation between
calls. The whole posting is sent (up to 20,000 characters, after the Run-2 truncation fix). Every call's raw output,
validator result, session id, cost, and timestamp are in `results.jsonl`.

## Results

| posting | title | calls | relevant | not_relevant | rejected/error | hand label | agree w/ hand |
|---|---|---|---|---|---|---|---|
| 7782805 | Staff Software Engineer (L4) Data Platform | 4 | 0 | 4 | 0 | not_relevant | 4/4 |
| 8047150 | Staff Analytics Engineer | 4 | 0 | 4 | 0 | not_relevant | 4/4 |
| 7992889 | Software Engineer - Data Platform | 4 | 0 | 4 | 0 | not_relevant | 4/4 |
| 8485884002 | Senior Data Engineer | 4 | 4 | 0 | 0 | relevant | 4/4 |
| 8299493002 | Senior Data Engineer, Ads | 4 | 0 | 4 | 0 | relevant | 0/4 |

20 calls, 20 passed the validator, 0 truncated, total reported cost $0.216. The CLI reported usage for `claude-sonnet-5-5` (the requested judge model) and
`claude-haiku-5-5` (used internally by Claude Code).

## What varied

- How many postings got the same verdict on all 4 calls: **5 of 5.**
- How many outputs the validator rejected, and why: **0 of 20.**
- Did the cited `resume_fields` vary even when the verdict didn't? **Yes, on every posting.** The 4 calls cited 2, 2, 4, 3, and 2 different sets of résumé fields
  (postings in table order). The verdict was stable, but the stated evidence wasn't.
- On 8299493002, all 4 calls rejected for the same reasons ("5+ years of ad-tech", lead/mentor scope). The posting's 5+ years is general ("writing
  production code and architecting data pipelines"), not ad-tech. So the calls repeated the **same misreading** four times.
- Outside this sample, the watch's Run 2 judged Samsara 7922530 eight times (one call per version): 5 relevant, 3 not relevant. A borderline posting can flip,
  and 4 calls per posting can easily miss a ~20–40% flip rate.

## What I can and cannot conclude

What I can conclude

For these five postings, using this prompt (judge_v1_baseline.txt) and this model (claude-sonnet-5-5), on this day, Claude gave the same verdict every single time. All 20 calls agreed, and none of them failed the validator. So for these cases, at least, the verdict is repeatable.

That doesn’t mean it’s correct, though. The Discord Senior Data Engineer (Ads) posting is a good example. Claude marked it “not relevant” all four times, which went against my label every time. When I went back and read the posting, I found Claude had misread it. It claimed the role needed 5+ years of ad-tech experience. The posting actually asks for 5+ years of writing production code and building data pipelines, and ads experience is only listed as a nice-to-have. So what I really got was the same mistake four times in a row. Being consistent didn’t make it accurate.

I also noticed the reasons changed more than the verdicts did. Even when the answer stayed the same, Claude pointed to different parts of my résumé each time. Because of that, I don’t take its explanations at face value. I see them as one possible reason, not the actual reason, and I check anything factual against the posting myself.

What I can’t conclude

I can’t say anything about other postings, other days, other prompts, or other models. Four calls per posting also isn’t enough to catch a verdict that only flips occasionally. In my earlier runs, the Samsara posting came out 5 relevant and 3 not relevant over eight runs, and a sample this small could easily miss a flip rate of 20–40%. Finally, I can’t claim Claude is “right” overall, because that depends on my labels. Two of my own labels ended up breaking the rule I wrote for myself, so my labels aren’t perfect either.
