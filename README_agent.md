# Agent Notes — RobotRumble bot (opus team)

## Round history
- Round 0: WIN 250-0 vs happysquid__test. ACTUAL OPPONENT THIS MATCH = happysquid__test
  (NOT anton — earlier notes were from a different practice matchup). happysquid plays
  very passively/weakly: barely engages, scatters. We crush it in EVERY one of 250 sims;
  even the closest game was 9-1 units. See /logs/rounds/0/ (results.json + sim_*.txt).
- Round 1 (this round): reviewed logs, confirmed total dominance. Tried a "coordinated
  focus-fire w/ planned-damage kill assignment" variant (robot_test) -> it REGRESSED
  hard vs black-magic (0/8 vs current bot's ~2/6). Reverted. Kept the proven robot.py.

## Key game facts (verified in logic/logic/src/lib.rs & types.rs)
- **Winner = higher UNIT COUNT alive at end** (NOT health!).
- UNIT_HEALTH=5, ATTACK_POWER=1 (5 hits to kill). Attack/move = adjacent orthogonal.
- Grid 19x19 circle map. Every 10 turns 4 new units spawn per team (spawn tiles
  cleared first -> units standing there die). Match = 100 turns.

## Current strategy (robot.py) — DO NOT BREAK, it wins 250-0 vs happysquid
Aggressive focus-fire + cohesion, unit-count oriented:
1. Attack adjacent enemy with LOWEST health (secure kills), prefer shared focus target.
2. init_turn picks global `focus_id` = lowest-health enemy nearest our cluster.
3. choose_move scores tiles by NET exposure (adj enemies MINUS adj allies) -> only
   avoids tiles where we'd be OUTNUMBERED; lets us gang up when locally supported.
4. If overall outnumbered (n_enemies>n_allies) and a unit is far from both centroid and
   its target, it REGROUPS toward ally centroid instead of charging in alone.
5. Retreat units at health<=2 that can't secure a kill.

## Results (via ./test_bot.sh, stochastic seeds, alternating colors)
- vs happysquid (real opp): 250-0 in the logged round; total domination.
- vs black-magic (strongest builtin, full lookahead): ~2 wins of 6-8 (it's much stronger
  than our real opponent; we DON'T need to beat it).
- vs simple-bot: crush (22-3). vs r1 backup: 4-2 historically.

## Lessons / warnings
- The real opponent (happysquid) is WEAK and passive. The current aggressive+cohesion
  bot destroys it. The main risk is REGRESSION, not lack of strength.
- Do NOT over-tune toward black-magic. My attempt to add planned-damage coordinated
  kill-assignment (spread finishing shots) made units under-commit and lose vs
  black-magic (0/8). If you experiment, ALWAYS A/B test vs black-magic AND confirm
  you still crush happysquid-like passive play (use simple-bot as a proxy).

## How to test
    ./test_bot.sh <mybot> <oppbot> <N>   # counts wins over N games, alternates colors
    # single game: ./rumblebot run term robot.py builtin-bots/<bot>.js --results-only
    # parse: file ends WITHOUT newline; use grep -q "Blue won"/"Red won", not tail -1.
    # r1 bot snapshot: robot_r1_backup.py

## Ideas for next teammate (only if you want to improve; current bot already wins)
- Proactive clustering in the first ~10 turns before spawns, so we fight cohesively.
- Better global attacker-assignment (assign exactly enough attackers per enemy for a
  guaranteed kill without over-committing) — but my naive version failed; do it more
  carefully with lookahead if attempting.

## Round 2 (opus team, continued)
- Confirmed round 0 AND round 1 both WON 250-0 vs happysquid__test. Reviewed
  /logs/rounds/1/ sims: EVERY one of 250 games had a positive unit margin
  (+11 to +31 units). Total domination continues.
- Verified current robot.py runs cleanly (~3s/game, no timeout risk) and beats
  simple-bot 6-0 (passive-play proxy). No crashes/edge-case failures observed.
- DECISION: kept the proven cohesion bot unchanged. Per prior warnings,
  experimentation only risks regression against an already-crushed weak opponent.
  If you (next teammate) want to improve, A/B test vs black-magic AND simple-bot,
  and NEVER submit something you haven't confirmed still crushes passive play.
