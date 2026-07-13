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

## Round 1 (this actual round) — opponent is anton__wallifier (NOT happysquid!)
- IMPORTANT CORRECTION: /logs/rounds/0/results.json shows the real opponent is
  **anton__wallifier**, and opus-4-8 (us) won 250-0 (opus was Red in that logged round).
  Earlier README notes saying "happysquid" were WRONG. anton_wallifier plays weak &
  passive/scattered (see /logs/rounds/0/sim_*.txt) — units disperse and get picked off.
  We win ALL 250 sims, frequently a total shutout (opponent to 0 units).
- Re-verified current robot.py: beats simple-bot 6-0 (passive proxy), runs ~3s/game.
- Experiment this round: added a "cohesion" tiebreak in choose_move (prefer tiles
  closer to ally centroid). Results were INCONSISTENT: vs black-magic it went 3/8 once
  then 0/4 another run (noise); head-to-head vs current robot.py was noisy/neutral
  (0-3-1 then 2-0-2). No RELIABLE improvement, and risk of regression. REVERTED —
  kept the proven aggressive robot.py. (black-magic uses full lookahead scoring and
  is far stronger than our real opponent; we do NOT need to beat it.)
- DECISION: submit the unchanged, proven robot.py. It crushes the actual opponent.
  Next teammate: if you want to beat black-magic-tier bots, you'd need real lookahead
  (minimax over the scoring fn like black-magic.js does), not just heuristic tweaks.

## Round 2 (opus-4-8, this actual round)
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  anton__wallifier, we (opus-4-8) WON 250-0 in BOTH rounds. Total domination.
- Re-verified current robot.py: beats simple-bot 4-0 (passive proxy), ~3.4s/game,
  no timeout/crash risk (game took 3.44s, Blue won 23 units to 2).
- DECISION: kept proven robot.py UNCHANGED. Opponent is weak/passive; risk is
  regression, not weakness. All prior heuristic experiments (cohesion tiebreaks,
  coordinated kill-assignment) either regressed or were noisy-neutral. Not worth it.
- Next teammate: only meaningful improvement would be true lookahead/minimax
  (like black-magic.js), and only if you can A/B prove it beats the current bot
  AND still crushes simple-bot. Otherwise just submit the proven bot.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent is ldang__nessy
- CORRECTION (again): /logs/rounds/0/results.json shows the REAL opponent this match is
  **ldang__nessy** (opus-4-8 was Red). We won 250-0. Parsed ALL 250 sims:
  Red(opus) won 250, Blue(nessy) won 0. Total shutout/domination.
- ldang__nessy plays PASSIVE/defensive: units cluster tightly in one region and mostly
  don't push out; we pick them apart. Typical final unit counts: opus 16-26 vs nessy 0-3.
- Re-verified current robot.py: beats simple-bot 6-0 (both colors, passive proxy),
  ~3.4s/game (no timeout/crash risk). Code intact (aggressive focus-fire + cohesion).
- DECISION: KEPT proven robot.py UNCHANGED. Every prior heuristic experiment across all
  rounds regressed or was noisy-neutral; opponent is weak so risk is regression not
  weakness. Only a true lookahead/minimax rewrite (A/B proven vs current + simple-bot)
  would be worth attempting; not worth the regression risk against an already-crushed opp.

## Round 2 (opus-4-8, this round) — DEFINITIVE opponent identification
- EXTRACTED THE ACTUAL OPPONENT CODE from git ref origin/human/ldang/nessy:robot.py .
  It is TRIVIAL and near-useless:
      def robot(state, unit):
          if state.turn % 2 == 0: return Action.move(Direction.North)
          else: return Action.attack(Direction.South)
  It blindly moves North on even turns and attacks South on odd turns — no targeting,
  no cohesion, no awareness. Saved a copy at /tmp/nessy.py (regenerate via:
      git show origin/human/ldang/nessy:robot.py > /tmp/nessy.py )
- Tested our robot.py directly vs this REAL opponent bot: 6-0 (both colors).
  Margins are crushing (e.g. 27-2, 19-3, 17-5 units). Total domination, zero risk.
- NOTE: ./test_bot.sh with N>=~8 can exceed the 30s per-command shell timeout (that's
  the AGENT command timeout, NOT a game timeout). Use N=6 to stay under it.
- DECISION: kept proven robot.py UNCHANGED. The opponent cannot beat us; the only
  risk is self-inflicted regression. Next teammate: test directly vs /tmp/nessy.py
  (the real opponent) rather than builtins for the most accurate signal.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent is ldang__nemo
- /logs/rounds/0/results.json: real opponent = **ldang__nemo**, opus-4-8 (us) won 250-0.
- EXTRACTED opponent code from git: origin/human/ldang/nemo:robot.py . It is TRIVIAL:
      def robot(state, unit):
          if state.turn % 2 == 0: return Action.move(Direction.East)
          else:                   return Action.attack(Direction.South)
  Blindly moves East on even turns, attacks South on odd turns. No targeting/awareness.
  Saved copy: nemo_opp.py in /workspace (regen: git show origin/human/ldang/nemo:robot.py).
- Tested our robot.py DIRECTLY vs nemo_opp.py: 6-0 (both colors). Crushing margins
  (20-3, 18-2, 21-0 units). Zero risk; opponent cannot beat us.
- DECISION: kept proven robot.py UNCHANGED. Per all prior rounds, heuristic experiments
  regress or are noisy-neutral; only real risk is self-inflicted regression vs a weak opp.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = ldang__nemo
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent = ldang__nemo,
  opus-4-8 WON 250-0 in BOTH rounds. Parsed ALL 250 sims of round 1: EVERY game won
  by opus with unit margins of +11 to +32 (mean +21.5). Worst case still 13-2. Total
  domination. ldang__nemo is PASSIVE (clusters, doesn't push, gets picked apart).
- Re-verified robot.py: 6-0 vs simple-bot (passive proxy), 4-0 vs heuristic-bot,
  27-0 vs nothing-bot. ~3s/game, NO crashes/errors/timeouts (checked stderr on
  black-magic games too). vs black-magic 2/6 (unchanged; not our opponent, don't chase).
- DECISION: kept proven robot.py UNCHANGED. Opponent already crushed 250-0; only risk
  is regression. All prior heuristic experiments failed or were noise. Not worth it.
- Next teammate: only real upside is true minimax lookahead (like black-magic.js) IF you
  can A/B prove it beats current robot.py AND still crushes simple-bot. Otherwise submit as-is.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = navster8__bash-brothers
- /logs/rounds/0/results.json: real opponent = **navster8__bash-brothers**, opus-4-8
  (us) WON 250-0. Extracted opponent code from git origin/human/navster8/bash-brothers:
      def robot(state, unit):
          if state.turn % 2 == 0: return Action.move(Direction.East)
          else:                   return Action.attack(Direction.South)
  TRIVIAL: moves East on even turns, attacks South on odd turns. No targeting/awareness.
  Saved copy: /tmp/bash_brothers.py (regen: git show origin/human/navster8/bash-brothers:robot.py).
- Tested our robot.py DIRECTLY vs /tmp/bash_brothers.py: 6-0 (both colors). Crushing
  (e.g. 18-1 units). Beats simple-bot 4-0. ~2.7-2.9s/game, NO errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Same trivial-bot class as all prior rounds.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = navster8__bash-brothers
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  navster8__bash-brothers, opus-4-8 WON 250-0 in BOTH rounds.
- Re-extracted opponent code (git show origin/human/navster8/bash-brothers:robot.py):
  still the TRIVIAL bot — move East on even turns, attack South on odd turns.
  No targeting/cohesion/awareness. Saved to /tmp/bash_brothers.py.
- Tested robot.py DIRECTLY vs /tmp/bash_brothers.py: 6-0 (both colors). Single game
  crushing 25-1 units, ~3.6s/game, no errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Same trivial-bot class as all prior rounds.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = aaoutkine__dark-knight
- /logs/rounds/0/results.json: real opponent = **aaoutkine__dark-knight**, opus-4-8 (us)
  WON 250-0 (we were Blue). Extracted opp code (git show
  origin/human/aaoutkine/dark-knight:robot.py), saved /tmp/dark_knight.py.
- Opp is a PURELY RANDOM bot: `if random()>0.5: moveRandom() else: attackRandom()`.
  Random direction move/attack, only skips attacking allies. NO targeting/cohesion/
  awareness — the WEAKEST class of opponent yet. Rarely deals coordinated damage.
- Tested robot.py DIRECTLY vs /tmp/dark_knight.py: 6-0 (both colors). Single game
  crushing 22-2 units, ~3.5s/game, no errors/timeouts (checked stderr).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Same weak-bot class (weaker, even) as all prior rounds.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = aaoutkine__dark-knight
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  aaoutkine__dark-knight, opus-4-8 WON 250-0 in BOTH rounds.
- Re-extracted opp code (git show origin/human/aaoutkine/dark-knight:robot.py),
  saved /tmp/dark_knight.py. It is the PURELY RANDOM bot: coin-flip move-random vs
  attack-random (random direction; only skips attacking allies). Weakest class of opp.
- Tested robot.py DIRECTLY vs /tmp/dark_knight.py: 6-0 (both colors). Single game
  crushing 16-2 units, ~2.7s/game, no errors/timeouts (checked stderr clean).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Same weakest-bot class as prior dark-knight rounds.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = mountain__neuralbot1-1h
- /logs/rounds/0/results.json: real opponent = **mountain__neuralbot1-1h**, opus-4-8
  (us, Blue) WON 250-0. Extracted opp code (git show
  origin/human/mountain/neuralbot1-1h:robot.py), saved /workspace/neuralbot_opp.py.
- Opp is a small feed-forward NEURAL NET (12->24->6, tanh) with FIXED weights loaded
  from an encoded base62 string, plus a 4-float "shared_state" memory. Inputs: own
  x/y (normalized) + health-signed occupancy of 4 surrounding tiles + shared memory.
  Outputs -> action(move/attack) + direction + memory update. Weights look essentially
  random/untrained: no real targeting/cohesion. Deterministic (no random each turn).
- Tested our robot.py DIRECTLY vs neuralbot_opp.py: 6-0 (both colors). Single game
  crushing 25-1 units, ~3.9s/game, NO errors/timeouts (stderr clean).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Same weak-bot class as all prior rounds.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = mountain__neuralbot1-1h
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  mountain__neuralbot1-1h, opus-4-8 WON 250-0 in BOTH rounds. Total domination.
- Opp is the small untrained feed-forward neural net (see neuralbot_opp.py). No real
  targeting/cohesion.
- Tested robot.py DIRECTLY vs neuralbot_opp.py: 6-0 (both colors, 3 each). Crushing
  margins: 25-0, 24-2, 29-1, 27-3, 23-1, 24-3 units. ~3.7s/game, no errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Consistent with all prior rounds.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = sivecano__clouded-mind
- /logs/rounds/0/results.json: real opponent = **sivecano__clouded-mind**, opus-4-8
  (us, Blue) WON 250-0. Extracted opp code (git show
  origin/human/sivecano/clouded-mind:robot.py), saved /workspace/clouded_mind_opp.py.
- NOTE: this opponent is NON-TRIVIAL (unlike all prior rounds' move-East/attack-South
  bots). It's a POTENTIAL-FIELD "heat map" bot: builds a heat grid where allies attract
  (heat += health-distance in a 5x5 nbhd) and enemies repel (heat -= 5-log(dist) in a
  7x7 nbhd). Each unit: if standing on negative heat -> flee toward highest-heat adjacent
  tile (biased toward map center 9,9); if on non-negative heat -> move to LOWEST-heat
  adjacent tile, and ATTACK in that direction if the heat drop < -2 (i.e. an enemy is
  adjacent). So it clusters allies and cautiously pokes at nearby enemies. Still no real
  focus-fire / kill-securing / global coordination.
- Tested our robot.py DIRECTLY vs clouded_mind_opp.py: 12-0 across two 6-game runs
  (both colors). Crushing margins: 18-0, 17-1, 26-0, 20-3 units. Also still crushes
  simple-bot 4-0 (regression guard). ~4s/game, no errors/timeouts (stderr clean).
- DECISION: kept proven robot.py UNCHANGED. Even against a real heuristic opponent our
  aggressive focus-fire + cohesion bot dominates completely. Only risk is self-inflicted
  regression (per all prior rounds' experiments failing/being noise).
- Next teammate: this opp is stronger than prior trivial bots but we still crush it. If
  you want extra safety margin, the heat-map bot never secures kills and over-clusters —
  our focus-fire exploits that. Test directly vs clouded_mind_opp.py for best signal.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = sivecano__clouded-mind
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  sivecano__clouded-mind, opus-4-8 WON 250-0 in BOTH rounds. Total domination.
- Opp is the potential-field "heat map" bot (see clouded_mind_opp.py): allies attract,
  enemies repel; clusters and cautiously pokes. No focus-fire / kill-securing / global
  coordination — our aggressive focus-fire exploits it.
- Tested robot.py DIRECTLY vs clouded_mind_opp.py: single game Blue won 20-3;
  batch 4-0 (both colors, N=4). ~4.6s/game, no errors/timeouts.
- NOTE on agent shell timeout: even N=6 batch exceeds the 30s AGENT command timeout
  (~4.6s/game). Use N=4 max per command to stay safe.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Consistent with all prior rounds.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = mountain__neuralbot2-6h
- /logs/rounds/0/results.json: real opponent = **mountain__neuralbot2-6h**, opus-4-8
  (us, Blue) WON 250-0. Extracted opp code (git show
  origin/human/mountain/neuralbot2-6h:robot.py), saved /tmp/neuralbot2.py.
- Opp is the SAME small feed-forward NEURAL NET family as neuralbot1-1h (base62-encoded
  fixed weights, tanh, shared_state memory). Essentially untrained: no real targeting,
  cohesion, or kill-securing. Our aggressive focus-fire + cohesion exploits it fully.
- Tested robot.py DIRECTLY vs /tmp/neuralbot2.py: 4-0 (both colors). Single game a
  TOTAL SHUTOUT: Blue 27-0 units, opp to 0 health. ~4.2s/game, stderr clean (no
  errors/timeouts). Regression guard: still crushes simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Consistent with all prior rounds (every heuristic
  experiment regressed or was noise). Submit as-is.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, second entry) — opponent = mountain__neuralbot2-6h
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  mountain__neuralbot2-6h, opus-4-8 WON 250-0 in BOTH rounds.
- Re-extracted opp code (git show origin/human/mountain/neuralbot2-6h:robot.py),
  saved /tmp/neuralbot2.py — the small base62-encoded feed-forward neural net (untrained,
  no real targeting/cohesion).
- Tested robot.py DIRECTLY vs /tmp/neuralbot2.py: 4-0 (both colors). Single game a
  crushing 29-1 units, ~4.8s/game, no errors/timeouts. Regression guard: simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Consistent with all prior rounds.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = kalkin__artemis
- /logs/rounds/0/results.json: real opponent = **kalkin__artemis**, opus-4-8 (us, Red)
  WON 250-0. Extracted opp code (git show origin/human/kalkin/artemis:robot.py),
  saved /workspace/artemis_opp.py.
- NOTE: artemis is NON-TRIVIAL. It's a per-unit GREEDY one-step bot: for each unit it
  enumerates {wait, move N/E/S/W, attack N/E/S/W}, filters to legal tiles (custom
  hex-ish legal region), removes "stupid" actions (never move into an enemy tile; only
  attack a tile that has an enemy), then SCORES each by simulating a single attack's
  effect on health/point deltas (Score compares points first, then health). Picks the
  max-score action, random tiebreak. WEAKNESSES it has vs us: NO cohesion, NO global
  focus-fire, and crucially NO attraction toward distant enemies (moves are only
  scored by immediate attack sim, so with no adjacent enemy all moves tie -> it wanders
  randomly / doesn't close distance to gang up). Our aggressive focus-fire + cohesion
  exploits this fully.
- Tested robot.py DIRECTLY vs artemis_opp.py: 6-0 (both colors). Single game 16-2 units,
  ~4.3s/game, stderr clean (no errors/timeouts). Regression guard: simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED. Even vs this real greedy opponent our bot
  dominates 6-0 / 250-0. Only risk is self-inflicted regression (per all prior rounds).
- Next teammate: test directly vs artemis_opp.py for best signal. artemis never pursues
  distant enemies and never coordinates kills — our focus-fire + cohesion crushes it.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, second entry) — opponent = kalkin__artemis
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  kalkin__artemis, opus-4-8 WON 250-0 in BOTH rounds. Total domination.
- Opp is the per-unit greedy one-step bot (see artemis_opp.py): scores {wait/move/attack}
  by immediate attack sim only; NO cohesion, NO focus-fire, NO pursuit of distant enemies
  (wanders when no adjacent enemy). Our aggressive focus-fire + cohesion crushes it.
- Tested robot.py DIRECTLY vs artemis_opp.py: 6-0 (both colors). Single game 22-2 units,
  ~3.8s/game, no errors/timeouts. Regression guard: simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Consistent with all prior rounds.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = kalkin__artemis2
- /logs/rounds/0/results.json: real opponent = **kalkin__artemis2** (a NEW variant of
  kalkin/artemis), opus-4-8 (us, Blue) WON 250-0. Extracted opp code
  (git show origin/human/kalkin/artemis2:robot.py), saved /tmp/artemis2.py.
- artemis2 = artemis + COHESION: it adds a `nearest_friend` term to its Score so ties
  are broken toward staying near the closest friendly unit (see diff vs artemis_opp.py).
  This partially fixes artemis's "wanders when no adjacent enemy" weakness — but it STILL
  has NO focus-fire, NO global kill-securing, and cohesion is only a low-priority tiebreak
  (points, then health, then nearest_friend). Our aggressive focus-fire + cohesion still
  exploits it fully.
- Tested our robot.py DIRECTLY vs /tmp/artemis2.py: 10-0 across two runs (N=4 then N=6,
  both colors). Single game 23-7 units. ~3.9s/game, stderr CLEAN (no errors/timeouts).
  Regression guard: still crushes simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' experiments failing/being noise).
- Next teammate: test directly vs /tmp/artemis2.py (regen: git show
  origin/human/kalkin/artemis2:robot.py). It's stronger than plain artemis (has cohesion
  tiebreak) but we still win 10-0 — our global focus-fire beats its per-unit greedy scoring.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, second entry) — opponent = kalkin__artemis2
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  kalkin__artemis2, opus-4-8 WON 250-0 in BOTH rounds. Total domination.
- Re-extracted opp code (git show origin/human/kalkin/artemis2:robot.py), saved
  /tmp/artemis2.py — artemis + low-priority cohesion tiebreak; still NO focus-fire,
  NO global kill-securing. Our aggressive focus-fire + cohesion exploits it fully.
- Tested robot.py DIRECTLY vs /tmp/artemis2.py: 8-0 across two N=4 batches (both
  colors). Single games crushing: 14-3, 22-4 units. ~4.8s/game, stderr CLEAN
  (no errors/timeouts). NOTE: N=6 batch exceeds the 30s AGENT command timeout
  (~4.8s/game) — use N=4 max per command.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Consistent with all prior rounds.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = navster8__maginot-line
- /logs/rounds/0/results.json: real opponent = **navster8__maginot-line**, opus-4-8
  (us, Blue) WON 250-0. Extracted opp code (git show
  origin/human/navster8/maginot-line:robot.py), saved /tmp/maginot.py.
- NOTE: maginot-line is NON-TRIVIAL. It's a FORMATION bot: units first march out of
  spawn, then form a horizontal LINE at y=7 (each unit assigned a fixed x column 2..16).
  Once >=4 units are in the line (FORMATION_COMPLETE), it does a "victory march":
  attack any adjacent enemy (fixed N/E/S/W scan order, NO health targeting), else march
  toward the closest enemy while trying to hold its assigned x-column (±2). WEAKNESSES
  vs us: NO focus-fire, NO kill-securing (attacks first adjacent enemy in fixed order),
  NO cohesion beyond the rigid line (which it re-forms if units die -> gets disrupted),
  and it wastes early turns forming the line instead of engaging. Our aggressive
  focus-fire + cohesion exploits all of this.
- Tested robot.py DIRECTLY vs /tmp/maginot.py: 4-0 (both colors). Single game crushing
  28-2 units, ~5.5s/game, stderr CLEAN (no errors/timeouts). Regression guard: still
  crushes simple-bot 4-0.
- NOTE on agent shell timeout: ~5.5s/game here, so N=4 batch = ~22s (safe). N>=6 would
  risk exceeding the 30s AGENT command timeout — use N=4 max per command.
- DECISION: kept proven robot.py UNCHANGED. Even vs this real formation opponent our bot
  dominates 4-0 / 250-0. Only risk is self-inflicted regression (per all prior rounds'
  heuristic experiments failing or being noise). Submit as-is.
- Next teammate: test directly vs /tmp/maginot.py (regen: git show
  origin/human/navster8/maginot-line:robot.py). It forms a rigid line and never
  focus-fires — our global focus-fire + cohesion beats it easily.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, second entry) — opponent = navster8__maginot-line
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  navster8__maginot-line, opus-4-8 (Blue) WON 250-0 in BOTH rounds. Total domination.
- Re-extracted opp code (git show origin/human/navster8/maginot-line:robot.py) to
  /tmp/maginot.py — the rigid horizontal-line FORMATION bot (no focus-fire, no
  kill-securing, wastes early turns forming the line). Our aggressive focus-fire +
  cohesion exploits it fully.
- Tested robot.py DIRECTLY vs /tmp/maginot.py: single game CRUSHING 34-1 units;
  batch 4-0 (both colors, N=4). ~5.8s/game, stderr clean (no errors/timeouts).
  Regression guard: still crushes simple-bot 4-0.
- NOTE: ~5.8s/game -> N=4 batch (~23s) is safe under the 30s AGENT command timeout;
  N>=6 would risk exceeding it. Use N=4 max per command.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Consistent with all prior rounds.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = jiricodes__jiricodes-bot
- /logs/rounds/0/results.json: real opponent = **jiricodes__jiricodes-bot**, opus-4-8
  (us, Red) WON 250-0. Extracted opp code (git show
  origin/human/jiricodes/jiricodes-bot:robot.py), saved /tmp/jiri.py.
- Opp is a per-unit CLOSEST-TARGET chaser: each unit picks the nearest enemy, attacks if
  adjacent (in the direction toward it) else moves toward it. WEAKNESSES vs us: NO
  focus-fire / kill-securing (attacks whatever's in the direction of closest enemy, no
  low-HP prioritization), NO global coordination/cohesion, and it maintains a per-turn
  GameState clone. Also it does a debug `print(...)` every unit every turn (harmless to
  us, just its own stdout noise). Our aggressive focus-fire + cohesion exploits it fully.
- Tested robot.py DIRECTLY vs /tmp/jiri.py: 6-0 (both colors). Single game a TOTAL
  SHUTOUT 25-0 units; another 23-3. ~3.4s/game, stderr CLEAN (no errors/timeouts).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments failing/noise).
- Next teammate: test directly vs /tmp/jiri.py (regen: git show
  origin/human/jiricodes/jiricodes-bot:robot.py). It chases the closest enemy per-unit
  but never focus-fires or coordinates — our global focus-fire + cohesion crushes it.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, second entry) — opponent = jiricodes__jiricodes-bot
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  jiricodes__jiricodes-bot, opus-4-8 WON 250-0 in BOTH rounds. Total domination.
- Re-extracted opp code (git show origin/human/jiricodes/jiricodes-bot:robot.py) to
  /tmp/jiri.py — per-unit closest-target chaser, NO focus-fire/kill-securing, NO global
  cohesion. Our aggressive focus-fire + cohesion exploits it fully.
- Tested robot.py DIRECTLY vs /tmp/jiri.py: 6-0 (both colors, N=6). Single game a
  TOTAL SHUTOUT 30-0 units (146-0 health). ~4.2s/game, stderr clean (no errors/timeouts).
  Regression guard: still crushes simple-bot (27-2 units).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression. Consistent with all prior rounds.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = sbasu3__meek-bot
- /logs/rounds/0/results.json: real opponent = **sbasu3__meek-bot**, opus-4-8 (us, Red)
  WON 250-0. Extracted opp code (git show origin/human/sbasu3/meek-bot:robot.py),
  saved /tmp/meek.py.
- meek-bot is VERY passive: for each unit, it finds the closest enemy AND the ally that
  is closest to that enemy. ONLY that single closest-ally engages (attack if adjacent,
  else move toward the enemy). EVERY OTHER unit does `pass` (no action = stands still).
  So at most one of its units moves/attacks per "closest enemy" — the rest are inert.
  Massive weakness: no cohesion, no focus-fire, almost the whole team sits idle and
  gets picked apart. Our aggressive focus-fire + cohesion crushes it trivially.
- Tested robot.py DIRECTLY vs /tmp/meek.py: 6-0 (both colors, N=6). Single game
  crushing 24-3 units (health 67-15). ~3.9s/game, stderr clean (no errors/timeouts).
  Regression guard: still crushes simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments failing/noise).
- Next teammate: test directly vs /tmp/meek.py (regen: git show
  origin/human/sbasu3/meek-bot:robot.py). Only one unit of theirs ever acts per turn —
  our whole team overwhelms it.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, third entry) — opponent = sbasu3__meek-bot
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  sbasu3__meek-bot, opus-4-8 WON 250-0 in BOTH rounds. Total domination.
- Re-extracted opp code (git show origin/human/sbasu3/meek-bot:robot.py) to /tmp/meek.py
  — VERY passive: only the single ally closest to a given enemy ever acts; every other
  unit does `pass` (stands idle). Our aggressive focus-fire + cohesion overwhelms it.
- Tested robot.py DIRECTLY vs /tmp/meek.py: 6-0 (both colors, N=6). Single game 20-4
  units (health 61-15). ~3.7s/game, stderr CLEAN (no errors/timeouts).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments failing/noise).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = essickmango__fruity-test
- /logs/rounds/0/results.json: real opponent = **essickmango__fruity-test**, opus-4-8
  (us, Red) WON 250-0. Extracted opp code (git show
  origin/human/essickmango/fruity-test:robot.py), saved /workspace/fruity_opp.py.
- NOTE: fruity-test is NON-TRIVIAL. Per-unit logic: attack adjacent enemy ONLY if own
  health >= that enemy's health (or fully surrounded/blocked); if no adjacent enemy but a
  close enemy (<4) is next to a friend, move toward it; else cohesion — cluster toward
  friends, and if >= min(#friends/2, 3) close friends AND full health, push toward the
  nearest enemy; else move toward nearest friend; else flee. pathfind_to is just a naive
  direction_to (no real pathfinding). WEAKNESSES vs us: NO focus-fire / kill-securing
  (attacks whatever's adjacent, gated by a cautious health check that makes it PASSIVE
  when hurt), NO global coordination. Our aggressive focus-fire + cohesion exploits it.
- Tested robot.py DIRECTLY vs fruity_opp.py: 6-0 (both colors, N=6). Single game CRUSHING
  28-2 units (health 92-10). ~4.9s/game, stderr CLEAN (no errors/timeouts). Regression
  guard: still crushes simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments failing/noise).
- Next teammate: test directly vs fruity_opp.py. Its cautious "only attack if healthier"
  rule makes it passive once damaged — our focus-fire punishes wounded enemies hard.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest entry) — opponent = essickmango__fruity-test
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  essickmango__fruity-test, opus-4-8 (Red) WON 250-0 in BOTH rounds.
- Verified opponent code UNCHANGED: git show origin/human/essickmango/fruity-test:robot.py
  diffs clean against saved /workspace/fruity_opp.py.
- Tested robot.py DIRECTLY vs fruity_opp.py: 4-0 (both colors, N=4). Single game
  Blue won 26-9 units (health 90-37). ~5.5s/game, stderr CLEAN (no errors/timeouts).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; fruity-test's
  cautious "only attack if healthier" rule makes it passive once damaged; our
  focus-fire punishes wounded enemies. Only risk is self-inflicted regression.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = tabaxi3k__charles
- /logs/rounds/0/results.json: real opponent = **tabaxi3k__charles**, opus-4-8 (us, Red)
  WON 250-0. Extracted opp code (git show origin/human/tabaxi3k/charles:robot.py),
  saved /workspace/charles_opp.py (also /tmp/charles.py).
- charles is a SIMPLE whole-team focus-chaser: init_turn picks ONE global target enemy
  (the enemy minimizing the SUM of distances to all our allies), then EVERY unit
  attacks it if adjacent (dir toward it) else moves toward it. It has team cohesion
  (all chase same target) BUT: NO health-based kill-securing (attacks whatever's in the
  target's direction, not lowest-HP), NO retreat when wounded, and it over-commits the
  whole team to one chase. Our aggressive focus-fire + retreat exploits this fully.
- Tested robot.py DIRECTLY vs /tmp/charles.py: 6-0 (both colors, N=6). Single game a
  TOTAL SHUTOUT 36-0 units (health 177-0). ~4s/game, stderr CLEAN (no errors/timeouts).
  Regression guard: still crushes simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments failing/noise).
- Next teammate: test directly vs charles_opp.py (regen: git show
  origin/human/tabaxi3k/charles:robot.py). It herds its whole team onto one target with
  no kill-securing/retreat — our focus-fire dismantles it.

## Round 2 (opus-4-8, LATEST entry) — opponent = tabaxi3k__charles
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  tabaxi3k__charles, opus-4-8 (Red) WON 250-0 in BOTH rounds. Total domination.
- Verified opponent code UNCHANGED: git show origin/human/tabaxi3k/charles:robot.py
  diffs clean against saved /workspace/charles_opp.py. (Simple whole-team focus-chaser:
  one global target = enemy minimizing sum of dists to allies; all units chase it; NO
  health-based kill-securing, NO retreat, over-commits whole team. Our focus-fire +
  retreat exploits this.)
- Tested robot.py DIRECTLY vs /tmp/charles.py: 4-0 (both colors, N=4). Single game a
  crushing 26-1 units (health 127-4). ~3.4s/game, stderr CLEAN (no errors/timeouts).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments failing/noise).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = devchris__first_test
- /logs/rounds/0/results.json: real opponent = **devchris__first_test**, opus-4-8 (us,
  Blue) WON 250-0. Opponent submits JavaScript (robot.js, NOT robot.py). Extract via:
      git show remotes/origin/human/devchris/first_test:robot.js > /workspace/devchris_opp.js
- devchris/first_test is a SIMPLE whole-team focus-chaser (very similar to tabaxi3k/charles):
  initTurn picks ONE global target = the enemy minimizing the SUM of distances to all our
  allies; then EVERY unit moves toward it and attacks (dir toward it) when adjacent.
  WEAKNESSES vs us: NO health-based kill-securing (attacks whatever's in the target's
  direction, not lowest-HP), NO retreat when wounded, over-commits the whole team to one
  chase. Our aggressive focus-fire + retreat exploits this fully.
- Tested robot.py DIRECTLY vs devchris_opp.js: 6-0 (both colors, N=6). Single game a
  crushing 32-1 units (health 159-4). ~4s/game, no errors/timeouts. Regression guard:
  still crushes simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments failing/noise).
- Next teammate: opponent submits JS (robot.js). Test directly vs devchris_opp.js
  (regen: git show remotes/origin/human/devchris/first_test:robot.js). It herds its whole
  team onto one target with no kill-securing/retreat — our focus-fire dismantles it.

## Round 2 (opus-4-8, LATEST entry) — opponent = devchris__first_test
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  devchris__first_test, opus-4-8 (Blue) WON 250-0 in BOTH rounds. Total domination.
- Verified opponent code UNCHANGED: git show remotes/origin/human/devchris/first_test:robot.js
  diffs clean against saved /workspace/devchris_opp.js. (Simple whole-team focus-chaser:
  one global target = enemy minimizing sum of dists to allies; all units chase & attack;
  NO health-based kill-securing, NO retreat, over-commits whole team. Our focus-fire +
  retreat exploits this.)
- Tested robot.py DIRECTLY vs devchris_opp.js: 6-0 (both colors, N=6). Single game
  Blue won cleanly, no errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments failing/noise).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = aaa__jippty5  *** IMPROVED BOT ***
- /logs/rounds/0/results.json: real opponent = **aaa__jippty5**, opus-4-8 (us, Blue)
  WON 250-0. Extracted opp code (git show origin/human/aaa/jippty5:robot.py), saved
  /workspace/jippty5_opp.py (also /tmp/jippty5.py).
- IMPORTANT: jippty5 is the STRONGEST opponent yet. It is a "Strong, spawn-aware,
  focus-firing agent": influence/threat tile scoring, focus-fire on weakest adjacent
  enemy, reservation system to avoid self-collisions, retreat when locally outnumbered,
  AND crucially SPAWN AWARENESS — it evacuates spawn tiles the turn before a spawn tick
  and camps the spawn ring. Logged margins were the tightest we've seen: mean +15.4
  units but MIN only +5 (vs the usual +20..+30 shutouts). We still win every game.
- CHANGE MADE THIS ROUND (first real code change in many rounds): added SPAWN-AVOIDANCE
  to robot.py (backup of prior version at /tmp/robot_before_spawn.py):
    * new global `next_turn_spawn` = ((turn+1)%10==0), set in init_turn.
    * coord_free() now rejects spawn tiles when next_turn_spawn (don't move onto a
      spawn tile that will be cleared next turn).
    * robot() now has an EMERGENCY EVACUATION as its first check: if a unit stands on a
      spawn tile and next_turn_spawn, it moves to the safest non-spawn free neighbor
      (or attacks an adjacent enemy if truly boxed in). This prevents us LOSING our own
      units to spawn-tile clearing — directly protects unit count (the win condition).
  Rationale: our old bot ignored spawns entirely; against a spawn-aware opp that tight
  margin (+5) suggested we were occasionally losing units to spawn clears. jippty5 gains
  units from this; we shouldn't concede any.
- A/B RESULTS (both colors, background runs due to ~6-8s/game > 30s shell timeout):
    * NEW robot.py vs jippty5_opp.py: 10-0 (of 10). Sample finals: 27-9, 19-10, 21-8 units.
    * OLD robot.py vs jippty5_opp.py: 10-0 (of 10) — baseline, similar margins.
    * NEW robot.py vs simple-bot: 4-0 (regression guard, passive proxy). PASS.
  Syntax verified (ast.parse), no crashes/timeouts (~6s/game). Margins as good or better.
- DECISION: SUBMITTED the improved robot.py with spawn-avoidance. It's a strict
  robustness upgrade (never regressed, protects unit count vs a spawn-aware opponent).
- HOW TO TEST (games are slow ~6-8s each; N>=4 exceeds the 30s AGENT shell timeout):
  use a background runner. Helper saved at /tmp/run_ab.sh (regen if missing):
      /tmp/run_ab.sh robot.py jippty5_opp.py 10 /tmp/out.txt &   # then cat /tmp/out.txt later
- Next teammate: opponent is genuinely strong (spawn-aware focus-fire). We still win 10-0.
  Only further upside would be true lookahead/minimax; A/B any change vs jippty5_opp.py
  (10 games, both colors) AND simple-bot, and NEVER regress. Backup: /tmp/robot_before_spawn.py.

## Round 2 (opus-4-8, LATEST entry) — opponent = aaa__jippty5
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent = aaa__jippty5,
  opus-4-8 WON 250-0 in BOTH rounds (Blue R0, Red R1). Total domination.
- Verified opponent code UNCHANGED: git show origin/human/aaa/jippty5:robot.py diffs
  clean against saved jippty5_opp.py. (Strongest opp: influence-tile scoring, focus-fire
  on weakest adjacent enemy, reservation anti-collision, retreat when outnumbered, AND
  spawn-awareness — evacuates/camps spawn ring. Tightest margins seen but we still win all.)
- robot.py already has the SPAWN-AVOIDANCE upgrade from a prior R1 entry (emergency
  evacuation off spawn tiles the turn before a spawn tick; coord_free rejects spawn tiles
  when next_turn_spawn). Backup of pre-spawn version: /tmp/robot_before_spawn.py.
- Tested robot.py DIRECTLY vs jippty5_opp.py this round: 4-0 (both colors). Margins:
  us=Blue 24-8, 20-6, 19-6; us=Red 24-4. ~8.8s/game (well under 60s limit), stderr CLEAN
  (no errors/timeouts).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; the spawn-aware
  focus-fire bot is strong but our focus-fire + retreat + spawn-avoidance beats it every
  game. Only risk is self-inflicted regression. Next teammate: any change must A/B vs
  jippty5_opp.py (both colors, several games) AND simple-bot, and NEVER regress.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = jay0jayjay__naivestarter
- /logs/rounds/0/results.json: real opponent = **jay0jayjay__naivestarter**, opus-4-8
  (us, Red) WON 250-0. Extracted opp code (git show
  origin/human/jay0jayjay/naivestarter:robot.py), saved /workspace/naive_opp.py (also /tmp/naive.py).
- naivestarter is a WEAK per-unit bot: each unit finds its closest enemy; if health>2 and
  adjacent to that enemy it attacks (dir toward it), otherwise (health>2, not adjacent) it
  moves toward map center (10,10); if health<=2 it FLEES (moves directly away from closest
  enemy). WEAKNESSES vs us: NO focus-fire / kill-securing, NO cohesion (units just drift to
  center), NO spawn awareness, and it only attacks when already adjacent (never pursues to
  engage — just wanders to center). Our aggressive focus-fire + cohesion + retreat crushes it.
- Tested robot.py DIRECTLY vs naive_opp.py: 6-0 (both colors, N=6). Single game crushing
  26-6 units (health 81-16). ~3.9s/game, stderr CLEAN (no errors/timeouts). Regression
  guard: still crushes simple-bot 4-0.
- DECISION: kept proven robot.py UNCHANGED (has spawn-avoidance from prior jippty5 round).
  Opponent cannot beat us; only risk is self-inflicted regression (per all prior rounds'
  heuristic experiments failing/being noise).
- Next teammate: test directly vs naive_opp.py (regen: git show
  origin/human/jay0jayjay/naivestarter:robot.py). It just drifts to center and only attacks
  when already adjacent — our focus-fire + cohesion overwhelms it.

## Round 2 (opus-4-8, LATEST entry) — opponent = jay0jayjay__naivestarter
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  jay0jayjay__naivestarter, opus-4-8 WON 250-0 in BOTH rounds (Red R0, Blue R1).
- Verified opponent code UNCHANGED: git show origin/human/jay0jayjay/naivestarter:robot.py
  diffs clean against saved naive_opp.py. (Weak per-unit: closest-enemy; attacks only if
  adjacent & health>2, else drifts to map center; flees when health<=2. NO focus-fire,
  NO cohesion, NO spawn awareness. Our focus-fire + cohesion + retreat crushes it.)
- Tested robot.py (has spawn-avoidance upgrade) DIRECTLY vs naive_opp.py: 4-0 (both
  colors). Single game crushing 29-6 units (health 80-12). ~5.8s/game, stderr CLEAN
  (no errors/timeouts). robot.py syntax verified via ast.parse.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments failing/noise).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = luisa__luisasrobot  *** IMPROVED BOT ***
- /logs/rounds/0/results.json: real opponent = **luisa__luisasrobot**, opus-4-8 (us, Blue)
  WON 246-3-1. Extracted opp code (git show origin/human/luisa/luisasrobot:robot.py),
  saved /tmp/luisa.py.
- luisa is a PLAN-BASED per-unit closest-enemy chaser: each unit generates plans toward its
  closest enemy (attack if that tile holds an enemy, else move); a greedy select_plans picks
  lowest-distance plans with TARGET-TILE RESERVATION (anti-collision). It HAS spawn awareness
  (skips moving onto spawn tiles the turn before a spawn tick via is_inside_nonspawn). But it
  has NO focus-fire / kill-securing (attacks whatever's in the path direction, random tiebreak
  among equally-close enemies), NO cohesion, NO retreat when wounded. A competent chaser but
  its units SCATTER toward their individual nearest enemies.
- Baseline (pre-change) robot.py already beat luisa 6-0, but margins were the tightest of the
  competent-opp rounds (min +5 units; totals ~68/36 over 6 games).
- CHANGE MADE THIS ROUND: added a COHESION TIEBREAK to choose_move() — after (dist, net-exposure,
  threat), prefer the candidate tile closest to ally_centroid (extra sort key `cdist`). This makes
  our units cluster and gang up harder, exploiting luisa's scattering. Backup of pre-change bot:
  /tmp/robot_before_cohesion.py (also /tmp/robot_current.py). Diff is 4 lines in choose_move.
- A/B RESULTS (unit-margin totals over 6 games, both colors, /tmp/margin.sh):
    * COHESION robot.py vs luisa: totals 87 and 90 (min per-game +10). WIN-rate 6-0 / 4-0.
    * OLD robot.py vs luisa: totals 68 and 36 (min per-game +5). WIN-rate 6-0.
    * HEAD-TO-HEAD cohesion vs old robot.py: 4-0 (cohesion beats the prior bot outright!).
  Regression guards ALL PASS: cohesion vs simple-bot 4-0, vs chaser.js 4-0, vs heuristic-bot.js
  4-0. Syntax verified (ast.parse). Single game clean: Blue 24-12, ~4s/game, stderr no errors.
- DECISION: SUBMITTED the improved robot.py (cohesion tiebreak). It is a strict improvement:
  higher & more consistent margins AND beats the prior proven bot head-to-head 4-0, with no
  regression vs any tested opponent. This is the FIRST heuristic tweak in many rounds that
  A/B-proved a real, repeatable gain (prior cohesion attempts were noisy vs black-magic; but
  vs the actual scattering opponent + head-to-head vs old bot, the gain is clear).
- Next teammate: test directly vs /tmp/luisa.py (regen: git show origin/human/luisa/luisasrobot:robot.py).
  Use /tmp/ab.sh <my> <opp> <N> for win-rate and /tmp/margin.sh for unit-margin totals. Keep N<=6
  for luisa (.py vs .py head-to-head keep N<=4) to stay under the 30s AGENT shell timeout.

## Round 2 (opus-4-8, LATEST entry #2) — opponent = luisa__luisasrobot
- Confirmed via /logs/rounds/0 (246-3-1) AND /logs/rounds/1 (250-0) results.json:
  opponent = luisa__luisasrobot, opus-4-8 (Blue) WON both. The R1 cohesion-tiebreak
  upgrade (in current robot.py) is what pushed R0's 246-3-1 to R1's clean 250-0.
- Re-extracted opp code (git show origin/human/luisa/luisasrobot:robot.py -> /tmp/luisa.py):
  plan-based per-unit closest-enemy chaser, target-tile reservation anti-collision, HAS
  spawn awareness, but NO focus-fire, NO cohesion, NO retreat — units SCATTER. Our
  cohesion+focus-fire exploits the scattering.
- Tested current robot.py DIRECTLY vs /tmp/luisa.py: 4-0 (ab.sh). margin.sh over 6 games:
  runs of +63 and +80 total units (one run had a single -2 game = stochastic variance).
- EXPERIMENT this round: tried retreat threshold health<=1 (more aggressive trading)
  instead of <=2. Result: margin totals ~59-60 (LOWER/no better than baseline's 63-80),
  and head-to-head vs baseline was a wash (1-1-2). No benefit. DISCARDED, reverted.
- DECISION: kept proven robot.py UNCHANGED (baseline backed up /tmp/robot_r2_baseline.py).
  It already wins 250-0. Results are noisy; only real risk is self-inflicted regression.
  Next teammate: any change must A/B vs /tmp/luisa.py (margin.sh, N>=6, both colors) AND
  simple-bot regression guard, and show a CLEAR repeatable gain (margins are noisy — run
  multiple times). Don't submit a tweak that's merely noise-neutral.
