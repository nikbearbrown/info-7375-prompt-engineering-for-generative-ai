# Prompt experiment (Chapter 2)

Labeling rule: labels/LABELING_RULE.md (committed in 7e76329, 2026-10-30 13:58 ET, before labeling). Labels committed in 251b7b7 (15:36:19 ET). Split frozen at commit a0c5f0b (15:36:28 ET, `labels/make_split.py --seed 7375`).
Frozen v1: prompts/v1.md as of commit 230cb5ee3780a91b71bd1498ece6d50344657a02 (git rev-parse HEAD, recorded before the first development experiment).
Model: claude-sonnet-5-5 (pinned with `--model`; every response.meta.json reports it) · judge: the Claude Code CLI 2.1.314 (`--judge claude-cli`, Amendment A14) · temperature: not set, because the CLI has no temperature flag · runs dated: 2026-10-30 (UTC and ET).

Drafted by Claude Code from the saved results on 2026-10-30. Every number below comes from one of these files:
- development: evidence/experiments/development/24ea45223186/results.json (v1) and evidence/experiments/development/9a4f0cb64ddb/results.json (v2)
- held-out: evidence/experiments/held-out/24ea45223186/results.json (v1) and evidence/experiments/held-out/9a4f0cb64ddb/results.json (v2)

The rule's scores are the `baseline_rule` block of the same files.

## Read this first: what the pass rates measure
The 20 labels were made quickly by me. At least 7 of them contradict labels/LABELING_RULE.md as committed. Every note is "work", including where the deciding criterion was level or location. The one exception is 7962437, noted "location".

| posting_id | title | my label | rule line it breaks |
|---|---|---|---|
| 8174963 | Staff Security Engineer, Abuse Control | relevant | Level: "Not relevant: Staff, …"; Work: security, not ML |
| 8194283 | PhD Data Scientist, Intern | relevant | Level: "interns, PhD-required roles" |
| 8148653 | Staff Machine Learning Engineer, Financial Connections | relevant | Level: "Staff" |
| 8022713 | ML Engineer Manager, AI Conversation Platform | relevant | Level: "people managers" |
| 7747640 | Forward Deployed AI Accelerator, Marketing | relevant | Work: "Sales, marketing, … do not count, even with 'AI' in the title" |
| 8175661 | Partner Marketing Manager, Online & Regional Events | relevant | Work: marketing, partnerships; Level: manager |
| 8198323 | Solutions Engineer, AI Build Team | relevant | Level: its stated minimum is 7+ years, and the rule rejects any minimum above 5. Work: possibly, if the role is pre-sales |

Three more contradictions surfaced later, from `location.name` and the years stated in the posting text:
- 8144196 (AI Engineer, relevant): its location is "Chicago", which fails the Location line.
- 8197886 (Machine Learning Engineer, Link, relevant): it states "6+ years", above the rule's 5.
- 8198323: as above, it states "7+ years".

**Pass rates therefore measure agreement with these labels. They measure neither the labeling rule nor correctness.**

## Agreement with the labeling rule's explicit exclusions (computed from titles only)
`scripts/exclusion_agreement.py` flags a posting when its **title alone** contains Staff, Manager, Intern, PhD, Account Executive, Sales, Marketing or Support as a whole word. These stand for the rule's explicit exclusions: Staff, people managers, interns and PhD roles under Level, and sales, marketing and support under Work. The script reads no description, so it can miss an exclusion stated only in the text, or flag a title wrongly. 10 of the 20 titles are flagged.

| judge | set | not_relevant on title-excluded postings |
|---|---|---|
| my hand labels | all 20 | 4 of 10 |
| rule (record) | all 20 | 10 of 10 |
| v1 | development | 4 of 4 |
| v2 | development | 3 of 4 (the fourth, 8194283, was rejected) |
| v1 | held-out | 6 of 6 |
| v2 | held-out | 6 of 6 |

On the development postings alone, my labels say not_relevant on 2 of the 4 title-excluded postings, against v1's 4 of 4 and the rule's 4 of 4. This is evidence that v1's low development pass rate largely reflects the labels, not a failure to apply the rule's exclusions.

## The one change
v1 → v2 (prompts/v2.md, commit fcd268a). One sentence is added to the System section, after "…they could work from one of the locations given.":

```diff
-Answer "relevant" when the core work of the role matches the persona's experience and skills, the level fits their years of experience, and they could work from one of the locations given. Otherwise answer "not_relevant".
+Answer "relevant" when the core work of the role matches the persona's experience and skills, the level fits their years of experience, and they could work from one of the locations given. For level, a stated minimum of 5 years or less fits this persona; a stated minimum of more than 5 years does not. Otherwise answer "not_relevant".
```

**What it was expected to fix.** On development, v1 called 7983456 ("5+ years") and 8222149 ("5 years") too senior for about 3 years. The added sentence was meant to flip both to relevant and to change nothing else.

**Why this change.** Claude Code proposed two candidates after the v1 development run. I picked A, this one, because it carries over LABELING_RULE.md's committed level threshold. B ("treat a stated minimum of years as a preference, not a hard limit") was rejected because it would tune the prompt toward labels that contradict that rule.

**What happened.** v2 did not flip either posting. Both reasons still treat the stated minimum as above the persona's years. The 7983456 reason (claude-sonnet-5-5 via the CLI, 2026-10-30T19:47Z, evidence/experiments/development/9a4f0cb64ddb/claude/7983456.validation.json) reads: "requires 5+ years of production ML experience. Riley has about 3 years of experience, below the stated minimum, so the level does not fit."

## Results
| set | n | rule (record) | prompt v1 | prompt v2 |
|---|---|---|---|---|
| development | 10 | 6/10 = 0.60 [0.313, 0.832]; wrong 4, rejected 0, error 0 | 3/10 = 0.30 [0.108, 0.603]; wrong 7, rejected 0, error 0 | 3/10 = 0.30 [0.108, 0.603]; wrong 6, rejected 1, error 0 |
| held-out | 10 | 4/10 = 0.40 [0.168, 0.687]; wrong 6, rejected 0, error 0 | 4/10 = 0.40 [0.168, 0.687]; wrong 6, rejected 0, error 0 | 4/10 = 0.40 [0.168, 0.687]; wrong 6, rejected 0, error 0 |

Pass rate = accepted and matching my label / 10, with a 95% Wilson interval (z ≈ 1.96). Rejections (the validator refused the output) and errors (the CLI failed) are counted apart from wrong verdicts (accepted but disagreeing with my label). The held-out set was run once, in commit 7d59b53. Each held-out prompt directory was created in that commit and never re-scored.

On held-out, v1, v2 and the rule gave the same verdict on all 10 postings: relevant only for 8243617.

## Per-posting results
✓ = matches my hand label, ✗ = does not.

| posting_id | set | title | hand | note | rule | v1 | v2 |
|---|---|---|---|---|---|---|---|
| 7983456 | development | Machine Learning Engineer, Radar | relevant | work | relevant ✓ | not_relevant ✗ | not_relevant ✗ |
| 8144196 | development | AI Engineer | relevant | work | not_relevant ✗ | not_relevant ✗ | not_relevant ✗ |
| 8174963 | development | Staff Security Engineer, Abuse Control | relevant | work | not_relevant ✗ | not_relevant ✗ | not_relevant ✗ |
| 8175828 | development | Account Executive, Product Sales - Currency Management | not_relevant | work | not_relevant ✓ | not_relevant ✓ | not_relevant ✓ |
| 8191708 | development | Account Executive, Product Sales - Open Issuance | not_relevant | work | not_relevant ✓ | not_relevant ✓ | not_relevant ✓ |
| 8194283 | development | PhD Data Scientist, Intern | relevant | work | not_relevant ✗ | not_relevant ✗ | rejected (value_not_found) |
| 8197886 | development | Machine Learning Engineer, Link | relevant | work | relevant ✓ | not_relevant ✗ | not_relevant ✗ |
| 8198323 | development | Solutions Engineer, AI Build Team | relevant | work | not_relevant ✗ | not_relevant ✗ | not_relevant ✗ |
| 8203220 | development | Fraud Architect | not_relevant | work | not_relevant ✓ | not_relevant ✓ | not_relevant ✓ |
| 8222149 | development | Data Scientist | relevant | work | relevant ✓ | not_relevant ✗ | not_relevant ✗ |
| 5601879 | held-out | Data Scientist | relevant | work | not_relevant ✗ | not_relevant ✗ | not_relevant ✗ |
| 7747640 | held-out | Forward Deployed AI Accelerator, Marketing | relevant | work | not_relevant ✗ | not_relevant ✗ | not_relevant ✗ |
| 7962437 | held-out | Social Media, Customer Support Associate | not_relevant | location | not_relevant ✓ | not_relevant ✓ | not_relevant ✓ |
| 8022713 | held-out | ML Engineer Manager, AI Conversation Platform | relevant | work | not_relevant ✗ | not_relevant ✗ | not_relevant ✗ |
| 8148653 | held-out | Staff Machine Learning Engineer, Financial Connections | relevant | work | not_relevant ✗ | not_relevant ✗ | not_relevant ✗ |
| 8175661 | held-out | Partner Marketing Manager, Online & Regional Events | relevant | work | not_relevant ✗ | not_relevant ✗ | not_relevant ✗ |
| 8212314 | held-out | Design Engineer, Expansion | not_relevant | work | not_relevant ✓ | not_relevant ✓ | not_relevant ✓ |
| 8224915 | held-out | Machine Learning Engineer, Growth Platform | relevant | work | not_relevant ✗ | not_relevant ✗ | not_relevant ✗ |
| 8237540 | held-out | Account Executive, Startup Platforms (Grower) | not_relevant | work | not_relevant ✓ | not_relevant ✓ | not_relevant ✓ |
| 8243617 | held-out | Machine Learning Engineer, Radar | relevant | work | relevant ✓ | relevant ✓ | relevant ✓ |

## A validator finding: an off-by-one citation, caught 4 times
Four responses were rejected with `value_not_found`. Each cites `{"source": "resume", "path": "/targets/exclude_title_terms/2", "value": "Intern"}`. In examples/persona_resume.json, index 2 is "Director"; "Intern" is index 3. In each case the verdict word (not_relevant) and the reason read as plausible. The citation did not resolve, so the validator refused the whole output instead of letting a miscited verdict through. This is Wrong version 2 in CONTRACT.md, seen in real output.
- evidence/experiments/development/9a4f0cb64ddb/claude/8194283.response.txt (v2, development)
- evidence/runs/20261030T195122Z_stripe/claude/8333122.response.txt (run 2)
- evidence/runs/20261030T195122Z_stripe/claude/8328664.response.txt (run 2)
- evidence/runs/20261030T195122Z_stripe/claude/8328662.response.txt (run 2)

## Honest limits
- **The labels.** See "Read this first": at least 7 labels contradict my own committed rule, and every note but one is "work". Pass rates are agreement with these labels, not a measure of the rule or of correctness.
- **Ten cases.** With n = 10, one posting moves a pass rate by 10 points.
- **Overlapping intervals.** Every interval in the Results table overlaps every other. On development, rule [0.313, 0.832] and v1 [0.108, 0.603] overlap, and v1 and v2 are identical. Nothing here shows that one judge is better than another.
- **One sample per case.** Each prompt saw each posting once. The sampling report shows that verdicts repeated on 5 development postings, but citations varied, and repeatability is not correctness.
- **I labelled alone**, quickly, on 2026-10-30, with no second labeller and no agreement check.
- **Truncation.** 4 of the 20 postings were cut at the 6000-character `content_text` limit, so the judge did not see their full text: 8144196, 8194283 and 8203220 (development) and 7747640 (held-out). When labelling I read the full text, from private/to_label.md: Claude Code wrote it on 2026-10-30 from the raw response, and it is kept private and not committed.
- **The judge is not a bare model call.** It is the Claude Code CLI, an agent wrapped around claude-sonnet-5-5. Here it was constrained by a replaced system prompt, no tools, no MCP servers, safe mode and an empty working directory. Its temperature and max_tokens cannot be set. That the default system prompt was replaced is inferred from about 2.7k–3.7k input tokens per call, not observed directly.
- **One model, one date, one board** (Stripe, 2026-10-30).
- **Run 2's agreement is on easy cases.** In run 2 (evidence/runs/20261030T195122Z_stripe/report.json), all 17 accepted judgments agreed with the rule. But all 20 new postings were clear negatives under the rule: 12 titles matched no target role, and 8 matched an excluded term. So 17 of 17 shows agreement on easy cases only.
