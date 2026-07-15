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

Round 1 current note (latest gpt-5-5):
- `/logs/rounds/0` shows current bot won all 250 sims as Blue, averaging ~36.3 units vs ~3.6. Opponent remains spawn/perimeter-stuck, so the evacuation/annulus macro is still the right plan.
- Made a small robustness fix in `robot.py`: replaced calls to `Coords.is_spawn()` with our own constant `SPAWN_SET`. The bundled Python stdlib defines `SPAWN_COORDS_STRINGS = map(str, SPAWN_COORDS)`, so repeated `is_spawn()` membership checks can consume the iterator and become unreliable. Local passive seed 1 improved from 37 to 39 surviving units while keeping strategy unchanged.
- Smoke tests after the fix: passive seed 1 wins as both colors (39-4 units); naive nearest-enemy chaser seeds 1-3 wins as both colors (e.g. Blue 33-0,25-5,30-1; Red 31-3,30-1,31-3). Runtime stayed ~2-3s/match.

Round 2 current note (this run vs navster8__bash-brothers):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`; both were 250/250 wins for us as Blue. `python3 analyze_logs.py` reports averages improving from ~36.3 to ~38.8 surviving Blue units while Red stays ~3-4 units. The opponent still appears spawn/perimeter-stuck and is wiped by the existing spawn-evacuation/annulus plan.
- Kept `robot.py` unchanged to avoid regressing a strategy that is already maxing the logged win rate.
- Smoke tests this session recreated `/tmp/passive.py` and `/tmp/chase.py`; current bot won as both Blue and Red on seeds 1-2, with ~36-39 units vs 4 and runtimes ~2.3-2.6s/match.

Round 1 current note (gpt-5-5 vs aaoutkine__dark-knight):
- Reviewed `/logs/rounds/0`: current bot won all 250 sims as Blue, averaging ~38.6 units vs ~6.0 for Red. Opponent still leaves many units on spawn/perimeter and is beaten decisively by spawn evacuation + annulus survival.
- Made one conservative safety tweak in `robot.py`: `best_step_toward()` now prefers non-spawn inward moves, using a spawn destination only as a last resort. This reduces any chance of pathing back onto clearable spawn tiles while preserving the existing macro.
- Smoke tests after tweak: passive seeds 1-3 still win as both colors (36-39 units vs 4); naive nearest-chaser seeds 1-3 still win as Blue (33-0,25-5,30-1) and Red for completed checks. Center/kite-ish local opponents also remained wins in checked seeds. Runtime remains a few seconds/match.

Round 2 current note (gpt-5-5 vs aaoutkine__dark-knight):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1` with `python3 analyze_logs.py`: current bot won all 500 sims (Blue 250/250 in r0, Red 250/250 in r1). Final unit averages were ~38.6-38.7 for us vs ~6.0-6.4 for opponent.
- Logs still show the opponent mostly stuck around spawn/perimeter; our spawn-evacuation + annulus survival plan remains decisive. Since the match score is already maxed, I left `robot.py` unchanged to avoid regression.
- Smoke tests this session: current bot still wins as both colors vs passive and naive chaser bots, and beats a simple spawn-evacuating chaser (`evac_chase`) decisively on seed 7 as both colors. Self-play remains mixed but acceptable; runtime ~5-6s/match, below limit.

Round 1 current note (gpt-5-5 vs mountain__neuralbot1-1h):
- Reviewed `/logs/rounds/0`: current bot won all 250 sims as Blue, averaging 38.72 units / 187.46 health vs Red 4.88 units / 18.78 health (`python3 analyze_logs.py`). Opponent still leaves many units on/near the spawn/perimeter; the existing spawn-evacuation + annulus survival macro remains decisive.
- Left `robot.py` unchanged to avoid regression because the logged win rate is already 250/250.
- Smoke tests this session: current bot still beats passive as both colors (seed 1: 39-4 units either side) and naive nearest-enemy chaser as both colors (seed 2: Blue 33-3, Red 30-2). Runtime per local match was about 2.6-4.3s, safely below the 60s limit.

Round 2 current note (gpt-5-5 vs mountain__neuralbot1-1h):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current bot won all 500 logged sims as Blue, scores 250-0 in both rounds. `python3 analyze_logs.py` shows ~38.6-38.7 surviving units / ~187 health for us vs ~4.9-5.3 units / ~19-21 health for Red.
- Opponent still appears spawn/perimeter-stuck; existing spawn-evacuation + defensive annulus + intercept micro is already maxing win count. I left `robot.py` unchanged to avoid unnecessary regression.
- Smoke tests this session: current bot still crushes passive as both colors (seed 1: 39-4 units either side) and beats naive nearest-enemy chaser as both colors (seed 2: Blue 25-5, Red 30-1). Runtime ~2.4-3.0s/match.

Round 1 current note (gpt-5-5 vs sivecano__clouded-mind):
- Reviewed `/logs/rounds/0`: our bot was Red and won all 250 sims, averaging 38.14 surviving units / 190.24 health vs Blue's 7.53 units / 36.45 health (`python3 analyze_logs.py`). Opponent moves more than old passive bots but still loses decisively to spawn evacuation + annulus survival.
- Left `robot.py` unchanged to avoid regression because the logged win rate is already 250/250.
- Smoke tests this session: current bot still crushes passive as both colors (seed 1: 39-4 units either side) and beats a naive nearest-enemy chaser as both colors (seed 2: Red 30-1 when our bot is Red; Blue 25-5 when our bot is Blue). Runtime ~2.6-3.2s/match.

Round 2 current note (gpt-5-5 vs sivecano__clouded-mind):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current bot won all 500 logged sims as Red, 250-0 each round. `python3 analyze_logs.py` shows Red averaging ~38.1-38.4 units / ~190-192 health vs Blue ~7.5 units / ~36 health.
- Opponent moves slightly but still fails to evacuate/contest enough; our spawn-evacuation + annulus survival + intercept micro remains decisively ahead. I left `robot.py` unchanged to avoid regression while win rate is already maxed.
- Quick smoke this session: self-play seed 1 completed in ~7.1s (Red 39 vs Blue 29 units), confirming runtime remains safely below 60s.

Round 1 current note (gpt-5-5 vs mountain__neuralbot2-6h):
- Reviewed `/logs/rounds/0`: our bot was Red and won all 250 sims, averaging 38.58 surviving units / 192.14 health vs Blue's 8.88 units / 33.79 health (`python3 analyze_logs.py`). The opponent moves somewhat but still loses decisively to spawn evacuation + defensive annulus survival.
- I left `robot.py` unchanged because the logged win rate is already 250/250 and past endgame/chase tweaks have risked self-play regressions without increasing match score.
- Smoke tests this session: current bot still crushes passive as both colors (seed 1: 39-4 units either side) and beats a naive nearest-enemy chaser as both colors (seed 2: Blue 25-5, Red 30-1). Runtime ~2.5-3s/match, safely below 60s.

Round 2 current note (gpt-5-5 vs mountain__neuralbot2-6h, this session):
- Checked `/logs/rounds/0` and `/logs/rounds/1`: our bot won all 500 logged sims (Red in r0, Blue in r1). `python3 analyze_logs.py` reports our side averaging about 38.3-38.6 units / 191-192 health vs opponent about 8.9-9.2 units / 34 health.
- Inspected a sample replay (`/logs/rounds/1/sim_0.txt`); opponent moves somewhat but still does not contest the spawn-clear/unit-count macro. Existing immediate spawn evacuation + defensive annulus + intercept micro remains decisive.
- I left `robot.py` unchanged this round to avoid regression. Current score is already maxed in logged rounds, and previous README notes show chase/endgame tweaks have sometimes hurt self-play without improving match score.

Round 1 current note (gpt-5-5 vs kalkin__artemis):
- Reviewed `/logs/rounds/0`: our current bot was Blue and won all 250 sims, averaging 38.78 surviving units / 183.73 health vs Red's 7.15 units / 26.60 health (`python3 analyze_logs.py`). Opponent moves somewhat but still does not preserve enough units against our immediate spawn evacuation + defensive annulus plan.
- I left `robot.py` unchanged. The logged win rate is already maxed, so changes aimed at chasing/killing the last few enemies would not improve score and could regress the robust survival macro.
- Smoke tests this session: current bot still crushes passive as both colors (seed 1: 39-4 units either side) and beats a naive nearest-enemy chaser as both colors (seed 2: Blue 33-1, Red 28-3). Self-play seed 1 completed in ~6s, under the limit.

Round 2 current note (gpt-5-5, this session vs kalkin__artemis):
- Re-ran `python3 analyze_logs.py`: `/logs/rounds/0` and `/logs/rounds/1` are both 250/250 wins for the current bot (Blue in r0, Red in r1), averaging about 38.8-38.9 surviving units vs about 7.1 opponent units.
- Sample replay `/logs/rounds/1/sim_0.txt` still shows the opponent leaving only a handful of units alive while our annulus/spawn-evacuation macro reaches ~40 units. No evidence of adaptation that would justify risky code changes.
- Left `robot.py` unchanged. Smoke check versus a passive local bot seed 1 still wins as both colors (39-4 units each side). The existing strategy is already maxing logged win rate; preserve it unless future logs show losses or close games.

Round 1 current note (gpt-5-5 vs kalkin__artemis2):
- Reviewed `/logs/rounds/0`: our current bot was Red and won all 250 sims, averaging 37.87 units / 169.17 health vs Blue's 4.54 units / 19.12 health (`python3 analyze_logs.py`). Sample replay still shows opponent ending with only a few units while our spawn-evacuation + annulus survival macro keeps ~39 units.
- I left `robot.py` unchanged. The logged win rate is already maxed at 250/250, so tactical changes aimed at killing the last stragglers are unnecessary and historically risk self-play regressions.
- Recommendation: keep preserving the immediate spawn evacuation and defensive annulus unless future logs show losses/close games or an opponent that consistently preserves reinforcements.

Round 2 current note (gpt-5-5 vs kalkin__artemis2, latest):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: our current bot was Red in both and won all 500 sims, 250-0 each round. `python3 analyze_logs.py` reports Red averaging ~37.7-37.9 surviving units / ~169 health vs Blue ~4.5 units / ~19 health.
- Opponent still loses to the established spawn-clear exploit: they preserve only a few units while our robots leave spawn immediately and hold the defensive annulus. No evidence of adaptation or close games.
- I left `robot.py` unchanged to avoid regression while win rate is already maxed. Smoke tests this session still win as both colors versus passive (seed 1: 39-4 units each side) and naive nearest-enemy chaser (seed 2: Blue 33-1, Red 27-3).

Round 1 current note (gpt-5-5 vs navster8__maginot-line):
- Reviewed `/logs/rounds/0` with `python3 analyze_logs.py`: current bot won all 250 sims as Blue, averaging 38.48 surviving units / 191.28 health vs Red's 11.67 units / 51.09 health.
- Sample replay `/logs/rounds/0/sim_0.txt` shows opponent preserves more units than older passive bots (often a wall/cluster on one side), but still loses decisively on unit count because our spawn-evacuation + defensive annulus keeps ~38-40 robots alive.
- Left `robot.py` unchanged. Since logged score is already 250/250, margin-improving chase/combat tweaks are unnecessary and risk regressing the proven survival macro.

Round 2 current note (gpt-5-5 vs navster8__maginot-line):
- Re-ran `python3 analyze_logs.py`: `/logs/rounds/0` and `/logs/rounds/1` are both 250/250 wins for the current bot, with us Blue in r0 and Red in r1. We average ~38.5 surviving units / ~191 health vs opponent ~11.6 units / ~51 health.
- Sample replay `/logs/rounds/1/sim_0.txt` shows the opponent preserves a larger side wall/cluster than older passive bots, but still loses badly on final unit count because our units evacuate spawn immediately and hold the defensive annulus.
- I left `robot.py` unchanged. The logged win rate is already maxed, and previous chase/combat margin tweaks have risked regressing the proven survival macro without increasing match score.

Round 1 current note (gpt-5-5 vs jiricodes__jiricodes-bot):
- Reviewed `/logs/rounds/0`: our current bot was Blue and won all 250 sims, averaging 37.73 surviving units / 186.87 health vs Red's 4.51 units / 16.30 health (`python3 analyze_logs.py`). Sample replay shows the opponent moving/attacking locally near the perimeter but still preserving only a handful of units while our spawn-evacuation + defensive annulus reaches ~38-40 robots.
- I left `robot.py` unchanged. The logged win rate is already 250/250, and prior notes show chase/endgame margin tweaks can regress self-play without increasing the match score.
- Smoke tests this session: current bot still crushes passive as both colors (seed 1: 39-4 units) and beats a naive nearest-enemy chaser as both colors (seed 2: 36-4 units). Runtime ~3-4s/match, safely below the 60s limit.

Round 2 current note (gpt-5-5 vs jiricodes__jiricodes-bot):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current bot won all 500 logged sims, Blue in r0 and Red in r1, 250-0 both rounds. `python3 analyze_logs.py` reports ~37.7-37.9 surviving units for us vs ~4.4-4.5 for opponent.
- Sample replay `/logs/rounds/1/sim_0.txt` shows the opponent actively moves/attacks nearest targets near the perimeter, but still preserves only a few units while our robots evacuate spawn and hold the annulus at ~38 units.
- Left `robot.py` unchanged. The win rate is already maxed and prior notes show chase/endgame/combat tweaks can regress the proven survival macro without increasing score.

Round 1 current note (gpt-5-5 vs sbasu3__meek-bot):
- Reviewed `/logs/rounds/0`: our current bot was Blue and won all 250 sims, averaging 36.15 surviving units / 153.44 health vs Red's 4.14 units / 16.02 health (`python3 analyze_logs.py`). Sample replay shows the opponent is still mostly spawn/perimeter-stuck and preserves only a few units while our spawn-evacuation + defensive annulus macro survives with ~31-40 units.
- I left `robot.py` unchanged. The logged win rate is already maxed at 250/250, and earlier notes show chase/endgame tweaks can regress the proven survival strategy without increasing score.
- Smoke tests this session still pass: current bot crushes a passive local bot as Blue (seed 1: 39-4 units) and beats a naive nearest-enemy chaser as both colors (seed 2: Blue 31-2 units, Red 31-2 units). Runtime ~2.4-2.9s/match.

Round 2 current note (gpt-5-5 vs sbasu3__meek-bot):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: current bot won all 500 logged sims, Blue in r0 and Red in r1, 250-0 both rounds. `python3 analyze_logs.py` reports ~36.2-36.3 surviving units for us vs ~4.1 for opponent.
- Opponent remains mostly spawn/perimeter-stuck and is beaten decisively by immediate spawn evacuation + defensive annulus + intercept micro. Since logged score is already maxed, I left `robot.py` unchanged to avoid regressing the proven survival macro.
- Smoke tests this session still pass: current bot beats passive as both colors (seed 1: 39-4 units) and naive nearest-enemy chaser as both colors (seed 2: Blue 25-5, Red 30-1). Runtime ~2.4-2.9s/match, well under 60s.

Round 1 current note (gpt-5-5 vs essickmango__fruity-test):
- Reviewed `/logs/rounds/0`: current bot was Blue and won all 250 sims, averaging 34.80 surviving units / 169.61 health vs Red's 15.37 units / 58.18 health (`python3 analyze_logs.py`). This opponent preserves more units than older passive bots, but still loses every game to our immediate spawn evacuation + defensive annulus survival plan.
- I left `robot.py` unchanged. The logged win rate is already maxed at 250/250; past README notes show chase/endgame/combat margin tweaks can regress the proven survival macro without improving match score.
- Smoke tests this session: current bot still crushes passive as Blue (seed 1: 39-4 units) and beats a naive nearest-enemy chaser as both colors (seed 2: Blue 33-1, Red 27-3). Runtime ~2.5-2.7s/match, safely below the 60s limit.

Round 2 current note (gpt-5-5 vs essickmango__fruity-test):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: our bot won 250/250 as Blue in r0, but as Red in r1 it went 249/250. The lone loss was `/logs/rounds/1/sim_4.txt`, a narrow endgame loss (Blue 25 units vs Red 24) after we had led 27-25 on turn 90 and then bled units in late trades.
- Made a very conservative late-game preservation tweak in `robot.py`: from turn 98 onward, if we have a unit-count lead and an adjacent attack is not a likely kill (`target.health > allies_on_target`), try to retreat; if no retreat exists, pass rather than taking a nonlethal trade. This only affects the last three turns and only while ahead, so the proven spawn-evacuation/annulus macro is unchanged.
- Smoke tests after the tweak: passive still loses hard (seed 1 Blue 39-4), naive chaser still loses (seed 2 Blue 25-5), and self-play/new-vs-previous on seeds 1-4 was essentially unchanged except seed 3 saved a few health. Runtime stayed ~2.7s vs simple bots and ~5s self-play.

Round 1 current note (gpt-5-5 vs tabaxi3k__charles):
- Reviewed `/logs/rounds/0`: current bot was Blue and went 249/250/1 tie. `python3 analyze_logs.py` reports Blue avg 32.95 units vs Red avg 17.73; the only non-win was `/logs/rounds/0/sim_138.txt`, a 28-28 tie. In that replay we led on units around turn 90 but bled down to equal units during late trades.
- Tightened the previous late-game preservation rule in `robot.py`: while ahead from turn 90 onward, nonlethal adjacent trades trigger retreat/pass (was only turn 98+). Added `kite_from_nearby()` so units with a lead also step away from nearby enemies in the final stretch if the move increases closest-threat distance. Spawn evacuation/annulus macro is unchanged.
- Smoke tests after edit: still crushes passive seed 1 (Blue 39-4) and beats naive nearest-chaser seed 2 as both colors (e.g. Blue 34-7, Red 28-3 before/after checks). New-vs-previous self-play on seed 138 was comparable (new as Red 30 vs old 32; new as Blue 32 vs old 29), but only partially tested due step/time limits. Watch future logs for possible late-game over-kiting/regressions.

Round 2 current note (gpt-5-5 vs tabaxi3k__charles):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`. Round 0 (before the latest late-game preservation tweak) was 249 wins + 1 tie; Round 1 with the current `robot.py` was 250/250 wins as Blue. `python3 analyze_logs.py` shows Round 1 Blue averaging 33.14 units vs Red 19.79, with the closest wins still +1 unit but no ties/losses.
- Kept `robot.py` unchanged. The current spawn-evacuation + defensive annulus strategy plus turn-90 lead-preservation/kiting fixed the prior tie without risking additional macro changes.
- Smoke tests this session: current bot still beats passive as both colors (seed 1: 39-4 units) and naive nearest-enemy chaser as both colors (seed 2: Blue 30-5, Red 31-7). Runtime remains about 2.5-3.1s versus simple bots, safely below the limit.

Round 1 current note (gpt-5-5 vs devchris__first_test):
- Reviewed `/logs/rounds/0`: current bot was Blue and won all 250 sims, averaging 33.33 units / 165.42 health vs Red's 20.50 units / 86.44 health (`python3 analyze_logs.py`). This opponent preserves substantially more units than older passive/spawn-stuck bots, with closest wins at +1 unit (`sim_109`, `sim_26`), but still lost every logged game.
- I inspected close replays; the existing turn-90 lead-preservation/kiting is relevant and appears to prevent late bleeding, while earlier/more aggressive kiting is risky (quick var80 self-play versus current bot was mixed/unfavorable). I left `robot.py` unchanged to preserve the proven 250/250 win rate.
- Recommendation for future rounds: if logs show ties/losses, focus on the close late-game cases around turns 90-100. Be cautious about widening the preservation trigger too much: equal-unit positions still need kills because equal units are ties, and prior chase/kite tweaks can regress self-play.

Round 2 current note (gpt-5-5 vs devchris__first_test):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: r0 was 250/250 wins as Blue, r1 was 249 wins + 1 tie. The tie was `/logs/rounds/1/sim_24.txt` (final 29-29 units). In that replay we led 29-25 on turn 87 and 32-29 after the final spawn, but bled units in late trades through turn 100.
- Made a small late-game preservation tweak in `robot.py`: the existing turn-90 lead-preservation/kiting still applies, and now also starts at turn 85 when we have a 2+ unit-count cushion. Equal/one-unit leads before 90 still fight normally so we can seek needed kills.
- Smoke tests after tweak: passive still loses as both colors (seeds 1/2/24/133 checked before timeout, ~36-39 vs 4); naive nearest chaser still loses as both colors seeds 1-3. New-vs-previous self-play on seeds 1-4 was identical/comparable to old-vs-old (no obvious regression; seed 4 remains a tie in one color ordering). Watch future logs for whether earlier kiting fixes the sim_24-style tie or over-kites.

Round 1 current note (gpt-5-5 vs aaa__jippty5):
- Reviewed `/logs/rounds/0`: our current bot was Red and won all 250 sims, averaging 37.10 surviving units / 183.34 health vs Blue's 16.08 units / 75.22 health (`python3 analyze_logs.py`). Closest final unit margin was still +11 (sim_99), so no close losses/ties to fix.
- Opponent preserves more units than older spawn-stuck bots but still loses decisively to immediate spawn evacuation + defensive annulus + late lead-preservation/kiting. I left `robot.py` unchanged to avoid regressing the proven 250/250 win rate.
- Smoke test this session: current bot still crushes a passive local bot as both colors on seed 1 (39-4 units, ~3s/match). Runtime remains safely below the 60s limit.

Round 2 current note (gpt-5-5 vs aaa__jippty5, latest):
- Reviewed `/logs/rounds/0` and `/logs/rounds/1`: our current bot was Red in both rounds and won all 500 logged sims, 250-0 each round. `python3 analyze_logs.py` reports Red averaging ~37.0-37.1 surviving units vs Blue ~16.1-16.4; closest margins were still comfortable (+11 in r0, +9 in r1).
- Because the logged win rate is already maxed and margins are not close, I left `robot.py` unchanged. The established immediate spawn evacuation + defensive annulus + late lead-preservation/kiting remains decisive against this opponent.
- Smoke tests this session still pass: passive seed 1 as Blue won 39-4 units; naive nearest-chaser seed 2 lost decisively in both color orders (our bot 36-4 units as Blue and as Red). Runtime stayed around 2.5-2.6s/match.
