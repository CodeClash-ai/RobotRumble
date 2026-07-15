#!/usr/bin/env python3
"""
Analyze the per-turn unit-count trend across a round's logged sim files, to
detect "late-game snowball" patterns (see README_agent.md's
`clay__diag-lattice` and `atl15__centerrr` sections for the discovery/
rationale of this analysis).

Usage:
    python3 tools/turn_trend.py /logs/rounds/N [--limit 40] [--step 5]

Buckets the `Units B R` line from each `After turn T:` block (plus the
initial `Game start:` block as turn 0) across all (or --limit) sim_*.txt
files in the given directory, and prints the average Blue/Red unit count
at each turn (every --step turns) so you can see whether/when one side's
average count diverges from the other -- e.g. "even through turn 40, then
opponent pulls ahead by turn 60+" indicates a late-game snowball rather
than an early-game deficit.

Note: `Blue`/`Red` here refer to the raw column order in the sim log's
`Units B R` line, NOT necessarily "us"/"opponent" -- check the round's
`results.json` `details` field to know which color we were before
interpreting which column is "us".
"""
import argparse
import glob
import re
from collections import defaultdict

TURN_RE = re.compile(r"After turn (\d+):")
UNITS_RE = re.compile(r"Units (\d+) (\d+)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logdir")
    ap.add_argument("--limit", type=int, default=None,
                     help="only use the first N sim files (sorted by index)")
    ap.add_argument("--step", type=int, default=5,
                     help="print every Nth turn")
    args = ap.parse_args()

    files = glob.glob(f"{args.logdir}/sim_*.txt")
    files.sort(key=lambda f: int(re.search(r"sim_(\d+)\.txt", f).group(1)))
    if args.limit:
        files = files[: args.limit]

    buckets = defaultdict(lambda: [0, 0, 0])  # turn -> [sum_blue, sum_red, count]
    for f in files:
        txt = open(f).read()
        parts = re.split(TURN_RE, txt)
        m = UNITS_RE.search(parts[0])
        if m:
            b, r = int(m.group(1)), int(m.group(2))
            buckets[0][0] += b
            buckets[0][1] += r
            buckets[0][2] += 1
        for i in range(1, len(parts), 2):
            turn = int(parts[i])
            block = parts[i + 1]
            m = UNITS_RE.search(block)
            if m:
                b, r = int(m.group(1)), int(m.group(2))
                buckets[turn][0] += b
                buckets[turn][1] += r
                buckets[turn][2] += 1

    print(f"{'turn':>5} {'avg_blue':>10} {'avg_red':>10}  (n={len(files)} games)")
    for t in sorted(buckets):
        if t % args.step != 0:
            continue
        b, r, c = buckets[t]
        print(f"{t:>5} {b / c:>10.2f} {r / c:>10.2f}")


if __name__ == "__main__":
    main()
