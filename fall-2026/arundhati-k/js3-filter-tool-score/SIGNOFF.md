# Sign-off: Job-Search Agent 3

Everything in [brackets] is for me (Arundhati) to write in my own words. The test names and pointers are facts from
the repository.

```text
Sign-off — Job-Search Agent 3
Checked:  [which properties, by which tests. Available tests:
           tests/test_filter.py      WrongVersions (W1 W2 W3), RoleWords, TopicWords, LevelAndUS, Threshold
           tests/test_filter_options.py  Options (us_required, max_years, topic_in_required_only)
           tests/test_evidence.py    SkillClaims, Abstention, LevelAndLocation, CurlyApostrophe, SpelledYears, StrictestYearsWins
           tests/test_mcp_server.py  Handshake, ToolList, ToolCall, Wire
           plus my own hand checks: 54 audit verdicts, 20 held-out labels]
How:      [by hand / by a test I wrote before reading Claude's code / by recomputation / with Claude's help.
           Fact: Claude wrote every test, from my FILTER.md, before writing the code.]
Not checked: [at least three real items, specific to this agent]
Not claiming: [what this agent does not show]
Signed or withheld: ____________ (name, date)
```

## Driver's seat

| task | Claude should | I should | why the judgment stays mine | pointer |
|---|---|---|---|---|
| filter rules | format them, find gaps, test them | decide which words and rules count, and why | [ ] | `a725b4a4`, FILTER.md Appendix A |
| reject audit | draw the sample blind, count, compute intervals | judge each posting | [ ] | `9ee00800`, audit/my-verdicts-2026-11-25.txt |
| rule changes A–D | measure each one | accept or reject each one | [ ] | `8a6b77e4`, FILTER.md Revisions |
| held-out labels | draw the set, hide verdicts | label each posting | [ ] | labels/my-heldout-labels-2026-11-25.txt |
| claim labels | auto-label, show the quote | confirm or override the "read" labels | [ ] | SHORTLIST.md |
| tool trust | run probes, record transcripts | decide whether to trust each server | [ ] | TOOL-EVALUATIONS.md |
| is a posting worth my time | rank and quote evidence | decide, and apply | [ ] | SCORE-CHANGES.md (#14, #4 vs my rules) |
