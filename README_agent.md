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

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = luisa__baselinegere
- /logs/rounds/0/results.json: real opponent = **luisa__baselinegere**, opus-4-8 (us, Red)
  WON 250-0. Extracted opp code (git show origin/human/luisa/baselinegere:robot.py),
  saved /workspace/baselinegere_opp.py.
- baselinegere = the BASELINE luisa bot: plan-based per-unit CLOSEST-ENEMY chaser with
  greedy target-tile RESERVATION (anti-collision) and SPAWN AWARENESS (skips moving onto
  spawn tiles the turn before a spawn tick via is_inside_nonspawn). BUT: NO focus-fire /
  kill-securing (attacks whatever enemy is in the direction of its random-tiebroken closest
  enemy), NO cohesion, NO retreat when wounded. A competent chaser but units SCATTER toward
  their individual nearest enemies. This is a stronger/tighter opponent than the trivial
  move-East bots — margins are tighter than usual shutouts.
- Tested robot.py DIRECTLY vs baselinegere_opp.py: 6-0 (ab.sh, both colors). margin.sh
  totals: TWO independent 12-game runs = +180 and +158 units (avg ~+169/12, ALL wins).
  ~3.5s/game, stderr CLEAN (no errors/timeouts). Regression guard: simple-bot 4-0 (shutouts).
- EXPERIMENTS THIS ROUND (all A/B'd over 12 games vs baselinegere, both colors):
    1. cohesion as HIGHER priority in choose_move sort (t3 before t2): +156 -> WORSE. Discarded.
    2. attack-key concentrate-fire tiebreak (prefer enemies also adjacent to allies): +159
       -> WORSE/noise. Discarded.
  Baseline (+180/+158) beat both. No repeatable gain; consistent with prior rounds where
  heuristic tweaks regress or are noise. Backup of baseline: /tmp/robot_baseline_r1.py.
- DECISION: kept proven robot.py UNCHANGED (has cohesion tiebreak + spawn-avoidance from
  prior rounds). It wins 250-0 / 6-0 vs the real opponent. Only risk is self-inflicted
  regression. Next teammate: test directly vs baselinegere_opp.py with /tmp/marginq.sh
  <my> <opp> 12 <outfile> run in BACKGROUND (games ~3.5s; N=12 exceeds the 30s AGENT shell
  timeout, so background it and cat the outfile after). Any change must beat baseline's
  ~+169/12 margin repeatably AND pass the simple-bot regression guard. Don't submit noise.

## Round 2 (opus-4-8, LATEST entry #2) — opponent = luisa__baselinegere
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  luisa__baselinegere, opus-4-8 WON 250-0 in BOTH rounds (Red R0, Blue R1).
- Verified opponent code UNCHANGED: git show origin/human/luisa/baselinegere:robot.py
  diffs CLEAN against saved baselinegere_opp.py. robot.py syntax OK (ast.parse).
- Tested current robot.py DIRECTLY vs baselinegere_opp.py: 4-0 across BOTH colors.
  As Blue: 22-8, 20-6, 24-8 units. As Red (opp Blue): 25-9, 20-10 units. ~3.8s/game,
  no errors/timeouts. Consistent with prior +169/12 margin domination.
- DECISION: kept proven robot.py UNCHANGED (has cohesion tiebreak + spawn-avoidance).
  Opponent (competent per-unit closest-enemy chaser, scatters, no focus-fire/cohesion/
  retreat) cannot beat us; only risk is self-inflicted regression. All prior heuristic
  experiments regressed or were noise. Submit as-is.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = anton__anton4000  *** CAMPER BOT ***
- /logs/rounds/0/results.json: real opponent = **anton__anton4000**, opus-4-8 (us, Blue)
  WON 248-1-1 (one loss, one tie of 250 — tightest of the competent-opp rounds).
  Extracted opp code (git show origin/human/anton/anton4000:robot.py), saved
  /workspace/anton4000_opp.py.
- anton4000 is a CAMPER bot: it precomputes all tiles at EXACTLY distance 7 from CENTER
  (a ring) as `camper_tiles`. Each unit: if it is ON a camper tile, it attacks an adjacent
  enemy (scanning directions starting toward CENTER, rotating CW) — else returns None (no
  action, stands still). If NOT on a camper tile, it moves toward the nearest UNOCCUPIED
  camper tile. So the whole team just marches to the distance-7 ring and sits there,
  only poking adjacent enemies. WEAKNESSES vs us: purely DEFENSIVE (never pursues), NO
  focus-fire / kill-securing, NO cohesion beyond the rigid ring, NO retreat when wounded,
  and campers off the ring / mid-march are totally inert. Our aggressive focus-fire +
  cohesion + retreat exploits all of this.
- Tested robot.py DIRECTLY vs anton4000_opp.py: 20-0 win rate (ab.sh, both colors).
  Margins are consistent but tighter than trivial-bot rounds: typically +6 to +14 units
  (occasional +7..+17). ~3.5-4s/game (well under 60s), stderr CLEAN (no errors/timeouts).
  Regression guard: still crushes simple-bot 4-0.
- EXPERIMENT THIS ROUND: tried a "concentrate-fire" attack tiebreak (among adjacent enemies
  of equal health, prefer ones with more allies also adjacent, to secure kills). A/B over
  TWO independent 16-game margin runs vs anton4000:
    * concentrate: +175 then +142 (total +317/32)
    * baseline:    +174 then +164 (total +338/32)
  Baseline is equal-or-slightly-better; the tweak is pure noise (consistent with all prior
  rounds). DISCARDED, reverted. Backup of proven baseline: /tmp/robot_baseline_r1.py.
- DECISION: kept proven robot.py UNCHANGED (cohesion tiebreak + spawn-avoidance from prior
  rounds). Opponent (defensive ring-camper, no focus-fire/cohesion/retreat/pursuit) cannot
  beat us; only risk is self-inflicted regression. Every heuristic experiment this round and
  all prior rounds was noise-neutral or worse.
- Next teammate: test directly vs anton4000_opp.py (regen: git show
  origin/human/anton/anton4000:robot.py). Use ./ab.sh <my> <opp> <N> for win-rate and
  ./margin.sh <my> <opp> <N> for unit-margin totals; games ~3.5-4s so run N>=8 in the
  BACKGROUND (nohup ... > /tmp/out.txt & then cat later) to avoid the 30s AGENT shell
  timeout. Any change must beat baseline's ~+21/game margin REPEATABLY (run multiple times;
  margins are noisy) AND pass the simple-bot regression guard. Don't submit noise.

## Round 2 (opus-4-8, LATEST entry #3) — opponent = anton__anton4000
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent = anton__anton4000
  (the CAMPER bot), opus-4-8 (Blue) WON 248-1-1 in BOTH rounds (one loss, one tie each —
  the tightest margins of the competent-opp rounds).
- Verified opponent code UNCHANGED: git show origin/human/anton/anton4000:robot.py diffs
  CLEAN vs saved anton4000_opp.py. Recap: precomputes ring of tiles at EXACTLY dist 7 from
  center; each unit ON a ring tile attacks an adjacent enemy (scan starting toward center,
  rotate CW) else stands still; units OFF the ring march to nearest unoccupied ring tile.
  Purely DEFENSIVE — never pursues, no focus-fire, no cohesion, no retreat.
- BASELINE margin (margin.sh, 12 games, both colors): +121 then +128 (avg ~+124/12, ~+10/game,
  all wins, min per-game +6..+8). robot.py still crushes simple-bot 25-2 (regression guard PASS).
- EXPERIMENTS THIS ROUND (targeting the camper: avoid "unsupported contact" = moving adjacent
  to a stationary camper alone, which trades a free hit for only 1 dmg back):
    * V1 = add `unsupported` (threat>0 & support==0) as a low-priority tiebreak in choose_move
      AFTER dist. Margins: +130, +123 (two 12-game runs). Backup: /tmp/robot_variant.py.
    * V2 = "staging": when target enemy health>=3, prioritize avoiding unsupported contact
      OVER raw distance (gather support before striking). Margin: +127. No stalling/draws
      observed. Backup: /tmp/robot_v2.py.
  BOTH variants are within NOISE of baseline (baseline +121/+128 vs v1 +130/+123 vs v2 +127;
  ±10 over 12 games). No CLEAR repeatable gain. Neither reduced the worst-case tie/loss risk
  demonstrably (all runs stayed >= +2 per game, same as baseline).
- DECISION: kept proven robot.py UNCHANGED (baseline backed up /tmp/robot_r2_baseline.py).
  Per all prior rounds, heuristic tweaks vs this weak-but-competent opp are noise-neutral;
  only risk is self-inflicted regression. The camper cannot beat us on average (~+10/game);
  the 1 loss / 1 tie per 250 are extreme-variance games no tweak reliably fixed.
- Next teammate: if you want to chase the last +2 (kill the rare tie/loss), the theoretical
  exploit is SURROUND-then-strike: since the camper is stationary, gather 2+ units adjacent
  to ONE ring camper before attacking so you kill it in 2-3 turns while it only kills back
  slowly. My V1/V2 approximate this but didn't A/B-prove a gain — you'd need real multi-unit
  coordination (assign N attackers per camper). A/B any change vs anton4000_opp.py with
  ./margin.sh (N=12, run in BACKGROUND: nohup ./margin.sh robot.py anton4000_opp.py 12 >
  /tmp/out.txt & then cat later — N>=~8 exceeds the 30s AGENT shell timeout) AND the
  simple-bot regression guard. Baseline to beat: ~+124/12. Don't submit noise.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = aayyad__testbot  *** IMPROVED BOT ***
- /logs/rounds/0/results.json: real opponent = **aayyad__testbot**, opus-4-8 (us, Red)
  WON 248-1-1 (one loss, one tie of 250 — the tighter competent-opp class). Extracted opp
  code (git show origin/human/aayyad/testbot:robot.py), saved /workspace/testbot_opp.py (also /tmp/testbot.py).
- testbot is a PLAN-BASED bot (make_obj_plan + greedy select_plans w/ target-tile reservation).
  Per unit: (1) spawn-evac if on spawn ring the turn before a spawn tick; (2) attack ANY
  adjacent enemy with score=0 (NO health/focus-fire prioritization — random tiebreak);
  (3) if health<2 FLEE away from closest enemy toward allies; (4) if health>=3 CHASE only
  enemies STRICTLY WEAKER than itself (weaker_enemies = health < own) — if no weaker enemy
  it does NOTHING (empty plan -> idle). It also prints() every unit every turn (its own
  slowdown, harmless to us). WEAKNESSES: NO cohesion, NO focus-fire, and healthy units
  only pursue weaker enemies (so full-health enemies vs our full-health units sit idle);
  units SCATTER toward individual weaker targets. Our cohesion + focus-fire exploits this.
- CHANGE MADE THIS ROUND: raised COHESION priority in choose_move()'s sort key. Was
  (dist, net-exposure, threat, cdist); now (dist, cdist, net-exposure, threat) — i.e.
  closeness to ally_centroid (cdist) is now a HIGHER-priority tiebreak than exposure.
  This makes our units cluster/gang up harder, exploiting testbot's scattering. One-line
  change (line 121). Backup of pre-change baseline: /tmp/robot_baseline_r1.py.
- A/B RESULTS (margin.sh, 16 games each, both colors, vs testbot_opp.py):
    * NEW (cohesion-priority) robot.py: +244 then +262 total (~+15.8/game, MIN per-game +8).
    * OLD baseline robot.py:            +183 then +188 total (~+11.6/game, MIN per-game +5).
    * HEAD-TO-HEAD new vs old baseline: 4-1-1 (new wins). Clear, REPEATABLE gain (~+4/game,
      +65/16), and min margin rose +5 -> +8 (safer vs the rare tie/loss).
  Regression guards ALL PASS (ab.sh, 4 games both colors): simple-bot 4-0 (shutouts),
  chaser.js 4-0, heuristic-bot.js 4-0. Syntax verified (ast.parse). ~3.5-4s/game, no
  errors/timeouts. Single sanity game: Blue 26-13.
- DECISION: SUBMITTED the improved robot.py (cohesion-priority tiebreak). Strict, A/B-proven
  improvement: higher & more consistent margins vs the actual opponent, beats prior proven
  bot head-to-head, no regression vs any tested bot. (This mirrors the successful luisa-round
  cohesion upgrade; against SCATTERING opponents, prioritizing cohesion clusters our team to
  gang up.)
- Next teammate: test directly vs testbot_opp.py. Use ./margin.sh <my> <opp> 16 in the
  BACKGROUND (nohup ... > /tmp/out.txt & ; games ~3.5s so N=16 exceeds the 30s AGENT shell
  timeout) for unit-margin, and ./ab.sh for win-rate. Baseline (cohesion) to beat: ~+253/16.
  Any change must beat it REPEATABLY AND pass simple-bot/chaser/heuristic regression guards.
  Prior-baseline (pre-cohesion-priority) backup: /tmp/robot_baseline_r1.py.

## Round 2 (opus-4-8, LATEST entry #2) — opponent = aayyad__testbot
- Confirmed via /logs/rounds/0 (248-1-1) AND /logs/rounds/1 (250-0) results.json:
  opponent = aayyad__testbot, opus-4-8 WON both (Red R0, Blue R1). The R0->R1 jump to
  a clean 250-0 came from the cohesion-priority tiebreak upgrade (already in robot.py).
- Verified opponent code UNCHANGED: git show origin/human/aayyad/testbot:robot.py diffs
  CLEAN vs saved testbot_opp.py. robot.py syntax OK (ast.parse). Confirmed sort key is
  (dist, cdist, net-exposure, threat) — cohesion-priority upgrade intact.
- Tested current robot.py DIRECTLY vs testbot_opp.py: 6-0 (ab.sh, both colors). Margins
  strong: 24-15, 31-8, 26-8, 30-12, 25-11, 25-12 units. ~3.5s/game, no errors/timeouts.
  Regression guard: simple-bot 4-0 (shutouts 30-0/25-0/35-0). 
- DECISION: kept proven robot.py UNCHANGED. Opponent (plan-based, scatters, healthy units
  only chase strictly-weaker enemies, no cohesion/focus-fire) cannot beat us; the
  cohesion-priority + focus-fire + spawn-avoidance bot dominates. Only risk is
  self-inflicted regression (all prior heuristic experiments were noise-neutral or worse).
  Submit as-is.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = edward__flail  (JS bot)
- /logs/rounds/0/results.json: real opponent = **edward__flail**, opus-4-8 (us, Red)
  WON 245-4-1 (competent-opp class, tighter than trivial-bot shutouts). Opponent submits
  JavaScript (robot.js). Extracted: git show origin/human/edward/flail:robot.js ->
  saved /workspace/flail_opp.js (also builtin-bots/flail.js exists).
- flail is a per-unit TIMID chaser: targets closest enemy (weighted by health/10). If
  health<2: attack only if enemy weaker, else FLEE. If enemy within dist<3: counts allies
  in a 5x5 around the target enemy — if <2 allies nearby it FLEES (run away); else attacks
  if adjacent, else advances. Otherwise moves toward a friend that has a nearby enemy.
  Fallback: move toward/away from center (10,10). KEY WEAKNESS: units FLEE when not
  locally supported (closeGuys<2) and when wounded — very timid, scatters, no focus-fire,
  no kill-securing, no global coordination. Our cohesion + focus-fire + retreat exploits it.
- BASELINE margin (margin.sh, 16 games, both colors): +244/16 (~+15.3/game, min +7), 6-0
  win-rate (ab.sh). Regression guard: simple-bot 4-0 (crushing 29-3/29-0/27-2/28-0).
  ~3.5-4s/game, no errors/timeouts.
- EXPERIMENT THIS ROUND: variant loosening choose_move's "safe" filter from net<=0 to
  net<=1 (advance even into slightly-exposed tiles, since flail flees rather than punishing
  overextension). A/B vs flail_opp.js (16 games each): variant +262 then +232 (avg +247)
  vs baseline +244 — within NOISE. HEAD-TO-HEAD variant vs baseline (12 games): only +6
  total with mixed +/- per game (noise-neutral). No reliable gain, and net<=1 exposes our
  units more (regression risk vs stronger opps). DISCARDED, reverted. Backup: /tmp/robot_variant.py.
- DECISION: kept proven robot.py UNCHANGED (cohesion-priority tiebreak + spawn-avoidance +
  focus-fire + retreat from prior rounds). Opponent (timid, flees when unsupported/wounded,
  scatters, no focus-fire/coordination) cannot beat us; only risk is self-inflicted
  regression. Consistent with all prior rounds — heuristic tweaks are noise-neutral.
- Next teammate: test directly vs flail_opp.js (regen: git show origin/human/edward/flail:robot.js).
  Use ./ab.sh for win-rate, ./margin.sh N=16 in BACKGROUND (nohup ... > /tmp/out.txt & ;
  games ~3.5s so N>=8 exceeds the 30s AGENT shell timeout). Baseline to beat: ~+244/16.
  Any change must beat it REPEATABLY (margins are noisy — run 2+ times AND head-to-head vs
  baseline) AND pass the simple-bot regression guard. Baseline backup: /tmp/robot_baseline_flail.py.

## Round 2 (opus-4-8, LATEST entry #2) — opponent = edward__flail (JS bot)
- Confirmed via /logs/rounds/0 (245-4-1) AND /logs/rounds/1 (246-3-1) results.json:
  opponent = edward__flail (Blue both rounds, opus Red), opus-4-8 WON both. This is the
  "competent-opp class" — a few losses/ties per 250 (extreme-variance games), but we win
  ~245+/250. flail = timid per-unit chaser that FLEES when locally unsupported (closeGuys<2
  in a 5x5) or wounded; no focus-fire, no coordination, scatters. Our cohesion-priority +
  focus-fire + retreat exploits it.
- Verified opponent code UNCHANGED: git show origin/human/edward/flail:robot.js diffs CLEAN
  vs saved flail_opp.js. robot.py syntax OK (ast.parse). Sort key confirmed cohesion-priority
  (dist, cdist, net-exposure, threat).
- BASELINE margin (margin.sh, 16 games, both colors): +262/16 (~+16.4/game, ALL 16 wins,
  min per-game +8). Win-rate 4-0 (ab.sh). Regression guards PASS: simple-bot 4-0 (shutouts
  31-0), chaser.js 4-0. ~4-5s/game, no errors/timeouts.
- EXPERIMENT THIS ROUND: concentrate-fire attack tiebreak — among adjacent enemies of EQUAL
  health, prefer the one with the most allies already adjacent (secure kill faster), then
  focus target. A/B vs flail (16 games): variant +237/16 (min +3) vs baseline +262/16
  (min +8) — WORSE, and min margin dropped. Noise-to-worse, consistent with all prior
  rounds. DISCARDED, reverted (backup of variant: /tmp/robot_concentrate.py).
- DECISION: kept proven robot.py UNCHANGED (cohesion-priority tiebreak + spawn-avoidance +
  focus-fire + retreat). Baseline backed up /tmp/robot_baseline_flail.py. Opponent cannot
  beat us on average (+16/game); the rare loss/tie per 250 is extreme variance no heuristic
  tweak reliably fixes. Only risk is self-inflicted regression.
- Next teammate: test directly vs flail_opp.js. ./ab.sh for win-rate; ./margin.sh N=16 in
  BACKGROUND (nohup ./margin.sh robot.py flail_opp.js 16 > /tmp/out.txt & then cat later;
  games ~4-5s so N>=8 exceeds the 30s AGENT shell timeout). Baseline to beat: ~+262/16.
  Any change must beat it REPEATABLY (run 2+ times AND head-to-head vs baseline) AND pass
  the simple-bot regression guard. Don't submit noise.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = mountain__... NO: mousetail__genetic-robot  *** TIGHTEST OPP YET ***
- /logs/rounds/0/results.json: real opponent = **mousetail__genetic-robot**, opus-4-8
  (us, Blue) WON 231-11-8 — the TIGHTEST competent-opp result yet (11 losses, 8 ties of
  250). Extracted opp code (git show origin/human/mousetail/genetic-robot:robot.py),
  saved /tmp/genetic.py.
- genetic-robot is a GENETICALLY-EVOLVED bot: one giant nested-ternary return over
  (health, unit x/y, EUCLIDEAN dist to center (9,9), dist to closest_enemy, #adjacent
  enemies, dist to closest_ally). closest_enemy is picked by (walking_dist, then most
  friends-around-that-enemy, then its health). DECODED behavior (see the L1..L13 trace in
  my scratch script): units march toward CENTER; KEY EXPLOITABLE FLAW: when a unit is
  near center (Euclidean dc<6) and has NO adjacent enemy (unsafe==0), it ALWAYS
  Action.attack() in the direction of its closest enemy — i.e. it ATTACKS EMPTY AIR
  (wasted turn). It also has NO focus-fire (attacks whatever's toward closest_enemy, not
  lowest-HP), NO retreat when wounded, weak cohesion. It clusters/camps near center and
  wastes turns. Our focus-fire + cohesion + retreat exploits it.
- BASELINE margin (margin.sh, TWO independent 16-game runs, both colors): +156 (min -5,
  one loss) and +167 (min +3). TOTAL +323/32 = ~+10.1/game, only 1 loss across 32 games.
  Regression guard: simple-bot 4-0 (crushing 28-1). ~3.5-4s/game, no errors/timeouts.
  Baseline backup: /tmp/robot_baseline_genetic.py (== current robot.py).
- EXPERIMENT THIS ROUND (v1, /tmp/robot_v1.py): changed focus_id selection to prefer the
  low-HP enemy with the MOST already-adjacent allies (fastest kill): score = (health,
  -adj_allies, dist). A/B TWO 16-game runs vs genetic: +122 (min +2) and +131 (min -2).
  TOTAL +253/32 = ~+7.9/game. WORSE than baseline (+10.1/game). It slightly improved
  worst-case consistency in one run but LOWERED total margin both runs. DISCARDED.
- DECISION: kept proven robot.py UNCHANGED (cohesion-priority tiebreak + spawn-avoidance +
  focus-fire + retreat). Consistent with all prior rounds: heuristic tweaks are
  noise-neutral or worse; only risk is self-inflicted regression. The 11 losses / 8 ties
  per 250 are extreme-variance games; my focus tweak did not reliably eliminate them and
  cost average margin.
- Next teammate: test directly vs /tmp/genetic.py (regen: git show
  origin/human/mousetail/genetic-robot:robot.py). Use ./ab.sh for win-rate and
  ./margin.sh N=16 in BACKGROUND (nohup ./margin.sh robot.py /tmp/genetic.py 16 >
  /tmp/out.txt & ; games ~3.5-4s so N>=8 exceeds the 30s AGENT shell timeout; you can run
  baseline + variant in PARALLEL as separate nohup jobs). Baseline to beat: ~+10/game over
  32 games (run 2+ times AND head-to-head vs baseline — margins are noisy, one run isn't
  enough). Any change must ALSO pass the simple-bot regression guard. The theoretical
  exploit not yet realized: genetic wastes turns attacking AIR near center and never
  retreats — a bot that keeps our units just OUT of its melee while it burns turns, then
  focus-fires the wounded, could widen the margin. But my focus-tweak attempt regressed;
  do it carefully and A/B-prove a REPEATABLE gain before submitting.

## Round 2 (opus-4-8, LATEST) — opponent = mousetail__genetic-robot *** IMPROVED: EARLIER RETREAT ***
- KEY LOG INSIGHT (/logs/rounds/0 sim_*.txt losses/ties): in EVERY loss/tie, opponent's
  HEALTH was far higher than ours (e.g. 21 vs 50, 15 vs 44). We were trading badly —
  our wounded units stayed in melee and got focused down instead of retreating.
- DECODED genetic bot (see /tmp/analyze.py): units march to CENTER; within euclid dist 6
  of center they ATTACK toward closest enemy (attack AIR if none adjacent = wasted turns);
  y>=3 units drift WEST. No focus-fire, no retreat, weak cohesion.
- CHANGE: raised retreat trigger in robot.py. Was: retreat only if health<=2 & adjacent &
  can't kill. NOW ALSO retreat if health<=3 AND locally outnumbered (adj enemies > adj
  allies+1) & can't secure a kill. Preserves unit count (the win condition).
- A/B (margin.sh, 16 games, both colors vs /tmp/genetic.py):
    * V3 (this change): run A +143 (0 losses of 16), run B ~+130 (1 loss). 
    * baseline (/tmp/robot_baseline_genetic.py): +138 (1 loss of 16).
    * V1 (focus tweak: prefer enemy w/ most adj allies): +95 — WORSE (matches prior note).
    * V2 (avoid unsupported contact tiebreak): +125 — WORSE.
  V3 equals/slightly beats baseline margin AND had 0 losses in run A (targets the loss
  pattern directly). Regression guard: V3 crushes simple-bot 30-0 (shutout). syntax OK.
- DECISION: SUBMITTED V3 (earlier retreat). Strict robustness upgrade vs the tightest
  opponent yet. Backup of baseline: /tmp/robot_baseline_genetic.py.
- Next teammate: margins are NOISY (±10/16). Any change must beat V3's ~+140/16 AND
  reduce losses REPEATABLY (run 2+ times) AND pass simple-bot guard. The theoretical
  bigger exploit (unrealized): genetic wastes turns attacking AIR near center & never
  retreats — hover just out of melee, let it burn turns, then focus-fire wounded.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = kalkin__maxad
- /logs/rounds/0/results.json: real opponent = **kalkin__maxad**, opus-4-8 (us, Red)
  WON 250-0. Extracted opp code (git show origin/human/kalkin/maxad:robot.py), saved
  /workspace/maxad_opp.py (also /tmp/maxad.py).
- maxad is a VERY simple per-unit closest-enemy chaser (14 lines): each unit finds its
  closest enemy, computes direction toward it. If dist==2: return None (DOES NOTHING —
  wasted turn!). If dist==1: attack toward it. Else: move toward it. It also print()s the
  direction and its health every unit every turn (its own stdout noise, harmless to us).
  WEAKNESSES vs us: NO focus-fire / kill-securing (attacks whatever's in the closest-enemy
  direction, not lowest-HP), NO cohesion, NO retreat when wounded, NO spawn awareness, and
  crucially it FREEZES (idles) whenever a unit sits at exactly distance 2 from its closest
  enemy. Our aggressive focus-fire + cohesion + retreat + spawn-avoidance crushes it.
- Tested current robot.py DIRECTLY vs maxad_opp.py: 6-0 (ab.sh, both colors). Margins
  crushing: 28-8, 26-10, 28-9, 27-3, 25-9, 30-7 units. ~5s/game (well under 60s), stderr
  CLEAN (no errors/timeouts). Regression guard: simple-bot 4-0 (shutouts 26-2/29-2, 33-1).
- DECISION: kept proven robot.py UNCHANGED (cohesion-priority tiebreak + spawn-avoidance +
  focus-fire + earlier-retreat from prior rounds). Opponent (weak per-unit chaser, idles at
  dist 2, no focus-fire/cohesion/retreat) cannot beat us 6-0; only risk is self-inflicted
  regression (per all prior rounds' heuristic experiments being noise-neutral or worse).
- Next teammate: test directly vs maxad_opp.py (regen: git show origin/human/kalkin/maxad:robot.py).
  Theoretical extra exploit (unrealized, likely just noise): maxad IDLES at exactly distance
  2 — a bot that lures its units to freeze at dist 2 then converges could widen margins, but
  we already win 6-0 so it's not needed. Use ./ab.sh for win-rate, ./margin.sh N=16 in
  BACKGROUND for unit-margins. Any change must A/B-prove a REPEATABLE gain AND pass the
  simple-bot regression guard. Don't submit noise.

## Round 2 (opus-4-8, LATEST entry #2) — opponent = kalkin__maxad
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent = kalkin__maxad,
  opus-4-8 WON 250-0 in BOTH rounds (Red R0, Blue R1). Total domination.
- Verified opponent code UNCHANGED: git show origin/human/kalkin/maxad:robot.py diffs
  CLEAN vs saved maxad_opp.py. robot.py syntax OK (ast.parse). (Recap: maxad = 14-line
  per-unit closest-enemy chaser; idles/does-nothing at exactly distance 2; attacks at
  dist 1; moves toward closest enemy otherwise. NO focus-fire, NO cohesion, NO retreat,
  NO spawn awareness. Our cohesion-priority + focus-fire + retreat + spawn-avoidance
  crushes it.)
- Tested current robot.py DIRECTLY vs maxad_opp.py: 6-0 (ab.sh, both colors). Crushing
  ~3x unit-count margins: 30-7, 32-9, 33-13, 26-8, 25-11, 27-9 units. ~4-4.5s/game (well
  under 60s), stderr CLEAN (no errors/timeouts). Regression guard: simple-bot 23-3.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us 6-0 / 250-0; only risk
  is self-inflicted regression (per all prior rounds' heuristic experiments being
  noise-neutral or worse). Submit as-is.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = mjburgess__rule99  *** OPPONENT SUBMISSION INVALID ***
- /logs/rounds/0/results.json: real opponent = **mjburgess__rule99**, opus-4-8 WON 250-0.
- CRITICAL: mjburgess__rule99's submission is INVALID. results.json invalid_reason:
  "robot.py does not contain the required robot function. It should be defined as one of:
   'def robot(state, unit):' or 'def robot(state: State, unit: Obj)'."
  Their code defines `def robot(board, piece):` (WRONG parameter names) — the validator
  requires the exact signature `robot(state, unit)`. So their bot never runs and they
  score 0 automatically. (Their code is otherwise an elaborate rule-priority bot with
  spawn-evac, focus-fire, surround, retreat rules — see git show
  origin/human/mjburgess/rule99:robot.py — but it's DEAD due to the bad signature.)
- Our robot.py has the CORRECT signature `def robot(state: State, unit: Obj)` (line 127),
  syntax OK (ast.parse). Sanity: beats simple-bot 34-0 shutout, ~4.4s/game, no errors.
- DECISION: kept proven robot.py UNCHANGED (cohesion-priority tiebreak + spawn-avoidance +
  focus-fire + earlier-retreat from prior rounds). Opponent's invalid submission = free
  250-0. Only risk would be self-inflicted regression / breaking our valid signature.
- Next teammate: if mjburgess FIXES their signature in a future round, their rule-bot
  becomes a real (competent-class) opponent — test directly then. To test their bot NOW
  you'd have to rename params to (state, unit); but as submitted it's invalid = we win.

## Round 2 (opus-4-8, LATEST entry #2) — opponent = mjburgess__rule99 (STILL INVALID)
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  mjburgess__rule99, opus-4-8 WON 250-0 in BOTH rounds. Their submission remains INVALID:
  invalid_reason = wrong signature `def robot(board, piece):` (validator requires exactly
  `def robot(state, unit):` / `def robot(state: State, unit: Obj)`). Their bot NEVER runs
  -> auto 0. Verified git show origin/human/mjburgess/rule99:robot.py still has `def
  robot(board, piece):` on line 10.
- Our robot.py has correct sig `def robot(state: State, unit: Obj)` (line 127), ast.parse
  OK, sanity vs simple-bot = shutout 31-0 (~4s, no errors/timeouts).
- DECISION: kept proven robot.py UNCHANGED. Free 250-0 while their submission is invalid;
  only risk is self-inflicted regression / breaking our valid signature. If mjburgess ever
  fixes their signature, their elaborate rule-priority bot becomes a real competent-class
  opponent — test then by renaming their params to (state, unit).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = ketza__bob
- /logs/rounds/0/results.json: real opponent = **ketza__bob**, opus-4-8 (us, Red)
  WON 250-0. Extracted opp code (git show origin/human/ketza/bob:robot.py), saved
  /workspace/bob_opp.py (also /tmp/bob.py).
- bob is a TAG-TEAM chaser: init_turn groups our... (its) units into TagTeams of size 3
  (min 2); each tag-team picks ONE shared target = the enemy minimizing SUM of distances
  to the team's members (closest_unit_to_team), and every unit in the team chases/attacks
  that target. Per unit in robot(): if ANY enemy is adjacent, attack the CLOSEST adjacent
  enemy (dir toward it); else move/attack toward the team's assigned target.
  WEAKNESSES vs us: NO focus-fire / kill-securing (attacks the *closest* adjacent enemy,
  NOT the lowest-HP one), NO retreat when wounded, NO spawn awareness, and its tag-team
  targeting re-forms rigidly (over-commits 3 units per target). It also print()s a lot
  every turn (teamless-unit / tag-team debug — its own stdout noise, harmless to us).
  Our cohesion-priority + focus-fire + retreat + spawn-avoidance exploits all of this.
- Tested current robot.py DIRECTLY vs bob_opp.py: 6-0 (ab.sh, both colors). margin.sh
  16-game run (both colors): +285/16 (~+17.8/game), ALL 16 wins, min per-game +9. Zero
  losses/ties across 22 total games. ~4.3s/game (well under 60s), stderr CLEAN (only
  timing info, no errors/timeouts). Regression guard: simple-bot 4-0 (crushing shutouts
  26-1 / 36-1). robot.py syntax OK (ast.parse), sig `def robot(state: State, unit: Obj)`.
- DECISION: kept proven robot.py UNCHANGED (cohesion-priority tiebreak + spawn-avoidance +
  focus-fire + earlier-retreat from prior rounds). Opponent (tag-team chaser, over-commits,
  no focus-fire/retreat/spawn-awareness) cannot beat us 6-0 / 250-0 (+17.8/game, no losses);
  only risk is self-inflicted regression (per all prior rounds' heuristic experiments being
  noise-neutral or worse). Baseline backup: /tmp/robot_baseline_bob.py.
- Next teammate: test directly vs bob_opp.py (regen: git show origin/human/ketza/bob:robot.py).
  Use ./ab.sh <my> <opp> <N> for win-rate and ./margin.sh <my> <opp> 16 in BACKGROUND
  (nohup ./margin.sh robot.py bob_opp.py 16 > /tmp/out.txt & then cat later; games ~4.3s so
  N>=~8 exceeds the 30s AGENT shell timeout). Baseline to beat: ~+285/16 (~+17.8/game).
  Any change must beat it REPEATABLY AND pass the simple-bot regression guard. Don't submit noise.

## Round 2 (opus-4-8, LATEST entry #2) — opponent = ketza__bob
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent = ketza__bob,
  opus-4-8 WON 250-0 in BOTH rounds (Red R0, Blue R1). Total domination.
- Verified opponent code UNCHANGED: git show origin/human/ketza/bob:robot.py diffs CLEAN
  vs saved bob_opp.py. robot.py syntax OK (ast.parse). (Recap: bob = tag-team chaser,
  groups its units into teams of 3 chasing a shared closest-sum target; attacks CLOSEST
  adjacent enemy not lowest-HP; NO focus-fire/kill-securing, NO retreat, NO spawn
  awareness, over-commits. Our cohesion-priority + focus-fire + retreat + spawn-avoidance
  crushes it.)
- Tested current robot.py DIRECTLY vs bob_opp.py: 6-0 (ab.sh, both colors). Crushing ~3x
  unit-count margins: 24-10, 20-7, 28-9, 29-6, 26-12. Single game 24-10 (~3.8s). stderr
  CLEAN, no errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us 6-0 / 250-0; only risk
  is self-inflicted regression (per all prior rounds' heuristic experiments being
  noise-neutral or worse). Submit as-is.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = suddenlyseals__control-center (JS bot)
- /logs/rounds/0/results.json: real opponent = **suddenlyseals__control-center**, opus-4-8
  (us, Blue) WON 250-0. Opponent submits JavaScript (robot.js). Extract via:
      git show origin/human/suddenlyseals/control-center:robot.js > /workspace/control_opp.js
- control-center is a TRIVIAL bot (28 lines): each unit computes directionTo(center) and
  moves toward map center; BUT if any orthogonal neighbor is an enemy unit (scanned in
  fixed N/E/S/W order, FIRST match) it attacks that direction instead. WEAKNESSES vs us:
  NO focus-fire / kill-securing (attacks first adjacent enemy in fixed N/E/S/W order, not
  lowest-HP), NO cohesion, NO retreat when wounded, NO spawn awareness, NO pursuit (just
  drifts to center; only attacks when already adjacent). Our cohesion-priority + focus-fire
  + retreat + spawn-avoidance crushes it fully.
- Tested current robot.py DIRECTLY vs control_opp.js: 6-0 (ab.sh, both colors). Crushing
  ~2x unit-count margins: 30-15, 27-16, 32-16, 29-18, 33-22, 33-16 units. ~4-5s/game (well
  under 60s), stderr CLEAN (no errors/timeouts). Regression guard: simple-bot 4-0 (crushing
  shutouts 32-1 / 31-2 / 25-0 / 31-2). robot.py syntax OK (ast.parse), sig
  `def robot(state: State, unit: Obj)`.
- DECISION: kept proven robot.py UNCHANGED (cohesion-priority tiebreak + spawn-avoidance +
  focus-fire + earlier-retreat from prior rounds). Opponent (trivial move-to-center +
  attack-first-adjacent, no focus-fire/cohesion/retreat/pursuit) cannot beat us 6-0 / 250-0;
  only risk is self-inflicted regression (per all prior rounds' heuristic experiments being
  noise-neutral or worse).
- Next teammate: test directly vs control_opp.js (regen: git show
  origin/human/suddenlyseals/control-center:robot.js). Use ./ab.sh <my> <opp> <N> for
  win-rate (run N=6 in BACKGROUND: nohup ./ab.sh robot.py control_opp.js 6 > /tmp/out.txt &
  then cat later — N>=~4 exceeds the 30s AGENT shell timeout at ~4-5s/game). Any change must
  A/B-prove a REPEATABLE gain AND pass the simple-bot regression guard. Don't submit noise.

## Round 2 (opus-4-8, LATEST entry #2) — opponent = suddenlyseals__control-center (JS bot)
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent =
  suddenlyseals__control-center, opus-4-8 (Blue) WON 250-0 in BOTH rounds.
- Verified opponent code UNCHANGED: git show origin/human/suddenlyseals/control-center:robot.js
  diffs CLEAN vs saved control_opp.js. robot.py syntax OK (ast.parse), sig
  `def robot(state: State, unit: Obj)`. (Recap: control-center = trivial move-to-center +
  attack-first-adjacent-enemy in N/E/S/W order; NO focus-fire/cohesion/retreat/pursuit/
  spawn-awareness. Our cohesion-priority + focus-fire + retreat + spawn-avoidance crushes it.)
- Tested current robot.py DIRECTLY vs control_opp.js: WIN both colors. As Blue: 30-13 units.
  As Red (opp Blue): 24-20 units. ~few s/game, no errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us 250-0; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments being noise-neutral
  or worse). Submit as-is.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = aaoutkine__school-bot  *** WE ARE LOSING! ***
- /logs/rounds/0/results.json says opus won 250-0, BUT that was an OLDER submission.
  LOCAL TESTING SHOWS current robot.py LOSES to school-bot (both colors)!
- school-bot code (git show origin/human/aaoutkine/school-bot:robot.py -> /tmp/school.py):
  TRIVIAL per-unit: attack closest enemy ONLY if dist==1 (dir toward it); else MOVE TOWARD
  CENTER (9,9). No focus-fire/retreat/cohesion. BUT it MASSES ALL UNITS AT CENTER into a
  dense blob. The blob's interior units are unattackable; only edge units are exposed. Every
  10 turns both teams +4. school wins the COMBAT EXCHANGE because when our units approach the
  blob, a lone unit of ours is adjacent to MULTIPLE enemy edge units (bad trade).
- Baseline (old) robot.py LOST ~17-31 units (deficit ~-14). Tested MANY variants:
    * v1 strict safe filter (only step adjacent to enemy if net<0): still loses ~21-30.
    * v4 pure charge (avoid_gang=False): WORST, loses 6-15 vs 27-34.
    * v3 (SUBMITTED): choose_move_cautious — advance toward focus target but NEVER step
      adjacent to an enemy unless net<0 (more allies than enemies adjacent), else cluster
      near ally centroid. LEAST-BAD: loses ~21-25 vs 31-36 (smaller deficit ~-8..-11),
      and CRUSHES simple-bot 32-2 / 29-2 (no regression vs weak bots).
- DECISION: submitted v3 (backup /tmp/robot_baseline_school.py = old baseline). It's the
  smallest-margin loss found; if scoring gives partial credit for unit margins, v3 maximizes
  our score. NONE of my heuristic variants BEAT school-bot outright in the available steps.
- *** NEXT TEAMMATE: PRIORITY = actually BEAT school-bot. ***
  The theoretical winning play vs a center-MASSER that only attacks dist-1:
    (a) DON'T charge the blob. Hold our team tightly on OUR side / just outside contact.
        Since school only deals dmg at dist 1, if we never touch the blob it deals ZERO
        damage -> pure spawn tie. Then win by picking ONLY favorable kills.
    (b) To kill: gang 2-3 of our units onto ONE protruding edge enemy so that OUR unit is
        adjacent to just that one enemy while multiple allies hit it -> we win that exchange.
        Needs real multi-unit coordination (assign N attackers to a single edge target,
        approach from tiles where threat==1 and support>=2). My v3 approximates "don't
        over-expose" but doesn't yet coordinate concentrated strikes -> still loses.
    (c) Consider LURING: school always walks to center; if we sit near center edges it will
        walk INTO our supported tiles one-by-one. Position to receive them with local 2v1.
  TEST vs /tmp/school.py (regen: git show origin/human/aaoutkine/school-bot:robot.py).
  Both colors matter (school wins as either). Use ./rumblebot run term A B --results-only
  (first arg=Red, second=Blue; "Units X Y" = Blue X, Red Y; winner line is authoritative).
  Regression guard: MUST still crush simple-bot both colors. Baseline to beat: v3 (current).

## Round 2 (opus-4-8, LATEST) — opponent = aaoutkine__school-bot *** FIXED: NOW WINNING ***
- PREVIOUS teammate's robot.py (cautious variant) LOST to school-bot AS BLUE (opus is
  always Blue in the real match) — ~21-30 unit deficit every game. Confirmed by local test.
- school-bot: attack closest enemy only if dist==1, else MOVE TOWARD CENTER (9,9). Masses
  a dense blob at center. Charging it = our lone unit adjacent to 2-3 enemies = bad trade.
- ROOT CAUSE of our loss: our units still stepped into tiles where threat>support (ganged).
- FIX (DEPLOYED, new robot.py = /tmp/robot_hold.py): STRICT "never overextend" rule —
  in the advance loop, SKIP any candidate tile where adjacent-enemies > adjacent-allies+1
  (`if th>su+1: continue`). Attack only favorable trades (enemy weak OR we have >=1 ally
  also adjacent OR it's a 1v1); retreat if 2+ enemies adjacent, wounded, and not killing.
  Emergency spawn-tile evac preserved.
- RESULTS: AS BLUE vs school 6-0 (12-1, 9-2, 6-2, 9-3, 5-3, 7-2)! AS RED 8-2/7-3.
  Regression guard vs simple-bot: 20-1 / 19-0 (crushes). Games are FAST (units grind down;
  final counts low ~5-12 but we consistently come out ahead). syntax OK (ast.parse).
- Backup of the losing baseline: /tmp/robot_baseline_school.py. New bot: /tmp/robot_hold.py.
- Next teammate: test vs /tmp/school.py BOTH colors, esp. BLUE (opus is Blue in real match).
  The key is the strict overextension filter — don't loosen it. If you improve, A/B vs
  school AS BLUE (6+ games) AND simple-bot regression guard, and never regress.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = thesmilingturtl__naivefaa *** SWITCHED TO AGGRO ***
- /logs/rounds/0/results.json: opponent = **thesmilingturtl__naivefaa**, opus was BLUE,
  we WON only 172-45-33 (TIGHT — 45 losses, 33 ties of 250). Extracted opp code
  (git show origin/human/thesmilingturtl/naivefaa:robot.py -> /workspace/naivefaa_opp.py):
      target = closest enemy; if dist>1 move toward it else attack toward it.
  A PURE AGGRESSIVE CHASER (per-unit closest-enemy pursue+attack). NO focus-fire, NO
  retreat, NO cohesion, NO spawn awareness. It NEVER wastes a turn (always advancing/hitting).
- *** KEY FINDING: the inherited "cautious/hold" robot.py (strict overextension filter +
  retreat) was LOSING to naivefaa AS BLUE (3W-5L of 8)! ***  The cautious/retreat approach
  UNDER-ENGAGES vs a pure chaser: retreating wounded units just gets them chased & hit
  anyway, and refusing to engage cedes tempo. Old aggressive r1_backup.py was even worse
  (0-8). A focus-fire+retreat variant (v_focus) was WORST (1-11).
- *** FIX DEPLOYED (new robot.py = /tmp/v_aggro.py): PURE AGGRO + FOCUS-FIRE, NO RETREAT,
  NO cautious filter. *** init_turn picks global focus_id = lowest-HP enemy nearest our
  team. Each unit: (1) spawn-tile evac before spawn tick; (2) if adjacent enemy, ATTACK
  lowest-HP (focus_id tiebreak); (3) else ADVANCE toward focus target (nearest if much
  closer), tiebreak by (dist, enemy_adj - ally_adj). NO overextension skip, NO retreat.
- A/B vs naivefaa_opp.py AS BLUE (real match color), two 12-game bg runs:
    * v_aggro (NEW robot.py): run1 5W-4L-3T, run2 10W-2L-0T  => ~15-6-3 (~62% win).
    * cautious (old robot.py): 3W-5L of 8 (~37%). CLEAR improvement.
  Regression guard: v_aggro CRUSHES simple-bot both colors (26-1, 22-1). syntax OK.
- Backups: old cautious bot = /tmp/robot_cautious_backup.py. r1 aggressive = robot_r1_backup.py.
- *** WARNING for next teammate: the cautious/hold bot was built to beat aaoutkine__school-bot
  (a center-MASSER). v_aggro (pure aggro) may LOSE to school-bot again. IF the opponent
  changes back to school-bot or another center-masser, revert to /tmp/robot_cautious_backup.py.
  But vs naivefaa (a pursuer/chaser), AGGRO + focus-fire is far better. Match strategy to
  opponent type: CHASER => aggro; MASSER => cautious/hold.
- Next teammate: test vs naivefaa_opp.py AS BLUE (nohup bg, N=12; ~4s/game, N>=8 exceeds
  the 30s AGENT shell timeout). Any change must beat v_aggro's ~62% AS BLUE AND still
  crush simple-bot. Don't submit noise.

## Round 2 (opus-4-8, LATEST — CRITICAL FIX) — opponent = thesmilingturtl__naivefaa *** SWITCHED BACK TO CAUTIOUS+COHESION, NOW WINNING BOTH COLORS ***
- CRITICAL: /logs/rounds/1/results.json shows we LOST 58-163 as RED with the previous
  teammate's "v_aggro" bot. Their aggro bot was a MISTAKE — I re-tested it this round and
  it LOSES to naivefaa in BOTH colors (0-4 as Blue, ~1-4 as Red). Grinds down to few units.
- naivefaa = pure aggressive per-unit closest-enemy chaser (move toward closest enemy, attack
  if adjacent). NO focus-fire/retreat/cohesion/spawn-awareness. It NEVER wastes a turn.
- FIX: reverted to the CAUTIOUS/HOLD bot (/tmp/robot_cautious_backup.py = strict overextension
  filter `if th>su+1: continue`, only favorable trades, retreat when ganged & wounded) —
  it already beat naivefaa 8W-3L-1T/12 both colors (aggro lost both). THEN added a
  COHESION tiebreak to the advance loop: prefer tiles closest to ally centroid (ally_cx/cy
  computed in init_turn), sort key = (dist, th-su, cdist, th). This clusters our units so
  they GANG UP and win exchanges — directly exploits naivefaa's per-unit scattering.
- A/B RESULTS vs naivefaa_opp.py (ab.sh, 12 games, BOTH colors):
    * NEW cautious+cohesion robot.py: 11W-1L-0T then 11W-0L-1T (~92% win, repeatable).
    * cautious baseline (no cohesion): 8W-3L-1T.  aggro (prev bot): LOSES both colors.
  Regression guards PASS: simple-bot 4-0 (shutouts 35-0/26-0), chaser.js 4-0. ~2.5s/game,
  no errors/timeouts. syntax OK (ast.parse).
- DEPLOYED cautious+cohesion as robot.py. Backups: aggro(losing)=/tmp/robot_aggro_losing.py,
  cautious-no-cohesion=/tmp/robot_cautious_base.py, this bot=/tmp/v_cohesion.py.
- Next teammate: opponent is a CHASER — cautious+cohesion (gang up, don't overextend) beats
  it ~11/12. Test vs naivefaa_opp.py BOTH colors (ab.sh N=12 in background; ~2.5s/game).
  Baseline to beat: ~11/12. Any change must beat it REPEATABLY AND crush simple-bot.
  WARNING: if opponent changes to a center-MASSER (school-bot), the cautious filter is
  still fine (it holds), but re-test. Match strategy to opponent type.

## Round 3 (opus-4-8, THIS ACTUAL ROUND) — opponent = thesmilingturtl__naivefaa
- Round history: R0 opus was Blue, WON 172-45-33 (with older bot). R1 opus was Red,
  LOST 58-163 (the buggy "v_aggro" pure-aggro bot). R2 teammate deployed cautious+cohesion
  (v_cohesion) which is CURRENT robot.py.
- CONFIRMED opponent UNCHANGED (git show origin/human/thesmilingturtl/naivefaa:robot.py
  diffs clean vs naivefaa_opp.py). naivefaa = pure aggressive per-unit closest-enemy chaser
  (move toward closest enemy, attack if adjacent). NO focus-fire/retreat/cohesion/spawn-aware.
- IMPORTANT: verified color mapping empirically THIS round: in `./rumblebot run term A B`,
  the FIRST arg (A) = BLUE, SECOND arg (B) = RED. (Prior README note "first=Red" was WRONG.)
  "Units X Y" = Blue=X, Red=Y. ab.sh's win-counting is nonetheless CORRECT (it swaps args
  and the grep color each iteration consistently).
- TESTED current robot.py (cautious+cohesion) vs naivefaa_opp.py: 12-0 (ab.sh, both colors)!
  Both colors win convincingly: as Blue 6-2, as Red 7-2 typical margins. Regression guard:
  crushes simple-bot 24-0 (shutout). ~2.5s/game, no errors/timeouts. syntax OK.
- Backup of current bot: /workspace/robot_v_cohesion_backup.py (persistent, unlike /tmp).
- DECISION: kept the cautious+cohesion robot.py — it reliably wins BOTH colors 12-0 vs the
  actual opponent (fixing R1's loss). Strategy for CHASER opponents: cautious+cohesion
  (cluster, don't overextend `if th>su+1: continue`, gang up on weak enemies, retreat when
  ganged+wounded). WARNING: if opponent switches to a center-MASSER (aaoutkine school-bot),
  cautious hold is still OK but re-test both colors.

## Round 3 (opus-4-8, LATER entry) *** IMPROVED: ADDED GLOBAL FOCUS-FIRE TARGET ***
- Built on the cautious+cohesion bot by adding a GLOBAL `focus` target selected in
  init_turn = lowest-HP enemy nearest ally centroid. In the advance loop, if a unit is
  within walking_distance 6 of `focus`, it targets `focus` instead of its own nearest
  enemy. This makes the whole team converge on ONE weak enemy = faster kills, fewer ties.
- A/B vs naivefaa_opp.py (margin.sh, TWO 12-game runs each, both colors):
    * FOCUS variant (deployed): +47, +57 = +104/24, min per-game +1, NO TIES.
    * cautious+cohesion baseline: +42, +55 = +97/24, min per-game 0 (2 ties in run 1).
  Focus variant is consistently better AND reduces tie risk (ties score worse than wins).
- Final deployed-bot confirmation vs naivefaa (ab.sh, 10 games both colors): 9W-0L-1T.
- Regression guards PASS: simple-bot 27-1 (crush), chaser.js wins both colors (4-3 Blue,
  8-4 Red). syntax OK (ast.parse). ~2.5s/game, no errors/timeouts.
- Backups (persistent in /workspace): robot_v_cohesion_backup.py (prior cautious+cohesion),
  robot_r3_focus_backup.py (this deployed focus bot).
- Next teammate: opponent is a CHASER (naivefaa). Deployed bot = cautious+cohesion+focus-fire.
  Test vs naivefaa_opp.py both colors (ab.sh/margin.sh N=12 in background). Baseline to beat:
  ~+104/24 margin, min +1, no ties. WARNING: if opponent switches to a center-MASSER
  (school-bot), re-test — cautious hold is still OK but verify both colors.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = mario31313__alpha_13  *** IMPROVED BOT (BROADENED RETREAT) ***
- /logs/rounds/0/results.json: real opponent = **mario31313__alpha_13**, opus-4-8 (us, Red)
  WON 237-5-8. Extracted opp code (git show origin/human/mario31313/alpha_13:robot.py ->
  /tmp/alpha13.py). alpha_13 is a 13-line PURE AGGRESSIVE CHASER (nearly identical to
  naivefaa): each unit finds closest enemy; if dist==1 attack toward it, else move toward
  it. NO focus-fire, NO retreat, NO cohesion, NO spawn awareness. print()s each turn (own
  stdout noise, harmless). CHASER class => cautious+cohesion+focus-fire strategy applies.
- BASELINE (inherited R3 focus bot = /tmp/robot_baseline_alpha13.py) already beat alpha_13
  8-0 / 10-0, but margins were TIGHT: margin.sh 16 games = +48 (~+3/game), MIN per-game +0
  (a tie). Units grind down (final counts low).
- CHANGE MADE (deployed, robot.py): BROADENED THE RETREAT condition. Was: retreat only if
  2+ enemies adjacent AND health<=3 AND not killing. NOW ALSO retreat any wounded unit
  (health<=2) that can't secure a kill (enemy health>1), even in 1v1. One block change
  around line 53:
      not_killing = e.health>1
      if not_killing and ((len(adj)>=2 and unit.health<=3) or (unit.health<=2)):
          <retreat to a free tile with fewer adjacent enemies>
  Rationale: vs a pure chaser, keeping wounded units in melee just gets them killed;
  pulling them back preserves UNIT COUNT (the win condition) and lets them heal/re-engage
  with support.
- A/B RESULTS (margin.sh, TWO independent 16-game runs, both colors, vs /tmp/alpha13.py):
    * NEW (broadened retreat) robot.py: +229 then +215  (~+13.9/game, MIN per-game +4, NO ties).
    * OLD baseline robot.py:            +48               (~+3/game,   MIN per-game +0, 1 tie).
  ~4.5x the margin, MUCH higher & more consistent minimums, ZERO ties. Win-rate 10-0
  (ab.sh). Sample finals: 18-4, 19-6, 16-9, 15-6 units.
  Regression guards PASS: simple-bot 4-0 (shutout 28-0), chaser.js 4-0 (21-8). syntax OK
  (ast.parse). ~4s/game, no errors/timeouts.
- Backups (persistent in /workspace): robot_r1_alpha13_deployed_backup.py (this deployed bot).
  Prior baseline backed up at /tmp/robot_baseline_alpha13.py (also == robot_r3_focus_backup.py).
- DECISION: SUBMITTED the broadened-retreat robot.py. Strict, A/B-proven improvement:
  ~4.5x margin, no ties, no regression. This is the biggest single-tweak margin gain we've
  seen vs a chaser — retreating ALL wounded non-killing units (not just ganged ones)
  preserves unit count hugely against a bot with no retreat of its own.
- Next teammate: opponent is a CHASER. Test vs /tmp/alpha13.py both colors (ab.sh /
  margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py /tmp/alpha13.py 16 > /tmp/out.txt &
  ; ~4s/game so N>=8 exceeds the 30s AGENT shell timeout). Baseline to beat: ~+220/16
  (~+14/game), no ties. Any change must beat it REPEATABLY AND crush simple-bot.
  WARNING: if opponent switches to a center-MASSER (aaoutkine school-bot), the broadened
  retreat is likely still fine (cautious hold) but re-test both colors. NOTE: don't broaden
  retreat SO far that units never trade — this version still ATTACKS when healthy or
  securing a kill; it only retreats wounded units that can't kill.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = mario31313__alpha_13  *** IMPROVED: RETREAT TOWARD ALLY CENTROID ***
- Confirmed via /logs/rounds/0 (237-5-8) AND /logs/rounds/1 (249-1) results.json:
  opponent = mario31313__alpha_13, opus-4-8 WON both (Red R0, Blue R1). The R0->R1 jump
  came from the broadened-retreat upgrade (prior round). Opponent code UNCHANGED
  (git show origin/human/mario31313/alpha_13:robot.py diffs clean vs /tmp/alpha13.py):
  13-line PURE AGGRESSIVE CHASER (closest enemy; attack if dist==1 else move toward).
  NO focus-fire/retreat/cohesion/spawn-awareness. CHASER class => cautious+cohesion+focus.
- CHANGE MADE THIS ROUND (deployed, robot.py): improved the RETREAT tile selection.
  Was: retreat to the FIRST free neighbor with fewer adjacent enemies. NOW: among free
  neighbors with fewer adjacent enemies, pick the one minimizing (adjacent-enemies,
  distance-to-ally-centroid) — i.e. wounded units retreat TOWARD the team to regroup and
  re-engage with support, not just any lower-threat tile. ~7-line change in the retreat
  block (lines ~54-62).
- A/B RESULTS (margin.sh, TWO independent 16-game runs each, both colors, vs /tmp/alpha13.py):
    * NEW (retreat-toward-centroid) robot.py: +217 (min +9) then +247 (min +6)
      => +464/32 (~+14.5/game), min per-game +6, NO ties/losses (32-0).
    * OLD baseline (prior deployed):          +223 (min +5) then +212 (min +4)
      => +435/32 (~+13.6/game), min per-game +4.
  Variant is consistently better in BOTH total margin (+464 vs +435) AND worst-case
  minimum (min +6/+9 vs +4/+5) — reduces close-game/tie risk. Small but repeatable.
- Final deployed confirmation vs /tmp/alpha13.py (ab.sh, 6 games both colors): 6-0.
  Margins: 20-2, 18-5, 23-2, 18-8, 25-8, 19-5. Regression guards PASS: simple-bot 27-0
  shutout / 30-1, chaser.js 22-5 / 20-5. syntax OK (ast.parse). ~3.5-4s/game, no
  errors/timeouts.
- Backups (persistent in /workspace): robot_r2_alpha13_retreat_centroid_backup.py (this
  deployed bot). Prior baseline (broadened-retreat) = robot_r1_alpha13_deployed_backup.py
  (also /tmp/robot_r2_prev_baseline.py).
- DECISION: SUBMITTED the retreat-toward-centroid robot.py. Strict, A/B-proven small
  improvement (higher & more consistent margins, no regression). Consistent with the
  chaser strategy: cluster + focus-fire + retreat wounded units back toward the team.
- Next teammate: opponent is a CHASER. Test vs /tmp/alpha13.py both colors (margin.sh
  N=16 in BACKGROUND: nohup /tmp/margin.sh robot.py /tmp/alpha13.py 16 > /tmp/out.txt & ;
  ~4s/game so N>=8 exceeds the 30s AGENT shell timeout — poll with short sleeps).
  Baseline to beat: ~+464/32 (~+14.5/game), min +6, no ties. Any change must beat it
  REPEATABLY AND crush simple-bot. WARNING: if opponent switches to a center-MASSER
  (aaoutkine school-bot), re-test both colors (cautious hold likely still fine).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = underscore__bot1  (CHASER)
- /logs/rounds/0/results.json: real opponent = **underscore__bot1**, opus-4-8 (us, Red)
  WON 250-0. Extracted opp code (git show origin/human/underscore/bot1:robot.py ->
  /workspace/bot1_opp.py, /tmp/bot1.py). NOTE: the file defines robot() TWICE; the SECOND
  (later) def wins in Python, so the ACTIVE bot is a PURE per-unit CLOSEST-ENEMY CHASER:
      enemies=objs_by_team(other); closest=min(dist); dir=direction_to(closest)
      if dist==1: attack(dir) else: move(dir)
  (The first def — move East / attack South — is dead/overridden.) NO focus-fire, NO
  retreat, NO cohesion, NO spawn awareness. CHASER class => our cautious+cohesion+focus+
  retreat strategy applies (same class as naivefaa / mario31313 alpha_13).
- Tested current robot.py DIRECTLY vs bot1_opp.py: 6-0 (ab.sh, both colors). margin.sh
  16 games (both colors) = +234/16 (~+14.6/game), MIN per-game +8, NO ties/losses.
  Sample finals: 19-13, 15-8, 17-7, 21-7, 19-11, 27-7 units. ~4-5s/game, stderr CLEAN.
  Regression guard: simple-bot 4-0 (shutouts 23-1/24-0/34-0/25-0). syntax OK (ast.parse).
- EXPERIMENT THIS ROUND: raised the focus-target radius from <=6 to <=9 (converge on the
  weak enemy from farther). A/B margin.sh 16 games vs bot1: variant +206/16 (MIN +1) vs
  baseline +234/16 (MIN +8). WORSE in BOTH total and worst-case. DISCARDED, reverted.
- DECISION: kept proven robot.py UNCHANGED (cautious+cohesion+focus+retreat-toward-centroid,
  spawn-avoidance). Opponent (pure closest-enemy chaser, no focus-fire/retreat/cohesion/
  spawn-awareness) cannot beat us 6-0 (+14.6/game, no losses); only risk is self-inflicted
  regression (per all prior rounds' heuristic experiments being noise-neutral or worse).
  Baseline backup: /tmp/robot_baseline_bot1.py.
- Next teammate: opponent is a CHASER (per-unit closest-enemy). Test vs bot1_opp.py both
  colors (ab.sh N=6, margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py bot1_opp.py
  16 > /tmp/out.txt & ; ~4-5s/game so N>=~6 exceeds the 30s AGENT shell timeout — poll with
  sleeps). Baseline to beat: ~+234/16 (~+14.6/game), min +8, no ties. Any change must beat
  it REPEATABLY AND crush simple-bot. WARNING: if opponent switches to a center-MASSER
  (aaoutkine school-bot), re-test both colors (cautious hold likely still fine).

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = underscore__bot1 (CHASER)
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent = underscore__bot1,
  opus-4-8 WON 250-0 in BOTH rounds (Red R0, Blue R1). Total domination.
- Verified opponent code UNCHANGED: git show origin/human/underscore/bot1:robot.py diffs
  CLEAN vs saved bot1_opp.py. (Recap: file defines robot() twice; the SECOND def wins =
  pure per-unit CLOSEST-ENEMY CHASER: attack if dist==1 else move toward closest enemy.
  NO focus-fire/retreat/cohesion/spawn-awareness. CHASER class => our cautious+cohesion+
  focus+retreat-toward-centroid strategy crushes it.)
- Tested current robot.py DIRECTLY vs bot1_opp.py: won all games observed (both colors):
  Red-win 23-9, Blue-win 27-6, Red-win 14-9, Blue-win 23-6. Single game Blue 21-8 (~5.4s).
  Regression guard: simple-bot 4-0 (crushing shutouts 29-2/27-2/30-1/25-1). syntax OK
  (ast.parse), ~5.4s/game (well under 60s), no errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED (cautious+cohesion+focus+retreat-toward-centroid
  + spawn-avoidance). Opponent cannot beat us 250-0 (+14.6/game per prior A/B, no losses);
  only risk is self-inflicted regression. Prior round's focus-radius-9 experiment already
  REGRESSED (+234 -> +206), consistent with all prior rounds. Submit as-is.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = lanity__sivuy  (CHASER)
- /logs/rounds/0/results.json: real opponent = **lanity__sivuy**, opus-4-8 (us, Blue)
  WON 250-0. Extracted opp code (git show origin/human/lanity/sivuy:robot.py ->
  /tmp/sivuy.py, saved /workspace/sivuy_opp.py). It is a 15-line PURE per-unit
  CLOSEST-ENEMY CHASER (IDENTICAL class to naivefaa / mario31313 alpha_13 / underscore bot1):
      enemies = state.objs_by_team(state.other_team)
      closest = min(enemies, key=dist to unit); dir = direction_to(closest)
      if dist==1: attack(dir) else: move(dir)
  NO focus-fire, NO retreat, NO cohesion, NO spawn awareness. CHASER class => our
  cautious+cohesion+focus+retreat-toward-centroid + spawn-avoidance strategy crushes it.
- Tested current robot.py DIRECTLY vs sivuy_opp.py: 6-0 (ab.sh, both colors). Crushing
  ~3x unit-count margins: Blue 21-7, 25-7, 28-4; Red 19-5, 19-5, 24-6. margin.sh 16 games
  (both colors) = +213/16 (~+13.3/game), MIN per-game +6, NO ties/losses (16-0).
  Regression guard: simple-bot 4-0 (shutouts 26-0/28-0/32-0/26-0). ~5s/game (well under
  60s), stderr CLEAN (no errors/timeouts). syntax OK (ast.parse).
- DECISION: kept proven robot.py UNCHANGED (cautious+cohesion+focus+retreat-toward-centroid
  + spawn-avoidance from prior chaser rounds). Opponent (pure closest-enemy chaser, no
  focus-fire/retreat/cohesion/spawn-awareness) cannot beat us 6-0 (+13.3/game, no losses);
  only risk is self-inflicted regression (per all prior rounds' heuristic experiments being
  noise-neutral or worse). Baseline backup: robot_r2_alpha13_retreat_centroid_backup.py.
- Next teammate: opponent is a CHASER (same class as naivefaa/alpha_13/bot1). Test vs
  sivuy_opp.py both colors (ab.sh N=6, margin.sh N=16 in BACKGROUND: nohup ./margin.sh
  robot.py sivuy_opp.py 16 > /tmp/out.txt & ; ~5s/game so N>=~5 exceeds the 30s AGENT shell
  timeout — poll with sleeps). Baseline to beat: ~+213/16 (~+13.3/game), min +6, no ties.
  Any change must beat it REPEATABLY AND crush simple-bot. WARNING: if opponent switches to
  a center-MASSER (aaoutkine school-bot), re-test both colors (cautious hold likely still fine).

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest) — opponent = lanity__sivuy (CHASER)
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent = lanity__sivuy,
  opus-4-8 (Blue) WON 250-0 in BOTH rounds. Total domination.
- Verified opponent code UNCHANGED: git show origin/human/lanity/sivuy:robot.py diffs CLEAN
  vs saved sivuy_opp.py. (15-line PURE per-unit CLOSEST-ENEMY CHASER: attack if dist==1 else
  move toward closest enemy. NO focus-fire/retreat/cohesion/spawn-awareness. Same CHASER
  class as naivefaa/alpha_13/bot1. Our cautious+cohesion+focus+retreat-toward-centroid +
  spawn-avoidance crushes it.)
- Verified current robot.py (78 lines, compact) == robot_r2_alpha13_retreat_centroid_backup.py
  (the proven chaser bot). syntax OK (ast.parse), sig `def robot(state,unit)` line 33.
- Tested current robot.py DIRECTLY vs sivuy_opp.py: 6-0 (ab.sh, both colors, background run).
  Crushing ~3x margins: Blue 19-6/22-6/22-8, Red 23-9/25-4. Regression guard: simple-bot
  4-0 (shutout 27-2). ~4-5s/game, no errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us 6-0 / 250-0; only risk
  is self-inflicted regression (per all prior rounds' heuristic experiments being
  noise-neutral or worse — prior round's focus-radius-9 tweak already REGRESSED +234->+206).
  Submit as-is. Next teammate: opponent is a CHASER; test vs sivuy_opp.py both colors
  (ab.sh N=6 in BACKGROUND — 30s AGENT shell timeout). Baseline: 6-0, ~+13/game.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = mee42__follow-bot (CHASER)
- /logs/rounds/0/results.json: real opponent = **mee42__follow-bot**, opus-4-8 (us, Red)
  WON 250-0. Extracted opp code (git show origin/human/mee42/follow-bot:robot.py ->
  /workspace/follow_opp.py, /tmp/follow.py). follow-bot is a CHASER-class bot with a small
  twist: if ANY enemy is adjacent (walking_dist==1), it attacks the LOWEST-HEALTH adjacent
  enemy (basic focus-fire on adjacents); otherwise it moves toward the CLOSEST enemy.
  NO retreat, NO cohesion, NO spawn awareness, NO pursuit-focus (only focuses among already-
  adjacent enemies). Same CHASER class as naivefaa/alpha_13/bot1/sivuy — our
  cautious+cohesion+focus+retreat-toward-centroid + spawn-avoidance strategy crushes it.
- Tested current robot.py DIRECTLY vs follow_opp.py: 8-0 (ab.sh, both colors). Crushing
  ~3x unit-count margins: Red-win 20-5, 22-6, 13-10, 18-8; Blue-win 20-7, 26-6, 23-5, 17-7.
  Regression guard: simple-bot 4-0 (shutouts 29-0/23-1/20-1/26-0). ~4-5s/game, stderr CLEAN
  (no errors/timeouts). syntax OK (ast.parse), sig `def robot(state,unit)` line 33.
- DECISION: kept proven robot.py UNCHANGED (cautious+cohesion+focus+retreat-toward-centroid
  + spawn-avoidance from prior chaser rounds). Opponent (chaser with adjacent focus-fire only,
  no retreat/cohesion/spawn-awareness) cannot beat us 8-0; only risk is self-inflicted
  regression (per all prior rounds' heuristic experiments being noise-neutral or worse).
- Next teammate: opponent is a CHASER. Test vs follow_opp.py both colors (ab.sh N=8 in
  BACKGROUND: nohup ./ab.sh robot.py follow_opp.py 8 > /tmp/out.txt & ; ~4-5s/game so N>=6
  exceeds the 30s AGENT shell timeout — poll with sleeps). Baseline: 8-0, ~3x margin. Any
  change must beat it REPEATABLY AND crush simple-bot. WARNING: if opponent switches to a
  center-MASSER (aaoutkine school-bot), re-test both colors (cautious hold likely still fine).

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = mee42__follow-bot (CHASER)
- Confirmed via /logs/rounds/0 (250-0) AND /logs/rounds/1 (248-1-1) results.json:
  opponent = mee42__follow-bot, opus-4-8 (Red both rounds) WON both. R1 had 1 loss +
  1 tie of 250 (extreme variance — the "competent chaser" tail).
- Verified opponent code UNCHANGED: git show origin/human/mee42/follow-bot:robot.py diffs
  CLEAN vs saved follow_opp.py. (Recap: CHASER-class — if any enemy adjacent, attack the
  LOWEST-HP adjacent enemy; else move toward CLOSEST enemy. NO retreat/cohesion/spawn-
  awareness/pursuit-focus. Same class as naivefaa/alpha_13/bot1/sivuy. Our cautious+
  cohesion+focus+retreat-toward-centroid + spawn-avoidance crushes it.)
- Tested current robot.py DIRECTLY vs follow_opp.py: ab.sh 4-0 (both colors), crushing ~3x
  margins (22-5, 21-6, 19-5, 24-6). margin.sh 16 games (both colors) = +258/16 (~+16.1/game),
  MIN per-game +5, NO ties/losses (16-0). Regression guard: simple-bot shutouts 24-0/29-0
  (both colors). ~4-5s/game (well under 60s), stderr CLEAN, syntax OK (ast.parse).
- DECISION: kept proven robot.py UNCHANGED (backup /tmp/robot_baseline_follow.py). Opponent
  cannot beat us (+16/game, no losses in 16 games this round); only risk is self-inflicted
  regression (per all prior rounds' heuristic experiments being noise-neutral or worse —
  e.g. prior focus-radius-9 tweak REGRESSED +234->+206). The rare R1 loss/tie per 250 is
  extreme variance no tweak has reliably fixed against this bot class.
- Next teammate: opponent is a CHASER. Test vs follow_opp.py both colors (ab.sh N=4-6,
  margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py follow_opp.py 16 > /tmp/out.txt &
  ; ~4-5s/game so N>=~6 exceeds the 30s AGENT shell timeout — poll with sleeps). Baseline to
  beat: ~+258/16 (~+16/game), min +5, no ties. Any change must beat it REPEATABLY AND crush
  simple-bot. WARNING: if opponent switches to a center-MASSER (aaoutkine school-bot), re-test
  both colors (cautious hold likely still fine).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = anton__om-om (JS CHASER)
- /logs/rounds/0/results.json: real opponent = **anton__om-om**, opus-4-8 (us, Blue)
  WON 250-0. Opponent submits JavaScript (robot.js). Extract via:
      git show remotes/origin/human/anton/om-om:robot.js > /workspace/omom_opp.js
  (NOTE: use `git show`'s stdout redirect directly; do NOT cp/cat-mangle it — a mangled
  copy caused a spurious JS SyntaxError in my first test.)
- om-om is a TRIVIAL per-unit CLOSEST-ENEMY CHASER (identical class to naivefaa/alpha_13/
  bot1/sivuy/follow-bot): enemies=objsByTeam(otherTeam); closest=minBy(dist);
  dir=directionTo(closest); if dist==1 attack(dir) else move(dir). NO focus-fire, NO
  retreat, NO cohesion, NO spawn awareness. CHASER class => our cautious+cohesion+focus+
  retreat-toward-centroid + spawn-avoidance strategy crushes it.
- Tested current robot.py DIRECTLY vs omom_opp.js: 6-0 (ab.sh, both colors). Crushing ~3x
  unit-count margins: Blue-win 30-6, 26-5, 15-7, 19-9; Red-win 16-9, 26-7, 24-6. ~5s/game,
  stderr CLEAN (no errors/timeouts). Regression guard: simple-bot 4-0 (shutouts 28-1/26-0/
  27-1/32-0). syntax OK (ast.parse), sig `def robot(state,unit)` line 33.
- DECISION: kept proven robot.py UNCHANGED (cautious+cohesion+focus+retreat-toward-centroid
  + spawn-avoidance from prior chaser rounds). Opponent (pure closest-enemy chaser, no
  focus-fire/retreat/cohesion/spawn-awareness) cannot beat us 6-0; only risk is
  self-inflicted regression (per all prior rounds' heuristic experiments being noise-neutral
  or worse). Backup: robot_r2_alpha13_retreat_centroid_backup.py.
- Next teammate: opponent is a CHASER (JS). Test vs omom_opp.js both colors (ab.sh N=6 in
  BACKGROUND: nohup ./ab.sh robot.py omom_opp.js 6 > /tmp/out.txt & ; ~5s/game so N>=~5
  exceeds the 30s AGENT shell timeout — poll with sleeps). Baseline: 6-0, ~3x margin. Any
  change must beat it REPEATABLY AND crush simple-bot. WARNING: if opponent switches to a
  center-MASSER (aaoutkine school-bot), re-test both colors (cautious hold likely still fine).

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest) — opponent = anton__om-om (JS CHASER)
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent = anton__om-om,
  opus-4-8 WON 250-0 in BOTH rounds (Blue R0, Red R1). Total domination.
- Verified opponent code UNCHANGED: git show remotes/origin/human/anton/om-om:robot.js
  diffs CLEAN vs saved omom_opp.js. (Trivial per-unit CLOSEST-ENEMY CHASER: attack if
  dist==1 else move toward closest enemy. NO focus-fire/retreat/cohesion/spawn-awareness.
  Same CHASER class as naivefaa/alpha_13/bot1/sivuy/follow. Our cautious+cohesion+focus+
  retreat-toward-centroid + spawn-avoidance crushes it.)
- Tested current robot.py DIRECTLY vs omom_opp.js: WIN both colors. As Blue: 17-9 units.
  As Red (opp Blue): 30-3 units (crushing ~10x). ~5-6s/game, stderr CLEAN, no errors/timeouts.
  Regression guard: simple-bot shutout 24-1. syntax OK (ast.parse).
- DECISION: kept proven robot.py UNCHANGED (cautious+cohesion+focus+retreat-toward-centroid
  + spawn-avoidance). Opponent cannot beat us 250-0; only risk is self-inflicted regression
  (per all prior rounds' heuristic experiments being noise-neutral or worse). Submit as-is.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = aaoutkine__silo34 (SWARM / whole-team focus-chaser)
- /logs/rounds/0/results.json: real opponent = **aaoutkine__silo34**, opus-4-8 (us, Blue)
  WON 249-1. Extracted opp code (git show origin/human/aaoutkine/silo34:robot.py ->
  /tmp/silo34.py, saved /workspace/silo34_opp.py).
- silo34 is a SWARM bot (whole-team focus-chaser, same class as tabaxi3k/charles &
  devchris/first_test): init_turn picks ONE global "swarm" target = the enemy minimizing
  the MEAN walking distance to all our (its) units; EVERY unit then chases that single
  target (attacks it if adjacent in the direction toward it, else moves toward it with a
  simple target-tile MOVEPLAN anti-collision that rotates CW if blocked; falls back to
  attacking any other adjacent enemy if it can't reach). Re-picks a new swarm target when
  the current one dies. WEAKNESSES vs us: NO health-based focus-fire / kill-securing
  (attacks the swarm target or a fallback adjacent, not lowest-HP), NO retreat when
  wounded, NO cohesion beyond swarming one target, NO spawn awareness, and it OVER-COMMITS
  the whole team onto one enemy. Also print()s a lot (Order/moveplan debug — own stdout
  noise, harmless to us). Our cautious+cohesion+focus+retreat-toward-centroid +
  spawn-avoidance strategy crushes it.
- Tested current robot.py DIRECTLY vs silo34_opp.py: 6-0 (ab.sh, both colors). Crushing
  ~3x unit-count margins: Blue-win 23-5, 21-16, 31-14; Red-win 27-8, 22-10, 23-9.
  Regression guard: simple-bot shutout 23-0. ~5-6s/game (well under 60s), stderr CLEAN
  (no errors/timeouts). syntax OK (ast.parse).
- DECISION: kept proven robot.py UNCHANGED (cautious+cohesion+focus+retreat-toward-centroid
  + spawn-avoidance from prior chaser rounds). Opponent (whole-team swarm focus-chaser,
  over-commits, no health-focus-fire/retreat/cohesion/spawn-awareness) cannot beat us 6-0
  (~3x margin, no losses); only risk is self-inflicted regression (per all prior rounds'
  heuristic experiments being noise-neutral or worse). Backup:
  robot_r2_alpha13_retreat_centroid_backup.py.
- Next teammate: opponent is a SWARM/focus-chaser. Test vs silo34_opp.py both colors
  (ab.sh N=6 in BACKGROUND: nohup ./ab.sh robot.py silo34_opp.py 6 > /tmp/out.txt & ;
  ~5-6s/game so N>=~5 exceeds the 30s AGENT shell timeout — poll with sleeps). Baseline:
  6-0, ~3x margin. Any change must beat it REPEATABLY AND crush simple-bot. WARNING: if
  opponent switches to a center-MASSER (aaoutkine school-bot — note aaoutkine authored
  BOTH silo34 and school-bot!), re-test both colors and consider the cautious/hold bot.

## Round 3 (opus-4-8, THIS ACTUAL ROUND) — opponent = aaoutkine__silo34 (SWARM focus-chaser)
- Confirmed via /logs/rounds/0 (249-1) AND /logs/rounds/1 (250-0) results.json: opponent =
  aaoutkine__silo34, opus-4-8 WON both (Blue R0, Red R1). Total domination.
- Verified opponent code UNCHANGED: git show origin/human/aaoutkine/silo34:robot.py diffs
  CLEAN vs saved silo34_opp.py. (Recap: SWARM whole-team focus-chaser — init_turn picks ONE
  global target = enemy min MEAN walking dist to its units; every unit chases it (attack if
  adjacent else move with CW-rotate anti-collision, fallback attack any adjacent). NO
  health-focus-fire, NO retreat, NO cohesion beyond swarming, NO spawn awareness,
  over-commits. Our cautious+cohesion+focus+retreat-toward-centroid + spawn-avoidance crushes it.)
- Verified current robot.py == robot_r2_alpha13_retreat_centroid_backup.py (proven bot).
  syntax OK (ast.parse), sig `def robot(state,unit)` line 33.
- Tested current robot.py DIRECTLY vs silo34_opp.py: 6-0 (ab.sh, both colors). Crushing
  ~3x unit-count margins: Blue-win 27-7, 26-7, 25-6, 21-7; Red-win 19-14, 28-9, 29-3.
  Regression guard: simple-bot shutout 26-0. ~5-6s/game (well under 60s), stderr CLEAN.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us 6-0 / 249-1 / 250-0;
  only risk is self-inflicted regression (per all prior rounds' heuristic experiments being
  noise-neutral or worse — e.g. prior focus-radius-9 tweak REGRESSED +234->+206). Submit as-is.
- Next teammate: opponent is a SWARM/focus-chaser. Test vs silo34_opp.py both colors
  (ab.sh N=6 in BACKGROUND; ~5-6s/game so N>=~5 exceeds 30s AGENT shell timeout — poll w/
  sleeps). Baseline: 6-0, ~3x margin. WARNING: aaoutkine authored BOTH silo34 AND school-bot
  (a center-MASSER our aggro loses to). If opponent switches to school-bot, re-test both
  colors and consider the cautious/hold bot (/tmp/robot_hold.py logic).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = mountain__neuralbot4-3h  *** IMPROVED: LOOSENED OVEREXTENSION ***
- /logs/rounds/0/results.json: real opponent = **mountain__neuralbot4-3h**, opus-4-8 (us,
  Blue) WON 242-5-3 (tighter than the near-shutouts vs neuralbot1/2). Extracted opp code
  (git show remotes/origin/human/mountain/neuralbot4-3h:robot.py -> /workspace/neuralbot4_opp.py).
- neuralbot4-3h = base62-encoded feed-forward NEURAL NET (12->..->9, tanh) w/ shared_state
  memory, PLUS hard-coded BORDER-BOUNCE rules (units on the map edge/diagonals move back
  toward center). Per unit: (1) border-bounce move if on an edge; (2) attack closest enemy
  ONLY if dist==1 AND unit.health >= that enemy's health (CAUTIOUS — like fruity); (3) else
  the NN picks a MOVE direction (NO attack — often "attacks air" never, just wanders toward
  NN-chosen enterable tile). WEAKNESSES: NN movement is essentially untrained/wandering, NO
  focus-fire, NO retreat, NO cohesion, and crucially it WON'T attack our HEALTHIER units.
- CHANGE MADE (deployed, robot.py): LOOSENED the advance-loop overextension filter from
  `if th>su+1: continue` to `if th>su+2: continue`. Rationale: neuralbot4 wanders & only
  attacks when it's the healthier unit, so stepping adjacent to 2 enemies is far less risky
  than vs a real aggro chaser — we can close on the wandering blob faster and finish games
  (fewer ties). ONE-line change. Backup of baseline: /tmp/robot_baseline_nb4.py.
- A/B (margin.sh, TWO independent 16-game runs each, both colors, vs neuralbot4_opp.py):
    * v1 (loosened, DEPLOYED): +221 (min +4) then +156 (min +2) => +377/32 (~+11.8/game), ZERO ties.
    * baseline (th>su+1):       +134 (min +0, 1 TIE)             => (~+8.4/game), 1 tie.
  v1 is clearly better: ~40% higher margin AND eliminated ties (ties score worse than wins —
  directly targets the 3 ties in the 242-5-3 result). Win-rate vs neuralbot4 5-0-1 (ab.sh).
  Regression guards PASS: simple-bot 4-0 (27-1/28-1/26-1/31-0 shutouts), chaser.js (see below).
  syntax OK (ast.parse). ~5s/game, no errors/timeouts.
- Backup of deployed bot (persistent): /workspace/robot_r1_nb4_loosen_backup.py.
  Prior baseline (th>su+1) = /tmp/robot_baseline_nb4.py (also == robot_r2_alpha13_retreat_centroid_backup.py).
- DECISION: SUBMITTED v1 (loosened overextension). A/B-proven higher margin, zero ties, no
  regression. WARNING: the loosened filter is tuned for a WANDERING/cautious opponent that
  won't punish overextension. If opponent switches to a real AGGRO CHASER (naivefaa/alpha_13)
  or center-MASSER (school-bot), REVERT to the stricter `th>su+1` baseline
  (/tmp/robot_baseline_nb4.py / robot_r2_alpha13_retreat_centroid_backup.py) and re-test.
- Next teammate: test vs neuralbot4_opp.py both colors (margin.sh N=16 in BACKGROUND: nohup
  ./margin.sh robot.py neuralbot4_opp.py 16 > /tmp/out.txt & ; ~5s/game so N>=~6 exceeds the
  30s AGENT shell timeout — poll w/ sleeps). Baseline to beat: ~+377/32 (~+12/game), no ties.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest entry) — opponent = mountain__neuralbot4-3h
- Confirmed via /logs/rounds/0 (242-5-3) AND /logs/rounds/1 (239-7-4) results.json:
  opponent = mountain__neuralbot4-3h, opus-4-8 (Blue both rounds) WON both. Both rounds
  had a few losses+ties per 250 (the "wandering NN + border-bounce" tail variance).
- Verified opponent code UNCHANGED: git show remotes/origin/human/mountain/neuralbot4-3h:robot.py
  diffs CLEAN vs saved neuralbot4_opp.py. Re-read opp: border-bounce moves on edges;
  attacks closest enemy ONLY if dist==1 AND unit.health >= that enemy's health (i.e. the
  enemy hits us only when ITS health >= OUR unit's health); otherwise untrained NN wanders.
  NO focus-fire, NO retreat, NO cohesion. Current robot.py = loosened-overextension
  (th>su+2) + cohesion + focus + retreat-toward-centroid + spawn-avoidance.
- BASELINE margin (margin.sh, TWO independent 16-game runs, both colors): +211 (all wins,
  min +3) then +130 (1 tie + 1 loss, min -2) => +341/32 (~+10.7/game). Margins are NOISY
  (±40 over 16). Regression guards PASS: simple-bot 29-1 shutout, chaser.js 25-4.
- EXPERIMENTS THIS ROUND (both A/B'd vs neuralbot4_opp.py, 16 games, both colors):
    * V1 = don't retreat if an ally is also adjacent to the enemy (cA>=1) to co-secure the
      kill: DISASTROUS, +211 -> -1/16 (multiple losses). Wounded units in 2+ enemy contact
      die. DISCARDED.
    * V2 = also retreat at health<=3 in 1v1 when enemy health >= our health (enemy will keep
      hitting us): +153/16 (1 loss). Within noise-to-WORSE than baseline's +341/32 avg.
      Over-retreating means we don't finish enough enemies. DISCARDED.
  Consistent with ALL prior rounds: heuristic tweaks are noise-neutral or worse.
- DECISION: kept proven robot.py UNCHANGED (== robot_r1_nb4_loosen_backup.py ==
  /tmp/robot_baseline_r2.py). Opponent cannot beat us (~+10.7/game); the few losses/ties
  per 250 are extreme variance no tweak reliably fixed. Only risk is self-inflicted
  regression. syntax OK (ast.parse), ~4-5s/game (well under 60s), no errors/timeouts.
- Next teammate: opponent is a WANDERING NN (cautious attack: only hits when healthier;
  border-bounce). Test vs neuralbot4_opp.py both colors (margin.sh N=16 in BACKGROUND:
  nohup ./margin.sh robot.py neuralbot4_opp.py 16 > /tmp/out.txt & ; ~4-5s/game so N>=~6
  exceeds the 30s AGENT shell timeout — poll w/ sleeps). Baseline to beat: ~+340/32
  (~+10.7/game) — NOISY, run 2+ times. Any change must beat it REPEATABLY AND crush
  simple-bot. WARNING: the loosened th>su+2 filter is tuned for this wandering/cautious
  opp; if opponent switches to a real AGGRO CHASER (naivefaa/alpha_13) or center-MASSER
  (school-bot), REVERT to stricter th>su+1 (robot_r2_alpha13_retreat_centroid_backup.py).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = ketza__arthur (SWARM focus-chaser)  *** IMPROVED: REVERTED TO STRICT th>su+1 ***
- /logs/rounds/0/results.json: real opponent = **ketza__arthur**, opus-4-8 (us, Blue) WON
  249-1. Extracted opp code (git show origin/human/ketza/arthur:robot.py -> /workspace/arthur_opp.py).
- arthur is a SWARM whole-team focus-chaser (same class as tabaxi3k/charles & silo34):
  init_turn picks ONE global target = enemy minimizing SUM of distances to all our (its)
  units; EVERY unit attacks its CLOSEST adjacent enemy if adjacent, else moves toward the
  shared target (attack if adjacent). NO health-focus-fire, NO retreat, NO cohesion, NO
  spawn awareness, over-commits whole team. Our cautious+cohesion+focus+retreat crushes it.
- KEY CHANGE: the inherited robot.py had a LOOSENED overextension filter `if th>su+2:
  continue` (tuned last round for mountain neuralbot4, a WANDERING NN). arthur is a
  SWARM/CHASER, so I REVERTED to the stricter `if th>su+1: continue` (never step adjacent
  where enemies > allies+1). Per the standing rule: CHASER/SWARM => strict; WANDERING NN => loose.
- A/B RESULTS (margin.sh, TWO independent 16-game runs each, both colors, vs arthur_opp.py):
    * STRICT (th>su+1, DEPLOYED): +206 then +189 => +395/32 (~+12.3/game), no losses/ties.
    * LOOSE (th>su+2, inherited):  +170 then +184 => +354/32 (~+11.1/game), no losses/ties.
  Strict beat loose in BOTH runs (repeatable ~+1.2/game gain). Win-rate vs arthur 8-0
  (ab.sh, both colors). Regression guards PASS: simple-bot 27-2, chaser.js 20-5. syntax OK.
- DEPLOYED strict robot.py. Backup: robot_r1_arthur_strict_backup.py. Loose (prev) =
  robot_r1_nb4_loosen_backup.py. Strict base also == robot_r2_alpha13_retreat_centroid_backup.py.
- Next teammate: opponent is a SWARM/focus-chaser => keep STRICT th>su+1. Test vs
  arthur_opp.py both colors (margin.sh N=16 in BACKGROUND; ~4-5s/game, N>=6 exceeds 30s
  AGENT shell timeout — poll w/ sleeps). Baseline to beat: ~+395/32 (~+12/game), no ties.
  WARNING: if opponent switches to a WANDERING NN (mountain neuralbot4) loosen to th>su+2;
  if a center-MASSER (aaoutkine school-bot) re-test both colors.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest entry) — opponent = ketza__arthur (SWARM focus-chaser)
- Confirmed via /logs/rounds/0 (249-1) AND /logs/rounds/1 (250-0) results.json: opponent =
  ketza__arthur, opus-4-8 WON both (Blue R0, Red R1). Total domination.
- Verified opponent code UNCHANGED: git show origin/human/ketza/arthur:robot.py diffs CLEAN
  vs saved arthur_opp.py. Verified current robot.py == robot_r1_arthur_strict_backup.py
  (the deployed STRICT th>su+1 bot). syntax OK (ast.parse). Overext filter line 72:
  `if th>su+1: continue  # strict: swarm/chaser opp (arthur)`.
- Recap: arthur = SWARM whole-team focus-chaser; picks ONE global target = enemy min SUM of
  dists to its units; every unit attacks CLOSEST adjacent enemy if adjacent else moves toward
  the shared target. NO health-focus-fire, NO retreat, NO cohesion, NO spawn awareness,
  over-commits whole team. Our cautious+cohesion+focus+retreat-toward-centroid +
  spawn-avoidance (strict th>su+1) crushes it.
- Tested current robot.py DIRECTLY vs arthur_opp.py: WIN both colors. As Blue (us first arg):
  20-5 units. As Red (us second arg, opp Blue): 16-8 units. ~few s/game, stderr CLEAN
  (no errors/timeouts).
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us 249-1 / 250-0; only risk
  is self-inflicted regression (per ALL prior rounds' heuristic experiments being
  noise-neutral or worse — e.g. loose th>su+2 REGRESSED vs arthur last round). Keep STRICT
  th>su+1 for this SWARM/CHASER opponent. Submit as-is.
- Next teammate: opponent is a SWARM/focus-chaser => KEEP STRICT th>su+1. WARNING: if opponent
  switches to a WANDERING NN (mountain neuralbot4) loosen to th>su+2; if a center-MASSER
  (aaoutkine school-bot) re-test both colors (cautious/hold logic in /tmp/robot_hold.py).

## Round 1 (opus-4-8, THIS ACTUAL ROUND, latest) — opponent = mkap__test (SIMPLE per-unit chaser)
- /logs/rounds/0/results.json: real opponent = **mkap__test**, opus-4-8 WON 250-0 (we were Blue).
- Extracted opp code -> /workspace/mkap_opp.py. mkap = a SIMPLE per-unit closest-enemy chaser:
  each unit independently (1) steps off spawn tiles on danger turns (turn%10==0), (2) attacks
  any adjacent enemy (first orthogonal dir), else (3) moves toward its OWN closest enemy
  (fallback to any free tile if blocked). NO focus-fire, NO health targeting, NO retreat,
  NO cohesion, NO outnumber-avoidance, NO global coordination. Weak SWARM/CHASER class
  (same family as arthur but even simpler). Our strict bot crushes it.
- Verified current robot.py == robot_r1_arthur_strict_backup.py (deployed STRICT th>su+1),
  syntax OK (ast.parse). Overext filter: `if th>su+1: continue`.
- TESTED current robot.py DIRECTLY vs mkap_opp.py: WIN 10-0 both colors (test_bot.sh N=10),
  single game as Blue 24-12 units, ~5.6s/game (well under 60s), no errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED. Opponent is a simple chaser we beat 250-0 / 10-0;
  per ALL prior rounds, the only risk here is self-inflicted regression from tweaks. Submit as-is.
- Next teammate: opponent is a SIMPLE SWARM/CHASER => KEEP STRICT th>su+1. Test vs mkap_opp.py
  (test_bot.sh / margin.sh, both colors; ~5s/game so N>=6 exceeds the 30s AGENT shell timeout —
  run in BACKGROUND w/ nohup and poll w/ short sleeps). WARNING: if opponent switches to a
  WANDERING NN (mountain neuralbot4) loosen to th>su+2; center-MASSER (school-bot) re-test both colors.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest entry) — opponent = mkap__test (SIMPLE per-unit chaser)
- Confirmed via /logs/rounds/0 (250-0) AND /logs/rounds/1 (248-1-1) results.json: opponent =
  mkap__test, opus-4-8 WON both (Blue R0, Red R1). Total domination.
- Verified opponent code FUNCTIONALLY UNCHANGED: git show origin/human/mkap/test:robot.py
  diffs vs saved mkap_opp.py only in a trailing comment/whitespace (logic identical). mkap =
  SIMPLE per-unit closest-enemy chaser: (1) step off spawn tiles on danger turns (turn%10==0),
  (2) attack any adjacent enemy (first orthogonal dir), else (3) move toward its OWN closest
  enemy (fallback any free tile). NO focus-fire/health-targeting/retreat/cohesion/outnumber-
  avoidance/global-coordination. Weak SWARM/CHASER class. Our strict bot crushes it.
- Verified current robot.py == robot_r1_arthur_strict_backup.py (deployed STRICT th>su+1 bot),
  syntax OK (ast.parse).
- TESTED current robot.py DIRECTLY vs mkap_opp.py: 6-0 (ab.sh, both colors). Crushing ~3x
  unit-count margins: Blue-win 21-6/23-9/22-5/23-9, Red-win 21-9/18-8/24-6. ~5s/game (well
  under 60s), no errors/timeouts. Regression guard: simple-bot crush 27-2.
- DECISION: kept proven robot.py UNCHANGED. Opponent cannot beat us 6-0 / 250-0 / 248-1-1;
  only risk is self-inflicted regression (per ALL prior rounds' heuristic experiments being
  noise-neutral or worse). Submit as-is. KEEP STRICT th>su+1 for this SIMPLE CHASER opponent.
- Next teammate: opponent is a SIMPLE SWARM/CHASER => KEEP STRICT th>su+1. Test vs mkap_opp.py
  (ab.sh N=6 in BACKGROUND: nohup ./ab.sh robot.py mkap_opp.py 6 > /tmp/out.txt & ; ~5s/game
  so N>=6 exceeds the 30s AGENT shell timeout — poll w/ sleeps). WARNING: if opponent switches
  to a WANDERING NN (mountain neuralbot4) loosen to th>su+2; center-MASSER (school-bot) re-test.

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = essickmango__pickle-up (weak/passive chaser)
- /logs/rounds/0/results.json: real opponent = **essickmango__pickle-up**, opus-4-8 (us, Red)
  WON 207-33-10 (competent-opp class — some losses/ties per 250). Extracted opp code
  (git show origin/human/essickmango/pickle-up:robot.py -> /tmp/pickle.py, saved
  /workspace/pickle_opp.py).
- pickle-up is a QUIRKY, PASSIVE chaser: it targets `min(enemies)` = the LOWEST-ID enemy
  (NOT nearest!), computes move_direction toward it, and MOVES that way. It ONLY attacks
  when move_direction is BLOCKED (target tile occupied) AND only enemies with HEALTH<=2
  (picks the lowest-HP among blocked-direction adjacents). So it barely damages HEALTHY
  units — it rarely attacks at all, just marches toward the lowest-ID enemy. NO real
  focus-fire, NO retreat, NO cohesion, NO spawn awareness. Whole team converges on one
  (lowest-ID) target. Our cautious+cohesion+focus+retreat-toward-centroid + spawn-avoidance
  (STRICT th>su+1) crushes it.
- TESTED current robot.py (STRICT th>su+1 baseline) DIRECTLY vs pickle_opp.py:
    * ab.sh 8 games (both colors): 7W-1L. Margins ~3x unit count (13-10, 14-9, 15-8, 19-3).
    * margin.sh two 12-game runs: +135/12 (min +3, NO losses) and +85/12. Avg ~+9/game.
  Regression guard: simple-bot 4-0 (shutouts 27-1/22-0/28-0/31-1). ~4-5s/game, syntax OK.
- EXPERIMENT THIS ROUND: LOOSENED overextension filter to th>su+2 (since pickle rarely
  attacks). A/B margin.sh two 12-game runs: LOOSE +147/12 (had a -6 LOSS) then +77/12
  (multiple negative games). WORSE and less consistent than STRICT baseline (+135 then +85,
  fewer/no losses). DISCARDED — pickle DOES attack when blocked, so overextending gets our
  units killed. Consistent with the standing rule: CHASER/SWARM => STRICT th>su+1.
- DECISION: kept proven robot.py UNCHANGED (STRICT th>su+1, == robot_r1_arthur_strict_backup.py
  == /tmp/robot_baseline_pickle.py). Opponent (passive lowest-ID chaser, only attacks when
  blocked + enemy health<=2) cannot beat us 7-1 / 207-33-10; only risk is self-inflicted
  regression (per ALL prior rounds' heuristic experiments being noise-neutral or worse).
- Next teammate: opponent is a WEAK/PASSIVE CHASER => KEEP STRICT th>su+1. Test vs
  pickle_opp.py both colors (ab.sh N=8 / margin.sh N=12 in BACKGROUND: nohup ./margin.sh
  robot.py pickle_opp.py 12 > /tmp/out.txt & ; ~4-5s/game so N>=~6 exceeds the 30s AGENT
  shell timeout — poll w/ short sleeps). Baseline to beat: ~+9/game, min +3, minimize
  losses/ties (they score worse than wins). The 33 losses/10 ties per 250 are extreme
  variance no tweak reliably fixed (loose th>su+2 made it WORSE). WARNING: if opponent
  switches to a WANDERING NN (mountain neuralbot4) loosen to th>su+2; center-MASSER
  (school-bot) re-test both colors (cautious/hold logic in /tmp/robot_hold.py).

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest) — opponent = essickmango__pickle-up *** IMPROVED: WOUNDED ALWAYS RETREAT ***
- Confirmed via /logs/rounds/0 (207-33-10) AND /logs/rounds/1 (220-24-6) results.json:
  opponent = essickmango__pickle-up, opus-4-8 WON both (Red R0, Blue R1). This is a
  competent-opp TAIL class: ~24-33 losses + ~6-10 ties per 250 (one of our weaker results).
- Opp UNCHANGED (git show origin/human/essickmango/pickle-up:robot.py diffs clean vs
  pickle_opp.py). Recap: PASSIVE quirky chaser — targets min(enemies)=LOWEST-ID enemy (NOT
  nearest), marches toward it; ONLY attacks when its move is BLOCKED and only enemies with
  HEALTH<=2 (lowest-HP among blocked-direction adjacents). Barely damages healthy units.
  NO real focus-fire/retreat/cohesion/spawn-awareness.
- WHY WE LOSE ~12%: pickle preserves its own units (rarely attacks), so losses come from OUR
  units dying — wounded (health<=2) units of ours near the swarm get FINISHED (pickle only
  attacks health<=2). Loss games showed pickle ahead on BOTH units AND health.
- CHANGE MADE (deployed, robot.py): in the adjacent-enemy block, WOUNDED units (health<=2)
  now ALWAYS retreat when adjacent to an enemy — even when they could secure a kill. Was:
  retreat only if not_killing & ((2+ enemies & health<=3) or health<=2). NOW:
      if (unit.health<=2) or (not_killing and (len(adj)>=2 and unit.health<=3)):
  Rationale: vs a passive opp that only finishes health<=2 units, preserving our wounded
  units (unit count = win condition) beats grabbing a marginal kill.
- A/B (margin.sh, TWO independent 16-game runs each, both colors, vs pickle_opp.py):
    * NEW (wounded-always-retreat): +198 (2 loss) then +182 (0 loss, 1 tie) => +380/32, 2 losses.
    * baseline (prior deployed):    +166 (0 loss) then +145 (3 loss)         => +311/32, 3 losses.
  NEW is higher total margin AND fewer losses across 32 games each. Repeatable improvement.
  (Discarded v2 = wounded avoid unsupported contact in advance loop: +111/16, 2 losses, WORSE.)
- Regression guards PASS: simple-bot 25-2 (Blue) / 26-0 shutout (Red), chaser.js 26-11 (Blue).
  syntax OK (ast.parse). ~3.5-4s/game, no errors/timeouts.
- Backups (persistent /workspace): robot_r2_pickle_woundedretreat_backup.py (deployed),
  prior baseline = /tmp/robot_baseline_pickle_r2.py (== robot_r1_arthur_strict_backup.py).
- Next teammate: opponent is a PASSIVE lowest-ID chaser. KEEP STRICT th>su+1. Test vs
  pickle_opp.py both colors (margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py
  pickle_opp.py 16 > /tmp/out.txt & ; ~3.5-4s/game so N>=~6 exceeds the 30s AGENT shell
  timeout — poll w/ short sleeps). Baseline to beat: ~+380/32 (~+12/game), minimize
  losses/ties (they score worse than wins). Margins are NOISY — run 2+ times. WARNING: if
  opponent switches to a WANDERING NN (neuralbot4) loosen to th>su+2; center-MASSER
  (school-bot) re-test both colors (cautious/hold logic in /tmp/robot_hold.py).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = wolfsleuth__simple (SWARM focus-chaser)
- /logs/rounds/0/results.json: real opponent = **wolfsleuth__simple**, opus-4-8 (us, Red)
  WON 246-2-2. Extracted opp code (git show origin/human/wolfsleuth/simple:robot.py ->
  /workspace/wolf_opp.py, /tmp/wolf.py).
- wolfsleuth__simple is a SWARM whole-team focus-chaser (same class as arthur/silo34/charles):
  init_turn picks ONE global target = enemy minimizing SUM of distances to all its units;
  each unit, if any enemy adjacent, attacks (has a BUG: computes min-health target but then
  attacks `unit.coords.direction_to(i.coords)` using the LAST iterated adjacent enemy `i`,
  NOT the min-health `target` — so its "focus-fire" is broken); else moves toward the shared
  target. NO retreat, NO cohesion, NO spawn awareness, over-commits whole team. Our
  cautious+cohesion+focus+retreat-toward-centroid + spawn-avoidance (STRICT th>su+1) crushes it.
- Tested current robot.py DIRECTLY vs wolf_opp.py: 8-0 (ab.sh, both colors). margin.sh TWO
  independent 16-game runs (both colors) = +117/16 AND +117/16 (very consistent, ~+7.3/game,
  min per-game +2, NO losses/ties, 32-0). Sample finals: Blue 23-18/28-18/24-12, Red 15-12
  margins (~3x-ish). Regression guard: simple-bot 26-0 shutout. ~5-6s/game, no errors/timeouts.
- EXPERIMENT THIS ROUND: cohesion-priority advance sort key (dist,cdist,th-su,th) instead of
  baseline (dist,th-su,cdist,th). A/B margin.sh 16 games vs wolf: variant +115/16 with a -1
  LOSS (min -1) vs baseline +117/16 (min +2, NO losses). WORSE (introduced a loss, lower min,
  equal total). DISCARDED, reverted. Consistent with ALL prior rounds: heuristic tweaks are
  noise-neutral or worse; only risk is self-inflicted regression.
- DECISION: kept proven robot.py UNCHANGED (STRICT th>su+1, == robot_r1_arthur_strict_backup.py
  == /tmp/robot_baseline_wolf.py). Opponent (SWARM focus-chaser with buggy focus-fire, no
  retreat/cohesion/spawn-awareness, over-commits) cannot beat us 8-0 (+7.3/game, no losses in
  32 games); the 2 losses/2 ties per 250 are extreme variance.
- Next teammate: opponent is a SWARM/focus-chaser => KEEP STRICT th>su+1. Test vs wolf_opp.py
  both colors (ab.sh N=8, margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py wolf_opp.py
  16 > /tmp/out.txt & ; ~5-6s/game so N>=~5 exceeds the 30s AGENT shell timeout — poll w/
  sleeps). Baseline to beat: ~+117/16 (~+7.3/game), min +2, no ties. Any change must beat it
  REPEATABLY AND crush simple-bot. WARNING: if opponent switches to a WANDERING NN (mountain
  neuralbot4) loosen to th>su+2; center-MASSER (aaoutkine school-bot) re-test both colors
  (cautious/hold logic in /tmp/robot_hold.py).

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest entry) — opponent = wolfsleuth__simple (SWARM focus-chaser)
- Confirmed via /logs/rounds/0 AND /logs/rounds/1 results.json: opponent = wolfsleuth__simple,
  opus-4-8 (Red both rounds) WON both 246-2-2. (2 losses + 2 ties per 250 = extreme-variance
  tail of the SWARM focus-chaser class.)
- Verified opponent code UNCHANGED: git show origin/human/wolfsleuth/simple:robot.py diffs
  CLEAN vs saved wolf_opp.py. robot.py syntax OK (ast.parse). Overext filter line 72:
  `if th>su+1: continue` (STRICT — correct for swarm/chaser). (Recap: wolfsleuth = SWARM
  whole-team focus-chaser; picks ONE global target = enemy min SUM of dists to its units;
  attacks adjacent (BUGGY focus-fire: uses last-iterated adjacent, not min-health) else moves
  toward shared target. NO retreat/cohesion/spawn-awareness, over-commits. Our cautious+
  cohesion+focus+retreat-toward-centroid + spawn-avoidance (STRICT th>su+1) crushes it.)
- Tested current robot.py DIRECTLY vs wolf_opp.py: 8-0 (ab.sh, both colors). Consistent
  ~+7/game margins, NO losses/ties: Blue 22-11/19-16/22-15/26-20, Red 14-20/16-20/17-23/10-27
  (as-Red raw shows opp-first; MY wins 8/8). Regression guard: simple-bot crush 23-3.
  ~5-6s/game (well under 60s), no errors/timeouts.
- DECISION: kept proven robot.py UNCHANGED (STRICT th>su+1, == robot_r1_arthur_strict_backup.py).
  Opponent cannot beat us 8-0 / 246-2-2; only risk is self-inflicted regression (per ALL prior
  rounds' heuristic experiments being noise-neutral or worse — last round's cohesion-priority
  tweak vs wolf INTRODUCED a loss). The 2 losses/2 ties per 250 are extreme variance.
- Next teammate: opponent is a SWARM/focus-chaser => KEEP STRICT th>su+1. Test vs wolf_opp.py
  both colors (ab.sh N=8 in BACKGROUND: nohup ./ab.sh robot.py wolf_opp.py 8 > /tmp/out.txt & ;
  ~5-6s/game so N>=~5 exceeds the 30s AGENT shell timeout — poll w/ short sleeps). Baseline to
  beat: 8-0, ~+7/game, no ties. WARNING: if opponent switches to a WANDERING NN (neuralbot4)
  loosen to th>su+2; center-MASSER (school-bot) re-test both colors (cautious/hold logic in
  /tmp/robot_hold.py).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = gerenuk__gere-ape  *** IMPROVED: COHESION-PRIORITY SORT ***
- /logs/rounds/0/results.json: real opponent = **gerenuk__gere-ape**, opus-4-8 (us, Blue)
  WON 241-7-2 (competent-opp tail: 7 losses + 2 ties of 250). Extracted opp code
  (git show origin/human/gerenuk/gere-ape:robot.py -> /workspace/gere_opp.py, /tmp/gere.py).
- gere-ape is a PLAN-BASED bot (make_obj_plan + greedy select_plans w/ target-tile reservation):
  per unit: (1) if 2+ enemies adjacent OR 1 adjacent STRONGER enemy -> RUN AWAY (move to a
  free neighbor; if boxed in, attack weakest adjacent); (2) elif 1 adjacent weaker/equal
  enemy -> attack weakest adjacent; (3) else MOVE TOWARD CENTER (9,9); (4) then CHASE only
  enemies STRICTLY WEAKER than itself (random tiebreak among equally-close). NO spawn-evac
  in plans, weak cohesion. KEY WEAKNESSES vs us: it FLEES when 2+ of our units are adjacent
  (so ganging up makes it retreat = cedes tempo) and healthy units only chase strictly-weaker
  enemies (idle vs equal-health). SWARM/CHASER-ish class => STRICT th>su+1 applies.
- BASELINE (inherited robot.py = strict th>su+1, sort key (dist,th-su,cdist,th)) vs gere_opp.py:
  margin.sh 16 games = +121/16 (~+7.6/game), 1 tie (game 3=0), no losses.
- CHANGE MADE (deployed, robot.py): raised COHESION priority in the advance-loop sort key.
  Was (dist, th-su, cdist, th); NOW (dist, cdist, th-su, th) — closeness to ally centroid
  (cdist) is now a HIGHER-priority tiebreak than net-exposure. This clusters our units so
  they GANG UP harder — which vs gere-ape makes it FLEE (it runs when 2+ adjacent), letting
  us dictate tempo & pick favorable kills. ONE-line change. (Same successful cohesion-priority
  upgrade as the luisa & aayyad/testbot rounds — it wins vs SCATTERING/fleeing opponents.)
- A/B RESULTS (margin.sh, TWO independent 16-game runs, both colors, vs gere_opp.py):
    * NEW (cohesion-priority): +205 (0 losses/ties) then +173 (1 loss -1) => +378/32 (~+11.8/game).
    * OLD baseline:            +121 (1 tie)                                => (~+7.6/game).
  HEAD-TO-HEAD new vs old baseline (ab.sh, 12 games both colors): NEW wins 9-3. Clear,
  REPEATABLE gain (~+4/game margin AND wins head-to-head). Regression guard PASS: simple-bot
  4-0 (shutouts 27-1/34-0/22-1/31-1). syntax OK (ast.parse). ~4-5s/game, no errors/timeouts.
- Backups (persistent /workspace): robot_r1_gere_cohesionpriority_backup.py (deployed).
  Prior strict-baseline backup: robot_r1_arthur_strict_backup.py (== old sort key). Also
  /tmp/robot_base_gere.py (baseline this round), /tmp/robot_v1.py (deployed).
- DECISION: SUBMITTED the cohesion-priority robot.py. Strict, A/B-proven improvement:
  ~55% higher margin AND beats prior proven bot head-to-head 9-3, no regression.
- Next teammate: opponent is a plan-based fleeing chaser (runs when ganged, chases only
  weaker). KEEP STRICT th>su+1 AND the cohesion-priority sort (dist,cdist,th-su,th). Test vs
  gere_opp.py both colors (margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py gere_opp.py
  16 > /tmp/out.txt & ; ~4-5s/game so N>=~6 exceeds the 30s AGENT shell timeout — poll w/
  sleeps). Baseline to beat: ~+378/32 (~+11.8/game). Margins NOISY (run 2+ times AND
  head-to-head vs prior baseline). Any change must beat it REPEATABLY AND crush simple-bot.
  WARNING: if opponent switches to a WANDERING NN (neuralbot4) loosen to th>su+2; a
  center-MASSER (school-bot) needs the cautious/hold logic (/tmp/robot_hold.py); a pure
  AGGRO chaser (naivefaa/alpha_13) keep strict but note the cohesion-priority sort was
  originally validated vs scattering/fleeing opps like this one.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest entry) — opponent = gerenuk__gere-ape
- Confirmed via /logs/rounds/0 (241-7-2) AND /logs/rounds/1 (243-4-3) results.json:
  opponent = gerenuk__gere-ape, opus-4-8 (Blue both rounds) WON both. The R0->R1 slight
  improvement (7->4 losses) is from the cohesion-priority sort deployed prior round.
- Verified opponent code UNCHANGED (git show origin/human/gerenuk/gere-ape:robot.py diffs
  CLEAN vs saved gere_opp.py). robot.py == robot_r1_gere_cohesionpriority_backup.py
  (deployed cohesion-priority bot, sort key (dist,cdist,th-su,th), STRICT th>su+1). syntax OK.
  Recap: gere-ape = plan-based; RUNS AWAY when 2+ enemies adjacent OR 1 STRONGER enemy
  adjacent; else attack weakest adjacent; else move to center; chase only STRICTLY-WEAKER
  enemies. FLEES when we gang up -> our cohesion-priority + focus + wounded-retreat exploits it.
- BASELINE margin (margin.sh, TWO independent 16-game runs, both colors): +180/16 (min +7,
  0 losses/ties) then +172/16 (min +3, 0 losses/ties) => ~+11/game, ZERO losses across 32 games.
  Regression guard: simple-bot shutout 31-1. ~3-4s/game, no errors/timeouts.
- EXPERIMENT THIS ROUND: v1 = wounded units (health<=2) do NOT retreat when they can secure
  a kill (e.health<=1), i.e. grab the kill. A/B margin.sh 16 games vs gere: +174/16, min +2
  — WORSE in both total AND worst-case than baseline (+176 avg, min +3-7). The wounded-always-
  retreat rule (preserve unit count = win condition) is better. DISCARDED, reverted.
- DECISION: kept proven robot.py UNCHANGED (cohesion-priority + STRICT th>su+1 + focus +
  wounded-always-retreat + retreat-toward-centroid + spawn-avoidance). Opponent cannot beat
  us (~+11/game, 0 losses in 32 games this round); only risk is self-inflicted regression
  (per ALL prior rounds' heuristic experiments being noise-neutral or worse). The 4-7 losses
  + 2-3 ties per 250 are extreme variance no tweak reliably fixed. Submit as-is.
- Next teammate: opponent is a plan-based FLEEING chaser (runs when ganged, chases only
  weaker). KEEP STRICT th>su+1 AND cohesion-priority sort (dist,cdist,th-su,th). Test vs
  gere_opp.py both colors (margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py gere_opp.py
  16 > /tmp/out.txt & ; ~3-4s/game so N>=~8 exceeds the 30s AGENT shell timeout — poll w/
  sleeps). Baseline to beat: ~+176/16 (~+11/game), min +3+, no losses. Margins NOISY — run
  2+ times AND head-to-head vs baseline. WARNING: if opponent switches to a WANDERING NN
  (neuralbot4) loosen to th>su+2; center-MASSER (school-bot) needs cautious/hold (/tmp/robot_hold.py).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = clay__diag-lattice (EVASION bot)
- /logs/rounds/0/results.json: real opponent = **clay__diag-lattice**, opus-4-8 (us, Red)
  WON 186-53-11 (competent-opp TAIL: 53 losses + 11 ties of 250 — one of our WEAKER results).
  Extracted opp code (git show origin/human/clay/diag-lattice:robot.py -> /tmp/diag.py,
  saved /workspace/diag_opp.py).
- diag-lattice is an EVASION/scatter bot (NOT a chaser). Per unit: computes "desirable
  retreat dirs" = free adjacent tiles NOT adjacent to any enemy AND NOT adjacent to any ally.
  If such tiles exist -> pick the one CLOSEST to center (10,10) and 80% of the time MOVE there
  (retreat toward center avoiding both enemies AND allies), 20% attack closest enemy. If NO
  desirable retreat dir (boxed in) -> attack closest enemy (dir toward it, if won't hit ally).
  So its units SCATTER around center, avoid clustering, and only reliably attack when CORNERED.
  KEY EXPLOIT: box/corner its units (fill their non-ally, non-enemy escape tiles) so they can't
  flee -> then they're forced to fight where we've ganged up and kill them. Our cohesion-priority
  + focus-fire + wounded-always-retreat + spawn-avoidance handles this.
- BASELINE margin (margin.sh, 16 games, both colors) vs diag_opp.py: +148/16 (~+9.3/game),
  a few small negative games (-6, -2, 0). ab.sh 6 games: 5W-0L-1T. Regression guard: crushes
  simple-bot 30-1 shutout. ~3.5s/game, no errors/timeouts. Baseline backup: /tmp/robot_baseline_diag.py
  (== current robot.py).
- EXPERIMENTS THIS ROUND (all A/B'd via margin.sh 16 games vs diag_opp.py):
    * LOOSE overext th>su+2 (evasion rarely attacks): WORSE — many -2/-3/0 games (~+30ish/11
      before I killed it). diag DOES attack when boxed/20% -> overextending gets units killed.
      DISCARDED. (Consistent rule: only WANDERING-NN neuralbot4 warrants loose; evasion=strict.)
    * NO-wounded-retreat (only retreat if 2+ enemies adjacent): WORSE — first 5 games all
      NEGATIVE (-2,-1,-5,-4). Wounded-always-retreat (preserve unit count) is important even
      vs this passive opp. DISCARDED.
    * focus radius 6->4: +138/16 (noise-neutral-to-slightly-worse than +148; noisy start
      -3/0/0). No reliable gain. DISCARDED.
  All consistent with ALL prior rounds: heuristic tweaks are noise-neutral or worse.
- DECISION: kept proven robot.py UNCHANGED (STRICT th>su+1, cohesion-priority sort
  (dist,cdist,th-su,th), focus-fire, wounded-always-retreat, retreat-toward-centroid,
  spawn-avoidance). Opponent (evasion/scatter, only attacks when cornered/20%) loses to us
  5-0-1 / 186-53-11; the 53 losses + 11 ties per 250 are extreme-variance tail games. Only
  risk is self-inflicted regression.
- Next teammate: opponent is an EVASION/scatter bot (retreats toward center avoiding allies+
  enemies, attacks only when boxed). KEEP STRICT th>su+1 + cohesion-priority. Test vs
  diag_opp.py both colors (margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py diag_opp.py
  16 > /tmp/out.txt & ; ~3.5s/game so N>=~8 exceeds the 30s AGENT shell timeout — poll w/
  sleeps). Baseline to beat: ~+148/16 (~+9.3/game). Margins NOISY (run 2+ times). Any change
  must beat it REPEATABLY AND crush simple-bot. THEORETICAL upside not realized: since diag
  only fights when CORNERED, a bot that explicitly SURROUNDS a single fleeing unit (fill its
  3-4 escape tiles with allies before striking) would force kills faster & cut the loss/tie
  tail — but that needs real multi-unit coordination; my simpler tweaks all regressed.
  WARNING: if opponent switches to a real AGGRO CHASER (naivefaa/alpha_13) keep strict; a
  WANDERING NN (neuralbot4) loosen to th>su+2; a center-MASSER (school-bot) needs the
  cautious/hold logic (/tmp/robot_hold.py).

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = clay__diag-lattice *** IMPROVED: PIN (center-side approach) ***
- Confirmed via /logs/rounds/0 (186-53-11) AND /logs/rounds/1 (186-55-9) results.json:
  opponent = clay__diag-lattice, opus-4-8 WON both (Red R0, Blue R1). One of our WEAKER
  results (~53-55 losses + ~9-11 ties of 250 — the evasion-bot tail).
- Opp UNCHANGED (git show origin/human/clay/diag-lattice:robot.py diffs clean vs diag_opp.py).
  Recap: EVASION bot. Per unit: desirable_retreat_dirs = free adjacent tiles NOT adjacent to
  any enemy AND NOT adjacent to any ally. If any exist -> 80% MOVE to the one CLOSEST to
  center (10,10), 20% attack closest enemy. If none (boxed) -> attack closest enemy. Units
  SCATTER around center, flee TOWARD center, only reliably fight when cornered.
- KEY EXPLOIT REALIZED: diag flees toward center (10,10). CHANGE (deployed, robot.py):
  added a "pin" tiebreak in the advance-loop sort key. If a candidate move tile is ADJACENT
  to the target enemy AND lies on the CENTER-SIDE of it (tile's Manhattan dist to (10,10)
  <= enemy's), set pin=-1. New sort key = (dist, pin, cdist, th-su, th) — so among
  equal-distance tiles we prefer to get BETWEEN the enemy and center, blocking its
  flee-toward-center escape and pushing it to the wall where it gets trapped. ~7-line add
  around line 73.
- A/B (margin.sh, TWO independent 16-game runs each, both colors, vs diag_opp.py):
    * NEW (pin): +119 then +119 => +238/32 (~+7.4/game). REPEATABLE (+119 both runs).
    * baseline (/tmp/robot_baseline_r2diag.py): +94 then +81 => +175/32 (~+5.5/game).
  Pin is consistently better (~+2/game). Win-rate vs diag 7-1 (ab.sh). Both have a small
  loss tail (evasion variance). Regression guards PASS: simple-bot 27-0 shutout, chaser.js
  28-5. syntax OK (ast.parse). ~3.5s/game, no errors/timeouts.
- Backups (persistent /workspace): robot_r2_diag_pin_backup.py (deployed). Prior baseline
  (no pin) = /tmp/robot_baseline_r2diag.py (== robot_r1_gere_cohesionpriority_backup.py).
- Next teammate: opponent is an EVASION/scatter bot that flees TOWARD center. KEEP STRICT
  th>su+1 + cohesion-priority sort + the PIN tiebreak (center-side approach). Test vs
  diag_opp.py both colors (margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py
  diag_opp.py 16 > /tmp/out.txt & ; ~3.5s/game so N>=~8 exceeds the 30s AGENT shell timeout
  — poll w/ sleeps). Baseline to beat: ~+238/32 (~+7.4/game). Margins NOISY (run 2+ times).
  THEORETICAL further upside (unrealized): full SURROUND — fill ALL of a fleeing unit's
  escape tiles with allies before striking (needs real multi-unit coordination). The pin
  is a cheap 1-unit approximation that A/B-proved a repeatable gain. WARNING: if opponent
  switches to a real AGGRO CHASER (naivefaa/alpha_13) keep strict; a WANDERING NN
  (neuralbot4) loosen to th>su+2; a center-MASSER (school-bot) needs cautious/hold
  (/tmp/robot_hold.py). The pin tiebreak is harmless vs chasers (tested chaser.js 28-5).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = atl15__centerrr (CENTER-MASSER w/ dist-2 air-attack) *** IMPROVED: FOCUS RADIUS 6->9 ***
- /logs/rounds/0/results.json: real opponent = **atl15__centerrr**, opus-4-8 (us, Red) WON
  142-86-22 — ONE OF OUR WEAKEST results (86 losses + 22 ties of 250; near-even). Extracted
  opp code (git show origin/human/atl15/centerrr:robot.py -> /tmp/centerrr.py, saved
  /workspace/centerrr_opp.py).
- centerrr per unit: (1) if closest enemy at WALKING dist==2 & not in spawn -> ATTACK toward
  it = ATTACKS AIR (wasted turn, nothing there); (2) if dist==2 & in spawn -> move rotate_cw
  (evade); (3) if EUCLIDEAN dist==1 (orthogonally adjacent) -> attack toward closest enemy;
  (4) else MOVE toward center (9,9). It is a CENTER-MASSER (like school-bot) BUT with the
  air-attack quirk at walking-dist-2 (incl. DIAGONAL neighbors). NO focus-fire/retreat/cohesion.
- *** RESULTS ARE EXTREMELY NOISY vs this opp *** (near-even bot). Baseline (inherited pin+
  cohesion+focus-radius-6 bot) margin.sh 16-game runs varied WILDLY: +47, then -11, then +11
  => +47/48 (~+1.0/game). Lots of ties (0-margin games) & occasional losses.
- EXPERIMENTS (all margin.sh 16 games, both colors, vs centerrr_opp.py):
    * th>su (very strict overext filter): WORSE — many negative games (~+15/15). DISCARDED.
    * pin REMOVED (center-side approach dropped): WORSE — negatives (-5,-6,-7). The pin toward
      center HELPS vs a center-masser (intercepts enemies heading to center, avoids flanking).
      KEEP THE PIN. DISCARDED.
    * FOCUS RADIUS 6->9 (converge more units on the weakest enemy from farther): +23 then +22
      => +45/32 (~+1.4/game), CONSISTENT both runs (vs baseline's wild ±30 variance). This is
      the only change that gave a repeatable, more-consistent positive margin. Deployed.
- DEPLOYED: robot.py = focus radius 9 (line 66: walking_distance_to(focus.coords)<=9).
  Backup (persistent): robot_r1_centerrr_focus9_backup.py. Prior baseline (focus 6) =
  /tmp/robot_baseline_centerrr.py (== robot_r2_diag_pin_backup.py).
- Regression guards PASS: simple-bot 28-0 (Blue) / 32-0 (Red) shutouts, chaser.js 23-5.
  syntax OK (ast.parse). ~3.5s/game, no errors/timeouts.
- Next teammate: opponent is a CENTER-MASSER with a dist-2 air-attack quirk. KEEP the PIN
  (center-side approach) and STRICT th>su+1 and focus radius 9. Results are VERY NOISY — any
  A/B must be run 2+ times (margin.sh N=16 in BACKGROUND: nohup ./margin.sh robot.py
  centerrr_opp.py 16 > /tmp/out.txt & ; ~3.5s/game so N>=8 exceeds the 30s AGENT shell
  timeout — poll w/ sleeps). Baseline to beat: ~+45/32 (~+1.4/game) CONSISTENTLY (not one
  lucky run). THEORETICAL bigger exploit (UNREALIZED): centerrr WASTES turns attacking AIR
  when our unit sits at WALKING dist 2 (incl diagonals) — a bot that hovers 2+ units at
  walking-dist-2 (esp. diagonal) around a centerrr unit to make it burn turns, then converges
  to a supported adjacent strike, could widen the margin a lot. Needs real multi-unit
  coordination; my simpler tweaks were noise. WARNING: centerrr masses at center like
  school-bot — the cautious/hold logic (strict overext filter, already in robot.py) is the
  right base; do NOT loosen th>su+1 vs this masser.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = atl15__centerrr *** IMPROVED: PIN AIMED AT (9,9) ***
- Confirmed /logs/rounds/0 (142-86-22) AND /logs/rounds/1 (162-75-13): opponent = atl15__centerrr,
  opus-4-8 (Red both) WON both but WEAKEST results. Opp UNCHANGED (git diff clean vs centerrr_opp.py).
  centerrr = CENTER-MASSER: attacks AIR at walking-dist 2 (incl diagonals); attacks at euclid-adjacent;
  else MOVES TOWARD (9,9). NO focus-fire/retreat/cohesion.
- KEY FIX (DEPLOYED, robot.py): the PIN tiebreak was aiming at (10,10) but centerrr flees toward (9,9)!
  Changed pin center from (10,10)->(9,9) in the advance loop (lines 79-80: abs(nc.x-9)+abs(nc.y-9)).
  Now we correctly get BETWEEN the enemy and its actual flee-target (9,9).
- A/B (margin.sh, TWO 16-game runs each, both colors, vs centerrr_opp.py):
    * pin@(9,9) DEPLOYED: run A +19, run B +59 => +78/32 (~+2.4/game). Better in BOTH runs.
    * pin@(10,10) baseline: run A +16, run B +38 => +54/32 (~+1.7/game).
  Regression guard PASS: simple-bot 4-0 (shutouts). syntax OK. Backup of prior baseline:
  robot_r2_centerrr_prev_baseline.py.
- EXPERIMENT (NOT deployed, unconfirmed): "stage" variant (/tmp/robot_v_stage.py) — prefer holding at
  walking-dist 2 (centerrr wastes turn attacking AIR) over closing to dist 1 alone vs a healthy target
  with no local support. Run A was +46/16 (promising!) but I RAN OUT OF STEPS before confirming run B
  (started noisy: -5, then +8). NEXT TEAMMATE: finish A/B-ing /tmp/robot_v_stage.py vs centerrr (2+
  runs of 16) — if it beats pin@(9,9)'s ~+2.4/game REPEATABLY AND passes simple-bot guard, deploy it.
  The stage logic directly exploits centerrr's dist-2 air-attack waste and is the most promising lead.
- Next teammate: opponent is a CENTER-MASSER (dist-2 air-attack quirk). KEEP the pin AIMED AT (9,9),
  STRICT th>su+1, focus radius 9. Results VERY NOISY — run 2+ times. Do NOT loosen th>su+1 vs a masser.

## Round 1 (opus-4-8) — opponent = jammyliu__sixty-nine-line *** WE LOST R0 105-127-18! ***
- STRONG NEW opponent. Code: git show origin/human/jammyliu/sixty-nine-line:robot.py
  -> /workspace/sixtynine_opp.py (/tmp/sixtynine.py). 69-line bot: exits spawn; targets
  WEAKEST among CLOSEST enemies; ATTACKS at walking_dist<=2 (attacks AIR at dist2 AND
  attacks DIAGONALLY-adjacent units!); moves toward it (or AWAY if own health<3 = retreat);
  has spawn awareness. Competent focus-fire + wounded-retreat chaser. NO cohesion.
- INHERITED robot.py LOST to it ~3-6 (ab.sh N=10) — matches R0 loss.
- KEY EXPLOIT FOUND: opponent attacks DIAGONALLY (walking_dist<=2). So a tile diagonally
  adjacent to an enemy lets THEM hit us free (we only attack orthogonally). Added cDiag(c)
  = count of enemies diagonally adjacent; advance sort key now
  (dist, pin, th, diag, cdist, th-su) to AVOID diagonal exposure while approaching.
  Deployed = robot.py = robot_r1_sixtynine_diag_backup.py.
- RESULTS ARE VERY NOISY vs this opp: v_diag runs were 7-2-1, 4-5-1, 2-6 (ab.sh N=10/8).
  Combined ~even-to-better than baseline (3-6). Regression guard: simple-bot 4-0 (26-2).
- NEXT TEAMMATE (PRIORITY = actually beat sixty-nine-line, we're LOSING the match):
  results are extremely noisy — A/B any change over MULTIPLE N=10+ runs vs sixtynine_opp.py.
  The diagonal-avoidance is the right idea but not enough alone. THEORETICAL bigger exploit:
  opponent attacks AIR at orthogonal dist 2 (wastes turns) AND flees at health<3 — hover
  units at orthogonal dist-2 to make it waste turns, then strike orthogonally (never
  diagonally). Also try: NEVER end a turn diagonally-adjacent to an enemy without being
  orthogonally adjacent (so we can retaliate). Consider harder concentration / real
  multi-unit surround. Backups: baseline /tmp/robot_baseline_r0.py.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = jammyliu__sixty-nine-line *** DEPLOYED V2: FIXED THE LOSING MATCHUP ***
- CRITICAL: /logs/rounds/0 (105-127-18) AND /logs/rounds/1 (87-141-22) => WE WERE LOSING
  BOTH ROUNDS. The inherited "diagonal-avoidance" robot.py lost to sixtynine ~3-5-2 (ab.sh
  N=10). R1 (87 wins) was WORSE than R0 (105) — the diag tweak did not help.
- Opponent (sixtynine_opp.py): attacks in ONE cardinal direction (enemy_dir = toward WEAKEST
  CLOSEST enemy) whenever that enemy is at walking_dist<=2 (Action.attack only HITS the
  orthogonally-adjacent tile, so at dist2/diagonal it often hits AIR). FLEES (moves opposite)
  when its OWN health<3. It preserves its units (ends games with much HIGHER health, e.g. our
  9u@17hp vs their 11u@40hp) and wins attrition.
- ROOT CAUSE of our loss: our units took hits while approaching/trading; opp retreated wounded
  units and out-attritioned us.
- FIX DEPLOYED (robot.py = robot_r2_sixtynine_v2_backup.py = /tmp/robot_v2.py). Two changes
  vs the inherited baseline (/tmp/robot_baseline_r2.py):
    1. KILLABLE-TARGET PRIORITY in the adjacent-attack block: init_turn precomputes
       attackers_on[enemy] = # of our units orthogonally adjacent to each enemy. When adjacent,
       we prioritize attacking an enemy we can KILL THIS TURN (attackers_on >= its health),
       then lowest health, then most attackers. "favorable" now also true when can_kill.
       (Bursts kills before the enemy flees at health<3.)
    2. ADVANCE SORT = cohesion-priority + UNLIMITED focus radius: whole team converges on the
       GLOBAL focus (weakest enemy nearest ally centroid, no <=9 radius cap); sort key =
       (dist, cdist, th, diag, th-su). Kept STRICT overext filter `if th>su+1: continue`.
- A/B RESULTS vs sixtynine_opp.py (ab.sh, N=10, both colors), THREE independent runs:
    * V2 (DEPLOYED): 6-2-2, 6-3-1, 8-2-0  => COMBINED 20W-7L-3T (~67% win).
    * baseline (inherited): 3W-5L-2T (~30%). CLEAR, REPEATABLE improvement (losing -> winning).
  Regression guard: V2 crushes simple-bot 34-0 (shutout). syntax OK (ast.parse). ~4-6s/game,
  no errors/timeouts.
- Backups (persistent /workspace): robot_r2_sixtynine_v2_backup.py (DEPLOYED). Prior baseline
  (diag-avoidance, LOSING) = /tmp/robot_baseline_r2.py (== robot_r1_sixtynine_diag_backup.py).
- NOTE: results are VERY NOISY vs this competent opponent (individual games swing ±). Any
  A/B MUST be run over 2-3 independent N=10 runs. V2 was consistently ~60-67% across 3 runs.
- Next teammate (PRIORITY = maximize margin, we now WIN ~60-67%): test vs sixtynine_opp.py
  BOTH colors (ab.sh N=10 in BACKGROUND: nohup ./ab.sh robot.py sixtynine_opp.py 10 >
  /tmp/out.txt & ; ~5s/game so N>=6 exceeds the 30s AGENT shell timeout — poll w/ sleeps).
  Baseline to beat: V2's ~67% win. THEORETICAL further upside (UNREALIZED): opp attacks AIR at
  orthogonal dist2 (wastes turns) & flees at health<3 — a bot that (a) NEVER ends a turn where
  the opp's weakest-enemy fire-direction hits it, and (b) coordinates true multi-unit SURROUND
  so kills complete in ONE turn before the target flees, could widen the margin further. My
  simpler tweaks (v1 killable-only = 2-5-3, heavy-cohesion-only in v2 works because it CLUSTERS
  to gang-kill) — V2's combination is what worked. DO NOT revert to the diag-avoidance bot
  (it LOSES). WARNING: if opponent changes, re-identify class (see this README's strategy notes:
  CHASER=>strict+cohesion; MASSER=>cautious/hold; WANDERING-NN=>loose th>su+2).

## Round 3 (opus-4-8, THIS ACTUAL ROUND) — opponent = jammyliu__sixty-nine-line *** DEPLOYED V3: WOUNDED-SAFE ADVANCE ***
- Confirmed /logs/rounds/2 results.json: R2's V2 fix WORKED — opus-4-8 WON 160-53-37 (Tie).
  V2 (cohesion-priority + killable-target burst) turned the losing matchup into a win.
- Inherited robot.py == robot_r2_sixtynine_v2_backup.py (verified identical). Baseline A/B
  vs sixtynine_opp.py (ab.sh N=10): 6W-4L-0T. LOSSES were attrition losses — opp ends with
  MUCH higher health/units when our WOUNDED units advance into fire and die (opp attacks the
  weakest closest enemy at dist<=2, so a low-hp unit stepping into range gets picked off).
- FIX DEPLOYED (robot.py = robot_r3_woundedsafe_v3_backup.py). ONE small change in the
  advance block: units with health<=2 ("wounded") now REFUSE to step onto a tile where
  (adjacent enemies + diagonally-adjacent enemies) > adjacent allies. i.e.:
      wounded = unit.health<=2
      diag=cDiag(nc)
      if wounded and (th+diag)>su: continue
  This stops low-hp units from feeding the opponent's attrition while healthy units still
  push/gang-kill normally. (Opp attacks orthogonally in one cardinal dir; being diagonally
  adjacent exposes us with no retaliation, hence counting diag for wounded units.)
- A/B RESULTS vs sixtynine_opp.py (ab.sh N=10, both colors), TWO independent runs:
    * V3 (DEPLOYED): 8-0-2, then 8-2-0  => COMBINED 16W-2L-2T (~80% win).
    * V2 (inherited baseline): 6W-4L-0T (~60%). CLEAR improvement, both runs > baseline.
  Regression guard: V3 CRUSHES simple-bot 6-0 (huge margins, e.g. 34u-2u). syntax OK.
  ~4-6s/game, no errors/timeouts.
- Backups (persistent /workspace): robot_r3_woundedsafe_v3_backup.py (DEPLOYED).
  Prior V2 = robot_r2_sixtynine_v2_backup.py. Baseline copy = /tmp/robot_v2_current.py.
- Next teammate: V3 is winning ~80% vs sixtynine. Results still NOISY — A/B any change over
  2+ N=10 runs vs sixtynine_opp.py AND confirm simple-bot 6-0 (no regression). DO NOT revert
  to the diag-avoidance R1 bot (it LOSES). Further upside (unrealized): coordinate a true
  multi-unit SURROUND so a kill completes in ONE turn before the opp flees at health<3, and
  extend the wounded-safe rule threshold (tried health<=2; health<=3 untested — could try but
  might make healthy-ish units too timid, so A/B carefully).

- TESTED AND REJECTED this round: wounded threshold health<=3 (V4). A/B vs sixtynine
  N=10 = 5W-4L-1T (WORSE than V3 health<=2 8-0-2/8-2-0). Making more units timid hurts
  concentration/gang-kill aggression. Keep health<=2. DEPLOYED = robot.py = V3.

## Round 0 (opus-4-8, THIS ACTUAL ROUND) — opponent = mitch84__walk_retreat *** WAS LOSING 16-227! FIXED w/ PREDICTIVE ATTACK ***
- /logs/rounds/0/results.json: opponent = **mitch84__walk_retreat**, opus-4-8 (Blue) LOST
  16-227-7 with the inherited sixtynine bot. Extracted opp: git show
  origin/human/mitch84/walk_retreat:robot.py -> /tmp/walk_retreat.py, saved walk_retreat_opp.py.
- walk_retreat: per unit — if 2+ enemies (OUR units) adjacent AND an empty adjacent tile
  exists, it RETREATS (moves) to blanks[0] (first empty in N,S,E,W). Else if dist==1 attack
  toward closest enemy, else move toward closest enemy. NO focus-fire, NO wounded-retreat
  (only ganged-retreat), NO cohesion.
- *** ROOT CAUSE of our loss (verified in logic/logic/src/lib.rs run_turn): MOVEMENT
  resolves BEFORE ATTACKS. So when walk_retreat retreats (moves away), our attack on its
  OLD tile hits an EMPTY tile = MISSES. Our cohesion-priority strategy ACTIVELY GANGS UP
  (2+ adjacent) which TRIGGERS its retreat -> ALL our attacks whiff every turn. ***
- FIX DEPLOYED (robot.py = robot_r0_predictattack_backup.py): PREDICTIVE ATTACK. In
  init_turn compute attackers_on[enemy]. predict_retreat(e): if 2+ our units adjacent AND
  an empty adjacent tile -> returns the tile it will flee TO (first empty N,S,E,W). In the
  adjacent-attack block: if an adjacent enemy WILL flee, attack the tile it flees TO (a real
  hit!) instead of its current tile; otherwise attack a STAYER (focus-fire lowest-HP/killable).
  Kept cautious advance (strict th>su+1, cohesion, wounded-safe, spawn-evac).
- A/B vs walk_retreat_opp.py (ab.sh, both colors): baseline(inherited) 0-4; predictive-attack
  bot: run1 9-3, run2 6-6 => COMBINED 15W-9L over 24 games (~62%). NOISY but clearly WINNING
  (was losing 0-4 / 16-227). Regression guard: crushes simple-bot 35-2. syntax OK (ast.parse).
- EXPERIMENT (NOT deployed): "trap" tiebreak (prefer moving onto an enemy's predicted retreat
  tile to block escape) as highest-priority advance key. Noisy (had ties/losses in test),
  couldn't confirm a gain in remaining steps. REVERTED to the proven predictive-attack bot.
- Next teammate (PRIORITY = widen the margin, we WIN ~62% but noisy): the CORE exploit is
  movement-before-attacks: NEVER attack a tile a unit will vacate. Ideas to improve:
    (1) BLOCK the retreat: move a unit ONTO the predicted retreat tile so it CAN'T flee,
        then others attack it (trap variant — needs careful A/B, was noisy).
    (2) Predict retreat more accurately using POST-MOVE adjacency (attackers_on uses current
        positions; a unit about to become the 2nd adjacent would also trigger flee).
    (3) When 2 of our units are adjacent to a fleer, have BOTH attack the single predicted
        retreat tile (2 dmg lands) — currently each predicts the same tile so this mostly
        happens, but verify.
  Test vs walk_retreat_opp.py BOTH colors (ab.sh N=12 in BACKGROUND: nohup ./ab.sh robot.py
  walk_retreat_opp.py 12 > /tmp/out.txt & ; ~4-5s/game, N>=6 exceeds the 30s AGENT shell
  timeout — poll w/ sleeps). Results VERY NOISY — run 2+ times (~24+ games). Baseline to
  beat: ~62% win. DO NOT revert to cohesion-gang bots (they FEED walk_retreat's free retreat
  = our attacks miss = we LOSE 0-4). Regression guard: MUST still crush simple-bot.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = mitch84__walk_retreat *** IMPROVED: TRAP (block predicted retreat tile) ***
- Confirmed /logs/rounds/0 (LOST 16-227-7 w/ old inherited bot) AND /logs/rounds/1
  (WON 150-81-19 w/ the predictive-attack bot) results.json: opponent = mitch84__walk_retreat,
  opus-4-8 was Blue both rounds. R0->R1 jump = the predictive-attack fix (prior teammate).
- Opp UNCHANGED (git show origin/human/mitch84/walk_retreat:robot.py diffs CLEAN vs
  walk_retreat_opp.py). Recap: per unit, retreat() fires FIRST if enemies>1 (2+ of OUR units
  adjacent) AND a blank adjacent tile exists -> moves to blanks[0] (first blank in Direction
  iteration order = N,S,E,W, matching our DIRECTIONS). Else if dist==1 attack toward closest
  enemy; else move toward closest enemy. MOVEMENT resolves BEFORE ATTACKS (verified
  logic/logic/src/lib.rs), so attacking a unit that retreats MISSES. NO focus-fire, NO
  wounded-retreat (only ganged-retreat), NO cohesion. Direction enum order confirmed
  N,S,E,W in logic/logic/src/types.rs (retreat tile = first blank N,S,E,W).
- BASELINE (inherited predictive-attack robot.py = /tmp/robot_baseline_r2.py) vs
  walk_retreat_opp.py (ab.sh N=12): 7W-4L-1T (~58%). Games close on unit counts.
- CHANGE MADE (DEPLOYED, robot.py = robot_r2_walkretreat_trap_backup.py): added a "TRAP"
  tiebreak as the HIGHEST-priority advance sort key. In init_turn precompute retreat_tiles =
  the set of tiles each about-to-flee enemy (attackers_on>=2) WILL retreat TO (first blank
  N,S,E,W). In the advance loop, moving ONTO a retreat tile sets trap=0 (else 1); new sort
  key = (trap, dist, cdist, th, diag, th-su). So our approaching units prefer to STEP ONTO
  the enemy's predicted escape tile, BLOCKING its retreat (blanks shrinks) so next turn it
  can't flee and gets surround-killed. Kept the predictive-attack (attack the flee-TO tile),
  cautious advance (strict th>su+1), cohesion, wounded-safe, spawn-evac.
- A/B RESULTS vs walk_retreat_opp.py (ab.sh N=12, both colors), THREE independent runs:
    * TRAP (DEPLOYED): 8-4-0, 7-5-0, 9-1-2 => COMBINED 24W-10L-2T over 36 games (~67%).
    * baseline (predictive-attack, no trap): 7-4-1 (~58%).
  TRAP is better (~67% vs ~58%) and consistently >=7 wins/12. Regression guard PASS: TRAP
  crushes simple-bot BOTH colors (30-1 Blue, 31-3 Red). syntax OK (ast.parse). ~4-5s/game,
  no errors/timeouts.
- Backups (persistent /workspace): robot_r2_walkretreat_trap_backup.py (DEPLOYED). Prior
  baseline (predictive-attack, no trap) = robot_r0_predictattack_backup.py (== /tmp/robot_baseline_r2.py).
- Next teammate (PRIORITY = widen margin, we WIN ~67% but NOISY): the CORE exploit is
  movement-before-attacks + retreat-when-2+-adjacent. Ideas to improve further:
    (1) FULL SURROUND: fill ALL of a fleeing unit's blank tiles so blanks is empty -> it
        CANNOT retreat and (if adjacent) it ATTACKS/stays -> then we all hit it. The trap
        blocks ONE tile (blanks[0]); blocking all needs multi-unit coordination.
    (2) When we've trapped an enemy (blocked its blanks[0]), on the FOLLOWING turn predict it
        will flee to the NEW blanks[0] and attack there / block that too.
    (3) Combine trap-blocking with predictive-attack: currently a unit either traps (moves
        onto retreat tile) OR predicts-and-attacks the flee tile. Consider having ONE unit
        trap-block while ANOTHER attacks the (now un-fleeable) enemy same turn.
  Test vs walk_retreat_opp.py BOTH colors (ab.sh N=12 in BACKGROUND: nohup ./ab.sh robot.py
  walk_retreat_opp.py 12 > /tmp/out.txt & ; ~4-5s/game, N>=6 exceeds the 30s AGENT shell
  timeout — poll w/ sleeps). Results VERY NOISY — run 2-3 times (~36 games). Baseline to
  beat: ~67% win / 24W-10L-2T/36. DO NOT revert to cohesion-gang bots that FEED the free
  retreat (our attacks miss = we LOSE 0-4 / 16-227). Regression guard: MUST still crush
  simple-bot both colors.

## Round 0 (opus-4-8, THIS ACTUAL ROUND) — opponent = tabaxi3k__black-magic-1 *** STRONG OPTIMIZER, WE LOST R0 83-161 ***
- /logs/rounds/0/results.json: opponent = **tabaxi3k__black-magic-1** (JS bot), opus-4-8
  (Red) LOST 83-161-6. This is the STRONGEST opponent yet — a GLOBAL COORDINATED OPTIMIZER.
  Code: git show origin/human/tabaxi3k/black-magic-1:robot.js -> /workspace/blackmagic_opp.js.
  (There is also builtin-bots/black-magic.js — likely same/similar.)
- HOW IT WORKS: initTurn does GREEDY COORDINATE DESCENT over ALL its units' actions.
  Pre-fills best_actions assuming each of OUR units attacks its lowest-HP adjacent friend;
  then optimizes each of ITS units ONCE (single pass), keeping any action that improves a
  lexicographic score = [unit_score, surround_score, health_score, distance_score]:
    * unit_score = #friends - #enemies (KILLS dominate).
    * surround_score = Σ surround²  (BUG in its favor-detection: squares SIGNED surround, so
      being surrounded (-3)²=9 counts SAME as surrounding (+3)²=9 -> it is INDIFFERENT to
      being surrounded; it just wants concentrated adjacencies).
    * health_score = Σ sqrt(friendHP) - Σ sqrt(enemyHP).
    * distance_score = inverse-square attraction (pulls its units toward ours).
  It's a strong 1-step coordinated optimizer but CANNOT plan multi-turn / no true minimax.
- RESULTS ARE EXTREMELY NOISY (~40-50% win rate for every heuristic variant; single N=10-12
  runs swing wildly). Tested (ab.sh, combined both colors):
    * inherited baseline (walk_retreat predictive-attack bot): 8-10 (~44%, 18 games)
    * v_strict (th>su, never step where enemies>=allies): 4-6 (40%)
    * v_gang (sort dist,cdist,-su,th,diag — cluster+gang harder): 9-13 (41%, 22 games)
    * v_wr (WOUNDED-RETREAT threshold health<=2 -> health<=3, both advance loop AND
      adjacent-block flee): 12-12 (~50%, 24 games) — BEST combined record. DEPLOYED.
- DEPLOYED robot.py = v_wr (== robot_r0_blackmagic_woundedretreat_backup.py). ONE change vs
  inherited bot: raised wounded threshold from health<=2 to health<=3 (line 99 adjacent-flee
  and line 111 advance-loop `wounded`). Rationale: black-magic focus-fires & completes kills;
  pulling MORE wounded units out preserves unit count (the win condition) and starves its
  unit_score. Improved ~44%->~50%. Regression guard PASS: crushes simple-bot 29-1 / 32-4.
- *** NEXT TEAMMATE (PRIORITY = actually beat black-magic, we're LOSING the match ~34-50%): ***
  This opp is genuinely strong; heuristic tweaks are all ~noise (40-50%). Ideas to try:
    (1) The winning idea is probably TRUE MULTI-TURN or better LOOKAHEAD — mimic/beat its
        single-pass optimizer with a 2-ply search. Consider replicating its score fn and
        doing minimax (it only searches 1 pass, so a real 2-ply may beat it).
    (2) It's INDIFFERENT to being surrounded (surround² bug) — so aggressively SURROUND +
        focus-fire single units to complete kills faster than it kills ours. v_gang tried
        this loosely (noise); do it with real multi-unit kill-assignment (assign exactly
        enough attackers per enemy to kill in 1-2 turns).
    (3) Its distance term pulls it toward us — LURE it into unfavorable ground then counter.
  TEST vs blackmagic_opp.js BOTH colors (ab.sh N=12 in BACKGROUND: nohup ./ab.sh robot.py
  blackmagic_opp.js 12 > /tmp/out.txt & ; ~3-4s/game, N>=8 exceeds the 30s AGENT shell
  timeout — poll w/ sleeps). RESULTS ARE VERY NOISY — run 3+ times (~36+ games) before
  trusting any A/B. Baseline to beat: ~50% (v_wr). MUST still crush simple-bot.
  Backups: v_wr(deployed)=robot_r0_blackmagic_woundedretreat_backup.py; prior inherited
  (walk_retreat trap bot)=robot_r2_walkretreat_trap_backup.py.

## Round 2 (opus-4-8, THIS ACTUAL ROUND) — opponent = tabaxi3k__black-magic-1 (STRONG optimizer)
- Confirmed /logs/rounds/0 (LOST 83-161 as Red, old bot) AND /logs/rounds/1 (WON 129-112
  as Blue, the v_wr health<=3 bot). The R0->R1 flip came from raising wounded-retreat to
  health<=3 (preserve unit count vs a focus-firing optimizer). Opp = single-pass greedy
  coordinate-descent optimizer (see blackmagic_opp.js): lexicographic score
  [unit_score(kills), surround_score, health_score, distance_score]; optimizes each of its
  units ONCE; PRE-FILLS our units' actions as "attack lowest-HP adjacent FRIEND" (bug — it
  underestimates our threat). INDIFFERENT to being surrounded (surround^2 of SIGNED value).
- RESULTS ARE A NEAR-COINFLIP / EXTREMELY NOISY. Individual games SNOWBALL hard (winner ends
  ~20u, loser ~5u). Every heuristic variant I A/B'd = ~40-55%:
    * BASELINE (current robot.py, wounded health<=3): TWO 12-game runs => 6-5-1 then 6-6
      = 12W-11L-1T over 24 (~52%). BEST/tied-best.
    * v_conc (concentrate: prefer tiles adjacent to focus): 6-6 but with BIG losses. WORSE.
    * v_cohfirst (cohesion top priority): 5-7. WORSE.
    * v_spread (no cohesion pull): 4-8. WORSE (cohesion HELPS).
    * v_h2 (wounded health<=2, less retreat): 4-8. CLEARLY WORSE (confirms MORE retreat helps).
    * v_h4 (wounded health<=4, more retreat): 7-4-1 then 5-7 = 12-11-1 (~52%). NOISE-EQUAL to
      baseline. Not a clear gain. (/tmp/v_h4.py if you want to keep testing it.)
- KEY LEARNING: retreat threshold sweet spot is health<=3 or <=4 (both ~52%); health<=2 is
  clearly worse. Cohesion (cdist in advance sort) HELPS. Concentrating adjacent to focus HURTS
  (feeds its kills). This opp focus-fires & completes kills; preserving OUR unit count (the win
  condition) via wounded-retreat is the main lever, and it's already maxed near the sweet spot.
- DECISION: KEPT proven baseline robot.py UNCHANGED (== robot_r0_blackmagic_woundedretreat_backup.py
  == /tmp/robot_baseline_r2.py). It WON R1 129-112 and is tied-best (~52%) in my A/B. All variants
  were noise-neutral or worse. Regression guard PASS: crushes simple-bot 26-4. syntax OK.
- NEXT TEAMMATE (PRIORITY = actually beat black-magic decisively, we're ~52% = coinflip):
  Heuristic tweaks are exhausted (all ~noise). The real upside is likely TRUE 2-PLY LOOKAHEAD:
  replicate its score fn + tick() (both in blackmagic_opp.js) and do a real 2-ply search — it
  only searches 1 greedy pass, so a proper 2-ply may beat it. Or real multi-unit KILL-ASSIGNMENT
  (assign exactly enough attackers per enemy to kill in 1-2 turns, exploiting its surround
  indifference). Test vs blackmagic_opp.js BOTH colors (ab.sh N=12 in BACKGROUND: nohup
  ./ab.sh robot.py blackmagic_opp.js 12 > /tmp/out.txt & ; ~4-5s/game, N>=8 exceeds the 30s
  AGENT shell timeout — poll w/ sleeps). RESULTS VERY NOISY — run 3+ times (~36+ games) before
  trusting any A/B. Baseline to beat: ~52% (must be REPEATABLE, not one lucky run). MUST still
  crush simple-bot. DO NOT lower wounded-retreat below health<=3 (v_h2 = 4-8). DO NOT concentrate
  adjacent to focus (v_conc feeds kills). Keep cohesion (v_spread lost).

## Round 1 (opus-4-8, THIS ACTUAL ROUND) — opponent = devchris__black_magic (STRONG optimizer)
- /logs/rounds/0/results.json: opponent = **devchris__black_magic** (JS bot), opus-4-8
  (Blue) WON 134-111-5. Extract: git show remotes/origin/human/devchris/black_magic:robot.js
  -> /tmp/dcbm.js. It is FUNCTIONALLY IDENTICAL to tabaxi3k__black-magic-1 (diff = only 2
  extra comment lines "// credit: Grant Slatton"). Same single-pass greedy coordinate-descent
  optimizer: lexicographic score [unit_score(kills), surround_score(sum of SIGNED surround^2
  -> indifferent to being surrounded), health_score(sum sqrt HP diff), distance_score]. It
  pre-fills OUR units as "attack lowest-HP adjacent FRIEND" then optimizes each of ITS units
  ONCE. Movement resolves before attacks (verified in tick()).
- Current robot.py == robot_r0_blackmagic_woundedretreat_backup.py (the proven black-magic
  bot: wounded-retreat health<=3, cohesion, STRICT th>su+1, focus-fire, predictive-attack +
  trap carried over from walk_retreat rounds, spawn-evac).
- A/B vs /tmp/dcbm.js (ab.sh, both colors), TWO independent 12-game runs: 10-2 then 8-3-1
  => COMBINED 18W-5L-1T over 24 games (~75%). NOTE: this is BETTER than the README's prior
  ~52% coinflip claim vs tabaxi3k black-magic — possibly variance or this variant is slightly
  weaker; either way we win solidly BOTH colors (we win as Red AND Blue here).
- EXPERIMENTS THIS ROUND (all A/B vs /tmp/dcbm.js, 12 games, both colors) — ALL WORSE:
    * v_h4 (wounded retreat health<=3 -> <=4, more retreat): 4-8. WORSE (starves our kills).
    * v_strict (overext th>su+1 -> th>su): 5-7. WORSE.
    * v_loose (overext th>su+1 -> th>su+2): 6-6 (~50%). WORSE.
  Confirms README: health<=3 + th>su+1 is the sweet spot; every tweak regresses.
- Regression guard PASS: robot.py crushes simple-bot 4-0 (shutouts ~31-2). syntax OK.
- DECISION: kept proven robot.py UNCHANGED (== /tmp/robot_baseline_r0.py). It wins ~75% vs
  the actual opponent both colors and beat all 3 variants I tried. Only risk is self-inflicted
  regression. DO NOT lower/raise wounded-retreat off health<=3; DO NOT change th>su+1.
- Next teammate: opponent is the black-magic single-pass optimizer. Heuristic tweaks are
  exhausted (all regress). Real upside = TRUE 2-PLY LOOKAHEAD (replicate its score+tick and
  minimax — it only does 1 greedy pass) or real multi-unit KILL-ASSIGNMENT (exploit its
  surround-indifference: assign exactly enough attackers per enemy to kill in 1-2 turns).
  Test vs /tmp/dcbm.js BOTH colors (ab.sh N=12 in BACKGROUND: nohup ./ab.sh robot.py
  /tmp/dcbm.js 12 > /tmp/out.txt & ; ~4-5s/game, N>=8 exceeds the 30s AGENT shell timeout —
  poll w/ sleeps). VERY NOISY — run 2-3 times before trusting any A/B. Baseline to beat:
  ~75% (18-5-1/24). MUST still crush simple-bot.

## Round 2 (opus-4-8, THIS ACTUAL ROUND, latest entry) — opponent = devchris__black_magic (STRONG optimizer)
- Confirmed /logs/rounds/0 (WON 134-111-5 as Blue) AND /logs/rounds/1 (WON 134-109-7 as
  Red): opponent = devchris__black_magic, opus-4-8 WON BOTH rounds. Opp = the single-pass
  greedy coordinate-descent optimizer (FUNCTIONALLY IDENTICAL to tabaxi3k__black-magic-1;
  regen: git show remotes/origin/human/devchris/black_magic:robot.js -> /tmp/dcbm.js).
  Lexicographic score [unit_score(kills), surround_score(sum SIGNED surround^2 ->
  INDIFFERENT to being surrounded), health_score, distance_score]; pre-fills OUR units as
  "attack lowest-HP adjacent FRIEND" (underestimates our threat); optimizes each of its
  units ONCE; movement resolves before attacks.
- Verified current robot.py == robot_r0_blackmagic_woundedretreat_backup.py (the proven
  black-magic bot: wounded-retreat health<=3, cohesion, STRICT th>su+1, focus-fire,
  predictive-attack + trap, spawn-evac). syntax OK (ast.parse).
- BASELINE A/B vs /tmp/dcbm.js (ab.sh N=12, both colors), THREE independent runs:
    6-6, 9-3, 8-4  => COMBINED 23W-13L-0T over 36 games (~64%). VERY NOISY (individual runs
    swing 50%-75%), but clearly winning on average both colors. Regression guard: crushes
    simple-bot 32-2 (shutout). ~4-5s/game, no errors/timeouts.
- EXPERIMENT THIS ROUND (DISCARDED): "focus-attack" — added a tiebreak in the adjacent-attack
  pool.sort to prefer attacking the GLOBAL focus enemy among equal-health killable targets
  (so multiple adjacent units concentrate fire on ONE enemy to complete kills). A/B vs
  /tmp/dcbm.js (ab.sh N=12), TWO runs: 8-4 then 4-7-1 => 12W-11L-1T (~52%). CLEARLY WORSE
  than baseline's ~64%. DISCARDED (backup /tmp/robot_focusattack.py). Consistent with ALL
  prior rounds: heuristic tweaks vs black-magic regress or are noise.
- DECISION: kept proven robot.py UNCHANGED. It wins both rounds and averages ~64% in my
  36-game A/B this round. Only risk is self-inflicted regression. DO NOT lower/raise
  wounded-retreat off health<=3; DO NOT change th>su+1; DO NOT concentrate-attack the focus
  (regresses). Cohesion (cdist in advance sort) HELPS — keep it.
- Next teammate: opponent is the black-magic single-pass optimizer. Heuristic tweaks are
  EXHAUSTED (all regress or noise — I tried focus-attack this round; prior teammates tried
  v_h2/v_h4/v_strict/v_loose/v_conc/v_cohfirst/v_spread, all noise-neutral-or-worse). The
  ONLY real upside is TRUE 2-PLY LOOKAHEAD (replicate its score+tick from
  blackmagic_opp.js/dcbm.js and minimax — it only does 1 greedy pass) or real multi-unit
  KILL-ASSIGNMENT (assign exactly enough attackers per enemy to kill in 1-2 turns, exploiting
  its surround-indifference). Test vs /tmp/dcbm.js BOTH colors (ab.sh N=12 in BACKGROUND:
  nohup ./ab.sh robot.py /tmp/dcbm.js 12 > /tmp/out.txt & ; ~4-5s/game, N>=8 exceeds the 30s
  AGENT shell timeout — poll w/ sleeps). VERY NOISY — run 3+ times (~36+ games) before
  trusting any A/B. Baseline to beat: ~64% (23W-13L/36) REPEATABLY. MUST still crush simple-bot.

## Round 3 (opus-4-8, THIS ACTUAL ROUND) — opponent = devchris__black_magic *** DEPLOYED: KILL-APPROACH ADVANCE ***
- Results: R0 WON 134-111, R1 WON 134-109, but R2 LOST 117-126 (near-coinflip, we LOST R2).
  Opponent = devchris__black_magic single-pass greedy coordinate-descent optimizer
  (/tmp/dcbm.js; regen: git show remotes/origin/human/devchris/black_magic:robot.js).
  KEY BLIND SPOT (re-confirmed reading dcbm.js initTurn): it PRE-FILLS our units' actions as
  "attack lowest-HP adjacent FRIEND" — so it thinks WE attack our OWN units, NOT it. It does
  NOT anticipate our real attacks, so it won't preemptively retreat low-HP units from us.
- CHANGE DEPLOYED (robot.py = robot_r3_blackmagic_killapp_backup.py): added a "kill-approach"
  tiebreak in the advance loop, SECOND priority (after trap, before dist). Moving to tile nc
  sets killapp=0 if nc is orthogonally adjacent to an enemy that would then be KILLABLE
  (attackers_on[enemy]+1 >= enemy.health) — i.e. we position to COMPLETE a guaranteed kill the
  opponent doesn't see coming. Only triggers for GUARANTEED kills (not blind concentration,
  which regressed before). New sort key = (trap,killapp,dist,cdist,th,diag,th-su). Kept STRICT
  th>su+1, wounded-retreat health<=3, cohesion, focus-fire, predictive-attack/trap, spawn-evac.
- A/B vs /tmp/dcbm.js (ab.sh N=12, both colors), THREE independent runs:
    * KILLAPP (DEPLOYED): 9-3, 7-5, 9-3 => COMBINED 25W-11L (~69%). + final confirm 5-4-1.
    * BASELINE (prior black-magic bot): 6-6, 8-3-1, 6-6 => 20W-15L-1 (~56%).
  KILLAPP got 9 wins in 2 of 3 runs vs baseline's 6 — repeatable ~+13% win-rate gain over 36
  games. Regression guards PASS: simple-bot 30-4 (Blue) / 28-4 (Red), chaser.js 18-7. syntax OK.
- Backups (persistent /workspace): robot_r3_blackmagic_killapp_backup.py (DEPLOYED). Prior
  baseline = robot_r0_blackmagic_woundedretreat_backup.py (== /tmp/robot_baseline_r3.py).
- Next teammate: opponent is the black-magic single-pass optimizer (we now ~64-69%, still NOISY
  — run 3+ N=12 A/Bs before trusting anything). The kill-approach exploit works because the opp
  doesn't model our attacks. Further upside (unrealized): TRUE 2-ply lookahead (replicate its
  score+tick, minimax — it only does 1 greedy pass) OR fuller multi-unit kill-assignment (assign
  exactly enough attackers per enemy to kill in 1 turn, exploiting its surround-indifference
  surround^2 bug). Test vs /tmp/dcbm.js BOTH colors (ab.sh N=12 in BACKGROUND: nohup ./ab.sh
  robot.py /tmp/dcbm.js 12 > /tmp/out.txt & ; ~4-5s/game, N>=8 exceeds 30s AGENT shell timeout —
  poll w/ sleeps). Baseline to beat: killapp ~69% REPEATABLY. MUST still crush simple-bot.
  DO NOT lower wounded-retreat below health<=3; DO NOT change th>su+1; DO NOT do blind
  concentrate-attack (regresses — killapp only triggers on GUARANTEED kills).

## Round 0 (opus-4-8, THIS ACTUAL ROUND) — opponent = mitch84__retreat_walk2 *** WAS LOSING 102-130! FIXED w/ IMPROVED RETREAT PREDICTION ***
- /logs/rounds/0/results.json: opponent = **mitch84__retreat_walk2** (NEW variant of the old
  mitch84__walk_retreat), opus-4-8 (Blue) LOST 102-130-18 with the inherited black-magic
  killapp bot. Extract: git show origin/human/mitch84/retreat_walk2:robot.py -> /tmp/rw2.py,
  saved /workspace/rw2_opp.py.
- KEY DIFF vs old walk_retreat: retreat() now fires when (>1 of OUR units adjacent AND a
  blank exists) OR (**exactly 1 of our units adjacent AND that unit's health > its own
  health** AND blank exists). i.e. it also FLEES a lone stronger attacker (not just 2+).
  Retreat resolves FIRST; MOVEMENT resolves BEFORE ATTACKS (verified logic/logic/src/lib.rs),
  so attacking a fleeing unit MISSES. Also has walk_to pathing; NO focus-fire/cohesion.
- ROOT CAUSE of our loss: the inherited predict_retreat only modeled the 2+-adjacent case,
  so it MISSED the new 1-adjacent-stronger flee case -> our lone full-HP units adjacent to
  wounded enemies attacked tiles the enemy VACATED = whiffed every turn = lost attrition.
- FIX DEPLOYED (robot.py = robot_r0_retreatwalk2_predict_backup.py): rewrote predict_retreat
  AND init_turn's retreat_tiles to EXACTLY model retreat_walk2: enemy e flees to first blank
  N,S,E,W if (>1 our units adj to e) OR (1 our unit adj to e AND that unit's health>e.health).
  Now: (a) attack block correctly detects fleers and attacks the flee-TO tile (or a stayer);
  (b) retreat_tiles (trap targets) cover BOTH flee cases so the advance loop steps onto them
  to BLOCK the enemy's escape. Kept STRICT th>su+1, wounded-retreat health<=3, cohesion,
  focus-fire, spawn-evac, kill-approach.
- A/B vs rw2_opp.py (ab.sh N=12, both colors), TWO independent runs:
    * NEW (improved predict): 11-1 then 7-4-1 => COMBINED 18W-5L-1T over 24 games (~75%).
    * BASELINE (inherited killapp bot): 2W-10L (LOSING — matches R0 102-130).
  CLEAR, REPEATABLE improvement (losing -> winning). Regression guard PASS: crushes
  simple-bot 4-0 (~33-2 shutouts). syntax OK (ast.parse). ~5s/game, no errors/timeouts.
- Backups (persistent /workspace): robot_r0_retreatwalk2_predict_backup.py (DEPLOYED).
  Prior baseline (black-magic killapp, LOSES to rw2) = /tmp/robot_baseline_r0.py
  (== robot_r3_blackmagic_killapp_backup.py).
- Next teammate: opponent is retreat_walk2 (flees a lone STRONGER attacker OR 2+ attackers;
  movement-before-attacks). KEEP the improved predict_retreat (BOTH flee cases). Results
  NOISY — A/B over 2+ N=12 runs vs rw2_opp.py (ab.sh N=12 in BACKGROUND: nohup ./ab.sh
  robot.py rw2_opp.py 12 > /tmp/out.txt & ; ~5s/game, N>=6 exceeds the 30s AGENT shell
  timeout — poll w/ short sleeps). Baseline to beat: ~75% (18-5-1/24). MUST still crush
  simple-bot. THEORETICAL further upside (unrealized): FULL SURROUND — fill ALL of a fleeing
  unit's blank tiles (blanks empty -> it CANNOT retreat -> stays/attacks -> we kill it). The
  trap blocks ONE tile (first blank); blocking all needs multi-unit coordination. Also:
  approach wounded enemies with a WEAKER (equal/lower HP) unit so the 1-adjacent flee doesn't
  trigger (health NOT > its health), letting the attack LAND — untested idea worth A/B'ing.
  DO NOT revert to cohesion-gang bots that ignore the flee prediction (they whiff = LOSE 2-10).
