package loop

import (
	"go/parser"
	"go/token"
	"path/filepath"
	"slices"
	"strconv"
	"strings"
	"testing"
)

// The agent has no tool that reaches the gate: the loop offers exactly the
// three file and command tools.
func TestAgentToolsAreOnlyTheThree(t *testing.T) {
	var names []string
	for name := range toolDefs {
		names = append(names, name)
	}
	slices.Sort(names)
	if strings.Join(names, " ") != "read_file run_command write_file" {
		t.Errorf("agent tools = %v", names)
	}
}

// Neither the loop nor the policy imports the gate, so no agent action can
// call it. ImportsOnly makes the parser stop after the import lines.
func TestLoopAndPolicyDoNotImportGate(t *testing.T) {
	for _, dir := range []string{".", "../policy"} {
		paths, err := filepath.Glob(filepath.Join(dir, "*.go"))
		if err != nil || len(paths) == 0 {
			t.Fatalf("no Go files in %s: %v", dir, err)
		}
		for _, p := range paths {
			f, err := parser.ParseFile(token.NewFileSet(), p, nil, parser.ImportsOnly)
			if err != nil {
				t.Fatal(err)
			}
			for _, imp := range f.Imports {
				path, _ := strconv.Unquote(imp.Path.Value) // the import path without its quotes
				if strings.HasSuffix(path, "/internal/gate") {
					t.Errorf("%s imports %s", p, path)
				}
			}
		}
	}
}
