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

Round 2 update:
- Round 1 logs (`/logs/rounds/1`) show our survival/annulus bot beat the still-passive opponent 250-0 as Red, commonly ending with ~30-38 units vs 0-4. The key exploit remains: units left on spawn are deleted before reinforcements.
- I kept the same macro but changed `robot.py` combat micro. Adjacent robots now attack only when a low-health kill/good local numbers are available; otherwise they try to move out of adjacency. This uses the engine fact that movement resolves before attacks, so dodging can avoid a planned adjacent attack.
- Local smoke tests: still beats a passive `return None` bot decisively as Blue seeds 1-5 (31-37 units vs 3-4). Versus simple chasers it is much more competitive than round-1 annulus, but combat is slower (~2-4s/match, still well below the 60s limit).
- Useful ad-hoc opponents used for testing were `/tmp/chase.py` and `/tmp/inward_chase.py` (not saved in repo); recreate if needed from the terminal history or write simple nearest-enemy bots.

Round 3 update (current):
- Added `intercept_dir()` micro in `robot.py`: after leaving spawn/perimeter, a unit attacks an adjacent empty square if an enemy at distance 2 could step into it. Since the engine resolves movement before attacks, this pre-fires simple chase bots and prevents our units from walking into brawls.
- Smoke tests: still crushes passive bots as Blue/Red seeds 1-3 (roughly 31-37 units vs 4). Against a naive nearest-enemy chaser, new bot won all tested seeds 1-3 as both sides, often by the same spawn-wipe margin; previous bot sometimes lost/tied. New bot also beat the previous `/tmp/current.py` copy in tested Blue seeds 1-4. Self-play is around 4-5s/match, well under 60s.
- The key macro remains unchanged: immediately leave spawn and keep an annulus around center; do not over-chase perimeter bait.

Round 2 verification note:
- I reviewed `/logs/rounds/0` and `/logs/rounds/1`; both were 250/250 wins for us by the same spawn-wipe exploit.  The opponent still appears passive (ends with only ~1-4 units and no meaningful damage).
- Added `analyze_logs.py` at repo root. Run `python3 analyze_logs.py` to summarize all available `/logs/rounds/*` text logs, winner counts, final unit/health averages and ranges.
- I intentionally left `robot.py` unchanged this round because the current survival/annulus + intercept micro already wins decisively against the logged opponent and smoke tests still beat a passive bot and a naive chaser as both colors. Avoid risking a regression unless future logs show the opponent adapted.

Round 1 (current handoff) note:
- Only `/logs/rounds/0` was available this time. It shows us winning 250-0 as Red against `anton__wallifier`; all 250 sims ended Red win. `python3 analyze_logs.py` summary: opponent averaged ~3.5 units / 16 health, us ~35.7 units / 176.8 health.
- I did not change `robot.py`. The logged opponent is still beaten by the existing spawn-wipe exploit, and local smoke tests versus a passive bot and a naive nearest-enemy chaser still win as both colors.
- Quick commands used: create `/tmp/passive.py` returning None and `/tmp/chase.py` nearest-enemy chaser, then run `./rumblebot run term --results-only --seed 1 robot.py /tmp/passive.py` (Blue won 37-4 units), swapped colors (Red won 37-4), and similarly versus chaser (wins 35-3 and 33-0 units).
