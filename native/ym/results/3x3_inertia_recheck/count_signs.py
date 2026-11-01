import sys
for ln in open(sys.argv[1]):
    if ln.startswith("INDEP_MINORS|"):
        f = dict(x.split("=", 1) for x in ln.strip().split("|")[1:] if "=" in x)
        s = f["signs"]
        prev = "+"
        neg = 0
        for c in s:
            if c != prev:
                neg += 1
            prev = c
        print(f"MINORS_COUNT|n={f['n']}|primes={f['primes']}|dropped={f['dropped_primes']}|hadamard_bits={f['hadamard_bits']}|negative={neg}|positive={len(s)-neg}|zero_minors={s.count('0')}|json=0")
