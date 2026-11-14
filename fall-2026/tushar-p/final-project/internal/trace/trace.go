// Package trace defines the run trace (schema v1, docs/trace-schema.md),
// writes it to disk as traces/<run_id>.json, and reads it back strictly
// (Decode). A trace records everything the harness did in one run, so a
// PASS or FAIL can be checked afterward.
package trace

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
)

// SchemaVersion is written into every trace so readers know the format.
// v1 (T2.5): commands say who issued them (actor, step), realpath lookups
// have their own phase (policy), and the token and cost totals live only
// in budget.used. Traces before T2.5 are v0.
const SchemaVersion = 1

// ExitReason says why a run stopped. It is its own type (a string
// underneath), so a function that takes an ExitReason cannot be handed
// any other string by mistake. The values are the fixed list from
// PLAN.md T2.2.
//
// check_passed / check_failed: the agent loop ended on its own (the model
// stopped calling tools, refused, or hit the per-reply max_tokens), and
// the check decided. The other reasons say which limit stopped the loop;
// the check still ran (except after error), and the verdict is its result.
type ExitReason string

const (
	ReasonCheckPassed          ExitReason = "check_passed"
	ReasonCheckFailed          ExitReason = "check_failed"
	ReasonBudgetSteps          ExitReason = "budget_steps"
	ReasonBudgetTokens         ExitReason = "budget_tokens"
	ReasonBudgetCost           ExitReason = "budget_cost"
	ReasonTimeout              ExitReason = "timeout"
	ReasonPolicyViolationLimit ExitReason = "policy_violation_limit"
	ReasonGateRefused          ExitReason = "gate_refused"  // on the fixed list, never set: the gate's outcome is in Trace.Gate (D23)
	ReasonGateDeferred         ExitReason = "gate_deferred" // on the fixed list, never set: the gate's outcome is in Trace.Gate (D23)
	ReasonError                ExitReason = "error"         // the harness failed; the check did not run
)

// Verdicts. Only the harness-run check produces PASS (D11).
const (
	VerdictPass = "PASS"
	VerdictFail = "FAIL"
)

// validReasons is a set: map keys are the members, struct{} takes no memory.
var validReasons = map[ExitReason]struct{}{
	ReasonCheckPassed: {}, ReasonCheckFailed: {}, ReasonBudgetSteps: {},
	ReasonBudgetTokens: {}, ReasonBudgetCost: {}, ReasonTimeout: {},
	ReasonPolicyViolationLimit: {}, ReasonGateRefused: {}, ReasonGateDeferred: {},
	ReasonError: {},
}

// ValidExitReason reports whether s is on the fixed list. It takes a plain
// string so it can check values read from a file.
func ValidExitReason(s string) bool {
	_, ok := validReasons[ExitReason(s)] // ok is true when the key exists
	return ok
}

// Trace is one run. The `json:"..."` tags set the field names in the file.
type Trace struct {
	SchemaVersion int        `json:"schema_version"`
	RunID         string     `json:"run_id"`
	TaskID        string     `json:"task_id"` // e.g. "001-fix-function"
	Pod           string     `json:"pod"`
	StartedAt     time.Time  `json:"started_at"` // time.Time encodes as RFC 3339
	EndedAt       time.Time  `json:"ended_at"`
	Commands      []Command  `json:"commands"`        // every host command, in order
	Steps         []Step     `json:"steps"`           // agent steps; empty without an agent
	ExitReason    ExitReason `json:"exit_reason"`     // why the run stopped
	Verdict       string     `json:"verdict"`         // PASS or FAIL: the check's result
	Check         Check      `json:"check"`           // the check that decided the verdict
	CheckRuns     []CheckRun `json:"check_runs"`      // every time the check ran (T2.3), in order
	Error         string     `json:"error,omitempty"` // harness error; omitempty drops it when ""

	// Agent fields. omitempty leaves them out of --no-agent traces.
	Model         string  `json:"model,omitempty"`
	PromptVersion string  `json:"prompt_version,omitempty"` // SHA-256 of everything fixed the harness sends the model (loop.PromptVersion); since T3.3
	LoopStop      string  `json:"loop_stop,omitempty"`      // why the agent loop ended: end_turn | max_tokens | refusal | limit | check_passed
	Budget        *Budget `json:"budget,omitempty"`         // limits and totals used; pointer: nil (omitted) without an agent

	Gate *Gate `json:"gate,omitempty"` // the human gate (T2.4); nil when no gate ran
}

// Gate is the human gate's record: what was shown, what was decided, and
// what (if anything) left the sandbox.
type Gate struct {
	Decision      string    `json:"decision"`                 // approved | refused | deferred | skipped | void | error
	Reason        string    `json:"reason,omitempty"`         // why, for skipped / void / error
	Interactive   bool      `json:"interactive"`              // stdin was a terminal
	Batch         bool      `json:"batch,omitempty"`          // eval mode: the gate always deferred (T3.3)
	Shown         []string  `json:"shown"`                    // what the approver saw; empty when nothing was shown
	DiffSHA256    string    `json:"diff_sha256,omitempty"`    // SHA-256 of the exact diff bytes shown (or written, when deferred)
	DiffBytes     int       `json:"diff_bytes"`               // length of that diff
	RecheckSHA256 string    `json:"recheck_sha256,omitempty"` // the diff rebuilt from the pod before export; must equal diff_sha256
	DecidedAt     time.Time `json:"decided_at"`
	ExportedPath  string    `json:"exported_path,omitempty"` // approved.patch or pending.patch; empty when nothing left
}

// Check is the hidden check's outcome. It runs after every exit except
// error.
type Check struct {
	Ran      bool `json:"ran"`
	ExitCode *int `json:"exit_code,omitempty"` // nil when it did not run; 0 means PASS
}

// CheckRun is one run of the hidden check. Its output stays in the
// commands (phase check); the model never sees it.
type CheckRun struct {
	AfterStep        int    `json:"after_step"` // the step that changed /workspace; 0 for the final check
	Trigger          string `json:"trigger"`    // workspace_changed | final
	ExitCode         int    `json:"exit_code"`
	Passed           bool   `json:"passed"`
	Killed           int    `json:"killed"`            // processes killed before the check ran
	WorkspaceSHA256  string `json:"workspace_sha256"`  // fingerprint of /workspace the check saw
	ChangedWorkspace bool   `json:"changed_workspace"` // the check run itself changed /workspace (see internal/stop)
}

// Check triggers, used in CheckRun.Trigger.
const (
	TriggerWorkspaceChanged = "workspace_changed" // a step changed /workspace
	TriggerFinal            = "final"             // the agent loop ended
)

// Budget is the run's limits and what it used (T2.2).
type Budget struct {
	Limits       BudgetLimits `json:"limits"`
	FromContract []string     `json:"from_contract"` // the limits the contract set; the others are harness defaults
	Used         BudgetUsed   `json:"used"`
}

// BudgetLimits mirrors budget.Limits, with JSON names.
type BudgetLimits struct {
	MaxSteps            int     `json:"max_steps"`
	MaxTotalTokens      int64   `json:"max_total_tokens"`
	MaxCostUSD          float64 `json:"max_cost_usd"`
	TimeoutSeconds      float64 `json:"timeout_seconds"`
	MaxPolicyViolations int     `json:"max_policy_violations"`
	MaxReplyTokens      int64   `json:"max_reply_tokens"` // per model reply; the worst case each pre-call check assumes
}

// BudgetUsed is what the agent loop spent.
type BudgetUsed struct {
	Steps            int     `json:"steps"`
	InputTokens      int64   `json:"input_tokens"`
	OutputTokens     int64   `json:"output_tokens"`
	TotalTokens      int64   `json:"total_tokens"`
	CostUSD          float64 `json:"cost_usd"`
	AgentSeconds     float64 `json:"agent_seconds"` // wall-clock time of the agent loop
	PolicyViolations int     `json:"policy_violations"`
	CountTokensCalls int     `json:"count_tokens_calls"` // pre-call token counts (free API calls, not in the totals)
}

// Command is one host command the sandbox ran, tagged with the run phase
// and with who it was for.
type Command struct {
	Phase string `json:"phase"`          // start | setup | agent | policy | fingerprint | check | gate | stop
	Actor string `json:"actor"`          // agent: it carried out an agent tool call; harness: anything else
	Step  int    `json:"step,omitempty"` // the agent step it belongs to (agent and policy commands); 0 otherwise

	// Embedded struct (a type with no field name): its fields (args,
	// stdout, stderr, exit_code) appear directly in this JSON object.
	sandbox.Result
}

// Step is one agent step: one model turn and the (at most one) tool call
// it made.
type Step struct {
	N          int    `json:"n"` // 1-based
	StopReason string `json:"stop_reason"`
	Text       string `json:"text,omitempty"`      // the model's text in this turn, truncated
	Tool       string `json:"tool,omitempty"`      // empty when the turn made no tool call
	Input      string `json:"input,omitempty"`     // tool input as raw JSON text, truncated
	Output     string `json:"output,omitempty"`    // tool result sent back to the model, truncated
	ExitCode   *int   `json:"exit_code,omitempty"` // pointer: nil (omitted) when nothing ran in the sandbox
	IsError    bool   `json:"is_error,omitempty"`
	Verdict    string `json:"verdict,omitempty"` // policy decision on the tool call: allowed | denied; empty when no tool call
	Rule       string `json:"rule,omitempty"`    // the policy rule that denied it (internal/policy Rule* constants)
	Reason     string `json:"reason,omitempty"`  // why it was denied; the same text the model was sent

	WorkspaceChanged bool  `json:"workspace_changed,omitempty"` // the step changed /workspace, so the check ran
	InputTokens      int64 `json:"input_tokens"`
	OutputTokens     int64 `json:"output_tokens"` // includes thinking tokens
}

// Policy verdicts on a step's tool call, used in Step.Verdict. A denied
// call was never executed.
const (
	StepAllowed = "allowed"
	StepDenied  = "denied"
)

// Phases of a run, used in Command.Phase.
const (
	PhaseStart  = "start"
	PhaseSetup  = "setup"
	PhaseAgent  = "agent"  // commands that carry out the agent's tool calls
	PhasePolicy = "policy" // realpath lookups the policy makes before a call runs (T2.1)

	PhaseFingerprint = "fingerprint" // the harness hashing /workspace after a step
	PhaseGate        = "gate"        // the human gate: kill, copy /workspace out (T2.4)
	PhaseCheck       = "check"
	PhaseStop        = "stop"
)

// Actors, used in Command.Actor.
const (
	ActorAgent   = "agent"
	ActorHarness = "harness"
)

// ActorFor returns who a command in this phase is for: only phase agent
// carries out the agent's tool calls; every other phase is the harness's
// own work (setup, policy lookups, fingerprints, checks, gate, stop).
func ActorFor(phase string) string {
	if phase == PhaseAgent {
		return ActorAgent
	}
	return ActorHarness
}

var validPhases = map[string]bool{
	PhaseStart: true, PhaseSetup: true, PhaseAgent: true, PhasePolicy: true,
	PhaseFingerprint: true, PhaseCheck: true, PhaseGate: true, PhaseStop: true,
}

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
	if !ValidExitReason(string(t.ExitReason)) {
		errs = append(errs, fmt.Errorf("exit_reason %q is not on the fixed list", t.ExitReason))
	}
	if t.Verdict != VerdictPass && t.Verdict != VerdictFail {
		errs = append(errs, fmt.Errorf("verdict %q, want PASS or FAIL", t.Verdict))
	}
	if t.Pod == "" {
		errs = append(errs, errors.New("pod is empty"))
	}
	if t.StartedAt.IsZero() || t.EndedAt.Before(t.StartedAt) {
		errs = append(errs, fmt.Errorf("started_at %v / ended_at %v out of order", t.StartedAt, t.EndedAt))
	}
	for i, c := range t.Commands {
		if !validPhases[c.Phase] {
			errs = append(errs, fmt.Errorf("commands[%d]: phase %q", i, c.Phase))
		}
		if c.Actor != ActorFor(c.Phase) {
			errs = append(errs, fmt.Errorf("commands[%d]: actor %q in phase %q, want %q", i, c.Actor, c.Phase, ActorFor(c.Phase)))
		}
	}
	for i, s := range t.Steps {
		if s.N != i+1 {
			errs = append(errs, fmt.Errorf("steps[%d]: n = %d, want %d", i, s.N, i+1))
		}
		switch s.Verdict {
		case "", StepAllowed:
		case StepDenied:
			if s.Rule == "" || s.Reason == "" {
				errs = append(errs, fmt.Errorf("steps[%d]: denied without a rule and reason", i))
			}
		default:
			errs = append(errs, fmt.Errorf("steps[%d]: verdict %q", i, s.Verdict))
		}
	}
	// The verdict is the check's result (D11), and only error skips it.
	switch {
	case t.ExitReason == ReasonError:
		if t.Check.Ran || t.Verdict != VerdictFail {
			errs = append(errs, errors.New("exit_reason error, but the check ran or the verdict is not FAIL"))
		}
	case !t.Check.Ran || t.Check.ExitCode == nil:
		errs = append(errs, errors.New("the check did not run, but exit_reason is not error"))
	case (*t.Check.ExitCode == 0) != (t.Verdict == VerdictPass):
		errs = append(errs, fmt.Errorf("verdict %s does not match check exit code %d", t.Verdict, *t.Check.ExitCode))
	}
	for i, r := range t.CheckRuns {
		if r.Trigger != TriggerWorkspaceChanged && r.Trigger != TriggerFinal {
			errs = append(errs, fmt.Errorf("check_runs[%d]: trigger %q", i, r.Trigger))
		}
		if r.Passed != (r.ExitCode == 0) {
			errs = append(errs, fmt.Errorf("check_runs[%d]: passed %v with exit code %d", i, r.Passed, r.ExitCode))
		}
	}
	if (t.Model != "") != (t.Budget != nil) {
		errs = append(errs, errors.New("model and budget must be set together (an agent run) or not at all"))
	}
	if t.Gate != nil && !validDecisions[t.Gate.Decision] {
		errs = append(errs, fmt.Errorf("gate decision %q", t.Gate.Decision))
	}
	return errors.Join(errs...)
}

// validDecisions are the gate's decisions (internal/gate Decision*).
var validDecisions = map[string]bool{
	"approved": true, "refused": true, "deferred": true, "skipped": true, "void": true, "error": true,
}

// required lists, for each JSON object in a trace, the keys that must be
// present. Keys left out of this list are optional (omitempty).
var required = map[string][]string{
	"trace":     {"schema_version", "run_id", "task_id", "pod", "started_at", "ended_at", "commands", "steps", "exit_reason", "verdict", "check", "check_runs"},
	"command":   {"phase", "actor", "args", "stdout", "stderr", "exit_code"},
	"step":      {"n", "stop_reason", "input_tokens", "output_tokens"},
	"check":     {"ran"},
	"check_run": {"after_step", "trigger", "exit_code", "passed", "killed", "workspace_sha256", "changed_workspace"},
	"budget":    {"limits", "from_contract", "used"},
	"limits":    {"max_steps", "max_total_tokens", "max_cost_usd", "timeout_seconds", "max_policy_violations", "max_reply_tokens"},
	"used":      {"steps", "input_tokens", "output_tokens", "total_tokens", "cost_usd", "agent_seconds", "policy_violations", "count_tokens_calls"},
	"gate":      {"decision", "interactive", "shown", "diff_bytes", "decided_at"},
}

// Decode reads one v1 trace strictly, with the standard library only:
//  1. every key must be one the schema knows (DisallowUnknownFields);
//  2. every required key must be present (checked on a generic copy);
//  3. the values must pass Validate.
//
// v0 traces (before T2.5) fail on purpose: their schema_version is 0.
func Decode(r io.Reader) (*Trace, error) {
	b, err := io.ReadAll(r)
	if err != nil {
		return nil, err
	}
	var t Trace
	dec := json.NewDecoder(bytes.NewReader(b))
	dec.DisallowUnknownFields()
	if err := dec.Decode(&t); err != nil {
		return nil, fmt.Errorf("decode: %w", err)
	}
	if dec.More() {
		return nil, errors.New("decode: extra data after the trace")
	}
	if err := checkRequired(b); err != nil {
		return nil, err
	}
	if err := t.Validate(); err != nil {
		return nil, err
	}
	return &t, nil
}

// object decodes raw as a JSON object and checks it has every key that
// required[kind] lists. map[string]json.RawMessage keeps each value as raw
// JSON, to be decoded further only where needed.
func object(raw json.RawMessage, kind, where string) (map[string]json.RawMessage, error) {
	var m map[string]json.RawMessage
	if err := json.Unmarshal(raw, &m); err != nil {
		return nil, fmt.Errorf("%s: %w", where, err)
	}
	for _, k := range required[kind] {
		if _, ok := m[k]; !ok {
			return nil, fmt.Errorf("%s: missing required key %q", where, k)
		}
	}
	return m, nil
}

// list decodes raw as a JSON array and checks each element as kind.
func list(raw json.RawMessage, kind, where string) error {
	var items []json.RawMessage
	if err := json.Unmarshal(raw, &items); err != nil {
		return fmt.Errorf("%s: %w", where, err)
	}
	for i, it := range items {
		if _, err := object(it, kind, fmt.Sprintf("%s[%d]", where, i)); err != nil {
			return err
		}
	}
	return nil
}

func checkRequired(b []byte) error {
	top, err := object(b, "trace", "trace")
	if err != nil {
		return err
	}
	if _, err := object(top["check"], "check", "check"); err != nil {
		return err
	}
	for key, kind := range map[string]string{"commands": "command", "steps": "step", "check_runs": "check_run"} {
		if err := list(top[key], kind, key); err != nil {
			return err
		}
	}
	if raw, ok := top["budget"]; ok {
		b, err := object(raw, "budget", "budget")
		if err != nil {
			return err
		}
		if _, err := object(b["limits"], "limits", "budget.limits"); err != nil {
			return err
		}
		if _, err := object(b["used"], "used", "budget.used"); err != nil {
			return err
		}
	}
	if raw, ok := top["gate"]; ok {
		if _, err := object(raw, "gate", "gate"); err != nil {
			return err
		}
	}
	return nil
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
	if t.CheckRuns == nil {
		t.CheckRuns = []CheckRun{}
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
	// Read back what is about to be written, strictly: a trace that Decode
	// would reject is never written.
	if _, err := Decode(bytes.NewReader(buf.Bytes())); err != nil {
		return "", fmt.Errorf("invalid trace: %w", err)
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
