# Agent notes

Status for this match-up (current logs):
- Official `/logs/rounds/0/results.json` and `/logs/rounds/1/results.json` both show `gpt-5-5` beat `navster8__bash-brothers` **250/250**.
  - In both rounds, `navster8__bash-brothers` was Blue and `gpt-5-5` was Red.
  - `python3 tools/analyze_rounds.py` summary: all 500 visual logs across rounds 0-1 were Red wins. Round 1 final averages: us ~113.8 health / 26.6 units, opponent ~4.6 health / 1.2 units.
- Recommendation while still facing `navster8__bash-brothers`: keep the current `robot.py`. It is a proven full sweep, so risky tuning is unlikely to improve the official score and could introduce regressions.

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
- `tools/local_eval.py` (added round 2) runs quick local multi-seed regression matches and parses final stats. Example:
  `python3 tools/local_eval.py --seeds 1-5 --opponent builtin-bots/black-magic.js --both-sides`

Useful testing commands:
- Single local match: `./rumblebot run term --results-only --seed 1 robot.py builtin-bots/black-magic.js`
- Reverse sides: `./rumblebot run term --results-only --seed 1 builtin-bots/black-magic.js robot.py`
- Passive-opponent sanity checks:
  - `./rumblebot run term --results-only --seed 1 robot.py builtin-bots/nothing-bot.js`
  - `./rumblebot run term --results-only --seed 1 builtin-bots/nothing-bot.js robot.py`

Round 2 note:
- Reviewed round 1 logs and kept `robot.py` unchanged because it swept again and there is no evidence the opponent changed. Added only `tools/local_eval.py` and this README update.

Potential future work:
- If still facing `navster8__bash-brothers`, preserve the proven winner.
- If a stronger mirror/black-magic-like opponent appears, test both colors over multiple seeds and tune score weights/order, especially center term and tie-breaking.
