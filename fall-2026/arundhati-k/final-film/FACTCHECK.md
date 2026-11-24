# FACTCHECK — Co-op Sponsor Check (Final Project Film)

Status: checked 2026-11-23 by Claude against the files named below; Arundhati Kandelkar to confirm on review.
Rule: past tense only for what exists and is in evidence; everything else is "will" / "next". Every beat audited, bookends included.
Paths: `FF/` = `fall-2026/arundhati-k/final-film/`; `PF/` = `fall-2026/arundhati-k/final-project-film/`; fork = the-reallocation-engine, branch `final/arundhatik26-and-fix`.

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| 1 | BNAME | "I'm Arundhati Kandelkar, a master's student at Northeastern"; card "MSIS, Northeastern University" | PASS | her own statement (graded pitch film, same line) | — |
| 2 | BBUILD | Building a tool that tells international students whether a company has sponsored someone for a software job | PASS | recipe `coop_sponsor_check.py` exists in the fork (commit `03784b0`) | — |
| 3 | BIDEA | A missing record looks like a no; my tool says I don't know instead | PASS | `test_F1_not_in_dataset_is_unknown_not_zero` passes (FF/evidence/tests-after-fix-2026-11-23.txt) | — |
| 4 | BWHAT | When done: public repo with the tool, 25-company evaluation set, failure log | EXEMPT | plan, spoken as "will be"; tag PLANNED on screen | — |
| 5 | P2 | "Part two. What already exists?" | EXEMPT | section title, no factual claim | — |
| 6 | B05 | Her hub search for Capital One listed Capital One National Association and Capital One Services | PASS | PF/evidence/eval-25-rows-2026-10-25.md row 12: "CAPITAL ONE NATIONAL ASSOCIATION · CAPITAL ONE SERVICES LLC (**my own search**, 20:22)" | tag dated 2026-10-25, "MY SEARCH" |
| 7 | B05 | My dataset has neither | PASS | FF/evidence/eval-after-fix-2026-11-23.json: Capital One → not-in-dataset, 0 candidates (also before the fix) | — |
| 8 | B05 | The hub is searched one employer at a time and has no job-title filter | PASS | PF/evidence/uscis-hub-search-2026-10-12.md: filters are Fiscal Year, Employer Name, NAICS, City, State, Zip | that file's search was run by Claude (10-12); the property of the site is what is claimed |
| 9 | BOS | She searched OpenSanctions (sanctions and risk screening) for Robinhood, Chime and SoFi | PASS | FF/MY-SEARCHES.md, her own text | — |
| 10 | BOS | Chime returned 11 results, mostly unrelated people; Chime Financial not among those she reviewed | PASS | FF/MY-SEARCHES.md: "It returned 11 results, mostly unrelated individuals. It did not show Chime Financial Inc. in the results I reviewed." | first draft said flatly "not Chime Financial"; reworded to her scope |
| 11 | BOS | On screen: 11 result rows, 2 shown as entities, 9 as people | EXEMPT | illustrative split of "mostly people"; she did not record an exact count of people | rows are grey bars, no names |
| 12 | BGL | GLEIF linked Robinhood → ROBINHOOD MARKETS, INC.; SoFi → SOCIAL FINANCE, LLC, previously SOCIAL FINANCE, INC. | PASS | FF/MY-SEARCHES.md, her own text | — |
| 13 | BCARE | Neither tool is built to find H-1B sponsoring employers; finding them takes time when brand ≠ legal name; my tool lets you verify | PASS | FF/MY-SEARCHES.md answers 1–2 (her words, condensed for narration) | — |
| 14 | BCARE | On screen: "Chime" → CHIME FINANCIAL INC, CHIME INC | PASS | FF/evidence/eval-after-fix-2026-11-23.json, Chime candidates | — |
| 15 | P3 | "Part three. How I'm building it." | EXEMPT | section title | — |
| 16 | B00 | Pushed a recipe to my fork on October third; tag "commit 03784b0" | PASS | `git log -1 03784b0` → Sat Oct 3 2026 (verified for the pitch film) | — |
| 17 | B01 | It checks three things: software-title record, co-op before graduation, posting live | PASS | gates G2–G4 in the recipe; PF/evidence/recipe-rerun-2026-10-10.txt | — |
| 18 | B02 | Missing company is not zero; it says unknown and tells you to ask a person | PASS | `test_F1_…`; next_action "NETWORK: … ask an alum or recruiter directly" | — |
| 19 | B03 | Data comes from a public dataset built from SEC funded-startup list; big banks not in it | PASS | fork `data/80-days-to-stay/README.md`; eval: 10/10 big banks not-in-dataset (rows 7–16) | — |
| 20 | BFIX | Today brand names fixed: first word "Chime" lists Chime Financial and Chime Inc; alias list points SoFi to Social Finance; a person picks | PASS | fork `coop_sponsor_check.py` (`resolve_company`, `load_aliases`), `inputs/brand-aliases.json`; tests `test_chime_lists_…`, `test_sofi_with_alias_…` | code written by Claude Code on her instruction (SOURCES.md); alias entry is her input |
| 21 | BFIX | Twenty-six tests pass | PASS | FF/evidence/tests-after-fix-2026-11-23.txt: "Ran 26 tests … OK"; before the fix 9 failed (tests-before-fix) | — |
| 22 | B06 | Next: hub as second source; then a written failure analysis and a README with a one-command demo | EXEMPT | plan; tag PLANNED | — |
| 23 | BRES | Needs laptop, Python, GitHub, public data incl. USCIS data; may use Claude Code; lookup is plain Python, no AI model at run time | PASS | FF/MY-SEARCHES.md answer 3 (her words); `coop_sponsor_check.py` imports only the standard library + a Node scorer, no model call | — |
| 24 | B09 | Will not give immigration advice or predict visas; reports history | PASS | scope in the brief; labels exist (`test_every_scorer_term_is_labeled`) | — |
| 25 | P4 | "Part four. How will I know it worked?" | EXEMPT | section title | — |
| 26 | B07 | 25 companies; every company looked up in the hub was there; in October the tool found a record for 2; it never guessed no | PASS | PF/evidence/eval-25-rows-2026-10-25.md | — |
| 27 | B07A | "Goldman Sachs and Co LLC" → "Goldman Sachs and"; fixed with a test that failed before and passes after | PASS | fork commit `379252f`; PF/BUILD-LOG.md | — |
| 28 | BAFTER | Robinhood, Chime, SoFi were missed (Chime: wrong tiny row) | PASS | PF/evidence/eval-25-rows-2026-10-25.md rows 19, 20, 25 | — |
| 29 | BAFTER | She predicted the first-word rule would catch two and SoFi would need the alias, before the fix | PASS | FF/PREDICTIONS.md, written 2026-11-23 15:32 EST; fix code written after (tests-before-fix at 15:33 still fail) | — |
| 30 | BAFTER | Now none of the three missed; 6 of 25 go to a person; no wrong automatic answers; table 3→0, 1→0, 0→6 | PASS | FF/evidence/eval-after-fix-2026-11-23.md totals | "none missed" = listed as a candidate, not auto-answered (said in BFIX) |
| 31 | BBAR | Pass / fail bar after the hub is added | PASS | FF/MY-SEARCHES.md answer 4 (her criteria, condensed: "results consistent and testable" and "cannot show which source" left out of the spoken list for length) | full list in MY-SEARCHES.md |
| 32 | BOUT | Title and her name; no instructor handle | PASS | ClaudeTitleOutro `handle` = her name (local toolkit edit, PF/BUILD-PROMPT.md §1) | — |
