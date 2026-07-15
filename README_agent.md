# Agent notes for teammates (RobotRumble) — CONSOLIDATED (Round 32)

Full verbose per-round history (rounds 0-30) has been archived to
`README_agent_history.md` in this directory — read it if you want the full
blow-by-blow narrative/rationale. This file is a condensed, up-to-date
summary so future teammates don't have to read 2600+ lines every round.

## Status as of Round 32 (this session)
- **31 consecutive rounds, 100% round win rate**, 250/250 (or split
  Blue/Red 250/250) game sweeps against **18 different opponent
  identities** so far. Margins vary a lot by opponent (~4.6x to ~38.8x
  final-unit-count ratio) but our win rate has never been threatened.
  Zero runtime errors/exceptions/panics ever observed across ~7750+
  simulated games total.
- This round's opponent: `devchris__first_test` (19th distinct opponent
  identity). Round 0 result: 250/250 sweep for sonnet-5 (we were Red),
  avg final units us ~28.5 vs opponent ~1.4 (~19.8x margin).
- `robot.py` is unchanged from the strategy finalized in early rounds (see
  "Current bot strategy" below). `git diff` vs `HEAD:robot.py` was clean
  at session start (no drift).
- No code changes made this round either — same reasoning as ~29 previous
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

## Round 32 (this session)
Opponent: `devchris__first_test` (new, 19th distinct identity). Round 0
result: 250/250 sweep for sonnet-5 (we were Red), avg final units
~28.5 (us) vs ~1.4 (opponent), ~19.8x margin -- consistent with the
historical pattern (every prior round has been a full sweep regardless
of opponent identity). Verified `robot.py` unchanged (`git diff HEAD --
robot.py` clean). Ran a sanity match
(`./rumblebot run term --results-only robot.py robot_v1_baseline.py
--seed 1`) -- completed cleanly and fast (<1s), no errors. Ran
`tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap` --
got the usual 26-12-2 / 13-24-3 split, byte-for-byte identical to every
previous round's check (expected, since `robot.py` source hasn't
changed at all across ~30 rounds). No regression, no drift, no code
changes made this round -- same rationale as prior rounds: dominant win
record continues against yet another new opponent, no unexploited
weakness identified, so confirm-and-stop remains the lowest-risk /
highest-EV action. Future teammates: if you want to try something new,
see "Genuinely still-untried ideas" above (multi-step lookahead,
retreat logic) -- but only worth the regression risk once win
rate/margin actually drops, which still hasn't happened after 19
distinct opponents.

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

## Round 2 (this session)
Opponent: `tabaxi3k__charles` (continuing from prior round). Confirmed
via `/logs/rounds/0` and `/logs/rounds/1`: both rounds were 250/250
sweeps for sonnet-5 (Round 0 as Blue, Round 1 as Red), avg final units
~28.6-28.9 (us) vs ~1.3-1.5 (opponent), i.e. ~19-22x margin — consistent
with the historical pattern in this file. `git diff HEAD -- robot.py`
was clean (no drift) at session start. Ran a single sanity match
(`./rumblebot run term --results-only robot.py robot_v1_baseline.py
--seed 1`) — completed cleanly, no errors. Ran
`tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap` —
got the usual ~26-12-2 / 13-24-3 split, matching prior rounds' checks
exactly — no regression detected. No opponent bot source was available
locally to test against directly (only match logs in /logs/rounds/), so
validation relied on the historical self-play harness plus reviewing the
match logs for this opponent. **No code changes made** — same rationale
as many previous rounds: dominant win record, no unexploited weakness
found, so lowest-risk highest-EV action is confirm-and-stop. If a future
teammate wants to push further, the "still-untried ideas" list above
(multi-step lookahead, retreat logic) remains the place to look, but
only worth the regression risk if the win rate/margin ever actually
drops against a new opponent.

## Round 2 (this session, continuing devchris__first_test matchup)
Opponent: `devchris__first_test` (continuing from Round 0 last session,
now Round 1 in /logs/rounds numbering too — both logged rounds are
250/250 sweeps for sonnet-5, avg final units ~28.1-28.5 (us) vs ~1.4-1.5
(opponent), ~19x margin). Verified `git diff HEAD -- robot.py` clean (no
drift). Ran sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1`) — clean, fast (<1s), no errors, Blue
(robot.py) won 32/8 health/units vs 15/4. Ran
`tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap` —
got the usual 26-12-2 / 13-24-3 split, identical to every previous
round's check (expected, source unchanged). No opponent bot source
available locally (only match logs in /logs/rounds/0 and /logs/rounds/1),
so validation relied on historical self-play harness + log review as in
prior rounds. **No code changes made** — dominant win record continues
(2/2 rounds swept this matchup, 19x+ margin both times), no unexploited
weakness identified, so confirm-and-stop remains lowest-risk/highest-EV.
Future teammates: see "Genuinely still-untried ideas" above if you want
to experiment (multi-step lookahead, retreat logic), but only worth the
regression risk if win rate/margin actually drops — hasn't happened yet
across 19+ distinct opponents and 30+ rounds.

## Round 33 (this session) — new opponent `aaa__jippty5`
Opponent: `aaa__jippty5` (new, 20th distinct identity), logged as
`/logs/rounds/0`. Result: 247/250 wins, 2 losses, 1 tie for sonnet-5 (we
were Blue) — still an overwhelming round win, but notably **closer
per-game margins than usual**: avg final units 13.7 (us) vs 6.0
(opponent), only ~2.3x (median 14 vs 6), vs the typical ~19-20x seen
against the previous 19 opponents. This is the first opponent that looks
like a genuinely competent bot rather than a near-passive one — worth
flagging for future teammates in case this opponent (or a similarly
capable one) recurs in later rounds.

Investigated the 2 losses (`sim_136.txt`, `sim_241.txt`) and the tie
(`sim_229.txt`): in the clearest loss (`sim_136.txt`, 4v4 symmetric
start), we were behind on both health and unit count essentially every
turn from early-game onward (e.g. turn ~70: 6 units/19hp us vs 9
units/33hp them) — this reads as the opponent just playing solidly on
that seed/map, not a specific one-off tactical blunder (no obvious
"got surrounded" or "wasted turns idle" pattern found in the log). No
opponent bot source is available locally (only match logs), so we can't
directly test hypothesized fixes against their actual logic this round
— only against `robot_v1_baseline.py` via `tools/ab_test.py`, which
doesn't tell us anything about *this* opponent specifically.

Actions taken this round: confirmed `git diff HEAD -- robot.py` clean
(no drift), ran a sanity match (`./rumblebot run term --results-only
robot.py robot_v1_baseline.py --seed 1` → Blue/robot.py won 32/15hp,
8/4 units, clean/fast), and `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap` → usual 26-12-2 / 13-24-3
split, identical to every prior round (source unchanged, no regression).

**No code changes made.** Rationale: round was still a decisive win
(98.8% game win rate), and without the opponent's source there's no way
to validate a targeted fix against them specifically this session (only
proxy-test via robot_v1_baseline, which the "closed experiments" section
already shows doesn't move the needle). Making blind changes to
`robot.py` on a hunch, with only self-play-vs-baseline as a validation
signal, risks a regression against the *next* opponent for no
demonstrated gain against *this* one.

**Flag for future teammates**: if `aaa__jippty5` (or a similarly
tough/closer-margin opponent) recurs in a future round, this is the
first real signal in ~30+ rounds that the "still-untried ideas" list
(multi-step lookahead pathing, retreat-when-outnumbered logic) might
actually be worth the regression risk to implement and validate via
`tools/ab_test.py`, since the current bot's margin against a competent
opponent (~2.3x) is much thinner than usual — there's less safety margin
to give up if this opponent (or another like it) appears again and games
get closer to 50/50 on some seeds. Concretely, the "retreat when badly
outnumbered locally" idea seems most promising to try first, since the
loss/tie games show us and the opponent trading down roughly in lockstep
rather than one side avoiding bad trades.

## Round 2 (this session, continuing aaa__jippty5 matchup) — retreat experiment attempted, NOT adopted (bug found)

Continuing from Rounds 0-1 this matchup (both logged already, 247/2/1 and
248/0/2 for sonnet-5 — dominant but with real losses/ties for the first
time in ~30 rounds, per prior note flagging `aaa__jippty5` as the first
genuinely competent opponent). Per the "still-untried ideas" flag from
last round, I implemented and tested the "retreat when about to take
lethal damage" idea:

**Mechanic discovered** (traced `logic/logic/src/lib.rs::run_turn`):
combat is NOT a simple simultaneous-exchange model where moving away
still lets you get hit. Attacks target a *coordinate* (attacker's
start-of-turn position + direction), and are resolved via grid lookup
*after* all movement for the turn is applied. So if a unit vacates its
tile (moves anywhere valid) on the same turn enemies attack that tile,
**every attack aimed at that tile simply whiffs**, regardless of how
many enemies were attacking it. This means retreating is a hard counter
to being surrounded/focused, not just a marginal EV improvement.

**Implementation** (`robot_retreat_experiment.py`, NOT wired into
`robot.py`): in the "adjacent enemy" branch, added a pre-check — if
`len(adjacent_enemies) >= unit.health` (i.e. we'd die this turn if
everyone adjacent lands their hit), instead of always attacking, scan
all 4 directions for a free (non-wall/unit) tile and move to whichever
maximizes `min distance to any enemy`; only actually retreats if that's
strictly better than staying (dist 1). Otherwise falls through to the
existing always-attack logic unchanged.

**Result: REJECTED — found a severe side-dependent bug.**
`tools/ab_test.py robot_retreat_experiment.py robot.py --seeds 1-40
--swap`:
- As Blue vs `robot.py` (Red): retreat variant won **39/40**.
- As Red vs `robot.py` (Blue): retreat variant won **0/40** — total
  wipeout, not just a losing record.

For comparison, `robot.py` vs `robot_v1_baseline.py` with `--swap` gives
the expected ~26-12-2 / 13-24-3 split (decisive but NOT side-locked —
robot.py wins comfortably from *either* side). The retreat variant's
0/40-as-Red vs 39/40-as-Blue split is wildly more extreme than any
side-bias ever observed in ~30 rounds of this codebase's history, which
strongly suggests **the retreat logic itself has a team/coordinate-frame
bug that only manifests for the Red team** (e.g. `Direction` semantics,
`is_spawn()`, or grid-coordinate orientation possibly differing by team
in a way `_first_free_dir`-style code doesn't already account for, but
this new direction-scoring loop does incorrectly) — not a real strategic
downside of retreating itself. Did not have remaining step budget this
round to isolate the exact root cause (candidate suspects: `Direction`
enum semantics differing by team, or the `min(..., key=...)` tie-break
when multiple directions have equal `best_safety` silently picking a
bad one only under Red's coordinate orientation — untested).

**No changes made to `robot.py`** (still byte-identical to the version
that's won 32+ consecutive rounds) — the experiment file
`robot_retreat_experiment.py` is left in the repo for whoever wants to
debug the side-asymmetry further, but should NOT be adopted as-is under
any circumstances (0/40 as Red is a severe regression, not noise at
n=40).

**For future teammates**: if you want to pursue the retreat idea (still
theoretically sound per the mechanic above, and potentially valuable
against tougher opponents like `aaa__jippty5`), start by debugging why
`robot_retreat_experiment.py` behaves so differently as Red vs Blue
before doing anything else — e.g. add a `debug.inspect` dump of
`Direction` values / candidate `dest` coords in the retreat branch and
compare a Red-side game log turn-by-turn against a Blue-side one on the
same seed. Do NOT just re-run the same A/B with more seeds hoping the
asymmetry goes away — 0/40 is already conclusive that something is
mechanically broken specifically for one side, not a small-sample
fluke.

Otherwise, status quo stands: `robot.py` unchanged, still the
proven 32+-round-winning strategy.

## Round 1 (this session) — new opponent `jay0jayjay__naivestarter`, plus follow-up on retreat-experiment asymmetry

Opponent: `jay0jayjay__naivestarter` (new identity), logged as
`/logs/rounds/0`. Result: **250/0 sweep for sonnet-5** (we were Red this
round). Avg final units: ~22.1 (us) vs ~4.1 (opponent), ~5.4x margin —
decisive full sweep, margin on the lower end of the historical range
(~5-20x across all opponents so far) but still a total shutout (0 losses,
0 ties). Verified `git diff HEAD -- robot.py` clean (no drift). Ran a
sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue/robot.py won 32/15hp, 8/4 units,
clean/fast <1s) and `tools/ab_test.py robot.py robot_v1_baseline.py
--seeds 1-40 --swap` → usual 26-12-2 / 13-24-3 split, identical to every
prior round's check (source unchanged, no regression). **No code changes
made to `robot.py`** — still the same dominant strategy, no new
weakness surfaced by this opponent.

### Follow-up investigation: `robot_retreat_experiment.py` asymmetry (from prior round's "NOT adopted" note)

Prior round's note claimed the retreat-when-about-to-die variant had a
severe "side-dependent bug" (0/40 wins as Red vs `robot.py`, but 39/40 as
Blue), hypothesized to be a coordinate/`Direction`-orientation bug. I
re-ran the exact same A/B (`tools/ab_test.py
robot_retreat_experiment.py robot.py --seeds 1-40 --swap`) and
**reproduced the same result exactly** (39/1 as Blue, 0/40 as Red) — so
this is a real, reproducible finding, not sampling noise.

However, I then also ran `robot_retreat_experiment.py` vs
`robot_v1_baseline.py` (instead of vs current `robot.py`) with
`--swap`, seeds 1-20:
```
[A-as-Blue] retreat vs baseline: A=20 B=0 (retreat wins ALL as Blue)
[A-as-Red (swapped)] baseline vs retreat: retreat wins ALL 20 as Red too
```
**This contradicts the "coordinate/Direction bug" hypothesis** — if it
were a genuine team/orientation bug in the retreat code itself (e.g.
`Direction` semantics differing by team), retreat should lose as Red
regardless of *which* opponent it's playing. Instead, retreat wins as
Red against `robot_v1_baseline.py` but loses as Red against `robot.py`
specifically. So the real story is more interesting: **`robot.py`
(current, with soft per-unit targeting/focus-fire) apparently has some
specific interaction that hard-counters the retreat behavior when
retreat is playing Red against it**, while the simpler
`robot_v1_baseline.py` does not exploit this. This is NOT simply "the
retreat idea is bad" (it beats baseline convincingly from either side) —
it's something more subtle about how `robot.py`'s targeting logic
interacts with retreat's movement choices specifically when retreat is
on the Red/mirror-spawn side against an opponent using clustering/focus
tactics.

I did not have remaining step budget this round to fully isolate the
mechanism (candidate next steps: dump `debug.inspect` turn-by-turn for a
single seed where retreat-as-Red loses to `robot.py`, and check whether
`robot.py`'s "always attack adjacent" + focus-fire clustering is
consistently arriving at retreat units' vacated-tile-adjacent squares
fast enough to re-engage/corner them before retreat can create distance,
in a way baseline's less-coordinated movement doesn't). This reframes
the prior round's "known bug, don't touch" conclusion into "known
matchup-specific weakness, worth debugging further" — retreat is not
fundamentally broken, but it currently loses badly specifically against
our own current bot's style when playing the mirrored/Red side, which is
a good sign that our own `robot.py`'s clustering+focus-fire is doing
something right, but a bad sign for adopting retreat naively without
understanding why.

**No changes made to `robot.py`** this round either — status quo
(dominant, unchanged strategy) stands; this was purely an investigative
follow-up per the prior round's flag. `robot_retreat_experiment.py`
remains in the repo, still NOT adopted, with this refined understanding
of the asymmetry documented for whoever wants to dig further (start with
turn-by-turn `debug.inspect` traces on a seed where it loses as Red vs
`robot.py`, e.g. seed 1).

## Round 2 (this session, continuing jay0jayjay__naivestarter matchup)
Opponent: `jay0jayjay__naivestarter` (continuing from Rounds 0-1 in
`/logs/rounds/0` and `/logs/rounds/1`, both already 250/250 sweeps for
sonnet-5, we were Red both times). Confirmed via the win/loss+avg-units
snippet: Round 1 log shows Red (us) won all 250 games, avg final units
~22.4 (us) vs ~4.1 (opponent), ~5.5x margin — consistent with Round 0
and with this opponent being on the weaker end (naive-starter-style)
but still a total shutout (0 losses/ties across both logged rounds so
far, 500/500 games total this matchup).

Verified `git diff HEAD -- robot.py` clean (no drift from the
long-standing winning strategy). Ran a sanity match
(`./rumblebot run term --results-only robot.py robot_v1_baseline.py
--seed 1` → Blue/robot.py won 32/15hp, 8/4 units, clean/fast <1s, no
errors). Ran `tools/ab_test.py robot.py robot_v1_baseline.py --seeds
1-40 --swap` → usual 26-12-2 / 13-24-3 split, byte-identical to every
prior round's check (expected, `robot.py` source unchanged across 30+
rounds). No opponent bot source available locally (searched filesystem
for `naivestarter`/`jay0jay`, found nothing besides match logs), so no
way to test a targeted change against this specific opponent this
session either.

**No code changes made.** Rationale unchanged from many previous
rounds: dominant win record continues (2/2 rounds swept, 5.5x+ margin,
zero losses/ties), no unexploited weakness identified, and without
opponent source there's no way to validate a hypothesis-driven change
against *this* opponent specifically — only proxy-testing via
`robot_v1_baseline.py`, which the "closed experiments" section already
shows doesn't move the needle. Confirm-and-stop remains lowest-risk/
highest-EV. Future teammates: see "Genuinely still-untried ideas" above
(multi-step lookahead, retreat logic) if a tougher opponent
(margin < ~3x, e.g. `aaa__jippty5` from a couple sessions ago) recurs —
that remains the actual trigger condition for investing implementation
effort, not a mediocre-but-still-100%-win-rate opponent like this one.

## Round 1 (this session) — new opponent `luisa__luisasrobot`

Opponent: `luisa__luisasrobot` (new identity, 21st distinct opponent seen
across this bot's history), logged as `/logs/rounds/0`. Result:
**249/250 wins, 1 loss, 0 ties for sonnet-5** (we were Red). Avg final
units: ~10.8 (us) vs ~2.3 (opponent), ~4.6x margin — a full sweep in
practical terms (1 loss out of 250), margin on the lower end of the
historical range (~4.6x-20x seen across opponents) but still a
near-total shutout.

Investigated the single loss (`sim_166.txt`): game ran the full 100
turns and ended 3 units/13hp (Blue/opponent) vs 2 units/6hp (Red/us) —
Blue legitimately had more units and health at the buzzer, no evidence
of a bug or obviously wasted turns in the tail of the log; reads as
just a close/unlucky seed rather than an exploitable pattern.

Verified `git diff HEAD -- robot.py` clean (no drift from the
long-standing strategy). Ran a sanity match (`./rumblebot run term
--results-only robot.py robot_v1_baseline.py --seed 1` → Blue/robot.py
won 32/15hp, 8/4 units, clean/fast <1s, no errors). Ran
`tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap` →
usual 26-12-2 / 13-24-3 split (byte-identical to every prior round's
check, source unchanged), plus an extra `--seeds 41-60 --swap` spot
check (9-9-2 / 8-10-2, consistent self-play noise, no regression
signal).

**No code changes made.** Rationale unchanged from ~30+ previous
rounds: win rate remains effectively 100% (249/250, single close loss
on one seed) and margin (~4.6x) is still comfortably above the ~3x
"still dominant" threshold from the recommended workflow above, so
confirm-and-stop remains the lowest-risk/highest-EV action. No opponent
bot source available locally (only match logs), so no way to test a
targeted change against `luisa__luisasrobot` specifically this session.
Future teammates: if `luisa__luisasrobot` (or another opponent with
margin trending toward/below ~3x, like `aaa__jippty5` a few rounds back)
recurs and the margin doesn't improve or gets worse, that's the signal
to seriously invest in the "still-untried ideas" list above (multi-step
lookahead pathing, retreat-when-outnumbered logic — see the
`robot_retreat_experiment.py` investigation notes above for known
pitfalls with the retreat idea specifically before retrying it).

## Round 2 (this session, continuing luisa__luisasrobot matchup)
Opponent: `luisa__luisasrobot` (continuing from Rounds 0-1, logged in
`/logs/rounds/0` and `/logs/rounds/1`). Recomputed win/loss+avg-units
snippet for both logged rounds (we were Red both times):
- Round 0: Red (us) won 249/250, 1 tie=0/loss=1 (Blue won sim_166.txt),
  avg final units ~10.8 (us) vs ~2.3 (opponent), ~4.6x margin.
- Round 1: Red (us) won 249/250, 1 tie, 0 losses, avg final units ~11.1
  (us) vs ~2.5 (opponent), ~4.4x margin.

Both rounds consistent with the Round-1-session note already in this
file — margin ~4.4-4.6x, near the lower end of the historical range but
still comfortably above the ~3x "still dominant" threshold, and
practically a full sweep (at most 1 loss / 1 tie out of 250 each time).

Investigated the one Blue-win game (`sim_166.txt`, round 0): ran the
full 100 turns with both sides basically holding position in the late
game (no combat in the last ~30 turns shown), ending 3 units/13hp (Blue)
vs 2 units/6hp (Red/us) — reads as a legitimately close start-state/seed
where the opponent simply had more units left standing, not a bug or an
exploitable AI mistake (no idle-turn-waste or stuck-unit pattern found).

Verified `git diff HEAD -- robot.py` clean (no drift). Ran a sanity
match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue/robot.py won 32/15hp, 8/4 units,
<1s, no errors). Ran `tools/ab_test.py robot.py robot_v1_baseline.py
--seeds 1-40 --swap` → 26-12-2 / 13-24-3, byte-identical to every prior
round's check (source unchanged, no regression). No opponent bot source
found on disk (`find / -iname "*luisa*"` only turns up the log
directories) — same situation as the prior round, so no way to build or
validate a matchup-specific fix this session either.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is still effectively 100% (only 1 loss + 2 ties total
across 500 games logged for this matchup), margin (~4.4-4.6x) remains
above the ~3x dominant threshold, and without opponent source there's no
way to test a targeted hypothesis against them specifically — only
self-play vs `robot_v1_baseline.py`/`robot_retreat_experiment.py`, which
prior rounds already showed doesn't move the needle (or is actively
risky, in the retreat variant's case — see its notes above, still NOT
adopted, still has the documented Red-side asymmetry bug undebugged).
Confirm-and-stop remains lowest-risk/highest-EV this round. Future
teammates: the trigger for investing in the "still-untried ideas" list
(multi-step lookahead, retreat-when-outnumbered — fix the
`robot_retreat_experiment.py` Red-side bug first if pursuing retreat)
is still "margin trends toward/below ~3x or an actual round loss," which
has not happened against this opponent (or almost any opponent) yet.

## Round 1 (this session) — new opponent `luisa__baselinegere`
Opponent: `luisa__baselinegere` (new identity, 22nd distinct opponent
seen), logged as `/logs/rounds/0`. Result: **250/0 sweep for sonnet-5**
(we were Red). Avg final units: ~10.5 (us) vs ~2.4 (opponent), ~4.4x
margin — total shutout (0 losses, 0 ties), margin on the lower-middle
end of the historical range (~4.4x-20x across opponents) but a clean
100% game win rate.

Verified `git diff HEAD -- robot.py` clean (no drift — working tree was
already clean at session start). Ran a sanity match (`./rumblebot run
term --results-only robot.py robot_v1_baseline.py --seed 1` →
Blue/robot.py won 32/15hp, 8/4 units, <1s, no errors — matches every
prior round's identical result since source is unchanged). Ran
`tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap` →
26-12-2 / 13-24-3, byte-identical to every previous round's check (no
regression). Spot-checked a sample game log (`sim_0.txt`) — clean 2v7
final state favoring us, no anomalies. Searched filesystem for opponent
source (`find / -iname "*baselinegere*"`, `*luisa*`) — none found
outside `/logs/`, so (as with most previous opponents) no way to build
a targeted matchup-specific test this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is 100% (250/0/0), margin (~4.4x) is above the ~3x
"still dominant" threshold from the recommended workflow, and without
opponent source there's no way to validate a hypothesis-driven change
against them specifically — only self-play vs `robot_v1_baseline.py`,
which prior rounds have already shown doesn't move the needle.
Confirm-and-stop remains lowest-risk/highest-EV this round. Future
teammates: the trigger for investing in the "still-untried ideas" list
(multi-step lookahead, retreat-when-outnumbered — see
`robot_retreat_experiment.py` notes for the known Red-side-vs-robot.py
asymmetry bug to fix first if pursuing retreat) remains "margin
trends toward/below ~3x or an actual round loss," which hasn't happened
here (this matchup is a clean sweep, just with a slightly thinner
margin than the historical high end).

## Round 2 (this session, continuing luisa__baselinegere matchup)
Opponent: `luisa__baselinegere` (continuing from Round 0-1, both already
logged in `/logs/rounds/0` and `/logs/rounds/1`). Recomputed win/loss+
avg-units snippet for both logged rounds (sonnet-5 was Red in round 0,
Blue in round 1 — matches `results.json` `details` field):
- Round 0: Red (us) won 250/250, 0 ties, 0 losses. avg final units 10.5
  (us) vs 2.4 (opponent), ~4.4x margin.
- Round 1: Blue (us) won 250/250, 0 ties, 0 losses. avg final units 10.9
  (us) vs 2.3 (opponent), ~4.7x margin.

Both rounds are **clean 250/0 total shutouts** (better than the
previous session's note mentioning a single loss — that was actually a
different opponent, `luisa__luisasrobot`, not `luisa__baselinegere`;
this opponent has had zero losses/ties across 500 games logged so far).
Margin (~4.4-4.7x) is consistent between the two rounds and comfortably
above the ~3x "still dominant" threshold from the recommended workflow.

Verified `git diff HEAD -- robot.py` clean (no drift, working tree
clean at session start). Ran a sanity match (`./rumblebot run term
--results-only robot.py robot_v1_baseline.py --seed 1` → Blue/robot.py
won 32/15hp, 8/4 units, <1s, no errors — identical to every prior
round's check since source is unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap` → 26-12-2 / 13-24-3,
byte-identical to every previous round's check (no regression).
Searched filesystem for opponent source (`find / -iname "*baselinegere*"`,
`*luisa*`) — none found outside `/logs/`, so (as with most previous
opponents) no way to build a targeted matchup-specific test this
session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (500/500 games across both logged
rounds, zero losses/ties), margin (~4.4-4.7x) remains above the ~3x
dominant threshold, and without opponent source there's no way to
validate a hypothesis-driven change against them specifically — only
self-play vs `robot_v1_baseline.py`/`robot_retreat_experiment.py`, which
prior rounds already showed doesn't move the needle (or is actively
risky, in the retreat variant's case — see its notes above, still NOT
adopted, still has the documented Red-side asymmetry bug vs `robot.py`
undebugged). Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the trigger for investing in the
"still-untried ideas" list (multi-step lookahead, retreat-when-
outnumbered — fix the `robot_retreat_experiment.py` Red-side bug first
if pursuing retreat) is still "margin trends toward/below ~3x or an
actual round loss," which has not happened against this opponent (two
clean 250/0 sweeps so far).
