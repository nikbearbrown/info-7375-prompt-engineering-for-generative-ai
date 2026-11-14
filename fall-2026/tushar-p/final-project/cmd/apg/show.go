package main

// apg show (PLAN.md T3.4): a step-by-step printout of one trace, readable
// in an 80-column terminal. It reads v1 traces strictly (trace.Decode) and
// shows only the header of a v0 trace.

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
	"unicode/utf8"

	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

const showUsage = `usage: apg show <run_id | trace path> [--full] [--traces dir]
  a run ID is looked up in traces/, then evidence/traces/
  --full shows every output line and every harness command`

const (
	width    = 80 // the printout's maximum line width
	cutLines = 20 // lines of output shown per block without --full
)

type showOpts struct {
	arg       string
	full      bool
	tracesDir string
}

func parseShowArgs(args []string) (showOpts, error) {
	var o showOpts
	fs := flag.NewFlagSet("show", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	fs.BoolVar(&o.full, "full", false, "show everything")
	fs.StringVar(&o.tracesDir, "traces", "traces", "traces directory")
	// Like apg run: flags may come before or after the argument.
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
		return o, fmt.Errorf("want one run ID or trace path, got %d", len(positional))
	}
	o.arg = positional[0]
	return o, nil
}

var runIDArg = regexp.MustCompile(`^[A-Za-z0-9_-]+$`)

// findTrace returns the trace file for arg: an existing path, or a run ID
// looked up in tracesDir, then evidence/traces.
func findTrace(arg, tracesDir string) (string, error) {
	if fi, err := os.Stat(arg); err == nil && !fi.IsDir() {
		return arg, nil
	}
	if !runIDArg.MatchString(arg) {
		return "", fmt.Errorf("%s: no such file, and not a run ID", arg)
	}
	for _, dir := range []string{tracesDir, filepath.Join("evidence", "traces")} {
		p := filepath.Join(dir, arg+".json")
		if _, err := os.Stat(p); err == nil {
			return p, nil
		}
	}
	return "", fmt.Errorf("no trace %s.json in %s or %s", arg, tracesDir, filepath.Join("evidence", "traces"))
}

func showMain(args []string, stdout, stderr io.Writer) int {
	o, err := parseShowArgs(args)
	if err != nil {
		fmt.Fprintf(stderr, "apg show: %v\n%s\n", err, showUsage)
		return exitError
	}
	path, err := findTrace(o.arg, o.tracesDir)
	if err != nil {
		fmt.Fprintf(stderr, "apg show: %v\n", err)
		return exitError
	}
	b, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(stderr, "apg show: %v\n", err)
		return exitError
	}
	// Colour only on a terminal, and never if NO_COLOR is set.
	color := false
	if f, ok := stdout.(*os.File); ok && isTerminal(f) && os.Getenv("NO_COLOR") == "" {
		color = true
	}
	if err := showTrace(stdout, b, path, o.full, color); err != nil {
		fmt.Fprintf(stderr, "apg show: %s: %v\n", path, err)
		return exitError
	}
	return exitPass
}

// printer writes lines no wider than width, wrapping long ones.
type printer struct {
	w     io.Writer
	color bool
	full  bool
}

// line prints s at indent, wrapping at width with a two-space hanging
// indent. A newline in s starts a new line.
func (p *printer) line(indent int, s string) {
	p.wrap(indent, "", "  ", s)
}

// wrap prints s at indent. Each line starts with first; when a line is too
// wide, it is cut at a space (or hard, if there is none) and continues on
// the next line after cont.
func (p *printer) wrap(indent int, first, cont, s string) {
	pad := strings.Repeat(" ", indent)
	for _, l := range strings.Split(s, "\n") {
		prefix := first
		for {
			room := width - indent - utf8.RuneCountInString(prefix)
			if room < 10 {
				room = 10
			}
			runes := []rune(l)
			if len(runes) <= room {
				fmt.Fprintln(p.w, strings.TrimRight(pad+prefix+l, " "))
				break
			}
			cut := room
			for i := room; i > room/2; i-- {
				if runes[i] == ' ' {
					cut = i
					break
				}
			}
			fmt.Fprintln(p.w, strings.TrimRight(pad+prefix+string(runes[:cut]), " "))
			l = strings.TrimLeft(string(runes[cut:]), " ")
			prefix = cont
		}
	}
}

// block prints a multi-line text (output, file content) at indent, cut to
// cutLines lines unless --full, saying how many lines were cut.
func (p *printer) block(indent int, text string) {
	text = strings.TrimRight(text, "\n")
	if text == "" {
		p.line(indent, "(empty)")
		return
	}
	lines := strings.Split(text, "\n")
	shown := lines
	if !p.full && len(lines) > cutLines {
		shown = lines[:cutLines]
	}
	for _, l := range shown {
		p.wrap(indent, "| ", "|   ", l) // a wrapped line keeps its "|"
	}
	if len(shown) < len(lines) {
		p.line(indent, fmt.Sprintf("… %d more lines (use --full)", len(lines)-len(shown)))
	}
}

// paint wraps s in an ANSI colour when colour is on. Only short words are
// painted, so wrapping is not affected.
func (p *printer) paint(code, s string) string {
	if !p.color {
		return s
	}
	return "\x1b[" + code + "m" + s + "\x1b[0m"
}

func (p *printer) verdict(v string) string {
	switch v {
	case trace.VerdictPass:
		return p.paint("32;1", v) // bold green
	case trace.VerdictFail:
		return p.paint("31;1", v) // bold red
	}
	return v
}

func (p *printer) heading(s string) {
	fmt.Fprintln(p.w)
	p.line(0, p.paint("1", s))
}

// showTrace prints the trace in b (read from path).
func showTrace(w io.Writer, b []byte, path string, full, color bool) error {
	var head struct {
		SchemaVersion int       `json:"schema_version"`
		RunID         string    `json:"run_id"`
		TaskID        string    `json:"task_id"`
		Model         string    `json:"model"`
		Verdict       string    `json:"verdict"`
		ExitReason    string    `json:"exit_reason"`
		StartedAt     time.Time `json:"started_at"`
	}
	if err := json.Unmarshal(b, &head); err != nil {
		return fmt.Errorf("not a trace: %w", err)
	}
	p := &printer{w: w, color: color, full: full}
	if head.SchemaVersion == 0 {
		p.line(0, "this trace is schema v0: it predates schema v1 (T2.5, docs/trace-schema.md); only its header is shown")
		fmt.Fprintln(w)
		p.line(0, "run      "+head.RunID)
		p.line(0, "task     "+head.TaskID)
		model := head.Model
		if model == "" {
			model = "(no agent)"
		}
		p.line(0, "model    "+model)
		p.line(0, "verdict  "+p.verdict(head.Verdict)+"  exit reason "+head.ExitReason)
		p.line(0, "started  "+head.StartedAt.UTC().Format(time.RFC3339))
		return nil
	}
	tr, err := trace.Decode(strings.NewReader(string(b)))
	if err != nil {
		return err
	}
	if head.SchemaVersion != trace.SchemaVersion {
		return errors.New("unknown schema version") // Decode already rejects this; kept for clarity
	}
	showHeader(p, tr, path)
	for _, s := range tr.Steps {
		showStep(p, tr, s)
	}
	showHarness(p, tr)
	showFinal(p, tr)
	showGate(p, tr)
	return nil
}

func showHeader(p *printer, tr *trace.Trace, path string) {
	p.line(0, p.paint("1", "run "+tr.RunID))
	p.line(0, "trace    "+path)
	p.line(0, fmt.Sprintf("task     %s   pod %s", tr.TaskID, tr.Pod))
	p.line(0, fmt.Sprintf("started  %s   took %s", tr.StartedAt.UTC().Format(time.RFC3339), tr.EndedAt.Sub(tr.StartedAt).Round(100*time.Millisecond)))
	if tr.Model != "" {
		pv := tr.PromptVersion
		if len(pv) > 12 {
			pv = pv[:12]
		}
		if pv == "" {
			pv = "(not recorded)"
		}
		p.line(0, fmt.Sprintf("model    %s   prompt %s", tr.Model, pv))
	} else {
		p.line(0, "model    (no agent)")
	}
	stop := ""
	if tr.LoopStop != "" {
		stop = "   loop stop " + tr.LoopStop
	}
	p.line(0, fmt.Sprintf("verdict  %s   exit reason %s%s", p.verdict(tr.Verdict), tr.ExitReason, stop))
	if tr.Error != "" {
		p.line(0, "error    "+tr.Error)
	}
	if tr.Gate != nil {
		p.line(0, "gate     "+gateMode(tr.Gate))
	}
	if b := tr.Budget; b != nil {
		u, l := b.Used, b.Limits
		p.line(0, fmt.Sprintf("budget   steps %d/%d  tokens %s/%s  cost $%.5f/$%g", u.Steps, l.MaxSteps,
			commas(u.TotalTokens), commas(l.MaxTotalTokens), u.CostUSD, l.MaxCostUSD))
		p.line(0, fmt.Sprintf("         time %.1fs/%gs  denied %d/%d", u.AgentSeconds, l.TimeoutSeconds, u.PolicyViolations, l.MaxPolicyViolations))
	}
}

func gateMode(g *trace.Gate) string {
	mode := ""
	switch {
	case g.Batch:
		mode = " (batch)"
	case g.Interactive:
		mode = " (interactive)"
	}
	return g.Decision + mode
}

// plural writes "1 line", "2 lines".
func plural(n int, word string) string {
	return pluralWord(n, word, word+"s")
}

func pluralWord(n int, one, many string) string {
	if n == 1 {
		return "1 " + one
	}
	return fmt.Sprintf("%d %s", n, many)
}

// commas writes n with thousands separators: 25103 -> "25,103".
func commas(n int64) string {
	s := fmt.Sprint(n)
	if n < 0 {
		return "-" + commas(-n)
	}
	for i := len(s) - 3; i > 0; i -= 3 {
		s = s[:i] + "," + s[i:]
	}
	return s
}

func showStep(p *printer, tr *trace.Trace, s trace.Step) {
	p.heading(fmt.Sprintf("step %d", s.N))
	if s.Text != "" {
		p.line(2, "model said:")
		p.block(4, s.Text)
	}
	if s.Tool == "" {
		p.line(2, fmt.Sprintf("(no tool call: %s)", stopWords(s.StopReason)))
		return
	}
	showCall(p, s)
	switch s.Verdict {
	case trace.StepDenied:
		p.line(2, fmt.Sprintf("policy:  %s (rule: %s): %s", p.paint("31;1", "DENIED"), s.Rule, s.Reason))
	case trace.StepAllowed:
		p.line(2, "policy:  allowed")
	}
	// The commands this step ran (agent) and the policy's lookups (harness).
	for _, c := range tr.Commands {
		if c.Step != s.N {
			continue
		}
		p.line(2, fmt.Sprintf("%s %s  (exit %d)", who(c), podCommand(c.Args), c.ExitCode))
		if c.Phase == trace.PhasePolicy && c.Stdout != "" && !p.full {
			p.line(4, "-> "+strings.ReplaceAll(strings.TrimSpace(c.Stdout), "\n", ", "))
		}
		if p.full {
			showStreams(p, c)
		}
	}
	if s.Verdict != trace.StepDenied || p.full {
		p.line(2, "output sent to the model:")
		p.block(4, s.Output)
	}
	changed := "no"
	if s.WorkspaceChanged {
		changed = "yes"
	}
	p.line(2, "/workspace changed: "+changed)
	for _, r := range tr.CheckRuns {
		if r.AfterStep == s.N {
			showCheckRun(p, 2, r)
		}
	}
}

// who marks a command: "[agent]" for one that carried out the agent's
// tool call, "[harness] <phase>:" for everything the harness ran itself.
func who(c trace.Command) string {
	if c.Actor == trace.ActorAgent {
		return "[agent]"
	}
	return "[harness] " + c.Phase + ":"
}

func stopWords(stop string) string {
	switch stop {
	case "end_turn":
		return "ended its turn"
	case "max_tokens":
		return "reply cut off at max_tokens"
	case "refusal":
		return "refused"
	}
	return stop
}

// showCall prints what the model asked for.
func showCall(p *printer, s trace.Step) {
	switch s.Tool {
	case "read_file":
		var in struct{ Path string }
		if json.Unmarshal([]byte(s.Input), &in) == nil {
			p.line(2, "asked:   read_file "+in.Path)
			return
		}
	case "run_command":
		var in struct{ Argv []string }
		if json.Unmarshal([]byte(s.Input), &in) == nil {
			p.line(2, "asked:   run_command "+shellJoin(in.Argv))
			return
		}
	case "write_file":
		var in struct{ Path, Content string }
		if json.Unmarshal([]byte(s.Input), &in) == nil {
			n := len(strings.Split(strings.TrimRight(in.Content, "\n"), "\n"))
			p.line(2, fmt.Sprintf("asked:   write_file %s (%s, %s)", in.Path, plural(n, "line"), plural(len(in.Content), "byte")))
			p.block(4, in.Content)
			return
		}
	}
	// Unknown tool, or input that does not parse (for example cut at 8 KiB).
	p.line(2, "asked:   "+s.Tool+" "+s.Input)
}

// podCommand returns the part of a kubectl command that ran in the pod:
// everything after "--" for kubectl exec, or "cp src dst" for kubectl cp.
func podCommand(args []string) string {
	for i, a := range args {
		if a == "--" {
			return shellJoin(args[i+1:])
		}
	}
	for i, a := range args {
		if a == "cp" {
			return "kubectl " + shellJoin(args[i:])
		}
	}
	return shellJoin(args)
}

// shellJoin joins argv for display, quoting arguments that are empty or
// hold spaces or shell characters, as a shell would need. It is only for
// reading: nothing here runs a shell.
func shellJoin(argv []string) string {
	out := make([]string, len(argv))
	for i, a := range argv {
		if a != "" && !strings.ContainsAny(a, " \t\n'\"\\$`|&;<>(){}*?[]#~!") {
			out[i] = a
			continue
		}
		out[i] = "'" + strings.ReplaceAll(a, "'", `'\''`) + "'"
	}
	return strings.Join(out, " ")
}

func showStreams(p *printer, c trace.Command) {
	if c.Stdout != "" {
		p.line(4, "stdout:")
		p.block(6, c.Stdout)
	}
	if c.Stderr != "" {
		p.line(4, "stderr:")
		p.block(6, c.Stderr)
	}
}

func showCheckRun(p *printer, indent int, r trace.CheckRun) {
	result := p.verdict(trace.VerdictFail)
	if r.Passed {
		result = p.verdict(trace.VerdictPass)
	}
	p.line(indent, fmt.Sprintf("check run (%s): exit %d, %s; killed %s first", r.Trigger, r.ExitCode, result, pluralWord(r.Killed, "process", "processes")))
	if r.ChangedWorkspace {
		p.line(indent+2, "the check run itself changed /workspace")
	}
}

// showHarness summarises the harness commands no step is tagged with
// (start, setup, fingerprints, checks, gate, stop); --full lists them.
func showHarness(p *printer, tr *trace.Trace) {
	var order []string
	counts := map[string]int{}
	for _, c := range tr.Commands {
		if c.Step != 0 {
			continue
		}
		if counts[c.Phase] == 0 {
			order = append(order, c.Phase)
		}
		counts[c.Phase]++
	}
	if len(order) == 0 {
		return
	}
	p.heading("harness commands not tied to a step")
	parts := make([]string, len(order))
	for i, ph := range order {
		parts[i] = fmt.Sprintf("%s %d", ph, counts[ph])
	}
	p.line(2, strings.Join(parts, ", "))
	if !p.full {
		p.line(2, "(use --full to list them with their output)")
		return
	}
	for _, c := range tr.Commands {
		if c.Step != 0 {
			continue
		}
		p.line(2, fmt.Sprintf("%s %s  (exit %d)", who(c), podCommand(c.Args), c.ExitCode))
		showStreams(p, c)
	}
}

func showFinal(p *printer, tr *trace.Trace) {
	p.heading("final check")
	if !tr.Check.Ran || tr.Check.ExitCode == nil {
		p.line(2, "did not run (harness error)")
		return
	}
	p.line(2, fmt.Sprintf("exit %d: %s", *tr.Check.ExitCode, p.verdict(tr.Verdict)))
	final := false
	for _, r := range tr.CheckRuns {
		if r.Trigger == trace.TriggerFinal {
			showCheckRun(p, 2, r)
			final = true
		}
	}
	if !final {
		for _, r := range tr.CheckRuns {
			if r.Passed {
				p.line(2, fmt.Sprintf("decided by the check run after step %d; no final check was needed", r.AfterStep))
			}
		}
	}
}

func showGate(p *printer, tr *trace.Trace) {
	if tr.Gate == nil {
		return
	}
	g := tr.Gate
	p.heading("gate")
	p.line(2, "decision  "+gateMode(g))
	if g.Reason != "" {
		p.line(2, "reason    "+g.Reason)
	}
	if g.DiffSHA256 != "" {
		p.line(2, fmt.Sprintf("diff      sha256 %s… (%d bytes)", g.DiffSHA256[:12], g.DiffBytes))
	}
	if g.RecheckSHA256 != "" {
		same := "matches"
		if g.RecheckSHA256 != g.DiffSHA256 {
			same = "DIFFERS"
		}
		p.line(2, fmt.Sprintf("recheck   sha256 %s… (%s the diff shown)", g.RecheckSHA256[:12], same))
	}
	shown := "nothing"
	if len(g.Shown) > 0 {
		shown = strings.Join(g.Shown, ", ")
	}
	p.line(2, "shown     "+shown)
	exported := "nothing left the sandbox"
	if g.ExportedPath != "" {
		exported = g.ExportedPath
	}
	p.line(2, "exported  "+exported)
}
