# Prompt versions

Each file is sent to Claude exactly as written (with the two field blocks filled in), so notes live here, not in the prompts.

| Version | Change from the previous version | Why |
|---|---|---|
| `judge-v1.md` | baseline prompt contract | |
| `judge-v2.md` | **one change:** the "Question" paragraph now asks Claude to judge the role itself (the work the title implies, and whether Priya's skills and level fit it) and says a `search.target_titles` keyword match alone is not enough. Fields sent, output format and validator are unchanged | In a development check on 2026-10-28, v1's reply re-applied the rule, quoting `search.target_titles` back, so the judgment was not independent of the record. Idea from Claude; chosen by me |
