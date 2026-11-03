# Reads the corrected run's receipts at fead9ed against one another and against the run folder on D:, read only.
# usage: receipts_check2.py ROOT_OF_EXPORT OUT_HBP   Integer only, json=0.
import hashlib, re, sys

X, OUT = sys.argv[1], sys.argv[2]
P = X + "/native/ym/results/3x4_stream/perron/"
A = P + "allpairs/"
F = A + "failclosed/"
PIN = F + "pin-0fd24d3/"
D = "D:/ym-3x4-room-run/p0-ball/allpairs-pin-0fd24d3/"
log = open(OUT, "w", encoding="utf-8", newline="\n")
bad = 0


def rd(p):
    return open(p, "rb").read()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def norm_rows(b):
    return re.sub(rb"\|secs=[0-9]+\|", b"|secs=S|", b.replace(b"\r\n", b"\n"))


def check(label, got, want):
    global bad
    ok = got == want
    bad += 0 if ok else 1
    log.write("RECEIPT|%s|got=%s|want=%s|met=%d|json=0\n" % (label, str(got)[:80], str(want)[:80], int(ok)))


out_pin = rd(PIN + "ALLPAIRS-3x4-PIN.out")
out_orig = rd(A + "ALLPAIRS-3x4.out")
check("pin_out_sha", sha(out_pin), "b53b281afc1f4e1313dbc739017cb99b84275d4be715f984acbaf76cb251b027")
check("pin_out_equals_D_file", sha(rd(D + "allpairs-3x4.out")), sha(out_pin))
check("D_stderr_bytes", len(rd(D + "allpairs-3x4.err")), 0)
check("D_source_sha", sha(rd(D + "allpairs.rs")), "5ab04b184a4395a779ec6b2189352ea54533f7d1c49b32275d0f30d15d83f4ef")
check("D_exe_sha", sha(rd(D + "allpairs.exe")), "cdb22218bbfe26a2ac5ad380b20a5fffa7b8d0316990edc1366c2289003e3b78")
check("D_run_script_equals_committed", sha(rd(D + "run_allpairs34.sh")), sha(rd(PIN + "run_allpairs34.sh")))
check("D_run_ledger_equals_committed", sha(rd(D + "RUN.hbp")), sha(rd(PIN + "PIN-RUN.hbp")))
check("D_compare_equals_committed", sha(rd(D + "PIN-COMPARE.hbp")), sha(rd(PIN + "PIN-COMPARE.hbp")))
check("D_compare_controls_equals_committed", sha(rd(D + "COMPARE-CONTROLS.hbp")), sha(rd(PIN + "COMPARE-CONTROLS.hbp")))
check("rows_normalised_pin", sha(norm_rows(out_pin)), "609bc96f41599df17c177fa6119daaee2b7f5dd54d31df7e91806ce5236a121a")
check("rows_normalised_original", sha(norm_rows(out_orig)), "609bc96f41599df17c177fa6119daaee2b7f5dd54d31df7e91806ce5236a121a")
check("compare_lf_sha", sha(rd(PIN + "PIN-COMPARE.hbp")), "0b7077a7f7423093d62bf4cbe673040d10caa00c2bd7e49057a2aae4cd215206")
check("compare_crlf_sha_of_the_row_before", sha(rd(PIN + "PIN-COMPARE.hbp").replace(b"\n", b"\r\n")), "e74b77b65ff2ba7e755b1570f7083eda606ec02e9bbf743b28ebe9ccff1b6554")
check("compare_controls_sha", sha(rd(PIN + "COMPARE-CONTROLS.hbp")), "8c3b0432c94c1ec942329e9d09339b89cac88ff97c01bd7eaa3af3e5b5cc1a5b")
hp = rd(PIN + "HEADER-CONTROLS-PIN.hbp")
hl = rd(F + "HEADER-CONTROLS.hbp")
hh = rd(F + "hosted/HEADER-CONTROLS.hbp")
cp = rd(PIN + "CONTROLS-PIN.hbp")
cr = rd(F + "CONTROLS-REPEAT.hbp")
co = rd(A + "CONTROLS.hbp")
check("header_pin_sha", sha(hp), "175f14d211eac729c3dfbb11200169d5159cbbd53902949b81fea875718a5c4c")
check("controls_pin_sha", sha(cp), "bf3aa65ed8ad059c918b8492bcd869b79a57599131f7368b28f4d2679eb9134f")
check("controls_repeat_sha", sha(cr), "8cb42c1d44028b27fabb04fb6384108914139f6f4dcead8ebfc1d857f80b7fce")
check("header_local_sha", sha(hl), "4c838bb1874167f48b2c605f14b7a1506bb8d8e167520efbdc1c57361e4dd0af")
check("header_hosted_sha", sha(hh), "c3cd178048e44acf0a699d6d1b54b6ce9a74d3c3482ef107c8e890b7902e2157")
check("controls_normalised_pin", sha(norm_rows(cp)), "0305a59320f28ec6a7b2dffbae9c2c13dad471924d423b5a6b1f9c884f3f8298")
check("controls_normalised_repeat", sha(norm_rows(cr)), "0305a59320f28ec6a7b2dffbae9c2c13dad471924d423b5a6b1f9c884f3f8298")
check("controls_normalised_original", sha(norm_rows(co)), "0305a59320f28ec6a7b2dffbae9c2c13dad471924d423b5a6b1f9c884f3f8298")
strip = lambda b: b"\n".join(x for x in b.split(b"\n") if not x.startswith(b"HEADER_TOOL|"))
check("header_rows_pin_equal_local_apart_from_tool_hash", sha(strip(hp)), sha(strip(hl)))
check("header_rows_hosted_equal_local_apart_from_tool_hash", sha(strip(hh)), sha(strip(hl)))
check("fixture_hosted_sha", sha(rd(F + "hosted/FIXTURE-CONTROLS.hbp")), "3ff98769cbe190d330258eb591083e7f6a97924c325095e7864e631d0fb46f01")
check("hosted_log_sha", sha(rd(F + "hosted/run.log")), "215915dd5bb9cfa0a7b227adaf03196f6541268086320c4f2c8c35dd5d4feb5a")
pred = rd(F + "HEADER-PREDICTION.hbp").decode().splitlines()
rows = [x for x in pred if x.startswith("HEADER_PREDICTION|")]
check("header_prediction_rows", len(rows), 62)
check("header_prediction_sha_row", sha("\n".join(rows).encode()), "5dffa11f51f5ded06b4deeaed3191d5c9395b3cff2f49cb83f1435809d0ab158")
# Every RESULT_FILE row that names a file under allpairs/, and the sidecar.
res = rd(P + "PERRON-RESULT.hbp").decode().splitlines()
n = m = 0
for r in res:
    if r.startswith("RESULT_FILE|allpairs/"):
        p = r.split("|")[1]
        want = r.split("sha256=")[1].split("|")[0]
        n += 1
        try:
            m += sha(rd(P + p)) == want
        except OSError:
            log.write("RECEIPT|result_file_missing|%s|json=0\n" % p)
check("result_file_rows_for_allpairs_match", m, n)
log.write("RECEIPT_RESULT_FILE_ROWS|rows=%d|json=0\n" % n)
check("perron_result_sidecar", rd(P + "PERRON-RESULT.sha256").decode().split()[0], sha(rd(P + "PERRON-RESULT.hbp")))
log.write("RECEIPTS_DONE|not_met=%d|json=0\n" % bad)
log.close()
print("RECEIPTS_DONE|not_met=%d|json=0" % bad)
sys.exit(1 if bad else 0)
