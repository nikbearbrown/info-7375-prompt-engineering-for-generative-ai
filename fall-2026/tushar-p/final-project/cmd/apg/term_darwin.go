package main

import "syscall"

// ioctlGetTermios is the "get terminal settings" request on macOS.
const ioctlGetTermios = syscall.TIOCGETA
