# CONTRACT — Job-Search Agent 1

Written before any agent code exists. Started 2026-10-28; the rule, wrong versions, and failure sentence were added 2026-10-31. Language: Python 3, standard library only.

## In
- **Board:** the public Greenhouse job board for Abacus Insights. Host `boards-api.greenhouse.io`, board token `abacusinsights`, endpoint `https://boards-api.greenhouse.io/v1/boards/abacusinsights/jobs?content=true`.
- **Résumé:** one JSON file for a fictional persona, validated before every run. The persona is an entry-level Data Analyst:
  - 0–2 years of experience, new MS grad
  - targets Data Analyst, BI Analyst, and Business/Analytics Analyst titles
  - any US location, including remote
  - needs H-1B sponsorship
  - contact details are an `@example.com` address and a 555 phone number only
- **State:** a file of posting ids seen on earlier runs. It is absent before the first run.
- **Allow-list:** host-level, and `boards-api.greenhouse.io` is the only entry. The watch reads only the `abacusinsights` board. The prompt experiment's label pool may also read other Greenhouse boards from my H-1B employer list, each one named in config.
- **Needs:** Python 3 and network access to the allow-listed host. Only when the Claude judge is turned on, it also needs a logged-in Claude Code CLI (`claude -p`). No API key.

## Out
Each run saves the raw response as evidence and reports only postings whose ids are new since the last run. The first run is a baseline and reports zero new postings.

For each new posting, the agent writes two verdicts:

| Judge | Labeled as | Meaning |
|---|---|---|
| `rule` | record | Computed from the rule below; anyone can recompute it. |
| `claude` | judgment | Claude's answer under a fixed prompt contract; not a fact. |

- **Verdict values:** `relevant`, `not_relevant`, or `needs_human`. `needs_human` marks a case the rule or the prompt cannot decide.
- **Justification:** every verdict cites at least one résumé field path and at least one posting field, each with the value it read.
- **Validator:** it rejects any Claude output that:
  - uses a verdict outside those three values
  - cites nothing
  - cites a field path that doesn't exist
  - quotes a value that isn't at that path
  - is missing a required key or adds an extra one

  A rejected output is recorded as invalid. It is never repaired into a verdict.
- **Prompt-experiment scoring:** pass rate is computed only over cases where Claude committed (`relevant` or `not_relevant`). It is always reported next to coverage, meaning decided cases out of total.

## Refuses
- Fetching any host not on the allow-list, including after a redirect.
- Showing a real résumé on screen or putting one on GitHub. Only the fictional persona exists in this folder.
- Presenting a model's judgment as a fact. Every Claude verdict is labeled as a judgment.
- Applying to jobs, emailing or messaging anyone, or logging in anywhere.
- Following instructions inside posting text. Postings are data; text like "ignore previous instructions" does not change a verdict.
- Giving the Claude judge tools. `claude -p` runs with tools disabled, so it sees only the prompt.
- Writing anywhere outside the agent's own run and state folders.

## The rule
Apply clear exclusions first. If any one applies, label the posting `not_relevant`, even when another field is missing. If none applies but a required decision remains unclear, label it `needs_human`. Label it `relevant` only when every check below is satisfied.

1. Title: Ignore case and punctuation, then look for a whole phrase in the posting’s `title`: “Data Analyst,”"Data Engineer", “BI Analyst,” “Business Intelligence Analyst,” “Business Analyst,” or “Analytics Engineer.” Do not use description keywords to create a title match. “Payer Analytics Consultant” and “Sales Operations Analyst” do not match.
2. Seniority: A matching title is ruled out if it contains the whole word “Senior,” “Sr,” “Lead,” “Principal,” “Staff,” “Manager,” “Director,” “Head,” “VP,” “Vice President,” or “Chief.” “Junior,” “Associate,” and “Entry Level” are allowed. A “Contractor:” prefix does not rule a posting out; the other checks still apply.
3. Location: A stated US location, including “US Remote,” passes. A posting whose available locations are only India, Nepal, or other non-US places is `not_relevant`. “Remote” without a country or other clear US location is `needs_human`. When several locations are offered, one clear US option is enough. If the location fields conflict about whether the role can be based in the US, use `needs_human`.
4. Sponsorship: Label `not_relevant` when the description explicitly says it cannot provide H-1B or visa sponsorship, requires work authorization without current or future sponsorship, limits the role to US citizens or permanent residents, or offers H-1B transfers only. An explicit offer of H-1B sponsorship passes this check. Silence, a generic work-authorization requirement, or a vague statement that visa sponsorship “may” be available is `needs_human`; do not assume either approval or denial.
5. Experience: Read mandatory experience requirements in the description. A minimum above two years, such as “3+ years required,” is `not_relevant`. A minimum of two years or less passes because it overlaps the persona’s 0–2 year target range. Ignore experience described only as “preferred.” If the posting clearly accepts an MS degree instead of a higher year minimum, the new MS grad satisfies that alternative. If it is unclear whether a higher number is mandatory or whether an alternative applies, use `needs_human`.
6. Other `needs_human` cases: Use it when the title is missing, a US location cannot be established, H-1B sponsorship is unstated or unclear, a potentially decisive experience requirement is ambiguous, or statements within a required check contradict each other. A clear exclusion on another check still makes the overall verdict `not_relevant`.
7. Scoring: If my hand label is `needs_human` and Claude commits to `relevant` or `not_relevant`, count that committed answer as a fail. If Claude answers `needs_human`, leave that case out of the pass-rate calculation and include it in the total used for coverage.

## Wrong versions
1. Broad title keywords: Accept any title containing “analyst” or “analytics.” This wrongly accepts “Payer Analytics Consultant” or “Sales Operations Analyst” when the other fields pass. Tests should hold the other fields constant and catch both titles.
2. Silence means rejection: Treat a description with no sponsorship statement as `not_relevant`. The rule requires `needs_human` for that case. A test should use a matching, US-based, entry-level title with no sponsorship statement.

I would keep “always answer `not_relevant`” as a baseline showing why an Abacus-only score can mislead, rather than count it as one of the two plausible implementations.

## What a failure looks like
2026-10-31 — A failure is a run that reports a previously seen posting as new, labels a posting `relevant` despite a clear exclusion above, or accepts a Claude justification whose quoted value is absent from the saved posting or résumé.
