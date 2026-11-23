# FILTER.md — what reaches me, and on what evidence

**Written before any JS3 code existed, and committed alone so the ordering is
checkable in git.** Frozen 2026-11-23.

**Filter version F-v2 (frozen as F-v1; §7 A1). Scorer version S-v2 (frozen as
S-v1; §7 A2). Evidence rules E-v1.**

This is layer 3 of my own job-search agent. Layers 1 and 2
(`fall-2026/weiting-w/js1-contract-and-watch`,
`fall-2026/weiting-w/js2-loop-tools-diff`) decide *whether a posting is one I
could take*: four ordered gates on title, discipline, job family and location,
written as rule R-v3. They answer a question about the job's shape.

They do not read a word of the posting. JS2 collected 452 real postings from
four boards and R-v3 judged every one of them on title, department and
location alone — which is why its one live run produced no verdict worth
keeping. This layer reads the posting.

---

## 1. The filter, as a document

Two stages, and the difference between them is the whole design.

**Stage A — gates (inherited, unchanged).** Four hard exclusions, carried from
JS1/JS2's R-v3 and *not* re-litigated here. A posting failing any of these is
rejected outright, with no score computed. These are facts about whether the
job is takeable, not matters of degree.

| gate | rule | one line of reasoning |
|---|---|---|
| **F1** `title_block` | Reject if the title contains any whole word in `title_block` (senior, staff, principal, lead, director, manager, intern, contract, …). | A new graduate is not eligible for these and no amount of topic overlap changes that; whole-word, so "Leadership" does not trip "lead". |
| **F2** `role` | Reject unless the title contains one of `target_title_phrases` ("software engineer", "machine learning engineer", …). | The title is the one field every board fills in honestly; if the role is not named there, the posting is for a different job. |
| **F3** `job_family` | Reject unless the posting's department/job-family field matches `target_job_families`. | A "Software Engineer" inside a Sales department is a sales-support role; the family is the board's own statement of what team this is. |
| **F4** `location` | Reject unless a `locations_ok` phrase occurs in the location; `remote_ok` filters rather than bypasses (R-v3). | Being remote is not a location — this was the defect JS2's review packet fixed, and it stays fixed. |

**Stage B — the score (S-v1, new in JS3).** A posting that clears the gates is
*takeable*. Whether it is *worth my time* is a matter of degree, so it gets a
score from the posting's own text, and a threshold decides the shortlist.

| signal | weight | one line of reasoning |
|---|---|---|
| **S1** core engineering topics — `api`, `backend`, `distributed systems`, `database`, `microservice`, `infrastructure` | **+2 each, capped at +6** | These are the things I have actually built; each additional one is weaker evidence than the first, hence the cap. |
| **S2** languages I write — `python`, `java`, `c++`, `typescript`, `javascript`, `go`, `rust`, `c#` | **+2 each, capped at +4** | A named language I know is concrete and checkable, unlike "strong fundamentals"; capped because listing eight languages signals a vague posting, not a better fit. |
| **S3** graphics / games — `unity`, `unreal`, `rendering`, `shader`, `game engine`, `real-time 3d` | **+3 each, capped at +6** | Weighted above S1 because this is the part of my coursework that is specialised, so a posting naming it is a much rarer match. |
| **S4** machine learning — `machine learning`, `pytorch`, `tensorflow`, `model training`, `inference` | **+2 each, capped at +4** | Real but shallower experience than S1 or S3; worth points, not worth outranking them. |
| **S5** new-graduate signals — `new grad`, `new graduate`, `entry level`, `early career`, `university graduate`, `0-2 years`, `1-2 years` | **+4** | The single strongest signal that I am inside the posting's intended audience; one flat bonus, because saying it twice does not make it twice as true. |
| **S6** experience wall — `5+ years`, `6+ years`, `7+ years`, `8+ years`, `10+ years`, `phd required`, `ph.d. required` | **−6** | A hard requirement I do not meet; negative rather than a gate because boards write these loosely and a single stray line should cost a posting its shortlist place, not its existence. |
| **S7** clearance / citizenship wall — `security clearance`, `ts/sci`, `must be a u.s. citizen` | **−8** | Unlike S6 this is rarely negotiable and never about me personally; the largest penalty in the table. |

**Shortlist threshold T = 6.** Hand-set before measuring, so the number has a
stated origin and the audit can disagree with it (§6).

### Matching rules that apply to every signal above

- **Case-insensitive, whole-word, on the plain-text body only.** Not on HTML:
  `<a href="...rendering...">` is markup, not a claim about the job.
- **A signal fires at most once per posting**, however many times its word
  appears. Repetition is a property of the writer, not of the job.
- **The matched span and its surrounding sentence are recorded for every
  signal that fires.** A score I cannot trace back to a sentence is a number I
  cannot defend, and §2 depends on having the sentence.

### What F-v1 deliberately does not do

- **It does not read the title for topics.** Only the body feeds the score.
  Titles are short and optimised; "Software Engineer, AI Platform" would score
  on `ai` without the job having anything to do with it.
- **It does not use the company name.** I have no evidence about companies, and
  a weight on the name would be a preference wearing a measurement's clothes.
- **It does not call a model to decide relevance.** The score is arithmetic over
  a word list I wrote, so every point is attributable. A Claude prompt appears
  in this system in exactly one place — §5 — and it is not the filter.

---

## 2. The evidence rules (E-v1)

Every claim the shortlist makes about a posting gets one of three labels,
judged **against that posting's own text and nothing else**.

| label | when |
|---|---|
| **supported** | A span of the posting's text states the claim, or states something that entails it, and the span is quoted in the justification. |
| **contradicted** | A span of the posting's text states the opposite, or states something incompatible with the claim. A contradiction outranks any number of supporting spans. |
| **insufficient** | The posting's text neither states nor excludes the claim — including when the field the claim would need **does not exist on that board**. |

**The three rules that decide a label.**

- **E1 — the span must be quotable.** If I cannot point at the characters in
  `descriptionPlain` that carry the claim, the label is `insufficient`. Not "it
  is clearly implied". The span goes in the output.
- **E2 — a word match is not a claim.** That a posting contains "python" supports
  "this posting mentions Python". It does not support "this job is a Python
  job", and it never supports "I am a fit". The claim is labelled against what
  the span actually says, not against what the match was for. This is the
  relevance-is-not-entailment rule and §4 of `reports/shortlist.md` is the
  worked example.
- **E3 — absence is not denial.** A posting that never mentions a visa is not a
  posting that offers one. Absence produces `insufficient`, never
  `contradicted`.

**The abstention rule.** The agent must answer **"I cannot tell"** — and must
not produce a score-backed claim — whenever:

1. the posting has **no body text at all** on the board it came from (see §3);
2. the claim needs a field the posting does not carry;
3. the only support is a match inside markup, a URL, a company boilerplate
   block, or a list of other open roles;
4. the spans found are **both** supporting and contradicting, and nothing in
   the text resolves which governs.

Abstention is an answer, not a failure. A shortlist entry that says "I cannot
tell whether this role is open to new graduates" is more use to me than one
that guesses, because I can go and read the posting myself.

**Known limit of this rule, stated before measuring.** The abstention rule is
about *missing* text, not *misleading* text. A posting that says "we love new
grads" in boilerplate it pastes into all 40 of its listings will be labelled
`supported`, because the span exists and says so. E-v1 has no notion of a span
being unreliable. `reports/shortlist.md` §5 is required to show a real
counterexample from the data.

---

## 3. The expected sources

Four boards, three applicant-tracking systems, 452 postings captured live by
JS2 on **2026-11-11T00:18Z** and committed in that folder's `evidence/raw/`.
JS3 reads those bytes and makes no network request of its own.

| board | postings | body text field | score can be computed? |
|---|---|---|---|
| `ashby:ramp` | 177 | `descriptionPlain` (~4.6 KB) | yes |
| `ashby:linear` | 33 | `descriptionPlain` (~5.8 KB) | yes |
| `lever:spotify` | 85 | `descriptionPlain` + `lists[]` | yes |
| `greenhouse:reddit` | **157** | **none — the field does not exist** | **no** |

**This is the single most important fact about this layer, and it was true
before I wrote a line of it.** Greenhouse's public board endpoint returns a
posting's title, location and metadata, and no description unless asked with a
parameter JS2 did not send. So **157 of 452 postings — 35% — have no text for
the filter to read.**

**What the agent answers when the body is missing.** Not zero. Not a guess from
the title. The posting is reported with:

```
score: null
status: "no_body_text"
reason: "greenhouse:reddit does not return a description on this endpoint;
         S1-S7 are undefined for this posting."
```

and it goes to **neither** the shortlist nor the reject pile. It goes to a third
bucket, `cannot_score`, which is reported with its own count everywhere a
count appears. Folding these into "rejected" would be the finished-wrong-answer
failure of JS2 wearing a new hat: a true-sounding number produced by treating
"I did not look" as "I looked and found nothing".

**What this costs, stated up front.** The reject audit in §6 can only speak to
the 295 postings that have text. Any statement I make about the other 157 is a
statement about a filter that never ran.

---

## 4. Wrong versions the tests must catch

Real code in `tests/wrong_versions.py`, with contract tests asserted to **fail**
on each.

- **W1 `missing_body_scores_zero`** — treats a posting with no body as a posting
  that scored 0, so all 157 Greenhouse postings land in the reject pile.
  Plausible because `sum([])` is 0 and the arithmetic never complains. Caught by
  requiring `cannot_score` to be its own bucket with its own count, and by a test
  that the three buckets sum to 452.
- **W2 `substring_topic_match`** — matches signal words as substrings rather than
  whole words, so `go` fires on "ongoing", "category" and "Chicago", and `c#`
  and `c++` leak into unrelated punctuation. Plausible because `in` is the
  obvious operator and it even looks *more* permissive in a good way. Caught by
  a test over the real corpus asserting that `go` fires on no posting whose only
  occurrence is inside a longer word.
- **W3 `score_from_the_whole_record`** — scores the JSON record rather than the
  plain-text body, so markup, URLs and the "other open roles" sidebar all count.
  Plausible because `json.dumps(record)` is one line and obviously contains
  everything. Caught by a test that a posting whose only `rendering` occurrence
  is inside an `<a href>` scores 0 on S3.
- **W4 `relevance_implies_support`** — labels a claim `supported` whenever the
  signal that produced it fired, i.e. treats a word match as entailment. This is
  the one I expect to be most tempting, because it makes every shortlist entry
  look well-evidenced. Caught by the worked case in `reports/shortlist.md` §4,
  asserted as a test.

---

## 5. Where every number comes from

Declared **before** any fitting, so that "fitted" cannot be claimed after the
fact for a number that was hand-set.

| number | origin at freeze | may it move? |
|---|---|---|
| `title_block`, `target_title_phrases`, `target_job_families`, `locations_ok` | **inherited** — JS1's persona, unchanged since 2026-10-21 | no, not in this layer |
| gate order F1→F4 | **inherited** — JS1 CONTRACT.md, R-v3 | no |
| S1–S7 signal word lists | **hand-set** — written in this document, from my own coursework | only by an amendment recorded in §7 |
| S1–S7 weights and caps | **hand-set** — reasoning in the §1 table | only by an amendment recorded in §7 |
| threshold **T = 6** | **hand-set** | **yes** — §6 of `reports/what-moves-the-score.md` refits it on a labelled training split and measures on a held-out split |
| the Claude prompt in `tools/explain_shortlist.py` | **hand-written**, and it is *not* part of the filter or the score | yes, and it is one of the one-at-a-time changes |

**What persistence is not proof of.** If a change to the prompt file, the word
list or the tool list changes the agent's behaviour in a later session, that is
a changed *input*, not a changed *model*. Nothing in this repository trains
anything. No weight is learned by gradient descent, no model is fine-tuned, and
a Claude prompt that produces different output after I edit it has been
*reconfigured*, not taught. `reports/what-moves-the-score.md` is required to say
this about each change it measures.

---

## 6. The audit I am committing to before I see its result

- A **random sample of at least 30 rejected postings**, drawn with a seed
  recorded in the report, judged by me by hand before I look at why the filter
  rejected them.
- **Every posting within ±2 of the threshold**, judged the same way, because the
  threshold is the number most likely to be wrong and these are the cases that
  decide it.
- **A sample of what was kept**, so the audit can find false positives and not
  only false negatives.
- **At least one false friend** — a word that matched for the wrong reason —
  found in the real corpus, named, and its rule either narrowed or removed, with
  the before-and-after counted.

**What a sample of this size can show, written before I have a number.** A hand
sample of 30–45 postings out of 452 gives a disagreement *count*, not a rate for
the corpus. With 30 rejects sampled, one disagreement is a point estimate of
3.3% whose 95% interval runs past 17%; the honest sentence is "I checked 30 and
disagreed with *n* of them", never "the filter's false-negative rate is *n*/30".
No number in any report here is to be written as a rate for all postings.

---

## 7. Amendments

Changes after the freeze, each dated, with a reason, and each one its own
commit. A change to a word list or a weight is an amendment; a change that moves
a verdict is a version bump.

- 2026-11-23 — none at freeze time.

### A1 — 2026-11-23. F3 inverts from an allowlist to a denylist. **F-v1 → F-v2.**

**What measuring showed.** F-v1 as frozen, run over all 452 postings, put
**zero** of them in front of the scorer (`reports/f-v1-as-frozen.txt`, commit
`ed9d7d1`). All 295 postings that carry a body were stopped by a gate: 167 at
F1 and 104 at F2, both correctly, and **24 at F3**.

Those 24 are titles F2 had already accepted — "Software Engineer, Backend,
Developer API", "Software Engineer, Frontend", "Machine Learning Engineer",
"Backend Engineer - Data Platform". F3 rejected them because
`target_job_families` is `['software engineering', 'machine learning', 'data
science']`, which is **Greenhouse's `Job Family` vocabulary**. Ashby writes
`Engineering` in a field it calls `department`; Lever writes `Platform`,
`Music`, `Subscriptions R&D` in `categories.team`.

So the gate was testing which words a board chose, not what the job is. The
same posting passes or fails depending on which applicant-tracking system the
company bought. §5 said the gates were inherited and not to be re-litigated
here; that was written before I knew the inherited list was single-board.

**The change.** F3 keeps its purpose — stop a posting filed under a function
that is not engineering, which is how "Software Engineer" inside a Sales org
gets caught — but it can no longer require a positive match, because there is
no vocabulary the three systems share. It becomes a **denylist of functions
that are not engineering organisations anywhere**, applied to whatever family
field that provider sends:

```
sales, marketing, legal, finance, accounting, payroll, tax,
human resources, people & talent, recruiting, pr & communications,
government affairs, business development, deal desk, customer experience,
advertising, music business, music marketing
```

Matched as a substring of the lower-cased family value, so "Advertising Sales
- Enterprise" and "Music Marketing" are caught by one entry each. A posting
whose family field is absent or `null` **passes** F3: absence is not denial
(E3), and F2 has already read the title.

**Why a denylist and not a per-board allowlist of engineering orgs.** An
allowlist would need me to decide that Spotify's "Experience" and
"Personalization" are engineering and "Music" is not, which is a guess about
one company's org chart dressed up as a rule. The denylist only asserts things
that hold at any company: a posting filed under Payroll is not a software
engineering job whatever its title says.

**Honesty about how this list was built.** I wrote it **after** seeing all 69
distinct family values the four boards use and after seeing how many postings
each choice admits. That makes it fitted to this corpus, not derived from
first principles, and an over-generous denylist shows up as false positives —
which is exactly what the kept-sample half of the audit in §6 is for. The
counts before and after are in `reports/reject-audit.md`.

**A version bump, not a letter bump**, because it moves verdicts: F-v1 → F-v2.
The predicted effect, written here before the code changed: the 24 postings
above move from `gated` to being scored, and no posting moves the other way,
because a denylist can only ever admit more than an allowlist that shared none
of its vocabulary. `tests/test_amendment_a1.py` asserts exactly that, naming
the 24.

**Not changed by A1:** F1, F2 and F4 stand as inherited. One change per
amendment.

### A2 — 2026-11-23. Three false friends cut from S-v1. **S-v1 → S-v2.**

Found by running every signal word against the 295 postings that carry a body
and reading the sentence each one matched, which is the measurement FILTER.md
§6 committed to. All three counts and quotations below are from that run.

**1. `infrastructure` (S1, +2) — cut.** It matched **206 of 295** postings, and
**177 of 177** on `ashby:ramp`. Every Ramp posting opens with the same
sentence:

> ABOUT RAMP — Ramp is building the smart **infrastructure** for finance teams…

so the word is in the company's boilerplate, not in the job. Ramp's Sales,
Legal and Payroll postings all scored +2 on a sentence about the company. A
signal present in 100% of a board's postings distinguishes none of them.

**2. `go` (S2, +2) — cut.** It matched 55 postings. Reading the sentences, at
most **9** plausibly name the Go language (always inside a list such as
"Python, Go, Java, or similar"); the other **46** are the English verb or a
compound: "You'll **go** deep on the product" on a Product Marketing posting,
"the **go**-to technical resource", "**go**-to-market motions". That is an 84%
false-positive rate, and no amount of whole-word matching fixes it, because
`go` *is* a whole word in English. **`golang` does not appear anywhere in the
corpus**, so there is no narrower replacement to swap in: the cost of this cut
is that the Go language becomes undetectable, and I am taking that cost rather
than keeping a signal that is wrong five times out of six.

**3. `0-2 years` and `1-2 years` (S5, +4) — cut.** Together they matched exactly
**one** posting, and it is a sales job:

> - **1-2 years** of quota-carrying SaaS **sales** experience in an SMB,
>   transactional, or high-velocity closing role.

A year range states how much experience is wanted, not that a posting is open
to new graduates, and here the +4 "you are the intended audience" bonus landed
on a job requiring sales experience I do not have.

**The consequence of cut 3, which is the part worth saying out loud.** With the
year ranges gone, S5's remaining phrases are `new grad`, `new graduate`,
`entry level`, `entry-level`, `early career`, `university graduate` — and
**not one of them occurs in any of the 295 postings**. So S5 can no longer fire
at all on this corpus. The signal FILTER.md §1 called "the single strongest
signal that I am inside the posting's intended audience" is dead here, and the
honest reading is not that the signal is broken: **none of these four boards
published a posting that says in words that it is open to new graduates.**
That is a fact about the boards, and it is the kind of thing a filter is
supposed to surface rather than paper over.

**Predicted effect, computed before the code changed** and saved verbatim in
`reports/a2-predicted-effect.txt`:

| | before A2 | after A2 |
|---|---|---|
| postings scored | 24 | 24 |
| shortlisted at T=6 | **14** | **7** |
| score range | [2, 10] | [−2, 8] |
| per-posting change | — | −2 on 17, −4 on 3, unchanged on 4 |

Halving the shortlist is not a sign the cuts were wrong. It is what removing a
+2 that 70% of the corpus received looks like: the old scores were inflated by
a constant, and a threshold set against inflated scores is the wrong threshold.
**T is the one number §5 permits to move**, and
`reports/what-moves-the-score.md` refits it on a labelled training split and
measures on a held-out split rather than my choosing a number that restores the
count I liked.

**A version bump: S-v1 → S-v2.** `tests/test_amendment_a2.py` pins the table
above.

**Not changed by A2:** every other word, every weight, every cap, and the
threshold. One change per amendment.
