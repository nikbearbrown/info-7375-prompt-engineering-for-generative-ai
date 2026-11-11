# GATE.md — Job-Search Agent 2: the exits and the policy, written first

Written and committed before Claude Code touched any `agent/` file. Nothing in
this file describes behaviour that was discovered by running the loop; where
the implementation later disagreed with this file, the disagreement is recorded
in `FRICTIONAL.md` and this file was amended with the amendment dated.

Author: Weiting W. (INFO 7375, Fall 2026)
Gate frozen: 2026-11-09
Policy version: **P-v1** · Loop version: **L-v1**

**Started from:** my own Job-Search Agent 1 (`../js1-contract-and-watch`), not
the Reallocation Engine and not Lectern. The allow-list check, the persona
guard, the R-v2 rule, the field-path resolver, the output validator and the
seen-ids state are carried over, file by file, and `SOURCES.md` says which
files are unchanged and which I modified. What is new in this layer is the
bounded loop, the budgets, the permission policy enforced in code, the
multi-ATS providers, the trace, and the independent cross-check.

---

## 1. Exits

The loop has exactly four terminal statuses. **A loop that stops is not a loop
that succeeded**, so the status is a field in the run report, not a tone of
voice, and three of the four are failures.

| status | when | what it reports |
|---|---|---|
| `finished` | every board in the plan was observed successfully, and no budget was exhausted | per-board counts, new postings, requests and seconds used, trace path |
| `incomplete` | the loop ran to the end of its plan but at least one board could not be observed after the error policy was applied | the same, **plus** which boards failed, with each one's classification and attempt count. The failed boards contribute **no** postings and are never reported as "0 new" |
| `budget_exhausted` | a budget limit (boards, requests, or seconds) was reached before the plan finished | which budget was hit, its limit, and the list of boards never attempted |
| `error` | the loop itself could not proceed: a permission refusal, an unwritable output root, or corrupt state | the exception class, the offending request or path, and nothing else — no partial posting list is emitted |

Two rules that make the statuses mean something:

- **E1.** `finished` is the only status under which the posting list is
  complete. Any consumer that treats the other three as "the answer, roughly"
  is misusing the report, so every report carries `complete: true|false`
  alongside the status.
- **E2.** Exit status is computed from the trace, not asserted by the code that
  wanted to succeed. `exit_status()` reads the recorded observations and
  derives the status; there is no code path that sets `finished` directly.

## 2. Budgets

| budget | limit | counted as |
|---|---|---|
| boards per run | **6** | entries in the plan actually attempted |
| HTTP requests per run | **12** | every outbound GET, **including retries** |
| wall-clock seconds per run | **90** | measured from the first request |
| retries per board | **2** | attempts after the first, per board |

The limits live in `config/budget.json`. **A budget changes only by a new
written decision**: an amendment in §8 of this file, dated, with a reason,
committed in the same commit as the new `config/budget.json`. The loop reads
the file; it never widens a limit at runtime, and a plan larger than
`boards` is truncated with the exit `budget_exhausted` rather than quietly
trimmed.

Who may change them: me. Not Claude Code on its own initiative, and not a
value passed on the command line — there is deliberately no `--max-requests`
flag, because a budget that any caller can raise is not a budget.

## 3. Repeat rule

**"The same action" is the pair `(method, url)` within one run.**

- The loop refuses to issue a `(method, url)` it has already issued in this
  run. The second attempt raises `RepeatedAction` and the run exits `error`.
- A **retry** is the one exception, and only when the error policy in §4
  authorised it. A retry is still counted against both `requests` (§2) and
  `retries per board`, so a board that flaps cannot consume the run.
- Across runs, repetition is the point — the whole agent is a watch. The rule
  is per run only.
- Why this rule and not "the same board": two different URLs on the same board
  (a listing and a pagination page) are two different actions, and the same
  URL reached through two different plan entries is one action that someone
  wrote down twice.

## 4. Error policy

On a board that fails, classify first, then act. **Never invent a value**: a
board that failed contributes no postings, and no failure is ever rendered as
"0 new postings".

| classification | trigger | action | why a retry here is or is not sound |
|---|---|---|---|
| `transient` | connection error, timeout, HTTP 5xx, HTTP 429 | retry up to 2 times, backoff 1s then 3s | the request is an idempotent GET on a public read-only endpoint, so a repeat is safe and the failure is plausibly transient. Counted against the request budget |
| `permanent` | HTTP 404, HTTP 403, unknown board token | **no retry**, mark the board failed, continue to the next board | retrying a board that does not exist cannot succeed; a retry would only spend budget and misrepresent one fault as three |
| `schema` | 200 but the body is not JSON, or has no postings array | **no retry**, mark the board failed, continue | the provider's shape changed or the token points at something that is not a board. A retry returns the same body. This is the class that must never be silently read as "no jobs" |
| `policy` | any refusal from §5 (`DisallowedHost`, `PathEscapes`, `NeedsApproval`, …) | **abort the whole run**, exit `error` | a policy refusal is a bug in the plan or in my code, not a fault in the world. Continuing would mean a run whose boundaries I no longer know |
| `budget` | a limit in §2 reached | stop issuing requests, exit `budget_exhausted` | — |

Escalation to me: `incomplete` and `error` both print a one-line
`ESCALATE:` summary naming the board and classification, and exit non-zero, so
a scheduled run cannot look successful in a log.

**One board in the plan is deliberately broken** so that this policy is
demonstrated rather than asserted: `config/boards.json` carries a Greenhouse
entry whose token does not exist. Predicted before running: classification
`permanent`, zero retries, the board reported as failed, the run exits
`incomplete`, and the other boards still produce their postings.

## 5. Permission policy (P-v1) — enforced in code, not in a prompt

The policy lives in `agent/policy.py` as a `Policy` object with three
gatekeeping methods. Every network call and every file write in the package
goes through it; there is no second path. It is enforced by Python, so it holds
whether or not a model is in the loop at all.

*This was not true when it was written — see §8 A3. Three of the four files the
agent writes bypassed `check_write` until 2026-11-09. The sentence stands
because the **code** was changed to make it true, which is the direction I want
this to be fixed in;
`tests/test_all_writes_go_through_the_policy.py` is what holds it.*

### 5.1 Network

- `ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.lever.co", "api.ashbyhq.com"}`
  — three hosts, three applicant-tracking systems.
- Scheme must be `https`. Port must be absent or 443.
- Method must be `GET`. There is no code path in the package that sends a
  request body, and `check_request` refuses any other method by name.
- Redirects are **not** followed; a redirect is a `transient`-class failure.
- Host matching is exact equality on the parsed hostname, lower-cased. Not
  `endswith`, not `in` — see wrong version W2.

### 5.2 Filesystem

- The agent may **write** only inside `OUTPUT_ROOT = evidence/`, decided by
  comparing fully resolved real paths (`Path.resolve()`, which resolves `..`
  and symlinks) and requiring `OUTPUT_ROOT` to be among the resolved path's
  parents. Writing to `OUTPUT_ROOT` itself is refused.
- The agent may **read** only `config/`, `data/`, `evidence/` and, for the
  cross-check, its own saved responses — and never a path matching
  `*.real.json`, which is the persona guard carried over from JS1.
- Read and write are separate permissions with separate methods, because a
  surface that may read a folder is not thereby allowed to write it.

### 5.3 Approval

A write that would **overwrite an existing file under `evidence/raw/`** needs
my explicit approval: without `--approve-overwrite` the call raises
`NeedsApproval` and nothing is written. Raw responses are the evidence this
submission rests on; silently replacing one is the single filesystem action I
most want to be unable to do by accident.

### 5.4 Never

No apply, no email, no message, no login, no form submission, no credential for
any board. Enforced structurally rather than by promise: the package imports no
HTTP method other than GET, no SMTP or mail library, no browser driver, and
reads **no environment variable at all**.

*Corrected after the freeze — see §8 A3. This said "reads no environment
variable except `ANTHROPIC_API_KEY` (used only by the carried-over Claude
judge, which is not part of the loop)", written while planning to carry JS1's
model judge across. It was not carried across: there is no `claude_judge` in
`agent/`, no API key is read, and no model is called anywhere in this package.
The correction makes the guarantee stronger, not weaker, and
`grep -rn "environ\|getenv" agent/` returns nothing.*

### 5.5 Boundary cases — predicted **before** running

Nineteen cases, with the outcome I expect written down here first. The table in
`reports/boundary-tests.md` repeats these predictions next to what actually
happened; `tools/boundary_table.py` generates that table by calling the real
`Policy`, and `tests/test_policy_boundaries.py` asserts the same 19 outcomes in
the suite. Both read their predictions from `tests/boundary_cases.py`, which
transcribes this table.

*Corrected after the freeze — see §8 A3. This paragraph said "Sixteen cases"
beside a table of nineteen rows, and credited the "actual" column to the test
file rather than to the generator. The predictions in the table below are
unchanged from the freeze commit `ce94b1f`; only this paragraph's prose was
wrong, and `git show ce94b1f:fall-2026/weiting-w/js2-loop-tools-diff/GATE.md`
shows the original.*

| # | request | predicted outcome |
|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/reddit/jobs` | **allow** |
| 2 | GET `https://api.lever.co/v0/postings/matterport` | **allow** |
| 3 | GET `https://api.ashbyhq.com/posting-api/job-board/ramp` | **allow** |
| 4 | GET `https://boards.greenhouse.io/v1/boards/reddit/jobs` (real but off-list host) | **deny** `DisallowedHost` |
| 5 | GET `https://boards-api.greenhouse.io.evil.example/v1/boards/reddit/jobs` (suffix trick) | **deny** `DisallowedHost` |
| 6 | GET `https://evil.example/?u=https://boards-api.greenhouse.io/` (allowed host in the query) | **deny** `DisallowedHost` |
| 7 | GET `http://boards-api.greenhouse.io/v1/boards/reddit/jobs` (plain http) | **deny** `DisallowedScheme` |
| 8 | GET `https://boards-api.greenhouse.io:8443/...` (odd port) | **deny** `DisallowedPort` |
| 9 | POST `https://boards-api.greenhouse.io/v1/boards/reddit/jobs` | **deny** `MethodNotAllowed` |
| 10 | write `evidence/raw/greenhouse-reddit.json` | **allow** |
| 11 | write `evidence/../../etc/passwd` (`..` traversal) | **deny** `PathEscapes` |
| 12 | write `evidence-evil/x.json` (prefix trick beside `evidence`) | **deny** `PathEscapes` |
| 13 | write `evidence/link/x.json` where `evidence/link` is a symlink to `/tmp` | **deny** `PathEscapes` |
| 14 | write `evidence/` itself | **deny** `PathEscapes` |
| 15 | read `data/resume.persona.json` | **allow** |
| 16 | read `data/resume.real.json` | **deny** `RefusedRealResume` |
| 17 | read `../../etc/passwd` | **deny** `PathEscapes` |
| 18 | write over an existing `evidence/raw/*.json` **without** `--approve-overwrite` | **deny** `NeedsApproval` |
| 19 | the same write **with** `--approve-overwrite` | **allow** |

Nineteen, not ten, because the categories the assignment names (off-list host,
`..`, a prefix trick, a symlink, read versus write, a write needing approval)
each deserve more than one shape.

## 6. The finished wrong answer, and the independent check

A run can exit `finished`, report truthfully that it saw no new postings, and
be wrong. The case I am building the check for: **a board that returns HTTP
200 with an empty postings array.** The loop has nothing to complain about —
the request succeeded, the schema parsed, there were zero postings, so zero
are new — and `finished` is the correct status for what the loop knows.

It is still wrong if the board actually has jobs and the token now points at a
retired or renamed board, or if the provider changed a field name so the
postings parse to nothing.

**The check must not be the agent's own report.** `tools/crosscheck.py` reads
the saved raw responses and the state file — not the run report — and flags:

- `SUSPECT_EMPTY`: a board observed with 0 postings whose previous recorded
  count in `evidence/state/` was greater than 0;
- `BELOW_FLOOR`: a board whose count is under the `expect_at_least` floor I
  wrote into `config/boards.json` by hand;
- `SUSPECT_TOTAL`: a run whose total postings fell by more than 50% against
  the previous run.

Predicted before running: the seeded empty board exits `finished` with "no new
postings", and the cross-check flags it `BELOW_FLOOR`. If the cross-check
stays silent on it, the check is wrong, not the agent.

## 7. Wrong versions the tests must catch

Real code in `tests/wrong_versions.py`, with the contract tests asserted to
**fail** on them.

- **W1 `failure_as_zero`** — folds a failed board into the report as
  `{"new": 0}` and still exits `finished`. Plausible because a failed board and
  an empty board look alike at the point where you build the summary row, and
  the row needs a number. Every count in the report is defensible; the run
  claims to be complete when a board was never observed. Caught by
  `test_exit_status_is_derived_not_asserted` and
  `test_a_failed_board_never_appears_as_zero_new`.
- **W2 `prefix_path_check`** — implements the write boundary as
  `str(path).startswith(str(output_root))`, which admits `evidence-evil/x.json`
  because the string does start with `evidence`. Plausible because it is the
  obvious one-liner and passes every test that only tries `..`. Caught by
  boundary cases 12 **and 14**.

  *Corrected after the freeze — see §8 A3. This said "caught by boundary case
  12", which was true and incomplete, and nothing was running the claim: W2 sat
  in `tests/wrong_versions.py` unused, so §7's assertion was about a test that
  never met the wrong version. It is now exercised, and it also fails case 14,
  the output root itself, because `startswith` cannot tell "inside the root"
  from "is the root" — so W2 would permit writing over `evidence/` itself. That
  is the more destructive of its two holes and it was not predicted.*
- **W3 `uncounted_retries`** — retries that do not count against the request
  budget, so a board that always times out spends requests without limit.
  Caught by `test_a_flapping_board_cannot_exceed_the_request_budget`.
- **W4 `repeat_allowed`** — no repeat rule: the same `(method, url)` issued
  twice in one run. Caught by `test_the_same_action_twice_in_one_run_is_refused`.

## 8. Amendments

Amendments after the freeze, each dated, with a reason. A budget or policy
change is an amendment; an amendment that changes what the loop reports is a
loop version bump.

- 2026-11-09 — none at freeze time.

**A1 — 2026-11-09, rule R-v2 → R-v2a (letter bump).** JS1's R-v2 read a
Greenhouse-shaped dict (`metadata[i].value`, `location.name`). JS2 watches three
applicant-tracking systems with no such paths, so the rule now reads
`agent.providers.base.Posting.for_rule()` and every justification carries both
the normalised field it compared and `provider_field`, the provider-native path
the value came from. A *letter* bump because it is not supposed to change any
verdict. That is not a promise, it is a test:
`tests/test_rule_carried_over.py` recomputes the rule over the 163 real postings
JS1 captured on 2026-10-31 and holds it to JS1's committed R-v2 verdicts.

**A2 — 2026-11-09, rule R-v2a → R-v3 (number bump).** G4 treated the substring
"remote" as though it were a location: when the persona had `remote_ok`, any
location containing "remote" passed the gate, so "Remote - Ontario, Canada"
counted as a place the persona could work. `remote_ok` is now a filter rather
than a bypass — a remote posting is rejected outright when the persona cannot
work remotely, and every posting, remote or not, must match a `locations_ok`
phrase to pass.

This is a *number* bump because it changes verdicts, and the amendment names
which ones before the diff is read: exactly two of JS1's 163 postings move,
both `relevant → not_relevant / G4_location`, both "Remote - Ontario, Canada"
(`greenhouse:7131934` Machine Learning Engineer, `greenhouse:6512458` Software
Engineer, Ads). `EXPECTED_MOVES` in `tests/test_rule_carried_over.py` is that
claim as a test, and it fails if a third verdict moves.

Procedure, in this order, each step its own commit so the order is checkable in
git: the defect was reproduced by a test written against the real capture and
committed while it still failed (`3a0896f`, output kept verbatim in
`review/before-patch-failure.txt`); then the patch; then the review. The record
is `review/review-packet.md`.

Not fixed by A2, and deliberately: G1 still infers seniority from title words
while these boards state it outright in a `Management Level` field. One change
per version — it is listed as a known defect in README.md's sign-off rather
than repaired in the same commit, where no review would cover it.

**A3 — 2026-11-09, permission policy P-v1 → P-v1a, plus two corrections to this
document.** Found while generating `reports/boundary-tests.md`: quoting §5's
sentence "every network call and every file write in the package goes through
it; there is no second path" into the report made me want to check it rather
than repeat it, and it was false. Saved responses went through
`Policy.check_write`. The run report (`agent/report.py`), the state file
(`agent/state.py`) and the trace (`agent/trace.py`) did not. The state file is
the one that bothers me most, because it is the agent's memory across runs and
it was the least protected of the four.

The 19 boundary cases of §5.5 could not have caught this, and that is the
useful part. They test whether the policy **decides** correctly, and it does —
19 of 19 still match these predictions. Whether every caller **asks** is a
different property, and nothing in the table was looking at it. The first
evidence of the gap was accidental: earlier the same day, a run pointed at a
directory outside the project refused to save its response and then wrote its
trace there anyway.

Closed by changing the code, not by weakening the sentence: `Trace`, `save()`
and `write()` take a policy and check the path before writing, and `agent/cli.py`
passes one at all three call sites. Test written first and committed red
(`12390f4`, output in `review/before-write-policy-fix.txt`), then the fix. The
suite now also reads `agent/*.py` for write primitives and fails if a module
that writes to disk never mentions `check_write`, so the next unchecked writer
surfaces as a test failure rather than in a sign-off.

A **letter** bump, P-v1 → P-v1a: no decision the policy makes changed, and
`reports/boundary-tests.md` still reports 19 of 19 against the frozen
predictions. What changed is how many callers are subject to it.

Two corrections to this document in the same amendment, both prose rather than
substance, both recorded here instead of being quietly edited:

- §5.5 said "Sixteen cases" above a table of nineteen rows. The table was
  always nineteen and is unchanged; the word was wrong.
- §5.5 credited the "actual" column of `reports/boundary-tests.md` to
  `tests/test_policy_boundaries.py`. It is generated by `tools/boundary_table.py`.
- §5.4 said the package reads no environment variable "except
  `ANTHROPIC_API_KEY`", for a carried-over Claude judge. The judge was never
  carried over, so the package reads no environment variable at all and calls
  no model. Corrected in the direction of the stronger claim, which is the
  direction that needs checking hardest: `grep -rn "environ\|getenv" agent/`
  returns nothing, and `tests/test_no_model_and_no_environment.py` asserts it.
- §7 said wrong version **W2** was "caught by boundary case 12", and no test
  ran it: `PrefixPathPolicy` sat in `tests/wrong_versions.py` unused, so the
  claim was about a test that had never met the wrong version. Now exercised —
  and W2 also fails **case 14**, the output root itself, because a `startswith`
  check cannot tell "inside the root" from "is the root". W2 would therefore
  permit writing over `evidence/`, the directory holding every saved response
  this submission rests on. The more destructive hole was the unpredicted one.

The freeze commit `ce94b1f` holds the original wording of both.

These new tests are **not** among the 19 pre-registered cases. They were
written after the freeze, and they say so in their own docstring.
