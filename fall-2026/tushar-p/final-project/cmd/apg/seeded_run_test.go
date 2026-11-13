package main

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"os/exec"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/anthropic-sdk-go/v2"

	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// scriptedClient replays fixed tool calls instead of asking a model. It
// lets a test drive the real loop, policy, and pod with known calls.
type scriptedClient struct {
	calls []string // tool name + raw JSON input, one per turn; then end_turn
	n     int
}

// CountTokens answers the budget check with a small count: the scripted
// run is about the policy, not the budget.
func (s *scriptedClient) CountTokens(context.Context, anthropic.MessageCountTokensParams) (*anthropic.MessageTokensCount, error) {
	return &anthropic.MessageTokensCount{InputTokens: 100}, nil
}

func (s *scriptedClient) New(_ context.Context, _ anthropic.MessageNewParams) (*anthropic.Message, error) {
	i := s.n
	s.n++
	msg := map[string]any{
		"id": "msg_scripted", "type": "message", "role": "assistant", "model": "scripted",
		"usage": map[string]int{"input_tokens": 0, "output_tokens": 0},
	}
	switch {
	case i < len(s.calls):
		name, input, _ := strings.Cut(s.calls[i], " ")
		msg["stop_reason"] = "tool_use"
		msg["content"] = []any{map[string]any{
			"type": "tool_use", "id": "toolu_" + string(rune('a'+i)), "name": name,
			"input": json.RawMessage(input),
		}}
	case i == len(s.calls):
		msg["stop_reason"] = "end_turn"
		msg["content"] = []any{map[string]any{"type": "text", "text": "scripted run done"}}
	default:
		return nil, errors.New("scripted client: no more turns")
	}
	b, err := json.Marshal(msg)
	if err != nil {
		return nil, err
	}
	var m anthropic.Message
	return &m, json.Unmarshal(b, &m)
}

// TestSeededRunOnKind is a seeded run: a scripted client (no model, no API
// key) drives the real loop and policy against a real kind pod on task 001.
// It shows, in a real trace:
//   - commands run in /workspace, and a relative path (calc/ops.py) is
//     resolved by realpath in the pod to /workspace/calc/ops.py;
//   - denied calls for each rule class, recorded with verdict "denied" and
//     never run;
//   - the known limit: python is allowed and can create a symlink or read
//     outside /workspace; the policy still denies read_file through the
//     symlink.
//
// The bug is not fixed, so the run must end FAIL check_failed. Set
// APG_SEEDED_TRACES=<dir> to keep the trace; otherwise it goes to a temp dir.
func TestSeededRunOnKind(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping kind test in -short mode")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()
	if err := exec.CommandContext(ctx, "kubectl", "--context", "kind-kind", "get", "--raw", "/readyz").Run(); err != nil {
		t.Skipf("no kind cluster (context kind-kind): %v", err)
	}

	tk, err := findTask("../../tasks", "001")
	if err != nil {
		t.Fatal(err)
	}
	// This run makes 5 denied calls on purpose. Task 001 stops after 3
	// (max_policy_violations, T2.2), so raise the limit here: this test is
	// about the policy, not the budget.
	tk.Limits.MaxPolicyViolations = 10
	sb, err := sandbox.NewKind()
	if err != nil {
		t.Fatal(err)
	}
	client := &scriptedClient{calls: []string{
		`run_command {"argv":["python","-c","import os; print(os.getcwd())"]}`,
		`run_command {"argv":["cat","calc/ops.py"]}`,
		`read_file {"path":"../etc/passwd"}`,
		`run_command {"argv":["sh","-c","cat /etc/passwd"]}`,
		`run_command {"argv":["find",".","-name","*.py","-delete"]}`,
		`run_command {"argv":["sed","-n","1e id","calc/ops.py"]}`,
		`run_command {"argv":["python","-c","import os; os.symlink('/etc', 'etc-link')"]}`,
		`read_file {"path":"etc-link/passwd"}`,
		`run_command {"argv":["python","-c","print(open('/etc/hostname').read().strip())"]}`,
	}}
	tr := runTask(ctx, sb, sb.PodName(), tk, client, nil)
	tr.Model = "scripted (no model)" // runTask fills in the default model name

	dir := os.Getenv("APG_SEEDED_TRACES")
	if dir == "" {
		dir = t.TempDir()
	}
	path, err := trace.Write(dir, tr)
	if err != nil {
		t.Fatal(err)
	}
	t.Logf("trace: %s", path)

	if tr.Verdict != trace.VerdictFail || tr.ExitReason != trace.ReasonCheckFailed {
		t.Fatalf("verdict %s reason %s (error %q), want FAIL check_failed", tr.Verdict, tr.ExitReason, tr.Error)
	}
	if len(tr.Steps) != 10 {
		t.Fatalf("steps = %d, want 10", len(tr.Steps))
	}
	want := []struct{ verdict, rule, output string }{
		{"allowed", "", "/workspace"},
		{"allowed", "", "def divide"},
		{"denied", "path", "outside /workspace"},
		{"denied", "program", "not on the allowlist"},
		{"denied", "flag", "deletes files"},
		{"denied", "flag", `"e" runs a shell command`},
		{"allowed", "", "exit_code: 0"},
		{"denied", "path", "resolves to /etc/passwd"},
		{"allowed", "", "apg-"}, // the pod's hostname is its name
	}
	for i, w := range want {
		s := tr.Steps[i]
		if s.Verdict != w.verdict || s.Rule != w.rule || !strings.Contains(s.Output, w.output) {
			t.Errorf("step %d: verdict=%q rule=%q output=%q, want %q %q containing %q", s.N, s.Verdict, s.Rule, s.Output, w.verdict, w.rule, w.output)
		}
		if s.Verdict == "denied" && s.ExitCode != nil {
			t.Errorf("step %d was denied but has an exit code", s.N)
		}
	}

	// The relative path in step 2 went through realpath in the pod, which
	// answered /workspace/calc/ops.py, and then cat ran with "calc/ops.py"
	// from the pod's working directory.
	var sawRealpath, sawCat bool
	for _, c := range tr.Commands {
		args := strings.Join(c.Args, " ")
		if strings.HasSuffix(args, "-- realpath -m -- /workspace/calc/ops.py") && c.Stdout == "/workspace/calc/ops.py\n" {
			sawRealpath = true
		}
		if strings.HasSuffix(args, "-- timeout 60 cat calc/ops.py") && c.ExitCode == 0 {
			sawCat = true
		}
		// Nothing denied may appear as a command in the pod.
		for _, bad := range []string{"sh -c", "-delete", "1e id", "cat /workspace/etc-link/passwd", "/etc/passwd"} {
			if c.Phase == trace.PhaseAgent && strings.Contains(args, bad) && !strings.Contains(args, "realpath") {
				t.Errorf("denied call ran in the pod: %s", args)
			}
		}
	}
	if !sawRealpath || !sawCat {
		t.Errorf("realpath of calc/ops.py seen=%v, cat calc/ops.py seen=%v", sawRealpath, sawCat)
	}
}
