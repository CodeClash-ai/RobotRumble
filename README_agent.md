# Agent notes

Status after official rounds 0 and 1 for this match-up:
- We beat `ldang__nemo` **250/250 in round 0** and **250/250 in round 1**.
  - In both rounds, `gpt-5-5` was Blue and `ldang__nemo` was Red.
  - `/logs/rounds/0/results.json` and `/logs/rounds/1/results.json` show full sweeps: `gpt-5-5` score 250, opponent score 0.
  - `python3 tools/analyze_rounds.py` summary:
    - round 0: all 250 visual logs were Blue wins; final averages us ~114.2 health / 26.8 units, opponent ~4.6 health / 1.2 units.
    - round 1: all 250 visual logs were Blue wins; final averages us ~112.0 health / 26.3 units, opponent ~4.3 health / 1.2 units.
- Recommendation: keep the current `robot.py` while still facing `ldang__nemo`. It is a proven sweep over 500 official sims, so risky tuning is unlikely to improve the official score and could only introduce regressions.

Current `robot.py` summary:
- Fast coordinated one-ply tactical planner adapted from built-in `black-magic.js`.
- `init_turn` builds tuple-coordinate maps of friendly/enemy units.
- Enemy model: adjacent enemies attack our lowest-health adjacent friend.
- For each friendly unit, tries pass/attack/legal moves and greedily keeps changes that improve a lexicographic score: unit advantage, surround, health, pressure, small center term.
- `robot` returns the precomputed per-unit action.
- Optimized vs original JS `black-magic`: cached direction deltas/legal coords, tuple math, avoids repeated `Coords` allocation.
- The small center term encourages units to leave spawn / edges and meet enemies instead of camping.

Tools:
- `tools/analyze_rounds.py` summarizes `/logs/rounds/*/results.json` plus parsed final health/unit stats from `sim_*.txt`.
  Run from `/workspace` with:
  `python3 tools/analyze_rounds.py`
  Note: the CLI final-state line prints values as `Health <blue> <red> Units <blue> <red>`.

Useful testing commands:
- Single local match: `./rumblebot run term --results-only --seed 1 robot.py builtin-bots/black-magic.js`
- Reverse sides: `./rumblebot run term --results-only --seed 1 builtin-bots/black-magic.js robot.py`
- Passive-opponent sanity checks:
  - `./rumblebot run term --results-only --seed 1 robot.py builtin-bots/nothing-bot.js`
  - `./rumblebot run term --results-only --seed 1 builtin-bots/nothing-bot.js robot.py`

Potential future work:
- If still facing `ldang__nemo`, preserve the proven winner.
- If a stronger mirror/black-magic-like opponent appears, test both colors over multiple seeds and tune score weights/order, especially center term and tie-breaking.
