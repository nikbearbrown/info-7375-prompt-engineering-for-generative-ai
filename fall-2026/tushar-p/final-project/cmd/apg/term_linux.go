package main

import "syscall"

// ioctlGetTermios is the "get terminal settings" request on Linux.
const ioctlGetTermios = syscall.TCGETS
