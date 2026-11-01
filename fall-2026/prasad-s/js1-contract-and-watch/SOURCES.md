# SOURCES.md — Job-Search Agent 1

## What I used

- **The JS1 brief** and the course AI policy (Canvas).
- **Greenhouse's public job-board API**, Stripe's board only:
  `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`.
  Public data, no login; saved responses are in evidence/. I had used
  Stripe as a test board in my earlier Mode Build assignment.
- **The persona "Alex Rivera"**: invented, with @example.com and 555-01xx
  details. No real résumé was used anywhere.
- **Python 3.13.17** (python.org installer), standard library only.
- **Claude.ai (Opus 5.5) as the judge under test**: 89 replies collected
  in fresh Incognito chats (run 2, sampling, prompt experiment), plus one
  for the action-surface Way 2 demo. These replies are data, not authorship.
- No Anthropic API key; no classmates' code or folders.

## What I wrote

- CONTRACT.md v0.1 written by me alone,
  and every decision in v0.2–v0.4: board, persona locations, the rule,
  the quirks, the skills minimum, the empty-state and phone rules.
- The four expected-outcome tables (all cases and expected answers),
  written before any code. Claude.ai typed the corrected rule table after
  flagging 4 answers; I checked each correction.
- The labeling protocol, the chat plan, and all 20 hand labels.
- The baseline prompt's rule text and failing-condition instruction.
- The revision choice (C), its reason, and the prediction.
- The conclusions of both reports, the action-surface "what could go
  wrong" row and the autonomy choice, and my FRICTIONAL.md entries.
- The scoring rule: adopted from a template Claude.ai suggested.

## What Claude.ai contributed (this Project chat)

- Reviews of the contract (16 issues, then the must-fix list) and
  suggested wording for the v0.2–v0.4 edits and amendments.
- Step-by-step guidance and every terminal command I ran outside
  Claude Code, including the fact-check scripts, the location check
  and the run 2 recount script.
- Suggested the persona's final locations; I accepted them after
  seeing Stripe's spellings.
- The skeleton of the baseline prompt and its field-names paragraph.
- Found the whole-list rejection pattern and listed options A, B, C;
  drafted revision_decision.md around my choice and prediction.
- Flagged overclaims in my conclusions and supplied corrected wording.
- Drafted the sign-off item list and the driver's-seat rows, and
  corrected attribution in three rows; I chose and confirmed each item.
- Checked FRICTIONAL.md for facts and attribution, and supplied
  corrected wording and the &nbsp; entry.

## What Claude Code contributed

- All code in agent/ and tools/, and the test runners in tests/
  (they load my tables; they do not contain my answers).
- The W1/W2 wrong versions and their checks, including two constructed
  replies in the test file, labeled there as not Claude output.
- The offline replay config, the README draft, and the tables in both
  reports (from my saved evidence files).
- The action-surface Way 3 demo (as the agent).
- Commits from CP4 onward carry its Co-Authored-By line; I approved each
  one before it was made and before each push.

## Other help

- Muse : drafted a v0.2 that named the Vercel
  board and cited checks and files I never made. I rejected it and
  replaced it with my own Stripe checks (see FRICTIONAL.md).

---