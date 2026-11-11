SEEDED RUN, not a live change. On 2026-10-30 the live board had 0 new postings, so 3 IDs were removed from a copy of the state to show that new postings are detected and judged by both judges. The real state and runs are untouched.

The first seeded run (`seeded/state/`, `seeded/runs/`) used `prompts/baseline.md`, the agent's default at the time, so its Claude replies have no `failed_check`. `seeded/rev1/` repeats it with the same seed (20261030) and the same 3 IDs using the frozen `prompts/revision-1.md` and its schema, after the default was switched to revision-1.
