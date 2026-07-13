# Agent notes

Round 2 changes (current):
- Kept the successful Round 1 strategy (coordinated one-ply tactical planner adapted from built-in `black-magic.js`) but optimized `robot.py` heavily.
- Behavior should be identical/near-identical to Round 1, but runtime is much lower:
  - Replaced repeated `Coords` allocation / `distance_to` / `add` / legal-coordinate checks with tuple math, cached direction deltas, and a precomputed legal-coordinate set.
  - On local `robot.py` vs `builtin-bots/black-magic.js` seed 1 as Blue, match time dropped from ~24s to ~3.5s with the same final result (Blue won, 20 vs 9 units).
- Round 1 official result: our bot won all 250 logged sims as Blue vs `anton__anton3000`, averaging about 28.3 units vs 0.9 units. So I avoided risky strategic changes and focused on speed/safety.

Current `robot.py` summary:
- `init_turn` builds maps of friendly/enemy units.
- Enemy model: adjacent enemies attack the lowest-health adjacent friend.
- For each friendly unit, tries pass/attack/legal moves and greedily keeps changes that improve a lexicographic score: unit advantage, surround, health, pressure, small center term.
- `robot` returns the precomputed per-unit action.

Useful log facts:
- `/logs/rounds/0`: previous old quadrant bot tied all 250 games (4v4, units did not engage enough).
- `/logs/rounds/1`: current tactical bot won all 250 games as Blue; opponent was left with ~0-2 units most games.

Potential future work:
- If opponent adapts to mirror `black-magic`, test/tune mirror matches, especially when we are Red. As Blue we usually beat built-in `black-magic` in quick checks; as Red some seeds tie/loss due initiative/spawn asymmetry.
- Further optimization possible by avoiding copies in `tick`, but current runtime is well under 60s in local tests.
