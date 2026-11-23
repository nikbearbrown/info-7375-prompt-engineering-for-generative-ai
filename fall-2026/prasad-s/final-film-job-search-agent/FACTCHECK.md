# FACTCHECK: WorthLoop final project film

Every factual claim in NARRATION.md, with its source. I read each
outside source on 2026-11-22. Claude Code checked the code references
read-only on 2026-11-21 and 2026-11-22. Paths are relative to
fall-2026/prasad-s/.

## From outside sources

- B3, Greenhouse said job ads on its platform draw about 254 applicants
  each (July 2026); its software runs many job pages: Fortune,
  2026-07-27, Orianna Rosa Royle, interviewing Greenhouse CEO Daniel
  Chait. The 254 is Greenhouse's own figure.
- B4, employers say auto-apply tools put the wrong information in the
  wrong fields; one company's HR chief called them snake oil: The
  Washington Post, 2026-03-01, Danielle Abril, republished by the
  Philadelphia Inquirer. The HR chief is Joseph Eitner, chief HR officer
  at Eaton Capital Management.
- B5, career-ops lets the person press Submit, and checked 740 listings
  for its maker: 68 applications, 12 interviews, one offer: the
  career-ops README, github.com/career-ops-hq/career-ops.
- B6, one standard there, AP2 (named on screen), says the asking screen
  must be plain code, not AI: AP2 specification v0.2, ap2-protocol.org.
  The Trusted Surface must be non-agentic.
- B6, others built the payment check well: the AsAsked README
  (github.com/ginjikurata/asasked) and the Mandate Shield README
  (github.com/LSUDOKO/Mandate-Shield). Mandate Shield reports 15 of 15
  attacks blocked and 35 of 35 legitimate cases passed on its own
  benchmark, and says itself that this shows internal consistency, not
  real-world proof.
- B7, in the job tools I didn't find a test locked before tuning, or
  approval tied to the exact packet: my reading of the career-ops
  README. It has golden evals and a check that CV facts aren't made up.
  I found no test set locked before tuning, and no approval bound to a
  fingerprint of the packet; the person reviews and presses Submit.

## From my own work

- B6, in October I pitched that check for payments: my pitch film,
  final-project-film/.
- B7 and B15, my filter missed the one worth-it posting in my last test,
  reading "prefers five years" as a hard rule:
  js3-filter-tool-score/MEASURE.md lines 39 and 46;
  js3-filter-tool-score/FILTER.md line 34 (F10).
- B8, the public job boards of four companies:
  js3-filter-tool-score/config.json lists five boards, and four are
  watched: js3-filter-tool-score/GATE.md lines 12-15 are the four
  watched boards; line 16 is a fifth that fails on purpose.
- B9, the filter checks title, level, place and years:
  js3-filter-tool-score/FILTER.md lines 18 (F3), 33 (F9), 19 (F4) and
  34 (F10).
- B10, the scorer is reached through MCP, rules in code limit each tool,
  and a run stops at 10 requests or 60 seconds:
  js3-filter-tool-score/tools/mcp_server.py;
  js3-filter-tool-score/agent/policy.py;
  js3-filter-tool-score/agent/run.py lines 30-34;
  js3-filter-tool-score/GATE.md lines 34-36.
- B12, free tools and no paid credits, with Claude through the
  university: js3-filter-tool-score/README.md (Python standard library
  only); the course repo's AGENTS.md lines 7-10.
- B13, the test set: 20 postings, drawn and sealed on 2026-11-15 before
  any tuning (js3-filter-tool-score/SEAL.md lines 39 and 65; commit
  449a200b; the first rule changes, v2, came on 2026-11-19,
  js3-filter-tool-score/FILTER.md line 104, so "before any tuning"
  rests on dates). The tools skip or refuse it:
  js3-filter-tool-score/tools/mcp_server.py,
  js3-filter-tool-score/tools/filter_run.py,
  js3-filter-tool-score/tools/measure.py.
- B13, about one in thirty worth it in my last test: 1 of 30 after my
  re-check; js3-filter-tool-score/MEASURE.md line 32.
- B15, a Staff title is too senior for Alex, who looks for roles asking
  three years or less: js3-filter-tool-score/FILTER.md line 33 (F9);
  js3-filter-tool-score/resume_persona.json line 8 (max_years_required
  3).

## Not claims of fact

B1, B2, B11, B14, B16 and B17 describe what I'm building and how I'll
test it. B9's posting is constructed. Alex Rivera is fictional.
