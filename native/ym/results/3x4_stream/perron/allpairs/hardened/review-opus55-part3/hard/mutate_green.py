# The six faults mutate_tool.py's harness stayed green on. For each: the author's unit tests, this seat's 42 named attacks on the faulted tool, and the widened harness.
# The checkout and the export stay as they are: each variant is built in its own copy under hard/mut. Integer only, json=0.
import os, re, shutil, subprocess, sys

R = "C:/tmp/opus55/allpairs-review-20261103/"
SRC = R + "hard/src/native/ym/crates/evolvers/src/bin/allpairs.rs"
TAIL = R + "hard/harness_tail.rs"
WORK = R + "hard/mut"
TORUSL = R + "hard/src/native/ym/crates/torusl/src/"
OUT = R + "hard/out/mutate-green.hbp"
FX = R + "hard/x/native/ym/results/3x4_stream/perron/allpairs/fixture-controls/fixture-2x2.rooms.gz"
ITER = sys.argv[1] if len(sys.argv) > 1 else "1500"
VARIANTS = [
    ("rooms_gate_always_pass", "let rooms_gate = Gate::compare(Some(rooms), c.rows + c.entries);", "let rooms_gate = Gate::Pass;\n    let _ = rooms;"),
    ("repeats_not_in_the_clean_rule", "            && self.total(|p| p.lower_repeated) == 0\n", ""),
    ("answered_rule_dropped", "            && self.total(|p| p.answered) == c.upper\n            && self.total(|p| p.value_mismatch) == 0\n            && self.total(|p| p.lower_without_upper) == 0\n            && self.total(|p| p.upper_without_lower) == 0\n            && self.total(|p| p.lower_repeated) == 0\n", "            && self.total(|p| p.value_mismatch) == 0\n            && self.total(|p| p.lower_without_upper) == 0\n"),
    ("sizes_padding_limit_removed", "    if hdr.payload - used >= MIB {\n", "    if hdr.payload - used >= u64::MAX {\n"),
    ("sizes_n_above_rooms_allowed", "    if hdr.n as u64 > rooms {\n", "    if hdr.n as u64 > u64::MAX - rooms {\n"),
    ("sizes_short_store_allowed", "if off.checked_add(stream).map_or(true, |end| end > store_len) {", "if off.checked_add(stream).map_or(true, |end| end > u64::MAX - store_len.min(0)) {"),
]
src = open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
tail = open(TAIL, encoding="utf-8", newline="").read().replace("\r\n", "\n")
log = open(OUT, "w", encoding="utf-8", newline="\n")
env = dict(os.environ, CARGO_TARGET_DIR=WORK + "/target")
BN = subprocess.BELOW_NORMAL_PRIORITY_CLASS
for name, a, b in VARIANTS:
    if src.count(a) != 1:
        raise SystemExit("pattern " + name + " count " + str(src.count(a)))
    w = WORK + "/" + name
    os.makedirs(w + "/src", exist_ok=True)
    shutil.copy(R + "fuzz/Cargo.toml", w + "/Cargo.toml")
    shutil.copy(R + "fuzz/rust-toolchain.toml", w + "/rust-toolchain.toml")
    tool = src.replace(a, b).replace('"../../../torusl/src/', '"' + TORUSL)
    open(w + "/src/main.rs", "w", encoding="utf-8", newline="\n").write(tool)
    t = subprocess.run(["cargo", "+1.81", "test", "--release", "--quiet"], cwd=w, capture_output=True, text=True, env=env, creationflags=BN)
    m = re.search(r"(\d+) passed; (\d+) failed", t.stdout)
    unit_failed = int(m.group(2)) if m else -1
    # The named attacks on the tool with its main.
    subprocess.run(["cargo", "+1.81", "build", "--release", "--quiet"], cwd=w, capture_output=True, text=True, env=env, creationflags=BN)
    exe = WORK + "/" + name + "-tool.exe"
    shutil.copy(WORK + "/target/release/fuzz.exe", exe)
    named_out = R + "hard/out/green-" + name + ".hbp"
    an = subprocess.run([sys.executable, "-I", "-X", "utf8", R + "hard/attack_new.py", exe, exe, FX, named_out], capture_output=True, text=True)
    named = "-"
    misses = "-"
    if an.stdout.strip():
        named = an.stdout.strip().splitlines()[-1].split("not_met=")[1].split("|")[0]
    if os.path.exists(named_out):
        rows = [x for x in open(named_out, encoding="utf-8") if "|met=0|" in x]
        misses = ",".join(x.split("case=")[1].split("|")[0] for x in rows)[:120] or "-"
    # The widened harness.
    open(w + "/src/main.rs", "w", encoding="utf-8", newline="\n").write(tool.replace("\nfn main() {", "\n#[allow(dead_code)]\nfn tool_main() {", 1) + tail)
    bb = subprocess.run(["cargo", "+1.81", "build", "--release", "--quiet"], cwd=w, capture_output=True, text=True, env=env, creationflags=BN)
    if bb.returncode:
        log.write("MUTATION_GREEN|variant=%s|build_failed=1|%s|json=0\n" % (name, bb.stderr[-300:].replace("\n", " ").replace("|", "~")))
        log.flush()
        continue
    r = subprocess.run([WORK + "/target/release/fuzz.exe", "fuzz", "13", ITER, w + "/tmp.bin"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, creationflags=BN)
    done = [x for x in r.stderr.splitlines() if x.startswith("FUZZ_DONE")]
    f = dict(x.split("=", 1) for x in done[-1].split("|") if "=" in x) if done else {}
    log.write("MUTATION_GREEN|variant=%s|unit_failed=%d|named_not_met=%s|named_missed=%s|harness_exit=%d|disagree_verdict=%s|disagree_exit_class=%s|disagree_gates=%s|disagree_pairs_clean=%s|disagree_counters=%s|harness_red=%d|json=0\n" % (name, unit_failed, named, misses, r.returncode, f.get("disagree_verdict", "-"), f.get("disagree_exit_class", "-"), f.get("disagree_gates", "-"), f.get("disagree_pairs_clean", "-"), f.get("disagree_counters_on_any_rows", "-"), int(r.returncode != 0)))
    log.flush()
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(R + "hard/examples", ignore_errors=True)
log.write("MUTATIONS_GREEN_DONE|json=0\n")
log.close()
print(open(OUT, encoding="utf-8").read())
