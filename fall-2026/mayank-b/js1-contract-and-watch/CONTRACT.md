# CONTRACT: Job-Search Agent 1 (The Contract and the Watch)

Written 2026-10-28, before any code exists. Author: Mayank Bhadrasen.

How this was written: Claude explained each section and offered options (`notes/contract-questions-with-my-answers.md`). I chose the board, the rule, the wrong versions and the failure sentence, and wrote my answers there. Claude then rewrote my answers into clearer sentences for a reader who doesn't know my earlier project, and made the corrections listed at the end ("Changes from my answers"), at my request.

## In

**1. The board.** Anthropic's public Greenhouse job board, list endpoint only:
`GET https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` (no `?content=true`, so no job descriptions).

Why this board: it posts new jobs most weekdays (1 to 13 a day over the 10 days before 2026-10-28), so a second run on a second calendar day should show a real change. A real second run is worth more than a high relevance rate.

**2. The allow-list.** The agent may contact exactly two hosts:

| Host | Why |
|---|---|
| `boards-api.greenhouse.io` | the board |
| `api.anthropic.com` | the Claude judge (Step 3) |

Every network request goes through one function that checks the host first.

**3. The résumé.** `persona/priya-nair.resume.json`: my copy of the fictional persona Priya Nair from The Reallocation Engine (`search/examples/priya-nair/resume.example.json`). I made two additions to my copy and they are marked in the file:
- A `search` block, which works as a control panel. The rule's words are not hard-coded in the code; they live in this block (`search.target_titles`, `search.exclude_titles`, `search.open_to_remote`, `search.open_to_relocate`). A TA can read every word the rule uses straight from the JSON, and changing a term never means editing code, which lowers the chance of errors.
- `search.open_to_relocate: ["San Francisco, CA", "New York City, NY"]`. Anthropic has almost no Boston postings, and keeping a candidate locked to one city loses good opportunities. Priya's original files do not say she would relocate; this is my change to the persona.
- `search.open_to_remote: true` copies `geography.open_to_remote` from Priya's original `profile.yml`.

Résumé fields **the rule reads**: `personal.location`, `search.target_titles`, `search.exclude_titles`, `search.open_to_remote`, `search.open_to_relocate`.

Résumé fields **the Claude judge also receives**: the same five plus `skills.languages`. The rule does not read skills.

Résumé fields **the persona validator checks**: `personal.email`, `personal.phone`, and every email-shaped string in the file.

**4. Posting fields used.** `id` (to decide what is new), `title` and `location.name` (for both judges), `absolute_url` (only copied into the output).

**5. Everything else it needs.**
- `state/seen-ids.json`: every posting id seen so far. If it does not exist, the run is the baseline.
- `runs/run-NN-YYYY-MM-DD/raw-response.json`: the board's response saved exactly as received, as evidence.
- `ANTHROPIC_API_KEY` in a local `.env` file (git-ignored, never committed). It is needed only when there are new postings to judge.
- Node.js 22 or later (built and tested on 24.8.0), npm, and one dependency: `@anthropic-ai/sdk`. Claude model: `claude-haiku-5-5`.

## Out

**For each new posting**, two verdicts side by side, one per judge:

```
{
  "posting_id": <Greenhouse id>,
  "title": "<posting title>",
  "url": "<absolute_url>",
  "rule": {
    "kind": "record",
    "verdict": "relevant" | "not_relevant",
    "justification": "<names at least one résumé field and one posting field, with their values>"
  },
  "claude": {
    "kind": "judgment",
    "verdict": "relevant" | "not_relevant" | "no_verdict",
    "justification": "<same requirement>",
    "resume_fields": ["<résumé field paths Claude cited>"],
    "posting_fields": ["<posting fields Claude cited>"],
    "model": "claude-haiku-5-5",
    "judged_at": "<ISO timestamp>",
    "raw_output": "<Claude's reply exactly as received>",
    "reason": "<only when no_verdict: why the answer was rejected>"
  }
}
```

- The rule's verdict is always `relevant` or `not_relevant`; it can always be computed.
- Claude's verdict is `no_verdict` only when its answer failed the validator or the call failed. A malformed answer is never guessed into a verdict.

**For each run:** run number, start time, host and URL, whether it was seeded (run against a saved response instead of a live fetch), whether it was the baseline, number of postings fetched, number of duplicate ids removed, number of new postings, and the raw-response file name with its SHA-256 hash.

**Where it goes:** a JSON report per run (`runs/run-NN-YYYY-MM-DD/report.json`) plus a short printed summary, one line per new posting showing both verdicts.

## Refuses

| The agent will never | What happens instead |
|---|---|
| Fetch any host not on the allow-list | It exits with an error naming the host; nothing is fetched |
| Show a real résumé on screen or on GitHub | The persona validator rejects the résumé if any email does not end in `@example.com` or the phone number does not contain `555`. The run stops before any fetch |
| Present a model's judgment as a fact | Every Claude verdict is stored and printed with `kind: "judgment"`, the model and the date, and is never mixed into the rule's record |
| Accept a Claude answer in the wrong format | The validator rejects it and records `no_verdict`, never a guess |
| Apply to a job, email or message anyone, or log in anywhere | No code path exists for any of these |
| Write outside its own folder | The state file and raw responses go only into `state/` and `runs/` inside this folder |

## The rule

A posting is **relevant** if all three conditions hold. Otherwise it is **not relevant**.

How terms match: case-insensitive, and whole words only. A term matches only when the character before it and the character after it are not letters or digits, so "Intern" does not match "Internal" and "Lead" does not match "Leadership". A multi-word term matches as a phrase. Runs of spaces in the title are collapsed to one space before matching.

1. **Title includes** at least one term from `search.target_titles`: "AI Engineer", "ML Engineer", "Machine Learning", "Applied AI", "Data Engineer", "LLM".
2. **Title excludes** every term in `search.exclude_titles`: "Senior", "Staff", "Principal", "Lead", "Manager", "Director", "Head of", "Intern". Priya has one co-op and a new MS degree, so senior titles are out.
3. **Location.** Split `location.name` on `|` and `;` into separate locations and trim each one. At least one of them must:
   - (a) equal `personal.location` ("Boston, MA"), or
   - (b) equal one entry of `search.open_to_relocate` ("San Francisco, CA", "New York City, NY"), or
   - (c) contain both the whole words "Remote" and "United States", when `search.open_to_remote` is true.

The rule's justification names the include term that matched (or says none did), any exclude term that matched, and the location that passed (or says none passed, listing them).

**Worked examples** (real titles and locations from the board on 2026-10-28):

| Title | location.name | Verdict | Why |
|---|---|---|---|
| Data Engineer, Product | San Francisco, CA \| New York City, NY \| Seattle, WA | relevant | "Data Engineer"; no exclude term; "San Francisco, CA" is in open_to_relocate |
| Manager, Applied AI Architect | Seoul, South Korea | not relevant | "Manager" is excluded (and Seoul fails the location check) |
| Applied AI Architect | Mumbai, India | not relevant | "Applied AI" matches, but no location passes |
| Research Engineer, Machine Learning (RL Velocity) | Remote-Friendly (Travel-Required) \| San Francisco, CA \| New York City, NY | relevant | "Machine Learning"; the remote location has no "United States", but "San Francisco, CA" passes |

Known weakness, found while checking the rule against the board on 2026-10-28: "Applied AI" also matches non-engineering titles such as "Recruiter, Applied AI" in San Francisco, which this rule calls relevant. The rule stays as written; this is a place where I expect the Claude judge to disagree.

## Wrong versions (my tests must catch these)

**W1. Substring matching.** The code uses `title.includes("intern")` instead of a whole-word match, so a title like "AI Engineer, Internal Tools" is wrongly excluded by "Intern", and "Lead" wrongly excludes "Leadership".
Caught by: fixture postings "AI Engineer, Internal Tools" and "ML Engineer, Leadership Programs", both in "Boston, MA", must both come out **relevant**.

**W2. Verdicts paired with the wrong postings.** The code matches Claude's results to postings by array position. When one Claude call fails or is skipped, every later verdict shifts onto the wrong posting.
Caught by: 3 new fixture postings where the Claude call for the middle one fails. Each Claude verdict's `posting_id` must equal its own posting's id, the middle one must be `no_verdict`, and the first and third must keep their own verdicts.

**W5. The baseline reports everything as new.** On the first run (no state file), the code prints every fetched posting (681 on the board today) as new.
Caught by: run 1 with no state file must report 0 new postings and save every fetched id to the state file.

## What a failure looks like

(2026-10-28) This agent fails if run 2 reports as new any posting id that was already saved in run 1's state file, or if the same posting id appears more than once in a run's list of new postings (a duplicate it should have removed).

## Changes from my answers (made by Claude at my request)

1. **Persona email check:** my answer said emails must end in `@northeastern.edu`. Corrected to `@example.com`: Priya's file uses `priya.nair@example.com`, the brief requires `@example.com` addresses, and a `@northeastern.edu` check would accept a real student email.
2. **Out:** my answer listed only the rule's verdict. Step 3 needs a Claude verdict for every new posting, and my W2 test checks Claude verdicts, so the `claude` block (from the shape I was offered) was added.
3. **In:** I listed skills as an input. The rule never reads skills, so `skills.languages` is listed as an input to the Claude judge only.
4. **The rule, location:** my answer did not say how to split `location.name`. On 2026-10-28, Anthropic's board joins locations with both `|` and `;` (for example "New York City, NY; San Francisco, CA"), so the rule splits on both. "Remote" plus "United States" now applies only when `search.open_to_remote` is true, and the relocation cities are written out.
5. **W1:** "Leadership Programs Engineer" contains no target term, so it could never be relevant. The test title is now "ML Engineer, Leadership Programs".
6. **W5 and the failure sentence:** "all 680" became "every fetched posting" (681 today). "fails to identify & remove the duplicate result" became the duplicate-id sentence above.
