#!/usr/bin/env python3
"""Summarize RobotRumble official round logs in /logs/rounds.

Usage from /workspace:
    python3 tools/analyze_rounds.py

It reports winner/score metadata plus final health/unit ranges parsed from sim_*.txt.
"""
import glob
import json
import os
import re
from collections import Counter

ROOT = "/logs/rounds"
FINAL_RE = re.compile(r"Final state: Health (\d+) (\d+) Units (\d+) (\d+)")
# CLI prints final values as: Health <blue> <red> Units <blue> <red>.
WIN_RE = re.compile(r"Done! (Red|Blue) won")

for round_dir in sorted(glob.glob(os.path.join(ROOT, "*")), key=lambda p: int(os.path.basename(p)) if os.path.basename(p).isdigit() else 999999):
    if not os.path.isdir(round_dir):
        continue
    name = os.path.basename(round_dir)
    results_path = os.path.join(round_dir, "results.json")
    print(f"round {name}")
    if os.path.exists(results_path):
        with open(results_path) as f:
            data = json.load(f)
        print("  winner:", data.get("winner"))
        print("  scores:", data.get("scores"))
        for detail in data.get("details", []):
            print("  detail:", detail)
    finals = []
    winners = Counter()
    for fn in glob.glob(os.path.join(round_dir, "sim_*.txt")):
        text = open(fn, errors="replace").read()
        m = FINAL_RE.search(text)
        if m:
            finals.append(tuple(map(int, m.groups())))
        w = WIN_RE.search(text)
        if w:
            winners[w.group(1)] += 1
    print("  sims:", len(finals), "visual winners:", dict(winners))
    if finals:
        labels = ("blue_health", "red_health", "blue_units", "red_units")
        for i, label in enumerate(labels):
            vals = [x[i] for x in finals]
            print(f"  {label}: min={min(vals)} avg={sum(vals)/len(vals):.1f} max={max(vals)}")
        print("  common finals:", Counter(finals).most_common(5))
    print()
