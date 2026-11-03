# Writes integer-only copies of the second seat's four fuzzers beside the originals, which stay as its evidence.
# Their floating point was a coin flip, a printed statistic and a timer. Each change below must apply as many times as stated. json=0.
# usage: make_integer_redo.py SECOND_SEAT_DIR OUT_DIR
import os, sys

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
CHANGES = {
    "c2_acc.py": [
        ("rng.random() < 0.3", "rng.randrange(10) < 3", 1),
        ("rng.random() < 0.5", "rng.randrange(2) == 0", 1),
    ],
    "c2_fuzz.py": [
        ("rng.random() < rng.choice([0.3, 0.6, 1.0])", "rng.randrange(10) < rng.choice([3, 6, 10])", 1),
        ("t0 = time.time()", "t0 = time.time_ns()", 1),
        ("secs_wall={time.time()-t0:.0f}", "secs_wall={(time.time_ns()-t0)//10**9}", 1),
    ],
    "c3_random.py": [
        ("rng.random() < 0.5", "rng.randrange(2) == 0", 2),
        ("rng.random() < 0.6", "rng.randrange(10) < 6", 2),
        ('float(prev_val), float(val)', 'str(prev_val), str(val)', 1),
        ('(float(v) if isinstance(v, F) else v)', '(str(v) if isinstance(v, F) else v)', 1),
        ("t0 = time.time()", "t0 = time.time_ns()", 1),
        ('f"secs={time.time()-t0:.1f}"', 'f"secs={(time.time_ns()-t0)//10**9}"', 1),
    ],
    "c4b_open.py": [
        ("rng.random() < 0.9", "rng.randrange(10) < 9", 1),
    ],
}
for name, pairs in CHANGES.items():
    t = open(os.path.join(SRC, name), encoding="utf-8", newline="").read()
    for a, b, k in pairs:
        have = t.count(a)
        if have != k:
            raise SystemExit("%s: %r appears %d times, not %d" % (name, a, have, k))
        t = t.replace(a, b)
    head = "# Integer-only copy of second-seat/%s, made on the operator's word that floating point is to be redone in integers. The original stays beside it as evidence.\n" % name
    open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n").write(head + t)
    print("INTEGER_COPY|file=%s|changes=%d|json=0" % (name, sum(k for _, _, k in pairs)))
