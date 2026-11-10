# FRICTIONAL — Job-Search Agent 2

Riya Kapadnis · 2026-11-09 to 2026-11-10. The entries are my answers, typed in the Claude Code chat and kept as I wrote
them (obvious typos fixed). Claude added only the "What happened" facts, the dates and the links to commits and files.

## 1. The instructor's empty-board note was out of date (2026-11-09)

**What happened:** Lectern's `ATS.md` (probed 2026-09-26) says Greenhouse `hubspot` returns a valid but empty board.
Before GATE.md, Claude curled it: it returned **HTTP 404**. I moved the empty-board trap to SmartRecruiters `hubspot`
(200, `totalFound: 0`), which still works. Recorded in GATE.md "Board facts" (`61c093d`) and SOURCES.md.

**In my words:** "no i didnt expect professors notes to be outdated. this taught me to cross check all the information before using it. If I hadn't, my demo would have used a board that just errors out."

## 2. `--allowedTools "Read,Edit"` did not limit the patch session (2026-11-09 20:41 UTC)

**What happened:** I started the Claude Code patch with `--allowedTools "Read,Edit"`, expecting Read and Edit only.
The session's tool log shows it ran a Bash `grep "intern" tests/ *.md`, which read my test file, and tried two more Bash
commands (a python write and the test run). Those two were refused only because a headless run cannot approve them.
Its Edits to `rules.py` were allowed and expected. Evidence: `review/patch_session_tool_calls.md` rows 2, 3, 8;
`permission_denials` in `review/claude_patch_response.json`; REVIEW_PACKET.md §3. Commit `8449968`.

**In my words:** "that really made me think about using a setting as it is and not checking it first, because there might
be a difference between what we think the setting will do and what it actually does, just like how in this case it searched
through my test file and tried to run commands, which i thought it never would."

**Unresolved:** I have not tested `--disallowedTools Bash`, the flag that should actually block it (SIGNOFF "Not checked" 7).

## 3. My first reproduce command failed (2026-11-09)

**What happened:** the command Claude gave me started with `cd fall-2026/riya-k/js2-loop-tools-diff`, but my shell was
already inside that folder, so it failed with `no such file or directory`. Claude sent the same command with the full
`~/Documents/...` path, and I re-ran it (the red-test output in REVIEW_PACKET.md §1).

**In my words:** "i was just confused as to why it happened, then Claude explained my terminal was already inside the folder, and the full-path command worked."

**What changed:** every command in README.md starts with one `cd fall-2026/riya-k/js2-loop-tools-diff` from the repo root, so it works from a fresh clone.

## 4. I went beyond the TA's Intern request: full-time only (2026-11-09)

**What happened:** the TA asked only for an Intern exclusion. I also asked to exclude co-op and part-time jobs, and agreed
to count Contract and Temporary as not full-time. Claude kept that as a separate change (amendment 4) so the review
packet stayed in scope: test committed red first (`2eb2a7c`), then the change (`295f3f5`). Checking the real day-1 data
turned up Notion's "Outcomes Architect [Contract]" with `employmentType: FullTime`, so the rule excludes a posting if
either the title or the field says it is not full-time (RULE.md, amendment 4).

**In my words (my answer, lightly reworded by Claude at my request):** "I wanted to exclude part-time and co-op jobs too,
because they work like internships. I can't do an internship now. I need a full-time job, 40 hours a week, not around 20
hours like an internship. This agent is also meant for people who are graduating and will only apply for full-time jobs."

**Unresolved:** Greenhouse gives no employment type, so a Greenhouse part-time job whose title doesn't say so still gets
through (SIGNOFF "Not checked" 3).

## 5. What was unclear to me (2026-11-09)

**In my words:** "what is unclear to me was what a budget or retry is and why a 404 wasnt retried like if it doesnt exist then it shouldnt show up"

**After Claude explained it (budget = a hard limit per run; retry = asking again once after a temporary failure; a failed
board is shown as `failed` with `postings: null` so it is never hidden or turned into "0 jobs"):**
"now i understood what retry means. a retry means trying once again after there is an issue but if it shows 404 then do not
retry because 404 means it doesnt exist and it is an answer in itself and we dont need to retry there because it will give
the same 404 answer"

**Unresolved (a fact, added by Claude):** a real retry never happened in my live runs. No board timed out or gave a 5xx,
so the retry has only been seen working in the tests (`test_timeout_retried_once_after_wait_then_succeeds`, `test_5xx_retried_at_most_once`).

## 6. Why I kept asking "is this correct / best practice?" (2026-11-09)

**What happened:** before committing GATE.md I asked whether my four choices were correct and best practice, and before the
boundary tests ran I asked whether so many "refuse" predictions were right. Claude explained why each choice fits the brief
(and that the five "allow" rows prove a refuse-everything policy would fail), and I kept them. GATE.md `61c093d`,
BOUNDARY.md `2b6071e`.

**In my words:** "a little of everything, because i want it to be perfect but also in order to be perfect i dont want to miss
out on basic things or basic practices as to how it is usually done and how i am doing"

## 7. The same run took 4 s on day 1 and 41 s on day 2 (2026-11-10)

**What happened:** with the same command and the same boards, day 1 took 4.03 s in total, while on day 2 the Databricks
response alone took 34.07 s (9.96 MB, 914 postings, compared with 918 the day before). The 20 s request timeout did not fire,
because it applies to each socket read and not to the whole download. The run still ended at 41.20 of its 60 s.
Evidence: `runs/trace/20261110T194501Z-live-day2.jsonl` (request at t=0.001, response at t=34.067); TRACE.md §4;
SIGNOFF "Not checked" 6.

**In my words, before:** "i thought that because it took 4sec yesterday it should take the same time today too but it took
extra time maybe because there were new job posts or yesterday the site was already opened and again to open it it took
only 4 sec."

**After Claude pointed out that both guesses don't fit the data (Databricks had fewer postings, and each run starts fresh
with nothing remembered from the day before):** "now i understand why it was slower and it has nothing to do with our agent,
it all depends on databricks server and internet and thats why we have budget of 60 sec to break the cycle if it takes more
time than that to complete or else it can go on and on"

**Unresolved (a fact, added by Claude):** I don't know why Databricks was slow on day 2, and nothing in my saved files can
show it. A run stopped by the 60 s budget (`budget_exhausted`) has still never happened live.

## What I accepted, modified, or rejected from Claude (facts, compiled by Claude from the chat and commits)

- **Accepted:** all four GATE.md choices I picked were the options Claude had marked "Recommended". I asked why they were
  best practice before accepting them. Also accepted: Claude's proposed repeat rule, exit wording and list of wrong versions; its three
  additions to GATE.md before the commit (independent check outside the agent's budget, `finished` shown by a seeded run,
  the naive mode labeled as a demonstration); the Intern patch (REVIEW_PACKET.md §5).
- **Modified:** Claude's first suggestion for which intern words to exclude offered three options; I chose the narrowest
  (Intern, Internship). I widened the rule myself with amendment 4 (full-time only), which the TA had not asked for.
  I corrected my own FRICTIONAL entry 2 after Claude pointed out that the Edits were allowed, and only the search and the
  attempted commands were unexpected.
- **Rejected:** nothing Claude proposed was rejected outright.
