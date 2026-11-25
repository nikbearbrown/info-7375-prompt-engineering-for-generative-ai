# Where every number in the scorer came from (Chapter 9)

Claude Code drafted this table on 2026-11-24 from FILTER.md, the code and the commit record. "Hand-set" means a person chose the value. "Fitted" would mean an optimizer chose it from labels. **Nothing in this scorer is fitted.** v0.1's numbers were all set before any hand label existed. v0.2's one new number (3 years) was chosen after the 50 development labels, never the 30 held-out ones. (This sentence was revised on 2026-11-24 after the reject audit; until then it read "no number was chosen by looking at a hand label".) "Inherited" means it was carried over unchanged from earlier work.

## The filter (FILTER.md v0.1, `jobwatch/screen.py`)

| Object | Value | Origin | Who | Record |
| --- | --- | --- | --- | --- |
| Role points | 1 | hand-set | the student | FILTER.md: "Give a matching title 1 point." "I set the weights and cutoff by hand for v0.1." |
| Title-topic points | 2 | hand-set | the student | FILTER.md |
| Description-topic points | 1 | hand-set | the student | FILTER.md |
| Cutoff | 2 | hand-set | the student | FILTER.md: "score at least 2" |
| One award per rule, not one per term | — | Claude Code's reading of "Add 2 points for … or data infrastructure" | Claude Code | `screen._award`, test C5 |
| Role words `engineer`, `developer` | — | `engineer` inherited from JS1's persona (`title_word`); `developer` added | the student | FILTER.md; `persona/alex_morgan.json` |
| Level words | 10 | 8 inherited from JS1's persona (`excluded_title_words`); `intern` and `internship` added | the student | FILTER.md |
| Title topics | 8 | `machine learning`, `ml`, `ai` and `inference` inherited from JS1's `focus_terms`; JS1's `data` dropped; `model serving`, `data engineer`, `data platform` and `data infrastructure` added | the student | FILTER.md |
| Description topics | 7 | new in v0.1 | the student | FILTER.md |
| Tokenizer (decode HTML, lowercase, split outside a–z0–9) | — | inherited from JS1 (`jobwatch/normalize.py`, unchanged) | JS1 | FILTER.md: "Decode HTML, lowercase the text, and match whole words" |
| Tie order: board identifier, then posting key | — | the rule is the student's; comparing as text is Claude Code's reading | the student; Claude Code | FILTER.md; `screen.rank` |
| U.S. words: United States, USA, US, U.S. | 4 | an option Claude Code worded, chosen by the student ("Country or state") | the student's choice | FILTER.md, additions |
| U.S. states, USPS codes, and DC | 51 + 51 | from Claude Code's knowledge, not checked against a USPS file | Claude Code | `jobwatch/location.py` |
| Other countries | 249 rows | inherited: tzdata 2026e `iso3166.tab` (public domain), copied unchanged, minus the U.S. and its territories, plus 4 aliases Claude Code added | tzdata; Claude Code | `jobwatch/data/iso3166.tab`, `location.ALIASES` |

## The shortlist and its claims

| Object | Value | Origin | Who |
| --- | --- | --- | --- |
| Shortlist size | 8 | chosen from Claude Code's options (5, 8, 10) | the student |
| The claims prompt | [prompts/claims-v1.md](../prompts/claims-v1.md) | hand-set, written once, not tuned | Claude Code |
| At most 3 qualification claims per posting | 3 | hand-set, to keep the labelling to about 60 claims | Claude Code |
| Model | `claude-opus-5-5` | inherited from JS1's judge (`DEFAULT_MODEL`) | JS1 |
| Temperature and other sampling settings | not set | `claude -p` has no flag for them. Claude Code's defaults applied and are **unknown** to this project | — |
| Context Claude Code adds to each `claude -p` call | not inspected | JS1 measured about 800 tokens of it and could not read it | — |

## The evaluation

| Object | Value | Origin | Who |
| --- | --- | --- | --- |
| Held-out design | 15 kept or review + 15 rejected | chosen from three options Claude Code wrote | the student |
| Reject audit size | 30 random rejects | the brief ("at least 30") and the student's bar ("thirty randomly picked rejects") | the brief; the student |
| Close calls | 5 one point under the cutoff + 5 at it | hand-set | Claude Code |
| Kept sample | 10 | hand-set | Claude Code |
| Sample seed, shuffle seed | 20261124, 1125 | hand-set (the date) | Claude Code |
| Bar | 27 of 30 held-out decisions; no unmet requirement cleared; at most one wrong exclusion | hand-set, before JS3 | the student (film beat B17, 2026-11-21) |
| Can’t tell in the held-out score | left out; pass at 90% of the Yes and No rows | chosen from Claude Code's options after the development audit, before the held-out run | the student |
| What counts as a cleared unmet requirement (filter side) | a reaching row labelled No whose reason states years without "preferred", or names a minimum, a requirement, a clearance, new graduates or entry-level applicants | Claude Code's mechanical reading of the student's "Both", fixed in FILTER.md and `jobwatch/held_out.py` before the run | Claude Code |

## FILTER.md v0.2 (added 2026-11-24, after the reject audit)

| Object | Value | Origin | Who | Record |
| --- | --- | --- | --- | --- |
| Experience minimum | 3 years (v0.1: no rule) | hand-set. The number is in the option Claude Code wrote, and the student chose that option. Claude Code put 3 in it because the one development posting labelled Yes that states years (P30) asks for 2+. 3 and 4 gave the same development result | the student's choice | FILTER.md; `variants/v0.2-experience-minimum.json` |
| How a description is read: block tags, a bold heading's 100-character limit, the preferred markers (preferred, nice to have, bonus, a plus, pluses, may also), the words that make a mention not a requirement (after, every, last, past, first, next, previous, recent, within; ago, thereafter, old), number words one to twenty | — | hand-set from FILTER.md ("Five years preferred") and the text of development and other non-held-out postings, before the held-out run | Claude Code | `jobwatch/experience.py`, `tests/test_experience.py` |
| Candidate changes not chosen | 3 committed specs | written by Claude Code to reproduce the development counts | Claude Code | `variants/candidates/` |

## Inherited from JS2, not changed in JS3

The run budget (at most 4 boards, 4 requests, 30 s, 5 s per request), the board list and the permission policy all come from the student's JS2 GATE.md, through `jobwatch/` copied at `9c1db18`.

## What "persistence" does not prove here

Every one of these objects persists: FILTER.md sits in the repository, the prompt is a file, and the seeds and the sample are committed. None of that is training. A later run that behaves differently because FILTER.md changed shows that **the input changed**. It does not show that anything was learned or that Claude's weights moved, and nothing in this project can see or change Claude's weights. The one-change-at-a-time test in [ONE-CHANGE.md](ONE-CHANGE.md) is the check: change one object, keep the rest fixed, and measure on labels that guided no choice.
