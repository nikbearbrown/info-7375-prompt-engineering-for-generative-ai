# Permission policy and boundary tests

The policy is in [GATE.md](GATE.md) and is enforced in `policy.py`. Every network request, read, write, and delete goes through it, and anything it refuses stops a run with `error`.

## Boundary cases

The **Predicted** column was written on 2026-11-09 from `GATE.md`, before any test or policy code existed. The **Actual** column is filled in from the test run, and each case is a test in `tests/test_policy.py` named after its id.

| Id | Action | Predicted | Actual |
|---|---|---|---|
| P1 | GET `https://boards-api.greenhouse.io/v1/boards/abacusinsights/jobs` | allowed | |
| P2 | GET `https://example.com/jobs` | refused: host not on the allow-list | |
| P3 | GET `http://boards-api.greenhouse.io/v1/boards/abacusinsights/jobs` | refused: not HTTPS | |
| P4 | GET `https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs` | refused: host not on the allow-list (suffix trick) | |
| P5 | POST `https://api.lever.co/v0/postings/xsolla` | refused: only GET | |
| P6 | GET an allowed URL with a `Cookie` header | refused: no cookies | |
| P7 | GET an allowed URL with an `Authorization` header | refused: no auth | |
| P8 | A redirect from `api.lever.co` to `https://example.com/` | refused: redirect target not on the allow-list | |
| P9 | GET `https://user:pw@api.lever.co/v0/postings/xsolla` | refused: credentials in the URL | |
| P10 | Write `runs/<new run>/trace.jsonl` | allowed | |
| P11 | Write `runs/../GATE.md` | refused: `..` escapes `runs/` | |
| P12 | Write `runs-evil/x.json`, a sibling of `runs/` | refused: shared prefix, outside `runs/` | |
| P13 | Write `runs/link/x.json`, where `runs/link` is a symlink to a folder outside | refused: the symlink escapes | |
| P14 | Read `config/boards.json` | allowed | |
| P15 | Write `config/boards.json` | refused: readable is not writable | |
| P16 | Read `../js1-contract-and-watch/CONTRACT.md` | refused: outside this folder | |
| P17 | Create a run folder that already exists | refused: no overwrite | |
| P18 | Write state that drops a seen id, with no terminal | refused: needs approval, and the answer is no | |
| P19 | Write state that drops a seen id, approver answers yes | allowed | |
| P20 | Write 6 MB into `runs/`, with no terminal | refused: over 5 MB needs approval | |
| P21 | Run with a board list that differs from the last run's, with no terminal | refused: needs approval | |
| P22 | Delete a run folder, with no terminal | refused: needs approval | |
| P23 | Delete a run folder, approver answers yes | allowed | |
