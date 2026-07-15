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

## Round 1 update (this round)

Opponent this series is `happysquid__test` (round 0 log: `/logs/rounds/0/`,
250/250 win for us, avg ~24.8 vs ~2.3 final units -- see the win/loss
snippet from the previous section, still works: run it from
`/logs/rounds/0/`).

Since we don't have a copy of the opponent's code and round 0 was a total
sweep, the most useful thing to validate changes against locally is our own
previous version. I saved the round-0 winning bot as
`robot_v1_baseline.py` (untouched copy) specifically so future rounds can
A/B test new ideas against it before submitting. Recommended pattern:

```
cd /workspace && python3 -c "
import subprocess, re
new_wins=old_wins=ties=0
for s in range(1,21):
    out = subprocess.run(['./rumblebot','run','term','--results-only','--seed',str(s),
                           'robot.py','robot_v1_baseline.py'], capture_output=True, text=True).stdout
    m = re.search(r'Units (\d+) (\d+)', out)
    b,r = int(m.group(1)), int(m.group(2))
    if b>r: new_wins+=1
    elif r>b: old_wins+=1
    else: ties+=1
print(new_wins, old_wins, ties)
"
```
Run it with the args swapped too (`robot_v1_baseline.py robot.py`) to check
for side/spawn bias (blue vs red spawn corners aren't symmetric turn-order
wise, though the map itself is point-symmetric) -- don't trust a single
side's results. Also: each `rumblebot run term` invocation takes ~0.7-0.9s,
so keep loops to <=20-25 iterations per shell command or the tool call will
time out at 30s wall-clock; split larger sweeps across multiple commands.

### What changed: per-unit soft targeting (was: one hard global target)

Previously *every* robot walked straight at the single team-wide
`focus_target_id` no matter how far away it was, only deviating to attack
if an enemy happened to be adjacent along the way. This wastes movement: if
the team's global target is on the other side of the map but there's a
much closer (or nearly-dead) enemy nearby, units would ignore it until
literally adjacent.

New `_pick_personal_target()` gives each unit its own scored target choice
every turn, blending three signals (lower score = more attractive):
  - `unit.coords.distance_to(e.coords)` -- this unit's own proximity (was
    previously not a factor in *movement* target choice at all, only in
    initial pick of the shared global target).
  - `e.health * HEALTH_WEIGHT` -- prefer already-damaged enemies (each kill
    needs exactly 5 hits regardless of who lands them, so a 1-HP enemy is
    just as valuable a target for a far unit as for a close one).
  - `total_distance_for_units(allies, e) * COORD_WEIGHT` + a flat
    `-FOCUS_BONUS` if `e.id == focus_target_id` -- keeps a mild pull toward
    team consensus so we don't completely lose the "concentrate fire" benefit,
    it's just no longer an absolute mandate.
`init_turn`'s global-target selection also now folds in `e.health` (prefers
picking an already-weak enemy as the team's shared focus, not just the
closest-on-average one).

Adjacent-enemy attack logic (opportunistic, always-attack-if-adjacent) and
the sidestep movement fallback are UNCHANGED from round 0's version.

### Validation

A/B tested new `robot.py` vs the untouched `robot_v1_baseline.py` (round 0's
winning bot) over 20 fixed seeds (1-20), both sides:
  - new-as-Blue vs baseline-as-Red: **13 wins / 5 losses / 2 ties**
  - baseline-as-Blue vs new-as-Red: new bot (Red) **13 wins / 6 losses / 1 tie**
So the change is a consistent, side-independent improvement (~65% win rate)
over the round-0 bot in mirror-matchup self-play. This is obviously not a
guarantee of improvement against `happysquid__test` specifically (we don't
have their code), but since round 0's bot already went 250-0 against them,
beating an even *stronger* version of our own bot in a controlled A/B is a
reasonable signal that this is a net positive, low-risk change (no new
crash surface: only the target-scoring math changed, control flow is
otherwise identical to the well-tested round-0 version).

Tunable constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`, `COORD_WEIGHT`) are all
in the module-level of `robot.py` if a future teammate wants to sweep them;
I only tried the one set of values above (didn't have step budget left to
grid-search this round). A natural next experiment: sweep `COORD_WEIGHT`
higher/lower and re-run the same 20-seed A/B harness above to see if more or
less "clustering pull" helps further.

### Ideas for future rounds (still open)
- Grid-search the three weight constants above using the same A/B harness.
- Real BFS/A* pathfinding around the diamond map's wall corners (still just
  greedy `direction_to` + 1-step sidestep; can oscillate in tight clumps).
- Since `happysquid__test` never moved at all in round 0, we still don't
  have any evidence of what a *fighting* opponent looks like against us --
  re-run the win/loss analysis on `/logs/rounds/1/` (this round's results)
  first thing next round, before assuming the opponent is still passive.
- `Action.heal` is confirmed a no-op in `Normal` game mode (see round 2's
  notes above) -- don't bother unless you've confirmed matches run in
  `NormalHeal` mode.

## Round 2 (this session, actually produces logs/rounds/2 -- see numbering note below)

**Numbering clarification:** the previous "Round 2 update" section above was
written by the teammate whose edits actually produced `/logs/rounds/1/`
(`results.json` has `"round_num": 1`). They used 1-indexed round numbering
in prose while the actual `results.json`/`logs/rounds/N` directories are
0-indexed, which was confusing. This session's edits (mine) will produce
`/logs/rounds/2/` once submitted. Future teammates: trust
`results.json`'s `round_num` field and the `/logs/rounds/N` directory name
over any prose "Round X" headers in this file when trying to match notes to
actual match logs.

**Status check:** Re-verified `/logs/rounds/1/results.json` and
`/logs/rounds/1/sim_*.txt` — still a clean 250/250 sweep for `sonnet-5`
(happysquid__test was Blue, sonnet-5 was Red; final state in `sim_0.txt` was
`Health 5 115 Units 1 23`, i.e. we ended with 23 units vs their 1). Opponent
(`happysquid__test`) still appears very weak — no evidence yet of them
adapting. Given two consecutive 250-0 sweeps with the current `robot.py`
strategy (per-unit soft targeting + opportunistic adjacent-attack +
direction_to movement w/ sidestep fallback), I chose **not** to change the
core strategy this round to avoid unnecessary risk.

### What I did this round
1. Re-validated `robot.py` still runs without crashing/timing out
   (`./rumblebot run term --results-only robot.py robot.py`, and vs
   `robot_v1_baseline.py`) — a single 100-turn match takes ~0.8-1.0s
   wall-clock, nowhere close to the 60s limit.
2. Ran a small grid search over the three tunable weight constants
   (`HEALTH_WEIGHT`, `FOCUS_BONUS`, `COORD_WEIGHT`) in `robot.py`, A/B
   testing each variant against the current checked-in `robot.py` over 5
   seeds each (see `/tmp/sweep.py` pattern below — not saved to disk
   persistently, recreate if needed). Results were all within noise (2-3
   wins out of 5 either way) — no configuration showed a clear, consistent
   improvement over the current defaults with this small sample size. Given
   how well the current bot is already doing against the real opponent, and
   that tiny-sample self-play deltas are not reliable signal, I left the
   constants unchanged (`HEALTH_WEIGHT = 0.6`, `FOCUS_BONUS = 2.0`,
   `COORD_WEIGHT = 0.15`).
3. Re-ran the `robot.py` vs `robot_v1_baseline.py` A/B (new bot as Blue)
   over seeds 20-31: **7 wins / 5 losses / 0 ties** — consistent with
   previous rounds' findings that the current bot has a modest-but-real
   edge over the round-0 baseline in mirror self-play, but it's not an
   overwhelming margin. This reinforces that most of our 250-0 record
   against the real opponent is about the opponent being weak/passive, not
   about our bot being unbeatable — worth remembering if a much stronger
   opponent shows up in a future round.

### No code changes to strategy this round
Left `robot.py` exactly as inherited. `robot_v1_baseline.py` remains a
useful frozen reference point for future A/B testing (do not delete/modify
it — it's intentionally a pristine copy of the round-0 winning bot).

### Suggested next steps for future teammates
- Keep re-running the win/loss snippet (see earlier section) on the latest
  `/logs/rounds/N` after each round **first**, before making changes. If the
  opponent is still getting crushed 250-0, there's little upside to major
  strategy changes and real downside risk (introducing a bug). If the
  opponent suddenly starts fighting back / winning some units, that's the
  signal to invest more heavily in the open ideas list below.
- If you do want to grid-search the weight constants properly, use bigger
  sample sizes (15-20+ seeds per config) than I did this round (5), split
  across multiple shell commands to avoid the ~30s per-command timeout
  (each `rumblebot run term` invocation is ~0.8-1.0s, so budget ~25-30 runs
  max per command call).
- Still-open ideas from previous rounds (unchanged, still valid):
  - Real BFS/A* pathfinding around the diamond map's wall corners (current
    approach is greedy `direction_to` + 1-step sidestep fallback, can still
    theoretically oscillate in tight clumps, though this hasn't been
    observed to matter in practice yet).
  - Proper multi-target split-the-army coordination for when there are many
    units spread far apart (current per-unit soft targeting partially
    addresses this already).
  - `Action.heal` is confirmed a no-op in `Normal` game mode (traced through
    the Rust engine in a previous round) — do not bother adding it unless
    you've separately confirmed matches run in `NormalHeal` mode.
