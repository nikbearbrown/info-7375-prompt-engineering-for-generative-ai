# Trace of run 2026-11-20T113915Z

| Step | Time (UTC) | Kind | What happened |
|---:|---|---|---|
| 1 | 11:39:15 | run_start | run_id: 2026-11-20T113915Z; source: live; gate_version: 1.0; contract_version: 0.2; budgets: {"boards": 5, "requests": 10, "claude_calls": 20, "seconds": 600}; resume: jane-doe.json; code_sha256: 6eebbe57c553a7898ef971828d67b5839e1e873c849c08b2c6b691b53baffc96; git_head: 1779827348dec1ada6d31043d41ba0daa89e1407; prompt: {"file": "baseline.txt", "sha256": "d616ca168220aafe6142bf01629832efbec5f6117007148d75fc290199e3712a", "model": "claude-sonnet-5-5"} |
| 2 | 11:39:15 | board_list | visiting: ["ashby-openai", "greenhouse-verkada", "lever-palantir", "greenhouse-no-such-board-js2-test"]; repeats: []; not_visited_boards_budget: []; deliberate_failure: ["greenhouse-no-such-board-js2-test"] |
| 3 | 11:39:15 | permission | board: ashby-openai; url: https://api.ashbyhq.com/posting-api/job-board/openai; allowed: True |
| 4 | 11:39:15 | request | board: ashby-openai; attempt: 1; retry: False; method: GET; url: https://api.ashbyhq.com/posting-api/job-board/openai; requests_used: 1 |
| 5 | 11:39:15 | answer | board: ashby-openai; attempt: 1; status: 200; bytes: 14343567; sha256: d595afc07e6388c74e510d380f637a28f71a64f29c05a599ec1a873941feb2e7; file: runs/2026-11-20T113915Z/boards/ashby-openai/attempt-1.json.gz; seconds: 0.54 |
| 6 | 11:39:15 | decision | board: ashby-openai; action: no retry; why: job 482 has no title; a retry cannot fix this answer (GATE.md, Error policy) |
| 7 | 11:39:15 | decision | board: ashby-openai; action: unverified; why: job 482 has no title. Its state stays as it was, nothing counts as new or gone, and it is escalated to you |
| 8 | 11:39:15 | permission | board: greenhouse-verkada; url: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true; allowed: True |
| 9 | 11:39:15 | request | board: greenhouse-verkada; attempt: 1; retry: False; method: GET; url: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true; requests_used: 2 |
| 10 | 11:39:16 | answer | board: greenhouse-verkada; attempt: 1; status: 200; bytes: 4157532; sha256: 1326899869f38b9bb6ea43bdd1b59c01cf9bc5de62649d9d558768827bbbf78a; file: runs/2026-11-20T113915Z/boards/greenhouse-verkada/attempt-1.json.gz; seconds: 0.41 |
| 11 | 11:39:16 | parse | board: greenhouse-verkada; postings: 348; mapped_from: greenhouse |
| 12 | 11:39:16 | diff | board: greenhouse-verkada; baseline: False; new: 38; gone: 32 |
| 13 | 11:39:16 | permission | board: lever-palantir; url: https://api.lever.co/v0/postings/palantir?mode=json; allowed: True |
| 14 | 11:39:16 | request | board: lever-palantir; attempt: 1; retry: False; method: GET; url: https://api.lever.co/v0/postings/palantir?mode=json; requests_used: 3 |
| 15 | 11:39:17 | answer | board: lever-palantir; attempt: 1; status: 200; bytes: 5954399; sha256: 95b992f2009e7050780c9b9d219f3aa906e682f3e9a193a2c29df7d2f9db4f64; file: runs/2026-11-20T113915Z/boards/lever-palantir/attempt-1.json.gz; seconds: 1.25 |
| 16 | 11:39:17 | parse | board: lever-palantir; postings: 307; mapped_from: lever |
| 17 | 11:39:17 | diff | board: lever-palantir; baseline: False; new: 14; gone: 11 |
| 18 | 11:39:17 | permission | board: greenhouse-no-such-board-js2-test; url: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true; allowed: True |
| 19 | 11:39:17 | request | board: greenhouse-no-such-board-js2-test; attempt: 1; retry: False; method: GET; url: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true; requests_used: 4 |
| 20 | 11:39:17 | answer | board: greenhouse-no-such-board-js2-test; attempt: 1; status: 404; bytes: 38; sha256: 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe; file: runs/2026-11-20T113915Z/boards/greenhouse-no-such-board-js2-test/attempt-1.json.gz; seconds: 0.09 |
| 21 | 11:39:17 | decision | board: greenhouse-no-such-board-js2-test; action: no retry; why: the board answered HTTP 404, not 200; a retry cannot fix this answer (GATE.md, Error policy) |
| 22 | 11:39:17 | decision | board: greenhouse-no-such-board-js2-test; action: unverified; why: the board answered HTTP 404, not 200. Its state stays as it was, nothing counts as new or gone, and it is escalated to you |
| 23 | 11:39:17 | judge_rule | postings: 52; relevant: 2 |
| 24 | 11:39:19 | claude_call | board: greenhouse-verkada; posting_id: 5291581007; why: new; valid: True; verdict: not_relevant; record: claude/6947c82328.json; calls_used: 1 |
| 25 | 11:39:22 | claude_call | board: greenhouse-verkada; posting_id: 4086589007; why: new; valid: True; verdict: not_relevant; record: claude/d8e6d3f8f4.json; calls_used: 2 |
| 26 | 11:39:26 | claude_call | board: greenhouse-verkada; posting_id: 5296748007; why: new; valid: True; verdict: relevant; record: claude/1a33044fde.json; calls_used: 3 |
| 27 | 11:39:29 | claude_call | board: greenhouse-verkada; posting_id: 5291606007; why: new; valid: True; verdict: not_relevant; record: claude/008193c27f.json; calls_used: 4 |
| 28 | 11:39:31 | claude_call | board: greenhouse-verkada; posting_id: 5106586007; why: new; valid: True; verdict: not_relevant; record: claude/e725ec8269.json; calls_used: 5 |
| 29 | 11:39:38 | claude_call | board: greenhouse-verkada; posting_id: 5106588007; why: new; valid: True; verdict: not_relevant; record: claude/5c2a181587.json; calls_used: 6 |
| 30 | 11:39:40 | claude_call | board: greenhouse-verkada; posting_id: 5279827007; why: new; valid: True; verdict: not_relevant; record: claude/430d361758.json; calls_used: 7 |
| 31 | 11:39:44 | claude_call | board: greenhouse-verkada; posting_id: 5302614007; why: new; valid: True; verdict: not_relevant; record: claude/d18cdf7bad.json; calls_used: 8 |
| 32 | 11:39:48 | claude_call | board: greenhouse-verkada; posting_id: 5302617007; why: new; valid: True; verdict: not_relevant; record: claude/f9b6370c18.json; calls_used: 9 |
| 33 | 11:39:49 | claude_call | board: greenhouse-verkada; posting_id: 5292769007; why: new; valid: True; verdict: not_relevant; record: claude/6f79e66ae0.json; calls_used: 10 |
| 34 | 11:39:56 | claude_call | board: greenhouse-verkada; posting_id: 5291075007; why: new; valid: True; verdict: not_relevant; record: claude/44634613ab.json; calls_used: 11 |
| 35 | 11:40:00 | claude_call | board: greenhouse-verkada; posting_id: 4140525007; why: new; valid: True; verdict: not_relevant; record: claude/c09aab35aa.json; calls_used: 12 |
| 36 | 11:40:02 | claude_call | board: greenhouse-verkada; posting_id: 5297849007; why: new; valid: True; verdict: not_relevant; record: claude/cd3dc7dd94.json; calls_used: 13 |
| 37 | 11:40:06 | claude_call | board: greenhouse-verkada; posting_id: 5300387007; why: new; valid: True; verdict: not_relevant; record: claude/a668973030.json; calls_used: 14 |
| 38 | 11:40:12 | claude_call | board: greenhouse-verkada; posting_id: 5293022007; why: new; valid: True; verdict: not_relevant; record: claude/c46003bf40.json; calls_used: 15 |
| 39 | 11:40:15 | claude_call | board: greenhouse-verkada; posting_id: 5294009007; why: new; valid: True; verdict: not_relevant; record: claude/9830a8ce39.json; calls_used: 16 |
| 40 | 11:40:22 | claude_call | board: greenhouse-verkada; posting_id: 5101666007; why: new; valid: True; verdict: relevant; record: claude/a54de0bb1a.json; calls_used: 17 |
| 41 | 11:40:24 | claude_call | board: greenhouse-verkada; posting_id: 5293617007; why: new; valid: True; verdict: not_relevant; record: claude/c1d0a3567c.json; calls_used: 18 |
| 42 | 11:40:27 | claude_call | board: greenhouse-verkada; posting_id: 5222017007; why: new; valid: True; verdict: not_relevant; record: claude/ee44fae818.json; calls_used: 19 |
| 43 | 11:40:30 | claude_call | board: greenhouse-verkada; posting_id: 5291572007; why: new; valid: True; verdict: not_relevant; record: claude/0e02258c7e.json; calls_used: 20 |
| 44 | 11:40:30 | budget_stop | budget: claude_calls; why: the budget of 20 Claude calls was used up; waiting_for_claude: 32 |
| 45 | 11:40:30 | report | files: ["report.md", "report.json"]; exit: budget-exhausted; reasons: ["claude_calls budget: the budget of 20 Claude calls was used up (32 postings wait for Claude's judgment)", "ashby-openai unverified: job 482 has no title", ... |
| 46 | 11:40:30 | state_write | board: ashby-openai; path: state/ashby-openai.json; write: none; why: the board was unverified, so its state stays exactly as it was |
| 47 | 11:40:30 | state_write | board: greenhouse-verkada; path: state/greenhouse-verkada.json; write: append; seen_ids: 385; waiting_for_claude: 18 |
| 48 | 11:40:30 | state_write | board: lever-palantir; path: state/lever-palantir.json; write: append; seen_ids: 319; waiting_for_claude: 14 |
| 49 | 11:40:30 | state_write | board: greenhouse-no-such-board-js2-test; path: state/greenhouse-no-such-board-js2-test.json; write: none; why: the board was unverified, so its state stays exactly as it was |
| 50 | 11:40:30 | exit | status: budget-exhausted; code: 4; reasons: ["claude_calls budget: the budget of 20 Claude calls was used up (32 postings wait for Claude's judgment)", "ashby-openai unverified: job 482 has no title", ... |
