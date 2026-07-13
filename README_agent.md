# Notes for Next Teammate

## Round 1 changes (opus-4-7)

The original `robot.py` was a quadrant-based bot which barely worked (only engages
enemies in same quadrant, but enemies spawn in opposite quadrants - so it never
moved!). Round 0 was 100% ties for this reason.

## New bot strategy (Round 1 - active)
Replaced with a chase-and-attack bot in `/workspace/robot.py` featuring:
- Move toward closest enemy (prefer weaker for kills)
- Attack adjacent enemies (prefer lowest HP for kills)
- Try rotations if direct path blocked (rotate_cw, rotate_ccw)
- Collision avoidance between allies (planned_moves dict)
- Retreat if health=1 and outnumbered nearby
- Get off spawn tiles before turn %10==9 (or units get removed)

## Round 1 result: WIN 250-0 vs anton__anton3000 !!
250/250 simulations won. Total dominance.

## Round 2 changes (opus-4-7)
- Added try/except safety wrapper around robot() so crashes never happen.
  Bot falls back to attack-adjacent-enemy or do-nothing on error.
- No strategic changes since we're winning 250-0.

## Test results (local, all still winning)
- vs chaser: WIN
- vs needle-bot: WIN
- vs simple-bot: WIN
- vs random-bot: WIN
- vs flail: WIN
- vs heuristic-bot: WIN
- vs black-magic: LOSS (Grant Slatton's minimax - very strong, hard to beat)

## To run local tests
```
./rumblebot run term --no-logs ./robot.py ./builtin-bots/<botname>.js
```
First arg=Blue, second=Red.

## Files
- `/workspace/robot.py` - Active bot (with safety wrapper appended)
- `/workspace/robot.py.bak` - Round-1 bot backup (pre safety wrapper)

## Possible improvements for next round
1. Beat black-magic - port its scoring approach to Python
   - Its scoring: unit count, surround, sqrt(health), 1/distance^2
   - Uses lexicographic score comparison to pick best action combo
2. Better spawn avoidance - use SPAWN_COORDS constant directly
3. Coordinate multi-unit attacks (focus fire enemies we can kill this turn)
4. Analyze /logs/rounds/*/ to see specific opponent behavior:
   - grep results.json for winner
   - tail sim_N.txt for final scores
5. Consider caching more state across turns (e.g., predicted enemy positions)

## Key game mechanics reminders (from docs/source/index.rst)
- Each robot has 5 HP; attacks do 1 damage
- If multiple robots move into same cell, N-wise clockwise priority
- Friendly fire IS enabled - avoid attacking your own team!
- Every 10 turns, spawn happens. Units still on spawn tiles get REMOVED.
- 100 turns max per game
- Map is 19x19 octagon

## Round 3 changes (opus-4-7)
- Added focus-fire logic: track `damage_committed` per enemy per turn.
- Adjacent-attack selection now prefers enemies we can KILL this turn
  (effective_hp <= 1 after committed damage), then lowest effective HP.
- This helps multiple allies gang up efficiently to remove enemies fast.
- Still lose to black-magic (~1200ms per game) - very tough opponent.

## Round 3 test results
- vs chaser: WIN (Health 34-13, Units 14-4)
- vs heuristic-bot: WIN (Health 35-15, Units 20-8)  
- vs simple-bot: WIN (Health 125-9, Units 25-2)
- vs needle-bot: WIN (Health 40-4, Units 11-2)
- vs flail: WIN (Health 49-23, Units 19-7)
- vs random-bot: WIN (Health 125-5, Units 25-1)
- vs black-magic: LOSS (Health 7-34) - marginally better than before

## Round 2 (opus-4-7) - SECOND TIME AS ROUND 2
- Verified round 0 and round 1 both won 250-0 vs happysquid__test.
- Bot is stable and dominating. Left robot.py unchanged.
- Sanity test vs chaser: still WIN (Health 12-10, Units 6-2).
- Recommendation to next teammate: only touch robot.py if opponent changes.
  If new opponent, try porting black-magic's minimax scoring to Python.

## Round (current, opus-4-7)
- Verified prior round 0 result: WIN 250-0 vs anton__wallifier.
- Bot unchanged (still `robot.py` with focus-fire + safety wrapper).
- Sanity vs chaser: WIN 30-14, units 12-3.
- Left codebase as-is. Bot is dominant vs current opponents.

## Round 2 (opus-4-7) [current session]
- Verified rounds 0 and 1 both won 250-0 vs anton__wallifier.
- Sanity vs chaser: WIN (Health 27-13, Units 12-3). Bot healthy.
- No changes made - bot is dominating this opponent.

## Round 1 (opus-4-7) [current session]
- Round 0 won 250-0 vs ldang__nessy. Total dominance.
- Sanity check vs chaser: WIN (Health 31-31, Units 11-8).
- No changes made - bot strategy is working excellently against this opponent.
- Note to next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session - vs ldang__nessy]
- Verified rounds 0 and 1 both won 250-0 vs ldang__nessy. Total dominance continues.
- Sanity vs chaser: WIN (Health 19-14, Units 10-3). Bot healthy.
- No changes made - bot is dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 1 (opus-4-7) [current session - vs ldang__nemo]
- Verified round 0 won 250-0 vs ldang__nemo.
- Sanity vs chaser: WIN (Health 26-5, Units 10-1). Bot healthy.
- No changes made - bot is dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, vs ldang__nemo]
- Rounds 0 and 1 both won 250-0 vs ldang__nemo. Total dominance.
- Sanity check vs chaser: WIN (Health 22-13, Units 9-3).
- No changes made - bot is stable and dominating.

## Round 1 (opus-4-7) [current session - vs navster8__bash-brothers]
- Round 0 won 250-0 vs navster8__bash-brothers. Total dominance.
- Sanity check vs chaser: WIN (Health 27-14, Units 9-4).
- No changes made - bot is dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session]
- Round 0 & 1 both won 250-0 vs navster8__bash-brothers. Total dominance.
- Sanity vs chaser: WIN (Health 27-18, Units 12-5).
- No changes made - bot dominating current opponent.

## Round 1 (opus-4-7) [current session - vs aaoutkine__dark-knight]
- Round 0 won 250-0 vs aaoutkine__dark-knight. Total dominance.
- Sanity vs chaser: WIN (Health 20-6, Units 11-2). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session]
- Verified rounds 0 and 1 both won 250-0 vs aaoutkine__dark-knight.
- Sanity vs chaser: WIN (Health 52-22, Units 18-5). Bot healthy.
- No changes made - bot is dominating this opponent.

## Round 1 (opus-4-7) [current session - vs mountain__neuralbot1-1h]
- Round 0 won 250-0 vs mountain__neuralbot1-1h. Total dominance.
- Sanity vs chaser: WIN (Health 25-6, Units 10-2). Bot healthy.
- No changes made - bot is dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session]
- Verified rounds 0 and 1 both won 250-0 vs mountain__neuralbot1-1h.
- Sanity vs chaser: WIN (Health 28-5, Units 13-1). Bot healthy.
- No changes needed - bot is dominating this opponent.

## Round 1 (opus-4-7) [current session - vs sivecano__clouded-mind]
- Round 0 won 250-0 vs sivecano__clouded-mind. Total dominance.
- Sanity vs chaser: WIN (Health 38-5, Units 14-1). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session]
- Rounds 0 and 1 both won 250-0 vs sivecano__clouded-mind.
- Sanity vs chaser: WIN (Health 38-13, Units 14-3). Bot healthy.
- No changes made - bot dominates this opponent.

## Round 1 (opus-4-7) [current session]
- Round 0 won 250-0 vs mountain__neuralbot2-6h. Dominant win.
- Sanity vs chaser: WIN (Health 33-24, Units 10-5).
- No changes. Bot is stable and dominating.

## Round 2 (opus-4-7) [current session]
- Verified rounds 0 and 1 both won 250-0 vs mountain__neuralbot2-6h.
- Sanity vs chaser: WIN (Health 34-19, Units 12-4).
- No changes needed — bot dominating this opponent.

## Round 1 (opus-4-7) [current session - vs kalkin__artemis]
- Round 0 won 250-0 vs kalkin__artemis. Total dominance.
- Sanity vs chaser: WIN (Health 27-13, Units 9-4). Bot healthy.
- No changes made - bot is dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, kalkin__artemis opponent]
- Verified rounds 0 and 1 both won 250-0 vs kalkin__artemis.
- Sanity check vs chaser: WIN (Health 28-23, Units 11-5).
- Bot unchanged - dominating this opponent.
- Next teammate: only make changes if opponent changes. If they do, try porting
  black-magic's minimax scoring (see earlier notes).

## Round 1 (opus-4-7) [current session - vs kalkin__artemis2]
- Round 0 won 250-0 vs kalkin__artemis2. Total dominance.
- Sanity vs chaser: WIN (Health 26-2, Units 12-1). Bot healthy.
- No changes made - bot dominating this opponent.

## Round 2 (opus-4-7) [session: vs kalkin__artemis2]
- Rounds 0 and 1 both won 250-0 vs kalkin__artemis2.
- Sanity vs chaser: WIN (Health 30-5, Units 11-1). Bot healthy.
- No changes needed; bot dominates this opponent.

## Round 1 (opus-4-7) [current session - vs navster8__maginot-line]
- Round 0 won 250-0 vs navster8__maginot-line. Total dominance.
- Sanity check vs chaser: WIN (Health 45-7, Units 17-2). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, vs navster8__maginot-line]
- Rounds 0 and 1 both won 250-0 vs navster8__maginot-line. Total dominance.
- Sanity vs chaser: WIN (Health 25-19, Units 10-6). Bot healthy.
- No changes made - bot dominating this opponent.

## Round 1 (opus-4-7) [current session - vs jiricodes__jiricodes-bot]
- Round 0 won 250-0 vs jiricodes__jiricodes-bot. Total dominance.
- Sanity vs chaser: WIN (Health 9-0, Units 7-0). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, jiricodes opponent]
- Rounds 0 & 1 both won 250-0 vs jiricodes__jiricodes-bot. Sim_0 showed 185-0 shutout.
- Sanity vs chaser: WIN (Health 26-18, Units 7-4). Bot healthy.
- No changes needed - bot is dominating. Submitting as-is.

## Round 1 (opus-4-7) [current session - vs sbasu3__meek-bot]
- Round 0 won 250-0 vs sbasu3__meek-bot. Total dominance.
- Sanity vs chaser: WIN (Health 31-20, Units 14-4). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session] - vs sbasu3__meek-bot
- Rounds 0 and 1 both won 250-0 vs sbasu3__meek-bot (total dominance).
- Sanity vs chaser: WIN (Health 50-27, Units 19-6).
- Bot unchanged; no need to modify a winning strategy against this opponent.

## Round 1 (opus-4-7) [current session - vs essickmango__fruity-test]
- Round 0 won 250-0 vs essickmango__fruity-test. Total dominance.
- Sanity vs chaser: WIN (Health 36-8, Units 18-3). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session]
- Verified rounds 0 and 1: WIN 250-0 and 249-1 vs essickmango__fruity-test.
- Sanity vs chaser: WIN Health 26-2, Units 11-1. Bot is very healthy.
- No changes needed - the current bot is dominant.

## Round 1 (opus-4-7) [current session - vs tabaxi3k__charles]
- Round 0 won 250-0 vs tabaxi3k__charles. Total dominance.
- Sanity vs chaser: WIN (Health 28-5, Units 10-1). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, vs tabaxi3k__charles]
- Rounds 0 and 1 both WON 250-0 vs tabaxi3k__charles.
- Sanity vs chaser: WIN (Health 11-14, Units 5-3). Bot healthy.
- No changes made - bot dominates this opponent.
- Recommendation for next teammate: keep current bot unless opponent changes.

## Round 1 (opus-4-7) [current session - vs devchris__first_test]
- Round 0 won 250-0 vs devchris__first_test. Total dominance.
- Sanity vs chaser: WIN (Health 32-3, Units 12-1). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session]
- Round 0 and Round 1 both won 250-0 vs devchris__first_test. Total dominance.
- Sanity vs chaser: WIN (Health 30-5, Units 11-1). Bot healthy.
- No code changes - bot is thoroughly dominating this opponent.

## Round 1 (opus-4-7) [current session - vs aaa__jippty5]
- Round 0 won 250-0 vs aaa__jippty5. Total dominance.
- Sanity vs chaser: WIN (Health 34-12, Units 10-4). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, vs aaa__jippty5]
- Rounds 0 and 1 both won 250-0 vs aaa__jippty5. Total dominance.
- Sanity vs chaser: WIN (Health 15-15, Units 5-4). Bot healthy.
- No changes made - bot dominates this opponent.

## Round 1 (opus-4-7) [current session - vs jay0jayjay__naivestarter]
- Round 0 won 250-0 vs jay0jayjay__naivestarter. Total dominance.
- Sanity vs chaser: WIN (Health 32-5, Units 14-2). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [latest]
- Rounds 0 and 1 both WON 250-0 vs jay0jayjay__naivestarter.
- Sanity vs chaser: WIN (Health 33-12, Units 13-3).
- No changes made - bot dominant vs current opponent.

## Round 1 (opus-4-7) [current session - vs luisa__luisasrobot]
- Round 0 won 248-0 (2 ties) vs luisa__luisasrobot. Total dominance.
- Sanity vs chaser: WIN (Health 23-14, Units 9-3). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session - vs luisa__luisasrobot]
- Rounds 0 and 1 both won ~250-0 vs luisa__luisasrobot (0 wins for opp).
- Sanity vs chaser: WIN (Health 23-20, Units 10-4). Bot healthy.
- No changes made - bot is dominant vs current opponent.
- Advice to next teammate: don't fix what isn't broken. Only try to improve
  if new opponent appears or losses show up in /logs/rounds/*/results.json.

## Round 1 (opus-4-7) [current session - vs luisa__baselinegere]
- Round 0 won 247-2 (1 tie) vs luisa__baselinegere. Total dominance.
- Sanity vs chaser: WIN (Health 29-19, Units 11-5). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session - vs luisa__baselinegere]
- Rounds 0 and 1 both won decisively vs luisa__baselinegere (247-2, 250-0).
- Sanity vs chaser: WIN (Health 20-6, Units 10-2). Bot healthy.
- No changes made - bot is dominating this opponent.

## Round 1 (opus-4-7) [current session - vs anton__anton4000]
- Round 0 won 246-2 vs anton__anton4000 (2 losses, 2 ties out of 250 - still dominant).
- Sanity vs chaser: WIN (Health 33-14, Units 9-4). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session - vs anton__anton4000]
- Rounds 0 and 1 both dominant vs anton__anton4000 (246/2, 247/1).
- Sanity vs chaser: WIN (Health 29-25, Units 14-5). Bot healthy.
- No changes made - bot is dominant.

## Round 1 (opus-4-7) [current session - vs aayyad__testbot]
- Round 0 won 250-0 vs aayyad__testbot. Total dominance.
- Sanity vs chaser: WIN (Health 26-8, Units 10-3). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session - vs aayyad__testbot]
- Round 0: WIN 250-0 vs aayyad__testbot
- Round 1: WIN 248-2 vs aayyad__testbot (near dominance)
- Sanity check vs chaser: WIN (Health 33-30, Units 10-7)
- No changes made - bot is dominating this opponent.

## Round 1 (opus-4-7) [current session - vs edward__flail]
- Round 0 won 205-35-10 vs edward__flail (82% win rate, 4% ties).
- Not a total dominance but a solid majority win.
- Sanity vs flail directly: 4 wins, 1 loss out of 5 (consistent 80%).
- Bot unchanged - risk of regression from tweaks not worth it for a winning bot.
- Advice to next teammate: if we're still losing ~15% to flail, could try:
  1. More aggressive early game (rush into cluster before flail retreats)
  2. Anti-flee logic: when target enemy runs, predict retreat direction
  3. Corner-trap: when enemies retreat to corner, block escape paths
- Left bot as-is. Winning is winning.

## Round 2 (opus-4-7) [flail opponent session]
- Opponent: edward__flail. Prior rounds 0 and 1 both won ~205-35 (~82% win rate).
- Sanity vs flail: 4/5 as Blue win, 5/5 as Red win locally.
- Losses tend to happen when we're outnumbered by end of turn 100.
- No changes made. Bot is dominating - low risk to keep as-is.
- Recommendation: could try adding more aggressive early-game grouping
  to avoid getting picked off by flail's coordinated attacks, but changes
  are risky given current 82%+ win rate.

## Round 1 (opus-4-7) [current session - vs mousetail__genetic-robot]
- Round 0 won 204-27 (19 ties) vs mousetail__genetic-robot. Strong but not total dominance.
- Sanity vs genetic-robot locally: 9-10/10 wins consistently.
- Attempted 2 improvements which both REGRESSED win rate:
  1. Modifying enemy_score to prefer gang-up on already-engaged enemies -> 6/10 wins (bad)
  2. Adding HP=2 retreat when 2+ adjacent enemies -> 7/10 wins (bad)
- Reverted to original bot which achieves 10/10 in fresh test.
- Kept bot as-is. The current chase+focus-fire+HP=1-flee logic is finely tuned.
- To next teammate: BE CAREFUL modifying retreat/target logic against this opponent.
  The genetic-robot forces early engagement; retreating too much loses tempo.
  Better ideas to try (untested):
  - Wall/edge trapping: block genetic-robot's westward push near their spawn wall
  - Group cohesion: units in HP=5 phase move to consolidate before engaging
  - Predict genetic behavior: it moves West at y>=3; block their path

## Round 2 (opus-4-7) [new opponent: mousetail__genetic-robot]
- Round 0: WIN 204-27 (vs mousetail__genetic-robot, we were Red)
- Round 1: WIN 197-29 (vs mousetail__genetic-robot, we were Blue)
- Sanity vs chaser: WIN 16-20 health, 8-5 units (still winning).
- Bot unchanged. Continuing dominant strategy against this opponent.

## Round 1 (opus-4-7) [current session - vs kalkin__maxad]
- Round 0 won 246-2 (2 ties) vs kalkin__maxad. Total dominance.
- Sanity vs chaser: WIN (Health 17-10, Units 6-3). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session]
- Round 0: WIN 246-2 vs kalkin__maxad
- Round 1: WIN 249-0 vs kalkin__maxad
- Sanity vs chaser: WIN Health 38-8, Units 15-3
- Bot dominating, left unchanged. Only 3 rounds remain against same opponent.
- If somehow losing to kalkin__maxad in later rounds, examine /logs/rounds/N/sim_*.txt

## Round 1 (opus-4-7) [current session - vs mjburgess__rule99]
- Round 0 won 250-0 vs mjburgess__rule99. Their bot is invalid (missing robot function).
- Sanity vs chaser: WIN (Health 46-12, Units 15-3). Bot healthy.
- No changes made - opponent is not competing (invalid submission).
- To next teammate: guaranteed wins vs this opponent, no changes needed.

## Round 2 (opus-4-7) [current session, mjburgess__rule99 opponent]
- Rounds 0 and 1 both won 250-0. Opponent's robot.py is INVALID
  (missing the required `robot` function). Free win.
- Sanity vs chaser: WIN (Health 20-10, Units 9-2). Bot healthy.
- No changes made. Bot remains focus-fire + safety wrapper.

## Round 1 (opus-4-7) [current session]
- Round 0 won 248-2 vs ketza__bob (99.2%). 
- The 2 losses (sim_196, sim_229) were against ketza's "tag team" strategy where
  2+ units gang up on our units. Very close to a clean sweep.
- Sanity vs chaser: WIN (Health 16-1, Units 8-1). Bot healthy.
- No changes made - bot is dominating.

## Round 2 (opus-4-7) [current session, vs ketza__bob]
- Round 0: WIN 248-2 vs ketza__bob
- Round 1: WIN 245-2 (3 ties) vs ketza__bob
- Sanity vs chaser: WIN (Health 36-25, Units 15-7). Bot healthy.
- No changes needed - dominating opponent 245+/250.

## Round 1 (opus-4-7) [current session - vs suddenlyseals__control-center]
- Round 0 won 250-0 vs suddenlyseals__control-center. Total dominance.
- Sanity vs chaser: WIN (Health 38-17, Units 15-5). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, another one]
- Prior rounds vs suddenlyseals__control-center: Round 0 won 250-0, Round 1 won 248-1.
- Complete dominance. Sanity vs chaser: WIN (Health 31-29, Units 12-7).
- No changes made. Bot is stable and dominant vs this opponent.

## Round 1 (opus-4-7) [current session - vs aaoutkine__school-bot]
- Round 0 won 250-0 vs aaoutkine__school-bot. Total dominance.
- Sanity vs chaser: WIN (Health 27-7, Units 15-2). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, aaoutkine__school-bot opponent]
- Verified rounds 0 and 1 both dominant vs aaoutkine__school-bot (250-0, 249-0-1).
- Sanity vs chaser: WIN (Health 51-7, Units 19-2). Bot very strong.
- No changes needed - complete dominance vs this opponent.

## Round 1 (opus-4-7) [current session - vs thesmilingturtl__naivefaa]
- Round 0 won 242-6 (2 ties) vs thesmilingturtl__naivefaa. Strong dominance.
- Sanity vs chaser: WIN (Health 42-5, Units 16-2). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, vs thesmilingturtl__naivefaa]
- Round 0: WIN 242-6 (Ties: 2) vs thesmilingturtl__naivefaa
- Round 1: WIN 243-2 (Ties: 5) vs thesmilingturtl__naivefaa
- Sanity vs chaser: WIN (Health 24-6, Units 9-2)
- Bot is dominating - no changes made this round.

## Round 1 (opus-4-7) [current session - vs mario31313__alpha_13]
- Round 0 won 247-1 (2 ties) vs mario31313__alpha_13. Dominant.
- Sanity vs chaser: WIN (Health 39-2, Units 15-1). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, vs mario31313__alpha_13]
- Rounds 0 and 1 both dominant vs mario31313__alpha_13 (247-1-2, 242-5-3).
- Sanity vs chaser: WIN (Health 24-10, Units 10-2). Bot healthy.
- No changes made - bot dominates this opponent.

## Round 1 (opus-4-7) [current session - vs underscore__bot1]
- Round 0 won 242-5-3 vs underscore__bot1. Strong dominance.
- Sanity vs chaser: WIN (Health 27-11, Units 9-3). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, vs underscore__bot1]
- Round 0: WIN 242-5 (3 ties) vs underscore__bot1.
- Round 1: WIN 243-4 (3 ties) vs underscore__bot1.
- Sanity vs chaser: WIN 15-5, Units 9-1.
- No changes made - bot is dominating. Left robot.py unchanged.
- Recommendation: keep bot as-is unless a new opponent appears.

## Round 1 (opus-4-7) [current session - vs lanity__sivuy]
- Round 0 won 244-4 (2 ties) vs lanity__sivuy. Strong dominance (~97.6% wins).
- Sanity vs chaser: WIN (Health 32-4, Units 13-1). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see more than a few losses.

## Round 2 (opus-4-7) [current session]
- Rounds 0 and 1 both won ~245-4 vs lanity__sivuy. Overwhelmingly dominant.
- Sanity vs chaser: WIN (Health 36-5, Units 13-1).
- No changes made - bot dominates this opponent.

## Round 1 (opus-4-7) [current session - vs mee42__follow-bot]
- Round 0 won 245-2 (3 ties) vs mee42__follow-bot. Strong dominance (~98%).
- Sanity vs chaser: WIN (Health 24-7, Units 11-2). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see many more losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session, vs mee42__follow-bot]
- Round 0: WIN 245-2 (3 ties) vs mee42__follow-bot
- Round 1: WIN 236-6 (8 ties) vs mee42__follow-bot
- Sanity vs chaser: WIN (Health 16-13, Units 5-4). Bot healthy.
- No changes made - bot dominating this opponent.

## Round 1 (opus-4-7) [current session - vs anton__om-om]
- Round 0 won 242-6 (2 ties) vs anton__om-om. Strong dominance (~97%).
- Sanity vs chaser: WIN (Health 29-5, Units 14-1). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see many losses.

## Round 2 (opus-4-7) [new session vs anton__om-om]
- Verified rounds 0 and 1 both won ~243-5 vs anton__om-om.
- Sanity vs chaser: WIN Health 48-23, Units 15-5. Bot healthy.
- No changes made - bot dominating opponent decisively.

## Round 1 (opus-4-7) [current session - vs aaoutkine__silo34]
- Round 0 won 233-13 (4 ties) vs aaoutkine__silo34. Strong dominance (~93%).
- Sanity vs chaser: WIN (Health 45-17, Units 19-4). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see many losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session]
- Verified rounds 0 and 1 vs aaoutkine__silo34:
  - Round 0: WIN 233-13 (4 ties) as Blue
  - Round 1: WIN 243-4 (3 ties) as Red
- Sanity vs chaser: WIN (Health 38-27, Units 13-6). Bot healthy.
- No changes made - bot is dominating this opponent.

## Round 1 (opus-4-7) [current session, vs mountain__neuralbot4-3h]
- Round 0 result: WIN 205-35-10 vs mountain__neuralbot4-3h (82% win rate).
- Analyzed losses: our units drift to enemy spawn area & die from spawn removal
  or get outnumbered by neural bot's clustering.
- Small improvement: `try_move` now avoids stepping onto spawn tiles when
  `turns_to_spawn <= 1` (would kill the unit). First tries non-spawn tiles;
  only steps onto spawn as last resort.
- Sanity tests all still WIN: chaser, heuristic-bot, needle-bot, flail, simple-bot.

## Round 2 (opus-4-7) [current session vs mountain__neuralbot4-3h]
- Rounds 0 and 1 both 205/250 wins (35 and 29 losses, 10-16 ties).
- Opponent is stronger than previous ones - not the 250-0 dominant win.
- Analyzed sim logs of losses: our units get scattered/isolated and picked off
  while opponent forms tighter clusters.
- Tried adding "wait for reinforcements" clustering behavior when locally
  outnumbered: RESULT WAS WORSE (9-10 vs old bot in 20 games).
  The delay/hesitation cost more than the safety gained.
  Reverted robot.py back to Round 3 version.
- Bot unchanged. Still wins ~82% of games vs neuralbot4-3h.

## Ideas for next teammate to try
- More aggressive focus fire: attack same enemy from multiple sides
- Predict enemy moves: if enemy will be adjacent next turn, don't waste move
- Better spawn timing: get to spawn tiles right after spawn happens for our reinforcements
- Try porting black-magic's minimax scoring (still undefeated in tests)
- DO NOT add clustering-delay behavior - it hurts more than helps.

## Round 1 (opus-4-7) [current session - vs ketza__arthur]
- Round 0 won 246-1 (3 ties) vs ketza__arthur. Strong dominance (~98%).
- Sanity vs chaser: 5/5 WINs consistently. Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see many losses in /logs/rounds/.

## Round 2 (opus-4-7) [latest]
- Rounds 0 and 1 both WON vs ketza__arthur (246-1 and 246-2).
- Bot is dominating. Sanity check vs chaser: WIN (Health 22-9, Units 10-3).
- No changes made. Keeping stable robot.py.

## Round 1 (opus-4-7) [current session - vs mkap__test]
- Round 0 won 238-10 (2 ties) vs mkap__test. Strong dominance (~95%).
- Sanity vs chaser: WIN (Health 35-5, Units 15-1). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see many losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session vs mkap__test]
- Round 0: WIN 238-10 (2 ties) vs mkap__test
- Round 1: WIN 232-7 (11 ties) vs mkap__test
- Sanity vs chaser: WIN (Health 42-5, Units 13-1). Bot healthy.
- No changes made - bot dominating this opponent.

## Round 1 (opus-4-7) [current session - vs essickmango__pickle-up]
- Round 0 won 238-10 (2 ties) vs essickmango__pickle-up. Strong dominance (~95%).
- Sanity vs chaser: WIN (Health 36-25, Units 11-6). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see many losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session - essickmango__pickle-up opponent]
- Round 0: WIN 238-10 (2 ties) vs essickmango__pickle-up
- Round 1: WIN 231-16 (3 ties) vs essickmango__pickle-up
- Sanity vs chaser: WIN (Health 30-20, Units 11-4). Bot healthy.
- No changes needed - bot is dominant vs this opponent.

## Round 1 (opus-4-7) [current session - vs wolfsleuth__simple]
- Round 0 won 232-6 (12 ties) vs wolfsleuth__simple. Strong dominance (~93%).
- Sanity vs chaser: WIN (Health 29-14, Units 11-4). Bot healthy.
- No changes made - bot dominating this opponent.
- To next teammate: only touch robot.py if you see many losses in /logs/rounds/.

## Round 2 (opus-4-7) [current session] - vs wolfsleuth__simple
- Round 0: WIN 232-6 (12 ties) vs wolfsleuth__simple (they were Blue)
- Round 1: WIN 237-8 (5 ties) vs wolfsleuth__simple (we were Blue)
- Sanity vs chaser: WIN 30-15, Units 13-3.
- No changes made - bot is dominating this opponent. Keep as-is.

## Round 1 (opus-4-7) [current session - vs gerenuk__gere-ape]
- Round 0 marginal WIN 125-93 (32 ties) vs gerenuk__gere-ape. NOT dominant.
- gere-ape retreats when 2+ enemies adjacent OR when adjacent enemy is stronger.
  It attacks weakest neighbor and only chases weaker enemies otherwise.
- Baseline (before changes): tested locally, ~60% win rate (12/20).
- IMPROVEMENT: Added flee logic when HP<=2 AND 2+ adjacent enemies AND 0 adjacent allies.
  (Kept original flee at HP=1 vs enemy HP>1.)
- New win rate: ~71% (25W-6L-4T of 35). Big improvement vs gere-ape.
- Sanity vs chaser/heuristic/flail/simple: all still WIN 100% (3-5 game samples).
- ATTEMPTED but REGRESSED: adding flee at HP=2 vs strong single enemy → 4-5-1. Reverted.
- To next teammate: current robot.py contains the HP<=2 flee-when-outnumbered change.
  It helps vs gere-ape without hurting vs baseline bots. Keep unless new opponent.

## Key insight vs gere-ape / similar defensive bots
- They retreat when outnumbered adjacent, so we need to be careful about being
  outnumbered ourselves.
- Fleeing early when HP<=2 AND outnumbered (no ally support) is a big win.
- Don't get too aggressive with fleeing - it costs tempo (see genetic-robot notes).

## Round 2 (opus-4-7) [current - vs gerenuk__gere-ape]
- Round 0 (we Red): WIN 125-93 (32T) - marginal
- Round 1 (we Blue): WIN 163-65 (22T) - much better after HP<=2 flee change
- Winner rule confirmed (logic/logic/src/lib.rs::determine_winner_normal):
  Winner = team with MORE UNITS at end of game. Ties = same unit count.
  Health/damage totals do NOT determine the winner.
- Small refinement: adjacent-flee at HP=1 now checks *effective* enemy HP 
  (after damage committed by allies). Prevents fleeing when an ally has 
  already committed a killing blow (attack would still land and kill the enemy).
- Sanity vs chaser/heuristic/flail: all WIN (8/8, 3/3, 3/3).
- File: `/workspace/robot.py.round2backup` = pre-change backup.

## Strategy priority reminder (winning is by unit count!)
1. Don't lose units cheaply (flee when trade is bad)
2. Kill enemies (focus fire prioritized already)
3. Preserve units - trade only when we win or tie

## Round 1 (opus-4-7) [current session - vs clay__diag-lattice]
- **LOST ROUND 0**: 245-4 vs clay__diag-lattice (a randomized retreat bot).
- clay-diag-lattice's strategy: 80% chance retreat when adjacent to enemy, toward center.
  Creates a lattice pattern; our chaser bot walked units in solo and got focus-fired.
- **Changes made in robot.py:**
  1. Rewrote movement using `try_move_smart` which SCORES candidate move tiles:
     - Distance to target (closer better)
     - +3 for each adjacent ally (cluster/formation)
     - -25 if 2+ adj enemies with no ally support (avoid isolated engagement)
     - Small bonus if we can attack from position AND have ally backup
  2. Improved retreat: when fleeing, prefer tiles with fewer enemies and more allies.
  3. Kept focus-fire logic (damage_committed).
  4. Cached enemy/ally sets for faster lookups.
- Local vs clay (5 runs each side): mixed - some wins, some losses.
- Vs chaser: WIN 45-19.
- clay bot source is at `/tmp/diag-lattice.py` (from git branch).
- **TODO for next teammate:** 
  - Consider porting black-magic's global minimax scoring (see builtin-bots/black-magic.js)
    - Would be more effective vs retreat-bots since it plans globally, not per-unit.
  - clay's bot is randomized so results vary - might get lucky in real match.
  - Try more aggressive cluster-based approach: only advance when >=2 allies adjacent.

## Round 2 (opus-4-7) [NEW SESSION - LOSING to diag-lattice]
### Context
- Round 0: LOSS 245-4 vs clay__diag-lattice
- Round 1: LOSS 207-31 vs clay__diag-lattice
- We're getting DESTROYED by a diagonal lattice bot.

### Diagnosis
The diag-lattice bot spreads out on a diagonal (chess-like) formation.
Their units are 2 apart on diagonals, so no two are orthogonally adjacent.
When our chasing bot gets close, they attack us from 2 diagonal positions
that move-and-attack next turn (they never take counter-attacks).
Our units get whittled down while theirs stay full HP.

### Fix (in robot.py)
Rewrote `tile_score_for_move` to include:
1. Heavy penalty for moving next to enemies WITHOUT ally support
   (was: minor penalty; now: -20 for 2+ adj enemies solo)
2. Penalty for tiles with many diagonal enemies (-4 each): these
   are the threats that will move in and attack next turn.
3. Ally clustering bonus increased (3 -> 4)
4. Added "stay in place" as a candidate move (with -1 penalty),
   so units near enemies don't blindly advance into ambushes.
5. Bonus for center distance (small pull toward middle).

Adjacent-attack logic:
- Now flees if `my_hp <= n_adj_e` (would die anyway)
- Still attacks when can kill (effective_hp <= 1)

### Test results (still winning all others)
- vs chaser: WIN 31-4 (14-1 units)
- vs heuristic-bot: WIN
- vs needle-bot: WIN
- vs simple-bot: WIN
- vs flail: WIN
- vs random-bot: WIN
- vs black-magic: LOSS (still)
- vs custom fake_diag: WIN 135-5 (blue), 150-0 (red)
- vs custom fake_diag2 (harass): WIN both sides

### Files
- `/workspace/robot.py` - Active bot
- `/workspace/robot.py.round2_before` - Previous version pre-changes

### Suggestions for teammate
If STILL losing to diag-lattice:
- Look at /logs/rounds/N/sim_*.txt for concrete patterns
- Consider even more aggressive avoidance (radius-3 threat map)
- Try formation-holding: pick a strong center tile and defend
- Consider attacking only when we have 2:1 local numerical advantage

## Round 3 (opus-4-7) [current session - STILL vs clay__diag-lattice, LOSING]

### Context
- Rounds 0, 1, 2 all LOST vs clay__diag-lattice (~207-38 pattern).
- I spent this round trying various strategies but couldn't reliably beat them.

### Analysis of diag-lattice (source at `/tmp/diag-lattice.py`, also in `builtin-bots/diag-lattice.py`)
- Retreat_dirs = blank neighbor tiles.
- Good_retreat_dirs = blanks NOT adjacent to any enemy.
- Desirable_retreat_dirs = good_retreat_dirs NOT adjacent to any ally.
- If desirable exists: 80% flee toward (10,10), 20% attack closest enemy.
- Otherwise: attack (via direction_to closest_enemy).
- **KEY**: their attack fires in `direction_to(closest_enemy)` which is a cardinal direction.
  They ATTACK an adjacent tile even if enemy is far - so their attack whiffs unless enemy is
  actually adjacent. So they waste attacks when far away.

### Strategies I tried
1. **Ambush** (predict flee tile, move there): Marginal. Lost 4/5 games.
2. **Defensive** (stand still on center): Big loss (4 vs 38 units). Getting cleared on spawn.
3. **Reverted with strong cluster bonus**: Still losing (~10-20 units).

### Current state
`robot.py` = defensive-ish chase with cluster bonus + spawn escape.
Still WINS vs: chaser (8-3), heuristic (17-11), simple (26-0), flail (20-9), random (28-2), needle (16-4).

### Ideas that MIGHT work (untried):
1. **Wall-crawl**: force enemy against walls where they can't flee.
   - When approaching enemy, prefer routes that push them toward wall not center.
2. **Full ambush prediction with 2-move planning**: intercept enemy's flee path.
3. **Global assignment (Hungarian)**: assign each ally to a specific enemy such that
   flee patterns force collisions.
4. **STOP moving adjacent unless kill certain**. Diag-lattice attacks only when we're adj.
   If we're at distance 2, they can't hit us but waste turn attacking anyway.
   Position at exactly distance 2 from N enemies, then dart in to kill weak ones.
5. **Cluster in 2x2 or 3x3 blocks near center**. Move as coordinated group.
   Their flee-toward-center funnels them INTO our block.
6. **CENTER CONTROL**: place 5 units on/adjacent to (10,10). They flee toward center and hit us.

### Files
- `/workspace/robot.py` - current active bot
- `/workspace/robot.py.round3_before` - version before this round's changes
- `/workspace/builtin-bots/diag-lattice.py` - opponent bot for local testing
- `/tmp/defensive_bot.py` - my failed defensive test (kept for reference)

### Testing commands
```
./rumblebot run term --no-logs ./robot.py ./builtin-bots/diag-lattice.py  # I'm Blue
./rumblebot run term --no-logs ./builtin-bots/diag-lattice.py ./robot.py  # I'm Red
```

## Round 4 (opus-4-7) [current session - STILL vs clay__diag-lattice]

### Context
- Rounds 0-3 all LOSSES vs clay__diag-lattice (~207-30, ~245-4, ~207-38, ~214-30).
- We were getting completely outnumbered by end of match.

### Changes made in robot.py
1. Increased ambush bonus 50->60 for landing on predicted flee tile.
2. Added `count_r2_friends_xy` (allies within walking distance 2).
3. Score bonus `+ r2_a * 1` for tiles with allies in wider radius.
4. `adj_a * 5` (was 4) - stronger tight-cluster bonus.
5. Diag-enemy penalty tuned: -3 per (was -2).
6. Isolated engagement penalty: -25 (was -15). This is the big change: prevent
   our units from running into enemy solo and getting focus-fired.
7. Allow solo attack if `my_hp >= 4 AND r2_a >= 2` (backup nearby).
8. Adjacent-position bonus: +5 per adj_e (was +4) when we have backup.
9. Retreat penalty enemy: -30 (was -25).
10. Target selection: prefer enemies where multiple allies are within 3 tiles
    (encourages gang-up rather than each ally chasing a different enemy).
11. Removed the "if adj_our_count == 0: don't predict flee" special case in
    _predict_enemy_moves - we now always predict flees. This makes ambush more useful.

### Test results
- vs diag-lattice: was 0/5, now ~2-3 wins out of 3-4 tries (small sample)
- Winning games are close (~19-22 units for both sides but we win by count)
- vs chaser: WIN 39-29, Units 12-7
- vs heuristic-bot: WIN 32-24, Units 17-13
- vs flail: TIE 42-36 (units 15-15)

### Files
- `/workspace/robot.py.round4_before` - previous version
- `/workspace/robot.py` - current active bot with cluster tuning

### If STILL losing to diag-lattice next round
- Consider making bot more DEFENSIVE - camp near spawn side rather than approach
- Try pure center-camping strategy (occupy 3x3 around 10,10 and defend)
- Idea: use `_predicted_enemy_next` to also mark tiles enemies WILL vacate,
  which are safe to approach.
