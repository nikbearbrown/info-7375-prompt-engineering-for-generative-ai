package loop

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/anthropic-sdk-go/v2"

	"github.com/tushar-patel28/agent-proving-ground/internal/budget"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
)

// fakeClient returns canned API responses in order and records every
// request. No network, no API key.
type fakeClient struct {
	responses []string // raw JSON, shaped like real Messages API responses
	calls     []anthropic.MessageNewParams
	err       error
	counts    int // CountTokens calls
}

// CountTokens answers the pre-call budget check with a small fixed count.
func (f *fakeClient) CountTokens(context.Context, anthropic.MessageCountTokensParams) (*anthropic.MessageTokensCount, error) {
	f.counts++
	return &anthropic.MessageTokensCount{InputTokens: 100}, nil
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

// fakeSandbox records calls. exec decides what each Exec returns, except
// for realpath (the policy's path resolver), which the fake answers itself:
// each path comes back unchanged unless links maps it (or a parent
// directory) somewhere else, like a symlink.
type fakeSandbox struct {
	execs  [][]string
	copied map[string]string // sandbox path -> content copied in
	exec   func(cmd []string) sandbox.Result
	links  map[string]string // symlink path -> target
}

func (f *fakeSandbox) Start(context.Context) ([]sandbox.Result, error) { return nil, nil }
func (f *fakeSandbox) Stop(context.Context) (sandbox.Result, error)    { return sandbox.Result{}, nil }
func (f *fakeSandbox) CopyOut(context.Context, string, string) (sandbox.Result, error) {
	return sandbox.Result{}, nil
}
func (f *fakeSandbox) Exec(_ context.Context, cmd ...string) (sandbox.Result, error) {
	f.execs = append(f.execs, cmd)
	r := sandbox.Result{Args: append([]string{"kubectl", "exec", "--"}, cmd...)}
	if cmd[0] == "realpath" { // realpath -m -- p1 p2 ...
		for _, p := range cmd[3:] {
			for from, to := range f.links {
				if p == from || strings.HasPrefix(p, from+"/") {
					p = to + strings.TrimPrefix(p, from)
				}
			}
			r.Stdout += p + "\n"
		}
		return r, nil
	}
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
		Model: "claude-haiku-5-5",
		Goal:  "Fix the bug.",
		Tools: []string{"read_file", "write_file", "run_command"},
		Limits: budget.Limits{MaxSteps: 10, MaxTotalTokens: 1_000_000, MaxCostUSD: 1,
			Timeout: time.Minute, MaxPolicyViolations: 10},
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
	var phases []string // "phase/step" for each recorded command
	res, err := Run(context.Background(), client, sb, cfg(), func(phase string, step int, r sandbox.Result) {
		recorded = append(recorded, r)
		phases = append(phases, phase+"/"+itoa(step))
	})
	if err != nil {
		t.Fatal(err)
	}
	// The policy's realpath lookups and the tool calls' own commands are
	// recorded under their own phases, with their step (schema v1).
	if got := strings.Join(phases, " "); got != "policy/1 agent/1 policy/2 agent/2 agent/2" {
		t.Errorf("recorded phases = %s", got)
	}

	if len(res.Steps) != 3 || res.Stop != StopEndTurn {
		t.Fatalf("steps=%d stop=%q, want 3 end_turn", len(res.Steps), res.Stop)
	}
	if res.Used.InputTokens != 450 || res.Used.OutputTokens != 60 || res.Used.Steps != 3 {
		t.Errorf("used = %+v, want 450 in, 60 out, 3 steps", res.Used)
	}
	// One token count before each of the three model calls.
	if client.counts != 3 || res.CountTokensCalls != 3 {
		t.Errorf("count_tokens calls = %d (result %d), want 3", client.counts, res.CountTokensCalls)
	}
	s1, s2, s3 := res.Steps[0], res.Steps[1], res.Steps[2]
	if s1.Tool != "read_file" || s1.Output != "return a // b\n" || s1.ExitCode == nil || *s1.ExitCode != 0 {
		t.Errorf("step 1 = %+v", s1)
	}
	if s1.Verdict != "allowed" || s2.Verdict != "allowed" || s3.Verdict != "" {
		t.Errorf("verdicts = %q %q %q, want allowed allowed and none for the final turn", s1.Verdict, s2.Verdict, s3.Verdict)
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

	// The relative path was resolved under /workspace (policy, then
	// realpath in the pod) before the file was read.
	if got := strings.Join(sb.execs[0], " "); got != "realpath -m -- /workspace/calc/ops.py" {
		t.Errorf("first exec = %q", got)
	}
	if got := strings.Join(sb.execs[1], " "); got != "cat /workspace/calc/ops.py" {
		t.Errorf("second exec = %q", got)
	}
	if sb.copied["/workspace/calc/ops.py"] != "fixed\n" {
		t.Errorf("write_file content not copied in: %v", sb.copied)
	}
	// realpath, cat, realpath, mkdir -p, cp: every sandbox command was recorded.
	if len(recorded) != 5 {
		t.Errorf("recorded %d commands, want 5", len(recorded))
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
		resp = append(resp, toolUse("toolu_x", "run_command", `{"argv":["ls"]}`, 10, 5))
	}
	client := &fakeClient{responses: resp}
	c := cfg()
	c.Limits.MaxSteps = 4
	res, err := Run(context.Background(), client, &fakeSandbox{}, c, func(string, int, sandbox.Result) {})
	if err != nil {
		t.Fatal(err)
	}
	if res.Stop != StopLimit || res.Exit != "budget_steps" || len(res.Steps) != 4 || len(client.calls) != 4 {
		t.Errorf("stop=%q exit=%q steps=%d calls=%d, want limit budget_steps 4 4", res.Stop, res.Exit, len(res.Steps), len(client.calls))
	}
}

func TestRunRejectsBadCalls(t *testing.T) {
	tests := []struct {
		name, tool, input, wantText, wantRule string
	}{
		{"parent escape", "read_file", `{"path":"../etc/passwd"}`, "outside /workspace", "path"},
		{"absolute escape", "write_file", `{"path":"/tmp/x","content":"y"}`, "outside /workspace", "path"},
		{"dotdot inside path", "read_file", `{"path":"/workspace/../etc/shadow"}`, "outside /workspace", "path"},
		{"not in contract", "delete_file", `{"path":"a"}`, "not allowed", "tool"},
		{"shell", "run_command", `{"argv":["sh","-c","cat /etc/passwd"]}`, "not on the allowlist", "program"},
		{"old command shape", "run_command", `{"command":"ls"}`, "invalid input", "input"},
		{"find -delete", "run_command", `{"argv":["find",".","-delete"]}`, "deletes files", "flag"},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			client := &fakeClient{responses: []string{
				toolUse("toolu_1", tc.tool, tc.input, 10, 5),
				endTurn("ok", 10, 5),
			}}
			sb := &fakeSandbox{}
			res, err := Run(context.Background(), client, sb, cfg(), func(string, int, sandbox.Result) {})
			if err != nil {
				t.Fatal(err)
			}
			s := res.Steps[0]
			if !s.IsError || !strings.Contains(s.Output, tc.wantText) {
				t.Errorf("step = %+v, want is_error containing %q", s, tc.wantText)
			}
			if s.Verdict != "denied" || s.Rule != tc.wantRule || !strings.Contains(s.Reason, tc.wantText) || s.ExitCode != nil {
				t.Errorf("trace step verdict=%q rule=%q reason=%q exit=%v, want denied %q", s.Verdict, s.Rule, s.Reason, s.ExitCode, tc.wantRule)
			}
			if len(sb.execs) != 0 || len(sb.copied) != 0 {
				t.Errorf("rejected call reached the sandbox: execs=%v copied=%v", sb.execs, sb.copied)
			}
			b, _ := json.Marshal(client.calls[1].Messages)
			if !strings.Contains(string(b), `"is_error":true`) || !strings.Contains(string(b), "denied by policy") {
				t.Errorf("model was not told the call was denied: %s", b)
			}
		})
	}
}

func TestToolNotInContractIsNotOffered(t *testing.T) {
	client := &fakeClient{responses: []string{endTurn("nothing to do", 10, 5)}}
	c := cfg()
	c.Tools = []string{"read_file"}
	if _, err := Run(context.Background(), client, &fakeSandbox{}, c, func(string, int, sandbox.Result) {}); err != nil {
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
	if _, err := Run(context.Background(), &fakeClient{}, &fakeSandbox{}, c, func(string, int, sandbox.Result) {}); err == nil {
		t.Error("an unknown tool in the contract should fail the run")
	}
}

func TestRunCommandOutputAndTruncation(t *testing.T) {
	big := strings.Repeat("é", maxOutput) // 2 bytes each: twice the cap
	client := &fakeClient{responses: []string{
		toolUse("toolu_1", "run_command", `{"argv":["pytest","-q"]}`, 10, 5),
		endTurn("ok", 10, 5),
	}}
	sb := &fakeSandbox{exec: func([]string) sandbox.Result {
		return sandbox.Result{Stdout: big, Stderr: "command terminated with exit code 1\n", ExitCode: 1}
	}}
	res, err := Run(context.Background(), client, sb, cfg(), func(string, int, sandbox.Result) {})
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
	// "-q" is an option with no path in it, so nothing needs realpath,
	// and the only exec is the command itself: argv form, no shell.
	if len(sb.execs) != 1 || strings.Join(sb.execs[0], " ") != "timeout 60 pytest -q" {
		t.Errorf("execs = %q", sb.execs)
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
	resp := strings.Replace(toolUse("toolu_1", "run_command", `{"argv":["find",".","-name","x"]}`, 10, 5),
		`"stop_reason":"tool_use"`, `"stop_reason":"max_tokens"`, 1)
	sb := &fakeSandbox{}
	res, err := Run(context.Background(), &fakeClient{responses: []string{resp}}, sb, cfg(), func(string, int, sandbox.Result) {})
	if err != nil {
		t.Fatal(err)
	}
	if res.Stop != StopMaxTokens || len(sb.execs) != 0 {
		t.Errorf("stop=%q execs=%v; a cut-off tool call must not run", res.Stop, sb.execs)
	}
}

func TestAPIErrorIsReturned(t *testing.T) {
	_, err := Run(context.Background(), &fakeClient{err: errors.New("529 overloaded")}, &fakeSandbox{}, cfg(), func(string, int, sandbox.Result) {})
	if err == nil || !strings.Contains(err.Error(), "529") {
		t.Errorf("err = %v", err)
	}
}

// A symlink out of /workspace passes the text checks, so the policy asks
// the sandbox (realpath) and denies the call; the read itself never runs.
func TestSymlinkDeniedAfterRealpath(t *testing.T) {
	client := &fakeClient{responses: []string{
		toolUse("toolu_1", "read_file", `{"path":"etc-link/passwd"}`, 10, 5),
		endTurn("ok", 10, 5),
	}}
	sb := &fakeSandbox{links: map[string]string{"/workspace/etc-link": "/etc"}}
	var recorded []sandbox.Result
	res, err := Run(context.Background(), client, sb, cfg(), func(_ string, _ int, r sandbox.Result) { recorded = append(recorded, r) })
	if err != nil {
		t.Fatal(err)
	}
	s := res.Steps[0]
	if s.Verdict != "denied" || s.Rule != "path" || !strings.Contains(s.Reason, "resolves to /etc/passwd") {
		t.Errorf("step = %+v", s)
	}
	if len(sb.execs) != 1 || sb.execs[0][0] != "realpath" {
		t.Errorf("execs = %q, want only realpath", sb.execs)
	}
	if len(recorded) != 1 {
		t.Errorf("recorded %d commands, want the realpath call", len(recorded))
	}
}

// sed runs with --sandbox, and every command is argv with timeout in front.
func TestRunCommandArgv(t *testing.T) {
	client := &fakeClient{responses: []string{
		toolUse("toolu_1", "run_command", `{"argv":["sed","-i","s|    return a // b|    return a / b|","calc/ops.py"]}`, 10, 5),
		endTurn("ok", 10, 5),
	}}
	sb := &fakeSandbox{}
	if _, err := Run(context.Background(), client, sb, cfg(), func(string, int, sandbox.Result) {}); err != nil {
		t.Fatal(err)
	}
	last := sb.execs[len(sb.execs)-1]
	want := []string{"timeout", "60", "sed", "--sandbox", "-i", "s|    return a // b|    return a / b|", "calc/ops.py"}
	if strings.Join(last, "\x00") != strings.Join(want, "\x00") {
		t.Errorf("exec = %q, want %q", last, want)
	}
}

// The run_command tool takes an argv array, and its description names the
// allowlist.
func TestRunCommandSchema(t *testing.T) {
	b, _ := json.Marshal(toolDefs["run_command"])
	for _, want := range []string{`"argv":{`, `"type":"array"`, `"items":{"type":"string"}`, "no shell", "python, sed"} {
		if !strings.Contains(string(b), want) {
			t.Errorf("run_command definition lacks %q: %s", want, b)
		}
	}
}
