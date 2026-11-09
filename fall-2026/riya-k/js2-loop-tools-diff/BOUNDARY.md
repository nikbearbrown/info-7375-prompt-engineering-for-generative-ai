# Boundary tests — predictions first

Written 2026-11-09, **before `jsagent/policy.py` existed and before any of these tests ran.**
Each prediction follows from the permission policy in GATE.md. Claude Code drafted the rows from GATE.md.
I reviewed them in chat on 2026-11-09 before the code was written. I asked whether so many "refuse" rows were right;
I kept them because the allow rows (B1, B8, B13 read, B15, B17) show a policy that refuses everything would fail. The "Observed" column is filled in only after running
`python3 -m unittest tests.test_policy -v`; a mismatch is recorded, not edited away.

In the tests, the output folder is a temp `runs/` with a sibling `runs-evil/` beside it, so the prefix trick is real.

| # | Request | Kind | Predicted | Why (GATE.md) | Observed |
|---|---|---|---|---|---|
| B1 | GET `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` | network | **allow** | host on allow-list, https, GET | |
| B2 | GET `https://evil.example.com/jobs` | network | **refuse** (host) | host off the allow-list | |
| B3 | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs` | network | **refuse** (host) | look-alike host; a substring check would wrongly pass it (wrong version 7) | |
| B4 | GET `http://boards-api.greenhouse.io/v1/boards/x/jobs` | network | **refuse** (scheme) | https only | |
| B5 | POST `https://api.ashbyhq.com/posting-api/job-board/notion` | network | **refuse** (method) | GET only; a POST is how an agent would apply or send something | |
| B6 | GET `https://api.lever.co/v0/postings/x` | network | **refuse** (host) | a real job board, but not on my list | |
| B7 | GET `https://me:pw@boards-api.greenhouse.io/v1/boards/x/jobs` | network | **refuse** (credentials) | credentials in a URL = logging in, never allowed | |
| B8 | write `runs/raw/x.json` | write | **allow** | inside the output folder | |
| B9 | write `runs/../GATE.md` | write | **refuse** (escape) | `..` resolves outside `runs/` | |
| B10 | write `runs-evil/x.json` | write | **refuse** (escape) | sibling folder that starts with "runs"; a prefix check would wrongly pass it (wrong version 6) | |
| B11 | write `runs/link/x.json`, where `runs/link` is a symlink to a folder outside | write | **refuse** (escape) | the resolved real path is outside `runs/` (wrong version 8) | |
| B12 | write an absolute path outside, e.g. `<tmp>/elsewhere/x.json` | write | **refuse** (escape) | not inside `runs/` | |
| B13 | **read** `persona/arya-sahni.json`, then **write** the same path | read vs write | read **allow**, write **refuse** | reading is allowed; read permission never implies write | |
| B14 | **read** a file outside the agent folder (e.g. `~/.ssh/id_rsa`) | read | **refuse** (read) | reads are limited to config, persona, own state and fixtures | |
| B15 | state write that only **adds** ids | write | **allow**, no approval needed | normal runs only add ids | |
| B16 | state write that **removes** ids, without `--approve` | write needing approval | **refuse**, file unchanged | removing ids needs my approval | |
| B17 | the same write as B16, **with** `--approve` | write needing approval | **allow**, and the approval is recorded in the trace | approval given | |

Every refusal must happen **before** any connection is opened or any byte is written, and must name its reason.
