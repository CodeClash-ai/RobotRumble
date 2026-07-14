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
