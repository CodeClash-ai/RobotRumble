#!/usr/bin/env python3
"""Summarize RobotRumble text logs.
Usage: python3 tools_analyze_logs.py /logs/rounds/1
Prints final win counts and average final health/units parsed from sim_*.txt.
"""
import re, sys
from pathlib import Path
root = Path(sys.argv[1] if len(sys.argv) > 1 else '/logs/rounds/1')
final_re = re.compile(r'Final state: Health (\d+) (\d+) Units (\d+) (\d+)')
win_re = re.compile(r'Done! (Blue|Red) won')
stats = []
for p in sorted(root.glob('sim_*.txt')):
    txt = p.read_text(errors='ignore')
    fm = final_re.search(txt)
    wm = win_re.search(txt)
    if fm:
        stats.append((p.name, wm.group(1) if wm else 'Tie', *map(int, fm.groups())))
print('files', len(stats))
from collections import Counter
print('wins', Counter(s[1] for s in stats))
if stats:
    n=len(stats)
    print('avg health blue/red', sum(s[2] for s in stats)/n, sum(s[3] for s in stats)/n)
    print('avg units  blue/red', sum(s[4] for s in stats)/n, sum(s[5] for s in stats)/n)
    print('worst blue unit margins:')
    for s in sorted(stats, key=lambda x: x[4]-x[5])[:10]:
        print(s)
