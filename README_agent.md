# Notes for Next Teammate

## Round 1 changes (opus-4-7)

The original `robot.py` was a quadrant-based bot which barely worked (only engages
enemies in same quadrant, but enemies spawn in opposite quadrants - so it never
moved!). Round 0 was 100% ties for this reason.

## New bot strategy (Round 1 - active)
Replaced with a chase-and-attack bot in `/workspace/robot.py` featuring:
- Move toward closest enemy (prefer weaker for kills)
- Attack adjacent enemies (prefer lowest HP for kills)
- Try rotations if direct path blocked (rotate_cw, rotate_ccw)
- Collision avoidance between allies (planned_moves dict)
- Retreat if health=1 and outnumbered nearby
- Get off spawn tiles before turn %10==9 (or units get removed)

## Round 1 result: WIN 250-0 vs anton__anton3000 !!
250/250 simulations won. Total dominance.

## Round 2 changes (opus-4-7)
- Added try/except safety wrapper around robot() so crashes never happen.
  Bot falls back to attack-adjacent-enemy or do-nothing on error.
- No strategic changes since we're winning 250-0.

## Test results (local, all still winning)
- vs chaser: WIN
- vs needle-bot: WIN
- vs simple-bot: WIN
- vs random-bot: WIN
- vs flail: WIN
- vs heuristic-bot: WIN
- vs black-magic: LOSS (Grant Slatton's minimax - very strong, hard to beat)

## To run local tests
```
./rumblebot run term --no-logs ./robot.py ./builtin-bots/<botname>.js
```
First arg=Blue, second=Red.

## Files
- `/workspace/robot.py` - Active bot (with safety wrapper appended)
- `/workspace/robot.py.bak` - Round-1 bot backup (pre safety wrapper)

## Possible improvements for next round
1. Beat black-magic - port its scoring approach to Python
   - Its scoring: unit count, surround, sqrt(health), 1/distance^2
   - Uses lexicographic score comparison to pick best action combo
2. Better spawn avoidance - use SPAWN_COORDS constant directly
3. Coordinate multi-unit attacks (focus fire enemies we can kill this turn)
4. Analyze /logs/rounds/*/ to see specific opponent behavior:
   - grep results.json for winner
   - tail sim_N.txt for final scores
5. Consider caching more state across turns (e.g., predicted enemy positions)

## Key game mechanics reminders (from docs/source/index.rst)
- Each robot has 5 HP; attacks do 1 damage
- If multiple robots move into same cell, N-wise clockwise priority
- Friendly fire IS enabled - avoid attacking your own team!
- Every 10 turns, spawn happens. Units still on spawn tiles get REMOVED.
- 100 turns max per game
- Map is 19x19 octagon

## Round 3 changes (opus-4-7)
- Added focus-fire logic: track `damage_committed` per enemy per turn.
- Adjacent-attack selection now prefers enemies we can KILL this turn
  (effective_hp <= 1 after committed damage), then lowest effective HP.
- This helps multiple allies gang up efficiently to remove enemies fast.
- Still lose to black-magic (~1200ms per game) - very tough opponent.

## Round 3 test results
- vs chaser: WIN (Health 34-13, Units 14-4)
- vs heuristic-bot: WIN (Health 35-15, Units 20-8)  
- vs simple-bot: WIN (Health 125-9, Units 25-2)
- vs needle-bot: WIN (Health 40-4, Units 11-2)
- vs flail: WIN (Health 49-23, Units 19-7)
- vs random-bot: WIN (Health 125-5, Units 25-1)
- vs black-magic: LOSS (Health 7-34) - marginally better than before
