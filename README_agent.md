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
