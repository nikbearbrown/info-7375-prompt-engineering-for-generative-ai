//go:build darwin || linux

package main

import (
	"os"
	"syscall"
	"unsafe"
)

// isTerminal reports whether f is a terminal. It asks the kernel for the
// terminal's settings (the ioctl behind tcgetattr), which succeeds only on
// a terminal. The file mode alone cannot tell: /dev/null is a character
// device too, but not a terminal. (Found in T2.5: the T2.4 check used the
// file mode and took /dev/null for a terminal.)
//
// unsafe.Pointer hands the kernel the address of t to fill in; that is
// the only use of package unsafe here. A pseudo-terminal counts as a
// terminal (docs/03: the gate trusts whoever types at it).
func isTerminal(f *os.File) bool {
	var t syscall.Termios
	_, _, errno := syscall.Syscall(syscall.SYS_IOCTL, f.Fd(), ioctlGetTermios, uintptr(unsafe.Pointer(&t)))
	return errno == 0
}
