# Agent notes for RobotRumble

Round 0 logs in `/logs/rounds/0` showed a 4-4 tie with no damage: the previous
quadrant bot often stayed on spawn/perimeter and never engaged.  Important rule
from `logic/logic/src/lib.rs`: on turns 11,21,... the engine calls
`clear_spawn()` before spawning reinforcements, deleting any unit still on a
spawn tile.  Normal mode winner is number of units alive after 100 turns.

Current `robot.py` is a survival/anti-passive strategy:
- attack adjacent low-health enemies;
- immediately move every spawned unit toward center off spawn;
- keep units in an interior annulus (Manhattan radius about 7), avoiding spawn;
- only chase enemies within distance 3 so it doesn't run back onto spawn.

Local tests versus a saved copy of the old bot (`old_robot.py`, not needed for
submission) won decisively as both Blue and Red across seeds 1-10 plus `test` and
`abc`, mostly by accumulating reinforcements while the old bot lost spawn units.
Use `./rumblebot run term --results-only --seed SEED robot.py other.py` for quick
tests.  Self-play is asymmetric/tactical and can produce either side winning,
but runtime is well below limits (~0.5-1s/match).
