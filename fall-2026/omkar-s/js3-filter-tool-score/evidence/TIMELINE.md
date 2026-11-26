# TIMELINE (order of work, UTC; times from the shell clock)

| When | Event | Proof |
|---|---|---|
| 2026-11-17T06:15:27Z | FILTER.md v1.0 written and frozen; js3 folder held FILTER.md and evidence/ only, with no code files | sha256 FILTER-v1.0-frozen.md = 2f86436ec8b9d651… (re-frozen at 06:15:35Z after correcting the written time in the header; no rule changed); file list: ./FILTER.md ./evidence/FILTER-v1.0-frozen.md ./evidence/TIMELINE.md ./persona/aarav-patel.example.json  |
| 2026-11-17T06:16:31Z | first code (`js3/collect.py`, vendored `js3/js2/`), first live collection: 8 sources, 8 requests, 1,142 postings; `greenhouse:webflow` empty | `data/runs/2026-11-17T06-16-31Z/sources.json` |
| 2026-11-17T06:16:44Z | `filter/filter-v1.0.json` written (machine copy of the frozen v1.0) | file mtime |
| 2026-11-17T06:20:45Z | `filter/filter-v1.1.json` (G1 USA suffix) after measuring v1.0 on the corpus | file mtime; FILTER.md change log |
| 2026-11-17T06:21:14Z | `filter/filter-v1.2.json` (T2 non-software phrases) after reading every T2 title | file mtime; FILTER.md change log |
| 2026-11-17T06:23:44Z | audit sample drawn with filter v1.2 (seed 7375003, 49 blind cards) | `audit/sample-key.json` meta |
| 2026-11-17T06:24:05–06:24:46Z | Claude second rater: 49 fresh `claude -p` calls (claude-sonnet-5-5), 49 valid | `audit/claude-second-rater.jsonl` (asked_utc per row) |
| 2026-11-17T~06:24Z | bug fix: sub-heading skills searched (1 claim flip) | FILTER.md change log |
| 2026-11-17T06:25:14Z | filter v1.3 (plural headings) and v1.4 (tech-stack headings end a section) after reading the generated shortlist; `filter/CURRENT` = v1.4 | FILTER.md change log; `shortlist/` |
| 2026-11-17T06:32Z | bug fix found by a test written before it: inline bold is not a heading (0 real labels flipped) | FILTER.md change log |
| 2026-11-17T06:33:35Z | experiment batch 1 locked (sha256 of prompt P1, 3 filter files, held-out labels, persona, scorer/textutil/mcp_server code) | `experiments/lock.json` |
| 2026-11-17T06:33–06:35Z | batch 1 ran: 100 `claude -p` calls (C0, C0b, E3, E4, E5 × 20), 0 invalid, $2.57 | `experiments/runs/*.jsonl` (asked_utc per row) |
| 2026-11-17T06:36:07Z | filter v1.5 (`N+ years` alone) after the Claude second rater's 2 disagreements on kept cards | FILTER.md change log |
| 2026-11-17T06:37:11Z | filter v1.6 (sub-requirements ignored); `filter/CURRENT` = v1.6 | FILTER.md change log |
