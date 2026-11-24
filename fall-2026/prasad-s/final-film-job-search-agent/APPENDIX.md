# APPENDIX: WorthLoop

Final Project Film, INFO 7375. Prasad Shinde.

The detail behind the film's Methods (B8 to B12) and Evaluation (B13 to
B16), from this folder's OUTLINE.md and the code in
js1-contract-and-watch/ (JS1), js2-loop-tools-diff/ (JS2) and
js3-filter-tool-score/ (JS3). File names without a folder are in
js3-filter-tool-score/; JS2's files are marked JS2. What ran is in the past
tense; what I am still building says "will".

## 1. What and why
WorthLoop is an agent I'm building that watches a few job boards for one
person, judges every new posting against that person's criteria, and
prepares an application packet only for the postings worth their time. A
packet will be released only after the person approves that exact packet;
WorthLoop never submits anything itself.

It matters because hiring is flooded. In July 2026, Greenhouse said job ads
on its platform draw about 254 applicants each (Fortune, 2026-07-27). Job
seekers waste hours on postings that were never a fit, and employers drown
in applications.

## 2. What others have done
- **Tools that apply for you.** They submit at scale. Employers told The
  Washington Post (2026-03-01, Danielle Abril, republished by the
  Philadelphia Inquirer) that these tools put the wrong information in the
  wrong fields; Joseph Eitner, chief HR officer at Eaton Capital
  Management, called them snake oil.
- **Open-source agents that score jobs and let you press Submit.**
  career-ops (github.com/career-ops-hq/career-ops) calls itself a filter
  that finds the few offers worth your time out of hundreds, and advises
  against applying below 4.0 out of 5 (this folder's OUTLINE.md). For its
  maker it checked 740 listings: 68 applications, 12 interviews, one
  offer. It is more careful than the first group: it has golden evals and
  a check that CV facts aren't made up. What I didn't find in it is a test
  set locked before tuning, or an approval bound to a fingerprint of the
  packet; the person reviews and presses Submit (this folder's
  FACTCHECK.md, B7).
- **Approval checks from AI payments.** The AP2 specification v0.2
  (ap2-protocol.org) requires that the Trusted Surface, the screen that
  asks the person, be non-agentic. AsAsked (github.com/ginjikurata/asasked)
  and Mandate Shield (github.com/LSUDOKO/Mandate-Shield) check intent and
  what-you-see-is-what-you-sign. Mandate Shield reports 15 of 15 attacks
  blocked and 35 of 35 legitimate cases passed on its own benchmark, and
  says itself that this shows internal consistency, not real-world proof.
  In October I pitched this check for payments (my pitch film, in
  final-project-film/ beside this folder). Others built it well, so I
  carried it to job applications.

What WorthLoop adds, from this folder's OUTLINE.md: verdicts measured
against hand labels sealed before tuning; an approval bound to a hash of
the exact packet, held outside the agent's reach (planned); and
product-management judgment, such as reading a Staff title or "prefers 5+
years" against a three-year ceiling — today's filter still gets "prefers"
wrong, and my own test caught it (see "The known F10 failure").

## 3. Methods

### The data
WorthLoop reads the public job boards of four companies
(config.json lines 3-7; GATE.md lines 12-15):

| Company | ATS | Board |
|---|---|---|
| Stripe | Greenhouse | stripe |
| Notion | Ashby | notion |
| Duolingo | Greenhouse | duolingo |
| Robinhood | Greenhouse | robinhood |

A fifth board, Ashby's js2nosuchboard, fails on purpose: the name doesn't
exist, so it returns 404 on every run, and because Ashby's 404 body is
plain text, every run also proves the adapter checks the status before it
reads jobs (GATE.md line 16). It is not counted.

Every request is a read-only GET to one of two URL forms
(agent/config.py lines 16-19):
- https://boards-api.greenhouse.io/v1/boards/{name}/jobs?content=true
- https://api.ashbyhq.com/posting-api/job-board/{name}?includeCompensation=true

Only those two hosts are allowed, with the exact path and query for each
(agent/policy.py lines 17-25). The only method used is GET
(agent/tool_layer.py lines 69-70), redirects are never followed (GATE.md
line 55), and the agent never applies, emails, messages, logs in, submits a
form, spends money or uses a credential (GATE.md line 68).

### The frozen corpus
JS3's corpus is 20 raw responses, collected through JS2's run 2
(2026-11-08T01:54:38Z) and nothing later: 8 from Stripe and 4 each from
Duolingo, Robinhood and Notion (FILTER.md lines 64-69). The seal commit
lists each file's SHA-256, and the filter run and the MCP server check the
files against that manifest before judging (tools/filter_run.py lines
15-16; CONTRACT.md line 867). The corpus holds 1,298 postings (Stripe 894,
Robinhood 179, Notion 164, Duolingo 61; FILTER.md line 73). Anything fetched
later is a snapshot that feeds JS4, not this filter (FILTER.md line 72).

Of the 1,298, 51 had already been seen, which left a pool of 1,247: 162
product and 1,085 other (SEAL.md line 45). From that pool I drew the final's
set (20) and JS3's held-out set (30); the other 1,248 postings are
development data.

### Alex Rivera
WorthLoop works for Alex Rivera, a fictional job seeker, "invented, not me"
(CONTRACT.md line 154). The agent refuses to run
unless the persona's email ends in @example.com and its phone number is a
555-01 number (CONTRACT.md lines 275-280), so no real person's data can be
in it. Alex's criteria (resume_persona.json lines 5-8):
- target titles: Associate Product Manager, Product Manager, Product
  Analyst;
- skills: Python, SQL, A/B testing, roadmapping, user research;
- locations: New York, NYC, Remote;
- max_years_required: 3.

### The loop
One run of the watcher (agent/run.py, JS2's loop
carried over unchanged):
1. Parse the config; a refusal or error ends the run here.
2. Before any fetch, check every board URL, the persona read and the
   writable folders against the permission rules.
3. Load and check the persona, and load the newest saved state.
4. Visit the boards in config order, checking the budget before each. For
   each board: GET, with one retry for a timeout, a 5xx or a connection
   error; save the raw response and a sidecar; classify it by status; and
   parse it with that ATS's adapter.
5. Diff the ids against the saved ones, keyed by (board, id): new is every
   id not seen before. A board's first run is a baseline and reports
   nothing new (GATE.md line 18).
6. Write the state, the exit and the report.

Today the loop does not call the filter: the filter and the scorer run as
separate tools (CONTRACT.md lines 861-867). In WorthLoop, each run will
spot what's new, filter and score the new postings, and prepare a packet
for each one worth Alex's time.

### The permission rules
agent/policy.py names each rule (lines 36-48):
- **Fetch:** https only; no userinfo; no non-default port; the host exactly
  boards-api.greenhouse.io or api.ashbyhq.com; one of the two URL forms; a
  board listed in the config for that host.
- **Read:** inside the project folder only.
- **Write:** inside the project folder only, one named file at a time;
  GATE.md is never written; evidence/gate_probes/ and evidence/snapshots/
  are read-only. An overwrite, a write outside state/, evidence/ and
  output/, or a change to config.json or CONTRACT.md needs
  --approve <exact path> on that run, and one approval covers one write.
- **Anything else** (any action other than fetch, read or write) is
  refused.

### The MCP tool
Claude reaches the scorer through a standard plug: tools/mcp_server.py, an
MCP server over stdio written with the standard library only, with one
tool, score_posting (TOOLSERVER.md line 11). It takes a board_key (one of
the four boards) and a posting_id, and returns FILTER v2's verdict, each
condition's status and reason, the score, any missing fields, and, for a
kept posting, the claims behind it. It never returns the posting's text.

It refuses, as a tool error: an extra, missing or non-string argument; an
unknown board; a posting in a sealed set, checked before the corpus loads
("refused: this posting is in a sealed set"); a corpus file that fails its
hash check; and an id that isn't in the corpus (tools/mcp_server.py lines
180-202). On 2026-11-20 it ran with Claude Code: a Stripe posting, 7737124,
came back relevant, and an id from the final's set was refused
(TOOLSERVER.md lines 14-18).

### The budget, and the five ways a run ends
Each run stops at 10 requests or 60 seconds, whichever comes first, with at
most 5 boards and 2 attempts per board; retries count as requests, and a
single request times out at 10 s (agent/run.py lines 30-34; GATE.md lines
34-36). A run ends in one of five ways (GATE.md lines 22-26):
1. **finished**: every board was visited and accounted for. A run with a
   failed board still ends "finished — with failures", naming the board; it
   is not a separate exit.
2. **incomplete**: an operator interrupt, or a required write was refused.
3. **budget-exhausted**: the boards, requests or seconds ran out; boards
   not attempted are listed as not attempted, never as zero.
4. **error**: something outside any one board broke, such as an invalid
   config or a corrupt state file.
5. **refused**: the run's own instructions break the rules; it ends before
   any fetch or write.

### The filter
FILTER.md v2 (2026-11-19) judges title, place, level and years: the title
must contain a target title (F3), the location must match (F4), and a
seniority word in the title (F9) or a stated minimum above 3 years (F10)
fails the level condition. The skills score now only orders the shortlist
(F5, F6). v1 was written on 2026-11-15, before any JS3 code; v2.1
(2026-11-20) clarified the labeling rule (FILTER.md lines 102-105).

### The planned packet and gate
These are not built yet. The packet will hold the posting, draft answers
built only from Alex's profile, and the evidence for the verdict. It will
be released only through an approve step that is plain code, not AI, so
the AI can't approve for you. The approval will be tied to a fingerprint, a
hash, of the exact packet: change one word, and the fingerprint changes.
The check will sit outside the agent's reach (this folder's OUTLINE.md,
part 3). The fingerprints in B11 are the real SHA-256 of two example
packet texts.

### The resources
WorthLoop runs on my laptop, in Python 3.11 or newer with the standard
library only; no pip install is needed (README.md line 21). 392 tests
passed on 2026-11-20 (README.md line 28). The agent holds no API key and
calls no model (CONTRACT.md lines 291-293). I reach Claude
through Claude Code, which enrolled students receive through NEU (the
course repo's AGENTS.md lines 7-10). It needs no paid API credits
(this folder's OUTLINE.md, part 3).

### Built, and next
Built in JS1 to JS3: the watcher (JS2's loop), the filter (FILTER.md,
agent/filter.py and tools/filter_run.py), the scorer (the MCP server), and
the sealed sets (SEAL.md). Next: the packet and the gate, then the final
test on the sealed set. JS4 will be due on December 1, and the final
project on December 20 (the course repo's
assignments/assignment-js4-the-plan-the-evidence-and-the-memory.md line 9
and the course repo's assignments/assignment-final-project.md line 9).

## 4. Evaluation

### The sealed set
The final's test set is 20 postings, 15 product and 5 other, drawn and
sealed on 2026-11-15 (SEAL.md lines 39 and 65; commit 449a200b, "JS3-CP2d:
the draw, sealed"). The draw was deterministic: the seed, a6ac8bbb, is the
first 8 characters of the commit that holds FILTER v1, fixed before the
seal file existed; each posting's rank is the SHA-256 of
a6ac8bbb:<board key>:<id>; and the final's set took the lowest ranks in
each group (SEAL.md lines 49-55). The command was
python3.13 tools/seal_draw.py draw --final 15 5 --js3 22 8.

The set is ids only. Nothing in it was opened or labeled in JS3, and no
labels for it exist anywhere (SEAL.md lines 12 and 63). The scorer refuses
its ids, and the filter, the measurement, the labeling view and the audit
tools skip or refuse them; the labeling view and the audit tool refuse a
final's-set id by name (tools/label_view.py lines 124-126; tools/audit.py
lines 178-180). It was locked before any tuning: the first rule
changes, v2, came on 2026-11-19. One note for honesty: during a read-only
check on 2026-11-21, Claude Code once ran a group count on the final's-set
file; it printed only "product 15" and "other 5", which SEAL.md already
states, and no id or title. Earlier, a directory listing showed the file's
name, size and date, and no contents (this folder's OUTLINE.md, "Seal
note").

Worth-it postings are rare: 1 of the 30 in JS3's held-out set, after my
re-check (MEASURE.md line 32). So the 20 will likely hold none or one. I
will report the exact count. If the set holds none, it can't show that
WorthLoop finds good postings, so JS4's plan will set how worth-it postings
are added: for example, postings published after the freeze, labeled blind
and sealed before any tuning.

### The bar
WorthLoop will have worked only if every check passes:
- it misses none of the worth-it postings;
- it keeps at most 2 of the rest;
- every claim in a packet is supported by Alex's profile;
- every released packet matches its approved fingerprint;
- all five traps are handled the way I decided in advance.

One failure anywhere, and it didn't work. The bar is pass/fail: it shows
the system cleared a stated line, not a reliable success rate.

### The five traps, with their right answers written first
1. **A Staff PM posting**: not a fit, over the level ceiling. F9 already
   fails a seniority word in the title (FILTER.md line 33).
2. **A posting that "prefers 5+ years" and fits Alex in every other way**:
   kept, because "prefers" still invites someone with fewer. Today's filter
   gets this wrong (see "The known F10 failure").
3. **An engineering posting that only mentions working with product
   managers**: not a fit. F3 reads the title only, and FILTER.md's W6
   ("Engineering Manager, Platform") is judged not relevant (FILTER.md line
   81).
4. **Instructions hidden in a posting's text**: ignored; the verdict comes
   from the posting's facts only. JS3 has no test for this yet.
5. **An empty board**: reported as an empty board, never as "no new jobs".
   In JS2's CP7 demo, a constructed empty Duolingo response first ended
   with Duolingo "ok — 0 jobs, 0 new", although 59 ids had been saved
   before (JS2 REVIEW_PACKET.md lines 21-29); after the fix it reads
   "failed — empty board: 0 jobs, 59 ids saved before" (JS2 README.md lines
   122-126), and JS3 tests it (tests/test_review_empty_board.py).

### The controlled failure
I will write the expected result down first. Then I will change a packet
after approval, on purpose. A check separate from the release code must
catch it and refuse it; the packet must be approved again; and I will
review that refusal.

### The stranger run
Last, someone who didn't help build WorthLoop will run it from the README,
on a clean machine.

### What the sample can't show
- A pass on 20 postings is not a success rate. With no errors in 20, a 95%
  upper bound on the error rate is still about 17%, by the formula JS3's
  README uses for its 30 postings, 1 − 0.025^(1/n) (README.md line 75).
- With likely none or one worth-it posting, the set says little about how
  well WorthLoop finds good postings.
- Every hand label is mine, with no second labeler, and the audit showed my
  own error rate: the Staff misread and the missed years (README.md line
  83). The re-check of JS3's held-out labels read only the worth rows, so
  it could move labels only one way (README.md line 80).

### The known F10 failure
F10 fails the level condition on any stated minimum above 3 years,
preferred included (FILTER.md line 97). The one worth-it posting in JS3's
held-out set, posting 23, only prefers 5+ years, and FILTER v2 missed it:
on the held-out set v2 kept nothing, one miss and no wrong keep (MEASURE.md
lines 39-47). On the development set it missed row 31 for the same reason.
The limit was recorded, not fixed (FILTER.md line 117). It is the mistake
the film's B7 and B15 describe.

### Open, for JS4's PLAN.md
JS4's PLAN.md doesn't exist yet. It will settle:
- how the final's set is labeled and opened: SEAL.md has no procedure for
  it yet;
- how worth-it postings are added if the final's set holds none;
- the F10 fix, so a posting that only prefers 5+ years isn't failed for
  that alone, made on development data only, before the final's set is
  opened;
- JS3's "Not checked" items (README.md lines 78-83): F10's years pattern on
  other phrasings, the held-out set's not_worth labels, and a second
  labeler.
