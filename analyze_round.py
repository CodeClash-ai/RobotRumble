#!/usr/bin/env python3
"""Analyze a completed round's sim logs. Usage: python3 analyze_round.py <round_num>
Reads /logs/rounds/<n>/sim_*.txt and summarizes wins/losses/ties by final Units.
Blue (A) = us (opus-4-8). Red (B) = opponent."""
import sys, glob, re, os

def main():
    rnd = sys.argv[1] if len(sys.argv) > 1 else "1"
    d = f"/logs/rounds/{rnd}"
    files = glob.glob(os.path.join(d, "sim_*.txt"))
    win = loss = tie = 0
    margins = []
    for f in sorted(files):
        with open(f) as fh:
            txt = fh.read()
        m = re.findall(r"Final state: Health (\d+) (\d+)\s+Units (\d+) (\d+)", txt)
        if not m:
            continue
        ha, hb, ua, ub = map(int, m[-1])
        if ua > ub or (ua == ub and ha > hb):
            win += 1
        elif ub > ua or (ua == ub and hb > ha):
            loss += 1
        else:
            tie += 1
        margins.append(ua - ub)
    n = win + loss + tie
    print(f"Round {rnd}: {n} sims. WIN={win} LOSS={loss} TIE={tie}")
    if margins:
        print(f"Avg unit margin (us-them): {sum(margins)/len(margins):.2f}")

if __name__ == "__main__":
    main()
