# Trace of run 2026-11-20T114036Z

| Step | Time (UTC) | Kind | What happened |
|---:|---|---|---|
| 1 | 11:40:36 | run_start | run_id: 2026-11-20T114036Z; source: live; gate_version: 1.0; contract_version: 0.2; budgets: {"boards": 5, "requests": 10, "claude_calls": 20, "seconds": 600}; resume: jane-doe.json; code_sha256: 6eebbe57c553a7898ef971828d67b5839e1e873c849c08b2c6b691b53baffc96; git_head: 1779827348dec1ada6d31043d41ba0daa89e1407; prompt: {"file": "baseline.txt", "sha256": "d616ca168220aafe6142bf01629832efbec5f6117007148d75fc290199e3712a", "model": "claude-sonnet-5-5"} |
| 2 | 11:40:36 | board_list | visiting: ["ashby-openai", "greenhouse-verkada", "lever-palantir", "greenhouse-no-such-board-js2-test"]; repeats: []; not_visited_boards_budget: []; deliberate_failure: ["greenhouse-no-such-board-js2-test"] |
| 3 | 11:40:36 | permission | board: ashby-openai; url: https://api.ashbyhq.com/posting-api/job-board/openai; allowed: True |
| 4 | 11:40:36 | request | board: ashby-openai; attempt: 1; retry: False; method: GET; url: https://api.ashbyhq.com/posting-api/job-board/openai; requests_used: 1 |
| 5 | 11:40:37 | answer | board: ashby-openai; attempt: 1; status: 200; bytes: 14343567; sha256: d595afc07e6388c74e510d380f637a28f71a64f29c05a599ec1a873941feb2e7; file: runs/2026-11-20T114036Z/boards/ashby-openai/attempt-1.json.gz; seconds: 0.51 |
| 6 | 11:40:37 | decision | board: ashby-openai; action: no retry; why: job 482 has no title; a retry cannot fix this answer (GATE.md, Error policy) |
| 7 | 11:40:37 | decision | board: ashby-openai; action: unverified; why: job 482 has no title. Its state stays as it was, nothing counts as new or gone, and it is escalated to you |
| 8 | 11:40:37 | permission | board: greenhouse-verkada; url: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true; allowed: True |
| 9 | 11:40:37 | request | board: greenhouse-verkada; attempt: 1; retry: False; method: GET; url: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true; requests_used: 2 |
| 10 | 11:40:39 | answer | board: greenhouse-verkada; attempt: 1; status: 200; bytes: 4157532; sha256: cface440ae606b2c8cfbf6a6567918f5a7b06ae9b41f317668908bb4e630fe86; file: runs/2026-11-20T114036Z/boards/greenhouse-verkada/attempt-1.json.gz; seconds: 1.83 |
| 11 | 11:40:39 | parse | board: greenhouse-verkada; postings: 348; mapped_from: greenhouse |
| 12 | 11:40:39 | diff | board: greenhouse-verkada; baseline: False; new: 0; gone: 0 |
| 13 | 11:40:39 | permission | board: lever-palantir; url: https://api.lever.co/v0/postings/palantir?mode=json; allowed: True |
| 14 | 11:40:39 | request | board: lever-palantir; attempt: 1; retry: False; method: GET; url: https://api.lever.co/v0/postings/palantir?mode=json; requests_used: 3 |
| 15 | 11:40:40 | answer | board: lever-palantir; attempt: 1; status: 200; bytes: 5954399; sha256: 95b992f2009e7050780c9b9d219f3aa906e682f3e9a193a2c29df7d2f9db4f64; file: runs/2026-11-20T114036Z/boards/lever-palantir/attempt-1.json.gz; seconds: 1.25 |
| 16 | 11:40:40 | parse | board: lever-palantir; postings: 307; mapped_from: lever |
| 17 | 11:40:40 | diff | board: lever-palantir; baseline: False; new: 0; gone: 0 |
| 18 | 11:40:40 | permission | board: greenhouse-no-such-board-js2-test; url: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true; allowed: True |
| 19 | 11:40:40 | request | board: greenhouse-no-such-board-js2-test; attempt: 1; retry: False; method: GET; url: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true; requests_used: 4 |
| 20 | 11:40:40 | answer | board: greenhouse-no-such-board-js2-test; attempt: 1; status: 404; bytes: 38; sha256: 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe; file: runs/2026-11-20T114036Z/boards/greenhouse-no-such-board-js2-test/attempt-1.json.gz; seconds: 0.09 |
| 21 | 11:40:40 | decision | board: greenhouse-no-such-board-js2-test; action: no retry; why: the board answered HTTP 404, not 200; a retry cannot fix this answer (GATE.md, Error policy) |
| 22 | 11:40:40 | decision | board: greenhouse-no-such-board-js2-test; action: unverified; why: the board answered HTTP 404, not 200. Its state stays as it was, nothing counts as new or gone, and it is escalated to you |
| 23 | 11:40:40 | judge_rule | postings: 32; relevant: 0 |
| 24 | 11:40:45 | claude_call | board: greenhouse-verkada; posting_id: 5292895007; why: waited; valid: True; verdict: not_relevant; record: claude/f22f05d7d6.json; calls_used: 1 |
| 25 | 11:40:51 | claude_call | board: greenhouse-verkada; posting_id: 5294939007; why: waited; valid: True; verdict: not_relevant; record: claude/259fac2a2d.json; calls_used: 2 |
| 26 | 11:40:58 | claude_call | board: greenhouse-verkada; posting_id: 5301451007; why: waited; valid: True; verdict: not_relevant; record: claude/bf20fd5ed1.json; calls_used: 3 |
| 27 | 11:41:01 | claude_call | board: greenhouse-verkada; posting_id: 5298284007; why: waited; valid: True; verdict: not_relevant; record: claude/dc613a7f27.json; calls_used: 4 |
| 28 | 11:41:04 | claude_call | board: greenhouse-verkada; posting_id: 5291267007; why: waited; valid: True; verdict: not_relevant; record: claude/57ed881f9f.json; calls_used: 5 |
| 29 | 11:41:06 | claude_call | board: greenhouse-verkada; posting_id: 5302623007; why: waited; valid: True; verdict: not_relevant; record: claude/882c7f7f39.json; calls_used: 6 |
| 30 | 11:41:09 | claude_call | board: greenhouse-verkada; posting_id: 5302630007; why: waited; valid: True; verdict: not_relevant; record: claude/3e445c18a8.json; calls_used: 7 |
| 31 | 11:41:12 | claude_call | board: greenhouse-verkada; posting_id: 5287692007; why: waited; valid: True; verdict: not_relevant; record: claude/5ff6bff5e0.json; calls_used: 8 |
| 32 | 11:41:15 | claude_call | board: greenhouse-verkada; posting_id: 5302631007; why: waited; valid: True; verdict: not_relevant; record: claude/405ce13783.json; calls_used: 9 |
| 33 | 11:41:19 | claude_call | board: greenhouse-verkada; posting_id: 5302088007; why: waited; valid: True; verdict: not_relevant; record: claude/10d1b7f16a.json; calls_used: 10 |
| 34 | 11:41:24 | claude_call | board: greenhouse-verkada; posting_id: 5290383007; why: waited; valid: True; verdict: not_relevant; record: claude/7ee63b0d50.json; calls_used: 11 |
| 35 | 11:41:26 | claude_call | board: greenhouse-verkada; posting_id: 5302824007; why: waited; valid: True; verdict: not_relevant; record: claude/8ccac1e743.json; calls_used: 12 |
| 36 | 11:41:28 | claude_call | board: greenhouse-verkada; posting_id: 5083834007; why: waited; valid: True; verdict: not_relevant; record: claude/9895e12e39.json; calls_used: 13 |
| 37 | 11:41:32 | claude_call | board: greenhouse-verkada; posting_id: 5302618007; why: waited; valid: True; verdict: not_relevant; record: claude/03c68a07c5.json; calls_used: 14 |
| 38 | 11:41:34 | claude_call | board: greenhouse-verkada; posting_id: 5143763007; why: waited; valid: True; verdict: not_relevant; record: claude/5c5cbc37ce.json; calls_used: 15 |
| 39 | 11:41:37 | claude_call | board: greenhouse-verkada; posting_id: 5197606007; why: waited; valid: True; verdict: not_relevant; record: claude/251c9a6aad.json; calls_used: 16 |
| 40 | 11:41:42 | claude_call | board: greenhouse-verkada; posting_id: 5225570007; why: waited; valid: True; verdict: not_relevant; record: claude/b673ef2e9e.json; calls_used: 17 |
| 41 | 11:41:44 | claude_call | board: greenhouse-verkada; posting_id: 5297293007; why: waited; valid: True; verdict: not_relevant; record: claude/5723e043b2.json; calls_used: 18 |
| 42 | 11:41:46 | claude_call | board: lever-palantir; posting_id: ac978161-6f46-4f6b-ad9e-a258e642751c; why: waited; valid: True; verdict: not_relevant; record: claude/0580c315b0.json; calls_used: 19 |
| 43 | 11:41:49 | claude_call | board: lever-palantir; posting_id: 8f15d728-99cc-4003-9add-928bd72a7f30; why: waited; valid: True; verdict: not_relevant; record: claude/552b1608bb.json; calls_used: 20 |
| 44 | 11:41:49 | budget_stop | budget: claude_calls; why: the budget of 20 Claude calls was used up; waiting_for_claude: 12 |
| 45 | 11:41:49 | report | files: ["report.md", "report.json"]; exit: budget-exhausted; reasons: ["claude_calls budget: the budget of 20 Claude calls was used up (12 postings wait for Claude's judgment)", "ashby-openai unverified: job 482 has no title", ... |
| 46 | 11:41:49 | state_write | board: ashby-openai; path: state/ashby-openai.json; write: none; why: the board was unverified, so its state stays exactly as it was |
| 47 | 11:41:49 | state_write | board: greenhouse-verkada; path: state/greenhouse-verkada.json; write: append; seen_ids: 385; waiting_for_claude: 0 |
| 48 | 11:41:49 | state_write | board: lever-palantir; path: state/lever-palantir.json; write: append; seen_ids: 319; waiting_for_claude: 12 |
| 49 | 11:41:49 | state_write | board: greenhouse-no-such-board-js2-test; path: state/greenhouse-no-such-board-js2-test.json; write: none; why: the board was unverified, so its state stays exactly as it was |
| 50 | 11:41:49 | exit | status: budget-exhausted; code: 4; reasons: ["claude_calls budget: the budget of 20 Claude calls was used up (12 postings wait for Claude's judgment)", "ashby-openai unverified: job 482 has no title", ... |
