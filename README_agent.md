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

Round 2 current edit note:
- Tiny safety/micro tweak in `robot.py`: intercept pre-fire squares are now recorded in `reserved_attack_squares`, and later robots avoid moving into those squares during the same turn. This avoids our own units stepping into friendly pre-fired attacks after movement resolution. Intercept squares also avoid already reserved movement destinations.
- Smoke tests after the tweak still crush passive bots as both colors seeds 1-3 (~32-37 vs 4 units), and still beat a naive nearest-enemy chaser as both colors seeds 1-3. Versus the previous `/tmp/current.py` copy, tested early seeds were mixed but generally comparable/slightly favorable; self-play remains ~4-5s/match.

Round 1 current note (this run):
- Available logs only had `/logs/rounds/0/results.json`: our current bot as Blue beat `ldang__nessy` 250-0. `python3 analyze_logs.py` shows all 250 sims Blue wins, averaging ~36.1 units vs 3.6. Opponent still appears passive/spawn-stuck, so spawn-wipe macro remains decisive.
- I experimented with an endgame chase tweak (turn >=92 sweep of remaining spawn/perimeter enemies). It improved final kills versus a passive bot but regressed badly in self-play versus the current bot, so I reverted `robot.py` to the prior version before submitting.
- Smoke tests after revert were already run earlier this session: current bot crushes passive (`return None`) and naive nearest-enemy chaser as both colors. Keep prioritizing survival/spawn evacuation unless future logs show opponent adapted.

Round 2 current note (gpt-5-5):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1` with `python3 analyze_logs.py`: current bot won all 500 logged sims (Blue 250/250 in r0, Red 250/250 in r1), averaging ~36 units vs ~3.5 for opponent. Logs still show opponent leaving units on/near spawn and getting wiped; no adaptation seen.
- Left `robot.py` unchanged to avoid regression; the survival/annulus + intercept micro is already maxing logged win rate.
- Smoke tests in this session versus simple local opponents still win as both colors: passive/nearest-chase/center-kite styles all lost decisively. Example seed 1 vs naive chase: Blue 30-2 units, Red 35-2 units; vs center mover: Blue 34-26, Red 35-22; vs kite-ish: Blue 25-11, Red 30-12.

Round 1 current note (gpt-5-5):
- Reviewed `/logs/rounds/0`: our bot won all 250 sims as Red, averaging ~36.4 units vs ~3.7. Opponent still appears spawn/perimeter-stuck and is beaten decisively by the existing spawn-wipe survival macro.
- Made one conservative safety tweak in `robot.py`: robots on spawn now prioritize moving inward before adjacent combat. This prevents a spawn robot from standing and fighting on a tile that will later be cleared; if no safe inward move exists it falls back to the usual combat logic.
- Smoke tests after the tweak: still crushes passive as both colors (seed 1: 37-4 units either side), beats naive nearest-chaser as both colors (seed 1: Blue 28-0, Red 32-2). Versus the previous bot copy self-play is mixed and comparable, so the macro remains unchanged.

Round 2 handoff note (latest gpt-5-5 run):
- Re-ran `python3 analyze_logs.py`: `/logs/rounds/0` and `/logs/rounds/1` are both 250/250 wins for us as Red against `ldang__nemo`, averaging ~36.3 surviving units for us vs ~3.7 for opponent. No evidence opponent adapted away from spawn/perimeter passivity.
- Reviewed `robot.py`; kept it unchanged. The existing spawn-evacuation + annulus survival macro already converts the opponent's spawn-stuck behavior into guaranteed wins, and changing combat/endgame chase risks self-play regressions without improving the recorded win count.
- Smoke checked locally: still beats a passive bot (seed 2, Blue won 32-4 units) and naive nearest-enemy chaser as both colors (seed 3: Blue 29-1, Red 31-1). Runtime remains a few seconds/match, well under 60s.
