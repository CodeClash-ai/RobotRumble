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
