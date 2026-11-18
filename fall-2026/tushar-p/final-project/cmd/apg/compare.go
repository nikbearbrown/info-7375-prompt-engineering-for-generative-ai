package main

// apg compare (PLAN.md T5.3): set two groups of evals side by side, per
// task and in totals, from results/eval-log.jsonl and the traces it cites.
// It is read-only: no model calls, no sandbox, no API key, no files written.
//
// Each side is one eval ID, a comma-separated list of eval IDs, or a filter
// such as contract=A,commit=6d7bafe,set=held-out. Warnings are printed
// before the tables whenever the sides differ in anything other than the
// prompt (the intended variable). Different sets or split files are refused
// unless --force is given. The output has counts, means and deltas only:
// no significance tests and no conclusions.

import (
	"flag"
	"fmt"
	"io"
	"math"
	"os"
	"path/filepath"
	"regexp"
	"slices"
	"strings"

	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

const compareUsage = `usage: apg compare <side-a> <side-b> [--force] [--log file] [--traces dir]
  a side is an eval ID, a comma-separated list of eval IDs, or a filter of
  key=value pairs (keys: set, contract, commit, model), e.g.
  contract=A,commit=6d7bafe,set=held-out
  --force compares sides with different sets or split files
  --log is the eval log (default results/eval-log.jsonl)
  a trace is looked up in --traces (default traces/), then evidence/traces/`

type compareOpts struct {
	sideA, sideB string
	force        bool
	logPath      string
	tracesDir    string
}

func parseCompareArgs(args []string) (compareOpts, error) {
	var o compareOpts
	fs := flag.NewFlagSet("compare", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	fs.BoolVar(&o.force, "force", false, "compare different sets or split files")
	fs.StringVar(&o.logPath, "log", filepath.Join("results", "eval-log.jsonl"), "eval log")
	fs.StringVar(&o.tracesDir, "traces", "traces", "traces directory")
	// Like apg run and apg show: flags may come before, between or after
	// the two sides.
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
	if len(positional) != 2 {
		return o, fmt.Errorf("want two sides, got %d", len(positional))
	}
	o.sideA, o.sideB = positional[0], positional[1]
	return o, nil
}

// selector is one side as typed: either eval IDs or a filter, never both.
type selector struct {
	text   string            // as typed, for the header
	ids    []string          // eval IDs, in the order given
	filter map[string]string // key -> value
}

// filterKeys are the keys a filter may use.
var filterKeys = map[string]bool{"set": true, "contract": true, "commit": true, "model": true}

// A commit in a filter is a hex prefix of at least 7 characters, as git
// prints short hashes.
var commitPrefix = regexp.MustCompile(`^[0-9a-f]{7,40}$`)

// parseSide parses one side.
func parseSide(s string) (selector, error) {
	sel := selector{text: s}
	parts := strings.Split(s, ",")
	nFilter := 0
	for _, p := range parts {
		if strings.Contains(p, "=") {
			nFilter++
		}
	}
	if nFilter > 0 && nFilter < len(parts) {
		return sel, fmt.Errorf("side %q mixes eval IDs and key=value filters", s)
	}
	seen := map[string]bool{}
	if nFilter == 0 {
		for _, id := range parts {
			switch {
			case id == "":
				return sel, fmt.Errorf("side %q has an empty part", s)
			case !runIDArg.MatchString(id): // the same rule as a run ID (show.go)
				return sel, fmt.Errorf("side %q: %q is not an eval ID", s, id)
			case seen[id]:
				return sel, fmt.Errorf("side %q names eval %s twice", s, id)
			}
			seen[id] = true
			sel.ids = append(sel.ids, id)
		}
		return sel, nil
	}
	sel.filter = map[string]string{}
	for _, p := range parts {
		// strings.Cut splits at the first "=": "commit=6d7bafe" -> "commit", "6d7bafe".
		key, value, _ := strings.Cut(p, "=")
		switch {
		case !filterKeys[key]:
			return sel, fmt.Errorf("side %q: unknown key %q (keys: set, contract, commit, model)", s, key)
		case value == "":
			return sel, fmt.Errorf("side %q: %s has no value", s, key)
		case seen[key]:
			return sel, fmt.Errorf("side %q: key %s given twice", s, key)
		case key == "commit" && !commitPrefix.MatchString(value):
			return sel, fmt.Errorf("side %q: commit %q must be at least 7 hex characters", s, value)
		}
		seen[key] = true
		sel.filter[key] = value
	}
	return sel, nil
}

// matches reports whether eval e passes the filter. An eval from before
// T5.1 has no prompt_contract, so it never matches contract=.
func (sel selector) matches(e evalEntry) bool {
	for key, v := range sel.filter {
		var ok bool
		switch key {
		case "set":
			ok = e.Set == v
		case "contract":
			ok = e.PromptContract == v
		case "commit":
			ok = strings.HasPrefix(e.GitCommit, v)
		case "model":
			ok = e.Model == v
		}
		if !ok {
			return false
		}
	}
	return true
}

// selectEvals returns the evals a side names, in eval-log order.
func selectEvals(entries []evalEntry, sel selector) ([]evalEntry, error) {
	var out []evalEntry
	if sel.filter != nil {
		for _, e := range entries {
			if sel.matches(e) {
				out = append(out, e)
			}
		}
		if len(out) == 0 {
			return nil, fmt.Errorf("no eval in the log matches %q", sel.text)
		}
		return out, nil
	}
	want := map[string]bool{}
	for _, id := range sel.ids {
		want[id] = true
	}
	found := map[string]int{}
	for _, e := range entries {
		if want[e.EvalID] {
			found[e.EvalID]++
			out = append(out, e)
		}
	}
	for _, id := range sel.ids {
		switch found[id] {
		case 0:
			return nil, fmt.Errorf("unknown eval ID %s: not in the eval log", id)
		case 1:
		default:
			return nil, fmt.Errorf("eval ID %s appears %d times in the eval log", id, found[id])
		}
	}
	return out, nil
}

// cmpRow is one eval-log row with what only its trace has.
type cmpRow struct {
	evalRow
	tokens     int64  // input + output tokens (budget.used.total_tokens)
	truncation string // how tool output was cut, as printed in the header
}

// stats adds up rows: one task on one side, or a group of tasks.
type stats struct {
	runs         int
	passed       int // verdict PASS, not counting harness errors
	returnedFail int // verdict FAIL, not counting harness errors
	outcomes     map[string]int
	steps        int
	denied       int
	tokens       int64
	cost         float64
}

func (s *stats) add(r cmpRow) {
	if s.outcomes == nil {
		s.outcomes = map[string]int{}
	}
	s.runs++
	// As in summarize (eval.go): a harness error is neither a pass nor a FAIL.
	if r.Outcome != OutcomeError {
		switch r.Verdict {
		case trace.VerdictPass:
			s.passed++
		case trace.VerdictFail:
			s.returnedFail++
		}
	}
	s.outcomes[r.Outcome]++
	s.steps += r.Steps
	s.denied += r.Denied
	s.tokens += r.tokens
	s.cost += r.CostUSD
}

func (s *stats) meanSteps() float64  { return float64(s.steps) / float64(s.runs) }
func (s *stats) meanTokens() float64 { return float64(s.tokens) / float64(s.runs) }

// taskInfo is one task on one side.
type taskInfo struct {
	stats
	expected     []string // distinct expected verdicts (one, unless the task changed)
	contractSHAs []string // distinct contract.json hashes (one, unless the task changed)
}

// side is everything one side of the comparison holds.
type side struct {
	sel   selector
	evals []evalEntry
	rows  []cmpRow // every row, in eval-log order
	tasks map[string]*taskInfo
	order []string // task IDs in order of first appearance
}

// appendNew appends v to list unless it is already there, keeping the
// order of first appearance.
func appendNew(list []string, v string) []string {
	for _, x := range list {
		if x == v {
			return list
		}
	}
	return append(list, v)
}

// truncationText describes a trace's truncation settings (D26).
func truncationText(t *trace.Truncation) string {
	if t == nil {
		return "not recorded (before D26)"
	}
	return fmt.Sprintf("limit %d, head %d, tail %d", t.LimitBytes, t.HeadBytes, t.TailBytes)
}

// loadSide reads the trace of every row of evals and adds the rows up. A
// trace that cannot be found, does not decode strictly, or disagrees with
// its row is an error: the comparison would be built on a wrong record.
func loadSide(sel selector, evals []evalEntry, tracesDir string) (*side, error) {
	sd := &side{sel: sel, evals: evals, tasks: map[string]*taskInfo{}}
	for _, e := range evals {
		for _, r := range e.Rows {
			// The log stores "traces/<run_id>.json"; the run ID is the file name.
			runID := strings.TrimSuffix(filepath.Base(r.Trace), ".json")
			path, err := findTrace(runID, tracesDir)
			if err != nil {
				return nil, fmt.Errorf("eval %s, %s run %d: %w", e.EvalID, r.Task, r.Run, err)
			}
			tr, err := readTrace(path)
			if err != nil {
				return nil, fmt.Errorf("%s: %w", path, err)
			}
			var tokens int64
			var denied int
			var cost float64
			if tr.Budget != nil {
				tokens, denied, cost = tr.Budget.Used.TotalTokens, tr.Budget.Used.PolicyViolations, tr.Budget.Used.CostUSD
			}
			switch {
			case tr.RunID != runID:
				return nil, fmt.Errorf("%s: run_id %s, want %s", path, tr.RunID, runID)
			case tr.TaskID != r.Task:
				return nil, fmt.Errorf("%s: task %s, but the eval log says %s", path, tr.TaskID, r.Task)
			case tr.Verdict != r.Verdict:
				return nil, fmt.Errorf("%s: verdict %s, but the eval log says %s", path, tr.Verdict, r.Verdict)
			// cost != r.CostUSD compares floats exactly. That is right here:
			// apg eval copied the trace's float64 into the row, and JSON
			// writes and reads a float64 back to the same value.
			case len(tr.Steps) != r.Steps || denied != r.Denied || cost != r.CostUSD:
				return nil, fmt.Errorf("%s: steps, denied calls or cost differ from the eval log", path)
			}
			row := cmpRow{evalRow: r, tokens: tokens, truncation: truncationText(tr.Truncation)}
			sd.rows = append(sd.rows, row)
			ti := sd.tasks[r.Task]
			if ti == nil {
				ti = &taskInfo{}
				sd.tasks[r.Task] = ti
				sd.order = append(sd.order, r.Task)
			}
			ti.add(row)
			ti.expected = appendNew(ti.expected, r.Expected)
			ti.contractSHAs = appendNew(ti.contractSHAs, r.ContractSHA256)
		}
	}
	if len(sd.rows) == 0 {
		return nil, fmt.Errorf("side %q has no runs", sel.text)
	}
	return sd, nil
}

// readTrace reads one trace strictly (trace.Decode).
func readTrace(path string) (*trace.Trace, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	return trace.Decode(strings.NewReader(string(b)))
}

// field is one property that should be the same on both sides, with each
// side's distinct values in order of first appearance.
type field struct {
	name   string
	refuse bool // a difference is refused unless --force
	get    func(sd *side) []string
}

func evalValues(f func(e evalEntry) string) func(sd *side) []string {
	return func(sd *side) []string {
		var vs []string
		for _, e := range sd.evals {
			vs = appendNew(vs, f(e))
		}
		return vs
	}
}

func short(s string, n int) string {
	if len(s) > n {
		return s[:n]
	}
	return s
}

// The fields compared between and within sides. The prompt contract and
// prompt version are left out on purpose: they are the intended variable.
var compareFields = []field{
	{"set", true, evalValues(func(e evalEntry) string { return e.Set })},
	{"split.json SHA-256", true, evalValues(func(e evalEntry) string { return short(e.SplitSHA256, 12) })},
	{"model", false, evalValues(func(e evalEntry) string { return e.Model })},
	{"commit", false, evalValues(func(e evalEntry) string { return short(e.GitCommit, 12) })},
	{"truncation", false, func(sd *side) []string {
		var vs []string
		for _, r := range sd.rows {
			vs = appendNew(vs, r.truncation)
		}
		return vs
	}},
}

// compareWarnings lists every difference other than the intended variable.
// refusals are the ones that need --force.
func compareWarnings(a, b *side) (warnings, refusals []string) {
	sides := []struct {
		name string
		sd   *side
	}{{"a", a}, {"b", b}}
	add := func(refuse bool, format string, args ...any) {
		w := fmt.Sprintf(format, args...)
		warnings = append(warnings, w)
		if refuse {
			refusals = append(refusals, w)
		}
	}
	for _, f := range compareFields {
		va, vb := f.get(a), f.get(b)
		for _, s := range sides {
			if v := f.get(s.sd); len(v) > 1 {
				add(f.refuse, "side %s mixes %s: %s", s.name, f.name, strings.Join(v, "; "))
			}
		}
		if strings.Join(va, "; ") != strings.Join(vb, "; ") {
			add(f.refuse, "%s differs: a %s, b %s", f.name, strings.Join(va, "; "), strings.Join(vb, "; "))
		}
	}
	// Runs per task, tasks on one side only, and tasks whose expected
	// outcome or contract.json changed.
	for _, s := range sides {
		counts := map[int]bool{}
		for _, id := range s.sd.order {
			counts[s.sd.tasks[id].runs] = true
		}
		if len(counts) > 1 {
			add(false, "side %s: runs per task are not all equal (%s)", s.name, runsPerTask(s.sd))
		}
	}
	for _, id := range taskOrder(a, b) {
		ta, tb := a.tasks[id], b.tasks[id]
		switch {
		case ta == nil:
			add(false, "task %s is only on side b", id)
			continue
		case tb == nil:
			add(false, "task %s is only on side a", id)
			continue
		}
		if ta.runs != tb.runs {
			add(false, "runs per task differ for %s: a %d, b %d", id, ta.runs, tb.runs)
		}
		if strings.Join(ta.expected, "; ") != strings.Join(tb.expected, "; ") || len(ta.expected) > 1 {
			add(false, "expected outcome of %s: a %s, b %s", id, strings.Join(ta.expected, "; "), strings.Join(tb.expected, "; "))
		}
		if strings.Join(ta.contractSHAs, ";") != strings.Join(tb.contractSHAs, ";") || len(ta.contractSHAs) > 1 {
			add(false, "contract.json of %s differs (SHA-256): a %s, b %s", id, shortAll(ta.contractSHAs), shortAll(tb.contractSHAs))
		}
	}
	// Records that are not clean: an uncommitted tree or an interrupted eval.
	for _, s := range sides {
		for _, e := range s.sd.evals {
			if e.GitDirty {
				add(false, "side %s: eval %s ran with uncommitted changes", s.name, e.EvalID)
			}
			if !e.Complete {
				add(false, "side %s: eval %s is incomplete (interrupted)", s.name, e.EvalID)
			}
		}
	}
	return warnings, refusals
}

func shortAll(vs []string) string {
	out := make([]string, len(vs))
	for i, v := range vs {
		out[i] = short(v, 12)
	}
	return strings.Join(out, "; ")
}

func runsPerTask(sd *side) string {
	parts := make([]string, len(sd.order))
	for i, id := range sd.order {
		parts[i] = fmt.Sprintf("%s %d", id, sd.tasks[id].runs)
	}
	return strings.Join(parts, ", ")
}

// taskOrder is every task on either side: side a's order, then any task
// only side b has.
func taskOrder(a, b *side) []string {
	order := append([]string{}, a.order...)
	for _, id := range b.order {
		order = appendNew(order, id)
	}
	return order
}

func compareMain(args []string, stdout, stderr io.Writer) int {
	fail := func(format string, a ...any) int {
		fmt.Fprintf(stderr, "apg compare: "+format+"\n", a...)
		return exitError
	}
	o, err := parseCompareArgs(args)
	if err != nil {
		return fail("%v\n%s", err, compareUsage)
	}
	selA, err := parseSide(o.sideA)
	if err != nil {
		return fail("%v", err)
	}
	selB, err := parseSide(o.sideB)
	if err != nil {
		return fail("%v", err)
	}
	entries, err := readLog(o.logPath)
	if err != nil {
		return fail("%v", err)
	}
	evalsA, err := selectEvals(entries, selA)
	if err != nil {
		return fail("side a: %v", err)
	}
	evalsB, err := selectEvals(entries, selB)
	if err != nil {
		return fail("side b: %v", err)
	}
	inA := map[string]bool{}
	for _, e := range evalsA {
		inA[e.EvalID] = true
	}
	for _, e := range evalsB {
		if inA[e.EvalID] {
			return fail("eval %s is on both sides", e.EvalID)
		}
	}
	a, err := loadSide(selA, evalsA, o.tracesDir)
	if err != nil {
		return fail("side a: %v", err)
	}
	b, err := loadSide(selB, evalsB, o.tracesDir)
	if err != nil {
		return fail("side b: %v", err)
	}
	warnings, refusals := compareWarnings(a, b)
	if len(refusals) > 0 && !o.force {
		for _, r := range refusals {
			fmt.Fprintf(stderr, "apg compare: refused: %s\n", r)
		}
		return fail("the sides are not comparable; pass --force to compare them anyway")
	}
	printCompare(stdout, o.logPath, a, b, warnings)
	return exitPass
}

// Number formats. Each delta is side b minus side a, from the unrounded
// values.
func fmtInt(n int) string        { return fmt.Sprint(n) }
func fmtDeltaInt(d int) string   { return fmt.Sprintf("%+d", d) }
func fmtTokens(x float64) string { return commas(int64(math.Round(x))) }
func fmtDeltaTokens(d float64) string {
	n := int64(math.Round(d))
	if n >= 0 {
		return "+" + commas(n)
	}
	return commas(n) // commas writes the "-"
}
func fmtCost(x float64) string { return fmt.Sprintf("$%.5f", x) }

// roundTo rounds d to the given number of decimals. A result of -0 (from a
// tiny negative difference) becomes +0, so it prints as "+0.0", not "-0.0".
func roundTo(d float64, decimals int) float64 {
	p := math.Pow(10, float64(decimals))
	d = math.Round(d*p) / p
	if d == 0 {
		d = 0 // -0 == 0 is true in Go, and this assigns a plain (positive) zero
	}
	return d
}

// fmtDelta writes d with a sign and the given number of decimals.
func fmtDelta(d float64, decimals int) string {
	return fmt.Sprintf("%+.*f", decimals, roundTo(d, decimals)) // "*" takes the precision from the argument list
}

func fmtDeltaCost(d float64) string {
	d = roundTo(d, 5)
	if d < 0 {
		return fmt.Sprintf("-$%.5f", -d)
	}
	return fmt.Sprintf("+$%.5f", d)
}
func fmtRate(n, of int) string { return fmt.Sprintf("%.1f%%", 100*float64(n)/float64(of)) }

// cmpTable prints rows of label | a | b | delta in fixed columns.
type cmpTable struct{ w io.Writer }

const colLabel, colValue = 32, 15 // 2 + 32 + 3*15 = 79 columns at most

func (t cmpTable) row(label, a, b, delta string) {
	// "%-*s" pads to a width given as an argument ("-": on the right, so
	// the label is left-aligned); "%*s" pads on the left (right-aligned).
	line := fmt.Sprintf("  %-*s%*s%*s%*s", colLabel, label, colValue, a, colValue, b, colValue, delta)
	fmt.Fprintln(t.w, strings.TrimRight(line, " "))
}

func (t cmpTable) head() {
	t.row("", "a", "b", "delta (b - a)")
}

// statsRows prints the rows two stats share. steps is the number of
// decimals for mean steps (1 per task, 2 for totals, as in docs/07).
// Either stats may be nil when a task is on one side only.
func statsRows(t cmpTable, a, b *stats, steps int, extra func(t cmpTable)) {
	dash := "–"
	cell := func(s *stats, f func(s *stats) string) string {
		if s == nil {
			return dash
		}
		return f(s)
	}
	delta := func(f func(a, b *stats) string) string {
		if a == nil || b == nil {
			return dash
		}
		return f(a, b)
	}
	ints := func(label string, get func(s *stats) int) {
		t.row(label,
			cell(a, func(s *stats) string { return fmtInt(get(s)) }),
			cell(b, func(s *stats) string { return fmtInt(get(s)) }),
			delta(func(a, b *stats) string { return fmtDeltaInt(get(b) - get(a)) }))
	}
	ofRuns := func(label string, get func(s *stats) int) {
		t.row(label,
			cell(a, func(s *stats) string { return fmt.Sprintf("%d/%d", get(s), s.runs) }),
			cell(b, func(s *stats) string { return fmt.Sprintf("%d/%d", get(s), s.runs) }),
			delta(func(a, b *stats) string { return fmtDeltaInt(get(b) - get(a)) }))
	}
	ints("runs", func(s *stats) int { return s.runs })
	ofRuns("passed", func(s *stats) int { return s.passed })
	ofRuns("returned FAIL", func(s *stats) int { return s.returnedFail })
	if extra != nil {
		extra(t)
	}
	for _, oc := range []struct{ label, key string }{
		{"outcome OK", OutcomeOK},
		{"outcome UNEXPECTED PASS", OutcomeUnexpectedPass},
		{"outcome UNEXPECTED FAIL", OutcomeUnexpectedFail},
		{"harness errors", OutcomeError},
	} {
		key := oc.key // a copy for the closure below
		ints(oc.label, func(s *stats) int { return s.outcomes[key] })
	}
	t.row("mean steps",
		cell(a, func(s *stats) string { return fmt.Sprintf("%.*f", steps, s.meanSteps()) }),
		cell(b, func(s *stats) string { return fmt.Sprintf("%.*f", steps, s.meanSteps()) }),
		delta(func(a, b *stats) string { return fmtDelta(b.meanSteps()-a.meanSteps(), steps) }))
	t.row("mean tokens (input + output)",
		cell(a, func(s *stats) string { return fmtTokens(s.meanTokens()) }),
		cell(b, func(s *stats) string { return fmtTokens(s.meanTokens()) }),
		delta(func(a, b *stats) string { return fmtDeltaTokens(b.meanTokens() - a.meanTokens()) }))
	ints("denied calls", func(s *stats) int { return s.denied })
	t.row("total cost (estimated)",
		cell(a, func(s *stats) string { return fmtCost(s.cost) }),
		cell(b, func(s *stats) string { return fmtCost(s.cost) }),
		delta(func(a, b *stats) string { return fmtDeltaCost(b.cost - a.cost) }))
}

// group is a totals block: the rows of one side whose expected verdict is
// in want ("" means every row).
func group(sd *side, want string) *stats {
	s := &stats{}
	for _, r := range sd.rows {
		if want == "" || r.Expected == want {
			s.add(r)
		}
	}
	if s.runs == 0 {
		return nil
	}
	return s
}

func printCompare(w io.Writer, logPath string, a, b *side, warnings []string) {
	p := &printer{w: w}
	p.line(0, "apg compare: side a vs side b")
	p.line(0, fmt.Sprintf("read-only, from %s and the traces it cites; no model calls", logPath))
	printSide(p, "a", a)
	printSide(p, "b", b)

	fmt.Fprintln(w)
	if len(warnings) == 0 {
		p.line(0, "warnings: none")
	} else {
		p.line(0, fmt.Sprintf("warnings (%d):", len(warnings)))
		for _, x := range warnings {
			p.wrap(2, "! ", "  ", x)
		}
	}

	t := cmpTable{w}
	fmt.Fprintln(w)
	p.line(0, "per task")
	for _, id := range taskOrder(a, b) {
		ta, tb := a.tasks[id], b.tasks[id]
		var sa, sb *stats
		exp := ""
		if ta != nil {
			sa, exp = &ta.stats, strings.Join(ta.expected, "/")
		}
		if tb != nil {
			sb = &tb.stats
			if exp == "" {
				exp = strings.Join(tb.expected, "/")
			}
		}
		fmt.Fprintln(w)
		p.line(0, fmt.Sprintf("%s (expected %s)", id, exp))
		t.head()
		statsRows(t, sa, sb, 1, nil)
	}

	fmt.Fprintln(w)
	p.line(0, "totals")
	for _, g := range []struct {
		title, want, rateLabel string
		rate                   func(s *stats) int
	}{
		{"normal tasks (expected PASS)", trace.VerdictPass, "pass rate", func(s *stats) int { return s.passed }},
		{"failure tasks (expected FAIL)", trace.VerdictFail, "returned FAIL rate", func(s *stats) int { return s.returnedFail }},
		{"all tasks", "", "outcome OK rate", func(s *stats) int { return s.outcomes[OutcomeOK] }},
	} {
		ga, gb := group(a, g.want), group(b, g.want)
		fmt.Fprintln(w)
		p.line(0, fmt.Sprintf("%s: %s", g.title, groupTasks(a, b, g.want)))
		t.head()
		rate := g.rate // a copy for the closure below
		statsRows(t, ga, gb, 2, func(t cmpTable) {
			ra, rb, d := "–", "–", "–"
			if ga != nil {
				ra = fmtRate(rate(ga), ga.runs)
			}
			if gb != nil {
				rb = fmtRate(rate(gb), gb.runs)
			}
			if ga != nil && gb != nil {
				pa := 100 * float64(rate(ga)) / float64(ga.runs)
				pb := 100 * float64(rate(gb)) / float64(gb.runs)
				d = fmtDelta(pb-pa, 1) + " pp"
			}
			t.row(g.rateLabel, ra, rb, d)
		})
		if ga != nil && gb != nil {
			t.row("total tokens", commas(ga.tokens), commas(gb.tokens), fmtDeltaTokens(float64(gb.tokens-ga.tokens)))
		}
	}

	fmt.Fprintln(w)
	p.line(0, "notes")
	p.line(2, "delta is b minus a, computed before rounding; pp: percentage points.")
	p.line(2, "Costs are estimates from list prices (internal/budget), not billed amounts.")
	p.line(2, "Tokens are input + output per run, from each trace's budget.used.")
	p.line(2, "No significance test is computed.")
}

// groupTasks lists the tasks of a totals block, with how many there are.
func groupTasks(a, b *side, want string) string {
	var ids []string
	for _, id := range taskOrder(a, b) {
		for _, sd := range []*side{a, b} {
			// slices.Contains: is want one of the task's expected verdicts?
			if ti := sd.tasks[id]; ti != nil && (want == "" || slices.Contains(ti.expected, want)) {
				ids = appendNew(ids, id)
			}
		}
	}
	nums := make([]string, len(ids))
	for i, id := range ids {
		nums[i] = short(id, 3) // "006-ledger-cents" -> "006"
	}
	return fmt.Sprintf("%d tasks (%s)", len(ids), strings.Join(nums, ", "))
}

// printSide prints one side's header block.
func printSide(p *printer, name string, sd *side) {
	ids := make([]string, len(sd.evals))
	for i, e := range sd.evals {
		ids[i] = e.EvalID
	}
	vals := func(f func(e evalEntry) string) string {
		return strings.Join(evalValues(f)(sd), "; ")
	}
	var truncs []string
	for _, r := range sd.rows {
		truncs = appendNew(truncs, r.truncation)
	}
	clean := "clean"
	for _, e := range sd.evals {
		if e.GitDirty {
			clean = "uncommitted changes"
		}
	}
	contract := vals(func(e evalEntry) string {
		if e.PromptContract == "" {
			return "not recorded (before T5.1)"
		}
		return e.PromptContract
	})
	counts := map[int]bool{}
	for _, id := range sd.order {
		counts[sd.tasks[id].runs] = true
	}
	perTask := "runs per task differ"
	if len(counts) == 1 {
		perTask = fmt.Sprintf("%d per task", sd.tasks[sd.order[0]].runs)
	}

	fmt.Fprintln(p.w)
	p.line(0, fmt.Sprintf("side %s: %s", name, sd.sel.text))
	const pad = "            " // 12 spaces: continuation lines line up under the values
	p.wrap(2, fmt.Sprintf("%-12s", fmt.Sprintf("evals (%d)", len(ids))), pad, strings.Join(ids, ", "))
	p.wrap(2, fmt.Sprintf("%-12s", "set"), pad, vals(func(e evalEntry) string { return e.Set }))
	p.wrap(2, fmt.Sprintf("%-12s", "model"), pad, vals(func(e evalEntry) string { return e.Model }))
	p.wrap(2, fmt.Sprintf("%-12s", "contract"), pad, contract)
	p.wrap(2, fmt.Sprintf("%-12s", "prompt"), pad, vals(func(e evalEntry) string { return e.PromptVersion }))
	p.wrap(2, fmt.Sprintf("%-12s", "commit"), pad, vals(func(e evalEntry) string { return e.GitCommit })+" ("+clean+")")
	p.wrap(2, fmt.Sprintf("%-12s", "split"), pad, vals(func(e evalEntry) string { return e.SplitSHA256 }))
	p.wrap(2, fmt.Sprintf("%-12s", "truncation"), pad, strings.Join(truncs, "; "))
	p.wrap(2, fmt.Sprintf("%-12s", "runs"), pad, fmt.Sprintf("%d (%d tasks, %s)", len(sd.rows), len(sd.order), perTask))
}
