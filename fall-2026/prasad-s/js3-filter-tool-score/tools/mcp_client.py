"""A minimal scripted MCP client over stdio, for probing any stdio MCP server (JS3 brief, Chapter 8).

    python3.13 tools/mcp_client.py --out PATH [--call NAME --args JSON] [--timeout SECONDS] -- <server command...>

It starts the server command, sends initialize, notifications/initialized and
tools/list (following nextCursor), then the optional tools/call, and saves
every line in both directions, unaltered (without its line break), to PATH as
{"utc", "direction", "line"} records, the transcript format of
tools/mcp_server.py. It refuses to overwrite PATH. It prints the server's tool
list and the call's result.

To get along with servers it did not write, it answers a server's ping with
an empty result and any other server request with "Method not found", skips
server notifications, accepts a batch (an array) of messages, and notes a
non-JSON line from the server on stderr instead of stopping. It asks for
protocol version 2025-11-25, the newest with the initialize handshake, and
goes on with whatever version the server answers, with a note on stderr if it
is not one it knows. When it is done it closes the server's stdin, waits, and
ends the process if it does not exit.

Exit status: 0 when the exchange completed (a tool result with isError true
still counts), 1 when it did not (no answer, a JSON-RPC error, PATH exists),
2 for bad arguments. Standard library only; it imports nothing from this
project, so it can be copied and used alone.
"""

import argparse
import json
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

CLIENT_VERSION = "2025-11-25"  # the newest MCP version with the initialize handshake
KNOWN_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
CLIENT_INFO = {"name": "js3-mcp-client", "version": "1.0.0"}
MAX_PAGES = 100  # tools/list pages followed before giving up


class ClientError(Exception):
    """The exchange could not be completed."""


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class Transcript:
    def __init__(self, path):
        self.handle = open(path, "x", encoding="utf-8")  # "x": never overwrite

    def record(self, direction, line):
        self.handle.write(json.dumps({"utc": utc_now(), "direction": direction, "line": line}) + "\n")
        self.handle.flush()

    def close(self):
        self.handle.close()


def _read_lines(stream, lines):
    for raw in iter(stream.readline, b""):
        lines.put(raw)
    lines.put(None)  # end of the server's stdout


class Session:
    def __init__(self, process, transcript, timeout, err):
        self.process = process
        self.transcript = transcript
        self.timeout = timeout
        self.err = err
        self.next_id = 1
        self.lines = queue.Queue()
        threading.Thread(target=_read_lines, args=(process.stdout, self.lines), daemon=True).start()

    def send(self, message):
        line = json.dumps(message, separators=(",", ":"))
        self.transcript.record("client->server", line)
        try:
            self.process.stdin.write(line.encode("ascii") + b"\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise ClientError("the server's stdin is closed") from exc

    def notify(self, method, params=None):
        self.send({"jsonrpc": "2.0", "method": method, **({} if params is None else {"params": params})})

    def request(self, method, params):
        """Send a request and wait for its response, handling whatever else the server sends meanwhile."""
        request_id = self.next_id
        self.next_id += 1
        self.send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ClientError(f"no response to {method} within {self.timeout:g} s")
            try:
                raw = self.lines.get(timeout=remaining)
            except queue.Empty:
                raise ClientError(f"no response to {method} within {self.timeout:g} s") from None
            if raw is None:
                self.lines.put(None)  # keep the end marker for close()
                raise ClientError(f"the server closed its stdout before answering {method}")
            for message in self.receive(raw):
                if message.get("id") == request_id and ("result" in message or "error" in message):
                    return message

    def receive(self, raw, answer=True):
        """Record one line from the server; return the responses in it, after answering its requests."""
        line = raw[:-1] if raw.endswith(b"\n") else raw
        self.transcript.record("server->client", line.decode("utf-8", "surrogateescape"))
        if not line.strip():
            return []
        try:
            parsed = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            self.err.write("note: the server wrote a line to stdout that is not JSON (recorded in the transcript)\n")
            return []
        responses = []
        for message in parsed if isinstance(parsed, list) else [parsed]:
            if not isinstance(message, dict):
                self.err.write("note: the server sent a JSON value that is not a message object\n")
            elif "method" in message and "id" in message:  # a request from the server
                if answer:
                    if message["method"] == "ping":
                        self.send({"jsonrpc": "2.0", "id": message["id"], "result": {}})
                    else:
                        self.send({"jsonrpc": "2.0", "id": message["id"],
                                   "error": {"code": -32601, "message": "Method not found"}})
            elif "method" in message:
                pass  # a notification: nothing to answer
            else:
                responses.append(message)
        return responses

    def close(self):
        """Close the server's stdin, wait for it to exit (or end it), and record anything it still writes."""
        grace = min(5.0, max(1.0, self.timeout))
        try:
            self.process.stdin.close()
        except OSError:
            pass
        try:
            self.process.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        while True:
            try:
                raw = self.lines.get(timeout=1)
            except queue.Empty:
                break
            if raw is None:
                break
            self.receive(raw, answer=False)
        try:
            self.process.stdout.close()
        except OSError:
            pass


def main(argv=None, out=None, err=None, server_stderr=None):
    out = out or sys.stdout
    err = err or sys.stderr
    parser = argparse.ArgumentParser(prog="mcp_client.py", description="Probe a stdio MCP server; save the transcript.")
    parser.add_argument("--out", required=True, metavar="PATH", help="the transcript to write (never overwritten)")
    parser.add_argument("--call", metavar="NAME", help="a tool to call after tools/list")
    parser.add_argument("--args", metavar="JSON", help="the tool's arguments, a JSON object (needs --call)")
    parser.add_argument("--timeout", type=float, default=30.0, metavar="SECONDS",
                        help="how long to wait for each response (default 30)")
    parser.add_argument("server", nargs="+", metavar="COMMAND", help="the server command, after --")
    args = parser.parse_args(argv)
    arguments = {}
    if args.args is not None:
        if args.call is None:
            parser.error("--args needs --call")
        try:
            arguments = json.loads(args.args)
        except ValueError:
            parser.error("--args is not JSON")
        if not isinstance(arguments, dict):
            parser.error("--args must be a JSON object")
    path = Path(args.out)
    try:
        transcript = Transcript(path)
    except FileExistsError:
        err.write(f"error: refusing to overwrite {path}\n")
        return 1
    except OSError as exc:
        err.write(f"error: cannot write {path} ({type(exc).__name__})\n")
        return 1
    try:
        process = subprocess.Popen(args.server, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=server_stderr)
    except OSError as exc:
        transcript.close()
        err.write(f"error: cannot start the server ({type(exc).__name__})\n")
        return 1
    session = Session(process, transcript, args.timeout, err)
    try:
        reply = session.request("initialize", {"protocolVersion": CLIENT_VERSION, "capabilities": {},
                                               "clientInfo": dict(CLIENT_INFO)})
        if "error" in reply:
            err.write("error: initialize failed: " + json.dumps(reply["error"]) + "\n")
            return 1
        init = reply.get("result") or {}
        version = init.get("protocolVersion")
        if version not in KNOWN_VERSIONS:
            err.write(f"note: the server answered protocol version {json.dumps(version)}, not one this client knows; "
                      f"going on\n")
        session.notify("notifications/initialized")
        tools, cursor = [], None
        for _ in range(MAX_PAGES):
            reply = session.request("tools/list", {"cursor": cursor} if cursor else {})
            if "error" in reply:
                err.write("error: tools/list failed: " + json.dumps(reply["error"]) + "\n")
                return 1
            page = reply.get("result") or {}
            tools += page.get("tools") or []
            cursor = page.get("nextCursor")
            if not cursor:
                break
        info = init.get("serverInfo") or {}
        out.write(f"server: {info.get('name')} {info.get('version')} (protocol {version})\n")
        out.write("tools:\n" + json.dumps(tools, indent=2, ensure_ascii=False) + "\n")
        if args.call:
            reply = session.request("tools/call", {"name": args.call, "arguments": arguments})
            if "error" in reply:
                out.write(f"error from tools/call {args.call}:\n" + json.dumps(reply["error"], indent=2) + "\n")
                return 1
            out.write(f"result of {args.call}:\n" + json.dumps(reply.get("result"), indent=2, ensure_ascii=False) + "\n")
        return 0
    except ClientError as exc:
        err.write(f"error: {exc}\n")
        return 1
    finally:
        session.close()
        transcript.close()


if __name__ == "__main__":
    sys.exit(main())
