# Puts one fault into a copy of the hardened allpairs and reports what turns red: the author's unit tests, and this seat's harness on that copy.
# The checkout and the export stay as they are: each variant is built in its own copy under hard/mut. Integer only, json=0.
import os, re, shutil, subprocess, sys

R = "C:/tmp/opus55/allpairs-review-20261103/"
SRC = R + "hard/src/native/ym/crates/evolvers/src/bin/allpairs.rs"
TAIL = R + "hard/harness_tail.rs"
WORK = R + "hard/mut"
TORUSL = R + "hard/src/native/ym/crates/torusl/src/"
OUT = R + "hard/out/mutate-tool.hbp"
ITER = sys.argv[1] if len(sys.argv) > 1 else "1500"
VARIANTS = [
    ("old_rule_gates_may_be_open", "gates.iter().all(|&g| g == Gate::Pass)", "gates.iter().all(|&g| g != Gate::Fail)"),
    ("rooms_gate_always_pass", "let rooms_gate = Gate::compare(Some(rooms), c.rows + c.entries);", "let rooms_gate = Gate::Pass;\n    let _ = rooms;"),
    ("padding_nonzero_ignored", "rows_fill_rooms && every_byte && end.padding_nonzero == 0 && end.padding_bytes < MIB", "rows_fill_rooms && every_byte && end.padding_bytes < MIB"),
    ("padding_rows_fill_rooms_ignored", "rows_fill_rooms && every_byte && end.padding_nonzero == 0 && end.padding_bytes < MIB", "every_byte && end.padding_nonzero == 0 && end.padding_bytes < MIB"),
    ("identity_by_line_alone", "t.header_sha256 == header_sha256 && t.line == line", "t.line == line"),
    ("identity_open_passes", "None => (Gate::Open, \"-\".to_string()),", "None => (Gate::Pass, \"-\".to_string()),"),
    ("identity_fail_passes", "Some(t) => (Gate::Fail, differing_fields(t.line, line)),", "Some(t) => (Gate::Pass, differing_fields(t.line, line)),"),
    ("d7_stored_minus_found_put_back", "out.upper_without_lower = out.stored - out.answered;", "out.upper_without_lower = out.stored.saturating_sub(out.found);"),
    ("repeats_not_in_the_clean_rule", "            && self.total(|p| p.lower_repeated) == 0\n", ""),
    ("answered_rule_dropped", "            && self.total(|p| p.answered) == c.upper\n            && self.total(|p| p.value_mismatch) == 0\n            && self.total(|p| p.lower_without_upper) == 0\n            && self.total(|p| p.upper_without_lower) == 0\n            && self.total(|p| p.lower_repeated) == 0\n", "            && self.total(|p| p.value_mismatch) == 0\n            && self.total(|p| p.lower_without_upper) == 0\n"),
    ("each_entry_may_answer_twice", "        win.mark_answered(at);\n", ""),
    ("sort_on_admission_removed", "            part.sort_by_key(|e| e.0);\n", "            let _ = &part;\n"),
    ("value_compare_removed", "if i64::from(w_i) * i64::from(z_ih) != i64::from(row.w) * i64::from(z_hi) {", "if i64::from(w_i) * i64::from(z_ih) == i64::MAX - i64::from(row.w) * i64::from(z_hi) {"),
    ("sizes_padding_limit_removed", "    if hdr.payload - used >= MIB {\n", "    if hdr.payload - used >= u64::MAX {\n"),
    ("sizes_n_above_rooms_allowed", "    if hdr.n as u64 > rooms {\n", "    if hdr.n as u64 > u64::MAX - rooms {\n"),
    ("sizes_stream_multiple_removed", "    if stream % MIB != 0 {\n", "    if stream % MIB == u64::MAX {\n"),
    ("sizes_short_store_allowed", "if off.checked_add(stream).map_or(true, |end| end > store_len) {", "if off.checked_add(stream).map_or(true, |end| end > u64::MAX - store_len.min(0)) {"),
    ("repeated_key_blind", "    keys.windows(2).find(|p| p[0] == p[1]).map(|p| p[0])\n", "    keys.windows(2).find(|p| p[0] == p[1] && p[0].is_empty() && p[0] != p[1]).map(|p| p[0])\n"),
]
src = open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
tail = open(TAIL, encoding="utf-8", newline="").read().replace("\r\n", "\n")
log = open(OUT, "w", encoding="utf-8", newline="\n")
env = dict(os.environ, CARGO_TARGET_DIR=WORK + "/target")
BN = subprocess.BELOW_NORMAL_PRIORITY_CLASS
fails = 0
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
    open(w + "/src/main.rs", "w", encoding="utf-8", newline="\n").write(tool.replace("\nfn main() {", "\n#[allow(dead_code)]\nfn tool_main() {", 1) + tail)
    bb = subprocess.run(["cargo", "+1.81", "build", "--release", "--quiet"], cwd=w, capture_output=True, text=True, env=env, creationflags=BN)
    if bb.returncode:
        log.write("MUTATION|variant=%s|build_failed=1|%s|json=0\n" % (name, bb.stderr[-300:].replace("\n", " ").replace("|", "~")))
        log.flush()
        fails += 1
        continue
    r = subprocess.run([WORK + "/target/release/fuzz.exe", "fuzz", "13", ITER, w + "/tmp.bin"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, creationflags=BN)
    done = [x for x in r.stderr.splitlines() if x.startswith("FUZZ_DONE")]
    f = dict(x.split("=", 1) for x in done[-1].split("|") if "=" in x) if done else {}
    red = r.returncode != 0
    fails += 0 if red else 1
    log.write("MUTATION|variant=%s|unit_failed=%d|harness_exit=%d|disagree_verdict=%s|disagree_exit_class=%s|disagree_counters=%s|disagree_identity=%s|disagree_padding=%s|panics=%s|harness_red=%d|json=0\n" % (name, unit_failed, r.returncode, f.get("disagree_verdict", "-"), f.get("disagree_exit_class", "-"), f.get("disagree_counters_on_any_rows", "-"), f.get("disagree_identity", "-"), f.get("disagree_padding", "-"), f.get("panics", "-"), int(red)))
    log.flush()
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(R + "hard/examples", ignore_errors=True)
log.write("MUTATIONS_DONE|variants=%d|harness_green_on_a_fault=%d|json=0\n" % (len(VARIANTS), fails))
log.close()
print(open(OUT, encoding="utf-8").read())
sys.exit(1 if fails else 0)
