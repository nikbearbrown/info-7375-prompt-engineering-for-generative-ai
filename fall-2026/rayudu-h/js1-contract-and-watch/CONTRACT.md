# CONTRACT.md — Job-Search Agent 1

> **Authorship.** Claude Code (Opus 5.5) generated the headings as boilerplate on Oct 31, 2026, at Hemanth's request. It then asked Hemanth one question at a time and wrote each answer in. Every decision here (board, persona, the rule, the edge cases, the refusals, the wrong versions, the failure sentence) is Hemanth's answer; the wording is mostly Claude's. The worked example was done by hand by Hemanth. No agent code existed while this was written.
>
> Contract written: Oct 31, 2026, between about 4 AM and 2:12 PM ET. The failure sentence is dated 4:52 AM; the management-title test was added at about 2:12 PM. · Commit: `b88cdbb` (pushed Oct 31, 2026, 14:38 ET, before any code existed). Later edits to this file are only this hash and one corrected timestamp; see `git log -p CONTRACT.md`.

## In

What the agent takes in, and what it needs in order to run.

| Input | Form | Example / where it lives | Required? |
|---|---|---|---|
| Board | Greenhouse board token | `anthropic` → `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` | yes |
| Résumé | JSON, fictional persona | Priya Nair, copied from The Reallocation Engine's `search/examples/priya-nair/resume.example.json` | yes |
| State from the last run | JSON list of posting `id`s already seen | `state/seen_ids.json` (absent on the first run → baseline) | no (created by the baseline) |
| Claude judge prompt contract | text file, versioned in git | `prompts/` | yes, for the Claude verdict |

What it needs to run: written in Python. Network access to `boards-api.greenhouse.io` only. Claude Code (`claude -p`) for the Claude judge; the rule judge needs no model.

What counts as invalid input, and what happens then: a résumé that fails validation (Refuses item 7), a board host not on the allow-list (item 1), or a fetch that fails or returns something other than the board's JSON. Each is skipped and logged (see Refuses). A failed fetch is reported as **fetch failed**, never as "nothing new".

## Out

For each **new** posting, the agent returns:

| Field | Meaning |
|---|---|
| Posting id | the Greenhouse posting `id` (the only field unique per posting), plus its `title` |
| Rule verdict | relevant / not relevant / cannot judge — a **record** |
| Rule justification | A fixed template that names the fields and quotes the matched words, e.g. `title "Applied AI Engineer, …" matched experience[].title word "AI"; content matched skills: Python, AWS; location: London, UK (not used)`. On **not relevant** it also says which test failed (e.g. `content matched no skill`). On **cannot judge** it names the missing field. |
| Claude verdict | relevant / not relevant / cannot judge, plus a confidence of low / medium / high. Always labeled a **judgment**, never shown as a fact. |
| Claude justification | Must name at least one résumé field and at least one posting field. The validator rejects any answer that doesn't fit this format. |

On the first (baseline) run: it saves the raw response and every posting id, and reports **no postings as new** (assignment requirement).

Where results go: printed on screen, and written to a `report.md` for each run.

Files every run also writes (required by the assignment): the raw board response, saved as evidence at `runs/<timestamp>/raw.json` (never overwritten), and the state file of posting ids already seen, `state/seen_ids.json`. The report is `runs/<timestamp>/report.md`.

Format a justification must follow: see the two justification rows in the table above.

## Refuses

The agent will not:

1. Fetch any host not on the allow-list. Allow-list: `boards-api.greenhouse.io`
2. Show a real résumé on screen or on GitHub. Only the fictional Priya Nair résumé is used; see item 7.
3. Present a model's judgment as a fact. Claude's verdict is always labeled a **judgment**; the rule's verdict is labeled a **record**.
4. Apply, email or message anyone, or log in anywhere.
5. Send Priya's contact fields (name, email, phone, links) to Claude. Only her `skills` and `experience[].title` are sent.
6. Overwrite an earlier raw response. Each run saves a new file.
7. Run if the résumé JSON fails validation: for example, a missing `skills` or `experience`, or an email that doesn't end in `@example.com`.
8. Follow links in a posting, such as `absolute_url`. The agent reads the board endpoint only.

What the agent does when asked to do one of these: it **skips only the offending action, logs the refusal (on screen and in `report.md`), and continues** with everything else. Because there is only one board host and one résumé, an off-list host means nothing is fetched, and an invalid résumé means nothing is judged; the refusal is still logged rather than crashing.

## The rule

How a posting is judged **relevant**, written so a TA could predict the verdict on a posting by hand.

Posting fields used: `title`, `location.name`, `content` (the job description)
Résumé fields used: `experience[].title`, `skills` (every skills list except `familiar_with_not_shipped`; Ray and Kubeflow do not count)

In Hemanth's words (2026-10-31): "If the title, position and skills match the job posting, then it is relevant to Priya." Made precise through the answers below:

Relevant if and only if **all three** hold:

1. **Title.** The posting `title` contains a word from Priya's `experience[].title` ("AI Engineer Co-op"), ignoring "Co-op": that is, "AI" or "Engineer" (or "Engineering"; see below).
2. **Skills.** The posting `content` names at least one of Priya's `skills`: Python, SQL, Databricks, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake, AWS. The `familiar_with_not_shipped` list (Ray, Kubeflow) does not count.
3. **Not a management title.** The posting `title` does not contain "Manager", "Director" or "Head".

`location.name` does not affect the verdict. It is shown in the justification only.

Ties, missing fields and edge cases:

- **Matching is whole-word and ignores case**, in both the title and the description. "AI" does not match the "ai" inside "Campaigns". "SQL" does not match "PostgreSQL". "AWS" does not match "laws".
- **"Engineering" also counts as a title match.** So "Engineering Manager, Claude Platform" passes the title test.
- **Management titles are excluded; other seniority words are not.** A title containing "Manager", "Director" or "Head" is not relevant (test 3). A title containing "Senior", "Staff", "Principal" or "Lead" can still be relevant. *(Changed by Hemanth on Oct 31, 2026, after the worked example below: the first answer was that seniority doesn't matter at all.)*
- **A missing field means no verdict.** If `title` or `content` is missing or empty, the verdict is **cannot judge**, and the output names the missing field. This is a third outcome alongside relevant and not relevant.

Worked example (by hand, Hemanth, Oct 31, 2026): posting `id` 5378643008, "Engineering Manager, Claude Platform", San Francisco, CA | New York City, NY (https://job-boards.greenhouse.io/anthropic/jobs/5378643008).

1. Title test: **pass**. The title contains "Engineering".
2. Skills test: **fail**. Searching the description by hand found none of the 10 skills.
3. Management test: **fail**. The title contains "Manager".
4. Verdict: **not relevant**, because tests 2 and 3 failed. Location was not used.

Hemanth's hand verdict gave "Engineering Manager" as the reason. The rule at that point excluded no seniority, so the reason didn't follow from the rule. Hemanth then added test 3 rather than change the stated reason.

A Claude Code script run on the same posting earlier that morning also found 0 skills; Hemanth's check was done without seeing that result.

## Wrong versions

Two plausible-but-wrong implementations the tests must catch.

### Wrong version 1: "new" keyed on the wrong id

- **What it does:** it remembers `requisition_id`, or `internal_job_id`, instead of the posting `id`.
- **Why it looks right:** both are numbers on every posting, and most of the time they're unique. On the Anthropic board fetched 2026-10-31 03:36 ET (corrected after commit b88cdbb, which said 03:39; the file timestamp is 03:36:51), 675 postings had 675 distinct `id`s but only 621 distinct `requisition_id`s. So the wrong version works on most postings and silently drops the rest.
- **The test that catches it:** `test_new_is_keyed_on_posting_id`. The input is a constructed, labeled fixture with two runs:
  - Run 1, the baseline: posting `id` 1 with `requisition_id` R.
  - Run 2: adds posting `id` 2 with the **same** `requisition_id` R.

  **Expected:** run 2 reports `id` 2 as new. **The wrong version** reports nothing new.

### Wrong version 2: verdicts paired with the wrong postings

- **What it does:** a verdict and its justification are attached to the wrong posting, for example shifted by one after the postings are sorted or filtered.
- **Why it looks right:** the number of verdicts equals the number of new postings, and every verdict looks well-formed.
- **The test that catches it:** `test_verdicts_pair_with_their_postings`. The input is a constructed, labeled fixture with three new postings whose verdicts differ (relevant, not relevant, cannot judge).

  **Expected:** each output row has the verdict the rule gives *that* posting, and its justification quotes *that* posting's own title. **The wrong version** gives at least one row a verdict or quote belonging to another posting.

## What a failure looks like

**Oct 31, 2026, 4:52 AM ET** (before any agent code existed or ran): A failure is any run where a new posting that was on the Anthropic board is never reported, a failed fetch is reported as "nothing new", a justification quotes words that are not in the posting it is attached to, or the rule's verdict and Claude's verdict disagree and the report does not make clear which one is the record and which is the judgment.

*(Hemanth chose to combine four candidate failures; Claude Code joined them into this one sentence at Hemanth's request.)*
