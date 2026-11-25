# FRICTIONAL - JS2

> The entries are my (Vrajesh's) own words, dictated in chat to Claude Code and placed here verbatim. [Brackets] are Claude's notes, not my words. The traceability table at the end was compiled by Claude from the files and runs.

## 2026-10-31

**Picking the boards and the budget.**
"It felt frustrating, but it showed me that my board list and budget did not match. I had to reconsider the limits instead of pretending every board could run."
[Facts: I picked 9 boards and a 6-board / 8-request budget. Claude pointed out they don't fit together, and I raised the budget to 12 / 15 / 180.]

**When my chosen defect didn't reproduce.**
"I was surprised when the years bug did not reproduce, but the evidence was clear. I stopped pursuing it and switched to a defect I could reproduce."
[Facts: I picked the years-regex false positive from my JS1 "Not checked" list. Claude found 0 of 72 on real data, and I switched to the Greenhouse location bug.]

## 2026-11-01

**What surprised me in the runs.**
"I was surprised that 190 new postings produced zero relevant Greenhouse jobs before the fix. I was also surprised that a run could say "finished" while still producing incorrect results."
[Facts: run2-live had 190 new postings and 0 relevant on Greenhouse, including a Databricks New Grad 2027 job rejected for "country None"; the finished-wrong demo reported "finished" with Palantir at 0.]

## 2026-11-10

**What I saw when I ran the review commands myself.**
"I saw that there are 7 new opening in commure and 91 new opening on GreenHouse stripr"
[All 4 review tests and all 57 tests passed for me; output saved verbatim in `review/6-my-run-2026-11-10.txt`.]

**The review decision: what I accepted, modified or rejected from Claude, and why.**
"Fix for Toronto: Add a conditional check that looks at the context of the abbreviation. If CA is preceded by a known Canadian city  (or if the input format allows for country codes), map it to Canada instead of the US state of California.Fix for Bare Cities: Implement a fallback dictionary or a named-entity recognition (NER) lookup for the world's top major cities.  If an input matches "Chicago", without a state or country attached, the system should automatically resolve it to its primary global location. "Keep It to United States Only""
[So: revise, not accept. Claude wrote the revision tests first (2 failed), then a US-only city list and the Canadian `, CA` check, not NER. 61 tests pass; 119 postings re-classified; this week's relevant set did not change. See REVIEW-PACKET.md step 6b.]

**What is unresolved.**
"Lowercase abbreviations like "sf, nyc," region codes such as USCA and AMER, and ambiguous locations like "Remote" are still unresolved. but that's not the major case So no major thing is unresolved"
[Claude's note, not mine: the README sign-off "Not checked" list also names a real timeout/5xx never happening in a live run, and the independent check verifying counts only, not new ids.]

## Traceability (compiled by Claude)

| What | Where |
|---|---|
| GATE.md written before code | commit `6a2e07e` (GATE.md only), before any `earlybird/` file existed |
| Deliberate failure | `config/boards.json` `stripe-typo`; `reports/run2-live-trace.jsonl` steps 37-39; `data/raw/2026-11-01/greenhouse_stripe-typo.error.txt` |
| Finished-but-wrong, caught independently | `experiments/finished_wrong.py`; `reports/demo-finished-wrong-console.txt`, `-check.json` |
| Budget exhausted | `reports/demo-budget-exhausted.md` |
| First defect did not reproduce | REVIEW-PACKET.md header (288 postings, 0 of 72) |
| R3 defect reproduced, test first, patch | `reports/run2-live.md`; `review/2-test-before-patch.txt`; `review/3-patch.diff`; `review/4-before-after.txt`; `review/5-location-audit.txt` |
| Mutation check of the tests | README "Permission policy" (3 mutants, each failed its 2 tests) |
| Console `·` printed as `�` on Windows | fixed to ASCII `|` in `earlybird/__main__.py` on 11-01 |
