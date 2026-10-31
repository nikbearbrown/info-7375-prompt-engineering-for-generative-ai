# CONTRACT.md — Job-Search Agent 1

## Executive summary

This is the contract the agent is built against. It states what goes in,
what comes out, what it refuses to do, the exact rule it uses to decide
relevance, two ways a correct-looking implementation could actually be
wrong, and what a failure would look like. This file was written before
any code, per the assignment's own instruction — Claude Code implements
against it, not the other way around.

## In

- `board`: a Greenhouse board token (string), e.g. `"gitlab"`.
- `resume`: a JSON résumé for a fictional persona (fields: name, target
  roles, key skills, years of experience, location/remote preference,
  visa/sponsorship need). No real person's data.

## Out

For each posting newly seen since the last run:
- `verdict`: `"relevant"` or `"not relevant"`.
- `justification`: a string naming the specific résumé field(s) and
  posting field(s) that drove the verdict — never a bare assertion with
  nothing named.

## Refuses

- Fetching any host not on the allow-list (`boards-api.greenhouse.io`
  only, for this board).
- Displaying a real résumé on screen or committing one to GitHub — only
  the fictional persona's JSON is ever shown or committed.
- Presenting Claude's judgment-verdict as if it were the rule-verdict, or
  vice versa — the two are always labeled separately (record vs. judgment).

## The rule (hand-computable)

A posting is **relevant** if, and only if:

Its `title` or `content` contains at least 2 of these 6 skills
(case-insensitive, whole-word match): **Python, RAG, LLM, PyTorch,
LangChain, vector databases**.

Otherwise: **not relevant**.

No location or department exclusion is applied — GitLab's board is
already mostly remote-friendly, and a TA should be able to verify a
verdict by reading the posting's title/description and counting skill
matches alone, with nothing else to check.

## Wrong versions (tests must catch both)

1. **Label/posting mismatch**: an implementation that correctly computes
   verdicts but zips them against postings in the wrong order (e.g., after
   a sort or a filter step reorders one list but not the other). Test:
   construct two postings with clearly different expected verdicts: verify
   verdict[0] corresponds to posting[0]'s id, not posting[1]'s.
2. **Justification that cites nothing**: an implementation that returns
   the correct verdict but a generic justification string ("seems like a
   good fit") that names no actual résumé or posting field. Test: assert
   the justification string contains at least one literal skill or field
   value from either the résumé or the posting JSON — not just prose.

## What a failure looks like

*(dated before any code was run)*

**2026-10-30**: a failure is any run where the agent marks a posting
"relevant" whose title or description explicitly states the role requires
on-site presence or excludes remote candidates — because a skill-keyword
match alone can't see that, and someone relying on this agent would waste
time applying somewhere they can't actually work.

## Toolchain

- Language: Python 3.x
- HTTP: `httpx` or `requests` (standard library `urllib` acceptable)
- Tests: `unittest` or `pytest`
- No external services beyond `boards-api.greenhouse.io` and the Claude
  API for the judgment step.
- Judgment model *(added 2026-10-30, after the contract above, before
  any judgment call was made)*: pinned to exactly `claude-opus-5-5` for
  the whole assignment, with no refusal fallback to another model. A
  response served by any other model is rejected as invalid. Chapter 1
  measures one model's repeatability, so the model must not vary.
