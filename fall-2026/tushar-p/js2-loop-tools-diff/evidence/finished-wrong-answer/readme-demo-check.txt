finished (exit 0): 1 succeeded, 0 failed, 0 pending, 0 duplicate(s) skipped; summary: /private/tmp/js2-readme-check-9ql1unjc/info7375-js2-demo.t14xma/fixture/runs/run-20261110T002239Z-3e9415/summary.json
Agent exit: 0
run run-20261110T002239Z-3e9415  mode: fixture  agent exit: finished
board              agent_new  independent_new  match  agent_fetched  independent_fetched
-----------------  ---------  ---------------  -----  -------------  -------------------
greenhouse/stripe  16         16               yes    719            719                
RESULT: all comparable boards match (1 compared, 0 not comparable)
Checker exit: 0
finished (exit 0): 1 succeeded, 0 failed, 0 pending, 0 duplicate(s) skipped; summary: /private/tmp/js2-readme-check-9ql1unjc/info7375-js2-demo.t14xma/seeded-wrong/runs/run-20261110T002239Z-c8d318/summary.json
Agent exit: 0
run run-20261110T002239Z-c8d318  mode: SEEDED-WRONG-EMPTY (deliberately wrong)  agent exit: finished
board              agent_new  independent_new  match     agent_fetched  independent_fetched
-----------------  ---------  ---------------  --------  -------------  -------------------
greenhouse/stripe  0          16               MISMATCH  0              719                
MISMATCH greenhouse/stripe: agent reported new=0, the saved response gives 16; missing from the agent's report: [7337544, 7746721, 8040052, 8048266, 8130876, 8168550, 8175637, 8267847, 8275558, 8280266, 8284978, 8311067, 8314318, 8329718, 8329719, 8331124]; extra in the agent's report: []
RESULT: MISMATCH on 1 of 1 board(s)
Checker exit: 1
