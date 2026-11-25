# Layer 2 test fixtures

Excerpts of real public board answers, used to test how each system's answer is read (GATE.md, "Postings from three systems"). Whole postings were left out; nothing inside a posting that was kept was changed.

| File | Source | What it keeps |
|---|---|---|
| `greenhouse-verkada-excerpt.json` | `GET https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true`, 2026-11-06 | 4 of 346 jobs: a 2027 new-grad backend role (San Mateo), a London role, an intern role ("Intern/Co-op") and a New York City role. Its `meta.total` still says 346. |
| `lever-palantir-excerpt.json` | `GET https://api.lever.co/v0/postings/palantir?mode=json`, 2026-11-06 | 5 of 305 postings: a New York software role, a US-government new-grad role, an internship in Paris, a London role, and the board's only remote posting. They carry Palantir's public accommodations address. |
| `ashby-openai-excerpt.json` | `runs/2026-10-31T231042Z/response.json` (layer 1's run 2) | 2 of 810 jobs. |
| `greenhouse-404.json`, `lever-404.json`, `ashby-404.txt` | the same three systems asked for the made-up board `no-such-board-js2-test`, 2026-11-06 | each system's whole HTTP 404 answer |

The one-off fetches of 2026-11-06 were made with curl while choosing the boards, before the agent's layer 2 existed; they are test inputs, not run evidence.
