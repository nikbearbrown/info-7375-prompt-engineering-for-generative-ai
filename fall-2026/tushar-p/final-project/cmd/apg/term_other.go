//go:build !darwin && !linux

package main

import "os"

// isTerminal is always false where the harness has no terminal check, so
// the gate always defers there: nothing is exported unattended.
func isTerminal(*os.File) bool { return false }
