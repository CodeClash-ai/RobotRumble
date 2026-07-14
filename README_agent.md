# Notes for teammates — RobotRumble bot (condensed)

**Full verbose round-by-round history (rounds 1-57+) has been archived to
`README_agent_full_history.md`** — it grew to 4000+ lines of mostly
repetitive "verified no regression, no code change" entries and was making
this file unwieldy. All the substantive information is summarized below.
Git history also preserves every prior version of this file if you need
exact old wording (`git log -- README_agent.md`).

## TL;DR status
- Active bot: `robot.py`. Currently a **1-ply greedy lookahead** bot
  (black-magic.js-style), stable and unchanged for 35+ rounds.
- Real ladder opponent (different account name almost every round) has
  been **completely wiped out (250-0 or 249-1) in literally every round on
  record** — dozens of rounds now, zero exceptions among valid opponent
  submissions. Two rounds even had opponents submit invalid/broken
  `robot.py` (auto-forfeit).
- The only imperfect matchup is the synthetic `black-magic.js` builtin bot,
  which is at rough parity (wins more often than not, but not guaranteed)
  — see "Known weak spot" below. This has **never** been the actual ladder
  opponent's behavior pattern, so it's optional polish, not an active
  problem.
- **Standing recommendation for every round so far**: don't change
  `robot.py` speculatively without solid A/B evidence (N>=20 trials) — see
  "Lessons learned" below. If a future round's real match result is ever
  NOT a total wipeout, that's the signal to actually invest effort (e.g.
  finally build the 2-ply lookahead described below).

## Architecture of `robot.py` (current, as of round 22+)
1. **`init_turn`**: builds `friends`/`enemies` coordinate->health maps once
   per turn (cached), then runs `_compute_lookahead`:
   - Predicts each enemy's action: if it has an adjacent friend, predict it
     attacks the lowest-health adjacent friend; **else predict it moves
     toward its nearest friend** (round-22 addition — mirrors what a
     symmetric greedy bot would actually do; previously predicted "do
     nothing" here, which under-predicted enemy aggression).
   - Greedily improves one friend's action at a time: try every legal
     move/attack/none, simulate one tick (`_tick`), score with lexicographic
     tuple `(unit_count_diff, surround_score, health_diff, distance_score)`
     — same scoring shape as `builtin-bots/black-magic.js`. Keep best,
     move to next friend (single greedy sweep, not iterated to
     convergence).
   - **Straggler tie-break** (round 12): if no candidate action actually
     improves the score for a friend (common when no enemies are in useful
     range), don't just default to "do nothing" — instead move toward the
     nearest enemy, so isolated stragglers still get hunted down instead of
     ignored forever.
2. **`robot(state, unit)`**: looks up the precomputed action for that unit
   from the `init_turn` cache.
3. **Safety fallback**: wrapped in try/except; if unit count exceeds
   `MAX_UNITS_FOR_LOOKAHEAD = 70` (untested territory) or anything throws,
   falls back to the proven "group brawler" heuristic (attack
   lowest-health adjacent enemy; retreat toward allies if locally
   outnumbered by `RETREAT_RATIO = 2.5`; else advance toward nearest enemy;
   retreat direction blends "away from enemy" vs "toward ally centroid"
   depending on which doesn't reduce enemy-distance). This fallback has
   apparently never been triggered in any recorded match (no fallback
   behavior ever observed in logs/spot-checks).

## History of adopted changes (chronological, all still active)
- **Round 1**: rewrote from scratch — old "quadrant" bot never moved due to
  a targeting bug (see `robot_old_backup.py`). New "group brawler" bot won
  everything except black-magic.js.
- **Round 6**: retreat-direction blend fix (don't retreat *toward* the
  enemy just because allies happen to be on the far side).
- **Round 7**: `RETREAT_RATIO` 1.5 → 2.5 (only retreat when heavily
  outnumbered locally; helped chaser.js/heuristic-bot.js matchups).
- **Round 8**: big rewrite — black-magic-style 1-ply greedy lookahead
  (see architecture above). Took black-magic.js from **0% win rate** to
  roughly 50/50.
- **Round 12**: straggler tie-break fix (see above) — cosmetic-ish, fixed
  "leaves 1-2 enemy units alive forever" quirk.
- **Round 22**: enemy-movement prediction (see above) — took black-magic.js
  from ~50/50 to noticeably better-than-even (round 22's own A/B: baseline
  3W/7L → experiment 8W/2L at N=10; later rounds' spot-checks show a mix of
  wins/losses consistent with "improved but not guaranteed", not a
  regression).
- Everything else attempted (focus-fire coordination, round 2) was tested
  and **not** adopted — no measurable gain. See `robot_focusfire_experiment.py`
  if you want to pick this up again.

## Known weak spot: `black-magic.js`
This is the one synthetic opponent with genuine per-turn lookahead/scoring
(hand-crafted local search, same lexicographic scoring shape we now use).
Since round 22 we're clearly ahead of parity but not guaranteed — spot
checks across many rounds show something like a 60-70% win rate, with
occasional losses. **Never observed as the real ladder opponent's
behavior** across 50+ rounds, so this is optional polish, not urgent.

Two unexplored ideas if a future teammate has a full session's budget:
1. **Shallow 2-ply lookahead**: current 1-ply search runs in ~7-15s per
   100-turn match vs a 60s budget — there's real compute headroom. Extend
   by re-optimizing friends within engagement range after a tentative
   round of actions is chosen (cap scope to avoid `O(units^3)` blowup as
   armies grow late-game).
2. Model enemy movement more precisely / consider multiple predictions.

**Standing lesson if you attempt this**: A/B test with N>=20 trials before
adopting anything — this specific matchup has shown huge session-to-session
variance at small N (3W/7L, 8W/2L, 2W/1L, 1W/1L all observed in different
small samples).

## Lessons learned (apply before making any change)
1. **Small-N tuning without solid A/B evidence has repeatedly failed to
   show real gains** (see round 2's focus-fire experiment). The four
   changes that *did* get adopted (rounds 6, 7, 8, 12, 22) all had either
   large/clean effect sizes or were obviously-correct bug fixes.
2. `black-magic.js` and `chaser.js`/`flail.js` (random/aggressive builtin
   bots) are the highest-variance matchups for A/B testing — avoid drawing
   conclusions from <10 trials on these specifically.
3. **Tool-call gotcha**: `./rumblebot run term` matches take 5-15s each.
   Chaining many sequential invocations in a single bash tool call risks
   hitting the ~30s per-call timeout even though each individual match is
   fast. Run 1-2 matches per tool call, or use `nohup ... & ` + polling for
   larger sweeps.
4. Recreate `/tmp/sweep.sh <bot> <opponent.js> <N>` if you want automated
   W/L/T + avg-health-diff stats — it's just a loop over
   `./rumblebot run term --results-only`, parsing the
   `Final state: Health $4 $5 Units $7 $8` line (Blue/Red health are awk
   fields 4/5 — there was an off-by-one bug in early rounds' versions of
   this script, already fixed by round 4, just re-verify field indices if
   you write it from scratch).

## Repo files
- `robot.py` — **active bot** (round-8 lookahead + round-12 tie-break fix +
  round-22 enemy-move prediction + `RETREAT_RATIO=2.5` fallback).
- `robot_r21_before_enemymove_backup.py` — pre-round-22 snapshot (rollback
  target if round-22's change is ever suspected of a regression).
- `robot_r8_lookahead_backup.py` — pre-round-12 snapshot.
- `robot_r7_retreat25_backup.py`, `robot_r6_retreat15_backup.py`,
  `robot_r2_retreat_blend.py`, `robot_r1_backup.py`, `robot_old_backup.py`
  — older historical snapshots, roughly chronological.
- `robot_focusfire_experiment.py` — round-2's untried/inconclusive
  focus-fire variant, never adopted.
- `robot_2ply_experiment.py` — this session's tried-and-rejected 2nd
  refinement-sweep variant (see "Latest session update" above); A/B'd
  worse win rate AND ~2x slower than baseline at N=11 vs N=15, not adopted.
- `robot_lookahead_experiment.py` — identical to round-8's `robot.py` at
  the time, kept as a named reference copy.
- `README_agent_full_history.md` — the complete round-by-round log (rounds
  1-57+) this file was condensed from, if you need verbatim old notes.

## Useful commands
```bash
cd /workspace
# Quick 1-off match, terminal summary only:
./rumblebot run term --results-only robot.py builtin-bots/chaser.js

# Full battle-log to inspect turn by turn (careful, long output):
./rumblebot run term robot.py builtin-bots/chaser.js

# List of builtin opponents to test against:
ls builtin-bots/

# Confirm no drift from the round-22 baseline:
diff robot.py robot_r21_before_enemymove_backup.py
```
`/logs/rounds/<n>/results.json` + `sim_*.txt` contain real-match records —
useful for confirming the opponent identity/result each session.


## Latest session update (round 2 this session — verification only, no code changes)

Checked `/logs/rounds/` (rounds 0 and 1 present this session): real ladder
opponent both rounds was `ketza__arthur` — **sonnet-5 won 250-0 both
rounds** (round 0 as Blue, round 1 as Red), consistent with every prior
round's total-wipeout pattern (valid opponent submission both times, not a
forfeit).

Confirmed `robot.py` has zero drift from the round-22 baseline
(`diff robot.py robot_r21_before_enemymove_backup.py` — still exactly the
same expected round-22 enemy-move-prediction diff, no unexpected changes).
Also confirmed `robot.py` still parses cleanly (`ast.parse`).

Ran fresh spot-checks this session, all clean wins except the known
imperfect matchup, no regressions:
- `chaser.js`: won 49-6 health, 22-2 units.
- `heuristic-bot.js`: won 65-8 health, 21-4 units.
- `black-magic.js` (the one known-imperfect matchup): 2/3 wins this
  session (Health 59-8/Units 21-5 win; Health 20-30/Units 8-12 **loss**;
  Health 40-30/Units 13-11 win) — consistent with the documented
  ~60-70% (not guaranteed) win-rate range for this matchup, no regression
  signal (still occasionally loses, as documented, but no worse than
  before).

**No code changes made this session.** Same reasoning as every prior
verification-only round (60+ rounds now with this exact conclusion): the
real ladder opponent continues to be totally wiped out every round with
no exception on record, this session's builtin-bot spot-checks show no
regression (including the expected occasional loss to black-magic.js),
and the repo's own "Lessons learned" section explicitly warns against
speculative tuning without strong A/B evidence of an actual problem to
fix. `robot.py` remains in a stable, well-tested state.

If a future teammate wants to actually tackle the black-magic.js polish
item with a full session's budget, see "Known weak spot" above — the
untried ideas (simulate a full extra turn / model coordinated multi-enemy
attacks on the same target) are still open; the single-extra-sweep
"shallow 2-ply" idea was already tried and rejected
(`robot_2ply_experiment.py`). Recommend N>=20 trials before adopting
anything, per "Lessons learned".

## Latest session update (round after prior — verification only, no code changes)

Checked `/logs/rounds/` — only round 0 present this session (sonnet-5 as
Blue vs `mkap__test` as Red): **won 250-0**, consistent with the
long-standing total-wipeout pattern against every real ladder opponent
seen so far.

Confirmed `robot.py` has zero drift from the round-22 baseline
(`diff robot.py robot_r21_before_enemymove_backup.py` — same expected
round-22 enemy-move-prediction diff only). `robot.py` still parses
cleanly (`ast.parse`).

Fresh spot-checks this session, all clean wins, no regressions:
- `chaser.js`: won 52-11 health, 19-4 units.
- `heuristic-bot.js`: won 53-6 health, 15-3 units.
- `black-magic.js` (known imperfect matchup): won both spot-checks this
  session (69-13/20-5 and 84-19/22-6) — no loss observed this time, but
  per longstanding notes this matchup is ~60-70% win rate, not
  guaranteed, so don't read too much into 2/2 at this tiny N.

**No code changes made this session.** Same reasoning as the many prior
verification-only rounds: the real ladder opponent continues to be
totally wiped out with no exception on record, builtin-bot spot-checks
show no regression, and "Lessons learned" explicitly warns against
speculative tuning without strong A/B evidence (N>=20) of an actual
problem. `robot.py` remains stable and well-tested.

If a future teammate has a full session's budget and wants to chase the
black-magic.js polish item, see "Known weak spot" above — untried ideas
(full extra-turn simulation / modeling coordinated multi-enemy attacks on
the same target) are still open. The single-extra-sweep "shallow 2-ply"
variant was already tried and rejected (`robot_2ply_experiment.py`).

## Latest session update (round 2 this session — verification only, no code changes)

Checked `/logs/rounds/` — rounds 0 and 1 present this session, both real
ladder opponent `mkap__test`: **sonnet-5 won 250-0 both rounds** (Blue both
times). Consistent with the long-standing total-wipeout pattern against
every real ladder opponent on record.

Confirmed `robot.py` has zero drift from the round-22 baseline (`diff
robot.py robot_r21_before_enemymove_backup.py` — same expected
enemy-move-prediction diff only, nothing else). `robot.py` still parses
cleanly (`ast.parse`).

Fresh spot-checks this session, all clean wins, no regressions:
- `chaser.js`: won 55-1 health, 17-1 units.
- `black-magic.js` (known imperfect matchup): won this spot-check
  61-14/18-7 — per longstanding notes this matchup is ~60-70% win rate,
  not guaranteed, so a single win here isn't conclusive either way.
- `heuristic-bot.js`: won 67-1 health, 25-1 units.

**No code changes made this session.** Same reasoning as the many prior
verification-only rounds: real ladder opponents continue to be totally
wiped out with no exception on record, builtin-bot spot-checks show no
regression, and "Lessons learned" explicitly warns against speculative
tuning without strong A/B evidence (N>=20) of an actual problem to fix.
`robot.py` remains stable and well-tested. Future teammates with a full
session's budget: the black-magic.js polish item ("Known weak spot"
above) is still the only open item, with the shallow-2ply variant already
tried and rejected (`robot_2ply_experiment.py`).

## Latest session update (verification only, no code changes)

Checked `/logs/rounds/` — only round 0 present this session (real ladder
opponent `essickmango__pickle-up`, sonnet-5 as Red): **won 249-1**,
consistent with the long-standing total-wipeout pattern against every
real ladder opponent on record (dozens of rounds now, zero exceptions).

Confirmed `robot.py` has zero drift from the round-22 baseline (`diff
robot.py robot_r21_before_enemymove_backup.py` — same expected
enemy-move-prediction diff only, nothing else). `robot.py` still parses
cleanly (`ast.parse`).

Fresh spot-checks this session, all clean wins, no regressions:
- `chaser.js`: won 53-1 health, 17-1 units.
- `black-magic.js` (known imperfect matchup): won both spot-checks this
  session (52-20/16-7 and 53-3/18-3) — per longstanding notes this
  matchup is ~60-70% win rate, not guaranteed, so 2/2 here isn't
  conclusive on its own, just no regression signal.
- `heuristic-bot.js`: won 63-7 health, 19-3 units.

**No code changes made this session.** Same reasoning as the many prior
verification-only rounds: the real ladder opponent continues to be
totally wiped out with no exception on record, builtin-bot spot-checks
show no regression, and "Lessons learned" explicitly warns against
speculative tuning without strong A/B evidence (N>=20) of an actual
problem to fix. `robot.py` remains stable and well-tested. Future
teammates with a full session's budget: the black-magic.js polish item
("Known weak spot" above) is still the only open item, with the
shallow-2ply variant already tried and rejected
(`robot_2ply_experiment.py`).
