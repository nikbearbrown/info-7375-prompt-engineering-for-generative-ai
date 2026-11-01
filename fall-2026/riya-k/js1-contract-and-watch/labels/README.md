# Hand labels

Labeled by Riya Kapadnis on 2026-10-31, before any Claude call on these 20 postings
(see the commit order: labels are committed before `experiments/` results exist).

- Selection: `experiments/select_postings.py` (seed 7375) → `selection.json`, `labeling_sheet.md`.
- How I labeled: Claude Code showed me each US posting's title, location, years required, which of Arya's
  skills the posting mentions, and the opening of its requirements, and I chose a label and reason
  from multiple-choice options in the chat. For the 11 non-US postings I gave one blanket instruction
  in the chat ("I want the location in US"), so they are all `not_relevant` for location.
- Labeling rule (CONTRACT.md) plus that location rule: relevant if Arya could apply honestly today, the role
  matches her AI/ML/data target, it is not senior, she has at least 2 of the core skills, and it is in the US.
- Result: 2 relevant (#3 Solutions Engineer NYC, #4 Software Engineer New Grad Distributed Data Systems), 18 not.
