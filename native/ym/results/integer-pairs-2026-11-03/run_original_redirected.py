#!/usr/bin/env python3
# Runs an original script unchanged, with one file it would write sent to another path, so a recorded output stays as it is.
# usage: run_original_redirected.py SCRIPT WRITES_TO SEND_TO [ARGS...]    Integer only, json=0.
import builtins
import runpy
import sys

script, writes_to, send_to = sys.argv[1:4]
real_open = builtins.open


def redirected(path, *rest, **named):
    return real_open(send_to if path == writes_to else path, *rest, **named)


builtins.open = redirected
sys.argv = [script] + sys.argv[4:]
runpy.run_path(script, run_name="__main__")
