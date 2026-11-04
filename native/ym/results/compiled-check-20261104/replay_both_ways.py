#!/usr/bin/env python3
"""
One source built two ways, compared on the recorded rows: the manifests as they stand on this branch (after), and the same tree with the manifests of the base commit put back (before), at the same paths.
Rows compared: every committed shard through hebc_ym_http0 verify, which recomputes run.hbp, index.hbi and run.anchor and compares them byte for byte; the cantorint rows with secs masked; each package driver's
RESULT.hbp through a fresh server, byte for byte; direct runs of the tools that reached a float function, compared between the builds with their time fields masked. The executables' hashes are listed.
Linux only: the tools print a matrix's name by cutting at the last '/', so these recorded rows carry Linux paths. Integer only, json=0.
usage: replay_both_ways.py build BASE_COMMIT       replay_both_ways.py run BASE_COMMIT
"""
import concurrent.futures
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.abspath(".")
WORK = "/tmp/both-ways"
MASK = re.compile(rb"\|(secs|ms|elapsed_ms|pass_ms|wall_ms|wall_secs)=\d+")
RESULTS = "native/ym/results"
IS_YM = os.path.isdir(RESULTS + "/2xL")
if IS_YM:
    PACKAGES = (("zwilson-2026-10-30-cloud", "zwilson", None),)
    SHARD_GROUPS = ("2xL/22", "2xL/23", "full_space_r9", "2xL/24")
    EXTRA_UNITS = ("independent/ladder/sturmrs", "independent/evolution_testground/evolvers")
else:
    PACKAGES = (("zt2-2026-10-30-cloud", "zt2", None), ("zwilson-2026-10-30-cloud", "zwilson", None), ("zqnn-2026-10-31-cloud", "zqnn", None), ("zq8-2026-10-30-cloud", "zq8", None), ("z2o-2026-10-30-cloud", "z2o", "0"), ("z2o-2026-10-30-cloud", "z2o", "2"))
    SHARD_GROUPS = ()
    EXTRA_UNITS = ()
fails = 0
failed_specs = {}


def say(text):
    print(text, flush=True)


def units():
    found = ["native/ym"]
    seen = set()
    for pkg, driver, _ in PACKAGES:
        if driver not in seen:
            seen.add(driver)
            found.append("%s/%s/%s" % (RESULTS, pkg, driver))
    return found + list(EXTRA_UNITS)


def target(state, unit):
    return "%s/%s/%s/release" % (WORK, state, unit.replace("/", "_"))


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True, check=True).stdout


def build(base):
    changed = [p for p in git("diff", "--name-only", "--diff-filter=M", base, "HEAD").splitlines() if os.path.basename(p) == "Cargo.toml"]
    say("BOTH_WAYS_MANIFESTS|base=%s|changed=%s|json=0" % (base, ",".join(changed)))
    for state in ("after", "before"):
        if state == "before":
            for p in changed:
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write(git("show", "%s:%s" % (base, p)))
        for u in units():
            env = dict(os.environ)
            env["CARGO_TARGET_DIR"] = "%s/%s/%s" % (WORK, state, u.replace("/", "_"))
            a = time.monotonic_ns()
            p = subprocess.run(["cargo", "+1.81.0", "build", "--release", "--locked"], cwd=u, env=env, capture_output=True)
            say("BOTH_WAYS_BUILD|state=%s|unit=%s|rc=%d|secs=%d|json=0" % (state, u, p.returncode, (time.monotonic_ns() - a) // 1000000000))
            if p.returncode:
                say(p.stderr.decode("utf-8", "replace")[-1500:])
                sys.exit(1)
    subprocess.run(["git", "checkout", "--"] + changed, check=True)
    status = git("status", "--porcelain", "--", "*Cargo.lock", "native/ym/vendor")
    say("BOTH_WAYS_LOCK_AND_VENDOR|bytes_moved=%d|json=0" % len(status))


def masked(b):
    return MASK.sub(lambda m: b"|" + m.group(1) + b"=T", b)


def verify_group(state, group):
    global fails
    t = target(state, "native/ym")
    root = "%s/roots/%s-%s" % (WORK, state, group.replace("/", "_"))
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)
    shutil.copytree("%s/%s/shards" % (RESULTS, group), root + "/shards")
    specs = [open("%s/shards/%s/spec" % (root, d), encoding="utf-8").read().strip() for d in sorted(os.listdir(root + "/shards"))]
    first = [s for s in specs if s.split("/")[0].endswith("sector")]
    rest = [s for s in specs if not s.split("/")[0].endswith("sector")]
    bad = []

    def one(spec):
        p = subprocess.run([t + "/hebc_ym_http0", "verify", root, spec], capture_output=True)
        if p.returncode or b"result=PASS" not in p.stdout:
            bad.append(spec)
            say("VERIFY_FAIL|state=%s|group=%s|spec=%s|rc=%d|err=%s|json=0" % (state, group, spec, p.returncode, (p.stderr or p.stdout).decode("utf-8", "replace").strip().replace("\n", " ").replace("|", "/")[:180]))

    a = time.monotonic_ns()
    for s in first:
        one(s)
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count() or 2) as ex:
        list(ex.map(one, rest))
    say("VERIFY_DONE|state=%s|group=%s|shards=%d|passed=%d|failed=%d|secs=%d|compared=run.hbp,index.hbi,run.anchor|json=0" % (state, group, len(specs), len(specs) - len(bad), len(bad), (time.monotonic_ns() - a) // 1000000000))
    failed_specs[(state, group)] = set(bad)
    shutil.rmtree(root, ignore_errors=True)


def run_driver(state, pkg, driver, part, port):
    global fails
    root = "%s/roots/%s-%s-%s" % (WORK, state, driver, part or "whole")
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)
    log = root + ".log"
    with open(log, "wb") as f:
        srv = subprocess.Popen([target(state, "native/ym") + "/hebc_ym_http0", "serve", root, str(port), "10000"], stdout=f, stderr=subprocess.STDOUT)
        for _ in range(60):
            if b"server=READY" in open(log, "rb").read():
                break
            time.sleep(1)
        exe = "%s/%s" % (target(state, "%s/%s/%s" % (RESULTS, pkg, driver)), driver)
        here = "%s/%s" % (RESULTS, pkg)
        env = dict(os.environ)
        if part:
            env["Z2O_PART"] = "s1:" + part
        a = time.monotonic_ns()
        p = subprocess.run([exe, str(port)], cwd=here, env=env, capture_output=True)
        secs = (time.monotonic_ns() - a) // 1000000000
        srv.kill()
        srv.wait()
    if part:
        env2 = dict(os.environ, Z2O_PART="s1rec:" + part, Z2O_S1_FROM="RESULT.hbp")
        q = subprocess.run([exe, "0"], cwd=here, env=env2, capture_output=True)
        same = int(p.returncode == 0 and q.returncode == 0 and bool(p.stdout) and p.stdout == q.stdout)
        rows = p.stdout.count(b"\n")
    else:
        want = open(here + "/RESULT.hbp", "rb").read()
        same = int(p.stdout == want)
        rows = want.count(b"\n")
    say("PACKAGE|state=%s|package=%s|part=%s|driver_rc=%d|rows=%d|bytes=%d|sha256=%s|byte_identical_to_recorded=%d|secs=%d|json=0" % (state, pkg, part or "whole", p.returncode, rows, len(p.stdout), hashlib.sha256(p.stdout).hexdigest(), same, secs))
    fails += 1 - same
    shutil.rmtree(root, ignore_errors=True)
    return p.stdout


def direct(state, name, exe, args, cwd="."):
    p = subprocess.run([exe] + args, cwd=cwd, capture_output=True)
    return p.returncode, masked(p.stdout), masked(p.stderr)


def direct_tools(mats):
    """The tools that reached a float function before the change, on inputs tracked or built here."""
    global fails
    t = {s: target(s, "native/ym") for s in ("before", "after")}
    os.makedirs(WORK + "/m", exist_ok=True)
    cases = []
    for name, tool, args in (
        ("cluster_s22", "cluster", [mats + "/s22.matrix", "1", "9"]),
        ("jumpto_s22_fixed", "jumpto", [mats + "/s22.matrix", "1", "9", "fixed", "6", "8"]),
        ("jumpto_s22_exact", "jumpto", [mats + "/s22.matrix", "1", "9", "exact", "1000003", "1000"]),
        ("sturmrs_s22", "sturmrs", [mats + "/s22.matrix", "1", "9", "20000"]),
        ("sturmfast_s22", "sturmfast", [mats + "/s22.matrix", "1", "9", "20000"]),
        ("ymwser_2_2_0_3", "ymwser", ["2", "2", "0", "3"]),
        ("ymwser_2_3_1_2", "ymwser", ["2", "3", "1", "2"]),
        ("ymwser_2_2_1_4", "ymwser", ["2", "2", "1", "4"]),
    ):
        cases.append((name, tool, args))
    for name, tool, args in cases:
        b = direct("before", name, "%s/%s" % (t["before"], tool), args)
        a = direct("after", name, "%s/%s" % (t["after"], tool), args)
        same = int(a == b)
        say("BOTH_WAYS_TOOL|case=%s|rc_before=%d|rc_after=%d|stdout_bytes=%d|sha256=%s|same_bytes=%d|masked=secs,ms,elapsed_ms,pass_ms,wall_ms,wall_secs|json=0" % (name, b[0], a[0], len(a[1]), hashlib.sha256(a[1]).hexdigest(), same))
        fails += 1 - same


def cantor():
    global fails
    f = RESULTS + "/cantor-integer-2026-11-03"
    for r in (9, 243):
        outs = {}
        for state in ("before", "after"):
            d = "%s/m-%s" % (WORK, state)
            os.makedirs(d, exist_ok=True)
            if not os.path.exists(d + "/s22.matrix"):
                subprocess.run([target(state, "native/ym") + "/ymsec", "2", "2", "1", "1", d + "/s22.matrix"], capture_output=True, check=True)
            sha = hashlib.sha256(open(d + "/s22.matrix", "rb").read()).hexdigest()
            p = subprocess.run([target(state, "native/ym") + "/cantorint", "run", d + "/s22.matrix", str(r), "4"], capture_output=True)
            outs[state] = masked(p.stdout)
            want = masked(open("%s/RESULT-r%d.hbp" % (f, r), "rb").read())
            same = int(outs[state] == want)
            say("CANTOR|state=%s|r=%d|matrix_sha256=%s|rc=%d|rows=%d|same_as_recorded=%d|masked=secs|json=0" % (state, r, sha, p.returncode, want.count(b"\n"), same))
            fails += 1 - same
        fails += int(outs["before"] != outs["after"])


def exes():
    for u in units():
        for d in sorted(os.listdir(target("after", u))):
            pa, pb = "%s/%s" % (target("after", u), d), "%s/%s" % (target("before", u), d)
            if os.path.isfile(pa) and os.access(pa, os.X_OK) and not d.endswith((".d", ".rlib", ".rmeta")) and os.path.exists(pb):
                a, b = hashlib.sha256(open(pa, "rb").read()).hexdigest(), hashlib.sha256(open(pb, "rb").read()).hexdigest()
                say("EXE|unit=%s|name=%s|before=%s|after=%s|same=%d|json=0" % (u, d, b, a, int(a == b)))


def run_all():
    if IS_YM:
        cantor()
        direct_tools(WORK + "/m-before")
    else:
        os.makedirs(WORK + "/m-before", exist_ok=True)
        subprocess.run([target("before", "native/ym") + "/ymsec", "2", "2", "1", "1", WORK + "/m-before/s22.matrix"], capture_output=True, check=True)
        direct_tools(WORK + "/m-before")
    port = 29000
    outs = {}
    for state in ("before", "after"):
        with concurrent.futures.ThreadPoolExecutor(2) as ex:
            futs = {}
            for pkg, driver, part in PACKAGES:
                port += 1
                futs[ex.submit(run_driver, state, pkg, driver, part, port)] = (pkg, part)
            for fu, key in futs.items():
                outs[(state, key)] = fu.result()
    for pkg, driver, part in PACKAGES:
        same = int(outs[("before", (pkg, part))] == outs[("after", (pkg, part))])
        say("BOTH_WAYS_PACKAGE|package=%s|part=%s|same_bytes=%d|json=0" % (pkg, part or "whole", same))
    global fails
    fails += sum(1 for pkg, driver, part in PACKAGES if outs[("before", (pkg, part))] != outs[("after", (pkg, part))])
    for state in ("before", "after"):
        for group in SHARD_GROUPS:
            verify_group(state, group)
    # A shard that fails on both builds differs from its record for a reason older than this branch. A shard that fails on one build is what this job looks for.
    for group in SHARD_GROUPS:
        b, a = failed_specs[("before", group)], failed_specs[("after", group)]
        say("VERIFY_BOTH_WAYS|group=%s|fail_on_both=%d|only_before=%d|only_after=%d|kinds_on_both=%s|json=0" % (group, len(a & b), len(b - a), len(a - b), ",".join(sorted({s.split("/")[0] for s in a & b})) or "-"))
        fails += len(a ^ b)
    exes()
    say("BOTH_WAYS_DONE|failed=%d|json=0" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build(sys.argv[2])
        sys.exit(0)
    sys.exit(run_all())
