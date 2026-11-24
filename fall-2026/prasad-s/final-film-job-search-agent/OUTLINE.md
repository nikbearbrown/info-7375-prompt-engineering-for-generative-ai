# WorthLoop: outline of the final project film

Final Project Film, INFO 7375. Prasad Shinde. Written 2026-11-21.

This is the plan for the film's four parts, in the professor's order. It
is not the narration: the narration will be shorter and plainer, and the
detail here becomes the backbone of APPENDIX.md.

## The four parts

1. Executive summary (done by 0:55): I'm Prasad. WorthLoop is an agent
   I'm building that watches a few job boards, judges every new posting
   against one person's criteria, and prepares an application packet that
   is released to the person only after they approve that exact packet —
   it never submits anything itself. It matters because the AI
   application flood wastes both sides: employers drown in spam, and job
   seekers burn their own hours on postings that were never a fit.

2. What others have done: Tools that apply for you submit at scale and
   got wrong information in the wrong fields and one employer's verdict
   of "snake oil" (Washington Post); open-source agents that score jobs
   and let you press Submit — career-ops calls itself a filter that finds
   the few offers worth your time out of hundreds, advises against
   applying below 4.0 out of 5, and its creator reports 740+ listings
   evaluated, 100+ tailored CVs, and one dream role landed; and approval
   checks from AI payments — AP2 requires a non-agentic approval screen,
   and AsAsked and Mandate Shield check intent and
   what-you-see-is-what-you-sign. In October, I pitched this approval
   check for payments. Others have built that well. So I carried the
   check over to job applications. Mine adds what I didn't find in
   theirs: verdicts measured against hand labels sealed before tuning,
   with deliberate failures; an approval bound to a hash of the exact
   packet, held outside the agent's reach; and product-management
   judgment — Staff titles and "prefers 5+ years" read against a
   three-year ceiling; today's filter still gets "prefers" wrong, and my
   own test caught it.

3. Methods: WorthLoop works for Alex Rivera, a fictional job seeker, so
   no real person's data is in it. It reads four job boards through their
   public APIs. Claude already reaches its first tool through a standard
   plug — the scorer — and the rest come next; rules in the code say what
   each tool may and may not do. Each run, it spots what's new since last
   time, filters and scores the new postings, and prepares a packet — the
   posting, draft answers built only from Alex's profile, and the
   evidence for the verdict — inside a hard limit of 10 requests and 60
   seconds per run. The packet is released only through an approve step
   that is plain code, not AI, so the AI can't approve for you, and the
   approval is tied to a fingerprint of the packet: change one word and
   the fingerprint changes. WorthLoop runs on my laptop with free tools,
   needs no paid API credits, and reaches Claude through the Claude Code
   access the university provides. What's built so far is the watcher,
   the filter, the tools, and a sealed test; what's next is the packet,
   the gate, and the final test on the sealed set.

4. Evaluation: Worth-it postings are rare — 1 of the 30 postings in my
   last test set, by my own labels — so the test set is the one already
   sealed for the final: 20 postings drawn alongside JS3's set on Nov 15,
   locked before any tuning, and withheld by the filter and measurement
   tools, with the scorer refusing it outright. It will
   likely hold none or one worth-it posting, and I will report exactly
   how many; if it holds none, it can't show that WorthLoop finds good
   postings, so JS4's plan sets how worth-it postings are added — for
   example, postings published after the freeze, labeled blind and sealed
   before any tuning. It worked if it misses none of them, keeps no more
   than 2 of the rest, every claim in a packet is supported by Alex's
   profile, every released packet matches its approved fingerprint, and
   all five traps are handled the way I decided in advance. It didn't
   work if it misses one worth-it posting, keeps more than 2, lets one
   unsupported claim into a packet, releases one packet whose fingerprint
   doesn't match, or falls for one trap. That bar is pass/fail — it shows
   the system cleared a stated line, not a reliable success rate. The
   five traps, each with its right answer written down first: a Staff PM
   posting — not a fit, over the level ceiling; a posting that "prefers
   5+ years" and fits Alex in every other way — kept, because "prefers"
   still invites someone with fewer; an engineering posting that only
   mentions working with product managers — not a fit; instructions
   hidden in a posting's text — ignored, the verdict comes from the
   posting's facts only; and an empty board — reported as an empty board,
   never as "no new jobs." The controlled failure is a packet changed
   after approval — predicted in writing first, triggered on purpose,
   caught by a check separate from the release code; the packet is
   refused, must be re-approved, and I review that refusal. Last, a
   stranger who didn't help build it runs WorthLoop from the README on a
   clean machine. How the final's set is labeled and opened, and how
   worth-it postings are added, go in JS4's PLAN.md and in the appendix.

## Checked against the code, 2026-11-21

Read-only checks by Claude Code in js1-contract-and-watch/,
js2-loop-tools-diff/ and js3-filter-tool-score/:

- Four boards are watched: Stripe, Duolingo and Robinhood on Greenhouse,
  Notion on Ashby (config.json, GATE.md). A fifth, js2nosuchboard, fails
  on purpose and is not counted.
- Every request is a GET; nothing posts to or writes to a board
  (agent/tool_layer.py, agent/policy.py).
- Per-run limits: 10 requests and 60 seconds (agent/run.py, GATE.md).
- The MCP server has one tool, score_posting, and refuses sealed ids
  (tools/mcp_server.py).
- The final's held-out set: 20 postings (15 product, 5 other), drawn and
  sealed on 2026-11-15 in commit 449a200b, unlabeled and unchanged since
  (SEAL.md for the size, mix, date and no labels; git log for the commit
  id and "unchanged since").
- JS3's held-out set: 1 worth-it posting of 30 after my re-check
  (SEAL.md, vault/).

Seal note: during these checks, Claude Code once ran a group count on
vault/final_heldout_ids.tsv. It printed only "product 15" and "other 5",
which SEAL.md already states. No id or title was shown. Earlier, a
directory listing of vault/ showed the file's name, size (2,030 bytes)
and date, and no contents.

## Open, for JS4's PLAN.md

- How the final's set is labeled and opened: SEAL.md has no procedure
  for it yet.
- How worth-it postings are added if the final's set holds none.
- Fix F10 so a posting that only prefers 5+ years isn't failed for
  that alone. FILTER v2 still fails it (FILTER.md:105, MEASURE.md:46).
  The fix uses development data only, before the final's set is
  opened.

## Sources

Checked by Claude.ai on 2026-11-21. I read each one myself before it
goes into narration.

- Fortune, 2026-07-27: Greenhouse CEO Daniel Chait on the "AI doom
  loop".
- The New York Times (DealBook), 2025-06-21, Sarah Kessler, "A.I. Sludge
  Has Entered the Job Search" (read through The Star's syndicated copy).
- TIME, 2025-03-23, Michael B. Horn, opinion: LazyApply and JobCopilot.
- The Washington Post, 2026-03-01, Danielle Abril, republished by the
  Philadelphia Inquirer: auto-apply tools; "snake oil".
- AP2 specification v0.2, ap2-protocol.org.
- AsAsked, github.com/ginjikurata/asasked.
- Mandate Shield, github.com/LSUDOKO/Mandate-Shield.
- career-ops, github.com/career-ops-hq/career-ops.
