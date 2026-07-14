# Notes for teammates (Round 1 recap)

## What was wrong before
The starter `robot.py` used a Quadrant-based target-assignment strategy
(`init_turn` picks one enemy per quadrant). It had a serious bug: the
movement fallback logic (rotate_cw/rotate_ccw + `past_coords` anti-oscillation
check) could get **permanently stuck** returning `None` forever whenever both
rotation options were blocked (by a wall or unit) - and it never had a
"break the deadlock" fallback. This is visible in `/logs/rounds/0/sim_*.txt`:
health stays at "20 20" the *entire* 100-turn match in every single game -
i.e. our bot never landed a single attack. Confirmed by testing locally:
```
./rumblebot run term --results-only robot.py builtin-bots/nothing-bot.js
# old code -> TIE (never engages a totally stationary opponent!)
```

## What changed (this round)
Rewrote `robot.py` with a much simpler & robust per-unit greedy strategy:
- Target selection: prefer any enemy already adjacent (finish the kill,
  weakest health first); otherwise pick the enemy minimizing
  `(distance, health)` (i.e. closest first, weakest as tiebreak - this beat
  chaser.js better than health-first ordering, see below).
- Movement: order candidate directions as [direct, rotate_cw/ccw sorted by
  resulting distance, opposite], skip cells occupied by a wall/unit, and
  avoid immediately reversing the last move *unless* we've been stuck for
  2+ turns in a row (anti-oscillation with a guaranteed unstick fallback).
  Crucially: if literally everything is blocked we pass, but we never
  permanently "freeze" once an opening appears, and we track `stuck_turns`
  per-unit in a global `robot_state` dict.

## Local test results (`./rumblebot run term --results-only robot.py builtin-bots/X.js`)
(map/team sizes vary run-to-run since no `--seed`/map-size was pinned, so
treat these as directional signal, not exact numbers)

| Opponent            | Result             |
|----------------------|---------------------|
| nothing-bot.js       | WIN (was a TIE)     |
| simple-bot.js        | WIN (was a TIE)     |
| flail.js             | WIN (was a TIE)     |
| random-bot.js        | WIN                 |
| chaser.js            | WIN (was a LOSS)    |
| heuristic-bot.js     | WIN                 |
| needle-bot.js        | WIN                 |
| black-magic.js       | LOSS (still)        |

`black-magic.js` runs a 1-ply minimax-style search over joint actions with a
scoring function (unit count diff, surrounding/focus-fire potential, health,
distance) - it's a genuinely strong bot. If you have budget, look at
`builtin-bots/black-magic.js` for the scoring idea and consider porting a
similar lookahead/joint-action-search into `robot.py`'s `init_turn` (assign
actions for all our units at once, evaluate a heuristic on the resulting
state, keep the best). That is the most promising next improvement.

## Useful commands
```bash
# Quick 1-off match vs a builtin bot, results only:
./rumblebot run term --results-only robot.py builtin-bots/<name>.js

# Full battle logs printed to terminal:
./rumblebot run term robot.py builtin-bots/<name>.js
```

## Game facts learned from `logic/logic/src/lib.rs`
- `UNIT_HEALTH = 5`, `ATTACK_POWER = 1`, `HEAL_POWER = 1` (per hit).
  So a unit needs 5 successful attacks to die; focus fire matters a lot.
- Map is Circle-type (diamond shape rendered in ASCII) with `Wall` terrain
  objects along the border - `state.obj_by_coords(coords)` returns those
  too, so checking "is this cell occupied by *any* Obj" is the right way to
  detect both walls and units blocking a move.
- `/logs/rounds/0/results.json` shows Round 0 was a **Tie** vs
  `anton__anton3000` (0 vs 0 score) because of the movement-freeze bug above.

## Ideas for next round
1. Port a black-magic-style local search / lookahead scoring for `init_turn`
   to jointly plan our team's moves each turn instead of pure greedy-per-unit.
2. Add explicit "surround" bonus: prefer moving to squares that are adjacent
   to an enemy but where multiple allies can simultaneously reach an enemy to
   focus fire and kill it in 1 turn combo.
3. Consider fleeing/retreating low-health units instead of always attacking,
   to reduce losses.
4. Pin `--seed` when testing locally for reproducible A/B comparisons.

## Round 2 update
Replaced the pure greedy per-unit robot.py with a joint-action
coordinate-ascent planner in `init_turn` (mirrors `black-magic.js`'s
algorithm: score = (unit_diff, surround^2, health_diff, distance^2),
lexicographically maximized), computed once per turn for the whole team,
with `robot()` just looking up the precomputed action per unit id.
- Enemy baseline assumption: each enemy attacks the lowest-health adjacent
  friend (same heuristic black-magic.js uses for itself).
- Added a `cheap_mode` guard (when friends*enemies > 60) that restricts each
  unit's option set to just "attack if adjacent" + "step toward nearest
  enemy" + pass, instead of the full 8 move/attack directions, because the
  full search timed out badly (~19s/game) once our team ballooned to
  20-30 units against a passive opponent like nothing-bot.js over 100
  turns. PASSES is currently 1 (matches black-magic.js's single sweep) -
  if you have time budget, try raising to 2-3 for small-to-medium fights
  only (guard on unit count) since multi-pass coordinate ascent should
  find a better local optimum and previously looked promising before the
  timeout was discovered.
- **IMPORTANT - NOT FULLY RE-VALIDATED**: ran out of step budget this
  round to re-test the full builtin-bot suite (nothing/simple/flail/
  random/chaser/heuristic/needle/black-magic) after adding the cheap_mode
  perf guard. Only confirmed nothing-bot.js runs quickly now (previously
  9-19s, needs to be re-timed) and that robot.py parses/loads. **Next
  teammate: please re-run the full suite below before making further
  changes, and especially check black-magic.js (the one bot Round-1's
  greedy bot lost to) and timing on the biggest-unit-count matchups.**
```bash
for bot in nothing-bot.js simple-bot.js flail.js random-bot.js chaser.js heuristic-bot.js needle-bot.js black-magic.js; do
  echo "=== $bot ==="; timeout 60 ./rumblebot run term --results-only builtin-bots/$bot robot.py
done
```
- If the new planner turns out worse/slower than Round 1's greedy bot in
  your re-testing, Round 1's `robot.py` is preserved in git history /
  `/logs/edits/sonnet-5_r1.traj.json` and in this file's earlier section -
  reverting to greedy-per-unit is a safe fallback that is known to beat
  every builtin bot except black-magic.js.

## Round 3 update
Investigated why the Round 2 joint-action planner (`robot.py`) was losing to
`black-magic.js`, `flail.js`, and `needle-bot.js` despite the algorithm being
essentially a faithful port of black-magic.js's own coordinate-ascent search.

**Root cause found:** the `cheap_mode` performance guard added in Round 2
(`friends*enemies > 60` -> restrict each unit to only 1 candidate direction
instead of all 4 move + 4 attack dirs) was far too aggressive. Because units
recurrently spawn (4 more every 10 turns per side while spawn points remain
open, see `logic/logic/src/lib.rs` `spawn_units`), both teams routinely reach
10-15+ units by turn 30-40, so `friends*enemies` blows past 60 almost
immediately and the bot spends most of the match in the dumbed-down
"walk toward nearest enemy" mode - exactly when tactical play (target
selection, focus fire, avoiding bad trades) matters most. `black-magic.js`
has NO such guard and always does the full search, which is why it kept
beating us even though our scoring function and algorithm structure are
copied from it.

**Fix:** raised the `cheap_mode` threshold from 60 to 4000 (i.e. effectively
disabled under all normal circumstances on this map size, kept only as a
pathological-case safety net). Re-measured worst-case runtime with the full
search always on:
- self-play (`robot.py` vs `robot.py`, the scenario most likely to keep both
  team sizes large simultaneously for a long time): **~9s/game**
- vs every builtin bot that survives long enough to build up a big team
  (`simple-bot.js`, `heuristic-bot.js`, `chaser.js`, `random-bot.js`,
  `nothing-bot.js`): **~7-13s/game**

All comfortably under the 60s forfeit limit, so there was no need for the
guard to ever trigger in practice - the Round 2 threshold was just picked
too conservatively without re-timing after the surrounding code changed.

### Results after the fix (single runs, no `--seed` so treat as directional)
| Opponent            | Before (threshold=60) | After (threshold=4000) |
|----------------------|------------------------|--------------------------|
| nothing-bot.js       | WIN                    | WIN                      |
| simple-bot.js        | WIN                    | WIN                      |
| flail.js             | mixed (won/lost across runs) | WIN (multiple runs) |
| random-bot.js        | WIN                    | WIN                      |
| chaser.js             | WIN                   | WIN                      |
| heuristic-bot.js     | WIN                    | WIN                      |
| needle-bot.js        | mixed (won/lost)       | WIN (multiple runs)      |
| black-magic.js       | LOSS (badly, e.g. 1-51 health) | mostly WIN, occasional close loss (e.g. 27-28 health) - much improved, was previously a blowout loss every time |

### Notes / caveats for next teammate
- No `--seed` flag was used in any of this round's local testing (maps are
  randomized each run), so all win/loss tables above are directional signal
  from a handful of runs each, not statistically rigorous. If you have step
  budget, add `--seed` (check `./rumblebot run term --help` /
  `run batch --help` for exact flag support) and run e.g. 10-20 iterations
  per matchup for real win-rate numbers, especially for the still-competitive
  `black-magic.js` matchup.
- `black-magic.js` is still the toughest matchup (near coin-flip now, was a
  guaranteed loss before this fix). Ideas if you want to push further:
  1. Try `PASSES = 2` or `3` (currently 1) now that we know we have runtime
     budget to spare (~9s/game at PASSES=1, 60s limit) - multi-pass
     coordinate ascent should find a better local optimum than a single
     sweep, which is likely necessary to actually beat (not just tie) an
     opponent using the *same* single-sweep algorithm as us.
  2. `black-magic.js` uses a hardcoded diamond-map legality formula
     (`is_legal_coordinate`) instead of querying real terrain objects - if
     the actual generated map ever has irregular obstacles beyond the plain
     diamond border, our `_is_blocked` (which queries `state.obj_by_coords`
     for real) may have an edge/disadvantage there; not investigated further
     this round.
  3. Consider re-lowering `cheap_mode`'s threshold back down ONLY if future
     map-size/spawn-setting changes make unit counts grow much larger than
     what was measured here (double-check timing again after any such
     change - don't just trust this round's numbers forever).
