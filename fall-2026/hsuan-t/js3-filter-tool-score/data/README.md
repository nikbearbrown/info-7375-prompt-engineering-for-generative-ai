# data/

Why this folder exists: two rule checks need word lists that should not depend on each user typing
them. These ship with the tool so a TA can still recompute every verdict by hand (CONTRACT: In).
JS2 adds the list of boards a run watches.

| File | Used by | Why built-in |
|---|---|---|
| `skill_aliases.json` | check 3 (skills) | Same skill, different spellings (JD "postgres", résumé "PostgreSQL"). Kept small and free of common English words (no `go`, `node`). Users add their own under `skill_aliases` in their profile, without editing this file. |
| `no_sponsorship_phrases.json` | check 5 (visa) | Phrases that say a job will NOT sponsor a visa. Matched as **whole phrases** (words together, in order), not order-free word matching (CONTRACT Wrong version 6). |
| `boards.json` | the watch / loop (JS2) | Which boards a run watches: our `name` (used for state and raw file names), the applicant-tracking system (`ats`: `greenhouse` or `ashby`) and the board's `slug` on it. `striqe` is misspelled on purpose (GATE): it must fail with a 404. Adding a board is one line here, no code change. |
