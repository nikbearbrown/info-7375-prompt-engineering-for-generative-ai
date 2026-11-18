package trace

// Tests for prompt_contract (T5.1).

import (
	"bytes"
	"strings"
	"testing"
)

// agent is good() as an agent run (model and budget set).
func agent() *Trace {
	tr := good()
	tr.Model, tr.LoopStop = "claude-haiku-5-5", "end_turn"
	tr.Budget = &Budget{
		Limits: BudgetLimits{MaxSteps: 10, MaxTotalTokens: 100_000, MaxCostUSD: 0.02, TimeoutSeconds: 300, MaxPolicyViolations: 3, MaxReplyTokens: 4096},
		Used:   BudgetUsed{Steps: 1, InputTokens: 100, OutputTokens: 10, TotalTokens: 110, CostUSD: 0.00002, CountTokensCalls: 1},
	}
	return tr
}

func TestPromptContract(t *testing.T) {
	for _, name := range []string{"A", "B"} {
		tr := agent()
		tr.PromptContract = name
		got, err := Decode(bytes.NewReader(encode(t, tr)))
		if err != nil || got.PromptContract != name {
			t.Errorf("contract %s: decoded %+v, %v", name, got, err)
		}
	}
	// Absent (every agent trace before T5.1): still accepted.
	if _, err := Decode(bytes.NewReader(encode(t, agent()))); err != nil {
		t.Errorf("agent trace without prompt_contract rejected: %v", err)
	}

	unknown := agent()
	unknown.PromptContract = "C"
	noAgent := good()
	noAgent.PromptContract = "A"
	for name, tc := range map[string]struct {
		tr   *Trace
		want string
	}{
		"unknown contract":   {unknown, "unknown prompt contract"},
		"contract, no agent": {noAgent, "without an agent"},
	} {
		if err := tc.tr.Validate(); err == nil || !strings.Contains(err.Error(), tc.want) {
			t.Errorf("%s: err = %v, want %q", name, err, tc.want)
		}
	}
}
