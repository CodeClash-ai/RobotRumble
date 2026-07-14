# Agent notes for RobotRumble (gpt-5-5)

Round 1 changes:
- Replaced the starter `robot.py` quadrant targeter. The starter can stalemate forever when mirrored armies start in different quadrants (as in `/logs/rounds/0`, all 200 sims tied 20-20/4-4).
- New strategy: every turn chooses one global focus target using total walking distance, enemy health, and allied adjacency; robots attack adjacent low-health enemies first and otherwise move toward the focus target with simple collision reservations.
- Includes spawn timing avoidance: on turns 10,20,... it avoids moving onto spawn squares because the engine clears spawn tiles at the start of turns 11,21,... before recurring spawns.

Useful local tests run:
```
./rumblebot run term --results-only --seed test robot.py builtin-bots/simple-bot.js      # Blue/gpt won 137-5
./rumblebot run term --results-only --seed test builtin-bots/simple-bot.js robot.py      # Red/gpt won 121-15
./rumblebot run term --results-only --seed test robot.py builtin-bots/heuristic-bot.js   # Blue/gpt won 48-24
./rumblebot run term --results-only --seed test builtin-bots/heuristic-bot.js robot.py   # Red/gpt won 44-14
./rumblebot run term --results-only --seed test robot.py builtin-bots/black-magic.js     # lost badly to black-magic (expected; builtin black-magic is very strong)
```
Against the previous checked-in starter (`git show HEAD:robot.py > /tmp/old_robot.py`), current bot wins as both colors on seeds `test` and `0` by large margins.

Potential future work:
- The builtin `black-magic.js` one-ply simulator is stronger than this Python bot; consider porting/adapting its local action scoring to Python if time allows.
- Current movement reservation is greedy in per-unit execution order and cannot coordinate swaps; a global planner in `init_turn` may improve engagements.

Round 2 notes:
- Reviewed `/logs/rounds/1/results.json`: current `robot.py` swept anton__anton3000 250-0 as Blue. Average final state across the 250 sim logs was about Blue 25.7 units / 117.9 HP vs Red 2.1 units / 10 HP.
- I did not change `robot.py`; a small experiment to force adjacent units off spawn on turns 10/20/... did not improve local regression (the previous/current bot beat it head-to-head), so it was reverted.
- Added `tools_analyze_logs.py` to summarize `/logs/rounds/N` text logs for future teammates.
- Current bot still loses badly to builtin `black-magic.js`; a Python port of its one-ply planner was tried in `/tmp` and beat black-magic in one game but was very slow (~20s/sim in Python), so do not drop it in without optimizing heavily.

Round 1 (current) update:
- Replaced `robot.py` again with a faster Python port/adaptation of builtin `black-magic.js` one-ply tactical planner. It precomputes each turn in `init_turn`, predicts adjacent enemy attacks, and greedily improves friendly moves/attacks using lexicographic simulated board score (unit count, surrounds, health, closeness). It keeps the earlier spawn-wipe avoidance for turns 10/20/...
- Saved the previous focus-fire bot as `robot_focus_round1.py` for regression testing/reference.
- Local regression: new `robot.py` beats `robot_focus_round1.py` convincingly as both colors across tested seeds 0,1,2,42 (e.g. seed 42: 17-1 units as Blue and 18-3 as Red). It still beats simple/heuristic/needle/chaser/flail/random builtins as both colors on spot checks.
- Against builtin `black-magic.js` it is much closer than the old focus bot: spot/batch testing was mixed but no longer a blowout (first 10 batch as Blue vs black-magic: 7-3). Runtime is about 1.5-2.8s per local CLI game, well below per-game timeout but slower than old focus bot.

Round 2 follow-up (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: both were 250-0 sweeps for gpt-5-5 against `happysquid__test` (round 0 as Red, round 1 as Blue). The current black-magic-style Python planner leaves the opponent at ~1-2 units on average.
- I kept `robot.py` unchanged after regression tests. It still crushes the saved focus bot (`robot_focus_round1.py`) as both colors on seeds 5-7. Spot checks versus builtin `black-magic.js` remain mixed but competitive.
- Experiments not adopted: a more exact Python movement simulator for the planner (modeled movement priority/blocked chains) regressed vs the current simpler black-magic tick; changing greedy planning order (center/high-adjacency/low-health variants) also regressed or was color-sensitive.
- Recommendation: keep the current bot unless logs show the opponent adapted; if improving, benchmark head-to-head as both colors over multiple seeds because many tactical tweaks are strongly seed/color dependent.

Round 1 review (latest agent):
- Checked `/logs/rounds/0/results.json`: current bot swept `anton__wallifier` 250-0 as Blue, with large average margins (about 28.3 vs 0.9 units, 134 vs 3.4 HP).
- Kept `robot.py` unchanged. The existing black-magic-style tactical planner is already dominating this opponent; earlier notes warn several tactical tweaks regressed in head-to-head tests.
- Spot regression still passes versus builtin heuristic as both colors on seed 0. Recommendation remains: do not change the planner unless new logs show losses or a clear issue.

Round 2 check (latest):
- Re-read current match logs `/logs/rounds/0` and `/logs/rounds/1` against `anton__wallifier`; current `robot.py` swept 250-0 as both Blue and Red. Margins remain huge (round0 avg 28.3 vs 0.9 units, round1 avg 27.7 vs 1.0 units for us).
- Verified `robot.py` still matches the intended fast black-magic-style planner and spot-tested locally versus builtin `black-magic.js`; results are mixed/competitive and runtime is around 2-2.5s per game.
- No bot logic changes made this turn. Given the opponent is being swept and previous tactical changes regressed, safest recommendation is to keep `robot.py` unchanged unless future logs show losses.

Current round check (ldang__nessy):
- Reviewed `/logs/rounds/0/results.json`: current bot swept `ldang__nessy` 250-0 as Blue.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/us 25.45 units / 102.1 HP vs Red 1.53 units / 6.0 HP; worst unit margin still +15 units. This opponent is not close to beating the current planner.
- Spot regression on seed 0 still beats builtin heuristic as both colors and remains competitive with builtin black-magic. No `robot.py` logic changes made; safest plan is to keep the current black-magic-style planner unless future logs show actual losses.

Round 2 check (current run vs ldang__nessy):
- Reviewed both available logs for this matchup: `/logs/rounds/0` had us Blue and `/logs/rounds/1` had us Red. Current `robot.py` swept both 250-0.
- Margins from `tools_analyze_logs.py`: round0/us Blue averaged 25.45 units / 102.1 HP vs 1.53 units / 6.0 HP; round1/us Red averaged 25.28 units / 101.4 HP vs 1.61 units / 6.3 HP. No close games observed.
- Spot-tested current bot locally vs builtin `black-magic.js` on seed 0 as both colors; split by color as expected from prior notes and runtime stayed ~2.25s/game.
- No `robot.py` changes made. The black-magic-style planner is crushing this opponent, and previous README notes indicate many tactical tweaks regressed, so keeping the bot stable is safest.

Round 1 check vs ldang__nemo (current agent):
- Reviewed `/logs/rounds/0/results.json`: opponent `ldang__nemo` was Blue, gpt-5-5/current bot was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0`: average final Blue/opponent 1.24 units / 4.55 HP vs Red/us 26.30 units / 112.14 HP; every sim was a Red win.
- Spot regression still passes locally: current `robot.py` beat builtin heuristic both colors on seed 0 and split/mirrored competitively with builtin `black-magic.js` on seed 0.
- No logic changes made. The existing fast black-magic-style planner is dominating this opponent; safest recommendation is to keep `robot.py` stable unless future logs show losses.

Round 2 check vs ldang__nemo (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current black-magic-style `robot.py` swept `ldang__nemo` 250-0 in both colors (round0 us Red, round1 us Blue).
- `tools_analyze_logs.py` margins remain very large: round0 avg us/Red 26.30 units / 112.14 HP vs opponent 1.24 units / 4.55 HP; round1 avg us/Blue 26.30 units / 111.62 HP vs opponent 1.22 units / 4.64 HP.
- Spot regression local seed 0 still beats builtin heuristic as both colors and is competitive with builtin black-magic (`robot.py` as Blue won 13-9 units; as Red lost mirrored 9-13 units). Runtime about 2.1-2.3s/game.
- No logic changes made. Given two sweeps and previous notes that tactical tweaks regressed, safest action is to keep the current planner stable unless later logs show losses.

Current round check vs navster8__bash-brothers:
- Reviewed `/logs/rounds/0/results.json`: opponent `navster8__bash-brothers` was Blue, gpt-5-5/current bot was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0`: average final Blue/opponent 1.216 units / 4.608 HP vs Red/us 26.148 units / 111.688 HP; every sim was a Red win, with several complete enemy wipes.
- Spot regression still passes locally: current `robot.py` beat builtin heuristic as Red on seed 0 (20-5 units) and as Blue on seed 0 (15-4 units).
- No logic changes made. The black-magic-style tactical planner continues to dominate this opponent by a very large margin, so keeping `robot.py` stable is safest unless later logs show actual losses.

Round 2 check vs navster8__bash-brothers (current agent):
- Reviewed `/logs/rounds/1/results.json`: gpt-5-5/current bot was Blue and swept `navster8__bash-brothers` 250-0. Combined with prior round0 Red sweep, this matchup is fully dominated in both colors.
- `tools_analyze_logs.py /logs/rounds/1`: average final Blue/us 26.31 units / 112.20 HP vs Red/opponent 1.25 units / 4.90 HP; worst listed unit margin still +16 units.
- Spot regression still passes locally versus builtin heuristic on seed 1 as both colors. No `robot.py` changes made; current black-magic-style planner remains the safest stable choice unless later logs show losses.

Current round check vs aaoutkine__dark-knight:
- Reviewed `/logs/rounds/0/results.json`: gpt-5-5/current bot was Blue and swept `aaoutkine__dark-knight` 250-0.
- `tools_analyze_logs.py /logs/rounds/0`: average final Blue/us 27.08 units / 126.21 HP vs Red/opponent 1.18 units / 4.34 HP; worst logged unit margin was still +17 units (20 vs 3/4 range), so this matchup is not close.
- Spot regression still passes locally versus builtin heuristic as both colors on seed 0, and remains competitive with builtin black-magic on seed 0. No `robot.py` changes made; the stable black-magic-style planner remains safest unless future logs show actual losses.

Round 2 check vs aaoutkine__dark-knight (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `aaoutkine__dark-knight` 250-0 in both recorded rounds (both logs list us as Blue). Margins stayed very large: round0 avg Blue/us 27.08 units / 126.21 HP vs Red/opponent 1.18 units / 4.34 HP; round1 avg Blue/us 26.95 units / 125.62 HP vs Red/opponent 1.18 units / 4.22 HP.
- Spot regression local seed 2 still beats builtin heuristic as both colors (17-6 units as Blue; 22-4 units as Red). Versus builtin black-magic on seed 2 the outcome was color/mirror-sensitive as before (our `robot.py` as Blue won 18-5; as Red lost 5-18), with runtime about 2s/game.
- No `robot.py` logic changes made. The current fast black-magic-style one-ply planner is crushing this opponent, and prior README notes document multiple tactical experiments that regressed, so keeping the bot stable remains safest.

Current round check vs mountain__neuralbot1-1h:
- Reviewed `/logs/rounds/0/results.json`: opponent `mountain__neuralbot1-1h` was Blue, gpt-5-5/current bot was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0`: average final Blue/opponent 1.20 units / 4.47 HP vs Red/us 28.90 units / 123.13 HP; every sim was a Red win and several ended with complete enemy wipes.
- Spot regression still passes locally versus builtin heuristic on seed 0 as both colors. No `robot.py` changes made; current black-magic-style one-ply planner is dominating this opponent, so keeping it stable is safest unless future logs show actual losses.
