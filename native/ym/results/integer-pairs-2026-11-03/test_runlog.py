#!/usr/bin/env python3
# memory_pilot_runner.py's runlog(), read out of its source and run alone, since importing the runner makes folders and its workflow is dispatch only.
# It must return whole-second ints from an integer clock: 0 and the exit on a finished command, 124 on a timeout. usage: test_runlog.py WORK_DIR   Integer only, json=0.
import ast
import os
import pathlib
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "..", "..", "python", "memory_pilot_runner.py")
source = open(path, encoding="utf-8").read()
compile(source, path, "exec")
tree = ast.parse(source)
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "runlog")
scope = {"time": time, "subprocess": subprocess, "Path": pathlib.Path}
header = ast.parse("from __future__ import annotations\n").body
exec(compile(ast.Module(header + [function], []), path, "exec"), scope)
runlog = scope["runlog"]
work = pathlib.Path(sys.argv[1])
work.mkdir(parents=True, exist_ok=True)
log = work.joinpath("runlog.out")
bad = 0
code, secs = runlog([sys.executable, "-c", "print('finished')"], log)
ok = code == 0 and type(secs) is int and secs >= 0 and log.read_text().strip() == "finished"
bad += 0 if ok else 1
print("RUNLOG_TEST|case=finished|exit=%d|secs_is_int=%d|log_read_back=%d|json=0" % (code, 1 if type(secs) is int else 0, 1 if ok else 0))
code, secs = runlog([sys.executable, "-c", "import sys; sys.exit(7)"], log)
ok = code == 7 and type(secs) is int
bad += 0 if ok else 1
print("RUNLOG_TEST|case=exit_7|exit=%d|secs_is_int=%d|json=0" % (code, 1 if type(secs) is int else 0))
code, secs = runlog([sys.executable, "-c", "import time; time.sleep(30)"], log, timeout=2)
ok = code == 124 and type(secs) is int and 2 <= secs < 30
bad += 0 if ok else 1
print("RUNLOG_TEST|case=timeout|exit=%d|secs_is_int=%d|secs_in_range=%d|json=0" % (code, 1 if type(secs) is int else 0, 1 if ok else 0))
print("RUNLOG_TEST_DONE|cases=3|failed=%d|json=0" % bad)
sys.exit(1 if bad else 0)
