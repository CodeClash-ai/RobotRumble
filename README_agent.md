# Agent notes

Status after official rounds 0 and 1 for this match-up:
- We beat `ldang__nessy` **250/250 in round 0** and **250/250 in round 1**.
  - In both recorded rounds `gpt-5-5` was Blue and `ldang__nessy` was Red.
  - `/logs/rounds/0/results.json` and `/logs/rounds/1/results.json` both show full sweeps.
  - `python3 tools/analyze_rounds.py` summary:
    - round 0: all 250 visual logs Blue wins; final averages us ~101 health / 25.1 units, opponent ~6.0 health / 1.6 units.
    - round 1: all 250 visual logs Blue wins; final averages us ~100.2 health / 24.9 units, opponent ~5.9 health / 1.6 units.
- Recommendation: keep the current `robot.py` while still facing `ldang__nessy`. It is a proven sweep over 500/500 official sims, so risky tuning is unlikely to improve the official score and could only introduce regressions.

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
- If still facing `ldang__nessy`, preserve the proven winner.
- If a stronger mirror/black-magic-like opponent appears, test both colors over multiple seeds and tune score weights/order, especially center term and tie-breaking.
