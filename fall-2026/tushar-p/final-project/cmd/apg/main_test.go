package main

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
)

func TestParseRunArgs(t *testing.T) {
	tests := []struct {
		name        string
		args        []string
		wantTask    string
		wantNoAgent bool
		wantErr     bool
	}{
		{"flag after task", []string{"001", "--no-agent"}, "001", true, false},
		{"flag before task", []string{"--no-agent", "001"}, "001", true, false},
		{"no flag", []string{"001"}, "001", false, false},
		{"no task", []string{"--no-agent"}, "", true, true},
		{"two tasks", []string{"001", "002"}, "", false, true},
		{"unknown flag", []string{"001", "--fast"}, "", false, true},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			o, err := parseRunArgs(tc.args)
			if (err != nil) != tc.wantErr {
				t.Fatalf("err = %v, wantErr %v", err, tc.wantErr)
			}
			if err == nil && (o.task != tc.wantTask || o.noAgent != tc.wantNoAgent) {
				t.Errorf("got task=%q noAgent=%v", o.task, o.noAgent)
			}
		})
	}
}

// makeTask creates tasksDir/<id> with repo/, check.sh, and a contract.
func makeTask(t *testing.T, tasksDir, id, contractID string) {
	t.Helper()
	dir := filepath.Join(tasksDir, id)
	if err := os.MkdirAll(filepath.Join(dir, "repo"), 0o755); err != nil {
		t.Fatal(err)
	}
	files := map[string]string{
		"check.sh":      "exit 0\n",
		"contract.json": `{"id": "` + contractID + `", "goal": "g", "allowed_tools": ["read_file"], "max_steps": 3}`,
	}
	for name, body := range files {
		if err := os.WriteFile(filepath.Join(dir, name), []byte(body), 0o644); err != nil {
			t.Fatal(err)
		}
	}
}

func TestFindTask(t *testing.T) {
	root := t.TempDir()
	makeTask(t, root, "001-fix-function", "001-fix-function")
	makeTask(t, root, "002-wrong-id", "002-something-else")
	makeTask(t, root, "003-a", "003-a")
	makeTask(t, root, "003-b", "003-b")

	tk, err := findTask(root, "001")
	if err != nil {
		t.Fatal(err)
	}
	if tk.ID != "001-fix-function" || tk.Short != "001" || tk.Repo != filepath.Join(root, "001-fix-function", "repo") {
		t.Errorf("unexpected task: %+v", tk)
	}

	for _, short := range []string{"002", "003", "004", "../x", "*", "01"} {
		if _, err := findTask(root, short); err == nil {
			t.Errorf("findTask(%q) should fail", short)
		}
	}
}

func TestRealTask001(t *testing.T) {
	// The real task directory in this repo must pass findTask.
	tk, err := findTask(filepath.Join("..", "..", "tasks"), "001")
	if err != nil {
		t.Fatal(err)
	}
	if tk.MaxSteps != 10 || len(tk.AllowedTools) != 3 || tk.Goal == "" {
		t.Errorf("contract not loaded: %+v", tk)
	}
}

func TestFindTaskRejectsIncompleteContracts(t *testing.T) {
	bad := map[string]string{
		"no goal":    `{"id": "001-x", "allowed_tools": ["read_file"], "max_steps": 3}`,
		"no tools":   `{"id": "001-x", "goal": "g", "max_steps": 3}`,
		"zero steps": `{"id": "001-x", "goal": "g", "allowed_tools": ["read_file"], "max_steps": 0}`,
	}
	for name, contract := range bad {
		t.Run(name, func(t *testing.T) {
			root := t.TempDir()
			makeTask(t, root, "001-x", "001-x")
			if err := os.WriteFile(filepath.Join(root, "001-x", "contract.json"), []byte(contract), 0o644); err != nil {
				t.Fatal(err)
			}
			if _, err := findTask(root, "001"); err == nil {
				t.Error("incomplete contract should be rejected")
			}
		})
	}
}

func TestRemoteExit(t *testing.T) {
	ok := []sandbox.Result{
		{ExitCode: 0},
		{ExitCode: 1, Stderr: "command terminated with exit code 1\n"},
	}
	for _, r := range ok {
		if err := remoteExit(r); err != nil {
			t.Errorf("%+v: unexpected error %v", r, err)
		}
	}
	gone := sandbox.Result{ExitCode: 1, Stderr: `Error from server (NotFound): pods "apg-x" not found`}
	if err := remoteExit(gone); err == nil {
		t.Error("a kubectl failure must not count as the check's exit code")
	}
}
