package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"slices"
	"strings"
	"testing"

	"github.com/anthropics/anthropic-sdk-go/v2"

	"github.com/tushar-patel28/agent-proving-ground/internal/loop"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/stop"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// checkSecret is printed by the fake check. It must never reach the model.
const checkSecret = "CHECK-SECRET-7f3a"

const buggy = "def divide(a, b):\n    return a // b\n"

// stopSandbox is a fake pod with a real (in-memory) /workspace, so that
// write_file, sed -i, and python really change what the fingerprint sees.
// The fake check passes when calc/ops.py has true division.
type stopSandbox struct {
	files map[string]string // /workspace path -> content

	leftover        bool            // a background process the agent started is alive
	leftoverAtCheck []bool          // was it alive when each check ran?
	checkDirs       map[string]bool // check directories that exist right now
	checkDirsMade   int
	log             []string // every Exec, as one string, in order
	fingerprints    int
	checks          int
	stopped         bool
}

func newStopSandbox() *stopSandbox {
	return &stopSandbox{
		files: map[string]string{
			"/workspace/calc/ops.py":       buggy,
			"/workspace/tests/test_ops.py": "def test_divide(): ...\n",
		},
		checkDirs: map[string]bool{},
	}
}

func (s *stopSandbox) Start(context.Context) ([]sandbox.Result, error) { return nil, nil }
func (s *stopSandbox) CopyOut(context.Context, string, string) (sandbox.Result, error) {
	return sandbox.Result{}, nil
}
func (s *stopSandbox) Stop(context.Context) (sandbox.Result, error) {
	s.stopped = true
	return sandbox.Result{}, nil
}

// CopyIn: write_file's temp file lands in /workspace; the check script
// lands in a check dir. The repo copy at setup is a no-op here.
func (s *stopSandbox) CopyIn(_ context.Context, host, dst string) (sandbox.Result, error) {
	if strings.HasPrefix(dst, "/workspace/") {
		b, err := os.ReadFile(host)
		if err != nil {
			return sandbox.Result{}, err
		}
		s.files[dst] = string(b)
	}
	return sandbox.Result{Args: []string{"kubectl", "cp", host, dst}}, nil
}

func (s *stopSandbox) Exec(_ context.Context, cmd ...string) (sandbox.Result, error) {
	s.log = append(s.log, strings.Join(cmd, " "))
	r := sandbox.Result{Args: cmd}
	switch {
	case slices.Equal(cmd, stop.FingerprintCmd):
		s.fingerprints++
		for p, c := range s.files { // map order is random: the harness must sort
			sum := sha256.Sum256([]byte(c))
			r.Stdout += hex.EncodeToString(sum[:]) + "  " + p + "\n"
		}
	case slices.Equal(cmd, stop.KillCmd):
		killed := []map[string]any{}
		if s.leftover {
			killed = append(killed, map[string]any{"pid": 42, "cmd": "python -c leftover"})
		}
		s.leftover = false
		b, _ := json.Marshal(map[string]any{"killed": killed, "left": 0})
		r.Stdout = string(b) + "\n"
	case cmd[0] == "mkdir" && cmd[1] == "-m":
		s.checkDirs[cmd[3]] = true
		s.checkDirsMade++
	case cmd[0] == "rm":
		delete(s.checkDirs, cmd[len(cmd)-1])
	case cmd[0] == "bash": // the hidden check
		s.checks++
		s.leftoverAtCheck = append(s.leftoverAtCheck, s.leftover)
		ops := s.files["/workspace/calc/ops.py"]
		if strings.Contains(ops, "a / b") && !strings.Contains(ops, "//") {
			r.Stdout = "4 passed\n"
		} else {
			r.Stdout = fmt.Sprintf("%s: FAIL in %s (exit code 1)\n", checkSecret, cmd[1])
			r.Stderr = "command terminated with exit code 1\n"
			r.ExitCode = 1
		}
	case cmd[0] == "ls" && len(cmd) == 3: // setup's ls -A /workspace
		r.Stdout = "calc\ntests\n"
	case cmd[0] == "realpath":
		r.Stdout = strings.Join(cmd[3:], "\n") + "\n"
	case cmd[0] == "cat": // read_file
		r.Stdout = s.files[cmd[1]]
	case cmd[0] == "timeout": // run_command: timeout 60 <argv>
		s.runCommand(cmd[2:], &r)
	}
	return r, nil
}

// runCommand fakes the few programs the tests use.
func (s *stopSandbox) runCommand(argv []string, r *sandbox.Result) {
	switch argv[0] {
	case "cat":
		r.Stdout = s.files["/workspace/"+argv[1]]
	case "sed": // sed --sandbox -i s|OLD|NEW| FILE
		script, file := argv[3], "/workspace/"+argv[4]
		parts := strings.Split(script[2:len(script)-1], script[1:2])
		s.files[file] = strings.ReplaceAll(s.files[file], parts[0], parts[1])
	case "python": // python -c "...spawn..." starts a background process
		if strings.Contains(argv[2], "spawn") {
			s.leftover = true
		}
	}
}

// stopClient is a fake model that plays turns in order and keeps every
// request it was sent. onNew, if set, runs at the start of each call.
type stopClient struct {
	turns    []turn
	requests []string // each request's messages, as JSON
	onNew    func()
}

type turn struct{ tool, input, text string }

func (c *stopClient) CountTokens(context.Context, anthropic.MessageCountTokensParams) (*anthropic.MessageTokensCount, error) {
	return &anthropic.MessageTokensCount{InputTokens: 100}, nil
}

func (c *stopClient) New(_ context.Context, p anthropic.MessageNewParams) (*anthropic.Message, error) {
	if c.onNew != nil {
		c.onNew()
	}
	b, _ := json.Marshal(p.Messages)
	c.requests = append(c.requests, string(b))
	i := len(c.requests) - 1
	if i >= len(c.turns) {
		return nil, fmt.Errorf("fake: no turn %d", i+1)
	}
	t := c.turns[i]
	msg := map[string]any{
		"id": "msg_fake", "type": "message", "role": "assistant", "model": "fake",
		"usage": map[string]int{"input_tokens": 100, "output_tokens": 10},
	}
	if t.tool != "" {
		msg["stop_reason"] = "tool_use"
		msg["content"] = []any{map[string]any{"type": "tool_use", "id": fmt.Sprintf("toolu_%d", i+1), "name": t.tool, "input": json.RawMessage(t.input)}}
	} else {
		msg["stop_reason"] = "end_turn"
		msg["content"] = []any{map[string]any{"type": "text", "text": t.text}}
	}
	b, _ = json.Marshal(msg)
	var m anthropic.Message
	return &m, json.Unmarshal(b, &m)
}

func writeTurn(path, content string) turn {
	b, _ := json.Marshal(map[string]string{"path": path, "content": content})
	return turn{tool: "write_file", input: string(b)}
}

func cmdTurn(argv ...string) turn {
	b, _ := json.Marshal(map[string]any{"argv": argv})
	return turn{tool: "run_command", input: string(b)}
}

var doneTurn = turn{text: "Done, all tests pass."}

const fixed = "def divide(a, b):\n    return a / b\n"

func runStop(t *testing.T, sb *stopSandbox, c *stopClient) *trace.Trace {
	t.Helper()
	tr := runTask(context.Background(), sb, "apg-fake", exitTask(roomy), c, nil)
	if _, err := trace.Write(t.TempDir(), tr); err != nil {
		t.Errorf("trace does not write: %v", err)
	}
	if !sb.stopped {
		t.Error("Stop was not called")
	}
	return tr
}

// The agent says it is done, but the check fails: the run is not a PASS.
// The agent's word only triggers the final check.
func TestDoneWithFailingCheckIsNotPass(t *testing.T) {
	sb := newStopSandbox()
	tr := runStop(t, sb, &stopClient{turns: []turn{doneTurn}})
	if tr.Verdict == trace.VerdictPass || tr.ExitReason != trace.ReasonCheckFailed {
		t.Fatalf("verdict=%s reason=%s, want FAIL check_failed", tr.Verdict, tr.ExitReason)
	}
	if len(tr.CheckRuns) != 1 || tr.CheckRuns[0].Trigger != trace.TriggerFinal || tr.CheckRuns[0].Passed {
		t.Errorf("check runs = %+v, want one failed final run", tr.CheckRuns)
	}
}

// A write through run_command (sed -i) changes /workspace, so the check
// runs after that step; here the edit is the fix, so the run stops.
func TestSedWriteTriggersCheck(t *testing.T) {
	sb := newStopSandbox()
	c := &stopClient{turns: []turn{cmdTurn("sed", "-i", "s|a // b|a / b|", "calc/ops.py"), doneTurn}}
	tr := runStop(t, sb, c)
	if len(tr.CheckRuns) == 0 || tr.CheckRuns[0].AfterStep != 1 || tr.CheckRuns[0].Trigger != trace.TriggerWorkspaceChanged {
		t.Fatalf("check runs = %+v, want a run after step 1 for workspace_changed", tr.CheckRuns)
	}
	if !tr.Steps[0].WorkspaceChanged {
		t.Errorf("step 1 should be marked workspace_changed")
	}
	if tr.ExitReason != trace.ReasonCheckPassed || len(c.requests) != 1 {
		t.Errorf("reason=%s model calls=%d, want check_passed after 1 call", tr.ExitReason, len(c.requests))
	}
}

// A step that changes nothing is fingerprinted but does not run the check.
func TestUnchangedStepRunsNoCheck(t *testing.T) {
	sb := newStopSandbox()
	tr := runStop(t, sb, &stopClient{turns: []turn{cmdTurn("cat", "calc/ops.py"), doneTurn}})
	if sb.fingerprints < 2 { // the baseline, then after step 1
		t.Errorf("fingerprints = %d, want at least 2", sb.fingerprints)
	}
	if tr.Steps[0].WorkspaceChanged {
		t.Error("cat should not change /workspace")
	}
	for _, r := range tr.CheckRuns {
		if r.AfterStep == 1 {
			t.Errorf("check ran after an unchanged step: %+v", r)
		}
	}
	if len(tr.CheckRuns) != 1 || tr.CheckRuns[0].Trigger != trace.TriggerFinal {
		t.Errorf("check runs = %+v, want only the final one", tr.CheckRuns)
	}
}

// When a step makes the check pass, the run stops at once with
// check_passed: no more model calls, no second check.
func TestCheckPassMidRunStopsImmediately(t *testing.T) {
	sb := newStopSandbox()
	c := &stopClient{turns: []turn{writeTurn("calc/ops.py", fixed), cmdTurn("ls"), cmdTurn("ls"), doneTurn}}
	tr := runStop(t, sb, c)
	if tr.ExitReason != trace.ReasonCheckPassed || tr.Verdict != trace.VerdictPass {
		t.Fatalf("reason=%s verdict=%s, want check_passed PASS", tr.ExitReason, tr.Verdict)
	}
	if len(tr.Steps) != 1 || len(c.requests) != 1 || sb.checks != 1 || len(tr.CheckRuns) != 1 {
		t.Errorf("steps=%d model calls=%d checks=%d runs=%d, want 1 1 1 1", len(tr.Steps), len(c.requests), sb.checks, len(tr.CheckRuns))
	}
	if !tr.Check.Ran || tr.Check.ExitCode == nil || *tr.Check.ExitCode != 0 {
		t.Errorf("check = %+v, want ran with exit 0", tr.Check)
	}
}

// After a failed mid-run check the model is told only that the task is not
// complete yet: never the check's output, exit code, or file names.
func TestModelNeverSeesCheckOutput(t *testing.T) {
	sb := newStopSandbox()
	c := &stopClient{turns: []turn{writeTurn("notes.txt", "thinking\n"), cmdTurn("cat", "calc/ops.py"), doneTurn}}
	tr := runStop(t, sb, c)
	if len(tr.CheckRuns) < 1 || tr.CheckRuns[0].AfterStep != 1 || tr.CheckRuns[0].Passed {
		t.Fatalf("check runs = %+v, want a failed run after step 1", tr.CheckRuns)
	}
	for i, req := range c.requests {
		for _, secret := range []string{checkSecret, "apg-check", "check.sh"} {
			if strings.Contains(req, secret) {
				t.Errorf("request %d contains %q: %s", i+1, secret, req)
			}
		}
	}
	if len(c.requests) < 2 || !strings.Contains(c.requests[1], loop.NotCompleteNote) {
		t.Errorf("request 2 should carry %q", loop.NotCompleteNote)
	}
	if strings.Count(strings.Join(c.requests, ""), loop.NotCompleteNote) > 2 { // request 2, and again in request 3's history
		t.Errorf("the note should be sent once (it repeats only as history)")
	}
}

// A process the agent left running is killed before the check runs, so it
// cannot tamper with the check.
func TestLeftoverProcessGoneBeforeCheck(t *testing.T) {
	sb := newStopSandbox()
	c := &stopClient{turns: []turn{
		cmdTurn("python", "-c", "spawn a background process"),
		writeTurn("notes.txt", "x\n"), // changes /workspace: the check runs
		doneTurn,
	}}
	tr := runStop(t, sb, c)
	if len(sb.leftoverAtCheck) == 0 {
		t.Fatal("no check ran")
	}
	for i, alive := range sb.leftoverAtCheck {
		if alive {
			t.Errorf("check %d ran with the leftover process alive", i+1)
		}
	}
	// The kill ran, and ran before the first check.
	kill, check := -1, -1
	for i, l := range sb.log {
		if l == strings.Join(stop.KillCmd, " ") && kill < 0 {
			kill = i
		}
		if strings.HasPrefix(l, "bash ") && check < 0 {
			check = i
		}
	}
	if kill < 0 || check < 0 || kill > check {
		t.Errorf("kill at %d, check at %d: the kill must come first", kill, check)
	}
	if tr.CheckRuns[0].Killed != 1 {
		t.Errorf("check run 1 killed %d processes, want 1", tr.CheckRuns[0].Killed)
	}
}

// Between steps the check directory does not exist: it is deleted after
// every check run, before the agent's next model call.
func TestCheckDirGoneBetweenSteps(t *testing.T) {
	sb := newStopSandbox()
	c := &stopClient{turns: []turn{writeTurn("notes.txt", "a\n"), writeTurn("notes.txt", "b\n"), doneTurn}}
	c.onNew = func() {
		if len(sb.checkDirs) != 0 {
			t.Errorf("model call %d: check dir still present: %v", len(c.requests)+1, sb.checkDirs)
		}
	}
	tr := runStop(t, sb, c)
	if sb.checkDirsMade < 2 {
		t.Errorf("check dirs made = %d, want one per mid-run check (2) at least", sb.checkDirsMade)
	}
	if len(sb.checkDirs) != 0 {
		t.Errorf("check dir left after the run: %v", sb.checkDirs)
	}
	if tr.ExitReason != trace.ReasonCheckFailed {
		t.Errorf("reason = %s", tr.ExitReason)
	}
}
