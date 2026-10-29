#!/usr/bin/env python3
"""Frozen 3x4 memory pilot runner. Measurement only; never lifts production HOLD.
Requires MEMORY-PILOT-SPEC.md and the existing memory_pilot_derive.py.
All outputs are integer HBP lines; status and SHA sidecar written on every normal outcome.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory_pilot_derive

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "native/ym/out"
OUT.mkdir(parents=True, exist_ok=True)
RECEIPT = OUT / "HEBC-YM-3X4-MEMORY-PILOT.hbp"
SIDECAR = OUT / "HEBC-YM-3X4-MEMORY-PILOT.sha256"
BUDGET = 12 * (1 << 30)
N_EXPECT = 45_508_080
STORE_SIZE = 35 * (1 << 30)
FREE_MARGIN = 1 << 30
KEY_BYTES = N_EXPECT * 8
PASSA_BYTES = N_EXPECT * 16
JOBS = (1, 2, 4)
RAW = []
temp = None
abort_requested = False

def field(line: str, name: str) -> str:
    m = re.search(r"(?:^|\|)" + re.escape(name) + r"=([^|]*)", line)
    return m.group(1) if m else ""

def emit(line: str) -> None:
    if "\n" in line or "\r" in line:
        raise RuntimeError("multiline_hbp")
    with RECEIPT.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(4 * (1 << 20)), b""):
            h.update(b)
    return h.hexdigest()

def safe(v: object) -> str:
    return str(v).replace("|", "/").replace("\n", " ").replace("\r", " ")

def runlog(command: list[str], outfile: Path, env: dict | None = None,
           timeout: int = 19000, preexec_fn=None) -> tuple[int, int]:
    t0 = time.monotonic()
    with outfile.open("w", encoding="utf-8") as stream:
        try:
            cp = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                env=env, timeout=timeout, preexec_fn=preexec_fn,
                                check=False)
            return cp.returncode, int(time.monotonic() - t0)
        except subprocess.TimeoutExpired:
            return 124, int(time.monotonic() - t0)

def ensure(cond: bool, reason: str) -> None:
    if not cond:
        raise RuntimeError(reason)

def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

def workers() -> int:
    return int(subprocess.check_output(["nproc"], text=True).strip())

def capture_identity() -> None:
    paths = [
        "native/ym/results/3x4_stream/MEMORY-PILOT-SPEC.md",
        "native/ym/results/3x4_stream/MEMORY-PILOT-SPEC.sha256",
        ".github/workflows/hebc-ym-3x4-memory-pilot.yml",
        "native/ym/python/memory_pilot_runner.py",
        "native/ym/python/memory_pilot_controls.py",
        "native/ym/python/memory_pilot_derive.py",
        "native/ym/crates/torusl/src/bin/ymroom.rs",
        "native/ym/crates/sturmrs/src/bin/roomschur.rs",
    ]
    emit(f"PILOT_IDENTITY|run={safe(os.environ.get('GITHUB_RUN_ID', '-'))}|head={git_head()}|budget={BUDGET}|json=0")
    for path in paths:
        p = ROOT / path
        ensure(p.is_file(), "missing_identity_file_" + path.replace("/", "_"))
        emit(f"PILOT_SOURCE|file={path}|sha256={digest(p)}|json=0")
    for binname in ("ymroom", "roomschur"):
        p = ROOT / "native/ym/target/release" / binname
        ensure(p.is_file(), "missing_binary_" + binname)
        emit(f"PILOT_BINARY|name={binname}|sha256={digest(p)}|json=0")
    ensure(subprocess.run(["git", "merge-base", "--is-ancestor",
                           "b45dbe3f2d27bd972c90d76a9af18c8fffd4c0cd",
                           "HEAD"], cwd=ROOT).returncode == 0, "P1_sources_not_in_head")
    ci = (ROOT / "native/ym/results/3x4_stream/ci-40936173167/HEBC-YM-ROOM-IDENTITY-CI.hbp").read_text()
    ensure("ROOM_IDENTITY_CI_RESULT|P2=PASS|P3_v2=AGREE|integrity_and_equivalence=1|" in ci,
           "P2_P3_receipt_missing")
    emit("PILOT_P1P3|P1=MERGED|P2=PASS|P3_v2=AGREE|P3_90M=AMBIGUOUS|json=0")

def host_identity() -> None:
    emit("PILOT_HOST|ImageOS=" + safe(os.environ.get("ImageOS", "-")) +
         "|ImageVersion=" + safe(os.environ.get("ImageVersion", "-")) +
         "|nproc=" + str(workers()) +
         "|kernel=" + safe(os.uname().release) +
         "|cgroup_v2=" + str(int(Path("/sys/fs/cgroup/cgroup.controllers").exists())) +
         "|json=0")
    mem = Path("/proc/meminfo").read_text()
    emit("PILOT_HOST_MEM|" + safe(next((x for x in mem.splitlines() if x.startswith("MemTotal:")), "-")) + "|json=0")
    cpu = Path("/proc/cpuinfo").read_text()
    emit("PILOT_HOST_CPU|" + safe(next((x for x in cpu.splitlines() if x.startswith("model name")), "-")) + "|json=0")

def cgroup_parent() -> Path:
    c = Path("/sys/fs/cgroup")
    ensure((c / "cgroup.controllers").exists(), "no_cgroup_v2")
    loc = next((l.split("::", 1)[1].strip() for l in Path("/proc/self/cgroup").read_text().splitlines()
                if l.startswith("0::")), None)
    ensure(loc is not None, "no_cgroup_path")
    path = c / loc.lstrip("/")
    ensure(path.exists() and os.access(path, os.W_OK), "cgroup_not_writable")
    controllers = (path / "cgroup.controllers").read_text().split()
    ensure("memory" in controllers, "cgroup_memory_controller_unavailable")
    return path

def check_cgroup(parent: Path) -> None:
    child = parent / ("hebc-p4-preflight-" + str(os.getpid()))
    child.mkdir()
    try:
        ensure((child / "memory.peak").exists(), "cgroup_peak_unavailable")
        ensure((child / "memory.events").exists(), "cgroup_events_unavailable")
        ensure((child / "memory.stat").exists(), "cgroup_stat_unavailable")
        (child / "memory.max").write_text(str(BUDGET))
    finally:
        child.rmdir()

def select_volume() -> tuple[Path, int]:
    mounts = subprocess.check_output(["df", "-B1", "-P"], text=True).splitlines()[1:]
    candidates = []
    for row in mounts:
        parts = row.split()
        if len(parts) < 6:
            continue
        m = Path(" ".join(parts[5:]))
        if not m.exists() or not os.access(m, os.W_OK | os.X_OK):
            continue
        free = os.statvfs(m).f_bavail * os.statvfs(m).f_frsize
        candidates.append((free, m))
        emit(f"PILOT_VOLUME|mount={safe(m)}|free_bytes={free}|json=0")
    ensure(bool(candidates), "no_writable_volume")
    free, mount = max(candidates, key=lambda x: x[0])
    ensure(free >= STORE_SIZE + KEY_BYTES + PASSA_BYTES + FREE_MARGIN,
           "disk_fit_failure")
    root = mount / ("hebc-p4-" + os.environ.get("GITHUB_RUN_ID", str(os.getpid())))
    root.mkdir(exist_ok=False)
    return root, free

def read_time(path: Path) -> int:
    t = path.read_text(errors="replace") if path.exists() else ""
    m = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", t)
    ensure(m is not None, "missing_ru_maxrss")
    return int(m.group(1))

def cgroup_run(parent: Path, k: int, room: Path) -> None:
    cg = parent / f"hebc-pilot-{os.getpid()}-K{k}"
    cg.mkdir()
    log = OUT / f"pilot-K{k}.hbp"
    tfile = OUT / f"pilot-K{k}.time"
    events = {"oom": 0, "oom_kill": 0}
    anon_max = 0
    proc = None
    try:
        (cg / "memory.max").write_text(str(BUDGET))
        def join():
            (cg / "cgroup.procs").write_text(str(os.getpid()))
        env = dict(os.environ, ROOMSCHUR_COLS=f"0:{k}", ROOMSCHUR_K=str(k),
                   ROOMSCHUR_BUDGET=str(BUDGET), WORKERS=str(workers()))
        cmd = ["/usr/bin/time", "-v", "-o", str(tfile),
               str(ROOT / "native/ym/target/release/roomschur"), str(room),
               "0", "1000", "9000", "60000000", "12", "1000", "2"]
        t0 = time.monotonic()
        with log.open("w", encoding="utf-8") as stream:
            proc = subprocess.Popen(cmd, stdout=stream, stderr=subprocess.STDOUT,
                                    env=env, preexec_fn=join, start_new_session=True)
            while proc.poll() is None:
                stats = (cg / "memory.stat").read_text()
                m = re.search(r"^anon (\d+)$", stats, re.MULTILINE)
                ensure(m is not None, "anon_stat_missing")
                anon_max = max(anon_max, int(m.group(1)))
                time.sleep(1)
            code = proc.wait()
        secs = int(time.monotonic() - t0)
        mm = re.search(r"^anon (\d+)$", (cg / "memory.stat").read_text(), re.MULTILINE)
        if mm:
            anon_max = max(anon_max, int(mm.group(1)))
        mempeak = int((cg / "memory.peak").read_text().strip())
        for line in (cg / "memory.events").read_text().splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[0] in events:
                events[parts[0]] = int(parts[1])
        text = log.read_text(errors="replace")
        scol0 = "".join(line + "\n" for line in text.splitlines()
                        if line.startswith("SCOL|") and "|cb=0|" in line)
        ensure(bool(scol0) or events["oom"] > 0 or events["oom_kill"] > 0,
               "missing_col0_scol")
        sha = hashlib.sha256(scol0.encode()).hexdigest() if scol0 else "-"
        admitted = next((field(line, "admitted") for line in text.splitlines()
                         if line.startswith("ROOMSCHUR_ADMISSION|")), "0")
        rss_kib = read_time(tfile) if tfile.exists() else 0
        ensure(tfile.exists() or events["oom"] > 0 or events["oom_kill"] > 0,
               "missing_ru_maxrss")
        line = (f"PILOT_RUN|K={k}|ru_maxrss_kib={rss_kib}|anon_max={anon_max}"
                f"|memory_peak={mempeak}|oom={events['oom']}|oom_kill={events['oom_kill']}"
                f"|exit={code}|admitted={admitted}|scol_col0_sha256={sha}|json=0")
        emit(line)
        emit(f"PILOT_RUN_BINDING|K={k}|seconds={secs}|full_log_sha256={digest(log)}|json=0")
        RAW.append(line)
    finally:
        if proc is not None and proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=20)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except OSError:
                    pass
                proc.wait(timeout=20)
        cg.rmdir()

def signal_stop(signum, _frame):
    global abort_requested
    abort_requested = True
    raise RuntimeError("signal_" + str(signum))

def main() -> int:
    global temp
    RECEIPT.write_text("", encoding="utf-8")
    signal.signal(signal.SIGTERM, signal_stop)
    try:
        capture_identity()
        host_identity()
        ensure(Path("/usr/bin/time").exists(), "missing_gnu_time")
        parent = cgroup_parent()
        check_cgroup(parent)
        temp, _ = select_volume()
        keys = temp / "keys.bin"
        room = temp / "store.rooms"
        passa = temp / "passa.bin"
        # Explicit disk reservation, not just a sparse truncate.
        for path, length in ((keys, KEY_BYTES), (room, STORE_SIZE)):
            cp = subprocess.run(["fallocate", "-l", str(length), str(path)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            ensure(cp.returncode == 0, "fallocate_failed_" + path.name)
        binary = str(ROOT / "native/ym/target/release/ymroom")
        a_log = OUT / "pilot-passa.hbp"
        env = dict(os.environ, WORKERS=str(workers()))
        atime = OUT / "pilot-passa.time"
        rc, sec = runlog(["/usr/bin/time", "-v", "-o", str(atime),
                          binary, "passa", "3", "4", str(passa)], a_log, env=env)
        ensure(rc == 0, "passa_failure")
        ptext = a_log.read_text()
        pa = next((x for x in ptext.splitlines() if x.startswith("YMROOM_PASSA|")), "")
        ensure(field(pa, "states") == str(N_EXPECT), "passa_state_mismatch")
        emit(f"PILOT_BUILD_A|seconds={sec}|ru_maxrss_kib={read_time(atime)}|{pa}|sha256={digest(passa)}|json=0")
        b_log = OUT / "pilot-build.hbp"
        btime = OUT / "pilot-build.time"
        rc, sec = runlog(["/usr/bin/time", "-v", "-o", str(btime),
                          binary, "build", "3", "4", str(passa), str(keys),
                          str(room), "0"], b_log, env=env)
        ensure(rc == 0, "room_build_failure")
        btext = b_log.read_text()
        hdr = next((x for x in btext.splitlines() if x.startswith("YMROOMHDR|")), "")
        build = next((x for x in btext.splitlines() if x.startswith("YMROOM_BUILD|")), "")
        ensure(field(hdr, "n") == str(N_EXPECT) and
               field(hdr, "w_self_adjoint") == "PASS" and
               field(build, "header_readback") == "EXACT", "room_build_identity_failure")
        emit(f"PILOT_BUILD_B|seconds={sec}|ru_maxrss_kib={read_time(btime)}|{hdr}|{build}|json=0")
        nline = f"PILOT_N|n={N_EXPECT}|json=0"
        emit(nline)
        RAW.append(nline)
        for k in JOBS:
            cgroup_run(parent, k, room)
        outcome = memory_pilot_derive.derive(RAW)
        for line in outcome:
            emit(line)
        return 0 if outcome[-1].startswith("PILOT_OUTCOME|PILOT_PASS|") else 2
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as e:
        reason = safe(e).replace(" ", "_")
        emit(f"PILOT_FAIL|reason={reason}|json=0")
        emit("PILOT_OUTCOME|INCONCLUSIVE|reason=pilot_failed_closed|json=0")
        return 2
    finally:
        # Never mutate the production admission spec here, even after PILOT_PASS.
        if temp is not None and temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
        SIDECAR.write_text(digest(RECEIPT) + "  " + RECEIPT.name + "\n")

if __name__ == "__main__":
    sys.exit(main())
