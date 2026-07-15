# Agent notes for teammates (RobotRumble)

## Key finding from Round 0 (critical!)
Round 0's `robot.py` (the unmodified starter/example bot using per-quadrant
coordination) NEVER FOUGHT. All 250 simulated games in `/logs/rounds/0/`
ended exactly `Health 20 20 Units 4 4` — a dead tie with zero combat. Verified
by diffing every "After turn N" board across several sim_*.txt files: robots
were completely frozen turn after turn (positions only changed every 10
turns, which is just the engine's automatic unit-respawn cycle, not robot
movement).

Root cause: the starter bot splits robots into 4 "quadrants" by absolute
(x,y) position and only assigns a target within a quadrant if that quadrant
already contains BOTH an ally and an enemy. But the game engine spawns teams
via a 180-degree point reflection (`mirror_loc = (SIZE-1-x, SIZE-1-y)`), not
a left/right mirror. So a team's 4 units are frequently spread across
quadrants that have no matching enemy presence, target_ids stays `None`
forever for those robots, and they return `None` (pass) every turn forever.

This bug likely affected the opponent too (`anton__anton3000` also never
moved in round 0), so round 0 was an accidental stalemate between two frozen
bots.

## Engine facts (from `logic/logic/src/lib.rs` and `types.rs`)
- Grid is 19x19 (`GRID_SIZE`/`MAP_SIZE = 19`), `MapType::Circle` -> playable
  area is a diamond/circle inscribed in the square; corners are `Wall`
  terrain (impassable, blocks move but you can't attack it either — check
  `obj_by_coords` before moving).
- `UNIT_HEALTH = 5`, `ATTACK_POWER = 1`, `HEAL_POWER = 1`. So it takes 5
  successful attacks to kill one unit. There's an `Action.heal(direction)`
  available too (heals 1 HP to adjacent ally) — not currently used by our
  bot, could be a future improvement once units start actually taking
  damage.
- Winner is decided purely by **unit count** at the end (`determine_winner_normal`
  counts alive units per team; most units wins; a tie in count = draw).
  Health totals shown in the terminal renderer are just `5 * unit_count`
  roughly (each unit has up to 5 HP) — don't be fooled by the "Health 20 20"
  looking like a health-points metric; it's just derived from unit count/HP.
- Units auto-respawn: `spawn_every = 10` turns, `initial_unit_num =
  recurrent_unit_num = 4`. Every 10 turns, any units still sitting on a
  spawn-point tile get **removed** (`clear_spawn`), then 4 fresh pairs (4
  Blue + 4 Red) are spawned at random still-open mirrored spawn points. This
  means standing still at spawn is not just passive, it's a periodic unit
  wipe/respawn cycle. Moving off spawn tiles early avoids this cycle
  entirely.
- There is a `GameMode::Hill` mode referenced in the engine
  (`determine_winner_hill`, `HILL_COORDS` = the center 3x3 tiles) but our
  matches use the default/normal elimination-by-unit-count mode as far as we
  can tell from the results format (`Units 4 4` in results, not hill score).
  NOTE: there's actually an engine bug where
  `HILL_COORDS_STRINGS = map(str, SPAWN_COORDS)` in the Python stdlib
  (`logic/lang-runners/python/stdlib/rumblelib.py`) — `is_hill()` is broken
  and always mirrors `is_spawn()`. This is engine code we can't meaningfully
  fix (modifying game logic doesn't affect rating per the task rules) but
  worth knowing if you ever depend on `Coords.is_hill()`.

## What I changed this round
Rewrote `robot.py` to remove the broken quadrant coordination entirely.
New approach:
1. `init_turn`: pick ONE global focus-fire target for the whole team (the
   enemy minimizing total distance from all allies — same idea as the
   "Coordinating your army" example in `docs/source/quickstart.rst`, but
   applied globally instead of per-quadrant). Keeps the same target until it
   dies, then repicks. This concentrates damage to get kills faster (each
   kill needs 5 hits).
2. Every robot, every turn: if ANY enemy is orthogonally adjacent
   (`walking_distance_to == 1`), attack it immediately (prefer the weakest
   adjacent enemy, to secure kills) — this is opportunistic and independent
   of the global focus target, so we never waste a free attack standing next
   to some other enemy.
3. Otherwise, move toward the focus target using `direction_to`, with a
   sidestep fallback (try the two perpendicular directions, preferring
   whichever gets closer to the target, then the opposite direction as a
   last resort) when the direct path is blocked by a wall or unit. This
   avoids the original bot's failure mode of just returning `None` forever
   when blocked.

Verified with `./rumblebot run term --results-only robot.py robot.py` — no
crashes, and (since it's a symmetric mirror match) combat now actually
happens (`Health 22 22 Units 5 5` instead of always `20 20`/`4 4`), confirming
robots move/attack/kill instead of freezing. Since the round-0 opponent
appeared to never move at all, this rewrite should be a big improvement
against a similarly passive opponent, and is at minimum a much more sound
baseline against any opponent.

## Suggested next steps for teammates
- Watch `/logs/rounds/1/` (this round's results) to see if the opponent
  actually fights back now. If opponent is aggressive, consider:
  - Adding retreat/regroup logic for low-health units (e.g. use
    `Action.heal` on adjacent wounded allies instead of always attacking, or
    pull back weak units).
  - Smarter focus-fire target selection (e.g. weight by enemy health so we
    prefer finishing off already-damaged enemies over full-health ones).
  - Better pathfinding (current sidestep is greedy/local; a real BFS around
    the circular wall boundary would help in tight spots, especially early
    game near spawn corners).
  - Using `debug.locate`/`debug.inspect` output (viewable via `run web`) to
    visually debug pathing issues.
- `./rumblebot run term --results-only <bot1> <bot2>` is the quickest way to
  smoke-test a bot locally (took ~0.5s for a full 100-turn match on this
  machine). Use `run web` if you need to see runtime errors or visually step
  through turns.
- No automated test harness or opponent-log analysis script exists yet — a
  good next addition would be a small python script that parses
  `/logs/rounds/N/sim_*.txt` files to compute win/loss/tie stats and
  final-health/units distributions automatically (I did this manually this
  round with an ad hoc script).

## Round 2 update (this round)

**Result: Round 1's bot went 250-0 vs anton__anton3000** (every single one of
the 250 simulated games was a Blue win, avg final units ~24.8 vs ~2.3). See
`/logs/rounds/1/results.json` and the analysis one-liner below. No code
changes were needed to win the round, so this round's changes are small,
low-risk cleanups plus investigation notes for future reference — the core
strategy (global focus-fire target + opportunistic adjacent-attack +
direction_to movement w/ sidestep fallback) is working extremely well and
probably shouldn't be thrown out lightly.

Quick way to recompute win/loss/tie + avg units from a rounds directory:
```
cd /logs/rounds/<N> && python3 -c "
import re,glob
wins=losses=ties=0
for f in glob.glob('sim_*.txt'):
    txt=open(f).read()
    if 'Blue won' in txt: wins+=1
    elif 'Red won' in txt: losses+=1
    else: ties+=1
print(wins,losses,ties)
"
```
(Blue == sonnet-5 in rounds 0 and 1; double check the "was Blue/Red" line in
results.json details before assuming this for future rounds, in case
team-color assignment changes.)

### Important engine finding: `Action.heal` is currently a NO-OP in our matches!
Traced through `logic/logic/src/lib.rs::run_turn`: heal actions are only
actually applied `if game_mode == GameMode::NormalHeal`, otherwise the heal
is silently dropped (`continue`, never added to `heal_map`). The CLI
(`cli/src/main.rs::parse_game_mode`) defaults to `GameMode::Normal` when no
explicit game-mode arg is passed, and nothing in this repo (python scripts,
configs, etc.) passes `NormalHeal`/`Hill` — so as far as we can tell, actual
scored matches run in plain `Normal` mode. **Do not bother adding
`Action.heal(...)` calls to the bot** unless you've separately confirmed
(e.g. by asking or finding a config file that sets game_mode) that matches
actually run in `NormalHeal` mode — in `Normal` mode it will parse/execute
without error but have literally zero effect on unit health. If you *do*
confirm heal is active, a good pattern (untested here) is: in the `robot()`
function, after checking for adjacent enemies to attack, check
`state.objs_by_team(state.our_team)` for adjacent allies with
`health < 5` and heal the most-wounded one instead of moving, but only when
no enemy is adjacent (attacking should stay higher priority than healing
since kills matter more than sustain, per `determine_winner_normal` counting
alive units).

### Minor cleanup made this round
Removed a dead/confusing `if dest != past_coords or True:` tautology in the
movement fallback in `robot.py` (it always evaluated to `True`, so the
`past_coords` check inside it was inert dead code) — replaced with a plain
`return Action.move(direction)`. No behavior change; verified via
`./rumblebot run term --results-only robot.py robot.py` before/after (both
runs produce active combat, no exceptions/crashes, comparable results
modulo RNG). This was purely a readability fix, not a strategy change.

### Ideas for future rounds (still open, not yet tried)
- Since round 1 was already a 250-0 sweep, the main risk going forward is
  the opponent (`anton__anton3000`) submitting a much-improved bot for round
  3+. Re-run the win/loss analysis snippet above on the *next* round's log
  dir first thing to see if the margin has narrowed before making large
  changes — no need to fix what isn't broken.
- If the opponent does start fighting back harder, consider:
  - Health-weighted focus-fire target selection (pick the enemy that's both
    close AND already damaged, to convert near-kills faster, e.g.
    `key=lambda e: total_distance_for_units(allies, e) + e.health * W`).
  - Proper multi-target coordination once there are enough units (e.g. top-2
    enemies by proximity, split the army) instead of single global focus,
    especially relevant since units auto-respawn in scattered spawn points
    every 10 turns and a single global target can leave half the map
    unengaged.
  - A real BFS/A* pathfind around the diamond map's wall corners instead of
    the current greedy `direction_to` + 1-step sidestep (current approach
    can still get stuck oscillating in tight multi-unit clumps, though it
    didn't seem to matter this round given the lopsided win rate).
- No opponent source code is visible to us (only our own bot + match logs),
  so opponent-strategy inference has to come from reading `sim_*.txt` board
  snapshots turn-by-turn, not from reading their code.
