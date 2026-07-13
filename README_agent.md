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

## Round 3 update (this session)

Reviewed `/logs/rounds/0/results.json` and `sim_*.txt`: our bot (`robot.py`,
unchanged "group brawler" logic from round 1) played as **Red** against
opponent `happysquid__test` (Blue) and won **250-0** — a total wipeout
(final state Health 0-110..120, Units 0-1 vs 22-24 for us, across the
recorded games). This confirms the current bot dominates the actual
ladder opponent completely; there is no headroom left to improve the score
against this specific opponent (already 0 for them).

### What I did this round
- Re-verified `robot.py` is byte-identical to `robot_r1_backup.py` (the
  proven round-1 winner) — confirmed, no drift.
- Re-ran the full builtin-bot test suite (see commands below) to confirm
  no regressions / no crashes / timing well within budget (all games
  complete in ~0.5-2s, far under the 60s limit):
  - chaser.js, simple-bot.js, needle-bot.js, random-bot.js, nothing-bot.js,
    flail.js, heuristic-bot.js: **all won**, similar margins to round 1's
    notes.
  - black-magic.js: still **loses** (re-confirmed with an 8-trial sweep
    using `/tmp/run_trials.sh robot.py builtin-bots/black-magic.js 8` →
    0W/7L/1T, avg health diff ≈ -31.5). This remains the one opponent
    archetype (real greedy hill-climbing lookahead) that beats us, but
    since the actual ladder opponent (`happysquid__test`) is far weaker
    and already fully defeated (250-0), I decided **not** to risk
    destabilizing the proven winning logic chasing black-magic.js parity
    this round — see "Decision" below.
- Recreated `/tmp/run_trials.sh <bot> <opponent.js> <N>` (N-trial
  win/loss/tie + avg health-diff sweep helper) since it doesn't persist
  between sessions; copy of the script contents is inlined in this file's
  git history / round-2 notes above if you need to recreate it again.

### Decision: no code changes this round
Given:
1. We already beat the real opponent as decisively as the scoring allows
   (250-0, complete unit wipeout), and
2. The opponent is the *same* team across all 5 rounds (per task setup),
   so there is no new information suggesting they'll suddenly play like
   black-magic.js,
3. Every prior attempt (see round 2 notes above, `robot_focusfire_experiment.py`)
   to improve beyond the round-1 baseline showed no measurable gain (or a
   slight loss) in only marginal test sizes,

...the highest-expected-value action this round was to **avoid regression
risk** rather than gamble on an unproven change against an opponent we've
already 100% defeated. `robot.py` is unchanged from `robot_r1_backup.py`.

### For future teammates
- If a future round's `/logs/rounds/<n>/results.json` ever shows a
  *closer* result (not 250-0) against the real opponent, that's a signal
  they've changed strategy or a different opponent has been substituted —
  worth revisiting the black-magic-style lookahead idea (see round-2 notes,
  point 1 in "Ideas for further improvement") at that point.
- `robot_focusfire_experiment.py` is still sitting there unused if someone
  wants to pick up focus-fire coordination again with a bigger sample size
  (N=20+ trials) than previous attempts used.
- Test suite command reminder:
  ```bash
  cd /workspace
  for f in builtin-bots/*.js; do
    echo "=== $f ==="
    ./rumblebot run term --results-only robot.py "$f" 2>&1 | tail -3
  done
  ```

## Round 4 update (this session)

Reviewed `/logs/rounds/0/` and `/logs/rounds/1/` results.json + sim logs:
our bot (`robot.py`, unchanged since round 1) has won **250-0** both times
against the real ladder opponent (`happysquid__test`), once as Red
(23 units vs 1, health 115 vs 3) and once as Blue (27 vs 0, health 135 vs 0
in a fresh confirmation run). This is a complete, repeated wipeout — there
is no score headroom left against this specific opponent, and the opponent
has been the same across all rounds so far.

### Bug found & fixed in the trial-analysis tooling
Recreated `/tmp/run_trials.sh` (per earlier round's instructions) and
discovered the **health-diff averaging in this helper (and possibly in
previous rounds' identical script) had an off-by-one `awk` field bug**:
`Final state: Health A B Units C D` has "Health" itself as a field, so
`{print $3}`/`{print $4}` grabbed `"Health"` and `A` instead of `A` and `B`.
Fixed to `$4`/`$5`. This means **some average-health-diff numbers quoted in
earlier rounds' notes (round 2/3 sections above) may be wrong/meaningless**
— though the win/loss/tie counts in those tables were derived from `grep`
on "Blue won"/"Red won" text, which is unaffected by this bug and should
still be trustworthy.

### Re-measured variance vs builtin bots (with the fixed script)
With the corrected script, re-ran larger samples against a couple of
opponents to sanity-check the claims in earlier rounds:
- `heuristic-bot.js`, N=8: **6W/2L**, avg health diff +23.5 — consistent
  with earlier rounds' notes (we're clearly ahead here, though not
  dominant).
- `black-magic.js`, N=6: **0W/6L**, avg health diff -37.3 — confirms this
  remains a real loss matchup (as documented in rounds 2/3), unchanged.
- `flail.js`: **this one is much less clear-cut than earlier rounds'
  tables suggested.** Combined over 20 trials (two batches of N=8 and
  N=12): **8W/10L/2T** — essentially a coin flip, not the "reliable win"
  (10W/6L or 41-12 health) claimed in round-1/round-2 notes. flail.js moves
  randomly, so matches against it seem to have very high position-dependent
  variance (who starts closer to whom, whether our "retreat when
  outnumbered locally" logic causes us to dodge productive fights, etc).
  This does **not** matter for the real ladder matchup (happysquid__test is
  not flail-like and we crush it 250-0 either way), but flagging it here so
  nobody assumes flail.js is an easy/solved matchup based on older notes —
  if you rerun any A/B tuning that uses flail.js as a benchmark, use a
  large N (20+) and don't trust small-sample health-diff numbers from
  before this fix.

### Decision: no code changes this round (again)
Same reasoning as rounds 2 and 3: we are already beating the actual
opponent as decisively as possible (250-0, near-total unit wipeout, twice
in a row), the opponent has shown no sign of changing strategy, and no
previously-attempted change (focus-fire experiment, retreat-ratio tuning)
has shown a clear, statistically solid improvement even against the
tougher synthetic bots. Given the step budget for this session, I chose to
spend it on (a) verifying no regressions/timing issues (all builtin-bot
matches still complete in 1-2s, far under the 60s budget) and (b) fixing
the measurement tooling bug above so future rounds get accurate signal,
rather than gambling on an unproven tweak. `robot.py` is byte-identical to
`robot_r1_backup.py`.

### For future teammates
- If a future round's real-match result is ever NOT a 250-0 wipeout, that's
  the signal to revisit strategy (black-magic-style 1-ply lookahead is
  still the most promising unexplored direction — see round 2 notes).
- Use the **fixed** `/tmp/run_trials.sh` (field indices `$4`/`$5`, not
  `$3`/`$4`) if recreating it, and prefer N>=20 for any matchup you plan to
  make tuning decisions from — variance is high (see flail.js above).
- `robot_focusfire_experiment.py` remains unused/unadopted; still there if
  someone wants to revisit it with a bigger, bug-fixed sample.

## Round 5 update (this session)

Reviewed `/logs/rounds/0/` (only round-log directory present this session,
`results.json` + 250 `sim_*.txt` files) — this time the real opponent is
named **`anton__wallifier`** (previous rounds faced `anton__anton3000` and
`happysquid__test`), so the opponent identity/account has changed again
across rounds. Result: **sonnet-5 (us) won 250-0** — checked several
`sim_*.txt` files (e.g. `sim_249.txt`) and the pattern is the same as every
previous round: opponent starts with the normal 4 units, gets rapidly wiped
out within the first ~10-20 turns, and then simply has **0 units for the
rest of the 100-turn match** (no respawns ever appear for them) while our
army grows via periodic spawns to 25-29 units. This looks like either a
very weak/non-adaptive opponent bot or an opponent that errors out early
(can't tell from logs alone, but functionally it doesn't matter — the
result is a total wipeout either way).

### What I did this round
- Confirmed `robot.py` is still byte-identical to `robot_r1_backup.py` (the
  original round-1 "group brawler" logic) — no drift, matches what rounds
  2-4 also found.
- Re-ran the full builtin-bot regression suite (all games <2s, well inside
  the 60s budget, no crashes):
  - **Won**: chaser.js (17-7, 4-2u), flail.js (39-16, 9-6u),
    heuristic-bot.js (18-6, 8-6u), needle-bot.js (47-0, 14-0u),
    nothing-bot.js (125-5, 25-1u), random-bot.js (120-12, 24-4u),
    simple-bot.js (145-5, 29-1u).
  - **Lost** (only remaining loss, unchanged since round 2): black-magic.js
    (9-39, 3-14u) — this is the one synthetic opponent with real per-turn
    lookahead/scoring, and it remains undefeated by our current heuristic
    bot. See rounds 2-4 notes above for detailed ideas on closing this gap
    (1-ply lookahead / minimax-style local scoring) if a future opponent
    ever plays similarly.
- Did **not** change any code this round. Rationale is identical to rounds
  3 and 4: we are already winning the real ladder matchup as decisively as
  the scoring system allows (250-0, complete and sustained unit wipeout —
  opponent never got a single unit back for the entire 100-turn match), the
  opponent keeps getting fully defeated regardless of account name changes,
  and every previously-attempted tuning/rewrite (focus-fire experiment,
  retreat-ratio sweeps) has failed to show a clear, well-sampled
  improvement even against the tougher synthetic bots. Given the 30-step
  budget, spending it on a risky, likely-marginal rewrite against a
  real opponent we already 100%-beat is negative expected value; verifying
  no regressions and keeping notes accurate for the next teammate is higher
  value.

### For future teammates
- If a future round ever shows a real-match result that is **not** a
  100% wipeout (e.g. opponent keeps units alive past the first ~20 turns,
  or actively contests our spawn regrowth), that's the signal the opponent
  has actually improved/changed strategy — that's the time to seriously
  invest in the black-magic-style 1-ply lookahead idea (see round 2's "Ideas
  for further improvement", point 1) since our heuristic bot's one known
  weakness is against opponents with real per-turn action lookahead.
- Otherwise, this bot ("group brawler": attack weakest adjacent enemy,
  retreat toward allies when locally outnumbered by `RETREAT_RATIO=1.5`,
  else advance toward nearest enemy) continues to be a robust, low-risk,
  well-tested default. Don't destabilize it without a large-N (20+) A/B
  test showing a clear win, per the mistakes/lessons in rounds 2-4.
