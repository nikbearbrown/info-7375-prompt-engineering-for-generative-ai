# GATE.md — Job-Search Agent 2: the loop, the tools, the diff

**Author:** Prasad Shinde
**Written:** 2026-11-05, before Claude Code changed any code in this folder
**Amended:** v0.3, 2026-11-07, after run 1 and the CP7 demo (see the Changelog).
**Started from:** JS1's js1-contract-and-watch/ at commit bff5356 (JS1-CP18, 2026-10-31), as signed off on 2026-10-31
**Written against:** evidence/gate_probes/ (probes of 2026-11-02) and evidence/snapshots/ (board snapshots of 2026-11-05)

## 0. Boards
| Board | ATS | Name | Host | Role (watched / fails on purpose) | Why |
|---|---|---|---|---|---|
| stripe | Greenhouse | Stripe | boards-api.greenhouse.io | watched | JS1's board. The loop has to reproduce JS1's watch on it before it may claim anything more. |
| notion | Ashby | Notion | api.ashbyhq.com | watched | A second ATS, different from Greenhouse in the ways that break adapters: its ids are UUID strings, not numbers; the job text comes in description fields, not in a content field behind ?content=true; and its error bodies are plain text, not JSON. Chosen over OpenAI: about 2.7 MB a run against about 14 MB, JS2 is graded on the loop rather than on PM yield, and OpenAI can be added later. |
| duolingo | Greenhouse | Duolingo | boards-api.greenhouse.io | watched | A second Greenhouse board — same adapter as Stripe, different board — so the loop has to be driven by the board list, not by one board wired in. In the 2026-11-05 snapshot: 56 jobs, about 0.68 MB a run. |
| robinhood | Greenhouse | Robinhood | boards-api.greenhouse.io | watched | A third Greenhouse board, in the middle on size — bigger than Duolingo, far smaller than Stripe's 763 jobs — so the loop is run at more than one size. In the 2026-11-05 snapshot: 151 jobs, about 1.95 MB a run. |
| js2nosuchboard | Ashby | — (no such board) | api.ashbyhq.com | fails on purpose | The name does not exist, so it 404s every run, on purpose. Ashby's 404 body is plain text, not JSON, so every run also proves the adapter checks the status before it tries to read jobs (§4) — instead of waiting for a real outage. |

Starting state: every board starts fresh in this folder, with no saved ids. The first run for each board is a baseline and reports nothing as new; the diff appears from the second run. JS1's state.json is not read, not copied, and not written — it stays as JS1 submitted it.

## 1. Exits
For each: when it happens, what the report says, what happens to saved ids.
- finished: every board in the run was visited and accounted for — fetched and processed, reported zero jobs, or reported failed under §4. The report gives, per board: status, jobs fetched, new ids, already-seen ids, attempts. Saved ids are updated for every board that returned a valid response; a failed board's saved ids do not change.
- incomplete: the loop stopped before every board was accounted for, for a reason that is neither a board failure nor a budget — an operator interrupt, or a required write being refused. The report names the boards completed and the boards not attempted. Saved ids stand for the completed boards only.
- budget-exhausted: a budget in §2 ran out mid-loop. The board in progress finishes its current request (no new retry starts), then the loop stops. The report names the budget that ran out and the board it ran out on; boards not attempted are listed as not attempted, never as zero. Saved ids stand for the completed boards only.
- error: something outside any one board broke — the state file is corrupt or unreadable, the config is invalid, the evidence folder is not writable. The report names the error. The board being processed adds no ids; boards already completed keep their updates.
- refused (if a refusal can end a run): the run's own instructions break §5 — a configured host is off the allow-list, or an output path resolves outside the writable folders. The run ends before any fetch or write. The report names the request and the rule it broke. Saved ids are unchanged.
A run with one or more failed boards ends as finished — with failures: the exit is still finished, and the exit line names the failed boards. It is not a separate exit, and it is never written as a plain finished.
A run that includes the deliberate failure ends as: finished — with failures, naming js2nosuchboard. A planned failure, reported as a failure, is a completed run, not an error.
"Finished" never means: every board succeeded, or any posting was relevant, or there were new postings. It means the loop visited every board and accounted for each one.

The judge in JS2: JS1's judge code is carried over unchanged, and no new Claude replies are collected. Every new posting therefore carries the line "rejected — no saved reply (judge not run in JS2)", which is JS1's contract verdict for a missing reply — not a format rejection, and not a judgment. JS2 claims no Claude verdicts.

## 2. Budgets
- Max boards per run: 5 — the five boards in §0. Adding a board takes a dated amendment to this file and a recheck of the request budget below.
- Max requests per run: 10 (do retries count? Yes. Every attempt is a request; a budget that retries don't count against is not a budget.) The number is the worst case §4 allows: 5 boards × 2 attempts = 10. It has no slack on purpose — a request beyond it is outside §4 by construction, and the run ends budget-exhausted.
- Max seconds per run: 60 (each probe took 0.1–0.9 s, so this is headroom, not a target; a single request times out at 10 s, per §4)
- When a budget runs out mid-loop: no new board and no new retry starts; the exit is budget-exhausted (§1).
- Who may change a budget, and how: only I may, by a dated amendment to this file. Never the agent, never a prompt, never mid-run, and a change is never retroactive to a run already reported.

## 3. Repeat rule
- Two actions are "the same" when: a fetch has the same method, host and path for the same board within one run; a write has the same tool, the same resolved absolute path, and the same content.
- On a repeat, the loop: does not execute it again. It returns the result recorded for the first execution and marks the line "repeat — not re-run" in the report, so the report shows the loop noticed.
- A retry is not a repeat. A retry is a second attempt, inside §4's allowance, at an action that has not produced a result yet: it executes, and it counts as a request. A repeat is the same action asked for after its result — or its final failure, once §4's retries are spent — is already recorded: it never executes, and the recorded outcome is returned.
- A posting id counts as seen per board — the key is (board, id) — because: an id is only unique inside its own board. Greenhouse's numeric ids and Ashby's ids are different namespaces, and the same string on two boards is two postings. Ids are compared as strings, converted at the boundary, as in JS1.

## 4. Error policy
| Failure | Retry? How many? | Why a retry is or isn't sound | Board result | Run exit |
|---|---|---|---|---|
| 404 (Greenhouse JSON / Ashby plain text) | No — 0 | A 404 is an answer, not a passing state: the board name is wrong or the board is gone. Retrying fetches the same answer and spends budget on it. The two body shapes change nothing; the status decides, and the body is never parsed as jobs. | failed — not found (404) | Continues with the other boards |
| Timeout — no answer within 10 s | Yes — 1 retry (2 attempts) | A timeout is transient and the request is a read-only GET; repeating it changes nothing on the server. The retry counts against the request budget. | failed — timeout after 2 attempts | Continues with the other boards |
| 5xx or connection error | Yes — 1 retry (2 attempts) | The failure is on the server's side or on the way to it, and the GET is idempotent, so one retry is sound. More than one is just spending the budget on a board that has already said no twice. | failed — 5xx / connection error after 2 attempts | Continues with the other boards |
| 200, but not the expected shape | No — 0 | A retry returns the same shape. A shape mismatch is a contract problem, not a transient one, and parsing a wrong shape as zero jobs would invent an empty board. The raw response is saved as evidence, unparsed. | failed — unexpected shape | Continues with the other boards |
| 200 with zero jobs, on a board with no saved ids | Not an error — no retry | Zero is a real answer here: the agent holds no saved ids for this board, so there is no history for it to contradict, and an empty board is not a change. | ok — 0 jobs, 0 new | Continues; the board's saved ids are unchanged |
| 200 with zero jobs, on a board with saved ids | No — 0 | The board has contradicted its own saved state: the state file holds ids for this board and the response holds none, and both can be checked by hand — that is exactly CP7's case. It is not a timeout, so there is nothing transient to retry; a second fetch of the same empty board would only spend budget. Reporting it as ok would call a board whose jobs all vanished an empty board. | failed — empty board: 0 jobs, N ids saved before | Continues with the other boards; the run ends finished — with failures, naming this board |
| Redirect | No — 0, and never followed | The allow-list pins the exact host; a redirect is precisely how a fetch leaves it (JS1's refusal cases). The status and the Location value are recorded instead. | failed — redirect refused | Continues with the other boards |

Instead of a value, a failed board's report says: the word "failed", the reason from this table, and the number of attempts — never 0 jobs and never an empty list.
That board's saved ids: unchanged. Nothing is added and nothing is removed; a failed board never updates, and never clears, its seen set.

A board that had saved ids and now returns zero jobs is reported as "failed — empty board: 0 jobs, N ids saved before" — never as "0 new". Its saved ids are unchanged, and its response is saved as evidence, as every live response is (a seeded board saves none, CONTRACT v0.7 item 1).

## 5. Permission policy
- Hosts the agent may call (exact match?): exact match only, over https: boards-api.greenhouse.io and api.ashbyhq.com. The host is compared whole and lowercased — no subdomains, no suffix or prefix matches, no userinfo, no non-default port, no http.
- Folders it may read: this folder (the JS2 project folder), including config, the persona, state, and evidence/gate_probes/. Nothing outside it.
- Folders it may write: inside this folder only, and only its working subfolders — state, evidence (raw responses), and output (run reports). One part of evidence is read-only: evidence/gate_probes/, the probes this file was written against, is never written.
- Writes that need my approval, and how approval is given: any write outside those subfolders, any overwrite of an existing file, and any change to CONTRACT.md or the config. Approval is mine, for one named path and one write. I say it in chat; the approval the program acts on is the flag typed on its command line — --approve <exact path> — on that run only. The program honors the flag for that one write to that exact path, records the flag in the run report, and ignores it on any later run. No flag, no write.
- Budgets live in §2 of this file, and nowhere else. The config holds no budget values; if one appears there, the run ends error (invalid config). No approval covers a budget — not even an approved config write. A budget changes only by a dated amendment to this file.
- Never: apply, email, message, log in, submit a form, spend money, use a credential, follow a redirect off the allow-list, change a budget, edit this file (GATE.md — no approval overrides this one), delete a file, or present a model's judgment as a fact.
- Enforced in code, at: the tool layer — one permission-check function that every fetch and every write passes through before it executes. The loop has no way to reach the network or the filesystem except through the tools, and the tests call the check function directly. It is not enforced in a prompt.

## 6. Wrong versions
(W1 and W2 carry over from JS1.)
- W3: a failed board laundered into an empty board — the loop reports it as "0 jobs, 0 new" and the run looks clean. Caught by: a test run against the deliberate-failure board: its line must say "failed" with the reason, its saved ids must be unchanged, and the run must end finished — with failures, naming that board — not a plain finished.
- W4: seen keyed by the id alone, board ignored — so a posting whose id matches another board's id is silently dropped as already seen. Caught by: a test where two boards return the same id string: it is new on each board, and both copies are reported.
- W5: a board whose saved state holds ids returns zero jobs, and the loop reports it as an ordinary empty board — "ok — 0 jobs, 0 new" — so a board whose jobs all vanished looks like a board that never had any, and the run ends a plain finished. Caught by: the test that reproduces CP7's demo (evidence/demo_finished_wrong_answer/) through the live path, with the network patched as in the other loop tests: saved state holding 59 ids for greenhouse:duolingo, as after run 1, and a constructed 200 response with zero jobs. The board's line must say "failed — empty board: 0 jobs, 59 ids saved before", its 59 saved ids must be unchanged, its response must be saved as evidence, and the run must end finished — with failures, naming greenhouse:duolingo.

## 7. Boundary tests — predicted 2026-11-05, before running
| ID | Case | Exact input | Predicted result | Why |
|---|---|---|---|---|
| B01 | Host off the allow-list | Fetch https://example.com/jobs | Refused; no request is sent; the refusal names the host | example.com is not an exact match for any allow-listed host (§5) |
| B02 | Path with `..` | Write output/../../outside.txt | Refused; nothing is written | The resolved path leaves the writable folders; paths are judged after resolution, not as written (§5) |
| B03 | Prefix trick (`boards-api.greenhouse.io-evil` beside `boards-api.greenhouse.io`) | Fetch https://boards-api.greenhouse.io-evil.example/jobs | Refused; no request is sent | A host that merely starts with an allow-listed host is a different host; matching is exact and whole (§5) |
| B04 | Symlink leading out of the output folder | Write output/link/report.txt, where output/link points outside the project folder | Refused; nothing is written | The check resolves the real path, and the real path is outside the writable folders (§5) |
| B05 | Read request in an allowed folder | Read a file under evidence/gate_probes/ | Allowed; the content is returned | Reads inside the project folder are permitted (§5) |
| B06 | Write request to the same path | Write to that same evidence/gate_probes/ path | Refused; nothing is written | gate_probes/ is read-only in §5, and overwriting an existing file would need approval besides. That a read is allowed says nothing about writes |
| B07 | Write that needs approval, without approval | Write config.json, with no --approve flag on the run | Refused; the file is unchanged | The config is named in §5 as approval-only, and no flag means no approval reached the program |
| B08 | The same write, with approval | Write config.json, with --approve config.json on that run | Allowed; the file is written, and the report records the flag | §5: approval is per path and per write, and the flag is how it reaches the program |
| B09 | Right host, wrong scheme | Fetch http://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true | Refused; no request is sent | The allow-list entry is https; the scheme is part of the match (§5, and JS1's U05) |
| B10 | Userinfo trick | Fetch https://boards-api.greenhouse.io@evil.example/jobs | Refused; no request is sent | The real host is evil.example; what stands before the @ is userinfo, not the host (§5) |
| B11 | Sibling-folder prefix trick | Write output-evil/report.txt, where output-evil/ sits beside output/ | Refused; nothing is written | The path is judged on whole folder names after resolution, not on a string prefix: output-evil is not output, just as in B03 (§5) |

## Changelog
- v0.1 — 2026-11-05: first version, written before any code in this folder.
- v0.2 — 2026-11-05: changes from a review by Claude (Claude.ai) on 2026-11-05; the decisions are mine. Items 1–10 from the review list: (1) Duolingo and Robinhood added as watched boards; request budget rechecked — 10 is now the §4 worst case for 5 boards, with the reason written into §2. (2) B11 added, the sibling-folder prefix trick. (3) GATE.md moved under Never, where no approval overrides it; B07/B08 now test the config write instead. (4) evidence/gate_probes/ made read-only in §5, and B06's reason fixed to match. (5) §3 now says how a retry differs from a repeat. (6) §1 names the exit for a run with failed boards — finished — with failures — and W3 is worded to match. (7) §5 now says approval reaches the program as a command-line flag, --approve <exact path>. (8) Zero jobs: §4 kept as written (option a); the policy is revisited only by a dated amendment after the empty-board demo, if the demo shows it wrong. (9) The 10-second timeout is now stated in §4 itself. (10) Notion's Why names the real differences from Greenhouse: id shape, description fields, error bodies.
- v0.3 — 2026-11-07: §4's zero-jobs row is split in two. Zero jobs stays ok on a board with no saved ids; on a board whose saved state already holds at least one id it is now a failure — "failed — empty board: 0 jobs, N ids saved before" — with no retry, the saved ids unchanged, the response saved as evidence (live responses; a seeded board saves none), and the run ending finished — with failures. W5 added in §6, tested through the live path. Why: the CP7 demo (evidence/demo_finished_wrong_answer/) showed the old row giving the wrong answer — a board with saved ids returned zero jobs and the run reported an ordinary empty board and finished clean. This is the amendment v0.2 item 8 said would follow if the demo showed §4 wrong. Not covered, named in advance as the cases this change still misses: a partial drop, such as 59 jobs falling to 3, which is still just a smaller board; and an empty first run, where a board with no saved ids reports zero jobs and is ok under this rule (CONTRACT v0.7 item 6). Reviewed by Claude (Claude.ai) on 2026-11-07, which suggested the live-path test, the concrete 59 ids, the reworded reason in the first row and the header line; the decisions and the wording are mine.