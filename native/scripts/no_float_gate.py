#!/usr/bin/env python3
"""
The operator's rule, November 3, 2026: "We can't use float." His direction for this gate: "The gate must reject operations capable of silently
introducing floating-point values." "Rust 1.81, Python, and every mathematical verifier must use exact integers, integer numerator/denominator
pairs, or explicitly certified algebraic-number representations." "No unsupported claims of complete protection."

It reads the blob of every tracked file, as git holds it, and fails on what it finds apart from what FLOAT-EVIDENCE.txt, beside this file, lists.

The list. A file row reads path | findings=N | sha256=H | reason, with N the findings counted in that file and H the sha256 of its blob. A folder row
reads folder/ | tree=H | reason, with H a sha256 over the mode, blob sha256 and path of every tracked entry under the folder. So a finding swapped for
another at the same count, a new file under a folder and an edited byte all fail. A reason must hold a letter, and a path may appear once. --pins prints
N and H for the paths a person names, with the reason left for that person to write. Rows are written by hand.

What it reads, by the lower-cased name:

Python: .py .pyw .pyi, and any file whose first line is a shebang naming python or pypy, whatever its name. It decodes as CPython does. A BOM is read through,
a coding cookie that decodes to anything but UTF-8 is a finding, and the syntax tree comes from CPython's own parse, so the cookie's reading is what gets
read. A file that fails to parse is one finding, and so is an expression too deep to read. On the tree:
float and complex literals; the names float and complex, except as the type being tested in isinstance, issubclass or a type() comparison; eval, exec,
compile, __import__, globals, vars, locals, setattr, delattr and __builtins__ as names; .eval, .exec, .__import__ and .compile outside re as attributes;
imports of numpy, scipy, mpmath, decimal, fractions, sympy, pandas, torch, statistics, cmath, timeit, ctypes, importlib, json, pickle, marshal, shelve,
tomllib, toml, yaml, plistlib, resource and psutil; any import outside a short allowed list of the standard library and outside the tracked Python; runpy,
builtins, inspect, types and the other modules that execute or rebind; private modules; a star import of an untracked module; a from-import of any denied
attribute name, from any module; a watched module reached through another module; an imported module passed around as a value;
any attribute of math, time or random outside their integer parts, through aliases and from-imports; the float methods of Random on any receiver, choices and
binomialvariate among them; a named list of attributes that return floats, and .pow; reflection attributes such as __self__, __dict__, __globals__ and
f_globals; a store into a module; sys.modules; getattr as a value, with a name the source does not show, or of a denied name; attrgetter and methodcaller the
same way; a call through __class__ or type(v); three-argument type(); __prepare__; class patterns that read a denied attribute; ast.parse;
struct and array calls with a float code or a format the source does not show, through aliases and from-imports, where a format built on struct itself by + and *
from visible strings counts as shown; .cast the same way;
true division, / and /=, unless a string, an f-string or Path(...) operand along the chain of joins, or a name whose every binding in the file comes from
Path, marks it as a path join, with that reading void where the file defines __truediv__ or rebinds Path, and where a concatenation on the chain holds a call other
than str and its kin or the file defines __add__ or __radd__;
** and two-argument pow unless the exponent is provably non-negative from the source: a non-negative literal, len, abs, min, max or % whose every operand
is proven, a range index, a comprehension's own target, or a sum or product of these, with every binding of a name in the file proven. A rebound builtin, a
star import, a numeric dunder or an int subclass in the file voids what depends on it, and a pow whose modulus may be None counts. Such a power is written
with an integer power that refuses a negative exponent, or with three-argument pow;
format specs, str.format, format(), and %-formats read by CPython's grammar, in any string and on the left of %, with a built format string on the left of %
counting too. The literal first argument of a strftime the file does not bind itself, and an f-string spec opening with %, are date formats and pass. The narrowings
that read isinstance, issubclass, type, bytes and bytearray hold only where the file leaves those names unbound.

Rust, .rs, with comments and strings removed across lines: f16 f32 f64 f128, to_f32 and its kin, the Float trait, hexf64, 1f64, 0.5, 2., 1e9 with underscores
anywhere in the exponent; c_double, c_float, c_longdouble and the named float crates; asm!, global_asm!, naked_asm!, intrinsics and std::arch; doc-test fences
that rustdoc would run; the plain forms of include! and #[path] with a target outside .rs.
C and C++, .c .h .cc .cxx .cpp .hh .hpp .c++ .cp .hxx .h++ .inl .ipp .tcc .txx, after line splices and the # digraph and trigraph: float, double, the _Float and
__float and _Decimal families, float64_t, _Complex, mpf and mpfr; every literal form with suffixes and digit separators; the float functions of the C library,
__builtin_ names outside the integer ones, DBL_ and FLT_ macros, the real distributions of <random>, std::numbers, ##, asm and intrinsics; float headers, and a
quoted include of a file the scan does not read.
Go, .go: float32, float64, complex64, complex128, math.*, the same literals, imaginary literals, ParseFloat, FormatFloat, Float32, Float64, big.Float, big.Rat,
Seconds, Minutes, Hours, and imports of math, math/rand, math/cmplx, encoding/json and C.
JavaScript and TypeScript, .js .mjs .cjs .ts .jsx .tsx .mts .cts, with comments, strings and regex literals blanked and template holes kept: Math, Number,
parseFloat, toFixed, toPrecision, toExponential, float arrays and DataView float calls, JSON, performance, globalThis, eval, Function, Reflect, NaN, Infinity,
unicode escapes in code, an integer literal of 16 or more digits, the same float literals; ** unless the exponent is a BigInt literal; arithmetic on a string;
and every / left in the code, across lines and in template holes, since a JavaScript number is a double, unless a BigInt literal sits on either side of it or
BigInt( on its right, or, in .jsx and .tsx, it closes a tag.
HTML and its relatives, .html .htm .xhtml .xht .shtml .svg .vue .svelte: script bodies and on* handlers under that reader, script src, srcdoc and javascript:.
Page text and CSS stay out of the reading.

Every tracked entry: a symlink; a submodule; a blob this clone does not hold; a .gitattributes holding filter, working-tree-encoding or ident; an LFS pointer in a
code path; NUL or non-UTF-8 bytes in native code; compiled or archived Python by name, or any blob with a zip directory in its last 66000 bytes; Python by another
extension (.pyx .pxd .pxi .ipy .sage .ipynb .py3 .rpy .pyde); text up to 1 MiB under any other name that parses as Python and holds an import, def, class,
assignment or call with a finding in it; a shell header that hands the file to Python; a line in .sh .bash .yml .yaml .ps1 .cmd .bat .mk that runs a tracked file
of another name under python; build.rs, a proc-macro crate, a Cargo target outside .rs, a dependency that leaves the tree, and a crate outside a short allowed
list, in Cargo.toml and Cargo.lock.

Limits.
A pass means these checks found nothing in what they read. It is evidence and no proof of integer-only execution. The checked_division runs and the receipts are
the measurements for specific scripts. Compiler-level checks, LLVM IR for Rust and assembly for C++, hold the type information this scan lacks and caught every plant
tried, on plants and a sample of real crates; they cover compiled code only.
Written rules did not converge. The second seat's candidate reading rules flagged 175 of 178 measured bypasses on the plants they were written from and 9 of 20 on
plants written afterwards, with the three candidate rules left out here among them; the rules kept here flag 6 of those 20. The next plant may pass.
It reads each tracked file's source alone, with no types, no values, no call graph and no view across files or into a run. A float returned by any function it does
not name passes it, and a vendored library can run f64 inside an integer-looking call: num-bigint with default features does so in BigInt::sqrt, Display and parse.
It cannot tell a format string from an integer on the left of %: s % v on two names passes, and s may hold %f built at run time.
It cannot see a value crossing a call: pow(a, -1, m) passes, and m = None from a caller makes it two-argument pow.
Its non-negative proofs hold for plain ints and for this file's own bindings. Another file can rebind a module's name through a route the scan does not name.
Denied names close what they name. An object from an allowed module can hand back a float through an attribute or an index that no list holds, as
socket.socket().timeout and os.wait4(...)[2][0] do.
Standard library functions can use floats inside and return integers. Random.sample uses _ceil(_log(k * 3, 4)) and stays allowed here; whether its lines count as
integer-only execution is an open decision.
A child process is outside it: subprocess, os.popen, awk, bc and python -c return text from any program.
Code written at run time is outside it: generated files, git show <sha>:file > x.py, pip installs, a shell that assembles a command in a variable, and a program that
writes a file and imports it, including under the name of a clean tracked module. For build.rs and proc macros it flags that they exist, and reads their code as any
other Rust.
Data is outside it: an integer read from a file may be the rounded output of a float run.
Third-party code is outside it. An import outside the allowed list draws a finding, and a row can then keep it; what that package does stays unread.
Shell scripts, inline workflow code, Makefiles, Dockerfiles, assembler, Lean, Perl, Java, Fortran, SQL and PowerShell are outside its reading, and notebooks and
.pyx files are flagged by name and left unread. The second seat's rules types, inline_shell and import_listed are left out for their cost on the three trees: 18, 14
and 12 rows, most of them true of harmless files. So an awk, bc, perl, node or dc line in a script passes, and a clean file may import a listed one.
The interpreter's environment is outside it: PYTHONPATH, sitecustomize and a missing -I change what other scripts run. This gate refuses to run without -I, and that is
as far as it reaches.
The parse belongs to whichever python3 runs it. Python 3.14 t-strings and any newer struct or array float codes are unread until a rule names them.
Its JavaScript reading is partial: integer-looking products above 2^53 and negative zero pass, and a / b on BigInt variables is flagged for want of types. A -D on a
compiler line is outside it. include! with brackets, braces or env!, #[path = r"..."], and a renamed asm pass it, as measured on the held-out plants.
The list: nothing checks what a reason says. A row is true of its file, and a listed file can be imported by a file that reads clean, so review each listed exec site for
whether it takes its code from a caller. A pin stops a later change to a listed file; a float added in the same change as its own pinned row passes this scan, because
the list is in that change.
The gate, its list and its workflow live in the pull request they check. no_float.yml runs the pull request's own copies. no_float_base.yml runs the base commit's gate
over the pull request's list and files as data, and flags any change to the gate, the list or either workflow for a person to read. Hosted behaviour of both is NOT_MEASURED
until a pull request runs them; a throwaway repository settles it, along with whether a second job of the same name muddies a required check.
A pull request that changes a rule so that a listed count moves reads differently under its own gate and the base gate, so one of the two jobs stays red until a person acts.
It reads what the index holds. A file edited and left unstaged is read as it was staged. A file above 1 MiB, or one holding a NUL, under a name the scan does not read stays unparsed.
Executing the attackers' Go, Ruby, Kotlin, Swift, Zig, Julia, Lua, Lean, Vue, Svelte, WAT, Cython and Docker plants is NOT_MEASURED, for want of a toolchain here, so what those rows hold is known by reading.

usage: no_float_gate.py [ROOT]          Scans ROOT. Exits 1 on a finding that is not listed, a moved count or pin, a bad row, or when no code is read.
       no_float_gate.py --selftest      Runs the snippets below. Exits 1 if one is misread. Integer only, json=0.
       no_float_gate.py --pins PATH...  Run from the repository root. Prints each path's row up to its reason: a file, or a folder ending in /.
Run it as python3 -I -X utf8.
"""
import sys

if __name__ == "__main__" and not sys.flags.isolated:
    # Without -I a tracked ast.py or re.py beside this file would load in place of the standard module.
    print("NO_FLOAT|needs_python3_-I=1|json=0")
    sys.exit(1)

import ast
import codecs
import hashlib
import html
import io
import os
import re
import string
import subprocess
import tokenize
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
LIST_NAME = "FLOAT-EVIDENCE.txt"
BAD_IMPORT = {"numpy", "scipy", "mpmath", "decimal", "fractions", "sympy", "pandas", "torch", "statistics", "cmath", "timeit", "ctypes", "importlib", "json", "pickle", "marshal", "shelve", "tomllib", "toml", "yaml", "plistlib", "resource", "psutil"}
# The integer parts of these modules. Any other attribute of them counts.
MATH_OK = {"isqrt", "gcd", "lcm", "factorial", "comb", "perm", "floor", "ceil", "trunc", "prod"}
TIME_OK = {"time_ns", "monotonic_ns", "perf_counter_ns", "process_time_ns", "thread_time_ns", "sleep", "gmtime", "localtime", "strftime", "struct_time", "timezone", "altzone", "daylight", "tzname", "ctime", "asctime"}
RANDOM_OK = {"Random", "SystemRandom", "seed", "getstate", "setstate", "randrange", "randint", "getrandbits", "randbytes", "choice", "shuffle", "sample"}
WATCHED = {"math": MATH_OK, "time": TIME_OK, "random": RANDOM_OK}
RANDOM_METHODS = {"random", "uniform", "gauss", "normalvariate", "betavariate", "expovariate", "gammavariate", "lognormvariate", "weibullvariate", "vonmisesvariate", "paretovariate", "triangular", "choices", "binomialvariate"}
BAD_ATTRIBUTE = {"truediv", "__truediv__", "__rtruediv__", "__itruediv__", "__float__", "__complex__", "fromhex", "getmtime", "getatime", "getctime", "st_mtime", "st_atime", "st_ctime", "total_seconds", "timestamp", "default_timer", "import_module", "literal_eval", "float", "complex", "__pow__", "__rpow__", "__ipow__", "ipow", "float_info", "getswitchinterval", "getloadavg", "as_integer_ratio"}
BAD_NAME = {"float", "complex", "eval", "exec", "compile", "__import__", "globals", "vars"}
STRUCT_CALLS = {"pack", "pack_into", "unpack", "unpack_from", "iter_unpack", "calcsize", "Struct"}
BAD_STRING = {"__truediv__", "__float__", "__pow__"}
FLOAT_SPEC = re.compile(r"[eEfFgG%]$")
FORMAT_FIELD = re.compile(r"\{[^{}]*:[^{}]*[eEfFgG%]\}")
PERCENT_FLOAT = re.compile(r"(?<!%)%(\([^)]*\))?[-+#0]*(\*|\d+)?(\.(\*|\d+))?[eEfFgG]")
PY_EXT = (".py", ".pyw", ".pyi")
BOUND_BUILTINS = ("len", "abs", "max", "min", "range", "enumerate")
# A narrowing that reads these names proves nothing where the file binds them.
NARROWING_BUILTINS = ("isinstance", "issubclass", "type", "bytes", "bytearray")
NUM_DUNDERS = {"__abs__", "__mod__", "__rmod__", "__gt__", "__lt__", "__ge__", "__le__", "__add__", "__radd__", "__mul__", "__rmul__", "__and__", "__rand__", "__or__", "__ror__", "__xor__", "__rxor__", "__lshift__", "__rlshift__", "__rshift__", "__rrshift__", "__floordiv__", "__rfloordiv__", "__pow__", "__rpow__", "__index__", "__int__", "__truediv__", "__rtruediv__"}
EXT_DUNDERS = {"__truediv__", "__rtruediv__", "__itruediv__", "itruediv", "__pow__", "__rpow__", "__ipow__", "ipow", "__complex__", "__float__", "__format__"}
EXT_BAD = BAD_ATTRIBUTE | RANDOM_METHODS | BAD_NAME | EXT_DUNDERS | {"pow", "__import__", "itruediv", "format", "format_map", "vformat", "format_field", "times", "st_birthtime"}
IMPORT_BAD = BAD_ATTRIBUTE | RANDOM_METHODS | BAD_NAME | EXT_DUNDERS | {"__import__"}
REFLECT_ATTR = {"__self__", "__setattr__", "__delattr__", "cell_contents", "__subclasses__", "__bases__", "__base__", "__mro__", "mro", "__dict__", "__globals__", "__builtins__", "__code__", "__closure__", "__getattribute__", "f_globals", "f_locals", "f_builtins", "f_code", "tb_frame", "gi_frame", "cr_frame", "ag_frame", "_getframe", "currentframe", "get_referrers", "get_referents", "get_objects", "get_type_hints", "getmembers", "getattr_static"}
EXEC_IMPORTS = {"builtins", "__main__", "inspect", "types", "gc", "runpy", "code", "codeop", "pkgutil", "pydoc", "doctest", "cProfile", "profile", "pstats", "trace", "pdb", "bdb", "zipimport", "site"}
MORE_ATTRS = {"times", "st_birthtime", "getfloat", "atof", "TIMEOUT_MAX", "created", "msecs", "relativeCreated", "ratio", "quick_ratio", "real_quick_ratio", "QUOTE_NONNUMERIC", "QUOTE_STRINGS", "QUOTE_NOTNULL", "ONE_THIRD", "ONE_SIXTH", "TWO_THIRD", "rgb_to_hsv", "rgb_to_hls", "rgb_to_yiq", "hsv_to_rgb", "hls_to_rgb", "yiq_to_rgb", "read_floatnl", "read_float8", "getdefaulttimeout", "gettimeout", "timefunc", "getstats", "totaltime", "inlinetime", "sched_rr_get_interval", "getitimer", "setitimer", "getloadavg", "_time", "_startTime", "ru_utime", "ru_stime"}
# With import_allow, an import outside this list and outside the tracked Python is a finding.
ALLOW_STDLIB = {"__future__", "sys", "os", "re", "math", "time", "random", "struct", "array", "hashlib", "subprocess", "pathlib", "itertools", "collections", "functools", "operator", "contextlib", "bisect", "heapq", "copy", "tempfile", "shutil", "io", "argparse", "atexit", "unittest", "tokenize", "ast", "datetime", "gzip", "zipfile", "urllib", "http", "threading", "socket", "signal", "concurrent", "numbers"}
STR_METHODS = {"join", "format", "format_map", "replace", "strip", "lstrip", "rstrip", "lower", "upper", "title", "capitalize", "swapcase", "center", "ljust", "rjust", "zfill", "expandtabs", "translate", "decode", "encode", "removeprefix", "removesuffix"}
ARGV_LIKE = {"argv", "stdout", "stderr", "stdin"}
GRAMMAR_FLOAT_SPEC = re.compile(r"^(?:.?[<>=^])?[-+ ]?z?#?0?(?:\d+|\{\w*\})?[,_]?(?:\.(?:\d+|\{\w*\}))?[eEfFgG%]$")
FIELD_NAME = re.compile(r"^\w*(?:\.\w+|\[\w+\])*$")
W_NAMES = set(WATCHED) | BAD_IMPORT | {"struct", "array", "builtins"}
PERCENT_CONV = "eEfFgG"
BARE_SPEC = re.compile(r"^.?[<>=^]?[-+ ]?z?#?0?\d*[,_]?\.\d+[eEfFgG%]$")
BRACE_ATTR = re.compile(r"\{[^{}:!]*\.(\w+)")
PROVEN_BINOPS = (ast.Add, ast.Mult, ast.FloorDiv, ast.BitAnd, ast.BitOr, ast.BitXor, ast.RShift, ast.LShift, ast.Pow)
AUG_PROVEN = (ast.Add, ast.Mult, ast.FloorDiv, ast.RShift, ast.LShift, ast.BitOr, ast.BitAnd, ast.BitXor, ast.Mod, ast.Pow)
COMP_TYPES = (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)
READ_ERRORS = (SyntaxError, ValueError, RecursionError, MemoryError, LookupError, OverflowError)
TOO_DEEP = "[recursion_guard] an expression too deep to read at line 1"
# Set per file by set_context: what the file's own bindings do to the proofs and to the path-join reading.
CTX_NONE = {"shadowed": frozenset(), "void": False, "path_ok": True, "defines_radd": False, "defines_div": False, "has_star": False}
CTX = dict(CTX_NONE)


def bound_names(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.add(n.id)
        elif isinstance(n, ast.arg):
            out.add(n.arg)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            out.update(a.asname or a.name.split(".")[0] for a in n.names)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            out.add(n.name)
        elif isinstance(n, (ast.MatchAs, ast.MatchStar)) and n.name:
            out.add(n.name)
        elif isinstance(n, ast.MatchMapping) and n.rest:
            out.add(n.rest)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            out.update(n.names)
    return out


def set_context(tree):
    # A proof builtin bound anywhere in the file proves nothing. A class with numeric dunders or an int or bool base voids abs, max, min and % there.
    bound = bound_names(tree)
    CTX["shadowed"] = {b for b in BOUND_BUILTINS + NARROWING_BUILTINS if b in bound}
    void, radd, div, path_ok, has_star = False, False, False, True, False
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef):
            for b in n.bases:
                if isinstance(b, ast.Name) and b.id in ("int", "bool"):
                    void = True
            for s in n.body:
                names = []
                if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names = [s.name]
                elif isinstance(s, ast.Assign):
                    names = [t.id for t in s.targets if isinstance(t, ast.Name)]
                for name in names:
                    void = void or name in NUM_DUNDERS
                    radd = radd or name in ("__radd__", "__add__")
                    div = div or name in ("__truediv__", "__rtruediv__")
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name in ("Path", "PurePath"):
            path_ok = False
        elif isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)) and n.id in ("Path", "PurePath"):
            path_ok = False
        elif isinstance(n, ast.arg) and n.arg in ("Path", "PurePath"):
            path_ok = False
        elif isinstance(n, ast.ImportFrom):
            has_star = has_star or any(a.name == "*" for a in n.names)
            for a in n.names:
                if (a.asname or a.name) in ("Path", "PurePath") and not (n.module or "").startswith("pathlib"):
                    path_ok = False
    CTX.update(void=void, defines_radd=radd, defines_div=div, path_ok=path_ok, has_star=has_star)
    if has_star:
        CTX["shadowed"] = set(BOUND_BUILTINS + NARROWING_BUILTINS)


def is_path_join(node):
    # Only the operands themselves, along a chain of joins or concatenations.
    if CTX["defines_div"]:
        return False
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        if CTX["defines_radd"]:
            return False
        for side in (node.left, node.right):
            if isinstance(side, ast.Call) and isinstance(side.func, ast.Name) and side.func.id not in ("str", "repr", "hex", "oct", "bin", "ascii", "chr", "format", "Path", "PurePath"):
                return False
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Add)):
        return is_path_join(node.left) or is_path_join(node.right)
    if isinstance(node, ast.JoinedStr) or (isinstance(node, ast.Constant) and isinstance(node.value, str)):
        return True
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("Path", "PurePath") and CTX["path_ok"]


# An int ** a negative int is a float, and a syntax tree cannot see a variable's value. So an exponent must be provably
# non-negative from the source, and anything else is a finding: write it with an integer power that refuses a negative exponent.
def proven_nonnegative(node, safe):
    if isinstance(node, ast.Constant):
        return type(node.value) in (int, bool) and node.value >= 0
    if isinstance(node, ast.Name):
        return node.id in safe
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Mod):
            return not CTX["void"] and proven_nonnegative(node.left, safe) and proven_nonnegative(node.right, safe)
        return isinstance(node.op, PROVEN_BINOPS) and proven_nonnegative(node.left, safe) and proven_nonnegative(node.right, safe)
    if isinstance(node, ast.IfExp):
        return proven_nonnegative(node.body, safe) and proven_nonnegative(node.orelse, safe)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
        fid = node.func.id
        if fid in CTX["shadowed"]:
            return False
        if fid == "len":
            return True
        if CTX["void"]:
            return False
        if fid == "abs":
            return len(node.args) == 1 and proven_nonnegative(node.args[0], safe)
        if fid in ("max", "min"):
            return bool(node.args) and all(proven_nonnegative(a, safe) for a in node.args)
    return False


def proven_iteration(node, safe):
    # What a for-loop's target takes: range with a proven start and a positive step, a range running down to a floor at or above zero, or a literal list of proven values.
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return all(proven_nonnegative(e, safe) for e in node.elts)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range" and not node.keywords:
        args = node.args
        if "range" in CTX["shadowed"] or any(isinstance(a, ast.Starred) for a in args):
            return False
        if len(args) == 1:
            return True
        if len(args) == 2:
            return proven_nonnegative(args[0], safe)
        if len(args) == 3:
            stop, step = args[1], args[2]
            down = isinstance(step, ast.UnaryOp) and isinstance(step.op, ast.USub) and isinstance(step.operand, ast.Constant) and type(step.operand.value) is int and step.operand.value > 0
            floor_ok = (isinstance(stop, ast.Constant) and type(stop.value) is int and stop.value >= 0) or (isinstance(stop, ast.UnaryOp) and isinstance(stop.op, ast.USub) and isinstance(stop.operand, ast.Constant) and stop.operand.value == 1)
            if down and floor_ok:
                return True
            return proven_nonnegative(args[0], safe) and isinstance(step, ast.Constant) and type(step.value) is int and step.value > 0
    return False


def proven_names(tree):
    # Least fixed point over the whole file. A name is proven only if every place that binds it, in any scope, is proven.
    sites, explained = {}, set()

    def note(target, kind, value):
        if isinstance(target, ast.Name):
            sites.setdefault(target.id, []).append((kind, value))
            explained.add(id(target))
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            if n.value is not None:
                for target in targets:
                    note(target, "value", n.value)
        elif isinstance(n, ast.AugAssign):
            note(n.target, "aug", n)
        elif isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension)):
            note(n.target, "iter", n.iter)
            if isinstance(n.target, ast.Tuple) and len(n.target.elts) == 2 and isinstance(n.target.elts[0], ast.Name) and isinstance(n.iter, ast.Call) and isinstance(n.iter.func, ast.Name) and n.iter.func.id == "enumerate" and len(n.iter.args) == 1 and not n.iter.keywords:
                if not isinstance(n.iter.args[0], ast.Starred) and "enumerate" not in CTX["shadowed"]:
                    note(n.target.elts[0], "index", None)
    poisoned = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)) and id(n) not in explained:
            poisoned.add(n.id)
        elif isinstance(n, ast.arg):
            poisoned.add(n.arg)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            poisoned.update(n.names)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            poisoned.update(a.asname or a.name.split(".")[0] for a in n.names)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            poisoned.add(n.name)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            poisoned.add(n.name)
        elif isinstance(n, (ast.MatchAs, ast.MatchStar)) and n.name:
            poisoned.add(n.name)
        elif isinstance(n, ast.MatchMapping) and n.rest:
            poisoned.add(n.rest)
    # A class body reads a mangled name from outside the class, and a star import can rebind anything.
    poisoned.update(name for name in sites if name.startswith("__") and not name.endswith("__"))
    if CTX["has_star"]:
        poisoned.update(sites)
    safe = set()
    changed = True
    while changed:
        changed = False
        for name, bound in sites.items():
            if name in safe or name in poisoned:
                continue
            ok, anchored = True, False
            for kind, value in bound:
                if kind == "value":
                    ok = ok and proven_nonnegative(value, safe)
                    anchored = True
                elif kind == "iter":
                    ok = ok and proven_iteration(value, safe)
                    anchored = True
                elif kind == "index":
                    anchored = True
                else:
                    ok = ok and isinstance(value.op, AUG_PROVEN) and proven_nonnegative(value.value, safe)
            if ok and anchored:
                safe.add(name)
                changed = True
    return safe


def constant_text(node):
    # Folds what the source shows of a string: constants, implicit parts, + chains, and f-strings with a digit for each hole.
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        return node.value if isinstance(node.value, str) else node.value.decode("latin-1")
    if isinstance(node, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "0" for v in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = constant_text(node.left), constant_text(node.right)
        if a is not None and b is not None:
            return a + b
    return None


def percent_float_conversions(s):
    # The %-format grammar as CPython reads it: a %(key) with nested parens, flags, width, .precision with digits optional, length, conversion.
    out, i, n = [], 0, len(s)
    while True:
        i = s.find("%", i)
        if i < 0 or i + 1 >= n:
            return out
        j = i + 1
        if s[j] == "%":
            i = j + 1
            continue
        if s[j] == "(":
            depth, j = 1, j + 1
            while j < n and depth:
                depth += (s[j] == "(") - (s[j] == ")")
                j += 1
        flags = ""
        while j < n and s[j] in "#0- +":
            flags += s[j]
            j += 1
        while j < n and (s[j].isdigit() or s[j] == "*"):
            j += 1
        precision = False
        if j < n and s[j] == ".":
            precision = True
            j += 1
            while j < n and (s[j].isdigit() or s[j] == "*"):
                j += 1
        while j < n and s[j] in "hlL":
            j += 1
        if j < n and s[j] in PERCENT_CONV:
            out.append((flags, precision))
        i = j if j > i else i + 1


def brace_float_fields(s):
    try:
        fields = list(string.Formatter().parse(s))
    except ValueError:
        return False
    for _, field, spec, _ in fields:
        if field is None or not spec or not FIELD_NAME.match(field):
            continue
        if GRAMMAR_FLOAT_SPEC.match(spec) or (spec[0] == "{" and spec[-1] == "}" and FIELD_NAME.match(spec[1:-1])):
            return True
    return False


def none_names(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AnnAssign)) and isinstance(n.value, ast.Constant) and n.value.value is None:
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            out.update(t.id for t in targets if isinstance(t, ast.Name))
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            a = n.args
            pos = a.posonlyargs + a.args
            for arg, default in zip(pos[len(pos) - len(a.defaults):], a.defaults):
                if isinstance(default, ast.Constant) and default.value is None:
                    out.add(arg.arg)
            for arg, default in zip(a.kwonlyargs, a.kw_defaults):
                if isinstance(default, ast.Constant) and default.value is None:
                    out.add(arg.arg)
    return out


def constant_bindings(tree):
    # name -> the constant strings it is ever bound to, only when every binding of the name in the file is one.
    good, bad = {}, set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    if isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                        good.setdefault(t.id, []).append(n.value.value)
                    else:
                        bad.add(t.id)
                elif not isinstance(t, (ast.Attribute, ast.Subscript)):
                    bad.update(s.id for s in ast.walk(t) if isinstance(s, ast.Name))
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Del):
            bad.add(n.id)
        elif isinstance(n, ast.arg):
            bad.add(n.arg)
        elif isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension, ast.AugAssign, ast.NamedExpr)):
            bad.update(t.id for t in ast.walk(n.target) if isinstance(t, ast.Name))
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            bad.update(n.names)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            bad.update(a.asname or a.name.split(".")[0] for a in n.names)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bad.add(n.name)
        elif isinstance(n, (ast.MatchAs, ast.MatchStar)) and n.name:
            bad.add(n.name)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            bad.add(n.name)
        elif isinstance(n, ast.withitem) and n.optional_vars is not None:
            bad.update(t.id for t in ast.walk(n.optional_vars) if isinstance(t, ast.Name))
    return {k: v for k, v in good.items() if k not in bad}


def visible_letters(node, constants):
    # The letters of a struct format built by + and * from strings the source shows. None when any piece is not shown.
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        return node.value if isinstance(node.value, str) else node.value.decode("latin-1")
    if isinstance(node, ast.Name) and node.id in constants:
        return "".join(constants[node.id])
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = visible_letters(node.left, constants), visible_letters(node.right, constants)
        return None if a is None or b is None else a + b
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        a, b = visible_letters(node.left, constants), visible_letters(node.right, constants)
        return a if a is not None else b
    return None


def path_names(tree):
    # A name whose every binding in the file is Path-derived, so a / on it is a join.
    def is_path(node, names):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("Path", "PurePath"):
            return CTX["path_ok"] and not CTX["defines_div"]
        if isinstance(node, ast.Name):
            return node.id in names
        if isinstance(node, ast.Attribute) and node.attr == "parent":
            return is_path(node.value, names)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("resolve", "absolute", "expanduser", "with_name", "with_suffix", "joinpath"):
            return is_path(node.func.value, names)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            return is_path(node.left, names) or is_path(node.right, names)
        return False
    candidates, bad = {}, set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    candidates.setdefault(t.id, []).append(n.value)
                elif not isinstance(t, (ast.Attribute, ast.Subscript)):
                    bad.update(s.id for s in ast.walk(t) if isinstance(s, ast.Name))
        elif isinstance(n, ast.arg):
            bad.add(n.arg)
        elif isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension, ast.AugAssign, ast.NamedExpr)):
            bad.update(s.id for s in ast.walk(n.target) if isinstance(s, ast.Name))
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            bad.update(n.names)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            bad.update(a.asname or a.name.split(".")[0] for a in n.names)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bad.add(n.name)
        elif isinstance(n, (ast.MatchAs, ast.MatchStar)) and n.name:
            bad.add(n.name)
        elif isinstance(n, ast.withitem) and n.optional_vars is not None:
            bad.update(s.id for s in ast.walk(n.optional_vars) if isinstance(s, ast.Name))
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            if n.value is None:
                bad.add(n.target.id)
            else:
                candidates.setdefault(n.target.id, []).append(n.value)
    names = set()
    changed = True
    while changed:
        changed = False
        for name, values in candidates.items():
            if name not in names and name not in bad and all(is_path(v, names) for v in values):
                names.add(name)
                changed = True
    return names, is_path


def comp_drop(out, node, local, base):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(child, COMP_TYPES):
            comp_handle(out, child, local, base)
            continue
        if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Pow) and proven_nonnegative(child.right, local) and not proven_nonnegative(child.right, base):
            message = "power with an unproven exponent at line %d" % child.lineno
            if message in out:
                out.remove(message)
        comp_drop(out, child, local, base)


def comp_handle(out, comp, outer, base):
    # A comprehension's own target is proven inside it, whatever the same name does elsewhere in the file.
    local = set(outer)
    for gen in comp.generators:
        comp_drop(out, ast.Expression(gen.iter), local, base)
        local -= {t.id for t in ast.walk(gen.target) if isinstance(t, ast.Name)}
        target = gen.target
        if isinstance(target, ast.Name) and proven_iteration(gen.iter, local):
            local.add(target.id)
        elif isinstance(target, ast.Tuple) and len(target.elts) == 2 and isinstance(target.elts[0], ast.Name) and isinstance(gen.iter, ast.Call) and isinstance(gen.iter.func, ast.Name) and gen.iter.func.id == "enumerate" and len(gen.iter.args) == 1 and not gen.iter.keywords and not isinstance(gen.iter.args[0], ast.Starred) and "enumerate" not in CTX["shadowed"]:
            local.add(target.elts[0].id)
        for cond in gen.ifs:
            comp_drop(out, ast.Expression(cond), local, base)
    parts = [comp.key, comp.value] if isinstance(comp, ast.DictComp) else [comp.elt]
    for part in parts:
        comp_drop(out, ast.Expression(part), local, base)


def date_format_args(tree, parent):
    # The literal first argument of a strftime call prints a date: %F and %f there are date directives. So does an f-string spec that opens with %, which an int or a float refuses.
    # A strftime the file binds itself proves nothing, and neither does a call whose result is formatted again on the left of %.
    out = set()
    own = "strftime" in bound_names(tree) or any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)) and s.name == "strftime" for c in ast.walk(tree) if isinstance(c, ast.ClassDef) for s in c.body)
    for n in ast.walk(tree):
        if isinstance(n, ast.FormattedValue) and n.format_spec is not None and len(n.format_spec.values) == 1:
            only = n.format_spec.values[0]
            if isinstance(only, ast.Constant) and only.value.startswith("%") and len(only.value) >= 2:
                out.add(id(only))
        if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str) and not own:
            f = n.func
            p = parent.get(n)
            reformatted = isinstance(p, ast.BinOp) and isinstance(p.op, ast.Mod) and p.left is n
            if ((isinstance(f, ast.Attribute) and f.attr == "strftime") or (isinstance(f, ast.Name) and f.id == "strftime")) and not reformatted:
                out.add(id(n.args[0]))
    return out


def tree_findings(tree, safe, parent, date_args, constants):
    aliases = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                top = a.name.split(".")[0]
                if top in WATCHED:
                    aliases[a.asname or a.name] = top
    paths, is_path = path_names(tree)
    out = []
    for n in ast.walk(tree):
        line = getattr(n, "lineno", 0)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (float, complex)):
                out.append("float literal at line %d" % line)
            elif isinstance(n.value, (str, bytes)):
                template = n.value if isinstance(n.value, str) else n.value.decode("latin-1")
                if PERCENT_FLOAT.search(template) and id(n) not in date_args:
                    out.append("float %%-format at line %d" % line)
                elif template in BAD_STRING:
                    out.append("the string %s at line %d" % (template, line))
        elif isinstance(n, ast.Import):
            out += ["import %s at line %d" % (a.name, line) for a in n.names if a.name.split(".")[0] in BAD_IMPORT]
        elif isinstance(n, ast.ImportFrom):
            top = (n.module or "").split(".")[0]
            if top in BAD_IMPORT:
                out.append("import %s at line %d" % (n.module, line))
            elif top in WATCHED:
                for a in n.names:
                    if a.name == "*" or (a.name not in WATCHED[top]) or (top == "random" and a.name in RANDOM_METHODS):
                        out.append("from %s import %s at line %d" % (top, a.name, line))
            elif top == "operator":
                out += ["from operator import %s at line %d" % (a.name, line) for a in n.names if a.name in ("truediv", "itruediv", "pow", "ipow", "*")]
            elif top == "builtins":
                out += ["from builtins import %s at line %d" % (a.name, line) for a in n.names if a.name in BAD_NAME or a.name in ("pow", "*")]
        elif isinstance(n, ast.Name):
            if n.id in BAD_NAME and not rejects_a_type(n, parent):
                out.append("%s at line %d" % (n.id, line))
        elif isinstance(n, ast.Attribute):
            if isinstance(n.value, ast.Name) and n.value.id in aliases and n.attr not in WATCHED[aliases[n.value.id]]:
                out.append("%s.%s at line %d" % (aliases[n.value.id], n.attr, line))
            elif n.attr == "fromhex" and isinstance(n.value, ast.Name) and n.value.id in ("bytes", "bytearray") and n.value.id not in CTX["shadowed"]:
                pass
            elif n.attr in RANDOM_METHODS or n.attr in BAD_ATTRIBUTE:
                out.append("%s at line %d" % (n.attr, line))
            elif n.attr == "pow" and isinstance(n.value, ast.Name) and n.value.id in ("operator", "builtins"):
                out.append("%s.pow at line %d" % (n.value.id, line))
            elif n.attr == "format" and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str) and FORMAT_FIELD.search(n.value.value):
                out.append("float format at line %d" % line)
        elif isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id == "pow":
                modulus = len(n.args) >= 3 or any(k.arg == "mod" for k in n.keywords)
                exponents = n.args[1:2] + [k.value for k in n.keywords if k.arg == "exp"]
                if not modulus and not (exponents and proven_nonnegative(exponents[0], safe)):
                    out.append("power with an unproven exponent at line %d" % line)
            elif isinstance(f, ast.Attribute) and f.attr in STRUCT_CALLS and isinstance(f.value, ast.Name) and f.value.id == "struct":
                layout = n.args[0] if n.args else None
                if not (isinstance(layout, ast.Constant) and isinstance(layout.value, (str, bytes))):
                    letters = visible_letters(layout, constants) if layout is not None else None
                    if letters is None or set(letters) & set("efd"):
                        out.append("struct with a format the source does not show at line %d" % line)
                else:
                    letters = layout.value if isinstance(layout.value, str) else layout.value.decode("latin-1")
                    if set(letters) & set("efd"):
                        out.append("struct float format at line %d" % line)
            elif isinstance(f, ast.Attribute) and f.attr == "cast" and len(n.args) >= 1 and isinstance(n.args[0], ast.Constant) and n.args[0].value in ("d", "f", "e"):
                out.append("float memoryview at line %d" % line)
            elif isinstance(f, ast.Name) and f.id == "format" and len(n.args) == 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str) and FLOAT_SPEC.search(n.args[1].value):
                out.append("float format at line %d" % line)
            elif isinstance(f, ast.Name) and f.id == "getattr" and len(n.args) >= 1 and isinstance(n.args[0], ast.Name) and n.args[0].id in aliases:
                out.append("getattr on %s at line %d" % (aliases[n.args[0].id], line))
            elif ((isinstance(f, ast.Name) and f.id == "array") or (isinstance(f, ast.Attribute) and f.attr == "array")) and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value in ("d", "f"):
                out.append("float array at line %d" % line)
        elif isinstance(n, ast.BinOp):
            if isinstance(n.op, ast.Div):
                p = parent.get(n)
                inner_join = isinstance(p, ast.BinOp) and isinstance(p.op, ast.Div) and p.left is n and is_path_join(p)
                if not (is_path_join(n) or inner_join or is_path(n.left, paths) or is_path(n.right, paths)):
                    out.append("true division at line %d" % line)
            elif isinstance(n.op, ast.Pow) and not proven_nonnegative(n.right, safe):
                out.append("power with an unproven exponent at line %d" % line)
        elif isinstance(n, ast.AugAssign):
            if isinstance(n.op, ast.Div):
                if not (is_path_join(n.value) or (isinstance(n.target, ast.Name) and n.target.id in paths)):
                    out.append("true division at line %d" % line)
            elif isinstance(n.op, ast.Pow) and not proven_nonnegative(n.value, safe):
                out.append("power with an unproven exponent at line %d" % line)
        elif isinstance(n, ast.FormattedValue) and n.format_spec is not None:
            values = n.format_spec.values
            spec = "".join(v.value for v in values if isinstance(v, ast.Constant))
            dynamic = any(isinstance(v, ast.FormattedValue) for v in values)
            type_fixed = dynamic and isinstance(values[-1], ast.Constant) and values[-1].value[-1:] in ("b", "c", "d", "o", "x", "X", "s")
            date_spec = not dynamic and spec.startswith("%") and len(spec) >= 2
            if (FLOAT_SPEC.search(spec) or dynamic) and not type_fixed and not date_spec:
                out.append("float format at line %d" % line)
    return out


def rejects_a_type(n, parent):
    # isinstance(v, float) and type(v) is float name the type in order to refuse it.
    p = parent.get(n)
    if n.id not in ("float", "complex") or not isinstance(n.ctx, ast.Load):
        return False
    if isinstance(p, ast.Tuple):
        p = parent.get(p)
    typecheck = isinstance(p, ast.Call) and isinstance(p.func, ast.Name) and p.func.id in ("isinstance", "issubclass") and p.func.id not in CTX["shadowed"] and len(p.args) == 2
    compare = isinstance(p, ast.Compare) and "type" not in CTX["shadowed"] and isinstance(p.left, ast.Call) and isinstance(p.left.func, ast.Name) and p.left.func.id == "type" and all(isinstance(o, (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)) for o in p.ops)
    return typecheck or compare


def route_findings(tree, parent, date_args, constants, local):
    # Routes with no float word on the line: reflection, aliases, computed formats. Each message names its rule.
    out = []

    def add(rule, msg, node):
        out.append("[%s] %s at line %d" % (rule, msg, getattr(node, "lineno", 0)))
    mod, frm = {}, {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.asname:
                    mod[a.asname] = a.name
                else:
                    top = a.name.split(".")[0]
                    mod[top] = top
        elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
            for a in n.names:
                frm[a.asname or a.name] = (n.module, a.name)

    def in_call_position(node):
        p = parent.get(node)
        return isinstance(p, ast.Call) and p.func is node

    def attr_receiver(node):
        p = parent.get(node)
        return isinstance(p, ast.Attribute) and p.value is node
    nones = none_names(tree)
    struct_names = {k for k, v in mod.items() if v in ("struct", "_struct")}
    struct_from = {k: v[1] for k, v in frm.items() if v[0] in ("struct", "_struct")}
    array_names = {k for k, v in mod.items() if v == "array"}
    array_from = {k for k, v in frm.items() if v[0] == "array" and v[1] in ("array", "ArrayType")}

    def check_layout(call):
        layout = call.args[0] if call.args else None
        if not (isinstance(layout, ast.Constant) and isinstance(layout.value, (str, bytes))):
            add("struct_alias", "struct with a format the source does not show", call)
        else:
            letters = layout.value if isinstance(layout.value, str) else layout.value.decode("latin-1")
            if set(letters) & set("efd"):
                add("struct_alias", "struct float format", call)

    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            top = (n.module or "").split(".")[0]
            for a in n.names:
                if a.name == "*" and top not in local:
                    add("star_import", "from %s import *" % n.module, n)
                if a.name in IMPORT_BAD:
                    add("operator_names", "from %s import %s" % (n.module, a.name), n)
                if not n.level and a.name in (W_NAMES | {"Decimal", "Fraction"}) and top not in ("datetime", a.name) and top not in BAD_IMPORT and top not in WATCHED:
                    add("reexport", "from %s import %s" % (n.module, a.name), n)
                if top == "sys" and a.name == "modules":
                    add("sys_modules", "from sys import modules", n)
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or ""]
            level = 0 if isinstance(n, ast.Import) else n.level
            for full in names:
                top = full.split(".")[0]
                if not level and (top in EXEC_IMPORTS or full.startswith("unittest.mock") or (isinstance(n, ast.ImportFrom) and top == "unittest" and any(a.name == "mock" for a in n.names))):
                    add("exec_imports", "import %s" % full, n)
                if top.startswith("_") and top not in ("__future__", "__main__") and not level:
                    add("underscore_imports", "import %s" % full, n)
                if not level and top and top not in ALLOW_STDLIB and top not in local:
                    add("import_allow", "import %s, outside the allowed list" % full, n)
        if isinstance(n, ast.Name):
            load = isinstance(n.ctx, ast.Load)
            if n.id == "pow" and load and not in_call_position(n):
                add("pow_value", "pow as a value", n)
            if n.id == "getattr" and load and not in_call_position(n):
                add("getattr_strict", "getattr as a value", n)
            if n.id == "format" and load and not in_call_position(n):
                add("format_calls", "format as a value", n)
            if n.id in ("__builtins__", "__loader__", "__spec__"):
                add("reflection_attrs", n.id, n)
            if n.id in ("locals", "setattr", "delattr"):
                add("locals_setattr", n.id, n)
            if load and n.id in mod and not attr_receiver(n):
                add("module_flow", "the module %s as a value" % n.id, n)
            if n.id in struct_from and load and not in_call_position(n):
                add("struct_alias", "a struct function as a value", n)
            if n.id in array_from and load and not in_call_position(n):
                add("array_cast", "an array constructor as a value", n)
            if n.id in frm and frm[n.id] == ("sys", "modules"):
                add("sys_modules", "sys.modules", n)
        elif isinstance(n, ast.Attribute):
            a = n.attr
            recv = n.value
            root_mod = isinstance(recv, ast.Name) and recv.id in mod
            if a == "pow":
                add("pow_attr", ".pow", n)
            if a == "itruediv":
                add("operator_names", ".itruediv", n)
            if a in ("__getattribute__", "get_field", "getattr_static", "getmembers"):
                add("getattr_strict", a, n)
            if a in ("attrgetter", "methodcaller") and not in_call_position(n):
                add("getattr_strict", "%s as a value" % a, n)
            if a in ("eval", "exec", "execfile", "__import__") or (a == "compile" and not (isinstance(recv, ast.Name) and mod.get(recv.id) == "re")):
                add("exec_attrs", ".%s" % a, n)
            if a in REFLECT_ATTR:
                add("reflection_attrs", a, n)
            if a in MORE_ATTRS:
                add("more_attrs", a, n)
            if isinstance(n.ctx, (ast.Store, ast.Del)) and root_mod and not (mod.get(recv.id) == "sys" and a in ARGV_LIKE):
                add("module_store", "a store into the module %s" % recv.id, n)
            if a == "modules":
                add("sys_modules", ".modules", n)
            if isinstance(recv, ast.Attribute) and recv.attr in W_NAMES:
                root = recv
                while isinstance(root, ast.Attribute):
                    root = root.value
                if isinstance(root, ast.Name) and root.id in mod and root.id != "datetime" and mod[root.id].split(".")[0] not in BAD_IMPORT and mod[root.id].split(".")[0] not in WATCHED:
                    add("reexport", "%s.%s" % (recv.attr, a), n)
            if root_mod and a in (W_NAMES | {"Decimal", "Fraction", "_time"}) and mod.get(recv.id) not in ("datetime", a) and mod[recv.id].split(".")[0] not in BAD_IMPORT and mod[recv.id].split(".")[0] not in WATCHED:
                add("reexport", "%s.%s" % (recv.id, a), n)
            if a in STRUCT_CALLS and isinstance(recv, ast.Name) and (recv.id in struct_names or recv.id == "struct") and not in_call_position(n):
                add("struct_alias", "a struct function as a value", n)
            if a in ("array", "ArrayType") and isinstance(recv, ast.Name) and recv.id in array_names and not in_call_position(n):
                add("array_cast", "an array constructor as a value", n)
            if a == "cast" and not in_call_position(n):
                add("array_cast", ".cast as a value", n)
            if a in ("__format__", "vformat", "format_field", "format_map", "Formatter"):
                add("format_calls", a, n)
            if a == "format" and not isinstance(recv, ast.Constant):
                shown = isinstance(recv, ast.Name) and recv.id in constants
                if shown and any(brace_float_fields(t) for t in constants[recv.id]):
                    add("format_receiver", ".format on a name holding a float field", n)
                elif not shown:
                    add("format_receiver", ".format on something the source does not show", n)
            if a == "parse" and isinstance(recv, ast.Name) and mod.get(recv.id) == "ast":
                add("ast_parse", "ast.parse", n)
        elif isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id == "pow":
                starred = any(isinstance(a, ast.Starred) for a in n.args) or any(k.arg is None for k in n.keywords)
                mods = n.args[2:3] + [k.value for k in n.keywords if k.arg == "mod"]
                literal = any(isinstance(m, ast.Constant) and m.value is None for m in mods)
                named = any(isinstance(m, ast.Name) and m.id in nones for m in mods)
                if starred or literal or named:
                    add("pow_none", "pow with a modulus that may be None", n)
            if isinstance(f, ast.Name) and f.id == "getattr" and len(n.args) >= 2:
                name = n.args[1]
                if not (isinstance(name, ast.Constant) and isinstance(name.value, str)):
                    add("getattr_strict", "getattr with a name the source does not show", n)
                elif name.value in EXT_BAD:
                    add("getattr_strict", "getattr of %s" % name.value, n)
            caller = (isinstance(f, ast.Attribute) and f.attr in ("attrgetter", "methodcaller")) or (isinstance(f, ast.Name) and f.id in frm and frm[f.id][1] in ("attrgetter", "methodcaller"))
            if caller:
                for arg in n.args:
                    if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                        add("getattr_strict", "attrgetter or methodcaller with a name the source does not show", n)
                    elif set(arg.value.split(".")) & EXT_BAD:
                        add("getattr_strict", "attrgetter or methodcaller of %s" % arg.value, n)
            if (isinstance(f, ast.Attribute) and f.attr == "__class__") or (isinstance(f, ast.Call) and isinstance(f.func, ast.Name) and f.func.id == "type"):
                add("class_call", "a call through a value's class", n)
            if isinstance(f, ast.Name) and f.id == "type" and len(n.args) == 3:
                add("class_call", "a class made at run time", n)
            if isinstance(f, ast.Attribute) and f.attr in STRUCT_CALLS and isinstance(f.value, ast.Name) and f.value.id in struct_names and f.value.id != "struct":
                check_layout(n)
            elif isinstance(f, ast.Name) and f.id in struct_from and struct_from[f.id] in STRUCT_CALLS:
                check_layout(n)
            if (isinstance(f, ast.Attribute) and f.attr in ("array", "ArrayType") and isinstance(f.value, ast.Name) and f.value.id in array_names) or (isinstance(f, ast.Name) and (f.id in array_from or f.id == "array")):
                code = n.args[0] if n.args else None
                if not (isinstance(code, ast.Constant) and isinstance(code.value, str)):
                    add("array_cast", "array with a typecode the source does not show", n)
                elif code.value in ("d", "f", "e"):
                    add("array_cast", "float array", n)
            if isinstance(f, ast.Attribute) and f.attr == "cast" and not (isinstance(f.value, ast.Name) and mod.get(f.value.id) == "typing"):
                fmt = [k.value for k in n.keywords if k.arg == "format"] + n.args[:1]
                if not fmt or not (isinstance(fmt[0], ast.Constant) and isinstance(fmt[0].value, str)):
                    add("array_cast", "cast with a format the source does not show", n)
                elif fmt[0].value.lstrip("@") in ("d", "f", "e"):
                    add("array_cast", "cast to a float format", n)
            if isinstance(f, ast.Name) and f.id == "format":
                spec = n.args[1] if len(n.args) > 1 else None
                if any(isinstance(a, ast.Starred) for a in n.args) or (len(n.args) >= 2 and not (isinstance(spec, ast.Constant) and isinstance(spec.value, str))):
                    add("format_calls", "format with a spec the source does not show", n)
        elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod):
            text = constant_text(n.left)
            if text is not None and percent_float_conversions(text):
                add("percent_parser", "float %-format on the left of %", n)
            left = n.left
            stringish_call = isinstance(left, ast.Call) and isinstance(left.func, ast.Attribute) and left.func.attr in STR_METHODS
            stringish_add = isinstance(left, ast.BinOp) and isinstance(left.op, ast.Add) and constant_text(left) is None and (constant_text(left.left) is not None or constant_text(left.right) is not None)
            if stringish_call or stringish_add:
                add("computed_percent", "a %-format the source builds", n)
        elif isinstance(n, ast.FunctionDef) and n.name == "__prepare__":
            add("prepare_def", "a metaclass that supplies a class body's names", n)
        elif isinstance(n, ast.MatchClass):
            for a in n.kwd_attrs:
                if a in EXT_BAD or a in NUM_DUNDERS:
                    add("match_attrs", "class pattern reads %s" % a, n)
        if isinstance(n, (ast.Constant, ast.JoinedStr, ast.BinOp)):
            text = constant_text(n)
            if text is not None and not isinstance(parent.get(n), (ast.JoinedStr, ast.BinOp, ast.FormattedValue)):
                if id(n) not in date_args:
                    for flags, precision in percent_float_conversions(text):
                        if " " in flags and not precision:
                            continue
                        add("percent_parser", "float %-format", n)
                        break
                if "{" in text and brace_float_fields(text):
                    add("brace_anywhere", "float field in a {}-format", n)
                if BARE_SPEC.match(text):
                    add("bare_spec", "a float format spec", n)
                if text in EXT_DUNDERS:
                    add("dunder_strings", "the string %s" % text, n)
                for m in BRACE_ATTR.finditer(text):
                    if m.group(1) in EXT_BAD:
                        add("format_attr_strings", "format string reads %s" % m.group(1), n)
    return out


def source_notes(data):
    # Decodes as CPython does: BOM, then a coding cookie on the first two lines, with CR and CRLF already read as line ends.
    normal = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    try:
        declared, _ = tokenize.detect_encoding(io.BytesIO(normal).readline)
        name = codecs.lookup(declared).name
    except READ_ERRORS:
        return ["[source_bytes] unreadable source encoding at line 1"]
    if name not in ("utf-8", "utf-8-sig"):
        return ["[source_bytes] source encoding %s at line 1" % declared]
    return []


def python_findings(data, local=frozenset()):
    # One file's bytes, or text taken as its UTF-8. local holds the names of the tracked Python, which import_allow and star_import let through; a caller that wants a scan's count passes local_modules of the tracked paths.
    if isinstance(data, str):
        data = data.encode("utf-8", "backslashreplace")
    notes = source_notes(data)
    try:
        tree = ast.parse(data)
    except RecursionError:
        return notes + [TOO_DEEP]
    except READ_ERRORS as e:
        return notes + ["syntax error at line %s" % getattr(e, "lineno", 0)]
    try:
        set_context(tree)
        safe = proven_names(tree)
        parent = {}
        for p in ast.walk(tree):
            for c in ast.iter_child_nodes(p):
                parent[c] = p
        date_args = date_format_args(tree, parent)
        constants = constant_bindings(tree)
        out = tree_findings(tree, safe, parent, date_args, constants)
        for n in ast.walk(tree):
            if isinstance(n, COMP_TYPES):
                p = parent.get(n)
                while p is not None and not isinstance(p, COMP_TYPES):
                    p = parent.get(p)
                if p is None:
                    comp_handle(out, n, safe, safe)
        return notes + out + route_findings(tree, parent, date_args, constants, local)
    except RecursionError:
        return notes + [TOO_DEEP]
    finally:
        CTX.update(CTX_NONE)


EXP = r"[eE][-+]?[\d_]*\d[\d_]*"
RS_LITERAL = r"(?<![\w.])\d[\d_]*\.\d|(?<![\w.])\d[\d_]*\.(?![\w.])|(?<![\w.])\d[\d_]*" + EXP + r"\b"
C_SUFFIX = r"(?:[fF](?:16|32|64|128|\d+x)?|[lL]|_\w+)?\b"
C_LITERAL = (r"(?<![\w.])\d[\d_]*\.\d|(?<![\w.])\d[\d_]*\.(?![\w.])|(?<![\w.])\d[\d_]*" + EXP + C_SUFFIX +
             r"|(?<![\w.])\d[\d_]*\.[eE][-+]?\d|(?<![\w.])\.\d|(?<![\w.])\d[\d_]*\.[fFlL]\b|\b0[xX][\da-fA-F_.]*[pP][-+]?[\d_]+")
C_FUNCS = (r"\b(?:atof|atold|strto(?:d|f|ld)|stod|stof|stold|sqrt[fl]?|cbrt[fl]?|expm1[fl]?|exp2?[fl]?|log(?:2|10|1p)?[fl]?|pow[fl]?|fabs[fl]?|fmod[fl]?|hypot[fl]?|"
           r"a?sinh?[fl]?|a?cosh?[fl]?|a?tanh?[fl]?|atan2[fl]?|ceil[fl]?|floor[fl]?|trunc[fl]?|l?l?round[fl]?|nearbyint[fl]?|l?l?rint[fl]?|ldexp[fl]?|frexp[fl]?|modf[fl]?|nan[fl]?|erfc?[fl]?|t?gamma[fl]?|lgamma[fl]?)\s*\(")
C_NAMES = (C_FUNCS + r"|\b__builtin_(?!clz|ctz|popcount|parity|ffs|bswap|expect|unreachable|assume|constant_p|add|sub|mul|sadd|uadd|ssub|usub|smul|umul|memcpy|memset|memcmp|strlen|prefetch|trap|abort|clrsb)\w+"
           r"|\b__(?:DBL|FLT|LDBL|DEC)\d*_\w+__\b|\b(?:DBL|FLT|LDBL)_[A-Z_]+\b|\bM_(?:PI|E|SQRT|LN|LOG)\w*\b|\bHUGE_VAL\w*\b|\bINFINITY\b"
           r"|\b(?:uniform_real_distribution|normal_distribution|lognormal_distribution|gamma_distribution|exponential_distribution|weibull_distribution|extreme_value_distribution|chi_squared_distribution|cauchy_distribution|fisher_f_distribution|student_t_distribution|bernoulli_distribution|generate_canonical)\b|\bnumbers::\w+"
           r"|##|\b(?:__asm__|__asm|asm)\b|\b_mm\d*_\w+|\b__m\d+[di]?\b")
RUST_LINES = (
    ("rust float word", re.compile(r"\b(f16|f32|f64|f128|Float)\b|\w_f(16|32|64|128)\b|\d_?f(16|32|64|128)\b|\bhexf(32|64)\b")),
    ("rust float literal", re.compile(RS_LITERAL)),
    ("[rs_cnames] a C float alias or a float crate", re.compile(r"\bc_(?:double|float|longdouble)\b|\b(?:FloatCore|FloatConst|BigDecimal|BigFloat|rust_decimal|bigdecimal|astro_float)\b|\breal::Real\b")),
    ("[rs_arch] assembly or intrinsics", re.compile(r"\b(?:global_asm|naked_asm|asm)!|\b_mm\d*_\w+|\b__m\d+[di]?\b|\b(?:std|core)::arch\b")),
)
C_LINES = (
    ("c float word", re.compile(r"\b(float|double|float32|float64|__float128)\b|#\s*include\s*<c?math(\.h)?>")),
    ("c float literal", re.compile(C_LITERAL)),
    ("[c_types] a float type", re.compile(r"\b(?:_Float\d+x?|__float\d+|__ibm128|_Decimal\d+|float\d*_t|double_t|bfloat16_t|__bf16|_Complex|_Imaginary|__complex__|mpf_\w+|mpfr_\w+|mpc_\w+)\b")),
    ("[c_names] a float function, macro, builtin or assembly", re.compile(C_NAMES)),
)
GO_LINES = (
    ("go float word", re.compile(r"\b(float32|float64|complex64|complex128)\b|\bmath\.[A-Z]\w*")),
    ("go float literal", re.compile(C_LITERAL)),
    ("[go_names] a float function or an imaginary literal", re.compile(r"\bParseFloat\b|\bFormatFloat\b|\bFloat(?:32|64)\b|\bNewFloat\b|\bbig\.(?:Float|Rat)\b|\bSetFloat64\b|\bNormFloat64\b|\bExpFloat64\b|\b(?:Seconds|Minutes|Hours)\(\)|(?<![\w.])\d[\d_]*i\b")),
)
JS_LINES = (
    ("javascript float route", re.compile(r"\bMath\.\w+|\bparseFloat\b|\btoFixed\b|\bNumber\(|\bFloat(32|64)Array\b")),
    ("javascript float literal", re.compile(C_LITERAL)),
    ("[js_names] a float name or an indirect route", re.compile(r"\bMath\b|\bNumber\b|\btoPrecision\b|\btoExponential\b|\bFloat\d+Array\b|\b[gs]etFloat\d+\b|\bJSON\b|\bperformance\b|\bglobalThis\b|\bwindow\s*\[|\bself\s*\[|\beval\b|\bFunction\s*\(|\bReflect\b|\bNaN\b|\bInfinity\b|\\u[\da-fA-F{]|(?<![\w.])\d{16,}(?![\d_n.])")),
    ("[js_ops] ** or arithmetic on a string", re.compile(r"\*\*(?!\s*\d[\d_]*n\b)|\"\"\s*[-*/%]|[-*/%]\s*\"\"|(?:^|[=(,:;!&|?{}\[])\s*\+\s*\"\"")),
)
C_BAD_HEADER = {"cmath", "math.h", "tgmath.h", "ctgmath", "complex", "complex.h", "random", "numbers", "stdfloat", "valarray", "cfloat", "float.h", "cfenv", "fenv.h", "immintrin.h", "x86intrin.h", "emmintrin.h", "xmmintrin.h", "pmmintrin.h", "smmintrin.h", "nmmintrin.h", "arm_neon.h", "bits/stdc++.h"}
C_INCLUDE = re.compile(r'^[ \t]*#[ \t]*include[ \t]*([<"])([^>"\n]+)[>"]', re.M)
GO_IMPORT = re.compile(r'"(?:math|math/rand|math/rand/v2|math/cmplx|encoding/json|C)"')
SCRIPT_ANY = re.compile(r"<script\b([^>]*)>(.*?)(?:</script\s*>|\Z)", re.S | re.I)
HANDLER = re.compile(r"""\bon[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", re.I)
SCRIPT_SRC = re.compile(r"\bsrc\s*=", re.I)
HTML_ACTIVE = re.compile(r"\bsrcdoc\s*=|\bjavascript:", re.I)
WORD = re.compile(r"[\w$]+")
REGEX_PREV_WORDS = {"return", "typeof", "instanceof", "in", "of", "void", "delete", "throw", "new", "case", "do", "else", "yield", "await"}
RS_INCLUDE = re.compile(r'\binclude!\s*\(\s*(?:"([^"]*)"|(concat!))|\bpath\s*=\s*"([^"]*)"')
RAW_STRING = re.compile(r'(?:b|c)?r(#*)"')
CHAR_LITERAL = re.compile(r"'(\\.[^'\n]*|[^'\\\n])'")
RAW_CPP = re.compile(r'(?:u8|u|U|L)?R"([^()\\\s]{0,16})\(')
NOT_RUN = ("text", "ignore", "none", "console", "bash", "sh", "json", "toml", "txt", "plain", "c", "cpp", "python", "py")
DOC_LINE = re.compile(r"^\s*(?:///|//!)(.*)$")
RUST_EXT = (".rs",)
C_EXT = (".c", ".h", ".cc", ".cxx", ".cpp", ".hh", ".hpp", ".c++", ".cp", ".hxx", ".h++", ".inl", ".ipp", ".tcc", ".txx")
GO_EXT = (".go",)
JS_EXT = (".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".mts", ".cts")
HTML_EXT = (".html", ".htm", ".xhtml", ".xht", ".shtml", ".svg", ".vue", ".svelte")
READ_EXT = PY_EXT + RUST_EXT + C_EXT + GO_EXT + JS_EXT + HTML_EXT
LFS = b"version https://git-lfs.github.com/spec/"
BOM = b"\xef\xbb\xbf"


def line_kinds(code, patterns, found=None):
    found = {} if found is None else found
    for i, line in enumerate(code.split("\n"), 1):
        if i not in found:
            for kind, pattern in patterns:
                if pattern.search(line):
                    found[i] = kind
                    break
    return found


def as_rows(found):
    return ["%s at line %d" % (found[i], i) for i in sorted(found)]


def rs_doc_fences(text):
    # Only an opening fence that rustdoc would run counts. A fence marked text and the like holds no code.
    found, open_fence = set(), False
    for n, line in enumerate(text.split("\n"), 1):
        m = DOC_LINE.match(line)
        if not m:
            open_fence = False
            continue
        body = m.group(1).strip()
        if body.startswith("```"):
            if open_fence:
                open_fence = False
            else:
                open_fence = True
                if body[3:].strip().split(",")[0].strip().lower() not in NOT_RUN:
                    found.add(n)
    for m in re.finditer(r"/\*[*!](?:[^*]|\*(?!/))*?```([^\n]*)", text):
        if m.group(1).strip().split(",")[0].strip().lower() not in NOT_RUN:
            found.add(text.count("\n", 0, m.start()) + 1)
    for m in re.finditer(r"#!?\[\s*doc\s*=\s*(?:\"(?:[^\"\\]|\\.)*```|include_str!)", text):
        found.add(text.count("\n", 0, m.start()) + 1)
    return found


def code_only(text, rust):
    # Rust and Go, comments and strings removed with the line count kept. Rust nests block comments, Go has backtick strings with no escapes, and a raw-string prefix counts only where no quote or apostrophe sits right before it.
    out, i, n = [], 0, len(text)
    while i < n:
        c, two = text[i], text[i:i + 2]
        if two == "//":
            while i < n and text[i] != "\n":
                i += 1
        elif two == "/*":
            depth, i = 1, i + 2
            while i < n and depth:
                if rust and text[i:i + 2] == "/*":
                    depth, i = depth + 1, i + 2
                elif text[i:i + 2] == "*/":
                    depth, i = depth - 1, i + 2
                else:
                    out.append("\n" if text[i] == "\n" else "")
                    i += 1
        elif c == "`" and not rust:
            end = text.find("`", i + 1)
            end = n if end < 0 else end + 1
            out.append('""' + "\n" * text.count("\n", i, end))
            i = end
        elif c == '"':
            i += 1
            while i < n and text[i] != c:
                i += 2 if text[i] == "\\" else 1
                out.append("\n" if text[i - 1] == "\n" else "")
            i += 1
            out.append('""')
        elif c in "bcr" and RAW_STRING.match(text, i) and not (i and (text[i - 1].isalnum() or text[i - 1] in "_'\"")):
            m = RAW_STRING.match(text, i)
            end = text.find('"' + m.group(1), m.end())
            end = n if end < 0 else end + 1 + len(m.group(1))
            out.append('""' + "\n" * text.count("\n", i, end))
            i = end
        elif c == "'":
            m = CHAR_LITERAL.match(text, i)
            if m:
                out.append("' '")
                i = m.end()
            else:
                out.append(c)
                i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def c_phases(text):
    # Line splices and the # digraph and trigraph go first, as in translation phases one and two. A spliced line keeps its count, so later line numbers hold.
    out, held, buffer = [], 0, ""
    for line in text.replace("??=", "#").replace("%:", "#").split("\n"):
        if line.endswith("\\"):
            buffer += line[:-1]
            held += 1
        else:
            out.append(buffer + line)
            out.extend([""] * held)
            buffer, held = "", 0
    if held:
        out.append(buffer)
        out.extend([""] * held)
    return "\n".join(out)


def c_code_only(text):
    out, i, n = [], 0, len(text)
    while i < n:
        c, two = text[i], text[i:i + 2]
        if two == "//":
            while i < n and text[i] != "\n":
                i += 1
        elif two == "/*":
            i += 2
            while i < n and text[i:i + 2] != "*/":
                out.append("\n" if text[i] == "\n" else "")
                i += 1
            i += 2
        elif c in "RuUL" and RAW_CPP.match(text, i) and not (i and (text[i - 1].isalnum() or text[i - 1] == "_")):
            m = RAW_CPP.match(text, i)
            close = ")" + m.group(1) + '"'
            end = text.find(close, m.end())
            end = n if end < 0 else end + len(close)
            out.append('""' + "\n" * text.count("\n", i, end))
            i = end
        elif c == '"':
            i += 1
            while i < n and text[i] != '"' and text[i] != "\n":
                i += 2 if text[i] == "\\" else 1
            i += 1 if i < n and text[i] == '"' else 0
            out.append('""')
        elif c == "'":
            j = i - 1
            while j >= 0 and (text[j].isalnum() or text[j] == "_"):
                j -= 1
            run = text[j + 1:i]
            if run and run[0].isdigit():
                out.append("_")
                i += 1
                continue
            i += 1
            while i < n and text[i] != "'" and text[i] != "\n":
                i += 2 if text[i] == "\\" else 1
            i += 1 if i < n and text[i] == "'" else 0
            out.append("' '")
        else:
            out.append(c)
            i += 1
    return "".join(out)


def js_code_only(text):
    # Keeps code in template holes, blanks regex literals, and ends comments and strings where JavaScript does: a single-quoted or double-quoted string stops at its line's end.
    term = "\n\r  "
    out, i, n, prev = [], 0, len(text), ""
    holes, in_template = [], False
    while i < n:
        c, two = text[i], text[i:i + 2]
        if in_template:
            if c == "\\":
                i += 2
            elif c == "`":
                in_template, prev = False, '"'
                out.append('""')
                i += 1
            elif two == "${":
                holes.append(0)
                in_template, prev = False, "("
                out.append('"" + (')
                i += 2
            else:
                out.append("\n" if c == "\n" else "")
                i += 1
            continue
        if two == "//":
            while i < n and text[i] not in term:
                i += 1
        elif two == "/*":
            i += 2
            while i < n and text[i:i + 2] != "*/":
                out.append("\n" if text[i] in term else "")
                i += 1
            i += 2
        elif c in "\"'":
            i += 1
            while i < n and text[i] != c and text[i] not in "\n\r":
                i += 2 if text[i] == "\\" else 1
            i += 1 if i < n and text[i] == c else 0
            out.append('""')
            prev = '"'
        elif c == "`":
            in_template = True
            i += 1
        elif c == "{" and holes:
            holes[-1] += 1
            out.append(c)
            prev = c
            i += 1
        elif c == "}" and holes:
            if holes[-1] == 0:
                holes.pop()
                in_template = True
                out.append(")")
            else:
                holes[-1] -= 1
                out.append(c)
            prev = c
            i += 1
        elif c == "/":
            if prev == "" or prev in REGEX_PREV_WORDS or (len(prev) == 1 and prev in "(,=:[!&|?{;+-*%<>~^"):
                j, in_class, closed = i + 1, False, False
                while j < n and text[j] not in term:
                    ch = text[j]
                    if ch == "\\":
                        j += 2
                        continue
                    if in_class:
                        in_class = ch != "]"
                    elif ch == "[":
                        in_class = True
                    elif ch == "/":
                        closed = True
                        break
                    j += 1
                if closed:
                    j += 1
                    while j < n and text[j].isalpha():
                        j += 1
                    out.append('""')
                    prev = '"'
                    i = j
                    continue
            out.append("/")
            prev = "/"
            i += 1
        elif c in term:
            out.append("\n")
            i += 1
        elif c.isspace():
            out.append(c)
            i += 1
        else:
            m = WORD.match(text, i)
            if m:
                out.append(m.group(0))
                prev = m.group(0)
                i = m.end()
            else:
                out.append(c)
                prev = c
                i += 1
    return "".join(out)


def js_lines(code, jsx):
    # Any / left in the code is a division on a double, unless a BigInt literal or BigInt( sits on one side of it.
    found = line_kinds(code, JS_LINES)
    for k, line in enumerate(code.split("\n"), 1):
        if k in found:
            continue
        for m in re.finditer(r"/", line):
            at = m.start()
            if jsx and ((at and line[at - 1] == "<") or line[at + 1:at + 2] == ">"):
                continue
            left, right = line[:at].rstrip(), line[at + 1:].lstrip().lstrip("=").lstrip()
            if re.search(r"\d[\d_]*n$", left) or re.match(r"\d[\d_]*n\b|BigInt\s*\(", right):
                continue
            found[k] = "javascript division"
            break
    return found


def html_findings(text):
    # Script bodies and on* handlers are code. Page text and CSS are read by neither rule, a script src names code the scan may never open, and srcdoc and javascript: hold code in a string.
    found = {}
    for m in SCRIPT_ANY.finditer(text):
        start = text.count("\n", 0, m.start(2)) + 1
        if SCRIPT_SRC.search(m.group(1)):
            found[text.count("\n", 0, m.start(1)) + 1] = "[html_view] a script src"
        for k, kind in js_lines(js_code_only(m.group(2)), False).items():
            found.setdefault(start + k - 1, kind)
    outside = SCRIPT_ANY.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    for m in HANDLER.finditer(outside):
        if js_lines(js_code_only(html.unescape(m.group(1).strip("\"'"))), False):
            found.setdefault(outside.count("\n", 0, m.start()) + 1, "[html_view] an inline handler computes")
    for m in HTML_ACTIVE.finditer(outside):
        found.setdefault(outside.count("\n", 0, m.start()) + 1, "[html_view] srcdoc or javascript:")
    return found


def native_findings(text, name):
    if name.endswith(RUST_EXT):
        found = line_kinds(code_only(text, True), RUST_LINES)
        for k in rs_doc_fences(text):
            found.setdefault(k, "[rs_doctest] a doc-test")
        for m in RS_INCLUDE.finditer(text):
            target = m.group(1) if m.group(1) is not None else m.group(3)
            if m.group(2) or (target is not None and not target.endswith(".rs")):
                found.setdefault(text.count("\n", 0, m.start()) + 1, "[rs_include] an include or path target outside .rs")
        return as_rows(found)
    if name.endswith(C_EXT):
        text = c_phases(text)
        found = line_kinds(c_code_only(text), C_LINES)
        for m in C_INCLUDE.finditer(text):
            head = m.group(2).strip()
            if head in C_BAD_HEADER or (m.group(1) == '"' and not head.lower().endswith(C_EXT)):
                found.setdefault(text.count("\n", 0, m.start()) + 1, "[c_include] a float header or a file the scan does not read")
        return as_rows(found)
    if name.endswith(GO_EXT):
        found = line_kinds(code_only(text, False), GO_LINES)
        for m in GO_IMPORT.finditer(text):
            if not text[text.rfind("\n", 0, m.start()) + 1:m.start()].lstrip().startswith("//"):
                found.setdefault(text.count("\n", 0, m.start()) + 1, "[go_names] a float import")
        return as_rows(found)
    if name.endswith(HTML_EXT):
        return as_rows(html_findings(text))
    if name.endswith(JS_EXT):
        return as_rows(js_lines(js_code_only(text), name.endswith((".jsx", ".tsx"))))
    return []


def findings(data, name, local=frozenset()):
    # What CPython or the compiler would read of one file's bytes. A text argument is taken as its UTF-8 bytes.
    if isinstance(data, str):
        data = data.encode("utf-8", "backslashreplace")
    if data.startswith(LFS):
        return ["[bytes] an LFS pointer in place of code"]
    if name.endswith(PY_EXT):
        return python_findings(data, local)
    notes = []
    if b"\0" in data:
        notes.append("[bytes] NUL bytes in code")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        notes.append("[bytes] code that is not UTF-8")
        text = data.decode("utf-8", "replace")
    if text.startswith("﻿"):
        text = text[1:]
    return notes + native_findings(text.replace("\r\n", "\n").replace("\r", "\n"), name)


COMPILED_EXT = (".pyc", ".pyo", ".pyd", ".so", ".dylib", ".dll", ".whl", ".egg", ".pyz", ".zip")
OTHER_PY_EXT = (".pyx", ".pxd", ".pxi", ".ipy", ".sage", ".ipynb", ".py3", ".rpy", ".pyde")
SCRIPT_EXT = (".sh", ".bash", ".yml", ".yaml", ".ps1", ".cmd", ".bat", ".mk")
PY_INVOKE = re.compile(r"python3?(?:\.\d+)?(?:\s+-[A-Za-z]+(?:\s+utf8)?)*\s+([^\s'\"$;|&<>()-][^\s;|&'\"<>()]*)")
RUN_TARGET = re.compile(r"\bpython3?(?:\.exe)?(?:[ \t]+-[A-Za-z]+(?:[ \t]+utf8)?)*[ \t]+\"?([\w./-]+)\"?")
PY_SHEBANG = re.compile(rb"python|pypy")
SHEBANG_EXEC = re.compile(rb"exec\s+\S*python|python\S*\s+\"?\$0")
ATTRS_BAD = re.compile(r"\b(?:filter|working-tree-encoding|ident)\b")
CRATE_ALLOW = {"autocfg", "num-traits", "num-integer", "num-bigint", "sha2", "digest", "block-buffer", "generic-array", "typenum", "crypto-common", "cpufeatures", "libc", "version_check", "cfg-if"}
TEXT_LIMIT = 1048576
ZIP_TAIL = 66000
RUNNABLE = (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef, ast.Assign, ast.Call)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def cargo_notes(base, path, data):
    # A build script and a proc macro write code at build time. A crate off the allow list brings code the scan has not read.
    text = data.decode("utf-8", "replace")
    notes = []
    if base == "build.rs":
        notes.append("[rs_buildsys] build.rs generates code at build time")
    elif base == "cargo.toml":
        if re.search(r"proc-macro\s*=\s*true", text):
            notes.append("[rs_buildsys] a proc-macro crate")
        for m in re.finditer(r'^\s*(?:path|build)\s*=\s*"([^"]+)"', text, re.M):
            if not m.group(1).endswith(".rs"):
                notes.append("[rs_buildsys] a Cargo target at %s" % m.group(1))
        section = ""
        for row in text.splitlines():
            row = row.strip()
            if row.startswith("["):
                section = row
            elif re.search(r"dependencies\]$", section) and "=" in row and not row.startswith("#"):
                dep = row.split("=", 1)[0].strip().strip('"')
                pm = re.search(r'path\s*=\s*"([^"]+)"', row)
                if pm:
                    where = os.path.normpath(os.path.join(os.path.dirname(path), pm.group(1))).replace("\\", "/")
                    if pm.group(1).startswith("/") or ":" in pm.group(1) or where.startswith(".."):
                        notes.append("[rs_buildsys] dependency %s leaves the tracked tree" % dep)
                elif "workspace" not in row and dep not in CRATE_ALLOW:
                    notes.append("[rs_buildsys] crate %s is not on the allow list" % dep)
    elif base == "cargo.lock":
        for block in text.split("[[package]]"):
            m = re.search(r'name = "([^"]+)"', block)
            if m and re.search(r'source = "(?:registry|git)', block) and m.group(1) not in CRATE_ALLOW:
                notes.append("[rs_buildsys] crate %s is not on the allow list" % m.group(1))
    return notes


def run_target_notes(data, tracked_set):
    # A script that hands a tracked file with another name to python.
    text = data.decode("utf-8", "replace")
    notes = {}
    for pattern in (PY_INVOKE, RUN_TARGET):
        for m in pattern.finditer(text):
            target = m.group(1)
            if target in tracked_set and not target.lower().endswith(PY_EXT):
                line = text.count("\n", 0, m.start()) + 1
                notes[(line, target)] = "[run_targets] python runs %s at line %d" % (target, line)
    return [notes[k] for k in sorted(notes)]


def holds_python(data):
    # A text file that parses as Python and does something, under any name: python3 runs any file it is handed.
    if len(data) > TEXT_LIMIT or b"\0" in data:
        return False
    try:
        tree = ast.parse(data)
    except READ_ERRORS:
        return False
    return any(isinstance(x, RUNNABLE) for x in ast.walk(tree))


def entry_findings(path, mode, data, tracked_set=frozenset(), local=frozenset(), in_folder=False):
    # One tracked entry, by its mode and blob bytes. Returns its findings, and whether a code reader took it.
    if mode == "160000":
        return ["[links] a submodule the scan cannot read"], False
    if data is None:
        return ["[links] a tracked file this clone does not hold"], False
    if mode == "120000":
        return ["[links] a symlink"], False
    name = path.lower()
    base = name.rsplit("/", 1)[-1]
    notes = []
    if base == ".gitattributes" and ATTRS_BAD.search(data.decode("utf-8", "replace")):
        notes.append("[links] a .gitattributes filter, working-tree-encoding or ident")
    if base in ("build.rs", "cargo.toml", "cargo.lock"):
        notes += cargo_notes(base, path, data)
    if name.endswith(COMPILED_EXT) or "__pycache__/" in name:
        notes.append("[binary_python] compiled or archived Python")
    if b"PK\x05\x06" in data[-ZIP_TAIL:]:
        notes.append("[binary_python] holds a zip directory, importable by path")
    if name.endswith(OTHER_PY_EXT):
        notes.append("[other_exts] Python by another extension")
    if name.endswith(SCRIPT_EXT):
        notes += run_target_notes(data, tracked_set)
    first = (data[len(BOM):] if data.startswith(BOM) else data).split(b"\n", 1)[0]
    reader = name if name.endswith(READ_EXT) else None
    if reader is None and first.startswith(b"#!"):
        if PY_SHEBANG.search(first):
            reader = name + ".py"
        elif SHEBANG_EXEC.search(data[:400]):
            notes.append("[shebang_any] a shell header that runs this file as Python")
            reader = name + ".py"
    if reader:
        return notes + findings(data, reader, local), True
    if not in_folder and holds_python(data):
        found = python_findings(data, local)
        if found:
            notes.append("[anything_python] Python under a name the scan does not read: " + found[0])
    return notes, False


def parse_list(lines):
    # File rows read path | findings=N | sha256=H | reason. Folder rows read folder/ | tree=H | reason. Returns the rows and the failures.
    folders, files, bad, seen = {}, {}, [], set()
    for line in lines:
        line = line.rstrip("\r\n")
        if not line.strip() or line.startswith("#"):
            continue
        row = line.split("|", 1)[0].strip()
        if row in seen:
            bad.append("row_twice=%s" % row)
            continue
        seen.add(row)
        if row.endswith("/"):
            parts = [p.strip() for p in line.split("|", 2)]
            pin, reason = parts[1] if len(parts) > 1 else "", parts[2] if len(parts) > 2 else ""
            label, count = "tree=", None
        else:
            parts = [p.strip() for p in line.split("|", 3)]
            count, pin, reason = parts[1] if len(parts) > 1 else "", parts[2] if len(parts) > 2 else "", parts[3] if len(parts) > 3 else ""
            label = "sha256="
            if not re.match(r"^findings=\d+$", count):
                bad.append("row_without_a_count=%s" % row)
                continue
            count = int(count.split("=")[1])
        if not pin.startswith(label) or not HEX64.match(pin[len(label):]):
            bad.append("row_without_a_pin=%s" % row)
            continue
        if not any(c.isalpha() for c in reason):
            bad.append("row_without_a_reason=%s" % row)
        if count is None:
            folders[row] = pin[len(label):]
        else:
            files[row] = (count, pin[len(label):])
    return folders, files, bad


def git_env():
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return env


def ls_files(root):
    raw = subprocess.run(["git", "-C", root, "ls-files", "-s", "-z"], capture_output=True, check=True, stdin=subprocess.DEVNULL, env=git_env()).stdout
    rows = []
    for row in raw.split(b"\0"):
        if row:
            head, path = row.split(b"\t", 1)
            mode, sha, stage = head.decode().split()
            rows.append((mode, sha, stage, path.decode("utf-8", "surrogateescape")))
    return rows


class Blobs:
    # The bytes git holds for a tracked entry, from the object store. A checkout's filters, sparse rules and symlinks play no part, and nothing from the tree runs.
    def __init__(self, root):
        self.p = subprocess.Popen(["git", "-C", root, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=git_env())

    def read(self, sha):
        self.p.stdin.write(sha.encode() + b"\n")
        self.p.stdin.flush()
        head = self.p.stdout.readline().split()
        if len(head) != 3:
            return None
        data = self.p.stdout.read(int(head[2]))
        self.p.stdout.read(1)
        return data

    def close(self):
        self.p.stdin.close()
        self.p.stdout.close()
        self.p.wait()


def local_modules(tracked_set):
    names = set()
    for p in tracked_set:
        if p.lower().endswith(".py"):
            parts = p.split("/")
            names.add(parts[-1][:-3])
            names.update(parts[:-1])
    return names


def blob_pin(sha, data):
    return hashlib.sha256(data).hexdigest() if data is not None else sha


def tree_pin(lines):
    # One line per tracked entry under the folder, in git's order: mode, the blob's sha256, path. A new file, a mode change or an edited byte moves it.
    return hashlib.sha256("".join(lines).encode("utf-8", "surrogateescape")).hexdigest()


def tree_line(mode, pin, path):
    return "%s %s %s\n" % (mode, pin, path)


def one_row(row):
    # Each row stays one line with its own prefix, so a file name holding a newline cannot start a line of its own, such as a workflow command in the job's log.
    print(row.replace("\r", "\\r").replace("\n", "\\n"))


def listed():
    # The rows of the list beside this file: folder pins, file (count, pin) pairs, and the failed rows.
    with open(os.path.join(HERE, LIST_NAME), encoding="utf-8") as f:
        return parse_list(f)


def scan(root):
    rows = ls_files(root)
    tracked_set = {r[3] for r in rows}
    local = local_modules(tracked_set)
    try:
        folders, files, bad_rows = listed()
    except (OSError, UnicodeDecodeError):
        print("NO_FLOAT|no_readable_list_beside_the_gate=%s|json=0" % LIST_NAME)
        return 1
    scanned, kept, fails, seen = 0, 0, 0, set()
    for row in bad_rows:
        fails += 1
        one_row("NO_FLOAT|%s|json=0" % row)
    folder_lines = {f: [] for f in folders}
    blobs = Blobs(root)
    for mode, sha, stage, path in rows:
        data = None if mode == "160000" else blobs.read(sha)
        pin = blob_pin(sha, data)
        folder = [f for f in folders if path.startswith(f)]
        found, is_code = entry_findings(path, mode, data, tracked_set, local, bool(folder))
        if stage != "0":
            found = ["[links] an unmerged path"] + found
        scanned += is_code
        for f in folder:
            folder_lines[f].append(tree_line(mode, pin, path))
        if folder:
            seen.update(folder)
            kept += len(found)
        elif path in files:
            seen.add(path)
            kept += len(found)
            listed_count, listed_pin = files[path]
            if len(found) != listed_count:
                fails += 1
                one_row("NO_FLOAT|count_moved=%s|listed=%d|found=%d|first=%s|json=0" % (path, listed_count, len(found), found[0] if found else "none"))
            if pin != listed_pin:
                fails += 1
                one_row("NO_FLOAT|pin_moved=%s|listed=%s|actual=%s|json=0" % (path, listed_pin, pin))
        elif found:
            fails += 1
            one_row("NO_FLOAT|file=%s|first=%s|count=%d|json=0" % (path, found[0], len(found)))
    blobs.close()
    for f in sorted(folders):
        if f in seen and tree_pin(folder_lines[f]) != folders[f]:
            fails += 1
            one_row("NO_FLOAT|pin_moved=%s|listed=%s|actual=%s|json=0" % (f, folders[f], tree_pin(folder_lines[f])))
    for gone in sorted((set(folders) | set(files)) - seen):
        fails += 1
        one_row("NO_FLOAT|listed_and_gone=%s|json=0" % gone)
    if scanned == 0:
        fails += 1
        one_row("NO_FLOAT|no_code_files_read=1|json=0")
    print("NO_FLOAT_DONE|code_files=%d|listed_files=%d|listed_folders=%d|listed_findings=%d|failed=%d|json=0" % (scanned, len(files), len(folders), kept, fails))
    return 1 if fails else 0


def pins(paths):
    # Prints what a row needs for each path, with the reason left empty for a person to write. A row pasted as printed fails until it holds one.
    rows = ls_files(".")
    tracked_set = {r[3] for r in rows}
    local = local_modules(tracked_set)
    blobs = Blobs(".")
    rc = 0
    for want in paths:
        hits = [r for r in rows if (r[3].startswith(want) if want.endswith("/") else r[3] == want)]
        if not hits:
            print("NO_FLOAT|not_tracked=%s|json=0" % want)
            rc = 1
        elif want.endswith("/"):
            lines = []
            for mode, sha, _, path in hits:
                data = None if mode == "160000" else blobs.read(sha)
                lines.append(tree_line(mode, blob_pin(sha, data), path))
            print("%s | tree=%s | " % (want, tree_pin(lines)))
        else:
            mode, sha, stage, path = hits[0]
            data = None if mode == "160000" else blobs.read(sha)
            found, _ = entry_findings(path, mode, data, tracked_set, local)
            print("%s | findings=%d | sha256=%s | " % (path, len(found) + (stage != "0"), blob_pin(sha, data)))
    blobs.close()
    return rc


FLOATS = (
    ("x.py", "x = 0.5"), ("x.py", "x = 1e9"), ("x.py", "x = 2j"), ("x.py", "x = float(3)"), ("x.py", "x = 1 / 2"), ("x.py", "a /= b"),
    ("x.py", "x = 2 ** -3"), ("x.py", "a **= -1"), ("x.py", "x = pow(2, -1)"), ("x.py", "e = -1\nx = 2 ** e"), ("x.py", "def f(e):\n    return 2 ** e"), ("x.py", "x = 2 ** (n - 1)"), ("x.py", "k = 3\nk -= 5\nx = 2 ** k"), ("x.py", "for e in range(-3, 3):\n    x = 2 ** e"), ("x.py", "for e in range(3, -3, -1):\n    x = 2 ** e"), ("x.py", "for e in (1, -1):\n    x = 2 ** e"), ("x.py", "e = 1\ndef f(e):\n    return 2 ** e"), ("x.py", "a, b = 1, -1\nx = 2 ** b"), ("x.py", "a = b\nb = a\nx = 2 ** a"), ("x.py", "x = pow(2, e)"), ("x.py", "a **= e"), ("x.py", "import operator\nx = operator.pow(2, e)"), ("x.py", "from operator import pow"), ("x.py", "x = (2).__pow__(e)"), ('x.py', 'x = getattr(b, "float")'), ("x.py", "x = globals()"), ("x.py", "import pickle"), ('x.py', 'import struct\nx = struct.unpack("<d", b)'), ("x.py", "import struct\nx = struct.unpack(fmt, b)"), ("x.py", 'x = memoryview(b).cast("d")'), ("x.py", "from builtins import float"), ("x.py", "import numpy"), ("x.py", "from decimal import Decimal"), ("x.py", "from fractions import Fraction as Q"), ("x.py", "import fractions"),
    ("x.py", "import math\nx = math.sqrt(2)"), ("x.py", "import math as m\nx = m.sqrt(2)"), ("x.py", "from math import sqrt"), ("x.py", "import math\nx = math.fabs(2)"),
    ("x.py", "import time\nx = time.time()"), ("x.py", "import time as t\nx = t.time()"), ("x.py", "from time import monotonic"), ("x.py", "x = rng.random()"), ("x.py", "from random import uniform"), ("x.py", "import random as r\nx = r.random()"),
    ("x.py", 'print(f"{a:.2f}")'), ("x.py", 'print("%.3f" % a)'), ("x.py", 'print(f"{a:.1%}")'), ("x.py", 'x = "{:.2f}".format(1)'), ("x.py", 'x = format(1, ".2f")'), ("x.py", 'x = "%(a).2f" % d'), ("x.py", 'x = "%.*f" % (2, 1)'), ("x.py", 'x = b"%.2f" % 1'), ("x.py", 's = ".2f"\nx = f"{1:{s}}"'),
    ("x.py", 'x = d["a"] / 2'), ("x.py", 'x = len("abc") / 2'), ("x.py", 'x = int("3") / 2'),
    ("x.py", "x = list(map(float, y))"), ("x.py", "F = float"), ("x.py", 'x = float.fromhex("a")'), ("x.py", "x = (1).__truediv__(2)"), ("x.py", "import operator\nx = operator.truediv(1, 2)"), ("x.py", "from operator import truediv"),
    ("x.py", 'x = __import__("fractions")'), ('x.py', 'import importlib'), ('x.py', 'x = eval("1/2")'), ("x.py", "x = o.st_mtime"), ("x.py", "x = d.total_seconds()"), ("x.pyw", "x = 0.5"), ('x.py', 's = "%.2f"'), ("x.py", "import builtins\nx = builtins.float(3)"), ('x.py', 'x = array("d", y)'), ("x.py", "import json"), ("x.py", "import ast\nx = ast.literal_eval(y)"),
    ("x.rs", "let a: f64 = 1;"), ("x.rs", "let a = 0.5;"), ("x.rs", "let a = 2.;"), ("x.rs", "let a = 1e9;"), ("x.rs", "let a = 1f64;"), ("x.rs", "let a = x.to_f64();"), ("x.rs", "let a = d.as_secs_f64();"), ("x.rs", "let a = Duration::from_secs_f32(y);"), ("x.rs", "let a: f128 = b;"), ("x.rs", "let a = 1e_3;"), ("x.rs", "fn f<T: Float>() {}"), ("x.rs", "let a = hexf64!(y);"),
    ("x.rs", "fn f<'a>(x: f64, y: &'a u8) {}"), ("x.rs", 'let s = "a\nb"; let c = 0.5;'), ("x.rs", "/* a /* b */ c */ let d = 0.5;"), ("x.rs", 'let s = r#"a"b"#; let c = 0.5;'), ("x.rs", 'let s = br#"a"#; let c = 0.5;'), ("x.rs", 'let s = cr#"a"#; let c = 0.5;'),
    ("x.c", "double a;"), ("x.cc", "double a;"), ("x.hpp", "double a;"), ("x.c", "__float128 a;"), ("x.cpp", "x = .5;"), ("x.cpp", "x = 1.f;"), ("x.cpp", "x = 0x1p-1;"), ("x.cpp", "#include <cmath>"), ("x.c", "#include <math.h>"), ("x.go", "var a float64"), ("x.go", "x := math.Sqrt(y)"), ("x.go", "x := .5"),
    ("x.html", "<script>Math.sqrt(2)</script>"), ("x.js", "let a = 1.5;"), ("x.js", "let a = .5;"), ("x.js", 'let a = Number("5");'), ("x.tsx", "let a = 1.5;"), ("x.js", "let a = new Float64Array(2);"), ("x.js", "let a = b / c;"), ("x.html", "<script>\nlet a = b / c;\n</script>"),
    ("x.html", "<p>don't</p>\n<script>let a = 0.5;</script>"), ("x.html", "<p>see http://x don't</p><script>let a = 0.5;</script>"), ("x.jsx", "const a = <p>don't</p>;\nlet b = 0.5;"), ("x.py", "from random import Random\nx = Random(1).choices(y)"), ("x.py", "x = rng.binomialvariate(3)"),
    ('x.py', 'def strftime(s):\n    return s\nx = strftime("%f") % 1'), ('x.py', 'class C:\n    def strftime(self, s):\n        return s\ny = C().strftime("%f")'), ('x.py', 'x = d.strftime("%f") % 1'), ("x.py", "isinstance = lambda a, b: b(a)\nx = isinstance(3, float)"), ("x.py", "def type(a):\n    return 3\nx = type(1) is float"), ('x.py', 'bytes = q\nx = bytes.fromhex("a")'), ("x.py", "from there import *\nx = isinstance(3, float)"),
)
# A row here must draw a finding whose text holds the third field, so each rule shows it fires.
POWER = "power with an unproven exponent"
NAMED = (
    # match, star_void, star_import, mangled, shadow, starred
    ("x.py", "e = 1\nmatch -1:\n    case e:\n        pass\nx = 2 ** e", POWER), ("x.py", "e = 1\nfrom there import *\nx = 2 ** e", POWER), ("x.py", "from subprocess import *", "[star_import]"), ("x.py", "_C__e = -1\n__e = 1\nclass C:\n    y = 2 ** __e", POWER),
    ("x.py", 'len = lambda s: -1\nx = 2 ** len("a")', POWER), ("x.py", "def abs(v):\n    return -1\nx = 2 ** abs(1)", POWER), ("x.py", "def range(n):\n    return [-1]\nfor e in range(3):\n    x = 2 ** e", POWER), ("x.py", "for e in range(*[-1, 0]):\n    x = 2 ** e", POWER), ("x.py", "for e, v in enumerate(*[[1], -1]):\n    x = 2 ** e", POWER),
    # methods_strict, void_dunder, strict_abs_mod, strict_max: the source shows no type, so an int subclass in another file can lie in each of these.
    ("x.py", "x = 2 ** y.count(1)", POWER), ("x.py", "x = 2 ** y.index(1)", POWER), ("x.py", "x = 2 ** y.bit_length()", POWER), ("x.py", "class C:\n    def __abs__(self):\n        return -1\nx = 2 ** abs(3)", POWER), ("x.py", "class N(int):\n    pass\nx = 2 ** (3 % 5)", POWER), ("x.py", "x = 2 ** abs(e)", POWER), ("x.py", "x = 2 ** (e % 3)", POWER), ("x.py", "x = 2 ** max(0, e)", POWER), ("x.py", "import n\nx = 2 ** max(0, n.N(-1))", POWER),
    # pow_none, pow_value, pow_attr, path_strict, recursion_guard
    ("x.py", "x = pow(2, -1, None)", "[pow_none]"), ("x.py", "def f(m=None):\n    return pow(2, -1, m)", "[pow_none]"), ("x.py", "x = pow(*a)", "[pow_none]"), ("x.py", "f = pow", "[pow_value]"), ("x.py", "x = b.pow(2, -1)", "[pow_attr]"), ("x.py", 'class P:\n    def __truediv__(self, o):\n        return 1\nx = P() / "a"', "true division"), ("x.py", 'x = (g() + "a") / 2', "true division"), ("x.py", 'def Path(v):\n    return 3\nx = Path("a") / 2', "true division"), ("x.py", "x = 2 ** (" + " + ".join(["1"] * 1400) + ")", "[recursion_guard]"),
    # operator_names, getattr_strict, dunder_strings, reflection_attrs, locals_setattr, module_store, sys_modules, exec_imports, underscore_imports, module_flow, reexport
    ("x.py", "from operator import itruediv", "[operator_names]"), ("x.py", "x = o.itruediv(1, 2)", "[operator_names]"), ("x.py", "x = getattr(a, b)", "[getattr_strict]"), ("x.py", "f = getattr", "[getattr_strict]"), ('x.py', 'from operator import attrgetter\nx = attrgetter("float")(a)', "[getattr_strict]"), ('x.py', 's = "__rtruediv__"', "[dunder_strings]"), ("x.py", "x = len.__self__", "[reflection_attrs]"), ("x.py", "x = a.__dict__", "[reflection_attrs]"), ("x.py", "x = __builtins__", "[reflection_attrs]"),
    ("x.py", 'locals()["e"] = -1', "[locals_setattr]"), ('x.py', 'setattr(m, "e", -1)', "[locals_setattr]"), ("x.py", "import b\nb.e = -1", "[module_store]"), ("x.py", "import sys\nx = sys.modules", "[sys_modules]"), ("x.py", "import runpy", "[exec_imports]"), ("x.py", "import builtins", "[exec_imports]"), ("x.py", "import _decimal", "[underscore_imports]"), ("x.py", "import math\nf(math)", "[module_flow]"), ("x.py", "from m import math", "[reexport]"), ("x.py", "import m\nx = m.math.sqrt(2)", "[reexport]"),
    # struct_alias, class_call, array_cast, match_attrs, more_attrs, import_allow, prepare_def, ast_parse, exec_attrs
    ('x.py', 'import struct as s\nx = s.unpack("<d", b)', "[struct_alias]"), ('x.py', 'from struct import unpack\nx = unpack("<d", b)', "[struct_alias]"), ("x.py", "from struct import unpack\nf = unpack", "[struct_alias]"), ("x.py", "x = y.__class__(1)", "[class_call]"), ("x.py", "x = type(y)(1)", "[class_call]"), ('x.py', 'T = type("T", (int,), {})', "[class_call]"), ('x.py', 'from array import array as A\nx = A("d", y)', "[array_cast]"), ("x.py", "x = memoryview(b).cast(fmt)", "[array_cast]"), ("x.py", "f = memoryview(b).cast", "[array_cast]"),
    ("x.py", "match o:\n    case C(float=f):\n        pass", "[match_attrs]"), ("x.py", "x = os.times()", "[more_attrs]"), ("x.py", "x = s.gettimeout()", "[more_attrs]"), ("x.py", "x = d.ratio()", "[more_attrs]"), ("x.py", "import pysat", "[import_allow]"), ("x.py", "class M(type):\n    def __prepare__(n, b):\n        return {}", "[prepare_def]"), ("x.py", "import ast\nx = ast.parse(s)", "[ast_parse]"), ("x.py", "x = b.eval(s)", "[exec_attrs]"), ("x.py", "x = b.compile(s)", "[exec_attrs]"),
    # percent_parser, computed_percent, brace_anywhere, format_calls, format_receiver, bare_spec, format_attr_strings
    ('x.py', 's = "%%%f"', "[percent_parser]"), ('x.py', 'x = "% .2f" % 1', "[percent_parser]"), ('x.py', 'x = "%lf" % 1', "[percent_parser]"), ('x.py', 'x = "%".join(["", "f"]) % 1', "[computed_percent]"), ('x.py', 'x = ("%" + y) % 1', "[computed_percent]"), ('x.py', 's = "{:.2f}"', "[brace_anywhere]"), ("x.py", "f = format", "[format_calls]"), ("x.py", "x = format(1, s)", "[format_calls]"), ("x.py", "x = y.format_map(d)", "[format_calls]"), ('x.py', 's = "{:.2f}"\nx = s.format(1)', "[format_receiver]"), ("x.py", "x = y.format(1)", "[format_receiver]"), ('x.py', 's = ".2f"', "[bare_spec]"), ('x.py', 's = "{0.__float__}"', "[format_attr_strings]"),
    # Native: rs_cnames, rs_arch, rs_literals, rs_lex, rs_doctest, rs_include
    ("x.rs", "let x = 1 as std::ffi::c_double / 3 as std::ffi::c_double;", "[rs_cnames]"), ("x.rs", "use std::ffi::c_float as Q;", "[rs_cnames]"), ("x.rs", 'global_asm!("divsd xmm0, xmm1");', "[rs_arch]"), ("x.rs", "let c = _mm_div_sd(a, b);", "[rs_arch]"), ("x.rs", "let a = 1e1_0;", "rust float literal"), ("x.rs", "let a = 1E+1_0;", "rust float literal"), ("x.rs", "let a = 1e3_;", "rust float literal"), ("x.rs", 'let s = m!(\'r"a\\"b");\nlet x = 0.5;\nlet t = "c";', "rust float literal"), ("x.rs", 'let s = m!("a"r"b\\"c");\nlet x = 0.5;\nlet t = "d";', "rust float literal"),
    ("x.rs", "/// ```\n/// let x = 1;\n/// ```\nfn f() {}", "[rs_doctest]"), ("x.rs", "/** ```\nlet x = 1;\n``` */\nfn f() {}", "[rs_doctest]"), ("x.rs", '#![doc = include_str!("../README.md")]', "[rs_doctest]"), ('x.rs', 'include!("helper.inc");', "[rs_include]"), ('x.rs', '#[path = "helper.txt"]\nmod helper;', "[rs_include]"), ('x.rs', 'include!(concat!(env!("OUT_DIR"), "/g.rs"));', "[rs_include]"),
    # c_types, c_literals, c_names, c_include, c_splice, c_lex
    ("x.c", "_Float64 x = 1;", "[c_types]"), ("x.c", "__float80 x = 1;", "[c_types]"), ("x.cpp", "std::float64_t x = 1;", "[c_types]"), ("x.cpp", "auto x = 1e5f;", "c float literal"), ("x.cpp", "auto x = 1.e5;", "c float literal"), ("x.cpp", "auto x = 1e5L;", "c float literal"), ("x.cpp", "auto x = 0x1'0p-1;", "c float literal"), ("x.cpp", "auto x = (R).5;", "c float literal"),
    ("x.cpp", "auto x = __builtin_sqrt(2);", "[c_names]"), ('x.cpp', 'auto x = std::atof("0.5");', "[c_names]"), ("x.cpp", "auto x = __DBL_EPSILON__;", "[c_names]"), ("x.cpp", "CAT(dou, ble) x = 1;\n#define CAT(a, b) a##b", "[c_names]"), ('x.cpp', '__asm__("divsd %xmm1,%xmm0");', "[c_names]"), ("x.cpp", "#include <complex>", "[c_include]"), ('x.cpp', '#include "real.inc"', "[c_include]"), ("x.cpp", "dou\\\nble x = 1;", "c float word"), ("x.cpp", "%:include <cmath>", "c float word"), ("x.cpp", "#inc\\\nlude <cmath>", "c float word"),
    ('x.cpp', 'const char *s = R"(a"b)";\nauto x = 0.5;\nconst char *t = "q";', "c float literal"), ('x.cpp', 'int q = \'a"\';\nauto x = 0.5;\nconst char *t = "q";', "c float literal"), ("x.cpp", "int q = '//'; auto x = 0.5;", "c float literal"), ("x.cpp", "int q = '/*'; auto x = 0.5; int r = '*/';", "c float literal"), ('x.cpp', '#warning a"b\nauto x = 0.5;\n#warning c"d', "c float literal"),
    # go_names, and a Go raw string where a backslash escapes nothing
    ('x.go', 'v, _ := strconv.ParseFloat("0.5", 64)', "[go_names]"), ("x.go", "x := rand.Float64()", "[go_names]"), ("x.go", 'import "math/rand"', "[go_names]"), ("x.go", 'import m "math"', "[go_names]"), ("x.go", "x := 1i", "[go_names]"), ("x.go", "a := `\\`; x := 0.5; b := `y`", "go float literal"),
    # js_names, js_ops, js_lex
    ('x.js', 'let x = JSON.parse("0.5");', "[js_names]"), ('x.js', 'let x = Math["sqrt"](2);', "[js_names]"), ("x.js", "const M = Math;", "[js_names]"), ('x.js', 'let x = eval("1/3");', "[js_names]"), ("x.js", "let x = v.getFloat64(0);", "[js_names]"), ("x.js", "let x = 9007199254740993;", "[js_names]"), ("x.js", "let x = 2 ** -1;", "[js_ops]"), ('x.js', 'let x = +"0.5";', "[js_ops]"), ('x.js', 'let x = "0.5" * 1;', "[js_ops]"), ("x.js", "x /= 2;", "javascript division"), ("x.js", "let x = 1 / -3;", "javascript division"), ("x.js", "let x = 1 /\n3;", "javascript division"), ('x.js', 'let x = 1 / "3";', "[js_ops]"),
    ('x.js', 'let r = /"/;\nlet x = 1.5;\nlet s = /"/;', "javascript float literal"), ("x.js", "let r = /[/*]/;\nlet x = 1.5;", "javascript float literal"), ("x.js", "let r = /[//]/; let x = 1.5;", "javascript float literal"), ("x.js", "// c\u2028let x = 1.5;", "javascript float literal"), ("x.js", "let x = `${1/3}`;", "javascript division"), ("x.js", "let x = `${0.5}`;", "javascript float literal"), ("x.js", "let x = `a${`b`}c${1/3}`;", "javascript division"), ("x.jsx", "function A() { return <p>don't</p>; }\nlet x = 1.5;\nfunction B() { return <p>can't</p>; }", "javascript float literal"), ("x.mts", "let x = 1.5;", "javascript float literal"), ("x.cts", "let x = 1.5;", "javascript float literal"), ("x.hxx", "double x;", "c float word"), ("x.inl", "double x;", "c float word"), ("x.c++", "double x;", "c float word"),
    # html_view
    ("x.html", '<body onload="document.title = 1/3">', "[html_view]"), ("x.html", "<body onload=document.title=1/3>", "[html_view]"), ("x.html", '<script src="calc.txt"></script>', "[html_view]"), ("x.html", '<iframe srcdoc="<script>parent.document.title = 1 / 3;</script>"></iframe>', "javascript division"), ("x.html", '<iframe srcdoc="<b>x</b>"></iframe>', "[html_view]"), ('x.html', '<a href="javascript:go()">x</a>', "[html_view]"), ("x.html", "<p>don't</p><script>document.title = 1.5;</script><p>can't</p>", "javascript float literal"), ("x.html", "<script>document.title = 1 / 3;</script >", "javascript division"), ("x.html", "<script>document.title = `${1/3}`;</script>", "javascript division"), ("x.svg", '<svg onload="document.title = 1 / 3"></svg>', "[html_view]"), ("x.vue", "<script>let a = 1 / 3;</script>", "javascript division"),
)
CLEAN = (
    ("x.py", "x = a // b"), ("x.py", 'p = root / "shards" / name'), ("x.py", 'p = root / f"{a}.hbp"'), ("x.py", 'p = base / (name + ".matrix")'), ("x.py", 'p = Path(a) / b'),
    ("x.py", "import math\nx = math.isqrt(9)"), ("x.py", "import math as m\nx = m.gcd(9, 3)"), ("x.py", "import time\nx = time.time_ns()"), ("x.py", "import time\ntime.sleep(1)"), ("x.py", "from math import isqrt"), ("x.py", "from random import Random"), ('x.py', 'print(f"{a:08x} {b:>9} {c:d}")'),
    ("x.py", 'print("%%-f %d" % a)'), ("x.py", "x = rng.randrange(2)"), ("x.py", "# 0.5 / float\nx = 1"), ("x.py", 's = "0.5 / float"'), ("x.py", "x = 2 ** 3"), ("x.py", 'x = "{:d}".format(1)'), ("x.py", "for k in range(5):\n    x = 2 ** k"), ("x.py", "x = 2 ** len(y)"), ("x.py", "k = 3\nx = 10 ** (2 * k + 1)"), ("x.py", "k = 0\nk += 2\nx = 2 ** k"), ("x.py", "x = pow(2, e, m)"), ("x.py", "x = pow(2, 5)"), ("x.py", "for i, v in enumerate(y):\n    x = 2 ** i"), ("x.py", "for k in range(2, 9, 2):\n    x = 2 ** k"), ("x.py", "x = 2 ** max(0, 3)"), ("x.py", "x = ipow(2, e)"), ('x.py', 'import struct\nx = struct.unpack("<IQ", b)'), ("x.py", "import time\nx = time.strftime(y, time.gmtime())"), ("x.py", "import math\nx = math.prod(y)"), ("x.py", "x = [2 ** k for k in range(3)]"),
    ("x.rs", "let a = x.0.1;"), ("x.rs", "for i in 0..5 {}"), ("x.rs", "for i in 0..=5 {}"), ("x.rs", "let a = 0x1e5;"), ("x.rs", "fn f<'a>(x: &'a u8, y: &'a u8) {}"), ("x.rs", "let c = 'f';"),
    ("x.rs", '// f64 0.5\nlet a = 1;'), ("x.rs", 'let s = "HTTP/1.1\nf64 0.5";'), ("x.rs", '/* f64 */ let a = 1;'), ("x.rs", 'let s = r#"a"f64"#;'), ("x.rs", 'let s = br#"f64"#;'), ("x.rs", "let a = 1.max(2);"), ("x.rs", "let a = 12_345;"),
    ("x.c", 'int a = 1; /* double */'), ("x.go", 'var a uint64'), ("x.go", 'x := `0.5`'), ("x.js", "let v = '1.5';"), ("x.html", '<small>HTTP/"1.1" Rust "1.81"</small>'), ("x.html", "<p>a / b</p>"), ('x.py', 'x = array("q", y)'), ('x.py', 's = "5% faster"'),
    ("x.html", "<small>HTTP/1.1 Rust 1.81</small>"), ("x.html", "<p>don't</p>"), ("x.html", "<!-- 0.5 -->"), ("x.html", "<style>p{font-size:1.5rem;opacity:.5}</style><script>document.title = String(7n / 2n);</script>"), ("x.html", "<svg width=100 height=100><path d=M0.5,1.5L2.5,3.5 /></svg>"), ("x.svg", '<svg><path d="M0.5,1.5L2.5,3.5"/></svg>'),
    # The narrowings: integer code these rules leave alone, with rows in FLOATS for the same forms where the file rebinds what the narrowing reads.
    ('x.py', 'x = bytes.fromhex("ff")'), ('x.py', 'x = bytearray.fromhex("ff")'), ("x.py", "x = isinstance(y, float)"), ("x.py", "x = isinstance(y, (float, complex))"), ("x.py", "x = type(y) is complex"), ('x.py', 'import time\nx = time.strftime("%F", time.gmtime(0))'), ('x.py', 'x = d.strftime("%Y%m%d%f")'), ('x.py', 'x = f"{d:%F}"'), ('x.py', 'root = Path("a")\nx = root / name'), ('x.py', 'x = Path("a").parent / name'), ('x.py', 'x = root / name / "c"'),
    ('x.py', 'import struct\nx = struct.unpack_from("<" + "Ii" * c, b)'), ('x.py', 'import struct\nFMT = "<I"\nx = struct.pack(FMT, 1)'), ('x.py', 'x = f"{n:>{w}d}"'), ("x.py", "def f(k):\n    return k\nx = [2 ** k for k in range(3)]"), ("x.py", "for k in range(n - 1, -1, -1):\n    x = 2 ** k"), ("x.py", "for k in range(9, 2, -1):\n    x = 2 ** k"), ("x.py", "k = 8\nk >>= 1\nx = 2 ** k"), ("x.py", "import time\nx = time.timezone"), ('x.py', 'x = {"kind": "float"}'), ('x.py', 'x = ["complex", "truediv", "fromhex"]'),
    ("x.js", "let x = 7n / 2n;"), ("x.js", 'let x = "aXb".replace(/x/gi, "");'), ("x.js", "let x = 2n ** 64n;"), ("x.jsx", "const a = <div>hi</div>;"), ("x.jsx", "const a = <br />;"), ("x.ts", "let x = id<bigint>(7n / 2n);"), ("x.rs", "/// ```text\n/// 0.5 f64\n/// ```\nfn f() {}"), ("x.cpp", "int x = 1'000'000;"), ("x.cpp", "int x = 0x1e5 + 0xFF;"), ("x.cpp", "auto double_it = 1;"), ("x.cpp", "int x = 7 / 2;"),
)
# (path, mode, blob, what the finding holds): rows the scan reads by name and mode. A blob of None stands for one this clone does not hold.
BLOB = "100644"
FILES_RED = (
    ("link.py", "120000", b"target.py", "[links]"), ("lib", "120000", b"exempt", "[links]"), ("sub", "160000", None, "[links]"), ("x.py", BLOB, None, "[links]"), (".gitattributes", BLOB, b"*.rs working-tree-encoding=UTF-16\n", "[links]"), ("a/.gitattributes", BLOB, b"*.py filter=x\n", "[links]"),
    ("helper.pyc", BLOB, b"\x00\x01", "[binary_python]"), ("__pycache__/h.pyc", BLOB, b"\x00\x01", "[binary_python]"), ("results.bin", BLOB, b"PK\x05\x06" + bytes(18), "[binary_python]"), ("x.ipynb", BLOB, b"{}\n", "[other_exts]"), ("x.pyx", BLOB, b"a = 1\n", "[other_exts]"),
    ("tool.v2", BLOB, b"#!/usr/bin/env python3\nx = 1 / 2\n", "true division"), ("tool.cgi", BLOB, b"#!/usr/bin/python3\nx = 1 / 2\n", "true division"), (".verify", BLOB, b"#!/usr/bin/env python3\nx = 1 / 2\n", "true division"), ("verify", BLOB, b"\xef\xbb\xbf#!/usr/bin/env python3\nx = 1 / 2\n", "true division"), ("verify", BLOB, b"#!/usr/bin/env pypy3\nx = 1 / 2\n", "true division"), ("verify", BLOB, b'#!/bin/sh\n"exec" "python3" "$0" "$@"\nx = 1\n', "[shebang_any]"),
    ("verify.txt", BLOB, b"x = 1 / 2\n", "[anything_python]"), ("verify.hbp", BLOB, b"x = 1 / 2\n", "[anything_python]"), ("verify", BLOB, b"x = 1 / 2\n", "[anything_python]"), ("x.py.", BLOB, b"x = 1 / 2\n", "[anything_python]"), ("x.txt", BLOB, b"# coding: utf-7\nx = 1\n", "[anything_python]"),
    ("c.py", BLOB, b"# coding: utf-7\nx = 1\n#+AAo-x = 1 +AC8- 2\n", "[source_bytes]"), ("c.py", BLOB, b"#!/usr/bin/env python3\n# vim: set fileencoding=utf-7 :\nx = 1\n", "[source_bytes]"), ("c.py", BLOB, b"#\r# coding: utf-7\rx = 1\r", "[source_bytes]"), ("c.py", BLOB, b'# coding: shift_jis\nx = 1\ns = "\x83\x5c"; x = 1 / 2 #"\n', "[source_bytes]"), ("c.py", BLOB, b"# coding: latin-1\nx = 1\n", "[source_bytes]"), ("c.py", BLOB, b"# coding: unicode_escape\nx = 1\n#\\x0ax = 1 / 2\n", "true division"), ("c.py", BLOB, b"# coding: nosuchcodec\nx = 1\n", "[source_bytes]"),
    ("c.py", BLOB, b"\xef\xbb\xbfx = 1 / 2\n", "true division"), ("c.py", BLOB, b"\xef\xbb\xbfy = 2 ** -1\nz = 3 / 4\n", POWER), ("x.rs", BLOB, b"version https://git-lfs.github.com/spec/v1\noid sha256:0\nsize 1\n", "[bytes]"), ("x.py", BLOB, b"version https://git-lfs.github.com/spec/v1\noid sha256:0\nsize 1\n", "[bytes]"), ("x.rs", BLOB, b"fn f() {}\0\n", "[bytes]"), ("x.rs", BLOB, b"// \xff\nfn f() {}\n", "[bytes]"),
    ("build.rs", BLOB, b"fn main() {}\n", "[rs_buildsys]"), ("Cargo.toml", BLOB, b"[lib]\nproc-macro = true\n", "[rs_buildsys]"), ("Cargo.toml", BLOB, b'[package]\nbuild = "gen.txt"\n', "[rs_buildsys]"), ("Cargo.toml", BLOB, b'[dependencies]\npaste = "1"\n', "[rs_buildsys]"), ("a/Cargo.toml", BLOB, b'[dependencies]\nq = { path = "../../q" }\n', "[rs_buildsys]"), ("Cargo.lock", BLOB, b'[[package]]\nname = "paste"\nsource = "registry+https://x"\n', "[rs_buildsys]"),
    ("run.yml", BLOB, b"run: python3 -I -X utf8 verify.txt\n", "[run_targets]"), ("run.sh", BLOB, b"python3 verify.txt\n", "[run_targets]"),
)
FILES_CLEAN = (
    ("c.py", BLOB, b"\xef\xbb\xbfx = 1\n"), ("c.py", BLOB, b"# coding: utf-8\nx = 1\n"), ("c.py", BLOB, b"# -*- coding: utf8 -*-\nx = 1\n"), ("c.py", BLOB, b"\xef\xbb\xbf# coding: utf-8\nx = 1\n"), ("tool.v2", BLOB, b"#!/usr/bin/env python3\nx = 1 // 2\n"), ("verify", BLOB, b"#!/bin/sh\nexec ./other\n"), ("run.sh", BLOB, b"#!/bin/sh\nawk 1\n"),
    ("notes.md", BLOB, b"# Title\n\nThe text holds 1.5 and 1 / 2.\n"), ("data.hbp", BLOB, b"ROW|a=0.5|json=0\n"), ("x.txt", BLOB, b"x = 1\n"), ("x.lock", BLOB, b"a = 1\n"), (".gitattributes", BLOB, b"*.hbp -text\n"), ("Cargo.toml", BLOB, b'[dependencies]\nnum-bigint = "0.4"\n'), ("a/Cargo.toml", BLOB, b'[dependencies]\nq = { path = "q" }\n'), ("run.yml", BLOB, b"run: python3 -I -X utf8 scripts/a.py\n"), ("blob.bin", BLOB, b"\x00\x01\x02"),
)
HASH = "0" * 64
LIST_RED = (
    ("a.py | findings=1 | sha256=%s | " % HASH, "row_without_a_reason"), ("a.py | findings=1 | sha256=%s | ." % HASH, "row_without_a_reason"), ("a/ | tree=%s | " % HASH, "row_without_a_reason"),
    ("a.py | findings=1 | a reason", "row_without_a_pin"), ("a.py | findings=1 | sha256=beef | a reason", "row_without_a_pin"), ("a/ | a reason", "row_without_a_pin"), ("a.py | findings=x | sha256=%s | a reason" % HASH, "row_without_a_count"), ("a.py | sha256=%s | a reason" % HASH, "row_without_a_count"),
    ("a.py | findings=1 | sha256=%s | a reason\na.py | findings=2 | sha256=%s | a reason" % (HASH, HASH), "row_twice"), ("a/ | tree=%s | a reason\na/ | tree=%s | a reason" % (HASH, HASH), "row_twice"),
)
LIST_CLEAN = ("# a comment", "", "a.py | findings=1 | sha256=%s | a reason, with | a bar" % HASH, "a/ | tree=%s | a reason" % HASH)


def selftest():
    fails = 0
    for name, text in FLOATS:
        if not findings(text, name):
            fails += 1
            print("NO_FLOAT_SELFTEST|missed=%r|json=0" % text)
    for name, text, holds in NAMED:
        found = findings(text, name)
        if not any(holds in f for f in found):
            fails += 1
            print("NO_FLOAT_SELFTEST|missed=%r|wanted=%s|first=%s|json=0" % (text[:80], holds, found[0] if found else "none"))
    for name, text in CLEAN:
        found = findings(text, name)
        if found:
            fails += 1
            print("NO_FLOAT_SELFTEST|flagged=%r|first=%s|json=0" % (text, found[0]))
    tracked = {"verify.txt", "scripts/a.py"}
    for path, mode, data, holds in FILES_RED:
        found, _ = entry_findings(path, mode, data, tracked)
        if not any(holds in f for f in found):
            fails += 1
            print("NO_FLOAT_SELFTEST|missed_file=%s|wanted=%s|first=%s|json=0" % (path, holds, found[0] if found else "none"))
    for path, mode, data in FILES_CLEAN:
        found, _ = entry_findings(path, mode, data, tracked)
        if found:
            fails += 1
            print("NO_FLOAT_SELFTEST|flagged_file=%s|first=%s|json=0" % (path, found[0]))
    for text, holds in LIST_RED:
        _, _, bad = parse_list(text.split("\n"))
        if not any(b.startswith(holds) for b in bad):
            fails += 1
            print("NO_FLOAT_SELFTEST|row_read_clean=%r|wanted=%s|json=0" % (text[:60], holds))
    folders, files, bad = parse_list(LIST_CLEAN)
    if bad or len(folders) != 1 or len(files) != 1:
        fails += 1
        print("NO_FLOAT_SELFTEST|clean_rows_misread=%d|json=0" % len(bad))
    print("NO_FLOAT_SELFTEST_DONE|must_flag=%d|must_name_its_rule=%d|must_pass=%d|file_rows=%d|list_rows=%d|failed=%d|json=0" % (len(FLOATS), len(NAMED), len(CLEAN), len(FILES_RED) + len(FILES_CLEAN), len(LIST_RED) + len(LIST_CLEAN), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    warnings.simplefilter("ignore")
    args = sys.argv[1:]
    if args == ["--selftest"]:
        sys.exit(selftest())
    if args[:1] == ["--pins"] and args[1:]:
        sys.exit(pins(args[1:]))
    sys.exit(scan(args[0] if args else "."))
