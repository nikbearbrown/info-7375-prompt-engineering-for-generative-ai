package trace

import (
	"encoding/json"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
)

// good returns a valid trace; tests change one field at a time.
func good() *Trace {
	start := time.Date(2026, 11, 12, 5, 1, 2, 0, time.UTC)
	return &Trace{
		SchemaVersion: SchemaVersion,
		RunID:         "20261112T050102Z-1a2b3c4d",
		TaskID:        "001-fix-function",
		Pod:           "apg-1a2b3c4d",
		StartedAt:     start,
		EndedAt:       start.Add(9 * time.Second),
		Commands: []Command{{
			Phase: PhaseCheck,
			Result: sandbox.Result{
				Args:     []string{"kubectl", "exec", "apg-1a2b3c4d", "--", "bash", "/tmp/check.sh"},
				Stdout:   "> assert 3 == 3.5\n1 failed, 3 passed\n",
				ExitCode: 1,
			},
		}},
		ExitReason: ReasonCheckFailed,
		Verdict:    VerdictFail,
	}
}

func TestValidate(t *testing.T) {
	// Table-driven test: each row is a name, a change to a good trace, and
	// whether Validate should fail.
	tests := []struct {
		name    string
		change  func(*Trace)
		wantErr bool
	}{
		{"good", func(*Trace) {}, false},
		{"path traversal run id", func(tr *Trace) { tr.RunID = "../x" }, true},
		{"slash in run id", func(tr *Trace) { tr.RunID = "a/b" }, true},
		{"empty run id", func(tr *Trace) { tr.RunID = "" }, true},
		{"empty task", func(tr *Trace) { tr.TaskID = "" }, true},
		{"unknown reason", func(tr *Trace) { tr.ExitReason = "model_said_done" }, true},
		{"bad verdict", func(tr *Trace) { tr.Verdict = "pass" }, true},
		{"wrong schema", func(tr *Trace) { tr.SchemaVersion = 1 }, true},
	}
	for _, tc := range tests {
		// t.Run makes each row its own subtest, named in the output.
		t.Run(tc.name, func(t *testing.T) {
			tr := good()
			tc.change(tr)
			err := tr.Validate()
			if (err != nil) != tc.wantErr {
				t.Errorf("Validate() err = %v, wantErr %v", err, tc.wantErr)
			}
		})
	}
}

func TestEveryPlanExitReasonIsValid(t *testing.T) {
	// The fixed list from PLAN.md T2.2.
	for _, r := range []string{"check_passed", "check_failed", "budget_steps", "budget_tokens",
		"budget_cost", "timeout", "policy_violation_limit", "gate_refused", "gate_deferred", "error"} {
		if !ValidExitReason(r) {
			t.Errorf("%q should be valid", r)
		}
	}
}

func TestWriteRoundTrip(t *testing.T) {
	dir := filepath.Join(t.TempDir(), "traces") // does not exist yet: Write creates it
	want := good()
	path, err := Write(dir, want)
	if err != nil {
		t.Fatal(err)
	}
	if path != filepath.Join(dir, want.RunID+".json") {
		t.Errorf("path = %q", path)
	}
	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var got Trace
	if err := json.Unmarshal(b, &got); err != nil {
		t.Fatal(err)
	}
	// reflect.DeepEqual compares nested structs and slices field by field.
	if !reflect.DeepEqual(&got, want) {
		t.Errorf("round trip mismatch:\n got %+v\nwant %+v", got, *want)
	}

	// The embedded Result's fields sit inline in each command, and an
	// empty Steps list is written as [] (not null).
	s := string(b)
	for _, frag := range []string{`"phase": "check"`, `"exit_code": 1`, `"args": [`, `"steps": []`, `"> assert`} {
		if !strings.Contains(s, frag) {
			t.Errorf("trace JSON missing %s:\n%s", frag, s)
		}
	}
	if strings.Contains(s, `"error"`) {
		t.Error(`empty Error should be omitted`)
	}
}

func TestWriteNeverOverwrites(t *testing.T) {
	dir := t.TempDir()
	if _, err := Write(dir, good()); err != nil {
		t.Fatal(err)
	}
	if _, err := Write(dir, good()); err == nil {
		t.Error("second Write with the same run ID should fail")
	}
}

func TestWriteRejectsInvalid(t *testing.T) {
	dir := t.TempDir()
	tr := good()
	tr.RunID = "../escape"
	if _, err := Write(dir, tr); err == nil {
		t.Fatal("Write should reject an invalid trace")
	}
	// Nothing may be written, inside or next to dir.
	if entries, _ := os.ReadDir(dir); len(entries) != 0 {
		t.Errorf("dir should be empty, has %d entries", len(entries))
	}
	if _, err := os.Stat(filepath.Join(filepath.Dir(dir), "escape.json")); err == nil {
		t.Error("escape.json was written outside dir")
	}
}

func TestNewRunID(t *testing.T) {
	// A non-UTC time must come out in UTC.
	est := time.FixedZone("EST", -5*60*60)
	got := NewRunID(time.Date(2026, 11, 12, 0, 1, 2, 0, est), "1a2b3c4d")
	if want := "20261112T050102Z-1a2b3c4d"; got != want {
		t.Errorf("NewRunID = %q, want %q", got, want)
	}
	if !runIDPattern.MatchString(got) {
		t.Errorf("%q does not match the run ID pattern", got)
	}
}

func TestAgentFieldsOmittedWithoutAgent(t *testing.T) {
	path, err := Write(t.TempDir(), good())
	if err != nil {
		t.Fatal(err)
	}
	b, _ := os.ReadFile(path)
	for _, key := range []string{`"model"`, `"loop_stop"`, `"total_input_tokens"`, `"estimated_cost_usd"`} {
		if strings.Contains(string(b), key) {
			t.Errorf("no-agent trace should not contain %s", key)
		}
	}
}

func TestStepRoundTrip(t *testing.T) {
	code := 1
	tr := good()
	tr.Model, tr.LoopStop = "claude-haiku-5-5", "end_turn"
	tr.TotalInputTokens, tr.TotalOutputTokens, tr.EstimatedCostUSD = 300, 40, 0.00005
	tr.Steps = []Step{
		{N: 1, StopReason: "tool_use", Tool: "run_command", Input: `{"command":"pytest -q"}`,
			Output: "exit_code: 1", ExitCode: &code, InputTokens: 100, OutputTokens: 20},
		{N: 2, StopReason: "end_turn", Text: "Done.", InputTokens: 200, OutputTokens: 20},
	}
	path, err := Write(t.TempDir(), tr)
	if err != nil {
		t.Fatal(err)
	}
	b, _ := os.ReadFile(path)
	var got Trace
	if err := json.Unmarshal(b, &got); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(&got, tr) {
		t.Errorf("round trip mismatch:\n got %+v\nwant %+v", got, *tr)
	}
	// Step 2 ran nothing in the sandbox, so it has no exit_code at all.
	if strings.Count(string(b), `"exit_code"`) != 2 { // one in commands, one in step 1
		t.Errorf("want exit_code only on the command and step 1:\n%s", b)
	}
}
