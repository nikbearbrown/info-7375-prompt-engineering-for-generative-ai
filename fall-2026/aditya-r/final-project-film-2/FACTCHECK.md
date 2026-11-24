# FACTCHECK — DayThread Final Project Film (2026-11-23)

DayThread is still a **plan**. The only thing that has run is the minimal two-day replay of
2026-10-25 (`final-project-film/replay/RESULTS.md`). No delegation contract, fine-tuned checker,
loop, memory, review page, tests or evaluation exists. Beats that draw the planned system carry
"Constructed — proposed workflow". Every frame carries "Synthesized voice reading Aditya's script".

| # | Beat | Claim | Verdict | Source | Fix |
|---|---|---|---|---|---|
| 1 | BIDEA | Aditya Raj; DayThread is Aditya's final project; the voice is synthesized | PASS | Kokoro `am_onyx`; disclosed aloud and on screen | — |
| 2 | B01 | DayThread *will* remember across days and show the client's exact words to a coordinator, who decides | EXEMPT (plan) | PROJECT-BRIEF.md §1, §5 | Future tense; [C] caption |
| 3 | B02 | "a coordinator shouldn't have to reread every conversation" | EXEMPT (motivation) | PROJECT-BRIEF.md §2 (intended benefit, not measured) | Stated as a reason, not a result |
| 4 | B02 | "In my October test, Claude's summaries all kept the fall, but nine of ten changed what the client meant" | PASS | replay/RESULTS.md: P1 0/5 omitted (constrained), P2 5/5 kept (normal) = 10/10 kept; R3 problem in 9 of 10 summaries (Aditya's review) | Caption "Replay run 2026-10-25 · synthetic data · fictional client"; on screen "kept the fall: 10 of 10", "meaning changed: 9 of 10" |
| 5 | B03 | "That small test is the only part that has run. Everything else in this film is a plan." | PASS | No DayThread code exists beyond replay/ (checked 2026-11-23: no final-project/ folder in the course repo) | — |
| 6 | B04 | Lifeline "says it doesn't detect every fall" | PASS | S1 verbatim: "Fall detection technology does not detect 100% of all falls." Read by Aditya 2026-10-14 | Caption "From each company's own documentation, read 2026-10-14" |
| 7 | B04 | DailyCall "makes daily AI phone calls with summaries for families" | PASS | S2: "DailyCall uses AI-generated phone calls for daily check-ins."; "Helpful summaries after calls" | Attributed to their documentation |
| 8 | B04 | DailyCall "says it can't guarantee every safety concern is detected or interpreted correctly" | PASS | S4 verbatim: "DailyCall cannot guarantee that every safety concern will be detected, interpreted correctly, or delivered to the right person in time." | Shortened, meaning kept |
| 9 | B05 | "I'm not claiming they lack anything"; DayThread's focus is narrower | PASS (scoped) | SOURCES.md analysis accepted by Aditya 2026-10-14 | No comparative claim |
| 10 | B06 | Delegation contract; Aditya will write the contract and tests before Claude writes code | EXEMPT (plan) | Course chapter 10, "Evidence belongs on the edges"; final-project spec, "the gate" device | Future tense; [C] |
| 11 | B07 | Append-only transcript; quoted claims; approval bound to evidence + action | EXEMPT (plan) | PROJECT-BRIEF.md §5 permissions; proposed contract | [C] |
| 12 | B08 | Loop with turn budget; stop not "the model said done" | EXEMPT (plan) | Final-project spec, "What agentic means here" | [C] |
| 13 | B09 | Base model DistilRoBERTa, from Hugging Face, fine-tuned by Aditya | EXEMPT (plan) | `distilbert/distilroberta-base`, licence `apache-2.0` (Hugging Face API, checked 2026-11-23). Not downloaded or trained yet | Future tense; [C] |
| 14 | B09 | "fails differently from the thing it checks" | EXEMPT (design reason) | Course chapter 10: "An edge needs something that fails differently from the thing it certifies." | — |
| 15 | B10 | Synthetic data; Claude writes training sentences; Aditya writes and seals held-out set first | EXEMPT (plan) | Plan agreed 2026-11-23 | Future tense |
| 16 | B11 | Claude Code through existing account, no API credits | PASS (fact about access) | replay/README.md: Claude Code CLI via Aditya's claude.ai login, no API key | — |
| 17 | B11 | Base model is a free download, no new account | PASS | Public model page; Hugging Face API returned it without authentication (2026-11-23) | — |
| 18 | B11 | Training will run on Aditya's laptop; Python, PyTorch, SQLite | EXEMPT (plan) | MacBook Pro, Apple M3 Pro, 18 GB (sysctl, 2026-11-23). PyTorch not installed yet | Future tense |
| 19 | B12 | Order of work; held-out run before December 20 | EXEMPT (plan) | Final-project due date: 20 Dec, 23:59 | — |
| 20 | B13 | Compare with keyword list and untrained model; pass mark written before looking; report a loss | EXEMPT (plan) | Final-project spec, "An evaluation that can say no" | Bars drawn empty with "?" — no results implied |
| 21 | B14 | Five deliberate failure cases | EXEMPT (plan) | Final-project spec: at least five deliberate failure cases | — |
| 22 | B15 | "My test never dropped the fall on its own" | PASS | replay/RESULTS.md: 0/5 constrained, 5/5 normal kept; P3 not tested | — |
| 23 | B15 | Forced omission, caught by the separate check, reviewed by a coordinator | EXEMPT (plan) | Final-project spec, "A controlled failure" | [C] |
| 24 | B16 | Can't show: real clients; changed meaning | PASS (limitation) | replay/RESULTS.md (meaning drift); synthetic-only data boundary | — |
| 25 | BOUT | DayThread, Aditya Raj, github.com/aditya-raj-sde | PASS | Aditya's confirmation, 2026-10-14 | Audio reused from the October film (identical line) |
