# Candidate rules for v1.1, measured on the 50 audit labels (held-out not read)

v1.0 agrees with my labels on 33/50 = 66% (95% CI 51%–79%).

## C1 cut title-level disqualifiers
- change: Cut Staff, Principal, Director, Manager, Head of from F2 (keep Intern, PhD, Contract, Temporary).
- why: My 2026-11-25 definition: title level doesn't count against a posting.
- audit agreement: 33 → **33** of 50 (+0)
- audit flips: 0 (0 toward my label)
- whole corpus: 7 of 714 postings change verdict; kept would be 32 (v1.0: 25)

## C2 punctuation inside phrases
- change: Let any punctuation sit between a phrase's words ('data-quality', 'Data & Integration').
- why: The gap found by the second-method recompute on 2026-11-24.
- audit agreement: 33 → **34** of 50 (+1)
- audit flips: 1 (1 toward my label)
- whole corpus: 1 of 714 postings change verdict; kept would be 26 (v1.0: 25)
  - toward my label: Technical Operations & Insights Analyst (reject → keep; my label relevant)

## C3 streaming means data streaming
- change: T5 counts only data-streaming phrases (streaming data, data streaming, streaming pipeline, streaming pipelines, ...), not bare 'streaming'.
- why: False friend: 9 of 10 Spotify 'streaming' matches are music/audio streaming.
- audit agreement: 33 → **33** of 50 (+0)
- audit flips: 0 (0 toward my label)
- whole corpus: 0 of 714 postings change verdict; kept would be 25 (v1.0: 25)

## C4 orchestration means workflow orchestration
- change: T4 counts only orchestration tool, orchestration tools, workflow orchestration, data orchestration, pipeline orchestration, ..., not bare 'orchestration'.
- why: False friend: 'program orchestration', 'resource orchestration', 'compute orchestration'.
- audit agreement: 33 → **33** of 50 (+0)
- audit flips: 0 (0 toward my label)
- whole corpus: 0 of 714 postings change verdict; kept would be 25 (v1.0: 25)

