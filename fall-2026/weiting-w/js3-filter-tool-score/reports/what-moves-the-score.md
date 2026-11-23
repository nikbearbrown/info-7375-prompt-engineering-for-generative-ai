# What moves the score

Chapter 9. Every number in this system, where it came from, and what happens
when I change one object at a time.

Raw measurements: `reports/one-change-measurements.txt`, produced by the script
block recorded in this repository's history. Baseline throughout is
**F-v2 / S-v5 / E-v1a, T = 6**, over the 452 postings JS2 captured on
2026-11-11T00:18Z.

```
BASELINE   shortlisted 4   below_threshold 20   gated 417   cannot_score 11
           score range [-6, 8]
```

---

## 1. Where every number came from

Declared in FILTER.md §5 **before any fitting**, so that "fitted" could not be
claimed afterwards for something hand-set. Reproduced here with what has
happened to each since.

| number | origin | moved since? |
|---|---|---|
| `title_block`, `target_title_phrases`, `locations_ok` | **inherited** — JS1's persona, unchanged since 2026-10-21 | no |
| gate order F1→F4 | **inherited** — JS1 CONTRACT.md, R-v3 | no |
| `target_job_families` | **inherited** | **replaced** by A1 — it was Greenhouse's vocabulary, so it was testing which applicant-tracking system a company bought |
| S1–S7 word lists | **hand-set**, from my own coursework | **cut** by A2 (three false friends), **rewritten** by A3 (S6 from strings to a number), and one cut **undone** by A5 |
| S1–S7 weights and caps | **hand-set**, reasoning in FILTER.md §1 | base weights no; **A4 added a section multiplier** on top of them |
| section weights (A4) | **hand-set**: 1, 1, ½, 0, 1 | no |
| `MIN_WALL_YEARS = 3` | **hand-set** by A3 | no |
| threshold **T = 6** | **hand-set** | §4 below |
| the explanation prompt | **hand-written**, and not part of the filter or the score | §3 below |

**Nothing here was fitted before §4.** Four of the nine rows changed, every one
of them because a measurement contradicted it, each recorded as a dated
amendment whose prediction was written before the code moved.

---

## 2. One change at a time: the objects that are not the prompt

### Change 1 — the filter file: put `infrastructure` back into S1

Measured **twice**, before and after A4, and the pair is the most useful thing
in this report.

| | shortlisted | below | range |
|---|---|---|---|
| under S-v3, baseline | 6 | 18 | [−6, 6] |
| under S-v3, with `infrastructure` | **11** | 13 | [−4, 8] |
| under S-v5, baseline | 4 | 20 | [−6, 8] |
| under S-v5, with `infrastructure` | **4** | 20 | [−6, 8] |

**The same one-word change nearly doubled the shortlist before A4 and does
nothing after it.** A2 cut the word because it fires on 206 of 295 postings and
177 of 177 at `ashby:ramp`, always from "Ramp is building the smart
infrastructure for finance teams". Under S-v3 putting it back added +2 to every
Ramp posting at once — a constant, and a constant added to every score is a
threshold change wearing a word list's clothes. Under S-v5 that sentence is in
a `company` section and scores 0.

Two things follow, and the second is the one I did not expect:

- **A signal that fires on most of the corpus does not rank the corpus, it
  shifts it.**
- **Whether a word is a good signal is not a property of the word.** It
  depended entirely on another object — the section weights — that did not
  exist when A2 measured it. A5 reinstated the word on the second row of this
  table.

### Change 2 — a setting: score the whole JSON record instead of the body

| | shortlisted | below | cannot_score | range |
|---|---|---|---|---|
| baseline | 6 | 18 | **11** | [−6, 6] |
| whole record | 6 | 29 | **0** | [−6, 6] |

This is wrong version W3, and the number to look at is not the shortlist —
it is **`cannot_score` going from 11 to 0**.

Every Greenhouse record has *some* JSON text in it: field names, a URL, a
metadata array. So scoring the record means a posting with no description is
suddenly scoreable, and the bucket that exists to say "this board sent me
nothing to read" empties out. W3 does not merely add noise; it silently
destroys the distinction W1 exists to protect. I had those filed as two
separate wrong versions and they turn out to be the same mistake entered from
two doors.

### Change 3 — a setting: drop Lever's `lists` from the body

| | shortlisted | below | range |
|---|---|---|---|
| baseline | **6** | 18 | [−6, 6] |
| `descriptionPlain` only | **3** | 21 | [−6, 6] |

**Half the shortlist is a decision about which field to read.** Lever's
`descriptionPlain` is a one-paragraph company blurb; the duties and
requirements are in `lists`, as HTML. Reading only the "plain" field — which is
the obvious, defensible-sounding choice, and the one whose name suggests it is
*the* body — loses all three Spotify entries.

No word list changed, no weight changed, no threshold changed. A field
selection moved the output as much as A2 and A3 did, and unlike them it would
never have appeared in an amendment, because it does not look like a rule.

### Change 4 — the section weights: treat `optional` as full weight

| | shortlisted | below | range |
|---|---|---|---|
| baseline (optional ×½) | **4** | 20 | [−6, 8] |
| optional ×1 | **6** | 18 | [−6, 8] |

This is the object A4 added, changed on its own. The two postings that come
back are `Software Engineer, iOS` and `Software Engineer, Android`, whose
every point is in a NICE TO HAVES block while their requirements ask for Swift
and a year of mobile development.

Half the difference between a four-entry shortlist and a six-entry one is a
single multiplier on a single section kind, and the two entries it decides are
exactly the two I would not have applied to.

### Change 5 — the tool list

Adding a second tool to `toolserver/server.py` changes **nothing** about the
filter's output, and saying so is the point: the tool list is not an input to
the score. What it changes is what a client may ask for, and the number that
matters there is surface area:

| | tools declared | arguments naming a location |
|---|---|---|
| as shipped | 1 | **0** |
| with a `search_postings` tool | 2 | **1** |

Zero to one is the step that matters. `score_posting` takes text, so there is
no path to validate and no confinement to get wrong; a tool that takes a query
over the corpus needs a path, and the whole of `reports/tool-evaluation.md`'s
analysis of the filesystem server is about what happens next.

---

## 3. One change at a time: the prompt, and a mistake I made doing it

The three prompts and the three real responses are in
`evidence/claude-responses/`, with their provenance and a stated limitation:
the model answering is the same assistant that wrote the code, so these say
what *these prompts* elicited *here*, and nothing about Claude in general.

**The mistake.** I wrote P-v1 (loose rules, full posting body) and P-v2 (strict
rules, only the spans that scored), compared them, and had to throw the
comparison away: **P-v1 → P-v2 changes the prompt and the context at the same
time.** That is two objects, and this section is about one. P-v3 — strict
rules, full body — is what isolates them.

| | rules | context | asserted a fit judgement | named the real requirements | new-graduate question |
|---|---|---|---|---|---|
| P-v1 | loose | full body | **yes** | yes | implicit |
| P-v2 | strict | 3 spans | no | **could not** | abstained |
| P-v3 | strict | full body | no | yes | **answered: no** |

- **P-v1 → P-v3 isolates the prompt.** The rules stopped the fit judgement.
  Both answers found the actual requirements, because both could see them.
- **P-v2 → P-v3 isolates the context.** The rules are identical and the answers
  are not comparable in quality: P-v2 could not mention Swift because Swift was
  not in what it was given.

**The result worth keeping.** P-v2 abstained, which is the behaviour the strict
prompt was written to produce — and it abstained **because it was starved, not
because it was careful**. Its "I cannot tell whether this is open to a new
graduate" is correct about the three spans and wrong about the posting, which
states "Minimum 1 year of experience in mobile development" two sections away.

A prompt that produces careful-looking output from insufficient context is
worse than a loose prompt with good context, and comparing P-v1 to P-v2 would
have told me the opposite.

### A second thing the prompts exposed

P-v3 answered the new-graduate question **no**, on the strength of "Minimum 1
year of experience in mobile development". `evidence.py` labels that same
posting `insufficient`, because `MIN_WALL_YEARS = 3` and one year is below it.

Both are defensible — 3 was hand-set by A3 as "already outside what a new
graduate has" — but they disagree about a real posting, and the disagreement is
between a number I chose and a reading anyone would make. **Not changed**, and
recorded in README.md's sign-off: changing `MIN_WALL_YEARS` to 1 would be a
fourth amendment on the last day, and the audit in `reports/reject-audit.md` is
the thing that should decide it, not me at 8pm.

---

## 4. The threshold, refit on held-out labels

T is the one number FILTER.md §5 permitted to move. This section is the only
part of this report that uses the hand labels, and it is written up in
`reports/reject-audit.md` §5 together with the audit those labels came from.

The method, fixed before the labels were looked at:

1. split the hand-labelled postings into a training half and a held-out half,
   with a recorded seed;
2. choose the T that best matches the labels **on the training half only**;
3. report that T's agreement **on the held-out half**, which is the only number
   that means anything;
4. report the baseline T = 6 on the same held-out half, so the refit has
   something to beat.

**What this cannot establish**, stated before the numbers exist: a split of a
48-posting sample gives two halves of about 24, and agreement measured on 24
postings has an interval around it wide enough to swallow most differences.
The honest output is "T = *n* agreed with me on *k* of *m* held-out postings,
against *j* of *m* for T = 6", never "the refit improved accuracy by *x*%".

---

## 4b. Measured against the held-out labels — and against a filter that knows nothing

§2 and §3 report what each change does to the **bucket counts**. That is a
description of the filter, not evidence that a change is an improvement. The
assignment asks for the changes to be measured on labels held out, so they
were: `reports/one-change-heldout.txt`, same split and seed as the threshold
refit, agreement = the filter's keep/drop matching my blind `yes`/`no`.

| change | train | **held out** |
|---|---|---|
| **baseline** F-v2 / S-v5 / T=6 | 18/21 | **21/21** |
| *trivial: reject everything* | *19/21* | ***20/21*** |
| *trivial: keep everything* | *2/21* | *1/21* |
| filter file: drop `infrastructure` (undo A5) | 18/21 | 21/21 |
| section weights: `optional` ×1 (undo A4) | 18/21 | **19/21** |
| setting: score the whole JSON record (W3) | 18/21 | 19/21 |
| setting: drop Lever's `lists` | 18/21 | 20/21 |
| threshold T=4 | 18/21 | 20/21 |
| threshold T=5 / T=7 / T=8 | 18–19/21 | 21/21 |

### The two rows that matter are the italic ones

**A filter that rejects every posting without reading it scores 20 of 21 on
the held-out half.** Mine scores 21. The entire apparatus in this
repository — four gates, seven signals, five amendments, a section
classifier — beats "reject everything" by **one posting**.

On the **training** half it does not beat it at all: 18/21 against 19/21.

The reason is in the labels. Of 42 postings I decided, **3 are `yes`**; the
held-out half contains **1**. A corpus where 93% of the answers are "no"
rewards a filter that says no, and a measurement against it cannot tell a
filter that understands the postings from one that is simply pessimistic.

**So this table cannot validate the filter, and I am not going to present it
as though it can.** What it can do is three narrower things:

- **Rule out the changes that are worse.** Undoing A4 costs two held-out
  postings; scoring the whole record (W3) costs two; dropping Lever's `lists`
  costs one. Those are real, in the right direction, and consistent with what
  §2 predicted from the bucket counts alone.
- **Confirm that A5 is inert**, which is what A5 itself claimed: dropping
  `infrastructure` again changes nothing on either half.
- **Confirm the threshold is not the lever.** T = 5, 6, 7 and 8 are
  indistinguishable on the held-out half, which is the same answer §4's refit
  gave by a different route.

### What would have made this measurable

More `yes` labels. Not more postings — more postings drawn the same way give
the same 93% "no". The sample would have to be **stratified on my verdict**,
which cannot be done before labelling, or drawn from a corpus with more
postings I would actually want, which means boards that publish new-graduate
roles. `FILTER.md` §7 A2 established that **none of these four boards says in
words that a posting is open to new graduates**, so that corpus is not this
one.

That is the honest shape of the problem: the filter was built against a corpus
with almost nothing in it for the persona it filters for, and no amount of
labelling my way out of that changes it.

## 5. What persistence is not proof of

If I edit `prompts/explain-P-v2.txt`, or cut a word from `jobfilter/score.py`,
or point `--raw-dir` somewhere else, this system behaves differently
afterwards — in this session and in every session after it, for as long as the
file stays edited.

**None of that is training, and none of it is learning.**

- **Nothing in this repository has weights that are fitted by gradient
  descent.** The only number that is fitted at all is the threshold in §4, and
  it is fitted by trying each integer and counting agreements — arithmetic I
  could do on paper.
- **No model is called anywhere in this system.** `tools/explain_shortlist.py`
  *prints* a prompt; it does not send one.
  `tests/test_no_model_and_no_network.py` reads the package source and fails if
  an `os.environ`, an `anthropic`, an `openai` or an `api_key` ever appears.
- **A Claude response that changes after I edit the prompt file has been
  reconfigured, not taught.** The three responses in §3 differ because the text
  I handed over differed. Hand the old text over again and the old behaviour
  comes back, which is exactly what training would not do.
- **A behaviour that survives a restart is a file that survived a restart.**
  Every durable thing here is a word list, a weight, a prompt, or a captured
  JSON response, all of them in git, all of them editable with a text editor.
  The system has no memory of its own runs: `jobfilter` keeps no state between
  invocations at all.

The one sentence I would defend: **everything this agent "knows" is a file I
can open, and every change in its behaviour is a diff.**
