package loop

// T5.1: prompt contracts A and B differ only in the system prompt.

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/anthropics/anthropic-sdk-go/v2"

	"github.com/tushar-patel28/agent-proving-ground/contracts"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/stop"
)

// Prompt versions, pinned. A is the version of every run before T5.1;
// B is frozen with its text (D30).
const (
	versionA = "77d9d716f4239fa8b9be66353e4aa88b4c880a2833dd8d9f215c60b449021be7"
	versionB = "3de39bebb4df2df5dc08888860563ab53dbb6511287fa102b6aa2a7f5728e775"
)

func TestContractPromptVersions(t *testing.T) {
	a := PromptVersion(contracts.MustGet("A").System)
	b := PromptVersion(contracts.MustGet("B").System)
	if a != versionA {
		t.Errorf("contract A: prompt version %s, want %s", a, versionA)
	}
	if b == a {
		t.Errorf("contract B has the same prompt version as A: %s", b)
	}
	if b != versionB {
		t.Errorf("contract B: prompt version %s, want %s (frozen, D30)", b, versionB)
	}
}

// failingStop is a stop condition whose check runs and fails after every
// step, so the not-complete note is sent.
type failingStop struct{}

func (failingStop) AfterStep(context.Context, int) (stop.StepResult, error) {
	return stop.StepResult{Changed: true, Ran: true, Passed: false}, nil
}

// requestsFor runs one scripted conversation (a write, so a failed check
// and its note; a denied call; the end) with the given system prompt, and
// returns every request the loop sent.
func requestsFor(t *testing.T, system string) []anthropic.MessageNewParams {
	t.Helper()
	client := &fakeClient{responses: []string{
		toolUse("toolu_1", "write_file", `{"path":"calc/ops.py","content":"x = 1\n"}`, 10, 5),
		toolUse("toolu_2", "run_command", `{"argv":["sh","-c","echo hi"]}`, 10, 5),
		endTurn("done", 10, 5),
	}}
	c := cfg()
	c.System = system
	c.Stop = failingStop{}
	if _, err := Run(context.Background(), client, &fakeSandbox{}, c, func(string, int, sandbox.Result) {}); err != nil {
		t.Fatal(err)
	}
	if len(client.calls) != 3 {
		t.Fatalf("%d requests, want 3", len(client.calls))
	}
	return client.calls
}

// Every request under A and under B is the same JSON once the system
// prompt is taken out, and the system prompt is exactly the contract's.
// That covers the task message, the tools and tool_choice, the
// not-complete note, and the denied-call result.
func TestContractsDifferOnlyInSystemPrompt(t *testing.T) {
	sysA, sysB := contracts.MustGet("A").System, contracts.MustGet("B").System
	reqA, reqB := requestsFor(t, sysA), requestsFor(t, sysB)
	for i := range reqA {
		for name, r := range map[string]struct {
			req  anthropic.MessageNewParams
			want string
		}{"A": {reqA[i], sysA}, "B": {reqB[i], sysB}} {
			if len(r.req.System) != 1 || r.req.System[0].Text != r.want {
				t.Errorf("request %d under %s: system is not the contract's text", i+1, name)
			}
		}
		// Copies of the structs (Go assigns structs by value), with the
		// system prompt removed; the slices inside are shared, not changed.
		a, b := reqA[i], reqB[i]
		a.System, b.System = nil, nil
		ja, err := json.Marshal(a)
		if err != nil {
			t.Fatal(err)
		}
		jb, err := json.Marshal(b)
		if err != nil {
			t.Fatal(err)
		}
		if string(ja) != string(jb) {
			t.Errorf("request %d: A and B differ outside the system prompt:\nA: %s\nB: %s", i+1, ja, jb)
		}
	}
}

// Without a system prompt the loop refuses to start.
func TestRunNeedsSystemPrompt(t *testing.T) {
	c := cfg()
	c.System = ""
	client := &fakeClient{responses: []string{endTurn("done", 1, 1)}}
	if _, err := Run(context.Background(), client, &fakeSandbox{}, c, func(string, int, sandbox.Result) {}); err == nil || len(client.calls) != 0 {
		t.Errorf("err = %v, calls = %d; want an error before any call", err, len(client.calls))
	}
}
