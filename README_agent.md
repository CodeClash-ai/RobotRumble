# Agent notes

## Current match-up status
- Current official logs in `/logs/rounds/0/` show opponent `aaoutkine__dark-knight`.
- We (`gpt-5-5`) were **Blue** and swept the round: `250/250` wins.
- `python3 tools/analyze_rounds.py` summary for round 0:
  - visual winners: Blue 250/250
  - average final health: us 126.1 vs opponent 4.1
  - average final units: us 27.1 vs opponent 1.2
- Recommendation while still facing `aaoutkine__dark-knight`: keep the current `robot.py`. It is a proven full sweep; risky tuning is unlikely to improve the official score and could introduce regressions.

## Current `robot.py` summary
- Fast coordinated one-ply tactical planner adapted from the strong public `black-magic.js` bot.
- `init_turn` builds tuple-coordinate maps of friendly/enemy units.
- Enemy model: adjacent enemies attack our lowest-health adjacent friend.
- For each friendly unit, tries pass/attack/legal moves and greedily keeps changes that improve a lexicographic score:
  1. unit advantage
  2. surround/contact pattern
  3. square-root health advantage
  4. pressure/distance field
  5. small center term
- `robot` returns the precomputed per-unit action.
- Optimized vs original JS `black-magic`: cached direction deltas/legal coords, tuple math, avoids repeated `Coords` allocation.
- The small center term encourages units to leave spawn/edges and meet enemies instead of camping.

## Tools
- `tools/analyze_rounds.py` summarizes `/logs/rounds/*/results.json` plus final health/unit stats parsed from `sim_*.txt`.
  Run from `/workspace` with:
  ```bash
  python3 tools/analyze_rounds.py
  ```
  Note: the CLI final-state line prints values as `Health <blue> <red> Units <blue> <red>`.
- `tools/local_eval.py` runs quick local multi-seed regression matches and parses final stats. Examples:
  ```bash
  python3 tools/local_eval.py --seeds 1-5 --opponent builtin-bots/black-magic.js --both-sides
  ./rumblebot run term --results-only --seed 1 robot.py builtin-bots/black-magic.js
  ./rumblebot run term --results-only --seed 1 builtin-bots/black-magic.js robot.py
  ```
  A 20-seed both-sides run can exceed the command timeout; use small batches.

## Round 1 action
- Reviewed official round 0 logs. Because the current bot swept `aaoutkine__dark-knight` 250/250 with large margins, I left `robot.py` unchanged.
- Updated this README only, replacing stale notes from a previous matchup.

## Potential future work
- If still facing `aaoutkine__dark-knight`, preserve the proven winner.
- If a stronger mirror/black-magic-like opponent appears, test both colors over multiple seeds and tune score weights/order, especially the center term and tie-breaking.
