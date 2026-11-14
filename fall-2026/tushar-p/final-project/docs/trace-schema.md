# Trace schema v1

Drafted by Claude Code, reviewed by Tushar
Date: Nov 13, 2026 (T2.5)

A trace is one run of one task: `traces/<run_id>.json`, written by `apg run` at the end of the run (`internal/trace.Write`). It records every host command the harness ran, every agent step, every check run, the budget, and the human gate, so a PASS or FAIL can be checked afterward without rerunning anything.

**Validation** uses the Go standard library only: `trace.Decode`, run by `trace.Write` on every trace before it is written, and by `TestEvidenceTraces` on every v1 trace in `evidence/traces/`.
1. A strict decode with `DisallowUnknownFields`: a key the schema does not know is an error.
2. Every key marked **required** below must be present.
3. The values must pass `Trace.Validate`:
   - `schema_version` is 1
   - `run_id` matches `^[A-Za-z0-9_-]+$`
   - `ended_at` is not before `started_at`
   - each command's `actor` matches its `phase`
   - steps are numbered 1..n
   - a denied step has a `rule` and a `reason`
   - `exit_reason` is on the fixed list
   - `exit_reason` is `error` exactly when the check did not run
   - `verdict` is PASS exactly when the deciding check exited 0
   - check-run triggers and gate decisions are known values
   - `budget` is present exactly when `model` is

## Older traces (v0)

Traces written before T2.5 are `schema_version: 0`. They are left in `evidence/traces/` exactly as they were and are not checked by `Decode` (it rejects them on `schema_version`). Compared with v1, v0:
- has no `actor` or `step` on commands
- records the policy's `realpath` lookups under phase `agent`
- duplicates the token and cost totals at the top level (`total_input_tokens`, `total_output_tokens`, `estimated_cost_usd`)
- in early traces, lacks the `budget`, `check`, `check_runs` and `gate` sections, which were added in T2.2–T2.4

The v0 traces in `evidence/traces/` (13):

| Trace | Run |
|---|---|
| `20261112T050512Z-3ddbacf5` | T1.3 `--no-agent`, FAIL `check_failed` |
| `20261112T050920Z-5dd372ce` | T1.3 bug-fixed copy, PASS |
| `20261112T053055Z-92239eb0` | T1.4 first agent run, PASS |
| `20261113T204817Z-a016749b` | T2.1 seeded run (scripted client), denied calls |
| `20261113T204837Z-3a19814c` | T2.1 model run, PASS |
| `20261113T211758Z-49d059aa` | T2.2 seeded timeout on kind |
| `20261113T211840Z-96b482d3` | T2.2 model run, PASS, budget section |
| `20261113T213318Z-f1a52be8` | T2.3 seeded run with a tamperer |
| `20261113T213336Z-b806fc06` | T2.3 model run, mid-run `check_passed` |
| `20261113T222626Z-2f2b40ec` | T2.4 gate approved: scripted answer via pseudo-terminal, not a human |
| `20261113T222801Z-3922d73c` | T2.4 gate refused: scripted answer via pseudo-terminal, not a human |
| `20261113T224740Z-a9a2c258` | T2.4 gate approved: human-answered by Tushar in a real terminal |
| `20261113T224827Z-cd9126a5` | T2.4 gate refused: human-answered by Tushar in a real terminal |

## Top level

| Field | Type | Req. | Set when | Written by |
|---|---|---|---|---|
| `schema_version` | int | yes | always; 1 for this schema | `runTask` (`trace.SchemaVersion`) |
| `run_id` | string | yes | always: UTC start time plus the pod suffix, e.g. `20261113T224740Z-a9a2c258` | `runTask` |
| `task_id` | string | yes | always, e.g. `001-fix-function` | `runTask` |
| `pod` | string | yes | always: the kind pod's name | `runTask` |
| `started_at`, `ended_at` | string (RFC 3339, UTC) | yes | always | `runTask` |
| `commands` | array of command | yes | always, in the order they ran (may be `[]`) | every phase |
| `steps` | array of step | yes | always; `[]` without an agent | agent loop |
| `exit_reason` | string | yes | always; why the run stopped (fixed list below) | `runTask`, after the final check |
| `verdict` | string | yes | always: `PASS` or `FAIL`, the deciding check's result (D11) | `runTask` |
| `check` | object | yes | always; the check that decided the verdict | `runTask` |
| `check_runs` | array of check run | yes | always; every time the check ran, in order (may be `[]`) | stop condition (`internal/stop`) |
| `error` | string | no | only when `exit_reason` is `error`: the harness failure | `runTask` |
| `model` | string | no | agent runs: the model ID, e.g. `claude-haiku-5-5` | `runAgent` |
| `prompt_version` | string | no | agent runs since T3.3: the SHA-256 (hex) of everything fixed the harness sends the model, i.e. the system prompt, the task-message template, the not-complete note, and every tool definition sorted by name (`loop.PromptVersion`). It does not cover the per-task goal. | `runAgent` |
| `loop_stop` | string | no | agent runs: why the loop ended: `end_turn`, `max_tokens`, `refusal`, `limit` (a budget, the timeout, or the policy-violation limit), or `check_passed` | agent loop |
| `budget` | object | no | agent runs (present exactly when `model` is) | `runAgent` |
| `gate` | object | no | when the human gate ran (`apg run`; tests may run without it) | gate phase |

**`exit_reason`**, the fixed list:
- `check_passed`, `check_failed`: the loop ended on its own, or a mid-run check passed, and the check decided.
- `budget_steps`, `budget_tokens`, `budget_cost`, `timeout`, `policy_violation_limit`: a limit stopped the loop. The check still ran, and the verdict is its result.
- `error`: the harness failed, and the check did not run.
- `gate_refused` and `gate_deferred` are on the list but never set: the gate's outcome is in `gate` (D23).

## command

One host command (`kubectl …`), as the sandbox ran it.

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `phase` | string | yes | When it ran (see the phase list below). |
| `actor` | string | yes | `agent` if it carried out an agent tool call, otherwise `harness`. Only phase `agent` has actor `agent`. |
| `step` | int | no | The agent step it belongs to (phases `agent` and `policy`); omitted otherwise. |
| `args` | array of string | yes | The exact argv run on the host, e.g. `["kubectl", "--context", "kind-kind", "-n", "apg-sandbox", "exec", "apg-…", "--", "cat", "/workspace/calc/ops.py"]`. Fake sandboxes in tests may leave it empty; the kind sandbox always fills it. |
| `stdout`, `stderr` | string | yes | Output, untruncated. |
| `exit_code` | int | yes | The host command's exit code; -1 if it could not run or its context expired. |

The phases:

| Phase | Actor | What runs |
|---|---|---|
| `start` | harness | `kubectl apply` of the pod, the wait for Ready, egress probes (`internal/sandbox`) |
| `setup` | harness | the repo copy into `/workspace`, `ls -A /workspace` |
| `agent` | agent | the commands that carry out a tool call: `cat` (read_file), `mkdir -p` and `kubectl cp` (write_file), `timeout 60 <argv>` (run_command) |
| `policy` | harness | the policy's `realpath -m -- …` lookups before a call runs (T2.1) |
| `fingerprint` | harness | `find /workspace … -exec sha256sum`: the baseline after setup, after each step, and around each check run (T2.3) |
| `check` | harness | the kill of every process except PID 1, the `__pycache__`/`*.pyc` cleanup, the check dir's mkdir, copy-in, the `bash check.sh` run, the kill again, the `rm -rf` (T2.3) |
| `gate` | harness | the kill and the copy of `/workspace` out, once per diff build (T2.4) |
| `stop` | harness | `kubectl delete pod` |

## step

One model turn and the (at most one) tool call it made. Written by the agent loop (`internal/loop`).

| Field | Type | Req. | Set when |
|---|---|---|---|
| `n` | int | yes | always; 1-based, consecutive |
| `stop_reason` | string | yes | always: the API's stop reason (`tool_use`, `end_turn`, `max_tokens`, `refusal`) |
| `text` | string | no | the model wrote text this turn (truncated to 8 KiB) |
| `tool` | string | no | the turn called a tool |
| `input` | string | no | the tool input as raw JSON text (truncated) |
| `output` | string | no | the result sent back to the model (truncated); for a denied call, `denied by policy (rule: …): …` |
| `exit_code` | int | no | something ran in the sandbox for this call |
| `is_error` | bool | no | the result was sent to the model as an error |
| `verdict` | string | no | the turn called a tool: `allowed` or `denied` (T2.1) |
| `rule`, `reason` | string | no | denied calls: the policy rule (`tool`, `input`, `path`, `check_file`, `program`, `flag`) and the reason sent to the model |
| `workspace_changed` | bool | no | the step changed `/workspace`, so the check ran after it (T2.3) |
| `input_tokens`, `output_tokens` | int | yes | always: this call's usage from the API (output includes thinking) |

## check

| Field | Type | Req. | Set when |
|---|---|---|---|
| `ran` | bool | yes | always; false only after `error` |
| `exit_code` | int | no | the check ran: 0 is PASS |

## check run

One run of the hidden check (`internal/stop`). Its output stays in the `check` commands; the model never sees it.

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `after_step` | int | yes | The step that changed `/workspace`; 0 for the final check. |
| `trigger` | string | yes | `workspace_changed` or `final`. |
| `exit_code` | int | yes | The check's exit code. |
| `passed` | bool | yes | `exit_code` is 0. |
| `killed` | int | yes | Processes killed before the check ran. |
| `workspace_sha256` | string | yes | The fingerprint of `/workspace` the check saw. |
| `changed_workspace` | bool | yes | The check run itself changed `/workspace`. |

## budget

Written by `runAgent` from the contract and the loop's totals (T2.2). This is the only place token and cost totals live in v1.

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `limits.max_steps` | int | yes | Model turns allowed. |
| `limits.max_total_tokens` | int | yes | Input plus output, over all calls. |
| `limits.max_cost_usd` | number | yes | Estimated cost cap, from the price table in `internal/budget`. |
| `limits.timeout_seconds` | number | yes | Wall-clock limit of the agent loop. |
| `limits.max_policy_violations` | int | yes | Denied calls allowed before the run stops. |
| `limits.max_reply_tokens` | int | yes | Per-reply cap; the worst case each pre-call check assumes (4,096). |
| `from_contract` | array of string | yes | Which limits the contract set; the rest are harness defaults. |
| `used.steps` | int | yes | Model calls made. |
| `used.input_tokens`, `used.output_tokens`, `used.total_tokens` | int | yes | Token totals from the API's usage. |
| `used.cost_usd` | number | yes | Estimated from list prices; not a bill. |
| `used.agent_seconds` | number | yes | Wall-clock time of the agent loop. |
| `used.policy_violations` | int | yes | Denied tool calls. |
| `used.count_tokens_calls` | int | yes | Pre-call token counts (free API calls, not in the totals). |

## gate

Written by the human gate (`internal/gate`, T2.4).

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `decision` | string | yes | `approved`, `refused`, `deferred`, `skipped` (empty diff, or the run failed), `void` (approved, but the diff changed or could not be rebuilt before export), or `error`. |
| `reason` | string | no | Why, for skipped, void, error, and deferred without a terminal. |
| `batch` | bool | no | since T3.3: eval mode (`apg eval`), where the gate always defers, whatever stdin is. | gate |
| `interactive` | bool | yes | stdin was a terminal. A pseudo-terminal counts, so this does not prove a person answered (docs/03). Four v1 traces were written before the T2.5 terminal fix and wrongly say `true` for stdin `/dev/null`: `20261113T230436Z-b034a8c4`, `20261113T230452Z-aca2acac`, `20261113T230507Z-9c042af9`, `20261113T230524Z-98800bd8`. They are kept as evidence of the bug. |
| `shown` | array of string | yes | What the approver saw: `diff`, `check_result`, `check_exit_code`, `exit_reason`, `diff_sha256_prefix`, plus `warnings` when the diff has WARNING lines. Empty when nothing was shown. |
| `diff_sha256` | string | no | SHA-256 of the exact diff bytes shown (or written, when deferred). |
| `diff_bytes` | int | yes | Length of that diff. |
| `recheck_sha256` | string | no | After an approval: the SHA-256 of the diff rebuilt from the pod. It must equal `diff_sha256`, or the approval is void. |
| `decided_at` | string (RFC 3339) | yes | When the decision was made. |
| `exported_path` | string | no | `out/<run_id>/approved.patch` or `pending.patch`; omitted when nothing left the sandbox. |
