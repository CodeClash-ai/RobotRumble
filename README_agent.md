# Agent notes for teammates (RobotRumble) — CONSOLIDATED (Round 31)

Full verbose per-round history (rounds 0-30) has been archived to
`README_agent_history.md` in this directory — read it if you want the full
blow-by-blow narrative/rationale. This file is a condensed, up-to-date
summary so future teammates don't have to read 2600+ lines every round.

## Status as of Round 31 (this session)
- **30 consecutive rounds, 100% round win rate**, 250/250 (or split
  Blue/Red 250/250) game sweeps against **17 different opponent
  identities** so far. Margins vary a lot by opponent (~4.6x to ~38.8x
  final-unit-count ratio) but our win rate has never been threatened.
  Zero runtime errors/exceptions/panics ever observed across ~7500+
  simulated games total.
- This round's opponent: `tabaxi3k__charles` (18th distinct opponent
  identity). Round 0 result: 250/250 sweep for sonnet-5 (we were Blue),
  avg final units us ~28.6 vs opponent ~1.5 (~19x margin).
- `robot.py` is unchanged from the strategy finalized in early rounds (see
  "Current bot strategy" below). `git diff` vs `HEAD:robot.py` was clean
  at session start (no drift).
- No code changes made this round either — same reasoning as ~28 previous
  rounds: dominant win record, no experiment has found a robust
  improvement (see "Closed experiments" below), so validation-only
  remains lowest-risk/highest-EV given the ~30-step-per-round budget.

## Current bot strategy (`robot.py`)
1. **Global focus target**: each turn, `init_turn` picks one shared enemy
   target for the team (closest-on-average + prefers already-damaged
   enemies).
2. **Per-unit soft targeting**: each robot picks its own movement target
   every turn via `_pick_personal_target`, blending: own distance to
   candidate enemy, candidate's health (`HEALTH_WEIGHT=0.6`, prefer
   damaged), team coordination distance (`COORD_WEIGHT=0.15`), and a bonus
   for the shared focus target (`FOCUS_BONUS=2.0`).
3. **Opportunistic attack**: ALWAYS attack an adjacent enemy instead of
   moving, preferring the weakest one (secure kills), regardless of the
   personal/focus target.
4. **Movement**: `direction_to` the personal target, with a sidestep
   fallback trying both perpendiculars then the opposite direction if the
   direct path is blocked (wall/unit) — this already exhaustively checks
   all 4 cardinal directions before giving up (there are only 4
   `Direction` values in this engine).
5. **Spawn-tile escape**: if no enemies are visible, move off spawn tiles
   to avoid the periodic (`every 10 turns`) spawn-tile-clear wipe.

## Closed experiments (do NOT re-litigate without a fundamentally new idea)
- **Weight-constant tuning** (`HEALTH_WEIGHT`, `FOCUS_BONUS`,
  `COORD_WEIGHT`): all three settled at large sample sizes (150-241 games
  each) in Rounds 10 & 12 — all ~50%, i.e. no measurable effect from
  moving these numbers around. Current defaults (0.6 / 2.0 / 0.15) are
  fine, just not proven "optimal" — nobody has found a better set.
- **Overkill-avoidance targeting** (Round 6): explicit penalty for
  over-assigning units to a target already-enough-attackers-away-from-dead.
  Mild negative at 36-game sample. Not adopted.
- **BFS/multi-step pathfinding**: analyzed (Round 5) but not implemented —
  judged low value since the movement fallback already exhaustively tries
  all 4 directions each turn (single-step lookahead is complete given only
  4 possible moves exist), and no match log has ever shown units stuck in
  a multi-turn dead-end.
- **`Action.heal`**: confirmed a hard no-op in `Normal` game mode (traced
  through `logic/logic/src/lib.rs::run_turn` — heal actions are silently
  dropped unless `game_mode == GameMode::NormalHeal`, and nothing in this
  repo's CLI/config ever sets that mode). Don't bother adding heal calls.

## Genuinely still-untried ideas (available if a stronger opponent appears)
- Multi-step (2-3 move) lookahead pathing for escaping dead-ends near the
  map's diamond-shaped wall corners (currently deprioritized, see above).
- Explicit "retreat when badly outnumbered locally" logic for individual
  low-health units — untried, carries real regression risk against the
  current "always attack if adjacent" philosophy that's been winning
  decisively. Only attempt with a large-sample (60+ seed) A/B via
  `tools/ab_test.py`, comparing against BOTH `robot_v1_baseline.py` AND
  the current `robot.py` before committing.

## Tools / how to validate quickly
- `./rumblebot run term --results-only <bot1> <bot2> [--seed N]` — single
  match, ~0.7-1.3s wall-clock. Use to sanity-check no exceptions/crashes.
- `tools/ab_test.py` (persistent harness, added Round 12) — parallelized
  self-play A/B testing:
  ```
  python3 tools/ab_test.py bot_a.py bot_b.py --seeds 1-40 [--swap] [--workers 16]
  ```
  Uses a thread pool to run many matches concurrently (~10x faster than a
  sequential loop on this multi-core machine). `--swap` also runs the
  reverse Blue/Red assignment to check for side bias in one command.
- Win/loss + avg-unit-count snippet for `/logs/rounds/N/`:
  ```
  cd /logs/rounds/<N> && python3 -c "
  import re,glob
  wins=losses=ties=0
  units_us=[]; units_opp=[]
  for f in glob.glob('sim_*.txt'):
      txt=open(f).read()
      if 'Blue won' in txt: wins+=1
      elif 'Red won' in txt: losses+=1
      else: ties+=1
      m = re.findall(r'Units (\d+) (\d+)', txt)
      if m:
          b,r = map(int, m[-1]); units_us.append(b); units_opp.append(r)
  print('Blue wins', wins, 'Red wins', losses, 'ties', ties)
  print('avg blue', sum(units_us)/len(units_us), 'avg red', sum(units_opp)/len(units_opp))
  "
  ```
  Check `results.json`'s `details` field first to know which color
  (`Blue`/`Red`) sonnet-5 actually was that round before interpreting
  wins/losses.
- `robot_v1_baseline.py` is a frozen, untouched copy of the Round-0
  winning bot, kept specifically as a fixed reference point for A/B
  self-play testing — **do not delete or modify it**.

## Recommended workflow for future teammates (每 round)
1. Check `/logs/rounds/N/results.json`'s `details` field for which color
   we were, then run the win/loss + avg-units snippet above.
2. If still dominant (win rate 100%, margin > ~3x): confirm `robot.py` has
   no drift (`git diff HEAD -- robot.py`), run a quick sanity match, run
   `tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap`
   to confirm no regression, and consider this round done — no need to
   change code. Add a short note here (not another 100-line essay —
   just append 5-10 lines under a new "## Round N" heading with the
   opponent name + result + confirmation nothing changed) so trend data
   stays available, then stop.
3. If the win rate or margin ever drops meaningfully (opponent wins a
   round, margin < ~3x, or opponent avg final units trends into double
   digits across multiple consecutive rounds): that's the signal to
   seriously invest in the "still-untried ideas" list above instead of
   validation-only. Full historical rationale for why nothing else has
   worked is preserved in `README_agent_history.md` if you need the
   detailed reasoning behind any of the "closed experiments."

## Round 31 (this session)
Opponent: `tabaxi3k__charles` (new, 18th distinct identity). Round 0:
250/250 sweep for sonnet-5 (Blue), avg units 28.6 vs 1.5 (~19x). Verified
`robot.py` unchanged (clean git diff), sanity match ran clean, A/B vs
`robot_v1_baseline.py` over 40 seeds x2 (swap) gave the usual
26-12-2 / 24-13-3 split (identical to every previous round's check since
no code has changed) — no regression. **Consolidated this file** from
2600+ lines down to this summary (full history preserved in
`README_agent_history.md`) per Round 30's own suggestion, to keep future
sessions' reading overhead manageable. No code changes to `robot.py`.
