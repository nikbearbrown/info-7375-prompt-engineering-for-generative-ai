"""Scratch experiment for REVIEW-PACKET.md: does the patched http_transport bound slow *headers*?"""
import socket, sys, threading, time
sys.path.insert(0, sys.argv[1])
from agent.tools import FetchError, http_transport

HEAD = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 2\r\n\r\n{}"
listener = socket.socket(); listener.bind(("127.0.0.1", 0)); listener.listen(1)
def serve():
    conn, _ = listener.accept()
    conn.recv(65536)
    try:
        for i in range(len(HEAD)):          # one byte every 0.3 s: about 22 s in all
            conn.sendall(HEAD[i:i + 1]); time.sleep(0.3)
    except OSError:
        pass
    conn.close()
threading.Thread(target=serve, daemon=True).start()
out = {}
def call():
    t = time.monotonic()
    try:
        out["r"] = http_transport("http://127.0.0.1:%d/x" % listener.getsockname()[1], 1.0, 1000)
    except FetchError as e:
        out["e"] = e
    out["s"] = time.monotonic() - t
th = threading.Thread(target=call, daemon=True); th.start(); th.join(5)
print("prediction: still running after 5 s with timeout=1.0 (headers are read inside opener.open, before the deadline check)")
print("observed: still running after 5 s:", th.is_alive())
th.join(30)
print("observed: finished after %.1f s with %s" % (out.get("s", -1), ("error " + out["e"].kind) if "e" in out else "HTTP %s" % out["r"].status))
