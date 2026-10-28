# JSA1 contract: guided questions (Claude's help sheet, NOT the contract)

Made 2026-10-28 by Claude to help Mayank write CONTRACT.md. Each question explains what the brief is really asking, gives options with tradeoffs (many from Applications Made Easy, AME), and a suggestion. **The contract itself must be in your words.** Pick, change or reject the options, then write your answer in the "Your answer" line. Those lines get copied into CONTRACT.md as-is.

Disclose in SOURCES.md: "Claude explained each contract section and offered options (js1-contract-questions.md); I chose the rule, the wrong versions and the failure sentence, and wrote CONTRACT.md myself."

Facts checked today (2026-10-28) that the options rely on:
- **Anthropic** Greenhouse board: 680 postings. Locations: San Francisco 489, New York 379, Seattle 190, "Remote-Friendly, United States" 32, **Boston 0**. New postings per day over the last 10 days: 1 to 13 (Mon 26: 1, Tue 27: 7).
- **Klaviyo** Greenhouse board: 158 postings, 78 in Boston, but 0 to 9 new a day, with several zero days.
- The list endpoint returns `id, title, location.name, first_published, updated_at, absolute_url, metadata`. **No description or departments** unless you add `?content=true`.
- Priya Nair (course persona): Boston, open to remote, MS Information Systems (Dec 2025), AI Engineer Co-op at Staples (2025-01 to 2025-08). Skills: Python, SQL, Databricks, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake, AWS (familiar only: Ray, Kubeflow). Targets (profile.yml): AI Engineer / ML Engineer, then Data Engineer; excluded: security-clearance roles. No relocation stated.

---

## Decision 0: which board? (Your plan says Anthropic; decide before the questions)

**Why it matters:** the "watch" section (12 points) needs "a real change" between run 1 and run 2. If no new postings appear by tomorrow, you must fall back to a seeded run, which is allowed but weaker.

| Option | For | Against |
|---|---|---|
| **A. Anthropic** (`boards-api.greenhouse.io/v1/boards/anthropic/jobs`) | Several new postings most weekdays, so run 2 will very likely show a real change | No Boston jobs, so Priya's location check will rarely pass unless she is open to SF/NYC/Seattle |
| **B. Klaviyo** (`boards-api.greenhouse.io/v1/boards/klaviyo/jobs`) | 78 Boston jobs, so verdicts can come out "relevant" naturally | Some days get 0 new postings: run 2 might show nothing |

**Suggestion:** A (Anthropic), since a real second run is worth more than a pretty relevance rate. "Relevant: 0 of 7 new" is an honest, fine result. If you want Priya to have a chance at relevant SF/NYC/Seattle roles, add `"open_to_relocate": ["San Francisco, CA", "New York City, NY"]` to your copy of her résumé, and say in the contract that you added it. - add open to relocate in her resume

Your choice: A (Anthropic) since a real second run is worth more than a relevance rate. That's wht Im adding open to relocate, keeping a candidate geographically restricted looses a good oppoprtunity.

---

## Q1. In: what goes into the agent, and what does it need to run?

**What it's really asking:** list every input so a TA could set it up from a fresh clone. It has three parts:
1. **The board:** the exact host and path (this is also your allow-list).
2. **The résumé:** which persona file, and **which fields your rule actually reads**, by exact JSON path. Only list fields the rule uses. If you list "skills" but the rule never reads it, a TA will notice.
3. **Everything else:** the state file of seen ids, the folder for raw responses, the API key for the Claude judge (in a local `.env`, never committed), and the Node version.

**Options:**
- **Simple (title + location only):** the rule reads `search.target_titles`, `search.exclude_titles`, `personal.location`, `search.open_to_remote`. The posting fields it reads are `title` and `location.name`. The list endpoint is enough.
- **With skills (closer to a real recruiter):** also reads `skills.languages` and `skills.backend_automation`, matched against the posting description. Needs `?content=true` (bigger responses, HTML to strip: AME's "decode, strip, decode, strip" for Greenhouse).
- **AME idea: a control panel.** Instead of hard-coding words in the code, put them in a `search` block in your copy of the résumé JSON (`target_titles`, `exclude_titles`, `locations`), the same way AME's "Build Config" node holds all filters as data. A TA reads the rule's words straight from the JSON.

**Suggestion:** simple rule plus the control-panel `search` block. It's easy for a TA to recompute by hand, and fewer moving parts means fewer ways to fail before Saturday.

Your answer (your words): It needs title, location, skills and a control panel 'search' block,
Instead of hard-coding words in the code, put them in a `search` block in your copy of the résumé JSON (`target_titles`, `exclude_titles`, `locations`, `skills.languages`), it makes it easy and decreases the chances of errors. 

---

## Q2. Out: what does the agent return for each new posting, and for a whole run?

**What it's really asking:** write the exact shape of the output, so a test can check it. The brief requires a verdict (relevant or not) and a justification that names the résumé fields **and** the posting fields behind it. You also have two judges (Step 3), so each new posting gets two verdicts.

**Suggested shape for each new posting** (edit freely):
```
posting_id, title, url
rule:   { verdict: "relevant" | "not_relevant",
          justification: names >= 1 résumé field and >= 1 posting field, with their values,
          kind: "record" }
claude: { verdict: "relevant" | "not_relevant" | "no_verdict",
          justification: same requirement,
          kind: "judgment", model, date }
```
Per run: `run number, timestamp, host, postings fetched, new since last run, baseline yes/no, raw response file name`.

**Choices to make:**
- Is there a third verdict like "unsure"? Suggestion: no for the rule (it's always computable). For Claude, use `no_verdict` only when the validator rejects its answer, so a malformed answer is never guessed into a verdict.
- Where does the output go? Suggestion: a JSON file per run (for example `runs/2026-10-28/report.json`) plus a short printed summary.

Your answer (your words): 
posting_id, title, url
rule:   { verdict: "relevant" | "not_relevant",
          justification: names >= 1 résumé field and >= 1 posting field, with their values,
          kind: "record" }
it goes into a JSON file per run (for example `runs/2026-10-28/report.json`) plus a short printed summary.
---

## Q3. Refuses: what will the agent never do, and what happens instead?

**What it's really asking:** limits, plus what the agent does when it hits one (stop with an error? skip? log?). The brief's minimum three are below; add your own.

| Refusal | What happens instead (suggested) |
|---|---|
| (required) Fetch any host not on the allow-list | Exit with an error naming the host; nothing is fetched |
| (required) Show a real résumé on screen or GitHub | The persona validator rejects any email not ending in `@example.com` or any phone without `555`; the run stops before fetching. (The rubric asks for a "validated persona résumé", so this check earns points) |
| (required) Present a model's judgment as a fact | Every Claude verdict is printed and stored with `kind: judgment`, the model and the date; never mixed into the rule's "record" |
| Accept a Claude answer in the wrong format | The validator rejects it and records `no_verdict`, never a guess |
| Apply, email, message anyone, or log in | No code path exists for these (the brief's boundary) |
| Write outside its own folder | State and raw responses go only into `state/` and `runs/` |
| Send anything to Claude beyond the posting and the résumé fields the rule uses | Keeps the prompt small and the data exposure minimal |

Your answer (your words; keep the required three, choose which extras):
|  Fetch any host not on the allow-list | Exit with an error naming the host; nothing is fetched |
|  Show a real résumé on screen or GitHub | The persona validator rejects any email not ending in `@northeastern.edu` or any phone without `555`; the run stops before fetching. |
|  Present a model's judgment as a fact | Every Claude verdict is printed and stored with `kind: judgment`, the model and the date; never mixed into the rule's "record" |
| Accept a Claude answer in the wrong format | The validator rejects it and records `no_verdict`, never a guess |
| Apply, email, message anyone, or log in | No code path exists for these (the brief's boundary) |
| Write outside its own folder | State and raw responses go only into `state/` and `runs/` |


---

## Q4. The rule: how is a posting judged relevant? (the most important answer)

**What it's really asking:** a rule a TA could apply **by hand** to any posting and get your verdict. That means only things visible in the data (title words, location text), every threshold as a number, and no words like "good fit" or "strong match".

**AME's proven pattern (from your Build Config / Filter, Rank & Cap nodes):** a posting is kept if its title hits an **include** term and no **exclude** term. Terms match **whole words**, case-insensitive, with an optional plural "s". Then a **location** check. AME learned the hard way that substring matching is wrong: "intern" excluded "Internal Tools", and "india" blocked "Indianapolis".

**A rule you could adapt** (with Priya's targets filled in):
> A posting is **relevant** if all three hold:
> 1. **Title includes** at least one of: "AI Engineer", "ML Engineer", "Machine Learning", "Applied AI", "Data Engineer", "LLM" (whole words, case-insensitive).
> 2. **Title excludes** all of: "Senior", "Staff", "Principal", "Lead", "Manager", "Director", "Head of", "Intern" (Priya has one co-op and a new MS degree, so senior titles are out).
> 3. **Location:** at least one location in `location.name` (split on " | ") is Boston, MA, **or** contains both "Remote" and "United States"*.
>
> Otherwise **not relevant**. The justification names the matched include term, any matched exclude term, and the location that passed or failed.

*If you chose relocation in Decision 0, add: "or is one of `open_to_relocate`".

**Decisions inside the rule:**
- **Include list:** too broad ("Engineer" matches 231 Anthropic titles, including sales engineering) or too narrow (misses good roles). Look at 20-30 real titles before fixing it.
- **Seniority:** Anthropic uses "Staff" in 101 titles. Excluding it is right for Priya's level, but write down why.
- **Title only, or description too?** Title only is hand-computable in seconds. Description matching is closer to reality but harder to check by hand.
- **Clearance exclusion:** Priya's profile excludes security-clearance roles. That would need the description, so either skip it (and list it under "Not checked") or add a title check for "Clearance" / "TS/SCI".

Your answer (your words): According to my course persona:
> A posting is **relevant** if all three hold:
> 1. **Title includes** at least one of: "AI Engineer", "ML Engineer", "Machine Learning", "Applied AI", "Data Engineer", "LLM" (whole words, case-insensitive).
> 2. **Title excludes** all of: "Senior", "Staff", "Principal", "Lead", "Manager", "Director", "Head of", "Intern" (Priya has one co-op and a new MS degree, so senior titles are out).
> 3. **Location:** at least one location in `location.name` is Boston, MA or is one of `open_to_relocate`, **or** contains both "Remote" and "United States"*.
>
> Otherwise **not relevant**. The justification names the matched include term, any matched exclude term, and the location that passed or failed.

---

## Q5. Wrong versions: two implementations that look right but are wrong, and the test that catches each

**What it's really asking:** predict two realistic bugs before Claude writes any code, and write the test that would catch each. The brief's examples are "labels paired with the wrong postings" and "a justification that cites nothing". Your best candidates are bugs **you actually hit in AME**, because those are true and you can explain them.

| Candidate | The plausible-but-wrong version | Test that catches it |
|---|---|---|
| **W1. Substring matching** (an AME lesson) | `title.includes("intern")` instead of a whole-word match, so "Software Engineer, Internal Tools" is wrongly excluded, and "Lead" kills "Leadership Programs Engineer" | A fixture posting titled "AI Engineer, Internal Tools" must come out relevant (if the location passes) |
| **W2. Verdicts paired with the wrong postings** (the brief's example; AME's "paired items" lesson) | Results matched by array position. When one Claude call fails or is skipped, every later verdict shifts onto the wrong posting | 3 fixture postings where the middle call fails: each verdict's `posting_id` must equal its posting's id, and the middle one must be `no_verdict` |
| **W3. Justification that cites nothing** (the brief's example) | The justification says "matches the candidate's background" without naming fields | The validator rejects any justification that doesn't name ≥ 1 résumé field path and ≥ 1 posting field with its value |
| **W4. "New" decided by title or URL, not id** | A reposted job with the same title is treated as seen, or a changed URL as new | Run 2 fixture: same id with a new title → not new; a new id with an old title → new |
| **W5. Baseline reports everything as new** | The first run (empty state) prints all 680 as new | Run 1 with no state file must report 0 new and save all ids |

**Suggestion:** W1 and W2. They're real, they come from your own work, and each has a crisp test. W5 is worth adding as a cheap third test even if you only list two in the contract.

**How (this matters for the sign-off):** you write these tests, or at least their exact cases (input to expected output), **before reading Claude's code**. Then the sign-off can truthfully say "by a test I wrote before reading Claude's code."

Your answer (your words): 
| Candidate | The plausible-but-wrong version | Test that catches it |
|---|---|---|
| **W1. Substring matching** | `title.includes("intern")` instead of a whole-word match, so "Software Engineer, Internal Tools" is wrongly excluded, and "Lead" kills "Leadership Programs Engineer" | A fixture posting titled "AI Engineer, Internal Tools" must come out relevant (if the location passes) |
| **W2. Verdicts paired with the wrong postings** | Results matched by array position. When one Claude call fails or is skipped, every later verdict shifts onto the wrong posting | 3 fixture postings where the middle call fails: each verdict's `posting_id` must equal its posting's id, and the middle one must be `no_verdict` |
| **W5. Baseline reports everything as new** | The first run (empty state) prints all 680 as new | Run 1 with no state file must report 0 new and save all ids |
---

## Q6. What a failure looks like: one dated sentence, written before anything runs

**What it's really asking:** commit in advance to the result that would prove the agent doesn't work, so you can't move the goalposts after you see the output. Date it today.

**Examples to adapt (don't copy):**
- "(2026-10-28) This agent fails if run 2 reports as new any posting id that was already saved in run 1's state file."
- "(2026-10-28) This agent fails if any rule verdict differs from what I get by applying THE RULE by hand to the same posting."
- "(2026-10-28) This agent fails if it shows a Claude verdict without the label 'judgment', or a justification that names no résumé field."

**Suggestion:** the first one (the core promise of the watch) or the second (the core promise of the rule). Pick the one you would be most embarrassed to see fail.

Your answer (your words, with today's date): (2026-10-28) This agent fails if run 2 reports as new any posting id that was already saved in run 1's state file or fails to identify & remove the duplicate result.

---

## After you answer
1. I turn your answers into CONTRACT.md using **your words**; any wording I change, I show you and you approve it.
2. You commit CONTRACT.md before any code exists (the commit time is your proof).
3. You write the W1/W2 test cases. Then Claude Code implements against the contract, and you run the tests yourself.
4. Run #1 (baseline) tonight. Write your first FRICTIONAL entry in your own words, 5 minutes after the session.
