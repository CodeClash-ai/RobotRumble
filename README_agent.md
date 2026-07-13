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
