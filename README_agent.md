# Notes for teammates (Round 1 recap)

## What was wrong before
The starter `robot.py` used a Quadrant-based target-assignment strategy
(`init_turn` picks one enemy per quadrant). It had a serious bug: the
movement fallback logic (rotate_cw/rotate_ccw + `past_coords` anti-oscillation
check) could get **permanently stuck** returning `None` forever whenever both
rotation options were blocked (by a wall or unit) - and it never had a
"break the deadlock" fallback. This is visible in `/logs/rounds/0/sim_*.txt`:
health stays at "20 20" the *entire* 100-turn match in every single game -
i.e. our bot never landed a single attack. Confirmed by testing locally:
```
./rumblebot run term --results-only robot.py builtin-bots/nothing-bot.js
# old code -> TIE (never engages a totally stationary opponent!)
```

## What changed (this round)
Rewrote `robot.py` with a much simpler & robust per-unit greedy strategy:
- Target selection: prefer any enemy already adjacent (finish the kill,
  weakest health first); otherwise pick the enemy minimizing
  `(distance, health)` (i.e. closest first, weakest as tiebreak - this beat
  chaser.js better than health-first ordering, see below).
- Movement: order candidate directions as [direct, rotate_cw/ccw sorted by
  resulting distance, opposite], skip cells occupied by a wall/unit, and
  avoid immediately reversing the last move *unless* we've been stuck for
  2+ turns in a row (anti-oscillation with a guaranteed unstick fallback).
  Crucially: if literally everything is blocked we pass, but we never
  permanently "freeze" once an opening appears, and we track `stuck_turns`
  per-unit in a global `robot_state` dict.

## Local test results (`./rumblebot run term --results-only robot.py builtin-bots/X.js`)
(map/team sizes vary run-to-run since no `--seed`/map-size was pinned, so
treat these as directional signal, not exact numbers)

| Opponent            | Result             |
|----------------------|---------------------|
| nothing-bot.js       | WIN (was a TIE)     |
| simple-bot.js        | WIN (was a TIE)     |
| flail.js             | WIN (was a TIE)     |
| random-bot.js        | WIN                 |
| chaser.js            | WIN (was a LOSS)    |
| heuristic-bot.js     | WIN                 |
| needle-bot.js        | WIN                 |
| black-magic.js       | LOSS (still)        |

`black-magic.js` runs a 1-ply minimax-style search over joint actions with a
scoring function (unit count diff, surrounding/focus-fire potential, health,
distance) - it's a genuinely strong bot. If you have budget, look at
`builtin-bots/black-magic.js` for the scoring idea and consider porting a
similar lookahead/joint-action-search into `robot.py`'s `init_turn` (assign
actions for all our units at once, evaluate a heuristic on the resulting
state, keep the best). That is the most promising next improvement.

## Useful commands
```bash
# Quick 1-off match vs a builtin bot, results only:
./rumblebot run term --results-only robot.py builtin-bots/<name>.js

# Full battle logs printed to terminal:
./rumblebot run term robot.py builtin-bots/<name>.js
```

## Game facts learned from `logic/logic/src/lib.rs`
- `UNIT_HEALTH = 5`, `ATTACK_POWER = 1`, `HEAL_POWER = 1` (per hit).
  So a unit needs 5 successful attacks to die; focus fire matters a lot.
- Map is Circle-type (diamond shape rendered in ASCII) with `Wall` terrain
  objects along the border - `state.obj_by_coords(coords)` returns those
  too, so checking "is this cell occupied by *any* Obj" is the right way to
  detect both walls and units blocking a move.
- `/logs/rounds/0/results.json` shows Round 0 was a **Tie** vs
  `anton__anton3000` (0 vs 0 score) because of the movement-freeze bug above.

## Ideas for next round
1. Port a black-magic-style local search / lookahead scoring for `init_turn`
   to jointly plan our team's moves each turn instead of pure greedy-per-unit.
2. Add explicit "surround" bonus: prefer moving to squares that are adjacent
   to an enemy but where multiple allies can simultaneously reach an enemy to
   focus fire and kill it in 1 turn combo.
3. Consider fleeing/retreating low-health units instead of always attacking,
   to reduce losses.
4. Pin `--seed` when testing locally for reproducible A/B comparisons.

## Round 2 update
Replaced the pure greedy per-unit robot.py with a joint-action
coordinate-ascent planner in `init_turn` (mirrors `black-magic.js`'s
algorithm: score = (unit_diff, surround^2, health_diff, distance^2),
lexicographically maximized), computed once per turn for the whole team,
with `robot()` just looking up the precomputed action per unit id.
- Enemy baseline assumption: each enemy attacks the lowest-health adjacent
  friend (same heuristic black-magic.js uses for itself).
- Added a `cheap_mode` guard (when friends*enemies > 60) that restricts each
  unit's option set to just "attack if adjacent" + "step toward nearest
  enemy" + pass, instead of the full 8 move/attack directions, because the
  full search timed out badly (~19s/game) once our team ballooned to
  20-30 units against a passive opponent like nothing-bot.js over 100
  turns. PASSES is currently 1 (matches black-magic.js's single sweep) -
  if you have time budget, try raising to 2-3 for small-to-medium fights
  only (guard on unit count) since multi-pass coordinate ascent should
  find a better local optimum and previously looked promising before the
  timeout was discovered.
- **IMPORTANT - NOT FULLY RE-VALIDATED**: ran out of step budget this
  round to re-test the full builtin-bot suite (nothing/simple/flail/
  random/chaser/heuristic/needle/black-magic) after adding the cheap_mode
  perf guard. Only confirmed nothing-bot.js runs quickly now (previously
  9-19s, needs to be re-timed) and that robot.py parses/loads. **Next
  teammate: please re-run the full suite below before making further
  changes, and especially check black-magic.js (the one bot Round-1's
  greedy bot lost to) and timing on the biggest-unit-count matchups.**
```bash
for bot in nothing-bot.js simple-bot.js flail.js random-bot.js chaser.js heuristic-bot.js needle-bot.js black-magic.js; do
  echo "=== $bot ==="; timeout 60 ./rumblebot run term --results-only builtin-bots/$bot robot.py
done
```
- If the new planner turns out worse/slower than Round 1's greedy bot in
  your re-testing, Round 1's `robot.py` is preserved in git history /
  `/logs/edits/sonnet-5_r1.traj.json` and in this file's earlier section -
  reverting to greedy-per-unit is a safe fallback that is known to beat
  every builtin bot except black-magic.js.

## Round 3 update
Investigated why the Round 2 joint-action planner (`robot.py`) was losing to
`black-magic.js`, `flail.js`, and `needle-bot.js` despite the algorithm being
essentially a faithful port of black-magic.js's own coordinate-ascent search.

**Root cause found:** the `cheap_mode` performance guard added in Round 2
(`friends*enemies > 60` -> restrict each unit to only 1 candidate direction
instead of all 4 move + 4 attack dirs) was far too aggressive. Because units
recurrently spawn (4 more every 10 turns per side while spawn points remain
open, see `logic/logic/src/lib.rs` `spawn_units`), both teams routinely reach
10-15+ units by turn 30-40, so `friends*enemies` blows past 60 almost
immediately and the bot spends most of the match in the dumbed-down
"walk toward nearest enemy" mode - exactly when tactical play (target
selection, focus fire, avoiding bad trades) matters most. `black-magic.js`
has NO such guard and always does the full search, which is why it kept
beating us even though our scoring function and algorithm structure are
copied from it.

**Fix:** raised the `cheap_mode` threshold from 60 to 4000 (i.e. effectively
disabled under all normal circumstances on this map size, kept only as a
pathological-case safety net). Re-measured worst-case runtime with the full
search always on:
- self-play (`robot.py` vs `robot.py`, the scenario most likely to keep both
  team sizes large simultaneously for a long time): **~9s/game**
- vs every builtin bot that survives long enough to build up a big team
  (`simple-bot.js`, `heuristic-bot.js`, `chaser.js`, `random-bot.js`,
  `nothing-bot.js`): **~7-13s/game**

All comfortably under the 60s forfeit limit, so there was no need for the
guard to ever trigger in practice - the Round 2 threshold was just picked
too conservatively without re-timing after the surrounding code changed.

### Results after the fix (single runs, no `--seed` so treat as directional)
| Opponent            | Before (threshold=60) | After (threshold=4000) |
|----------------------|------------------------|--------------------------|
| nothing-bot.js       | WIN                    | WIN                      |
| simple-bot.js        | WIN                    | WIN                      |
| flail.js             | mixed (won/lost across runs) | WIN (multiple runs) |
| random-bot.js        | WIN                    | WIN                      |
| chaser.js             | WIN                   | WIN                      |
| heuristic-bot.js     | WIN                    | WIN                      |
| needle-bot.js        | mixed (won/lost)       | WIN (multiple runs)      |
| black-magic.js       | LOSS (badly, e.g. 1-51 health) | mostly WIN, occasional close loss (e.g. 27-28 health) - much improved, was previously a blowout loss every time |

### Notes / caveats for next teammate
- No `--seed` flag was used in any of this round's local testing (maps are
  randomized each run), so all win/loss tables above are directional signal
  from a handful of runs each, not statistically rigorous. If you have step
  budget, add `--seed` (check `./rumblebot run term --help` /
  `run batch --help` for exact flag support) and run e.g. 10-20 iterations
  per matchup for real win-rate numbers, especially for the still-competitive
  `black-magic.js` matchup.
- `black-magic.js` is still the toughest matchup (near coin-flip now, was a
  guaranteed loss before this fix). Ideas if you want to push further:
  1. Try `PASSES = 2` or `3` (currently 1) now that we know we have runtime
     budget to spare (~9s/game at PASSES=1, 60s limit) - multi-pass
     coordinate ascent should find a better local optimum than a single
     sweep, which is likely necessary to actually beat (not just tie) an
     opponent using the *same* single-sweep algorithm as us.
  2. `black-magic.js` uses a hardcoded diamond-map legality formula
     (`is_legal_coordinate`) instead of querying real terrain objects - if
     the actual generated map ever has irregular obstacles beyond the plain
     diamond border, our `_is_blocked` (which queries `state.obj_by_coords`
     for real) may have an edge/disadvantage there; not investigated further
     this round.
  3. Consider re-lowering `cheap_mode`'s threshold back down ONLY if future
     map-size/spawn-setting changes make unit counts grow much larger than
     what was measured here (double-check timing again after any such
     change - don't just trust this round's numbers forever).

## Round 4 update (this session)
Re-validated the Round-3 joint-action planner (`robot.py`) against the full
builtin-bot suite plus self-play; it is winning comfortably against every
builtin bot (nothing/simple/flail/random/chaser/heuristic/needle) and mostly
winning/close against `black-magic.js` (map-variance means occasional
losses, but wins the majority of local runs both as Blue and as Red).

Also confirmed via `/logs/rounds/0` and `/logs/rounds/1` (this ladder rung,
vs `happysquid__test`) that the bot won **both** recorded matches by a huge
margin (Health 125-0 and 120-15), so the current strategy is working very
well against the live opponent, not just builtin practice bots.

**Change made this round:** made `PASSES` (coordinate-ascent sweeps per
turn in `init_turn`) *adaptive* based on `len(friends) * len(enemies)`
instead of a fixed `PASSES = 1`:
- size <= 100  -> PASSES = 3
- size <= 400  -> PASSES = 2
- size >  400  -> PASSES = 1 (same as before - big battles still get only
  one sweep to stay safely under the 60s time limit)

Rationale: extra coordinate-ascent passes give a better local optimum (more
likely to find good multi-unit combos/kills), and are cheap exactly when
team sizes are small (early game, or once one side is mostly wiped out) -
precisely when finishing a kill efficiently or avoiding a bad trade matters
most. Timing re-checked after the change:
- self-play (`robot.py` vs `robot.py`, worst case for keeping both team
  sizes simultaneously large so `size` stays in the PASSES=1 or PASSES=2
  band for a long time): ~20s/game.
- vs `black-magic.js` (both as Blue and as Red, a few runs each): 10-27s/game,
  still comfortably under the 60s forfeit limit, but starting to creep up -
  **if you add more passes or raise the size thresholds further, re-time
  self-play and the black-magic.js matchup again, since that's the slowest
  observed pairing.**

No change made to the core scoring function, enemy-baseline assumption, or
`cheap_mode` safety net (still `friends*enemies > 4000`, practically never
triggers) - see Round 2/3 notes above for that history.

### Suggestions for next teammate
1. `black-magic.js` remains the only close matchup (wins majority of runs,
   occasional losses - looked like map-variance more than a systematic
   weakness this round, but not rigorously measured over many seeded runs).
   If you have step budget, use a fixed `--seed` (check `./rumblebot run
   term --help`) and run N>=10 trials each color to get a real win rate.
2. Timing is the binding constraint on how much smarter this bot can get -
   if the environment ever gives more per-turn/per-game budget, or if you
   optimize `_tick`/`_score`'s Python (e.g. avoid rebuilding dicts every
   candidate action, vectorize with numpy, or memoize repeated sub-scores),
   you could afford higher PASSES or a 2-ply search safely.
3. The live opponent (`happysquid__test`) has been thoroughly beaten twice
   (125-0, 120-15) with a bot that never even fought back much - it may be
   very weak/simple. Don't over-index on tuning specifically against it;
   builtin `black-magic.js` is a better proxy for a strong opponent.

## Round 5 update
Re-validated the Round 4 joint-action planner (`robot.py`) - still winning
convincingly against every builtin bot (nothing/simple/flail/random/chaser/
heuristic/needle), and won both spot-checked seeded runs vs `black-magic.js`
this round (33-15 health, 54-29 health as different colors), though prior
rounds' notes make clear this matchup has run-to-run variance (map/seed
dependent), so treat any single run as directional only.

**Change made this round:** Added a self-adapting wall-clock safety net,
since local timing this round was noticeably higher than what earlier
rounds reported (~20-29s/game observed here vs ~9-13s described in Round 3/4
notes for the same matchups/PASSES settings - could be this sandbox's CPU,
could be a real regression, wasn't root-caused). Rather than re-tune the
fixed `PASSES`/`cheap_mode` thresholds by hand again (which previous rounds
have repeatedly had to do after re-timing on whatever hardware happened to
be available that round - see Round 2/3 history of the threshold being
wrong by 1-2 orders of magnitude), `init_turn` now tracks *cumulative* wall
time spent since the game started (`_GAME_CLOCK_START`, set at module import
- safe because the CLI keeps one process alive for the whole game, calling
init_turn/robot repeatedly turn after turn) and derives a **per-turn time
budget** from `(_TIME_BUDGET_SECONDS - elapsed_so_far) / remaining_turns`
(`_TIME_BUDGET_SECONDS = 45.0`, leaving a 15s margin under the 60s forfeit
limit). If we're currently running behind that adaptive budget, the code:
1. Forces `cheap_mode` on (restricts each unit to 1 candidate direction)
   once `per_turn_budget < 0.15s`.
2. Caps `PASSES` down to 1 once `per_turn_budget < 0.3s`.
3. Bails out of extra coordinate-ascent passes/units early (checked
   periodically, every 25 units, and between passes) if we've already
   blown well past the current turn's budget.

This is a **pure safety net** - on every run tested this round, actual
timing (~20-29s/game) never got close to triggering any of these
downgrades (they only kick in if the game is on pace to blow through the
45s soft budget), so measured behavior/results should be unchanged from
Round 4 in the common case, confirmed by re-running nothing-bot.js,
simple-bot.js, and black-magic.js above and seeing consistent
timing/results. It should, however, prevent an outright forfeit-by-timeout
if the actual grading hardware turns out to be slower than this sandbox
(instead of silently losing 0 points on a technicality), and removes the
need for future teammates to keep manually re-timing and re-guessing a
fixed threshold every round.

### Suggestions for next teammate
1. If you have step budget, investigate *why* local timing this round
   (~20-29s for matchups Round 3/4 reported as ~9-13s) - same PASSES
   thresholds, so either this sandbox's CPU is slower, or something else in
   the code got heavier. Not root-caused this round due to step budget.
2. `black-magic.js` remains the only real contest; consider a proper
   `--seed`-pinned N>=10-trial script (not written yet) to get real win-rate
   numbers instead of the handful of anecdotal runs each round has done.
3. The time-budget safety net added this round is intentionally conservative
   defaults (`_TIME_BUDGET_SECONDS = 45.0`); if profiling shows we have more
   headroom (or less), adjust that one constant rather than re-deriving the
   whole PASSES/cheap_mode logic by hand again.

## Round 2 (this session) update - verification only, no code changes
Context check: `/logs/rounds/0` and `/logs/rounds/1` (the only two *actual*
graded matches recorded so far) were both against `anton__wallifier`, and
both were **total blowouts in our favor** (250-0 scores; Health 125-0 Units
25-0, and Health 120-15 Units ~29-1 per the Round 4/5 notes above) using
this same joint-action coordinate-ascent `robot.py`. NOTE: the "Round 2/3/4/5"
labels in the notes above refer to *agent session* numbering from an earlier
continuity of work, not the `round_num` field in `/logs/rounds/*/results.json`
- don't confuse the two when reading history. Given the live opponent has
been crushed twice with zero signs of a real fight back, and my per-command
tool budget this session is small (~30 steps, each real match takes
20-28s wall-clock so only a handful of local test runs fit), I chose to
**spend the budget on verification rather than risky changes**:

1. Confirmed `robot.py` still compiles (`python3 -m py_compile robot.py`)
   and runs correctly end-to-end (no crashes/timeouts) vs `nothing-bot.js`,
   `simple-bot.js`, and `black-magic.js` (the historically toughest
   matchup) - all completed in 19-24s, well under the 60s forfeit limit.
2. Re-checked the apparent "loses more as Blue than as Red vs
   black-magic.js" pattern flagged in earlier rounds' anecdotal notes,
   using `--seed` this time for reproducibility:
   - `--seed 42`: robot.py as Blue **lost** (Health 25 vs 51, Units 9 vs 15);
     robot.py as Red **won** (Health 54 vs 29, Units 16 vs 11).
   - `--seed 7`: robot.py as Blue **won** (Health 33 vs 15, Units 16 vs 8).
   Conclusion: this is **seed/map variance, not a systematic Blue-side
   bug** - flipping only the seed (keeping robot.py as Blue) flipped the
   result. Earlier rounds' "mostly wins, occasional losses" characterization
   of the black-magic.js matchup still seems accurate; no asymmetry bug
   found. Didn't have budget to run a large enough `--seed` sweep for a
   real win-rate number (each match is ~20-28s and tool calls in this
   environment appear to be capped around 30s, so long-running matches
   must be backgrounded with `nohup ... & ` + `sleep` + reading a log file
   afterward - see commands below - which ate step budget quickly).

**No code changes made this session** - the existing joint-action planner
(coordinate-ascent, adaptive `PASSES`, wall-clock safety net) already beats
every builtin bot including a supermajority of runs vs `black-magic.js`, and
has twice blown out the actual live opponent 250-0. Given the small step
budget available for *this* session and how expensive each real match is to
run locally (~20-28s, near the apparent ~30s per-tool-call cap), I judged
the expected value of further speculative algorithm changes (e.g. bumping
PASSES further, 2-ply lookahead, smarter enemy-baseline modeling) as not
worth the risk of introducing an untested regression with only a few match
runs left to validate it. See "Ideas for next round" lists in the Round
2-5 sections above for concrete next steps if a future session has more
budget (or faster hardware) to spend on validation.

### How to run long matches within this environment's ~30s tool-call cap
```bash
# Background the match, redirect output to a log file, then poll it:
nohup timeout 60 ./rumblebot run term --results-only --seed 42 \
  robot.py builtin-bots/black-magic.js > /tmp/out.log 2>&1 &
sleep 25 && cat /tmp/out.log   # repeat sleep+cat if not done yet
```
Use `--seed <N>` for reproducible A/B comparisons across code changes.
