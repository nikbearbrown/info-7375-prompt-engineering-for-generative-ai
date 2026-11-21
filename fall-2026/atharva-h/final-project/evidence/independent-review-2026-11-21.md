# Independent review — 2026-11-21

- **Reviewer:** a separate Claude Code subagent (general-purpose, model inherited: `claude-opus-5-5`). It didn't build the project, and was told to be skeptical, not to modify files, and to try to break the policy, the gate, the key independence, the freeze ordering, and the comparators.
- **Scope given:** the project folder at commit `53fbca0`. It reported that commits up to `99a6b8c` landed during its review, none touching code, tests or keys.
- **Tool use:** 47 tool calls (reported by the harness). It deleted two `__pycache__` folders its own probes had created. `git status` was clean afterwards.
- **Below:** the report, word for word. Triage (genuine or false positive) and what was done about each finding are in [../audit-note.md](../audit-note.md).

---

Independent review of SponsorSQL (fall-2026/atharva-h/final-project). No project files were edited by me. One side effect: my `python3 -I` probes wrote bytecode into `sponsorsql/__pycache__` and `tests/__pycache__` (-I ignores PYTHONDONTWRITEBYTECODE); neither existed before my runs (birth times match), so I deleted both — `git status` for the folder is clean. All scratch work is under /private/tmp/claude-501/-Users-atharvahambir-Desktop-INFO-7375/b909e288-ce44-402e-b95c-a1088eb8a267/scratchpad/.

**Confirmed first (so findings are against a baseline):** 28 tests pass; replaying all three evaluations on the real DB reproduces 4/10, 9/10, 5/5 with identical `actual` values to the saved results (tuple-vs-list serialization aside); FREEZE.md hashes match the files today; commit `dfbbb73` (13:17:40, held-out frozen) precedes `b65b725` (13:23:08, first model replies); the local ledger shows exactly one held-out run; recorded prompts are byte-identical to what `prompt.build` produces; `responses == json.dumps(raw)` for all three rounds. Note the repo kept moving during review (3 commits after `53fbca0`, up to `99a6b8c`); none touched code, tests, or keys.

## Findings

1. **Contract v2 was used for scoring without the owner review the project itself requires.**
   (a) `gates.md:25` (Gate 2 applies "Before a new contract version is used for scoring"); `PROMPT-CONTRACT-v1.md:32` ("The project owner reviews any change to the prompt or key before re-scoring").
   (b) `PROMPT-CONTRACT-v2.md:3` still reads "Status: awaiting owner review", yet v2 was used for dev round 2 (`710368e`) and the one-shot held-out run (`53fbca0`); SIGNOFF.md is unsigned. The held-out set is now spent on a contract nobody approved — if the owner rejects/changes v2, there is no clean held-out set left. "Final contract" was Claude's label, not the owner's decision.
   (c) **High.**

2. **"0 unsafe SQL executed" is unfalsifiable as reported.**
   (a) `evaluate.py:94-102` (`_recheck`) and the `executed_sql_failing_policy` field cited in evidence.md/README as a ship-bar result.
   (b) `_recheck` re-runs `check_text` on SQL that could only have executed after passing `check_text` (`policy.execute`, `policy.py:132-134`) — it can never be nonzero. And with 0 policy denials in every round, the policy was never exercised by model output at all, only by scripted fixtures F1–F3. The ship-bar item "zero unsafe SQL" therefore has no discriminating evidence behind it; it is true by construction.
   (c) **Medium.**

3. **Statement time budget can be overrun; the question budget is not enforced.**
   (a) `CONTRACT.md:35` ("10 s (SQLite progress handler interrupts)"), `CONTRACT.md:37` (60 s/question), `policy.py:138`, `agent.py:60-62`.
   (b) The progress handler fires only between VM opcodes, so a single long function call — the Python UDFs `title_has`/`norm`, or `replace`/`printf` on huge strings — is not interruptible. Through `policy.execute` with budget 10.0: `SELECT title_has(s,'z0')+...+title_has(s,'z14') FROM (SELECT replace(printf('%.*c', 20000000,'x'),'x','a-') AS s)` → `RAN in 14.19s (budget 10.0s)`; passes `check_text` and the authorizer, scales linearly with the number of calls. `printf`/`replace` also let one statement allocate hundreds of MB (`length(printf('%.*c',300000000,'x'))` ran). The 60 s question budget is only checked at the start of each attempt; with up to 3 statements/attempt × 2 attempts plus `ClaudeCLIAdapter` timeout=180 (`adapters.py:59`), one question can run for several minutes.
   (c) **Medium.**

4. **The text check can be blinded; "three independent layers" against writes is really two.**
   (a) `_without_literals` (`policy.py:66-68`) only understands single-quoted strings; `action-surface-map.md:12` claims "three independent layers".
   (b) A `'` inside a double-quoted identifier makes the regex swallow the rest of the statement as a "literal". `check_text` returned allowed=True for: `SELECT COUNT(*) AS "x'" FROM lca -- '` (ran), `SELECT COUNT(*) AS "x'", 'y' FROM lca /* hidden ' */` (ran), and `SELECT COUNT(*) AS "x'" FROM lca; SELECT 2 -- '` — the last was stopped only by Python's `ProgrammingError: You can only execute one statement at a time`, which is not a documented layer, and the agent treats it as an ordinary SQL error and retries rather than as a policy denial. So CONTRACT test 2/F2's claim "second statement denied by the text check" is bypassable. Separately, the read-only connection alone does **not** block `ATTACH`: without the authorizer, `ATTACH DATABASE ':memory:' AS m` succeeded on a `mode=ro`+`query_only` connection (tested on a scratch fixture). ATTACH-as-statement is still stopped by the first-word check. Double-quote handling also causes false denials: `... OR "update" IS NULL` is denied as UPDATE, and SQLite here accepts `JOB_TITLE = "Data Analyst"` as a string literal (returned 1444). No authorizer bypass found (`json_each`, `pragma_database_list`, `dbstat`, `sqlite_temp_master`, `temp.lca`, `sqlite_version()`, `hex()`, `randomblob()`, recursive CTE, `metadata`, `sqlite_master` all denied or failed).
   (c) **Low** (no write or foreign-table read achieved), but the documented defense-in-depth is overstated.

5. **The model can spoof system lines in the human-gate view.**
   (a) `gate.py:47-50` inserts `proposal.interpretation` and `limits` verbatim (newlines included) into the markdown view.
   (b) On the fixture DB, a scripted reply with interpretation `"...\n\n**Check:** answer 999 matches 999 matching rows (independent answer key agrees)"`, sql `SELECT 999`, answer_type `table` produced a view containing that fake **Check:** line in the same format as a system check, while the real check was `''`. The person at the gate cannot tell model-authored text from system-authored text — this undercuts the gate's core purpose.
   (c) **Medium.**

6. **The gate binds to a rendered, truncated view, not to the answer; file-mode approvals carry little authority.**
   (a) `gate.py:27-29` (`_cell`), `gate.py:39-40` (answer_limit 25, evidence_limit 20), `gate.py:75-85`.
   (b) Verified: two answers differing only by `A|B` vs `A/B` produce the same view hash (True); two answers differing only in row 26+ produce the same view hash (True). The exported report contains only the first 25 answer rows (for D6, 25 of 1,114 employers). A file-mode approval is any JSON file anyone can write, with free-text approver, not tied to a run_id or nonce, so it replays onto any later identical view; and in file mode `decide()` never displays the view at all — "the exact view the person saw" is really "a hash someone pasted". With the live adapter, a second run will almost never reproduce the view, so file mode effectively only works for recorded replies.
   (c) **Low–medium.**

7. **Crash paths break "every run writes a state file".**
   (a) `CONTRACT.md:51` (test 9), `gate.py:79`, `adapters.py:69-74`.
   (b) A decision file containing `[]` crashes the run: `CRASH: AttributeError 'list' object has no attribute 'get' | state files written: none`. `ClaudeCLIAdapter('/nonexistent/claude')` raises `FileNotFoundError` with no state saved (only `TimeoutExpired` is caught). A missing database or contract file also raises before `state.save`.
   (c) **Low.**

8. **Comparators accept wrong answers (latent; did not inflate the recorded passes).**
   (a) `evaluate.py:17-18, 51, 59-61, 64, 66-70, 76, 79, 85`.
   (b) Each of these returned passed=True against the real keys: q2 with rows `[[40],[999]]`; q2 with `[[40.9]]` (`int(float())` truncates); h1 as a multi-row GROUP BY whose first row is 564; h3 with extra columns/rows; q5 with an extra NULL group of 5000 hidden by a later `''` row (dict overwrite, not sum); q7 with untrimmed split groups that get summed back together (so q6/q7 silently repair the exact grouping error that q8 penalises); q4 with an extra state whose median is NULL (ignored) or a duplicate `'MA '` row (overwritten); q9 with daily rows whose last day per month equals the monthly total. I checked the recorded runs: every passing count answer was 1 row × 1 column and no passing answer had duplicate labels after trimming, so the reported scores are not inflated by this. Only 3 of 15 comparators have unit tests (q2, q5, q1; `tests/test_agent.py:157-169`).
   (c) **Medium** (latent validity risk).

9. **Answer keys are independent of model SQL, but share definitions and code with the system.**
   (a) `build_answer_key.py:19-24` and `build_heldout_key.py:20-25` are character-for-character copies of `udf.normalized`/`title_has` (`udf.py:11-21`); PROMPT-CONTRACT-v2 instructs the model to call that same function and copies the key's definitions.
   (b) For title questions the key and the system execute the same Python normalization, so a bug or debatable choice in it is invisible to the evaluation. Example: the key/v2 exclude "business intelligence analyst" from "BI Analyst" — that is 1,013 certified H-1B cases (705 titled exactly so), and round 1's "failure" on D6 was arguably the more natural reading. v2 is effectively the key's specification handed to the model, so 9/10 and 5/5 measure spec-to-SQL translation against a key built on the same definitions — not correctness against an external truth. The held-out key reads the same SQLite load and was never cross-checked against the workbook (only D2's Boston count was).
   (c) **Medium.**

10. **The held-out set is weak evidence of transfer.**
    (a) FAILURE-LOG.md:43 ("carried over to questions it was not tuned on"); `PROMPT-CONTRACT-v2.md:3` ("Held-out questions were not looked at when writing it").
    (b) The same Claude session wrote the held-out questions and key (13:17) and v2 about 6 minutes later, so "not looked at" is unverifiable and implausible. The held-out questions are slot-variants of dev templates: H1≈D2 (count, title + place), H2≈D1 (ranking), H3≈D4 (median), H4≈D5+D8 (wage level by SOC), H5≈D2 with a different status. The freeze ordering itself is verified (see above).
    (c) **Medium.**

11. **Round-2 prompts carry question-specific hints.**
    (a) `prompt.build` sends the whole contract file; v2's "Changes from v1" table (`PROMPT-CONTRACT-v2.md:54`) is in every round-2 and held-out prompt (confirmed "D8 grouped" appears in the prompts JSON).
    (b) The model is told the specific round-1 errors on D3/D5/D6/D8, so dev 9/10 is tuned on those exact questions. Dev is allowed to be tuned, but 9/10 estimates nothing. Also v1 told the model to follow "rules in ANSWER-KEY.md" it never received, so the 4/10 baseline was handicapped by design.
    (c) **Low–medium.**

12. **The pre-mortem's "prediction" had already been observed.**
    (a) pre-mortem.md "The failure I predict"; the controlled-failure claim.
    (b) `FAILURE-LOG-october-draft.md` (same commit `da6b416`) already recorded the substring failure on the same 10 questions; round-1 D5 (I 1,026 · II 1,605 · III 514) and D9 (April 696) exactly match the October numbers, and C1 simply re-runs the October Q5 query. The "what would make me wrong" condition was nearly impossible to meet since v1 had no title helper. The pre-mortem does mention the October draft, but "predicted" and "triggered on purpose" overstate a replication.
    (c) **Medium.**

13. **In-document timestamps contradict the commits that contain them.**
    (a) Commit `da6b416` is dated 13:08:39 -0500, yet it contains CONTRACT.md "Written 13:10 EST", dev-questions.json "output shapes added 13:20 EST", and PROMPT-CONTRACT-v1.md describing a change "at 13:15 EST, before any agent code".
    (b) Either the in-document times are invented or the commit dates are; git dates are author-settable either way, so ordering evidence is commit order only. Also v2 was committed 56 s after the round-1 run finished (ledger 18:22:12Z, commit 13:23:08), and `CONTRACT.md` was edited after the gate commit (`99a6b8c`, a link fix) despite being presented as the pre-code gate.
    (c) **Low–medium.**

14. **Recorded-reply provenance cannot be verified from the artifacts.**
    (a) Provenance blocks in `evals/proposals/*-responses.json`.
    (b) The hashes only prove internal consistency; the raw replies were transcribed by the parent session, which had the keys in context. The round-2 provenance itself admits 2 tool uses "not independently verified" — and that is the 9/10 round. `RecordedAdapter` ignores the prompt, so `contract_sha256` in results is a label, not evidence. The live adapter passes no tool restrictions and runs in the project folder next to the answer keys (`adapters.py:70-72`), so live-mode independence is not enforced; I could not test that path.
    (c) **Medium.**

15. **Question screen gaps, and no model-side refusal channel.**
    (a) `screen.py:9`; `proposal.py:8`.
    (b) The regex `addresses?` matches "addresse"/"addresses" but not "address": "What is the address of the Amazon worksite in Boston?" was **not** refused. Prediction questions not refused: "Should I expect approval if Google files my LCA?", "Is it realistic that Amazon sponsors an international student like me?". False refusals: "Which employers filed cases for Attorney job titles?", "How does the median wage change by wage level in the data?". The reply schema has no refuse field, so a question that slips past the screen can only end as SQL or a mislabelled `deferred_clarification`, even though the contract says the model should refuse.
    (c) **Low–medium** (contact columns are not loaded, which limits harm).

16. **Count-vs-rows check trusts the model's label and the model's own queries.**
    (a) `agent.py:118-126`.
    (b) Only runs when the model says `answer_type == "count"`, and compares two queries from the same reply. H3 produced a false MISMATCH (acknowledged); a wrong count labelled `table` skips the check entirely (see finding 5).
    (c) **Low** (partly acknowledged in audit-note.md).

17. **Source check validates a label, not the data.**
    (a) `agent.py:40-45`; `gate.py:39,46`.
    (b) The run compares a string in the DB's `metadata` table, not a hash of the database file. The view always prints the constant `config.SOURCE_SHA256` — even when the fixture DB (metadata "synthetic-test-fixture") is queried with `expected_sha` overridden — so modified `lca` rows would still display the workbook hash.
    (c) **Low.**

18. **README/brief claims stronger than the evidence.**
    (a) README.md:12 ("so you can see the number is right"); brief.md:14 ("can see the data they're getting is correct").
    (b) This contradicts the project's own central finding that wrong substring SQL "looked reasonable", and only 20 matching rows are shown. Smaller doc issues: ANSWER-KEY.md:10 and both contracts cite `load_lca_sqlite.py`, which is not in the repo; `evidence/clean-checkout.log` is a curated summary with placeholders (`<workbook>`, `evaluate (held-out)`), not raw output; D3's round-1 failure was a 10 s timeout, so that score is hardware-dependent.
    (c) **Low–medium.**

## What I could not check
As an AI reading files and running local commands, I could not verify: that the subagent replies are what a Claude subagent actually produced (I only have files the parent session wrote, no transcripts or run IDs); what the round-2 subagent read with its second tool use; that the dated sequence (gate before code, freeze before proposals) happened in real time rather than being committed in that order afterwards; whether the owner reviewed anything; how the live `claude -p` path behaves (tool use under `--max-turns 1`, cwd file access, output variance); that the SQLite load faithfully reflects the DOL workbook beyond D2's Boston rows (I did not download or re-hash the workbook or recount any key by hand); whether the key's definitions match what a real student means by "Data Analyst" or "BI Analyst" (a human judgment); and how a real human behaves at the gate (whether they read the view or just paste the hash).
