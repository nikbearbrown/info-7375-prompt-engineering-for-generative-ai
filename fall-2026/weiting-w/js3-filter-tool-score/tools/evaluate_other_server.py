import json,subprocess,sys,os
SB=os.path.abspath("sandbox"); OUT=os.path.abspath("outside")
reqs=[
 {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"js3-evaluator","version":"1.0.0"}}},
 {"jsonrpc":"2.0","method":"notifications/initialized"},
 {"jsonrpc":"2.0","id":2,"method":"tools/list"},
 {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"read_text_file","arguments":{"path":SB+"/allowed.txt"}}},
 {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"read_text_file","arguments":{"path":OUT+"/secret.txt"}}},
 {"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"read_text_file","arguments":{"path":SB+"/../outside/secret.txt"}}},
 {"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"read_text_file","arguments":{"path":SB+"/escape-link.txt"}}},
 {"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"write_file","arguments":{"path":SB+"/written-by-client.txt","content":"a compatible client wrote this"}}},
 {"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"write_file","arguments":{"path":OUT+"/written-outside.txt","content":"should be refused"}}},
 {"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"list_allowed_directories","arguments":{}}},
]
p=subprocess.Popen(["npx","-y","@modelcontextprotocol/server-filesystem@2.4.0",SB],
   stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
lines=[]
for r in reqs:
    w=json.dumps(r); lines.append("--> "+w)
    p.stdin.write(w+"\n"); p.stdin.flush()
    if "id" not in r:
        lines.append("    (notification: no reply expected)"); continue
    try: lines.append("<-- "+p.stdout.readline().rstrip("\n"))
    except Exception as e: lines.append("<-- [no reply: %s]"%e)
p.stdin.close()
try: p.wait(timeout=10)
except Exception: p.kill()
err=p.stderr.read()
print("\n".join(lines))
print("\n--- stderr ---\n"+err.strip()[:800])
