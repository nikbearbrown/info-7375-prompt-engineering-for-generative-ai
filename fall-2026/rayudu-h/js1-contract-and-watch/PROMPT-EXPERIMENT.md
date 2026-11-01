# Prompt experiment (Chapter 2)

## The labeling rule, written first

The labeling rule is "The rule" in `CONTRACT.md`. It was committed as `b88cdbb` (Oct 31, 2026, 14:38 ET) before any posting was labeled. The management test was added to it before that commit. A posting is **relevant** if and only if all three hold:

1. its title has "AI", "Engineer" or "Engineering" as a whole word;
2. its description names one of Priya's 10 skills as a whole word;
3. its title has no "Manager", "Director" or "Head".

## The 20 postings

- **Source:** real Anthropic postings from the live baseline response (`runs/2026-10-31T144337/`), picked by `scripts/select_postings.py` (seed 20261031).
- **The split:** each set got 6 postings whose title passes the title and management tests, plus 4 others. That way both sets contain postings that could be relevant. Only the titles were used for this; the skills test wasn't run while picking.
- **Labels:** `experiment/labels.csv`.

**How the labels were made. Read this before trusting the numbers.**

- **Dev set:** Hemanth labeled all 10 by hand from the job pages.
  - On #1 and #2, Hemanth's first labels were "not relevant", with the reasons "very senior position" and "it's a recruiter position". Neither reason is in the rule, so Hemanth relabeled both by the rule. Both first labels are kept in the `first_instinct_label` column.
  - On #2 Hemanth first reported finding Python and AWS. A script check showed "AWS" occurs only inside "Scaling **Laws**". Hemanth then labeled #2 not relevant from the skill-evidence sheet.
- **Held-out set:** Hemanth labeled all 10 from `experiment/skill_evidence_sheet.md`. That sheet was made by `scripts/skill_evidence.py`, which shows where each skill occurs in a description but never a verdict. So **for the held-out set, the skills test in the hand labels used the same matcher as the code.** "Rule code vs hand label" there isn't an independent check of the code. Claude versus the hand labels still is.

## One change

- **Baseline, `prompts/judge_v1.md`:** "Decide whether this job posting is worth the candidate's time", plus the candidate's titles and skills, the posting, and the output contract.
- **Revision, `prompts/judge_v2.md`:** identical, plus **one** paragraph, the written rule. `tests/test_claude_validator.py::test_one_change_between_prompt_versions` checks that v2 only adds lines that begin with "Apply this rule."

## Procedure

- **Model and isolation:** `claude-sonnet-5-5` through Claude Code 2.1.316. Each call was a fresh `claude -p` with no tools.
- **Calls:** one per posting per prompt.
- **Order:**
  1. Dev set first (14:45–14:46 ET), and its results were looked at.
  2. Then the held-out set was labeled.
  3. Only after that did its Claude calls run (17:28–17:29 ET).
- **Nothing changed between them:** no prompt was edited after the dev results.
- **Commands:**
  - `python scripts/claude_batch.py experiment experiment/results_<set>.jsonl --set <set> --versions v1 v2`
  - then `python scripts/analyze.py experiment <set>`

## Results

| Set | Claude v1 vs hand label | Claude v2 vs hand label | Rule code vs hand label | Valid answers |
|---|---:|---:|---:|---:|
| Development (10) | **5/10** | **10/10** | 10/10 | 20/20 |
| Held-out (10) | **5/10** | **10/10** | 10/10 (not independent; see above) | 20/20 |

Per-posting tables: run `python scripts/analyze.py experiment dev` (or `heldout`). The raw answers are in `experiment/results_dev.jsonl` and `experiment/results_heldout.jsonl`.

## What this shows, and how little

- **v1 never said "relevant".** On all 20 postings it answered "not relevant". Its 5/10 on each set is exactly the share of not-relevant postings in each set. Saying "not relevant" every time would have scored the same. So v1's pass rate measures the label mix, not skill.
- **v1 is judging something else.** Its justifications cite seniority and domain, for example a co-op versus Staff, or GTM data. That's close to Hemanth's first instinct on #1 and #2, before relabeling them by the rule.
- **v2 matched every label on both sets.** With the rule in the prompt, Claude applied it correctly 20 times out of 20. That shows Claude can follow a written rule on these postings. It doesn't show that the rule picks good jobs: the labels were made with the same rule.
- **Ten cases are very few.**
  - Even with 10/10 on held-out, the true error rate could plausibly be 20–30%. A rough 95% upper bound for 0 errors in 10 is about 26%.
  - Each posting got one call per prompt, and the sampling report shows Claude can flip on some postings.
  - The held-out labels share the code's skill matcher.
- **For the agent:** v2 nearly duplicates the rule's record, while v1 adds a different opinion. Which one the agent should use is Hemanth's decision; see the README.
