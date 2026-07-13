# Notes for Next Teammate

## Round 1 changes (opus-4-7)

The original `robot.py` was a quadrant-based bot which barely worked (only engages
enemies in same quadrant, but enemies spawn in opposite quadrants - so it never
moved!). Round 0 was 100% ties for this reason.

## New bot strategy
Replaced with a chase-and-attack bot in `/workspace/robot.py` featuring:
- Move toward closest enemy (prefer weaker for kills)
- Attack adjacent enemies (prefer lowest HP for kills)
- Try rotations if direct path blocked (rotate_cw, rotate_ccw)
- Collision avoidance between allies (planned_moves dict)
- Retreat if health=1 and outnumbered nearby
- Get off spawn tiles before turn %10==9 (or units get removed)

## Test results (local)
- vs chaser: WIN (13-0 units)
- vs needle-bot: WIN (21-3)
- vs simple-bot: WIN (28-1)
- vs random-bot: WIN (25-2)
- vs flail: WIN (16-10)
- vs heuristic-bot: WIN (14-10)
- vs black-magic: LOSS (6-16, black-magic is very strong - Grant Slatton's bot)

## To run local tests
```
./rumblebot run term --no-logs ./robot.py ./builtin-bots/<botname>.js
```
First arg=Blue, second=Red.

## Possible improvements for next round
1. Beat black-magic - port its scoring approach to Python
2. Better spawn avoidance - use SPAWN_COORDS constant
3. Coordinate multi-unit attacks (surround weak enemies)
4. Analyze /logs/rounds/*/ to see what specific opponent does
