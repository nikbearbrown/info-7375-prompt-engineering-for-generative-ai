package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"slices"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/anthropic-sdk-go/v2"

	"github.com/tushar-patel28/agent-proving-ground/internal/budget"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/stop"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// exitClient is a fake model. Each turn it returns the next reply from
// replies (repeating the last one when they run out), and each token count
// returns the next value from counts (repeating the last). With block set,
// New waits until its context is done, like a call that never answers.
type exitClient struct {
	replies []reply
	counts  []int64
	block   bool
	err     error // returned by New, if set

	newCalls, countCalls int
}

// reply is one fake model turn: a tool call (tool != "") or a final answer.
type reply struct {
	tool, input string
	in, out     int64 // usage
}

func (c *exitClient) CountTokens(context.Context, anthropic.MessageCountTokensParams) (*anthropic.MessageTokensCount, error) {
	n := c.counts[min(c.countCalls, len(c.counts)-1)] // min is built in since Go 1.21
	c.countCalls++
	return &anthropic.MessageTokensCount{InputTokens: n}, nil
}

func (c *exitClient) New(ctx context.Context, _ anthropic.MessageNewParams) (*anthropic.Message, error) {
	c.newCalls++
	if c.block {
		<-ctx.Done() // wait until the deadline (or cancel)
		return nil, ctx.Err()
	}
	if c.err != nil {
		return nil, c.err
	}
	r := c.replies[min(c.newCalls-1, len(c.replies)-1)]
	msg := map[string]any{
		"id": "msg_fake", "type": "message", "role": "assistant", "model": "fake",
		"usage": map[string]int64{"input_tokens": r.in, "output_tokens": r.out},
	}
	if r.tool != "" {
		msg["stop_reason"] = "tool_use"
		msg["content"] = []any{map[string]any{"type": "tool_use", "id": fmt.Sprintf("toolu_%d", c.newCalls), "name": r.tool, "input": json.RawMessage(r.input)}}
	} else {
		msg["stop_reason"] = "end_turn"
		msg["content"] = []any{map[string]any{"type": "text", "text": "done"}}
	}
	b, _ := json.Marshal(msg)
	var m anthropic.Message
	return &m, json.Unmarshal(b, &m)
}

// exitSandbox is a fake pod. The check (bash .../check.sh) exits with
// checkExit. It records whether the check ran and whether Stop was called
// with a live context.
type exitSandbox struct {
	checkExit  int
	checkRan   bool
	stopped    bool
	stopCtxErr error
}

func (s *exitSandbox) Start(context.Context) ([]sandbox.Result, error) { return nil, nil }
func (s *exitSandbox) CopyIn(ctx context.Context, _, _ string) (sandbox.Result, error) {
	return sandbox.Result{}, ctx.Err()
}
func (s *exitSandbox) CopyOut(context.Context, string, string) (sandbox.Result, error) {
	return sandbox.Result{}, nil
}
func (s *exitSandbox) Stop(ctx context.Context) (sandbox.Result, error) {
	s.stopped, s.stopCtxErr = true, ctx.Err()
	return sandbox.Result{Args: []string{"kubectl", "delete", "pod"}}, nil
}
func (s *exitSandbox) Exec(ctx context.Context, cmd ...string) (sandbox.Result, error) {
	r := sandbox.Result{Args: cmd}
	if err := ctx.Err(); err != nil { // like kubectl, killed by its context
		r.ExitCode = -1
		return r, err
	}
	switch {
	case cmd[0] == "ls" && len(cmd) == 3: // setup's ls -A /workspace
		r.Stdout = "calc\n"
	case cmd[0] == "realpath":
		r.Stdout = strings.Join(cmd[3:], "\n") + "\n"
	case slices.Equal(cmd, stop.KillCmd): // before each check: nothing to kill here
		r.Stdout = `{"killed": [], "left": 0}` + "\n"
	case cmd[0] == "bash": // the check
		s.checkRan = true
		r.ExitCode = s.checkExit
		if s.checkExit != 0 {
			r.Stderr = fmt.Sprintf("command terminated with exit code %d\n", s.checkExit)
		}
	}
	return r, nil
}

func exitTask(lim budget.Limits) task {
	return task{
		Short: "001", ID: "001-x", Repo: "repo", Check: "check.sh",
		Goal: "Fix the bug.", AllowedTools: []string{"read_file", "write_file", "run_command"},
		Limits: lim, FromContract: []string{"max_steps"},
	}
}

// Generous limits; each case tightens one.
var roomy = budget.Limits{MaxSteps: 10, MaxTotalTokens: 1_000_000, MaxCostUSD: 1, Timeout: time.Minute, MaxPolicyViolations: 3}

var ls = reply{tool: "run_command", input: `{"argv":["ls"]}`, in: 100, out: 10}
var shell = reply{tool: "run_command", input: `{"argv":["sh","-c","ls"]}`, in: 100, out: 10}
var done = reply{in: 100, out: 10}

// Each exit reason, forced with the fake client. After every exit except
// error the check runs and decides the verdict; Stop always runs with a
// live context.
func TestEachExitReason(t *testing.T) {
	tests := []struct {
		name      string
		limits    func(*budget.Limits)
		client    *exitClient
		checkExit int

		wantReason   trace.ExitReason
		wantVerdict  string
		wantCheck    bool
		wantNewCalls int
	}{
		{name: "check_passed", client: &exitClient{replies: []reply{ls, done}, counts: []int64{100}},
			wantReason: trace.ReasonCheckPassed, wantVerdict: "PASS", wantCheck: true, wantNewCalls: 2},
		{name: "check_failed", client: &exitClient{replies: []reply{done}, counts: []int64{100}}, checkExit: 1,
			wantReason: trace.ReasonCheckFailed, wantVerdict: "FAIL", wantCheck: true, wantNewCalls: 1},

		// The step budget stops the loop; the check still decides. Here the
		// check passes, so the verdict is PASS with reason budget_steps.
		{name: "budget_steps", limits: func(l *budget.Limits) { l.MaxSteps = 2 },
			client:     &exitClient{replies: []reply{ls}, counts: []int64{100}},
			wantReason: trace.ReasonBudgetSteps, wantVerdict: "PASS", wantCheck: true, wantNewCalls: 2},

		// Step 1 uses 95,000 + 1,000 tokens. Before step 2, 96,000 + 1,000
		// counted + 4,096 worst-case reply > 100,000: step 2 never starts.
		{name: "budget_tokens", limits: func(l *budget.Limits) { l.MaxTotalTokens = 100_000 },
			client:     &exitClient{replies: []reply{{tool: "run_command", input: `{"argv":["ls"]}`, in: 95_000, out: 1_000}}, counts: []int64{1_000}},
			checkExit:  1,
			wantReason: trace.ReasonBudgetTokens, wantVerdict: "FAIL", wantCheck: true, wantNewCalls: 1},

		// The worst case of the first call is 1,000 in ($0.0001) + 4,096 out
		// ($0.002048) = $0.002148 > $0.002: no model call starts at all.
		{name: "budget_cost", limits: func(l *budget.Limits) { l.MaxCostUSD = 0.002 },
			client:    &exitClient{replies: []reply{done}, counts: []int64{1_000}},
			checkExit: 1, wantReason: trace.ReasonBudgetCost, wantVerdict: "FAIL", wantCheck: true, wantNewCalls: 0},

		// The model call never answers; the agent's deadline cuts it off.
		{name: "timeout", limits: func(l *budget.Limits) { l.Timeout = 200 * time.Millisecond },
			client:    &exitClient{block: true, counts: []int64{100}},
			checkExit: 1, wantReason: trace.ReasonTimeout, wantVerdict: "FAIL", wantCheck: true, wantNewCalls: 1},

		// Two denied calls (sh is not on the allowlist) with a limit of 2.
		{name: "policy_violation_limit", limits: func(l *budget.Limits) { l.MaxPolicyViolations = 2 },
			client:    &exitClient{replies: []reply{shell}, counts: []int64{100}},
			checkExit: 1, wantReason: trace.ReasonPolicyViolationLimit, wantVerdict: "FAIL", wantCheck: true, wantNewCalls: 2},

		// A harness failure: no check, FAIL.
		{name: "error", client: &exitClient{err: errors.New("500 internal server error"), counts: []int64{100}},
			wantReason: trace.ReasonError, wantVerdict: "FAIL", wantCheck: false, wantNewCalls: 1},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			lim := roomy
			if tc.limits != nil {
				tc.limits(&lim)
			}
			sb := &exitSandbox{checkExit: tc.checkExit}
			tr := runTask(context.Background(), sb, "apg-fake", exitTask(lim), tc.client, nil)

			if tr.ExitReason != tc.wantReason || tr.Verdict != tc.wantVerdict {
				t.Fatalf("reason=%s verdict=%s (error %q), want %s %s", tr.ExitReason, tr.Verdict, tr.Error, tc.wantReason, tc.wantVerdict)
			}
			if sb.checkRan != tc.wantCheck || tr.Check.Ran != tc.wantCheck {
				t.Errorf("check ran: sandbox %v, trace %v; want %v", sb.checkRan, tr.Check.Ran, tc.wantCheck)
			}
			if tc.wantCheck && (tr.Check.ExitCode == nil || *tr.Check.ExitCode != tc.checkExit) {
				t.Errorf("trace check exit = %v, want %d", tr.Check.ExitCode, tc.checkExit)
			}
			if tc.client.newCalls != tc.wantNewCalls {
				t.Errorf("model calls = %d, want %d", tc.client.newCalls, tc.wantNewCalls)
			}
			if !sb.stopped || sb.stopCtxErr != nil {
				t.Errorf("stop called=%v with ctx err %v; want a live context", sb.stopped, sb.stopCtxErr)
			}
			// The budget section is always there for an agent run, and the
			// trace validates.
			if tr.Budget == nil || tr.Budget.Limits.MaxSteps != lim.MaxSteps || tr.Budget.Used.Steps != len(tr.Steps) {
				t.Errorf("budget = %+v, steps %d", tr.Budget, len(tr.Steps))
			}
			if _, err := trace.Write(t.TempDir(), tr); err != nil {
				t.Errorf("trace does not write: %v", err)
			}
		})
	}
}

// Ctrl-C (a cancelled context, not a deadline) is a harness error, not a
// timeout: the check does not run, and Stop still runs.
func TestInterruptIsAnError(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	client := &exitClient{block: true, counts: []int64{100}}
	sb := &exitSandbox{}
	go func() { time.Sleep(100 * time.Millisecond); cancel() }() // "go" runs the func concurrently
	tr := runTask(ctx, sb, "apg-fake", exitTask(roomy), client, nil)
	if tr.ExitReason != trace.ReasonError || sb.checkRan || !sb.stopped || sb.stopCtxErr != nil {
		t.Errorf("reason=%s checkRan=%v stopped=%v stopErr=%v", tr.ExitReason, sb.checkRan, sb.stopped, sb.stopCtxErr)
	}
}

// A timeout while a tool is running (kubectl killed by the deadline) is
// also the timeout exit, and the cut-off step is in the trace.
func TestTimeoutDuringTool(t *testing.T) {
	lim := roomy
	lim.Timeout = 200 * time.Millisecond
	client := &exitClient{replies: []reply{ls}, counts: []int64{100}}
	sb := &slowToolSandbox{exitSandbox: exitSandbox{checkExit: 1}}
	tr := runTask(context.Background(), sb, "apg-fake", exitTask(lim), client, nil)
	if tr.ExitReason != trace.ReasonTimeout || !sb.checkRan || !sb.stopped {
		t.Fatalf("reason=%s checkRan=%v stopped=%v (error %q)", tr.ExitReason, sb.checkRan, sb.stopped, tr.Error)
	}
	if len(tr.Steps) != 1 || !strings.Contains(tr.Steps[0].Output, "deadline exceeded") {
		t.Errorf("steps = %+v, want the cut-off ls step", tr.Steps)
	}
}

// slowToolSandbox is exitSandbox, except that an agent command (timeout 60
// ...) hangs until its context ends. Embedding exitSandbox gives it all of
// exitSandbox's methods; Exec here replaces that one.
type slowToolSandbox struct{ exitSandbox }

func (s *slowToolSandbox) Exec(ctx context.Context, cmd ...string) (sandbox.Result, error) {
	if cmd[0] == "timeout" {
		<-ctx.Done()
		return sandbox.Result{Args: cmd, ExitCode: -1}, fmt.Errorf("exec: %w", ctx.Err())
	}
	return s.exitSandbox.Exec(ctx, cmd...)
}
