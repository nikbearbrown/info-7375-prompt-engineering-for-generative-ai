# PLAN.md — Agent Proving Ground

Build plan for Tushar Patel's INFO7375 final project. Every chat in this Project and every Claude Code session should read this file first.
**Update rule:** the copy in the repo is the live plan. When a task finishes, tick it here in the same commit (Claude Code can do this once Tushar has reviewed). Milestones go in the Milestone log, decisions in the Decision log. The claude.ai Project copy is a baseline only: re-upload it only when phases, tasks, or dates change, not for ticks.

- **Due:** Sun Dec 20, 11:59 pm ET. **Target submit:** Fri Dec 18.
- **Pace:** phase dates are latest-by dates. Work ahead whenever possible; finishing early is the goal.
- **Local repo:** `~/Documents/agent-proving-ground`
- **Public repo:** `github.com/tushar-patel28/agent-proving-ground`
- **Course folder (at submission):** `fall-2026/tushar-p/final-project/`
- **Build agent:** Claude Code, on Tushar's Claude subscription (university enterprise plan). Claude Code builds the project; it is not part of the system being built.

---

## Current status

- **Phase:** 2 — The full agentic loop
- **Next task:** T3.1
- **Last updated:** Nov 13, 2026

---

## How every task runs (the working loop)

1. Claude Code writes the task contract, checks, and tests; Tushar reviews and approves.
2. **Plan in Claude Code:** start `claude` in the repo, switch to plan mode, give it the task ID (for example "Do T1.2 from PLAN.md"). Review the plan before it edits.
3. **Claude Code implements.** Keep permission prompts on for commands and edits.
4. **Tushar reviews:** read the diff, run `go vet ./...` and `go test ./...`, and run the task's "Done when" check by hand.
5. **Commit** with the task ID in the message: `T1.2: kind sandbox via os/exec`.
6. **Log:** tell the claude.ai Project chat what went wrong or what you rejected (it keeps the friction log). Tushar writes FRICTIONAL.md at the end. Tick the task here, in the same commit.

Traces cited in PLAN.md or docs are copied to evidence/traces/ and committed; traces/ stays ignored.

## Course repo sync (at every milestone)

The personal repo is where the work happens, at your own pace. The course folder gets a copy at each milestone (M0–M8).

1. In the personal repo, commit everything and note the commit hash (`git rev-parse --short HEAD`).
2. Copy the tree, without `.git`, caches, binaries, or `.env`, into `fall-2026/tushar-p/final-project/` in the course repo.
3. Commit in the course repo with the message `M<n> sync from agent-proving-ground@<hash>`. Push.
4. Add the course commit hash to the Milestone log below.

In FRICTIONAL.md, link to personal-repo commits by full URL so a grader can open them.

**Driver's seat:** Claude Code implements everything; Tushar reviews and approves everything. FRICTIONAL.md stays in Tushar's own words.

---

## Phase 0 — Setup and Go basics (Oct 23 – Nov 5)

**T0.1 Install the toolchain** ✅ Done Oct 23: go1.27.3 darwin/arm64, Docker hello-world OK, git 2.52.0, Claude Code 2.1.306, harness API test call OK
1. Install Go 1.27.x (latest patch from go.dev/dl). Check: `go version`.
2. Install Docker Desktop. Check: `docker run hello-world`.
3. Install Git and the VS Code Go extension (includes gopls).
4. Check Claude Code: `claude --version`, signed in with your Pro account (it is already installed).
5. API key for the harness (needed from T1.4): create a Console workspace `apg-harness` with its own key and a spend limit (about $20 to start). Put `ANTHROPIC_API_KEY` in `~/.zshrc`, never in the repo.
- 🔎 **Research:** Claude Code plan mode, permission settings, and CLAUDE.md (code.claude.com/docs).
- **Done when:** all four tools print a version, and the test API call works with the harness key.

**T0.2 Create the repo** ✅ Done Oct 23: public repo github.com/tushar-patel28/agent-proving-ground, first commit df7b1bd pushed to main; `go build ./...` printed `go: warning: "./..." matched no packages`, exit 0
1. Create `~/Documents/agent-proving-ground`. Run `git init`.
2. Add `.gitignore` first (`.env`, `/bin/`, `/dist/`, OS and editor files). Commit.
3. Copy `PLAN.md` and `CLAUDE.md` (from this chat) into the repo root.
4. Run `go mod init github.com/tushar-patel28/agent-proving-ground`.
5. Add a stub `README.md` (one paragraph, future tense) and a `LICENSE`.
6. Create the public GitHub repo `agent-proving-ground` and push.
- 🔎 **Research:** pick a license (MIT vs Apache-2.0); Go module paths.
- **Done when:** the public repo shows the first commit, and `go build ./...` runs.

**T0.3 Go basics (by hand, no Claude Code)** ✅ Done Oct 31: dockerver exercise written by hand outside the repo, explained
1. Do the Tour of Go: basics, methods and interfaces, generics overview.
2. Read "Effective Go" sections on errors, interfaces, and package names.
3. Learn these, since the project uses them: modules and packages, structs and interfaces, error handling, `os/exec`, `encoding/json`, `context` (timeouts), `crypto/sha256`, `testing` with table-driven tests.
4. Exercise: write `scratch/dockerver/main.go` yourself. It runs `docker version --format json` via `os/exec`, parses two fields, and prints them. Add one table-driven test. Delete `scratch/` or keep it out of the build afterward.
- 🔎 **Research:** all of the above. This is the main Go learning stretch.
- **Done when:** you wrote and can explain the exercise without help.

**T0.4 Packet first drafts and logs** ✅ Done Nov 3: drafted by Claude Code, reviewed by Tushar
1. `docs/01-brief.md`: adapt PROJECT-BRIEF.md to the Go stack.
2. `docs/02-data-boundary.md`: every source labeled (tasks: synthetic; traces: synthetic; API key: credential, never stored).
3. `docs/06-premortem.md`: at least 3 predicted failures, written now, before the build. One of them becomes the controlled failure in Phase 6.
4. Start `FRICTIONAL.md` (your words, dated entries) and `SOURCES.md` (list Claude Code, the Claude models, the Go SDK).
- **Done when:** the three docs are committed with today's dates.

**T0.5 kind basics (by hand)** ✅ Done Nov 11: kind cluster from config, kubectl run/exec/cp, locked-down pod spec, deny-egress NetworkPolicy enforced
1. Install kind and kubectl. Check: `kind version`, `kubectl version --client`.
2. Create a cluster from a kind config file.
3. Run a pod, `kubectl exec` and `kubectl cp` into it, delete it.
- 🔎 **Research:** kind quickstart, Pod spec, `securityContext`, `automountServiceAccountToken`, resource limits, NetworkPolicy and whether kind's CNI (kindnet) enforces it.
- **Done when:** you can do the steps by hand.

**Milestone M0:** toolchain works, public repo exists, premortem committed.

---

## Phase 1 — First slice (Nov 6 – Nov 12)

Goal: one task, one kind pod, one trace file, one PASS/FAIL line.

**T1.1 Task 001 and the sandbox image** ✅ Done Nov 11: apg-sandbox:dev built (pytest 9.2.0, uid 1000) and kind-loaded; in a locked-down kind pod, check.sh failed on the untouched repo (1 failed, 3 passed), passed with the bug fixed, and failed on the hash when only the test file was edited
1. `tasks/001-fix-function/repo/`: a tiny Python package with one bug and one pytest file.
2. `tasks/001-fix-function/contract.json`: goal, allowed tools, step budget, required output.
3. `tasks/001-fix-function/check.sh`: runs pytest, and also checks that the test file was not changed.
4. `sandbox/Dockerfile`: `python:3.12-slim` with pytest preinstalled. Build it with `docker build` as `apg-sandbox:dev`, then `kind load docker-image apg-sandbox:dev`.
- **Done when:** running `check.sh` in a pod by hand fails on the untouched repo.

**T1.2 Sandbox interface and kind implementation** ✅ Done Nov 11: Go test started a pod, ran `echo hi`, copied a file in and out, and deleted it; with the deny-all-egress policy, TCP to 1.1.1.1:443 and DNS failed while a control pod without the policy connected. kindnet enforces NetworkPolicy (no Calico), but only ~1–2s after the pod is Ready, so `Start` waits until an egress probe is blocked; egress block confirmed by probe before agent runs (D19)
1. `internal/sandbox/sandbox.go`: interface `Sandbox` with `Start`, `Exec`, `CopyIn`, `CopyOut`, `Stop`.
2. `internal/sandbox/kind.go`: uses `kubectl` through `os/exec`. One pod per run.
3. Pod settings: non-root, drop all capabilities, no service-account token (`automountServiceAccountToken: false`), CPU and memory limits, default-deny egress NetworkPolicy.
4. Every command the sandbox runs is returned so it can be written into the trace.
5. A test pod tries to reach the internet and must fail. If kindnet does not enforce the NetworkPolicy, install Calico and document it.
- **Done when:** a Go test starts a pod, runs `echo hi`, and deletes it, and the egress test pod fails to connect.

**T1.3 First run without an agent (1a)** ✅ Done Nov 12: `apg run 001 --no-agent` printed `001  FAIL  steps=0  reason=check_failed  trace=traces/20261112T050512Z-3ddbacf5.json` and wrote the trace (11 host commands: start incl. egress probes, setup, check, stop; evidence/traces/20261112T050512Z-3ddbacf5.json); a bug-fixed copy (under the ignored traces/fixed-001/) gave `PASS reason=check_passed` (evidence/traces/20261112T050920Z-5dd372ce.json)
1. `internal/trace/trace.go`: trace schema v0 (run ID, task, steps, commands, exit reason, verdict).
2. `cmd/apg/main.go`: `apg run 001 --no-agent` runs only the check.
- **Done when:** it prints `001  FAIL  steps=0  reason=check_failed` and writes `traces/<run_id>.json`.

**T1.4 Minimal agent loop (1b)** ✅ Done Nov 12: `apg run 001` with `claude-haiku-5-5` printed `001  PASS  steps=3  reason=check_passed`; the agent read the repo and fixed `//` → `/` via `run_command`, then the hidden check passed (4 passed); 3,925 input / 437 output tokens, est. $0.000611 (evidence/traces/20261112T053055Z-92239eb0.json)
1. `internal/loop/loop.go`: send the task, receive tool calls, execute them in the sandbox, send results back, max 10 steps.
2. Tools for now: `read_file`, `write_file`, `run_command`.
3. After the loop ends, the harness runs the check. The check decides PASS or FAIL.
- 🔎 **Research:** Claude tool use (how tool_use and tool_result messages work), the Go SDK tool-use example.
- **Done when:** `apg run 001` prints PASS or FAIL, and the trace lists every step.

**Fallback (Thu Nov 12):** if task 001 cannot run on kind by Thu Nov 12, Claude Code writes `internal/sandbox/docker.go`. Log why (friction log in the claude.ai Project, then FRICTIONAL.md at the end) and the Decision log. Not triggered: task 001 ran on kind on Nov 12 (T1.3).

**Milestone M1:** first slice works end to end on kind.

---

## Phase 2 — The full agentic loop (Nov 13 – Nov 19)

**T2.1 Permission policy** ✅ Done Nov 13:
- **Tests first:** `internal/policy/policy_test.go` was committed before `policy.go` (commit 07a724f), and all 146 subtests pass.
- **run_command is now argv with no shell** (D20). The pod spec sets `workingDir: /workspace`.
- **Seeded run** (scripted client, no model, real kind pod; evidence/traces/20261113T204817Z-a016749b.json): 5 denied steps (path, program, flag ×2, and a symlink caught by `realpath` in the pod). The trace also shows the python limit: python's symlink creation and its read of /etc/hostname were allowed. Result `FAIL check_failed`.
- **Model run:** `apg run 001` with `claude-haiku-5-5` printed `001  PASS  steps=7  reason=check_passed`, with no denials; 10,977 input / 705 output tokens, est. $0.00145 (evidence/traces/20261113T204837Z-3a19814c.json).
- **Docs:** docs/03-action-surface-map.md drafted.
1. `internal/policy/policy_test.go` first: paths outside `/workspace` denied, commands not on the allowlist denied, tools not in the contract denied, check files not writable.
2. `internal/policy/policy.go`: every tool call goes through `policy.Check` before it runs. Denied calls are recorded in the trace and never executed.
- **Done when:** all policy tests pass, and a trace shows a denied call.

**T2.2 Budget and exits** ✅ Done Nov 13:
- **Budget:** the contract sets the limits, with harness defaults for any it leaves out: steps, total tokens, estimated cost, timeout, policy violations. Prices live in `internal/budget`, the only place. Before each model call the loop checks the timeout, then denied calls and steps, then whether the worst case fits: `count_tokens` input plus the full 16,000-token reply (D21).
- **Exit reasons:** a typed list, with `gate_*` reserved for T2.4. After every exit except `error` the check still runs, and the verdict is its result.
- **Tests:** `cmd/apg/exits_test.go` forces each of the 8 wired exits with a fake client.
- **Timeout on kind** (seeded, scripted `sleep 30`, 3 s timeout; evidence/traces/20261113T211758Z-49d059aa.json): `timeout` after 3 s, the check still ran (exit 1), and `kubectl get pod` returned NotFound afterwards.
- **Model run:** `apg run 001` with `claude-haiku-5-5` printed `001  PASS  steps=6  reason=check_passed`. Used 9,809 of 100,000 tokens, est. $0.00125 of $0.02, 10.8 s of 300 s, 0 of 3 violations, 6 count_tokens calls (evidence/traces/20261113T211840Z-96b482d3.json).
1. Budget: max steps, max tokens, estimated cost cap, wall-clock timeout (`context.WithTimeout`).
2. Exit reasons as a fixed list: `check_passed`, `check_failed`, `budget_steps`, `budget_tokens`, `budget_cost`, `timeout`, `policy_violation_limit`, `gate_refused`, `gate_deferred`, `error`.
- **Done when:** a test forces each budget exit.

**T2.3 Stop condition** ✅ Done Nov 13:
- **Tests first:** `cmd/apg/stop_test.go` and `stop_kind_test.go` were committed before `internal/stop` (commit bf07b04).
- **Stop condition:** after every step the harness fingerprints /workspace. If it changed, it kills every pod process except PID 1, then runs the check, kills again, and deletes the check dir before the next step. A pass stops the run. A failure tells the model only `The task is not complete yet.` end_turn only triggers the final check.
- **Reply cap:** 4,096 tokens.
- **check.sh:** now runs python with `-B`, because `-I` had ignored PYTHONDONTWRITEBYTECODE and the mid-run check left `__pycache__` files in /workspace.
- **Seeded kind run** (tamperer; evidence/traces/20261113T213318Z-f1a52be8.json): the tamperer was killed before the mid-run check, the check failed honestly, python found no check dir at the next step, and the run ended `FAIL check_failed`.
- **Model run:** `apg run 001` with `claude-haiku-5-5` printed `001  PASS  steps=4  reason=check_passed`. The mid-run check after step 4 (`write_file`) passed and the loop stopped; 5,659 tokens, est. $0.00074 (evidence/traces/20261113T213336Z-b806fc06.json).
1. `internal/stop/stop.go`: after each write action, the harness runs the hidden check. PASS stops the run.
2. If the agent says it is done, that only triggers the check. The model's word is never the verdict.
- **Done when:** a test shows that an agent saying "done" with a failing check does not produce PASS.

**T2.4 Human gate** ✅ Done Nov 13:
- **Tests first:** `internal/gate/gate_test.go` and `cmd/apg/gate_test.go` were committed before `internal/gate` (commit 38c30d2).
- **The gate:** after the verdict, with the pod alive, it kills leftover processes, copies /workspace out, and diffs it against the task repo, leaving out `__pycache__` and `.pytest_cache`. It shows the approver the diff, the check result and exit code, the exit reason, and the hash prefix, then asks approve / refuse / defer. It binds the decision to the SHA-256 of the bytes shown and rebuilds the diff before export (a mismatch is void). Without a terminal on stdin it defers.
- **T2.3 follow-up:** each check run deletes `__pycache__` after the kill, and the fingerprint ignores the caches.
- **Human-answered by Tushar in a real terminal** (`claude-haiku-5-5`):
  - `001  PASS  steps=4  reason=check_passed  gate=approved` (evidence/traces/20261113T224740Z-a9a2c258.json). The patch's SHA-256 equals `diff_sha256` = `recheck_sha256` (evidence/patches/20261113T224740Z-a9a2c258.approved.patch).
  - `gate=refused`, PASS `check_passed` in 5 steps (evidence/traces/20261113T224827Z-cd9126a5.json). Its out/ dir was never created, so nothing was written.
- **Scripted answer via pseudo-terminal, not a human** (Claude Code piped the answer into `script`):
  - approve (evidence/traces/20261113T222626Z-2f2b40ec.json; patch in evidence/patches/20261113T222626Z-2f2b40ec.approved.patch; `git apply --check` passed on a copy of the task repo)
  - refuse (evidence/traces/20261113T222801Z-3922d73c.json)
- **Known limit** (docs/03): the gate trusts whoever types at the terminal, and a pty can answer it.
1. `internal/gate/gate.go`: before any change leaves the sandbox, show the diff and the check output, then ask approve / refuse / defer.
2. Record the SHA-256 of the exact diff shown. If the diff changes, the approval is void.
3. In batch mode (`apg eval`), the gate always defers. Nothing is exported unattended.
- **Done when:** tests cover approve, refuse, defer, and a changed-diff approval being rejected.

**T2.5 Trace schema v1 and 5 tasks** ✅ Done Nov 13:
- **Schema v1** (`docs/trace-schema.md`): commands carry `actor` (agent | harness) and `step`, and `realpath` lookups have their own phase `policy`. The top-level token and cost totals are gone (`budget.used` only).
- **Validation:** `trace.Decode` decodes strictly (DisallowUnknownFields, required keys, value checks). `trace.Write` decodes every trace it writes, and `TestEvidenceTraces` decodes every v1 evidence trace (9 v1; the 13 v0 traces are kept as they were).
- **Small fixes:** every `*.pyc` is deleted before each check; the gate shows a WARNING line with path and size for every non-text file.
- **Tasks 002–005** (off-by-one, slugify, implement from a docstring, a fix across two files), with `reference.patch` for 001–005 outside `repo/`. `cmd/apg/tasks_test.go` runs each check in apg-sandbox:dev: FAIL untouched, PASS with the reference patch.
- **Bug found and fixed:** the T2.4 terminal check took `/dev/null` for a terminal. It now uses the tcgetattr ioctl.
- **Real runs** with `claude-haiku-5-5`, stdin `/dev/null`, after the fix:
  - `002 PASS steps=4`, `003 PASS steps=4`, `004 PASS steps=5`, `005 PASS steps=7`: all `reason=check_passed gate=deferred`, with `interactive: false`.
  - In 005, the check after step 6 (one file fixed) failed and the check after step 7 passed.
  - Evidence: evidence/traces/20261113T230736Z-5465d81d, …230750Z-8b6ebce6, …230804Z-ac0f7f94, …230821Z-607ddc3e. The pre-fix runs are kept and labelled in docs/trace-schema.md.
  - `001 PASS steps=5 gate=deferred` (20261113T230904Z-3d625236) gives 001 a v1 trace.
- **M2:** loop, tools, policy, stop and gate all exist with tests. The milestone row waits for the course-repo sync hash.
1. `docs/trace-schema.md`: every field explained.
2. Add tasks 002–005.
- **Done when:** all 5 tasks run, and each trace validates against the schema.

**Milestone M2:** loop, tools, policy, state, stop, and gate all exist and have tests.

---

## Phase 3 — Task suite and evaluation harness (Nov 20 – Nov 23)

**T3.1 Grow the suite to 12–20 tasks**
1. Include at least 5 deliberate failure cases, each meant to make the system say no. Ideas: a task that tempts editing the tests, a task that needs network, a task that needs a forbidden tool, a task that cannot fit the budget, a task with an impossible spec.
- **Done when:** every task has a contract, a check, and a one-line purpose in `tasks/README.md`.

**T3.2 Freeze the split (before any prompt tuning)**
1. `tasks/split.json`: dev vs held-out.
2. Commit it. Write the commit hash in `docs/07-evidence.md`.
- **Done when:** the split commit exists and no prompt tuning happened before it.

**T3.3 `apg eval`**
1. Runs a set of tasks, prints the results table (task, PASS/FAIL, steps, denied (blocked tool calls), exit reason, cost), and appends to `results/eval-log.jsonl`.
2. Each eval-log entry records the model and the contract version.
- **Done when:** `apg eval --set dev` prints the table.

**T3.4 `apg show <trace>`**
1. Readable step-by-step trace printout in the terminal.
- **Done when:** `apg show traces/<run_id>.json` prints every step.

**Milestone M3:** suite frozen, eval command works.

---

## Phase 4 — Isolation proof (Nov 24 – Nov 29, light)

**T4.1 Isolation tests**
1. One test per sandbox limit: no network, non-root, no service-account token, CPU and memory limits enforced.
2. Save the results for `docs/07-evidence.md`.
- **Done when:** every limit has a passing test and the results are saved.

**Milestone M4:** isolation tests pass, results saved.

---

## Phase 5 — Evaluation runs (Nov 30 – Dec 3)

**T5.1 Two prompt contracts**
1. Write contract A and contract B (for example, terse vs detailed instructions).
2. Run both on the held-out set, at least 3 runs each, same model and settings.
- **Done when:** the eval log holds both, with pass rates side by side.

**T5.2 Honest limits**
1. In `docs/07-evidence.md`, write what a sample of this size can and cannot show.

**T5.3 `apg compare <run-a> <run-b>`**
1. Prints per-task changes and the pass-rate delta between two runs (a prompt or model change).
- **Done when:** `apg compare` on the two T5.1 contract runs prints per-task changes and the pass-rate delta.

**Milestone M5:** comparison results saved, limits written.

---

## Phase 6 — Controlled failure and audit (Dec 4 – Dec 9)

**T6.1 Controlled failure**
1. Pick one failure from the premortem (for example, the agent edits the test file to make it pass).
2. Trigger it on purpose. Save the trace.
3. Show the independent check that catches it (for example, the check's hash of the test file).
4. Recover: fix, review the fix, rerun, save the new trace.
- **Done when:** one command reproduces the failure, and the evidence doc shows all four steps.

**T6.2 Remaining packet docs**
1. `docs/03-action-surface-map.md`, `docs/04-plan.md` (the packet's plan, not this file), `docs/05-gates.md`.
2. `docs/07-evidence.md`: exact commands and results, labeled as code inspection, fixture output, model output, or human observation.
3. `docs/09-audit-note.md`: your predictions first, then a reviewer's findings (judged genuine or false positive), failed cases, and the Gap Account.
4. `FAILURES.md`: short failure analysis (light, may grow).

**Milestone M6:** controlled failure done, 9 of 10 packet docs drafted.

---

## Phase 7 — Ship readiness (Dec 10 – Dec 15)

1. **T7.1 README and demo script:** what it is, toolchain list, exact commands, results table, what ran, what did not, and a "Changes since the pitch" section. Add `./demo.sh`: checks prerequisites, builds the image, creates the cluster if missing, loads the image, runs task 001, prints the result line and trace path.
2. **T7.2 Fresh-clone test:** clone into a new folder, follow only the README.
3. **T7.3 Stranger run:** someone who did not help runs it. Write `STRANGER-RUN.md`.
4. **T7.4 Demo:** 5 minutes or less, showing the loop, tools, and gate. Record its filename and SHA-256. Keep the MP4 out of GitHub.
5. **T7.5 Sign-off and driver's seat:** what you checked, how, real "Not checked" entries, what you are not claiming. A driver's-seat table: what Claude Code did, what you did, and why.
6. **T7.6 Link check:** open every link between the ten docs and confirm each says what the link claims.
- 🔎 **Research:** GitHub Actions for `go vet` and `go test` (optional, good for the resume), and a terminal recording tool.

**Milestone M7:** a stranger ran it from the README.

---

## Phase 8 — Submit (Dec 16 – Fri Dec 18; Dec 19–20 buffer)

1. **T8.1** Finish `SOURCES.md` and `docs/10-transfer-reflection.md` (ship / narrow / defer / stop, with reasons). Finish `FRICTIONAL.md` in your own words.
2. **T8.2** Tag `v1.0` in the public repo.
3. **T8.3** Final sync: run the Course repo sync steps from the `v1.0` tag. Add your repo link, tag, and commit hash to the course folder's README. Commit and push.
4. **T8.4** Build `Patel_Tushar_INFO7375_FinalProject.zip` from that course folder.
5. **T8.5** Submit on Canvas with the course repo folder link, the commit hash, your repo link and tag, and the run instructions.

**Milestone M8:** submitted.

---

## Stretch (only if ahead of schedule)

- GitHub Actions badge in the README.
- A short write-up in the README of the most interesting failure found.

---

## Research list (quick view)

| When | Topic |
|---|---|
| T0.1 | Claude Code plan mode, permissions, CLAUDE.md |
| T0.2 | License choice, Go module paths |
| T0.3 | Go basics (main learning stretch) |
| T0.5 | kind, Pods, securityContext, SA token, limits, NetworkPolicy in kind |
| T1.2 | kind pod isolation settings |
| T1.4 | Claude tool use, Go SDK tool-use example |
| T7.x | GitHub Actions for Go, terminal recording |

---

## Decision log

| ID | Date | Decision | Status |
|---|---|---|---|
| D1 | Oct 22 | Whole platform in Go (TA confirmed any language is allowed) | Decided |
| D2 | Oct 22 | Official Anthropic Go SDK; agent loop written by hand | Partly superseded Nov 3 by D14 (loop now by Claude Code; Go SDK unchanged) |
| D3 | Oct 22 | Tasks are small Python repos checked with pytest in the container | Decided |
| D4 | Oct 23 | Plain Docker first; kind cutoff Sun Nov 22 | Superseded Nov 3 by D16 |
| D5 | Oct 23 | Target submit Fri Dec 18 | Decided |
| D6 | Oct 23 | Build with Claude Code on the Pro plan. omp dropped: since Apr 4, 2026, Pro limits no longer cover third-party harnesses, so omp would bill per token | Decided (Oct 23, revised) |
| D7 | Oct 23 | Local repo `~/Documents/agent-proving-ground`; public repo `agent-proving-ground` | Decided |
| D8 | Oct 23 | Full project lives in the course folder (graded copy). Build in the personal repo; sync to the course folder at every milestone; final sync from the `v1.0` tag | Decided (Oct 23) |
| D9 | Oct 23 | Go talks to Docker (and later kubectl) through the CLI via `os/exec` | Partly superseded Nov 3 by D16 (kubectl primary; docker for image builds and fallback; os/exec unchanged) |
| D10 | Oct 23 | Task contracts in JSON (standard library only) | Decided (Oct 23) |
| D11 | Oct 23 | Verdict comes only from the harness-run hidden check | Decided (Oct 23) |
| D12 | Oct 23 | Gate bound to the SHA-256 of the diff shown; batch mode always defers | Decided (Oct 23) |
| D13 | Oct 23 | Personal repo public from the start | Decided |
| D14 | Nov 3 | Claude Code writes the agent loop (pitch said hand-written; noted in README changes and driver's seat) | Decided |
| D15 | Nov 3 | Add apg compare, denied column, apg show, FAILURES.md, demo.sh | Decided |
| D16 | Nov 3 | Kubernetes (kind) from the start; Docker sandbox only as fallback after Nov 12 | Decided |
| D17 | Nov 3 | Claude Code drafts packet docs; Tushar reviews | Decided |
| D18 | Nov 11 | Claude Code implements everything; Tushar reviews and approves | Decided |
| D19 | Nov 11 | kindnet enforces NetworkPolicy ~1–2 s after Ready; Start probes until egress is blocked (30 s limit, fail and delete pod), probes recorded with Start's commands | Decided |
| D20 | Nov 13 | run_command takes an argv list and runs with no shell (`timeout 60 <argv>`), so the program allowlist means something; symlinks are caught by running `realpath -m` in the pod before a call runs; sed always gets `--sandbox`; the pod sets `workingDir: /workspace`. python/pytest still run arbitrary code: the pod is the boundary (docs/03) | Decided |
| D21 | Nov 13 | Budget exits: the exit reason says why the loop stopped and the verdict is still the check's result (PASS with `budget_steps` is possible); the timeout covers the agent loop only (setup, check and stop have fixed harness limits, so the check and pod cleanup run after a timeout); a step starts only if `count_tokens` input + the full per-reply max_tokens fits the token and cost limits; Ctrl-C is `error`, not `timeout` | Decided |
| D22 | Nov 13 | Stop condition: the check runs after any step that changes /workspace (sha256 fingerprint of every regular file, taken by the harness), and a pass stops the run; the model hears only "The task is not complete yet."; before every check run all pod processes except PID 1 are killed, and the check dir is deleted before the next step; reply cap 4,096 tokens | Decided |
| D23 | Nov 13 | The gate's outcome goes in the trace's `gate` section, not in `exit_reason`. exit_reason stays the loop's reason, and `gate_refused`/`gate_deferred` stay on the fixed list but are never set. Why: `apg eval` is never interactive, so its gate always defers, and every eval row would otherwise read `gate_deferred`, hiding why the loop stopped. The gate is bound to the SHA-256 of the exact diff shown, and the diff is rebuilt from the pod before export | Decided |
| D24 | Nov 13 | Trace schema v1: every command says who it was for (actor agent/harness, step), the policy's realpath lookups get phase `policy`, totals live only in budget.used; traces are read back with a strict standard-library decode, and v0 traces stay as they were. "stdin is a terminal" is decided by the tcgetattr ioctl, not the file mode | Decided |

---

## Open questions

- Ask the TA: OK for FRICTIONAL.md to link personal-repo commits?

---

## Milestone log

| ID | Date | Milestone | Evidence (commit / file) |
|---|---|---|---|
| — | Oct 22 | Pitch film resubmitted with the Go stack; graded 50/50 | course repo commit e9bef08 |
| M0 | Nov 3 | Toolchain works, public repo exists, premortem committed; synced to the course folder | course repo commit 73af1fc (from agent-proving-ground@2a1a722) |
| M1 | Nov 12 | First slice works end to end on kind (T1.1–T1.4: `apg run 001` PASS with claude-haiku-5-5, evidence/traces/20261112T053055Z-92239eb0.json); synced to the course folder | course repo commit 8349ba9a (from agent-proving-ground@e3454c0) |
