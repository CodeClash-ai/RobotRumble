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

Round 2 check vs mountain__neuralbot1-1h (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: both recorded rounds had opponent Blue and gpt-5-5/current bot Red, and we swept 250-0 in both.
- `tools_analyze_logs.py` margins stayed enormous: round0 avg opponent/Blue 1.20 units / 4.47 HP vs us/Red 28.90 units / 123.13 HP; round1 avg opponent/Blue 1.18 units / 4.47 HP vs us/Red 28.52 units / 122.05 HP.
- Spot regression on seed 3 still beats builtin heuristic as both colors. Versus builtin black-magic remains color/seed mixed as previously documented, but runtime stayed around 2-3s/game.
- No `robot.py` logic changes made. The stable black-magic-style planner is crushing this opponent; safest recommendation is still to keep it unchanged unless future logs show actual losses.

Current round check vs sivecano__clouded-mind:
- Reviewed `/logs/rounds/0/results.json`: opponent `sivecano__clouded-mind` was Blue, gpt-5-5/current bot was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0`: average final Blue/opponent 1.74 units / 6.50 HP vs Red/us 25.74 units / 125.08 HP; every sim was a Red win, with many complete enemy wipes.
- No `robot.py` logic changes made. The existing fast black-magic-style one-ply planner is dominating this opponent by a large margin, and previous README notes document several tactical tweaks that regressed, so keeping the bot stable remains safest unless later logs show actual losses.

Round 2 check vs sivecano__clouded-mind (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: both recorded rounds had opponent `sivecano__clouded-mind` as Blue and gpt-5-5/current bot as Red; current `robot.py` swept both 250-0.
- `tools_analyze_logs.py` margins remain huge: round0 avg opponent/Blue 1.744 units / 6.496 HP vs us/Red 25.740 units / 125.080 HP; round1 avg opponent/Blue 1.664 units / 6.364 HP vs us/Red 25.464 units / 123.892 HP.
- Spot regression on seed 4 still beats builtin heuristic as both colors. No `robot.py` changes made; current fast black-magic-style one-ply planner is dominating this opponent, so stability is safest unless later logs show actual losses.

Current round check vs mountain__neuralbot2-6h:
- Reviewed `/logs/rounds/0/results.json`: opponent `mountain__neuralbot2-6h` was Blue, gpt-5-5/current bot was Red, and current `robot.py` swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0`: average final Blue/opponent 1.56 units / 6.22 HP vs Red/us 32.50 units / 156.70 HP; every sim was a Red win, with many complete enemy wipes and huge margins.
- Spot regression local seed 0 still beats builtin heuristic as both colors. No `robot.py` logic changes made; the existing fast black-magic-style one-ply planner is dominating this opponent, so keeping it stable is safest unless future logs show actual losses.

Round 2 current check vs mountain__neuralbot2-6h (gpt-5-5):
- Reviewed `/logs/rounds/1/results.json` in addition to prior round0 notes: opponent `mountain__neuralbot2-6h` was Blue, gpt/current bot was Red, and we swept 250-0 again.
- `tools_analyze_logs.py /logs/rounds/1`: average final Blue/opponent 1.61 units / 6.32 HP vs Red/us 32.16 units / 155.04 HP; many complete wipes and huge margins.
- Spot regression on seed 5 still beats builtin heuristic as both colors. No `robot.py` logic changes made; current fast black-magic-style tactical planner is dominating this opponent, so keeping it stable is safest.

Current round check vs kalkin__artemis:
- Reviewed `/logs/rounds/0/results.json`: gpt-5-5/current bot was Blue and swept `kalkin__artemis` 250-0.
- `tools_analyze_logs.py /logs/rounds/0`: average final Blue/us 26.96 units / 98.52 HP vs Red/opponent 1.86 units / 6.65 HP; worst unit margin found was still +15 units (19 vs 4), so no close losses.
- Spot regression still passes locally versus builtin heuristic as both colors on seed 0, and remains competitive with builtin black-magic on seed 0. No `robot.py` logic changes made; current fast black-magic-style one-ply planner is dominating this opponent, so stability is safest unless future logs show actual losses.

Round 2 check vs kalkin__artemis (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `kalkin__artemis` 250-0 in both colors (round0 us Blue, round1 us Red).
- `tools_analyze_logs.py` margins: round0 avg us/Blue 26.96 units / 98.52 HP vs opponent 1.86 units / 6.65 HP; round1 avg opponent/Blue 1.96 units / 7.23 HP vs us/Red 26.83 units / 98.92 HP. Worst margins were still very large.
- Spot regression on seed 6 still beats builtin heuristic as both colors. No `robot.py` logic changes made; the fast black-magic-style tactical planner remains safest given repeated sweeps and previous regressing experiments.

Current round check vs kalkin__artemis2 (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `kalkin__artemis2` was Blue, gpt/current `robot.py` was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0`: average final opponent/Blue 1.75 units / 5.84 HP vs us/Red 22.87 units / 67.57 HP; every sim was a Red win.
- Spot regression on seed 7 still beats builtin heuristic as both colors and is competitive with builtin black-magic (split by color/mirror on this seed). No `robot.py` logic changes made; current fast black-magic-style tactical planner remains safest given the sweep and prior notes that tweaks often regress.

Round 2 check vs kalkin__artemis2 (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `kalkin__artemis2` 250-0 in both recorded rounds. Both logs list opponent as Blue and us as Red.
- `tools_analyze_logs.py /logs/rounds/1` summary: avg final opponent/Blue 1.75 units / 5.89 HP vs us/Red 23.35 units / 68.74 HP; worst unit margins were still very large and every sim was a Red win.
- Spot regression on seed 8 still beats builtin heuristic as both colors. No `robot.py` logic changes made; current fast black-magic-style tactical planner remains safest given repeated sweeps and prior regressing experiments.

Current round check vs navster8__maginot-line (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: gpt/current `robot.py` was Blue and swept `navster8__maginot-line` 250-0.
- `tools_analyze_logs.py /logs/rounds/0`: average final Blue/us 32.43 units / 142.80 HP vs Red/opponent 0.95 units / 3.17 HP; every sim was a Blue win and the worst unit margin was still very large (19 vs 2 in sim_234).
- Spot regression on seed 0 still beats builtin heuristic as both colors. Against builtin black-magic seed 0 remains mirror/color split as in prior notes (our bot as Blue wins 13-9; as Red matchup mirrored loses 9-13), runtime around 2s/game.
- No `robot.py` logic changes made. The existing fast black-magic-style tactical planner is crushing this opponent, so stability is safest unless later logs show actual losses.

Round 2 check vs navster8__maginot-line (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: both recorded rounds list gpt-5-5/current `robot.py` as Blue vs `navster8__maginot-line` as Red, and we swept 250-0 in both.
- `tools_analyze_logs.py /logs/rounds/1` summary: avg final Blue/us 32.55 units / 141.71 HP vs Red/opponent 0.99 units / 3.36 HP; worst listed margin was still very large (21 vs 6 units in sim_213) and every sim was a Blue win.
- Spot regression on seed 1 still beats builtin heuristic as both colors (15-11 units as Blue; 18-3 units as Red). No `robot.py` changes made; the current fast black-magic-style one-ply planner is dominating this opponent, so keeping it stable remains safest.

Current round check vs jiricodes__jiricodes-bot (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: gpt/current `robot.py` was Blue and swept `jiricodes__jiricodes-bot` 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/us 29.93 units / 145.56 HP vs Red/opponent 0.17 units / 0.49 HP; every sim was a Blue win and most were complete/near-complete wipes.
- Spot regression on seed 0 still beats builtin heuristic as both colors. No `robot.py` logic changes made; the existing fast black-magic-style one-ply planner is overwhelmingly winning this matchup, so stability is safest unless future logs show losses.

Round 2 check vs jiricodes__jiricodes-bot (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `jiricodes__jiricodes-bot` 250-0 in both colors (round0 us Blue, round1 us Red).
- `tools_analyze_logs.py` margins were overwhelming: round0 avg us/Blue 29.93 units / 145.56 HP vs opponent 0.17 units / 0.49 HP; round1 avg opponent/Blue 0.15 units / 0.36 HP vs us/Red 29.70 units / 144.16 HP.
- Spot regression on seed 9 still beats builtin heuristic as both colors and is competitive/mixed with builtin black-magic; runtime stayed around 2-3s/game.
- No `robot.py` logic changes made. The fast black-magic-style one-ply planner is crushing this opponent and prior tactical tweaks often regressed, so keeping the bot stable remains safest.

Current round check vs sbasu3__meek-bot (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: gpt/current `robot.py` was Blue and swept `sbasu3__meek-bot` 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/us 21.98 units / 59.94 HP vs Red/opponent 1.52 units / 4.81 HP; every sim was a Blue win and the worst unit margin was still +14 units.
- Spot regression on seed 0 still beats builtin heuristic as both colors and remains mirror/color competitive with builtin black-magic. No `robot.py` logic changes made; current fast black-magic-style planner is safely dominating this opponent, so stability remains the best recommendation unless future logs show losses.

Round 2 check vs sbasu3__meek-bot (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `sbasu3__meek-bot` 250-0 in both recorded rounds; both list us as Blue.
- `tools_analyze_logs.py` margins remain comfortable despite this being one of the lower-HP sweeps: round0 avg Blue/us 21.98 units / 59.94 HP vs Red/opponent 1.52 units / 4.81 HP; round1 avg Blue/us 21.75 units / 60.42 HP vs Red/opponent 1.57 units / 4.84 HP. Worst unit margins were still +12 or better.
- Spot regression on seed 10 still beats builtin heuristic as both colors. No `robot.py` logic changes made; current fast black-magic-style planner is safely winning and previous tactical experiments often regressed, so stability remains recommended unless logs show losses.

Current round check vs essickmango__fruity-test (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: gpt/current `robot.py` was Blue and swept `essickmango__fruity-test` 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/us 22.00 units / 72.63 HP vs Red/opponent 2.41 units / 8.31 HP; every sim was a Blue win and worst unit margin was still comfortably positive (+8 units in sim_45).
- Spot regression on seed 0 still beats builtin heuristic as both colors. No `robot.py` logic changes made; current fast black-magic-style one-ply planner is safely winning and previous tactical tweaks often regressed, so stability remains recommended unless future logs show losses.

Round 2 check vs essickmango__fruity-test (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `essickmango__fruity-test` 250-0 in both colors (round0 us Blue, round1 us Red).
- `tools_analyze_logs.py` margins: round0 avg us/Blue 22.00 units / 72.63 HP vs opponent/Red 2.41 units / 8.31 HP; round1 avg opponent/Blue 2.22 units / 7.37 HP vs us/Red 21.75 units / 71.92 HP. Worst unit margins remained comfortably positive.
- No `robot.py` logic changes made. The existing fast black-magic-style one-ply planner is safely winning this matchup, and prior notes document many regressing tactical tweaks, so keeping the bot stable is still recommended unless future logs show losses.

Current round check vs tabaxi3k__charles (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `tabaxi3k__charles` was Blue, gpt/current `robot.py` was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/opponent 0.60 units / 1.84 HP vs Red/us 34.66 units / 166.48 HP; every sim was a Red win, with many complete wipes and enormous margins.
- Spot regression on seed 0 still beats builtin heuristic as both colors. No `robot.py` logic changes made; current fast black-magic-style one-ply planner is overwhelmingly winning this matchup, so keeping it stable is safest unless later logs show actual losses.

Round 2 check vs tabaxi3k__charles (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: both recorded rounds had opponent `tabaxi3k__charles` as Blue and gpt/current `robot.py` as Red; current bot swept both 250-0.
- `tools_analyze_logs.py /logs/rounds/1`: avg final opponent/Blue 0.56 units / 1.68 HP vs us/Red 34.96 units / 167.89 HP; every sim was a Red win, many complete wipes.
- Spot regression on seed 11 still beats builtin heuristic as both colors. No `robot.py` logic changes made; the existing fast black-magic-style one-ply planner is overwhelmingly winning, so stability remains safest unless future logs show losses.

Current round check vs devchris__first_test (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `devchris__first_test` was Blue, gpt/current `robot.py` was Red, and current bot swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 0.53 units / 1.64 HP vs us/Red 34.88 units / 167.97 HP; every sim was a Red win with many complete wipes.
- Spot regression on seed 0 still beats builtin heuristic as both colors and remains mirror/color competitive with builtin black-magic. No `robot.py` logic changes made; the existing fast black-magic-style one-ply planner is overwhelmingly winning this matchup, so stability is safest unless future logs show losses.

Round 2 check vs devchris__first_test (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: both recorded rounds had opponent `devchris__first_test` as Blue and gpt/current `robot.py` as Red; current bot swept both 250-0.
- `tools_analyze_logs.py` margins were enormous: round0 avg opponent/Blue 0.53 units / 1.64 HP vs us/Red 34.88 units / 167.97 HP; round1 avg opponent/Blue 0.62 units / 1.86 HP vs us/Red 34.76 units / 167.40 HP.
- Spot regression on seed 12 still beats builtin heuristic as both colors. No `robot.py` changes made; the existing fast black-magic-style one-ply planner is overwhelmingly winning this matchup, so keeping it stable remains safest unless future logs show losses.

Current round check vs aaa__jippty5 (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: gpt/current `robot.py` was Blue and swept `aaa__jippty5` 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/us 22.57 units / 71.46 HP vs Red/opponent 2.62 units / 8.76 HP. Worst listed unit margin was still +15 units, so this matchup is comfortably winning.
- Spot regression local seed 0 still beats builtin heuristic as both colors and simple-bot as Blue. Versus builtin black-magic seed 0 remains the expected mirror/color split (Blue wins 13-9 either side), so current planner is healthy.
- No `robot.py` logic changes made. The existing fast black-magic-style one-ply planner is safely winning, and prior notes document many tactical tweaks that regressed, so keeping it stable remains safest unless future logs show actual losses.

Round 2 check vs aaa__jippty5 (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `aaa__jippty5` 250-0 in both recorded rounds; both list gpt/current bot as Blue.
- `tools_analyze_logs.py` margins: round0 avg Blue/us 22.57 units / 71.46 HP vs Red/opponent 2.62 units / 8.76 HP; round1 avg Blue/us 22.72 units / 71.24 HP vs Red/opponent 2.61 units / 8.86 HP. Worst sampled unit margins remain comfortably positive.
- Spot regression on seed 13 still beats builtin heuristic as both colors and simple-bot as Blue, with runtime about 2s/game.
- No `robot.py` logic changes made. The existing fast black-magic-style one-ply planner is safely winning this matchup; given many prior tactical tweaks regressed, keeping it stable remains safest unless future logs show losses.

Current round check vs jay0jayjay__naivestarter (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `jay0jayjay__naivestarter` was Blue, gpt/current `robot.py` was Red, and current bot swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/opponent 2.24 units / 4.82 HP vs Red/us 28.45 units / 87.13 HP; every sim was a Red win, with several complete enemy wipes.
- Spot regression on seed 0 still beats builtin heuristic as both colors. No `robot.py` logic changes made; the existing fast black-magic-style one-ply planner is safely dominating this opponent, so keeping it stable remains best unless later logs show actual losses.

Round 2 check vs jay0jayjay__naivestarter (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: both recorded rounds had opponent `jay0jayjay__naivestarter` as Blue and gpt/current `robot.py` as Red; current bot swept both 250-0.
- `tools_analyze_logs.py` margins remained large: round0 avg opponent/Blue 2.24 units / 4.82 HP vs us/Red 28.45 units / 87.13 HP; round1 avg opponent/Blue 1.99 units / 4.41 HP vs us/Red 28.55 units / 87.45 HP.
- Spot regression on seed 14 still beats builtin heuristic as both colors (18-7 units as Blue, 24-5 units as Red). No `robot.py` logic changes made; the existing fast black-magic-style one-ply planner is safely winning this matchup, so keeping it stable remains safest unless future logs show losses.

Current round check vs luisa__luisasrobot (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: gpt/current `robot.py` was Blue and swept `luisa__luisasrobot` 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/us 17.72 units / 42.31 HP vs Red/opponent 2.36 units / 7.23 HP; every sim was a Blue win. This is a lower-margin sweep than many prior opponents, but worst listed unit margins were still safely positive (+6 units or more in the worst samples).
- Spot regression on seed 0 still beats builtin heuristic as both colors. No `robot.py` changes made; the current fast black-magic-style one-ply planner is winning this matchup cleanly, and prior notes document many tactical tweaks that regressed, so stability remains safest unless future logs show actual losses.

Round 2 current check vs luisa__luisasrobot (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `luisa__luisasrobot` 250-0 in both colors (round0 us Blue, round1 us Red).
- `tools_analyze_logs.py` margins: round0 avg us/Blue 17.72 units / 42.31 HP vs opponent/Red 2.36 units / 7.23 HP; round1 avg opponent/Blue 2.44 units / 7.38 HP vs us/Red 18.06 units / 43.32 HP. This is a lower-margin sweep than many previous opponents, but no close losses were observed.
- Spot regression on seed 15 still beats builtin heuristic as both colors. No `robot.py` changes made; the existing fast black-magic-style one-ply planner remains safely winning and prior tactical tweaks often regressed, so keeping it stable is recommended unless future logs show actual losses.

Current round check vs luisa__baselinegere (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `luisa__baselinegere` was Blue, gpt/current `robot.py` was Red, and current bot swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 2.44 units / 7.16 HP vs us/Red 18.24 units / 44.25 HP; every sim was a Red win. This is a lower-margin sweep than many simple opponents but still safely positive (worst unit samples around +23/+24 Red units in analyzer output because it reports blue-margin ordering awkwardly).
- Spot regression on seed 0 still beats builtin heuristic as both colors and shows the expected mirror/color split vs builtin black-magic (Blue side wins 13-9 either way). No `robot.py` logic changes made; the existing fast black-magic-style one-ply planner remains safest given repeated sweeps and prior regressing experiments.

Round 2 check vs luisa__baselinegere (current agent):
- Reviewed `/logs/rounds/0/results.json` and `/logs/rounds/1/results.json`: current `robot.py` swept `luisa__baselinegere` 250-0 in both colors (round0 us Red, round1 us Blue).
- `tools_analyze_logs.py` margins are safe though smaller than some earlier easy opponents: round0 avg opponent/Blue 2.44 units / 7.16 HP vs us/Red 18.24 units / 44.25 HP; round1 avg us/Blue 17.99 units / 43.12 HP vs opponent/Red 2.45 units / 7.47 HP. Worst listed unit margins were still positive (e.g. round1 worst 11 vs 7 units).
- No `robot.py` logic changes made. Since the matchup is already a full sweep in both colors and README history documents many tactical tweaks that regressed against the current black-magic-style planner, stability remains the safest choice.

Current round check vs anton__anton4000 (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: current `robot.py` was Blue vs `anton__anton4000` Red and swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` margins: avg final Blue/us 19.21 units / 50.57 HP vs Red/opponent 2.96 units / 10.28 HP. This is lower margin than many earlier sweeps but still all wins; worst sampled final unit count was 10 vs 9 (sim_67) with Blue/us ahead on health 27-42? Note analyzer prints health blue/red: sim_67 final Health 27 42 Units 10 9, so Blue won by unit tiebreak despite lower health.
- Spot regression on seed 0 still beats builtin heuristic as both colors. Given the existing planner swept the opponent and README history documents many tactical tweaks that regressed, I kept `robot.py` unchanged for stability.

Round 2 check vs anton__anton4000 (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: both recorded rounds list gpt/current `robot.py` as Blue vs `anton__anton4000` as Red, and current bot swept both 250-0.
- `tools_analyze_logs.py` margins are positive but this opponent leaves more survivors than many prior matchups: round0 avg Blue/us 19.21 units / 50.57 HP vs Red/opponent 2.96 units / 10.28 HP; round1 avg Blue/us 19.60 units / 51.54 HP vs Red/opponent 3.08 units / 10.73 HP. Worst unit margins in these logs were still wins (e.g. 10 vs 9 with higher enemy HP in sim_67, but score is by unit win and every sim is Blue win).
- Spot regression on seed 14 still beats builtin heuristic as both colors and remains mirror/color competitive with builtin black-magic on seed 0. No `robot.py` changes made; prior tactical experiments often regressed, so I kept the stable fast black-magic-style one-ply planner.

Current round check vs aayyad__testbot (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: gpt/current `robot.py` was Blue and swept `aayyad__testbot` 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/us 19.46 units / 48.84 HP vs Red/opponent 2.33 units / 7.40 HP. This is a smaller-margin sweep than very weak opponents, but every sim was still a Blue win; the worst sampled final unit margin was 11 vs 6 (sim_55), still safely ahead on units/health.
- Spot regression on seed 16 still beats builtin heuristic as both colors and remains mirror/color competitive with builtin black-magic on seed 0. No `robot.py` logic changes made; the existing fast black-magic-style one-ply planner is safely sweeping this opponent, and prior README history documents many tactical tweaks that regressed.

Current round check vs aayyad__testbot (round 2, current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`. Round0 had us Blue and swept 250-0 with avg 19.46 units / 48.84 HP vs opponent 2.33 / 7.40.
- Round1 had opponent Blue and us Red; current bot scored 248-1-1 (one Blue/opponent win in `sim_238`, one tie in `sim_153`). Average still strongly favored us as Red: opponent/Blue 2.44 units / 7.71 HP vs us/Red 18.50 units / 46.74 HP.
- Investigated the two non-wins. Both reached turn 100 with small unit-count endings (sim_238 final Blue 9 vs Red 8; sim_153 final 8 vs 8 tie). The game winner is unit count only, not health.
- Quick experiments not adopted: forcing units off spawn on spawn-clear turns, changing score priority to health earlier/later/final turns, and allowing spawn moves on turn100. Head-to-head spot tests versus current `robot.py` were mixed or worse (notably late/final health variants often hurt Red/seed238), so I left `robot.py` unchanged for stability.
- Future idea if time: build a replay/simulation harness for the exact aayyad non-win seeds and test endgame-specific unit-preservation/kill-confirm heuristics, but benchmark heavily because prior tactical tweaks regress color/seed matchups.


Current round check vs edward__flail (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: current bot was Blue vs `edward__flail` Red and won the round 241-6-3, but this was the first recent matchup with actual losses/ties. Analyzer showed avg Blue/us 18.2 units / 61.7 HP vs Red 5.8 units / 17.7 HP; worst loss was sim_215 ending 6 vs 14 units.
- Investigated flail losses: Red flail tends to scatter/retreat and our surround-prioritized planner can over-trade in the late game.
- Modified `robot.py` minimally: added `CURRENT_TURN` and, from turn 80 onward, changed the lexicographic tactical score order to prioritize health before surround pattern (`unit_score, health_score, surround_score, distance_score`). Early/midgame behavior remains unchanged.
- Spot checks vs builtin `flail.js` on problematic/local seeds improved all tested seeds to Blue wins (including seed 215 now 22-3 units; seeds 10/28/122/153/178 also wins). Versus builtin `black-magic.js` spot results remain mixed/competitive, with one regression on seed1 but no broad benchmark due step/time limits.
- Future teammates: if later logs show this late-health tweak regresses stronger opponents, consider reverting to `/tmp/robot_current.py` style old score order, but for this flail matchup it appears to fix the observed non-wins.

Round 2 follow-up vs edward__flail (current agent):
- Available logs: round0 us Blue won 241-6-3; round1 us Red won 239-7-4. This flail opponent is the first recent matchup with non-wins in both colors.
- Previous agent added a late-game (turn >=80) score order that prioritizes health before surround to reduce over-trading. I tested moving that switch earlier.
- Changed `robot.py` threshold from turn >=80 to turn >=60 for the health-before-surround tactical score. Rationale: flail scatters/flees, and preserving healthy unit count earlier in the endgame improved sampled losing/tie seeds.
- Spot tests vs builtin `flail.js`: threshold60 won sampled problematic Blue seeds 116/122/178/215 and Red seeds 118/130/151/209, plus seeds 0-4 as Red in the partial timed batch. Existing threshold80 already did well locally but logs still had non-wins; threshold60 often produced larger margins on these samples.
- Regression spot checks: threshold60 still beats builtin heuristic both colors (seed1) and remains mixed/competitive with builtin black-magic over seeds 0-2, with no obvious runtime issue (~2-3s/game). This is a small risk vs the historically stable planner, but targeted at the only observed current weakness.

Current round check vs mousetail__genetic-robot (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: current bot was Blue vs `mousetail__genetic-robot` Red and won 247-2-1. This opponent is closer than most prior sweeps. Analyzer showed avg final Blue/us 17.82 units / 53.10 HP vs Red/opponent 3.28 units / 11.96 HP; non-wins were sim_178 (11-13 units), sim_243 (8-11), and sim_235 tie (14-14). In the bad logs, Red gained/kept extra units after late spawn waves while our late-health planner sometimes still traded down or failed to preserve enough friendly bodies.
- Changed `robot.py` scoring slightly for very late game only: `_score` now tracks `friend_health_score`, and from turn >=85 returns `(unit_score, friend_health_score, health_score, surround_score, distance_score)`. Turn 60-84 remains the prior flail-targeted `(unit_score, health_score, surround_score, distance_score)`, and early game is unchanged. Rationale: winner is unit count, and in the last 15 turns keeping our damaged units alive should matter more than chasing enemy HP/surrounds.
- Local spot tests: this variant beat current threshold60 head-to-head as Blue on seeds 178/235/243 (the problematic log seeds), lost narrowly on seed0, tied seed1. Versus builtin `flail.js`, it improved/kept wins on sampled seeds 0/1/178/235/243. Regression spots still beat builtin heuristic both colors on seed0 and remain mixed/competitive with builtin black-magic seed0. This is a targeted risk for the close mousetail matchup; revert the >=85 friend-health tier if future logs show broad regression.

Round 2 check vs mousetail__genetic-robot (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` wins strongly but not a full sweep. Round0 (us Blue) scored 247-2-1; round1 (us Red) scored 247-1-2.
- `tools_analyze_logs.py` margins: round0 avg Blue/us 17.82 units / 53.10 HP vs Red/opponent 3.28 units / 11.96 HP; round1 avg opponent/Blue 5.33 units / 21.62 HP vs us/Red 17.66 units / 60.16 HP. The few non-wins were late-map split/evasion positions, not broad tactical failure.
- Investigated possible tweaks but did not adopt them: late aggressive enemy-HP scoring, late distance/chase-first scoring, and a full spawn-ring avoidance fix. These changed head-to-head outcomes in seed/color-sensitive ways and often regressed versus current or builtin black-magic. The current stable black-magic-style planner remains the safest choice.
- Important code observation for future teammates: `_setup()` uses `Coords.is_spawn()` while the bundled Python stdlib defines `SPAWN_COORDS_STRINGS = map(...)`, a one-shot iterator. In standalone testing this only detected `(1,5)` after repeated calls. A formula-based 48-tile spawn ring is more correct, but local head-to-head `/tmp/robot_spawnfix.py` was mixed/regressive, likely because the old bot was more aggressive on perimeter turn-10 moves. Revisit only with careful multi-seed tests.

Current round check vs kalkin__maxad (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `kalkin__maxad` was Blue, gpt/current `robot.py` was Red, and current bot swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 4.40 units / 17.84 HP vs us/Red 19.78 units / 65.74 HP; every sim was a Red win. This is not as overwhelming as the weakest opponents, but still a clean sweep with safe margins (worst listed final unit counts around 9 Blue vs 27 Red, etc.).
- Spot regression on seed 0 still beats builtin heuristic as both colors. No `robot.py` changes made; given the sweep and prior notes that many tactical tweaks regress, keeping the current fast black-magic-style planner stable is safest.

Round 2 check vs kalkin__maxad (current agent follow-up):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`. Round0 had opponent Blue/us Red and was a 250-0 sweep. Round1 had us Blue/opponent Red and scored 249-0-1, with the only non-win `sim_70` ending tied 10-10 units (opponent ahead on HP, but winner is unit count; ties split no win).
- Round1 averages from `tools_analyze_logs.py`: us/Blue 19.78 units / 66.25 HP vs opponent/Red 4.35 units / 17.78 HP. Worst wins after the tie were still positive unit margins (e.g. 13-10, 15-10), so this is a very safe matchup overall.
- Investigated the tie: late spawn cycles reduced a 16-8 lead around turn 72 to 12-11 by turn 90, then passive split/evasion ended 10-10 at turn 100. Tested small late-game scoring variants in `/tmp` (more chase/contact after turn 95, late close-game aggression, formula-based spawn ring avoidance). Results were seed/color-sensitive and often regressed head-to-head against current `robot.py`, so no bot logic changes were adopted.
- Spot regression on seed 17 still beats builtin heuristic as both colors. Recommendation remains to keep the current fast black-magic-style planner stable unless future logs show real losses or repeated ties in this matchup.

Current round check vs mjburgess__rule99 (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent submission was invalid (`robot.py` missing required robot function), so current `robot.py` won 250-0 by validity/forfeit.
- Ran a spot regression locally versus builtin heuristic on seed 0; current bot still wins as Blue (13-10 units). No logic changes made.
- Recommendation: keep the current fast black-magic-style planner stable unless future logs show real losses; this round provides no gameplay evidence requiring a change.

Round 2 check vs mjburgess__rule99 (current agent):
- Reviewed `/logs/rounds/0/results.json` and `/logs/rounds/1/results.json`: opponent submission is still invalid in both recorded rounds (`robot.py` missing required robot function), so current `robot.py` won 250-0 by validity/forfeit twice.
- Spot regression local seed 0 versus builtin heuristic still passes as both colors (Blue won 13-10 units; Red won 24-7 units in the checked run).
- No bot logic changes made. With no gameplay evidence from this opponent and prior notes showing many tactical tweaks regressed, keeping the current fast black-magic-style planner stable is safest.

Current round check vs ketza__bob (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: current bot was Blue vs `ketza__bob` Red and scored 248-0-2 over 250 games. `tools_analyze_logs.py /logs/rounds/0` showed avg final Blue/us 20.14 units / 69.0 HP vs Red/opponent 4.76 units / 19.28 HP; only ties were sim_95 and sim_123, both tied on units but with us ahead on health.
- Made a very conservative endgame tweak in `robot.py`: on turns >=95 only when simulated unit count is tied and simulated sqrt-health is not ahead, the score now prioritizes lowering enemy health before the usual late-game self-health tiebreaker. This is intended to avoid preserving losing/tied-health unit-count draws while leaving winning endgames unchanged.
- Regression spot checks: unchanged wins vs builtin heuristic as both colors on seed 0; unchanged Blue win vs builtin black-magic seed 0 (13-12 units); head-to-head vs the previous `/tmp/robot_orig.py` on seed 0 still wins as Blue (19-18 units). Earlier broader experiments with more aggressive late-game enemy-health scoring regressed, so keep this condition narrow unless future logs justify more.

Round 2 follow-up vs ketza__bob (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`. Round0 (with previous code before the narrow >=95 tie-break tweak) was 248-0-2; round1 after the tweak was a clean 250-0 sweep with gpt/current bot Blue vs ketza__bob Red.
- `tools_analyze_logs.py /logs/rounds/1` summary: avg final Blue/us 20.35 units / 69.18 HP vs Red/opponent 4.78 units / 19.45 HP; worst final unit margin in the analyzer sample was still +4 units (12 vs 8), so the matchup now looks safe.
- Spot regression local seed 18 still beats builtin heuristic as both colors (21-9 units as Blue, 21-6 as Red). No `robot.py` changes made this turn; kept the existing black-magic-style planner plus prior conservative endgame tie-break.

Current round check vs suddenlyseals__control-center (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `suddenlyseals__control-center` was Blue, current bot was Red, and we scored 249 wins with 1 tie (no losses). `tools_analyze_logs.py /logs/rounds/0` shows avg final opponent/Blue 4.74 units / 18.62 HP vs us/Red 19.39 units / 62.17 HP.
- The lone tie was `/logs/rounds/0/sim_90.txt`: final units 11-11 but us/Red had lower raw HP (40 vs 53) despite leading before the final spawn wave. It exposed a sign error in the previous late-endgame tie-breaker: it preferred *higher* enemy sqrt-health when tied on units and behind on health.
- Changed only that tiny late-game scoring branch in `robot.py`: on turns >=95, tied units, and not ahead on sqrt-health, the secondary key is now `-enemy_sqrt_health` (implemented as `health_score - friend_health_score`) and then usual health/friend-health terms. This should make tied final positions more likely to convert by killing/damaging enemies instead of preserving their HP.
- Regression spot checks after the change: still beats builtin heuristic as both colors on seeds 0-3; still matches prior seed-0 outcomes vs builtin black-magic (Blue win/Red win according to side). Head-to-head vs the previous version is noisy/mirror-sensitive, but the change only triggers in very late tied-unit losing-health positions and directly targets the observed tie.

Round 2 follow-up vs suddenlyseals__control-center (current agent):
- Reviewed `/logs/rounds/1/results.json`: after the prior tiny late-game tie-break fix, current `robot.py` swept `suddenlyseals__control-center` 250-0 as Red (opponent Blue), improving from round0's 249-0-1.
- `tools_analyze_logs.py /logs/rounds/1` shows avg final opponent/Blue 4.72 units / 18.76 HP vs us/Red 19.34 units / 62.24 HP; worst listed margins remain very safe and every sim was a Red win.
- Spot regression on seed 19 still beats builtin heuristic as both colors. No `robot.py` logic changes made this turn; the current black-magic-style planner plus the narrow >=95 tied-unit enemy-health fix is performing well, so stability remains safest.

Current round check vs aaoutkine__school-bot (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `aaoutkine__school-bot` was Blue, current `robot.py` was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 3.62 units / 13.88 HP vs us/Red 23.84 units / 81.26 HP; every sim was a Red win and worst sampled margins were still huge.
- Spot regression on seed 20 still beats builtin heuristic as both colors. No `robot.py` logic changes made; current black-magic-style planner plus the narrow late-game tie fixes is safely winning this matchup, so stability is recommended unless later logs show actual losses.

Round 2 check vs aaoutkine__school-bot (current agent):
- Reviewed both available logs: `/logs/rounds/0` had opponent Blue/us Red, `/logs/rounds/1` had us Blue/opponent Red. Current `robot.py` swept 250-0 in both colors.
- `tools_analyze_logs.py` margins are large: round0 avg opponent/Blue 3.62 units / 13.88 HP vs us/Red 23.84 units / 81.26 HP; round1 avg us/Blue 23.94 units / 81.63 HP vs opponent/Red 3.58 units / 14.12 HP. Worst sampled finals still had wide unit margins.
- Spot regression on seed 21 still beats builtin heuristic as both colors. No `robot.py` changes made; the current black-magic-style planner plus prior narrow late-game tie fixes is safely sweeping this matchup, so stability remains recommended unless future logs show losses.

Current round check vs thesmilingturtl__naivefaa (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: current `robot.py` was Blue and scored 249 wins, 1 tie, 0 losses against `thesmilingturtl__naivefaa`.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/us 19.08 units / 63.90 HP vs Red/opponent 4.70 units / 19.44 HP. The single tie was `sim_30.txt` at 10-10 units but still 39-38 HP for us; next-worst margins were wins by +4 or more units.
- Spot regression still passes locally versus builtin heuristic as both colors on seed 0; current bot also remains competitive/mixed with builtin black-magic on seed 0.
- I experimented only in `/tmp` with a more aggressive late-game score to try to convert equal-unit endgames, but it regressed badly in self-play, so it was not adopted. No `robot.py` logic changes made; keeping the stable black-magic-style planner is safest given 249-0-1 and prior notes that tactical tweaks often regress.

Round 2 follow-up vs thesmilingturtl__naivefaa (current agent):
- Reviewed `/logs/rounds/1/results.json`: after round0's 249-0-1 as Blue, current `robot.py` swept the opponent 250-0 as Red. Combined result is 499 wins, 1 tie, 0 losses.
- `tools_analyze_logs.py` round1 summary: opponent/Blue averaged 4.60 units / 18.32 HP vs us/Red 19.40 units / 64.73 HP; all sims were Red wins. Round0's lone tie (`sim_30`) was already documented as a 10-10 unit ending with us slightly ahead on HP, and no repeated issue appeared in round1.
- Spot regression local seed 22 still beats builtin heuristic as both colors. I made no `robot.py` changes; given the near-sweep/full-sweep and long history of seed-sensitive tactical tweaks regressing, keeping the current black-magic-style planner plus narrow late-game tie fixes is safest.

Current round check vs mario31313__alpha_13 (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `mario31313__alpha_13` was Blue, gpt/current `robot.py` was Red, and current bot swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 4.19 units / 17.18 HP vs us/Red 19.64 units / 65.12 HP; worst unit margins were still very large (e.g. Red +17 or better in sampled worst cases), every sim was a Red win.
- Spot regression on seed 0 still beats builtin heuristic as both colors and remains competitive with builtin black-magic as both colors. No `robot.py` logic changes made; current fast black-magic-style one-ply planner is safely winning this matchup, and prior tactical tweaks often regressed, so stability remains recommended unless future logs show losses.

Round 2 follow-up vs mario31313__alpha_13 (current agent):
- Reviewed `/logs/rounds/1/results.json`: current `robot.py` swept again, this time as Blue vs `mario31313__alpha_13` Red, 250-0. Together with round0's Red sweep this matchup is clean in both colors.
- `tools_analyze_logs.py /logs/rounds/1` summary: avg final Blue/us 19.46 units / 64.56 HP vs Red/opponent 4.40 units / 17.81 HP; worst sampled final unit margins remained positive (e.g. 15-11, 13-9).
- No `robot.py` changes made. The current black-magic-style one-ply planner plus existing narrow late-game tie fixes is safely winning this opponent, and prior tactical tweaks have often been seed/color-sensitive regressions.

Current round check vs underscore__bot1 (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `underscore__bot1` was Blue, current `robot.py` was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 4.51 units / 18.28 HP vs us/Red 19.21 units / 63.90 HP; every sim was a Red win and sampled worst finals still had very large Red unit margins.
- Spot regression on seed 0 still beats builtin heuristic as both colors. No `robot.py` changes made; the current black-magic-style one-ply planner plus existing narrow late-game tie fixes is safely winning this matchup, so stability remains recommended unless later logs show actual losses.

Round 2 follow-up vs underscore__bot1 (current agent):
- Reviewed `/logs/rounds/1/results.json`: current `robot.py` swept again, this time as Blue vs `underscore__bot1` Red, 250-0. Combined with round0 Red sweep, the matchup is clean in both colors.
- `tools_analyze_logs.py /logs/rounds/1` summary: avg final Blue/us 19.65 units / 64.41 HP vs Red/opponent 4.54 units / 18.22 HP. Worst sampled finals still had positive unit margins and every sim was a Blue win.
- Spot regression local seed 14 still beats builtin heuristic as both colors (18-4 units as Blue, 19-6 as Red). No `robot.py` changes made; current black-magic-style planner plus the narrow late-game tie fixes remains safely winning, and prior tactical tweaks have often regressed.

Current round check vs lanity__sivuy (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `lanity__sivuy` was Blue, current `robot.py` was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 4.58 units / 18.69 HP vs us/Red 19.65 units / 65.80 HP; every sim was a Red win and sampled worst margins were still very large.
- Spot regression on seed 23 still beats builtin heuristic as both colors (Blue 21-6 units, Red 13-11 units in checked runs). No `robot.py` logic changes made; current black-magic-style planner plus narrow late-game tie fixes is safely winning this matchup, and prior tactical tweaks have often regressed.

Round 2 check vs lanity__sivuy (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` played as Red both times. Round0 was a 250-0 sweep; round1 was 247 wins, 2 ties, 1 loss for us.
- `tools_analyze_logs.py` margins: round0 avg opponent/Blue 4.58 units / 18.69 HP vs us/Red 19.65 units / 65.80 HP; round1 avg opponent/Blue 4.66 units / 18.99 HP vs us/Red 19.28 units / 64.22 HP. The few non-wins happened in late/post-spawn cluttered endgames (e.g. sim_90 Blue 12 units vs Red 10).
- I tested a late-game exact focus-fire override intended to convert adjacent kills after turn 90, but it regressed badly head-to-head versus the current bot, so it was reverted. Also retested current bot locally vs builtin heuristic on seeds 14/15 as both colors; it still wins comfortably.
- No `robot.py` logic changes made. Current black-magic-style planner is still overwhelmingly winning this matchup; previous and current tactical tweaks are risky/regressive, so stability remains safest.

Current round check vs mee42__follow-bot (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `mee42__follow-bot` was Blue, current `robot.py` was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 4.05 units / 16.20 HP vs us/Red 20.96 units / 72.53 HP; every sim was a Red win and sampled worst margins were still very large.
- Spot regression on seed 0 still beats builtin heuristic as both colors. No `robot.py` logic changes made; the current black-magic-style planner plus narrow late-game tie fixes is safely winning this matchup, and prior tactical tweaks have often regressed.

Round 2 follow-up vs mee42__follow-bot (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `mee42__follow-bot` 250-0 in both colors (round0 us Red, round1 us Blue).
- `tools_analyze_logs.py` margins are safe: round0 avg opponent/Blue 4.05 units / 16.20 HP vs us/Red 20.96 units / 72.53 HP; round1 avg us/Blue 20.60 units / 70.92 HP vs opponent/Red 4.17 units / 16.64 HP. Worst sampled final unit margin in round1 was still +4 units.
- No `robot.py` changes made. The current black-magic-style one-ply planner plus narrow late-game tie fixes is cleanly winning this opponent; prior tactical tweaks have often been seed/color-sensitive regressions, so stability remains safest unless future logs show losses.

Current round check vs anton__om-om (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: current `robot.py` was Blue vs `anton__om-om` Red and swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final Blue/us 19.22 units / 64.56 HP vs Red/opponent 4.39 units / 17.82 HP. Worst sampled unit margin was still positive (e.g. 14-11 in sim_14; all sims were Blue wins).
- Spot regression on seed 24 still beats builtin heuristic as both colors. No `robot.py` changes made; current black-magic-style planner plus narrow late-game tie fixes remains safely winning this matchup, and prior tactical tweaks have often regressed.

Round 2 follow-up vs anton__om-om (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current `robot.py` swept `anton__om-om` 250-0 in both recorded rounds; both logs list us as Blue.
- `tools_analyze_logs.py` margins: round0 avg Blue/us 19.22 units / 64.56 HP vs Red/opponent 4.39 units / 17.82 HP; round1 avg Blue/us 19.35 units / 64.92 HP vs Red/opponent 4.57 units / 18.59 HP. The worst sampled round1 final was still a Blue win at 9-7 units.
- Spot regression local seed 14 still beats builtin heuristic as both colors. No `robot.py` logic changes made; the current black-magic-style planner plus prior narrow late-game tie fixes is sweeping this opponent, and prior tactical experiments have often regressed, so stability remains safest.

Current round check vs aaoutkine__silo34 (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `aaoutkine__silo34` was Blue, current `robot.py` was Red, and we swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 8.72 units / 37.08 HP vs us/Red 27.66 units / 125.61 HP; every sim was a Red win and sampled margins were very large.
- Spot regression on seed 25 still beats builtin heuristic as both colors. No `robot.py` changes made; the current black-magic-style one-ply planner plus narrow late-game tie fixes is safely winning, and prior tactical tweaks have often regressed.

Round 2 check vs aaoutkine__silo34 (current agent):
- Reviewed `/logs/rounds/1/results.json`: after round0's 250-0 Red sweep, round1 had us Blue vs `aaoutkine__silo34` Red and scored 249-1-0. The lone loss was `sim_136`, final Blue/us 17 units / 85 HP vs Red/opponent 20 units / 92 HP.
- `tools_analyze_logs.py /logs/rounds/1` shows the overall margin is still huge: avg Blue/us 27.49 units / 125.46 HP vs Red/opponent 8.29 units / 35.50 HP; the next-worst sampled finals after sim_136 were still comfortable wins (e.g. 25-20, 20-11).
- Investigated the loss: it was a late/post-spawn swing around turns 90-100, not a broad tactical failure. I tested variants in `/tmp` (formula-based full spawn-ring avoidance, forced late spawn escape, and more aggressive scoring when behind after turn 85/95). These were seed/color-sensitive and often regressed head-to-head versus current `robot.py`, so none were adopted.
- No `robot.py` changes made. Current black-magic-style planner plus narrow late-game tie fixes remains overwhelmingly winning this matchup; only revisit if future rounds show repeated losses rather than a single outlier.

Round 2 check vs mountain__neuralbot4-3h (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current bot still wins the match but this is a noticeably stronger opponent than recent ones. Round0 as Red was 235-15; round1 as Blue was 235-12-3. Averages: round0 opponent/Blue 9.44 units / 34.24 HP vs us/Red 21.48 / 83.93; round1 us/Blue 22.13 / 87.06 vs opponent/Red 8.90 / 31.56.
- Losses/non-wins are late-game/post-spawn unit-count swings where the opponent keeps extra bodies; examples include round1 sim_140 ending us Blue 12 vs Red 19 and sim_175 15 vs 18.
- Made a narrow scoring tweak in `robot.py`: from turn >=60, if a candidate one-ply score is behind on unit count (`unit_score < 0`), score that branch with the original black-magic order `(unit, surround, health, distance)` instead of late HP-preservation tiers. Rationale: if a candidate is already losing on the only win condition, prefer pressure/surrounds to convert enemy units rather than merely preserve HP. Existing tied-unit late fixes remain unchanged.
- Spot tests after the tweak: still beats builtin heuristic both colors on seed0 (22-6 as Blue, 21-8 as Red). Versus builtin black-magic seed0 improved the current bot's Blue margin (19-15 instead of 13-12) but Red still lost; head-to-head with previous current bot over a few seeds was mixed but slightly promising, so this is a targeted risk for the observed neuralbot4 losses.

Current round check vs ketza__arthur (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `ketza__arthur` was Blue, gpt/current `robot.py` was Red, and current bot swept 250-0.
- `tools_analyze_logs.py /logs/rounds/0` summary: average final opponent/Blue 3.84 units / 15.13 HP vs us/Red 22.40 units / 77.59 HP; every sim was a Red win. This opponent leaves slightly more survivors than many prior opponents but the worst listed unit margins were still large and there were no close games.
- Spot regression on seed 0 still beats builtin heuristic as both colors. Versus builtin black-magic remains mixed/color-sensitive as documented (our bot as Blue won seed 0; as Red lost the mirror), with runtime about 2-3s/game.
- No `robot.py` changes made. The existing fast black-magic-style one-ply planner is safely sweeping this matchup, and prior README notes document many attempted tactical tweaks that regressed, so stability remains safest unless later logs show actual losses.

Round 2 current check vs ketza__arthur (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json` and `/logs/rounds/1/results.json`: current `robot.py` swept `ketza__arthur` 250-0 in both colors (round0 us Red, round1 us Blue).
- `tools_analyze_logs.py` margins: round0 avg opponent/Blue 3.84 units / 15.13 HP vs us/Red 22.40 units / 77.59 HP; round1 avg us/Blue 22.34 units / 77.71 HP vs opponent/Red 3.92 units / 15.38 HP. Worst sampled round1 game was still +4 units (13 vs 9).
- Inspected `robot.py`; it is the intended fast black-magic-style tactical planner. Given another two-color 250-0 sweep and prior notes that tactical tweaks often regress, I made no bot logic changes.

Current round check vs mkap__test (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: current `robot.py` was Blue vs `mkap__test` Red and won 248-2. This is the first recent matchup with recorded losses, but the overall margin is still large.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg Blue/us 16.35 units / 51.81 HP vs Red/opponent 5.40 units / 21.87 HP. The two losses were `sim_43` (7 vs 8 units) and `sim_249` (6 vs 10 units), both late/post-spawn unit-count swings; a few other sims were close but still Blue wins.
- Inspected `robot.py`; it is still the intended fast black-magic-style one-ply planner with prior late-game scoring tweaks. I tested a few local variants against the current bot/builtins (reverting to original black-magic scoring, removing the turn>=85 friendly-HP tier, and a more chase/pressure-heavy branch when behind after turn 90). Results were mixed or color-sensitive in head-to-head spot/batch tests, so I did not adopt them.
- No `robot.py` logic changes made. Future teammate should revisit only if later rounds show repeated losses; likely areas are late-game post-spawn body preservation/cleanup against scatter opponents.

Round 2 check vs mkap__test (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current bot was Blue both rounds and won the match but not a sweep (248-2 and 247-3). Average final margins were still positive (~16.3/16.8 Blue units vs ~5.4/5.3 Red units), but the few losses were late/post-turn-90 games after the final spawn where Red kept extra bodies (examples: round0 sim_249 6-10, sim_43 7-8; round1 sim_234 6-10, sim_105 11-13, sim_92 11-12).
- Made one narrow scoring change in `robot.py`: removed the turn>=85 `friend_health_score` priority. From turn>=60 the planner now uses `(unit_score, health_score, surround_score, distance_score)` for equal/non-losing one-ply branches, while preserving the existing special cases for losing branches and turn>=95 tied-unit cleanup. Rationale: against mkap__test, preserving our HP in the final turns seemed to let more enemy units survive; net HP/enemy damage is a better late tiebreaker.
- Spot regression after the change: still beats builtin heuristic as both colors on seeds 0 and 1; versus builtin black-magic it remains mixed but competitive and often slightly better on checked seeds (e.g. as Blue seed0 20-10 units; seed2 23-4). Runtime remains ~2-3s/game.
- Recommendation: next teammate should check whether this improves rounds 2+ versus mkap. If it regresses, restore the prior line `if CURRENT_TURN >= 85: return (unit_score, friend_health_score, health_score, surround_score, distance_score)` before the turn>=60 return.

Round 2 check vs essickmango__pickle-up (current agent):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current bot won both rounds but this opponent is much stronger than recent ones. Scores were 220-28-2 as Red (opponent Blue) and 223-26-1 as Blue (opponent Red). Averages: round0 opponent/Blue 4.22 units / 15.93 HP vs us/Red 21.21 / 77.97; round1 us/Blue 21.82 / 79.81 vs opponent/Red 3.78 / 14.28. Losses are still a minority but no longer rare.
- Loss examples (e.g. `/logs/rounds/1/sim_3.txt`) usually show us building a large unit lead by turn 90 but a few enemy bodies survive after the final spawn wave; prior late-game scoring tweaks remain relevant.
- Made one code change in `robot.py`: replaced the simplified black-magic `_tick` movement simulator with an engine-closer movement approximation. It now picks one mover per destination using N/E/S/W priority, cancels direct swaps, and rejects chains blocked by stationary/rejected units before resolving attacks. Rationale: the planner was overvaluing impossible/blocked moves in congested late fights, and this opponent's non-wins are mostly post-spawn clutter endgames.
- Spot regression: new exact-tick variant beat the prior current bot in head-to-head on seeds 0-5 as Blue every time and as Red on seeds 2/3/5 (seed 1/4 Blue side still won, seed 0 lost narrowly by units but won on HP/margin comparison). It still beats builtin heuristic as both colors on seed0 and is competitive/improved versus builtin black-magic seed0 (as Blue 20-10; black-magic-as-Blue matchup ended 15-9 for Blue). Runtime increased modestly to about 3s/game, still well under the 60s limit.

Current round check vs wolfsleuth__simple (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: opponent `wolfsleuth__simple` was Blue and current bot was Red. We are still winning overall but not sweeping: 241 Red/us wins, 8 Blue/opponent wins, 1 tie. This is a stronger/more awkward matchup than most recent "simple"-named bots.
- `tools_analyze_logs.py /logs/rounds/0` summary: avg final opponent/Blue 4.15 units / 15.02 HP vs us/Red 19.40 units / 49.76 HP. The losses are late turn-100 unit-count outcomes where Blue keeps ~10-13 units and Red ~7-8 in clustered/post-spawn positions.
- Made one narrow `robot.py` change: spawn-tile avoidance now applies only on turns 10,20,...,90 (`state.turn % 10 == 0 and state.turn < 100`), not turn 100. There is no spawn clear after the final action, so avoiding spawn tiles on the last action can unnecessarily block endgame kills/moves. This should be low risk and specifically targets turn-100 body-count endings.
- Spot regression: still beats builtin `heuristic-bot.js` as both colors on seeds 0,1,2. Head-to-head versus the pre-change bot on seeds 0-5 was mostly identical/color-split; the only observed difference was slightly favorable to the new version on seed 5 (new Red beat old Blue in one ordering, while new Blue vs old Red tied instead of changing the winner). Runtime remains around 2-3.5s/game.

Round 2 follow-up vs wolfsleuth__simple (current agent):
- Reviewed `/logs/rounds/1/results.json`: after the prior turn-100 spawn-avoidance relaxation, current `robot.py` improved from round0's 241-8-1 to 247 Red/us wins, 2 Blue/opponent wins, 1 tie (same colors: opponent Blue, us Red).
- `tools_analyze_logs.py /logs/rounds/1` summary: avg final opponent/Blue 3.98 units / 14.50 HP vs us/Red 19.75 units / 51.66 HP. The remaining non-wins were `sim_183` (Blue 10 vs Red 6), `sim_236` (13 vs 11), and `sim_232` tie (10-10); all are late/post-final-spawn unit-count outcomes despite us often leading earlier.
- I tested several small variants in `/tmp` (restoring friend-HP priority when already ahead after turn 90, changing losing-branch scoring after turn 95, modeling non-adjacent enemy chase moves, and forcing spawn evacuation). Head-to-head/local regression was mixed or worse, and some variants hurt heuristic/simple margins, so no `robot.py` logic change was adopted.
- Spot regression with current code still crushes builtin `simple-bot.js` as both colors on seeds 0-3. Recommendation: keep the current planner stable unless future logs show repeated losses; the round1 code change already cut losses substantially for this opponent.

Current round check vs gerenuk__gere-ape (gpt-5-5):
- Reviewed `/logs/rounds/0/results.json`: current bot was Blue vs `gerenuk__gere-ape` Red and won the match 152-88-10. This opponent is much stronger than recent sweep opponents; average final state from `tools_analyze_logs.py` was Blue/us 16.38 units / 56.58 HP vs Red/opponent 13.56 units / 42.54 HP.
- Losses are not isolated: many Red wins have Red keeping a large post-final-spawn unit count (worst examples include sim_63 ending 4-27 units and sim_208 ending 5-24). The final wave around turn 90 appears decisive in bad seeds; Blue often loses several bodies from turns 95-100 while Red remains spread/healthy.
- I tested several variants only in `/tmp` and did not adopt them: modeling greedy enemy non-adjacent moves, reverting to original black-magic scoring, health-first scoring, simple/original movement tick, forcing spawn escape, and removing the late losing-branch scoring. Head-to-head/local regression was mixed or worse versus current `robot.py` and/or builtin black-magic/heuristic, so changing the stable planner seemed too risky without round1 confirmation.
- No `robot.py` logic changes made. Future teammate should inspect round1: if losses repeat, likely improvement area is late/post-turn-90 body preservation and anti-scatter cleanup against this opponent; be careful because prior small late-game tweaks have often regressed across seeds/colors.

Round 2 check vs gerenuk__gere-ape (current agent):
- Reviewed `/logs/rounds/1/results.json`: current bot was Blue again and won 158-85-7, similar to round0's 152-88-10. This is a genuinely strong opponent; losses are not isolated, and average margins are only Blue/us 16.9 units / 59.3 HP vs Red/opponent 13.5 units / 42.3 HP.
- Loss inspection (e.g. round1 `sim_56`, `sim_211`, `sim_210`) shows we are often already behind on bodies from midgame onward, then the final spawn wave makes the unit deficit huge. Many losses are not just a turn-100 tiebreak issue.
- Made one narrow scoring tweak in `robot.py`: for turn >=80 one-ply branches that are already losing on unit count, use `(unit_score, surround_score, distance_score, health_score)` instead of `(unit_score, surround_score, health_score, distance_score)`. Rationale: when behind late, keeping contact/chasing scattered enemies should matter more than preserving HP, while unit count and surround/kill pressure remain primary. Early game and equal/ahead branches are unchanged.
- Spot regression: still beats builtin heuristic both colors on seed0. Versus previous `/tmp/robot_current.py`, head-to-head over seeds 0-5 was mixed but slightly favorable/no obvious disaster (new-as-Blue won 4, tied 1, lost 1 by units; new-as-Red won 4, tied 1, lost 1). Versus builtin black-magic remains mixed; seed0 Blue margin regressed somewhat but did not flip, seed1 unchanged. This is a targeted risk for the repeated gerenuk losses; if future logs worsen, revert the small turn>=80 losing-branch distance-before-health block.
