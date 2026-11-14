// Command apg runs tasks in the sandbox and records a trace.
//
//	apg run 001               run the agent, then the hidden check (T1.4)
//	apg run 001 --no-agent    run only the hidden check (T1.3)
//	apg eval --set dev        run every dev task, compare with the expected outcomes (T3.3)
//	apg show <run_id>         print a trace step by step (T3.4)
package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"os/signal"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/budget"
	"github.com/tushar-patel28/agent-proving-ground/internal/gate"
	"github.com/tushar-patel28/agent-proving-ground/internal/loop"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/stop"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// model is the agent's model for now; contracts do not choose it yet.
const model = "claude-haiku-5-5"

// maxReplyTokens caps each model reply. The budget check assumes every
// reply could use all of it. (16,000 until T2.3; task 001's longest reply
// so far was 304 tokens.)
const maxReplyTokens = 4096

// Time limits for the harness's own steps. The agent's limit comes from
// the contract (timeout_seconds); these are separate so that the check and
// the cleanup still run after the agent times out.
const (
	setupTimeout = 5 * time.Minute // start the pod, copy the repo in
	checkTimeout = 3 * time.Minute // copy in and run the hidden check
	gateTimeout  = 2 * time.Minute // each diff build for the gate (the person's think time has no limit)
	stopTimeout  = time.Minute     // delete the pod
)

const usage = `usage: apg run <task> [--no-agent] [--tasks dir] [--traces dir] [--out dir]
  <task> is the task number, e.g. 001
  --no-agent runs only the hidden check
  --out is where the human gate writes patches (default out/)`

// Process exit codes.
const (
	exitPass  = 0
	exitFail  = 1
	exitError = 2 // usage error or harness error
)

func main() {
	// main only wires up real stdout/stderr; run is testable on its own.
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

func run(args []string, stdout, stderr io.Writer) int {
	if len(args) > 0 && args[0] == "eval" {
		return evalMain(args[1:], stdout, stderr)
	}
	if len(args) > 0 && args[0] == "show" {
		return showMain(args[1:], stdout, stderr)
	}
	if len(args) == 0 || args[0] != "run" {
		fmt.Fprintf(stderr, "%s\n%s\n%s\n", usage, evalUsage, showUsage)
		return exitError
	}
	opts, err := parseRunArgs(args[1:])
	if err != nil {
		fmt.Fprintf(stderr, "apg run: %v\n%s\n", err, usage)
		return exitError
	}
	tk, err := findTask(opts.tasksDir, opts.task)
	if err != nil {
		fmt.Fprintf(stderr, "apg run: %v\n", err)
		return exitError
	}

	// NotifyContext cancels ctx on Ctrl-C, so the run stops early but the
	// pod still gets deleted (Stop uses its own context). Each phase of the
	// run sets its own time limit under ctx (runTask).
	ctx, stopSignals := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stopSignals()

	sb, err := sandbox.NewKind()
	if err != nil {
		fmt.Fprintf(stderr, "apg run: %v\n", err)
		return exitError
	}
	var client loop.Client // nil means no agent
	if !opts.noAgent {
		client = loop.NewAnthropicClient()
	}
	// The human gate. It prompts on stderr, so stdout keeps only the result
	// line. Without a terminal on stdin it always defers.
	g := &gate.Config{In: os.Stdin, Out: stderr, Interactive: isTerminal(os.Stdin), OutDir: opts.outDir}
	tr := runTask(ctx, sb, sb.PodName(), tk, client, g)

	path, err := trace.Write(opts.tracesDir, tr)
	if err != nil {
		fmt.Fprintf(stderr, "apg run: write trace: %v\n", err)
		path = "<not written>"
	}
	decision := "none"
	if tr.Gate != nil {
		decision = tr.Gate.Decision
	}
	fmt.Fprintf(stdout, "%s  %s  steps=%d  reason=%s  gate=%s  trace=%s\n",
		tk.Short, tr.Verdict, len(tr.Steps), tr.ExitReason, decision, path)
	if tr.Error != "" {
		fmt.Fprintf(stderr, "apg run: %s\n", tr.Error)
	}

	switch {
	case err != nil || tr.ExitReason == trace.ReasonError:
		return exitError
	case tr.Verdict == trace.VerdictPass:
		return exitPass
	default:
		return exitFail
	}
}

type runOpts struct {
	task      string
	noAgent   bool
	tasksDir  string
	tracesDir string
	outDir    string
}

// parseRunArgs accepts flags before or after the task number.
func parseRunArgs(args []string) (runOpts, error) {
	var o runOpts
	fs := flag.NewFlagSet("run", flag.ContinueOnError) // return errors instead of exiting
	fs.SetOutput(io.Discard)                           // we print our own usage
	fs.BoolVar(&o.noAgent, "no-agent", false, "run only the check")
	fs.StringVar(&o.tasksDir, "tasks", "tasks", "tasks directory")
	fs.StringVar(&o.tracesDir, "traces", "traces", "traces directory")
	fs.StringVar(&o.outDir, "out", "out", "gate output directory")

	// flag.Parse stops at the first non-flag argument ("001"). So: parse,
	// take one positional argument, and parse again on what follows, until
	// nothing is left.
	var positional []string
	for {
		if err := fs.Parse(args); err != nil {
			return o, err
		}
		if fs.NArg() == 0 {
			break
		}
		positional = append(positional, fs.Arg(0))
		args = fs.Args()[1:]
	}
	if len(positional) != 1 {
		return o, fmt.Errorf("want exactly one task, got %d", len(positional))
	}
	o.task = positional[0]
	return o, nil
}

// task is one task directory, e.g. tasks/001-fix-function.
type task struct {
	Short string // "001"
	ID    string // "001-fix-function"
	Dir   string
	Repo  string // copied into /workspace
	Check string // hidden check, copied in only after setup

	// From contract.json.
	Goal         string
	AllowedTools []string
	Limits       budget.Limits // the contract's limits, with harness defaults for the ones it leaves out
	FromContract []string      // which limits the contract set, by JSON name
	Expected     expectation   // the right outcome (T3.1); never sent to the model
}

// expectation is a task's right outcome, from contract.json "expected".
// Normal tasks expect PASS. A deliberate failure case expects FAIL, with
// the exit reasons a run will most likely end with and the reason no
// legitimate fix exists inside the sandbox. Only the goal is ever sent to
// the model; this is for the harness and for whoever reads the results.
type expectation struct {
	Verdict           string   `json:"verdict"`                       // PASS or FAIL
	LikelyExitReasons []string `json:"likely_exit_reasons,omitempty"` // FAIL tasks only
	WhyNoFix          string   `json:"why_no_fix,omitempty"`          // FAIL tasks only
}

// A task number is exactly three digits, so it is safe inside a glob.
var taskNumber = regexp.MustCompile(`^[0-9]{3}$`)

// findTask finds the single directory tasksDir/<short>-* and checks that
// it has repo/, check.sh, and a contract.json whose id matches the dir name
// and that has a goal, tools, and a positive step budget.
func findTask(tasksDir, short string) (task, error) {
	if !taskNumber.MatchString(short) {
		return task{}, fmt.Errorf("task %q: want a three-digit number like 001", short)
	}
	matches, err := filepath.Glob(filepath.Join(tasksDir, short+"-*"))
	if err != nil {
		return task{}, err
	}
	if len(matches) != 1 {
		return task{}, fmt.Errorf("task %s: want one directory %s-*, found %d", short, filepath.Join(tasksDir, short), len(matches))
	}
	dir := matches[0]
	tk := task{
		Short: short,
		ID:    filepath.Base(dir),
		Dir:   dir,
		Repo:  filepath.Join(dir, "repo"),
		Check: filepath.Join(dir, "check.sh"),
	}
	for _, p := range []string{tk.Repo, tk.Check} {
		if _, err := os.Stat(p); err != nil {
			return task{}, fmt.Errorf("task %s: %w", tk.ID, err)
		}
	}
	b, err := os.ReadFile(filepath.Join(dir, "contract.json"))
	if err != nil {
		return task{}, fmt.Errorf("task %s: %w", tk.ID, err)
	}
	var contract struct {
		ID           string   `json:"id"`
		Goal         string   `json:"goal"`
		AllowedTools []string `json:"allowed_tools"`
		MaxSteps     int      `json:"max_steps"`

		// Optional budget fields. Pointers, so a missing field (nil) can be
		// told apart from one set to 0, which is an error.
		MaxTotalTokens      *int64   `json:"max_total_tokens"`
		MaxCostUSD          *float64 `json:"max_cost_usd"`
		TimeoutSeconds      *float64 `json:"timeout_seconds"`
		MaxPolicyViolations *int     `json:"max_policy_violations"`

		Expected *expectation `json:"expected"` // optional when parsing; every real task has one (tasks_test.go)
	}
	if err := json.Unmarshal(b, &contract); err != nil {
		return task{}, fmt.Errorf("task %s: contract.json: %w", tk.ID, err)
	}
	switch {
	case contract.ID != tk.ID:
		return task{}, fmt.Errorf("task %s: contract id %q does not match directory", tk.ID, contract.ID)
	case strings.TrimSpace(contract.Goal) == "":
		return task{}, fmt.Errorf("task %s: contract has no goal", tk.ID)
	case len(contract.AllowedTools) == 0:
		return task{}, fmt.Errorf("task %s: contract allows no tools", tk.ID)
	case contract.MaxSteps <= 0:
		return task{}, fmt.Errorf("task %s: max_steps must be positive", tk.ID)
	}
	tk.Goal, tk.AllowedTools = contract.Goal, contract.AllowedTools
	if e := contract.Expected; e != nil {
		if err := e.validate(); err != nil {
			return task{}, fmt.Errorf("task %s: expected: %w", tk.ID, err)
		}
		tk.Expected = *e
	}
	tk.FromContract = []string{"max_steps"}
	tk.Limits = budget.Limits{
		MaxSteps:            contract.MaxSteps,
		MaxTotalTokens:      budget.DefaultMaxTotalTokens,
		MaxCostUSD:          budget.DefaultMaxCostUSD,
		Timeout:             budget.DefaultTimeout,
		MaxPolicyViolations: budget.DefaultMaxPolicyViolations,
	}
	// Each optional field, if present, must be positive and replaces the default.
	bad := func(name string) error { return fmt.Errorf("task %s: %s must be positive", tk.ID, name) }
	if v := contract.MaxTotalTokens; v != nil {
		if *v <= 0 {
			return task{}, bad("max_total_tokens")
		}
		tk.Limits.MaxTotalTokens = *v
		tk.FromContract = append(tk.FromContract, "max_total_tokens")
	}
	if v := contract.MaxCostUSD; v != nil {
		if *v <= 0 {
			return task{}, bad("max_cost_usd")
		}
		tk.Limits.MaxCostUSD = *v
		tk.FromContract = append(tk.FromContract, "max_cost_usd")
	}
	if v := contract.TimeoutSeconds; v != nil {
		if *v <= 0 {
			return task{}, bad("timeout_seconds")
		}
		// Seconds (float) to a time.Duration, which counts nanoseconds.
		tk.Limits.Timeout = time.Duration(*v * float64(time.Second))
		tk.FromContract = append(tk.FromContract, "timeout_seconds")
	}
	if v := contract.MaxPolicyViolations; v != nil {
		if *v <= 0 {
			return task{}, bad("max_policy_violations")
		}
		tk.Limits.MaxPolicyViolations = *v
		tk.FromContract = append(tk.FromContract, "max_policy_violations")
	}
	return tk, nil
}

// runTask starts the sandbox, copies the repo in, runs the agent (unless
// client is nil), then copies in and runs the check, and always stops the
// sandbox. Every host command goes into the trace. It never returns an
// error: failures become exit_reason "error" in the trace.
//
// Each phase has its own context and time limit, all under ctx (which
// Ctrl-C cancels): setup, the agent (the contract's timeout), and the
// check. So when the agent's deadline passes, only the agent's context is
// done; the check still runs, and Stop, which uses a fresh context of its
// own, still deletes the pod.
//
// After the verdict, while the pod is still alive, the human gate runs (if
// g is not nil and the harness did not fail): it is the only way a change
// leaves the sandbox.
func runTask(ctx context.Context, sb sandbox.Sandbox, pod string, tk task, client loop.Client, g *gate.Config) *trace.Trace {
	start := time.Now().UTC()
	tr := &trace.Trace{
		SchemaVersion: trace.SchemaVersion,
		RunID:         trace.NewRunID(start, strings.TrimPrefix(pod, "apg-")),
		TaskID:        tk.ID,
		Pod:           pod,
		StartedAt:     start,
	}
	// rec is a closure that appends to tr.Commands. "rs ...sandbox.Result"
	// makes it variadic: it takes any number of Results.
	rec := func(phase string, rs ...sandbox.Result) {
		for _, r := range rs {
			// ActorFor marks the command as the harness's own work, unless
			// the phase is agent (schema v1).
			tr.Commands = append(tr.Commands, trace.Command{Phase: phase, Actor: trace.ActorFor(phase), Result: r})
		}
	}

	// The stop condition (internal/stop): it fingerprints /workspace after
	// every agent step and runs the hidden check when something changed.
	checker := stop.New(sb, tk.Check, rec)

	var loopExit trace.ExitReason // set when a limit or a mid-run pass stopped the agent loop
	checkExit, err := func() (int, error) {
		// A func literal called at once: its defers (the cancels) run when
		// it returns, before Stop below.
		setupCtx, cancel := context.WithTimeout(ctx, setupTimeout)
		defer cancel()
		if err := setup(setupCtx, sb, tk, rec); err != nil {
			return 0, err
		}
		if err := checker.Baseline(setupCtx); err != nil {
			return 0, fmt.Errorf("setup: %w", err)
		}

		if client != nil {
			var err error
			loopExit, err = runAgent(ctx, sb, tk, client, checker, rec, tr)
			if err != nil {
				return 0, fmt.Errorf("agent: %w", err)
			}
		}
		if loopExit == trace.ReasonCheckPassed {
			// A step made the check pass; that run is the verdict.
			return 0, nil
		}

		// The final check, after every other exit. It gets its own context
		// from ctx, not the agent's (which may have timed out).
		checkCtx, cancel := context.WithTimeout(ctx, checkTimeout)
		defer cancel()
		return checker.Run(checkCtx, trace.TriggerFinal, 0)
	}()
	tr.CheckRuns = checker.Runs

	// The exit reason says why the run stopped; the verdict is the check's
	// result, whatever stopped the loop (D11). After a harness error the
	// check did not run, so the verdict is FAIL.
	switch {
	case err != nil:
		tr.ExitReason, tr.Verdict, tr.Error = trace.ReasonError, trace.VerdictFail, err.Error()
	default:
		code := checkExit
		tr.Check = trace.Check{Ran: true, ExitCode: &code}
		tr.Verdict = trace.VerdictFail
		tr.ExitReason = trace.ReasonCheckFailed
		if checkExit == 0 {
			tr.Verdict, tr.ExitReason = trace.VerdictPass, trace.ReasonCheckPassed
		}
		if loopExit != "" {
			tr.ExitReason = loopExit
		}
	}

	// The human gate, while the pod is still alive. Its outcome goes in
	// tr.Gate only; exit_reason stays the loop's (D23).
	if g != nil {
		if err != nil {
			tr.Gate = &trace.Gate{Decision: gate.DecisionSkipped, Reason: "the run failed (harness error): nothing is exported", Shown: []string{}, DecidedAt: time.Now().UTC()}
		} else {
			sum := gate.Summary{CheckRan: tr.Check.Ran, CheckExit: tr.Check.ExitCode, Verdict: tr.Verdict, ExitReason: tr.ExitReason}
			rg := gate.Run(ctx, *g, tr.RunID, sum, buildDiff(sb, tk, checker, rec))
			tr.Gate = &rg
		}
	}

	// Stop always runs, with a fresh context: ctx may have been cancelled by
	// Ctrl-C, and a phase may have timed out. A failed Stop is recorded but
	// does not change the verdict (the pod also deletes itself after an hour).
	stopCtx, cancel := context.WithTimeout(context.Background(), stopTimeout)
	defer cancel()
	r, stopErr := sb.Stop(stopCtx)
	rec(trace.PhaseStop, r)
	if stopErr != nil {
		fmt.Fprintf(os.Stderr, "apg run: warning: stop %s: %v\n", pod, stopErr)
	}
	tr.EndedAt = time.Now().UTC()
	return tr
}

// runAgent runs the agent loop under the contract's timeout and fills in
// the agent fields of tr. It returns what stopped the loop early (a limit,
// or check_passed from a mid-run check; "" if the model ended its turn) or
// a harness error.
func runAgent(ctx context.Context, sb sandbox.Sandbox, tk task, client loop.Client, checker *stop.Checker, rec func(string, ...sandbox.Result), tr *trace.Trace) (trace.ExitReason, error) {
	cfg := loop.Config{
		Model:     model,
		Goal:      tk.Goal,
		Tools:     tk.AllowedTools,
		Limits:    tk.Limits,
		MaxTokens: maxReplyTokens,
		Stop:      checker,
	}
	// The wall-clock budget: agentCtx is done when Timeout passes (or when
	// ctx is cancelled). cancel frees its timer if the loop ends early.
	agentCtx, cancel := context.WithTimeout(ctx, tk.Limits.Timeout)
	defer cancel()
	began := time.Now()
	res, err := loop.Run(agentCtx, client, sb, cfg, func(phase string, step int, r sandbox.Result) {
		tr.Commands = append(tr.Commands, trace.Command{Phase: phase, Actor: trace.ActorFor(phase), Step: step, Result: r})
	})
	elapsed := time.Since(began)

	tr.Model, tr.Steps, tr.LoopStop = model, res.Steps, res.Stop
	tr.PromptVersion = loop.PromptVersion()
	tr.Budget = &trace.Budget{
		Limits: trace.BudgetLimits{
			MaxSteps:            tk.Limits.MaxSteps,
			MaxTotalTokens:      tk.Limits.MaxTotalTokens,
			MaxCostUSD:          tk.Limits.MaxCostUSD,
			TimeoutSeconds:      tk.Limits.Timeout.Seconds(),
			MaxPolicyViolations: tk.Limits.MaxPolicyViolations,
			MaxReplyTokens:      maxReplyTokens,
		},
		FromContract: tk.FromContract,
		Used: trace.BudgetUsed{
			Steps:            res.Used.Steps,
			InputTokens:      res.Used.InputTokens,
			OutputTokens:     res.Used.OutputTokens,
			TotalTokens:      res.Used.TotalTokens(),
			CostUSD:          res.Used.CostUSD,
			AgentSeconds:     elapsed.Seconds(),
			PolicyViolations: res.Used.PolicyViolations,
			CountTokensCalls: res.CountTokensCalls,
		},
	}
	return res.Exit, err
}

// setup starts the sandbox and copies the repo into /workspace.
func setup(ctx context.Context, sb sandbox.Sandbox, tk task, rec func(string, ...sandbox.Result)) error {
	rs, err := sb.Start(ctx)
	rec(trace.PhaseStart, rs...)
	if err != nil {
		return fmt.Errorf("start: %w", err)
	}

	// The trailing "/." makes kubectl cp copy the repo's contents into
	// /workspace instead of creating /workspace/repo. (filepath.Join would
	// drop the ".", so the string is built by hand.)
	r, err := sb.CopyIn(ctx, tk.Repo+string(filepath.Separator)+".", "/workspace")
	rec(trace.PhaseSetup, r)
	if err != nil {
		return fmt.Errorf("copy repo: %w", err)
	}
	r, err = sb.Exec(ctx, "ls", "-A", "/workspace")
	rec(trace.PhaseSetup, r)
	if err != nil || r.ExitCode != 0 || strings.TrimSpace(r.Stdout) == "" {
		return fmt.Errorf("workspace empty after copy (exit %d, err %v)", r.ExitCode, err)
	}
	return nil
}

// buildDiff returns the gate's diff builder for this run: kill whatever is
// still running in the pod, copy /workspace out to a fresh host temp dir,
// and diff it against the task's original repo. The gate calls it twice
// for an approval: once to show the diff, once more just before export.
func buildDiff(sb sandbox.Sandbox, tk task, checker *stop.Checker, rec func(string, ...sandbox.Result)) gate.BuildFunc {
	return func(ctx context.Context) ([]byte, error) {
		ctx, cancel := context.WithTimeout(ctx, gateTimeout)
		defer cancel()
		if _, err := checker.Kill(ctx, trace.PhaseGate); err != nil {
			return nil, err
		}
		tmp, err := os.MkdirTemp("", "apg-gate-*")
		if err != nil {
			return nil, err
		}
		defer os.RemoveAll(tmp) // the copy is only needed to build the diff
		// kubectl cp to a path that does not exist yet creates it with
		// /workspace's contents. The content is untrusted: kubectl cp
		// refuses archive paths that would land outside it.
		ws := filepath.Join(tmp, "ws")
		r, err := sb.CopyOut(ctx, "/workspace", ws)
		rec(trace.PhaseGate, r)
		if err != nil {
			return nil, fmt.Errorf("copy /workspace out: %w", err)
		}
		return gate.Diff(tk.Repo, ws)
	}
}

// validate checks an expectation: PASS with nothing else, or FAIL with at
// least one exit reason from the fixed list and a written reason.
func (e expectation) validate() error {
	switch e.Verdict {
	case trace.VerdictPass:
		if len(e.LikelyExitReasons) > 0 || e.WhyNoFix != "" {
			return errors.New("a PASS task takes no likely_exit_reasons or why_no_fix")
		}
	case trace.VerdictFail:
		if len(e.LikelyExitReasons) == 0 || strings.TrimSpace(e.WhyNoFix) == "" {
			return errors.New("a FAIL task needs likely_exit_reasons and why_no_fix")
		}
		for _, r := range e.LikelyExitReasons {
			if !trace.ValidExitReason(r) {
				return fmt.Errorf("likely exit reason %q is not on the fixed list", r)
			}
		}
	default:
		return fmt.Errorf("verdict %q, want PASS or FAIL", e.Verdict)
	}
	return nil
}
