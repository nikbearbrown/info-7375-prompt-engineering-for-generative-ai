# Blind reject audit — how to fill it in

Kit built by `python -m audit.make_kit --seed 20261124` from FILTER.md v1's run over the 182 unique postings saved by my JS2 loop (`out3/filter-run/`, commit 8e759bf). Seed: **20261124**.

## My audit rule (from AUDIT-RULE.md, committed before this sample was drawn)

My audit judgment is not the filter re-applied. For each sampled posting I answer: would I want Priya to see this? Yes if it is an individual-contributor data, analytics or machine-learning role, based in the US or US-remote, whose work uses skills on her résumé, judged from the whole posting as a person would read it, not from keywords. I judge before seeing the filter's reason.

## What is in the kit

| Group | Count | How it was drawn |
| --- | ---: | --- |
| reject | 30 | uniform random sample of all 166 rejected postings |
| close | 5 | rejected postings, not in the 30, that fail exactly one of F1–F4 checked independently; preferring only-F4 (0 skills), then only-F2, then only-F1 with a borderline title word, then only-F3 |
| accept | 10 | random sample of the 16 accepted postings |

The 45 rows of `audit.csv` are shuffled. The group is shown; the filter's reason, failing rule and close-call tier are not.

## Steps

1. Do **not** open `out3/filter-run/results.json` or `shortlist.md` until every row is judged: they contain the filter's reasons.
2. For each row of `audit.csv`, read `postings/<posting_id with : replaced by _>.txt` in full (title, location, text with HTML removed; line breaks kept for reading).
3. Fill `my_relevant` with `yes` or `no` by the rule above, and `my_note` with the sentence in the posting that decided it.
4. Commit the filled `audit.csv` before comparing with the filter's reasons.
5. Then compare: a reject I mark `yes` is a filter miss; an accept I mark `no` is a false accept. From 30 random rejects, report the count and what a sample of 30 can and cannot show about the 166.
