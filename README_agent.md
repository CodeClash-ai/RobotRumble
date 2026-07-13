# Agent notes

Status after official round 0 for this match-up:
- We beat `ldang__nessy` **250/250** in `/logs/rounds/0/results.json`.
  - Detail: `gpt-5-5` was Blue, `ldang__nessy` was Red.
  - Final-state averages from `python3 tools/analyze_rounds.py`: us ~101 health / 25 units, opponent ~6 health / 1.6 units.
  - All 250 visual logs show Blue winning.
- Recommendation: keep the current `robot.py` unless future logs show losses. It is already a proven sweep against this opponent, so risky tuning is unlikely to improve the official score.

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
