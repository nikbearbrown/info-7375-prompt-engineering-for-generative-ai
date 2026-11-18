// Package contracts holds the prompt contracts compared in T5.1 (PLAN.md).
// A prompt contract is the system prompt the agent gets, and nothing else:
// the task-message template, the tool definitions, and the not-complete
// note live in internal/loop and are the same for every contract.
//
// Not to be confused with a task's contract.json (the task's goal, tools,
// and limits). To keep the two apart, traces and the eval log call this one
// "prompt_contract".
//
// Each system prompt is a text file in this directory, embedded into the
// binary when it is built, so the bytes sent are exactly the file's bytes.
// A and B are frozen (D30): changing a file changes the prompt version.
package contracts

import (
	_ "embed" // the blank import enables the //go:embed lines below
	"fmt"
	"strings"
)

// Default is the contract apg run and apg eval use without --contract.
const Default = "A"

// The //go:embed line fills the string below it with the file's contents
// at build time. Files must be in this package's directory or below it.

//go:embed A-system.txt
var systemA string

//go:embed B-system.txt
var systemB string

// Contract is one prompt contract.
type Contract struct {
	Name   string // "A" or "B"
	System string // the system prompt, byte for byte from <Name>-system.txt
}

// all is every contract, in name order.
var all = []Contract{
	{Name: "A", System: systemA}, // the system prompt used since 10abc03 (T2.3)
	{Name: "B", System: systemB}, // Tushar's process-oriented prompt (T5.1, D30)
}

// Names returns the contract names, in order.
func Names() []string {
	names := make([]string, len(all))
	for i, c := range all {
		names[i] = c.Name
	}
	return names
}

// Get returns the contract with this name, or an error naming the valid ones.
func Get(name string) (Contract, error) {
	for _, c := range all {
		if c.Name == name {
			return c, nil
		}
	}
	return Contract{}, fmt.Errorf("unknown prompt contract %q (want %s)", name, strings.Join(Names(), " or "))
}

// MustGet is Get for names fixed in code (such as Default); an unknown name
// is a bug, so it panics.
func MustGet(name string) Contract {
	c, err := Get(name)
	if err != nil {
		panic(err)
	}
	return c
}
