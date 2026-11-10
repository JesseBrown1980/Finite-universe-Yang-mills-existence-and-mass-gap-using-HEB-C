import sys
rows = open(sys.argv[1]).read().split("\n")
assert rows[-1] == ""
rows = rows[:-1]
bad = 0
kinds = {}
ids = set()
table = {}
for i, r in enumerate(rows, 1):
    parts = r.split("|")
    kinds[parts[0]] = kinds.get(parts[0], 0) + 1
    if parts[-1] != "json=0":
        print("no json=0 end", i); bad += 1
    for f in parts[1:]:
        if "=" not in f or f.index("=") == 0 or " " in f[:f.index("=")]:
            print("bad field", i, f[:60]); bad += 1
    kv = dict((f.split("=", 1)[0], f.split("=", 1)[1]) for f in parts[1:] if "=" in f)
    if "id" in kv:
        if kv["id"] in ids:
            print("dup id", kv["id"]); bad += 1
        ids.add(kv["id"])
    if parts[0] in ("ROW", "TABLE", "GAUGE_FIRST_BREAK"):
        for need in ("id", "tag", "met", "not_met", "falsifier"):
            if need not in kv:
                print("missing", need, i); bad += 1
        if parts[0] == "ROW" and ("quantity" not in kv or "predicted" not in kv):
            print("missing quantity/predicted", i); bad += 1
        if kv.get("tag") not in ("DERIVED", "REPORTED", "CONJECTURE", "OPEN", "MEASURED"):
            print("bad tag", i, kv.get("tag")); bad += 1
    if parts[0] == "TABLE":
        table[int(kv["k"])] = "k=%s|n=%s|M=%s" % (kv["k"], kv["n"], kv["M"])
canon = "".join(table[k] + "\n" for k in sorted(table))
ref = open(sys.argv[2]).read()
print("table_rows_match_file=%d" % (canon == ref))
print("kinds=%s" % sorted(kinds.items()))
print("rows=%d bad=%d" % (len(rows), bad))
