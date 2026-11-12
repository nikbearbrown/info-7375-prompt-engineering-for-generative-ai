// Package trace defines the run trace (schema v0) and writes it to disk as
// traces/<run_id>.json. A trace records everything the harness did in one
// run, so a PASS or FAIL can be checked afterward.
package trace

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
)

// SchemaVersion is written into every trace so readers know the format.
const SchemaVersion = 0

// Exit reasons: the fixed list from PLAN.md T2.2. Only check_passed,
// check_failed, and error are used before T2.2.
const (
	ReasonCheckPassed          = "check_passed"
	ReasonCheckFailed          = "check_failed"
	ReasonBudgetSteps          = "budget_steps"
	ReasonBudgetTokens         = "budget_tokens"
	ReasonBudgetCost           = "budget_cost"
	ReasonTimeout              = "timeout"
	ReasonPolicyViolationLimit = "policy_violation_limit"
	ReasonGateRefused          = "gate_refused"
	ReasonGateDeferred         = "gate_deferred"
	ReasonError                = "error"
)

// Verdicts. Only the harness-run check produces PASS (D11).
const (
	VerdictPass = "PASS"
	VerdictFail = "FAIL"
)

// validReasons is a set: map keys are the members, struct{} takes no memory.
var validReasons = map[string]struct{}{
	ReasonCheckPassed: {}, ReasonCheckFailed: {}, ReasonBudgetSteps: {},
	ReasonBudgetTokens: {}, ReasonBudgetCost: {}, ReasonTimeout: {},
	ReasonPolicyViolationLimit: {}, ReasonGateRefused: {}, ReasonGateDeferred: {},
	ReasonError: {},
}

// ValidExitReason reports whether s is on the fixed list.
func ValidExitReason(s string) bool {
	_, ok := validReasons[s] // ok is true when the key exists
	return ok
}

// Trace is one run. The `json:"..."` tags set the field names in the file.
type Trace struct {
	SchemaVersion int       `json:"schema_version"`
	RunID         string    `json:"run_id"`
	TaskID        string    `json:"task_id"` // e.g. "001-fix-function"
	Pod           string    `json:"pod"`
	StartedAt     time.Time `json:"started_at"` // time.Time encodes as RFC 3339
	EndedAt       time.Time `json:"ended_at"`
	Commands      []Command `json:"commands"` // every host command, in order
	Steps         []Step    `json:"steps"`    // agent steps; empty without an agent
	ExitReason    string    `json:"exit_reason"`
	Verdict       string    `json:"verdict"`
	Error         string    `json:"error,omitempty"` // harness error; omitempty drops it when ""

	// Agent fields. omitempty leaves them out of --no-agent traces.
	Model             string  `json:"model,omitempty"`
	LoopStop          string  `json:"loop_stop,omitempty"` // why the agent loop ended: end_turn | max_steps | max_tokens | refusal
	TotalInputTokens  int64   `json:"total_input_tokens,omitempty"`
	TotalOutputTokens int64   `json:"total_output_tokens,omitempty"`
	EstimatedCostUSD  float64 `json:"estimated_cost_usd,omitempty"` // from list prices; not a bill
}

// Command is one host command the sandbox ran, tagged with the run phase.
type Command struct {
	Phase string `json:"phase"` // start | setup | agent | check | stop

	// Embedded struct (a type with no field name): its fields (args,
	// stdout, stderr, exit_code) appear directly in this JSON object.
	sandbox.Result
}

// Step is one agent step: one model turn and the (at most one) tool call
// it made.
type Step struct {
	N            int    `json:"n"` // 1-based
	StopReason   string `json:"stop_reason"`
	Text         string `json:"text,omitempty"`      // the model's text in this turn, truncated
	Tool         string `json:"tool,omitempty"`      // empty when the turn made no tool call
	Input        string `json:"input,omitempty"`     // tool input as raw JSON text, truncated
	Output       string `json:"output,omitempty"`    // tool result sent back to the model, truncated
	ExitCode     *int   `json:"exit_code,omitempty"` // pointer: nil (omitted) when nothing ran in the sandbox
	IsError      bool   `json:"is_error,omitempty"`
	InputTokens  int64  `json:"input_tokens"`
	OutputTokens int64  `json:"output_tokens"` // includes thinking tokens
}

// Phases of a run, used in Command.Phase.
const (
	PhaseStart = "start"
	PhaseSetup = "setup"
	PhaseAgent = "agent" // commands run by the agent's tool calls
	PhaseCheck = "check"
	PhaseStop  = "stop"
)

// NewRunID returns a sortable, file-name-safe run ID: UTC time plus a
// suffix, e.g. "20261112T050102Z-1a2b3c4d".
func NewRunID(now time.Time, suffix string) string {
	// Go time layouts are written using the reference date
	// Mon Jan 2 15:04:05 2006; each part shows where that field goes.
	return now.UTC().Format("20060102T150405Z") + "-" + suffix
}

// runIDPattern allows letters, digits, "_" and "-" only, so a run ID can
// never contain "/" or ".." and escape the traces directory.
var runIDPattern = regexp.MustCompile(`^[A-Za-z0-9_-]+$`)

// Validate checks the fields a reader relies on.
func (t *Trace) Validate() error {
	// errors.Join returns nil if every error is nil, or one error listing all.
	var errs []error
	if t.SchemaVersion != SchemaVersion {
		errs = append(errs, fmt.Errorf("schema_version %d, want %d", t.SchemaVersion, SchemaVersion))
	}
	if !runIDPattern.MatchString(t.RunID) {
		errs = append(errs, fmt.Errorf("run_id %q: only letters, digits, _ and - allowed", t.RunID))
	}
	if t.TaskID == "" {
		errs = append(errs, errors.New("task_id is empty"))
	}
	if !ValidExitReason(t.ExitReason) {
		errs = append(errs, fmt.Errorf("exit_reason %q is not on the fixed list", t.ExitReason))
	}
	if t.Verdict != VerdictPass && t.Verdict != VerdictFail {
		errs = append(errs, fmt.Errorf("verdict %q, want PASS or FAIL", t.Verdict))
	}
	return errors.Join(errs...)
}

// Write validates t and writes it to dir/<run_id>.json. It never
// overwrites: if the file exists, it returns an error.
func Write(dir string, t *Trace) (string, error) {
	if err := t.Validate(); err != nil {
		return "", fmt.Errorf("invalid trace: %w", err)
	}
	// A nil slice encodes as null; an empty one as []. Readers get [].
	if t.Commands == nil {
		t.Commands = []Command{}
	}
	if t.Steps == nil {
		t.Steps = []Step{}
	}
	// An Encoder (not json.Marshal) so HTML escaping can be turned off:
	// by default Go writes ">" as "\u003e", which makes pytest output in
	// traces hard to read. Encode also adds the final newline.
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	enc.SetIndent("", "  ")
	if err := enc.Encode(t); err != nil {
		return "", err
	}
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", err
	}
	path := filepath.Join(dir, t.RunID+".json")
	// O_EXCL with O_CREATE fails if the file already exists.
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o644)
	if err != nil {
		return "", err
	}
	if _, err := f.Write(buf.Bytes()); err != nil {
		f.Close()
		return "", err
	}
	return path, f.Close() // Close can report a failed write, so return its error
}
