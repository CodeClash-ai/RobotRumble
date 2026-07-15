#!/usr/bin/env python3
"""
Reusable parallelized A/B self-play harness for RobotRumble bots.

Usage:
    python3 tools/ab_test.py bot_a.py bot_b.py --seeds 1-60 [--swap] [--workers 16]

Runs `./rumblebot run term --results-only --seed N bot_a.py bot_b.py` for each
seed in parallel (bot_a=Blue, bot_b=Red), tallies wins/losses/ties for bot_a,
and (if --swap) also runs the reverse side assignment to check for side bias.

This is the pattern introduced in "Round 10" of README_agent.md (see that
file for full history) -- reusing it here as a persistent, documented script
instead of recreating it in /tmp each round (which doesn't survive between
sessions). Each individual `rumblebot run term` invocation is single-threaded
and CPU-light, so running many in parallel via a thread pool is ~10x faster
wall-clock than a sequential loop on a multi-core machine.

Example (from /workspace):
    python3 tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap
"""
import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

UNITS_RE = re.compile(r"Units (\d+) (\d+)")


def run_one(bot_a, bot_b, seed):
    out = subprocess.run(
        ["./rumblebot", "run", "term", "--results-only", "--seed", str(seed), bot_a, bot_b],
        capture_output=True, text=True, cwd="/workspace",
    ).stdout
    m = UNITS_RE.search(out)
    if not m:
        return "error"
    blue, red = int(m.group(1)), int(m.group(2))
    if blue > red:
        return "a"  # bot_a (Blue) won
    elif red > blue:
        return "b"  # bot_b (Red) won
    else:
        return "tie"


def parse_seeds(spec):
    seeds = []
    for part in spec.split(","):
        if "-" in part:
            lo, hi = part.split("-")
            seeds.extend(range(int(lo), int(hi) + 1))
        else:
            seeds.append(int(part))
    return seeds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bot_a")
    ap.add_argument("bot_b")
    ap.add_argument("--seeds", default="1-30")
    ap.add_argument("--swap", action="store_true", help="also run with sides swapped")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    seeds = parse_seeds(args.seeds)

    def tally(bot_a, bot_b, label):
        a_wins = b_wins = ties = errors = 0
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            results = list(ex.map(lambda s: run_one(bot_a, bot_b, s), seeds))
        for r in results:
            if r == "a":
                a_wins += 1
            elif r == "b":
                b_wins += 1
            elif r == "tie":
                ties += 1
            else:
                errors += 1
        print(f"[{label}] {bot_a} (Blue) vs {bot_b} (Red) over {len(seeds)} seeds: "
              f"A={a_wins} B={b_wins} tie={ties} errors={errors}")
        return a_wins, b_wins, ties

    tally(args.bot_a, args.bot_b, "A-as-Blue")
    if args.swap:
        tally(args.bot_b, args.bot_a, "A-as-Red (swapped)")


if __name__ == "__main__":
    main()
