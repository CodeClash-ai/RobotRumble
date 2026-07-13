# Agent notes

Round 1 changes:
- Replaced the original quadrant-target bot in `robot.py`; it could leave robots idle when no target existed in a quadrant, causing round-0 4v4 ties.
- Current `robot.py` is a coordinated one-ply tactical planner adapted from the strong built-in `black-magic.js` idea:
  - `init_turn` builds maps of all friendly/enemy units.
  - Assumes enemies attack adjacent lowest-health friends.
  - Greedily tries each friendly action (pass/attack/move) and keeps actions that improve a lexicographic score: unit advantage, surround, health, pressure, small center term.
  - `robot` simply returns the precomputed per-unit action.

Quick tests run with `./rumblebot run term --results-only --seed N ...`:
- Beats built-in `chaser.js` from both colors by large margins (seed 2: 21 units vs 4 / 21 vs 2).
- Beats the previous `robot.py` copy by large margins (seed 3 as blue: 24 units vs 3 before timeout on reverse test).
- Beats `nothing-bot.js` (seed 1: 26 units vs 2), so it no longer camps spawn.
- Versus `black-magic.js`: blue won seed 2 (20 units vs 7); reverse seed 2 tied (10 vs 10). Runtime around 15-23s per full match in local CLI, under the 60s forfeit limit but notably slower than simple bots.

Potential future work:
- Optimize `score`/`tick` if runtime becomes an issue (many tuple->Coords conversions). A faster Manhattan/squared distance approximation may help.
- Tune score weights or add conflict-aware movement to improve black-magic mirror matches.
