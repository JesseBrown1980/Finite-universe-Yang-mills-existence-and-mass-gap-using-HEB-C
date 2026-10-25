#!/usr/bin/env python3
"""
HEB-C evolution test ground: a local backend page that lets the finite S3
2x2-torus Hamiltonian evolve in Euclidean time and measures the gap from the
relaxation, side by side with the certified Sturm brackets from ledger.hbp.

Routes (127.0.0.1 only, text lines end json=0; no JSON anywhere):
  /                      page: table + one SVG per ratio
  /evolve/JE/JB          one measurement line
  /svg/JE/JB             integer SVG of log2(energy drop) per step
Integer-only: the plot's y-axis is bit_length() of each drop (exact log2), so
a clean exponential decay is a straight line whose slope gives the gap.
"""
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import evolve as V

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(HERE)
MATRIX = os.environ.get("HEBC_MATRIX", os.path.join(S, "p9", "matrix.txt"))  # PR #9 1393-state export
LEDGER = os.environ.get("HEBC_LEDGER", os.path.join(S, "ladder", "ledger.hbp"))
RATIOS = [(1, 0), (1, 1), (1, 2), (1, 3), (1, 5), (1, 6)]
STEPS = {0: 400, 1: 600, 2: 900, 3: 1500, 5: 3000, 6: 3500}
RESULTS = {}
LOCK = threading.Lock()


def certified():
    out = {}
    if os.path.exists(LEDGER):
        for line in open(LEDGER):
            f = dict(kv.split("=", 1) for kv in line.strip().split("|")[1:] if "=" in kv)
            if f.get("kind") == "rung":
                out[int(f["r"])] = (f["E0_upper"], f["E1_lower"], f["gap_per_JE_gt"])
    return out


def compute(je, jb):
    key = (je, jb)
    with LOCK:
        if key in RESULTS:
            return RESULTS[key]
    en, c24 = V.evolve(MATRIX, je, jb, STEPS.get(jb, 2000))
    gap, e0 = V.measure_gap(en, c24, je)
    drops = [en[k] - en[k + 1] for k in range(len(en) - 1)]
    res = {"gap": gap, "e0": e0, "c24": c24, "steps": len(en),
           "logd": [d.bit_length() if d > 0 else 0 for d in drops]}
    with LOCK:
        RESULTS[key] = res
    return res


def line(je, jb):
    r = compute(je, jb)
    return ("EVOLVE|JE=%d|JB=%d|steps=%d|c=%d/24|E0_measured=%s/1000|gap_measured=%s/1000|kind=MEASUREMENT_NOT_CERTIFICATE|json=0\n"
            % (je, jb, r["steps"], r["c24"], r["e0"], r["gap"]))


def svg(je, jb):
    r = compute(je, jb)
    ys = r["logd"]
    W, H, pad = 640, 240, 30
    n = max(1, len(ys) - 1)
    ymax = max(ys) if ys else 1
    pts = " ".join("%d,%d" % (pad + (k * (W - 2 * pad)) // n, H - pad - (y * (H - 2 * pad)) // max(1, ymax))
                   for k, y in enumerate(ys) if y > 0)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">'
            '<rect width="100%%" height="100%%" fill="#fff"/>'
            '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#999"/>'
            '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#999"/>'
            '<polyline fill="none" stroke="#2563eb" stroke-width="2" points="%s"/>'
            '<text x="%d" y="18" font-size="13" font-family="sans-serif">r = %d/%d: log2(energy drop) vs Euclidean step; straight line = single exponential (slope = gap)</text>'
            '</svg>' % (W, H, W, H, pad, H - pad, W - pad, H - pad, pad, pad, pad, H - pad, pts, pad, jb, je))


def page():
    cert = certified()
    rows = []
    for je, jb in RATIOS:
        r = compute(je, jb)
        c = cert.get(jb)
        inside = "-"
        if c and r["gap"] is not None:
            lo = int(c[2].split("/")[0])
            inside = "yes" if r["gap"] >= lo else "NO"
        rows.append("<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (jb, r["e0"], c[0] if c else "-", r["gap"], c[2] if c else "-", inside, r["steps"]))
    imgs = "".join('<h3>r = %d</h3><img src="/svg/%d/%d" alt="relaxation r=%d">' % (jb, je, jb, jb) for je, jb in RATIOS)
    return ("<!doctype html><meta charset=utf-8><title>HEB-C evolution test ground</title>"
            "<style>body{font-family:sans-serif;max-width:760px;margin:24px auto;padding:0 16px}"
            "table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:4px 8px;text-align:right}</style>"
            "<h1>HEB-C evolution test ground</h1>"
            "<p>Finite S3 2x2 torus, H = JE*E + JB*M (JE = 1). Euclidean evolution v &larr; (c &minus; H)v, "
            "integer-only. <b>Measured</b> values are relaxation measurements, not certificates; "
            "<b>certified</b> values are interval-Sturm bounds from the ledger. Energies in units of 1/1000 JE.</p>"
            "<table><tr><th>r</th><th>E0 measured</th><th>E0 certified &lt;</th><th>gap measured</th>"
            "<th>gap certified &gt;</th><th>measured above certified</th><th>steps</th></tr>%s</table>%s"
            % ("".join(rows), imgs))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parts = [p for p in self.path.split("/") if p]
        try:
            if not parts:
                body, ctype = page(), "text/html; charset=utf-8"
            elif parts[0] in ("evolve", "svg") and len(parts) == 3:
                je, jb = int(parts[1]), int(parts[2])
                if not (1 <= je <= 64 and 0 <= jb <= 1000):
                    raise ValueError
                body, ctype = (line(je, jb), "text/plain; charset=utf-8") if parts[0] == "evolve" else (svg(je, jb), "image/svg+xml")
            else:
                self.send_error(404)
                return
        except ValueError:
            self.send_error(400)
            return
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5099
    print("EVOLVE-SERVE|host=127.0.0.1|port=%d|json=0" % port, flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
