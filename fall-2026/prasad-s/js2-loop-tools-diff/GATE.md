# GATE.md — Job-Search Agent 2: the loop, the tools, the diff

**Author:** Prasad Shinde
**Written:** 2026-11-05, before Claude Code changed any code in this folder
**Started from:** JS1's js1-contract-and-watch/ at commit bff5356 (JS1-CP18, 2026-10-31), as signed off on 2026-10-31
**Written against:** evidence/gate_probes/ (probes of 2026-11-02)

## 0. Boards
| Board | ATS | Name | Host | Role (watched / fails on purpose) | Why |
|---|---|---|---|---|---|
| stripe | Greenhouse | Stripe | boards-api.greenhouse.io | watched | JS1's board. The loop has to reproduce JS1's watch on it before it may claim anything more. |
| notion | Ashby | Notion | api.ashbyhq.com | watched | A second ATS with a different shape — a jobs array, and plain-text error bodies — so the loop cannot quietly assume Greenhouse's shape. Chosen over OpenAI: about 2.7 MB a run against about 14 MB, JS2 is graded on the loop rather than on PM yield, and OpenAI can be added later. |
| js2nosuchboard | Ashby | — (no such board) | api.ashbyhq.com | fails on purpose | The name does not exist, so it 404s every run, on purpose. Ashby's 404 body is plain text, not JSON, so every run also proves the adapter checks the status before it tries to read jobs (§4) — instead of waiting for a real outage. |

Starting state: every board starts fresh in this folder, with no saved ids. The first run for each board is a baseline and reports nothing as new; the diff appears from the second run. JS1's state.json is not read, not copied, and not written — it stays as JS1 submitted it.

## 1. Exits
For each: when it happens, what the report says, what happens to saved ids.
- finished: every board in the run was visited and accounted for — fetched and processed, reported zero jobs, or reported failed under §4. The report gives, per board: status, jobs fetched, new ids, already-seen ids, attempts. Saved ids are updated for every board that returned a valid response; a failed board's saved ids do not change.
- incomplete: the loop stopped before every board was accounted for, for a reason that is neither a board failure nor a budget — an operator interrupt, or a required write being refused. The report names the boards completed and the boards not attempted. Saved ids stand for the completed boards only.
- budget-exhausted: a budget in §2 ran out mid-loop. The board in progress finishes its current request (no new retry starts), then the loop stops. The report names the budget that ran out and the board it ran out on; boards not attempted are listed as not attempted, never as zero. Saved ids stand for the completed boards only.
- error: something outside any one board broke — the state file is corrupt or unreadable, the config is invalid, the evidence folder is not writable. The report names the error. The board being processed adds no ids; boards already completed keep their updates.
- refused (if a refusal can end a run): the run's own instructions break §5 — a configured host is off the allow-list, or an output path resolves outside the writable folders. The run ends before any fetch or write. The report names the request and the rule it broke. Saved ids are unchanged.
A run that includes the deliberate failure ends as: finished — with that board reported failed under §4. A planned failure, reported as a failure, is a completed run, not an error.
"Finished" never means: every board succeeded, or any posting was relevant, or there were new postings. It means the loop visited every board and accounted for each one.

The judge in JS2: JS1's judge code is carried over unchanged, and no new Claude replies are collected. Every new posting therefore carries the line "rejected — no saved reply (judge not run in JS2)", which is JS1's contract verdict for a missing reply — not a format rejection, and not a judgment. JS2 claims no Claude verdicts.

## 2. Budgets
- Max boards per run: 5
- Max requests per run: 10 (do retries count? Yes. Every attempt is a request; a budget that retries don't count against is not a budget.)
- Max seconds per run: 60 (each probe took 0.1–0.9 s, so this is headroom, not a target; a single request times out at 10 s, per §4)
- When a budget runs out mid-loop: no new board and no new retry starts; the exit is budget-exhausted (§1).
- Who may change a budget, and how: only I may, by a dated amendment to this file. Never the agent, never a prompt, never mid-run, and a change is never retroactive to a run already reported.

## 3. Repeat rule
- Two actions are "the same" when: a fetch has the same method, host and path for the same board within one run; a write has the same tool, the same resolved absolute path, and the same content.
- On a repeat, the loop: does not execute it again. It returns the result recorded for the first execution and marks the line "repeat — not re-run" in the report, so the report shows the loop noticed.
- A posting id counts as seen per board — the key is (board, id) — because: an id is only unique inside its own board. Greenhouse's numeric ids and Ashby's ids are different namespaces, and the same string on two boards is two postings. Ids are compared as strings, converted at the boundary, as in JS1.

## 4. Error policy
| Failure | Retry? How many? | Why a retry is or isn't sound | Board result | Run exit |
|---|---|---|---|---|
| 404 (Greenhouse JSON / Ashby plain text) | No — 0 | A 404 is an answer, not a passing state: the board name is wrong or the board is gone. Retrying fetches the same answer and spends budget on it. The two body shapes change nothing; the status decides, and the body is never parsed as jobs. | failed — not found (404) | Continues with the other boards |
| Timeout | Yes — 1 retry (2 attempts) | A timeout is transient and the request is a read-only GET; repeating it changes nothing on the server. The retry counts against the request budget. | failed — timeout after 2 attempts | Continues with the other boards |
| 5xx or connection error | Yes — 1 retry (2 attempts) | The failure is on the server's side or on the way to it, and the GET is idempotent, so one retry is sound. More than one is just spending the budget on a board that has already said no twice. | failed — 5xx / connection error after 2 attempts | Continues with the other boards |
| 200, but not the expected shape | No — 0 | A retry returns the same shape. A shape mismatch is a contract problem, not a transient one, and parsing a wrong shape as zero jobs would invent an empty board. The raw response is saved as evidence, unparsed. | failed — unexpected shape | Continues with the other boards |
| 200 with zero jobs | Not an error — no retry | Zero is a real answer. | ok — 0 jobs, 0 new | Continues; the board's saved ids are unchanged, because a board reporting zero jobs does not erase its history |
| Redirect | No — 0, and never followed | The allow-list pins the exact host; a redirect is precisely how a fetch leaves it (JS1's refusal cases). The status and the Location value are recorded instead. | failed — redirect refused | Continues with the other boards |

Instead of a value, a failed board's report says: the word "failed", the reason from this table, and the number of attempts — never 0 jobs and never an empty list.
That board's saved ids: unchanged. Nothing is added and nothing is removed; a failed board never updates, and never clears, its seen set.

## 5. Permission policy
- Hosts the agent may call (exact match?): exact match only, over https: boards-api.greenhouse.io and api.ashbyhq.com. The host is compared whole and lowercased — no subdomains, no suffix or prefix matches, no userinfo, no non-default port, no http.
- Folders it may read: this folder (the JS2 project folder), including config, the persona, state, and evidence/gate_probes/. Nothing outside it.
- Folders it may write: inside this folder only, and only its working subfolders — state, evidence (raw responses), and output (run reports).
- Writes that need my approval, and how approval is given: any write outside those subfolders, any overwrite or deletion of an existing file, and any change to GATE.md, CONTRACT.md or the config. Approval is mine, given in chat, for one named path and one write ("yes, write <path>") — never blanket, and it does not carry over to the next write.
- Never: apply, email, message, log in, submit a form, spend money, use a credential, follow a redirect off the allow-list, change a budget, edit this file, delete a file, or present a model's judgment as a fact.
- Enforced in code, at: the tool layer — one permission-check function that every fetch and every write passes through before it executes. The loop has no way to reach the network or the filesystem except through the tools, and the tests call the check function directly. It is not enforced in a prompt.

## 6. Wrong versions
(W1 and W2 carry over from JS1.)
- W3: a failed board laundered into an empty board — the loop reports it as "0 jobs, 0 new" and the run looks clean. Caught by: a test run against the deliberate-failure board: its line must say "failed" with the reason, its saved ids must be unchanged, and the run's exit is finished-with-a-failed-board, not a clean finished.
- W4: seen keyed by the id alone, board ignored — so a posting whose id matches another board's id is silently dropped as already seen. Caught by: a test where two boards return the same id string: it is new on each board, and both copies are reported.

## 7. Boundary tests — predicted 2026-11-05, before running
| ID | Case | Exact input | Predicted result | Why |
|---|---|---|---|---|
| B01 | Host off the allow-list | Fetch https://example.com/jobs | Refused; no request is sent; the refusal names the host | example.com is not an exact match for any allow-listed host (§5) |
| B02 | Path with `..` | Write output/../../outside.txt | Refused; nothing is written | The resolved path leaves the writable folders; paths are judged after resolution, not as written (§5) |
| B03 | Prefix trick (`boards-api.greenhouse.io-evil` beside `boards-api.greenhouse.io`) | Fetch https://boards-api.greenhouse.io-evil.example/jobs | Refused; no request is sent | A host that merely starts with an allow-listed host is a different host; matching is exact and whole (§5) |
| B04 | Symlink leading out of the output folder | Write output/link/report.txt, where output/link points outside the project folder | Refused; nothing is written | The check resolves the real path, and the real path is outside the writable folders (§5) |
| B05 | Read request in an allowed folder | Read a file under evidence/gate_probes/ | Allowed; the content is returned | Reads inside the project folder are permitted (§5) |
| B06 | Write request to the same path | Write to that same evidence/gate_probes/ path | Refused | Read permission is not write permission: evidence is not one of the working subfolders for new writes, and overwriting an existing file needs approval (§5) |
| B07 | Write that needs approval, without approval | Write GATE.md, with no approval given | Refused; the file is unchanged | GATE.md is named in §5 as approval-only |
| B08 | The same write, with approval | Write GATE.md, after I approve that named path in chat | Allowed; the file is written, and the report records the approval | §5: approval is per path and per write |
| B09 | Right host, wrong scheme | Fetch http://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true | Refused; no request is sent | The allow-list entry is https; the scheme is part of the match (§5, and JS1's U05) |
| B10 | Userinfo trick | Fetch https://boards-api.greenhouse.io@evil.example/jobs | Refused; no request is sent | The real host is evil.example; what stands before the @ is userinfo, not the host (§5) |
