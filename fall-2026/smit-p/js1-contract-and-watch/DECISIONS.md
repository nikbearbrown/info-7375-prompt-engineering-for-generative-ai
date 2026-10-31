# Decisions record — who decided what

## Executive summary

This file records, word for word, the decisions Smit P. made in the 2026-10-24 Claude
Code build session. It also records where Claude only offered options or wrote things
up. It is the evidence behind the "driver's seat" table in the README. Every decision
below was made through a multiple-choice prompt in the session (Claude offered options,
Smit picked one or typed an answer). The answers are quoted as given.

| # | Decision | Smit's answer (verbatim) | Where it landed |
|---|---|---|---|
| D1 | Board | "Airbnb (Greenhouse)" | CONTRACT.md (commit `c29d163`) |
| D2 | Persona | "Aarav Patel" | CONTRACT.md, `persona/` |
| D3 | Relevance rule | "Title + 2 skills (Recommended)" | CONTRACT.md "The rule" |
| D4 | Wrong version 1 | "Labels on wrong postings" | CONTRACT.md, `tests/` `WrongVersion1_*` |
| D5 | Wrong version 2 | "Empty justification" (asked again: the first answer named only one wrong version) | CONTRACT.md, `tests/` `WrongVersion2_*` |
| D6 | Failure sentence | "Missed new posting" | CONTRACT.md "What a failure looks like" |
| D7 | Labeling rule v1 | "IC + early-career + US (Recommended)" | `experiments/LABELING-RULE.md` (commit `783402f`) |
| D8 | Development labels | "None of these 3" ×3, "8257909 Not relevant" | `experiments/labels.json` |
| D9 | Held-out labels 4–6 | typed: "Software Engineer or Cloud Engineer or Full Stack Engineer under 3 to 4 yeara" | **Claude inferred** from this that none of 8263303 / 7747259 / 8053132 is relevant, and read it as a narrower rule. Smit confirmed the three labels explicitly in D12 |
| D10 | Rule conflict | "Amend rule, log it (Rec.)" | LABELING-RULE.md amendment v2 (commit `56ca4e8`) |
| D11 | 8274152 | "Relevant" (the first pass returned no answer) | `experiments/labels.json` |
| D12 | 2026-10-28: re-label explicitly the three held-out postings that D9 only implied (8263303, 7747259, 8053132) | "None of these 3" | `experiments/labels.json` `_provenance_correction`; the labels are unchanged |
| D13 | 2026-10-28: don't push yet | "Don't push yet; I'll do the day-2 run and sign-off first." | nothing pushed |
| D14 | 2026-10-28: the live day-2 run | Smit ran `python3 src/watch.py … --label live --claude` personally | `runs/*20261028T153510*` |

## What Claude decided without asking (and should be checked)

- Replacing the first 20-posting draw (19/20 senior titles) with a stratified one, before
  any labeling (`experiments/selection-v1-degenerate.json` is kept).
- The single change in the revision prompt (adding a US-location condition), chosen
  from the development miss.
- Building the "earlier" seeded snapshot by removing the 10 most recently published
  postings.
- Not fixing the output-format bug the experiment found. Fixing it would have been a
  second change.
- Choosing `claude-sonnet-5-5` as the judge model, and the isolation flags for "fresh
  conversation".
