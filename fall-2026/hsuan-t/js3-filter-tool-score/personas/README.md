# personas/

Why this folder exists: the agent needs a résumé and job preferences to judge postings, but the
brief forbids a real résumé on GitHub or on screen (CONTRACT: Refuses). So every input person here
is **fictional** (`@example.com` email, 555 phone), and the code refuses a résumé whose email is not
`@example.com`.

| File | What it is |
|---|---|
| `aarav-patel.resume.json` | What Aarav has done. JSON Resume format (https://jsonresume.org/schema/), hand-converted from the Reallocation Engine example persona `search/examples/aarav-patel/resume.example.json`. |
| `aarav-patel.profile.json` | What Aarav wants (target roles, excluded title words, locations, years, visa, salary). Same values as the demo profile in CONTRACT.md → Examples. `skill_aliases` is where a user adds their own skill spellings. |
