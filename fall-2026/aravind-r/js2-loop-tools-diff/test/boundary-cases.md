# test/boundary-cases.md — DRAFT proposed by Claude Code, 2026-11-10

> Claude drafted this. Check each prediction yourself, change any you disagree with, and commit
> it as `js2-loop-tools-diff/test/boundary-cases.md` **before** the tests run. The prediction
> column has to exist before the result column does.

Each row is one call to `src/policy.mjs`. Decisions: `allow`, `deny`, `ask` (needs my approval; the loop treats `ask` as refused).

| # | kind | request | predicted | reason (GATE.md) | result (fill after running) |
|---|---|---|---|---|---|
| 1 | net | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | allow | on the allow-list | |
| 2 | net | GET `https://api.lever.co/v0/postings/spotify?mode=json` | allow | on the allow-list | |
| 3 | net | GET `https://example.com/jobs` | deny | host off the list | |
| 4 | net | GET `https://boards-api.greenhouse.io.evil.example/v1/boards/stripe/jobs` | deny | suffix trick; exact host match only | |
| 5 | net | GET `http://boards-api.greenhouse.io/v1/boards/stripe/jobs` | deny | not HTTPS | |
| 6 | net | POST `https://api.lever.co/v0/postings/spotify/<id>/apply` | deny | not GET; apply is never allowed | |
| 7 | net | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs/123/questions` | deny | path not on the list | |
| 8 | net | allow-listed GET that answers 301 → `https://evil.example/` | deny | redirects refused | |
| 9 | net | GET `https://user:pw@api.lever.co/v0/postings/spotify` | deny | credentials in URL = login | |
| 10 | write | `out/traces/run.json` | allow | inside `out/` | |
| 11 | write | `out/../boards.json` | deny | `..` resolves outside `out/` | |
| 12 | write | `out-evil/x.json` (sibling of `out/`) | deny | prefix trick | |
| 13 | write | `out/link/x.json`, where `out/link` → `/tmp` | deny | symlink resolves outside `out/` | |
| 14 | read | `boards.json` | allow | read inside the project | |
| 15 | write | `boards.json` | deny | same file, write: outside `out/` | |
| 16 | read | `~/.ssh/id_ed25519` | deny | read outside the project | |
| 17 | write | delete `out/state/gh-stripe.json` | ask | deleting under `out/` needs approval | |
| 18 | write | overwrite `out/state/gh-stripe.json` with fewer ids than it holds | ask | state shrink needs approval | |
| 19 | net | `mailto:recruiter@example.com` | deny | never email | |
