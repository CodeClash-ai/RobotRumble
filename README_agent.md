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

## ROUND (this session, opus-4-8) UPDATE — IMPORTANT CORRECTIONS
- analyze_round.py has SWAPPED SIDES for round 0 logs: results.json says
  "happysquid__test was Blue and opus-4-8 was Red", so WE ARE RED (B) there.
  The script's "-18.90 margin" = Red(us) - Blue = we WON 250-0 ("Red won").
  => Do NOT trust analyze_round.py's WIN/LOSS labels; check results.json.
- Opponent name is uncertain: README earlier said anton__anton3000 but round 0
  log is vs happysquid__test. Either way current bot dominates that opponent.

## IMPROVED robot.py (v2) — adopted this round
Added GROUPING to movement scoring + stronger anti-dive:
  - Compute ally centroid (excl self); tie-break moves toward it (group_dist)
    so units advance as a pack and win trades.
  - Danger penalty raised: outnumbered*4 (was *3) in effective approach cost.
Backups: robot_baseline.py (old), robot_v2.py (== current robot.py).
Results (compare_bots.sh, WIN=BLUE=first arg):
  - vs heuristic-bot: 17/20 wins as Blue (was 9/20), 8/10 as Red (was ~5/10).
  - v2 vs baseline head-to-head: 5-1. Crushes simple(26-2), flail(12-8).
  - Still LOSE to black-magic (strong minimax) — unlikely to be our opponent.
Test harness: ./compare_bots.sh <blue> <red> <nseeds>  (fixed parser).
  NOTE: bash calls time out ~30s; keep nseeds<=12 per invocation.

## Next teammate ideas
- To beat black-magic, need a lookahead like its own score() (unit,surround,
  health,distance). Could port that scorer and do 1-ply best-response.
- Model diamond map (is_legal_coordinate in black-magic.js) to avoid illegal
  moves; our in_bounds() only uses MAP_SIZE square, may waste moves at edges.

## ROUND 2 SESSION (opus-4-8) — DECISION: KEEP robot.py UNCHANGED
- Confirmed opponent = happysquid__test (NOT anton). Rounds 0 & 1 BOTH 250-0.
- Analyzed round 1: 250/250 seed wins, avg unit margin +25.6 (we=Red=B).
- robot.py == robot_v2.py (v2 grouping+anti-dive active). Verified working:
  vs simple-bot 25-0; vs heuristic-bot 7/8 seeds WIN.
- Tried retreat threshold hp<=2 -> hp<=3: REGRESSED vs heuristic (3/6 vs 6/6),
  did NOT fix black-magic loss. Discarded. DO NOT raise retreat threshold.
- Still lose to black-magic (needs full lookahead rewrite = high risk). happysquid
  is far weaker, so not worth risking our perfect record.
- CONCLUSION: No code change. robot.py stays. It maximizes score vs this opponent.
  Next teammate: only change the bot if happysquid suddenly upgrades (check
  /logs/rounds/N/results.json and sim margins first). If so, port a black-magic
  style 1-ply best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = anton__wallifier (name suggests a "wall" builder).
- Round 0 log (in /logs/rounds/0/): we WON 250-0. We are RED (B) there.
  End state sim_0: Health 0 vs 135, Units 0 vs 29 — total domination.
- Observed opponent behavior (sim_0): anton spreads units thinly across the
  map, never groups; our focus-fire + grouped-advance crushes it. At turn 20
  we (Red) already led 11 units/55hp vs their 6/29.
- Sanity checks this session (robot.py, default seed):
    simple-bot: WIN 28-0 | needle-bot: WIN 18-1 | chaser: WIN 3-2 (closer)
- robot.py == robot_v2.py (grouping + anti-dive*4 active). Verified functional,
  full match ~3.5s (well under 60s limit).
- CONCLUSION: No code change. Bot already maxes score (250-0) vs this opponent.
  Touching a perfect result only risks regression. Next teammate: only change if
  anton__wallifier upgrades (check /logs/rounds/N/results.json + sim end states).
  If forced to improve robustness, target chaser/black-magic via a 1-ply
  best-response scorer (see earlier notes) rather than tweaking retreat/dive.

## ROUND 2 SESSION (opus-4-8) — DECISION: KEEP robot.py UNCHANGED
- Confirmed opponent = anton__wallifier. Rounds 0 & 1 BOTH scored 250-0 (we=Red).
- Reviewed round 1 sim end states: we consistently finish with 25-32 units vs 0-2
  for the opponent across all 250 seeds. Total domination.
- Sanity check this session: robot.py vs simple-bot = WIN 35-0, runtime ~4.4s
  (well under 60s limit). Bot is functional and fast.
- robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. The bot maximizes score (250-0) vs anton__wallifier.
  Any tweak risks regressing a perfect result for zero upside vs this opponent.
  Next teammate: only change if anton__wallifier upgrades (check
  /logs/rounds/N/results.json + sim margins). If forced to improve robustness
  (e.g. new stronger opponent like black-magic), port a 1-ply best-response
  scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, ldang__nessy) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = ldang__nessy (NEW opponent, first appearance).
- Round 0 result: WON 250-0 (we=Red=B). scores: ldang__nessy 0, opus-4-8 250.
  End states (sim_0: 27u/102hp vs 2u/4hp; sim_5: 25u/106hp vs 0u/0hp). Domination.
- Opponent behavior (sim_0): spreads 4 units to map corners, adds reinforcements
  scattered thinly, never groups. By turn 30 we lead 13u/60hp vs 5u/22hp.
  Our grouped focus-fire + anti-dive crushes it every seed.
- Sanity check: robot.py == robot_v2.py (grouping + anti-dive*4). vs simple-bot
  WIN 28-0, runtime ~3.2s (well under 60s limit). Functional & fast.
- CONCLUSION: No code change. Bot maxes score (250-0) vs ldang__nessy. Any tweak
  risks regressing a perfect result for zero upside. Next teammate: only change
  if ldang__nessy upgrades (check /logs/rounds/N/results.json + sim margins).
  If forced to improve robustness vs a stronger bot (black-magic style), port a
  1-ply best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, ldang__nessy) — DECISION: KEEP robot.py UNCHANGED
- Opponent = ldang__nessy. Rounds 0 & 1 BOTH scored 250-0 (we=Red=B).
- analyze_round.py margin -27.34 (round 1) = we WON by ~27 units/sim (script
  labels are swapped; trust results.json which shows opus-4-8 score 250 both rounds).
- Sanity checks this session (robot.py vs simple-bot, ~3.3s runtime, well under 60s):
    default seed: WIN 31-0 | seed1: WIN 26-2 | seed7: WIN 30-0 | seed42: WIN 26-1.
  Dominant across all seeds. Bot functional & fast, no regression.
- robot.py == robot_v2.py (grouping + anti-dive*4). Untouched.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs ldang__nessy. Any
  tweak risks regressing a perfect result for zero upside vs this opponent.
  Next teammate: only change if ldang__nessy upgrades (check results.json + sim
  margins). If forced to improve robustness vs a stronger bot (black-magic style),
  port a 1-ply best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, ldang__nemo) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = ldang__nemo (name variant of ldang family). Round 0 = WON
  250-0 (we=Red=B). results.json: opus-4-8 250, ldang__nemo 0. analyze_round.py
  margin -26.82 (labels swapped) => we WON by ~27 units/sim. Domination.
- End states: sim_0 = 1u/4hp vs 29u/126hp; sim_42 = 3u/9hp vs 28u/113hp (us=Red).
  Opponent spreads units thinly, never groups; our grouped focus-fire crushes it.
- Sanity checks this session (robot.py vs simple-bot, ~3s runtime <<60s limit):
    default: WIN 26-0 | seed1: WIN 26-2 | seed7: WIN 30-0. Functional & fast.
- robot.py == robot_v2.py (grouping + anti-dive*4). Untouched, no regression.
- CONCLUSION: No code change. Bot maxes score (250-0) vs ldang__nemo. Any tweak
  risks regressing a perfect result for zero upside. Next teammate: only change
  if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, ldang__nemo) — DECISION: KEEP robot.py UNCHANGED
- Opponent = ldang__nemo. Rounds 0 & 1 BOTH scored 250-0 (results.json: opus-4-8
  250, ldang__nemo 0). Total domination continues.
- Sanity check this session: robot.py vs simple-bot = WIN 27-1, runtime ~3.4s
  (well under 60s limit). Bot functional & fast, no regression.
- robot.py == robot_v2.py (grouping + anti-dive*4). Untouched.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs ldang__nemo. Any
  tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if ldang__nemo upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, navster8__bash-brothers) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = navster8__bash-brothers (NEW opponent). Round 0 = WON
  250-0 (results.json: opus-4-8 250, navster8__bash-brothers 0). We are Red (B).
- All 250 seed sims = "Red won" (verified via grep). Total domination, e.g.
  sim_0: 33u/131hp vs 0u/0hp; sim_42: 31u/139hp vs 0u/0hp. Opponent wiped out.
- Sanity check this session: robot.py vs simple-bot = WIN 26-1, runtime ~3.2s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs navster8__bash-brothers.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, navster8__bash-brothers) — DECISION: KEEP robot.py UNCHANGED
- Opponent = navster8__bash-brothers. Rounds 0 & 1 BOTH scored 250-0
  (results.json: opus-4-8 250, navster8__bash-brothers 0). We are Red (B).
- Verified round 1: all 250 seed sims = "Red won" (grep uniq count = 250). Total domination.
- Sanity check this session: robot.py vs simple-bot = WIN 27-1, runtime ~3.2s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs this opponent.
  Any tweak risks regressing a perfect result for zero upside. Next teammate:
  only change if the opponent upgrades (check results.json + sim margins). If
  forced to improve robustness vs a stronger bot (black-magic style), port a
  1-ply best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, aaoutkine__dark-knight) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = aaoutkine__dark-knight (NEW opponent). Round 0 = WON
  250-0 (results.json: opus-4-8 250, aaoutkine__dark-knight 0). We are Red (B).
- Verified round 0: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 17u/80hp vs 1u/5hp; sim_42: 31u/144hp vs 1u/3hp;
  sim_123: 28u/136hp vs 0u/0hp. Opponent finishes with 0-1 units every seed.
- Opponent behavior: spreads units thinly / never groups (same weakness as prior
  opponents); our grouped focus-fire + anti-dive crushes it.
- Sanity check this session: robot.py vs simple-bot = WIN 24-1, runtime ~3.1s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs aaoutkine__dark-knight.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, aaoutkine__dark-knight) — DECISION: KEEP robot.py UNCHANGED
- Opponent = aaoutkine__dark-knight. Rounds 0 & 1 BOTH scored 250-0
  (results.json: opus-4-8 250, aaoutkine__dark-knight 0).
- Verified round 1: all 250 seed sims = "Blue won" (we were Blue this round;
  grep uniq count = 250/250). Total domination.
- Sanity checks this session:
    robot.py vs simple-bot: WIN 28-3, runtime ~3.3s (well under 60s limit).
    robot.py vs heuristic-bot seeds 1-5: WIN all 5 (units 9-7,10-7,15-5,11-9,10-4).
  Bot functional, fast, robust vs heuristic. robot.py == robot_v2.py (no regression).
- CONCLUSION: No code change. Bot maximizes score (250-0) vs this opponent.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, mountain__neuralbot1-1h) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = mountain__neuralbot1-1h (NEW opponent). Round 0 = WON
  250-0 (results.json: opus-4-8 250, mountain__neuralbot1-1h 0). We are Red (B).
- Verified round 0: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 29u/121hp vs 2u/6hp; sim_42: 26u/104hp vs 0u/0hp;
  sim_123: 31u/121hp vs 0u/0hp. Opponent finishes with 0-2 units every seed.
- Opponent spreads units thinly / never groups (same weakness as prior opponents);
  our grouped focus-fire + anti-dive crushes it.
- Sanity check this session: robot.py vs simple-bot = WIN 22-0, runtime ~2.6s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs mountain__neuralbot1-1h.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, mountain__neuralbot1-1h) — DECISION: KEEP robot.py UNCHANGED
- Opponent = mountain__neuralbot1-1h. Rounds 0 & 1 BOTH scored 250-0
  (results.json: opus-4-8 250, mountain__neuralbot1-1h 0). Round 0 we were Red,
  round 1 we were Blue.
- Verified round 1: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination.
- Sanity check this session: robot.py vs simple-bot = WIN 25-0, runtime ~3.3s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs this opponent.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, sivecano__clouded-mind) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = sivecano__clouded-mind (NEW opponent). Round 0 = WON
  250-0 (results.json: opus-4-8 250, sivecano__clouded-mind 0). We are Red (B).
- Verified round 0: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 26u/126hp vs 1u/4hp; sim_42: 25u/122hp vs 1u/5hp;
  sim_123: 30u/145hp vs 1u/1hp. Opponent finishes with ~1 unit every seed.
- Opponent spreads units thinly / never groups (same weakness as prior opponents);
  our grouped focus-fire + anti-dive crushes it.
- Sanity check this session: robot.py vs simple-bot = WIN 26-2, runtime ~3.3s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs sivecano__clouded-mind.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, sivecano__clouded-mind) — DECISION: KEEP robot.py UNCHANGED
- Opponent = sivecano__clouded-mind. Rounds 0 & 1 BOTH scored 250-0
  (results.json: opus-4-8 250, sivecano__clouded-mind 0). We are Red (B).
- Verified round 1: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Total domination.
- Sanity checks this session (well under 60s limit):
    robot.py vs simple-bot: WIN 23-0, runtime ~3.2s.
    robot.py vs heuristic-bot seeds 1-3: WIN all 3 (9-7, 10-7, 15-5).
  robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs this opponent.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, mountain__neuralbot2-6h) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = mountain__neuralbot2-6h (variant of neuralbot family).
  Round 0 = WON 250-0 (results.json: opus-4-8 250, mountain__neuralbot2-6h 0).
  We are Red (B).
- Verified round 0: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 30u/143hp vs 0u/0hp; sim_42: 30u/145hp vs 0u/0hp;
  sim_123: 29u/142hp vs 1u/5hp. Opponent finishes with 0-1 units every seed.
- Opponent spreads units thinly / never groups (same weakness as prior opponents);
  our grouped focus-fire + anti-dive crushes it.
- Sanity check this session: robot.py vs simple-bot = WIN 29-1, runtime ~3.4s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs mountain__neuralbot2-6h.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, mountain__neuralbot2-6h) — DECISION: KEEP robot.py UNCHANGED
- Opponent = mountain__neuralbot2-6h. Rounds 0 & 1 BOTH scored 250-0
  (results.json: opus-4-8 250, opponent 0). Round 0 we were Red, round 1 Blue.
- Verified round 1: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination.
- Sanity check this session: robot.py vs simple-bot = WIN 25-2, runtime ~2.9s
  (well under 60s). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs this opponent.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, kalkin__artemis) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = kalkin__artemis (NEW opponent). Round 0 = WON 250-0
  (results.json: opus-4-8 250, kalkin__artemis 0). We are Red (B).
- Verified round 0: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 23u/85hp vs 4u/13hp; sim_42: 25u/90hp vs 4u/12hp;
  sim_123: 28u/104hp vs 2u/8hp. Opponent finishes with 2-4 units every seed.
- Opponent spreads units thinly / never groups (same weakness as prior opponents);
  our grouped focus-fire + anti-dive crushes it.
- Sanity check this session: robot.py vs simple-bot = WIN 28-0, runtime ~3.2s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs kalkin__artemis.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, kalkin__artemis) — DECISION: KEEP robot.py UNCHANGED
- Opponent = kalkin__artemis. Rounds 0 & 1 BOTH scored 250-0 (results.json:
  opus-4-8 250, kalkin__artemis 0). Round 0 we were Red, round 1 we were Blue.
- Verified round 1: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination.
- Sanity check this session: robot.py vs simple-bot = WIN 27-0, runtime ~3.0s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs kalkin__artemis.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, kalkin__artemis2) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = kalkin__artemis2 (variant of kalkin__artemis, which we
  crushed 250-0 in earlier matches). Round 0 = WON 250-0 (results.json: opus-4-8
  250, kalkin__artemis2 0). We are Red (B).
- Verified round 0: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 13u/45hp vs 2u/7hp; sim_42: 17u/44hp vs 0u/0hp;
  sim_123: 14u/50hp vs 3u/7hp. Opponent finishes with 0-3 units every seed.
- Sanity check this session: robot.py vs simple-bot = WIN 28-0, runtime ~2.9s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs kalkin__artemis2.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, kalkin__artemis2) [2nd occurrence] — DECISION: KEEP robot.py UNCHANGED
- Opponent = kalkin__artemis2. Rounds 0 & 1 BOTH scored 250-0 (results.json:
  opus-4-8 250, kalkin__artemis2 0). We were Red both rounds.
- Verified round 1: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Total domination.
- Sanity check this session: robot.py vs simple-bot = WIN 26-0, runtime ~3.0s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs kalkin__artemis2.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, navster8__maginot-line) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = navster8__maginot-line (NEW; name suggests a defensive
  "wall" strategy). Round 0 = WON 250-0 (results.json: opus-4-8 250,
  navster8__maginot-line 0). We were BLUE this round.
- Verified round 0: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 35u/158hp vs 0u/0hp; sim_42: 32u/148hp vs 0u/0hp;
  sim_123: 35u/175hp vs 1u/4hp. Opponent finishes with 0-1 units every seed.
- Sanity check this session: robot.py vs simple-bot = WIN 22-0, runtime ~3.1s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs navster8__maginot-line.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, navster8__maginot-line) [2nd occurrence] — DECISION: KEEP robot.py UNCHANGED
- Opponent = navster8__maginot-line. Rounds 0 & 1 BOTH scored 250-0 (results.json:
  opus-4-8 250, navster8__maginot-line 0). We were BLUE both rounds.
- Verified round 1: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 32u/146hp vs 0u/0hp; sim_42: 24u/114hp vs 1u/1hp.
- Sanity check this session: robot.py vs simple-bot = WIN 25-1, runtime ~3.1s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs navster8__maginot-line.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, jiricodes__jiricodes-bot) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = jiricodes__jiricodes-bot (NEW opponent). Round 0 = WON
  250-0 (results.json: opus-4-8 250, jiricodes__jiricodes-bot 0). We were BLUE.
- Verified round 0: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 31u/154hp vs 0u/0hp; sim_42: 33u/163hp vs 0u/0hp;
  sim_123: 34u/169hp vs 0u/0hp. Opponent finishes with 0 units every seed.
- Sanity check this session: robot.py vs simple-bot = WIN 25-1, runtime ~3.0s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs jiricodes__jiricodes-bot.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, jiricodes__jiricodes-bot) [2nd occurrence] — DECISION: KEEP robot.py UNCHANGED
- Opponent = jiricodes__jiricodes-bot. Rounds 0 & 1 BOTH scored 250-0
  (results.json: opus-4-8 250, jiricodes__jiricodes-bot 0). We were BLUE both rounds.
- Verified round 1: all 250 seed sims = "Blue won" (grep count = 250/250).
  Total domination, e.g. sim_0: 29u/142hp vs 0u/0hp; sim_123: 26u/130hp vs 1u/1hp.
- Sanity check this session: robot.py vs simple-bot = WIN 30-0, runtime ~3.4s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs jiricodes__jiricodes-bot.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, sbasu3__meek-bot) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = sbasu3__meek-bot (NEW opponent). Round 0 = WON 250-0
  (results.json: opus-4-8 250, sbasu3__meek-bot 0). We are Red (B).
- Verified round 0: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 8u/25hp vs 0u/0hp; sim_42: 15u/52hp vs 2u/10hp;
  sim_123: 8u/22hp vs 1u/5hp. Opponent finishes with 0-2 units every seed.
- Sanity check this session: robot.py vs simple-bot = WIN 29-0, runtime ~3.9s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs sbasu3__meek-bot.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, sbasu3__meek-bot) [2nd occurrence] — DECISION: KEEP robot.py UNCHANGED
- Opponent = sbasu3__meek-bot. Rounds 0 & 1 BOTH scored 250-0 (results.json:
  opus-4-8 250, sbasu3__meek-bot 0). Round 0 we were Red, round 1 we were Blue.
- Verified round 1: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination.
- Sanity check this session: robot.py vs simple-bot = WIN 32-0, runtime ~3.7s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs sbasu3__meek-bot.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, essickmango__fruity-test) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = essickmango__fruity-test (NEW opponent). Round 0 = WON
  250-0 (results.json: opus-4-8 250, essickmango__fruity-test 0). We were BLUE.
- Verified round 0: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 15u/50hp vs 2u/9hp; sim_42: 20u/75hp vs 1u/5hp;
  sim_123: 17u/62hp vs 2u/9hp. Opponent finishes with 1-2 units every seed.
- Sanity check this session: robot.py vs simple-bot = WIN 26-0, runtime ~3.3s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs essickmango__fruity-test.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, essickmango__fruity-test) [2nd occurrence] — DECISION: KEEP robot.py UNCHANGED
- Opponent = essickmango__fruity-test. Rounds 0 & 1 BOTH scored 250-0
  (results.json: opus-4-8 250, essickmango__fruity-test 0). Round 0 we were Blue,
  round 1 we were Red.
- Verified round 1: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Domination, e.g. sim_0: 11u/39hp vs 2u/4hp; sim_1: 15u/57hp vs 0u/0hp;
  sim_5: 20u/74hp vs 2u/6hp; sim_100: 14u/50hp vs 4u/9hp. Margins are somewhat
  tighter than versus some earlier opponents (we finish ~11-20u vs 0-4u) but
  every seed is a clean win.
- Sanity check this session: robot.py vs simple-bot = WIN 26-0, runtime ~3.6s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs this opponent.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, tabaxi3k__charles) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = tabaxi3k__charles (NEW opponent). Round 0 = WON 250-0
  (results.json: opus-4-8 250, tabaxi3k__charles 0). We were BLUE.
- Verified round 0: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 28u/137hp vs 0u/0hp; sim_42: 36u/177hp vs 0u/0hp;
  sim_123: 31u/153hp vs 1u/1hp. Opponent finishes with 0-1 units every seed.
- Sanity check this session: robot.py vs simple-bot = WIN 33-1, runtime ~4.2s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs tabaxi3k__charles.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, tabaxi3k__charles) [2nd occurrence] — DECISION: KEEP robot.py UNCHANGED
- Opponent = tabaxi3k__charles. Rounds 0 & 1 BOTH scored 250-0 (results.json:
  opus-4-8 250, tabaxi3k__charles 0). We were BLUE both rounds.
- Verified round 1: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 33u/162hp vs 0u/0hp; sim_42: 32u/156hp vs 0u/0hp;
  sim_123: 27u/131hp vs 0u/0hp. Opponent finishes with 0 units every seed.
- Sanity check this session: robot.py vs simple-bot = WIN 33-2, runtime ~4.0s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs tabaxi3k__charles.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, devchris__first_test) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = devchris__first_test (NEW opponent). Round 0 = WON 250-0
  (results.json: opus-4-8 250, devchris__first_test 0). We were BLUE.
- Verified round 0: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  Total domination, e.g. sim_0: 32u/156hp vs 1u/5hp; sim_42: 33u/161hp vs 0u/0hp;
  sim_123: 27u/134hp vs 0u/0hp. Opponent finishes with 0-1 units every seed.
- Sanity check this session: robot.py vs simple-bot = WIN 26-1, runtime ~3.8s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs devchris__first_test.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, devchris__first_test) [2nd occurrence] — DECISION: KEEP robot.py UNCHANGED
- Opponent = devchris__first_test. Rounds 0 & 1 BOTH scored 250-0 (results.json:
  opus-4-8 250, devchris__first_test 0). Round 0 we were Blue, round 1 we were Red.
- Verified round 1: all 250 seed sims = "Red won" (grep count = 250/250). Domination.
- Sanity check this session: robot.py vs simple-bot = WIN 29-1, runtime ~3.4s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs devchris__first_test.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, aaa__jippty5) — CODE CHANGED (legal_coord + spawn logic)
- Opponent THIS round = aaa__jippty5 (NEW, STRONGER than prior opponents).
  Round 0 result: opus-4-8 247, Tie 2, aaa__jippty5 1 (NOT a clean 250-0!).
  We are RED. Non-wins: sim_201 tie(8-8), sim_229 tie(5-5), sim_79 LOSS(6-7).
  These were close games where our units ended scattered.
- ROOT-CAUSE ANALYSIS of missed mechanics in the old bot (robot_prev_247.py):
  1. Map is a 19x19 OCTAGONAL arena (walls cut corners). Old in_bounds() used a
     plain square 0..MAP_SIZE check -> bot tried illegal moves at edges (rejected
     = wasted turns). FIXED: added legal_coord() mirroring black-magic's
     is_legal_coordinate (x,y in 1..17 with 4 diagonal cutoffs).
  2. SPAWN CLEARING: logic/lib.rs clear_spawn() runs at START of turns 11,21,31...
     (when (turn-1)%10==0) and DELETES any unit (friend OR foe) sitting on a
     spawn cell, right before new units spawn. Old bot ignored this -> units
     lingering on edge spawn cells died for free. FIXED: embedded SPAWN_CELLS set
     (48 edge cells; do NOT use Coords.is_spawn() — rumblelib bug: it checks a
     `map` generator that is exhausted after first use = unreliable). Added:
       - movement spawn penalty (mild always=+1; +100 when clearing_next so we
         never end a turn on spawn right before a clear).
       - SPAWN ESCAPE branch (before attack): if clearing_next and on a spawn
         cell, move to a legal empty non-spawn cell instead of attacking/staying.
- clearing_next = (state.turn % 10 == 0): our move this turn lands us off-spawn
  before turn+1's clear.
- TESTING:
    robot.py vs simple-bot: 32u-0 / 27u-0 (old bot got ~24u) -> fewer wasted moves.
    robot.py vs heuristic-bot: WIN 6/6 seeds (old also won). No regression.
  NOTE: head-to-head mirror (new vs prev) is swingy/side-asymmetric on the
  diamond map (blue/red start differently) -> NOT a reliable signal; ignore it.
  Both changes are strictly-correct game-mechanics fixes, so kept.
- Backups: robot_prev_247.py (old 247-score bot), robot_v2.py (== new robot.py).
- Next teammate: if this still isn't 250-0 vs aaa__jippty5, consider exploiting
  spawn clearing OFFENSIVELY (don't waste attacks on enemies about to be auto-
  cleared; or push enemies to linger). Also consider 1-ply best-response scorer
  (black-magic style) for the truly close seeds. Timing ~3.8s, ample headroom.

## ROUND 2 SESSION (opus-4-8, aaa__jippty5) [after legal_coord+spawn fix] — KEEP robot.py UNCHANGED
- Opponent = aaa__jippty5 (STRONGER than the older opponents). History:
  Round 0 (OLD bot, robot_prev_247.py): opus-4-8 247, Tie 2, aaa__jippty5 1
    (we were Red; 1 loss sim_79 6-7, ties sim_201 8-8 / sim_229 5-5 — close
    scattered endgames).
  Round 1 (NEW bot with legal_coord + spawn-clearing fix): 250-0, ALL Blue wins
    (grep uniq count = 250/250). The fix converted the close/tie/loss seeds into
    clean wins => the diamond-map legal_coord + spawn-escape logic was the key.
- Sanity checks this session (all well under 60s; runtime ~3.8s):
    robot.py vs simple-bot: WIN 32-1.
    robot.py vs heuristic-bot: seed1 WIN 12-5, seed201 WIN 11-7, seed229 WIN 21-4,
      seed79 TIE 10-10 (heuristic is much stronger than aaa__jippty5; the lone
      tie is vs heuristic, NOT our opponent).
- robot.py == robot_v2.py (grouping + anti-dive*4 + legal_coord + spawn logic).
  No regression. Confirmed the current file already has the round-1-winning code.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs aaa__jippty5 after
  the spawn/legal-coord fix. Any tweak risks regressing a perfect result for zero
  upside vs this opponent. Next teammate: only change if aaa__jippty5 upgrades
  (check results.json + sim margins). Remaining robustness gap is vs heuristic/
  black-magic (stronger than our opponent) — would need a 1-ply best-response
  scorer, high risk. Not worth it while we score 250-0.

## ROUND 1 SESSION (opus-4-8, jay0jayjay__naivestarter) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = jay0jayjay__naivestarter (NEW opponent; name suggests a
  naive starter template). Round 0 = WON 250-0 (results.json: opus-4-8 250,
  jay0jayjay__naivestarter 0). We are RED (B).
- Verified round 0: all 250 seed sims = "Red won" (grep count = 250/250, 0 Blue).
  Total domination, e.g. sim_0: 26u/90hp vs 1u/1hp; sim_42: 22u/69hp vs 6u/10hp;
  sim_123: 25u/88hp vs 5u/9hp. Opponent finishes with 1-6 units every seed.
- Sanity check this session: robot.py vs simple-bot = WIN 35-0, runtime ~4.8s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4 +
  legal_coord + spawn logic). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs jay0jayjay__naivestarter.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if the opponent upgrades (check results.json + sim margins). If forced to
  improve robustness vs a stronger bot (heuristic/black-magic style), port a 1-ply
  best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, jay0jayjay__naivestarter) [2nd occurrence] — KEEP robot.py UNCHANGED
- Opponent = jay0jayjay__naivestarter. Rounds 0 & 1 BOTH scored 250-0
  (results.json: opus-4-8 250, jay0jayjay__naivestarter 0). Round 0 we were Red,
  round 1 we were Blue.
- Verified round 1: all 250 seed sims = "Blue won" (grep count = 250/250). Domination.
- Sanity check this session: robot.py vs simple-bot = WIN 34-0, runtime ~3.9s
  (well under 60s limit). robot.py == robot_v2.py (grouping + anti-dive*4 +
  legal_coord + spawn logic). No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs this opponent.
  Any tweak risks regressing a perfect result for zero upside. Next teammate:
  only change if the opponent upgrades (check results.json + sim margins). If
  forced to improve robustness vs a stronger bot (heuristic/black-magic style),
  port a 1-ply best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, luisa__luisasrobot) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = luisa__luisasrobot (NEW opponent, one of the STRONGER
  ones — trades units efficiently early, tighter margins than most). Round 0 =
  WON 250-0 (results.json: opus-4-8 250, luisa__luisasrobot 0). We were BLUE.
- Verified round 0: all 250 seed sims = "Blue won" (grep uniq count = 250/250).
  BUT margins are tighter than usual: sim_0 7u/26hp vs 2u/9hp; sim_42 12u vs 3u;
  sim_123 10u vs 4u; sim_79 10u vs 2u. Opponent survives with 2-4 units each seed
  (vs 0-1 for weaker opponents). Early game is often even (turn 20 ~7v6) then our
  focus-fire pulls ahead. Still a clean 250-0 sweep.
- Opponent behavior (sim_0): starts 4 units in corners, advances toward center in
  pairs, trades 1-for-1 in early skirmishes. More aggressive/competent than the
  "spread thin, never group" opponents seen before, but still loses every seed.
- Sanity checks this session (all well under 60s limit):
    robot.py vs simple-bot: WIN 32-0, runtime ~3.8s.
    robot.py vs heuristic-bot: seed1 WIN 12-5, seed42 WIN 15-4, seed79 TIE 10-10.
  robot.py == robot_v2.py (grouping + anti-dive*4 + legal_coord + spawn logic).
  No regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs luisa__luisasrobot.
  Margins are tighter but every seed is still a win, so any tweak risks regressing
  a perfect result for zero upside. Next teammate: WATCH THIS OPPONENT — it is
  stronger than most; if it upgrades and starts winning/tying seeds (check
  results.json + sim margins), port a 1-ply best-response scorer (black-magic
  style: unit,surround,health,distance) rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, luisa__luisasrobot) [2nd occurrence] — KEEP robot.py UNCHANGED
- Opponent = luisa__luisasrobot (one of the STRONGER opponents; tighter margins).
  Rounds 0 & 1 BOTH scored 250-0 (results.json: opus-4-8 250, luisa 0).
  Round 0 we were Blue, round 1 we were Red.
- Verified round 1: all 250 seed sims = "Red won" (grep uniq count = 250/250).
  Margins tighter than most opponents (we finish ~6-10u vs 2-6u): sim_0 2u/7hp
  vs 6u/20hp? -> WAIT that's health-first format "Health A B Units A B" where
  A=Blue(luisa), B=Red(us). sim_0: Health 7 20, Units 2 6 => us(Red)=6u/20hp vs
  luisa=2u/7hp. sim_123: us 10u/29hp vs 4u/20hp. Clean sweep every seed.
- Sanity checks this session (all well under 60s; runtime ~4.2s):
    robot.py vs simple-bot: WIN 33-1 (default), 34-0 (seed123).
    robot.py vs heuristic-bot: seed1 WIN 12-5, seed42 WIN 15-4, seed79 TIE 10-10.
  robot.py == robot_v2.py (grouping + anti-dive*4 + legal_coord + spawn logic).
  Syntax OK, no regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs luisa__luisasrobot.
  Margins are tighter but every seed is still a win, so any tweak risks regressing
  a perfect result for zero upside. Next teammate: WATCH THIS OPPONENT (stronger
  than most). If luisa upgrades and starts winning/tying seeds (check results.json
  + sim margins), port a 1-ply best-response scorer (black-magic style:
  unit,surround,health,distance) rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, luisa__baselinegere) — CODE CHANGED (isolation grouping)
- Opponent THIS round = luisa__baselinegere (NEW). Round 0 result was NOT a clean
  sweep: opus-4-8 246, Tie 4, luisa 0 (we were RED). 4 TIE seeds: 96, 126, 179, 206.
- CONFIRMED via logic/lib.rs determine_winner_from_units_count: winner = MORE
  UNITS ONLY. Health is IRRELEVANT to win/tie. Ties = equal unit count at turn 100.
  (compare_bots.sh WRONGLY uses health as tiebreak -> overcounts wins. Use the new
   compare_real.sh which applies the REAL rule: units only.)
- The 4 ties all ended with equal units in a scattered stalemate: our units split
  into small isolated groups (e.g. sim_126 had two lone "3" units cut off on the
  left) that couldn't finish the enemy. Root cause = stragglers left behind.
- FIX (adopted in robot.py): added an ISOLATION PENALTY to movement scoring.
  When a unit's own distance to the ally centroid >= 5 (isolated), add group_dist
  to its effective move cost so it prioritizes REJOINING the pack. This keeps
  units concentrated -> win more trades -> finish with a bigger unit margin ->
  fewer ties.
    my_group_dist = abs(my.x-acx)+abs(my.y-acy)
    iso_pen = group_dist if my_group_dist >= 5 else 0
    key = (eff + iso_pen, outnumbered, osc, group_dist, -support, threat)
- TESTING (vs heuristic-bot, the strongest builtin proxy; REAL unit-only rule):
  v3 (this change) gets LARGER unit margins than old bot on 5/6 seeds 1-6
  (e.g. seed3 old +13 -> v3 +17; seed5 old +8 -> v3 +13). Former TIE seed 79
  (11-11) became a WIN (14-11). vs simple-bot 38-3. Runtime ~5s (<<60s).
- REJECTED changes this session (regressed vs heuristic): (a) disabling retreat
  in late game (turn>=85), (b) halving anti-dive penalty late game. Both made us
  over-aggressive and LOST trades vs strong bots -> smaller margins. DO NOT redo.
- Backups: robot_prev_246.py (old 246-score bot), robot_v3.py (== new robot.py).
- Next teammate: if still not 250-0 vs luisa__baselinegere, tune iso threshold
  (>=5) or iso weight. Could also add explicit endgame kill-securing (attack the
  cell an adjacent low-hp enemy will occupy) for the last few turns. Note we do
  NOT have opponent source, so validate via unit-margin vs heuristic + compare_real.sh.

## ROUND 2 SESSION (opus-4-8, luisa__baselinegere) [after isolation fix] — KEEP robot.py UNCHANGED
- Opponent = luisa__baselinegere. Round 0 (OLD bot robot_prev_246.py): opus-4-8
  246, Tie 4 (seeds 96,126,179,206), luisa 0 — scattered-straggler ties.
- Round 1 (NEW bot robot_v3.py w/ ISOLATION grouping penalty): CLEAN 250-0,
  all 250 sims "Blue won" (grep count = 250/250). The iso fix converted the 4
  tie seeds into wins => isolation penalty was the key.
- Verified this session: robot.py == robot_v3.py (syntax OK, functional).
    robot.py vs simple-bot: WIN 34-1, runtime ~4.5s (well under 60s limit).
    robot.py vs heuristic-bot (strong proxy) on the FORMER TIE SEEDS (real
    unit-only rule): seed96 WIN 14-8, seed126 WIN 11-8, seed179 WIN 16-5,
    seed206 WIN 19-6. The iso fix is robust even vs a much stronger bot on
    exactly the seeds that used to tie our opponent.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs luisa__baselinegere
  after the isolation grouping fix. Any tweak risks regressing a perfect result
  for zero upside. Next teammate: only change if luisa upgrades (check
  results.json + sim margins). Remaining robustness gap is vs heuristic/black-magic
  (stronger than our opponent) — would need a 1-ply best-response scorer, high
  risk. Not worth it while we score 250-0.

## ROUND 1 SESSION (opus-4-8, anton__anton4000) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = anton__anton4000 (variant of anton family; one of the
  STRONGER opponents seen). Round 0 = WON 250-0 (results.json: opus-4-8 250,
  anton__anton4000 0). We were BLUE.
- Verified round 0: all 250 seed sims = "Blue won" (grep count = 250/250).
  Margins TIGHTER than most opponents: avg unit margin +10.64 (min +5, max +21);
  opponent survives with avg ~6 units (max 10). e.g. sim_0 16u/45hp vs 5u/22hp;
  sim_42 18u vs 8u; sim_123 10u vs 5u. Still a clean sweep every seed.
- Sanity checks this session (all well under 60s; runtime ~4.0s):
    robot.py vs simple-bot: WIN 31-2.
    robot.py vs heuristic-bot (strong proxy): seed1 WIN 11-7, seed42 WIN 17-8,
      seed79 WIN 12-8, seed123 WIN 12-8. All wins with +4..+9 margins.
- robot.py == robot_v3.py (grouping + anti-dive*4 + legal_coord + spawn logic +
  isolation penalty). Syntax OK, no regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs anton__anton4000.
  Margins are tighter than weaker opponents but every seed is still a clean win,
  so any tweak risks regressing a perfect result for zero upside. Next teammate:
  WATCH THIS OPPONENT (anton__anton4000 is stronger than most). If it upgrades and
  starts winning/tying seeds (check results.json + sim margins), port a 1-ply
  best-response scorer (black-magic style: unit,surround,health,distance) rather
  than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, anton__anton4000) [2nd occurrence] — KEEP robot.py UNCHANGED
- Opponent = anton__anton4000 (one of the STRONGER opponents). Rounds 0 & 1 BOTH
  scored 250-0 (results.json: opus-4-8 250, anton__anton4000 0). Round 0 we were
  Blue, round 1 we were Red.
- Verified round 1: all 250 seed sims = "Red won" (grep count = 250/250). Margins
  are GOOD here (not tight): sim_0 14u-8u, sim_42 15u-5u, sim_79 19u-5u,
  sim_123 14u-3u, sim_201 18u-5u, sim_229 12u-6u (us=Red=B, second number).
- Sanity checks this session (all well under 60s; runtime ~5s):
    robot.py vs simple-bot: WIN 38-2.
    robot.py vs heuristic-bot (strong proxy): seed1 WIN 11-7, seed42 WIN 17-8,
      seed123 WIN 12-8. All comfortable wins.
- robot.py == robot_v3.py (grouping + anti-dive*4 + legal_coord + spawn logic +
  isolation penalty). Syntax OK, no regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs anton__anton4000 with
  strong margins. Any tweak risks regressing a perfect result for zero upside.
  Next teammate: only change if anton__anton4000 upgrades (check results.json + sim
  margins). Remaining robustness gap is vs heuristic/black-magic (stronger than our
  opponent) — would need a 1-ply best-response scorer, high risk. Not worth it
  while we score 250-0.

## ROUND 1 SESSION (opus-4-8, aayyad__testbot) — DECISION: KEEP robot.py UNCHANGED
- Opponent THIS round = aayyad__testbot (NEW opponent). Round 0 = WON 250-0
  (results.json: opus-4-8 250, aayyad__testbot 0). We were BLUE.
- Verified round 0: all 250 seed sims = "Blue won" (grep count = 250/250).
  Margins slightly tighter than weakest opponents (opponent survives 1-3 units),
  e.g. sim_0 12u/29hp vs 2u/5hp; sim_42 10u vs 3u; sim_123 13u vs 1u. Clean sweep.
- Sanity checks this session (all well under 60s; runtime ~4.6s):
    robot.py vs simple-bot: WIN 36-2.
    robot.py vs heuristic-bot: seed1 WIN 11-7, seed42 WIN 17-8. No regression.
- robot.py == robot_v3.py (grouping + anti-dive*4 + legal_coord + spawn logic +
  isolation penalty). Syntax OK, functional.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs aayyad__testbot.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if aayyad__testbot upgrades (check results.json + sim margins). If forced
  to improve robustness vs a stronger bot (heuristic/black-magic style), port a
  1-ply best-response scorer rather than tweaking retreat/dive weights.

## ROUND 2 SESSION (opus-4-8, aayyad__testbot) [2nd occurrence] — KEEP robot.py UNCHANGED
- Opponent = aayyad__testbot. Rounds 0 & 1 BOTH scored 250-0 (results.json:
  opus-4-8 250, aayyad__testbot 0). Round 0 we were Blue, round 1 we were Red.
- Verified round 1: all 250 seed sims = "Red won" (grep count = 250/250). Domination.
- Sanity check this session: robot.py vs simple-bot = WIN 37-2, runtime ~5.1s
  (well under 60s limit). robot.py == robot_v3.py (grouping + anti-dive*4 +
  legal_coord + spawn logic + isolation penalty). Syntax OK, no regression.
- CONCLUSION: No code change. Bot maximizes score (250-0) vs aayyad__testbot.
  Any tweak risks regressing a perfect result for zero upside. Next teammate: only
  change if aayyad__testbot upgrades (check results.json + sim margins). If forced
  to improve robustness vs a stronger bot (heuristic/black-magic style), port a
  1-ply best-response scorer rather than tweaking retreat/dive weights.

## ROUND 1 SESSION (opus-4-8, edward__flail) — CODE CHANGED (anti-dive*5 + iso>=4)
- Opponent THIS round = edward__flail. This is the SAME as builtin-bots/flail.js
  (credit: Edward) — we can TEST DIRECTLY against it! Strongest opponent so far.
- Round 0 (OLD bot, robot_prev_flail.py): opus-4-8 227, edward__flail 22, Tie 1.
  22 LOSSES + 1 tie / 250 seeds (~91%). All losses were CLOSE (e.g. 11-6, 12-8,
  13-11). Our units chase scattered flail units and get picked apart.
- flail.js behavior: minBy nearest enemy. If health<2: flee/attack-if-kill. If
  enemy within dist<3: counts allies in 5x5 around enemy; if <2 allies it FLEES,
  else attacks/approaches. => flail only fights with LOCAL numerical superiority
  and flees otherwise. Beating it needs a TIGHTER pack so we always outnumber
  locally and win trades.
- CHANGE (adopted): robot.py now == robot_v4.py:
    (1) anti-dive penalty raised: outnumbered*4 -> outnumbered*5 (never dive into
        a cell where flail's local group would win the trade).
    (2) isolation threshold lowered: my_group_dist >= 5 -> >= 4 (regroup sooner,
        keep the pack tight so no stragglers get flanked).
- TESTING (RED=robot.py vs BLUE=flail.js, REAL unit-only rule, seeds 1-45):
    BASELINE (old): 37W / 8L  (losses 3,4,13,17,30,34,39,40)
    v4 (adopted):   37W / 6L + 1T (non-wins 13,17,18,27,34,38T,40,43)
  v4 FIXED 4 old losses (3,4,30,39 -> big wins e.g. 16-5, 14-11) and only its
  new losses are razor-thin (12-11, 11-10). Net: fewer non-wins, decisive wins.
- Runtime ~3s per match (well under 60s limit). Syntax verified OK.
- Backups: robot_prev_flail.py (old 227-score bot), robot_v4.py (== new robot.py).
- Next teammate: remaining losses (13,17,18,27,34,40,43) are ALL within 1 unit.
  To close them, consider: (a) endgame kill-securing (predict the cell a fleeing
  low-hp flail unit moves to and attack THAT cell, since flail flees predictably
  away from nearest enemy); (b) even tighter grouping late-game; (c) push flail
  units into map edges/spawn cells before a clear. Test tools: run
  `./rumblebot run term builtin-bots/flail.js robot.py --results-only --seed N`
  (we are RED=2nd number). Sweep helper: /tmp/sweep*.sh pattern (nohup, batches
  of ~10, bash calls time out at 30s so keep batches small).
