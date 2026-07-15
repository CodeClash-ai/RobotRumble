"""Summarize RobotRumble text logs from /logs/rounds.

Usage:
    python3 analyze_logs.py              # all rounds under /logs/rounds
    python3 analyze_logs.py /logs/rounds/1

Prints winner counts and final health/unit ranges.  Kept for future agents so
we can quickly verify whether the opponent has changed strategy between rounds.
"""
import glob
import os
import re
import statistics
import sys
from collections import Counter


def summarize(path: str) -> None:
    files = sorted(glob.glob(os.path.join(path, "sim_*.txt")))
    winners = Counter()
    vals = []
    for fn in files:
        txt = open(fn, errors="ignore").read()
        m = re.search(r"Done! (\w+) won", txt)
        winners[m.group(1) if m else "Tie/unknown"] += 1
        m = re.search(r"Final state: Health (\d+) (\d+) Units (\d+) (\d+)", txt)
        if m:
            vals.append(tuple(map(int, m.groups())))
    print(f"{path}: {len(files)} logs")
    print("  winners:", dict(winners))
    if vals:
        bu = [v[2] for v in vals]
        ru = [v[3] for v in vals]
        bh = [v[0] for v in vals]
        rh = [v[1] for v in vals]
        print(f"  Blue units avg/min/max: {statistics.mean(bu):.2f}/{min(bu)}/{max(bu)}")
        print(f"  Red  units avg/min/max: {statistics.mean(ru):.2f}/{min(ru)}/{max(ru)}")
        print(f"  Blue health avg/min/max: {statistics.mean(bh):.2f}/{min(bh)}/{max(bh)}")
        print(f"  Red  health avg/min/max: {statistics.mean(rh):.2f}/{min(rh)}/{max(rh)}")


def main() -> None:
    args = sys.argv[1:]
    paths = args or sorted(glob.glob("/logs/rounds/[0-9]*"))
    for p in paths:
        summarize(p)


if __name__ == "__main__":
    main()
