"""Record where math.exp runs out of float range, in both directions (evidence for B07 and B08).

Run:  python3 exp_sweep.py > evidence/exp_sweep_output.txt
Every value the B07/B08 counters show is read back from that file by scenes.py.
"""
import datetime
import math
import platform
import sys

print("run date:", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
print("python:", platform.python_version(), "|", sys.platform)
print("largest float (sys.float_info.max):", repr(sys.float_info.max))
print("smallest positive float (math.ulp(0.0)):", repr(math.ulp(0.0)))
print("smallest normal float (sys.float_info.min):", repr(sys.float_info.min))
print()

print("UP  x  math.exp(x)")
for x in [0, 100, 200, 300, 400, 500, 600, 700, 705, 709, 710]:
    try:
        print("UP", x, repr(math.exp(x)))
    except OverflowError as err:
        print("UP", x, f"{type(err).__name__}: {err}")
print()

print("DOWN  x  math.exp(-x)")
for x in [0, 100, 200, 300, 400, 500, 600, 700, 708, 720, 730, 740, 744, 745, 746]:
    print("DOWN", x, repr(math.exp(-x)))
