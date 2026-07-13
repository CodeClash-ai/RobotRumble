# Agent Notes — RobotRumble bot (opus team)

## Round history
- Round 0: TIE. Old bot (git HEAD) used a QUADRANT-based targeting scheme: units
  only chased enemies in the SAME quadrant, so corner-spawned units never engaged.
  Result: 250/250 sims ended 20-20 / 4v4 units with ZERO combat. Opponent
  (anton__anton3000) also stayed passive -> tie.

## Key game facts (verified in logic/logic/src/lib.rs & types.rs)
- **Winner = higher UNIT COUNT alive at end** (NOT total health!). See
  `determine_winner_from_units_count`. Ties -> Tie.
- UNIT_HEALTH = 5, ATTACK_POWER = 1 (so 5 hits to kill). Attack range = adjacent
  orthogonal tile (distance 1). Move = 1 orthogonal step.
- Grid 19x19 circle map. Units spawn at spawn ring.
- SpawnSettings default: initial 4, recurrent 4, spawn_every 10. => every 10 turns
  4 new units spawn per team; spawn tiles are cleared first (units standing there die).
- Match is 100 turns.

## Current strategy (robot.py)
Aggressive focus-fire, unit-count oriented:
1. Attack adjacent enemy with LOWEST health (secure kills), preferring shared focus target.
2. init_turn picks a global `focus_id` = lowest-health enemy nearest our cluster.
3. Move toward focus (or a much-closer enemy) using `choose_move` which AVOIDS
   tiles where 2+ enemies could hit us (anti-gang), and avoids friendly collisions
   via `planned` set.
4. Retreat units at health<=2 that can't secure a kill (preserve unit count).

## Results (run term, --results-only; stochastic seeds)
- vs simple-bot: crush (26-0)
- vs heuristic-bot: WIN (~15-11)
- vs chaser: ~tie/win (14-14)
- vs flail: ~tie (15-15)
- vs black-magic (strongest, full lookahead): usually lose but sometimes tie/win
- vs OLD passive bot: crush both colors (21-2, 12-0). Since anton TIED the old bot,
  we should beat anton decisively.

## How to test
    ./rumblebot run term robot.py builtin-bots/<bot>.js --results-only
    # old bot snapshot:  git show HEAD:robot.py > /tmp/old_robot.py
Timing ~1-2.5s per game, well under the 60s limit.

## Ideas for next teammate
- Beat black-magic: it does full-state lookahead scoring. Consider 1-ply lookahead
  for our own units (simulate attack outcomes), or better clustering to always
  fight outnumbered engagements in our favor.
- Consider defending spawn areas / controlling center since spawns replenish.
- Could tune the anti-gang threshold and retreat-health cutoff.
- The opponent's actual code isn't in the repo; only our logs of round outcomes.
