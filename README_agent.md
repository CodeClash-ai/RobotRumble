# Agent notes

Current status after official round 0:
- `robot.py` is the fast coordinated one-ply tactical planner adapted from built-in `black-magic.js`.
- Official `/logs/rounds/0` result: **gpt-5-5 won 250/250 as Red** vs `happysquid__test` (Blue). The opponent appears very weak/passive; many sims ended with us having 25-32 units and opponent 0-1.
- I made no strategic code changes this round because the current bot is decisively winning and already runs comfortably under the 60s limit.

Current `robot.py` summary:
- `init_turn` builds tuple-coordinate maps of friendly/enemy units.
- Enemy model: adjacent enemies attack our lowest-health adjacent friend.
- For each friendly unit, tries pass/attack/legal moves and greedily keeps changes that improve a lexicographic score: unit advantage, surround, health, pressure, small center term.
- `robot` returns the precomputed per-unit action.
- Optimized vs the original JS `black-magic`: cached direction deltas/legal coords, tuple math, avoids repeated `Coords` allocation.

Useful testing commands:
- Single local match: `./rumblebot run term --results-only --seed 1 robot.py builtin-bots/black-magic.js`
- Reverse sides: `./rumblebot run term --results-only --seed 1 builtin-bots/black-magic.js robot.py`
- Official logs: `/logs/rounds/0/results.json` and `/logs/rounds/0/sim_*.txt`

Potential future work:
- Keep this strategy unless the opponent adapts substantially; it crushed the current opponent.
- If facing a stronger mirror/black-magic-like bot, test both colors over many seeds and tune the scoring weights/order, especially the center term and tie-breaking.
