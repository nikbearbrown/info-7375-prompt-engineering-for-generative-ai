# The permission policy: as written, as enforced, as tested

Claude Code drafted this page from the code and the record. The policy itself is the student's, in [GATE.md](GATE.md) ("Permission policy"). The predictions are the student's, in [policy/BOUNDARY-PREDICTIONS.md](policy/BOUNDARY-PREDICTIONS.md).

## As written (the student's words, from GATE.md)

> Allow HTTPS GET only on the configured list endpoints at `boards-api.greenhouse.io` and `api.ashbyhq.com`. […] Check the exact host, path, query, and method before sending. Refuse redirects and links found in postings. Use the local screening rule for this version and make no model calls.
>
> Read only the fictional persona, the watch state, and saved run evidence when needed. Write new evidence and results only under the current run's folder in `runs/`. Creating or replacing `state/state.json` requires my explicit approval for that file and that run, supplied locally before the run starts. […] Check containment against the fixed project paths, refuse parent traversal and symlink paths, and check approval separately from read access. Never apply, submit forms, email, message, log in, or access my real résumé or contacts.

Two of the student's later decisions belong to this policy (2026-11-08, each a choice between two readings of the gate that Claude Code laid out):
- An approval that names another run or another file counts as missing. The run ends `incomplete` and the state is not written.
- A board that answers with a redirect is not followed. That board is `unverified` and the run keeps going.

## As enforced: the checks, in the order the code makes them

**Requests**, in `jobwatch/policy.py` `Policy.check_request`, called by `jobwatch/loop.py` before every request:

| # | Check | Refusal names |
|---|---|---|
| 1 | The method is exactly `GET` | `method` |
| 2 | The scheme is `https` | `scheme` |
| 3 | The parsed host is `boards-api.greenhouse.io` or `api.ashbyhq.com`, with no user name, password or port in the URL | `host` |
| 4 | The whole URL, query included, is one of the four configured endpoints ([jobwatch/boards.py](jobwatch/boards.py)) | `endpoint` |

`jobwatch/net.py` uses `http.client`, which never follows a redirect. A 3xx reaches `loop.classify_response` as an answer and leaves that board `unverified`.

**Files**, in `Policy.check_file`, called by every method of `jobwatch/files.py`. Each method then operates on the path the policy returns.

| # | Check | Refusal names |
|---|---|---|
| 1 | The operation is `read` or `write` | `operation` |
| 2 | The path has no `..` part, even one that would land inside | `parent-traversal` |
| 3 | The path is inside the project folder | `outside-project` |
| 4 | No existing component between the project folder and the target is a symlink, even one that points inside | `symlink` |
| 5 | The resolved path is still inside the project folder | `outside-project` |
| 6 | A read is the persona, the state, or something under `runs/` | `not-readable` |
| 7 | A write is inside `runs/<this run>/`. Otherwise it is `state/state.json`, its temporary file `state/.state.json.*.tmp`, or the `state` folder | `not-writable` |
| 8 | A write from row 7's second list needs an approval naming this run and `state/state.json` | `approval` |

**The approval** is given on the command line before the run starts: `--approve-state RUN_ID:state/state.json` ([jobwatch/__main__.py](jobwatch/__main__.py)). Only a `finished` run tries the state write. Every approval in the tests is a SIMULATED fixture. The one real approval in this repository is the student's: they typed it for the run `2026-11-08-normal-1` ([their terminal output](evidence/terminal/2026-11-08-normal-1-run-by-student.txt)).

**Never apply, submit forms, email, message, log in.** No code path for any of these exists. On 2026-11-09 Claude Code searched `jobwatch/` for every file and network operation (`open`, `read_bytes`, `write_bytes`, `mkdir`, `unlink`, `replace`, `exists`, `HTTPSConnection`, `urlopen`, `socket`, `subprocess`, `smtplib`, `os.system`). The only file operations are in `files.Files`, which uses the path `check_file` returns, and in the policy's own symlink check. The one exception, in the CLI, was fixed test-first in `c17621e`. The only network call is `net.https_get`, which `loop.run` makes right after `check_request`. Nothing starts a process, sends mail, or posts anything.

## As tested

- **[policy/BOUNDARY-RESULTS.md](policy/BOUNDARY-RESULTS.md):** every boundary case, run through the real policy by [policy/boundary_table.py](policy/boundary_table.py), beside the student's prediction. **All 21 predictions match the outcome.** The 14 X cases are Claude Code's. Their expected results were written into `tests/test_policy.py` (`7db4ab4`) before the policy code existed (`208d1e3`).
- **[tests/test_policy.py](tests/test_policy.py):** the same cases as unit tests, each asserting which rule fires, plus tests that a refused write creates nothing and a refused read returns nothing.
- **[tests/test_wrong_versions_caught.py](tests/test_wrong_versions_caught.py):** GATE.md wrong versions 5 and 6 as code. Each is swapped in alone and must fail its named tests: write allowed because read was allowed; a URL-prefix host check; POST let through; redirects followed; `..` let through; containment by string prefix; no symlink check.

## What the testing showed that the predictions did not

1. **N6 matched for a different reason.** The student predicted that "links found inside postings aren't fetched". No rule about postings exists. The link `https://jobs.ashbyhq.com/...` is refused because its host is not on the allow-list (`host`). The outcome agrees; the mechanism is the allow-list.
2. **F7 alone cannot catch the classic string-prefix bug.** `runs-evil/R2/trace.json` is refused even by a policy that compares paths as strings, because writes are only allowed inside `runs/R2`, which `runs-evil/...` never starts with. The prefix bug shows up at **X13** (`runs/R2-evil/...` next to `runs/R2`) and **X14** (reading from `runs-evil/`). Claude Code found this while writing the wrong versions and added both cases before the code existed.
3. **With the symlink check removed, F8 is still refused,** by check 5 (`outside-project`) instead of check 4, and F9 then gets through. The test pins the rule that fires, so it catches that wrong version anyway.
4. **The student's policy is stricter than Chapter 5's reference.** It refuses any `..` and any symlink, even ones that stay inside (F6, F9, X1). The reference resolves the path and checks only where it lands.

## What this policy does not guarantee

Chapter 5's five limits, each tied to what was done here:

| Limit | Here |
|---|---|
| **Coverage:** it protects nothing that bypasses it | Checked by search on 2026-11-09 (above), not by a test. A new file or network call added later would need the same check. |
| **Authentication:** who supplied the approval? | Not checked. `--approve-state` is a string; nothing proves who typed it. In the one real case, the student's own pasted terminal output is the evidence. |
| **Time of check vs. time of use** | Not tested. `files.py` uses the path the policy resolved, but a folder swapped for a link between the check and the write is not defended against. |
| **Meaning:** an approved write can still be wrong | Shown, not prevented, by the policy. Before the review-packet patch, a run with an empty board finished and wrote state with full approval ([demos/finished-wrong-answer/](demos/finished-wrong-answer/)). The independent check, not the policy, caught it. |
| **Data beyond location** | The saved bodies are public job postings. Nothing classifies content, and nothing stops a later step from copying a saved file elsewhere. |
