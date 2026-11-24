# FRICTIONAL — Final Project Film

Yudan Zhou (@yudanzhou) · INFO 7375 · 2026-11-23

An honest log of making this film. Everything below happened today. Where a claim
was wrong, it says who found it and what replaced it.

## How I worked

I wrote the film with two Claude sessions running separately: one drafting the
beat sheet, one reviewing it. They disagreed several times, and in two of those
cases both were partly wrong. I passed each session's findings to the other and made the
final call on each disputed claim. The entries below are those decisions.

## What I tried, what happened, what I did

| # | What happened | What I checked or changed | Where it shows |
|---|---|---|---|
| 1 | My first beat sheet said Jobright "gives each job a match score from zero to one hundred" | Neither session could find a 0–100 scale on any of Jobright's three relevant pages. Their own blog says of a percentage example, "The score is illustrative, not a Jobright result." **Deleted the scale from B04.** | B04 |
| 2 | The reviewing session proposed quoting Jobright's "do not assume the tool knows an employer's private evaluation criteria". The drafting session checked two product pages, did not find it, and called it unverified | Both were partly right. The sentence **is** on jobright.ai's blog page, verbatim. The phrase "a decision aid—not a guarantee" is **not** there — it is in the FAQ of the AI Job Matcher page. Two sources, two different pages, each session had checked only one. **B04 now quotes the decision-aid line**, which is the one that sits on Jobright's own product page | B04 |
| 3 | The reviewing session suggested naming F1 Hire, a browser extension that joins H-1B history to live postings, as the nearest competitor. The source was a university career-services page | f1hire.com now shows only a closing notice. But the product was renamed, not shut down: Binghamton's career page is titled "FrogHire.ai (formerly F1Hire)", and the Chrome Web Store listing is the **same extension ID** under both names. The university page the reviewing session started from was stale. **Lesson: check the product, not a list that mentions it** | not in the film — see #4 |
| 4 | Even with the name fixed, the line the reviewing session wanted to draw was "a rating scores every posting, including ones with no record; mine does not" | That property belongs to my **Mode Build** triage tool, which joins funding and H-1B approval records and holds blanks out. **This agent queries no sponsorship database at all** — rule R6 reads the posting text for whether sponsorship is ruled out. Putting that line in the film would have merged two different projects. **Dropped the competitor beat entirely**; Part 2 keeps LinkedIn and Jobright, both quote-backed | B05 |
| 5 | My nine checks were illustrated as "title, seniority and location", so the word *sponsorship* never appeared in the film | R5 (no citizenship requirement) and R6 (sponsorship not ruled out) are two of the nine. The examples Claude picked happened to skip both, which would have read as a change of project after a pitch film about sponsorship. **Changed the examples to title, work country, and whether the posting requires citizenship or rules out sponsorship** | B07 |
| 6 | B12's success criteria began "every verdict traces to a rule" | My own tests already enforce that, so it cannot fail. A criterion that cannot fail is not a criterion — the same thing I found in Mode Build, where my sensitivity ranges could never have reached a flip point. **Deleted it** | B12 |
| 7 | The first patch to B12 added "it did not work if saying skip to everything would have scored as well" | Wrong hole. "Skip everything" already fails the criterion "no posting I labelled relevant is missed". The strategy that **passes** that criterion for free is marking everything relevant. **B12 now rules out both lazy rules** | B12 |
| 8 | B12's wording packed three conditions into one spoken sentence with two "or"s | A film is heard once. **Split into three sentences, ending on the concrete examples**, and avoided em-dashes because the voice may not render them as pauses | B12 |
| 9 | B05 claims "the verdict names the phrase it found". The reviewing session proposed the weaker "names that check", because it was not sure which was true | Claude read `rule.py` line 154, which prints the matched phrases, so **B05 kept the stronger wording**. Later I ran four sentences through R6 myself: my output shows `fail`/`pass` per sentence, and Claude's run of the same test shows the phrase list. The run also exposed a gap: see below | B05 |

## What I learned about my own rule while checking the film

Testing claim #9 meant running R6 against four ways a posting can rule out
sponsorship. I ran this in my own PowerShell on 2026-11-23, from the JS2 folder:

```
python -c "import json; from agent import rule; r=json.load(open('persona/resume.json',encoding='utf-8'));
[print([y for y in rule.judge({'id':1,'title':'Data Analyst','location':{'name':'New York, NY'},
'content':s},r)['reasons'] if y['check']=='R6'][0]['result'], '|', s) for s in [...]]"
```

Two were caught and two were not:

| Sentence in the posting | R6 |
|---|---|
| "We **will not sponsor** visas." | fail — caught |
| "Offered **without sponsorship**." | fail — caught |
| "We **do not provide visa sponsorship**." | pass — **missed** |
| "**Sponsorship is not offered**." | pass — **missed** |

R6 matches a fixed list of phrases. The list holds `do not sponsor` and
`not offer sponsorship`, but a posting written as "do not **provide** visa
sponsorship" or "is not **offered**" slips past it. Nothing in the film claims
the check is complete, so the narration stands as recorded. But this is a false
negative in the direction that costs me an application on a job I could not take,
and I did not know about it until today. Widening the list is filter work, which
is what Job-Search Agent 3 is about.

## Numbers in the film, and where each came from

Every figure I say aloud is from the JS1 or JS2 submission. Claude re-checked
each one today against the file named beside it, rather than letting my memory
of the number stand; the checks are recorded in `FACTCHECK.md`.

| Said in the film | Checked against |
|---|---|
| nine checks | `CONTRACT.md` — R1 to R9, nine distinct rules |
| six boards, twelve requests, two minutes | JS2 run report `budget.limits`: `max_boards 6`, `max_requests 12`, `max_seconds 120` |
| eighty-seven tests pass | `python -m unittest discover -s tests` on the submitted folder |
| one hundred seventy-six on Ashby | `runs/wrong-ats/terminal-crosscheck.txt` |
| three hundred sixty-four of fifteen hundred | `review/compare_behaviour.py`: "1561 real postings; R3 changed on 364" |
| thirty-four new postings | JS2 run 2: Pinterest 6, Databricks 16, Ramp 9, Palantir 3 |

## What I accepted, modified, and rejected from Claude

- **Accepted:** the four-part skeleton, the phrasing of B02 ("a tool that silently
  misses a board looks exactly like a quiet day"), and the B12 rewrite in #7.
- **Modified:** B04 and B07, after the sessions checked the sources and I decided (#1, #2, #5).
  B12's wording for the ear (#8). B05's wording upward, after testing (#9).
- **Rejected:** the F1 Hire beat (#3, #4), and the first B12 patch (#7). Both came
  from a review session; both were wrong for reasons I could check.

## What is unresolved

- R6's phrase list is incomplete, as the table above shows. I have not widened it,
  because changing the rule the day I describe it would make the film's numbers
  stale.
- I did not verify how FrogHire handles a company with no filings on record. I
  expect its public pages do not say, and the film no longer depends on it.
- Part 2 compares my agent with two tools I have not used. The film describes
  them from their public pages.

## Note on the voice

The narration is a synthetic voice reading a script I approved line by line. The film says this
in its first line.
