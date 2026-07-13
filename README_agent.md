# Agent notes

Status after official round 0 (current match-up):
- We beat `anton__wallifier` **250/250**.
  - Round 0: opponent was Blue, we were Red; official score 250-0.
  - `/logs/rounds/0/results.json` confirms winner `gpt-5-5` and all 250 sims won by Red.
- Opponent appears extremely passive/wall-like. In sampled logs it mostly stays near spawn/edges; the game engine clears spawn every 10 turns, and our bot wins by leaving spawn, accumulating units, and cleaning up. Final round-0 averages: us ~135 health / 28 units, opponent ~3 health / <1 unit.
- I made no strategic code changes this round. Current `robot.py` is already crushing this opponent; avoid risky tuning unless future logs show losses or an adapted opponent.

Current `robot.py` summary:
- Fast coordinated one-ply tactical planner adapted from built-in `black-magic.js`.
- `init_turn` builds tuple-coordinate maps of friendly/enemy units.
- Enemy model: adjacent enemies attack our lowest-health adjacent friend.
- For each friendly unit, tries pass/attack/legal moves and greedily keeps changes that improve a lexicographic score: unit advantage, surround, health, pressure, small center term.
- `robot` returns the precomputed per-unit action.
- Optimized vs original JS `black-magic`: cached direction deltas/legal coords, tuple math, avoids repeated `Coords` allocation.
- The small center term is important against passive spawn/edge campers because it encourages units to leave spawn rather than get cleared.

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
- If still facing `anton__wallifier`, preserve the proven winner.
- If a stronger mirror/black-magic-like opponent appears, test both colors over multiple seeds and tune score weights/order, especially center term and tie-breaking.
