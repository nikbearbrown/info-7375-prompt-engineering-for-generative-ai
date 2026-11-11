# Prompt experiment (Chapter 2)

**Question:** does changing one thing in the prompt contract make Claude agree more with my own hand labels, on postings I didn't tune on?

## Setup

| | |
|---|---|
| Labels | 20 real Stripe postings, `labels/labels.csv`, labeled with `labels/LABELING_RULE.md` (rule committed in ab1e292 in my working repo (see `evidence/git-history.txt`), labels in 926f9e6) |
| Postings | Picked by `labels/select_postings.py` (fixed seed, mixed difficulty), text from `evidence/raw/2026-10-31T214118Z/stripe_content.json` |
| Split | `labels/split.py` → `labels/split.json`: 10 dev + 10 held-out, random within each label, 6 relevant + 4 not_relevant in each set. Made after the labels were committed |
| Baseline | `prompts/claude_judge.v1.md` |
| Revision | `prompts/claude_judge.v2.md`: **one change**, the paragraph that sets how strict the verdict is (below) |
| Judge | Same as the agent: `claude -p`, `claude-sonnet-5-5`, same validator; one call per posting per prompt |
| Pass | Claude's verdict equals my hand label. A rejected answer would count as a fail (there were none) |
| Order | v1 on dev → chose the change from v1's dev misses → v2 on dev → v2 declared final → v1 and v2 on held-out, once |
| Data | `reports/experiment/<prompt>.<split>.json` (every verdict + justification) and `.raw.jsonl` (every reply). Script: `reports/experiment.py`, which refuses held-out until v2 exists and `--final` is given |

## The one change

v1:
> The verdict is `relevant` only if the posting fits on every point the posting gives information about. A point the posting says nothing about does not count against it. Otherwise the verdict is `not_relevant`.

v2:
> The verdict is `relevant` unless the posting is clearly a bad fit. Close or related is enough: the job seeker may simply not have thought of this kind of role. A point the posting says nothing about does not count against it. Clearly a bad fit means something like this: the job seeker does backend development, and the posting centers on machine-learning tools and requirements they don't have. Only then is the verdict `not_relevant`.

Why this change: both of v1's misses on dev were v1 being stricter than I am (a Solutions Architect title; one "security domain" minimum requirement). I label leniently: if a posting isn't clearly a bad fit, it's worth applying to. Nothing else in the file changed (`diff prompts/claude_judge.v1.md prompts/claude_judge.v2.md` shows one line).

## Pass rates

| | dev (10) | held-out (10), as first labeled | held-out (10), after one label correction |
|---|---|---|---|
| v1 baseline | **8/10** | 6/10 | **7/10** |
| v2 revision | **9/10** | 10/10 | **9/10** |

**One label was wrong, and I corrected it after the held-out run.** 8128744 (Software Engineer, New Grad): I first labeled it relevant. v1's reason pointed to a line I had missed: "New grad candidates should have no more than 18 months of professional experience (excluding internship experience)". Aarav has about 25 months at Infosys (2021-06 to 2023-07; the Dassault co-op is an internship). So my rule's step 6 makes it not_relevant. I changed the label for this reason, from the posting's own text, not to move a score: the correction lowers v2 (10 → 9) and raises v1 (6 → 7). The first label is still in commit 926f9e6; no Claude call was re-run, only the scoring. Dev is unchanged (this posting is held-out).

## Every posting

| Set | posting_id | Title | My label | v1 | v2 |
|---|---|---|---|---|---|
| dev | 6042172 | Backend Engineer, Core Technology | relevant | ✅ | ✅ |
| dev | 7235875 | Backend Engineer, Privy | relevant | ✅ | ✅ |
| dev | 7913700 | Backend Engineer, Data | not_relevant | ✅ | ✅ |
| dev | 7984866 | Product Manager, Ecosystem Risk | not_relevant | ✅ | ✅ |
| dev | 8072257 | Solutions Architect, Metronome (Startups) | relevant | ❌ | ❌ |
| dev | 8130052 | Account Executive, Hunter (CEE) | not_relevant | ✅ | ✅ |
| dev | 8131144 | Backend Engineer, Link | relevant | ✅ | ✅ |
| dev | 8265763 | Software Engineer, Internal Identity | relevant | ❌ | ✅ |
| dev | 8301253 | Backend / API Engineer, Radar | relevant | ✅ | ✅ |
| dev | 8311067 | Program Manager, GTM Experience | not_relevant | ✅ | ✅ |
| held-out | 6176758 | Backend/API Engineer, Money as a Service | relevant | ✅ | ✅ |
| held-out | 7208537 | Software Engineer, Money Movement (London) | not_relevant | ✅ | ✅ |
| held-out | 7292520 | Backend Engineer, Developer & End-user Experience Platform | relevant | ✅ | ✅ |
| held-out | 7895284 | Full Stack Software Engineer, Brazil | not_relevant | ✅ | ✅ |
| held-out | 8089353 | Software Engineer, Vulnerability Management | relevant | ❌ | ✅ |
| held-out | 8127182 | Software Engineer, Revenue and Financial Automation | not_relevant | ✅ | ✅ |
| held-out | 8128744 | Software Engineer, New Grad | not_relevant (corrected; first: relevant) | ✅ (❌ before the correction) | ❌ (✅ before the correction) |
| held-out | 8198207 | Software Engineer, Payins Card Networks | relevant | ❌ | ✅ |
| held-out | 8230294 | Legal Operations Team Lead | not_relevant | ✅ | ✅ |
| held-out | 8332676 | Software Engineer - Full stack | relevant | ❌ | ✅ |

v1's reasons on its four held-out misses against the first labels, all strictness: no security-domain experience (8089353); the New Grad role caps experience at 18 months and Aarav has about 25 (8128744); ISO 8583 is a minimum requirement Aarav lacks (8198207); 2 years each of Ruby, React and Go required (8332676).

The one miss v2 keeps (8072257): Claude still calls Solutions Architect a sales role ("demos, discovery calls, landing deals"). I see it as software-related and worth a try. That's a difference in judging the role, not something the posting can settle.

## What this shows, and how little

- **On these 20 postings, v2 agrees with my labels more than v1** (18/20 vs 15/20 after the correction; 19/20 vs 14/20 before), and the gain held on the held-out set that wasn't used to choose the change.
- **What v2 really did is match how lenient I am.** My labels are lenient by design, so a prompt that says "relevant unless clearly a bad fit" fits them better. That says v2 is closer to my preference, not that v2 is better at finding good jobs.
- **Agreeing with my label is not the same as being right.** On 8128744 (New Grad), v2 agreed with my first label, and both of us were wrong: v1 was the one that read the 18-month cap. A lenient prompt and a lenient labeler can share the same blind spot. On 8332676, v1's strict reading (three languages Aarav doesn't have) is also defensible.
- **v2's risk was not really tested.** The worry with a lenient prompt is that it lets bad fits through. All 4 held-out not_relevant postings were easy (London, São Paulo, 5+ years, a legal role), and v2 kept all of them not_relevant; there was no hard negative where leniency could go wrong.
- **Ten cases can show very little.** On held-out, the difference between 7/10 and 9/10 is two postings, and one wrong label alone moved each prompt by 10 points. Each prompt ran once per posting, and with 10 cases one or two answers changing by chance would move the rate by 10–20 points. The 5 postings in the sampling report were stable over 4 tries with v1, but these 20 were not repeated.
- **Same model, same day:** all calls used `claude-sonnet-5-5` on 2026-10-31.

## My review

I missed the New Grad experience cap when labeling; v1 caught it. I corrected that one label after the held-out run, for the reason above.
