package loop

import (
	"context"
	"encoding/json"
	"errors"
	"math"
	"os"
	"strings"
	"testing"

	"github.com/anthropics/anthropic-sdk-go/v2"

	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
)

// fakeClient returns canned API responses in order and records every
// request. No network, no API key.
type fakeClient struct {
	responses []string // raw JSON, shaped like real Messages API responses
	calls     []anthropic.MessageNewParams
	err       error
}

func (f *fakeClient) New(_ context.Context, p anthropic.MessageNewParams) (*anthropic.Message, error) {
	f.calls = append(f.calls, p)
	if f.err != nil {
		return nil, f.err
	}
	i := len(f.calls) - 1
	if i >= len(f.responses) {
		return nil, errors.New("fake: no more responses")
	}
	var m anthropic.Message
	if err := json.Unmarshal([]byte(f.responses[i]), &m); err != nil {
		return nil, err
	}
	return &m, nil
}

// toolUse builds a response with one text block and one tool call.
func toolUse(id, name, input string, in, out int) string {
	return `{"id":"msg_` + id + `","type":"message","role":"assistant","model":"claude-haiku-5-5",
	  "content":[{"type":"text","text":"calling ` + name + `"},
	             {"type":"tool_use","id":"` + id + `","name":"` + name + `","input":` + input + `}],
	  "stop_reason":"tool_use","usage":{"input_tokens":` + itoa(in) + `,"output_tokens":` + itoa(out) + `}}`
}

func endTurn(text string, in, out int) string {
	return `{"id":"msg_end","type":"message","role":"assistant","model":"claude-haiku-5-5",
	  "content":[{"type":"text","text":"` + text + `"}],
	  "stop_reason":"end_turn","usage":{"input_tokens":` + itoa(in) + `,"output_tokens":` + itoa(out) + `}}`
}

func itoa(n int) string { b, _ := json.Marshal(n); return string(b) }

// fakeSandbox records calls. exec decides what each Exec returns.
type fakeSandbox struct {
	execs  [][]string
	copied map[string]string // sandbox path -> content copied in
	exec   func(cmd []string) sandbox.Result
}

func (f *fakeSandbox) Start(context.Context) ([]sandbox.Result, error) { return nil, nil }
func (f *fakeSandbox) Stop(context.Context) (sandbox.Result, error)    { return sandbox.Result{}, nil }
func (f *fakeSandbox) CopyOut(context.Context, string, string) (sandbox.Result, error) {
	return sandbox.Result{}, nil
}
func (f *fakeSandbox) Exec(_ context.Context, cmd ...string) (sandbox.Result, error) {
	f.execs = append(f.execs, cmd)
	r := sandbox.Result{Args: append([]string{"kubectl", "exec", "--"}, cmd...)}
	if f.exec != nil {
		out := f.exec(cmd)
		r.Stdout, r.Stderr, r.ExitCode = out.Stdout, out.Stderr, out.ExitCode
	}
	return r, nil
}
func (f *fakeSandbox) CopyIn(_ context.Context, host, dst string) (sandbox.Result, error) {
	b, err := os.ReadFile(host)
	if err != nil {
		return sandbox.Result{}, err
	}
	if f.copied == nil {
		f.copied = map[string]string{}
	}
	f.copied[dst] = string(b)
	return sandbox.Result{Args: []string{"kubectl", "cp", host, "pod:" + dst}}, nil
}

func cfg() Config {
	return Config{
		Model:     "claude-haiku-5-5",
		Goal:      "Fix the bug.",
		Tools:     []string{"read_file", "write_file", "run_command"},
		MaxSteps:  10,
		MaxTokens: 1000,
	}
}

func TestRunReadWriteEnd(t *testing.T) {
	client := &fakeClient{responses: []string{
		toolUse("toolu_1", "read_file", `{"path":"calc/ops.py"}`, 100, 20),
		toolUse("toolu_2", "write_file", `{"path":"/workspace/calc/ops.py","content":"fixed\n"}`, 150, 30),
		endTurn("Done.", 200, 10),
	}}
	sb := &fakeSandbox{exec: func(cmd []string) sandbox.Result {
		if cmd[0] == "cat" {
			return sandbox.Result{Stdout: "return a // b\n"}
		}
		return sandbox.Result{}
	}}
	var recorded []sandbox.Result
	res, err := Run(context.Background(), client, sb, cfg(), func(r sandbox.Result) { recorded = append(recorded, r) })
	if err != nil {
		t.Fatal(err)
	}

	if len(res.Steps) != 3 || res.Stop != StopEndTurn {
		t.Fatalf("steps=%d stop=%q, want 3 end_turn", len(res.Steps), res.Stop)
	}
	if res.InputTokens != 450 || res.OutputTokens != 60 {
		t.Errorf("tokens in=%d out=%d, want 450/60", res.InputTokens, res.OutputTokens)
	}
	s1, s2, s3 := res.Steps[0], res.Steps[1], res.Steps[2]
	if s1.Tool != "read_file" || s1.Output != "return a // b\n" || s1.ExitCode == nil || *s1.ExitCode != 0 {
		t.Errorf("step 1 = %+v", s1)
	}
	if s1.InputTokens != 100 || s1.OutputTokens != 20 || s1.Text != "calling read_file" {
		t.Errorf("step 1 tokens/text = %+v", s1)
	}
	if s2.Tool != "write_file" || !strings.Contains(s2.Output, "wrote 6 bytes") {
		t.Errorf("step 2 = %+v", s2)
	}
	if s3.Tool != "" || s3.Text != "Done." || s3.ExitCode != nil {
		t.Errorf("step 3 = %+v", s3)
	}

	// The relative path was resolved under /workspace before reaching the sandbox.
	if got := sb.execs[0]; strings.Join(got, " ") != "cat /workspace/calc/ops.py" {
		t.Errorf("first exec = %q", got)
	}
	if sb.copied["/workspace/calc/ops.py"] != "fixed\n" {
		t.Errorf("write_file content not copied in: %v", sb.copied)
	}
	// cat, mkdir -p, cp: every sandbox command was recorded.
	if len(recorded) != 3 {
		t.Errorf("recorded %d commands, want 3", len(recorded))
	}

	// The second request carries the tool_result for toolu_1, and the
	// first request offered exactly the contract's three tools.
	if len(client.calls) != 3 {
		t.Fatalf("model calls = %d", len(client.calls))
	}
	b, _ := json.Marshal(client.calls[1].Messages)
	if !strings.Contains(string(b), `"tool_use_id":"toolu_1"`) {
		t.Errorf("tool_result for toolu_1 missing from request 2: %s", b)
	}
	tb, _ := json.Marshal(client.calls[0].Tools)
	for _, name := range []string{"read_file", "write_file", "run_command"} {
		if !strings.Contains(string(tb), `"name":"`+name+`"`) {
			t.Errorf("tool %s not offered", name)
		}
	}
	if !strings.Contains(string(tb), `"additionalProperties":false`) || !strings.Contains(string(tb), `"strict":true`) {
		t.Errorf("tools should be strict: %s", tb)
	}
	pb, _ := json.Marshal(client.calls[0])
	if !strings.Contains(string(pb), `"disable_parallel_tool_use":true`) {
		t.Errorf("parallel tool use should be disabled: %s", pb)
	}
}

func TestRunStopsAtMaxSteps(t *testing.T) {
	var resp []string
	for i := 0; i < 20; i++ {
		resp = append(resp, toolUse("toolu_x", "run_command", `{"command":"ls"}`, 10, 5))
	}
	client := &fakeClient{responses: resp}
	c := cfg()
	c.MaxSteps = 4
	res, err := Run(context.Background(), client, &fakeSandbox{}, c, func(sandbox.Result) {})
	if err != nil {
		t.Fatal(err)
	}
	if res.Stop != StopMaxSteps || len(res.Steps) != 4 || len(client.calls) != 4 {
		t.Errorf("stop=%q steps=%d calls=%d, want max_steps 4 4", res.Stop, len(res.Steps), len(client.calls))
	}
}

func TestRunRejectsBadCalls(t *testing.T) {
	tests := []struct {
		name, tool, input, wantText string
	}{
		{"parent escape", "read_file", `{"path":"../etc/passwd"}`, "outside /workspace"},
		{"absolute escape", "write_file", `{"path":"/tmp/x","content":"y"}`, "outside /workspace"},
		{"dotdot inside path", "read_file", `{"path":"/workspace/../etc/shadow"}`, "outside /workspace"},
		{"not in contract", "delete_file", `{"path":"a"}`, "not allowed"},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			client := &fakeClient{responses: []string{
				toolUse("toolu_1", tc.tool, tc.input, 10, 5),
				endTurn("ok", 10, 5),
			}}
			sb := &fakeSandbox{}
			res, err := Run(context.Background(), client, sb, cfg(), func(sandbox.Result) {})
			if err != nil {
				t.Fatal(err)
			}
			s := res.Steps[0]
			if !s.IsError || !strings.Contains(s.Output, tc.wantText) {
				t.Errorf("step = %+v, want is_error containing %q", s, tc.wantText)
			}
			if len(sb.execs) != 0 || len(sb.copied) != 0 {
				t.Errorf("rejected call reached the sandbox: execs=%v copied=%v", sb.execs, sb.copied)
			}
			b, _ := json.Marshal(client.calls[1].Messages)
			if !strings.Contains(string(b), `"is_error":true`) {
				t.Errorf("model was not told the call failed: %s", b)
			}
		})
	}
}

func TestToolNotInContractIsNotOffered(t *testing.T) {
	client := &fakeClient{responses: []string{endTurn("nothing to do", 10, 5)}}
	c := cfg()
	c.Tools = []string{"read_file"}
	if _, err := Run(context.Background(), client, &fakeSandbox{}, c, func(sandbox.Result) {}); err != nil {
		t.Fatal(err)
	}
	tb, _ := json.Marshal(client.calls[0].Tools)
	if strings.Contains(string(tb), "run_command") || strings.Contains(string(tb), "write_file") {
		t.Errorf("only read_file should be offered: %s", tb)
	}
}

func TestUnknownContractToolIsAnError(t *testing.T) {
	c := cfg()
	c.Tools = []string{"read_file", "browse_web"}
	if _, err := Run(context.Background(), &fakeClient{}, &fakeSandbox{}, c, func(sandbox.Result) {}); err == nil {
		t.Error("an unknown tool in the contract should fail the run")
	}
}

func TestRunCommandOutputAndTruncation(t *testing.T) {
	big := strings.Repeat("é", maxOutput) // 2 bytes each: twice the cap
	client := &fakeClient{responses: []string{
		toolUse("toolu_1", "run_command", `{"command":"pytest -q"}`, 10, 5),
		endTurn("ok", 10, 5),
	}}
	sb := &fakeSandbox{exec: func([]string) sandbox.Result {
		return sandbox.Result{Stdout: big, Stderr: "command terminated with exit code 1\n", ExitCode: 1}
	}}
	res, err := Run(context.Background(), client, sb, cfg(), func(sandbox.Result) {})
	if err != nil {
		t.Fatal(err)
	}
	s := res.Steps[0]
	if s.IsError || s.ExitCode == nil || *s.ExitCode != 1 {
		t.Errorf("non-zero exit is data, not a tool error: %+v", s)
	}
	if !strings.Contains(s.Output, "...[truncated") || len(s.Output) > maxOutput+100 {
		t.Errorf("output not truncated: len=%d", len(s.Output))
	}
	if strings.Contains(s.Output, "command terminated") {
		t.Error("kubectl's own stderr line should be removed")
	}
	if got := strings.Join(sb.execs[0], " "); got != "timeout 60 sh -c pytest -q" {
		t.Errorf("exec = %q", got)
	}
}

func TestTruncateKeepsUTF8Valid(t *testing.T) {
	s := strings.Repeat("a", maxOutput-1) + "é" + "tail" // é straddles the cut
	got := truncate(s)
	if !strings.HasPrefix(got, strings.Repeat("a", maxOutput-1)+"\n...[truncated") {
		t.Errorf("cut inside a character: %q", got[maxOutput-5:])
	}
}

func TestStopsOnMaxTokensWithoutRunningTool(t *testing.T) {
	resp := strings.Replace(toolUse("toolu_1", "run_command", `{"command":"rm -rf /workspace"}`, 10, 5),
		`"stop_reason":"tool_use"`, `"stop_reason":"max_tokens"`, 1)
	sb := &fakeSandbox{}
	res, err := Run(context.Background(), &fakeClient{responses: []string{resp}}, sb, cfg(), func(sandbox.Result) {})
	if err != nil {
		t.Fatal(err)
	}
	if res.Stop != StopMaxTokens || len(sb.execs) != 0 {
		t.Errorf("stop=%q execs=%v; a cut-off tool call must not run", res.Stop, sb.execs)
	}
}

func TestAPIErrorIsReturned(t *testing.T) {
	_, err := Run(context.Background(), &fakeClient{err: errors.New("529 overloaded")}, &fakeSandbox{}, cfg(), func(sandbox.Result) {})
	if err == nil || !strings.Contains(err.Error(), "529") {
		t.Errorf("err = %v", err)
	}
}

func TestEstimateCost(t *testing.T) {
	// 100K input is still the normal rate: 0.1 * $0.10 + 1 * $0.50.
	got, err := EstimateCost("claude-haiku-5-5", 100_000, 1_000_000)
	if err != nil || math.Abs(got-0.51) > 1e-9 {
		t.Errorf("100K in + 1M out = %v (err %v), want 0.51", got, err)
	}
	long, _ := EstimateCost("claude-haiku-5-5", 200_000, 0) // over 100K: long-prompt rate
	if math.Abs(long-0.10) > 1e-9 {
		t.Errorf("200K long-prompt input = %v, want 0.10", long)
	}
	if _, err := EstimateCost("unknown-model", 1, 1); err == nil {
		t.Error("unknown model should be an error")
	}
}
