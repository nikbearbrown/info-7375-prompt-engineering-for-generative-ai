package main

import (
	"bufio"
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// taskDirs returns every tasks/NNN-* directory.
func taskDirs(t *testing.T) []string {
	t.Helper()
	dirs, err := filepath.Glob(filepath.Join("..", "..", "tasks", "[0-9][0-9][0-9]-*"))
	if err != nil || len(dirs) < 5 {
		t.Fatalf("want at least 5 tasks, found %d (%v)", len(dirs), err)
	}
	return dirs
}

// protected reads the contract's required_output.unchanged_files.
func protected(t *testing.T, dir string) []string {
	t.Helper()
	b, err := os.ReadFile(filepath.Join(dir, "contract.json"))
	if err != nil {
		t.Fatal(err)
	}
	var c struct {
		RequiredOutput struct {
			UnchangedFiles []string `json:"unchanged_files"`
		} `json:"required_output"`
	}
	if err := json.Unmarshal(b, &c); err != nil {
		t.Fatal(err)
	}
	if len(c.RequiredOutput.UnchangedFiles) == 0 {
		t.Fatalf("%s: contract lists no unchanged_files", dir)
	}
	return c.RequiredOutput.UnchangedFiles
}

// patchedFiles lists the paths a unified diff touches (its ---/+++ lines).
func patchedFiles(patch []byte) []string {
	var out []string
	sc := bufio.NewScanner(bytes.NewReader(patch))
	for sc.Scan() {
		line := sc.Text()
		for _, prefix := range []string{"--- a/", "+++ b/"} {
			if strings.HasPrefix(line, prefix) {
				out = append(out, strings.TrimPrefix(line, prefix))
			}
		}
	}
	return out
}

// Every task is complete and consistent: the contract loads with budget
// fields, check.sh pins the SHA-256 of each protected test file, and the
// reference patch (outside repo/, so it never reaches the pod) touches no
// protected file.
func TestTaskFiles(t *testing.T) {
	for _, dir := range taskDirs(t) {
		id := filepath.Base(dir)
		t.Run(id, func(t *testing.T) {
			tk, err := findTask(filepath.Dir(dir), id[:3])
			if err != nil {
				t.Fatal(err)
			}
			if len(tk.FromContract) != 5 {
				t.Errorf("contract sets %v, want all five budget fields", tk.FromContract)
			}
			check, err := os.ReadFile(filepath.Join(dir, "check.sh"))
			if err != nil {
				t.Fatal(err)
			}
			patch, err := os.ReadFile(filepath.Join(dir, "reference.patch"))
			if err != nil {
				t.Fatal(err)
			}
			touched := patchedFiles(patch)
			if len(touched) == 0 {
				t.Error("reference.patch touches no file")
			}
			for _, f := range protected(t, dir) {
				b, err := os.ReadFile(filepath.Join(dir, "repo", f))
				if err != nil {
					t.Fatal(err)
				}
				sum := sha256.Sum256(b)
				if !bytes.Contains(check, []byte(`EXPECTED="`+hex.EncodeToString(sum[:])+`"`)) {
					t.Errorf("check.sh does not pin the sha256 of %s", f)
				}
				for _, p := range touched {
					if p == f || strings.HasPrefix(p, "tests/") {
						t.Errorf("reference.patch touches %s", p)
					}
				}
			}
			if _, err := os.Stat(filepath.Join(dir, "repo", "reference.patch")); err == nil {
				t.Error("reference.patch is inside repo/: it would reach the pod")
			}
		})
	}
}

// runCheck runs a task's check.sh in apg-sandbox:dev with repo mounted
// read-only at /workspace and no network, and returns its exit code.
func runCheckInImage(t *testing.T, repo, check string) (int, string) {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()
	cmd := exec.CommandContext(ctx, "docker", "run", "--rm", "--network", "none",
		"-v", repo+":/workspace:ro", "-v", check+":/check/check.sh:ro",
		"apg-sandbox:dev", "bash", "/check/check.sh")
	out, err := cmd.CombinedOutput()
	if exitErr, ok := err.(*exec.ExitError); ok {
		return exitErr.ExitCode(), string(out)
	}
	if err != nil {
		t.Fatalf("docker run: %v: %s", err, out)
	}
	return 0, string(out)
}

// copyTree copies src to a new temp dir and returns it.
func copyTree(t *testing.T, src string) string {
	t.Helper()
	dst := t.TempDir()
	err := filepath.WalkDir(src, func(p string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel(src, p)
		if d.IsDir() {
			return os.MkdirAll(filepath.Join(dst, rel), 0o755)
		}
		b, err := os.ReadFile(p)
		if err != nil {
			return err
		}
		return os.WriteFile(filepath.Join(dst, rel), b, 0o644)
	})
	if err != nil {
		t.Fatal(err)
	}
	return dst
}

// Each task's check, run in the real sandbox image: it must FAIL on the
// untouched repo and PASS on the repo with reference.patch applied. The
// mount is read-only, so this also shows the check writes nothing into
// /workspace.
func TestChecksAgainstReferencePatches(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping docker test in -short mode")
	}
	for _, tool := range []string{"docker", "git"} {
		if _, err := exec.LookPath(tool); err != nil {
			t.Skipf("%s not installed", tool)
		}
	}
	if err := exec.Command("docker", "image", "inspect", "apg-sandbox:dev").Run(); err != nil {
		t.Skip("image apg-sandbox:dev not built")
	}
	for _, dir := range taskDirs(t) {
		id := filepath.Base(dir)
		t.Run(id, func(t *testing.T) {
			abs, _ := filepath.Abs(dir)
			check := filepath.Join(abs, "check.sh")

			untouched := copyTree(t, filepath.Join(abs, "repo"))
			if code, out := runCheckInImage(t, untouched, check); code == 0 {
				t.Errorf("check passed on the untouched repo:\n%s", out)
			}

			fixed := copyTree(t, filepath.Join(abs, "repo"))
			apply := exec.Command("git", "apply", filepath.Join(abs, "reference.patch"))
			apply.Dir = fixed
			if out, err := apply.CombinedOutput(); err != nil {
				t.Fatalf("git apply reference.patch: %v: %s", err, out)
			}
			if code, out := runCheckInImage(t, fixed, check); code != 0 {
				t.Errorf("check failed (exit %d) with reference.patch applied:\n%s", code, out)
			}
		})
	}
}
