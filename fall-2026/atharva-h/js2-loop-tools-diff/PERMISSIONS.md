# Permission policy and boundary tests

The policy is in [GATE.md](GATE.md) and is enforced in `policy.py`. Every network request, read, write, and delete goes through it, and anything it refuses stops a run with `error`.

## Boundary cases

The **Predicted** column was written on 2026-11-09 from `GATE.md`, before any test or policy code existed. The **Actual** column is filled in from the test run, and each case is a test in `tests/test_policy.py` named after its id.

| Id | Action | Predicted | Actual |
|---|---|---|---|
| P1 | GET `https://boards-api.greenhouse.io/v1/boards/abacusinsights/jobs` | allowed | allowed, as predicted (`test_P1_…` passed 2026-11-09) |
| P2 | GET `https://example.com/jobs` | refused: host not on the allow-list | refused, as predicted (`test_P2_…` passed 2026-11-09) |
| P3 | GET `http://boards-api.greenhouse.io/v1/boards/abacusinsights/jobs` | refused: not HTTPS | refused, as predicted (`test_P3_…` passed 2026-11-09) |
| P4 | GET `https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs` | refused: host not on the allow-list (suffix trick) | refused, as predicted (`test_P4_…` passed 2026-11-09) |
| P5 | POST `https://api.lever.co/v0/postings/xsolla` | refused: only GET | refused, as predicted (`test_P5_…` passed 2026-11-09) |
| P6 | GET an allowed URL with a `Cookie` header | refused: no cookies | refused, as predicted (`test_P6_…` passed 2026-11-09) |
| P7 | GET an allowed URL with an `Authorization` header | refused: no auth | refused, as predicted (`test_P7_…` passed 2026-11-09) |
| P8 | A redirect from `api.lever.co` to `https://example.com/` | refused: redirect target not on the allow-list | refused, as predicted (`test_P8_…` passed 2026-11-09) |
| P9 | GET `https://user:pw@api.lever.co/v0/postings/xsolla` | refused: credentials in the URL | refused, as predicted (`test_P9_…` passed 2026-11-09) |
| P10 | Write `runs/<new run>/trace.jsonl` | allowed | allowed, as predicted (`test_P10_…` passed 2026-11-09) |
| P11 | Write `runs/../GATE.md` | refused: `..` escapes `runs/` | refused, as predicted (`test_P11_…` passed 2026-11-09) |
| P12 | Write `runs-evil/x.json`, a sibling of `runs/` | refused: shared prefix, outside `runs/` | refused, as predicted (`test_P12_…` passed 2026-11-09) |
| P13 | Write `runs/link/x.json`, where `runs/link` is a symlink to a folder outside | refused: the symlink escapes | refused, as predicted (`test_P13_…` passed 2026-11-09) |
| P14 | Read `config/boards.json` | allowed | allowed, as predicted (`test_P14_…` passed 2026-11-09) |
| P15 | Write `config/boards.json` | refused: readable is not writable | refused, as predicted (`test_P15_…` passed 2026-11-09) |
| P16 | Read `../js1-contract-and-watch/CONTRACT.md` | refused: outside this folder | refused, as predicted (`test_P16_…` passed 2026-11-09) |
| P17 | Create a run folder that already exists | refused: no overwrite | refused, as predicted (`test_P17_…` passed 2026-11-09) |
| P18 | Write state that drops a seen id, with no terminal | refused: needs approval, and the answer is no | refused, as predicted (`test_P18_…` passed 2026-11-09) |
| P19 | Write state that drops a seen id, approver answers yes | allowed | allowed, as predicted (`test_P19_…` passed 2026-11-09) |
| P20 | Write 6 MB into `runs/`, with no terminal | refused: over 5 MB needs approval | refused, as predicted (`test_P20_…` passed 2026-11-09) |
| P21 | Run with a board list that differs from the last run's, with no terminal | refused: needs approval | refused, as predicted (`test_P21_…` passed 2026-11-09) |
| P22 | Delete a run folder, with no terminal | refused: needs approval | refused, as predicted (`test_P22_…` passed 2026-11-09) |
| P23 | Delete a run folder, approver answers yes | allowed | allowed, as predicted (`test_P23_…` passed 2026-11-09) |
