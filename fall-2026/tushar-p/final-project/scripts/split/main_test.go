package main

import (
	"bytes"
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

// The committed tasks/split.json is exactly what the rule and its seed
// give for the current task directories: anyone can redraw it and get the
// same split.
func TestSplitFileMatchesDraw(t *testing.T) {
	path := filepath.Join("..", "..", "tasks", "split.json")
	b, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		t.Skip("tasks/split.json not drawn yet")
	}
	if err != nil {
		t.Fatal(err)
	}
	var got Split
	dec := json.NewDecoder(bytes.NewReader(b))
	dec.DisallowUnknownFields()
	if err := dec.Decode(&got); err != nil {
		t.Fatal(err)
	}
	ids, err := taskIDs(filepath.Join("..", "..", "tasks"))
	if err != nil {
		t.Fatal(err)
	}
	want, err := Draw(got.Seed, ids, io.Discard)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("split.json does not match the draw for seed %d:\n got %+v\nwant %+v", got.Seed, got, want)
	}
	// Every task is in exactly one of dev and held_out.
	seen := map[string]int{}
	for _, id := range append(append([]string{}, got.Dev...), got.HeldOut...) {
		seen[id]++
	}
	for _, id := range ids {
		if seen[id] != 1 {
			t.Errorf("task %s appears %d times", id, seen[id])
		}
	}
}

// The same seed always gives the same draw; the rule's group sizes hold.
func TestDraw(t *testing.T) {
	var ids []string
	for _, id := range []string{"001-a", "002-a", "003-a", "004-a", "005-a", "006-a", "007-a", "008-a", "009-a", "010-a", "011-a", "012-a", "013-a", "014-a", "015-a", "016-a"} {
		ids = append(ids, id)
	}
	a, err := Draw(42, ids, io.Discard)
	if err != nil {
		t.Fatal(err)
	}
	b, _ := Draw(42, ids, io.Discard)
	if !reflect.DeepEqual(a, b) {
		t.Error("the same seed gave two different draws")
	}
	if len(a.Dev) != 5+2+2 || len(a.HeldOut) != 4+3 {
		t.Errorf("dev %d held_out %d, want 9 and 7", len(a.Dev), len(a.HeldOut))
	}
	if _, err := Draw(42, append(ids, "017-extra"), io.Discard); err == nil {
		t.Error("a task outside every group should be an error")
	}
}

// write never overwrites an existing split.
func TestWriteRefusesToOverwrite(t *testing.T) {
	path := filepath.Join(t.TempDir(), "split.json")
	if err := write(path, Split{Seed: 1}); err != nil {
		t.Fatal(err)
	}
	if err := write(path, Split{Seed: 2}); err == nil {
		t.Error("second write should fail: the split is frozen")
	}
}
