# FILTER.md — Job-Search Agent 3: The Filter, the Tool, and the Score

## Executive summary

Written before any code, per the assignment's own rule. This defines what
makes a collected posting worth showing Priya, what counts as supported
evidence in a shortlist justification, which boards/fields the agent
expects to see, and two plausible-but-wrong filter/ranking implementations
the tests must catch.

## Starting point

Builds directly on Job-Search Agent 1 (contract, single-board watch, rule
+ Claude judgment) and Job-Search Agent 2 (bounded loop across gitlab,
stripe, palantir; removal detection; permissions enforced in code). This
assignment adds a third layer on top of what JS2 already collects: a
readable filter, a reject audit, a source-grounded shortlist, an MCP tool
server, and a held-out scoring experiment.

## The filter (v1.0.0), as a document

A collected posting is RELEVANT if ALL of the following hold. Each rule
has one line of reasoning.

1. Title or content contains at least 2 of 6 role/skill words (inherited
   from JS1/JS2's rule: Python, RAG, LLM, PyTorch, LangChain, vector
   databases), matched whole-word, case-insensitive.
   Reasoning: a direct carryover from JS1's tested rule -- it's a known
   quantity with a documented false-negative gap ("LLMs" plural), not a
   new unexamined rule.
2. Title does not contain a sales/GTM/people-ops role-type word (Sales,
   Account Executive, Solutions Architect, Compensation, Recruiter, HR),
   UNLESS the content also contains an explicit AI-systems-building phrase
   (train, fine-tune, RAG pipeline, build an agent, LLM application).
   Reasoning: JS1's Sampling Report found the rule's biggest failure mode
   was sales/pre-sales roles matching on stray keyword mentions; this
   narrows that specific false-positive class without re-litigating every
   case.
3. A posting whose content is empty or missing is NOT silently filtered
   as "not relevant" -- it is flagged insufficient_data and excluded from
   both the relevant and rejected buckets.
   Reasoning: JS2's FINISHED-WRONG-ANSWER.md demonstrated that a quiet
   empty response looks identical to "nothing relevant here"; the filter
   must not repeat that mistake at this layer.

## Evidence rules (for the source-grounded shortlist)

For each claim in a shortlisted posting's justification:

- Supported: the claim can be directly traced to an exact substring
  of posting.title or posting.content.
- Contradicted: the posting's own text states something that conflicts
  with the claim (e.g., justification claims "remote-friendly" but the
  posting explicitly requires on-site presence).
- Insufficient: the claim is plausible but nothing in the posting's
  text confirms or denies it (e.g., a claim about visa sponsorship when
  the posting never mentions it).

Abstention rule: if a shortlisted posting has ANY claim labeled
contradicted, the agent must not present a relevant verdict without
surfacing that contradiction explicitly -- it may not silently drop the
contradicted claim and show only the supported ones.

## Expected sources

Same three boards as JS2: gitlab, stripe (Greenhouse), palantir (Lever).
Expected fields: id, title, content (or Lever's equivalent
descriptionPlain). If content/descriptionPlain is null or empty for
a posting that otherwise has an id and title, the agent reports
insufficient_data for that posting, never a default relevance verdict.

## Wrong versions (tests must catch both)

1. Reject bucket silently drops insufficient-data postings: a filter
   implementation that treats an empty-content posting as "not relevant"
   rather than flagging it insufficient_data and excluding it from the
   reject audit's sampling pool entirely (since you can't hand-judge a
   posting with no text).
2. Shortlist justification cites a claim with no grounding check: an
   implementation that produces a relevance verdict and prose
   justification without running each claim through the
   supported/contradicted/insufficient classifier -- i.e., the label step
   is skipped or hard-coded to "supported" for everything.

## What a failure looks like

(dated before any code was run)

2026-11-21: a failure is any shortlisted posting whose justification
contains a claim labeled supported that cannot actually be found as a
substring (or a clear paraphrase traceable to one) anywhere in that
posting's own text -- i.e., a hallucinated grounding label, not an honest
insufficient.

## Toolchain

- Language: Python 3.x (same as JS1/JS2)
- Reuses: JS2's agent/loop.py (collection), agent/boards.py,
  agent/permissions.py
- New: a filter module, a reject-audit worksheet generator, a
  source-grounding classifier, an MCP-shaped tool server (stdlib only or
  a minimal MCP SDK -- decide at build time), a scoring-experiment harness
- No external services beyond JS2's existing allow-list, plus
  api.anthropic.com for the shortlist judgment and tool-server scoring
  calls

## Amendment 2026-11-22: v1.1.0, rule 4

Everything above this heading is v1.0.0 as originally written, and is not
edited. v1.1.0 is v1.0.0 plus the rule below, and nothing else. The
evidence is in EXPERIMENT.md (sections 4, 7 and 8). The code is
`js3/rule4.py` and `js3/filter_v110.py`.

4. A posting that passes rules 1-3 is REJECTED if its content states an
   explicit experience minimum of 3 years or more ("N+ years", "N-M years"
   taking the lower bound, "at least N years", "minimum (of) N years", or
   "N or more years"), OR its title contains a seniority word, whole-word
   (Staff, Principal, Director, Manager, Head of), OR its content contains
   a people-management phrase ("managing managers", "lead a team of N",
   "manage ... team(s)", "own the P&L", "people management", "direct
   reports").
   Reasoning: the reject audit (REJECT-AUDIT.md) found 19 of the 20
   v1.0.0-relevant postings not relevant, mostly on an experience,
   seniority or management axis the filter did not have.

   Graduation-date and security-clearance requirements are FLAGGED, never
   rejected. `resume.json` has no graduation date or clearance field, so a
   mechanical rule cannot know whether they are met. Rule 3 still runs
   first: a posting with no content is never evaluated by rule 4.

**What it was promoted on.** It removed 10 of 11 false positives on the
dev split (90.9%) and 5 of 8 on the held-out split (62.5%; 95% CI
24.5–91.5%). It fired on no hand-relevant posting in either split.

**What it was not promoted on:**
- **Bucket precision.** On held-out it stayed 0/8 → 0/3 = 0.000. Held-out
  contains no true positives in that bucket, so no reject-only rule could
  move it.
- **Any claim that rule 4 catches every experience or eligibility
  mismatch.**

**What held-out could not test.** It could not test whether rule 4 wrongly
rejects a genuinely good posting. Held-out had one hand-relevant posting
(B032). Rule 4 did not fire on it, but the flag-not-reject choice for
graduation and clearance was made with B032's text already known.

**Known, unfixed limitations of v1.1.0:**
- **"Senior" is not a seniority word.** C04 and C01 (*Senior ...*
  engineering roles) stay relevant. For C04, Om's actual reason was
  Go/Rust and application-security experience, not seniority.
- **The year threshold is 3.** A stated floor of "2+ years" (C14) does not
  fire.
- **No detection of required experience outside Priya's stack**, for
  example security research (C06) or Go/Rust (C04). Rule 4 does not
  attempt this.
- **Any qualifying path counts.** "BS with 4-8 years" fires even when a
  "PhD with 1-3 years" path is also offered (C20).
- **Palantir field scope.** Rule 4 reads `content`, which for Lever is
  `descriptionPlain` only, the same as rules 1-3 (FRICTIONAL.md entry 1).
  Palantir puts its requirements in `lists`, so rule 4 is largely blind on
  Palantir. This amendment deliberately does not change that.
- **Scope of the evidence.** It holds for one collection run (2026-11-21),
  one persona (Priya Nair) and 88 hand-judged postings whose labels the
  designers had already read. Generalization beyond that is not measured.

**Explicitly not done in this amendment:** adding "Senior" or other title
words, lowering the year threshold, an out-of-stack experience detector,
and reading Lever `lists`. Each is a candidate for a future dev-set
experiment, and needs postings that have not already been used as
held-out.
