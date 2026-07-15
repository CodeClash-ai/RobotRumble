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
