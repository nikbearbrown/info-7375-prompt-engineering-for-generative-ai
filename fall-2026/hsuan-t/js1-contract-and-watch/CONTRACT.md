# CONTRACT — Job-Search Agent 1

English translation of `CONTRACT.zh.md` (the version Isaac wrote and revised in Chinese). If they ever differ, the code follows this file.

Author: Isaac Tai · Written: 2026-10-29 (before any code ran) · Revised: 2026-10-31

## In

| Input | What it is | When missing or broken |
|---|---|---|
| **board** | Greenhouse, company `stripe`: `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | Can't fetch (not 200, not JSON) → report the error and stop; don't update state |
| **resume** | `personas/aarav-patel.resume.json`, the fictional persona Aarav Patel, in JSON Resume format (https://jsonresume.org/schema/) | Report the error and stop, naming the missing field |
| **profile** | `personas/aarav-patel.profile.json`, the user's job-search preferences (fields below) | Report the error and stop, naming the missing field |
| **state** | `state/stripe.state.json` (below) | File doesn't exist → baseline; file broken → report the error and stop |
| **Built-in alias table** | `data/skill_aliases.json`, built into the tool and shipped with the repo (below) | File missing or broken → report the error and stop |
| **Built-in "no sponsorship" phrase list** | `data/no_sponsorship_phrases.json`, built into the tool (below) | File missing or broken → report the error and stop |
| **Claude** | Default: `claude -p` (Claude Code, logged in with your own subscription), no API key needed. Optional: `--claude-via api` + the environment variable `ANTHROPIC_API_KEY` (needs API credits); **the key is never written to any file or committed** | `claude` not found, not logged in (or no key in api mode) → the Claude judge reports an error; the rule judge runs as usual |

### Required résumé fields (JSON Resume)
`resume.basics.name`, `resume.basics.email`, `resume.basics.phone`, `resume.basics.profiles[]`, `resume.work[]`, `resume.projects[]`, `resume.skills[].keywords[]`.
Any one missing → report the error and stop; the message names the missing field (for example `missing resume.skills[].keywords`). No verdict is produced.

### Profile fields
| Field | Type | Example |
|---|---|---|
| `profile.target_roles[]` | Job-title phrases I want | `["software engineer", "backend"]` |
| `profile.exclude_title_words[]` | Words that rule a title out | `["senior", "quant"]` |
| `profile.locations[]` | Location phrases I accept | `["boston", "us remote", "us"]` |
| `profile.skill_aliases` | (optional) the user's own extra spellings, same format as the built-in table | `{"PostgreSQL": ["pg"]}` |
| `profile.years_experience` | (optional) my own years of work experience, a number | `2` |
| `profile.years_stretch` | (optional) how many more years than mine a JD may ask for and I'd still apply, a number | `2` |
| `profile.needs_sponsorship` | (optional) whether I need the company to sponsor a visa (for example H-1B), true / false | `true` |
| `profile.min_salary` | (optional) the lowest yearly salary I accept, in US dollars | `100000` |

The first three are required and need at least one value. The others can be left out: a check whose field is missing is **skipped**, and the justification says `skipped` (check 4 runs only when both `years_experience` and `years_stretch` are present).

### Skill aliases
The same skill is often written differently in the JD and the résumé (the JD says `postgres`, the résumé says `PostgreSQL`). In check 3, a résumé keyword counts as found if **the keyword itself or any of its aliases** appears in the JD. Aliases come from two places, and both are used:

1. **Built-in table** `data/skill_aliases.json`: common spellings prepared by the tool, kept small (about 10–20 entries), for example:
   ```json
   {"PostgreSQL": ["postgres"], "Kubernetes": ["k8s"], "JavaScript": ["js"], "Node.js": ["nodejs"], "Go": ["golang"]}
   ```
   The résumé keyword and **all** its aliases are searched (the résumé says `Go` → look for `go` and `golang`). The table doesn't add ordinary English words as aliases (for example, no `node` for Node.js: "each node" in distributed systems).
2. **Added by the user**: put `profile.skill_aliases` in your own profile file (same format as the built-in table). Spellings the built-in table doesn't have go here; **no need to change the tool**. If both tables list the same skill, their aliases are merged.

**Telling the user where to add them**:
- The README has a section "Add a skill spelling" with the profile file's location and a format example.
- The last line of every run summary always says: `Missed a skill written another way? Add it under "skill_aliases" in personas/aarav-patel.profile.json` (the path is the profile file actually used in that run).
- The justification for check 3 says which spelling was found (for example `"found: PostgreSQL (as postgres)"`), so the user can see whether an alias worked.

### "No sponsorship" phrase list
`data/no_sponsorship_phrases.json`: common sentences in a JD saying visa sponsorship is **not offered**. Built into the tool and shipped with the repo:
```json
["no sponsorship", "unable to sponsor", "not able to sponsor", "cannot sponsor", "will not sponsor",
 "do not sponsor", "does not sponsor", "not provide sponsorship", "not offer sponsorship",
 "not eligible for sponsorship", "without sponsorship", "sponsorship is not available", "sponsorship not available"]
```
These phrases are matched as **whole phrases** (see The rule), not with the usual word matching.

### State file
`state/stripe.state.json`, contents:
```json
{"board": "stripe", "seen_ids": [8172510, 6042172], "last_run_at": "2026-10-30T15:00:00Z"}
```
- Doesn't exist → treated as the baseline: report 0 new postings, then create the state.
- Broken (not valid JSON, missing fields) → report the error and stop. It must not be quietly treated as an empty file, or every posting would count as new, which is the same as running the baseline again.

## Out

Every run produces four things:

1. **raw response**: `evidence/raw/<UTC time>/stripe_content.json` (the original data, kept as evidence)
2. **updated state**: `state/stripe.state.json`
3. **run results**: `runs/<UTC time>/verdicts.json` + `runs/<UTC time>/summary.md`
4. **Claude's replies**: `runs/<UTC time>/claude_raw.jsonl` (Claude's reply for each posting as received, including ones the validator rejected; only when there are new postings)

### The verdict for each new posting (`verdicts.json`)

- `status`: `"ok"` or `"error"`. **Read status first**: the verdict only means something when it's `ok`; when it's `error`, read `error_message`.
- `verdict`: only `"relevant"` or `"not_relevant"`. When `status` is `error`, it is always `"not_relevant"`.
- `judge` + `kind`: the rule's are `"rule"` + `"record"`; Claude's are `"claude"` + `"judgment"`.
- `justification`: each line is one check: which field of the posting, compared with what, and the result. It must name the actual fields, not just give a conclusion. It can't be empty when `status` is `ok`. For a posting that was cut, the justification goes up to the check that cut it (the last line is the reason).
- No new postings (including the first, baseline run) → `"verdicts": []`.

```json
{
  "posting_id": 6042172,
  "status": "ok",
  "error_message": null,
  "verdict": "relevant",
  "judge": "rule",
  "kind": "record",
  "justification": [
    {"posting_field": "title", "compared_to": "profile.exclude_title_words[]", "result": "no match"},
    {"posting_field": "title", "compared_to": "profile.target_roles[]", "result": "match: backend"},
    {"posting_field": "location.name", "compared_to": "profile.locations[]", "result": "match: us remote"},
    {"posting_field": "content", "compared_to": "resume.skills[].keywords[]", "result": "1 found: Java"},
    {"posting_field": "content", "compared_to": "profile.years_experience + profile.years_stretch", "result": "min 2 years ≤ 4"},
    {"posting_field": "content", "compared_to": "data/no_sponsorship_phrases.json", "result": "no phrase found"},
    {"posting_field": "content", "compared_to": "profile.min_salary", "result": "skipped: no salary in posting"}
  ]
}
```

An error example (the JD is empty, so the skills check can't run):
```json
{
  "posting_id": 12345,
  "status": "error",
  "error_message": "posting.content is empty, skills check cannot run",
  "verdict": "not_relevant",
  "judge": "rule",
  "kind": "record",
  "justification": []
}
```

### Claude judge (judgment)
Claude's output has **the same** format as above, with only two differences:

1. **Every justification line has one more field, `quote`**: a piece of text copied from that `posting_field` as evidence, so a reader can see what Claude based its judgment on.
2. **`judge` and `kind` are filled in by the program** (`"claude"` + `"judgment"`), not written by Claude, so they can't be mislabeled.

What Claude sees: one posting (`title`, `location.name`, `content`, with the HTML removed from content), the résumé, and the profile. It may only return this JSON:
```json
{
  "posting_id": 6042172,
  "verdict": "relevant",
  "justification": [
    {"posting_field": "title", "compared_to": "profile.target_roles[]",
     "result": "backend role matches", "quote": "Backend Engineer, Core Technology"},
    {"posting_field": "content", "compared_to": "resume.skills[].keywords[]",
     "result": "requires Java, which the résumé lists", "quote": "programming languages like Go, Java, C/C++"}
  ]
}
```

**Validator**: after Claude replies and before anything is saved, the program checks the reply. If any check fails → the reply is rejected, the posting is recorded as `status: "error"`, `verdict: "not_relevant"`, with the reason in `error_message` (for example `"quote not found in posting.content"`), and there is no retry.

| Check | Example that gets rejected |
|---|---|
| Valid JSON, and only JSON | A sentence: "This job looks like a good fit!"; or JSON wrapped in ```` ```json ```` |
| Exactly the fields `posting_id`, `verdict`, `justification`, no more, no fewer | `justification` missing, or an extra `confidence` |
| `posting_id` is the one that was sent | Sent 6042172, got back 8138044 |
| `verdict` is `relevant` or `not_relevant` | `"maybe"` |
| `justification` has at least one line, each line has exactly 4 fields, and every field is a non-empty string | `[]`, or `quote` missing, or `"quote": ""` (an empty string is "found" in any text) |
| `posting_field` is one of `title`, `location.name`, `content` | `"posting_field": "salary"` |
| `compared_to` starts with `resume.` or `profile.` | `"compared_to": "common sense"` |
| `quote` really appears in that field's original text (compared after removing HTML, lowercasing, and treating any run of spaces as one) | `"quote": "5+ years of Rust required"`, but the JD has no such sentence |

The validator can only confirm that Claude **answered in the format and that the evidence really exists**. Whether the evidence supports the conclusion (does that sentence really mean the posting requires Java?) is judgment, and is checked by the sampling report and the hand labels.

### Run summary (`summary.md`, also printed in the terminal)

```
Run 2026-10-30T15:00:00Z · board: stripe
State file: state/stripe.state.json · updated: 2026-10-30T15:00:00Z
Raw response: evidence/raw/2026-10-30T150000Z/stripe_content.json
```

| | rule (record) | Claude (judgment) |
|---|---|---|
| Postings fetched | 737 | — |
| New postings | 28 | 28 |
| Cut: 1a exclude words | 12 | — |
| Cut: 1b title | 10 | — |
| Cut: 2 location | 4 | — |
| Cut: 3 skills | 1 | — |
| Cut: 4 years | 1 | — |
| Cut: 5 visa | 0 | — |
| Cut: 6 salary | 0 | — |
| error | 0 | 0 |
| **relevant** | **1** | 2 |
| Judges disagree | 1 | |

(The numbers are only illustrative. Claude only gives relevant / not_relevant, not which check cut a posting, so those cells are —.)

```
Missed a skill written another way? Add it under "skill_aliases" in personas/aarav-patel.profile.json
```

## Refuses

| What it won't do | How / how you can tell |
|---|---|
| Fetch a host that isn't on the allow-list | The allow-list is only `boards-api.greenhouse.io` and `api.anthropic.com`. Every request the program itself makes checks the host first; not on the list → report the error and stop. Covered by a test. **Limit**: with the default `claude -p`, the request to Claude is made by Claude Code, and the program can't see its host. The program only guarantees that it doesn't contact a host off the allow-list itself, and that it starts `claude` with all tools and MCP turned off, no settings loaded, and `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL` removed |
| Show a real résumé on screen or on GitHub | Only files under `personas/` are read; `resume.basics.email` not ending in `@example.com` → report the error and stop. `.gitignore` blocks `my_resume/` and `*.pdf`. The terminal and the summary only print field names and matched keywords, never the whole résumé |
| Present the model's judgment as a fact | Every Claude output is labeled `kind: "judgment"`, and the summary table's column also says "Claude (judgment)". The validator rejects Claude output without this label |

If any of the above is triggered → return an error message and stop.

## The rule

### How words are matched (read this first)
Every check compares words, not raw text. Before comparing, both sides are turned
into a list of words:

1. Lowercase everything.
2. Split at every character that is not a letter or a digit: spaces, "/", ",", "-",
   "(", tabs ... Empty pieces are dropped.

   "Backend/API Engineer, Money"  ->  [backend, api, engineer, money]
   "Backend / API Engineer"       ->  [backend, api, engineer]

A target phrase matches a title when **every word of that phrase is in the title's
word list**. Order does not matter, and extra words in the title are ignored:

   title  "market software engineer" -> [market, software, engineer]
   target "software engineer"        -> [software, engineer]
   software ✓  engineer ✓  -> match ("market" is simply ignored)

   title  "security engineer"        -> [security, engineer]
   target "software engineer"        -> software ✗  -> no match

Why: companies write the same title in different ways ("Backend/API Engineer",
"Backend / API Engineer"), and often longer than my target, so I compare words
instead of exact text. But one shared word is not enough: matching on any single word
of my targets ("engineer", "platform", ...) let 163 of 737 Stripe titles through on
2026-10-29, including "Android Engineer, Identity", "Designer, Web Presence & Platform"
and "SaaS Platform and AI Partner Marketing Lead". Requiring every word of one target
phrase cut that to 92.

**Exception — whole phrases (check 5 only).** The "no sponsorship" phrases are matched as a
**whole phrase**: the words must appear together, in the same order. Lowercase-and-split
first, so "No  Sponsorship" or "no-sponsorship" still match:

   JD     "... must be authorized to work without sponsorship ..."
   phrase "without sponsorship"  -> found -> fail

   JD     "No degree required. Visa sponsorship is available."
   phrase "no sponsorship"       -> not found (the words are not together) -> pass

Why not the normal word matching: the second JD has both "no" and "sponsorship", so it
would be wrongly failed, even though it says sponsorship IS available.

**Numbers (checks 4 and 6).** Read straight from the JD text with HTML removed:

- Years: every number written right before "year", "years" or "yrs": "5 years", "5+ years",
  "2-12 years", "2–12+ years" (a range counts as its first number). Take the **smallest**.
- Salary: every dollar amount written with commas, like "$156,800". Take the **largest**.

### The checks
A posting goes through the checks in this order. The first check that fails gives
not_relevant. If all pass, the verdict is relevant.

| Order | Check | Compares | Passes when |
|---|---|---|---|
| 1a | exclude words | `posting.title` ↔ `profile.exclude_title_words[]` | The title's words contain **none** of the exclude words |
| 1b | title | `posting.title` ↔ `profile.target_roles[]` | Every word of at least one target phrase is in the title |
| 2 | location | `posting.location.name` ↔ `profile.locations[]` | Every word of at least one location phrase is in the location (same word splitting). No location written (empty, `N/A`, `na`) or only `Remote` → pass, and the justification says `skipped: no location in posting` |
| 3 | skills | `posting.content` ↔ `resume.skills[].keywords[]` (+ aliases: `data/skill_aliases.json`, `profile.skill_aliases`) | HTML tags removed first, then the same word splitting; **at least 1** résumé keyword (itself or any alias) appears in the JD |
| 4 | years | `posting.content` ↔ `profile.years_experience` + `profile.years_stretch` | The smallest years number in the JD ≤ years_experience + years_stretch. No years in the JD → pass |
| 5 | visa | `posting.content` ↔ `data/no_sponsorship_phrases.json` | Only checked when `profile.needs_sponsorship` is true. Any phrase from the list appears in the JD as a whole phrase → fail; none appears → pass |
| 6 | salary | `posting.content` ↔ `profile.min_salary` | The largest amount in the JD ≥ min_salary. No salary in the JD → pass |

- Check 3 counts the other way round: each résumé keyword is looked up in the JD. Greenhouse has no "skills list" field, and `content` is one block of HTML, so "how many skills the JD lists" can't be counted without AI.
- Check 3 is the only check that uses the résumé (the brief requires the justification to name a résumé field and a posting field).
- Check 2's "not written → pass" goes the same direction as checks 4–6: information the board didn't give is not used to cut a posting.
- The data for checks 4–6 is only in the JD text (Greenhouse has no years, visa or salary field; `pay_input_ranges` was checked on 2026-10-30 and is empty for both Stripe and WPP), so they all "check only if the JD says it, pass if it doesn't".
- Check 4 takes the smallest number and check 6 the largest amount, both leaning toward leniency: better to keep one more posting for a person to look at than to cut one because a number was misread.
- `posting.content` is empty → `status: "error"`, `verdict: "not_relevant"`.

### Known limits (where this rule is known to be wrong)
This rule aims to be predictable and recomputable, not to be the most accurate. The errors below are known in advance: computing the rule by hand gives the same wrong result. Judgments that need understanding the meaning go to the Claude judge.

- **Appears ≠ required**: check 3 only looks at whether a keyword appears in the JD; it doesn't tell "required" from "nice to have", and it can't understand sentences like "Java or Go" or "migrating away from Redis".
- **The whole JD is searched**, including the company introduction. Measured (2026-10-29 Stripe): of the 60 postings that pass the title checks, searching only the "Minimum requirements" section changes the result for just 2 (41 → 39). Section search wasn't adopted because section headings are each company's own, and another company may not have them.
- **A threshold of ≥ 1 is lenient**: common words like Java, SQL or AWS pass with a single match.
- **Different spellings of the same skill**: for example, the JD says `postgres` and the résumé says `PostgreSQL` (2 JDs did this on 2026-10-29 Stripe). Handled with the alias table, but the table is never complete: a spelling that's neither in the built-in table nor added by the user is still missed.
- **Skill names that are ordinary English words get misread**: Go is itself a common word, and the rule can't tell "Python, Go, Java" (a language) from "Go-to-Market" or "go further" (ordinary English). Measured (2026-10-29 Stripe): 283 of 737 JDs contain `go`, mostly Go-to-Market; but of the 60 engineering postings that pass the title checks, 27 contain `go`, of which 17 really require Go, 8 are the company introduction sentence (next item), and 2 are only Go-to-Market. So the title checks already block most of the misreads. Understanding sentences is left to the Claude judge. (Aarav's skills don't include Go, so this run's results aren't affected.)
- **The company's standard introduction sentence is also matched**: 11 Stripe JDs have the same sentence "We work mostly in Java, Ruby, JavaScript, Scala, and Go". It's the company's description of its tech, not this posting's requirement, but Java passes check 3 because of it.
- **A years number may not be about a requirement**: check 4 takes any number written before "years", including ones that aren't about work experience (7 Stripe JDs on 2026-10-29 say "At least 1 year of university education"), or the smaller one in "5+ years … 2+ years with Kafka". Because it takes the smallest, this mostly lets more postings through rather than cutting them by mistake. Measured (2026-10-29 Stripe): 654 of 737 have a years number; a common form is "2–12+ years".
- **Visa: not mentioned ≠ will sponsor**: check 5 can only cut postings that say explicitly they won't sponsor. Measured (2026-10-29 Stripe): none of the 737 JDs contains a phrase from the list; the word "sponsor" appears 18 times, all like "executive sponsor". So this check doesn't cut any Stripe posting, but whether Stripe sponsors is still unknown. The phrase list can't cover every wording either.
- **Salary is rarely given, and only a few formats are read**: check 6 only reads dollar amounts with commas like "$156,800". Measured (2026-10-29 Stripe): only 24 of 737 give a salary. Hourly pay ("/hr"), other currencies, and amounts that aren't salaries ("$1,000,000 in funding") can't be told apart.
- **Location is read literally**: places in the US whose text has no `us`, like `Seattle, WA` or `San Francisco, New York`, are cut at check 2 (2026-10-31 Stripe: many of the 49 postings cut at location are like this). A bare `Remote` always passes, though it may actually be remote in another country.
- **Work arrangement**: hybrid / on-site is not checked. The Job Board API has no such field, and only some JD texts mention it, so it's outside the checks. Remote is checked through `profile.locations[]`.
- **Full-time / contract**: there's no field; handled with `profile.exclude_title_words[]` (titles saying "Intern" or "Contract" are excluded). If it's only in the text and not the title, it's missed.

### Examples
Actually run on the Stripe data saved on 2026-10-29 (`evidence/raw/2026-10-30T033237Z/stripe_content.json`) with this **demo profile**:

```json
{"target_roles": ["software engineer", "backend", "platform engineer", "devops engineer", "site reliability engineer"],
 "exclude_title_words": ["senior", "staff", "principal", "lead", "manager", "director", "head", "quant", "sales", "intern", "frontend", "contract"],
 "locations": ["boston", "us remote", "us"],
 "years_experience": 2, "years_stretch": 2,
 "needs_sponsorship": true,
 "min_salary": 100000}
```
(Aarav is on F-1 STEM OPT and will need H-1B later, so `needs_sponsorship: true`. `min_salary` is a demo number.)
Résumé keywords (Aarav's 17): TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit, Jenkins, Rust, Terraform

| posting_id | posting.title | posting.location.name | 1a exclude words | 1b title | 2 location | 3 skills | 4 years (≤ 4) | 5 visa | 6 salary | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 8138044 | Account Executive, AI Sales | San Francisco, CA | ❌ sales | — | — | — | — | — | — | not_relevant |
| 8172510 | Abuse Investigator | Seattle, San Francisco, New York City | ✅ | ❌ no target phrase | — | — | — | — | — | not_relevant |
| 8198280 | Software Engineer, Backend | Seattle, WA | ✅ | ✅ software engineer, backend | ❌ no boston / us / remote | — | — | — | — | not_relevant |
| 8089353 | Software Engineer, Vulnerability Management | US - Remote | ✅ | ✅ software engineer | ✅ us remote | ❌ 0 | — | — | — | not_relevant |
| 8127182 | Software Engineer, Revenue and Financial Automation | San Francisco, New York City, Seattle, Chicago, US-Remote | ✅ | ✅ software engineer | ✅ us remote | ✅ 1: Java | ❌ smallest 5 ("5–12+ years") | — | — | not_relevant |
| 6176758 | Backend/API Engineer, Money as a Service | US | ✅ | ✅ backend | ✅ us | ✅ 3: AWS, Kubernetes, Docker | ✅ smallest 2 | ✅ no phrase | ✅ not given, skipped | **relevant** |
| 6042172 | Backend Engineer, Core Technology | US-Remote, Chicago, Seattle, San Francisco | ✅ | ✅ backend | ✅ us remote | ✅ 1: Java | ✅ smallest 2 | ✅ no phrase | ✅ not given, skipped | **relevant** |
| 7292520 | Backend Engineer, Developer & End-user Experience Platform | Toronto Canada, San Francisco, Remote in US, Remote in Canada | ✅ | ✅ backend, platform engineer | ✅ us remote (remote and us both present) | ✅ 3: AWS, Kubernetes, Docker | ✅ smallest 2 | ✅ no phrase | ✅ not given, skipped | **relevant** |

The same profile on all 737: 1a cuts 355, 1b cuts 322, 2 cuts 49, 3 cuts 4, 4 cuts 2, 5 cuts 0, 6 cuts 0, **5 relevant** (the 3 in the table above, plus 2 engineering postings whose location is `na`). Before check 2 became "not written → pass" it was: 2 cuts 55, 3 cuts 1, 4 cuts 1, 3 relevant.

## Wrong versions

1. **A label attached to the wrong posting**: posting A's verdict ends up on posting B.
   - Plausible because: the label is written straight into the output after judging, without checking the matching posting_id. The count is right and the format is right, so looking at the output as a whole shows nothing.
   - Test: put in 2 mock postings with opposite expected results at once (one relevant, one not_relevant), and check that each `posting_id` gets its own verdict.
2. **An empty justification, or just "good fit"**
   - Plausible because: the verdict is right, and people only look at the conclusion, not the reasons.
   - Test: for every `status: "ok"` output, `justification` can't be empty, and each line's `posting_field` / `compared_to` must be field names that really exist. Also, a mock posting with blank `content` must return `status: "error"` + `error_message`, not `relevant`. On the Claude judge side: a fake Claude reply whose `quote` isn't in the original text must be rejected by the validator (`status: "error"`).
3. **State not saved, or not read**
   - Plausible because: every posting is treated as new because state isn't compared properly, or state isn't updated after the fetch. The first run looks completely normal.
   - Test: run twice, 5 postings the first time and 5 the second with 2 repeated; it should report 3 new postings. If state wasn't saved properly, it reports 5.
4. **Case or spacing changes a verdict**
   - Plausible because: matching didn't lowercase, or didn't handle spaces and symbols.
   - How: every check calls **the same** word-splitting function (lowercase + split) before comparing; none does it on its own.
   - Test: test this function directly, with the different styles of input each check will see:

     | Which check it imitates | input | should give |
     |---|---|---|
     | 1 title | `"\tSoftware   Engineer/Backend"` | `[software, engineer, backend]` |
     | 2 location | `"US-Remote, Chicago"` | `[us, remote, chicago]` |
     | 3 JD text (HTML removed) | `"Experience with JAVA, Node.js"` | `[experience, with, java, node, js]` |
     | 3 résumé keyword | `"Fluent Bit"` | `[fluent, bit]` |
     | 5 visa phrase | `"Without  Sponsorship"` | `[without, sponsorship]` |

     Without lowercasing, or without splitting at symbols and spaces, the results would be different.
5. **The wrong judge label**
   - Plausible because: the rule's output is labeled as Claude's, or Claude's as the rule's; the format is completely right, only one label is off.
   - Test: every rule judge output must be `judge: "rule"` + `kind: "record"`; every Claude judge output must be `judge: "claude"` + `kind: "judgment"`.
6. **The visa phrases matched with ordinary word matching**
   - Plausible because: reusing the earlier "all the words are there" matching means less code, and a JD that really says "no sponsorship" still gets cut, so it looks right.
   - Test: `needs_sponsorship: true`. Mock posting A's JD is "No degree required. Visa sponsorship is available."; check 5 should **pass** (there's no "no sponsorship" phrase). With ordinary word matching, "no" and "sponsorship" are both there, so it would be wrongly cut. Mock posting B says "must be authorized to work without sponsorship" and should **fail**.

## What a failure looks like

2026-10-29: This agent has failed when: it picks up postings it has already judged as new again; or it judges wrongly, calling a posting relevant when it doesn't fit, or not_relevant when it does fit; worst of all, it can't fetch the data, or the data it fetches is wrong; or the justification compares the wrong things, for example comparing skills with the title or some other field when they should be compared with the JD's requirements.
(Translated from the original Chinese sentence, unchanged in meaning; original in CONTRACT.zh.md.)
