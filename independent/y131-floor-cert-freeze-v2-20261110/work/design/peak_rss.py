# FLOOR REFIX-2: run one command and print its true peak resident set, measured from outside the process.
# Usage: python3 -I -B peak_rss.py CMD [ARGS...]. The child keeps this process's stdin, stdout and stderr; after it
# exits, one line PEAK_RSS|kB=<ru_maxrss>|exit=<code>|wall_ms=<ms>|argv0=<CMD> goes to stdout, and the exit code is
# the child's (128+signal if it was killed). ru_maxrss (kB on Linux) from wait4 is the kernel's resident high-water
# mark of the child; in the REFIX-2 checks it read at most 1 MB below the sampled /proc VmHWM. Integers only.
import os
import sys
import time

argv = sys.argv[1:]
if not argv:
    print("PEAK_RSS|REFUSE|usage: peak_rss.py CMD [ARGS...]")
    sys.exit(2)
sys.stdout.flush()
t0 = time.monotonic_ns()
pid = os.fork()
if pid == 0:
    try:
        os.execvp(argv[0], argv)
    except OSError as e:
        os.write(2, ("PEAK_RSS|REFUSE|exec failed: %s\n" % e).encode())
        os._exit(127)
_, status, ru = os.wait4(pid, 0)
wall_ms = (time.monotonic_ns() - t0) // 1000000
if os.WIFEXITED(status):
    code = os.WEXITSTATUS(status)
else:
    code = 128 + os.WTERMSIG(status)
print("PEAK_RSS|kB=%d|exit=%d|wall_ms=%d|argv0=%s" % (ru.ru_maxrss, code, wall_ms, argv[0]))
sys.stdout.flush()
sys.exit(code)
