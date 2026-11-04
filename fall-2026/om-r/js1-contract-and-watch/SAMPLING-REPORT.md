# SAMPLING-REPORT.md: Sampling Report (Chapter 1)

## Executive summary

I asked Claude the same question 20 times: is this job posting relevant to
the fictional persona Priya Nair? That was 5 real GitLab postings, 4
separate calls each. Each call used the same prompt contract (`judge-v1`),
the same résumé, and the same pinned model, with no memory between calls.

**Every call returned the same verdict for its posting: "not relevant", 20
out of 20.** The reasons were not equally stable. On one posting, one call
treated the "Remote-Global" label as a location conflict and three calls
treated it as a fit. The facts were the same, the readings were opposite,
and the verdict was the same.

The sample is weak evidence of stability. Four of the five postings are
obviously non-engineering roles (sales, pre-sales, compensation), so
agreement there was the expected result. The one posting where I
disagreed with Claude, a backend role with an explicit agentic-AI
requirement, shows a real blind spot. It comes from what the prompt
contract gives Claude, not from randomness: the résumé is a skills list
with no work history, and the posting's location field is never passed.

## Method

- **Postings.** 5 postings from the real baseline response
  `evidence/gitlab_jobs_20261030T201528Z.json` (fetched 2026-10-30T20:15:28Z,
  238 postings). They were chosen by a seeded random draw,
  `random.Random(20261030).sample(pool, 5)`, from the 232 postings not used
  in the earlier compare step. The 7 compare-step ids were excluded: the
  seeded 9999999002, plus 8704363002, 8883003002, 8565469002, 8621733002,
  8738179002, and 8646544002. Script: `scripts/make_sampling_worksheet.py`.
  They were drawn randomly, not chosen by hand, because the earlier dry
  check had already computed rule verdicts for the whole board.
- **Calls.** 4 independent calls per posting, 20 in total
  (`scripts/sample_judge.py`). Each call was a separate, stateless Messages
  API request: the same `judge-v1` system prompt, the same `resume.json`,
  and the same posting text. No conversation history was carried between
  calls. Calls rotated across the 5 postings. All 20 returned distinct API
  message ids and ended with `stop_reason: end_turn`. All 20 passed the
  strict output validator; none was rejected or unavailable. They ran
  2026-10-30T20:57:55Z to 20:58:58Z and used 64,836 input and 5,237 output
  tokens.
- **Model.** Pinned to exactly `claude-opus-5-5`, with no refusal fallback
  to another model. Any response served by another model would have been
  rejected (CONTRACT.md, Toolchain). All 20 were served by `claude-opus-5-5`.
- **No temperature control.** This model rejects `temperature` and the
  other sampling parameters, so the calls ran at the model's default
  sampling. I could not raise randomness to stress-test stability, or
  lower it to pin it down. "Variance" here means variance at the default
  setting only.
- **What Claude saw.** Per the prompt contract, the posting's id, title,
  and content (HTML tags removed), plus `resume.json`. Claude did **not**
  see the posting's `location` field, departments, or any other metadata.
- **Hand labels.** My labeling rule, quoted exactly from
  `logs/sampling_hand_labels.md`:

  > "I label a job relevant when its specific responsibilities or
  > requirements involve building, integrating, or operating AI systems;
  > general company statements about AI or selling an AI-powered product
  > do not count."

  How and when the labels were written: I composed the rule and all 5
  labels in a chat conversation with Claude, which I used as a drafting
  and thinking tool. That happened after the blank worksheet was
  generated (20:36:45Z) and, by my own account, before the sampling calls
  ran (20:57:55Z). The only evidence of that timing is the chat's own
  timestamps. The labels were transcribed into
  `logs/sampling_hand_labels.md` afterward, at 21:05:10Z, so no repository
  file records them before the calls. The worksheet itself was never
  filled in. No judge verdict and no rule verdict for these 5 postings had
  been shown to me when I labeled them. The 20:18Z dry check computed rule
  verdicts for all 238 postings but displayed only the 6 relevant ones,
  and none of these 5 was among them. Because Claude helped draft the
  labels, they are not fully independent of the model they are compared
  against (see FRICTIONAL.md, 2026-10-30).

- **Rule records.** For reference, the CONTRACT.md rule was run on the same
  5 postings after sampling (`logs/sampling_rule_records.txt`). It matched
  0 of the 6 skills on every one, so all 5 are **not relevant**.
- **Raw data.** Every call's full output, verdict, justification, prompt,
  message id, and token usage: `logs/sampling_raw/<posting_id>_<call_n>.json`.
  Per-posting tables: `logs/sampling_summary.md`.

## Result: zero verdict variance, real reasoning variance

| Posting | Title | Call 1 | Call 2 | Call 3 | Call 4 | Spread | Rule (record) | Hand label |
|---|---|---|---|---|---|---|---|---|
| 8716143002 | Senior Backend Engineer, India | not relevant | not relevant | not relevant | not relevant | unanimous | not relevant | relevant |
| 8783485002 | Senior Solutions Architect | not relevant | not relevant | not relevant | not relevant | unanimous | not relevant | not relevant |
| 8860219002 | Regional Sales Director | not relevant | not relevant | not relevant | not relevant | unanimous | not relevant | not relevant |
| 8860273002 | Demo Architect, EMEA | not relevant | not relevant | not relevant | not relevant | unanimous | not relevant | not relevant |
| 8918216002 | Senior Compensation Manager | not relevant | not relevant | not relevant | not relevant | unanimous | not relevant | not relevant |

There were 0 splits in 20 calls. Against my hand labels, the judge agreed
on 4 of 5 postings (16 of 20 calls) and the rule agreed on 4 of 5. Both
disagreed with me on the same posting, 8716143002.

### Same fact, opposite readings: "Remote-Global" on 8860219002

In all four calls, Claude cited the posting's "Remote-Global" text and its
focus on the German market. The calls drew opposite conclusions about
whether the location fits:

- **Call 1** (a conflict): "The role focuses on the German market, which
  conflicts with resume.location_preference (Boston, MA, open to remote)
  and resume.visa_sponsorship_needed, despite the "Remote-Global" label."
- **Call 2** (a fit): "The role is "Remote-Global", which suits
  resume.location_preference.open_to_remote, but it is a senior sales
  management position that does not fit resume.years_of_experience of 1."
- **Call 3** (a fit): "The posting is "Remote-Global", which suits
  resume.location_preference open_to_remote, but the function mismatch is
  decisive."
- **Call 4** (a fit): "The role is "Remote-Global", which suits
  resume.location_preference.open_to_remote, but the job function is a
  fundamental mismatch."

The verdict did not change, because every call treated the sales function
as decisive. But the location reading, which is the factor CONTRACT.md's
dated failure case is about, flipped between calls. Claude never saw the
posting's actual `location` field, which says `Remote, Germany`.

Smaller variations of the same kind:

- On 8716143002, the visa need is cited in calls 1 and 3 but not in calls
  2 and 4.
- On 8918216002, calls 1 and 4 note that remote work suits the persona;
  calls 2 and 3 don't mention it.
- Across postings, which of the 10 `key_skills` each call lists as absent
  changes from call to call.

### Why unanimity here is weak evidence

Four of the five postings are unambiguous non-engineering roles: a sales
director, a Korean-language presales architect, a pre-sales demo
architect, and a compensation manager. For a persona targeting AI/ML
engineering roles, "not relevant" is the obvious answer, so 4 for 4 on
those was expected. The draw contained no genuinely contested posting
where a model on the fence might flip. The one posting where a human
reader could reasonably go either way (8716143002) was also unanimous,
which is one data point, not a trend.

## Where Claude's judgment disagreed with my hand label

**8716143002, Senior Backend Engineer, India.** My hand label was
**relevant**. The posting explicitly requires "Proven experience building
or operating agentic systems in production—moving beyond prompt
engineering to architecting loops, tool-use, and error-handling strategies
that ensure reliability at scale." All 4 Claude calls said **not
relevant**. So did the rule, which matched 0 of 6 skills. Both machine
judges disagree with me here, and they agree with each other for related
reasons.

**Root cause: the résumé contract.** This project's `resume.json` has a
skills list and no experience narrative. The persona Priya was rebuilt
from (the Reallocation Engine's `search/examples/priya-nair/`) built a
production LangGraph agent used by 120+ analysts in her co-op. That fact is
not in `resume.json`, so Claude never saw it. The only evidence of agentic
work Claude had was the names `LangChain` and `LangGraph` in `key_skills`,
and the posting never uses those words. It says "agentic systems" and
"tool-use". A check of the posting text against `resume.json` found that
0 of the persona's 10 key skills appear literally anywhere in this posting.

Claude was not purely literal-matching. Every call acknowledged the
agentic requirement, and call 4 called it "secondary to general backend
architecture." No call connected "agentic systems… tool-use" to LangGraph
or LangChain. With no work history to point to, the agentic requirement
lost out to the other reasons.

**Claude's other reasons were not baseless.** All four calls also cited a
senior title against `years_of_experience: 1`, backend work against AI/ML
target roles, and an India-located role against a Boston-based persona
who needs US visa sponsorship. The posting's real `location` field is
`Bangalore, India`, so the location objection is factually right. Whether
the agentic match should outweigh the location and seniority issues is a
judgment call. That is exactly what a hand label is for.

**A visibility gap: what Claude sees vs. what a person checks.** Claude
inferred "India" from the word in the title. The prompt contract passes
only the title and content, never the `location` field. Here the inference
happened to be right. On a posting whose title doesn't name its location,
Claude would be reasoning about location without the field a human reader
would check first. The "Remote-Global" contradiction above shows the same
gap: that posting's location field (`Remote, Germany`) was never shown to
Claude.

## What this does and doesn't show

**It shows:**

- A perfectly repeatable verdict can sit on top of unstable reasoning. Four
  identical verdicts on 8860219002 came with opposite readings of the same
  location fact. Repeating an answer is not evidence that the model
  reasoned the same way each time.
- One real, traceable case where comparing judges matters in two different
  ways. Rule vs. judgment: they agreed on 8716143002, both for lack of
  literal skill terms. That agreement is not confirmation, because both
  share the same blind spot. Human vs. judgment: the disagreement points to
  the root cause, which is the résumé contract, not the model's randomness.
- A design gap in the prompt contract: no work history in the résumé, and
  no location field from the posting.

**It does not show:**

- Whether Claude's verdict varies on a genuinely contested posting. This
  random draw did not contain one. That is a limit of this sample, not a
  conclusion about the model.
- Whether any verdict is correct. Repeatability is not correctness; the
  only correctness check here is my hand labels, on 5 postings.
- A fully independent human baseline. Claude helped draft the hand labels,
  and the repository has no timestamped record of them before the
  sampling calls. Their timing rests on my statement and that chat's own
  timestamps.
- Anything about other sampling settings. Temperature could not be set,
  so this is the default setting only.
- Anything about other prompts, models, résumés, or boards. One prompt
  version (`judge-v1`), one model, one persona, one board snapshot.

## Honest conclusion

Five postings and twenty calls can support only narrow claims. On this
draw, `claude-opus-5-5` under `judge-v1` gave the same verdict every time
it was asked. That is a statement about repeatability, on postings that
were mostly easy. The sample cannot support a claim that the judge is
stable in general, and it cannot support a claim that the judge is right.
On the one posting where I disagreed, Claude was consistently, repeatably
"wrong" by my label. That is the opposite of what repeatability is often
mistaken for.

The most useful finding is about inputs, not randomness. The judge cannot
weigh experience it is never shown, or a location field it is never
passed. Before reading more into variance, the next change worth testing
is the résumé contract (adding an experience narrative) or the posting
input (passing `location`). Following Chapter 2, that means one change at
a time, measured against held-out labels.
