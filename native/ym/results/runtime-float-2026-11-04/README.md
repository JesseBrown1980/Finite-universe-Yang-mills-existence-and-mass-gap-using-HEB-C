# Floating point at run time

The second seat's run-time evidence, filed as its rows. The source gate reads text and the compiled check reads IR, and this folder holds what executed: which floating-point instructions the integer tools ran before and after the manifest change. Every number below is a row here, and each section names its file. All of it is MEASURED by the second seat on November 3 and 4, 2026, unless a line says otherwise.

**The three builds.** On this repository at `7ae2806348d1f3638ac8a3ab4588ff4d10694c99` and the companion at `da113593c6bdd6483a78b623902100de82ad752f`, Rust 1.81.0, release:

| Variant | Manifests |
|---|---|
| `before` | As on `main` at those commits |
| `half` | `default-features = false` on `num-bigint` only |
| `after` | `default-features = false` on `num-bigint`, `num-integer` and `num-traits` in every crate that uses them |

**The prediction.** [`PREDICTION.hbp`](PREDICTION.hbp) was written before any tool ran. [`rows/SCOREBOARD.hbp`](rows/SCOREBOARD.hbp) reads it: 17 rows MET, 1 MISS, 1 MISS_IN_PART and 1 MISS_ON_WINDOWS, each with its measured value, and 8 METHOD_FAILED rows naming the instruments that failed and what replaced them.

## Cluster on `b33_k1.matrix 1 9`

The tracked tool `cluster`, on input sha256 `a9de0a8c…`. From [`rows/runtime_before.hbp`](rows/runtime_before.hbp), [`runtime_half.hbp`](rows/runtime_half.hbp), [`runtime_after.hbp`](rows/runtime_after.hbp), [`runtime_linux_single.hbp`](rows/runtime_linux_single.hbp) and [`misc.hbp`](rows/misc.hbp), read together in [`rows/REPORT_ROWS.hbp`](rows/REPORT_ROWS.hbp):

| Route | What it counts | `before` | `half` | `after` |
|---|---|---|---|---|
| A | A row printed at each float site of a scratch copy of the vendored crates | **34**, all at `to_radix_digits_estimate` | 0 | **0** |
| A, the recheck's patch | The same, as the second seat first patched it | 34 | 0 | 0 |
| gdb | Breakpoints at `divsd`, `subpd` and `cvttsd2si` | 34, 34, 34 | | |
| gdb, library | Breakpoints on `ceil`, `log2`, `pow`, `trunc` and `sqrt` in the C runtime | 34 hit rows | | none |
| Site breakpoints | Every float-classed instruction in the executable | 42 sites, 10 hit: 272 executions, `divsd` 34, `addsd` 34, `subpd` 34, `subsd` 34, `cvttsd2si` 68, `ucomisd` 68, and 68 calls to `ceil` | 8 sites, 0 hit | 0 sites |
| Unmasked traps | Float exceptions raised | 68, all in the executable | 0 | 0 |
| Sticky flags | MXCSR at thread exit | `0x20`, inexact | `0x0` | `0x0` |
| CPU counters | `FP_ARITH_INST_RETIRED` by `perf_event_open`, Linux build, same stdout | 136: scalar double 102, packed 128-bit double 34 | 0 | 0 |

Each route divides to the same 34 estimates of a print's digit count: 8 levels times 4 values, plus 2 gap ends, as the prediction derived. The printed rows are the same in all three builds, apart from `ms`.

With all three crates off, each of the 18 named inputs reads 0 at every route it ran (75 `RUNTIME` rows in `runtime_after.hbp`, and the `AFTER` field of each row in `REPORT_ROWS.hbp`). The CPU counter route is `NOT_MEASURED` on one of them, the CRLF copy of this input, which runs on Windows alone.

## `num-bigint`'s defaults alone left float running

In `half`, `num-bigint` has its defaults off and `cluster` on `1 9` reads 0, since that input reaches no root. The same executable on `b33_k1.matrix 1 9 1 0 1 1`, and `jumpto` on `fixed 3 27`, each read 1 hit at `int_sqrt_guess`, 3 traps, 8 arithmetic executions including `sqrtsd`, sticky `0x20`, and 4 on the CPU counters.

The cause is in [`rows/features_ym_half.hbp`](rows/features_ym_half.hbp): `sturmrs` names `num-integer` with its defaults, and in the workspace build that re-enables `num-integer/std` for `evolvers` too. The row reads `ENABLES_STD|variant=half|manifest=native/ym/Cargo.toml|crate=num-integer|edges=evolvers…;num-integer feature 'default';num-integer feature 'std';sturmrs feature 'default'…`. So `<u64 as num_integer::roots::Roots>::sqrt::go` stays in `cluster` and `jumpto`, with 8 arithmetic instructions. All three crates must be off in every dependent, and that is the `after` build.

## Effective features

From `cargo tree` in [`rows/features_ym_before.hbp`](rows/features_ym_before.hbp), [`features_ym_half.hbp`](rows/features_ym_half.hbp) and [`features_ym_after.hbp`](rows/features_ym_after.hbp), agreeing with the compiler's own `--cfg` values and cargo's fingerprints in [`rows/rustc_cfg.hbp`](rows/rustc_cfg.hbp). On the workspace `native/ym`:

| Variant | `num-bigint` | `num-integer` | `num-traits` | Crates with `std` on |
|---|---|---|---|---|
| `before` | default, std | default, i128, std | default, i128, std | 3 |
| `half` | none | default, i128, std | default, i128, std | 2 |
| `after` | none | i128 | i128 | 0 |

Over all 34 manifests of this repository, 6 hold a num crate: `std` on in 6, 6 and 0 of them. `cargo tree` reads 21 of the 34 alone, and each of the other 13 has a `TREE_ERROR` row with its first line. [`rows/other_packages.hbp`](rows/other_packages.hbp) holds the packages built apart, with 3 at `NOT_MEASURED`, each with its build error.

## The binaries

From the disassembly of every workspace binary, by two readers that agree on every site, in [`rows/asm_ym_before.hbp`](rows/asm_ym_before.hbp), [`asm_ym_half.hbp`](rows/asm_ym_half.hbp), [`asm_ym_after.hbp`](rows/asm_ym_after.hbp) and the tallies of [`rows/ROLLUP.hbp`](rows/ROLLUP.hbp):

| Repository | Binaries | Arithmetic float instructions, `before` | `half` | `after` | `.text` equal before and after |
|---|---|---|---|---|---|
| This one | 34 | 134 | 16 | 0 | 12 |
| The companion | 29 | 150 | 24 | 0 | 12 |

The functions that held them, `before`: `BigUint::sqrt`, `<u64 as Roots>::sqrt::go`, `BigUint::from_f64` and `to_radix_le`. Left in `after` are scalar moves with no arithmetic, in `rustc_demangle::demangle`, `std::sys::pal::windows::fs::metadata`, `biguint_shr2` and `ymroom::main`, and `SCALAR_MOVE_CONTEXT` rows show each with its neighbouring instructions. On Linux, `before` also holds `__powidf2` from `compiler_builtins` in 11 binaries ([`rows/linux_float_binaries.hbp`](rows/linux_float_binaries.hbp)). The binary check reads `with_float` 6, 2 and 0 on Windows, and 11, 2 and 0 on Linux ([`rows/check_binaries_windows.hbp`](rows/check_binaries_windows.hbp), [`check_binaries_linux.hbp`](rows/check_binaries_linux.hbp)).

The compiled check's own branch built here reads the same `.text` as `after` on all 34 and all 29 ([`rows/branch_compare.hbp`](rows/branch_compare.hbp)). The IR reading in [`rows/ROLLUP.hbp`](rows/ROLLUP.hbp) holds 21 functions with a float `before` and 4 `after`, those 4 all in `num_traits`. They reach no `.text`: the linker drops them, and `IR_VS_ASM` names them.

## Outputs are byte-equal

All 216 `OUTPUT_COMPARE` rows in [`rows/ROLLUP.hbp`](rows/ROLLUP.hbp) read `equal_apart_from_time_fields=1`: 18 of 18 inputs, on stdout and stderr, across the three builds and each instrument. The fields that differ are `ms`, `secs` and `elapsed_ms`, and 81 of the rows differ in none.

`cargo clippy -D warnings` and `cargo test` on both repositories read the same before and after: 105 tests on this one and 5 on the companion, in the `GATE` rows of [`rows/CONSOLIDATED.hbp`](rows/CONSOLIDATED.hbp).

## The adversarial set

From [`rows/misc.hbp`](rows/misc.hbp). `BigInt` `sqrt`, `Display`, `parse` and radix over ten families, powers of two, squares, edge values, random squares, values above 2⁴⁰⁹⁶, decimal, small, primitive, `u16` and radix: 141,377 rows, 14,399,713 bytes, the same sha256 `548fc109…` from the default build, from the `after` build and from Python's `isqrt` and integers, with 0 violations of `r² ≤ n < (r+1)²`. The parse rows are 2,151 bytes, the same on both builds. `u32` square roots, all 4,294,967,296, read 0 violations and the same digest on both builds.

The sticky flags by family read `0x28` or `0x20` on the default build, and `0x0` on every family of the `after` build.

## Cost

From [`rows/cost.hbp`](rows/cost.hbp), alternating warm runs: `after` against `before`, 985 to 1,010 per 1,000 on the five tools, 1,197 per 1,000 on the adversarial rows, and `u32` square roots 97 s against 60 s.

## Limits

- **Two targets on one CPU.** `x86_64-pc-windows-msvc`, and `x86_64-unknown-linux-gnu` under WSL2, on this machine. Other targets, CPUs and rustc versions are unread here.
- **The named inputs.** 18 inputs on the tools in `REPORT_ROWS.hbp`. A path no input reaches reads 0 at every run-time route, as `half` shows on `cluster 1 9`. The binary reading covers the rest of each executable.
- **The two GMP verifiers.** `seat_sturm_biginterval.cpp` and `seat_sturm_exact_gmp.cpp` link libgmp, whose `__gmpn_tdiv_qr` holds 7 arithmetic float instructions and 2 scalar moves in each static binary ([`rows/cpp_asm_linux.hbp`](rows/cpp_asm_linux.hbp)). On the recorded inputs the CPU counters read 0 float instructions on all 3 runs of those two, and on the 2 runs of the third C++ verifier, `seat_sturm_prefix.cpp` ([`rows/cpp_linux.hbp`](rows/cpp_linux.hbp)). Other inputs are unread. The compiled branch keeps this open as `the_float_threshold_in_libgmp_mpn_tdiv_qr_under_the_two_gmp_verifiers`.
- **The Python interpreter.** CPython 3.13.2 itself runs float: 128 traps on an empty script under `-I -S`, all in `python313.dll`, and 135 on an integer-only script, 131 there and 4 in `ucrtbase.dll` (`PYTHON_SCOPE` rows, [`rows/misc.hbp`](rows/misc.hbp)). The Python verifiers' integers are exact, and these rows are the interpreter's own.
- **The instruments.** The instrumented routes run scratch copies of the vendored crates, and the executable hashes in the rows name which build each route read. The CPU counters ran under WSL2, each event alone, after several open at once showed a stray count ([`rows/runtime_linux_single.hbp`](rows/runtime_linux_single.hbp), and the METHOD_FAILED rows of the scoreboard). The source gate and the compiled check state their own scopes in their headers.

## What is here

`PREDICTION.hbp`, byte-identical to the second seat's. `rows/`, its small rows, with `first_pass/` and `first_pass_cantorint_usage_error.hbp` kept as the runs its METHOD_FAILED rows name. `rows/REPORT_ROWS.hbp` is filed with LF line ends in place of CRLF, and everything else byte-identical. `rows/CONSOLIDATED.hbp.sha256` and `rows/check_scripts.sha256` are its own hash rows. [`SHA256SUMS`](SHA256SUMS) covers every file here but itself. The binaries stay out of git, and the rows hold each one's sha256. The scripts that made the rows stay on the second seat's machine, at the hashes in `check_scripts.sha256` for its two checks.
