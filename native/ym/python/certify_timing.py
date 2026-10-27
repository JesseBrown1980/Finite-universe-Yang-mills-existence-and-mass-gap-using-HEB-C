#!/usr/bin/env python3
"""Runner seconds for the certify budget (CERTIFY-SPEC.md), from the GitHub job timings.
Integer seconds only, json=0.

usage: certify_timing.py OWNER/REPO CERTIFY_RUN_ID STAGE_B_RUN_ID [STAGE_B_RUN_ID ...]
prints: TIMING|stage_b_seconds=..|certify_seconds=..|json=0
(certify_seconds counts the certify run's completed jobs, i.e. every watcher.)
"""
import json
import os
import sys
import urllib.request


def iso_seconds(s):
    # 2026-10-27T10:00:00Z -> integer seconds since an arbitrary epoch (differences only)
    d, t = s.rstrip("Z").split("T")
    y, mo, da = (int(x) for x in d.split("-"))
    h, mi, se = (int(x) for x in t.split(":"))
    a = (14 - mo) // 12
    yy, mm = y + 4800 - a, mo + 12 * a - 3
    jdn = da + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045
    return jdn * 86400 + h * 3600 + mi * 60 + se


def run_seconds(repo, run):
    tok = os.environ["GH_TOKEN"]
    total, page = 0, 1
    while True:
        req = urllib.request.Request("https://api.github.com/repos/%s/actions/runs/%s/jobs?per_page=100&page=%d"
                                     % (repo, run, page), headers={"Authorization": "Bearer " + tok})
        jobs = json.load(urllib.request.urlopen(req))["jobs"]
        for j in jobs:
            if j.get("started_at") and j.get("completed_at"):
                total += max(0, iso_seconds(j["completed_at"]) - iso_seconds(j["started_at"]))
        if len(jobs) < 100:
            return total
        page += 1


def main():
    repo, cert, runs = sys.argv[1], sys.argv[2], sys.argv[3:]
    b = sum(run_seconds(repo, r) for r in runs)
    print("TIMING|stage_b_seconds=%d|certify_seconds=%d|json=0" % (b, run_seconds(repo, cert)))


if __name__ == "__main__":
    main()
