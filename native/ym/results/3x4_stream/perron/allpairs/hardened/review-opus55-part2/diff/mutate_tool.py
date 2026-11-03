# Puts one fault into a copy of the corrected allpairs and reports what turns red: the author's unit tests, and this seat's differential harness.
# The checkout and the pinned export stay as they are: each variant is built in its own copy under diff/mut. Integer only, json=0.
import os, re, shutil, subprocess, sys

R = "C:/tmp/opus55/allpairs-review-20261103/"
SRC = R + "diff/src-0fd24d3/native/ym/crates/evolvers/src/bin/allpairs.rs"
TAIL = R + "diff/harness_tail.rs"
WORK = R + "diff/mut"
TORUSL = "C:/tmp/opus55/allpairs-review-20261103/diff/src-0fd24d3/native/ym/crates/torusl/src/"
OUT = R + "diff/out/mutate-tool.hbp"
VARIANTS = [
    # name, pattern, replacement, unit tests claimed to fail (from PERRON-TWO-SIDED.md) or None
    ("old_rule_put_back", "pairs_clean && structure_clean && entries == Gate::Pass && count == Gate::Pass", "pairs_clean && structure_clean && entries != Gate::Fail && count != Gate::Fail", 2),
    ("header_check_removed", "    check_header(&line, &hdr)?;\n", "", 1),
    ("empty_store_allowed", "    if hdr.n == 0 {\n", "    if hdr.n == usize::MAX {\n", 1),
    ("lenient_numbers", "    (n.to_string() == v).then_some(n)\n", "    let _ = v;\n    Some(n)\n", 4),
    ("repeated_key_blind", "    keys.windows(2).find(|p| p[0] == p[1]).map(|p| p[0])\n", "    keys.windows(2).find(|p| p[0] == p[1] && false).map(|p| p[0])\n", None),
    ("gate_compare_passes_any_value", "            Some(_) => Gate::Fail,\n", "            Some(_) => Gate::Pass,\n", None),
    ("gate_none_passes", "            None => Gate::Open,\n", "            None => Gate::Pass,\n", None),
    ("zero_lattice_allowed", "if v == 0 || number::<u32>(nl?)? != v.checked_mul(2)? {", "if number::<u32>(nl?)? != v.checked_mul(2)? {", None),
    ("check_only_n_canonical", ' || field(line, "payload_bytes=").and_then(number::<u64>) != Some(hdr.payload)', "", None),
]
src = open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
tail = open(TAIL, encoding="utf-8").read()
log = open(OUT, "w", encoding="utf-8", newline="\n")
env = dict(os.environ, CARGO_TARGET_DIR=WORK + "/target")
fails = 0
for name, a, b, claimed in VARIANTS:
    if a not in src:
        raise SystemExit("pattern " + name)
    w = WORK + "/" + name
    os.makedirs(w + "/src", exist_ok=True)
    shutil.copy(R + "fuzz/Cargo.toml", w + "/Cargo.toml")
    shutil.copy(R + "fuzz/rust-toolchain.toml", w + "/rust-toolchain.toml")
    tool = src.replace(a, b).replace('"../../../torusl/src/', '"' + TORUSL)
    # The unit tests alone, on the tool with its main.
    open(w + "/src/main.rs", "w", encoding="utf-8", newline="\n").write(tool)
    t = subprocess.run(["cargo", "+1.81", "test", "--release", "--quiet"], cwd=w, capture_output=True, text=True, env=env)
    m = re.search(r"(\d+) passed; (\d+) failed", t.stdout)
    unit_failed = int(m.group(2)) if m else -1
    # The harness on the same fault.
    open(w + "/src/main.rs", "w", encoding="utf-8", newline="\n").write(tool.replace("\nfn main() {", "\n#[allow(dead_code)]\nfn tool_main() {", 1) + tail)
    bb = subprocess.run(["cargo", "+1.81", "build", "--release", "--quiet"], cwd=w, capture_output=True, text=True, env=env)
    if bb.returncode:
        log.write("MUTATION|variant=%s|build_failed=1|%s|json=0\n" % (name, bb.stderr[-200:].replace("\n", " ").replace("|", "~")))
        fails += 1
        continue
    r = subprocess.run([WORK + "/target/release/fuzz.exe", "fuzz", "13", "6000", w + "/tmp.bin"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    done = [x for x in r.stderr.splitlines() if x.startswith("FUZZ_DONE")]
    f = dict(x.split("=", 1) for x in done[-1].split("|") if "=" in x) if done else {}
    red = r.returncode != 0
    claim_ok = claimed is None or unit_failed == claimed
    fails += 0 if red and claim_ok else 1
    log.write("MUTATION|variant=%s|unit_failed=%d|unit_claimed=%s|claim_met=%d|harness_exit=%d|harness_disagree_verdict=%s|harness_disagree_exit_class=%s|harness_false_pass=%s|harness_red=%d|json=0\n" % (name, unit_failed, claimed if claimed is not None else "-", int(claim_ok), r.returncode, f.get("disagree_verdict"), f.get("disagree_exit_class"), f.get("false_pass_main_property"), int(red)))
    log.flush()
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(R + "diff/fuzz/examples", ignore_errors=True)
log.write("MUTATIONS_DONE|variants=%d|failed=%d|json=0\n" % (len(VARIANTS), fails))
log.close()
print(open(OUT, encoding="utf-8").read())
sys.exit(1 if fails else 0)
