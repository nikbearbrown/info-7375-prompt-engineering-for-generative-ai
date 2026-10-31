# Why the board changed from Databricks to Stripe (contract v1 → v2)

Everything here was produced on 2026-10-31 by the code in this folder. Nothing is constructed.

| File | What it is |
|---|---|
| `raw/2026-10-31T10-42-37Z/board.json` | Live baseline run under contract v1 (`python -m agent run --mode live`, 06:42 ET). 901 postings. Same sha256 (`f2c0e004…`) as `evidence/snapshot-morning/` from 05:50 ET. |
| `state/state.json` | That run's state: 901 `seen_ids`, baseline complete. Moved here so the Stripe watch starts from its own baseline. |
| `label-selection/` | Output of `python -m agent select-labels --board raw/2026-10-31T10-42-37Z/board.json`: the seed-42 selection of 20 postings (ids and titles only, no verdicts). |

## The base-rate check (CONTRACT.md, Hand-label set)

```text
901 postings, 4 pass title+seniority; selected 20 (4 from candidates, 16 from the rest); dev 10, held_out 10
base-rate check: 0 of 20 are rule-relevant (count only, by design)
```

That is fewer than 3, so the contract requires a slug change, recorded as v2.

## Choosing the new slug

`tools/base_rate_scan.py` ran the same count-only check on 35 public Greenhouse boards, all on
`boards-api.greenhouse.io` (responses not saved). It used a generic cut at "benefits", so the counts are rough. Output, 2026-10-31 ~06:47 ET:

```text
stripe           postings  746  title+seniority  11  location-ok  247  base-rate (rule-relevant of the 20) 3
datadog          postings  397  title+seniority   3  location-ok  192  base-rate (rule-relevant of the 20) 0
airbnb           postings  202  title+seniority   2  location-ok   32  base-rate (rule-relevant of the 20) 0
lyft             postings  170  title+seniority  14  location-ok   66  base-rate (rule-relevant of the 20) 1
pinterest        postings  170  title+seniority  13  location-ok  120  base-rate (rule-relevant of the 20) 0
figma            postings  140  title+seniority   6  location-ok   94  base-rate (rule-relevant of the 20) 1
discord          postings   41  title+seniority   1  location-ok   36  base-rate (rule-relevant of the 20) 1
reddit           postings  163  title+seniority   3  location-ok  128  base-rate (rule-relevant of the 20) 1
dropbox          postings   24  title+seniority   0  location-ok    9  base-rate (rule-relevant of the 20) 0
instacart        postings   96  title+seniority   0  location-ok   60  base-rate (rule-relevant of the 20) 0
coinbase         postings  250  title+seniority   5  location-ok  174  base-rate (rule-relevant of the 20) 1
brex             postings  263  title+seniority   4  location-ok  184  base-rate (rule-relevant of the 20) 1
robinhood        postings  160  title+seniority   2  location-ok   71  base-rate (rule-relevant of the 20) 1
samsara          postings  325  title+seniority  15  location-ok  125  base-rate (rule-relevant of the 20) 3
anthropic        postings  675  title+seniority  22  location-ok  518  base-rate (rule-relevant of the 20) 0
affirm           postings  245  title+seniority   4  location-ok  108  base-rate (rule-relevant of the 20) 1
chime            postings   75  title+seniority   1  location-ok   71  base-rate (rule-relevant of the 20) 1
gusto            postings   84  title+seniority   1  location-ok   69  base-rate (rule-relevant of the 20) 0
asana            postings  110  title+seniority   4  location-ok   37  base-rate (rule-relevant of the 20) 0
twilio           postings  132  title+seniority   1  location-ok   57  base-rate (rule-relevant of the 20) 0
cloudflare       postings  464  title+seniority   3  location-ok    2  base-rate (rule-relevant of the 20) 0
gitlab           postings  238  title+seniority   4  location-ok  121  base-rate (rule-relevant of the 20) 1
okta             postings  388  title+seniority   2  location-ok  106  base-rate (rule-relevant of the 20) 0
mongodb          postings  366  title+seniority   2  location-ok   62  base-rate (rule-relevant of the 20) 0
elastic          postings  407  title+seniority   3  location-ok   10  base-rate (rule-relevant of the 20) 0
duolingo         postings   57  title+seniority   3  location-ok   37  base-rate (rule-relevant of the 20) 2
plaid            error HTTPError
flexport         postings  193  title+seniority   0  location-ok   29  base-rate (rule-relevant of the 20) 0
klaviyo          postings  156  title+seniority   0  location-ok  107  base-rate (rule-relevant of the 20) 0
toast            postings  328  title+seniority   1  location-ok   71  base-rate (rule-relevant of the 20) 1
scaleai          postings  170  title+seniority  15  location-ok   84  base-rate (rule-relevant of the 20) 3
airtable         only 5 postings
grammarly        error HTTPError
squarespace      postings   27  title+seniority   0  location-ok   21  base-rate (rule-relevant of the 20) 0
peloton          postings   58  title+seniority   2  location-ok   16  base-rate (rule-relevant of the 20) 0
```

With board-specific cut headings, Stripe, Samsara and Scale AI each stayed at 3 of 20. Siddi chose Stripe because it is the largest board, and so the most likely to change before the second live run.

A check of Stripe's live board with the v2 Appendix C, run before v2 was committed:

```text
746 postings | heading in-office expectations as a block element: 6 | blurb phrase in a sentence: 668 | empty requirements: 0
base-rate with v2 config: title+seniority 11, rule-relevant of the 20: 3
```

The base-rate check that counts is the one on the Stripe baseline run's own board; see the README.
