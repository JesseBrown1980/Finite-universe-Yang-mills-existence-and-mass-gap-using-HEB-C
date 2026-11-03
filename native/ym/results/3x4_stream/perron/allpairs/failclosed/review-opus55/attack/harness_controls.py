# Would the differential harness turn red if allpairs were broken? Builds copies of the harness with one fault put into the tool's code and runs each.
# Every variant must report at least one disagreement, a false pass, or a nonzero exit. Nothing here touches the checkout. Integer only, json=0.
import os, re, shutil, subprocess, sys

ROOT = "C:/tmp/opus55/allpairs-review-20261103"
SRC = ROOT + "/fuzz/src/main.rs"
WORK = ROOT + "/fuzz_mut"
ITER = "6000"
VARIANTS = [
    ("window_forgets_its_last_row", "(self.start..self.end).contains(&i)", "(self.start..self.end.saturating_sub(1)).contains(&i)", "disagree"),
    ("value_mismatch_not_counted", "out.value_mismatch += 1;", "out.value_mismatch += 0;", "false_pass"),
    ("closing_a_window_skips_the_row", "            self.closed = true;\n            return;", "            self.closed = true;\n            self.end = h + 1;\n            return;", "disagree"),
    ("pair_gates_dropped", "        self.covers(n)\n            && c.upper == c.lower\n            && c.entries == c.upper + c.lower + c.diag\n            && self.total(|p| p.stored) == c.upper\n            && self.total(|p| p.found) == c.upper\n            && self.total(|p| p.value_mismatch) == 0\n            && self.total(|p| p.lower_without_upper) == 0\n            && self.total(|p| p.upper_without_lower) == 0", "        let _ = (n, c);\n        true", "false_pass"),
    ("lower_entry_answered_twice", "        out.lookups += 1;\n", "        out.lookups += 1;\n        out.found += u64::from(h % 7 == 3);\n", "disagree"),
    ("merkle_compare_removed", "if merkle != hdr.merkle {", "if merkle != hdr.merkle && false {", "disagree"),
]
src = open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
# The roomio fault lives in a file the copy includes by path, so that variant gets its own copy of roomio.rs.
ROOMIO = "C:/tmp/opus55/ym-review-wt/native/ym/crates/torusl/src/roomio.rs"
fails = 0
for name, a, b, want in VARIANTS:
    w = WORK + "/" + name
    os.makedirs(w + "/src", exist_ok=True)
    shutil.copy(ROOT + "/fuzz/Cargo.toml", w + "/Cargo.toml")
    shutil.copy(ROOT + "/fuzz/rust-toolchain.toml", w + "/rust-toolchain.toml")
    s = src
    if name == "merkle_compare_removed":
        r = open(ROOMIO, encoding="utf-8", newline="").read().replace("\r\n", "\n")
        if a not in r:
            raise SystemExit("pattern " + name)
        open(w + "/src/roomio_copy.rs", "w", encoding="utf-8", newline="\n").write(r.replace(a, b))
        s = s.replace('"C:/tmp/opus55/ym-review-wt/native/ym/crates/torusl/src/roomio.rs"', '"%s/src/roomio_copy.rs"' % w)
    else:
        if a not in s:
            raise SystemExit("pattern " + name)
        s = s.replace(a, b)
    open(w + "/src/main.rs", "w", encoding="utf-8", newline="\n").write(s)
    env = dict(os.environ, CARGO_TARGET_DIR=WORK + "/target")
    b1 = subprocess.run(["cargo", "+1.81", "build", "--release", "--quiet"], cwd=w, capture_output=True, text=True, env=env)
    if b1.returncode:
        print("HARNESS_CONTROL|variant=%s|build_failed=1|%s|json=0" % (name, b1.stderr[-300:].replace("\n", " ")))
        fails += 1
        continue
    exe = WORK + "/target/release/fuzz.exe"
    r = subprocess.run([exe, "fuzz", "11", ITER, w + "/tmp.bin"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    done = [x for x in r.stderr.splitlines() if x.startswith("FUZZ_DONE")]
    f = dict(x.split("=", 1) for x in done[-1].split("|") if "=" in x) if done else {}
    red = r.returncode != 0
    print("HARNESS_CONTROL|variant=%s|fault_in_tool=1|exit=%d|false_pass=%s|disagree_verdict=%s|disagree_exit_class=%s|disagree_counters=%s|panics=%s|turned_red=%d|json=0" % (name, r.returncode, f.get("false_pass_main_property"), f.get("disagree_verdict"), f.get("disagree_exit_class"), f.get("disagree_counters_on_ascending_rows"), f.get("panics"), int(red)), flush=True)
    fails += 0 if red else 1
shutil.rmtree(WORK, ignore_errors=True)
print("HARNESS_CONTROLS_DONE|failed=%d|json=0" % fails)
sys.exit(1 if fails else 0)
