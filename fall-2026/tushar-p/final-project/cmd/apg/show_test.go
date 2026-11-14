package main

import (
	"bytes"
	"flag"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"unicode/utf8"

	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// update rewrites the golden files: go test ./cmd/apg -run TestShowGolden -update
// (then read the diff before committing).
var update = flag.Bool("update", false, "rewrite the apg show golden files")

func render(t *testing.T, fixture string, full bool) string {
	t.Helper()
	path := filepath.Join("testdata", "show", fixture)
	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var out bytes.Buffer
	if err := showTrace(&out, b, path, full, false); err != nil {
		t.Fatalf("%s: %v", fixture, err)
	}
	return out.String()
}

// Golden output for each fixture: a PASS run (also with --full), a run
// with denied calls, a mid-run check failure, and a v0 trace.
func TestShowGolden(t *testing.T) {
	cases := []struct {
		fixture, golden string
		full            bool
	}{
		{"pass.json", "pass.golden", false},
		{"pass.json", "pass.full.golden", true},
		{"denied.json", "denied.golden", false},
		{"midrun-fail.json", "midrun-fail.golden", false},
		{"v0.json", "v0.golden", false},
	}
	for _, tc := range cases {
		t.Run(tc.golden, func(t *testing.T) {
			got := render(t, tc.fixture, tc.full)
			golden := filepath.Join("testdata", "show", tc.golden)
			if *update {
				if err := os.WriteFile(golden, []byte(got), 0o644); err != nil {
					t.Fatal(err)
				}
			}
			want, err := os.ReadFile(golden)
			if err != nil {
				t.Fatalf("%v (run with -update to create it)", err)
			}
			if got != string(want) {
				t.Errorf("output differs from %s (run with -update, then read the diff):\n%s", golden, got)
			}
			// Readable in an 80-column terminal, and plain text.
			for i, line := range strings.Split(got, "\n") {
				if n := utf8.RuneCountInString(line); n > width {
					t.Errorf("line %d is %d columns: %q", i+1, n, line)
				}
			}
			if strings.Contains(got, "\x1b[") {
				t.Error("colour codes in output that is not a terminal")
			}
		})
	}
}

// The fixtures are valid v1 traces (and the v0 one is not).
func TestShowFixturesDecode(t *testing.T) {
	for _, f := range []string{"pass.json", "denied.json", "midrun-fail.json"} {
		file, err := os.Open(filepath.Join("testdata", "show", f))
		if err != nil {
			t.Fatal(err)
		}
		if _, err := trace.Decode(file); err != nil {
			t.Errorf("%s: %v", f, err)
		}
		file.Close()
	}
}

// Output is cut to 20 lines, saying how many were cut; --full shows all.
func TestShowCutVersusFull(t *testing.T) {
	cut, full := render(t, "pass.json", false), render(t, "pass.json", true)
	if !strings.Contains(cut, "| line 20 of calc/ops.py") || strings.Contains(cut, "| line 21 of calc/ops.py") ||
		!strings.Contains(cut, "… 30 more lines (use --full)") {
		t.Errorf("cut output wrong:\n%s", cut)
	}
	if !strings.Contains(full, "| line 50 of calc/ops.py") || strings.Contains(full, "more lines (use --full)") {
		t.Errorf("--full output wrong:\n%s", full)
	}
	// --full also lists the harness commands with their output.
	if !strings.Contains(full, "[harness] fingerprint:") || strings.Contains(full, "(use --full to list them") {
		t.Error("--full should list the harness commands")
	}
}

// A run ID is found in traces/, then evidence/traces/; a path is used as
// is; anything else is an error.
func TestShowFindTrace(t *testing.T) {
	dir := t.TempDir()
	p := filepath.Join(dir, "20261113T120000Z-abcd1234.json")
	if err := os.WriteFile(p, []byte("{}"), 0o644); err != nil {
		t.Fatal(err)
	}
	if got, err := findTrace("20261113T120000Z-abcd1234", dir); err != nil || got != p {
		t.Errorf("run ID in traces dir: %q, %v", got, err)
	}
	if got, err := findTrace(p, "nowhere"); err != nil || got != p {
		t.Errorf("path: %q, %v", got, err)
	}
	// From cmd/apg, evidence/traces is not reachable, so a missing ID fails.
	for _, bad := range []string{"20261113T999999Z-missing", "../etc/passwd", "a b"} {
		if _, err := findTrace(bad, dir); err == nil {
			t.Errorf("findTrace(%q) should fail", bad)
		}
	}
}

// An invalid v1 trace is refused, with the decode error, and exit 2.
func TestShowInvalidTrace(t *testing.T) {
	b, err := os.ReadFile(filepath.Join("testdata", "show", "pass.json"))
	if err != nil {
		t.Fatal(err)
	}
	bad := strings.Replace(string(b), `"pod":`, `"surprise": 1, "pod":`, 1)
	p := filepath.Join(t.TempDir(), "bad.json")
	if err := os.WriteFile(p, []byte(bad), 0o644); err != nil {
		t.Fatal(err)
	}
	var stdout, stderr bytes.Buffer
	if code := showMain([]string{p}, &stdout, &stderr); code != exitError || !strings.Contains(stderr.String(), "unknown field") || stdout.Len() != 0 {
		t.Errorf("exit %d, stdout %q, stderr %q", code, stdout.String(), stderr.String())
	}
}

// Every evidence trace (v0 and v1) prints without error.
func TestShowEvidenceTraces(t *testing.T) {
	paths, err := filepath.Glob(filepath.Join("..", "..", "evidence", "traces", "*.json"))
	if err != nil || len(paths) == 0 {
		t.Fatalf("no evidence traces: %v", err)
	}
	for _, p := range paths {
		b, err := os.ReadFile(p)
		if err != nil {
			t.Fatal(err)
		}
		for _, full := range []bool{false, true} {
			var out bytes.Buffer
			if err := showTrace(&out, b, p, full, false); err != nil {
				t.Errorf("%s (full %v): %v", filepath.Base(p), full, err)
			}
			for _, line := range strings.Split(out.String(), "\n") {
				if utf8.RuneCountInString(line) > width {
					t.Errorf("%s: line over %d columns: %q", filepath.Base(p), width, line)
					break
				}
			}
		}
	}
}
