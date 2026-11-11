# Boundary Test Predictions — Sreevarshan Sathiyamurthy, 2026-11-06
Written before running any boundary test.

| # | Input | Expected result | Policy rule |
|---|---|---|---|
| 1 | allow_request("http://boards-api.greenhouse.io/...") | blocked — scheme is http, not https | GATE §6: https only |
| 2 | allow_request("https://evil.com/jobs") | blocked — host not in allow-list | GATE §6: allowed hosts only |
| 3 | allow_request("https://boards-api.greenhouse.io.evil.com/...") | blocked — host is greenhouse.io.evil.com, not greenhouse.io | GATE §6: exact host match |
| 4 | allow_write("/Users/sreevarshansathiyamurthy/eng_job 2/output/raw/file.json") | allowed — inside output folder | GATE §6: writes inside output/ |
| 5 | allow_write("/Users/sreevarshansathiyamurthy/eng_job 2/output/../../../etc/passwd") | blocked — resolves outside output/ via .. | GATE §6: .. escape blocked |
| 6 | allow_write("/Users/sreevarshansathiyamurthy/output-evil/file.json") | blocked — sibling folder named output-evil | GATE §6: prefix trick blocked |
| 7 | allow_write(symlink inside output/ pointing to /tmp/outside.json) | blocked — symlink target is outside output/ | GATE §6: symlinks blocked |
| 8 | allow_write(existing file output/raw/live-run.json) | needs_approval — overwriting existing evidence | GATE §6: overwrite needs approval |
| 9 | allow_write("/Users/sreevarshansathiyamurthy/eng_job 2/output/raw/newfile.json") — file does not exist | allowed — new file inside output/ | GATE §6: new writes allowed |
| 10 | allow_request("https://api.lever.co/v0/postings/spotify?mode=json") | allowed — Lever is on the allow-list | GATE §6: allowed hosts |
| 11 | allow_write("/Users/sreevarshansathiyamurthy/Downloads/Eng_job/output/file.json") | blocked — JS1 folder is outside output/ | GATE §6: JS1 must not be modified |
| 12 | allow_request("ftp://boards-api.greenhouse.io/...") | blocked — ftp scheme not allowed | GATE §6: https only |

## Results — run by me in Terminal, 2026-11-06

| # | Actual result | Match |
|---|---|---|
| 1 | False | ✓ |
| 2 | False | ✓ |
| 3 | False | ✓ |
| 4 | True | ✓ |
| 5 | False | ✓ |
| 6 | False | ✓ |
| 7 | False | ✓ |
| 8 | needs_approval | ✓ |
| 9 | True | ✓ |
| 10 | True | ✓ |
| 11 | False | ✓ |
| 12 | False | ✓ |

All 12 cases matched their predictions.
