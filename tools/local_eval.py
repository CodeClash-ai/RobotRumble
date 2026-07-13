#!/usr/bin/env python3
"""Run quick local RobotRumble evaluations over multiple seeds.

Examples from /workspace:
  python3 tools/local_eval.py --seeds 1-10 --opponent builtin-bots/black-magic.js
  python3 tools/local_eval.py --seeds 1,2,3 --opponent builtin-bots/nothing-bot.js --both-sides

This is intended as a lightweight regression helper for future teammates. It
parses the rumblebot `--results-only` output and reports wins/final units/health.
"""
import argparse
import os
import re
import subprocess
import sys

WIN_RE = re.compile(r"Done! (?:(Red|Blue) won|it was a tie)")
FINAL_RE = re.compile(r"Final state: Health (\d+) (\d+) Units (\d+) (\d+)")


def parse_seeds(spec):
    out = []
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = map(int, part.split('-', 1))
            out.extend(range(a, b + 1))
        else:
            out.append(int(part))
    return out


def run_one(blue, red, seed):
    cmd = ["./rumblebot", "run", "term", "--results-only", "--seed", str(seed), blue, red]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    text = p.stdout
    wm = WIN_RE.search(text)
    fm = FINAL_RE.search(text)
    if p.returncode != 0 or not wm or not fm:
        print(text, file=sys.stderr)
        raise RuntimeError(f"could not parse result for seed {seed}: {' '.join(cmd)}")
    return (wm.group(1) or "Tie"), tuple(map(int, fm.groups()))  # blue_hp, red_hp, blue_units, red_units


def summarize(label, rows, our_color):
    wins = sum(1 for _, winner, _ in rows if winner == our_color)
    print(f"{label}: {wins}/{len(rows)} wins as {our_color}")
    if not rows:
        return
    # convert final tuple into our/opponent health and units
    our_h = []
    opp_h = []
    our_u = []
    opp_u = []
    for _, _, (bh, rh, bu, ru) in rows:
        if our_color == "Blue":
            our_h.append(bh); opp_h.append(rh); our_u.append(bu); opp_u.append(ru)
        else:
            our_h.append(rh); opp_h.append(bh); our_u.append(ru); opp_u.append(bu)
    def avg(xs): return sum(xs) / len(xs)
    print(f"  avg health us/opp: {avg(our_h):.1f}/{avg(opp_h):.1f}; avg units us/opp: {avg(our_u):.1f}/{avg(opp_u):.1f}")
    losses = [(seed, winner, final) for seed, winner, final in rows if winner != our_color]
    if losses:
        print("  losses:", losses[:10])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bot", default="robot.py")
    ap.add_argument("--opponent", default="builtin-bots/black-magic.js")
    ap.add_argument("--seeds", default="1-5", help="comma list and/or inclusive ranges, e.g. 1-10,42")
    ap.add_argument("--both-sides", action="store_true")
    args = ap.parse_args()
    if not os.path.exists("./rumblebot"):
        raise SystemExit("run from /workspace so ./rumblebot exists")
    seeds = parse_seeds(args.seeds)

    blue_rows = []
    for s in seeds:
        blue_rows.append((s, *run_one(args.bot, args.opponent, s)))
    summarize(f"{args.bot} vs {args.opponent}", blue_rows, "Blue")

    if args.both_sides:
        red_rows = []
        for s in seeds:
            red_rows.append((s, *run_one(args.opponent, args.bot, s)))
        summarize(f"{args.opponent} vs {args.bot}", red_rows, "Red")


if __name__ == "__main__":
    main()
