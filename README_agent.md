# Agent notes

Status after official rounds 0 and 1:
- We beat `happysquid__test` **250/250 in both rounds**.
  - Round 0: opponent Blue, us Red; official score 250-0.
  - Round 1: us Blue, opponent Red; official score 250-0.
- Opponent remains very weak/passive. Logs show our side typically finishes with ~19-38 units while the opponent has 0-4 units.
- I made no risky strategic changes in round 2; preserving the proven winner is likely best unless a later log shows adaptation.

Current `robot.py` summary:
- Fast coordinated one-ply tactical planner adapted from built-in `black-magic.js`.
- `init_turn` builds tuple-coordinate maps of friendly/enemy units.
- Enemy model: adjacent enemies attack our lowest-health adjacent friend.
- For each friendly unit, tries pass/attack/legal moves and greedily keeps changes that improve a lexicographic score: unit advantage, surround, health, pressure, small center term.
- `robot` returns the precomputed per-unit action.
- Optimized vs original JS `black-magic`: cached direction deltas/legal coords, tuple math, avoids repeated `Coords` allocation.

Tools added:
- `tools/analyze_rounds.py` summarizes `/logs/rounds/*/results.json` plus parsed final health/unit stats from `sim_*.txt`.
  Run from `/workspace` with:
  `python3 tools/analyze_rounds.py`
  Note: the CLI final-state line prints values as `Health <blue> <red> Units <blue> <red>`.

Useful testing commands:
- Single local match: `./rumblebot run term --results-only --seed 1 robot.py builtin-bots/black-magic.js`
- Reverse sides: `./rumblebot run term --results-only --seed 1 builtin-bots/black-magic.js robot.py`
- Official logs: `/logs/rounds/<n>/results.json` and `/logs/rounds/<n>/sim_*.txt`

Potential future work:
- If still facing `happysquid__test`, do not overfit or risk regressions; current bot is crushing it on both colors.
- If a stronger mirror/black-magic-like opponent appears, test both colors over multiple seeds and tune score weights/order, especially center term and tie-breaking.
