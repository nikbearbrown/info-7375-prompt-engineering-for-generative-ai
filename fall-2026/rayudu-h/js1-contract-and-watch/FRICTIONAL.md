# FRICTIONAL.md — Job-Search Agent 1

> **How this was written.** Claude Code organized these entries from the working session on Oct 31, 2026. Every fact here comes from that session, a file, or a command output. Quotations marked as Hemanth's words are Hemanth's own; where Hemanth gave no words, there is no entry. Times are ET.

## Oct 31, about 3:30–4:00 AM: starting late, and the gate

- **I tried / expected:** I started JS1 on its due date with nothing built. Claude pointed out that the assignment says the contract comes first and must be mine. I asked Claude for a CONTRACT.md boilerplate only, then asked it to quiz me one question at a time and write in my answers.
- **What Claude contributed:** the question list and the options for each question. It also checked facts before I chose: the Greenhouse fields, the persona fields, how many Anthropic postings each option would pass. For example, it showed that only `id` is unique per posting, since `requisition_id` repeats (Airbnb: 19 distinct across 202).
- **Evidence:** CONTRACT.md, committed alone before any code as `b88cdbb` (pushed 2:38 PM).

## Oct 31, 4–5 AM, then about 2:12 PM: making "the rule" precise

- **What happened:** my first statement of the rule was "If the title, position and skills match the job posting, then it is relevant to Priya." Claude pointed out three problems:
  - "match" was undefined;
  - none of Priya's skills appears in any Anthropic title (0 titles contain "Python"), so "and skills" would make every posting not relevant;
  - location had nothing to compare against.

  I then answered sub-questions:
  - Title: contains "AI" or "Engineer" from Priya's experience title.
  - Skills: searched in the description; Ray and Kubeflow don't count.
  - Location: doesn't decide.
  - Matching: whole words, "Engineering" counts.
  - Seniority: didn't matter (at first).
  - A missing field gives "cannot judge".
- **Friction:** on the hand-worked example ("Engineering Manager, Claude Platform") I said "not relevant because it's an Engineering Manager position". Claude pointed out that my own rule said seniority doesn't matter, so my reason didn't follow from my rule. The verdict was the same either way, because no skill appears. I changed the rule (test 3: Manager, Director or Head means not relevant) rather than the reason.
- **Evidence:** CONTRACT.md, "The rule" and the worked example, which records the change.

## Oct 31, 2:38–2:45 PM: build, tests, baseline

- **What happened:**
  - Claude Code wrote the agent (Python 3.9, standard library plus pytest) against the contract.
  - First test run: 26 passed, 1 failed. The failing test used a relative résumé path, so the résumé "failed validation" and nothing was judged. The bug was in the test, not the agent; it was fixed with an absolute path. 27 passed.
  - Claude also made run folders unique, so two runs in one second can't collide.
- **Live baseline, 2:43 PM:** 675 postings, none reported as new. **The raw response was byte-for-byte identical** to a fetch Claude made at 3:36 AM while researching the contract (sha256 `1e5b62fe…7e88`). On a Saturday the board didn't change.
- **What I did:** because a second calendar day isn't possible before the deadline, I used the seeded option. A script made an "earlier" response by removing the 9 postings first published on Oct 30. A seeded baseline on it, then a run on the real response, reported those 9 as new. Both runs are labeled SEEDED everywhere.
- **Evidence:** `runs/2026-10-31T144337/` (live baseline), `runs/2026-10-31T144406-seeded/` and `-seeded-2/`, `scripts/make_seeded_earlier.py`.

## Oct 31, 2:45–2:50 PM: Claude calls, and a false alarm in my own check

- **What happened:**
  - The first background batch silently skipped the sampling calls. The shell redirect pointed into a folder that didn't exist yet, so only the dev-set calls ran. It was re-run.
  - All 40 answers passed the validator.
  - The quote check (built for my failure sentence "a justification quotes words that are not in the posting") flagged 9 dev answers. They were all prompt-v2 answers quoting the rule's own words ("Manager", "Director") or field names ("content"). That's a false alarm: those words were in the prompt.
  - Claude widened the check to everything Claude was shown. After that, 0 of the 40 were flagged.
  - The saved records still carry the old flag field; `scripts/analyze.py` recomputes it.
- **Evidence:** `jsagent/claude_judge.py` `ungrounded_quotes`; `experiment/results_dev.jsonl`.

## Oct 31, about 2:50 PM: I almost switched boards

- **I tried / expected:** I thought most Anthropic postings don't contain Priya's skills, and wanted to watch "all companies on Greenhouse" instead. (Hemanth, later: "I didn't find skills in Anthropic posting titles.")
- **What happened:** Claude showed:
  - JS1 asks for one board, and multi-board watching is JS2's task.
  - Greenhouse has no public list of all companies.
  - On Anthropic, 173 of the 251 postings passing title and management do name a skill. My impression came from the titles, not the descriptions.
  - On Databricks, every engineering posting would pass, because "Databricks" is both a skill and the company name.
- **What I did:** kept Anthropic.

## Oct 31, 2:47–2:51 PM: same posting, three surfaces

- **What happened:** on "Data Engineer" (5464234008), Claude said not relevant in a pasted chat (2:47:30) and with a file to read (2:47:39). It said relevant in the agent's seeded run (2:44). The rule says relevant.
  - With Claude Code as a fetching agent, the permission policy denied its chained `mkdir && curl && python3` command and a later `python3` command. It saved the raw board but never wrote the state file, and said so.
- **Evidence:** `ACTION-SURFACE.md`, `action-surface/`.

## Oct 31, afternoon: hand-labeling the dev set, and my instinct vs my rule

- **What happened:** I labeled the 10 dev postings from the job pages. My first labels gave reasons that aren't in my rule:
  - #1 "very senior position";
  - #2 "it's a recruiter position";
  - others "finance role" and "economics role".

  For #3–#7 the verdict was the same either way, because those titles fail the title or management test. For #1 and #2 it wasn't: both titles pass the title test.
- **What I did:**
  - I relabeled #1 by the rule: Python and AWS are in the description, so it's relevant.
  - For #2 I first wrote "same" (Python, AWS). Claude's check showed no skill in that description; "AWS" occurs only inside "Scaling Laws". I labeled it not relevant.
  - On #8 I had listed Azure, Go, Rust and Kubernetes. Claude pointed out that only Python is on Priya's list; the verdict stayed relevant.
  - My first-instinct labels are kept in `experiment/labels.csv`.

## Oct 31, before 5:28 PM: labeling the held-out set with a helper

- **What happened:** I didn't want to search for the 10 skills on every posting, and I asked Claude to check them for me.
- **What I did:** Claude wrote `scripts/skill_evidence.py`, which shows the sentence where each skill occurs but no verdict, and I labeled the 10 held-out postings from that sheet.
- **The cost:** for the held-out set, my labels and the rule code use the same skill matcher. "Rule code vs hand label: 10/10" there isn't an independent check. This is written in `PROMPT-EXPERIMENT.md`.

## Oct 31, 5:28–5:30 PM: results

- **Prompt v1** (no rule) said "not relevant" on all 20 postings: 5/10 on dev and 5/10 on held-out, which is exactly the share of not-relevant postings.
- **Prompt v2** (the rule added, the one change) matched every label: 10/10 and 10/10.
- **Sampling:** 5 postings × 4 fresh calls gave 20 identical verdicts, and 4 of the 5 postings were wrong against my labels, every time.
- **What surprised me (Hemanth's words):** "it surprised me that it picked up irrelevant postings with finance."

## Oct 31, 6:24 PM: the second live run

- **What happened:** 0 new postings, but the raw response changed (sha256 `2cc748f7…` vs `1e5b62fe…`). Comparing the two showed one posting edited at 15:08 (location narrowed); the 675 ids were the same.
- **What it shows (Claude's observation, not Hemanth's words):** the agent only notices new ids. An edited posting, for example one that moves to Boston or changes its description, is never reported. That's what the contract says, but it's a gap worth fixing in JS2.
- **Evidence:** `runs/2026-10-31T182441/`.

## Oct 31, about 5:50 PM: decisions after the results

- **Prompt:** I chose **v2** for the agent (commit `dcf2b7c`).
- **Scope, second time:** I asked again to watch every board and change the contract. Claude repeated that JS1 asks for one board and multi-board watching is JS2's task. I kept one board and put multi-board in the README as the next step.
- **What I accepted, changed or rejected (Hemanth's words):** "I told what are relevant and rejected irrelevant postings."
- **Sign-off:** I accepted Claude's drafted "Not checked" list. The signature line is mine to fill in.
