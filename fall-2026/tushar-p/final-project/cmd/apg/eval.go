package main

// apg eval (PLAN.md T3.3): run every task of a split set through the same
// code path as apg run, compare each verdict with the task's expected
// outcome, print a results table, and append a record to
// results/eval-log.jsonl (and regenerate results/EVAL-LOG.md).
//
// The gate always defers in eval: it is set by eval mode (gate.Config.Batch),
// never inferred from stdin, so nothing is exported unattended.

import (
	"bufio"
	"bytes"
	"context"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"strings"
	"text/tabwriter"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/gate"
	"github.com/tushar-patel28/agent-proving-ground/internal/loop"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

const evalUsage = `usage: apg eval --set dev|held-out [--runs N] [--held-out-ok] [--tasks dir] [--traces dir] [--out dir] [--results dir]
  runs every task of the set (in tasks/split.json order), N times each
  --held-out-ok is required for --set held-out, which is reserved for T5.1`

// Outcomes of one eval row: how the verdict compares with the expected one.
const (
	OutcomeOK             = "OK"
	OutcomeUnexpectedPass = "UNEXPECTED PASS" // an expected-FAIL task passed: review the trace, it is not a success
	OutcomeUnexpectedFail = "UNEXPECTED FAIL" // an expected-PASS task failed
	OutcomeError          = "ERROR"           // the harness failed; says nothing about the task
)

// outcome classifies one run.
func outcome(expected, verdict string, exit trace.ExitReason) string {
	switch {
	case exit == trace.ReasonError:
		return OutcomeError
	case verdict == expected:
		return OutcomeOK
	case expected == trace.VerdictFail:
		return OutcomeUnexpectedPass
	default:
		return OutcomeUnexpectedFail
	}
}

// evalRow is one run of one task, as logged.
type evalRow struct {
	Task           string  `json:"task"`
	Run            int     `json:"run"` // 1..runs
	Expected       string  `json:"expected"`
	Verdict        string  `json:"verdict"`
	Outcome        string  `json:"outcome"`
	Steps          int     `json:"steps"`
	Denied         int     `json:"denied"` // tool calls the policy denied
	ExitReason     string  `json:"exit_reason"`
	CostUSD        float64 `json:"cost_usd"`
	Gate           string  `json:"gate"` // the gate's decision (always deferred in eval)
	ContractSHA256 string  `json:"contract_sha256"`
	Trace          string  `json:"trace"`
}

// evalSummary is the eval's totals.
type evalSummary struct {
	ExpectedPassRuns int     `json:"expected_pass_runs"`
	Passed           int     `json:"passed"`    // expected-PASS runs that passed
	PassRate         float64 `json:"pass_rate"` // passed / expected_pass_runs (0 if there are none)
	ExpectedFailRuns int     `json:"expected_fail_runs"`
	SaidNo           int     `json:"said_no"` // expected-FAIL runs that failed (not counting harness errors)
	UnexpectedPass   int     `json:"unexpected_pass"`
	UnexpectedFail   int     `json:"unexpected_fail"`
	Errors           int     `json:"errors"`
	TotalCostUSD     float64 `json:"total_cost_usd"`
	WallSeconds      float64 `json:"wall_seconds"`
}

// evalEntry is one line of results/eval-log.jsonl.
type evalEntry struct {
	EvalID        string      `json:"eval_id"`
	Timestamp     time.Time   `json:"timestamp"`
	GitCommit     string      `json:"git_commit"`
	GitDirty      bool        `json:"git_dirty"` // uncommitted changes outside results/ when the eval started
	Model         string      `json:"model"`
	PromptVersion string      `json:"prompt_version"`
	SplitSHA256   string      `json:"split_sha256"`
	Set           string      `json:"set"`
	Runs          int         `json:"runs"`
	Complete      bool        `json:"complete"` // false if the eval was interrupted
	Rows          []evalRow   `json:"rows"`
	Summary       evalSummary `json:"summary"`
}

// summarize adds up the rows. Harness errors count in the totals of their
// expected verdict but never as a pass or a "no".
func summarize(rows []evalRow, wall time.Duration) evalSummary {
	var s evalSummary
	for _, r := range rows {
		s.TotalCostUSD += r.CostUSD
		switch r.Outcome {
		case OutcomeUnexpectedPass:
			s.UnexpectedPass++
		case OutcomeUnexpectedFail:
			s.UnexpectedFail++
		case OutcomeError:
			s.Errors++
		}
		switch r.Expected {
		case trace.VerdictPass:
			s.ExpectedPassRuns++
			if r.Verdict == trace.VerdictPass && r.Outcome != OutcomeError {
				s.Passed++
			}
		case trace.VerdictFail:
			s.ExpectedFailRuns++
			if r.Verdict == trace.VerdictFail && r.Outcome != OutcomeError {
				s.SaidNo++
			}
		}
	}
	if s.ExpectedPassRuns > 0 {
		s.PassRate = float64(s.Passed) / float64(s.ExpectedPassRuns)
	}
	s.WallSeconds = wall.Seconds()
	return s
}

type evalOpts struct {
	set        string // "dev" or "held-out"
	runs       int
	heldOutOK  bool
	tasksDir   string
	tracesDir  string
	outDir     string
	resultsDir string
}

func parseEvalArgs(args []string) (evalOpts, error) {
	var o evalOpts
	fs := flag.NewFlagSet("eval", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	fs.StringVar(&o.set, "set", "", "dev or held-out")
	fs.IntVar(&o.runs, "runs", 1, "runs per task")
	fs.BoolVar(&o.heldOutOK, "held-out-ok", false, "allow --set held-out")
	fs.StringVar(&o.tasksDir, "tasks", "tasks", "tasks directory")
	fs.StringVar(&o.tracesDir, "traces", "traces", "traces directory")
	fs.StringVar(&o.outDir, "out", "out", "gate output directory")
	fs.StringVar(&o.resultsDir, "results", "results", "results directory")
	if err := fs.Parse(args); err != nil {
		return o, err
	}
	switch {
	case fs.NArg() > 0:
		return o, fmt.Errorf("unexpected argument %q", fs.Arg(0))
	case o.set != "dev" && o.set != "held-out":
		return o, fmt.Errorf("--set must be dev or held-out, got %q", o.set)
	case o.runs < 1:
		return o, fmt.Errorf("--runs must be at least 1, got %d", o.runs)
	}
	return o, nil
}

// errHeldOut is the held-out guard's refusal.
var errHeldOut = errors.New("held-out is reserved for T5.1 (docs/07-evidence.md); pass --held-out-ok to run it")

// checkHeldOut refuses the held-out set unless --held-out-ok was given.
func checkHeldOut(o evalOpts) error {
	if o.set == "held-out" && !o.heldOutOK {
		return errHeldOut
	}
	return nil
}

// evalEnv is what an eval needs from outside; tests pass fakes.
type evalEnv struct {
	newSandbox func() (sandbox.Sandbox, string, error) // a fresh sandbox and its pod name, per run
	client     loop.Client
	git        func() (commit string, dirty bool)
	now        func() time.Time
	stdout     io.Writer
	stderr     io.Writer // progress lines
}

// evalMain is "apg eval" with the real sandbox, model, and git.
func evalMain(args []string, stdout, stderr io.Writer) int {
	o, err := parseEvalArgs(args)
	if err != nil {
		fmt.Fprintf(stderr, "apg eval: %v\n%s\n", err, evalUsage)
		return exitError
	}
	ctx, stopSignals := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stopSignals()
	env := evalEnv{
		newSandbox: func() (sandbox.Sandbox, string, error) {
			k, err := sandbox.NewKind()
			if err != nil {
				return nil, "", err
			}
			return k, k.PodName(), nil
		},
		client: loop.NewAnthropicClient(),
		git:    hostGit,
		now:    time.Now,
		stdout: stdout,
		stderr: stderr,
	}
	return runEval(ctx, env, o)
}

// splitFile is the part of tasks/split.json eval reads.
type splitFile struct {
	Dev     []string `json:"dev"`
	HeldOut []string `json:"held_out"`
}

func runEval(ctx context.Context, env evalEnv, o evalOpts) int {
	fail := func(format string, a ...any) int {
		fmt.Fprintf(env.stderr, "apg eval: "+format+"\n", a...)
		return exitError
	}
	if err := checkHeldOut(o); err != nil {
		return fail("%v", err)
	}

	// The set, in split.json order, and the file's hash for the log.
	splitBytes, err := os.ReadFile(filepath.Join(o.tasksDir, "split.json"))
	if err != nil {
		return fail("%v", err)
	}
	var split splitFile
	if err := json.Unmarshal(splitBytes, &split); err != nil {
		return fail("split.json: %v", err)
	}
	ids := split.Dev
	if o.set == "held-out" {
		ids = split.HeldOut
	}
	if len(ids) == 0 {
		return fail("split.json has no %s tasks", o.set)
	}
	type planned struct {
		tk          task
		contractSHA string
	}
	var tasks []planned
	for _, id := range ids {
		if len(id) < 4 {
			return fail("split.json: bad task id %q", id)
		}
		tk, err := findTask(o.tasksDir, id[:3])
		if err != nil {
			return fail("%v", err)
		}
		if tk.ID != id {
			return fail("split.json names %s, but task %s is %s", id, id[:3], tk.ID)
		}
		if tk.Expected.Verdict == "" {
			return fail("task %s has no expected outcome in contract.json", tk.ID)
		}
		b, err := os.ReadFile(filepath.Join(tk.Dir, "contract.json"))
		if err != nil {
			return fail("%v", err)
		}
		tasks = append(tasks, planned{tk, sha256Hex(b)})
	}

	start := env.now().UTC()
	commit, dirty := env.git()
	suffix := make([]byte, 4)
	if _, err := rand.Read(suffix); err != nil {
		return fail("%v", err)
	}
	entry := evalEntry{
		EvalID:        trace.NewRunID(start, hex.EncodeToString(suffix)),
		Timestamp:     start,
		GitCommit:     commit,
		GitDirty:      dirty,
		Model:         model,
		PromptVersion: loop.PromptVersion(),
		SplitSHA256:   sha256Hex(splitBytes),
		Set:           o.set,
		Runs:          o.runs,
		Complete:      true,
		Rows:          []evalRow{},
	}
	// Eval mode: the gate always defers. It never reads stdin.
	gateCfg := &gate.Config{In: strings.NewReader(""), Out: io.Discard, Interactive: false, Batch: true, OutDir: o.outDir}

	total := len(tasks) * o.runs
	n := 0
run:
	for _, p := range tasks {
		for r := 1; r <= o.runs; r++ {
			if ctx.Err() != nil {
				entry.Complete = false
				break run // "break run" leaves both loops (run is the label above)
			}
			n++
			sb, pod, err := env.newSandbox()
			if err != nil {
				return fail("sandbox: %v", err)
			}
			tr := runTask(ctx, sb, pod, p.tk, env.client, gateCfg)
			path, err := trace.Write(o.tracesDir, tr)
			if err != nil {
				fmt.Fprintf(env.stderr, "apg eval: write trace: %v\n", err)
				path = "<not written>"
			}
			row := evalRow{
				Task: p.tk.ID, Run: r, Expected: p.tk.Expected.Verdict, Verdict: tr.Verdict,
				Outcome:    outcome(p.tk.Expected.Verdict, tr.Verdict, tr.ExitReason),
				Steps:      len(tr.Steps),
				ExitReason: string(tr.ExitReason), ContractSHA256: p.contractSHA, Trace: path,
			}
			if tr.Budget != nil {
				row.Denied, row.CostUSD = tr.Budget.Used.PolicyViolations, tr.Budget.Used.CostUSD
			}
			if tr.Gate != nil {
				row.Gate = tr.Gate.Decision
			}
			entry.Rows = append(entry.Rows, row)
			fmt.Fprintf(env.stderr, "[%d/%d] %s run %d: %s %s (%s)\n", n, total, row.Task, r, row.Verdict, row.ExitReason, row.Outcome)
		}
	}
	entry.Summary = summarize(entry.Rows, env.now().Sub(start))

	printEval(env.stdout, entry)
	if err := appendLog(o.resultsDir, entry); err != nil {
		return fail("eval log: %v", err)
	}
	fmt.Fprintf(env.stdout, "\nlogged as %s in %s and %s\n", entry.EvalID,
		filepath.Join(o.resultsDir, "eval-log.jsonl"), filepath.Join(o.resultsDir, "EVAL-LOG.md"))

	s := entry.Summary
	if s.UnexpectedPass+s.UnexpectedFail+s.Errors > 0 || !entry.Complete {
		return exitFail
	}
	return exitPass
}

func sha256Hex(b []byte) string {
	sum := sha256.Sum256(b)
	return hex.EncodeToString(sum[:])
}

// rowName is the task cell: the task, plus "#k" when there are several runs.
func rowName(r evalRow, runs int) string {
	if runs > 1 {
		return fmt.Sprintf("%s #%d", r.Task, r.Run)
	}
	return r.Task
}

// printEval prints the results table, a loud block for every UNEXPECTED
// PASS, and the summary.
func printEval(w io.Writer, e evalEntry) {
	fmt.Fprintf(w, "\napg eval %s: set %s, %d run(s) per task, model %s, prompt %s\n\n", e.EvalID, e.Set, e.Runs, e.Model, e.PromptVersion[:12])
	// tabwriter lines up the columns: cells are separated by tabs, and
	// Flush pads them.
	tw := tabwriter.NewWriter(w, 0, 0, 2, ' ', 0)
	fmt.Fprintln(tw, "task\texpected\tverdict\toutcome\tsteps\tdenied\texit reason\tcost")
	for _, r := range e.Rows {
		out := r.Outcome
		if out == OutcomeUnexpectedPass {
			out += " !!!"
		}
		fmt.Fprintf(tw, "%s\t%s\t%s\t%s\t%d\t%d\t%s\t$%.5f\n", rowName(r, e.Runs), r.Expected, r.Verdict, out, r.Steps, r.Denied, r.ExitReason, r.CostUSD)
	}
	tw.Flush()
	for _, r := range e.Rows {
		if r.Outcome == OutcomeUnexpectedPass {
			fmt.Fprintf(w, "\n!!! UNEXPECTED PASS: %s — a task expected to FAIL passed. Review the trace: %s. This is not a success.\n", rowName(r, e.Runs), r.Trace)
		}
	}
	fmt.Fprintln(w)
	writeSummary(w, e.Summary, e.Complete, "")
}

// writeSummary prints the summary lines, each starting with prefix.
func writeSummary(w io.Writer, s evalSummary, complete bool, prefix string) {
	rate := "n/a"
	if s.ExpectedPassRuns > 0 {
		rate = fmt.Sprintf("%.1f%%", 100*s.PassRate)
	}
	fmt.Fprintf(w, "%spass rate (expected PASS): %d/%d runs (%s)\n", prefix, s.Passed, s.ExpectedPassRuns, rate)
	fmt.Fprintf(w, "%ssaid no (expected FAIL):   %d/%d runs\n", prefix, s.SaidNo, s.ExpectedFailRuns)
	fmt.Fprintf(w, "%sUNEXPECTED PASS:           %d\n", prefix, s.UnexpectedPass)
	fmt.Fprintf(w, "%sUNEXPECTED FAIL:           %d\n", prefix, s.UnexpectedFail)
	fmt.Fprintf(w, "%sharness errors:            %d\n", prefix, s.Errors)
	fmt.Fprintf(w, "%stotal cost:                $%.5f (estimated from list prices)\n", prefix, s.TotalCostUSD)
	fmt.Fprintf(w, "%swall-clock time:           %s\n", prefix, (time.Duration(s.WallSeconds * float64(time.Second))).Round(time.Second))
	if !complete {
		fmt.Fprintf(w, "%sINCOMPLETE: the eval was interrupted before every run finished\n", prefix)
	}
}

// appendLog appends entry as one line to eval-log.jsonl, then regenerates
// EVAL-LOG.md from every line.
func appendLog(dir string, entry evalEntry) error {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	b, err := json.Marshal(entry)
	if err != nil {
		return err
	}
	path := filepath.Join(dir, "eval-log.jsonl")
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0o644)
	if err != nil {
		return err
	}
	if _, err := f.Write(append(b, '\n')); err != nil {
		f.Close()
		return err
	}
	if err := f.Close(); err != nil {
		return err
	}
	entries, err := readLog(path)
	if err != nil {
		return err
	}
	return writeMarkdown(filepath.Join(dir, "EVAL-LOG.md"), entries)
}

// readLog reads every line of eval-log.jsonl strictly.
func readLog(path string) ([]evalEntry, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	var out []evalEntry
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 1<<20), 16<<20) // lines can be long: allow up to 16 MiB
	for line := 1; sc.Scan(); line++ {
		var e evalEntry
		dec := json.NewDecoder(bytes.NewReader(sc.Bytes()))
		dec.DisallowUnknownFields()
		if err := dec.Decode(&e); err != nil {
			return nil, fmt.Errorf("%s line %d: %w", path, line, err)
		}
		out = append(out, e)
	}
	return out, sc.Err()
}

// writeMarkdown writes the readable eval log (every eval so far), via a
// temp file and a rename, so a reader never sees half a file.
func writeMarkdown(path string, entries []evalEntry) error {
	var b strings.Builder
	b.WriteString("# Eval log\n\n")
	b.WriteString("Generated by `apg eval` from `results/eval-log.jsonl` after every eval; do not edit by hand. ")
	b.WriteString("Every row is model output from a real run, checked by the task's hidden check. ")
	b.WriteString("Trace paths point at `traces/`, which is not committed; traces cited in the docs are copied to `evidence/traces/` under the same name.\n")
	for _, e := range entries {
		fmt.Fprintf(&b, "\n## %s: set %s, %d run(s) per task\n\n", e.EvalID, e.Set, e.Runs)
		dirty := ""
		if e.GitDirty {
			dirty = " (uncommitted changes outside results/)"
		}
		fmt.Fprintf(&b, "- Started: %s\n- Commit: `%s`%s\n- Model: `%s`\n- Prompt version: `%s`\n- split.json SHA-256: `%s`\n\n",
			e.Timestamp.Format(time.RFC3339), e.GitCommit, dirty, e.Model, e.PromptVersion, e.SplitSHA256)
		b.WriteString("| task | expected | verdict | outcome | steps | denied | exit reason | cost | trace |\n|---|---|---|---|---|---|---|---|---|\n")
		for _, r := range e.Rows {
			out := r.Outcome
			if out == OutcomeUnexpectedPass {
				out = "**UNEXPECTED PASS** (review the trace)"
			}
			fmt.Fprintf(&b, "| %s | %s | %s | %s | %d | %d | %s | $%.5f | `%s` |\n", rowName(r, e.Runs), r.Expected, r.Verdict, out, r.Steps, r.Denied, r.ExitReason, r.CostUSD, r.Trace)
		}
		b.WriteString("\n")
		writeSummary(&b, e.Summary, e.Complete, "- ")
	}
	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, []byte(b.String()), 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, path) // replaces path in one step
}

// hostGit returns the current commit and whether there are uncommitted
// changes outside results/ (the eval log itself changes with every eval).
// "unknown" and dirty=true if git cannot tell.
func hostGit() (string, bool) {
	out, err := exec.Command("git", "rev-parse", "HEAD").Output()
	if err != nil {
		return "unknown", true
	}
	status, err := exec.Command("git", "status", "--porcelain", "--", ".", ":(exclude)results").Output()
	if err != nil {
		return strings.TrimSpace(string(out)), true
	}
	return strings.TrimSpace(string(out)), len(bytes.TrimSpace(status)) > 0
}
