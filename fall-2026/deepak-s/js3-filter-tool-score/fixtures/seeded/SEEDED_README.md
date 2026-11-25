# fixtures/seeded/: SEEDED test fixtures

Every file here is SEEDED: constructed by Claude Code (Claude Opus 5.5) on 2026-11-10 for the offline tests in tests/js2/. None is a captured response. The field names follow the real bodies in evidence/manual-capture/20261110T184001Z/ (Greenhouse `jobs[].{id,title,location.name,absolute_url}`, Lever top-level list of `{id,text,categories.location,hostedUrl}`, Ashby `jobs[].{id,title,location,jobUrl}`). The ids, titles and URLs are made up.

| File | Stands for |
|---|---|
| SEEDED_greenhouse_two_jobs.json | a Greenhouse board with 2 postings |
| SEEDED_greenhouse_three_jobs.json | the same board one run later, with 1 new posting (9000003) |
| SEEDED_greenhouse_404.json | a bad board token; same body as the captured 404 in CAPTURE.md row 02 |
| SEEDED_lever_six.json | a Lever board with 6 postings |
| SEEDED_lever_empty.json | a Lever 200 with `[]` (the finished-wrong-answer shape) |
| SEEDED_lever_html_200.html | a 200 whose body is HTML (GATE.md section 4, W10); no such response was captured |
| SEEDED_ashby_two_jobs.json | an Ashby board with 2 postings |
| SEEDED_wrong_shape.json | valid JSON with no postings array where expected |

Transport-level cases (302, 429, 5xx, timeouts) are built in the tests by the SEEDED fake transport in tests/js2/js2kit.py, not stored as files.
