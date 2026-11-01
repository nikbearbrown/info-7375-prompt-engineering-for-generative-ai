# Sampling report (2026-10-31)

Evidence: `experiments/sampling/` (prompts, replies, spoiled runs, PLAN.md) and `labels/HAND_LABELS.md`.

## 1. Method

- **Run:** 2026-10-31, run by me in the Claude app (incognito, Sonnet 4.6, web search off), one reply per chat, no retry.
- **Postings:** 5 development-split postings: 8546367002, 8921476002, 8401114002, 8648494002, 8847738002.
- **Runs:** 4 fresh incognito chats per posting in the Claude app, Sonnet 4.6, web search off. That makes 20 replies.
- **Prompt:** the baseline prompt (`prompts/baseline.txt`), built for each posting with the judge's own prompt-building code (`python3 -m experiments.sampling build`). The text was pasted into each chat unchanged.
- **Why the app:** the CLI hit its usage limit: "You've hit your limit · resets 8pm (America/New_York)".
- **The app is not the CLI subprocess:** tools are not disabled the same way, and there is no retry. Each reply was saved verbatim and checked once with the judge's JSON validator (`python3 -m experiments.sampling check`).
- **Spoiled runs:** 5 runs were spoiled by my clipboard mistakes and redone. They are kept in `experiments/sampling/spoiled/`:
  - 8546367002 runs 1, 2 and 3: shell commands or terminal text were saved instead of a reply.
  - 8648494002 runs 3 and 4: the prompt was saved instead of a reply.
- **Selection:** my planned selection (Q13 below) differed from the actual one. My plan called for one clear AI/ML match and one data engineering match, but none of my hand labels is "relevant". So the 5 were picked from the dev split as proposed by the chat assistant, and I accepted them.

## 2. Results

Computed from the reply files by `python3 -m experiments.sampling_report`. Each reply is checked with the judge's validator; the skill counts are the length of each reply's `skills_cited` list.

| posting_id | title | my hand label | verdicts, runs 1-4 | split | valid | skills cited, runs 1-4 |
|---|---|---|---|---|---|---|
| 8546367002 | AI Engineer – Forward Deployed Engineering (AI FDE) | not relevant | not relevant / not relevant / not relevant / not relevant | 4-0 (not relevant-relevant) | 4/4 | 0 / 3 / 3 / 3 |
| 8921476002 | Forward Deployed Engineer | not relevant | not relevant / not relevant / not relevant / invalid | 3-0 (not relevant-relevant), 1 invalid | 3/4 | 0 / 4 / 3 / 5 |
| 8401114002 | Staff Machine Learning Engineer | not relevant | not relevant / not relevant / not relevant / not relevant | 4-0 (not relevant-relevant) | 4/4 | 5 / 0 / 3 / 4 |
| 8648494002 | Forward Deployed Engineer | not relevant | not relevant / not relevant / not relevant / not relevant | 4-0 (not relevant-relevant) | 4/4 | 0 / 0 / 3 / 3 |
| 8847738002 | Software Engineering Intern (2027 Start) - London | not relevant | not relevant / not relevant / not relevant / not relevant | 4-0 (not relevant-relevant) | 4/4 | 0 / 0 / 0 / 0 |

- **Total valid:** 19/20
- **Total invalid:** 1/20
  - `8921476002-4.txt`: resume_field 'resume_experience_tools' is not a field given in the input

## 3. Observations

Counted by Claude Code reading each reply. The coding rule is stated with each count, and every reply is listed so the counts can be checked. Counts are over the 19 valid replies unless stated otherwise.

**Location given as a reason for the verdict: 11 of 19.**
The contract says location is reported, not used to reject (CONTRACT.md, Final § The rule, item 7: "I want location to be reported rather than used to reject a job." (D0§4)); 11 of the 19 valid replies used it as a reason anyway.
- **Counted:** the explanation treats the posting's location as a barrier or a disqualifier.
  - 8648494002 runs 1–4
  - 8847738002 runs 1–4
  - 8921476002 runs 1–3
- **Location mentioned only to say it is not an exclusion: 3.**
  - 8401114002 runs 1–3
- **Location not mentioned: 5.**
  - 8401114002 run 4
  - 8546367002 runs 1–4
- **Invalid reply:** 8921476002 run 4 also gives location as a reason.

**Export-control note mentioned as a sponsorship issue: 10 of 19.** All 5 prompts contain the export-control note.
- **Counted:** the explanation ties the note to `needs_sponsorship` or to sponsorship risk.
  - 8401114002 runs 1 and 4
  - 8546367002 runs 1–3
  - 8847738002 runs 1–4
  - 8921476002 run 1
- **Note mentioned, but not as a sponsorship issue: 3.**
  - 8401114002 runs 2 and 3: they say it is not a security clearance requirement.
  - 8648494002 run 3: it says the clause "also applies", with no link to sponsorship stated.
- **Note not mentioned: 6.**
  - 8546367002 run 4
  - 8648494002 runs 1, 2 and 4
  - 8921476002 runs 2 and 3
- **Invalid reply:** 8921476002 run 4 also ties the note to sponsorship.

**Skills cited per posting (min–max over the 4 runs):**

| posting_id | min | max |
|---|---|---|
| 8546367002 | 0 | 3 |
| 8921476002 | 0 | 5 (4 among valid replies; the 5 is the invalid run 4) |
| 8401114002 | 0 | 5 |
| 8648494002 | 0 | 3 |
| 8847738002 | 0 | 0 |

**Explanation contradicts its own `skills_cited`.**

**Counted, 6 replies:** `skills_cited` is empty, but the explanation says one or more résumé skills match, align or overlap with the posting.
- 8546367002 run 1: "Databricks and AWS from skills.data_bi and skills.database_cloud align"
- 8648494002 run 1: "Skills alignment (Python, Databricks, Unity Catalog, Delta Lake, AWS, MLflow) is reasonable"
- 8648494002 run 2: "Skill overlaps with Databricks, Python, AWS, and Delta Lake exist"
- 8847738002 run 1: "Python in skills.languages and Databricks in skills.data_bi, which match description requirements"
- 8847738002 run 2: "required skills (Python, algorithms, data structures, OOP) do overlap with Priya's resume"
- 8921476002 run 1: "surface-level matches to the description's platform references"

**Related cases, not counted above:**
- **Matches named, but the empty list is explained: 1.**
  - 8847738002 run 3: "No skills were cited because the disqualification is structural"
- **List is not empty, but the explanation names one more matching skill that is not in it: 2.**
  - 8401114002 run 1: "her use of the Databricks Genie API are surface-level matches". Genie API is not cited.
  - 8546367002 run 4: "LangGraph aligns with LangChain-adjacent tooling". LangGraph is not cited.
- **List is empty, and the explanation names résumé skills without calling them a match: 2.**
  - 8401114002 run 2: "adjacent but do not satisfy"
  - 8847738002 run 4: "While Priya has Python and Databricks platform experience"

## 4. My plan and conclusions

BEGIN
**13. Five postings.** I'll select five real postings from my dataset: one clear AI/ML match, one data engineering match, one senior-level position, one with unknown sponsorship, and one borderline case involving experience or clearance. I'll record their actual posting IDs before testing.

**14. Number of runs.** I'll run each posting four times in separate fresh Claude conversations, giving me 20 responses in total.

**15. Prompt selection.** I'll use the baseline prompt for all 20 sampling responses. I want to measure variation without changing the prompt between runs.

**16. High variation.** If all four runs give the same verdict, I'll report no observed variation. A 3–1 split counts as moderate variation because one response disagrees with the other three. A 2–2 split counts as high variation because there's no majority verdict. I'll report the actual split for every posting.

**17. Repeatability versus correctness.** Repeating the same answer shows consistency under the tested conditions, not that the answer is correct. I'll compare each response against my own hand label to evaluate correctness.
END

## 5. Limits

- **Sample size:** n = 5 postings × 4 runs.
- **No relevant case:** all 5 hand labels are "not relevant", so no relevant case was sampled.
- **Validator bug:** one invalid result came from the validator rejecting "resume_experience_tools", a key the judge's own input provides.
