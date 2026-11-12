// Command apg runs tasks in the sandbox and records a trace.
//
//	apg run 001               run the agent, then the hidden check (T1.4)
//	apg run 001 --no-agent    run only the hidden check (T1.3)
package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
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

	"github.com/tushar-patel28/agent-proving-ground/internal/loop"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// model is the agent's model for now; contracts do not choose it yet.
const model = "claude-haiku-5-5"

const usage = `usage: apg run <task> [--no-agent] [--tasks dir] [--traces dir]
  <task> is the task number, e.g. 001
  --no-agent runs only the hidden check`

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
	if len(args) == 0 || args[0] != "run" {
		fmt.Fprintln(stderr, usage)
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
	// pod still gets deleted (Stop uses its own context).
	ctx, stopSignals := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stopSignals()
	ctx, cancel := context.WithTimeout(ctx, 10*time.Minute)
	defer cancel()

	sb, err := sandbox.NewKind()
	if err != nil {
		fmt.Fprintf(stderr, "apg run: %v\n", err)
		return exitError
	}
	var client loop.Client // nil means no agent
	if !opts.noAgent {
		client = loop.NewAnthropicClient()
	}
	tr := runTask(ctx, sb, sb.PodName(), tk, client)

	path, err := trace.Write(opts.tracesDir, tr)
	if err != nil {
		fmt.Fprintf(stderr, "apg run: write trace: %v\n", err)
		path = "<not written>"
	}
	fmt.Fprintf(stdout, "%s  %s  steps=%d  reason=%s  trace=%s\n",
		tk.Short, tr.Verdict, len(tr.Steps), tr.ExitReason, path)
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
}

// parseRunArgs accepts flags before or after the task number.
func parseRunArgs(args []string) (runOpts, error) {
	var o runOpts
	fs := flag.NewFlagSet("run", flag.ContinueOnError) // return errors instead of exiting
	fs.SetOutput(io.Discard)                           // we print our own usage
	fs.BoolVar(&o.noAgent, "no-agent", false, "run only the check")
	fs.StringVar(&o.tasksDir, "tasks", "tasks", "tasks directory")
	fs.StringVar(&o.tracesDir, "traces", "traces", "traces directory")

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
	MaxSteps     int
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
	tk.Goal, tk.AllowedTools, tk.MaxSteps = contract.Goal, contract.AllowedTools, contract.MaxSteps
	return tk, nil
}

// runTask starts the sandbox, copies the repo in, runs the agent (unless
// client is nil), then copies in and runs the check, and always stops the
// sandbox. Every host command goes into the trace. It never returns an
// error: failures become exit_reason "error" in the trace.
func runTask(ctx context.Context, sb sandbox.Sandbox, pod string, tk task, client loop.Client) *trace.Trace {
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
			tr.Commands = append(tr.Commands, trace.Command{Phase: phase, Result: r})
		}
	}

	// agent runs between setup and the check. It is a closure so it can
	// fill in tr; with no client it does nothing.
	agent := func() error {
		if client == nil {
			return nil
		}
		cfg := loop.Config{
			Model:     model,
			Goal:      tk.Goal,
			Tools:     tk.AllowedTools,
			MaxSteps:  tk.MaxSteps,
			MaxTokens: 16000,
		}
		res, err := loop.Run(ctx, client, sb, cfg, func(r sandbox.Result) { rec(trace.PhaseAgent, r) })
		tr.Model, tr.Steps, tr.LoopStop = model, res.Steps, res.Stop
		tr.TotalInputTokens, tr.TotalOutputTokens, tr.EstimatedCostUSD = res.InputTokens, res.OutputTokens, res.CostUSD
		if err != nil {
			return fmt.Errorf("agent: %w", err)
		}
		return nil
	}

	checkExit, err := setupAndCheck(ctx, sb, tk, rec, agent)

	// Stop always runs, with a fresh context: ctx may have timed out or been
	// cancelled by Ctrl-C. A failed Stop is recorded but does not change the
	// verdict (the pod also deletes itself after an hour).
	stopCtx, cancel := context.WithTimeout(context.Background(), time.Minute)
	defer cancel()
	r, stopErr := sb.Stop(stopCtx)
	rec(trace.PhaseStop, r)
	if stopErr != nil {
		fmt.Fprintf(os.Stderr, "apg run: warning: stop %s: %v\n", pod, stopErr)
	}

	switch {
	case err != nil:
		tr.ExitReason, tr.Verdict, tr.Error = trace.ReasonError, trace.VerdictFail, err.Error()
	case checkExit == 0:
		tr.ExitReason, tr.Verdict = trace.ReasonCheckPassed, trace.VerdictPass
	default:
		tr.ExitReason, tr.Verdict = trace.ReasonCheckFailed, trace.VerdictFail
	}
	tr.EndedAt = time.Now().UTC()
	return tr
}

// setupAndCheck returns the check's exit code, or an error if the harness
// itself failed (so a broken run is never reported as check_failed).
func setupAndCheck(ctx context.Context, sb sandbox.Sandbox, tk task, rec func(string, ...sandbox.Result), agent func() error) (int, error) {
	rs, err := sb.Start(ctx)
	rec(trace.PhaseStart, rs...)
	if err != nil {
		return 0, fmt.Errorf("start: %w", err)
	}

	// Setup. The trailing "/." makes kubectl cp copy the repo's contents
	// into /workspace instead of creating /workspace/repo. (filepath.Join
	// would drop the ".", so the string is built by hand.)
	r, err := sb.CopyIn(ctx, tk.Repo+string(filepath.Separator)+".", "/workspace")
	rec(trace.PhaseSetup, r)
	if err != nil {
		return 0, fmt.Errorf("copy repo: %w", err)
	}
	r, err = sb.Exec(ctx, "ls", "-A", "/workspace")
	rec(trace.PhaseSetup, r)
	if err != nil || r.ExitCode != 0 || strings.TrimSpace(r.Stdout) == "" {
		return 0, fmt.Errorf("workspace empty after copy (exit %d, err %v)", r.ExitCode, err)
	}

	// Agent. An agent failure (API or sandbox error) ends the run as
	// "error" without running the check.
	if err := agent(); err != nil {
		return 0, err
	}

	// Check: copied in only now, after setup and the agent, into a
	// directory with a random name so nothing can be planted there in
	// advance. Known gap: a process the agent left running could still find
	// and change it before it runs (T2.x).
	b := make([]byte, 8)
	if _, err := rand.Read(b); err != nil {
		return 0, err
	}
	checkDir := "/tmp/apg-check-" + hex.EncodeToString(b)
	r, err = sb.Exec(ctx, "mkdir", "-m", "700", checkDir)
	rec(trace.PhaseCheck, r)
	if err != nil || r.ExitCode != 0 {
		return 0, fmt.Errorf("mkdir %s (exit %d, err %v)", checkDir, r.ExitCode, err)
	}
	r, err = sb.CopyIn(ctx, tk.Check, checkDir+"/check.sh")
	rec(trace.PhaseCheck, r)
	if err != nil {
		return 0, fmt.Errorf("copy check: %w", err)
	}
	r, err = sb.Exec(ctx, "bash", checkDir+"/check.sh")
	rec(trace.PhaseCheck, r)
	if err != nil {
		return 0, fmt.Errorf("run check: %w", err)
	}
	if err := remoteExit(r); err != nil {
		return 0, fmt.Errorf("run check: %w", err)
	}
	return r.ExitCode, nil
}

// remoteExit tells a non-zero exit from the check apart from kubectl
// failing (for example, the pod is gone). When the command in the pod exits
// non-zero, kubectl exec prints "command terminated with exit code N" on
// stderr; any other non-zero exit is kubectl's own failure.
func remoteExit(r sandbox.Result) error {
	if r.ExitCode == 0 || strings.Contains(r.Stderr, "command terminated with exit code") {
		return nil
	}
	return errors.New("kubectl exec failed: " + strings.TrimSpace(r.Stderr))
}
