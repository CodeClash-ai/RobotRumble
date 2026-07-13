# Notes for teammates — RobotRumble bot

## Status as of this round
The bot in `robot.py` was rewritten from scratch. The previous version
(saved as `robot_old_backup.py` for reference) used a "quadrant" targeting
scheme that had a critical bug: it only ever set a target for a quadrant if
BOTH an ally AND an enemy already existed in that exact quadrant. Because
starting positions are mirrored across the map, this condition was often
never true, so `target_ids` stayed `None` forever and robots simply never
moved — several recorded matches in `/logs/rounds/0/` end in 4v4/20hp-20hp
ties with zero movement for all 100 turns. Against real builtin bots it lost
almost every match (see test commands below).

## New strategy (current `robot.py`)
Simple but effective "group brawler" logic, no macro/global targeting needed:
1. If an enemy is adjacent, always attack — prefer the **lowest-health**
   adjacent enemy, to finish kills as fast as possible (each unit has 5 HP,
   1 dmg/attack, so finishing wounded units reduces the enemy's total attack
   output fastest).
2. Otherwise, look at all allies/enemies within `RADIUS` (=6) tiles and sum
   their HP as a proxy for "local fighting power" on each side.
   - If the enemy local power exceeds ally local power by more than
     `RETREAT_RATIO` (currently 1.5), retreat toward the centroid of nearby
     allies (regroup) instead of engaging piecemeal.
   - Otherwise, advance toward the nearest enemy.
3. Movement avoids obstacles by trying the direct direction, then rotate_cw/
   rotate_ccw, and tries not to immediately backtrack to the previous tile
   (to reduce oscillation), falling back to allowing backtrack if that's the
   only legal move.

Game mechanics learned from `logic/logic/src/lib.rs` (useful for tuning):
- `UNIT_HEALTH = 5`, `ATTACK_POWER = 1`, `HEAL_POWER = 1` (heal only matters
  in `NormalHeal` game mode).
- Units respawn periodically (`SpawnSettings`, default `spawn_every = 10`
  turns) at team spawn points — armies grow over the match, so protecting
  and grouping existing units compounds advantage over time.

## Test results (this round's rewrite vs previous bot)
Using `./rumblebot run term --results-only robot.py builtin-bots/<bot>.js`
(robot.py = Blue):

| Opponent (builtin-bots/) | Old bot result | New bot result |
|---|---|---|
| chaser.js       | Red won (0-110, 0-22u) | **Blue won** (19-6, 4-2u) |
| simple-bot.js   | Red won (20-25, 4-5u)  | **Blue won** (100-0, 20-0u) |
| needle-bot.js   | Red won (0-95, 0-19u)  | **Blue won** (52-7, 14-3u) |
| random-bot.js   | Red won (20-70, 4-14u) | **Blue won** (120-1, 24-1u) |
| nothing-bot.js  | Tie (never moved)      | **Blue won** (115-5, 23-1u) |
| flail.js        | Tie (never moved)      | **Blue won** (41-12, 10-6u) |
| heuristic-bot.js| Red won (10-40, 2-9u)  | Red won, but much closer (11-22, 5-15u @ ratio 1.1; 29-17, 8-10u @ ratio 1.5) |
| black-magic.js  | Red won (1-125, 1-25u) | Red won (13-39, 4-13u) — still losing, this bot does real lookahead/minimax over possible actions (see `builtin-bots/black-magic.js`), it's currently our toughest opponent to beat. |

`RETREAT_RATIO` was tuned a little (tried 1.1, 1.25, 1.5) — 1.5 looked like
the best overall tradeoff (only lightly tested; feel free to sweep further,
e.g. with a small script that loops over values and records the final
health/units margin against heuristic-bot.js and black-magic.js).

## Ideas for further improvement (not yet done, good next steps)
1. **Beat black-magic.js / heuristic-bot.js**: both remaining losses. Look at
   `builtin-bots/black-magic.js` — it evaluates candidate joint-actions with
   a hand-crafted scoring function (unit count diff, health diff, "surround"
   score, distance score) using something like a greedy/local-search over
   assignments. A similar (even simplified) local scoring/lookahead for our
   bot's move+attack choices could help, especially avoiding trades that
   let 2 enemies gang up on 1 of ours.
2. **Focus fire coordination across allies**: current bot only chases the
   nearest enemy per-unit; a global "team target" (like the tutorial/old bot
   attempted) that biases multiple allies to converge on the *same* weak
   enemy cluster (not just nearest-to-self) could create bigger local
   superiority swings. Just make sure to fix the original bug (don't gate
   target selection on "both quadrant lists non-empty").
3. **Better retreat pathing**: currently retreats toward the centroid of
   nearby allies, which can sometimes still walk toward the enemy if allies
   are on the far side of the enemy. Consider retreating away from the
   nearest enemy AND toward allies simultaneously (weighted vector).
4. **Tune `RADIUS` / `RETREAT_RATIO`** more rigorously — write a sweep
   script using `./rumblebot run term --results-only robot.py <opponent>`
   in a loop, parsing final health/units to score each parameter combo.
5. Consider exploiting the periodic-spawn mechanic — e.g., timing pushes to
   just after your own spawn wave lands, or defending your spawn area late
   game if you're ahead on numbers.

## Useful commands
```bash
cd /workspace
# Quick 1-off match, terminal summary only:
./rumblebot run term --results-only robot.py builtin-bots/chaser.js

# Full battle-log to inspect turn by turn (careful, long output):
./rumblebot run term robot.py builtin-bots/chaser.js

# List of builtin opponents to test against:
ls builtin-bots/
```
`/logs/rounds/<n>/sim_*.txt` contain ASCII-rendered turn-by-turn logs from
actual scored rounds — useful for post-mortem analysis of what really
happened in competitive play (e.g. `/logs/rounds/0/` showed the old bot's
"never moved" bug in real matches).

`robot_old_backup.py` is kept in the repo root for reference/diffing; feel
free to delete once no longer useful.

## Round 2 update

Round 1 result: **sonnet-5 won 250-0** against the real opponent
(`anton__anton3000`) — see `/logs/rounds/1/results.json` and
`/logs/rounds/1/sim_*.txt` (final state was Health 0(them) vs 85(us),
Units 0 vs 17 — a total wipeout). The "group brawler" bot described above
is working very well against the actual competitive opponent.

This round I experimented with adding a **shared "focus fire" target**
(computed once per turn in `init_turn`, cached in `_turn_cache`, biasing
all units' advance direction towards whichever enemy is weakest / already
has the most allies converging on it — not just each unit's own nearest
enemy) on top of the existing retreat/attack logic. Idea: make our own
units gang up the way `black-magic.js` gangs up on us (it always has each
enemy attack whichever adjacent ally has the lowest health, and its scoring
function explicitly rewards "surround").

**Result: inconclusive / slightly worse, not adopted.** I A/B tested the
experimental version (saved as `robot_focusfire_experiment.py`, NOT the
active `robot.py`) against the proven round-1 bot using
`/tmp/run_trials.sh <bot> <opponent.js> <N>` (recreate this script if it's
gone — it's just a loop calling `./rumblebot run term --results-only` and
parsing the `Final state: Health A B Units C D` line; A/B are Blue/Red
health). With N=6 trials per matchup (small sample, high variance —
starting positions/board seed differ each run, so treat this as a rough
signal, not gospel):

| Opponent | old bot (r1) avg health diff | focus-fire experiment avg health diff |
|---|---|---|
| flail.js         | +13 (4W/2L)  | +12 (4W/2L) — basically a wash |
| heuristic-bot.js | +18 (5W/1L)  | +14 (3W/2L/1T) — old bot looked better |
| black-magic.js   | -33 (0W/6L)  | -40 (0W/6L) — old bot looked (slightly) better |

Given the extra complexity and no clear win, I **reverted `robot.py` back
to the exact round-1 version** (identical to `robot_r1_backup.py`) rather
than risk a regression. The focus-fire code is preserved in
`robot_focusfire_experiment.py` in case a future teammate wants to pick it
up, debug/tune it further (e.g. `FOCUS_ALLY_WEIGHT`, `FOCUS_HEALTH_WEIGHT`,
`FOCUS_SCAN_RADIUS`, or the "don't bias if focus target is >3 tiles further
than nearest enemy" heuristic — all currently pretty arbitrary/untuned), or
run a much larger N to get a statistically meaningful comparison (N=6 is
really not enough given how much variance there is even for the *same*
bot/opponent pair — see the flail.js numbers in the previous round's table
in this same file, which don't match what I measured this round for the
supposedly-identical old bot).

**Still unresolved from round 1**: both the shipped bot and the focus-fire
experiment lose consistently to `black-magic.js` (a real 1-ply hill-climbing
lookahead bot, see `builtin-bots/black-magic.js`) and are inconsistent
against `heuristic-bot.js`. Since we're crushing the *actual* human/agent
opponent (`anton__anton3000`) 250-0, this may not matter competitively, but
if a future opponent plays more like black-magic.js, it's worth another
serious look. Ideas if you pick this up:
- Implement a real (even shallow, 1-ply) lookahead like black-magic.js does:
  for each unit try all legal actions, simulate the immediate result
  (including "what would enemies adjacent to us do"), and score with
  something like unit-count-diff + health-diff + surround-diff, taking the
  best-scoring action greedily per unit. This is a bigger rewrite than the
  focus-fire tweak and would need careful testing (also watch the 60s time
  budget — with up to ~20-25 units per side this could get slow if not
  careful, e.g. avoid recomputing the same simulated board per unit from
  scratch if possible, or cap the number of enemies/allies considered per
  simulation).
- Rerun the A/B script above with N=20+ per matchup to get real signal
  before adopting any change — 6 trials was not enough this round given
  time constraints (30-step budget).

### Tools left in the repo
- `robot.py` — active bot, currently == `robot_r1_backup.py` (round-1
  winning version, unchanged this round).
- `robot_r1_backup.py` — explicit copy of the round-1 winning bot, kept as
  a stable reference/baseline to A/B test against.
- `robot_focusfire_experiment.py` — this round's untried/inconclusive
  focus-fire variant, not currently used, but may be worth iterating on.
- `robot_old_backup.py` — the original (broken, "never moves") bot from
  before round 1, kept for historical reference only.
- Recreate `/tmp/run_trials.sh` (see above) if you want quick win/loss +
  average-health-diff stats over N trials instead of eyeballing single-game
  terminal output.
