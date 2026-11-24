package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
	"unicode/utf8"

	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// updateCompare rewrites the apg compare golden file:
// go test ./cmd/apg -run TestCompareT51 -update-compare (then read the diff).
var updateCompare = flag.Bool("update-compare", false, "rewrite the apg compare golden file")

// The real T5.1 data: the committed eval log and the trace copies.
const (
	realLog    = "../../results/eval-log.jsonl"
	realTraces = "../../evidence/traces"
	t51A       = "contract=A,commit=6d7bafe,set=held-out"
	t51B       = "contract=B,commit=6d7bafe,set=held-out"
)

// loadReal builds one side from the real eval log, as compareMain does.
func loadReal(t *testing.T, text string) *side {
	t.Helper()
	sel, err := parseSide(text)
	if err != nil {
		t.Fatal(err)
	}
	entries, err := readLog(realLog)
	if err != nil {
		t.Fatal(err)
	}
	evals, err := selectEvals(entries, sel)
	if err != nil {
		t.Fatal(err)
	}
	sd, err := loadSide(sel, evals, realTraces)
	if err != nil {
		t.Fatal(err)
	}
	return sd
}

// TestCompareT51MatchesDocs07 checks apg compare's numbers on the T5.1
// held-out runs against the two tables in docs/07-evidence.md ("Held-out
// results (T5.1)"), copied here by hand. If one differs, the fix is not to
// edit docs/07 to match: find out which one is wrong first.
func TestCompareT51MatchesDocs07(t *testing.T) {
	a, b := loadReal(t, t51A), loadReal(t, t51B)
	if len(a.evals) != 5 || len(b.evals) != 5 {
		t.Fatalf("want 5 evals per side, got %d and %d", len(a.evals), len(b.evals))
	}
	sides := map[string]*side{"A": a, "B": b}

	// docs/07 "Per task and contract": task, contract, passes, mean steps,
	// denied, mean tokens, total cost.
	perTask := []struct{ task, contract, passes, steps, denied, tokens, cost string }{
		{"006-ledger-cents", "A", "5/5", "5.8", "0", "10,591", "$0.00687"},
		{"006-ledger-cents", "B", "5/5", "5.6", "0", "13,772", "$0.00853"},
		{"007-booking-slots", "A", "5/5", "4.0", "0", "7,782", "$0.00597"},
		{"007-booking-slots", "B", "5/5", "6.0", "0", "19,733", "$0.01277"},
		{"008-config-parser", "A", "5/5", "4.6", "0", "17,777", "$0.01527"},
		{"008-config-parser", "B", "5/5", "6.4", "4", "31,869", "$0.02146"},
		{"011-shared-default", "A", "5/5", "5.0", "0", "7,846", "$0.00523"},
		{"011-shared-default", "B", "5/5", "4.4", "0", "9,522", "$0.00613"},
		{"012-wrong-test", "A", "0/5", "6.2", "0", "10,381", "$0.00747"},
		{"012-wrong-test", "B", "0/5", "6.2", "0", "14,647", "$0.01004"},
		{"015-tiny-budget", "A", "0/5", "1.0", "0", "1,242", "$0.00101"},
		{"015-tiny-budget", "B", "0/5", "1.0", "0", "1,904", "$0.00141"},
		{"016-contradictory-spec", "A", "0/5", "4.2", "0", "6,697", "$0.00529"},
		{"016-contradictory-spec", "B", "0/5", "4.0", "0", "8,658", "$0.00602"},
	}
	for _, w := range perTask {
		ti := sides[w.contract].tasks[w.task]
		if ti == nil {
			t.Errorf("%s %s: missing", w.task, w.contract)
			continue
		}
		got := []string{fmt.Sprintf("%d/%d", ti.passed, ti.runs), fmt.Sprintf("%.1f", ti.meanSteps()),
			fmt.Sprint(ti.denied), fmtTokens(ti.meanTokens()), fmtCost(ti.cost)}
		want := []string{w.passes, w.steps, w.denied, w.tokens, w.cost}
		for i, name := range []string{"passes", "mean steps", "denied", "mean tokens", "total cost"} {
			if got[i] != want[i] {
				t.Errorf("%s %s %s: apg compare %s, docs/07 %s", w.task, w.contract, name, got[i], want[i])
			}
		}
	}

	// docs/07 "Per contract": group, contract, runs, PASS, FAIL, mean
	// steps, denied, mean tokens, total tokens, total cost.
	perGroup := []struct{ group, contract, runs, pass, fail, steps, denied, mean, total, cost string }{
		{trace.VerdictPass, "A", "20", "20", "0", "4.85", "0", "10,999", "219,974", "$0.03334"},
		{trace.VerdictPass, "B", "20", "20", "0", "5.60", "4", "18,724", "374,478", "$0.04890"},
		{trace.VerdictFail, "A", "15", "0", "15", "3.80", "0", "6,106", "91,596", "$0.01377"},
		{trace.VerdictFail, "B", "15", "0", "15", "3.73", "0", "8,403", "126,044", "$0.01748"},
		{"", "A", "35", "20", "15", "4.40", "0", "8,902", "311,570", "$0.04711"},
		{"", "B", "35", "20", "15", "4.80", "4", "14,301", "500,522", "$0.06637"},
	}
	for _, w := range perGroup {
		g := group(sides[w.contract], w.group)
		got := []string{fmt.Sprint(g.runs), fmt.Sprint(g.passed), fmt.Sprint(g.returnedFail), fmt.Sprintf("%.2f", g.meanSteps()),
			fmt.Sprint(g.denied), fmtTokens(g.meanTokens()), commas(g.tokens), fmtCost(g.cost)}
		want := []string{w.runs, w.pass, w.fail, w.steps, w.denied, w.mean, w.total, w.cost}
		for i, name := range []string{"runs", "PASS", "FAIL", "mean steps", "denied", "mean tokens", "total tokens", "total cost"} {
			if got[i] != want[i] {
				t.Errorf("group %q %s %s: apg compare %s, docs/07 %s", w.group, w.contract, name, got[i], want[i])
			}
		}
	}

	// The printout itself: no warnings, 80 columns, golden text.
	var out, errOut bytes.Buffer
	code := compareMain([]string{t51A, t51B, "--log", realLog, "--traces", realTraces}, &out, &errOut)
	if code != exitPass {
		t.Fatalf("exit %d: %s", code, errOut.String())
	}
	got := out.String()
	for _, s := range []string{"warnings: none", "pass rate", "+0.0 pp", "returned FAIL rate"} {
		if !strings.Contains(got, s) {
			t.Errorf("output lacks %q", s)
		}
	}
	if strings.Contains(got, "said no") {
		t.Error(`output says "said no"; use "returned FAIL"`)
	}
	for i, l := range strings.Split(got, "\n") {
		if n := utf8.RuneCountInString(l); n > width {
			t.Errorf("line %d is %d columns: %q", i+1, n, l)
		}
	}
	golden := filepath.Join("testdata", "compare", "t51.golden")
	if *updateCompare {
		if err := os.MkdirAll(filepath.Dir(golden), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(golden, []byte(got), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	want, err := os.ReadFile(golden)
	if err != nil {
		t.Fatalf("%v (run with -update-compare to create it)", err)
	}
	if got != string(want) {
		t.Errorf("output differs from %s (run with -update-compare, then read the diff):\n%s", golden, got)
	}
}

func TestParseSide(t *testing.T) {
	good := []struct {
		in     string
		ids    []string
		filter map[string]string
	}{
		{"20261118T034100Z-57e06904", []string{"20261118T034100Z-57e06904"}, nil},
		{"E1,E2,E3", []string{"E1", "E2", "E3"}, nil},
		{"contract=A,commit=6d7bafe,set=held-out", nil, map[string]string{"contract": "A", "commit": "6d7bafe", "set": "held-out"}},
		{"model=claude-haiku-5-5", nil, map[string]string{"model": "claude-haiku-5-5"}},
		{"commit=6d7bafe132844b2649be527f36427452667dd9a8", nil, map[string]string{"commit": "6d7bafe132844b2649be527f36427452667dd9a8"}},
	}
	for _, tc := range good {
		sel, err := parseSide(tc.in)
		if err != nil {
			t.Errorf("%q: %v", tc.in, err)
			continue
		}
		if fmt.Sprint(sel.ids) != fmt.Sprint(tc.ids) || fmt.Sprint(sel.filter) != fmt.Sprint(tc.filter) {
			t.Errorf("%q: got ids %v filter %v", tc.in, sel.ids, sel.filter)
		}
	}
	bad := []struct{ in, want string }{
		{"E1,contract=A", "mixes eval IDs"},
		{"color=red", "unknown key"},
		{"contract=A,contract=B", "given twice"},
		{"E1,,E2", "empty part"},
		{"E1,E1", "twice"},
		{"contract=", "no value"},
		{"commit=6d7b", "at least 7 hex"},
		{"commit=XYZ1234", "at least 7 hex"},
		{"../etc", "not an eval ID"},
	}
	for _, tc := range bad {
		_, err := parseSide(tc.in)
		if err == nil || !strings.Contains(err.Error(), tc.want) {
			t.Errorf("%q: got %v, want an error with %q", tc.in, err, tc.want)
		}
	}
}

// fakeRun and fakeEval describe a small synthetic eval log for the tests
// below. Each run gets a real, valid trace (trace.Write), so loadSide reads
// it with the same strict decode as for real traces.
type fakeRun struct {
	task, expected, verdict string
	steps, denied           int
	tokens                  int64
	cost                    float64
	noTruncation            bool   // a trace from before D26
	contractSHA             string // the task's contract.json hash; "" means "c1"
}

type fakeEval struct {
	id, set, model, contract, commit, split string
	runs                                    []fakeRun
}

// baseEval is one eval with a normal task and a failure task.
func baseEval(id, contract string) fakeEval {
	return fakeEval{
		id: id, set: "dev", model: "m-1", contract: contract,
		commit: "aaaaaaa1111111111111111111111111111111aa", split: "s1",
		runs: []fakeRun{
			{task: "001-x", expected: "PASS", verdict: "PASS", steps: 4, tokens: 1000, cost: 0.001},
			{task: "012-y", expected: "FAIL", verdict: "FAIL", steps: 3, tokens: 500, cost: 0.0005},
		},
	}
}

// writeFixture writes the evals' log and traces under dir.
func writeFixture(t *testing.T, dir string, evals ...fakeEval) (logPath, tracesDir string) {
	t.Helper()
	tracesDir = filepath.Join(dir, "traces")
	var log bytes.Buffer
	start := time.Date(2026, 11, 18, 0, 0, 0, 0, time.UTC)
	for _, fe := range evals {
		e := evalEntry{
			EvalID: fe.id, Timestamp: start, GitCommit: fe.commit, Model: fe.model,
			PromptVersion: "pv-" + fe.contract, PromptContract: fe.contract,
			SplitSHA256: fe.split, Set: fe.set, Runs: 1, Complete: true, Rows: []evalRow{},
		}
		for i, r := range fe.runs {
			runID := fmt.Sprintf("%s-r%d", fe.id, i+1)
			code, reason := 1, trace.ReasonCheckFailed
			if r.verdict == trace.VerdictPass {
				code, reason = 0, trace.ReasonCheckPassed
			}
			steps := make([]trace.Step, r.steps)
			for j := range steps {
				steps[j] = trace.Step{N: j + 1, StopReason: "tool_use"}
			}
			var cut *trace.Truncation
			if !r.noTruncation {
				cut = &trace.Truncation{LimitBytes: 8192, HeadBytes: 4096, TailBytes: 4096}
			}
			tr := &trace.Trace{
				SchemaVersion: trace.SchemaVersion, RunID: runID, TaskID: r.task, Pod: "apg-test",
				StartedAt: start, EndedAt: start.Add(time.Second),
				Steps: steps, ExitReason: reason, Verdict: r.verdict,
				Check: trace.Check{Ran: true, ExitCode: &code},
				Model: fe.model, PromptVersion: "pv-" + fe.contract, PromptContract: fe.contract,
				Budget: &trace.Budget{FromContract: []string{"max_steps"}, Used: trace.BudgetUsed{
					Steps: r.steps, InputTokens: r.tokens, TotalTokens: r.tokens, CostUSD: r.cost, PolicyViolations: r.denied}},
				Truncation: cut,
			}
			if _, err := trace.Write(tracesDir, tr); err != nil {
				t.Fatal(err)
			}
			sha := r.contractSHA
			if sha == "" {
				sha = "c1"
			}
			e.Rows = append(e.Rows, evalRow{
				Task: r.task, Run: 1, Expected: r.expected, Verdict: r.verdict,
				Outcome: outcome(r.expected, r.verdict, reason), Steps: r.steps, Denied: r.denied,
				ExitReason: string(reason), CostUSD: r.cost, Gate: "deferred", ContractSHA256: sha,
				Trace: "traces/" + runID + ".json",
			})
		}
		e.Summary = summarize(e.Rows, 0)
		b, err := json.Marshal(e)
		if err != nil {
			t.Fatal(err)
		}
		log.Write(append(b, '\n'))
	}
	logPath = filepath.Join(dir, "eval-log.jsonl")
	if err := os.WriteFile(logPath, log.Bytes(), 0o644); err != nil {
		t.Fatal(err)
	}
	return logPath, tracesDir
}

// runCompare runs apg compare on a fixture and returns exit code, stdout, stderr.
func runCompare(t *testing.T, evals []fakeEval, args ...string) (int, string, string) {
	t.Helper()
	logPath, tracesDir := writeFixture(t, t.TempDir(), evals...)
	var out, errOut bytes.Buffer
	code := compareMain(append(args, "--log", logPath, "--traces", tracesDir), &out, &errOut)
	return code, out.String(), errOut.String()
}

func TestCompareNoWarnings(t *testing.T) {
	code, out, errOut := runCompare(t, []fakeEval{baseEval("A1", "A"), baseEval("B1", "B")}, "A1", "contract=B")
	if code != exitPass {
		t.Fatalf("exit %d: %s", code, errOut)
	}
	if !strings.Contains(out, "warnings: none") {
		t.Errorf("want no warnings:\n%s", out)
	}
}

// Each change to side b (or a second eval on side a) must print its warning
// before the first table.
func TestCompareWarnings(t *testing.T) {
	cases := []struct {
		name  string
		sideA string
		evals func() []fakeEval
		want  string
	}{
		{"model", "A1", func() []fakeEval {
			b := baseEval("B1", "B")
			b.model = "m-2"
			return []fakeEval{baseEval("A1", "A"), b}
		}, "model differs: a m-1, b m-2"},
		{"commit", "A1", func() []fakeEval {
			b := baseEval("B1", "B")
			b.commit = "bbbbbbb2222222222222222222222222222222bb"
			return []fakeEval{baseEval("A1", "A"), b}
		}, "commit differs: a aaaaaaa11111, b bbbbbbb22222"},
		{"truncation", "A1", func() []fakeEval {
			b := baseEval("B1", "B")
			b.runs[0].noTruncation, b.runs[1].noTruncation = true, true
			return []fakeEval{baseEval("A1", "A"), b}
		}, "truncation differs: a limit 8192, head 4096, tail 4096, b not recorded (before D26)"},
		{"runs per task", "A1", func() []fakeEval {
			b := baseEval("B1", "B")
			b.runs = append(b.runs, b.runs[0])
			return []fakeEval{baseEval("A1", "A"), b}
		}, "runs per task differ for 001-x: a 1, b 2"},
		{"task on one side", "A1", func() []fakeEval {
			b := baseEval("B1", "B")
			b.runs = append(b.runs, fakeRun{task: "013-z", expected: "FAIL", verdict: "FAIL", steps: 2, tokens: 10, cost: 0.00001})
			return []fakeEval{baseEval("A1", "A"), b}
		}, "task 013-z is only on side b"},
		{"contract.json", "A1", func() []fakeEval {
			b := baseEval("B1", "B")
			b.runs[0].contractSHA = "c2"
			return []fakeEval{baseEval("A1", "A"), b}
		}, "contract.json of 001-x differs (SHA-256): a c1, b c2"},
		{"mixed side", "A1,A2", func() []fakeEval {
			a2 := baseEval("A2", "A")
			a2.commit = "ccccccc3333333333333333333333333333333cc"
			return []fakeEval{baseEval("A1", "A"), a2, baseEval("B1", "B")}
		}, "side a mixes commit: aaaaaaa11111; ccccccc33333"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			code, out, errOut := runCompare(t, tc.evals(), tc.sideA, "B1")
			if code != exitPass {
				t.Fatalf("exit %d: %s", code, errOut)
			}
			// The part before the "per task" heading line, with the wrapped
			// lines joined back (strings.Fields splits on any run of spaces
			// and newlines), must hold the warning.
			head, _, found := strings.Cut(out, "\nper task\n")
			if !found {
				t.Fatalf("no per-task section in:\n%s", out)
			}
			if !strings.Contains(strings.Join(strings.Fields(head), " "), tc.want) {
				if strings.Contains(strings.Join(strings.Fields(out), " "), tc.want) {
					t.Fatalf("warning %q printed after the tables", tc.want)
				}
				t.Fatalf("no warning %q in:\n%s", tc.want, out)
			}
		})
	}
}

func TestCompareRefusesSetOrSplit(t *testing.T) {
	for _, tc := range []struct {
		name   string
		change func(e *fakeEval)
		want   string
	}{
		{"set", func(e *fakeEval) { e.set = "held-out" }, "set differs: a dev, b held-out"},
		{"split", func(e *fakeEval) { e.split = "s2" }, "split.json SHA-256 differs: a s1, b s2"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			b := baseEval("B1", "B")
			tc.change(&b)
			evals := []fakeEval{baseEval("A1", "A"), b}
			code, out, errOut := runCompare(t, evals, "A1", "B1")
			if code != exitError || !strings.Contains(errOut, "refused: "+tc.want) || out != "" {
				t.Errorf("without --force: exit %d, stdout %q, stderr %q", code, out, errOut)
			}
			code, out, errOut = runCompare(t, evals, "A1", "B1", "--force")
			if code != exitPass || !strings.Contains(out, tc.want) {
				t.Errorf("with --force: exit %d, stderr %q, stdout:\n%s", code, errOut, out)
			}
		})
	}
}

func TestCompareUnknownEvalID(t *testing.T) {
	evals := []fakeEval{baseEval("A1", "A"), baseEval("B1", "B")}
	code, _, errOut := runCompare(t, evals, "A1,NOPE", "B1")
	if code != exitError || !strings.Contains(errOut, "unknown eval ID NOPE") {
		t.Errorf("exit %d, stderr %q", code, errOut)
	}
	code, _, errOut = runCompare(t, evals, "A1", "contract=B,model=other")
	if code != exitError || !strings.Contains(errOut, "no eval in the log matches") {
		t.Errorf("filter with no match: exit %d, stderr %q", code, errOut)
	}
}

func TestCompareSameEvalBothSides(t *testing.T) {
	code, _, errOut := runCompare(t, []fakeEval{baseEval("A1", "A"), baseEval("B1", "B")}, "A1", "A1,B1")
	if code != exitError || !strings.Contains(errOut, "eval A1 is on both sides") {
		t.Errorf("exit %d, stderr %q", code, errOut)
	}
}

// A trace that disagrees with its eval-log row stops the comparison.
func TestCompareTraceDisagreesWithLog(t *testing.T) {
	dir := t.TempDir()
	logPath, tracesDir := writeFixture(t, dir, baseEval("A1", "A"), baseEval("B1", "B"))
	b, err := os.ReadFile(logPath)
	if err != nil {
		t.Fatal(err)
	}
	// The log now says 001-x in A1 cost more than its trace says.
	b = bytes.Replace(b, []byte(`"cost_usd":0.001`), []byte(`"cost_usd":0.002`), 1)
	if err := os.WriteFile(logPath, b, 0o644); err != nil {
		t.Fatal(err)
	}
	var out, errOut bytes.Buffer
	code := compareMain([]string{"A1", "B1", "--log", logPath, "--traces", tracesDir}, &out, &errOut)
	if code != exitError || !strings.Contains(errOut.String(), "differ from the eval log") {
		t.Errorf("exit %d, stderr %q", code, errOut.String())
	}
}
