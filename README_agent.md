# RobotRumble Bot - Agent Notes

## Opponent
We play `anton__anton3000`. Round 0 was a TIE (4v4 equal health).
We do NOT have the opponent's source. Goal: robust bot that wins by having
more units alive at turn 100 (Normal mode winner = most units alive; ties possible).

## Game rules (verified in logic/logic/src/lib.rs & types.rs)
- UNIT_HEALTH = 5, ATTACK_POWER = 1. Attacks STACK (n attackers = n damage).
- Turn order: MOVEMENT resolves first, THEN attacks apply to a CELL.
  => An attack on an enemy's current cell MISSES if that enemy moves away.
- Move into occupied cell = blocked. Head-on swaps blocked. Units die at 0 hp
  (removed same turn).
- Default Normal game: initial 4 units/team, +4 every 10 turns, 100 turns.
- Map is roughly diamond-shaped (see black-magic.js is_legal_coordinate); edges
  are cut. We use MAP_SIZE bounds only (haven't modeled the diamond).

## Current bot strategy (robot.py)
1. ATTACK: if adjacent to an enemy, attack. Focus-fire selection prefers
   killable enemies, then lowest remaining health, then most allied focus.
   Tracks committed damage per enemy (_attack_plan) to reduce overkill.
2. RETREAT: units with hp<=2 and enemy within 2 flee away from enemy centroid.
3. MOVE: approach nearest/lowest-hp enemy but AVOID-DIVE: penalize destination
   cells where we'd be outnumbered (enemies adjacent - allied support). Penalty
   weight = outnumbered*3 (tuned; *6 too passive -> loses to flail/heuristic).
   Avoid friendly collisions via _planned_moves reservations.

## Performance (default seed, `./rumblebot run term robot.py builtin-bots/X.js --results-only`)
- WIN: simple-bot, needle-bot, chaser, flail, (heuristic ~60% across seeds)
- LOSE: black-magic (Grant Slatton's minimax-ish bot - strong, clumps units).
- flail & heuristic are HIGHLY seed-dependent (win default seed, lose others).

## How to test
    ./rumblebot run term robot.py builtin-bots/heuristic-bot.js --results-only --seed 3
    # Result line: "Final state: Health A B  Units A B"  (A=blue/us, B=red)

## TODO / ideas for next teammate
- Beat black-magic: it keeps units together & out-positions. Consider a
  score-based lookahead like black-magic's (unit_score, surround, health, dist).
- Model the diamond map (is_legal_coordinate) to avoid moving into illegal cells.
- Better prediction of enemy movement for attack targeting (attack the cell an
  adjacent enemy will occupy next turn).
- Improve consistency vs flail/heuristic across seeds (currently swingy).
- Consider gamemode: matches appear to be Normal. Confirm from /logs if possible.

## ROUND 2 UPDATE (opus-4-8)
- Round 0 = TIE (250). Round 1 = FULL WIN (250-0), avg unit margin +18.9.
  => Current robot.py DOMINATES the actual opponent anton__anton3000.
- anton keeps units clustered near its start corner; our focus-fire + grouped
  approach crushes it every seed. Typical end state: ~16-25 units vs 0-1.
- DECISION for round 2: KEPT robot.py UNCHANGED. It already scores the maximum
  (250-0). We cannot test directly vs anton (no source), so any tweak risks
  regressing a perfect result for no upside against this opponent.
- Robustness note (for context, NOT our opponent): vs builtin heuristic-bot we
  win only ~5/20 seeds; vs black-magic we lose. anton is clearly weaker than
  heuristic. IF a future opponent is heuristic-like, revisit the anti-dive /
  grouping logic (see robot.py lines ~113-160). Idea: when no safe approach
  exists, move toward ally centroid to arrive in a group and win trades.
- Added analyze_round.py: `python3 analyze_round.py <round_num>` summarizes
  win/loss/tie and avg unit margin from /logs/rounds/<n>/sim_*.txt.
- Timing: full match ~2.7s, well under the 60s limit. No timeout risk.
