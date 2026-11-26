"""Runs a Python server script with the network blocked: every socket raises before it can connect.

    python3 -B scripts/run_blocked.py path/to/server.py

Used to check another server's "fetches nothing live" by behaviour, not only by reading its imports (EVAL-SERVERS.md).
"""
import runpy
import socket
import sys


def refuse(*args, **kwargs):
    raise OSError("network blocked by run_blocked.py")


socket.socket = refuse
socket.create_connection = refuse
socket.getaddrinfo = refuse

target = sys.argv[1]
sys.argv = [target] + sys.argv[2:]
runpy.run_path(target, run_name="__main__")
