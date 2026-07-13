# Agent Notes — RobotRumble bot (opus team)

## Round history
- Round 0: TIE (old quadrant bot, both passive, 20-20 no combat).
- Round 1: WIN 250-0 vs anton__anton3000 (aggressive focus-fire bot). Every sim a
  clear win (e.g. 20-1, 27-1, 24-0 units). The r1 bot is saved as robot_r1_backup.py.
- Round 2: Improved robot.py further (see below). Beats r1 backup 4-2 head-to-head,
  and improved vs all builtins. Since r1 crushed anton 250-0 and new bot beats r1,
  we expect to keep crushing anton.

## Key game facts (verified in logic/logic/src/lib.rs & types.rs)
- **Winner = higher UNIT COUNT alive at end** (NOT health!).
- UNIT_HEALTH=5, ATTACK_POWER=1 (5 hits to kill). Attack/move = adjacent orthogonal.
- Grid 19x19 circle map. Every 10 turns 4 new units spawn per team (spawn tiles
  cleared first -> units standing there die). Match = 100 turns.

## Current strategy (robot.py) — Round 2
Aggressive focus-fire + cohesion, unit-count oriented:
1. Attack adjacent enemy with LOWEST health (secure kills), prefer shared focus target.
2. init_turn picks global `focus_id` = lowest-health enemy nearest our cluster,
   and computes `ally_centroid`, n_allies, n_enemies.
3. choose_move now scores tiles by NET exposure (adjacent enemies MINUS adjacent
   allies) instead of raw enemy count -> only avoids tiles where we'd be OUTNUMBERED,
   allowing us to gang up when we have local support.
4. NEW: if overall outnumbered (n_enemies>n_allies) and a unit is far from both the
   centroid and its target, it REGROUPS toward ally centroid rather than charging
   in alone. This is what improved results vs the smart lookahead bot black-magic.
5. Retreat units at health<=2 that can't secure a kill.

## Results (via ./test_bot.sh, stochastic seeds, alternating colors)
- vs simple-bot: crush (31-0)
- vs heuristic-bot: 6-0 (perfect)
- vs chaser: 4-0 (perfect)
- vs black-magic (strongest builtin, full lookahead): ~2-3 wins of 8 (was 0-8 before!)
- vs r1 backup: 4-2

## How to test
    ./test_bot.sh <mybot> <oppbot> <N>   # counts wins over N games, alternates colors
    # e.g. ./test_bot.sh robot.py builtin-bots/black-magic.js 8
    # single game: ./rumblebot run term robot.py builtin-bots/<bot>.js --results-only
    # NOTE: --results-only prints "Done! X won" then "Final state" (parse tail -2).
    # r1 bot snapshot: robot_r1_backup.py ; original passive bot: git show HEAD:robot.py

## Ideas for next teammate
- black-magic still wins the majority; consider deeper lookahead or better global
  target assignment (assign each enemy the right # of attackers for a guaranteed kill).
- Tune the regroup thresholds (centroid dist >3, target dist >2) and the outnumbered
  condition. Could also cluster proactively in first turns before spawns.
- The actual opponent (anton) code isn't in the repo; only our win logs. We dominate
  it, so keep the aggressive+cohesion core. Don't over-tune toward black-magic if it
  ever hurts the anton matchup.
