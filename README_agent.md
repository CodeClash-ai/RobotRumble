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

## Round 3 (this session — will produce /logs/rounds/1/ once submitted)

**Status check (first thing, per previous teammates' advice):** Re-verified
`/logs/rounds/0/results.json` and all 250 `sim_*.txt` files for this
session's *starting point*. Opponent this series is now `anton__wallifier`
(a different name than the `happysquid__test`/`anton__anton3000` opponents
referenced in older notes above — this looks like a new opponent-name
episode, but same overall dynamic). Result: **250/250 win for sonnet-5**
(sonnet-5 was Red). Computed via the win/loss snippet (still works, run
from `/logs/rounds/0/`): `Blue wins: 0 Red wins: 250 ties: 0`. Also checked
final unit counts across all 250 sims: opponent (Blue/anton__wallifier)
averaged **1.9** final units (range 0-5) vs our **27.9** (range 16-38). So
the opponent is still extremely weak/passive relative to us — another total
sweep, even more lopsided in final-unit-count terms than the round
summarized earlier in this file.

### What I did this round
1. Confirmed `robot.py` still matches the strategy described in the
   docstring/prior notes (per-unit soft targeting blending own-distance +
   target health + team focus-bonus + coordination-distance; opportunistic
   always-attack-if-adjacent; `direction_to` movement with sidestep
   fallback). No drift/staleness between code and docs.
2. Sanity-checked `robot.py` still runs cleanly and fast:
   `./rumblebot run term --results-only robot.py robot.py` → completes in
   ~1s wall-clock (well under the 60s limit), no exceptions, real combat
   happens (not frozen).
3. Grid-swept the three tunable weight constants again (`HEALTH_WEIGHT`,
   `FOCUS_BONUS`, `COORD_WEIGHT`) via temp copies in `/tmp`, A/B'd each
   variant vs the current checked-in `robot.py` over ~12-24 seeds per
   variant (pattern: copy `robot.py` to a temp file, `sed`/`re.sub` the
   constant, run `./rumblebot run term --results-only --seed N
   variant.py current.py` in a loop, tally `Units X Y` regex). Findings:
   - `HEALTH_WEIGHT=1.0` (vs default 0.6): 7-4-1 over seeds 1-12, but
     5-7-0 over seeds 13-24 → net ~roughly even (12-11-1 combined), i.e.
     within noise, NOT a clear improvement.
   - `FOCUS_BONUS=4.0` (vs default 2.0): 6-4-2 over seeds 1-12 — mild edge
     but small sample, didn't extend the sweep further.
   - `COORD_WEIGHT=0.0` and `COORD_WEIGHT=0.3` (vs default 0.15): both
     roughly break-even (5-5-2 and 7-5-0 respectively) over seeds 1-12.
   - **Conclusion: none of the swept configs showed a clear, robust
     improvement over the current defaults** at the sample sizes I could
     afford this round (~12-24 seeds/config, limited by the ~30s per-shell-command
     budget — each `rumblebot run term` call is ~0.8-1s). Left the
     constants unchanged (`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`,
     `COORD_WEIGHT=0.15`).
4. **No code changes made this round.** Given (a) a 250/250 sweep with an
   even *larger* final-unit-count margin than previous rounds, and (b) no
   statistically clear win from re-sweeping the weight constants, the
   highest-value action was to validate-and-document rather than risk
   introducing a regression for an already-dominant matchup.

### Suggested next steps for future teammates
- Keep doing the "check `/logs/rounds/N/results.json` + unit-count margins
  first" step before changing anything. If `anton__wallifier` (or whatever
  the opponent is named by then) starts actually fighting back / winning
  units, *that's* the signal to invest in the open ideas list below. Right
  now every round has been an overwhelming sweep, so low-risk, incremental
  validation is more valuable than large rewrites.
- If you want to re-attempt the weight sweep, use bigger seed counts
  (30-50+ per config) split across multiple shell commands (each
  `./rumblebot run term` call is ~0.8-1s; a single shell command times out
  around 30s wall-clock, so budget ~25-30 runs per `bash` tool call) — the
  12-24 seed samples this round and in round 2's notes were both too small
  to distinguish real signal from noise (deltas of 1-2 games out of 12).
- Still-open, still-untried ideas from earlier rounds (see sections above
  for full rationale, unchanged):
  - Real BFS/A* pathfinding around the diamond map's wall corners (current
    approach is greedy `direction_to` + 1-step sidestep fallback).
  - Proper multi-target split-the-army coordination for widely separated
    unit clusters (partially mitigated already by per-unit soft targeting).
  - `Action.heal` is a confirmed no-op in `Normal` game mode (traced
    through the Rust engine) — don't add it unless you've separately
    confirmed matches run in `NormalHeal` mode.
- `robot_v1_baseline.py` remains a frozen, untouched copy of the round-0
  winning bot, kept specifically for A/B self-play testing — do not
  delete/modify it.

## Round 4 (this session — will produce /logs/rounds/2/ once submitted)

**Status check (first thing):** Re-verified `/logs/rounds/1/results.json` and
`sim_*.txt` — still `anton__wallifier` as opponent, still a clean **250/250
sweep for sonnet-5** (avg final units: opponent ~1.98, us ~28.1 — computed
with the standard win/loss snippet from earlier sections, still works).
Third consecutive total sweep across rounds 0/1 of this series against this
opponent name. No sign of the opponent adapting.

### What I did this round
1. Re-ran the weight-constant grid search one more time (`HEALTH_WEIGHT`,
   `FOCUS_BONUS`, `COORD_WEIGHT`) via temp variants in `/tmp/variants/`,
   A/B'd against the current defaults over ~20-30 seeds each split across
   several shell calls (each `rumblebot run term` call ~0.8-1s; keep
   loops to <=10-15 iterations per `bash` call to avoid the ~30s per-command
   timeout — I hit a timeout once this round with 15 iterations x 4 variants
   in one call, had to split further). Result: consistent with rounds 2/3's
   findings — `HEALTH_WEIGHT` around 1.0-1.2 shows a *mild* positive trend
   (~16-12-2 combined across 30 games, i.e. ~57%) but it's within
   plausible noise for this sample size, same conclusion as previous
   rounds. **Did not change the weight constants** — three rounds running
   now of nobody finding a robust signal here; if a future teammate wants
   to resolve this, it needs a much bigger sample (50+ seeds) or, better,
   actual evidence the opponent is competitive enough that these marginal
   gains matter.

2. **Found and fixed a real (if low-probability) bug**: when `enemies` is
   empty (no visible enemy units — can happen briefly between wiping the
   opposing team and the next periodic respawn wave, since spawns happen
   every `spawn_every=10` turns per `logic/logic/src/lib.rs::run`), the old
   `robot()` unconditionally `return None`d, i.e. every unit freezes
   completely. Traced the engine's spawn-cycle code
   (`clear_spawn`/`spawn_units` in `run()`): at the *start* of every turn
   where `(turn - 1) % spawn_every == 0` (turns 11, 21, 31, ...,
   BEFORE that turn's robot actions are even requested), `clear_spawn()`
   deletes **any unit of either team still sitting on a spawn-point
   tile**, no exceptions. So if one of our own units happens to be
   idling (frozen because `enemies` was empty) on a spawn tile when this
   turn hits, we lose that unit for free, for no reason
   (`determine_winner_normal` only counts alive units, so this is a pure,
   avoidable unit-count loss).
   Fix: in `robot()`, when `enemies` is empty, check
   `unit.coords.is_spawn()` first; if true, actively move to any adjacent
   free non-spawn tile instead of passing (falls through to `return None`
   otherwise, same as before). Cheap, low-risk, purely defensive — doesn't
   change behavior at all when enemies are visible (the overwhelming
   majority of turns in every game we've observed so far, since the
   opponent has 250/250 always still had *some* units alive most of the
   match). See the diff in `robot.py`'s `robot()` function, right after
   `enemies = state.objs_by_team(state.other_team)`.
   - Validated: `./rumblebot run term --results-only robot.py robot.py`
     and `... robot.py robot_v1_baseline.py` both run cleanly, no
     exceptions, combat still happens normally.
   - Re-ran the standard 10-seed A/B vs `robot_v1_baseline.py`: **6 wins /
     4 losses / 0 ties** — consistent with previous rounds' ~55-65% edge
     over the baseline, i.e. no regression from this change (expected,
     since it only fires in the rare "zero visible enemies" case which
     didn't come up much in these particular seeds either way — this fix
     is more of an insurance policy against an edge case than a strategy
     change, so seeing "no measurable difference" in a small sample is
     actually the expected/desired outcome, not a null result).

### Suggested next steps for future teammates
- Same standing advice as previous rounds: check
  `/logs/rounds/N/results.json` + unit-count margins FIRST. If the
  opponent (`anton__wallifier` as of this writing) is still getting
  crushed 250-0, prioritize low-risk validation over big rewrites.
- The "zero visible enemies -> move off spawn tile" fix this round is
  purely defensive/edge-case; it's very unlikely to have caused any of the
  3 sweeps so far (opponent always had units alive), so don't expect it to
  suddenly change score against a currently-weak opponent. It's there in
  case a future stronger opponent gets fully wiped out mid-match by us and
  the empty-enemies branch actually starts mattering.
- Weight-constant tuning (`HEALTH_WEIGHT`/`FOCUS_BONUS`/`COORD_WEIGHT`) has
  now been attempted and inconclusive across 3 separate rounds (this one,
  and the two "Round 2"/"Round 3" sections above) — recommend NOT
  re-attempting this with small samples again; either commit to a large
  (50+ seed) sweep in one sitting, or leave it alone and focus effort
  elsewhere (BFS pathfinding, multi-target split-army coordination — both
  still untried, see earlier sections).
- Remember: `rumblebot run term` calls are ~0.8-1s each; a `bash` tool
  call here times out around 30s wall-clock, so keep any A/B-loop to
  <=15-20 iterations per call (I hit exactly this timeout once this round).

## Round 5 (this session — will produce /logs/rounds/1/ once submitted, since
starting point this session was /logs/rounds/0/)

**Status check (first thing, per standing advice):** Re-verified
`/logs/rounds/0/results.json` for this session's starting point. Opponent
this series is `ldang__nessy` (yet another new opponent name — 5th
different name across the rounds documented in this file:
`happysquid__test`, `anton__anton3000`, `anton__wallifier`, and now
`ldang__nessy`). Result: **250/250 sweep for sonnet-5** again (`Blue wins 0,
Red wins 250, ties 0` via the standard win/loss snippet; sonnet-5 was Red).
Avg final units: opponent (Blue/ldang__nessy) ~2.56, us (Red) ~27.18. Same
overwhelming-dominance pattern as every previous round in this file — 5
opponent names, 5 total sweeps.

### What I did this round
1. Confirmed `robot.py` is unchanged from the version described in the
   Round 4 section above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). No drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~0.95s wall clock, no
   exceptions) and `--seed 42` (grepped output for
   error/exception/traceback — none found).
3. **Re-examined the movement/pathing "TODO: real BFS pathfinding" item
   from previous rounds' notes and concluded it's likely not worth
   pursuing**: `Direction` only has 4 values (North/South/East/West — see
   `logic/lang-runners/python/stdlib/rumblelib.py`), and the existing
   sidestep fallback in `_first_free_dir` already tries `direction`,
   `direction.rotate_cw`, `direction.rotate_ccw`, and `direction.opposite`
   as its dir list going into `robot()`'s fallback branch (3 dirs) plus the
   direct `direction` attempt beforehand — i.e. **all 4 possible adjacent
   moves are already checked exhaustively every turn before giving up and
   passing**. A real BFS could still help find a better *2+ step* route
   around obstacles instead of greedy 1-step preference, but given we're
   already winning with a >10x final-unit-count margin every round, and
   nobody has been able to show a robust A/B improvement from tuning
   *any* aspect of this bot in 4+ attempts across previous rounds (see
   Round 2/3/4 sections above), I did not implement this — flagging it as
   probably low-value/deprioritize unless a future teammate specifically
   observes units getting stuck via `debug.inspect`/`run web` traces.
4. Re-ran the standard `robot.py` vs `robot_v1_baseline.py` self-play A/B
   (new-as-Blue) over seeds 1-12: **7 wins / 4 losses / 1 tie** — consistent
   with every previous round's finding of a modest (~55-65%) but real edge
   over the round-0 baseline. No regression.
5. **No code changes made this round.** Same reasoning as rounds 2-4: the
   bot is sweeping 250/250 against every opponent name we've seen so far,
   with an ever-growing final-unit-count margin, and no experiment run
   across 4+ rounds of trying (weight tuning, this round's pathing
   analysis) has found a clear, low-risk improvement worth risking a
   regression for. Validation-only round.

### Suggested next steps for future teammates
- Standing advice unchanged: check `/logs/rounds/N/results.json` +
  final-unit-count margins FIRST thing next round. Given 5 consecutive
  250/250 sweeps against 5 different-named opponents now, this matchup
  looks structurally lopsided (possibly these are all weak/starter-level
  bots from the opponent's side) — keep prioritizing low-risk validation
  over large rewrites unless/until an opponent actually contests unit
  count.
- The "is BFS pathfinding worth it" question can probably be marked
  low-priority/closed unless someone has concrete evidence (via `run web`
  + `debug.inspect`) of units actually getting stuck for multiple turns in
  a real match log — the *single-step* exhaustiveness analysis above
  suggests the theoretical failure mode (needing to look 2+ steps ahead to
  escape a dead end) is narrow and hasn't been observed to matter in
  practice across 5 rounds of sweeps.
- Weight-constant tuning (`HEALTH_WEIGHT`/`FOCUS_BONUS`/`COORD_WEIGHT`) has
  now been attempted/inconclusive across 4 separate rounds — still
  recommend not re-attempting with small samples; either a large (50+
  seed) one-sitting sweep, or leave it alone.
- `robot_v1_baseline.py` remains the frozen round-0 reference for A/B
  self-play testing — do not delete/modify it.

## Round 6 (this session — starting point was /logs/rounds/1/, will produce /logs/rounds/2/)

**Status check (first thing, per standing advice):** Re-verified
`/logs/rounds/1/results.json` for this session's starting point. Opponent
this series is `ldang__nessy` (same name as documented in the previous
"Round 5" section above — so this is actually round 1 of that same
opponent-name series, not a new opponent). Result: **250/250 sweep for
sonnet-5** again (sonnet-5 was Blue this time; `Blue wins 250, Red wins 0,
ties 0` via the standard win/loss snippet). Avg final units: us (Blue)
~27.29, opponent (Red) ~2.64. Sixth consecutive total sweep documented in
this file (across 5 differently-named opponent identities), with a
consistently huge (~10x) final-unit-count margin every time.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in the
   Round 4/5 sections above (per-unit soft targeting + opportunistic
   adjacent-attack + `direction_to` movement w/ sidestep fallback +
   spawn-tile-escape when no enemies visible). No drift.
2. Sanity-checked it still runs clean and fast (`./rumblebot run term
   --results-only robot.py robot.py`, ~0.75-1.0s wall-clock, no
   exceptions, real combat happens both ways).
3. **Tried a new idea not attempted in previous rounds: "overkill
   avoidance"** — added a per-turn `assigned_attackers` counter (reset in
   `init_turn`) that tracks how many of our units have already picked a
   given enemy as their personal movement target *this turn*, and added a
   penalty term to `_pick_personal_target`'s scoring
   (`max(0, assigned_attackers.get(e.id,0) - e.health) * OVERKILL_WEIGHT`)
   so that once "enough" units are already converging on a target to kill
   it, additional units get nudged toward other enemies instead of all
   piling onto the same one. Rationale: avoids wasting movement/turns
   having 4+ units all beeline for the same already-doomed enemy while
   other enemies go completely unengaged.
   - Implemented as a standalone variant (not committed to `robot.py`) at
     `/tmp/variants/robot_overkill.py` (this is in `/tmp` so it will NOT
     survive to next round — if a future teammate wants to pick this idea
     back up, the diff is fully described here and is small/mechanical to
     reproduce; see the `python3` heredoc pattern used to generate it,
     preserved below for convenience).
   - A/B tested vs the current `robot.py` (renamed `robot_baseline.py` in
     the same temp dir) over 36 total self-play games (seeds 1-24 with
     overkill-as-Blue, seeds 1-12 again with sides swapped
     overkill-as-Red): **combined record was 16 wins / 20 losses / 0 ties
     for the overkill variant** — i.e. it was *not* an improvement, if
     anything a small regression (within plausible noise, but no
     supporting signal either way). Given this, **did NOT adopt the
     change** — left `robot.py` completely unchanged this round.
   - Plausible explanation for why it didn't help: the existing
     `HEALTH_WEIGHT` + `FOCUS_BONUS`/`COORD_WEIGHT` scoring already
     naturally spreads units somewhat (health term makes an
     already-heavily-targeted, now-very-low-health enemy *more* attractive
     up until it's about to die, not less, since low health enemies score
     well specifically because they're easy kills) — so the extra explicit
     overkill penalty was probably fighting against a signal that was
     already roughly self-correcting, and instead sometimes pulled a unit
     away from a target it could have helped kill *this turn* in favor of
     a farther one it wouldn't reach for several turns, net negative.
4. **No code changes made this round.** Same reasoning as several previous
   rounds: dominant sweep record, no experiment (this round's overkill
   idea, or previous rounds' weight sweeps / pathing analysis) has found a
   robust improvement, so validation-only is the lowest-risk choice.

### Reproducing this round's overkill-avoidance experiment (if a future
teammate wants to revisit it with a bigger sample or a smaller
`OVERKILL_WEIGHT`)
```python
# Apply on top of a copy of robot.py:
# 1. Add global: assigned_attackers: Dict[str, int] = {}
# 2. Add constant: OVERKILL_WEIGHT = 1.2  (this round's untuned guess --
#    worth trying smaller values like 0.3-0.5 since 1.2 may have been too
#    aggressive at pulling units off nearly-dead targets)
# 3. In init_turn, add `assigned_attackers.clear()` near the top (after
#    getting `global focus_target_id`).
# 4. In _pick_personal_target's `score()` closure, add:
#      overkill = max(0, assigned_attackers.get(e.id, 0) - e.health)
#      s += overkill * OVERKILL_WEIGHT
#    then change the final `return min(enemies, key=score)` to assign to
#    `chosen`, increment `assigned_attackers[chosen.id]`, and return
#    `chosen`.
```
36-seed A/B result this round: 16-20-0 (variant lost slightly). Try
OVERKILL_WEIGHT in the 0.2-0.5 range and/or a much larger sample (50+
seeds) if revisiting — this round's sample is still on the small side per
the standing "don't trust <30-seed self-play deltas" caution from earlier
rounds.

### Suggested next steps for future teammates
- Standing advice unchanged (6th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round. Opponent is still `ldang__nessy` as of this writing, and has
  now lost 500/500 games (250 in the previous session + 250 this session)
  by an ~10x unit-count margin both times, with zero sign of adapting.
  Prioritize low-risk validation over large rewrites unless this changes.
- Ideas tried and found inconclusive/negative so far (do not re-attempt
  with small samples, or only with much larger samples): weight-constant
  tuning (`HEALTH_WEIGHT`/`FOCUS_BONUS`/`COORD_WEIGHT`, 4+ rounds now),
  BFS pathfinding (analyzed but not implemented, judged low-value since
  the 4-direction sidestep fallback is already exhaustive for single-step
  lookahead), and now overkill-avoidance targeting (this round, mild
  negative at 36 seeds).
- Genuinely still-untried ideas: multi-step lookahead pathing (2-3 moves
  ahead, not just 1-step sidestep) for escaping dead-ends near the map's
  wall corners; explicit "retreat when badly outnumbered locally" logic
  for individual low-health units (currently every unit always advances/
  attacks regardless of local odds — hasn't mattered yet since opponents
  have been weak, but could matter against a genuinely competitive
  opponent).
- `robot_v1_baseline.py` remains the frozen round-0 reference for A/B
  self-play testing — do not delete/modify it. Confirmed still gives
  `robot.py` its usual modest (~55-65%) edge in this round's spot-check
  (5-3-0 over seeds 25-32).

## Round 7 (this session — starting point was /logs/rounds/0/, will produce /logs/rounds/1/)

**Status check (first thing, per standing advice):** Re-verified
`/logs/rounds/0/results.json` for this session's starting point. Opponent
this series is `ldang__nemo` (yet another new opponent name — 6th
different name across the rounds documented in this file). Result:
**250/250 sweep for sonnet-5** again (sonnet-5 was Red; `Blue wins 0, Red
wins 250, ties 0` via the standard win/loss snippet). Avg final units:
opponent (Blue/ldang__nemo) ~2.51, us (Red) ~29.34. Seventh consecutive
total sweep documented in this file (across 6 differently-named opponent
identities, all crushed by ~10x+ final-unit-count margins). Checked all 250
`sim_*.txt` files for any error/exception/traceback/panic strings — zero
found, confirming the bot ran cleanly for the entire series.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in the
   Round 4-6 sections above (per-unit soft targeting blending own-distance
   + target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). No drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~0.75s wall-clock, no exceptions,
   real combat happens — final state e.g. `Health 15 13 Units 5 4`).
3. Re-ran the standard `robot.py` vs `robot_v1_baseline.py` self-play A/B
   in BOTH directions to double check side-independence one more time:
   - new-as-Red vs baseline-as-Blue, seeds 1-12: **7 wins / 4 losses / 1
     tie**
   - new-as-Red vs baseline-as-Blue, seeds 13-24: **10 wins / 2 losses / 0
     ties**
   Combined: 17-6-1 over 24 games (~71%), consistent with (and maybe even
   a bit stronger than) the ~55-65% edge reported in previous rounds' notes
   — still a real, reproducible, side-independent edge over the round-0
   baseline, no regression.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2, 3, 4, 5, 7 in this file's numbering): the bot has now swept
   7 consecutive rounds (250/250 each) against 6 different opponent names,
   with a consistently huge (~10x+) final-unit-count margin every single
   time, zero runtime errors across 250 simulated games, and no experiment
   attempted in any previous round (weight-constant tuning across 4+
   rounds, overkill-avoidance targeting, BFS-pathing analysis) has found a
   robust, low-risk improvement worth committing. Given this extremely
   strong and stable track record, I prioritized validation over risking a
   regression this round too.

### Suggested next steps for future teammates
- Standing advice unchanged (7th time writing something like this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. If the current/next opponent is
  still getting swept ~250-0 by a ~10x+ unit-count margin, there is very
  little upside and real downside risk to large rewrites — keep doing
  cheap validation (self-play A/B vs `robot_v1_baseline.py`, error-string
  grep across `sim_*.txt`) and only invest heavily in new strategy ideas
  if an opponent actually starts contesting unit count.
- Ideas tried and found inconclusive/negative across multiple past rounds
  (do not re-attempt with small samples; either commit to 50+ seed
  one-sitting sweeps, or leave alone): weight-constant tuning
  (`HEALTH_WEIGHT`/`FOCUS_BONUS`/`COORD_WEIGHT`), overkill-avoidance
  targeting (round 6, mild negative at 36 seeds), BFS/multi-step
  pathfinding (analyzed multiple times, judged low-value given the
  4-direction single-step sidestep fallback is already exhaustive and
  units haven't been observed getting stuck in any reviewed match log).
- Genuinely still-untried ideas (unchanged from round 5/6 notes):
  multi-step (2-3 move) lookahead pathing for escaping dead-ends near the
  map's wall corners; explicit "retreat when badly outnumbered locally"
  logic for individual low-health units. Neither has been necessary yet
  since every opponent seen so far (7 rounds, 6 names) has been thoroughly
  passive/weak relative to us, but could matter if a genuinely competitive
  opponent ever shows up.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent, reproducible, side-independent edge (this round: 17-6-1
  combined over 24 games across both sides).

## Round 8 (this session — starting point was /logs/rounds/1/, will produce /logs/rounds/2/)

**Status check (first thing, per standing advice, 8th time):** Re-verified
`/logs/rounds/1/results.json` for this session's starting point. Opponent
this series is `ldang__nemo` (same name as round 7's notes above — this is
round 1 of that same opponent-name series). Result: **250/250 sweep for
sonnet-5 again** (sonnet-5 was Red; `Blue wins 0, Red wins 250, ties 0` via
the standard win/loss snippet). Avg final units: opponent (Blue) ~2.42, us
(Red) ~29.2. Eighth consecutive total sweep documented in this file (across
6 differently-named opponent identities). Zero error/exception/traceback/
panic strings found across all 250 `sim_*.txt` files.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-7 above (per-unit soft targeting + opportunistic
   adjacent-attack + `direction_to` movement w/ sidestep fallback +
   spawn-tile-escape when no enemies visible). No drift, no uncommitted
   changes (`git status --short` clean at session start).
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~0.85s wall-clock, no exceptions,
   real combat, final state e.g. `Health 20 18 Units 4 4` — a tie in this
   particular mirror-vs-self match, expected since it's the exact same
   code on both sides).
3. Re-ran the standard `robot.py` vs `robot_v1_baseline.py` self-play A/B
   (new-as-Blue) over seeds 1-12: **7 wins / 4 losses / 1 tie** —
   consistent with every previous round's ~55-70% edge over the round-0
   baseline. No regression.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-7 in this numbering): 8 consecutive 250/250 sweeps across 6
   different opponent names, consistently huge (~10x+) final-unit-count
   margins, zero runtime errors ever observed, and every previous attempt
   at finding a robust improvement (weight-constant tuning across 4+
   rounds, overkill-avoidance targeting in round 6, BFS-pathing analysis
   in round 5) has come back inconclusive or mildly negative. Validation-
   only round again — no reason to introduce regression risk into a
   matchup we're winning this decisively.

### Suggested next steps for future teammates
- Standing advice unchanged (8th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Keep doing cheap validation
  (self-play A/B vs `robot_v1_baseline.py`, error-string grep across
  `sim_*.txt`) and only invest heavily in new strategy ideas if an
  opponent actually starts contesting unit count — that has not happened
  even once across 8 rounds / 6 opponent names so far.
- Ideas tried and found inconclusive/negative across multiple past rounds
  (do not re-attempt with small samples; either commit to 50+ seed
  one-sitting sweeps, or leave alone): weight-constant tuning
  (`HEALTH_WEIGHT`/`FOCUS_BONUS`/`COORD_WEIGHT`), overkill-avoidance
  targeting (round 6), BFS/multi-step pathfinding (analyzed multiple
  times, judged low-value).
- Genuinely still-untried ideas (unchanged from earlier rounds): multi-step
  (2-3 move) lookahead pathing for escaping dead-ends near the map's wall
  corners; explicit "retreat when badly outnumbered locally" logic for
  individual low-health units. Neither has been necessary yet since every
  opponent seen so far has been thoroughly passive/weak relative to us.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent edge (this round: 7-4-1 over seeds 1-12).

## Round 9 (this session — starting point was /logs/rounds/0/, will produce /logs/rounds/1/)

**Status check (first thing, per standing advice, 9th time):** Re-verified
`/logs/rounds/0/results.json` for this session's starting point. Opponent
this series is `navster8__bash-brothers` (7th differently-named opponent
across the rounds documented in this file). Result: **250/250 sweep for
sonnet-5** (sonnet-5 was Blue; `Blue wins 250, Red wins 0, ties 0` via the
standard win/loss snippet). Avg final units: us (Blue) ~28.86, opponent
(Red) ~2.40. Ninth consecutive total sweep documented in this file (across
7 differently-named opponent identities, every single one crushed by
~10x+ final-unit-count margins). Grepped all 250 `sim_*.txt` for
`raceback|xception|panic` — zero hits, confirming clean execution across
the entire series.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-8 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). `git status --short` was clean at session start —
   no drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~0.7s wall-clock, no exceptions,
   real combat: `Health 27 17 Units 7 4`).
3. Re-ran the standard `robot.py` vs `robot_v1_baseline.py` self-play A/B
   (new-as-Blue) over seeds 1-12: **7 wins / 4 losses / 1 tie** — same
   ~55-65% edge over the round-0 baseline reported consistently across
   every previous round. No regression.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-8 in this numbering): 9 consecutive 250/250 sweeps across 7
   different opponent names, consistently huge (~10x+) final-unit-count
   margins, zero runtime errors ever observed across ~2000+ simulated
   games total, and every previous attempt at finding a robust improvement
   (weight-constant tuning across 4+ rounds, overkill-avoidance targeting
   in round 6, BFS-pathing analysis in round 5) has come back inconclusive
   or mildly negative. Validation-only round again.

### Suggested next steps for future teammates
- Standing advice unchanged (9th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Keep doing cheap validation
  (self-play A/B vs `robot_v1_baseline.py`, error-string grep across
  `sim_*.txt`) and only invest heavily in new strategy ideas if an
  opponent actually starts contesting unit count — that has not happened
  even once across 9 rounds / 7 opponent names so far.
- If this pattern *ever* breaks (opponent wins units, or final-unit-count
  margin shrinks well below ~5x), that's the trigger to revisit the
  still-untried ideas list: multi-step (2-3 move) lookahead pathing for
  escaping dead-ends near the map's wall corners; explicit "retreat when
  badly outnumbered locally" logic for individual low-health units. Both
  remain untried since no opponent so far has been strong enough to make
  them matter.
- Ideas tried and found inconclusive/negative across multiple past rounds
  (do not re-attempt with small samples; either commit to 50+ seed
  one-sitting sweeps, or leave alone): weight-constant tuning
  (`HEALTH_WEIGHT`/`FOCUS_BONUS`/`COORD_WEIGHT`), overkill-avoidance
  targeting (round 6), BFS/multi-step pathfinding (analyzed multiple
  times, judged low-value).
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent edge (this round: 7-4-1 over seeds 1-12).

## Round 10 (this session — starting point was /logs/rounds/1/, will produce /logs/rounds/2/)

**Status check (first thing, per standing advice, 10th time):** Re-verified
`/logs/rounds/1/results.json` for this session's starting point. Opponent
this series is `navster8__bash-brothers` (same name as round 9's notes
above — this is round 1 of that same opponent-name series). Result:
**250/250 sweep for sonnet-5** again (sonnet-5 was Blue; `Blue wins 250,
Red wins 0, ties 0` via the standard win/loss snippet). Avg final units: us
(Blue) ~28.37, opponent (Red) ~2.49. Tenth consecutive total sweep
documented in this file (across 7 differently-named opponent identities).
Grepped all 250 `sim_*.txt` for `raceback|xception|panic` — zero hits.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-9 above. `git status --short` clean at session start — no
   drift.
2. Sanity-checked it still runs clean and fast (`./rumblebot run term
   --results-only robot.py robot.py`, ~0.7-0.9s wall-clock, no exceptions,
   real combat).
3. **Ran a much bigger `HEALTH_WEIGHT` sweep than previous rounds managed**,
   using a new parallelized A/B harness (`/tmp/run_ab.py`, `/tmp/run_ab2.py`
   — NOT persisted to `/workspace`, recreate if needed; pattern: Python
   `concurrent.futures.ThreadPoolExecutor` with `max_workers=16` to launch
   many `./rumblebot run term` subprocesses at once, since this machine has
   64 cores and each individual run is single-threaded and CPU-light — this
   cut wall-clock roughly 10x vs sequential loops used in earlier rounds'
   notes, e.g. 121 seeds in ~11s instead of ~110s). Recommend future
   teammates reuse this pattern for any large-sample self-play testing —
   it's the single most useful tooling addition from this round.
   Tested `HEALTH_WEIGHT=1.0` vs the checked-in default (`0.6`) over a
   combined **241 games** (seeds 1-60 both directions + seeds 100-220
   one direction): final combined tally **112 wins / 109 wins / 20 ties**
   (HW1.0 / HW0.6 / tie) — i.e. **~50.7% win rate, a dead coin flip**. This
   finally gives a large-sample, low-noise answer to the question raised
   in rounds 2/3/4/6's notes ("is HEALTH_WEIGHT=1.0 actually better, or was
   the small-sample mild-positive trend just noise?") — **it was noise**.
   Confirmed: do not change `HEALTH_WEIGHT` from `0.6`. This closes out the
   multi-round open question on weight tuning with a definitive negative
   result rather than another inconclusive small sample.
4. **No code changes made this round.** 10 consecutive 250/250 sweeps
   across 7 different opponent names, still no experiment (weight tuning
   now tested at high sample size and confirmed no effect;
   overkill-avoidance in round 6; BFS-pathing analysis in round 5) has
   found a robust improvement. Validation-only round again, but with a
   more conclusive weight-tuning result than previous attempts thanks to
   the new parallelized harness.

### Suggested next steps for future teammates
- **Reuse the parallelized A/B harness** (recreate `/tmp/run_ab.py`'s
  `ThreadPoolExecutor`-based pattern shown above if it's not on disk
  anymore) for any future large-sample self-play testing — it's ~10x
  faster wall-clock than sequential loops on this 64-core machine, letting
  you get 200+ game samples in under 15s instead of needing to split work
  across many separate `bash` tool calls.
- `HEALTH_WEIGHT` tuning can now be considered **closed/settled** (241-game
  sample, ~50.7%, i.e. no effect) — no need for future teammates to
  re-litigate this specific constant. `FOCUS_BONUS`/`COORD_WEIGHT` have
  only been tested at small samples in earlier rounds though, so those
  remain technically open if someone wants to use the new harness to
  settle them too (low priority, same reasoning as always: no opponent
  seen so far has been strong enough for these marginal gains to matter).
- Standing advice unchanged (10th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round. If the current opponent (`navster8__bash-brothers` as of
  this writing) or any future one starts contesting unit count seriously,
  that's the trigger to revisit genuinely untried ideas: multi-step (2-3
  move) lookahead pathing for escaping dead-ends; explicit "retreat when
  badly outnumbered locally" logic for individual low-health units.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. `robot.py` still beats it
  cleanly in quick spot-checks this round (e.g. `Health 15 23 Units 3 6`
  as Red vs baseline as Blue).

## Round 11 (this session — starting point was /logs/rounds/0/, will produce /logs/rounds/1/)

**Status check (first thing, per standing advice, 11th time):** Re-verified
`/logs/rounds/0/results.json` for this session's starting point. Opponent
this series is `aaoutkine__dark-knight` (8th differently-named opponent
across the rounds documented in this file: anton__anton3000,
happysquid__test, anton__wallifier, ldang__nessy, ldang__nemo,
navster8__bash-brothers, and now aaoutkine__dark-knight). Result:
**250/250 sweep for sonnet-5** (sonnet-5 was Red; `Blue wins 0, Red wins
250, ties 0` via the standard win/loss snippet). Avg final units: opponent
(Blue) ~3.55, us (Red) ~26.19. Eleventh consecutive total sweep documented
in this file. Note: opponent's avg final units (~3.55) is a bit *higher*
than the two previous rounds vs `navster8__bash-brothers` (~2.40, ~2.49),
which *might* be a very slight uptick in opponent strength, but it's still
an overwhelming ~7.4x unit-count sweep, nowhere close to competitive.
Grepped all 250 `sim_*.txt` for `raceback|xception|panic` — zero hits,
confirming clean execution.

Also noticed (from `git log --oneline`) that commit messages reference a
`Rung N/58 (opponent, elo #M)` ladder system — e.g. `navster8__bash-brothers`
was "Rung 6/58, elo #53". This implies we're climbing a fixed ladder of 58
opponents from weakest to strongest as we keep winning (rung number goes
up, elo rank number goes down = climbing toward stronger competition). This
round's opponent (`aaoutkine__dark-knight`) is presumably Rung 7 or 8 in
that same ladder. Worth flagging for future teammates: as the ladder
climbs, expect opponents to *eventually* get harder — the still-untried
ideas list below (multi-step pathing, retreat logic) may become relevant
sooner rather than later. Keep an eye on avg-final-units trends round over
round as an early warning signal (this round's 3.55 avg for the opponent is
the highest opponent average recorded in this file's history so far, though
still trivial to beat).

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-10 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). `git status --short` clean at session start — no
   drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~1.0-1.2s wall-clock incl. ~90ms
   setup, no exceptions, real combat) and vs `robot_v1_baseline.py`
   (~0.55s, no exceptions).
3. Re-ran the parallelized self-play A/B vs `robot_v1_baseline.py`
   (`robot.py` as Blue) using the `ThreadPoolExecutor`-based harness
   documented in Round 10's notes, over seeds 1-40: **26 wins / 12 losses /
   2 ties** (~65-68% win rate) — consistent with every previous round's
   ~55-70% edge over the round-0 baseline, confirming no regression at a
   larger (40-seed) sample size than most previous single-round checks.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-10 in this numbering): 11 consecutive 250/250 sweeps across 8
   different opponent names, still overwhelming (~7x+) final-unit-count
   margins even in this round's slightly-less-lopsided result, zero
   runtime errors ever observed across ~2500+ simulated games total, and
   no experiment in any previous round (weight-constant tuning — now
   settled at large sample as no-effect per Round 10 — overkill-avoidance
   targeting, BFS-pathing analysis) has found a robust improvement.
   Validation-only round again.

### Suggested next steps for future teammates
- Standing advice (11th time writing this, still true): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes.
- **New this round**: also glance at `git log --oneline` for the
  `Rung N/58 (opponent, elo #M)` pattern in recent commit messages to get a
  sense of ladder position/trajectory — rung numbers should keep climbing
  (and elo-rank numbers dropping) as long as we keep winning. If a rung
  number ever *doesn't* advance, or the avg-opponent-final-units trend
  (tracked round-over-round in this file) keeps climbing rather than
  staying flat/low, that's a concrete signal the matchups are getting
  harder — time to seriously invest in the still-untried ideas list below
  instead of validation-only rounds.
- Genuinely still-untried ideas (unchanged from several previous rounds):
  multi-step (2-3 move) lookahead pathing for escaping dead-ends near the
  map's wall corners; explicit "retreat when badly outnumbered locally"
  logic for individual low-health units. Still not necessary yet (11
  rounds, 8 opponent names, all crushed), but keep this list ready in case
  the ladder trend noted above starts to matter.
- Settled/closed questions (do not re-litigate without a very large new
  sample): `HEALTH_WEIGHT`/`FOCUS_BONUS`/`COORD_WEIGHT` tuning (settled
  no-effect at 241 games in Round 10), overkill-avoidance targeting
  (Round 6, mild negative at 36 games), BFS/multi-step pathfinding
  (analyzed, judged low-value given exhaustive single-step sidestep
  fallback already in place).
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent edge (this round: 26-12-2 over 40 seeds, the largest sample
  yet for a single-round check).

## Round 12 (this session — starting point was /logs/rounds/1/, will produce /logs/rounds/2/)

**Status check (first thing, per standing advice, 12th time):** Re-verified
both `/logs/rounds/0/results.json` and `/logs/rounds/1/results.json` for
this session (both already present at session start). Opponent this series
is `aaoutkine__dark-knight` (same name as the previous "Round 11" section
above — this is round 1 of that opponent-name series, matching git log
`Rung 7/58 (aaoutkine__dark-knight, elo #52) — Round 1 Update`). Result:
**250/250 sweep for sonnet-5 in BOTH logged rounds** (`Blue wins 0, Red
wins 250, ties 0` in round 1 via the standard win/loss snippet; sonnet-5
was Red both times). Avg final units in round 1: opponent (Blue) ~3.51, us
(Red) ~26.1 — consistent with round 0's ~3.55/~26.19 reported previously.
Twelfth consecutive total sweep documented in this file (across 8
differently-named opponent identities). `git status --short` was clean
(no drift in `robot.py`) at session start.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-11 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). No drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` and `... robot.py
   robot_v1_baseline.py` (~0.8-1.0s wall-clock each, no exceptions, real
   combat both times).
3. **Added a persistent, documented A/B testing harness**:
   `tools/ab_test.py` (new file, committed to `/workspace` this round so it
   survives between sessions — previous rounds' notes mention recreating a
   similar `ThreadPoolExecutor`-based script in `/tmp` each time, which is
   lost every session). Usage:
   ```
   python3 tools/ab_test.py bot_a.py bot_b.py --seeds 1-60 [--swap] [--workers 16]
   ```
   Runs many `./rumblebot run term --results-only --seed N ...` invocations
   in parallel via a thread pool (this machine is multi-core and each
   individual run is single-threaded/CPU-light, so this is ~10x faster
   wall-clock than a sequential loop — e.g. 60 seeds finishes in a few
   seconds instead of ~50s). `--swap` also runs the reverse Blue/Red
   assignment to check for side bias in one command. **Future teammates:
   use this instead of recreating an equivalent script in `/tmp` each
   round.**
4. Used the new harness to re-litigate the two remaining "technically
   open" weight constants from Round 10's notes (`FOCUS_BONUS` and
   `COORD_WEIGHT` — `HEALTH_WEIGHT` was already settled at large sample in
   Round 10) with bigger, side-balanced samples than any previous round
   managed:
   - `FOCUS_BONUS=4.0` (vs default `2.0`) over 150 total games split
     across both sides (seeds 1-50 and 51-100 as Blue, seeds 1-50 as Red):
     **67 wins / 70 wins / 13 ties** for the variant vs default — a dead
     coin flip, no effect.
   - `COORD_WEIGHT=0.3` (vs default `0.15`) over 210 total games split
     across both sides (seeds 1-60 and 61-150 as Blue, seeds 1-60 as Red):
     **103 wins / 91 wins / 16 ties** for the variant — a slightly higher
     raw win count, but well within plausible noise at this sample size (a
     first small batch, seeds 1-60 both sides, looked like a promising
     ~56% edge before the larger seeds 61-150 batch reverted it back
     toward even; classic small-sample-then-regression-to-mean pattern,
     the same trap earlier rounds' notes specifically warned about).
   - **Conclusion: both constants remain settled/no-effect, consistent
     with `HEALTH_WEIGHT`'s Round-10 finding.** All three tunable weight
     constants in `robot.py` (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
     `COORD_WEIGHT`) can now be considered closed questions with
     reasonably large-sample evidence behind each — recommend NOT
     re-litigating any of them again without a very good reason (e.g. a
     fundamentally different targeting algorithm, not just retuning these
     three numbers).
5. Re-ran the standard `robot.py` vs `robot_v1_baseline.py` self-play A/B
   using the new harness (both sides, seeds 1-30, `--swap`): new-as-Blue
   **19 wins / 9 losses / 2 ties**; new-as-Red (swapped) **17 wins / 12
   losses / 1 tie**. Consistent with every previous round's ~55-70% edge
   over the round-0 baseline. No regression.
6. **No changes to `robot.py` this round.** Reasoning: 12 consecutive
   250/250 sweeps across 8 different opponent names, still overwhelming
   (~7x+) final-unit-count margins, zero runtime errors ever observed
   across ~2750+ simulated games total (including this round's ~600+
   additional self-play games run for the weight-constant re-litigation),
   and this round's larger-sample re-test of the two previously-"open"
   weight constants closes them out as no-effect too. The only durable
   artifact from this round is the new `tools/ab_test.py` harness.

### Suggested next steps for future teammates
- Standing advice unchanged (12th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes.
- **Use `tools/ab_test.py`** (now committed, not just a `/tmp` scratch
  script) for any future self-play A/B testing — see its docstring/usage
  above. Don't recreate an equivalent script from scratch.
- **All three tunable weight constants are now settled/closed** at
  reasonably large sample sizes across multiple rounds:
  `HEALTH_WEIGHT` (Round 10, 241 games, ~50.7%), `FOCUS_BONUS` (this
  round, 150 games, ~47.9% i.e. no effect), `COORD_WEIGHT` (this round,
  210 games, ~52.5%, i.e. no effect once sample is large enough — note the
  first 60-game batch alone looked like a false-positive ~56% edge, a
  cautionary tale about trusting <100-game samples for these small
  numeric tweaks). Do not re-litigate without a fundamentally different
  idea, not just a different number for one of these three.
- Genuinely still-untried ideas (unchanged from several previous rounds):
  multi-step (2-3 move) lookahead pathing for escaping dead-ends near the
  map's wall corners (still judged low-value per Round 5's analysis — the
  4-direction single-step sidestep fallback is already exhaustive and
  units haven't been observed getting stuck in any reviewed match log);
  explicit "retreat when badly outnumbered locally" logic for individual
  low-health units (still untried — no opponent so far has been strong
  enough to make this matter, and it carries real regression risk since
  it would work against the current bot's "always attack if adjacent, no
  matter what" philosophy that has been winning decisively).
- Keep an eye on the `Rung N/58 (opponent, elo #M)` pattern in `git log
  --oneline` commit messages and the avg-opponent-final-units trend
  tracked round-over-round in this file (currently ~2.4-3.6 range across
  the last several rounds, essentially flat/low) as an early-warning
  signal for when the ladder starts getting genuinely harder — that's the
  trigger to invest heavily in the untried ideas above instead of
  validation-only rounds.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent, reproducible, side-independent edge (this round: 19-9-2 and
  17-12-1 across both sides, seeds 1-30).

## Round 13 (this session — starting point was /logs/rounds/0/, will produce /logs/rounds/1/)

**Status check (first thing, per standing advice, 13th time):** Re-verified
`/logs/rounds/0/results.json` for this session's starting point. Opponent
this series is `mountain__neuralbot1-1h` (9th differently-named opponent
across the rounds documented in this file). Result: **250/250 sweep for
sonnet-5** (sonnet-5 was Red; `Blue wins 0, Red wins 250, ties 0` via the
standard win/loss snippet from earlier sections). Avg final units: opponent
(Blue) ~3.35, us (Red) ~28.78 (min/max blue units across all 250 games: 0
to 7). Thirteenth consecutive total sweep documented in this file (across
9 differently-named opponent identities). Grepped all 250 `sim_*.txt` for
`raceback|xception|panic` — zero hits, confirming clean execution.

Latest `git log --oneline` shows we're at "Rung 7/58 (aaoutkine__dark-knight,
elo #52)" as of the last committed round notes — this round's opponent name
(`mountain__neuralbot1-1h`) suggests we've since climbed to a new rung
(presumably Rung 8/58), consistent with the standing observation that we
keep climbing the ladder as long as we keep sweeping.

### What I did this round
1. Confirmed `robot.py` is unchanged from the version described in rounds
   4-12 above (per-unit soft targeting blending own-distance + target
   health + team coordination-distance + focus-bonus; opportunistic
   always-attack-if-adjacent, weakest-first; `direction_to` movement w/
   full 4-direction sidestep fallback; spawn-tile-escape when no enemies
   visible). `git status --short` clean at session start — no drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~1.0s wall-clock incl. setup, no
   exceptions, real combat: `Health 2 29 Units 1 8`).
3. Used the persistent `tools/ab_test.py` harness (added in Round 12) to
   re-confirm `robot.py`'s edge over `robot_v1_baseline.py` over 30 seeds,
   both sides (`--swap`): new-as-Blue **19 wins / 9 losses / 2 ties**;
   new-as-Red (swapped) **12 wins / 17 losses / 1 tie**. Consistent with
   previous rounds' ~55-70% edge in one direction; the swapped direction
   this particular 30-seed sample skewed the other way, which is within
   the range of side/seed noise documented in earlier rounds (e.g. Round
   12's larger-sample re-tests showed these small-sample deltas often
   regress toward even) — no cause for concern, no regression evidence.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-12 in this numbering): 13 consecutive 250/250 sweeps across 9
   different opponent names, still overwhelming (~8.6x) final-unit-count
   margin this round, zero runtime errors ever observed across ~3000+
   simulated games total, and every tunable knob in the bot (all 3 weight
   constants, overkill-avoidance targeting, BFS-pathing) has already been
   explored across rounds 2-12 with no robust improvement found. Given
   this extremely strong and stable track record, validation-only remains
   the correct call.

### Suggested next steps for future teammates
- Standing advice unchanged (13th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Use `tools/ab_test.py` (see Round 12
  notes for usage) for any self-play A/B testing rather than recreating a
  script from scratch.
- All three tunable weight constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`) remain settled/closed from Rounds 10 & 12's large-sample
  tests (all ~50% i.e. no effect) — do not re-litigate without a
  fundamentally different targeting idea.
- Genuinely still-untried ideas (unchanged across many rounds): multi-step
  (2-3 move) lookahead pathing for escaping dead-ends near the map's wall
  corners (still low-value per Round 5's analysis); explicit "retreat when
  badly outnumbered locally" logic for individual low-health units (still
  untried, carries real regression risk against the current "always
  attack if adjacent" philosophy that keeps winning decisively).
- Keep watching the `Rung N/58 (opponent, elo #M)` pattern in `git log
  --oneline` and the avg-opponent-final-units trend (flat/low, ~2.4-3.55
  across rounds 5-13) as the early-warning signal for when the ladder
  actually gets harder. This round's opponent (`mountain__neuralbot1-1h`)
  continues the pattern — no sign of a genuinely competitive opponent yet.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it.

## Round 14 (this session — starting point was /logs/rounds/1/, will produce /logs/rounds/2/)

**Status check (first thing, per standing advice, 14th time):** Re-verified
`/logs/rounds/1/results.json` for this session's starting point. Opponent
this series is `mountain__neuralbot1-1h` (same name as round 13's notes
above — this is round 1 of that opponent-name series, matching git log
`Rung 8/58 (mountain__neuralbot1-1h, elo #51) — Round 1 Update`). Result:
**250/250 sweep for sonnet-5** again (sonnet-5 was Red; `Blue wins 0, Red
wins 250, ties 0` via the standard win/loss snippet). Avg final units:
opponent (Blue) ~3.30, us (Red) ~28.73 — consistent with round 0's ~3.35/
~28.78 reported in round 13's notes. Fourteenth consecutive total sweep
documented in this file (across 9 differently-named opponent identities).
Grepped all 250 `sim_*.txt` for `raceback|xception|panic` — zero hits,
confirming clean execution.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-13 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). `git status --short` clean at session start — no
   drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~1.0s wall-clock incl. setup, no
   exceptions, real combat: `Health 21 6 Units 5 2`).
3. Used the persistent `tools/ab_test.py` harness (from Round 12) to
   re-confirm `robot.py`'s edge over `robot_v1_baseline.py` over 20 seeds
   (new-as-Blue): **13 wins / 5 losses / 2 ties** — consistent with every
   previous round's ~55-70% edge over the round-0 baseline. No regression.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-13 in this numbering): 14 consecutive 250/250 sweeps across 9
   different opponent names, still overwhelming (~8.7x) final-unit-count
   margin this round, zero runtime errors ever observed across ~3250+
   simulated games total, and every tunable knob in the bot (all 3 weight
   constants — settled no-effect at large sample in Rounds 10 & 12 —
   overkill-avoidance targeting — Round 6, mild negative — BFS-pathing —
   judged low-value in Round 5) has already been explored with no robust
   improvement found. Validation-only round again.

### Suggested next steps for future teammates
- Standing advice unchanged (14th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Use `tools/ab_test.py` (see Round 12
  notes for usage) for any self-play A/B testing rather than recreating a
  script from scratch.
- All three tunable weight constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`) remain settled/closed from Rounds 10 & 12's large-sample
  tests (all ~50% i.e. no effect) — do not re-litigate without a
  fundamentally different targeting idea.
- Genuinely still-untried ideas (unchanged across many rounds): multi-step
  (2-3 move) lookahead pathing for escaping dead-ends near the map's wall
  corners (still low-value per Round 5's analysis); explicit "retreat when
  badly outnumbered locally" logic for individual low-health units (still
  untried, carries real regression risk against the current "always
  attack if adjacent" philosophy that keeps winning decisively).
- Keep watching the `Rung N/58 (opponent, elo #M)` pattern in `git log
  --oneline` and the avg-opponent-final-units trend (flat/low, ~2.4-3.55
  across rounds 5-14) as the early-warning signal for when the ladder
  actually gets harder. This round's opponent (`mountain__neuralbot1-1h`)
  continues the pattern — no sign of a genuinely competitive opponent yet.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent edge (this round: 13-5-2 over 20 seeds).

## Round 15 (this session — starting point was /logs/rounds/0/, will produce /logs/rounds/1/)

**Status check (first thing, per standing advice, 15th time):** Re-verified
`/logs/rounds/0/results.json` for this session's starting point. Opponent
this series is `sivecano__clouded-mind` (10th differently-named opponent
across the rounds documented in this file). Result: **250/250 sweep for
sonnet-5** (sonnet-5 was Red; `Blue wins 0, Red wins 250, ties 0` via the
standard win/loss snippet). Avg final units: opponent (Blue) ~4.22
(min 0, max 10), us (Red) ~25.95. Fifteenth consecutive total sweep
documented in this file (across 10 differently-named opponent identities).
Grepped all 250 `sim_*.txt` for `raceback|xception|panic` — zero hits,
confirming clean execution across the entire series.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-14 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). `git status --short` clean at session start — no
   drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~1.1s wall-clock incl. setup, no
   exceptions, real combat: `Health 10 20 Units 2 5`).
3. Re-read the engine's `Action` API one more time
   (`logic/lang-runners/python/stdlib/rumblelib.py`) to double-check
   nothing new is exploitable: confirmed there are still only exactly 3
   action types (`Move`, `Attack`, `Heal`), one per unit per turn, 4
   cardinal directions only — no new mechanics to leverage since the last
   time this was checked (several rounds ago). `Action.heal` remains a
   confirmed no-op in `Normal` game mode (traced in earlier rounds'
   notes) — still not worth adding.
4. Used the persistent `tools/ab_test.py` harness (from Round 12) to
   re-confirm `robot.py`'s edge over `robot_v1_baseline.py` over 30 seeds,
   both sides (`--swap`): new-as-Blue **19 wins / 9 losses / 2 ties**;
   new-as-Red (swapped) **12 wins / 17 losses / 1 tie**. Same pattern as
   several previous rounds (strong edge as Blue in this particular seed
   range, weaker/negative as Red) — this is consistent with prior notes
   that small-sample (~30 seed) per-direction deltas are noisy; the
   *combined* two-direction total (31 wins / 26 losses / 3 ties across 60
   games) is still a modest positive edge (~54%), in line with the
   long-running ~50-70% edge range reported across many rounds. No
   regression evidence.
5. **No code changes made this round.** Same reasoning as most previous
   rounds (2-14 in this numbering): 15 consecutive 250/250 sweeps across
   10 different opponent names, still overwhelming (~6x+) final-unit-count
   margin this round, zero runtime errors ever observed across ~3500+
   simulated games total, and every tunable knob in the bot (all 3 weight
   constants — settled no-effect at large sample in Rounds 10 & 12 —
   overkill-avoidance targeting — Round 6, mild negative — BFS-pathing —
   judged low-value in Round 5) has already been explored with no robust
   improvement found, and the engine's action API offers nothing new to
   exploit. Validation-only round again.

### Suggested next steps for future teammates
- Standing advice unchanged (15th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Use `tools/ab_test.py` (see Round 12
  notes for usage) for any self-play A/B testing rather than recreating a
  script from scratch.
- All three tunable weight constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`) remain settled/closed from Rounds 10 & 12's large-sample
  tests (all ~50% i.e. no effect) — do not re-litigate without a
  fundamentally different targeting idea.
- Genuinely still-untried ideas (unchanged across many rounds): multi-step
  (2-3 move) lookahead pathing for escaping dead-ends near the map's wall
  corners (still low-value per Round 5's analysis); explicit "retreat when
  badly outnumbered locally" logic for individual low-health units (still
  untried, carries real regression risk against the current "always
  attack if adjacent" philosophy that keeps winning decisively).
- The opponent's avg-final-units has bounced around ~2.4-4.2 across rounds
  5-15 with no clear upward trend — still no sign of a genuinely
  competitive opponent on this ladder. Keep watching for a rung where this
  changes (e.g. avg opponent final units climbing above ~10, or opponent
  actually winning some games) as the trigger to invest heavily in the
  untried ideas above instead of validation-only rounds.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it.

## Round 16 (this session — starting point was /logs/rounds/1/, will produce /logs/rounds/2/)

**Status check (first thing, per standing advice, 16th time):** Re-verified
`/logs/rounds/1/results.json` for this session's starting point. Opponent
this series is `sivecano__clouded-mind` (same name as round 15's notes
above — this is round 1 of that same opponent-name series, matching git
log `Rung 9/58 (sivecano__clouded-mind, elo #50) — Round 1 Update`).
Result: **250/250 sweep for sonnet-5** again (sonnet-5 was Red; `Blue wins
0, Red wins 250, ties 0` via the standard win/loss snippet). Avg final
units: opponent (Blue) ~4.24 (min 1, max 10), us (Red) ~25.96 —
consistent with round 0's ~4.22/~25.95 reported in round 15's notes.
Sixteenth consecutive total sweep documented in this file (across 10
differently-named opponent identities). Grepped all 250 `sim_*.txt` for
`raceback|xception|panic` — zero hits, confirming clean execution across
the entire series.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-15 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). `git status --short` clean at session start — no
   drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~1.3s wall-clock incl. setup, no
   exceptions, real combat: `Health 0 28 Units 0 6`).
3. Used the persistent `tools/ab_test.py` harness (from Round 12) to
   re-confirm `robot.py`'s edge over `robot_v1_baseline.py` over 40 seeds,
   both sides (`--swap`): new-as-Blue **26 wins / 12 losses / 2 ties**;
   new-as-Red (swapped) **24 wins / 13 losses / 3 ties** (i.e. baseline
   won 13 as Blue). Combined across both directions: **50 wins / 25
   losses / 5 ties** for `robot.py` (~62.5% win rate) — consistent,
   side-independent, matches the long-running ~55-70% edge over the
   round-0 baseline reported across nearly every previous round. No
   regression.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-15 in this numbering): 16 consecutive 250/250 sweeps across
   10 different opponent names, still overwhelming (~6x+) final-unit-count
   margin this round, zero runtime errors ever observed across ~3750+
   simulated games total, and every tunable knob in the bot (all 3 weight
   constants — settled no-effect at large sample in Rounds 10 & 12 —
   overkill-avoidance targeting — Round 6, mild negative — BFS-pathing —
   judged low-value in Round 5) has already been explored with no robust
   improvement found, and the engine's action API offers nothing new to
   exploit (re-verified in Round 15). Validation-only round again.

### Suggested next steps for future teammates
- Standing advice unchanged (16th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Use `tools/ab_test.py` (see Round 12
  notes for usage) for any self-play A/B testing rather than recreating a
  script from scratch.
- All three tunable weight constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`) remain settled/closed from Rounds 10 & 12's large-sample
  tests (all ~50% i.e. no effect) — do not re-litigate without a
  fundamentally different targeting idea.
- Genuinely still-untried ideas (unchanged across many rounds, ~16 rounds
  running now): multi-step (2-3 move) lookahead pathing for escaping
  dead-ends near the map's wall corners (still low-value per Round 5's
  analysis); explicit "retreat when badly outnumbered locally" logic for
  individual low-health units (still untried, carries real regression
  risk against the current "always attack if adjacent" philosophy that
  keeps winning decisively). Given the ladder (`Rung 9/58` as of this
  writing) has shown zero sign of a genuinely competitive opponent across
  16 rounds and 10 opponent names, these remain low-priority unless the
  avg-opponent-final-units trend (currently bouncing ~2.4-4.24, no clear
  upward trend) or actual win/loss record changes.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent, reproducible, side-independent edge (this round: 50-25-5
  combined across both sides, 40 seeds each direction, 80 games total).

## Round 17 (this session — starting point was /logs/rounds/0/, will produce /logs/rounds/1/)

**Status check (first thing, per standing advice, 17th time):** Re-verified
`/logs/rounds/0/results.json` for this session's starting point. Opponent
this series is `mountain__neuralbot2-6h` (11th differently-named opponent
across the rounds documented in this file — note this is a *different*
name from `mountain__neuralbot1-1h` seen in rounds 13/14, so it's a new
opponent identity, not a continuation). Result: **250/250 sweep for
sonnet-5** (sonnet-5 was Red; `Blue wins 0, Red wins 250, ties 0` via the
standard win/loss snippet). Avg final units: opponent (Blue) ~3.82
(min 0, max 9), us (Red) ~31.81. Seventeenth consecutive total sweep
documented in this file (across 11 differently-named opponent identities).
Grepped all 250 `sim_*.txt` for `raceback|xception|panic` — zero hits,
confirming clean execution across the entire series.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-16 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). `git status --short` clean at session start — no
   drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~0.81s wall-clock incl. setup, no
   exceptions, real combat: `Health 21 16 Units 5 4`) and vs
   `robot_v1_baseline.py` (~1.2s, no exceptions, `Health 37 10 Units 9 3`).
3. Used the persistent `tools/ab_test.py` harness (from Round 12) to
   re-confirm `robot.py`'s edge over `robot_v1_baseline.py` over 40 seeds,
   both sides (`--swap`): new-as-Blue **26 wins / 12 losses / 2 ties**;
   new-as-Red (swapped) **24 wins / 13 losses / 3 ties**. Combined across
   both directions: **50 wins / 25 losses / 5 ties** for `robot.py`
   (~62.5% of decisive games) — consistent, side-independent, matches the
   long-running ~55-70% edge over the round-0 baseline reported across
   nearly every previous round. No regression.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-16 in this numbering): 17 consecutive 250/250 sweeps across
   11 different opponent names, still overwhelming (~8.3x) final-unit-count
   margin this round, zero runtime errors ever observed across ~4000+
   simulated games total, and every tunable knob in the bot (all 3 weight
   constants — settled no-effect at large sample in Rounds 10 & 12 —
   overkill-avoidance targeting — Round 6, mild negative — BFS-pathing —
   judged low-value in Round 5) has already been explored with no robust
   improvement found. Validation-only round again.

### Suggested next steps for future teammates
- Standing advice unchanged (17th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Use `tools/ab_test.py` (see Round 12
  notes for usage) for any self-play A/B testing rather than recreating a
  script from scratch.
- All three tunable weight constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`) remain settled/closed from Rounds 10 & 12's large-sample
  tests (all ~50% i.e. no effect) — do not re-litigate without a
  fundamentally different targeting idea.
- Genuinely still-untried ideas (unchanged across many rounds, ~17 rounds
  running now): multi-step (2-3 move) lookahead pathing for escaping
  dead-ends near the map's wall corners (still low-value per Round 5's
  analysis); explicit "retreat when badly outnumbered locally" logic for
  individual low-health units (still untried, carries real regression
  risk against the current "always attack if adjacent" philosophy that
  keeps winning decisively). Given the ladder has shown zero sign of a
  genuinely competitive opponent across 17 rounds and 11 opponent names,
  these remain low-priority unless the avg-opponent-final-units trend
  (currently bouncing ~2.4-4.24, no clear upward trend) or actual
  win/loss record changes.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent, reproducible, side-independent edge (this round: 50-25-5
  combined across both sides, 40 seeds each direction, 80 games total).

## Round 18 (this session — starting point was /logs/rounds/0/, will produce /logs/rounds/1/... actually both 0 and 1 already existed at session start)

**Status check (first thing, per standing advice, 18th time):** Both
`/logs/rounds/0/results.json` and `/logs/rounds/1/results.json` were
already present at session start (this session picked up right after the
previous teammate's round-17 submission). Opponent this series is
`mountain__neuralbot2-6h` (same name as round 17's notes above — round 0
and round 1 here are both part of that same opponent-name series). Both
rounds: **250/250 sweep for sonnet-5** (round 0: sonnet-5 Red, `Red wins
250`; round 1: sonnet-5 Blue, `Blue wins 250`). Avg final units in round 1:
us (Blue) ~32.37, opponent (Red) ~3.77 — consistent with round 0's
~31.81/~3.82 reported in round 17's notes. Eighteenth consecutive total
sweep documented in this file (across 11 differently-named opponent
identities so far). Grepped all `sim_*.txt` in `/logs/rounds/1/` for
`raceback|xception|panic` — zero hits, confirming clean execution.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-17 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). `git status --short` clean at session start — no
   drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~0.9s wall-clock incl. setup, no
   exceptions, real combat: `Health 15 10 Units 3 2`) and vs
   `robot_v1_baseline.py` (~1.1s, no exceptions, `Health 34 13 Units 8 3`).
3. Used the persistent `tools/ab_test.py` harness (from Round 12) to
   re-confirm `robot.py`'s edge over `robot_v1_baseline.py` over 20 seeds,
   both sides (`--swap`): robot.py-as-Blue **13 wins / 5 losses / 2 ties**;
   robot.py-as-Red (swapped) **13 wins / 6 losses / 1 tie**. Combined
   across both directions: **26 wins / 11 losses / 3 ties** for `robot.py`
   (~70% of decisive games) — consistent, side-independent, matches the
   long-running ~55-70% edge over the round-0 baseline reported across
   nearly every previous round. No regression.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-17 in this numbering): 18 consecutive 250/250 sweeps across
   11 different opponent names, still overwhelming (~8.5x) final-unit-count
   margin this round, zero runtime errors ever observed across ~4250+
   simulated games total, and every tunable knob in the bot (all 3 weight
   constants — settled no-effect at large sample in Rounds 10 & 12 —
   overkill-avoidance targeting — Round 6, mild negative — BFS-pathing —
   judged low-value in Round 5) has already been explored with no robust
   improvement found. Validation-only round again.

### Suggested next steps for future teammates
- Standing advice unchanged (18th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Use `tools/ab_test.py` (see Round 12
  notes for usage) for any self-play A/B testing rather than recreating a
  script from scratch.
- All three tunable weight constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`) remain settled/closed from Rounds 10 & 12's large-sample
  tests (all ~50% i.e. no effect) — do not re-litigate without a
  fundamentally different targeting idea.
- Genuinely still-untried ideas (unchanged across many rounds, ~18 rounds
  running now): multi-step (2-3 move) lookahead pathing for escaping
  dead-ends near the map's wall corners (still low-value per Round 5's
  analysis); explicit "retreat when badly outnumbered locally" logic for
  individual low-health units (still untried, carries real regression
  risk against the current "always attack if adjacent" philosophy that
  keeps winning decisively). Given the ladder has shown zero sign of a
  genuinely competitive opponent across 18 rounds and 11 opponent names,
  these remain low-priority unless the avg-opponent-final-units trend
  (currently bouncing ~2.4-4.24, no clear upward trend) or actual
  win/loss record changes.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent, reproducible, side-independent edge (this round: 26-11-3
  combined across both sides, 20 seeds each direction, 40 games total).

## Round 19 (this session — starting point was /logs/rounds/0/, will produce /logs/rounds/1/)

**Status check (first thing, per standing advice, 19th time):** Re-verified
`/logs/rounds/0/results.json` for this session's starting point. Opponent
this series is `kalkin__artemis` (12th differently-named opponent across
the rounds documented in this file). Result: **250/250 sweep for
sonnet-5** (sonnet-5 was Red; `Blue wins 0, Red wins 250, ties 0` via the
standard win/loss snippet). Avg final units: opponent (Blue) ~5.61
(min 2, max 10), us (Red) ~25.92. Nineteenth consecutive total sweep
documented in this file (across 12 differently-named opponent identities).
Note: opponent's avg final units (~5.61) is the *highest* opponent average
recorded in this file's history so far (previous high was ~4.24 in rounds
15/16), and the min-units-across-all-250-games is 2 (never fully wiped out)
— a mild continuation of the very slow upward creep noted in round 11's
notes, but still an overwhelming ~4.6x unit-count sweep, nowhere close to
competitive. Grepped all 250 `sim_*.txt` for `raceback|xception|panic` —
zero hits, confirming clean execution across the entire series.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-18 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). `git status --short` clean at session start — no
   drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~0.86s wall-clock incl. setup, no
   exceptions, real combat: `Health 11 11 Units 3 3`, a tie as expected
   for an exact mirror match).
3. Used the persistent `tools/ab_test.py` harness (from Round 12) to
   re-confirm `robot.py`'s edge over `robot_v1_baseline.py` over 20 seeds,
   both sides (`--swap`): robot.py-as-Blue **13 wins / 5 losses / 2 ties**;
   robot.py-as-Red (swapped) **6 wins / 13 losses / 1 tie**. Combined
   across both directions: **19 wins / 18 losses / 3 ties** — this
   particular 20-seed sample landed almost exactly at 50/50 combined,
   which is on the low end of (but still consistent with, given the
   documented seed-to-seed noise) the long-running ~55-70% edge over the
   round-0 baseline reported across most previous rounds. Not treating
   this as a regression signal by itself (single small sample, same
   "swapped direction often looks worse" pattern noted in rounds 13 and
   15), but flagging for future teammates: if a future round's A/B also
   comes back near-even or negative with a *larger* sample, that would be
   worth investigating (possibly re-run with 60-100+ seeds using the
   parallelized harness before concluding anything).
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-18 in this numbering): 19 consecutive 250/250 sweeps across
   12 different opponent names, still overwhelming (~4.6x) final-unit-count
   margin this round (the *tightest* margin recorded so far, worth
   watching), zero runtime errors ever observed across ~4500+ simulated
   games total, and every tunable knob in the bot (all 3 weight constants
   — settled no-effect at large sample in Rounds 10 & 12 — overkill-
   avoidance targeting — Round 6, mild negative — BFS-pathing — judged
   low-value in Round 5) has already been explored with no robust
   improvement found. Validation-only round again, but flagging the
   slow-creeping opponent-strength trend explicitly below for whoever
   picks this up next.

### Suggested next steps for future teammates
- Standing advice unchanged (19th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Use `tools/ab_test.py` (see Round 12
  notes for usage) for any self-play A/B testing rather than recreating a
  script from scratch.
- **Watch the opponent-strength trend more closely now**: avg opponent
  final units by round-file, in chronological order across this file's
  history: ~2.3 → ~1.9-2.0 → ~2.4-2.6 → ~2.4-2.5 → ~3.5 → ~3.3-3.4 →
  ~4.2-4.24 → ~3.8 → **~5.6 (this round)**. This is not a dramatic spike,
  but it IS the highest value recorded yet, and the last several rounds
  show a gentle-but-real upward drift rather than pure noise around a flat
  baseline. Still nowhere close to threatening our win rate (still 4.6x+
  margins, 100% round win rate), but if the *next* round's opponent
  average continues climbing (e.g. into double digits) or margins drop
  below ~3x, that's a much stronger signal than anything seen so far to
  seriously invest in the untried ideas below rather than doing another
  validation-only round.
- All three tunable weight constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`) remain settled/closed from Rounds 10 & 12's large-sample
  tests (all ~50% i.e. no effect) — do not re-litigate without a
  fundamentally different targeting idea.
- Genuinely still-untried ideas (unchanged across many rounds, ~19 rounds
  running now): multi-step (2-3 move) lookahead pathing for escaping
  dead-ends near the map's wall corners (still low-value per Round 5's
  analysis, but worth re-checking via `run web`/`debug.inspect` if the
  opponent-strength trend above keeps climbing — a stronger opponent may
  actually create the traffic-jam/dead-end situations that make this
  matter); explicit "retreat when badly outnumbered locally" logic for
  individual low-health units (still untried, carries real regression
  risk against the current "always attack if adjacent" philosophy that
  keeps winning decisively, but becomes more worth the risk if the
  opponent trend continues).
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. This round's 20-seed A/B
  came back close to even combined (19-18-3) rather than the usual clear
  edge — worth a bigger-sample re-check next round using
  `tools/ab_test.py` with 60-100 seeds before concluding whether this is
  just noise (most likely, per the pattern of previous rounds' small
  samples regressing to ~50% before larger samples clarified things) or an
  actual drift.

### Follow-up within this same round: resolved the near-even A/B with a bigger sample
Re-ran `tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-60` (60
seeds, single direction, robot.py as Blue) right after noticing the
close-to-even 20-seed combined result above: **35 wins / 21 losses / 4
ties** for `robot.py` (~62.5% of decisive games) — this matches the
long-running historical edge over the baseline perfectly. Confirms the
20-seed near-even combined result earlier in this section was just noise
(small-sample variance, same trap warned about in Round 12's notes), NOT
evidence of any regression or opponent-related drift in `robot.py`'s
self-play performance. No action needed; `robot.py` is unchanged and
healthy. The opponent-strength creep noted above (~5.61 avg final units
for `kalkin__artemis`) is still worth watching over future rounds, but is
unrelated to this self-play A/B number.

## Round 20 (this session — starting point had /logs/rounds/0/ AND /logs/rounds/1/
already present, will produce /logs/rounds/2/)

**Status check (first thing, per standing advice, 20th time):** Both
`/logs/rounds/0/results.json` and `/logs/rounds/1/results.json` were
already present at session start (this session picked up right after the
previous teammate's round-19 submission, which itself produced round 1).
Opponent this series is `kalkin__artemis` (same name as round 19's notes
above — round 0 and round 1 here are both part of that same opponent-name
series, per git log `Rung 11/58 (kalkin__artemis, elo #48) — Round 1
Update`). Both rounds: **250/250 sweep for sonnet-5** (round 0: sonnet-5
Red, `Red wins 250`; round 1: sonnet-5 Blue, `Blue wins 250`). Twentieth
consecutive total sweep documented in this file (across 12 differently-named
opponent identities so far).

Recomputed avg final units for both rounds (standard win/loss snippet +
final-`Units` regex, see earlier sections):
- round 0: opponent (Blue) avg **5.61**, us (Red) avg **25.92** (matches
  round 19's notes exactly — same numbers, since round 19's session
  produced this exact round-0 log).
- round 1: opponent (Red) avg **5.54**, us (Blue) avg **26.76**.

So the opponent-strength trend flagged in round 19's notes (avg final units
crept up from ~2.3 to ~5.6 over ~19 rounds) has **stabilized, not continued
climbing** — round 1's ~5.54 is essentially flat vs round 0's ~5.61, not a
further increase. Still an overwhelming ~4.7x unit-count sweep in both
rounds, 100% round win rate maintained. Grepped all `sim_*.txt` in
`/logs/rounds/1/` for `raceback|xception|panic` — zero hits, confirming
clean execution.

### What I did this round
1. Confirmed `robot.py` is byte-identical to the version described in
   rounds 4-19 above (per-unit soft targeting blending own-distance +
   target health + team coordination-distance + focus-bonus;
   opportunistic always-attack-if-adjacent, weakest-first; `direction_to`
   movement w/ full 4-direction sidestep fallback; spawn-tile-escape when
   no enemies visible). `git status --short` clean at session start — no
   drift.
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~1.15s wall-clock incl. setup, no
   exceptions, real combat: `Health 16 10 Units 4 3`) and vs
   `robot_v1_baseline.py` (~0.68s, no exceptions, `Health 23 13 Units 7
   4`).
3. Used the persistent `tools/ab_test.py` harness (from Round 12) to
   re-confirm `robot.py`'s edge over `robot_v1_baseline.py` over 30 seeds,
   both sides (`--swap`): robot.py-as-Blue **19 wins / 9 losses / 2
   ties**; robot.py-as-Red (swapped) **17 wins / 12 losses / 1 tie**.
   Combined across both directions: **36 wins / 21 losses / 3 ties**
   (~63% of decisive games) — consistent, side-independent, matches the
   long-running ~55-70% edge over the round-0 baseline reported across
   nearly every previous round. No regression. (This also resolves any
   lingering doubt from round 19's initial close-to-even 20-seed sample —
   that was confirmed as noise within the same round-19 session via a
   60-seed re-check, and this round's fresh 60-game combined sample
   reproduces the normal healthy edge again.)
4. **No code changes made this round.** Same reasoning as rounds 2-19: 20
   consecutive 250/250 sweeps across 12 different opponent names, still
   overwhelming (~4.7x) final-unit-count margins in both of this session's
   logged rounds, zero runtime errors ever observed across ~5000+
   simulated games total, and every tunable knob in the bot (all 3 weight
   constants — settled no-effect at large sample in Rounds 10 & 12 —
   overkill-avoidance targeting — Round 6, mild negative — BFS-pathing —
   judged low-value in Round 5) has already been explored with no robust
   improvement found. The opponent-strength creep flagged as a
   watch-item in round 19 appears to have plateaued rather than continued
   climbing (~5.6 → ~5.54, flat), so there's still no strong trigger to
   abandon the validation-only pattern that has worked for 19+ consecutive
   rounds.

### Suggested next steps for future teammates
- Standing advice unchanged (20th time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Use `tools/ab_test.py` (see Round 12
  notes for usage) for any self-play A/B testing rather than recreating a
  script from scratch.
- **Opponent-strength trend update**: the slow creep noted in round 19
  (avg opponent final units climbing from ~2.3 up to ~5.61 over many
  rounds) appears to have **plateaued** at this round (round 0: 5.61,
  round 1: 5.54 — essentially flat, not a new high). Keep tracking this
  number each round; if it starts climbing again (especially past ~8-10)
  or margins drop meaningfully below ~4x, that's the trigger to seriously
  invest in the still-untried ideas below instead of another
  validation-only round.
- All three tunable weight constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`) remain settled/closed from Rounds 10 & 12's large-sample
  tests (all ~50% i.e. no effect) — do not re-litigate without a
  fundamentally different targeting idea.
- Genuinely still-untried ideas (unchanged across ~20 rounds now):
  multi-step (2-3 move) lookahead pathing for escaping dead-ends near the
  map's wall corners (still low-value per Round 5's analysis); explicit
  "retreat when badly outnumbered locally" logic for individual low-health
  units (still untried, carries real regression risk against the current
  "always attack if adjacent" philosophy that keeps winning decisively).
  Neither has been necessary yet across 20 rounds and 12 opponent names,
  all crushed by 4x+ unit-count margins minimum.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. Still gives `robot.py` a
  consistent, reproducible, side-independent edge (this round: 36-21-3
  combined across both sides, 30 seeds each direction, 60 games total).

## Round 21 (this session — starting point was fresh /logs/rounds/0/ only, will produce /logs/rounds/1/)

**Status check (first thing, per standing advice, 21st time):** Only
`/logs/rounds/0/results.json` was present at session start. Opponent this
series is `kalkin__artemis2` (note the "2" suffix — a *new* opponent
identity distinct from the previous `kalkin__artemis` seen in rounds
19/20, per git log `Rung 11/58 (kalkin__artemis, elo #48) — Round 2
Update` being the most recent commit before this session but the actual
round-0 log here already shows the new `kalkin__artemis2` name — likely
the ladder advanced to a new rung between sessions). Result: **250/250
sweep for sonnet-5** (sonnet-5 was Blue; `Blue wins 250, Red wins 0, ties
0` via the standard win/loss snippet). Avg final units: us (Blue) ~15.84
(min 7, max 26), opponent (Red) ~2.83 (min 0, max 6). Twenty-first
consecutive total sweep documented in this file (across 13 differently-
named opponent identities now, counting `kalkin__artemis2` separately from
`kalkin__artemis`). Note: this round's ~5.6x unit-count margin and our own
avg-units (~15.84) are both noticeably *lower* than the previous several
rounds' numbers (our avg units had been climbing into the high-20s/low-30s
range in rounds 15-20) — this is likely just seed/opponent variance rather
than a real regression (opponent avg final units ~2.83 is actually *lower*
than the ~5.5-5.6 seen in rounds 19/20, so if anything this looks like an
easier matchup, just with lower absolute unit counts on both sides, maybe
due to different spawn RNG or a shorter/different combat pattern this
opponent triggers). Grepped all 250 `sim_*.txt` for
`raceback|xception|panic` — zero hits, confirming clean execution.

### What I did this round
1. Confirmed `robot.py` is byte-identical to `git show HEAD:robot.py`
   (explicit `diff` check, zero output) — no drift from the version
   described in rounds 4-20 above (per-unit soft targeting blending
   own-distance + target health + team coordination-distance +
   focus-bonus; opportunistic always-attack-if-adjacent, weakest-first;
   `direction_to` movement w/ full 4-direction sidestep fallback;
   spawn-tile-escape when no enemies visible).
2. Sanity-checked it still runs clean and fast: `./rumblebot run term
   --results-only robot.py robot.py` (~0.9s wall-clock incl. ~99ms setup,
   no exceptions, real combat: `Health 30 11 Units 8 3`).
3. Used the persistent `tools/ab_test.py` harness (from Round 12) to
   re-confirm `robot.py`'s edge over `robot_v1_baseline.py` over 30 seeds,
   both sides (`--swap`): robot.py-as-Blue **19 wins / 9 losses / 2
   ties**; robot.py-as-Red (swapped) **12 wins / 17 losses / 1 tie**.
   Combined across both directions: **31 wins / 26 losses / 3 ties**
   (~54% of decisive games) — on the lower end of, but still consistent
   with, the long-running ~55-70% edge range over the round-0 baseline
   reported across nearly every previous round (per rounds 12/13/19's
   notes, per-direction small samples are noisy and the "swapped" side
   often looks weaker in any given sample; a 60-game combined sample
   landing at ~54% is unremarkable noise, not a regression signal). No
   code changes made in response to this, consistent with the historical
   pattern of this specific check being noisy at n=60.
4. **No code changes made this round.** Same reasoning as most previous
   rounds (2-20 in this numbering): 21 consecutive 250/250 sweeps across
   13 different opponent names/identities, still overwhelming (~5.6x)
   final-unit-count margin this round, zero runtime errors ever observed
   across ~5250+ simulated games total, and every tunable knob in the bot
   (all 3 weight constants — settled no-effect at large sample in Rounds
   10 & 12 — overkill-avoidance targeting — Round 6, mild negative —
   BFS-pathing — judged low-value in Round 5) has already been explored
   with no robust improvement found. Validation-only round again.

### Suggested next steps for future teammates
- Standing advice unchanged (21st time writing this): check
  `/logs/rounds/N/results.json` + final-unit-count margins FIRST thing
  next round, before making changes. Use `tools/ab_test.py` (see Round 12
  notes for usage) for any self-play A/B testing rather than recreating a
  script from scratch.
- **Opponent naming note**: this round's opponent (`kalkin__artemis2`) has
  a "2" suffix distinct from the plain `kalkin__artemis` seen in rounds
  19/20 — treat it as a new/different opponent identity in the ladder, not
  a continuation, when computing trend lines in future notes (I've counted
  it as opponent #13 in the "differently-named opponent" tally above,
  separate from `kalkin__artemis`'s earlier #12).
- All three tunable weight constants (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`) remain settled/closed from Rounds 10 & 12's large-sample
  tests (all ~50% i.e. no effect) — do not re-litigate without a
  fundamentally different targeting idea.
- Genuinely still-untried ideas (unchanged across ~21 rounds now):
  multi-step (2-3 move) lookahead pathing for escaping dead-ends near the
  map's wall corners (still low-value per Round 5's analysis); explicit
  "retreat when badly outnumbered locally" logic for individual low-health
  units (still untried, carries real regression risk against the current
  "always attack if adjacent" philosophy that keeps winning decisively).
  Neither has been necessary yet across 21 rounds and 13 opponent
  identities, all crushed by 4x+ unit-count margins minimum.
- `robot_v1_baseline.py` remains the frozen round-0 reference bot for A/B
  self-play testing — do not delete/modify it. This round's A/B landed on
  the lower end of the historical edge range (~54% combined over 60
  games) — not concerning on its own (see reasoning above), but if a
  future round's larger-sample A/B also comes back near-even or negative,
  that would be worth a deeper look (e.g. re-verify `robot.py` hasn't
  silently drifted, or consider whether `robot_v1_baseline.py` itself
  needs refreshing as a reference point after ~20 rounds of no changes to
  compare against).
