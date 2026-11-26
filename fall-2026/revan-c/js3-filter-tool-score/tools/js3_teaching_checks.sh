#!/bin/sh
# Checks on the Chapter 8 teaching server (third_party/ch8_teaching_server, unmodified copy), in a temp dir.
# 1) a stdio session creates no files; 2) the "ready inside initialize" wrong version still passes its own 6 tests.
set -e
T=$(mktemp -d); cp -r third_party/ch8_teaching_server "$T/"; cd "$T/ch8_teaching_server"
echo "== run at $(date -u +%Y-%m-%dT%H:%M:%SZ), python: $(python3 --version)"
echo "== 1) files before/after one stdio session"
ls -R > ../before.txt
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize"}' '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"lookup","arguments":{"key":"office"}}}' | python3 -I main.py --stdio
ls -R > ../after.txt
diff ../before.txt ../after.txt && echo "no files created or removed in its folder"
echo "== 2) mutant: ready set inside initialize"
sed -i '' 's/            self.initialized = True$/            self.initialized = True; self.ready = True/' main.py
grep -n "self.initialized = True; self.ready = True" main.py
python3 -I -m unittest discover -s tests 2>&1 | tail -2
echo "-- mutant answers tools/list with no initialized notification:"
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize"}' '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | python3 -I main.py --stdio | tail -1 | cut -c1-90
rm -rf "$T"
