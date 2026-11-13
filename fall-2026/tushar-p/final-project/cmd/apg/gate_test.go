package main

import (
	"bytes"
	"context"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"testing"

	"github.com/tushar-patel28/agent-proving-ground/internal/gate"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/stop"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// gateSandbox is stopSandbox (an in-memory /workspace) plus a working
// CopyOut and __pycache__ cleanup. Embedding *stopSandbox promotes all of
// its methods; the two below replace Exec and CopyOut.
type gateSandbox struct {
	*stopSandbox
	copyOuts int
}

// Exec handles the __pycache__ cleanup and passes everything else on.
func (s *gateSandbox) Exec(ctx context.Context, cmd ...string) (sandbox.Result, error) {
	if slices.Equal(cmd, stop.CleanPycacheCmd) {
		s.log = append(s.log, strings.Join(cmd, " "))
		for p := range s.files {
			if strings.Contains(p, "/__pycache__/") {
				delete(s.files, p) // deleting from a map while ranging over it is allowed in Go
			}
		}
		return sandbox.Result{Args: cmd}, nil
	}
	return s.stopSandbox.Exec(ctx, cmd...)
}

// CopyOut writes /workspace into the host dir, plus tool caches that the
// diff must leave out.
func (s *gateSandbox) CopyOut(_ context.Context, src, host string) (sandbox.Result, error) {
	s.copyOuts++
	extra := map[string]string{
		"/workspace/calc/__pycache__/ops.cpython-312.pyc": "\x00pyc",
		"/workspace/.pytest_cache/v/cache/lastfailed":     "{}\n",
	}
	for _, m := range []map[string]string{s.files, extra} {
		for p, c := range m {
			full := filepath.Join(host, strings.TrimPrefix(p, src))
			if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
				return sandbox.Result{}, err
			}
			if err := os.WriteFile(full, []byte(c), 0o644); err != nil {
				return sandbox.Result{}, err
			}
		}
	}
	return sandbox.Result{Args: []string{"kubectl", "cp", "pod:" + src, host}}, nil
}

// gateRepo is the task's original repo on the host, matching the fake's
// starting /workspace.
func gateRepo(t *testing.T) string {
	t.Helper()
	dir := t.TempDir()
	for p, c := range map[string]string{"calc/ops.py": buggy, "tests/test_ops.py": "def test_divide(): ...\n"} {
		os.MkdirAll(filepath.Join(dir, filepath.Dir(p)), 0o755)
		if err := os.WriteFile(filepath.Join(dir, p), []byte(c), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	return dir
}

// End to end with a fake pod: the agent fixes the bug, the check passes,
// and an approved gate exports exactly the fix, with no tool caches.
func TestGateApproveEndToEnd(t *testing.T) {
	sb := &gateSandbox{stopSandbox: newStopSandbox()}
	sb.files["/workspace/calc/__pycache__/ops.cpython-312.pyc"] = "planted" // deleted before the check
	tk := exitTask(roomy)
	tk.Repo = gateRepo(t)
	var shown bytes.Buffer
	g := &gate.Config{In: strings.NewReader("approve\n"), Out: &shown, Interactive: true, OutDir: t.TempDir()}

	tr := runTask(context.Background(), sb, "apg-fake", tk, &stopClient{turns: []turn{writeTurn("calc/ops.py", fixed)}}, g)

	if tr.ExitReason != trace.ReasonCheckPassed || tr.Gate == nil || tr.Gate.Decision != gate.DecisionApproved {
		t.Fatalf("reason %s gate %+v (error %q)", tr.ExitReason, tr.Gate, tr.Error)
	}
	want := filepath.Join(g.OutDir, tr.RunID, "approved.patch")
	b, err := os.ReadFile(want)
	if err != nil || tr.Gate.ExportedPath != want {
		t.Fatalf("approved.patch: %v (exported_path %q)", err, tr.Gate.ExportedPath)
	}
	p := string(b)
	if !strings.Contains(p, "-    return a // b\n+    return a / b\n") {
		t.Errorf("patch lacks the fix:\n%s", p)
	}
	for _, bad := range []string{"__pycache__", ".pytest_cache", "test_ops.py"} {
		if strings.Contains(p, bad) {
			t.Errorf("patch contains %q:\n%s", bad, p)
		}
	}
	if sb.copyOuts != 2 {
		t.Errorf("copy-outs = %d, want 2 (show, then rebuild)", sb.copyOuts)
	}
	if !strings.Contains(shown.String(), p) {
		t.Error("the approver was not shown the exported diff")
	}
	// Gate commands are in the trace under their own phase.
	n := 0
	for _, c := range tr.Commands {
		if c.Phase == trace.PhaseGate {
			n++
		}
	}
	if n < 4 { // kill + copy-out, twice
		t.Errorf("gate commands in trace = %d, want at least 4", n)
	}
	if !sb.stopped {
		t.Error("pod not stopped after the gate")
	}
	// The exit reason stays the loop's; the gate's outcome is only in gate.
	if strings.HasPrefix(string(tr.ExitReason), "gate_") {
		t.Errorf("exit_reason = %s", tr.ExitReason)
	}
}

// A harness error skips the gate: nothing is exported from a broken run.
func TestGateSkippedOnError(t *testing.T) {
	sb := &gateSandbox{stopSandbox: newStopSandbox()}
	tk := exitTask(roomy)
	tk.Repo = gateRepo(t)
	g := &gate.Config{In: strings.NewReader("approve\n"), Out: &bytes.Buffer{}, Interactive: true, OutDir: t.TempDir()}
	tr := runTask(context.Background(), sb, "apg-fake", tk, &stopClient{}, g) // no turns: the model call fails
	if tr.ExitReason != trace.ReasonError || tr.Gate == nil || tr.Gate.Decision != gate.DecisionSkipped || sb.copyOuts != 0 {
		t.Errorf("reason %s gate %+v copy-outs %d", tr.ExitReason, tr.Gate, sb.copyOuts)
	}
}

// Every check run deletes __pycache__ after the kill and before the check,
// so a planted .pyc cannot stand in for the source.
func TestPycacheDeletedBeforeCheck(t *testing.T) {
	sb := &gateSandbox{stopSandbox: newStopSandbox()}
	sb.files["/workspace/calc/__pycache__/ops.cpython-312.pyc"] = "planted"
	runTask(context.Background(), sb, "apg-fake", exitTask(roomy), &stopClient{turns: []turn{doneTurn}}, nil)
	kill, clean, check := -1, -1, -1
	for i, l := range sb.log {
		switch {
		case l == strings.Join(stop.KillCmd, " ") && kill < 0:
			kill = i
		case l == strings.Join(stop.CleanPycacheCmd, " ") && clean < 0:
			clean = i
		case strings.HasPrefix(l, "bash ") && check < 0:
			check = i
		}
	}
	if !(kill >= 0 && kill < clean && clean < check) {
		t.Errorf("order kill=%d clean=%d check=%d, want kill < clean < check", kill, clean, check)
	}
	if _, ok := sb.files["/workspace/calc/__pycache__/ops.cpython-312.pyc"]; ok {
		t.Error("planted .pyc still there after the check")
	}
}
