# Labeling rule: my 20 hand labels

Version 1.0, 2026-10-30. Written before any label and before any Claude call. The decisions behind it are listed at the end.

The labels are the answer key for the prompt experiment and the sampling report. Each one is my own reading of one real posting from the Friday baseline response (`runs/2026-10-30T093102Z/response.json`), for the fictional persona Jane Doe (`persona/jane-doe.json`).

## Labels

`relevant` or `not_relevant`. Every posting gets one, and a `not_relevant` label names its reason: a failed contract check, senior scope in words, or a missing specialty.

## The rule

A posting is `relevant` only if all three of these hold.

1. **The contract's seven checks pass** (CONTRACT.md v0.1, The rule): full-time; a location on Jane's list; no level word in the title; a software engineering role; no U.S.-person, clearance or no-sponsorship phrase; no start before May 2027; at most 3 years of experience asked, where stating no years passes.
2. **No senior scope in words.** The text does not ask for seniority in words, even when it states no number: for example leading a team or other engineers, setting technical direction, or "extensive" or "deep" experience. Experience with, or familiarity with, a tool or an area is not senior scope on its own.
3. **No must-have specialty Jane lacks.** No requirement listed as required asks for a specialty her résumé (skills, experience, projects) does not show, for example GPU kernels, compilers or chip design. Lines marked "nice to have", "a plus", "bonus" or "preferred" do not count.

## How the labels are made

- The 20 postings were picked by `tools/select_postings.py` before I labeled anything: from the baseline postings with "Engineer" in the title, 10 the rule judges relevant and 10 it does not, chosen with seed 7375, then split into a development set and a held-out set of 5 + 5 each. The rule's verdict was used only to balance the set. It is in `labels/selection.json`, and it is not on the sheet I label from.
- I label from `labels/SHEET.md`: for each posting, its title, locations, employment type, link, and its own text down to "About OpenAI" (the company boilerplate below that line is left out, except any line with a status, start-date or export-control phrase, which is shown).
- Each posting is labeled once. The labels are committed before any Claude call. A label changed later would be a new commit with its reason, and the experiment would report both.

## After labeling (added 2026-10-30)

- For the ten postings the rule rejects, I confirmed my labels in one answer, against the rule's record (the check that failed), so their agreement with every judge is by construction. The experiment report says so and scores the other ten separately.
- I relabeled posting 11 from relevant to not relevant after the Claude calls, when an independent review pointed out that its required lines are the same kind of specialty I used for postings 1 and 4. The first label stays in `labels/labels.json` and in commit 882909e, and the experiment reports both.

## Where these choices come from

- **Decided on 2026-10-30:** labels use the contract's seven checks plus seniority in words; a must-have specialty Jane lacks makes a posting not relevant, and only must-haves count; the 20 postings are engineering titles, 10 the rule calls relevant and 10 it does not, seed 7375, 5 + 5 in each of the development and held-out sets.
- **Defaults I accepted:** the wording of the examples, the line that experience with a tool or an area is not senior scope on its own, the three reasons a `not_relevant` label names, and the sheet's layout.
