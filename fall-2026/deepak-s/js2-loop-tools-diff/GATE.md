# GATE.md: exits, budgets, repeat rule, error policy and permission policy

Job-Search Agent 2, "The Loop, the Tools, and the Diff". Deepak Kumaran T S, INFO 7375, fall 2026.


Provenance: the first draft was written in a claude.ai chat (Claude Opus 5.5, 2026-11-10) from my plan. At Gate 1, Claude Code reviewed it against the brief and listed 21 gaps, contradictions and untestable rules. This revision, which answers those items, was drafted in the same claude.ai chat. My decisions: I have not independently read and accepted all 21 answers in the revised GATE.md in this review, so I will not claim that I did. My gate decisions are to keep boards.json writes protected, restrict the verify read exception to verification, mark the 100hires source as unread, require exact host-to-system matching, apply the corrected W12 fix, and keep write_file subject to the explicit approval policy rather than silently authorizing protected writes in non-interactive mode. I also agree that the W12 example must be corrected and that the Lever claim must have a source before being presented as verified.

Started from: my JS1 agent, "The Contract and the Watch", personal repo commit b91c877 (graded 95/100). Lectern and the Reallocation Engine were not used.

This file is the spec. If code and this file disagree, this file wins. If it is unclear or silent, Claude Code stops and asks.

## 0. Definitions

- **Board.** A board is identified by (system, slug), for example (lever, lever). The host is a separate config field and is not part of the identity. state/seen.json is keyed by "system:slug". Pointing a board at a different host keeps its history.
- **Config.** config/boards.json is an object. Its "boards" key is a list of {system, slug, host}. The other top-level keys (decided_by, decided_on, decision_ref, identity) are documentation. A board entry may also carry "deliberate_failure": true. That field is a label for readers only: the loop must behave identically with or without it, and a test checks this. Before any fetch, the loop validates the config: the system is greenhouse, lever or ashby; the host is in the section 5 allow-list and belongs to that system (greenhouse: boards-api.greenhouse.io; lever: api.lever.co or api.eu.lever.co; ashby: api.ashbyhq.com); and no (system, slug) appears twice. Any violation ends the run with ERROR before any fetch.
- **Run id.** A UTC timestamp, YYYYMMDDTHHMMSSZ. Each run writes runs/<run-id>/. "Earlier run" means a smaller run id.
- **Baseline.** If state/seen.json does not exist, every board is on its first observation. If state exists but a board is not in it, that board alone is on its first observation. A board on its first observation reports its posting count, new = 0 and "baseline": true. This matches JS1.
- **Corrupt state.** state/seen.json exists but cannot be read or does not validate. This is ERROR, not baseline.

## 1. Exits

Every run ends in exactly one exit. runs/<run-id>/summary.json and the process exit code always agree.

| Exit | Code | When | What it reports |
|---|---|---|---|
| FINISHED | 0 | Every planned board was fetched, validated and diffed within budget. | Per board: posting count, new ids, baseline flag, sha256 of the raw bytes. |
| INCOMPLETE | 3 | The loop visited every planned board, but at least one failed under the error policy. | Which boards failed, the HTTP status or error class, and retries used. |
| BUDGET_EXHAUSTED | 4 | A budget was reached before the plan was done (section 2). | Which budget, the value reached, the board in progress, and the boards not visited. |
| ERROR | 1 | Invalid config, corrupt state, a policy denial raised by our own code, or an unexpected exception. | The error, the step where it happened, and the fact that state was not updated. |

If more than one condition holds, the first in this order wins: ERROR, BUDGET_EXHAUSTED, INCOMPLETE, FINISHED.

These rules hold for every exit:
- A board that failed or was not visited is never reported as "0 new". Its count is null and its reason is recorded.
- state/seen.json changes only on FINISHED or INCOMPLETE, only for boards that succeeded, and only through one atomic replace at the end of the run.
- A clean exit is not proof of a right answer. `python -m jobwatch verify runs/<run-id>` is the independent check (section 7).

**Escalation to Deepak.** Every non-zero exit prints exactly one line to stderr: `jobwatch: <EXIT>: <cause>`. summary.json carries "needs_deepak": true for ERROR and for any denied approval.

## 2. Budgets

Values live only in config/budgets.json. The code reads that file and nothing else.

| Budget | Value | Counts |
|---|---|---|
| max_boards | 6 | boards planned for one run |
| max_requests | 20 | every HTTP request, retries included |
| max_seconds | 120 | wall-clock seconds from loop start |
| request_timeout_seconds | 10 | per request |
| min_seconds_between_same_host | 1 | spacing between requests to one host |
| max_retries_per_action | 1 | see section 4 |
| retry_backoff_seconds | 2 | wait before the one retry |

**When budgets are checked.** Before every request, retries included. If requests used equals max_requests, or elapsed seconds have reached max_seconds, no request is sent. The board in progress is FAILED with reason "budget", the remaining boards are unvisited, and the run exits BUDGET_EXHAUSTED.

**Too many boards.** If boards.json lists more than max_boards, the first max_boards in file order are planned. The rest are recorded as unvisited, and the run exits BUDGET_EXHAUSTED.

**Arithmetic check.** 6 boards with one retry each is 12 requests, under 20. In the worst case, 6 boards that all time out twice need about 6 x (10 + 2 + 10) = 132 s, over 120 s. That run ends BUDGET_EXHAUSTED by design rather than running long.

**Who may change a budget.** Only Deepak, by adding a dated entry below and committing it with the edited config/budgets.json. What the code enforces:
- there is no command-line flag for any budget (tested);
- a write to config/ needs approval (POLICY.md B12).
What presubmit checks: the decision_ref in budgets.json names an entry below. The dated entry itself is process, not code.

### Budget decisions
- B-1, 2026-11-10, Deepak: the values above. Reason: up to six boards with one retry each fit inside 20 requests, and 120 s covers timeouts plus backoff. The Phase 3 plan uses four boards.

## 3. Repeat rule

An action is identified by:
- a fetch: (tool, method, canonical URL). The canonical URL has a lowercase scheme and host, no default port, sorted query parameters and no fragment.
- a write: (tool, resolved real path).

What the loop does:
- The first fetch of an action runs. One retry is allowed only when section 4 permits it.
- Any further identical fetch in the same run is refused, logged as REPEAT in the trace, and the board is marked FAILED with reason "repeat".
- A second write to the same path in one run is refused.

**Bookkeeping exemptions.** These are still path-checked by the policy but are not actions under this rule:
- runs/<run-id>/trace.jsonl is appended one line per action through write_file(..., mode="append");
- runs/<run-id>/manifest.json and summary.json are each written once, at the end of the run;
- state/seen.json is replaced once, at the end of the run.

Signature: write_file(path, data, approval=None, mode="replace"). mode="append" is used only for trace.jsonl.

## 4. Error policy

Retry timing uses retry_backoff_seconds and max_retries_per_action from config/budgets.json.

| Condition | Retry | Board result | Why |
|---|---|---|---|
| HTTP 4xx other than 429 (for example the bad token, captured as a 404 with a JSON body) | none | FAILED | The answer is deterministic. A retry repeats it and spends budget. |
| HTTP 429 | none | FAILED, Retry-After recorded | The host asked us to slow down. Retrying would ignore that. |
| Timeout, connection error, HTTP 5xx | 1 | FAILED if the retry also fails | Likely transient. GET is idempotent and reads only public data, so a retry cannot change anything on the server. The retry counts against max_requests. |
| HTTP 200 whose content-type or body is not JSON | 1 | FAILED if the retry also fails | A defensive rule. A third-party Lever API guide reports intermittent HTML responses (https://100hires.com/lever-api.html, listed in SOURCES.md; not read by me). None appeared in our capture: all 3 Lever responses in evidence/manual-capture/CAPTURE.md were JSON. |
| HTTP 200, JSON, wrong shape | none | FAILED | A retry would return the same shape. |
| HTTP 3xx | none | FAILED, redirect refused | The permission policy forbids following redirects. |
| HTTP 200, JSON, valid shape, zero postings | none | OK with count 0 | Not an error to the loop, but it is the finished-wrong-answer risk. verify flags it (section 7). |
| Invalid config (section 0) | none | run exits ERROR before any fetch | A duplicate or unknown board would corrupt state keys. |
| Corrupt state | none | run exits ERROR before any fetch | Diffing against bad state would report wrong "new" postings. |
| An action that needs approval | none | see section 5, Approval | Approval belongs to Deepak. |

The loop never invents a value. A failed board has count null, its error saved, and its raw response bytes saved when there were any.

## 5. Permission policy

Enforced in jobwatch/policy.py, called by every tool in jobwatch/tools.py. Not enforced by any prompt.

**Network**
- Method: GET only.
- Scheme and port: https on 443 only. No userinfo in the URL. No IP literals (POLICY.md B16).
- Redirects: refused, never followed.
- Hosts, matched exactly after parsing:

| Host | System |
|---|---|
| boards-api.greenhouse.io | Greenhouse |
| api.lever.co | Lever (US) |
| api.eu.lever.co | Lever (EU) |
| api.ashbyhq.com | Ashby |

**Disk.** Paths are resolved with os.path.realpath, and containment is checked with os.path.commonpath.
- Read: config/, examples/, schema/, fixtures/, state/, runs/ inside this folder.
- Write: runs/<run-id>/ only.
- state/seen.json is changed only by the atomic replace at the end of a FINISHED or INCOMPLETE run.

**Needs Deepak's approval**
- resetting or overwriting state outside the end-of-run replace
- any write to config/

**Approval mechanism.** Interactive mode needs the --interactive flag and stdin attached to a TTY. In that mode the agent prints the action and path, and only the answer "y" approves. In every other case the action is denied, logged in the trace, and summary.json gets "needs_deepak": true. Tests inject an approver function instead of a TTY.

**Never, with or without approval**, and how each is enforced:

| Never | Enforced by |
|---|---|
| any method other than GET | policy.check rejects it (POLICY.md B05); a source-scan test finds no non-GET call site |
| apply, email, message or log in | by proxy: GET only, the host allow-list, and a source-scan test for smtplib and any POST, PUT, PATCH or DELETE |
| delete anything | tools.py has no delete tool; a source-scan test finds no os.remove, os.unlink, shutil.rmtree or Path.unlink in the package |
| read the home directory, SSH keys or credential files | path policy (POLICY.md B14) |
| read environment secrets | a source-scan test finds no os.environ or getenv in the loop path (loop, tools, policy, providers, verify and the loop and verify CLI). The JS1 judge modules are outside the loop path, and a test checks the loop never imports them. |
| contact a host not in the table above | policy.check (POLICY.md B01 to B04, B15, B16) |

## 6. Wrong versions the tests must catch

Plausible but wrong implementations. Each needs a test that fails against it. Phase 2 fills the last column.

| ID | Wrong version | Example input it gets wrong | Test that catches it |
|---|---|---|---|
| W01 | Path check with str.startswith | runs-evil/x.json beside runs/ | test_B08_prefix_trick; shown by test_W01_startswith_path_check_is_caught_by_B08 |
| W02 | Host check by substring or endswith | boards-api.greenhouse.io.evil.com; https://evil.com/boards-api.greenhouse.io | test_B02_suffix_trick_host; shown by test_W02_substring_host_check_is_caught_by_B02 |
| W03 | Host taken from the raw string, not the parsed URL | https://boards-api.greenhouse.io@evil.com/ | test_B03_userinfo_trick; shown by test_W03_host_from_raw_string_is_caught_by_B03 |
| W04 | Following redirects | a 302 from an allowed host (SEEDED mock transport) | test_B06_redirect_refused; shown by test_W04_following_redirects_is_caught_by_B06 |
| W05 | Path check without realpath | a symlink inside runs/ pointing outside | test_B09_symlink_escape; shown by test_W05_path_check_without_realpath_is_caught_by_B09 |
| W06 | Failed board counted as 0 new | a 404 board | test_404_board_counts_null_not_zero; shown by test_W06_failed_board_counted_as_zero_new_is_caught |
| W07 | Timeout reported as FINISHED | a board that times out twice (SEEDED) | test_timeout_twice_board_failed_run_incomplete; shown by test_W07_timeout_reported_as_finished_is_caught |
| W08 | Retries not counted against max_requests | many boards with 5xx (SEEDED) | test_retries_count_against_max_requests; shown by test_W08_retries_not_counted_is_caught |
| W09 | Retrying a 404 | a bad board token | test_404_fetched_once_no_retry; shown by test_W09_retrying_a_404_is_caught |
| W10 | Lever HTML body parsed as an empty list | an HTML 200 response (SEEDED) | test_html_200_is_failed_not_empty; shown by test_W10_lever_html_parsed_as_empty_list_is_caught |
| W11 | Empty 200 accepted with no independent check | an empty board that had postings last run | test_verify_flags_suspect_after_6_then_0; shown by test_W11_empty_200_with_no_independent_check_is_caught |
| W12 | Host included in board identity | the same board moved from api.eu.lever.co to api.lever.co gets a new state key, so the loop treats its second run as a baseline | test_identity_ignores_host; shown by test_W12_host_in_board_identity_is_caught |
| W13 | Duplicate (system, slug) accepted | one board listed twice with two hosts | test_duplicate_board_is_error; shown by test_W13_duplicate_board_accepted_is_caught |
| W14 | Host checked against the allow-list but not against the board's system | {system: greenhouse, host: api.lever.co} | test_host_system_mismatch_is_error; shown by test_W14_host_not_checked_against_system_is_caught |

## 7. Independent check

`python -m jobwatch verify runs/<run-id>` lives in jobwatch/verify.py.

**Independence**
- verify imports only the Python standard library. It imports no jobwatch module, including providers/ and the loop. A source-scan test enforces this.
- verify counts postings on its own: the length of the postings array, at the location for each system written in verify.py and taken from the bodies in evidence/manual-capture/, not from memory.
- So a parser bug like W10 cannot pass both the loop and verify.
- **Reads.** verify reads files with the standard library's open(path, "rb") only, and only under runs/, after its own realpath and commonpath containment check. It never writes, never uses the network, and prints its report to stdout. This is the one exception to "all disk access goes through tools.py". The source-scan test allows read-only open() in jobwatch/verify.py and nowhere else outside tools.py.

**What it checks**
- recomputes every board's count from the saved raw bytes, and checks each sha256 against the manifest
- SUSPECT: a board had more than 0 postings in its prior run and has 0 now
- UNCONFIRMED: a board's first observation is a 200 with 0 postings
- INVALID: a saved response is not JSON
- MISMATCH: its counts differ from summary.json

"Prior run" for a board is the latest earlier runs/<id>/ in which the same (system, slug) ended OK. Its count is recomputed from that run's raw bytes.

**Exit codes.** 0 when nothing is flagged; 2 when anything is flagged. 2 collides with no loop exit code.

A second independent check, outside the program, is my own manual curl capture in evidence/manual-capture/.

## Amendments

Amendments come after the Gate 1 commit 891446a. Each is dated and names the evidence that caused it.

- A-1, 2026-11-10, Deepak. Cause: evidence/pytest/20261110T193805Z-full-v.txt, 17 source-scan failures, all in modules imported unchanged from JS1 b91c877. Change: the source scans in section 5 and section 7 still scan every module in the package. These modules, imported unchanged from JS1, are named as legacy: jobwatch/fetch.py, judge_cli.py, experiment.py, evidence.py, labels.py, inputs.py, judge.py, prompt.py, replay.py, run.py, saved_run.py, state.py. A legacy module keeps its JS1 file and network behavior, and is reachable only through the JS1 subcommands. Any module not on this list that makes a forbidden call fails the scan. A test computes the transitive import closure of the loop path and fails if any legacy module is in it. The JS2 guarantees in section 5 (GET only, writes only under runs/, no delete, no environment reads) are claimed for the loop path, not for the legacy JS1 subcommands. test_legacy_modules_are_byte_identical_to_b91c877 checks that each legacy module is unchanged; persona.py holds a JS2 copy of the checks in JS1's load_resume (inputs.py at b91c877) so the loop path never imports inputs.py.
- A-2, 2026-11-10, Deepak. Cause: Gate 2 report. verify also lists directories under runs/ with os.listdir and os.path.isdir to find the prior run. This is read-only metadata access and is added to the section 7 Reads exception.
- A-3, 2026-11-10, Deepak. Cause: review of patch 3a4c1fb. If the final state replace fails after the run record was written, summary.json is rewritten exactly once with exit ERROR, so that summary.json and the exit code agree. This is the only permitted second write of summary.json. trace.md is rendered before the state replace and does not show it; trace.jsonl records it as its last line.

Wording drafted in the claude.ai chat; the decision is mine.
