# Shot list — Ground Truth SQL final project film v4

## Executive summary

v4 (2026-11-22) re-cuts the v3 pitch film into the four parts the final brief requires: executive
summary, introduction, methods, evaluation. The first beat of each part opens on a "Part N of 4"
card with the part's name. All scenes are native Manim vector code (`scenes.py`); the only raster
image is the cropped screenshot of Riya's own Vanna run (B07). Captions are burned in after the master.

| Beat | Part | What moves (the claim) | Real data? |
|---|---|---|---|
| B01 | 1-executive-summary | Title card: the project name writes on, Riya Kapadnis and the course fade in under it, then the one-line problem appears with a terracotta underline. | illustration / plan |
| B02 | 1-executive-summary | A 'Part 1 · Executive summary' card, then a chat box: the question types in; an SQL panel types itself out; a 'ran · 0 errors' pill ticks; the result table shows USA 4,667.06; a terracotta cross lands and 523.06 drops in. | real (example query drafted with Claude, checked by me, labelled) |
| B03 | 1-executive-summary | Three reasons build left to right: a person who only sees the answer (SQL greyed out behind it); the AI at a database with question marks over its tables; a confident number landing on a meeting screen. | illustration / plan |
| B04 | 1-executive-summary | Your data (a server) and your questions feed a 'Ground Truth SQL' box; a report card fills: two rows crossed with their reason underneath, one row ticked. | illustration / plan |
| B05 | 1-executive-summary | The report card sits in the middle; five places light up around it one by one (store, finance, hospital, marketing, AI assistant); then three people step in, each with a two-word takeaway. | illustration / plan |
| B06 | 2-introduction | A 'Part 2 · Introduction' card; BIRD's shelf of its own databases; three counts tick in (12,751 questions, 95 databases, checked by results); two bars grow (people 93%, best AI shorter); a 'your data' pill outside the shelf gets a cross. | real (bird-bench.github.io, read 2026-11-22) |
| B07 | 2-introduction | Riya's real Vanna 2.0.2 run (screenshot, evidence/vanna_check.py, 2026-10-21) on the left; on the right 'works on your data' ticks and 'checks words, not numbers' gets a cross; a 'USA 4,667 · passed' pill lands. | real (Riya's own Vanna 2.0.2 run, screenshot) |
| B08 | 2-introduction | A small grid fills row by row: columns 'checks the numbers' and 'on your data'; BIRD gets a tick and a cross, Vanna a cross and a tick, Ground Truth SQL two ticks and a terracotta outline. | illustration / plan |
| B09 | 3-methods | A 'Part 3 · Methods' card; the Chinook database (server) with its label; three counts tick in (11 tables, 59 customers, 412 orders); a timeline 2009 to 2013 draws under them. | real (read-only Chinook counts) |
| B10 | 3-methods | A stack of question cards ('about 50'); one card opens: question, checked SQL, answer 523.06; a second path (plain Python from the raw tables) arrives at the same 523.06; an '=' and a tick: 'today 8 of 8 agree'. | real (Q03 gold; cross_check.py 8/8) |
| B11 | 3-methods | Two input cards (table layout, the question) feed Claude's workstation; three run chips appear; an arrow to the database with a 'read-only · 1 query' pill; 'the data never changes' lands below. | illustration / plan |
| B12 | 3-methods | Two different SQL panels side by side; both run into the same result 523.06; an '=' appears and a line reads 'compare results, not wording'. | real |
| B13 | 3-methods | Four cause cards flip in one by one, each with the wrong number (crossed) and the right one: revenue 4,667 vs 523, long songs 3,503 vs 1,069, rock buyers 835 vs 59, busiest rep (empty) vs Jane Peacock, 21. | real (run_slice.py variants) |
| B14 | 3-methods | Two columns fill: 'what I have' (laptop, Python, free database, Claude via my Claude Code plan) with ticks, and 'what I don't need' (cloud servers, extra token credits) with crosses. | illustration / plan |
| B15 | 3-methods | Two columns fill: 'the finished project will have' (1 sample database · Chinook, ~50 test questions, Claude as the AI being tested) and 'it will not' (be a chat app, change any data · read-only). | illustration / plan |
| B16 | 4-evaluation | A 'Part 4 · Evaluation' card; the question as a heading; nine labeled test queries (3 correct rewrites, 6 with a mistake); two bars grow: compare wording 6 of 9, compare results 9 of 9. | real |
| B17 | 4-evaluation | A terminal window types the real score_claude_runs.py result (three blind Claude runs, 2026-10-21), shortened; the 22 / 24 line is underlined; the two Q02 fails light up; a card shows France 5 and Brazil 5: a tie. | real (2026-10-21 Claude runs, shortened) |
| B18 | 4-evaluation | A timeline 2009-2013; a '2023' marker slides past the end; two empty result boxes show '=' ; a terracotta cross lands on the '='; a new rule card stamps on: 'empty right answer -> rejected'. | real |
| B19 | 4-evaluation | 'It worked if' fills with three ticked lines; 'it didn't work if' adds one crossed line; a bar shows today's 22 of 24 nearly full, and a note 'next: 50 harder questions'. | illustration / plan |
| B20 | 4-evaluation | Four recap rows build (problem / solution / today / next), each with its own heading; then they clear and the closing two lines write on alone. | illustration / plan |
