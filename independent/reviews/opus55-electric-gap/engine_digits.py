#!/usr/bin/env python3
"""GPT-6's engine, its bytes unchanged, called through its own run() with a digits argument. Integer only, json=0.
The command line of the engine fixes digits at 40. run() takes digits as a parameter.
usage: engine_digits.py ENGINE_PATH SECTOR_DIR T DIGITS
"""
import hashlib
import importlib.util
import sys
from pathlib import Path


def main(argv):
    engine, directory, t, digits = argv[0], Path(argv[1]), int(argv[2]), int(argv[3])
    with open(engine, "rb") as h:
        sha = hashlib.sha256(h.read()).hexdigest()
    spec = importlib.util.spec_from_file_location("gpt6_sturm_interval", engine)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print("ATTACK_DIGITS_ENGINE|sha256=%s|T=%d|digits=%d|json=0" % (sha, t, digits), flush=True)
    module.run(directory, 1, 0, t, None, digits)


if __name__ == "__main__":
    main(sys.argv[1:])
