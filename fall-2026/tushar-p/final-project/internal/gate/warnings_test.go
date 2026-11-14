package gate

import (
	"context"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"testing"
)

// Every binary or non-text file in the diff gets a WARNING line with its
// path and size, inside the diff bytes (so the hash covers it).
func TestDiffWarnsAboutNonTextFiles(t *testing.T) {
	orig := writeTree(t, map[string]string{
		"img.bin": "\x00\x01",
		"old.bin": "\x00gone",
	})
	cur := writeTree(t, map[string]string{
		"img.bin":    "\x00\x01\x02\x03",
		"latin1.txt": "caf\xe9\n", // not valid UTF-8
		"ok.txt":     "plain text\n",
	})
	if err := os.Symlink("/etc/passwd", filepath.Join(cur, "link")); err != nil {
		t.Fatal(err)
	}
	d, err := Diff(orig, cur)
	if err != nil {
		t.Fatal(err)
	}
	s := string(d)
	for _, w := range []string{
		"WARNING: non-text file b/img.bin, 4 bytes (was 2); its content is not in this patch\n",
		"WARNING: non-text file b/latin1.txt, 5 bytes (new file); its content is not in this patch\n",
		"WARNING: non-text file a/old.bin, deleted, was 5 bytes; its content is not in this patch\n",
		"WARNING: non-text file b/link (symlink), 11 bytes; a symlink is not in this patch\n",
		"+plain text\n",
	} {
		if !strings.Contains(s, w) {
			t.Errorf("diff lacks %q:\n%s", w, s)
		}
	}
	if strings.Contains(s, "WARNING: non-text file b/ok.txt") {
		t.Errorf("a text file got a warning:\n%s", s)
	}
}

// The gate repeats the WARNING lines after the diff, next to the result,
// and lists "warnings" in what was shown.
func TestGateRepeatsWarnings(t *testing.T) {
	c, out := cfg(t, "refuse\n", true)
	calls := 0
	diff := "WARNING: non-text file b/x.bin, 3 bytes (new file); its content is not in this patch\nBinary files /dev/null and b/x.bin differ\n"
	g := Run(context.Background(), c, "run1", summary, builds(&calls, diff))
	shown := out.String()
	end := strings.Index(shown, "==== end of diff ====")
	if end < 0 || !strings.Contains(shown[end:], "WARNING: non-text file b/x.bin, 3 bytes") {
		t.Errorf("warning not repeated after the diff:\n%s", shown)
	}
	if !slices.Contains(g.Shown, "warnings") || slices.Contains(Shown, "warnings") {
		t.Errorf("shown = %v (package Shown = %v)", g.Shown, Shown)
	}
}

// Eval (batch) mode defers even when stdin is a terminal and the answer
// would be "approve": nothing is shown, nothing is approved.
func TestBatchModeAlwaysDefers(t *testing.T) {
	c, out := cfg(t, "approve\n", true) // Interactive: true, as if stdin were a terminal
	c.Batch = true
	calls := 0
	g := Run(context.Background(), c, "run1", summary, builds(&calls, patch))
	if g.Decision != DecisionDeferred || !g.Batch || len(g.Shown) != 0 || !strings.Contains(g.Reason, "eval mode") {
		t.Fatalf("gate = %+v, want deferred in eval mode, nothing shown", g)
	}
	if out.Len() != 0 {
		t.Errorf("printed in batch mode: %q", out.String())
	}
	if got := files(t, c.OutDir); slices.Contains(got, "run1/approved.patch") || !slices.Contains(got, "run1/pending.patch") {
		t.Errorf("files = %v, want pending only", got)
	}
}
