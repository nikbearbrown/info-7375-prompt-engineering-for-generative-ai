package main

// Tests for --contract (T5.1).

import (
	"bytes"
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/anthropic-sdk-go/v2"

	"github.com/tushar-patel28/agent-proving-ground/contracts"
	"github.com/tushar-patel28/agent-proving-ground/internal/loop"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

func TestRunArgsContract(t *testing.T) {
	for _, tc := range []struct {
		args []string
		want string // "" means an error
	}{
		{[]string{"001"}, "A"},
		{[]string{"001", "--contract", "B"}, "B"},
		{[]string{"--contract", "B", "001"}, "B"},
		{[]string{"001", "--contract=A"}, "A"},
		{[]string{"001", "--contract", "C"}, ""},
		{[]string{"001", "--contract", "b"}, ""},
		{[]string{"001", "--contract", ""}, ""},
	} {
		o, err := parseRunArgs(tc.args)
		switch {
		case tc.want == "" && err == nil:
			t.Errorf("parseRunArgs(%q) should fail", tc.args)
		case tc.want != "" && (err != nil || o.contract.Name != tc.want || o.contract.System != contracts.MustGet(tc.want).System):
			t.Errorf("parseRunArgs(%q) = contract %q, err %v; want %s", tc.args, o.contract.Name, err, tc.want)
		}
	}
}

func TestEvalArgsContract(t *testing.T) {
	if o, err := parseEvalArgs([]string{"--set", "dev"}); err != nil || o.contract != "A" {
		t.Errorf("default: contract %q, err %v; want A", o.contract, err)
	}
	if o, err := parseEvalArgs([]string{"--set", "dev", "--contract", "B"}); err != nil || o.contract != "B" {
		t.Errorf("--contract B: contract %q, err %v", o.contract, err)
	}
	if _, err := parseEvalArgs([]string{"--set", "dev", "--contract", "C"}); err == nil {
		t.Error("--contract C should fail")
	}
}

// systemSpy is stopClient that also keeps the system prompt of each request.
type systemSpy struct {
	stopClient
	systems []string
}

func (s *systemSpy) New(ctx context.Context, p anthropic.MessageNewParams) (*anthropic.Message, error) {
	for _, b := range p.System {
		s.systems = append(s.systems, b.Text)
	}
	return s.stopClient.New(ctx, p) // the embedded stopClient's New does the rest
}

// apg eval --contract B: B's system prompt is what the model gets, and the
// eval-log line, EVAL-LOG.md, and the trace all name contract B.
func TestEvalContractB(t *testing.T) {
	root := t.TempDir()
	tasksDir := filepath.Join(root, "tasks")
	writeEvalTask(t, tasksDir, "001-pass", "PASS")
	split := `{"seed": 1, "dev": ["001-pass"], "held_out": []}`
	if err := os.WriteFile(filepath.Join(tasksDir, "split.json"), []byte(split), 0o644); err != nil {
		t.Fatal(err)
	}
	opts := evalOpts{set: "dev", contract: "B", runs: 1, tasksDir: tasksDir, tracesDir: filepath.Join(root, "traces"),
		outDir: filepath.Join(root, "out"), resultsDir: filepath.Join(root, "results")}
	client := &systemSpy{stopClient: stopClient{turns: []turn{doneTurn}}}
	var stdout, stderr bytes.Buffer
	env := evalEnv{
		newSandbox: func() (sandbox.Sandbox, string, error) {
			return &evalSandbox{exitSandbox{checkExit: 0}}, fmt.Sprintf("apg-fake%d", time.Now().UnixNano()%1e6), nil
		},
		client: client,
		git:    func() (string, bool) { return "abc1234", false },
		now:    time.Now,
		stdout: &stdout,
		stderr: &stderr,
	}
	if code := runEval(context.Background(), env, opts); code != exitPass {
		t.Fatalf("exit %d\nstdout:\n%s\nstderr:\n%s", code, stdout.String(), stderr.String())
	}

	b := contracts.MustGet("B")
	if len(client.systems) == 0 {
		t.Fatal("no model request")
	}
	for i, s := range client.systems {
		if s != b.System {
			t.Errorf("request %d: system prompt is not contract B's", i+1)
		}
	}
	wantVersion := loop.PromptVersion(b.System)
	if !strings.Contains(stdout.String(), "contract B, prompt "+wantVersion[:12]) {
		t.Errorf("eval header does not name contract B:\n%s", stdout.String())
	}
	entries, err := readLog(filepath.Join(opts.resultsDir, "eval-log.jsonl"))
	if err != nil || len(entries) != 1 {
		t.Fatalf("eval log: %d entries, %v", len(entries), err)
	}
	e := entries[0]
	if e.PromptContract != "B" || e.PromptVersion != wantVersion {
		t.Errorf("eval-log line: contract %q, prompt version %s; want B, %s", e.PromptContract, e.PromptVersion, wantVersion)
	}
	md, _ := os.ReadFile(filepath.Join(opts.resultsDir, "EVAL-LOG.md"))
	if !strings.Contains(string(md), "- Prompt contract: `B`\n") {
		t.Errorf("EVAL-LOG.md does not name contract B:\n%s", md)
	}
	f, err := os.Open(e.Rows[0].Trace)
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()
	tr, err := trace.Decode(f)
	if err != nil {
		t.Fatal(err)
	}
	if tr.PromptContract != "B" || tr.PromptVersion != wantVersion {
		t.Errorf("trace: contract %q, prompt version %s; want B, %s", tr.PromptContract, tr.PromptVersion, wantVersion)
	}
}

// Eval-log lines from before T5.1 have no prompt_contract; EVAL-LOG.md
// says so, and says whether their prompt version is contract A's.
func TestContractCellOldLines(t *testing.T) {
	a := loop.PromptVersion(contracts.MustGet("A").System)
	for _, tc := range []struct {
		e    evalEntry
		want string
	}{
		{evalEntry{PromptContract: "B"}, "`B`"},
		{evalEntry{PromptVersion: a}, "not recorded (before T5.1); the prompt version is contract A's"},
		{evalEntry{PromptVersion: "0123"}, "not recorded (before T5.1)"},
	} {
		if got := contractCell(tc.e); got != tc.want {
			t.Errorf("contractCell(%+v) = %q, want %q", tc.e, got, tc.want)
		}
	}
}

// apg show names the prompt contract when the trace has one, and keeps the
// old header line when it does not (the golden files cover that case).
func TestShowContract(t *testing.T) {
	path := filepath.Join("testdata", "show", "pass.json")
	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	withB := strings.Replace(string(b), `"model": "claude-haiku-5-5"`, `"model": "claude-haiku-5-5", "prompt_contract": "B"`, 1)
	if withB == string(b) {
		t.Fatal("test setup: the fixture has no model key to add the contract after")
	}
	var out bytes.Buffer
	if err := showTrace(&out, []byte(withB), path, false, false); err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(out.String(), "model    claude-haiku-5-5   contract B   prompt ") {
		t.Errorf("header does not name contract B:\n%s", out.String())
	}
}
