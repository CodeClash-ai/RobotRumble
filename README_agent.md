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
