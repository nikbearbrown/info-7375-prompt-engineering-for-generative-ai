# Prompt experiment (Chapter 2)

## Design, fixed before any experiment call

**Labels.** An AI assistant drafted 20 labels for real Klaviyo postings using [LABELING_RULE.md](LABELING_RULE.md), written first. I read all 20 full postings, checked each decision against the rule, and adopted the labels before these calls.
- **Which postings:** every snapshot posting whose title contains a résumé `target_titles` phrase.
- **Result:** 3 `relevant`, 17 `not_relevant`. Labels committed in `2edbefa`.
- **One correction:** a later note fix in `335d280` changed no label.

**Split.** A stratified split with seed 7375, made once (`da980a7`).
- **Development:** 10 postings, 2 relevant.
- **Held-out:** 10 postings, 1 relevant.

**Prompts.** The two prompts differ by exactly one added line (`diff` shows only line 8):
- **Baseline:** `prompts/baseline.txt`, sha256 `d96d6a80649a…`.
- **Revision 1:** `prompts/revision-1.txt`, sha256 `53f62a5f0499…`, committed in `ba3a9b8`, before any baseline or experiment call. The added line:

  > A missing qualification marked "preferred" or "nice to have" alone must not make the verdict "not_relevant".

**Model.** `claude-opus-5-5`, effort `medium`, no temperature sent. All 40 calls were served by `claude-opus-5-5`.

**Scoring.**
- **Pass:** Claude's verdict equals the hand label.
- **Fail:** any other verdict, or an `invalid` / `unavailable` output. An output that breaks the prompt contract produces no usable verdict, so it cannot pass.

**Order.** Dev baseline, then dev revision, then held-out baseline, then held-out revision. All ran on 2026-10-31 between 06:05:36 and 06:08:17 UTC, by Revan in a terminal. The script refused held-out runs until each prompt was committed, unedited, and already run on dev.

## Results

| Set | Prompt | Pass | 95% Wilson interval | Invalid | Disagreements with hand label | Tokens in / out |
|---|---|---|---|---|---|---|
| Development | baseline | **9/10** | 0.60–0.98 | 1 | 0 | 33,953 / 3,041 |
| Development | revision 1 | **10/10** | 0.72–1.00 | 0 | 0 | 34,323 / 2,857 |
| Held-out | baseline | **10/10** | 0.72–1.00 | 0 | 0 | 34,710 / 2,142 |
| Held-out | revision 1 | **9/10** | 0.60–0.98 | 1 | 0 | 35,080 / 2,296 |

**All 38 valid verdicts matched the hand label.** No valid output disagreed with a label in either direction: there was no false positive and no false negative. The two failures were both `invalid`:

| Run | Posting | Validator reason | Verdict inside the output |
|---|---|---|---|
| Dev, baseline | 7777369003 | `resume_field 'devops_cicd' is not an allowed path` | not_relevant |
| Held-out, revision 1 | 7990569003 | invalid JSON: the output contained `"resume_field": "devops_cicd" == "" ? "skills.devops_cicd" : "skills.devops_cicd"` | not_relevant (visible, but not parseable) |

Both failures came from citing Kubernetes under the `skills.devops_cicd` path. The same slip appeared twice more in the sampling run, on 7777369003.

## What this shows, and what it does not

**These results do not show that the revision helped or hurt.**
- **The observed pass-rate moves are one case each.** On dev the pass rate went from 9/10 to 10/10; on held-out it went from 10/10 to 9/10.
- **Each move came from an invalid response.** Both validator rejections involved the same recurring citation-path problem, not a changed verdict about preferred qualifications. This does not establish the cause of the format failures.
- **The intervals overlap almost completely.** Ten cases per set cannot separate 90% from 100%. A Wilson interval for 9/10 runs from 0.60 to 0.98.

**The posting set gave the revision almost nothing to act on.**
- **The added sentence only matters for some postings.** It only changes a verdict where a preferred qualification is decisive.
- **That rarely happened here.** Thirteen of the 20 postings have a Senior, Sr., Lead, or Principal title. The other four `not_relevant` postings fail on a required 5+ years (the two Full Stack roles), a location outside Boston (San Francisco, London), or a mobile focus; some fail on more than one.
- **So the experiment had little power to detect the change.** The honest conclusion is "not shown to help or hurt on this set", not "no effect".

**Held-out agreement does not show the judge generalizes.** The held-out set contains one relevant posting. Getting 10/10 there mostly means rejecting Senior and Lead titles correctly.

**A disclosure.** Before the split, live watch run 2 (05:51 UTC) had already shown me Claude's baseline verdict on 7792539003, which later landed in the held-out set. Revision 1 was committed at `ba3a9b8`, before that run, so that verdict could not have influenced the revision.

**An information gap between me and Claude.**
- **What Claude receives:** only eight résumé paths: target titles, location, years, exclusions, and four skill lists.
- **What my labels used:** three of my `relevant` labels also cite `experience` or `projects`. Claude never sees those.
- **The effect here:** the verdicts agreed anyway in this set, but on harder postings that gap is a likely source of disagreement.

## Comparison with the mechanical rule (a record, not a judgment)

The five-condition rule in CONTRACT.md agreed with my reviewed labels on 19 of 20 postings.
- **The one disagreement:** **7727703003**, Full Stack Software Engineer - People Systems, Boston.
- **Why:** the rule says `relevant`, because the title, location, and skills pass and the title has no seniority word. My label says `not_relevant`, because the description asks for "5+ years of engineering or data engineering experience" and describes the role as a lead role.
- **What Claude said:** `not_relevant` under both prompts (held-out).

This is the clearest case in the data where reading the full description changes the answer, which is exactly what the mechanical rule does not do.

## What I would try next (not run)

- **Revision 2, a format fix:** list the full allowed `resume_field` strings as a quoted, comma-separated set, and say that the `skills.` prefix is required. This targets the only failure mode observed. I did not loosen the validator to accept `devops_cicd`, because changing the measurement after seeing results would make the comparison meaningless.
- **A harder posting set:** for the "preferred" revision, select postings where preferred and required qualifications actually conflict, so the sentence has something to act on.
- **More cases:** to separate pass rates that differ by 10 points with any confidence, the sets would need to be many times larger than 10.
