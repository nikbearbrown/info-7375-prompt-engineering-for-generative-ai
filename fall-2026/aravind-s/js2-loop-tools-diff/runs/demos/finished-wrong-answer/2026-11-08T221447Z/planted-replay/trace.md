# Trace of run 2026-11-08T222025Z

| Step | Time (UTC) | Kind | What happened |
|---:|---|---|---|
| 1 | 22:20:25 | run_start | run_id: 2026-11-08T222025Z; source: replay of the saved answers in runs/source/2026-11-08T221447Z, not a live run; gate_version: 1.0; contract_version: 0.1; budgets: {"boards": 5, "requests": 10, "claude_calls": 20, "seconds": 600}; resume: jane-doe.json; code_sha256: 7699424a9b1986910fbffdceed950f72f28efc0a9d3970e42c1f932da3f372eb; git_head: None; prompt: {"file": "baseline.txt", "sha256": "d616ca168220aafe6142bf01629832efbec5f6117007148d75fc290199e3712a", "model": "claude-sonnet-5-5"} |
| 2 | 22:20:25 | board_list | visiting: ["ashby-openai", "greenhouse-verkada", "lever-palantir", "greenhouse-no-such-board-js2-test"]; repeats: []; not_visited_boards_budget: []; deliberate_failure: ["greenhouse-no-such-board-js2-test"] |
| 3 | 22:20:25 | permission | board: ashby-openai; url: https://api.ashbyhq.com/posting-api/job-board/openai; allowed: True |
| 4 | 22:20:25 | request | board: ashby-openai; attempt: 1; retry: False; method: GET; url: https://api.ashbyhq.com/posting-api/job-board/openai; requests_used: 1 |
| 5 | 22:20:25 | answer | board: ashby-openai; attempt: 1; status: 200; bytes: 13641063; sha256: 7aff4139e7e97306874e8b0cf659a2e4ad9ca5703261dda5c7885154c3e62d04; file: runs/replay/2026-11-08T222025Z/boards/ashby-openai/attempt-1.json.gz; seconds: 0.13 |
| 6 | 22:20:25 | parse | board: ashby-openai; postings: 816; mapped_from: ashby |
| 7 | 22:20:25 | diff | board: ashby-openai; baseline: True; new: 0; gone: 0 |
| 8 | 22:20:25 | permission | board: greenhouse-verkada; url: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true; allowed: True |
| 9 | 22:20:25 | request | board: greenhouse-verkada; attempt: 1; retry: False; method: GET; url: https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true; requests_used: 2 |
| 10 | 22:20:25 | answer | board: greenhouse-verkada; attempt: 1; status: 200; bytes: 4091423; sha256: c2ad7305148deb4aa9f09787c5a43c48e0f9978ae5e5805179a97d560f855127; file: runs/replay/2026-11-08T222025Z/boards/greenhouse-verkada/attempt-1.json.gz; seconds: 0.04 |
| 11 | 22:20:26 | parse | board: greenhouse-verkada; postings: 343; mapped_from: greenhouse |
| 12 | 22:20:26 | diff | board: greenhouse-verkada; baseline: True; new: 0; gone: 0 |
| 13 | 22:20:26 | permission | board: lever-palantir; url: https://api.lever.co/v0/postings/palantir?mode=json; allowed: True |
| 14 | 22:20:26 | request | board: lever-palantir; attempt: 1; retry: False; method: GET; url: https://api.lever.co/v0/postings/palantir?mode=json; requests_used: 3 |
| 15 | 22:20:26 | answer | board: lever-palantir; attempt: 1; status: 200; bytes: 5942874; sha256: 8ce0bf74addf9535ad893e502af565854d1d01450ae81712ea94f1db4b052ca9; file: runs/replay/2026-11-08T222025Z/boards/lever-palantir/attempt-1.json.gz; seconds: 0.03 |
| 16 | 22:20:26 | parse | board: lever-palantir; postings: 305; mapped_from: lever |
| 17 | 22:20:26 | diff | board: lever-palantir; baseline: True; new: 0; gone: 0 |
| 18 | 22:20:26 | permission | board: greenhouse-no-such-board-js2-test; url: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true; allowed: True |
| 19 | 22:20:26 | request | board: greenhouse-no-such-board-js2-test; attempt: 1; retry: False; method: GET; url: https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true; requests_used: 4 |
| 20 | 22:20:26 | answer | board: greenhouse-no-such-board-js2-test; attempt: 1; status: 404; bytes: 38; sha256: 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe; file: runs/replay/2026-11-08T222025Z/boards/greenhouse-no-such-board-js2-test/attempt-1.json.gz; seconds: 0.0 |
| 21 | 22:20:26 | parse | board: greenhouse-no-such-board-js2-test; postings: 0; mapped_from: greenhouse |
| 22 | 22:20:26 | diff | board: greenhouse-no-such-board-js2-test; baseline: True; new: 0; gone: 0 |
| 23 | 22:20:26 | report | files: ["report.md", "report.json"]; exit: finished; reasons: [] |
| 24 | 22:20:26 | state_write | board: ashby-openai; path: state/replay/ashby-openai.json; write: first; seen_ids: 816; waiting_for_claude: 0 |
| 25 | 22:20:26 | state_write | board: greenhouse-verkada; path: state/replay/greenhouse-verkada.json; write: first; seen_ids: 343; waiting_for_claude: 0 |
| 26 | 22:20:26 | state_write | board: lever-palantir; path: state/replay/lever-palantir.json; write: first; seen_ids: 305; waiting_for_claude: 0 |
| 27 | 22:20:26 | state_write | board: greenhouse-no-such-board-js2-test; path: state/replay/greenhouse-no-such-board-js2-test.json; write: first; seen_ids: 0; waiting_for_claude: 0 |
| 28 | 22:20:26 | exit | status: finished; code: 0; reasons: [] |
