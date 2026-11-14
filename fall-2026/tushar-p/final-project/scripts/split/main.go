// Command split draws the dev / held-out split of the task suite (PLAN.md
// T3.2) from a seed, prints the draw, and writes tasks/split.json.
//
//	go run ./scripts/split -seed 42
//
// The rule (Tushar's decision):
//   - 001-005 go to dev: the model already ran on them (Nov 13, 2026).
//   - 006-011: 2 to dev, 4 to held-out.
//   - 012-016: 2 to dev, 3 to held-out.
//
// The draw, within each group: rank the tasks by sha256("<seed>:<task id>")
// in ascending hex order, and put the first k in dev. That is a fixed
// shuffle anyone can recompute by hand, for example with
// printf '42:006-ledger-cents' | shasum -a 256
// so the split depends only on the seed, not on a Go version's random
// number generator.
//
// split.json is frozen once committed (CLAUDE.md): this command refuses to
// overwrite it.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strconv"
)

// group is one part of the rule: tasks first..last, k of them to dev.
type group struct {
	First, Last int
	Dev         int
	Why         string
}

var rule = []group{
	{1, 5, 5, "the model already ran on them (Nov 13, 2026), so they cannot be held out"},
	{6, 11, 2, "harder normal tasks: 2 to dev, 4 held out"},
	{12, 16, 2, "deliberate failure cases: 2 to dev, 3 held out"},
}

// Split is the content of tasks/split.json.
type Split struct {
	Seed    int64       `json:"seed"`
	Method  string      `json:"method"`
	Rule    []ruleEntry `json:"rule"`
	Dev     []string    `json:"dev"`
	HeldOut []string    `json:"held_out"`
}

type ruleEntry struct {
	Tasks   string   `json:"tasks"`
	Dev     []string `json:"dev"`
	HeldOut []string `json:"held_out"`
	Why     string   `json:"why"`
}

const method = `within each group, rank the tasks by sha256("<seed>:<task id>") in ascending hex order; the first k go to dev`

func main() {
	seed := flag.Int64("seed", -1, "the seed (required)")
	tasksDir := flag.String("tasks", "tasks", "tasks directory")
	out := flag.String("out", filepath.Join("tasks", "split.json"), "where to write the split")
	flag.Parse()
	if *seed < 0 {
		fmt.Fprintln(os.Stderr, "split: -seed is required")
		os.Exit(2)
	}
	ids, err := taskIDs(*tasksDir)
	if err != nil {
		fmt.Fprintln(os.Stderr, "split:", err)
		os.Exit(1)
	}
	s, err := Draw(*seed, ids, os.Stdout)
	if err != nil {
		fmt.Fprintln(os.Stderr, "split:", err)
		os.Exit(1)
	}
	if err := write(*out, s); err != nil {
		fmt.Fprintln(os.Stderr, "split:", err)
		os.Exit(1)
	}
	fmt.Printf("\nwrote %s\n", *out)
}

// taskIDs lists the task directories (NNN-name) in dir, sorted.
func taskIDs(dir string) ([]string, error) {
	matches, err := filepath.Glob(filepath.Join(dir, "[0-9][0-9][0-9]-*"))
	if err != nil {
		return nil, err
	}
	var ids []string
	for _, m := range matches {
		if fi, err := os.Stat(m); err == nil && fi.IsDir() {
			ids = append(ids, filepath.Base(m))
		}
	}
	sort.Strings(ids)
	return ids, nil
}

// rank is the hex SHA-256 of "<seed>:<id>"; the draw sorts by it.
func rank(seed int64, id string) string {
	sum := sha256.Sum256([]byte(strconv.FormatInt(seed, 10) + ":" + id))
	return hex.EncodeToString(sum[:])
}

// Draw applies the rule to ids and prints each group's ranking to w. Every
// task must fall in exactly one group, and each group must have enough
// tasks.
func Draw(seed int64, ids []string, w io.Writer) (Split, error) {
	s := Split{Seed: seed, Method: method, Dev: []string{}, HeldOut: []string{}}
	used := map[string]bool{}
	for _, g := range rule {
		var members []string
		for _, id := range ids {
			n, err := strconv.Atoi(id[:3])
			if err == nil && n >= g.First && n <= g.Last {
				members = append(members, id)
				used[id] = true
			}
		}
		if len(members) != g.Last-g.First+1 || g.Dev > len(members) {
			return Split{}, fmt.Errorf("group %03d-%03d: found %d tasks %v", g.First, g.Last, len(members), members)
		}
		// Sort the members by their rank. sort.Slice takes a "less"
		// function comparing two positions.
		sort.Slice(members, func(i, j int) bool { return rank(seed, members[i]) < rank(seed, members[j]) })

		e := ruleEntry{Tasks: fmt.Sprintf("%03d-%03d", g.First, g.Last), Dev: []string{}, HeldOut: []string{}, Why: g.Why}
		fmt.Fprintf(w, "tasks %s (%d to dev): %s\n", e.Tasks, g.Dev, g.Why)
		for i, id := range members {
			where := "held_out"
			if i < g.Dev {
				where = "dev"
				e.Dev = append(e.Dev, id)
			} else {
				e.HeldOut = append(e.HeldOut, id)
			}
			fmt.Fprintf(w, "  %d. sha256(%q) = %s...  -> %s\n", i+1, fmt.Sprintf("%d:%s", seed, id), rank(seed, id)[:16], where)
		}
		sort.Strings(e.Dev)
		sort.Strings(e.HeldOut)
		s.Dev = append(s.Dev, e.Dev...)
		s.HeldOut = append(s.HeldOut, e.HeldOut...)
		s.Rule = append(s.Rule, e)
	}
	for _, id := range ids {
		if !used[id] {
			return Split{}, fmt.Errorf("task %s is in no group of the rule", id)
		}
	}
	sort.Strings(s.Dev)
	sort.Strings(s.HeldOut)
	fmt.Fprintf(w, "\ndev (%d):      %v\nheld_out (%d): %v\n", len(s.Dev), s.Dev, len(s.HeldOut), s.HeldOut)
	return s, nil
}

// write writes s to path as indented JSON. It never overwrites: the split
// is frozen once committed.
func write(path string, s Split) error {
	// An Encoder, not json.MarshalIndent, so that "<" and ">" in the method
	// text stay readable instead of becoming \u003c and \u003e.
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	enc.SetIndent("", "  ")
	if err := enc.Encode(s); err != nil { // Encode adds the final newline
		return err
	}
	b := buf.Bytes()
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o644)
	if errors.Is(err, os.ErrExist) {
		return fmt.Errorf("%s already exists: the split is frozen, it is never redrawn", path)
	}
	if err != nil {
		return err
	}
	if _, err := f.Write(b); err != nil {
		f.Close()
		return err
	}
	return f.Close()
}
