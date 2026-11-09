#!/usr/bin/env python3
"""
The operator's rule: "The gate must reject operations capable of silently introducing floating-point values."

Scope. Compiled code, read after the compiler has resolved names, aliases, macros and generics.

Rust. Each tracked Cargo package is built through `cargo +1.81.0 rustc --release --locked --all-targets`, with optimisation off,
and RUSTFLAGS asking for LLVM IR and MIR from every crate in the build. A crate is third-party when its Cargo.lock entry carries a source; every other crate is a project crate.
 1. Project crates, IR: float types and instructions, with names and quoted text removed first, and inline or module assembly that names float registers or opcodes.
 2. Project crates, MIR: the types f16, f32, f64, f128. This holds what IR no longer shows: const evaluation, statics, dead functions, constants folded while the IR is built.
 3. Call graph over all the IR: an edge is any symbol reference in a body or a constant table. A project crate that reaches a function holding a float, or an external float
    function of the standard library, fails. A function present in a third-party crate and not reached is listed as evidence and passes.
 4. Manifests: each num-* dependency must say default-features = false, and must not ask for std or libm by name.
 5. Tracked .rs files no package compiled are built alone with rustc and read the same way. What cannot be built is a failure unless COMPILED-NOT-BUILT.txt beside this file names it.
 6. A tracked compiled object (.rlib, .o, .a, .so, .dll, .exe, .pyc, .wasm and the like) fails, because no reader here can see inside it.
C and C++. Each tracked source is compiled -O0 -S and read for scalar float opcodes, scalar float moves, and calls to the soft-float and libm routines.

Limits, measured or by construction. It reads what these builds compile, on one target and one set of cfg values. The standard library is precompiled, so its bodies are not read:
an external function counts by its signature and by its path under core::fmt::float, core::num::flt2dec, core::num::dec2flt, core::f32, core::f64, std::f32, std::f64. Doc-tests are not
compiled here. Objects and static libraries from outside the tree that a build script names, child processes, files read at run time and code a program writes while running are outside it. Python,
JavaScript and shell are outside it; no_float_gate.py and the checked runs cover those for what they read. A pass means these reads found nothing in what they read. Integer only, json=0.

usage: compiled_float_check.py rust ROOT [--only MANIFEST]... [--opt-level N] [--keep TARGET_BASE]
       compiled_float_check.py cpp ROOT [--only FILE]...
       compiled_float_check.py plants ROOT rust|cpp      Each plant must go red through the real command; each control must stay green.
       compiled_float_check.py selftest
"""
import collections
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

TOOLCHAIN = "+1.81.0"
HERE = os.path.dirname(os.path.abspath(__file__))
NOT_BUILT_LIST = os.path.join(HERE, "COMPILED-NOT-BUILT.txt")

IR_QUICK = re.compile(r"double|float|half|fp128|fp80|fadd|fsub|fmul|fdiv|frem|fneg|fcmp|sitofp|uitofp|fptosi|fptoui|fpext|fptrunc")
IR_FP = re.compile(r"\b(?:double|float|half|bfloat|fp128|x86_fp80|ppc_fp128|fadd|fsub|fmul|fdiv|frem|fneg|fcmp|sitofp|uitofp|fptosi|fptoui|fpext|fptrunc)\b")
ASM_LINE = re.compile(r"^\s*(?:module\s+asm\b)|\bcall\b.*\basm\b|\binvoke\b.*\basm\b")
ASM_FP = re.compile(r"\b(?:[xyz]mm\d+|st\(\d\)|v?(?:add|sub|mul|div|sqrt|min|max|ucomi|comi|cmp[a-z]*)s[sdhq]|v?cvt\w+|f(?:ld|st|add|sub|mul|div|sqrt|ild|ist|xch|chs|abs|com|ucom)\w*)\b", re.I)
QUOTED = re.compile(r'"[^"]*"')
NAME = re.compile(r"[@%!#]\S*")
DEFINE = re.compile(r'^define\b.*?@("[^"]+"|[\w.$-]+)\(')
DECLARE = re.compile(r'^declare\b.*?@("[^"]+"|[\w.$-]+)\(')
SYMBOL = re.compile(r'@("[^"]+"|[\w.$-]+)')
# Externals whose bodies the IR does not hold: the standard library's own float code, by symbol path.
STD_FP_SYMBOL = re.compile(r"_ZN4core3fmt5float|_ZN4core3num7flt2dec|_ZN4core3num7dec2flt|_ZN3std3f32|_ZN3std3f64|_ZN4core3f32|_ZN4core3f64")
MIR_STRING = re.compile(r'"(?:[^"\\]|\\.)*"')
MIR_FP = re.compile(r"\bf(?:16|32|64|128)\b|\d_?f(?:16|32|64|128)\b")
CPP_OP = re.compile(r"^\s+(?:(?:v?(?:add|sub|mul|div|sqrt|min|max|ucomi|comi|cmp[a-z]*)s[sd])|v?cvt\w+|f(?:ld|st|add|sub|mul|div|sqrt|ild|ist|xch|chs|abs|com|ucom)\w*)\b", re.M)
CPP_MOVE = re.compile(r"^\s+(?:v?movs[sd]|v?movd|v?movq)\s[^\n]*%[xy]mm\d", re.M)
# g++ zeroes a 24-byte object such as a std::vector with pxor, movaps and movq on one xmm register. That is a block move of zero and holds no float.
CPP_ZEROED_BLOCK = re.compile(r"^\s+v?pxor\s+%xmm(\d+),\s*%xmm\1\n(?:\s+v?mov(?:aps|ups|dqa|dqu)\s+%xmm\1,[^\n]*\n)*\s+v?movq\s+%xmm\1,\s*-?\d*\(%r[a-z0-9]+\)", re.M)
# GCC may use an XMM register solely to zero integer storage. A pxor
# followed only by zero stores and a final movd is a bitwise-zero transfer.
# Require the exact proven-zero sequence; ordinary movd and any FP operation
# remain covered by CPP_MOVE and CPP_OP.
CPP_ZEROED_DWORD = re.compile(
    r"^\s+v?pxor\s+%xmm(\d+),\s*%xmm\1\n"
    r"(?:\s+v?mov(?:aps|ups|dqa|dqu)\s+%xmm\1,[^\n]*\n)*"
    r"\s+v?movd\s+%xmm\1,\s*(?:%[er][a-z0-9]+|-?\d*\(%r[a-z0-9]+\))",
    re.M,
)

CPP_CALL = re.compile(
    r"^\s+call[ql]?\s+\*?_*(?:__(?:add|sub|mul|div|neg|extend|trunc|fixuns|fix|floatun|float|cmp|unord|eq|ne|ge|gt|le|lt|pow)\w*?(?:tf|xf|df|sf|hf|bf|td|dd|sd)\d?\w*|__bid_\w+|__dpd_\w+"
    r"|(?:sqrt|cbrt|pow|exp|exp2|expm1|log|log2|log10|log1p|sin|cos|tan|asin|acos|atan|atan2|sinh|cosh|tanh|floor|ceil|round|trunc|rint|nearbyint|fmod|fabs|hypot|ldexp|frexp|modf"
    r"|strtod|strtof|strtold|atof|lround|llround|lrint|llrint|tgamma|lgamma|erf|erfc)[fl]?)(?:@PLT)?\s*$",
    re.M,
)
NUM_DEP = re.compile(r'^\s*"?(num-[a-z0-9-]+)"?\s*=\s*(.*)$')
RENAMED_NUM = re.compile(r'package\s*=\s*"(num-[a-z0-9-]+)"')
TRACKED_OBJECT = re.compile(r"\.(rlib|rmeta|o|obj|a|lib|so|dll|dylib|exe|pyc|pyo|pyd|wasm|class|jar|whl|pyz)$", re.I)
ABSOLUTE_PATH = re.compile(r'(#\[path\s*=\s*r?")([A-Za-z]:/[^"]+|/[^"]+)(")')
PATH_MAP = ((re.compile(r".*/(native/ym/crates/.+)$"), r"\1"), (re.compile(r".*/kernel/core/src/tribit/mod\.rs$"), "native/vendor/clasy_x3/vendor/canonical/tribit/mod.rs"))


def say(text):
    print(text, flush=True)


def shown(path, root):
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def clean(text):
    return text.replace("|", "/").replace("\r", " ").replace("\n", " ")[:170]


def run(cmd, cwd, env=None, stdin_text=None):
    full = dict(os.environ)
    full.update(env or {})
    kwargs = {}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.BELOW_NORMAL_PRIORITY_CLASS
    p = subprocess.run(cmd, cwd=cwd, env=full, capture_output=True, stdin=subprocess.DEVNULL, **kwargs)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def tracked(root):
    rc, out, err = run(["git", "-C", root, "ls-files", "-z"], root)
    if rc:
        raise SystemExit("COMPILED_ERROR|reason=git_ls_files|detail=%s|json=0" % clean(err))
    return [p for p in out.split("\0") if p]


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def table(text, name):
    return re.search(r"^\[%s\]\s*$" % re.escape(name), text, re.M) is not None


def third_party_dir(path, root):
    """True when the file sits in a crate unpacked by cargo vendor, which leaves .cargo-checksum.json at the crate's top."""
    d = os.path.dirname(os.path.abspath(path))
    top = os.path.abspath(root)
    while d.startswith(top) and len(d) >= len(top):
        if os.path.exists(os.path.join(d, ".cargo-checksum.json")):
            return True
        if d == top:
            return False
        d = os.path.dirname(d)
    return False


def manifests_of(root, only):
    if only:
        return [os.path.abspath(m) for m in only]
    found = []
    for p in tracked(root):
        if os.path.basename(p) == "Cargo.toml" and not third_party_dir(os.path.join(root, p), root):
            found.append(os.path.abspath(os.path.join(root, p)))
    return found


def manifest_findings(path):
    """num-* dependencies must have default features off and must not name std or libm."""
    out = []
    section = ""
    block_name = None
    block_lines = []

    def close_block():
        if block_name is not None:
            body = " ".join(block_lines)
            if not re.search(r"default-features\s*=\s*false", body):
                out.append((block_name, "default_features_on"))
            if re.search(r'features\s*=\s*\[[^\]]*"(?:std|libm)"', body):
                out.append((block_name, "names_std_or_libm"))

    for line in read_text(path).splitlines():
        s = line.strip()
        if s.startswith("["):
            close_block()
            block_name, block_lines = None, []
            section = s.strip("[]")
            m = re.match(r"(?:.*\.)?(?:dev-|build-)?dependencies\.(num-[a-z0-9-]+)$", section)
            if m:
                block_name = m.group(1)
            continue
        if block_name is not None:
            block_lines.append(s)
            continue
        if not re.search(r"(?:^|\.)(?:dev-|build-)?dependencies$", section):
            continue
        m = NUM_DEP.match(s)
        renamed = RENAMED_NUM.search(s)
        if m or renamed:
            crate = renamed.group(1) if renamed else m.group(1)
            if not re.search(r"default-features\s*=\s*false", s):
                out.append((crate, "default_features_on"))
            if re.search(r'features\s*=\s*\[[^\]]*"(?:std|libm)"', s):
                out.append((crate, "names_std_or_libm"))
    close_block()
    return out


def lock_of(start, stop):
    d = start
    while True:
        p = os.path.join(d, "Cargo.lock")
        if os.path.exists(p):
            return p
        if d == stop or os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)


def lock_third_party(lock):
    names = set()
    if not lock:
        return names
    name = None
    for line in read_text(lock).splitlines():
        m = re.match(r'name = "([^"]+)"', line)
        if m:
            name = m.group(1)
        elif line.startswith("source = ") and name:
            names.add(name)
    return names


def workspace_of(manifest, root):
    """(workspace dir or None, member). A manifest with its own [workspace] table is its own root."""
    d = os.path.dirname(manifest)
    if table(read_text(manifest), "workspace"):
        return d, True
    top = os.path.abspath(root)
    if not d.startswith(top):
        return None, True
    while d != top:
        d = os.path.dirname(d)
        parent = os.path.join(d, "Cargo.toml")
        if os.path.exists(parent):
            text = read_text(parent)
            if table(text, "workspace"):
                m = re.search(r"members\s*=\s*\[(.*?)\]", text, re.S)
                members = re.findall(r'"([^"]+)"', m.group(1)) if m else []
                rel = os.path.relpath(os.path.dirname(manifest), d).replace("\\", "/")
                return d, any(rel == x.rstrip("/") or (x.endswith("*") and rel.startswith(x[:-1])) for x in members)
    return None, True


def replaced_source_dir(start, root):
    """The vendor folder that a .cargo/config.toml above `start` replaces crates.io with, or None."""
    d = start
    top = os.path.abspath(root)
    while d.startswith(top):
        c = os.path.join(d, ".cargo", "config.toml")
        if os.path.exists(c):
            m = re.search(r'directory\s*=\s*"([^"]+)"', read_text(c))
            if m:
                return os.path.join(d, m.group(1))
        if d == top:
            break
        d = os.path.dirname(d)
    return None


def holds_absolute_path(d):
    for base, dirs, names in os.walk(d):
        dirs[:] = [x for x in dirs if x != "target"]
        for n in names:
            if n.endswith(".rs") and ABSOLUTE_PATH.search(read_text(os.path.join(base, n))):
                return True
    return False


def map_absolute_paths(scratch, root):
    """Rewrites absolute #[path] lines in a scratch copy to the same files in this repository. Returns what it mapped."""
    mapped = []
    for base, _, names in os.walk(scratch):
        for n in names:
            if not n.endswith(".rs"):
                continue
            full = os.path.join(base, n)
            text = read_text(full)

            def one(m):
                for pattern, repl in PATH_MAP:
                    if pattern.match(m.group(2)):
                        to = pattern.sub(repl, m.group(2))
                        mapped.append((m.group(2), to))
                        return m.group(1) + os.path.join(root, to).replace("\\", "/") + m.group(3)
                return m.group(0)

            new = ABSOLUTE_PATH.sub(one, text)
            if new != text:
                with open(full, "w", encoding="utf-8", newline="") as f:
                    f.write(new)
    return mapped


def plan_units(root, manifests):
    """Group manifests into builds: workspace members share one target folder; a crate cargo refuses in place, or whose locked crates the vendor folder lacks, builds in a scratch copy."""
    units = collections.OrderedDict()
    skipped = 0
    for m in manifests:
        text = read_text(m)
        d = os.path.dirname(m)
        if not table(text, "package"):
            skipped += 1
            continue
        ws, member = workspace_of(m, root)
        lock = lock_of(d, os.path.abspath(root)) if d.startswith(os.path.abspath(root)) else (os.path.join(d, "Cargo.lock") if os.path.exists(os.path.join(d, "Cargo.lock")) else None)
        copy = not member
        # A path-dependency crate with no lock of its own: its own targets build in a scratch copy, locked there, offline.
        if not os.path.exists(os.path.join(ws or d, "Cargo.lock")):
            copy = True
        if not copy and member and table(text, "workspace") and holds_absolute_path(d):
            copy = True
        vendor = replaced_source_dir(d, root) if d.startswith(os.path.abspath(root)) else None
        if vendor and lock and not copy:
            have = set(os.listdir(vendor)) if os.path.isdir(vendor) else set()
            if lock_third_party(lock) - have:
                copy = True
        key = ("copy", m) if copy else (ws or d)
        units.setdefault(key, {"dir": ws or d, "members": [], "copy": copy, "lock": lock})["members"].append(m)
    return units, skipped


def crate_of(path, target):
    """The crate a compiler output file belongs to: its name up to the hash. Anything under a build script's folder, autocfg's probes among them, belongs to that folder's package."""
    parts = os.path.relpath(path, target).replace("\\", "/").split("/")
    if "build" in parts[:2]:
        i = parts.index("build")
        if i + 2 < len(parts):
            return parts[i + 1].rsplit("-", 1)[0].replace("-", "_")
    return os.path.basename(path).split("-")[0].split(".")[0]


def files_under(target, ext):
    found = []
    for d, _, names in os.walk(target):
        found += [os.path.join(d, n) for n in names if n.endswith(ext)]
    return found


def demangle(symbol):
    m = re.match(r"_ZN(.*)E$", symbol.strip('"'))
    if not m:
        return symbol.strip('"')
    s, parts = m.group(1), []
    while s:
        k = re.match(r"(\d+)", s)
        if not k:
            break
        n = int(k.group(1))
        parts.append(s[k.end():k.end() + n])
        s = s[k.end() + n:]
    if parts and re.fullmatch(r"h[0-9a-f]{16}", parts[-1]):
        parts = parts[:-1]
    return "::".join(parts).replace("$LT$", "<").replace("$GT$", ">").replace("$u20$", " ").replace("$C$", ",").replace("..", "::")


def ir_line_has_float(line):
    """Float types and instructions, with names and quoted text gone; assembly text is read separately."""
    if ASM_LINE.search(line):
        for q in QUOTED.findall(line):
            if ASM_FP.search(q):
                return True
    if not IR_QUICK.search(line):
        return False
    if line.startswith((";", "source_filename", "target ")):
        return False
    return IR_FP.search(NAME.sub("", QUOTED.sub('""', line))) is not None


def read_ir(target, third_party):
    """Returns project float lines by crate, float functions, the reference graph and which crate defines each function."""
    project_lines = collections.Counter()
    samples = {}
    fp_funcs = {}
    edges = collections.defaultdict(set)
    owner = {}
    files = files_under(target, ".ll")
    for path in files:
        crate = crate_of(path, target)
        is_third = crate in third_party
        current = None
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if ir_line_has_float(line):
                    if not is_third:
                        project_lines[crate] += 1
                        samples.setdefault(crate, line.strip()[:120])
                    m = DEFINE.match(line) or DECLARE.match(line)
                    if current is not None:
                        fp_funcs.setdefault(current, line.strip()[:100])
                    elif m:
                        fp_funcs.setdefault(m.group(1), line.strip()[:100])
                if line.startswith("define"):
                    m = DEFINE.match(line)
                    if m:
                        current = m.group(1)
                        owner[current] = crate
                    continue
                if line.startswith("declare"):
                    m = DECLARE.match(line)
                    if m and STD_FP_SYMBOL.search(m.group(1)):
                        fp_funcs.setdefault(m.group(1), "external:" + demangle(m.group(1))[:90])
                    continue
                if current is not None:
                    if line.startswith("}"):
                        current = None
                    elif "@" in line:
                        edges[current].update(SYMBOL.findall(line))
                    continue
                if line.startswith("@"):
                    found = SYMBOL.findall(line)
                    if found:
                        edges[found[0]].update(found[1:])
    return files, project_lines, samples, fp_funcs, edges, owner


def read_mir(target, third_party):
    lines = collections.Counter()
    samples = {}
    files = [p for p in files_under(target, ".mir") if crate_of(p, target) not in third_party]
    for path in files:
        crate = crate_of(path, target)
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith(("//", "debug ", "scope ")):
                    continue
                if MIR_FP.search(MIR_STRING.sub('""', s)):
                    lines[crate] += 1
                    samples.setdefault(crate, s[:120])
    return files, lines, samples


def reach(fp_funcs, edges, owner, third_party):
    rev = collections.defaultdict(set)
    for a, bs in edges.items():
        for b in bs:
            rev[b].add(a)
    seen = set(fp_funcs)
    parent = {}
    frontier = list(fp_funcs)
    while frontier:
        x = frontier.pop()
        for y in rev.get(x, ()):
            if y not in seen:
                seen.add(y)
                parent[y] = x
                frontier.append(y)
    hits = collections.defaultdict(list)
    for f, crate in owner.items():
        if crate not in third_party and f in seen:
            hits[crate].append(f)
    chains = {}
    for crate, fs in hits.items():
        chain = [sorted(fs)[0]]
        while chain[-1] in parent and len(chain) < 8:
            chain.append(parent[chain[-1]])
        chains[crate] = (len(fs), " -> ".join(demangle(c)[:70] for c in chain))
    forward = set()
    frontier = [f for f, crate in owner.items() if crate not in third_party]
    while frontier:
        x = frontier.pop()
        if x in forward:
            continue
        forward.add(x)
        frontier.extend(edges.get(x, ()))
    return chains, forward


def not_built_list():
    rows = {}
    if os.path.exists(NOT_BUILT_LIST):
        for line in read_text(NOT_BUILT_LIST).splitlines():
            if line.strip() and not line.startswith("#"):
                parts = [p.strip() for p in line.split("|", 1)]
                rows[parts[0]] = parts[1] if len(parts) > 1 else ""
    return rows


def compiled_sources(target, bases, mapping):
    """Source files named by the compiler's dep-info files, as absolute paths in the repository."""
    found = set()
    for path in files_under(target, ".d"):
        for line in read_text(path).splitlines():
            if ":" not in line or line.startswith("#"):
                continue
            head, _, rhs = line.partition(": ")
            for tok in re.findall(r"(?:\\ |\S)+", rhs):
                p = tok.replace("\\ ", " ")
                if not p.endswith(".rs"):
                    continue
                candidates = [p] if os.path.isabs(p) else [os.path.join(b, p) for b in bases]
                for c in candidates:
                    c = os.path.abspath(c)
                    for old, new in mapping:
                        if c.startswith(old):
                            c = new + c[len(old):]
                    if os.path.exists(c):
                        found.add(os.path.normcase(c))
                        break
    return found


def build_unit(root, key, unit, opt, base, n):
    target = os.path.join(base, "u%d" % n)
    env = {
        "CARGO_TARGET_DIR": target,
        "RUSTFLAGS": "--emit=llvm-ir,mir -C codegen-units=1",
        "CARGO_INCREMENTAL": "0",
        "CARGO_PROFILE_RELEASE_OPT_LEVEL": str(opt),
        "CARGO_PROFILE_RELEASE_DEBUG": "0",
        "CARGO_PROFILE_RELEASE_LTO": "off",
        "CARGO_PROFILE_RELEASE_CODEGEN_UNITS": "1",
        "CARGO_TERM_COLOR": "never",
    }
    mapping = []
    workdirs = []
    if unit["copy"]:
        original = os.path.dirname(unit["members"][0])
        scratch = os.path.join(base, "copy%d" % n)
        shutil.copytree(original, scratch, ignore=shutil.ignore_patterns("target"))
        mp = os.path.join(scratch, "Cargo.toml")
        if not table(read_text(mp), "workspace"):
            with open(mp, "a", encoding="utf-8", newline="\n") as f:
                f.write("\n[workspace]\n")
        if not os.path.exists(os.path.join(scratch, "Cargo.lock")):
            run(["cargo", TOOLCHAIN, "generate-lockfile", "--offline"], scratch, env)
        for frm, to in map_absolute_paths(scratch, root):
            say("COMPILED_PATH_MAPPED|unit=%s|from=%s|to=%s|json=0" % (shown(original, root), frm, to))
        workdirs = [scratch]
        mapping = [(os.path.abspath(scratch), os.path.abspath(original))]
    else:
        workdirs = [os.path.dirname(m) for m in unit["members"]]
    rc = 0
    last = "-"
    started = time.monotonic_ns()
    for w in workdirs:
        code, _, err = run(["cargo", TOOLCHAIN, "rustc", "--release", "--locked", "--all-targets"], w, env)
        if code:
            tail = [x for x in err.strip().splitlines() if x.strip()]
            first = clean(tail[-1]) if tail else "-"
            code, _, err = run(["cargo", TOOLCHAIN, "rustc", "--release", "--locked"], w, env)
            if code == 0:
                say("COMPILED_TESTS_NOT_BUILT|unit=%s|all_targets=%s|default_targets_read=1|json=0" % (shown(w, root), first))
            else:
                rc = code
                tail = [x for x in err.strip().splitlines() if x.strip()]
                last = clean(tail[-1]) if tail else "-"
    # Features unify across a workspace when all its members build together, so the graph is read that way too.
    if rc == 0 and len(workdirs) > 1:
        code, _, err = run(["cargo", TOOLCHAIN, "build", "--release", "--locked", "--workspace", "--all-targets"], workdirs[0], env)
        if code:
            rc = code
            tail = [x for x in err.strip().splitlines() if x.strip()]
            last = clean(tail[-1]) if tail else "-"
    secs = (time.monotonic_ns() - started) // 1000000000
    bases = [os.path.dirname(unit["lock"]) if unit["lock"] else unit["dir"], unit["dir"]] + workdirs
    return target, rc, last, secs, bases, mapping


def rust_check(root, only, opt, keep):
    root = os.path.abspath(root)
    manifests = manifests_of(root, only)
    fails = 0
    for p in tracked(root):
        if TRACKED_OBJECT.search(p):
            fails += 1
            say("COMPILED_TRACKED_OBJECT|file=%s|json=0" % p)
    for m in manifests:
        for crate, problem in manifest_findings(m):
            fails += 1
            say("COMPILED_MANIFEST|file=%s|crate=%s|problem=%s|json=0" % (shown(m, root), crate, problem))
    units, skipped = plan_units(root, manifests)
    listed = not_built_list()
    seen_not_built = set()
    base = keep or tempfile.mkdtemp(prefix="compiled-")
    os.makedirs(base, exist_ok=True)
    compiled = set()
    totals = collections.Counter()
    for n, (key, unit) in enumerate(units.items()):
        rel = shown(unit["dir"], root)
        if unit["copy"]:
            rel = shown(unit["members"][0], root)
        target, rc, last, secs, bases, mapping = build_unit(root, key, unit, opt, base, n)
        totals["units"] += 1
        if rc:
            if rel in listed or os.path.dirname(rel) in listed:
                seen_not_built.add(rel if rel in listed else os.path.dirname(rel))
                say("COMPILED_NOT_BUILT_LISTED|unit=%s|rc=%d|last=%s|json=0" % (rel, rc, last))
            else:
                fails += 1
                say("COMPILED_NOT_BUILT|unit=%s|rc=%d|last=%s|json=0" % (rel, rc, last))
            continue
        third = {x.replace("-", "_") for x in lock_third_party(unit["lock"] or os.path.join(unit["dir"], "Cargo.lock"))}
        if unit["copy"]:
            third |= {x.replace("-", "_") for x in lock_third_party(os.path.join(base, "copy%d" % n, "Cargo.lock"))}
        lls, project_lines, samples, fp_funcs, edges, owner = read_ir(target, third)
        mirs, mir_lines, mir_samples = read_mir(target, third)
        chains, forward = reach(fp_funcs, edges, owner, third)
        for crate, count in sorted(project_lines.items()):
            fails += 1
            say("COMPILED_PROJECT_FP|unit=%s|crate=%s|lines=%d|first=%s|json=0" % (rel, crate, count, clean(samples[crate])))
        for crate, count in sorted(mir_lines.items()):
            fails += 1
            say("COMPILED_MIR_FP|unit=%s|crate=%s|lines=%d|first=%s|json=0" % (rel, crate, count, clean(mir_samples[crate])))
        reached_third = 0
        for crate, (count, chain) in sorted(chains.items()):
            fails += 1
            reached_third += 1
            say("COMPILED_REACH|unit=%s|crate=%s|functions=%d|example=%s|json=0" % (rel, crate, count, clean(chain)))
        present = unreached = 0
        for f in sorted(fp_funcs):
            crate = owner.get(f, "external")
            if crate in third or crate == "external":
                present += 1
                if f in forward:
                    say("COMPILED_PRESENT_AND_REACHED|unit=%s|crate=%s|function=%s|json=0" % (rel, crate, clean(demangle(f))))
                else:
                    unreached += 1
                    say("COMPILED_PRESENT_UNREACHED|unit=%s|crate=%s|function=%s|json=0" % (rel, crate, clean(demangle(f))))
        say("COMPILED_UNIT|unit=%s|mode=%s|members=%d|build_rc=0|secs=%d|ll_files=%d|mir_files=%d|project_fp_lines=%d|project_mir_lines=%d|float_functions_in_third_party_or_external=%d|of_those_unreached=%d|project_crates_reaching_a_float_function=%d|json=0" % (
            rel, "copy" if unit["copy"] else "in_place", len(unit["members"]), secs, len(lls), len(mirs), sum(project_lines.values()), sum(mir_lines.values()), present, unreached, reached_third))
        totals["built"] += 1
        totals["ll"] += len(lls)
        totals["project_fp"] += sum(project_lines.values())
        totals["mir_fp"] += sum(mir_lines.values())
        totals["reaching"] += reached_third
        totals["present"] += present
        totals["unreached"] += unreached
        compiled |= compiled_sources(target, bases, mapping)
        if not keep:
            shutil.rmtree(target, ignore_errors=True)
    if not only:
        loose_fails, loose_seen, loose_built = loose_files(root, compiled, opt, base, listed)
        fails += loose_fails
        seen_not_built |= loose_seen
        totals["loose_built"] = loose_built
        for gone in sorted(set(listed) - seen_not_built):
            fails += 1
            say("COMPILED_NOT_BUILT_ROW_STALE|path=%s|json=0" % gone)
    if not keep:
        shutil.rmtree(base, ignore_errors=True)
    say("COMPILED_RUST_DONE|manifests=%d|workspace_roots_with_no_package=%d|units=%d|built=%d|listed_not_built=%d|loose_rs_built=%d|ll_files=%d|project_fp_lines=%d|project_mir_lines=%d|project_crates_reaching=%d|float_functions_in_third_party_or_external=%d|of_those_unreached=%d|opt_level=%d|failed=%d|json=0" % (
        len(manifests), skipped, totals["units"], totals["built"], len(seen_not_built), totals["loose_built"], totals["ll"], totals["project_fp"], totals["mir_fp"], totals["reaching"], totals["present"], totals["unreached"], opt, fails))
    return 1 if fails else 0


def loose_files(root, compiled, opt, base, listed):
    fails = built = 0
    seen = set()
    for n, p in enumerate(tracked(root)):
        full = os.path.join(root, p)
        if not p.endswith(".rs") or os.path.normcase(os.path.abspath(full)) in compiled or third_party_dir(full, root) or not os.path.isfile(full):
            continue
        out = os.path.join(base, "loose%d" % n)
        os.makedirs(out, exist_ok=True)
        kind = "bin" if re.search(r"\bfn\s+main\s*\(", read_text(full)) else "lib"
        rc, _, err = run(["rustc", TOOLCHAIN, "--edition", "2021", "--crate-type", kind, "--crate-name", "loose", "-A", "warnings", "-C", "opt-level=%d" % opt, "-C", "codegen-units=1", "--emit=llvm-ir,mir", "--out-dir", out, full], root)
        if rc:
            if p in listed:
                seen.add(p)
                say("COMPILED_NOT_BUILT_LISTED|file=%s|json=0" % p)
            else:
                fails += 1
                tail = [x for x in err.strip().splitlines() if x.startswith("error")]
                say("COMPILED_NOT_BUILT|file=%s|first=%s|json=0" % (p, clean(tail[0]) if tail else "-"))
            shutil.rmtree(out, ignore_errors=True)
            continue
        built += 1
        lls, project_lines, samples, fp_funcs, edges, owner = read_ir(out, set())
        mirs, mir_lines, mir_samples = read_mir(out, set())
        if sum(project_lines.values()) or sum(mir_lines.values()):
            fails += 1
            first = samples.get("loose") or mir_samples.get("loose") or "-"
            say("COMPILED_PROJECT_FP|file=%s|lines=%d|mir_lines=%d|first=%s|json=0" % (p, sum(project_lines.values()), sum(mir_lines.values()), clean(first)))
        else:
            say("COMPILED_LOOSE|file=%s|kind=%s|project_fp_lines=0|project_mir_lines=0|json=0" % (p, kind))
        shutil.rmtree(out, ignore_errors=True)
    return fails, seen, built


def cpp_read(text):
    text = CPP_ZEROED_BLOCK.sub("", text)
    text = CPP_ZEROED_DWORD.sub("", text)
    ops = [m.group(0) for pattern in (CPP_OP, CPP_MOVE, CPP_CALL) for m in pattern.finditer(text)]
    return len(ops), ops[:3]


def cpp_one(src, cwd):
    compilers = [["gcc", "-std=gnu17"]] if src.lower().endswith(".c") else [["g++", "-std=c++23"], ["g++", "-std=c++17"]]
    first_err = ""
    with tempfile.TemporaryDirectory(prefix="compiled-asm-") as t:
        out = os.path.join(t, "a.s")
        for compiler in compilers:
            rc, _, err = run(compiler + ["-w", "-O0", "-S", src, "-o", out], cwd)
            if rc == 0:
                return (*cpp_read(read_text(out)), "")
            first_err = first_err or err
    return None, [], first_err


def cpp_check(root, only):
    root = os.path.abspath(root)
    files = [os.path.abspath(p) for p in only] if only else [os.path.join(root, p) for p in tracked(root) if p.lower().endswith((".c", ".cc", ".cpp", ".cxx"))]
    fails = measured = not_measured = 0
    for full in files:
        rel = shown(full, root)
        n, sample, err = cpp_one(full, os.path.dirname(full))
        if n is None:
            if re.search(r"gmp\w*\.h[x+]*[^\n]*No such file", err) or re.search(r"fatal error: gmp", err):
                not_measured += 1
                say("COMPILED_CPP|file=%s|result=NOT_MEASURED|reason=no_gmp_headers|json=0" % rel)
            else:
                fails += 1
                say("COMPILED_CPP_NOT_BUILT|file=%s|first=%s|json=0" % (rel, clean(err.strip().splitlines()[0] if err.strip() else "-")))
            continue
        measured += 1
        say("COMPILED_CPP|file=%s|fp_ops=%d|sample=%s|json=0" % (rel, n, clean(";".join(x.strip() for x in sample)) if sample else "-"))
        if n:
            fails += 1
    say("COMPILED_CPP_DONE|files=%d|measured=%d|not_measured=%d|failed=%d|json=0" % (len(files), measured, not_measured, fails))
    return 1 if fails else 0


C = "std::ffi::c_double"
RUST_PLANTS = (
    ("alias_division", {"src/main.rs": "fn main() { let n = std::env::args().count() as %s; let x = n / 3 as %s; println!(\"{}\", (x * 9 as %s) as u8); }" % (C, C, C)}, ("COMPILED_PROJECT_FP", "COMPILED_MIR_FP"), False),
    ("constants_folded_before_ir", {"src/main.rs": "fn main() { let x = 1 as %s / 2 as %s; let y = (x * 4 as %s) as u8; println!(\"{y}\"); }" % (C, C, C)}, ("COMPILED_MIR_FP",), False),
    ("extern_libm", {"src/main.rs": "extern \"C\" { fn sqrt(x: %s) -> %s; }\nfn main() { let y = unsafe { sqrt(2 as %s) }; println!(\"{}\", y as u8); }" % (C, C, C)}, ("COMPILED_PROJECT_FP",), False),
    ("inline_asm", {"src/main.rs": "fn main() { let (a, b) = (1i64, 3i64); let o: i64; unsafe { core::arch::asm!(\"cvtsi2sd xmm0, {a}\", \"cvtsi2sd xmm1, {b}\", \"divsd xmm0, xmm1\", \"movq {o}, xmm0\", a = in(reg) a, b = in(reg) b, o = out(reg) o, out(\"xmm0\") _, out(\"xmm1\") _); } println!(\"{o}\"); }"}, ("COMPILED_PROJECT_FP",), False),
    ("module_asm", {"src/main.rs": "core::arch::global_asm!(\".globl plant_third\", \"plant_third:\", \"cvtsi2sd xmm0, rdi\", \"ret\");\nextern \"C\" { fn plant_third(a: i64) -> i64; }\nfn main() { println!(\"{}\", unsafe { plant_third(1) }); }"}, ("COMPILED_PROJECT_FP",), False),
    ("const_eval", {"src/main.rs": "const N: u64 = (3 as %s / 2 as %s * 4 as %s) as u64;\nfn main() { println!(\"{}\", N); }" % (C, C, C)}, ("COMPILED_MIR_FP",), False),
    ("static_display", {"src/main.rs": "static X: %s = 5e-1;\nfn main() { println!(\"{}\", X); }" % C}, ("COMPILED_MIR_FP",), False),
    ("dead_private_fn", {"src/main.rs": "#[allow(dead_code)]\nfn dead() -> u8 { (1 as %s / 3 as %s) as u8 }\nfn main() { println!(\"1\"); }" % (C, C)}, ("COMPILED_MIR_FP",), False),
    ("generic_by_alias", {"src/main.rs": "fn half<T: std::ops::Div<Output = T> + From<u8>>(a: T) -> T { a / T::from(2u8) }\nfn main() { let v: %s = half(3u8.into()); println!(\"{}\", v as u8); }" % C}, ("COMPILED_PROJECT_FP",), False),
    ("sse_intrinsic", {"src/main.rs": "use std::arch::x86_64::*;\nfn main() { let v = unsafe { _mm_cvtsi128_si64(_mm_castpd_si128(_mm_div_sd(_mm_cvtsi32_sd(_mm_setzero_pd(), 1), _mm_cvtsi32_sd(_mm_setzero_pd(), 3)))) }; println!(\"{v}\"); }"}, ("COMPILED_PROJECT_FP",), False),
    ("include_text_file", {"src/main.rs": "include!(\"helper.inc\");\nfn main() { println!(\"{}\", third() as u8); }", "src/helper.inc": "fn third() -> %s { 1 as %s / 3 as %s }" % (C, C, C)}, ("COMPILED_PROJECT_FP",), False),
    ("build_script_output", {"src/main.rs": "include!(concat!(env!(\"OUT_DIR\"), \"/gen.rs\"));\nfn main() { println!(\"{}\", third() as u8); }", "build.rs": "fn main() { let d = std::env::var(\"OUT_DIR\").unwrap(); std::fs::write(d + \"/gen.rs\", \"fn third() -> %s { 1 as %s / 3 as %s }\").unwrap(); }" % (C, C, C)}, ("COMPILED_PROJECT_FP",), False),
    ("test_only_module", {"src/main.rs": "fn main() { println!(\"1\"); }\n#[cfg(test)]\nmod t { #[test] fn x() { let y = 1 as %s / 3 as %s; assert!(y > 0 as %s); } }" % (C, C, C)}, ("COMPILED_MIR_FP",), False),
    ("path_dependency", {"src/main.rs": "fn main() { println!(\"{}\", helper::third()); }", "Cargo.toml+": "helper = { path = \"helper\" }\n", "helper/Cargo.toml": "[package]\nname = \"helper\"\nversion = \"0.1.0\"\nedition = \"2021\"\n", "helper/src/lib.rs": "pub fn third() -> u8 { (1 as %s / 3 as %s * 9 as %s) as u8 }" % (C, C, C)}, ("COMPILED_MIR_FP",), False),
    ("vendored_sqrt_default_features", {"src/main.rs": "fn main() { println!(\"{}\", num_bigint::BigInt::from(2).pow(200).sqrt()); }", "Cargo.toml+": "num-bigint = \"0.4\"\n"}, ("COMPILED_REACH", "COMPILED_MANIFEST"), True),
    ("vendored_display_names_std", {"src/main.rs": "fn main() { println!(\"{}\", num_bigint::BigInt::from(2).pow(200)); }", "Cargo.toml+": "num-bigint = { version = \"0.4\", default-features = false, features = [\"std\"] }\n"}, ("COMPILED_REACH", "COMPILED_MANIFEST"), True),
    ("vendored_parse_through_a_table", {"src/main.rs": "fn main() { let v: num_bigint::BigInt = \"12345678901234567890123\".parse().unwrap(); println!(\"{}\", v.bits()); }", "Cargo.toml+table": "[dependencies.num-bigint]\nversion = \"0.4\"\n"}, ("COMPILED_REACH", "COMPILED_MANIFEST"), True),
    ("workspace_feature_unification", {"src/main.rs": "fn main() { println!(\"{}\", other::go() + num_bigint::BigInt::from(2).pow(200).sqrt().bits()); }", "Cargo.toml+": "num-bigint = { version = \"0.4\", default-features = false }\nother = { path = \"other\" }\n", "other/Cargo.toml": "[package]\nname = \"other\"\nversion = \"0.1.0\"\nedition = \"2021\"\n[dependencies]\nnum-bigint = \"0.4\"\n", "other/src/lib.rs": "pub fn go() -> u64 { num_bigint::BigInt::from(3).bits() }"}, ("COMPILED_REACH",), True),
)
RUST_CONTROLS = (
    ("clean_bigint", {"src/main.rs": "fn main() { let n: num_bigint::BigInt = num_bigint::BigInt::from(2).pow(200) + 1; let s = n.to_string(); let p: num_bigint::BigInt = s.parse().unwrap(); println!(\"{} {}\", n.sqrt(), p == n); }", "Cargo.toml+": "num-bigint = { version = \"0.4\", default-features = false }\n"}, True),
    ("names_only", {"src/main.rs": "#[allow(non_camel_case_types)]\nstruct double(u8);\nfn float() -> u8 { 1 }\nmod fadd { pub fn half() -> u8 { 2 } }\nfn main() { let f64 = double(float()); println!(\"{} {} double float fadd 0.5 f64\", f64.0, fadd::half()); }"}, False),
    ("wide_integers", {"src/main.rs": "fn main() { let a: u128 = 340282366920938463463374607431768211455; let b = a / 3 + a % 7; let v: Vec<u128> = (0..9).map(|i| b >> i).collect(); println!(\"{:?}\", v); }"}, False),
)
CPP_PLANTS = (
    ("plain_double", "int main() { volatile double a = 1; volatile double b = 3; return static_cast<int>(a / b * 9); }\n"),
    ("float_suffix_exponent", "int main() { auto x = 1e5f; return static_cast<int>(x) & 1; }\n"),
    ("float64_type", "int main() { volatile _Float64 a = 3; volatile _Float64 b = 2; return static_cast<int>(a / b); }\n"),
    ("long_double_x87", "int main() { volatile long double a = 1; volatile long double b = 3; return static_cast<int>(a / b * 9); }\n"),
    ("quad_soft_float", "int main() { volatile __float128 a = 1; volatile __float128 b = 3; return static_cast<int>(a / b * 9); }\n"),
    ("decimal_soft_float.c", "int main(void) { volatile _Decimal64 a = 3; volatile _Decimal64 b = 2; return (int)(a / b); }\n"),
    ("cmath_no_float_word", "#include <cmath>\nint main() { return static_cast<int>(std::sqrt(2)); }\n"),
    ("builtin_sqrt", "int main() { volatile int n = 2; return static_cast<int>(__builtin_sqrt(n)); }\n"),
    ("stod_no_float_word", "#include <string>\nint main() { auto v = std::stod(\"0.5\"); return static_cast<int>(v * 2); }\n"),
    ("random_real", "#include <random>\nint main() { std::mt19937 g; std::uniform_real_distribution<> d(0, 1); return static_cast<int>(d(g)); }\n"),
    ("sse_intrinsic", "#include <emmintrin.h>\nint main() { __m128d a = _mm_cvtsi32_sd(_mm_setzero_pd(), 1); __m128d b = _mm_cvtsi32_sd(_mm_setzero_pd(), 3); return static_cast<int>(_mm_cvtsi128_si64(_mm_castpd_si128(_mm_div_sd(a, b))) & 1); }\n"),
    ("inline_asm", "int main() { long long o, a = 1, b = 3; __asm__(\"cvtsi2sdq %1,%%xmm0\\n cvtsi2sdq %2,%%xmm1\\n divsd %%xmm1,%%xmm0\\n movq %%xmm0,%0\" : \"=r\"(o) : \"r\"(a), \"r\"(b) : \"xmm0\", \"xmm1\"); return static_cast<int>(o & 1); }\n"),
)
CPP_CONTROLS = (
    ("wide_integer_moves", "int main() { volatile __int128 a = 7; volatile __int128 b = a * a; __int128 c[4] = {a, b, a, b}; __int128 d[4]; for (int i = 0; i < 4; i++) d[i] = c[i]; return static_cast<int>(d[1] % 5); }\n"),
    ("vector_string", "#include <string>\n#include <vector>\nint main() { std::vector<std::string> v{\"a\", \"b\"}; v.push_back(std::to_string(12)); return static_cast<int>(v.size()); }\n"),
)
FAIL_TAGS = ("COMPILED_PROJECT_FP", "COMPILED_MIR_FP", "COMPILED_REACH", "COMPILED_MANIFEST", "COMPILED_NOT_BUILT", "COMPILED_CPP|")


def write_plant(where, name, files, vendored):
    os.makedirs(where, exist_ok=True)
    manifest = "[package]\nname = \"plant_%s\"\nversion = \"0.1.0\"\nedition = \"2021\"\n\n[dependencies]\n%s\n%s[workspace]\n" % (name, files.get("Cargo.toml+", ""), files.get("Cargo.toml+table", ""))
    if "build.rs" in files:
        manifest = manifest.replace("edition = \"2021\"\n", "edition = \"2021\"\nbuild = \"build.rs\"\n")
    for rel, body in files.items():
        if rel.startswith("Cargo.toml+"):
            continue
        p = os.path.join(where, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
    with open(os.path.join(where, "Cargo.toml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(manifest)


def plants(root, lang):
    root = os.path.abspath(root)
    me = os.path.abspath(__file__)
    fails = red = green = 0
    if lang == "rust":
        vendored_home = os.path.join(root, "native", "ym", "results")
        scratch = tempfile.mkdtemp(prefix="compiled-plants-")
        for name, files, expect, vendored in RUST_PLANTS:
            where = os.path.join(vendored_home if vendored else scratch, ".plant-" + name)
            rc, stdout = plant_run(root, me, where, name, files, vendored)
            missing = [t for t in expect if not re.search(r"^%s\|" % t, stdout, re.M)]
            ok = rc == 1 and not missing
            red += ok
            fails += not ok
            say("PLANT|lang=rust|name=%s|rc=%d|expect=%s|missing=%s|result=%s|json=0" % (name, rc, ",".join(expect), ",".join(missing) or "-", "RED" if ok else "WRONG"))
            shutil.rmtree(where, ignore_errors=True)
        for name, files, vendored in RUST_CONTROLS:
            where = os.path.join(vendored_home if vendored else scratch, ".control-" + name)
            rc, stdout = plant_run(root, me, where, name, files, vendored)
            ok = rc == 0
            green += ok
            fails += not ok
            say("CONTROL|lang=rust|name=%s|rc=%d|result=%s|json=0" % (name, rc, "GREEN" if ok else "WRONG"))
            if not ok:
                say(stdout[:1500])
            shutil.rmtree(where, ignore_errors=True)
        shutil.rmtree(scratch, ignore_errors=True)
        total, ctl = len(RUST_PLANTS), len(RUST_CONTROLS)
    else:
        scratch = tempfile.mkdtemp(prefix="compiled-plants-")
        for name, body in CPP_PLANTS:
            p = os.path.join(scratch, name if name.endswith(".c") else name + ".cpp")
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(body)
            rc, stdout, _ = run([sys.executable, "-I", "-X", "utf8", me, "cpp", root, "--only", p], root)
            hit = re.search(r"\|fp_ops=([1-9]\d*)\|", stdout) is not None
            ok = rc == 1 and hit
            red += ok
            fails += not ok
            say("PLANT|lang=cpp|name=%s|rc=%d|read=%s|result=%s|json=0" % (name, rc, clean(stdout.splitlines()[0] if stdout else "-"), "RED" if ok else "WRONG"))
        for name, body in CPP_CONTROLS:
            p = os.path.join(scratch, name + ".cpp")
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(body)
            rc, stdout, _ = run([sys.executable, "-I", "-X", "utf8", me, "cpp", root, "--only", p], root)
            ok = rc == 0
            green += ok
            fails += not ok
            say("CONTROL|lang=cpp|name=%s|rc=%d|read=%s|result=%s|json=0" % (name, rc, clean(stdout.splitlines()[0] if stdout else "-"), "GREEN" if ok else "WRONG"))
        shutil.rmtree(scratch, ignore_errors=True)
        total, ctl = len(CPP_PLANTS), len(CPP_CONTROLS)
    say("PLANTS_DONE|lang=%s|plants=%d|red=%d|controls=%d|green=%d|failed=%d|json=0" % (lang, total, red, ctl, green, fails))
    return 1 if fails else 0


def plant_run(root, me, where, name, files, vendored):
    shutil.rmtree(where, ignore_errors=True)
    write_plant(where, name, files, vendored)
    # A plant with a path dependency locks it too; the crates come from the vendor folder or from nowhere, so this stays offline.
    code, _, err = run(["cargo", TOOLCHAIN, "generate-lockfile", "--offline"], where)
    if code:
        return 3, "lockfile: " + err[:400]
    rc, stdout, stderr = run([sys.executable, "-I", "-X", "utf8", me, "rust", root, "--only", os.path.join(where, "Cargo.toml")], root)
    return rc, stdout + stderr


IR_MUST_FLAG = (
    "  %1 = fdiv double %a, %b", "  %2 = uitofp i64 %x to double", "  %3 = fptosi double %x to i64", "  %x = alloca double, align 8", "declare double @sqrt(double)",
    '%"t" = type { double, i64 }', "  store <2 x double> %a, ptr %b, align 16", '  %5 = call i64 asm sideeffect alignstack inteldialect "cvtsi2sd xmm0, ${0:q}", "=r,r,~{xmm0}"(i64 %a)',
    'module asm "divsd xmm0, xmm1"', "  %6 = fneg float %x", "  %7 = fcmp olt half %x, %y", "  %8 = bitcast i64 %x to double",
)
IR_MUST_PASS = (
    "define void @_ZN5float6double17h0123456789abcdefE() {", '  call void @"float::double::fadd"()', '@alloc = private unnamed_addr constant [12 x i8] c"double float", align 1',
    "; float comment double", 'source_filename = "float.double"', '  %_5 = call i64 asm sideeffect alignstack inteldialect "div {0}", "=r,r,~{dirflag},~{fpsr},~{flags}"(i64 %a)',
    "  %halfway = add i64 %double, %half", 'attributes #0 = { nounwind "target-features"="+fxsr,+sse,+sse2" "denormal-fp-math"="dynamic" }', "  %x = mul i128 %a, %b", "  %y = load <2 x i64>, ptr %p, align 16",
)
MIR_MUST_FLAG = ("let _1: f64;", "fn f(_1: f32) -> u8 {", "_0 = const 5e-1_f64;", "_2 = const 1f32;", "static X: f64 = {", "_3 = <f64 as Display>::fmt(move _4) -> [return: bb1, unwind: bb2];")
MIR_MUST_PASS = ('_1 = const "f64 0.5";', "let _1: u64;", "_2 = foo_f64() -> [return: bb1, unwind: bb2];", "let _1: myf32;")
CPP_MUST_FLAG = ("\tdivsd\t%xmm1, %xmm0\n", "\tmovsd\t-8(%rbp), %xmm0\n", "\tcvtsi2sdq\t%rax, %xmm0\n", "\tfldt\t16(%rbp)\n", "\tmovq\t%xmm0, %rax\n", "\tcall\tsqrt\n", "\tcall\t__divtf3\n", "\tcall\t__bid_divdd3\n", "\tcall\tsqrt@PLT\n", "\tvaddsd\t%xmm1, %xmm0, %xmm0\n", "\tpxor\t%xmm1, %xmm1\n\tmovq\t%xmm0, -8(%rbp)\n", "\tpxor\t%xmm0, %xmm0\n\tmovsd\t%xmm0, -8(%rbp)\n")
CPP_MUST_PASS = ("\tmovaps\t%xmm0, -32(%rbp)\n", "\tmovdqa\t-48(%rbp), %xmm0\n", "\tcall\t__divti3\n", "\tcall\t__udivti3\n", "\tcall\t__modti3\n", "\tcall\t__multi3\n", "\tmovq\t%rax, %rdx\n", "\tcall\t_Z4sqrti\n", "\t.file\t\"float.cpp\"\n", "\tmovl\t$0, %r8d\n", "\tpxor\t%xmm0, %xmm0\n\tmovaps\t%xmm0, -240(%rbp)\n\tmovq\t%xmm0, -224(%rbp)\n")


# Explicit integer-zero controls and scalar-floating instruction controls.
# Keep the register sigil as a character to avoid interpreting the fixtures
# as Python percent formatting by the strict source audit.
_ASM_REG_SIGIL = chr(37)
CPP_MUST_PASS += (
    f"\tpxor\t{_ASM_REG_SIGIL}xmm0, {_ASM_REG_SIGIL}xmm0\n\tmovups\t{_ASM_REG_SIGIL}xmm0, ({_ASM_REG_SIGIL}rax)\n\tmovd\t{_ASM_REG_SIGIL}xmm0, {_ASM_REG_SIGIL}ecx\n",
    f"\tpxor\t{_ASM_REG_SIGIL}xmm0, {_ASM_REG_SIGIL}xmm0\n\tmovups\t{_ASM_REG_SIGIL}xmm0, 18({_ASM_REG_SIGIL}rax)\n\tmovups\t{_ASM_REG_SIGIL}xmm0, 34({_ASM_REG_SIGIL}rax)\n\tmovd\t{_ASM_REG_SIGIL}xmm0, 50({_ASM_REG_SIGIL}rax)\n",
)
CPP_MUST_FLAG += (
    f"\tmovd\t{_ASM_REG_SIGIL}xmm0, 50({_ASM_REG_SIGIL}rax)\n",
    f"\tpxor\t{_ASM_REG_SIGIL}xmm0, {_ASM_REG_SIGIL}xmm0\n\taddsd\t{_ASM_REG_SIGIL}xmm1, {_ASM_REG_SIGIL}xmm0\n\tmovd\t{_ASM_REG_SIGIL}xmm0, 50({_ASM_REG_SIGIL}rax)\n",
)

def mir_flag(line):
    s = line.strip()
    return not s.startswith(("//", "debug ", "scope ")) and MIR_FP.search(MIR_STRING.sub('""', s)) is not None


def selftest():
    fails = 0
    for line in IR_MUST_FLAG:
        if not ir_line_has_float(line):
            fails += 1
            say("SELFTEST|missed_ir=%s|json=0" % clean(line))
    for line in IR_MUST_PASS:
        if ir_line_has_float(line):
            fails += 1
            say("SELFTEST|flagged_ir=%s|json=0" % clean(line))
    for line in MIR_MUST_FLAG:
        if not mir_flag(line):
            fails += 1
            say("SELFTEST|missed_mir=%s|json=0" % clean(line))
    for line in MIR_MUST_PASS:
        if mir_flag(line):
            fails += 1
            say("SELFTEST|flagged_mir=%s|json=0" % clean(line))
    for line in CPP_MUST_FLAG:
        if not cpp_read(line)[0]:
            fails += 1
            say("SELFTEST|missed_asm=%s|json=0" % clean(line.strip()))
    for line in CPP_MUST_PASS:
        if cpp_read(line)[0]:
            fails += 1
            say("SELFTEST|flagged_asm=%s|json=0" % clean(line.strip()))
    say("COMPILED_SELFTEST_DONE|ir_flag=%d|ir_pass=%d|mir_flag=%d|mir_pass=%d|asm_flag=%d|asm_pass=%d|failed=%d|json=0" % (len(IR_MUST_FLAG), len(IR_MUST_PASS), len(MIR_MUST_FLAG), len(MIR_MUST_PASS), len(CPP_MUST_FLAG), len(CPP_MUST_PASS), fails))
    return 1 if fails else 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "selftest":
        return selftest()
    root = argv[2] if len(argv) > 2 else "."
    rest = argv[3:]
    only, opt, keep, i = [], 0, None, 0
    while i < len(rest):
        if rest[i] == "--only":
            only.append(rest[i + 1])
            i += 2
        elif rest[i] == "--opt-level":
            opt = int(rest[i + 1])
            i += 2
        elif rest[i] == "--keep":
            keep = rest[i + 1]
            i += 2
        else:
            i += 1
    if cmd == "rust":
        return rust_check(root, only, opt, keep)
    if cmd == "cpp":
        return cpp_check(root, only)
    if cmd == "plants":
        return plants(root, rest[0])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
