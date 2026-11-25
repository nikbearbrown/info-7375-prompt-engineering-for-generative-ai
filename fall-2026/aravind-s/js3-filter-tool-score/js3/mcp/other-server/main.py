# INFO 7375: MCP from scratch
# Companion: lessons/08-mcp-from-scratch/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
import argparse
import json
import sys

class Server:
    def __init__(self):
        self.initialized = False
        self.ready = False

    def handle(self, message):
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return {"jsonrpc":"2.0","id":None,"error":{"code":-32600,"message":"Invalid request"}}
        method = message.get("method")
        if "id" not in message:
            if method == "notifications/initialized" and self.initialized:
                self.ready = True
            return None
        identity = message["id"]
        def failure(code, text):
            return {"jsonrpc":"2.0","id":identity,"error":{"code":code,"message":text}}
        if method == "initialize":
            self.initialized = True
            result = {"protocolVersion":"2025-11-25","capabilities":{"tools":{}},
                      "serverInfo":{"name":"info7375-readonly","version":"1.0.0"}}
        elif not self.ready:
            return failure(-32000, "Initialize and notify before using tools")
        elif method == "tools/list":
            result = {"tools":[{"name":"lookup","description":"Read a public course fixture",
                       "inputSchema":{"type":"object","properties":{"key":{"type":"string"}},
                                      "required":["key"],"additionalProperties":False}}]}
        elif method == "tools/call":
            params = message.get("params", {})
            if not isinstance(params, dict) or params.get("name") != "lookup":
                return failure(-32602, "Unknown tool")
            args = params.get("arguments", {})
            if not isinstance(args, dict) or set(args) != {"key"} or not isinstance(args["key"], str):
                return failure(-32602, "Expected a string key")
            value = {"office":"505A Dana Hall"}.get(args["key"])
            result = {"content":[{"type":"text","text":value or "Record not found"}],
                      "isError":value is None}
        else:
            return failure(-32601, "Method not found")
        return {"jsonrpc":"2.0","id":identity,"result":result}

def demo():
    server = Server()
    server.handle({"jsonrpc":"2.0","id":1,"method":"initialize"})
    server.handle({"jsonrpc":"2.0","method":"notifications/initialized"})
    return server.handle({"jsonrpc":"2.0","id":2,"method":"tools/list"})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdio", action="store_true")
    args = parser.parse_args()
    if not args.stdio:
        print(json.dumps(demo(), indent=2))
        return
    server = Server()
    for line in sys.stdin:
        try:
            response = server.handle(json.loads(line))
        except ValueError:
            response = {"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":"Parse error"}}
        if response is not None:
            print(json.dumps(response), flush=True)

if __name__ == "__main__":
    main()
