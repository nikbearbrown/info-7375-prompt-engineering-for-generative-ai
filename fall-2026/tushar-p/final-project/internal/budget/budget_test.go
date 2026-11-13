package budget

import (
	"math"
	"testing"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

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

var lim = Limits{MaxSteps: 10, MaxTotalTokens: 50_000, MaxCostUSD: 0.01, Timeout: time.Minute, MaxPolicyViolations: 3}

func TestBefore(t *testing.T) {
	tests := []struct {
		name string
		used Used
		want trace.ExitReason
	}{
		{"fresh", Used{}, ""},
		{"one step left", Used{Steps: 9}, ""},
		{"steps used up", Used{Steps: 10}, trace.ReasonBudgetSteps},
		{"two denials", Used{PolicyViolations: 2}, ""},
		{"third denial", Used{PolicyViolations: 3}, trace.ReasonPolicyViolationLimit},
		{"both: violations win", Used{Steps: 10, PolicyViolations: 3}, trace.ReasonPolicyViolationLimit},
	}
	for _, tc := range tests {
		if got := lim.Before(tc.used); got != tc.want {
			t.Errorf("%s: Before = %q, want %q", tc.name, got, tc.want)
		}
	}
}

func TestFits(t *testing.T) {
	// Haiku: $0.10 in, $0.50 out per million. A 16,000-token reply costs at
	// most $0.008, so with $0.01 the cost limit bites before 50K tokens.
	// (The harness's reply cap is 4,096 since T2.3; these cases pass the
	// reply size explicitly, so they test the arithmetic, not the cap.)
	tests := []struct {
		name            string
		used            Used
		input, maxReply int64
		want            trace.ExitReason
	}{
		{"fits", Used{}, 1_000, 16_000, ""},
		{"exactly the token limit", Used{InputTokens: 30_000, OutputTokens: 3_000}, 1_000, 16_000, ""},
		{"one token over", Used{InputTokens: 30_000, OutputTokens: 3_001}, 1_000, 16_000, trace.ReasonBudgetTokens},
		{"already over (count was low)", Used{InputTokens: 50_001}, 0, 0, trace.ReasonBudgetTokens},
		{"cost: worst case over", Used{CostUSD: 0.0025}, 1_000, 16_000, trace.ReasonBudgetCost}, // 0.0025 + 0.0001 + 0.008
		{"cost: worst case fits", Used{CostUSD: 0.0015}, 1_000, 16_000, ""},                     // 0.0015 + 0.0001 + 0.008
	}
	for _, tc := range tests {
		got, err := lim.Fits("claude-haiku-5-5", tc.used, tc.input, tc.maxReply)
		if err != nil || got != tc.want {
			t.Errorf("%s: Fits = %q (err %v), want %q", tc.name, got, err, tc.want)
		}
	}
	if _, err := lim.Fits("unknown-model", Used{}, 1, 1); err == nil {
		t.Error("unknown model should be an error")
	}
}
