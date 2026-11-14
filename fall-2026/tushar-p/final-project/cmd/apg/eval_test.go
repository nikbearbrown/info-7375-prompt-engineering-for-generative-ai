package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/loop"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

func TestOutcome(t *testing.T) {
	tests := []struct {
		expected, verdict string
		exit              trace.ExitReason
		want              string
	}{
		{"PASS", "PASS", trace.ReasonCheckPassed, OutcomeOK},
		{"FAIL", "FAIL", trace.ReasonBudgetSteps, OutcomeOK},
		{"FAIL", "PASS", trace.ReasonCheckPassed, OutcomeUnexpectedPass},
		{"PASS", "FAIL", trace.ReasonCheckFailed, OutcomeUnexpectedFail},
		{"FAIL", "FAIL", trace.ReasonError, OutcomeError}, // a harness error is never a "no"
		{"PASS", "FAIL", trace.ReasonError, OutcomeError},
	}
	for _, tc := range tests {
		if got := outcome(tc.expected, tc.verdict, tc.exit); got != tc.want {
			t.Errorf("outcome(%s, %s, %s) = %s, want %s", tc.expected, tc.verdict, tc.exit, got, tc.want)
		}
	}
}

func TestSummarize(t *testing.T) {
	row := func(expected, verdict string, exit trace.ExitReason, cost float64) evalRow {
		return evalRow{Expected: expected, Verdict: verdict, ExitReason: string(exit), Outcome: outcome(expected, verdict, exit), CostUSD: cost}
	}
	rows := []evalRow{
		row("PASS", "PASS", trace.ReasonCheckPassed, 0.001),
		row("PASS", "PASS", trace.ReasonCheckPassed, 0.002),
		row("PASS", "FAIL", trace.ReasonCheckFailed, 0.003), // UNEXPECTED FAIL
		row("PASS", "FAIL", trace.ReasonError, 0),           // ERROR: counted in the total, not a pass
		row("FAIL", "FAIL", trace.ReasonBudgetSteps, 0.004), // said no
		row("FAIL", "PASS", trace.ReasonCheckPassed, 0.005), // UNEXPECTED PASS
		row("FAIL", "FAIL", trace.ReasonError, 0),           // ERROR: not a "no"
	}
	s := summarize(rows, 90*time.Second)
	want := evalSummary{ExpectedPassRuns: 4, Passed: 2, PassRate: 0.5, ExpectedFailRuns: 3, SaidNo: 1,
		UnexpectedPass: 1, UnexpectedFail: 1, Errors: 2, WallSeconds: 90}
	cost := s.TotalCostUSD
	s.TotalCostUSD = 0
	if s != want || math.Abs(cost-0.015) > 1e-12 {
		t.Errorf("summary = %+v cost %v\nwant      %+v cost 0.015", s, cost, want)
	}
	if empty := summarize(nil, 0); empty.PassRate != 0 || empty.ExpectedPassRuns != 0 {
		t.Errorf("empty summary = %+v", empty)
	}
}

func TestEvalArgs(t *testing.T) {
	if o, err := parseEvalArgs([]string{"--set", "held-out", "--held-out-ok", "--runs", "3"}); err != nil || !o.heldOutOK || o.runs != 3 {
		t.Errorf("opts %+v err %v", o, err)
	}
	for _, bad := range [][]string{{}, {"--set", "test"}, {"--set", "dev", "--runs", "0"}, {"--set", "dev", "extra"}} {
		if _, err := parseEvalArgs(bad); err == nil {
			t.Errorf("parseEvalArgs(%q) should fail", bad)
		}
	}
}

// The held-out guard refuses before anything runs.
func TestEvalHeldOutGuard(t *testing.T) {
	var stderr bytes.Buffer
	env := evalEnv{
		newSandbox: func() (sandbox.Sandbox, string, error) { t.Fatal("a sandbox was started"); return nil, "", nil },
		git:        func() (string, bool) { return "x", false },
		now:        time.Now,
		stdout:     &bytes.Buffer{},
		stderr:     &stderr,
	}
	code := runEval(context.Background(), env, evalOpts{set: "held-out", runs: 1, tasksDir: t.TempDir()})
	if code != exitError || !strings.Contains(stderr.String(), "held-out is reserved for T5.1") {
		t.Errorf("exit %d, stderr %q", code, stderr.String())
	}
	if err := checkHeldOut(evalOpts{set: "held-out", heldOutOK: true}); err != nil {
		t.Errorf("--held-out-ok should allow it: %v", err)
	}
}

// evalSandbox is exitSandbox (its check exits with checkExit) plus a
// CopyOut that writes one changed file, so the gate has a diff to defer.
type evalSandbox struct{ exitSandbox }

func (s *evalSandbox) CopyOut(_ context.Context, _, host string) (sandbox.Result, error) {
	if err := os.MkdirAll(host, 0o755); err != nil {
		return sandbox.Result{}, err
	}
	return sandbox.Result{Args: []string{"kubectl", "cp"}}, os.WriteFile(filepath.Join(host, "code.py"), []byte("changed\n"), 0o644)
}

// writeEvalTask creates tasksDir/<id> with an expected outcome.
func writeEvalTask(t *testing.T, tasksDir, id, expected string) {
	t.Helper()
	dir := filepath.Join(tasksDir, id)
	if err := os.MkdirAll(filepath.Join(dir, "repo"), 0o755); err != nil {
		t.Fatal(err)
	}
	exp := `{"verdict": "PASS"}`
	if expected == "FAIL" {
		exp = `{"verdict": "FAIL", "likely_exit_reasons": ["check_failed"], "why_no_fix": "a test task"}`
	}
	files := map[string]string{
		"repo/code.py": "original\n",
		"check.sh":     "exit 0\n",
		"contract.json": `{"id": "` + id + `", "goal": "g", "allowed_tools": ["read_file", "write_file", "run_command"], "max_steps": 3,
			"max_total_tokens": 100000, "max_cost_usd": 1, "timeout_seconds": 60, "max_policy_violations": 3, "expected": ` + exp + `}`,
	}
	for name, body := range files {
		if err := os.WriteFile(filepath.Join(dir, name), []byte(body), 0o644); err != nil {
			t.Fatal(err)
		}
	}
}

// End to end with fakes: three tasks (an expected PASS that passes, an
// expected FAIL that fails, and an expected FAIL that passes), run twice.
// Checks the table, the loud UNEXPECTED PASS block, the forced defer, the
// prompt version in every trace, and the eval-log line format.
func TestEvalEndToEnd(t *testing.T) {
	root := t.TempDir()
	tasksDir := filepath.Join(root, "tasks")
	writeEvalTask(t, tasksDir, "001-pass", "PASS")
	writeEvalTask(t, tasksDir, "002-says-no", "FAIL")
	writeEvalTask(t, tasksDir, "003-sneaky", "FAIL")
	split := `{"seed": 1, "dev": ["001-pass", "002-says-no", "003-sneaky"], "held_out": []}`
	if err := os.WriteFile(filepath.Join(tasksDir, "split.json"), []byte(split), 0o644); err != nil {
		t.Fatal(err)
	}
	checkExits := []int{0, 1, 0} // what each task's check returns, in split order
	opts := evalOpts{set: "dev", runs: 2, tasksDir: tasksDir, tracesDir: filepath.Join(root, "traces"),
		outDir: filepath.Join(root, "out"), resultsDir: filepath.Join(root, "results")}

	evalOnce := func() (int, string, *stopClient) {
		n := 0
		client := &stopClient{turns: []turn{doneTurn, doneTurn, doneTurn, doneTurn, doneTurn, doneTurn}}
		var stdout, stderr bytes.Buffer
		env := evalEnv{
			newSandbox: func() (sandbox.Sandbox, string, error) {
				sb := &evalSandbox{exitSandbox{checkExit: checkExits[n/opts.runs]}}
				n++
				return sb, fmt.Sprintf("apg-fake%d%d", time.Now().UnixNano()%1e6, n), nil
			},
			client: client,
			git:    func() (string, bool) { return "abc1234", true },
			now:    time.Now,
			stdout: &stdout,
			stderr: &stderr,
		}
		return runEval(context.Background(), env, opts), stdout.String(), client
	}

	code, out, client := evalOnce()
	if code != exitFail {
		t.Errorf("exit %d, want %d (an UNEXPECTED PASS is not success)", code, exitFail)
	}
	if len(client.requests) != 6 {
		t.Errorf("model calls = %d, want 6 (3 tasks x 2 runs)", len(client.requests))
	}
	for _, want := range []string{
		"task", "expected", "outcome", "exit reason",
		"001-pass #1", "001-pass #2", "002-says-no #2", "UNEXPECTED PASS !!!",
		"!!! UNEXPECTED PASS: 003-sneaky #1", "This is not a success.",
		"pass rate (expected PASS): 2/2 runs (100.0%)",
		"said no (expected FAIL):   2/4 runs",
		"UNEXPECTED PASS:           2",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("output lacks %q:\n%s", want, out)
		}
	}

	// The eval-log line: strict decode, and every row's trace defers in eval mode.
	logPath := filepath.Join(opts.resultsDir, "eval-log.jsonl")
	entries, err := readLog(logPath)
	if err != nil || len(entries) != 1 {
		t.Fatalf("eval log: %d entries, %v", len(entries), err)
	}
	e := entries[0]
	if e.GitCommit != "abc1234" || !e.GitDirty || e.Model != model || e.PromptVersion != loop.PromptVersion() ||
		e.Set != "dev" || e.Runs != 2 || !e.Complete || len(e.Rows) != 6 || len(e.SplitSHA256) != 64 || e.EvalID == "" {
		t.Errorf("entry = %+v", e)
	}
	wantOutcomes := []string{OutcomeOK, OutcomeOK, OutcomeOK, OutcomeOK, OutcomeUnexpectedPass, OutcomeUnexpectedPass}
	for i, r := range e.Rows {
		if r.Outcome != wantOutcomes[i] || r.Gate != "deferred" || len(r.ContractSHA256) != 64 || r.Trace == "" {
			t.Errorf("row %d = %+v", i, r)
		}
		f, err := os.Open(r.Trace)
		if err != nil {
			t.Fatal(err)
		}
		tr, err := trace.Decode(f)
		f.Close()
		if err != nil {
			t.Fatal(err)
		}
		if tr.PromptVersion != loop.PromptVersion() || tr.Gate == nil || !tr.Gate.Batch || tr.Gate.Decision != "deferred" || len(tr.Gate.Shown) != 0 {
			t.Errorf("trace %s: prompt %q gate %+v", r.Trace, tr.PromptVersion, tr.Gate)
		}
	}
	// Every key of the line format is present.
	raw, _ := os.ReadFile(logPath)
	var keys map[string]json.RawMessage
	if err := json.Unmarshal(bytes.TrimSpace(raw), &keys); err != nil {
		t.Fatal(err)
	}
	for _, k := range []string{"eval_id", "timestamp", "git_commit", "git_dirty", "model", "prompt_version", "split_sha256", "set", "runs", "complete", "rows", "summary"} {
		if _, ok := keys[k]; !ok {
			t.Errorf("eval-log line lacks %q", k)
		}
	}

	// A second eval appends a line, and EVAL-LOG.md shows both.
	evalOnce()
	entries, err = readLog(logPath)
	md, _ := os.ReadFile(filepath.Join(opts.resultsDir, "EVAL-LOG.md"))
	if err != nil || len(entries) != 2 || strings.Count(string(md), "\n## ") != 2 || !strings.Contains(string(md), "**UNEXPECTED PASS** (review the trace)") {
		t.Errorf("after two evals: %d entries (%v); EVAL-LOG.md:\n%s", len(entries), err, md)
	}
}
