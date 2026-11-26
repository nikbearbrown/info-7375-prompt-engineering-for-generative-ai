# FRICTIONAL — Job-Search Agent 3

**Status: final (2026-11-25).** Aravind's log. Entries Claude Code typed from Aravind's dictation are
marked as dictated. This file was drafted by Claude (claude.ai chat, Claude Opus 5.5) from Aravind's
answers and the decisions recorded in this project's chat and commits; Aravind reviewed and edited it.

**How I reviewed, overall.** At checkpoints I read Claude Code's summaries and relied on a second
Claude (a claude.ai chat, "chat-Claude") to review them. I did not read every generated file in full.
Every hand verdict, label, and claim confirmation was mine, made in the judging tool. I verified the
filesystem-server findings in its source myself.

## 2026-11-25: manual Phase 3 replies saved under the wrong filenames (dictated by Aravind)

- **What happened.** I skipped a `pbcopy` step while pasting the manual claude.ai replies, so the
  clipboard still held the previous reply. The replies for **A005** and **A010** were first saved
  under the wrong filenames (`A010.txt` and `A014.txt`).
- **How I caught it.** I grepped the replies for `posting_id` and compared each one with its
  filename. I renamed the files; **no content was edited**. A014 was then run afterward in its own
  incognito chat.
- **What changed.** `tools/import-manual.mjs` now rejects any reply whose `posting_id` names a
  different posting than its filename (`checkReplyPosting` in `src/justify.mjs`). Nothing is written
  for that reply, and the exit code is 3 (`test/import-manual.test.mjs`).
- **Verified before import (Claude Code, read-only, 2026-11-25):** all 7 files now have a
  `posting_id` that matches their filename.

## Gate and tests
Commits: `bb88c420` (FILTER.md + tests before code), `affdd761` (W11 fixture fix), Checkpoint 1 edits

- **Accepted from Claude:** Claude Code's FILTER.md v1 structure, wrong versions W1–W12, and the
  interval-based "cannot tell" rule. Option A: Claude writes only the justification; keep/reject is
  deterministic.
- **Modified:** Threshold 0.70 → 0.80. Chat-Claude pointed out that at 0.70 a core-PM posting with
  location = 0 or experience = 0 scored 0.75 and passed, silently loosening JS1's gates. I accepted
  this and added W13 with four exact combinations.
- **Rejected:** Nothing at this checkpoint.
- **What I checked:** The summaries and chat-Claude's review, not every line of FILTER.md.
- **Unresolved:** The weights 0.40/0.25/0.25/0.10 were hand-set and accepted without comparing
  alternatives. Claude Code wrote a W11 test that could never fail (the fixture scored 1.0); it was
  fixed in its own commit, but it shows tests written in the same pass can be vacuous.

## Filter v1.0.0 and the shortlist definition
Commits: `13b4c6c4`, `67e959fb`

- **Accepted from Claude:** Don't loosen the filter to manufacture a shortlist when v1.0.0 kept 0 of
  1,064. Fix the shortlist definition (keep ∪ cannot_tell) before any verdicts.
- **Modified:** The audit plan. I added a 15-row PM-titled stratum on chat-Claude's suggestion, then
  cut it from the judged plan to save time. The cut was committed (`90fcd369`) before judging, so I
  didn't drop rows after seeing them.
- **Rejected:** Claude Code's first plan to judge "A001–A030". It was wrong: rows were shuffled after
  drawing, so the plan uses the seeded draw order instead.
- **What I checked:** That the plan commit came before any verdict.
- **Unresolved:** The PM stratum (15 of 133) was never judged, so there's no error estimate where
  false rejects are most likely. Claude Code also misreported the pool as 136 before correcting it to
  133.

## Reject audit, first pass and recheck
Commits: `90fcd369`, `1c9ce17b`, `2c29cbab`, `7dc781af`, `8f27d02d`, `c711833a`

- **Accepted from Claude:** Claude Code stopped and reported that my verdicts conflicted with the
  written definition, instead of silently changing a rule. Keeping my first-pass verdicts in history
  and reporting both passes side by side.
- **Modified:** 10 of 14 rechecked verdicts. In my first pass I judged from excerpts and never opened
  the full text for years. I marked 12 closest calls relevant that required 5+ to 10+ years, and
  A035 (Dublin) relevant. In the recheck, with full text and a note on every row, I revised 10.
- **Rejected:** Nothing at this checkpoint.
- **What I checked:** Every recheck row against the full posting text, with the deciding line in
  the note.
- **Unresolved:** The random-reject result (0/30 against final verdicts, interval up to 11.6%) is a
  bound for this snapshot under v1.0.0, not a rate. View B is dev use.

## Persona correction and v1.1.0-a
Commits: `f3cefa22`, `cd672e2f`, `bdc146c8`

- **Accepted from Claude:** Recording the correction as made after the audit results, citing the 12
  closest-call rows, and labeling v1.1.0-a as dev use.
- **Modified:** The persona. `years_pm 2` (ceiling 3) did not match the real policy the persona
  stands in for. I apply mostly to roles needing ≤4 years, sometimes 5+ or 6+, never 7+. It became
  `preferred_max_years 4`, `stretch_max_years 6`. v1.1.0-a: keep 0 → 7.
- **Rejected:** Chat-Claude's first recommendation, which was to keep the rules and re-check my
  verdicts against the 2-year definition. I overruled it because the persona, not my judgment, was
  wrong. Chat-Claude then agreed.
- **What I checked:** That the changed rule reproduced my stated policy on the recheck rows.
- **Unresolved:** Because the definition changed after seeing results, v1.1.0-a can't be validated
  on the rows that motivated it, and held-out had no positives to validate it either.

## v1.1.0-b to v1.1.0-e
Commits: `de871afa`, `537bebd0`, `242af122`, `6acfa20d`, `4abf4d39`, `70c22c16` (tag `js3-filter-final`)

- **Accepted from Claude:** One change per version, each with its own commit and measurement.
  -b: boilerplate topic words; keep 7 → 6, the only change was unjudged A065. -c: two veto phrasings,
  0 decision changes. -d: ranges read the lower bound; A010 reject → keep.
- **Modified:** -e: TPM titles dropped to the adjacent tier, citing A027/A044/A052. That made 3
  decisions change, and keep 7 → 4. Fixing the range misread (-d) instead of only logging it was
  chat-Claude's recommendation, and I accepted it.
- **Rejected:** Reading the posting body for product ownership to decide TPM roles. That's a
  judgment, not a rule, and it wasn't buildable in time.
- **What I checked:** Before/after counts for each version. That frozen files didn't change after
  the tag.
- **Unresolved:** Claude Code committed -c (`537bebd0`) after a failed edit, without its CHANGELOG
  row, and fixed it in `242af122`. The boilerplate rule only catches exact copies: 159 Stripe postings
  still count "payments" from reworded intros. A TPM role that truly owns product direction can now
  be wrongly rejected.

## Veto check
Commits: `e0d80ff0`, `63aacc6b`

- **Accepted from Claude:** The sponsor/visa grep. It showed "0 vetoes" meant 0 matches of listed
  phrases, not 0 postings refusing sponsorship. Two real refusals were missed.
- **Modified:** The v1.1 evidence rule, amended before verdicts: changes that can only *remove*
  postings may cite a committed measurement artifact. Changes that add postings still need audit rows.
- **Rejected:** A broad `sponsor|visa` regex. 29 of 31 lines it matched meant something else, like
  "executive sponsor" or "Visa and Mastercard".
- **What I checked:** The two missed lines in the grep table.
- **Unresolved:** Only two phrasings were added. Other wordings of refusal are untested.

## False friends
Commits: `0797611f`, `df3c6ff8`

- **Accepted from Claude:** The primary false friend is "program manager" in the title rule. It
  matched A027/A044/A052 as PM roles and changed 3 decisions against my hand verdicts.
- **Modified:** Claude Code first recorded "training" (Airbnb pay boilerplate, A014/A047) as the
  false friend. Chat-Claude pointed out "training" isn't a filter word, so it never matched anything.
  I moved it to a secondary note.
- **Rejected:** Naming a false friend from corpus counts alone ("payments" 746/776). I required it to
  come from rows I judged.
- **What I checked:** The title of each row and the line where the word appeared.
- **Unresolved:** "Product" in titles also matched non-PM roles in my labels (L04 sales AE, L10
  commercial program manager, D11 product-marketing hybrid). This wasn't measured as a rate.

## Labels
Commits: `28cfad43`, `106cd4a7`, `6fc19f50`

- **Accepted from Claude:** Blind label mode, held-out first, held-out frozen by hash before any
  rule change.
- **Modified:** Nothing.
- **Rejected:** Nothing.
- **What I checked:** I opened the full text for every PM-titled row (the lesson from the audit) and
  judged by the minimum-requirements section only.
- **Unresolved:** All 40 labels came out not relevant. Of the 16 PM-titled label rows, the filter
  read 9 as requiring 7+ years, 4 as 5–6, and 3 as not stated (with the extraction limits in
  §5.4); my notes record why each was not relevant to me. Recall on held-out is unmeasured.

## Claude calls: spend limit and manual route
Commits: `59d8fc69`, `3caf2978`, `21609f36`, `9ab830b9`, `0a3cc5e8`, `d495dfb8`, `1d65ff45`

- **Accepted from Claude:** Keeping the 7 failed `claude -p` calls as evidence. Rendering
  byte-identical prompts for a manual route. An importer using the same validator.
- **Modified:** The route. I ran the 7 prompts in claude.ai incognito chats (Claude Opus 5.5), one
  chat per posting. Incognito was chat-Claude's advice, so project memory and this chat's opinions
  couldn't contaminate the replies.
- **Rejected:** Waiting for the spend limit to reset.
- **What I checked:** That every reply's `posting_id` matched its file (see the dictated entry
  above).
- **Unresolved:** The manual route isn't tool-less the way `--tools ""` is. claude.ai has its own
  system prompt, the model name is self-reported, and there's no session id. The Claude Code session
  was also archived mid-Phase 3 and recovered from git state.

## Claim labels and the location-field amendment
Commits: `40cdc6e8`, `ffd5e49f`, `47cbd6e6`

- **Accepted from Claude:** 46 of Claude's 54 proposed claim labels.
- **Modified:** 8 labels. The 6 Stripe "no location stated" abstentions became **contradicted**,
  because the location field counts as the posting's own text. A010.4 and A042.4 became
  **supported**, citing the "Preferred Qualifications" heading. Both changes were chat-Claude's
  recommendation, which I accepted. The location amendment was made after seeing the replies, and
  that's recorded.
- **Rejected:** Re-running Claude after the amendment.
- **What I checked:** That every supported/contradicted label has an exact quote; the tool refuses
  otherwise.
- **Unresolved:** 39 of 54 claims are judgments, and domain-fit claims (e.g. A020.8) are inferences,
  not entailments.

## MCP server, clients, evaluations
Commits: `461b608d`, `82f18acc`, `592026e1`, `903d314b`, `8c91ddc0`, `111cc67b`

- **Accepted from Claude:** A from-scratch JSON-RPC server with one read-only tool, tests, and a
  pinned hash so the evaluation covers the exact file that ran.
- **Modified:** The client. The Claude Code client run reached `tools/list` but never `tools/call`
  (HTTP 429). I ran 3 calls myself in Claude Desktop: keep, veto, and the boundary test
  `../../README.md`, which was refused server-side.
- **Rejected:** Using Claude's chat explanation as evidence for the boundary. The evidence is the
  transcript and the tests.
- **What I checked:** The 3 calls and screenshots, myself. The filesystem server's key findings
  (Roots replace the allowed directories unless `--confine-roots`; read-only enforced; non-atomic
  writes) in its source, myself.
- **Unresolved:** The tool description said "no posting text" while a veto returns up to 300
  characters of posting text. I found it live in call 2 and fixed it after the run (`111cc67b`). I
  never ran the filesystem server, so its trust decision rests on source reading.

## Phase 5
Commits: `452cffbf`, `450ee861`

- **Accepted from Claude:** The origin table (every number hand-set or inherited, none fitted), and
  one change committed before any held-out look: threshold 0.80 → 0.70.
- **Modified:** I added a diff-set. I hand-judged, blind, the 12 postings that 0.70 adds as keeps:
  3 relevant (D04, D09, D12), 9 not relevant. Two of them are London postings that fail location
  outright.
- **Rejected:** A Phase 5 prompt change, since the held-out r/c set was empty.
- **What I checked:** All 12 diff-set rows, with the full text on the PM rows.
- **Unresolved:** Held-out (all 20 not relevant) only bounds false keeps (up to 16.8%). The diff-set
  is post hoc and not held-out. D09 (5+ years, Seattle/SF) shows 0.80 has a real recall cost:
  stretch roles only pass if a topic word survives the boilerplate rule.

## Lessons I'm taking forward

- **Judge from full text, not excerpts.** My first pass missed the years line on every closest call.
- **The persona must match my real policy.** A wrong persona made the filter "right" and my verdicts
  "wrong" for the wrong reason.
- **Run measurements before changing rules.** Every rule change worth keeping (threshold, vetoes,
  TPM tier, range parse) came from a measurement. The one I nearly made without one, loosening the
  filter to get a shortlist, would have been wrong.