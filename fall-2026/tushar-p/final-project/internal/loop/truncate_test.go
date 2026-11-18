package loop

// Tests for D26: long tool output keeps its head and its tail.

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"testing"
	"unicode/utf8"

	"github.com/tushar-patel28/agent-proving-ground/contracts"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
)

// runPytest runs the loop for one run_command call whose sandbox returns
// stdout and stderr, and returns the step's output and the JSON of the
// message that carried the tool result back to the model.
func runPytest(t *testing.T, stdout, stderr string, exit int) (output, sentJSON string) {
	t.Helper()
	client := &fakeClient{responses: []string{
		toolUse("toolu_1", "run_command", `{"argv":["python","-m","pytest","-q"]}`, 10, 5),
		endTurn("done", 10, 5),
	}}
	sb := &fakeSandbox{exec: func([]string) sandbox.Result {
		return sandbox.Result{Stdout: stdout, Stderr: stderr, ExitCode: exit}
	}}
	res, err := Run(context.Background(), client, sb, cfg(), func(string, int, sandbox.Result) {})
	if err != nil {
		t.Fatal(err)
	}
	if len(client.calls) != 2 {
		t.Fatalf("model calls = %d, want 2", len(client.calls))
	}
	// The second request's last message is the user message holding the
	// tool result: exactly what the model saw.
	msgs := client.calls[1].Messages
	b, err := json.Marshal(msgs[len(msgs)-1])
	if err != nil {
		t.Fatal(err)
	}
	return res.Steps[0].Output, string(b)
}

// pytestOutput builds pytest-style output over the limit, with the real
// error only on its last lines, like dev run 014.
func pytestOutput() string {
	var b strings.Builder
	b.WriteString("F                                                                        [100%]\n")
	b.WriteString("=================================== FAILURES ===================================\n")
	b.WriteString("___________________________ test_commit_matches_git ____________________________\n\n")
	for i := 0; b.Len() < maxOutput+1500; i++ {
		fmt.Fprintf(&b, "/usr/local/lib/python3.12/subprocess.py:%d: in _execute_child\n    self.pid = _fork_exec(args, executable_list, close_fds)\n", 1000+i)
	}
	b.WriteString(">                   raise child_exception_type(errno_num, err_msg, err_filename)\n")
	b.WriteString("E                   FileNotFoundError: [Errno 2] No such file or directory: 'git'\n\n")
	b.WriteString("=========================== short test summary info ============================\n")
	b.WriteString("FAILED tests/test_version.py::test_commit_matches_git - FileNotFoundError: [E...\n")
	b.WriteString("1 failed in 0.02s\n")
	return b.String()
}

const gitError = "FileNotFoundError: [Errno 2] No such file or directory: 'git'"

func TestLongPytestOutputKeepsTheError(t *testing.T) {
	out, sent := runPytest(t, pytestOutput(), "command terminated with exit code 1\n", 1)
	for _, want := range []string{gitError, "1 failed in 0.02s", "exit_code: 1", " bytes cut ...]"} {
		if !strings.Contains(out, want) {
			t.Errorf("step output lacks %q", want)
		}
		if !strings.Contains(sent, want) {
			t.Errorf("tool result sent to the model lacks %q", want)
		}
	}
	if strings.Count(out, "bytes cut ...]") != 1 {
		t.Errorf("want exactly one cut marker, got %d", strings.Count(out, "bytes cut ...]"))
	}
}

// Replays the real output of dev run 014, step 6: the error the model
// never saw now reaches it, and the marker counts the same 544 bytes the
// old head-only cut dropped.
func TestRun014OutputReachesTheModel(t *testing.T) {
	b, err := os.ReadFile("../../evidence/traces/20261114T010633Z-9ee17ef3.json")
	if err != nil {
		t.Fatal(err)
	}
	// Only the fields this test needs; encoding/json ignores the rest.
	var tr struct {
		Commands []struct {
			Phase    string `json:"phase"`
			Step     int    `json:"step"`
			Stdout   string `json:"stdout"`
			Stderr   string `json:"stderr"`
			ExitCode int    `json:"exit_code"`
		} `json:"commands"`
	}
	if err := json.Unmarshal(b, &tr); err != nil {
		t.Fatal(err)
	}
	found := false
	for _, c := range tr.Commands {
		if c.Phase != "agent" || c.Step != 6 {
			continue
		}
		found = true
		out, sent := runPytest(t, c.Stdout, c.Stderr, c.ExitCode)
		if !strings.Contains(out, gitError) || !strings.Contains(sent, gitError) {
			t.Errorf("the git error did not reach the model")
		}
		if !strings.Contains(out, "\n[... 544 bytes cut ...]\n") {
			t.Errorf("want marker for 544 bytes; output around the middle: %q", out[headBytes-20:headBytes+40])
		}
	}
	if !found {
		t.Fatal("no agent command for step 6 in the 014 trace")
	}
}

func TestTruncateMarkerCount(t *testing.T) {
	tests := []struct {
		name     string
		s        string
		wantCut  int
		wantHead int // bytes kept at the start
		wantTail int // bytes kept at the end
	}{
		{"one byte over", strings.Repeat("x", maxOutput+1), 1, headBytes, tailBytes},
		{"544 bytes over (014)", strings.Repeat("x", maxOutput+544), 544, headBytes, tailBytes},
		// é is 2 bytes. Its first byte is the last head byte, so the head
		// steps back one byte and keeps the whole é out.
		{"character at the head cut", strings.Repeat("a", headBytes-1) + "é" + strings.Repeat("z", tailBytes+10), 12, headBytes - 1, tailBytes},
		// The tail would start on é's second byte, so it starts one later.
		{"character at the tail cut", strings.Repeat("a", headBytes+10) + "é" + strings.Repeat("z", tailBytes-1), 12, headBytes, tailBytes - 1},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got := truncate(tc.s)
			want := tc.s[:tc.wantHead] + fmt.Sprintf("\n[... %d bytes cut ...]\n", tc.wantCut) + tc.s[len(tc.s)-tc.wantTail:]
			if got != want {
				t.Errorf("truncate differs from head + marker + tail (len got %d, want %d)", len(got), len(want))
			}
			// The bytes cut plus the bytes kept are the whole input.
			if tc.wantCut+tc.wantHead+tc.wantTail != len(tc.s) {
				t.Errorf("cut %d + head %d + tail %d != len %d", tc.wantCut, tc.wantHead, tc.wantTail, len(tc.s))
			}
			if !utf8.ValidString(got) {
				t.Error("result is not valid UTF-8")
			}
		})
	}
}

func TestShortOutputUnchanged(t *testing.T) {
	for _, n := range []int{0, 1, maxOutput - 1, maxOutput} {
		s := strings.Repeat("é", n/2) + strings.Repeat("x", n%2) // n bytes
		if got := truncate(s); got != s {
			t.Errorf("len %d: changed (len %d)", n, len(got))
		}
	}
	// Through the loop: a short run_command result is the exact text.
	out, _ := runPytest(t, "1 passed in 0.01s\n", "", 0)
	if want := "exit_code: 0\n--- stdout ---\n1 passed in 0.01s\n\n--- stderr ---\n"; out != want {
		t.Errorf("output = %q, want %q", out, want)
	}
}

// D26 changed only how tool output is formatted, not what the harness
// tells the model up front. This pins the prompt version of contract A,
// the prompt every run before T5.1 used (see also contracts_test.go).
func TestPromptVersionUnchangedByD26(t *testing.T) {
	const want = "77d9d716f4239fa8b9be66353e4aa88b4c880a2833dd8d9f215c60b449021be7"
	if got := PromptVersion(contracts.MustGet("A").System); got != want {
		t.Errorf("PromptVersion = %s, want %s", got, want)
	}
}

func TestOutputLimits(t *testing.T) {
	c := OutputLimits()
	if c.LimitBytes != 8192 || c.HeadBytes != 4096 || c.TailBytes != 4096 {
		t.Errorf("OutputLimits = %+v", c)
	}
}
