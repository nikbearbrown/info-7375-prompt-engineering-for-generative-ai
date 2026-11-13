// Package budget holds a run's limits (steps, tokens, estimated cost,
// wall-clock time, denied calls), the harness defaults, the model prices,
// and the checks the loop makes before each model call.
//
// The rule: a model call starts only if its worst case fits. Before each
// call the loop asks the API how many input tokens the next request has
// (count_tokens), and assumes the reply uses the full per-reply max_tokens
// (4,096 since T2.3).
// If that worst case would pass the token or cost limit, the run stops
// instead. Actual usage is added after each call; if count_tokens was ever
// low and the total went over, the next check stops the run, and the trace
// shows the overshoot.
package budget

import (
	"fmt"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// Harness defaults, used when the contract leaves a limit out. max_steps
// has no default: every contract must set it.
const (
	DefaultMaxTotalTokens      = 200_000
	DefaultMaxCostUSD          = 0.05
	DefaultTimeout             = 5 * time.Minute
	DefaultMaxPolicyViolations = 3
)

// Limits are one run's budget. Timeout covers the agent loop only; the
// harness's own steps (start, setup, check, stop) have fixed limits of
// their own, so the check can still run after the agent times out.
type Limits struct {
	MaxSteps            int     // model turns
	MaxTotalTokens      int64   // input + output, summed over all model calls
	MaxCostUSD          float64 // estimated from list prices (Prices)
	Timeout             time.Duration
	MaxPolicyViolations int // stop after this many denied tool calls
}

// Used is what a run has spent so far.
type Used struct {
	Steps            int
	InputTokens      int64
	OutputTokens     int64
	CostUSD          float64
	PolicyViolations int
}

// TotalTokens is input plus output.
func (u Used) TotalTokens() int64 { return u.InputTokens + u.OutputTokens }

// Before reports whether the next model call may start, judging by the
// counts alone: steps and denied calls. It returns "" if it may, or the
// exit reason that stops the run.
func (l Limits) Before(u Used) trace.ExitReason {
	switch {
	case u.PolicyViolations >= l.MaxPolicyViolations:
		return trace.ReasonPolicyViolationLimit
	case u.Steps >= l.MaxSteps:
		return trace.ReasonBudgetSteps
	}
	return ""
}

// Fits reports whether a call with nextInput input tokens (from
// count_tokens) and a reply of up to maxReply tokens fits in what is left.
// It returns "" if it does, or budget_tokens / budget_cost.
func (l Limits) Fits(model string, u Used, nextInput, maxReply int64) (trace.ExitReason, error) {
	if u.TotalTokens()+nextInput+maxReply > l.MaxTotalTokens {
		return trace.ReasonBudgetTokens, nil
	}
	worst, err := EstimateCost(model, nextInput, maxReply)
	if err != nil {
		return "", err
	}
	if u.CostUSD+worst > l.MaxCostUSD {
		return trace.ReasonBudgetCost, nil
	}
	return "", nil
}

// Price is USD per million tokens. The long-prompt rates apply when one
// request's input exceeds LongOver tokens.
type Price struct {
	In, Out         float64
	InLong, OutLong float64
	LongOver        int64
}

// Prices are list prices, USD per million tokens. This is the only place
// prices live.
//
// Source: Anthropic's Claude API pricing page,
// https://platform.claude.com/docs/en/about-claude/pricing.md, as listed
// in Claude Code's claude-api reference (model table "cached: 2026-11-03")
// on Nov 3, 2026: Claude Haiku 5.5 $0.10 input / $0.50 output, and
// $0.50 / $2.50 for prompts over 100K tokens. Not re-checked against the
// live page since; check it before relying on these numbers.
//
// The estimate ignores prompt caching (not used) and taxes; it is not a bill.
var Prices = map[string]Price{
	"claude-haiku-5-5": {In: 0.10, Out: 0.50, InLong: 0.50, OutLong: 2.50, LongOver: 100_000},
}

// EstimateCost returns the estimated USD cost of one request.
func EstimateCost(model string, inputTokens, outputTokens int64) (float64, error) {
	p, ok := Prices[model]
	if !ok {
		return 0, fmt.Errorf("no price for model %q", model)
	}
	in, out := p.In, p.Out
	if inputTokens > p.LongOver {
		in, out = p.InLong, p.OutLong
	}
	return (float64(inputTokens)*in + float64(outputTokens)*out) / 1e6, nil
}
