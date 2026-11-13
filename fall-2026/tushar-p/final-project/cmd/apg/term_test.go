package main

import (
	"os"
	"testing"
)

// None of these is a terminal, so the gate must defer with any of them on
// stdin. /dev/null is the case the T2.4 check got wrong: it is a
// character device, but not a terminal.
func TestNotTerminals(t *testing.T) {
	null, err := os.Open(os.DevNull)
	if err != nil {
		t.Fatal(err)
	}
	defer null.Close()
	r, w, err := os.Pipe() // os.Pipe returns both ends of a pipe
	if err != nil {
		t.Fatal(err)
	}
	defer r.Close()
	defer w.Close()
	file, err := os.CreateTemp(t.TempDir(), "stdin")
	if err != nil {
		t.Fatal(err)
	}
	defer file.Close()
	for name, f := range map[string]*os.File{"/dev/null": null, "pipe": r, "regular file": file} {
		if isTerminal(f) {
			t.Errorf("%s reported as a terminal", name)
		}
	}
}
