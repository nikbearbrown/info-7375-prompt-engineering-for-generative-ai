# INFO 7375 — Job-Search Agent 3: The Filter, the Tool, and the Score

Weiting W. (`fall-2026/weiting-w`)

**Layer 3 of my own job-search agent.** The base is
[`fall-2026/weiting-w/js2-loop-tools-diff`](../js2-loop-tools-diff/) in this
repository, commit `1fb701b3`. Not the Reallocation Engine, not Lectern.

JS2 collected 452 real postings from four boards across three
applicant-tracking systems and judged every one of them on title, department
and location alone — it never opened a description. **This layer reads the
posting**: a filter I can read, a score whose every point traces back to a
sentence, a way to offer the agent to Claude as a tool, and claim labels that
abstain when the text does not settle the question.

## Language and toolchain

- **Python 3**, standard library only — the filter, the scorer, the evidence
  rules, the tool server and every tool. No HTTP client, no scraping library,
  no model, no SDK.
- **pytest**, the only dependency (`requirements-dev.txt`).
- Developed on Python 3.13.16 in a Linux container.
- **Node/npm** only to reproduce the second tool-server evaluation; nothing in
  this folder depends on them.
- **No network at any point.** JS3 reads the bytes JS2 saved on
  2026-11-11T00:18Z.

## The gate came first

`FILTER.md` was committed **alone**, before any JS3 code existed:

```
git log --oneline -- fall-2026/weiting-w/js3-filter-tool-score
git show --stat ee698f2
```

`ee698f2` contains `FILTER.md` and `.gitignore` and nothing else. Each
amendment after it is **two commits — the document, then the code** — so the
order is checkable rather than asserted.

That this command works is a fix, not a feature: JS2's README told a TA to run
the same check and the commit it named had never reached GitHub.
`FRICTIONAL.md` §0 has the whole of it.

## Running it

```
cd js3-filter-tool-score
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

The filter over all 452 postings:

```
python3 -m jobfilter run        # writes audit/decisions.json and audit/summary.json
python3 -m jobfilter summary    # counts only
```

```
filter=F-v2  scorer=S-v3  threshold=6
corpus: 452 postings, 295 with a body, 157 without

  shortlisted         6
  below_threshold    18
  gated             417
  cannot_score       11   (no body on that board; not a zero, not a rejection)
  ----------------------------------
  total             452
```

The shortlist with every claim and its span, and the audit form:

```
python3 tools/make_shortlist.py     # reports/shortlist.json
python3 tools/make_audit_form.py    # audit/audit-form.html, blind
python3 tools/analyse_audit.py audit/labels-weiting.json
```

The tool server, and a real session with it:

```
python3 -m toolserver                       # JSON-RPC 2.0 on stdio
python3 tools/drive_toolserver.py           # evidence/transcripts/session.txt
```

The second tool server, if you want to reproduce that evaluation (needs npm):

```
python3 tools/evaluate_other_server.py      # npx @modelcontextprotocol/server-filesystem@2.4.0
```

The explanation prompts — **this prints a prompt and never sends one**:

```
python3 tools/explain_shortlist.py P-v1 --first
python3 tools/explain_shortlist.py P-v3 --first
```

Deliberately absent: any flag that changes a weight, a word list or the
threshold. FILTER.md §5 says those move only by an amendment in §7, and a
number any caller can set is not a declared number.

## What is in here

| path | what it is |
|---|---|
| `FILTER.md` | the gate: the filter, the evidence rules, the expected sources, four wrong versions, the origin of every number, and three amendments |
| `jobfilter/` | corpus, gates, scorer, evidence rules, pipeline, CLI |
| `inherited/` | JS2's adapters, R-v3 and the persona, copied with import lines rewritten and a test holding that claim |
| `toolserver/` | the MCP server, 241 lines, standard library |
| `tools/` | the audit form, the audit analyser, the shortlist, the prompt renderer, both transcript drivers |
| `reports/reject-audit.md` | 30+ rejects judged by hand, blind, plus the near-threshold and kept samples |
| `reports/shortlist.md` | 6 entries, 24 claims, each labelled against a span |
| `reports/tool-evaluation.md` | both servers, same three questions, two trust decisions |
| `reports/what-moves-the-score.md` | one object at a time, measured |
| `evidence/transcripts/` | both real sessions, both directions |
| `evidence/claude-responses/` | the three prompts and the three real answers, dated |
| `SOURCES.md`, `FRICTIONAL.md` | what came from where; what fought back |

## The three amendments, and what each one cost

Every one was found by measuring, written up before the code moved, and
predicted before it was applied.

| | what it fixed | the shortlist |
|---|---|---|
| **A1** | F3 required Greenhouse's vocabulary, so the same job passed or failed depending on which applicant-tracking system the company bought. F-v1 as frozen put **0** postings in front of the scorer. | 0 → 14 |
| **A2** | Three false friends. `infrastructure` fired on **177/177** postings of one board, all from "Ramp is building the smart infrastructure for finance teams". | 14 → 7 |
| **A3** | The experience wall was a list of literal strings, so "a **minimum of 5 years**" and even `3+ years` slipped through. | 7 → **6** |

A3 deleted the highest-scoring entry on the list. It was found while building
the Chapter 8 tool server: rendering a prompt prints the whole posting, and
that was the first time its requirements section was in front of me.

---

## Sign-off — Job-Search Agent 3

**Checked** — which properties, by which of my own tests:

1. *The filter was written before the code.* `git show --stat ee698f2` is two
   files; each amendment is a document commit then a code commit.
2. *`inherited/` differs from JS2 only in its import lines.*
   `tests/test_inherited_is_unchanged.py` compares every file line by line and
   requires each differing line to be an import.
3. *A missing body is never a zero.* `tests/test_wrong_versions.py` —
   `test_W1_turns_157_unscorable_postings_into_rejects` and
   `test_the_real_pipeline_never_scores_a_posting_with_no_body`, plus
   `test_the_buckets_add_up`.
4. *Each amendment moved what it said it would.*
   `tests/test_amendment_a1.py`, `_a2.py`, `_a3.py`, each pinning a table
   written before the code changed.
5. *S5 cannot fire on this corpus.*
   `test_s5_cannot_fire_on_this_corpus` — none of these four boards says in
   words that a posting is open to new graduates.
6. *The scorer and the evidence rules never disagree about a sentence.*
   `test_the_scorer_and_the_evidence_rules_agree_about_every_body`, which
   found a real bug in A3 (a range read as its upper bound).
7. *Nothing trains, nothing calls a model, nothing reaches the network.*
   `tests/test_no_model_and_no_network.py`, which reads every shipped module.
8. *The tool server has no argument naming a location, and enforces its own
   schema.* `tests/test_toolserver.py`.
9. *The shortlist's claim totals and both worked cases.*
   `tests/test_shortlist_claims.py`.

**How** — honestly split:

- *By a test written before the code it tests:* items 1 and 4. All three
  amendments were written up with a predicted table, committed, and only then
  implemented; `reports/a2-predicted-effect.txt` and
  `a3-predicted-effect.txt` are the predictions as computed at the time.
- *By recomputation:* the amendment tables, recomputed over all 452 postings
  on every test run rather than stored.
- *By hand, by me:* the **48 blind labels** in `audit/labels-weiting.json`,
  which are the whole of `reports/reject-audit.md`; accepting A1, A2 and A3
  after reading each prediction and measurement; and declining a fourth
  amendment to `MIN_WALL_YEARS`.
- *With Claude's help:* everything else. Claude (Opus 5) wrote `FILTER.md`,
  every module, every test, the tool server and every report, in one session
  on 2026-11-23. It also found three defects against its own work unasked, the
  third of which deleted the best-looking entry in the submission
  (`SOURCES.md`).

**Not checked** — and these are real:

1. **Section headings are not read, so "nice to have" scores like "required".**
   Two of the six shortlisted postings — `Software Engineer, iOS` and
   `Software Engineer, Android` — score **all six** of their points from a
   NICE TO HAVES block, while their actual requirements are Swift, SwiftUI and
   a minimum of one year of mobile development. A third of the shortlist is
   matched on the optional list.
2. **157 postings (35% of the corpus) have no text at all.** Greenhouse sends
   no description on the endpoint JS2 called. They are in `cannot_score`,
   counted separately, and nothing in any report here speaks to them.
3. **`MIN_WALL_YEARS = 3` disagrees with an ordinary reading.** P-v3 read
   "Minimum 1 year of experience" as disqualifying; `evidence.py` labels the
   same posting `insufficient`. A number I picked against a reading anyone
   would make, left for the audit to settle.
4. **E-v1a cannot read "Senior" as a contradiction**, and the obvious repair
   is wrong — it would mislabel a posting whose sentence is "Partner closely
   with senior and staff ML engineers", where the adjective is about the
   colleagues.
5. **A1's denylist is fitted to this corpus.** I wrote it after seeing all 69
   distinct family values and after seeing how many postings each choice
   admits. It is not derived from principle, and an over-generous entry shows
   up only as a false positive in the kept sample.
6. **The Go language is undetectable.** A2 cut `go`, `golang` appears nowhere
   in the corpus, and nothing replaced it.
7. **`tests/test_inherited_is_unchanged.py` skips when the JS2 folder is
   absent.** A clone of this folder alone cannot check that the copies are
   faithful, which is the one case where they could drift unnoticed.
8. **The second tool server was evaluated with nine requests and a read of the
   import graph.** No hardlink test, no TOCTOU race, no NUL-byte path, and the
   `streamable-http` transport was never exercised.

**Not claiming** — what this agent does not show:

- **It does not show that these are good jobs.** 22 claims are supported by
  quoted spans; every one of them is a statement about the posting's *text*.
  Not one says the job is a fit, and E-v1a has no rule that would get there.
- **It does not show a false-negative rate.** The audit is a hand sample. Its
  output is "I checked *n* and disagreed with *k*", and no number in any report
  here is written as a rate for all 452 postings.
- **It does not show that Claude behaves this way.** The three responses in
  `evidence/claude-responses/` came from the same assistant that wrote the
  code, which knows what this filter is for. They are evidence about three
  prompts in one session.
- **It does not show that the filter would work on other boards.** Every rule
  here met exactly four, and A1 exists because a rule tuned on one of them did
  not survive the other two.
- **Nothing here was trained.** No gradient descent, no fine-tuning, no model
  call. The one fitted number is the threshold, fitted by trying each integer
  and counting agreements. A behaviour that persists is a file that persists.
- **It is not a system anyone should job-hunt with.** It reads 65% of what it
  collects, scores two of its six recommendations on their optional
  qualifications, and cannot tell you whether any of them will take a new
  graduate.

**Signed:** Weiting Wang — 2026-11-23

## Driver's seat

| decision | mine | Claude's | how to tell |
|---|---|---|---|
| Build layer 3 on my own JS2 rather than Lectern or the Reallocation Engine | ✅ | | `SOURCES.md`; `inherited/` differs only in import lines |
| The filter's rules, weights, caps and evidence rules | | ✅ | written in `FILTER.md`, which Claude wrote |
| The threshold T = 6 as a starting point | | ✅ | `FILTER.md` §1, declared hand-set |
| All implementation, tests, tool server and reports | | ✅ | stated plainly in `SOURCES.md` |
| Finding that F-v1 scored nothing, and the three false friends | | ✅ | `FRICTIONAL.md` §1–§3; reported unasked |
| **Whether a posting is worth my time — all 48 verdicts** | ✅ | | `audit/labels-weiting.json`, blind by construction |
| Accepting A1, A2 and A3 on their evidence | ✅ | | each is a prediction commit then a code commit |
| **Declining a fourth amendment** to `MIN_WALL_YEARS` | ✅ | | `FRICTIONAL.md` §5 |
| What the sign-off refuses to claim | ✅ | | I kept all eight "Not checked" items |

**Why the judgement that a posting is worth my time stays mine.** The filter
can tell me what a posting's text says — that is what the 22 supported claims
are, and every one of them quotes a span. It cannot tell me what I can do, what
I am willing to learn in three months, or which of two mediocre matches I would
actually turn up to. Those are facts about me, and the only place they exist is
in my own head.

The audit is the mechanism, not a gesture: the labels were taken **blind**, on
a form that showed no score and no bucket, before I saw what the filter had
decided. If my judgement were only a rubber stamp on the filter's, the audit
would agree with it everywhere, and that is a thing the numbers can show.

## Troubleshooting

**`FileNotFoundError: .../js2-loop-tools-diff/evidence/raw`.** JS3 reads the
postings JS2 captured. Run it from a clone that contains both folders, or pass
`--raw-dir`.

**`python3 -m jobfilter` prints nothing.** The subcommand is required: `run` or
`summary`.

**pytest collects another student's files.** Run it from inside
`js3-filter-tool-score/`, not from the repository root.

**`tools/evaluate_other_server.py` fails.** It needs npm and network access to
the npm registry. Everything else in this folder runs offline.
