# Job watch — exit: **incomplete**

> Not a clean finish: one or more boards failed or were skipped.

> `finished` means every board was fetched and parsed. It does not mean the answer is right: run `python3 check_run.py <run_dir>` for the independent check.

Budget used: {'boards': 7, 'requests': 7, 'seconds': 3.875} of {'boards': 10, 'requests': 15, 'seconds': 120}

| board | status | HTTP | attempts | fetched | new | relevant (rule) | reason |
|---|---|---|---|---|---|---|---|
| greenhouse/stripe | ok | 200 | 1 | 771 | 0 | 0 |  |
| greenhouse/anthropic | ok | 200 | 1 | 676 | 0 | 0 |  |
| ashby/openai | ok | 200 | 1 | 811 | 0 | 0 |  |
| ashby/notion | ok | 200 | 1 | 153 | 0 | 0 |  |
| lever/palantir | ok | 200 | 1 | 304 | 0 | 0 |  |
| greenhouse/stripe-js2-bad | failed | 404 | 1 | — | — | — | HTTP 404 |
| greenhouse/ramp | ok | 200 | 1 | 1 | 0 | 0 |  |

