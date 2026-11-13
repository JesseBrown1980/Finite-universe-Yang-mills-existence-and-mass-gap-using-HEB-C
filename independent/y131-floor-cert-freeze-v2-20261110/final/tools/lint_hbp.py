# Record lint for the floor lane's frozen prediction (HBP house form). Integers only; python3 -I -B.
# Usage: python3 -I -B lint_hbp.py FILE.hbp FLOOR_ROOT
import sys
import re
import hashlib
import os

path, root = sys.argv[1], sys.argv[2]
raw = open(path, "rb").read()
errors = []
def err(n, msg):
    errors.append("line %d: %s" % (n, msg))

TYPES = {"FREEZE", "PIN", "REQUIRED", "PREDICT", "LINK", "STATUS", "DISCLOSE"}
TAGS = {"DERIVED", "CONJECTURE", "REPORTED", "OPEN", "REQUIRED"}
TYPE_TAGS = {"FREEZE": {"REQUIRED"}, "PIN": {"REQUIRED"}, "REQUIRED": {"REQUIRED"},
             "PREDICT": {"CONJECTURE", "OPEN", "DERIVED"}, "LINK": {"REPORTED", "REQUIRED"},
             "STATUS": {"REPORTED", "DERIVED", "OPEN"}, "DISCLOSE": {"REPORTED"}}
MUST = ["id", "quantity", "value", "tag", "met_if", "not_met_if", "falsifier"]
NODEC = ["value", "met_if", "not_met_if", "falsifier"]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
KEY = re.compile(r"^[a-z][a-z0-9_]*$")
KEY_END = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
DEC = re.compile(r"[0-9]\.[0-9]")
SHA16 = re.compile(r"(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])")
# 16-hex fingerprints quoted in DISCLOSE rows that name files no longer on disk (deleted, disclosed in the row itself)
EXTERNAL16 = {"4c72b3e31eb4a1f2"}

if b"\r" in raw:
    err(0, "CR found (LF only)")
if not raw.endswith(b"\n"):
    err(0, "no final newline")
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = ""
    err(0, "not UTF-8")
for i, ch in enumerate(text):
    if ord(ch) > 126 or (ord(ch) < 32 and ch != "\n"):
        err(0, "non-ASCII or control character at offset %d" % i)
        break

lines = text.split("\n")[:-1]
rows, end, ids = [], None, []
seen_row = False
for n, line in enumerate(lines, 1):
    if line.startswith("#"):
        if seen_row:
            err(n, "comment after the first row")
        continue
    if line == "":
        err(n, "empty line")
        continue
    if " " in line or "\t" in line:
        err(n, "whitespace inside a row")
    seen_row = True
    parts = line.split("|")
    typ = parts[0]
    if parts[-1] != "json=0":
        err(n, "last field is not json=0")
    kv = {}
    for p in parts[1:]:
        if "=" not in p:
            err(n, "field without '=': %s" % p[:40])
            continue
        k, v = p.split("=", 1)
        if not (KEY_END if typ == "PREDICTION_END" else KEY).match(k):
            err(n, "bad key %s" % k)
        if v == "":
            err(n, "empty value for %s" % k)
        if k in kv:
            err(n, "duplicate key %s" % k)
        kv[k] = v
    if typ == "PREDICTION_END":
        if end is not None:
            err(n, "second PREDICTION_END")
        end = (n, kv)
        continue
    if end is not None:
        err(n, "row after PREDICTION_END")
    if typ not in TYPES:
        err(n, "unknown row type %s" % typ)
        continue
    for k in MUST:
        if k not in kv:
            err(n, "missing %s" % k)
    tag = kv.get("tag", "")
    if tag not in TAGS:
        err(n, "bad tag %s" % tag)
    elif tag not in TYPE_TAGS[typ]:
        err(n, "tag %s not allowed on %s" % (tag, typ))
    for k in NODEC:
        if k in kv and DEC.search(kv[k]):
            err(n, "decimal number in machine field %s (use a/b)" % k)
    if kv.get("falsifier", "").lower() in ("none", "na", "n/a", "-"):
        err(n, "falsifier is not concrete")
    if typ == "PREDICT" and tag == "CONJECTURE" and "basis" not in kv:
        err(n, "CONJECTURE without basis")
    rows.append((n, typ, kv))
    ids.append(kv.get("id", ""))

for want, (n, typ, kv) in enumerate(rows, 1):
    if kv.get("id") != "%03d" % want:
        err(n, "id %s, expected %03d" % (kv.get("id"), want))
idset = set(ids)
# cross-references to this file's rows: every "row_NNN" outside #137 contexts must exist
for n, typ, kv in rows:
    for k, v in kv.items():
        for m in re.finditer(r"(#137_)?rows?_([0-9]{3})((?:_and_|-|_)([0-9]{3}))*", v):
            if m.group(1) or "#137" in v[max(0, m.start() - 20):m.start()]:
                continue
            for ref in re.findall(r"[0-9]{3}", m.group(0)):
                if ref not in idset:
                    err(n, "reference row_%s not in this file (key %s)" % (ref, k))

# PIN rows with a path: recompute sha256
npin = 0
for n, typ, kv in rows:
    if typ == "PIN" and "path" in kv:
        npin += 1
        v = kv["value"]
        if not HEX64.match(v):
            err(n, "PIN value is not 64 lowercase hex")
            continue
        fp = os.path.normpath(os.path.join(root, kv["path"]))
        try:
            got = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        except OSError:
            err(n, "PIN path unreadable %s" % kv["path"])
            continue
        if got != v:
            err(n, "PIN mismatch %s: file %s" % (kv["path"], got[:16]))
    for k in ("value",):
        if typ == "PIN" and kv.get("quantity", "").startswith("row_hash") and not HEX64.match(kv.get(k, "")):
            err(n, "row hash is not 64 hex")

# DISCLOSE fingerprints are bound to named files. Each files= entry path@sha16 must be the sha16 of that file; a
# complete=DIR row must list every file under DIR (target/ excluded); every other 16-hex fingerprint in the row must
# equal an entry of its own files=, a PIN value (bound to the PIN's path above) or an EXTERNAL16 entry.
def sha16(fp):
    h = hashlib.sha256()
    with open(fp, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]
pinvals = set(kv["value"][:16] for n, typ, kv in rows if typ == "PIN" and HEX64.match(kv.get("value", "")))
n16 = nbound = nfiles = 0
for n, typ, kv in rows:
    if typ != "DISCLOSE":
        continue
    named = {}
    for e in kv.get("files", "").split(",") if "files" in kv else []:
        if e.count("@") != 1:
            err(n, "files entry without one @: %s" % e[:60])
            continue
        rel, want = e.split("@")
        if rel in named:
            err(n, "files entry %s named twice" % rel)
        named[rel] = want
        nfiles += 1
        fp = os.path.normpath(os.path.join(root, rel))
        if not re.match(r"^[0-9a-f]{16}$", want):
            err(n, "files entry %s: fingerprint is not 16 hex" % rel)
        elif not os.path.isfile(fp):
            err(n, "files entry %s: no such file" % rel)
        elif sha16(fp) != want:
            err(n, "files entry %s: named file is %s, row says %s" % (rel, sha16(fp), want))
    if "complete" in kv:
        d = kv["complete"]
        if not d.startswith("work/") or "/" in d[5:] or not os.path.isdir(os.path.join(root, d)):
            err(n, "complete=%s is not an existing top-level work/ dir" % d)
        else:
            for dp, dn, fn in os.walk(os.path.join(root, d)):
                dn[:] = [x for x in dn if x != "target"]
                for f in fn:
                    rel = os.path.relpath(os.path.join(dp, f), root)
                    if rel not in named:
                        err(n, "complete=%s: file %s is not in files=" % (d, rel))
    bound = set(named.values())
    for k, v in kv.items():
        if k == "files":
            continue
        for m in SHA16.finditer(v):
            n16 += 1
            g = m.group(0)
            if g in bound or g in pinvals or g in EXTERNAL16:
                nbound += 1
            else:
                err(n, "fingerprint %s (key %s) is bound to no named file of this row, no PIN and no EXTERNAL16" % (g, k))

# PREDICTION_END counts
if end is None:
    err(0, "no PREDICTION_END")
else:
    n, kv = end
    cnt = {"rows": len(rows)}
    for t in TYPES:
        cnt[t] = sum(1 for r in rows if r[1] == t)
    for t in TAGS:
        cnt[t + "_TAG" if t == "REQUIRED" else t] = sum(1 for r in rows if r[2].get("tag") == t)
    for k, v in cnt.items():
        if kv.get(k) != str(v):
            err(n, "PREDICTION_END %s=%s, counted %d" % (k, kv.get(k), v))
    if kv.get("r9_quantities_computed_by_this_lane") != "NONE":
        err(n, "r9 declaration missing")
    if kv.get("json") != "0":
        err(n, "json=0 missing")

me = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
print("LINT|file=%s|sha256=%s|rows=%d|pins_checked=%d|disclose_files_checked=%d|disclose_fingerprints_bound=%d/%d|lint_sha256=%s"
      % (os.path.basename(path), hashlib.sha256(raw).hexdigest(), len(rows), npin, nfiles, nbound, n16, me))
for e in errors:
    print("ERROR|" + e)
print("LINT_RESULT|errors=%d" % len(errors))
sys.exit(1 if errors else 0)
