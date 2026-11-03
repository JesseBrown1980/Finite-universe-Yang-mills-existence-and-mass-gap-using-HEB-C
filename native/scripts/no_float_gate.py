#!/usr/bin/env python3
"""
The operator's rule, November 3, 2026: "We can't use float."

Scans tracked code for binary floating point and for Python's Fraction, and fails on what it finds apart from what
FLOAT-EVIDENCE.txt lists. Each row there names a file, how many findings it holds and why it stays, so one more float in a
listed file fails as well. A row ending in / covers a whole folder. Every row needs a reason.

What it reads:
Python (.py .pyw .pyi, and files with a python shebang), by syntax tree: float and complex literals; the names float and
complex; imports of numpy, scipy, mpmath, decimal, fractions, sympy, pandas, torch, statistics, cmath, timeit, ctypes, struct
and json; float arrays; any attribute of math, time or random outside their integer parts, through aliases and from-imports; operator.truediv,
__truediv__, __float__ and clock or file-time attributes; true division, unless a string or Path(...) operand along the chain
marks it as a path join; powers with a negative constant exponent; format specs, str.format, format() and any string holding a %-format
that prints as float; eval, exec, __import__ and importlib, which can reach any of these out of sight.
Rust (.rs): f16 f32 f64 f128, to_f32, as_secs_f64, mul_f64 and their kin, the Float trait, hexf64, 1f64, 0.5, 2. and 1e9.
C, C++, Go (.c .h .cc .cxx .cpp .hh .hpp .go): float, double, float32, float64, __float128, math.* in Go, and the same
literals with .5, 1.f, 1.e5 and 0x1p-1.
JavaScript and HTML (.js .mjs .cjs .ts .jsx .tsx .html .htm): Math.*, parseFloat, toFixed, Number(, Float64Array, the same literals,
and any division in script code, since a JavaScript number is a double unless it is a BigInt.
Native comments and strings are removed first, across lines. Exact rationals in Python are the integer pairs of intpair.py,
divided by name with qdiv. A / on any other exact class counts as a finding, and the list says which those are.

Shell scripts, notebooks and inline code in workflow files are outside this scan. Types are out of reach here too: 2 ** e with a
negative e in a variable, or a float reaching a variable through an unread route, passes, which is why it fails on every route it can name.

usage: no_float_gate.py [ROOT]      Scans ROOT. Exits 1 on a finding that is not listed, when a listed count has moved, or when no code is read.
       no_float_gate.py --selftest  Runs the snippets below. Exits 1 if one is misread. Integer only, json=0.
"""
import ast
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BAD_IMPORT = {"numpy", "scipy", "mpmath", "decimal", "fractions", "sympy", "pandas", "torch", "statistics", "cmath", "timeit", "ctypes", "struct", "importlib", "json"}
# The integer parts of these modules. Any other attribute of them counts.
MATH_OK = {"isqrt", "gcd", "lcm", "factorial", "comb", "perm", "floor", "ceil", "trunc"}
TIME_OK = {"time_ns", "monotonic_ns", "perf_counter_ns", "process_time_ns", "thread_time_ns", "sleep"}
RANDOM_OK = {"Random", "SystemRandom", "seed", "getstate", "setstate", "randrange", "randint", "getrandbits", "randbytes", "choice", "shuffle", "sample"}
WATCHED = {"math": MATH_OK, "time": TIME_OK, "random": RANDOM_OK}
RANDOM_METHODS = {"random", "uniform", "gauss", "normalvariate", "betavariate", "expovariate", "gammavariate", "lognormvariate", "weibullvariate", "vonmisesvariate", "paretovariate", "triangular"}
BAD_ATTRIBUTE = {"truediv", "__truediv__", "__rtruediv__", "__itruediv__", "__float__", "__complex__", "fromhex", "getmtime", "getatime", "getctime", "st_mtime", "st_atime", "st_ctime", "total_seconds", "timestamp", "default_timer", "import_module", "literal_eval", "float", "complex"}
BAD_NAME = {"float", "complex", "eval", "exec", "__import__"}
FLOAT_SPEC = re.compile(r"[eEfFgG%]$")
FORMAT_FIELD = re.compile(r"\{[^{}]*:[^{}]*[eEfFgG%]\}")
PERCENT_FLOAT = re.compile(r"(?<!%)%(\([^)]*\))?[-+#0]*(\*|\d+)?(\.(\*|\d+))?[eEfFgG]")
LITERAL = r"(?<![\w.])\d[\d_]*\.\d|(?<![\w.])\d[\d_]*\.(?![\w.])|(?<![\w.])\d[\d_]*[eE][-+]?_*\d+\b"
C_LITERAL = LITERAL + r"|(?<![\w.)\]])\.\d|(?<![\w.])\d[\d_]*\.[fFlL]\b|(?<![\w.])\d[\d_]*\.[eE][-+]?\d+|\b0[xX][\da-fA-F.]*[pP][-+]?\d+"
PY_EXT = (".py", ".pyw", ".pyi")
NATIVE = (
    ((".rs",), re.compile(r"\b(f16|f32|f64|f128|to_f32|to_f64|from_f32|from_f64|Float)\b|\w_f(16|32|64|128)\b|\d_?f(16|32|64|128)\b|\bhexf(32|64)\b|" + LITERAL)),
    ((".c", ".h", ".cc", ".cxx", ".cpp", ".hh", ".hpp"), re.compile(r"\b(float|double|float32|float64|__float128)\b|" + C_LITERAL)),
    ((".go",), re.compile(r"\b(float32|float64|complex64|complex128)\b|\bmath\.[A-Z]\w*|" + C_LITERAL)),
    ((".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".html", ".htm"), re.compile(r"\bMath\.\w+|\bparseFloat\b|\btoFixed\b|\bNumber\(|\bFloat(32|64)Array\b|" + C_LITERAL)),
)
JS_DIVISION = re.compile(r"[\w)\]]\s*/\s*[\w(]")
SCRIPT_BLOCK = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S | re.I)
RAW_STRING = re.compile(r'(?:b|c)?r(#*)"')
CHAR_LITERAL = re.compile(r"'(\\.[^'\n]*|[^'\\\n])'")


def is_path_join(node):
    # Only the operands themselves, along a chain of joins or concatenations.
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Add)):
        return is_path_join(node.left) or is_path_join(node.right)
    if isinstance(node, ast.JoinedStr) or (isinstance(node, ast.Constant) and isinstance(node.value, str)):
        return True
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("Path", "PurePath")


def negative_constant(node):
    return isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub)


def python_findings(text):
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        return ["syntax error at line %s" % e.lineno]
    aliases = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                top = a.name.split(".")[0]
                if top in WATCHED:
                    aliases[a.asname or a.name] = top
    out = []
    for n in ast.walk(tree):
        line = getattr(n, "lineno", 0)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (float, complex)):
                out.append("float literal at line %d" % line)
            elif isinstance(n.value, (str, bytes)):
                template = n.value if isinstance(n.value, str) else n.value.decode("latin-1")
                if PERCENT_FLOAT.search(template):
                    out.append("float %%-format at line %d" % line)
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
                out += ["from operator import truediv at line %d" % line for a in n.names if a.name == "truediv"]
        elif isinstance(n, ast.Name):
            if n.id in BAD_NAME:
                out.append("%s at line %d" % (n.id, line))
        elif isinstance(n, ast.Attribute):
            if isinstance(n.value, ast.Name) and n.value.id in aliases and n.attr not in WATCHED[aliases[n.value.id]]:
                out.append("%s.%s at line %d" % (aliases[n.value.id], n.attr, line))
            elif n.attr in RANDOM_METHODS or n.attr in BAD_ATTRIBUTE:
                out.append("%s at line %d" % (n.attr, line))
            elif n.attr == "format" and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str) and FORMAT_FIELD.search(n.value.value):
                out.append("float format at line %d" % line)
        elif isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id == "pow" and len(n.args) == 2 and negative_constant(n.args[1]):
                out.append("negative power at line %d" % line)
            elif isinstance(f, ast.Name) and f.id == "format" and len(n.args) == 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str) and FLOAT_SPEC.search(n.args[1].value):
                out.append("float format at line %d" % line)
            elif isinstance(f, ast.Name) and f.id == "getattr" and len(n.args) >= 1 and isinstance(n.args[0], ast.Name) and n.args[0].id in aliases:
                out.append("getattr on %s at line %d" % (aliases[n.args[0].id], line))
            elif ((isinstance(f, ast.Name) and f.id == "array") or (isinstance(f, ast.Attribute) and f.attr == "array")) and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value in ("d", "f"):
                out.append("float array at line %d" % line)
        elif isinstance(n, ast.BinOp):
            if isinstance(n.op, ast.Div) and not is_path_join(n):
                out.append("true division at line %d" % line)
            elif isinstance(n.op, ast.Pow) and negative_constant(n.right):
                out.append("negative power at line %d" % line)
        elif isinstance(n, ast.AugAssign):
            if isinstance(n.op, ast.Div) and not is_path_join(n.value):
                out.append("true division at line %d" % line)
            elif isinstance(n.op, ast.Pow) and negative_constant(n.value):
                out.append("negative power at line %d" % line)
        elif isinstance(n, ast.FormattedValue) and n.format_spec is not None:
            spec = "".join(v.value for v in n.format_spec.values if isinstance(v, ast.Constant))
            dynamic = any(isinstance(v, ast.FormattedValue) for v in n.format_spec.values)
            if FLOAT_SPEC.search(spec) or dynamic:
                out.append("float format at line %d" % line)
    return out


def code_only(text, name):
    nested_comments = name.endswith(".rs")
    backtick = name.endswith((".go", ".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".html", ".htm"))
    single_quoted = name.endswith((".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".html", ".htm"))
    out, i, n = [], 0, len(text)
    while i < n:
        c, two = text[i], text[i:i + 2]
        if two == "//":
            while i < n and text[i] != "\n":
                i += 1
        elif two == "/*":
            depth, i = 1, i + 2
            while i < n and depth:
                if nested_comments and text[i:i + 2] == "/*":
                    depth, i = depth + 1, i + 2
                elif text[i:i + 2] == "*/":
                    depth, i = depth - 1, i + 2
                else:
                    out.append("\n" if text[i] == "\n" else "")
                    i += 1
        elif c == '"' or (backtick and c == "`") or (single_quoted and c == "'"):
            i += 1
            while i < n and text[i] != c:
                i += 2 if text[i] == "\\" else 1
                out.append("\n" if text[i - 1] == "\n" else "")
            i += 1
            out.append('""')
        elif c in "bcr" and RAW_STRING.match(text, i) and not (i and (text[i - 1].isalnum() or text[i - 1] == "_")):
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


def native_findings(text, name):
    for exts, pattern in NATIVE:
        if name.endswith(exts):
            code = code_only(text, name)
            found = {i for i, line in enumerate(code.split("\n"), 1) if pattern.search(line)}
            if name.endswith((".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx")):
                found |= {i for i, line in enumerate(code.split("\n"), 1) if JS_DIVISION.search(line)}
            elif name.endswith((".html", ".htm")):
                for block in SCRIPT_BLOCK.finditer(code):
                    start = code.count("\n", 0, block.start(1)) + 1
                    found |= {start + k for k, line in enumerate(block.group(1).split("\n")) if JS_DIVISION.search(line)}
            return ["line %d" % i for i in sorted(found)]
    return []


def findings(text, name):
    return python_findings(text) if name.endswith(PY_EXT) else native_findings(text, name)


def listed():
    folders, files, bad = {}, {}, []
    for line in open(os.path.join(HERE, "FLOAT-EVIDENCE.txt"), encoding="utf-8"):
        line = line.rstrip("\r\n")
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|", 2)]
        if parts[0].endswith("/"):
            if len(parts) != 2 or not parts[1]:
                bad.append(parts[0])
            folders[parts[0]] = parts[1] if len(parts) > 1 else ""
        else:
            if len(parts) != 3 or not parts[2] or not parts[1].startswith("findings="):
                bad.append(parts[0])
                continue
            files[parts[0]] = int(parts[1].split("=")[1])
    return folders, files, bad


def looks_like_python(full):
    try:
        with open(full, "rb") as f:
            first = f.readline(200)
    except OSError:
        return False
    return first.startswith(b"#!") and b"python" in first


def scan(root):
    raw = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, check=True).stdout
    tracked = [p for p in raw.decode("utf-8", errors="surrogateescape").split("\0") if p]
    folders, files, bad_rows = listed()
    scanned, kept, fails, seen = 0, 0, 0, set()
    for row in bad_rows:
        fails += 1
        print("NO_FLOAT|row_without_a_reason=%s|json=0" % row)
    extensions = PY_EXT + tuple(e for exts, _ in NATIVE for e in exts)
    for path in tracked:
        full = os.path.join(root, path)
        if not os.path.isfile(full):
            continue
        name = path.lower()
        base = os.path.basename(name)
        if not name.endswith(extensions):
            if "." in base or not looks_like_python(full):
                continue
            name = name + ".py"
        scanned += 1
        found = findings(open(full, encoding="utf-8", errors="replace").read(), name)
        folder = [f for f in folders if path.startswith(f)]
        if folder:
            seen.add(folder[0])
            kept += len(found)
        elif path in files:
            seen.add(path)
            kept += len(found)
            if len(found) != files[path]:
                fails += 1
                print("NO_FLOAT|count_moved=%s|listed=%d|found=%d|first=%s|json=0" % (path, files[path], len(found), found[0] if found else "none"))
        elif found:
            fails += 1
            print("NO_FLOAT|file=%s|first=%s|count=%d|json=0" % (path, found[0], len(found)))
    for gone in sorted((set(folders) | set(files)) - seen):
        fails += 1
        print("NO_FLOAT|listed_and_gone=%s|json=0" % gone)
    if scanned == 0:
        fails += 1
        print("NO_FLOAT|no_code_files_read=1|json=0")
    print("NO_FLOAT_DONE|code_files=%d|listed_files=%d|listed_folders=%d|listed_findings=%d|failed=%d|json=0" % (scanned, len(files), len(folders), kept, fails))
    return 1 if fails else 0


FLOATS = (
    ("x.py", "x = 0.5"), ("x.py", "x = 1e9"), ("x.py", "x = 2j"), ("x.py", "x = float(3)"), ("x.py", "x = 1 / 2"), ("x.py", "a /= b"),
    ("x.py", "x = 2 ** -3"), ("x.py", "a **= -1"), ("x.py", "x = pow(2, -1)"), ("x.py", "import numpy"), ("x.py", "from decimal import Decimal"), ("x.py", "from fractions import Fraction as Q"), ("x.py", "import fractions"), ("x.py", "from fractions import Fraction"), ("x.py", "def f():\n    from fractions import Fraction as F\n    return F(1, 2)"), ("x.py", "from intpair import qdiv\nx = qdiv(1, 2) / 3"),
    ("x.py", "import math\nx = math.sqrt(2)"), ("x.py", "import math as m\nx = m.sqrt(2)"), ("x.py", "from math import sqrt"), ("x.py", "import math\nx = math.fabs(2)"),
    ("x.py", "import time\nx = time.time()"), ("x.py", "import time as t\nx = t.time()"), ("x.py", "from time import monotonic"), ("x.py", "x = rng.random()"), ("x.py", "from random import uniform"), ("x.py", "import random as r\nx = r.random()"),
    ("x.py", 'print(f"{a:.2f}")'), ("x.py", 'print("%.3f" % a)'), ("x.py", 'print(f"{a:.1%}")'), ("x.py", 'x = "{:.2f}".format(1)'), ("x.py", 'x = format(1, ".2f")'), ("x.py", 'x = "%(a).2f" % d'), ("x.py", 'x = "%.*f" % (2, 1)'), ("x.py", 'x = b"%.2f" % 1'), ("x.py", 's = ".2f"\nx = f"{1:{s}}"'),
    ("x.py", 'x = d["a"] / 2'), ("x.py", 'x = len("abc") / 2'), ("x.py", 'x = int("3") / 2'),
    ("x.py", "x = list(map(float, y))"), ("x.py", "F = float"), ("x.py", 'x = float.fromhex("a")'), ("x.py", "x = (1).__truediv__(2)"), ("x.py", "import operator\nx = operator.truediv(1, 2)"), ("x.py", "from operator import truediv"),
    ("x.py", 'x = __import__("fractions")'), ("x.py", 'import importlib'), ("x.py", 'x = eval("1/2")'), ("x.py", "x = o.st_mtime"), ("x.py", "x = d.total_seconds()"), ("x.pyw", "x = 0.5"), ('x.py', 's = "%.2f"'), ("x.py", "import builtins\nx = builtins.float(3)"), ('x.py', 'x = array("d", y)'), ("x.py", "import json"), ("x.py", "import ast\nx = ast.literal_eval(y)"),
    ("x.rs", "let a: f64 = 1;"), ("x.rs", "let a = 0.5;"), ("x.rs", "let a = 2.;"), ("x.rs", "let a = 1e9;"), ("x.rs", "let a = 1f64;"), ("x.rs", "let a = x.to_f64();"), ("x.rs", "let a = d.as_secs_f64();"), ("x.rs", "let a = Duration::from_secs_f32(y);"), ("x.rs", "let a = d.mul_f64(y);"), ("x.rs", "let a: f128 = b;"), ("x.rs", "let a = 1e_3;"), ("x.rs", "fn f<T: Float>() {}"), ("x.rs", "let a = hexf64!(y);"),
    ("x.rs", "fn f<'a>(x: f64, y: &'a u8) {}"), ("x.rs", 'let s = "a\nb"; let c = 0.5;'), ("x.rs", "/* a /* b */ c */ let d = 0.5;"), ("x.rs", 'let s = r#"a"b"#; let c = 0.5;'), ("x.rs", 'let s = br#"a"#; let c = 0.5;'), ("x.rs", 'let s = cr#"a"#; let c = 0.5;'),
    ("x.c", "double a;"), ("x.cc", "double a;"), ("x.hpp", "double a;"), ("x.c", "__float128 a;"), ("x.cpp", "x = .5;"), ("x.cpp", "x = 1.f;"), ("x.cpp", "x = 0x1p-1;"), ("x.cpp", "x = 1.e5;"), ("x.go", "var a float64"), ("x.go", "x := math.Sqrt(y)"), ("x.go", "x := .5"),
    ("x.html", "<script>Math.sqrt(2)</script>"), ("x.js", "let a = 1.5;"), ("x.js", "let a = .5;"), ("x.js", 'let a = Number("5");'), ("x.tsx", "let a = 1.5;"), ("x.js", "let a = b / c;"), ("x.html", "<script>\nlet a = b / c;\n</script>"), ("x.html", "<script>let a = new Float64Array(2);</script>"),
)
CLEAN = (
    ("x.py", "x = a // b"), ("x.py", 'p = root / "shards" / name'), ("x.py", 'p = root / f"{a}.hbp"'), ("x.py", 'p = base / (name + ".matrix")'), ("x.py", 'p = Path(a) / b'),
    ("x.py", "import math\nx = math.isqrt(9)"), ("x.py", "import math as m\nx = m.gcd(9, 3)"), ("x.py", "import time\nx = time.time_ns()"), ("x.py", "import time\ntime.sleep(1)"), ("x.py", "from math import isqrt"), ("x.py", "from random import Random"), ('x.py', 'print(f"{a:08x} {b:>9} {c:d}")'),
    ("x.py", 'print("%%-f %d" % a)'), ("x.py", "x = rng.randrange(2)"), ("x.py", "# 0.5 / float\nx = 1"), ("x.py", 's = "0.5 / float"'), ("x.py", "x = 2 ** 3"), ("x.py", 'x = "{:d}".format(1)'),
    ("x.rs", "let a = x.0.1;"), ("x.rs", "for i in 0..5 {}"), ("x.rs", "for i in 0..=5 {}"), ("x.rs", "let a = 0x1e5;"), ("x.rs", "fn f<'a>(x: &'a u8, y: &'a u8) {}"), ("x.rs", "let c = 'f';"),
    ("x.rs", '// f64 0.5\nlet a = 1;'), ("x.rs", 'let s = "HTTP/1.1\nf64 0.5";'), ("x.rs", '/* f64 */ let a = 1;'), ("x.rs", 'let s = r#"a"f64"#;'), ("x.rs", 'let s = br#"f64"#;'), ("x.rs", "let a = 1.max(2);"), ("x.rs", "let a = 12_345;"),
    ("x.c", 'int a = 1; /* double */'), ("x.go", 'var a uint64'), ("x.go", 'x := `0.5`'), ("x.js", "let v = '1.5';"), ("x.html", '<small>HTTP/"1.1" Rust "1.81"</small>'), ("x.html", "<p>a / b</p>"), ('x.py', 'x = array("q", y)'), ('x.py', 's = "5% faster"'),
    ("x.py", "from intpair import IntPair as F, qdiv\nx = qdiv(F(1, 2), 3)"), ("x.py", "import time\nx = time.monotonic_ns()"), ("x.py", "# from fractions import Fraction\nx = 1"), ("x.py", 's = "from fractions import Fraction"'), ("x.rs", "let a = q.sqrt();"),
)


def selftest():
    fails = 0
    for name, text in FLOATS:
        if not findings(text, name):
            fails += 1
            print("NO_FLOAT_SELFTEST|missed=%r|json=0" % text)
    for name, text in CLEAN:
        found = findings(text, name)
        if found:
            fails += 1
            print("NO_FLOAT_SELFTEST|flagged=%r|first=%s|json=0" % (text, found[0]))
    print("NO_FLOAT_SELFTEST_DONE|must_flag=%d|must_pass=%d|failed=%d|json=0" % (len(FLOATS), len(CLEAN), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    sys.exit(scan(sys.argv[1] if len(sys.argv) > 1 else "."))
