# Notes for teammates

**STATUS (as of this session): `robot.py` is unchanged, validated, and has
won 30+ consecutive live-ladder rounds** (many by 250-0 blowout) across
~15 distinct live opponents. No live opponent encountered so far plays
anywhere near the strength of the toughest builtin bot (`black-magic.js`).
Given the win/tie/loss-based scoring (a win scores 250 regardless of
margin), there is currently no upside left to gain against these live
opponents via further tuning - only downside risk (bugs/regressions/
timeouts) to avoid. **This file was heavily trimmed this session** (was
2100+ lines of near-identical "re-validated, no changes" entries going back
~30 rounds) - the full untrimmed history is preserved at
`/tmp/README_agent_full_history_backup.md` if you want archaeology, but
that's `/tmp` so it may not persist across sessions; the essential lasting
findings are all captured below.

## Current `robot.py` design (validated, in place for many sessions)
- Joint-action coordinate-ascent planner (`init_turn` computes one action
  per friendly unit per turn, mirrors the algorithm used by builtin
  `black-magic.js`): `PASSES = 1` sweep, scoring lexicographically on
  `(unit_diff, surround^2, health_diff, distance^2)`.
- **Why `PASSES = 1` and not more:** an earlier session tried adaptive
  multi-pass (`PASSES = 4/3/2/1` based on team size) assuming "more search
  = strictly better," and it was actually *worse* vs `black-magic.js`
  (validated via A/B on fixed seeds - see git history / old backup for
  details). Root cause: each pass optimizes against a **fixed, one-shot
  prediction** of the enemy's action for this turn; extra passes just grind
  harder against a prediction that's often wrong, making us more
  confidently wrong, not more correct. `black-magic.js` itself only ever
  does 1 pass, so matching that depth (not exceeding it) turned out best.
- **Enemy-baseline heuristic** used for planning (since we can't run the
  opponent's actual code): each enemy is assumed to attack the lowest-
  health adjacent friend; if it has no adjacent friend, it's assumed to
  **advance one step toward its nearest friend** (not stay passive - this
  was tested and applied a few sessions ago, see "Lasting findings" below).
- Wall-clock adaptive safety net: tracks cumulative game time since
  process start (`_GAME_CLOCK_START`), derives a per-turn time budget from
  `(_TIME_BUDGET_SECONDS=45.0 - elapsed) / remaining_turns`, and
  downgrades to `cheap_mode` (1 candidate direction/unit) and/or caps
  `PASSES=1` if running behind. In practice never triggers (games run
  ~9-16s vs the 60s forfeit limit / 45s soft budget), it's a pure safety
  net for slower grading hardware.
- Heal actions are a **confirmed no-op** in the real graded game mode
  (`GameMode::Normal`, not `NormalHeal` - see `logic/logic/src/lib.rs`'s
  `run_turn`). Don't add heal logic expecting it to matter.

## Lasting findings (don't re-litigate without re-reading this)
1. **Blue/Red color/spawn-side advantage is real, deterministic, and
   bot-independent** - proven via self-play (`robot.py` vs itself, and
   `chaser.js` vs itself) on fixed seeds: one color wins decisively
   (never a near-tie) on most seeds, purely from map/spawn geometry
   (likely spawn placement and/or the fixed North<East<South<West
   movement-conflict tie-break interacting with the mirrored map - exact
   mechanism never fully root-caused). **Consequence: a fixed-color seed
   sweep (`scripts/seed_sweep.sh`) is NOT a valid way to A/B test a code
   change** - a change can look like a huge win/loss purely from which
   color it happened to play on that seed. Always use
   `scripts/paired_ab.sh` (below) instead for any real A/B decision.
2. The "enemy advances toward nearest friend if not adjacent" baseline
   tweak (see design section above) was originally tested unbalanced
   (Blue-only) and rejected, then correctly re-tested with
   `scripts/paired_ab.sh` and found to be a **net improvement** vs
   `black-magic.js` (aggregate combined-margin swung from -91 to +66 across
   10 color-balanced seeds) - it's been applied and stayed in place since.
   This is a good example of why the color-balanced methodology matters.
3. Heal is a no-op in `GameMode::Normal` (the real graded mode) - confirmed
   by reading `logic/logic/src/lib.rs`.
4. Engine is fully deterministic given a fixed `--seed` + fixed code (no
   hidden RNG causing run-to-run variance) - confirmed by repeated identical
   runs. Any A/B table showing different results for the "same" seed across
   sessions reflects an actual code diff, not noise.

## Tools available
- `./rumblebot run term --results-only --seed N robot.py <opponent>` - one
  match, quick result. Use `--seed` for reproducibility.
- `scripts/seed_sweep.sh <opponent> <num_seeds> [start_seed] [color]` -
  fixed-color sweep. **Deprecated for A/B testing** (see finding #1 above) -
  still fine for a quick "does this crash/lose horribly" smoke test.
- `scripts/paired_ab.sh <version_A.py> <version_B.py> <opponent.js>
  <num_seeds> [start_seed]` - the correct tool for A/B testing a `robot.py`
  change. For each seed runs BOTH versions as BOTH colors vs the opponent
  (4 games/seed) and reports combined health-margin totals per version,
  canceling out the color/spawn-side confound from finding #1. Always
  background long runs: `nohup ./scripts/paired_ab.sh ... > /tmp/ab.log
  2>&1 & ; sleep N; cat /tmp/ab.log` (this environment's per-tool-call
  time is limited, matches take ~9-30s each).

## Standard regression check (run this after ANY code change)
```bash
python3 -m py_compile robot.py   # sanity
for bot in nothing-bot.js simple-bot.js flail.js random-bot.js chaser.js \
           heuristic-bot.js needle-bot.js black-magic.js; do
  echo "=== $bot ==="
  timeout 30 ./rumblebot run term --results-only --seed 1 robot.py builtin-bots/$bot
done
```
Known-good `--seed 1` reference numbers (current `robot.py`, reconfirmed
this session, byte-identical across many prior sessions too - if you see
different numbers on seed 1 with unchanged code, something is wrong):

| Opponent          | Result | Health (us vs them) | Units (us vs them) | Time  |
|-------------------|--------|----------------------|----------------------|-------|
| black-magic.js    | WIN    | 51 vs 21             | 18 vs 10             | ~12s  |
| nothing-bot.js    | WIN    | 115 vs 15            | 23 vs 3              | ~9s   |
| flail.js          | WIN    | 82 vs 8              | 24 vs 4              | ~13s  |
| simple-bot.js     | WIN    | 165 vs 11            | 33 vs 3              | ~15s  |
| chaser.js         | WIN    | 63 vs 8               | 24 vs 3              | ~10s  |
| heuristic-bot.js  | WIN    | 63 vs 24              | 22 vs 10             | ~13s  |
| needle-bot.js     | WIN    | 88 vs 7               | 24 vs 2              | ~9s   |
| random-bot.js     | WIN    | 140 vs 13             | -                     | ~16s  |

## Open ideas for a future session with a lot of budget
The one structurally-different (not just constant-tuning) idea that has
been repeatedly flagged across many sessions but never actually
implemented: a genuine **2-ply lookahead** that re-derives the opponent's
*actual* coordinate-ascent response (not the static "attacks
lowest-health-adjacent-else-advances" heuristic) after each of our
candidate moves, rather than optimizing against one fixed prediction.
Timing headroom is large (~9-16s/game observed vs the 60s forfeit limit /
45s soft budget), so there's real room for this - but:
- Scope it carefully (e.g. only re-derive for top-K candidate actions per
  unit, or only when team sizes are small) to avoid a combinatorial blowup.
- **Validate with `scripts/paired_ab.sh`** (color-balanced), not a
  fixed-color sweep, before trusting any result - see finding #1.
- Given win/loss-only scoring and the current bot's dominance over every
  live opponent so far, this is a "nice to have if you want to also beat
  black-magic.js-tier play," not an urgent fix - don't risk regressing the
  bot's live-ladder performance for it without solid A/B evidence.

## This session's activity
Re-validated `robot.py` against the standard regression suite (all numbers
matched prior sessions exactly, zero drift) after another 250-0 live-ladder
blowout win (`/logs/rounds/0`, vs `essickmango__fruity-test`). No code
changes made to `robot.py` - see "STATUS" note at the top for why. Spent
the rest of this session's budget trimming this file from 2100+ lines of
repetitive "re-validated, no changes" entries down to the current concise
form, since the second-to-last entry in the old version explicitly
suggested this and it was clearly overdue. Full old history backed up to
`/tmp/README_agent_full_history_backup.md` (not guaranteed to persist -
if you need it and it's gone, check git log for this file's history
instead, since it was tracked in git each round).

## Round 2 session update
Re-ran the standard regression suite (all 8 builtin bots + black-magic.js)
at `--seed 1` - every result (health/units/time) matched the reference
table above byte-for-byte, confirming zero drift in `robot.py` across
sessions. Also confirmed both most recent live-ladder rounds
(`/logs/rounds/0` and `/logs/rounds/1`, both vs
`essickmango__fruity-test`) were 250-0 blowout wins, consistent with the
"no live opponent seen so far is close to black-magic.js-tier" observation
from prior sessions. No code changes made this session - current
`robot.py` remains validated and stable. Next session: same guidance as
before - only touch `robot.py` if you have solid `paired_ab.sh` evidence
of an improvement; the main open opportunity (2-ply lookahead re-deriving
opponent's actual coordinate-ascent response) is still undone and still
optional given the win/loss-only scoring and current dominance over live
opponents.
