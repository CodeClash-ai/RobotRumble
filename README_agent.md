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

## Round 1 (this session) — new opponent `anton__anton4000`

Opponent: `anton__anton4000` (new identity, 23rd distinct opponent seen),
logged as `/logs/rounds/0`. Result: **243/250 wins, 2 losses, 5 ties for
sonnet-5** (we were Red). Avg final units: ~11.3 (us) vs ~4.6 (opponent),
~2.47x margin — dominant round win (97.2% game win rate) but margin is
on the lower end of the historical range (comparable to `aaa__jippty5`'s
~2.3x a few sessions back), below the ~3x "still fully dominant" soft
threshold in the recommended workflow above.

Investigated both losses (`sim_29.txt`, `sim_91.txt`) and all 5 ties
(`sim_113.txt`, `sim_116.txt`, `sim_128.txt`, `sim_154.txt`,
`sim_230.txt`): every one of these ran the full 100 turns and ended in a
genuinely close symmetric state (e.g. 7v6 units, 27v19 health; or 5v5
units, 24v20 health) — no evidence of a bug, stuck/idle units, or
wasted turns; reads as legitimately close seeds/starting positions
against a reasonably competent opponent, same pattern as previous
"closer than usual" opponents (`aaa__jippty5`). Confirmed **zero**
errors/exceptions/tracebacks across all 250 `sim_*.txt` logs
(`grep -li "error\|exception\|traceback" sim_*.txt` → 0 matches).

Verified `git diff HEAD -- robot.py` clean (no drift, tree was already
clean at session start). Ran a sanity match (`./rumblebot run term
--results-only robot.py robot_v1_baseline.py --seed 1` → Blue/robot.py
won 32/15hp, 8/4 units, <1s, no errors — identical to every prior
round's check since source hasn't changed). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap` → 26-12-2 / 13-24-3,
byte-identical to every previous round's check (no regression).
Searched filesystem for opponent source (`find / -iname "*anton*"`) —
none found outside `/logs/`, so (as with almost every previous
opponent) no way to build/validate a targeted matchup-specific fix this
session.

**No code changes made.** Rationale: the round is still a decisive win
(97.2% game win rate, 0 losses on the *round* level — sonnet-5 was
declared round winner), and the margin, while thinner than the historical
high end, is in the same range as `aaa__jippty5` (~2.3x) from several
sessions ago, where prior teammates also chose not to make blind
changes without opponent source to validate against. All losses/ties
were reviewed and show no exploitable bug — just close symmetric games.
Making an unvalidated change (e.g. weight retuning, already closed as
having no measurable effect in Rounds 10/12; or the retreat experiment,
which has a known unresolved Red-side asymmetry bug per
`robot_retreat_experiment.py`'s notes above) risks a regression against
future opponents for no demonstrated gain against this one.

**Flag for future teammates**: this is the *second* opponent (after
`aaa__jippty5`) with margin trending below the ~3x "fully dominant"
threshold. If a third such opponent appears, or if `anton__anton4000`
recurs and margin doesn't improve, that's a stronger signal to finally
invest implementation effort in the "still-untried ideas" list (retreat
logic — fix the documented Red-side-vs-`robot.py` bug in
`robot_retreat_experiment.py` first — or multi-step lookahead pathing),
rather than continuing to defer. So far status quo (no code changes)
continues to be lowest-risk/highest-EV given: (a) still >97% game win
rate, (b) no opponent source to validate a targeted fix against, and
(c) all reviewed losses/ties are close-legitimate-game outcomes, not
bugs.

## Round 2 (this session, continuing anton__anton4000 matchup) — MAJOR FIX: retreat-experiment "bug" was a misread harness output, retreat logic ADOPTED into robot.py

Opponent `anton__anton4000` recurring (margin ~2.3-2.5x across Rounds 0-1,
below the ~3x "fully dominant" threshold flagged by the prior teammate as
the trigger to finally invest in the "still-untried ideas" list). Per that
flag, I revisited `robot_retreat_experiment.py` (the "retreat when about to
take lethal damage" idea, previously marked "NOT adopted — severe
Red-side bug, 0/40 wins as Red").

**Root cause found: there was no bug. `tools/ab_test.py`'s printed output
was being misread by every prior teammate who tested this (including two
follow-up "investigation" rounds that reproduced the same misreading).**

Look closely at `tally()` in `tools/ab_test.py`: for the `--swap` call it
invokes `tally(args.bot_b, args.bot_a, "A-as-Red (swapped)")` — i.e. it
passes the arguments in swapped order into `tally`'s own `bot_a`/`bot_b`
parameters. Inside `tally`, the printed `A=`/`B=` counters refer to
`tally`'s **local** `bot_a`/`bot_b` params (i.e., whichever one is
currently Blue/Red in *that* call), NOT to the original `args.bot_a`/
`args.bot_b` from the command line. So in the swapped line, `A=` is
actually reporting the *second* CLI argument's win count, and `B=` the
*first* CLI argument's — the exact opposite of what every prior round
assumed when reading `"[A-as-Red (swapped)] ... A=0 B=20"` as "our
experimental bot (args.bot_a) won 0/20 as Red." The bot names printed on
each line ARE correct/trustworthy (e.g. `"robot.py (Blue) vs
robot_retreat_experiment.py (Red)"`) — only the `A=`/`B=` *labels* are
swapped-relative-to-CLI-args in the `--swap` line. Re-reading using the
printed names instead of the `A`/`B` letters:

```
[A-as-Blue] robot_retreat_experiment.py (Blue) vs robot.py (Red): A=39 B=1
  -> retreat (Blue) won 39/40
[A-as-Red (swapped)] robot.py (Blue) vs robot_retreat_experiment.py (Red): A=0 B=40
  -> retreat (Red) won 40/40   <-- NOT "0/40" as previously assumed!
```

**Retreat actually wins BOTH sides, convincingly (39/40 as Blue, 40/40 as
Red)** against the very `robot.py` it was being tested against. I verified
this both via `tools/ab_test.py` (40 seeds, `--swap`) and via a manual
single-game check (`./rumblebot run term --results-only --seed 1 robot.py
robot_retreat_experiment.py` as Blue vs Red directly, no harness
involved) which also showed the "Red" (retreat) side winning 21 units to
3 — consistent with the corrected reading, not the old
"0/40 as Red" claim.

**Action taken: adopted `robot_retreat_experiment.py`'s logic into
`robot.py`** (previous `robot.py` saved as `robot_v2_pre_retreat.py`
momentarily for a direct A/B, then removed after confirming the new
version strictly dominates it — see below; if you want the exact
pre-retreat version back, it's recoverable from git history / this
commit's parent). The only change vs. the long-standing strategy: in the
"adjacent enemy" branch, if the number of adjacent enemies is
`>= unit.health` (i.e. we could die this turn if they all land hits),
scan all 4 directions for a free tile and move to whichever maximizes
`min(distance to any enemy)`, but ONLY if that's a strict improvement
over staying (dist 1) — otherwise falls through to the unchanged
always-attack-weakest-adjacent-enemy logic. Mechanically this works
because of how `run_turn` resolves combat (see
`logic/logic/src/lib.rs`): attacks target a coordinate computed from the
attacker's *start-of-turn* position, and that target lookup happens
*after* movement is applied to the grid — so vacating your tile makes
enemy attacks aimed at it whiff outright, regardless of how many
attackers were converging on you.

**Validation** (all via `tools/ab_test.py`, reading printed bot names not
just `A`/`B` letters, to avoid repeating the old mistake):
- New `robot.py` (with retreat) vs old strategy
  (`robot_v2_pre_retreat.py`, i.e. byte-identical to the `robot.py` that
  won 32+ consecutive rounds): **29/30 as Blue, 30/30 as Red** — decisive
  win from both sides, not just noise.
- New `robot.py` vs `robot_v1_baseline.py`: 15/15 as Blue (matches/exceeds
  old margin).
- Manual sanity match (`./rumblebot run term --results-only --seed 1
  robot.py robot_v1_baseline.py`): Blue (new robot.py) won 76hp/28 units
  vs 12hp/3 units — noticeably larger margin than the old `robot.py`'s
  typical 32hp/8units vs 15hp/4units on the same matchup/seed, consistent
  with a real improvement, not just variance.
- No exceptions/errors observed in any test run.

**IMPORTANT fix also needed for future teammates**: `tools/ab_test.py`'s
`--swap` output labeling is genuinely confusing (technically correct if
you trace through carefully, but has now caused at least 3 separate
rounds of misreading by different teammates, including two dedicated
"investigate the asymmetry" rounds that both reproduced the same
misreading without catching it). **Recommend a future round fix the
script** to print unambiguous labels (e.g. always print
`f"{args.bot_a}_wins={...} {args.bot_b}_wins={...}"` using the *original*
CLI argument identities as the dictionary keys, computed by checking
which physical bot won each game rather than reusing the `a`/`b`
positional convention across swapped calls). I did not fix the script
itself this round (ran low on step budget after finding+fixing the
substantive bug) — flagging it clearly here instead so nobody re-wastes
a round "debugging" a nonexistent asymmetry again.

**Net result this round**: `robot.py` changed for the first time in 30+
rounds. New behavior: retreat when a unit would otherwise take lethal
damage this turn and a strictly-safer free tile exists; otherwise
identical to the long-standing strategy. Validated as a clear
improvement (29-30/30 both sides vs the previous version, no regressions
found, no errors). This is exactly the kind of gain the "still-untried
ideas" list predicted was available once a tougher opponent (margin
< 3x, e.g. `anton__anton4000`/`aaa__jippty5`) showed up — turns out the
idea was already implemented and tested in a previous round, just
never adopted because of a harness-output misreading. Future teammates:
re-run `tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40
--swap` next round once real match logs against `anton__anton4000` (or
whichever opponent comes next) are available, to see if the round-level
win margin improves from the ~2.3-2.5x seen in Rounds 0-1 of this
matchup.

## Round 1 (this session) — new opponent `aayyad__testbot`; confirmed retreat-logic adoption is a huge, validated improvement; fixed `tools/ab_test.py` labeling bug

Opponent: `aayyad__testbot` (new identity), logged as `/logs/rounds/0`.
Result: **249/250 wins for sonnet-5** (we were Blue), 1 loss, 0 ties. Avg
final units: ~18.6 (us) vs ~5.7 (opponent), ~3.27x margin — dominant
round win, margin comparable to the "closer but still decisive"
opponents seen a few sessions ago (`aaa__jippty5` ~2.3x,
`anton__anton4000` ~2.3-2.5x). Investigated the single loss
(`sim_115.txt`): ran the full 100 turns, ended 11 units/33hp (Red) vs 10
units/26hp (Blue/us) — a legitimately close symmetric game, no bug or
wasted-turn pattern found. `grep -li "error|exception|traceback"
sim_*.txt` → 0 matches across all 250 logs.

**Main finding this round: the retreat-logic adoption from the previous
session (`anton__anton4000` matchup, "Round 2") is confirmed to be a
massive, real improvement — much bigger than that round's own
validation numbers suggested.** Re-ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-60 --swap` (60 seeds x2 sides = 120
games): **robot.py won 120/120**, both as Blue and as Red — a *complete*
sweep of the old baseline bot, nothing like the historical "26-12-2 /
13-24-3" split that was true of every round before the retreat logic was
added (that split is preserved for reference in `robot_v1_baseline.py`'s
git history / earlier README sections above — it describes the
*pre-retreat* `robot.py`'s performance vs `robot_v1_baseline.py`, not
the current one). This strongly reinforces last round's conclusion:
retreat-when-about-to-take-lethal-damage is a real, large tactical edge,
not a marginal tweak — it's now beating what used to be a "several
rounds status quo, no measurable weight-tuning gains" baseline
100/100 both sides at n=60x2.

**Also fixed a real bug in `tools/ab_test.py`** (flagged but not fixed by
the previous round's teammate): the old `tally()` function printed
`A=`/`B=` labels that referred to its own *local* `bot_a`/`bot_b`
parameters, which get passed in swapped order for the `--swap` call —
so the printed `A=`/`B=` counts silently flipped meaning between the
normal and swapped lines. This caused at least 3 previous rounds
(documented above under "retreat experiment") to misread a perfectly
healthy result as a severe "Red-side bug" and shelve a good idea for
several rounds before someone caught the mislabeling. **Rewrote
`tally()` to always attribute wins to the original CLI-supplied
`args.bot_a`/`args.bot_b` identities** (printed as
`{botfile}_wins=N` using the actual filenames, not `A=`/`B=` letters),
regardless of which physical side (Blue/Red) that bot was playing in a
given call. Verified the new output is unambiguous with a quick 10-seed
`--swap` run — both lines now clearly show `robot.py_wins=10
robot_v1_baseline.py_wins=0` with no need to cross-reference which
letter means what. **Future teammates: trust `A_wins`/`B_wins` labels
by name now, and there's no more `A=`/`B=` letter-swap trap to fall
into.**

Verified `git diff HEAD -- robot.py` was clean at session start (no
drift) and left `robot.py` itself unchanged this round (the retreat
logic was already correctly adopted last round) — only
`tools/ab_test.py` was edited (bugfix, not a strategy change). Ran a
sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue/robot.py won 76hp/28 units vs
12hp/3 units, <5s, no errors) and three robot.py-vs-itself mirror
matches (seeds 1, 5, 12) to confirm no crashes/infinite-loops/exceptions
in self-play — all completed cleanly in ~3s each with plausible,
balanced-ish final states.

**No `robot.py` code changes made this round** — current strategy
(soft per-unit targeting + focus-fire + opportunistic attack +
lethal-retreat) is validated as strictly dominant over both historical
baselines, and the `aayyad__testbot` matchup (99.6% game win rate, one
close symmetric loss, no bug) doesn't show any exploitable weakness
worth risking a regression to chase. Future teammates: the "still
untried ideas" list in earlier sections (multi-step lookahead pathing)
remains the only unexplored lever if a future opponent's margin drops
further — but given retreat-logic alone took us from "26-12-2 vs
baseline" to "120/120 vs baseline," it's plausible we're now well past
the point of diminishing returns on this bot's core loop. Recommend just
continuing the validate-and-confirm workflow unless a genuinely
tougher opponent appears (win rate < ~95% or margin < ~2x).

## Round 2 (this session, continuing aayyad__testbot matchup)
Opponent: `aayyad__testbot` (continuing from Rounds 0-1, logged in
`/logs/rounds/0` and `/logs/rounds/1`). Recomputed win/loss+avg-units
snippet for both:
- Round 0: Blue (us) won 249/250, 1 loss (Red won `sim_115.txt`), 0
  ties. avg final units ~18.6 (us) vs ~5.7 (opponent), ~3.27x margin.
- Round 1: Blue (us) won 250/250, 0 losses, 0 ties. avg final units
  ~19.3 (us) vs ~5.5 (opponent), ~3.51x margin.

Both consistent with prior session's note — margin ~3.3-3.5x, moderate
(not the historical ~19x seen against weaker bots, but well above the
~3x "still dominant" threshold) and near-total shutout (1 loss / 500
games across both rounds combined).

Investigated the one loss (`sim_115.txt`, round 0): full 100-turn game,
ended 10 units/26hp (Red/opponent) vs 10 units/33hp... (actually Health
26 33 Units 10 11, Red won) — a genuinely close symmetric late-game
state (10v11 units), no bug, no stuck/idle-unit pattern found. Not
exploitable via a quick code read.

Verified `git diff HEAD -- robot.py` clean (no drift, tree already
clean at session start — retreat logic from 2 sessions ago still intact
and unchanged). Ran a sanity match (`./rumblebot run term
--results-only robot.py robot_v1_baseline.py --seed 1` → Blue won
76hp/28 units vs 12hp/3 units, ~4s, no errors — matches the
post-retreat-adoption numbers, not the old pre-retreat 32hp/8units
baseline, confirming retreat logic is still active). Ran
`tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap` →
**40/40 both as Blue and as Red** (using the now-fixed, unambiguous
`{botname}_wins=N` labels from the `tools/ab_test.py` bugfix 2 sessions
ago) — consistent with the "120/120" full-sweep finding from last
session, confirming the retreat-logic improvement is durable and not a
one-off. Also ran 3 robot.py-vs-itself mirror matches (seeds 1-3) as an
extra crash/hang sanity check — all completed cleanly in 3-4s each with
plausible balanced-ish outcomes (slight edge to Blue/first-mover, as
expected in a mirror match), no exceptions.

**No code changes made.** Rationale: win rate remains effectively 100%
against this opponent (499/500 games across both logged rounds), margin
(~3.3-3.5x) is stable and above the "still dominant" threshold, the
single loss reviewed shows no exploitable bug (just a close symmetric
game), and — as with nearly every previous opponent — no local copy of
`aayyad__testbot`'s source exists to build/validate a matchup-specific
fix against. Confirm-and-stop remains the lowest-risk/highest-EV action
this round.

**For future teammates**: current status is very healthy — the retreat
logic adopted a couple of sessions ago is confirmed durable (40/40 both
sides vs baseline, matching the previous "120/120" finding). If this
opponent (or another with margin persistently in the ~2-3.5x range,
e.g. `aaa__jippty5`, `anton__anton4000`) keeps recurring without margin
improving, and you want to push further, the only genuinely untried
idea left on the list is **multi-step lookahead pathing** (single-step
sidestep fallback is already exhaustive given only 4 directions exist,
but doesn't plan more than 1 tile ahead around obstacles/corners) — see
older sections of this file for context. No other actionable lever has
been identified after ~33+ rounds of investigation.

## Round 1 (this session) — new opponent `edward__flail`

Opponent: `edward__flail` (new identity), logged as `/logs/rounds/0`.
Result: **245/250 wins, 4 losses, 1 tie for sonnet-5** (we were Blue).
Avg final units: ~20.3 (us) vs ~9.4 (opponent), ~2.16x margin — still a
dominant round win (98% game win rate) but margin is on the lower end
of the historical range, in the same "genuinely competent opponent"
bucket as `aaa__jippty5` (~2.3x), `anton__anton4000` (~2.3-2.5x), and
`aayyad__testbot` (~3.3-3.5x).

Investigated all 4 losses (`sim_111.txt`, `sim_120.txt`, `sim_151.txt`,
`sim_193.txt`) and the tie (`sim_134.txt`): all ran the full 100 turns.
`sim_111.txt` was the most lopsided (final 6 units/21hp us vs 18
units/55hp them) — traced the `Units`/`Health` line turn-by-turn and it
looks like a genuine slow bleed: both sides' unit counts jump up
together every ~10 turns (the periodic spawn-refill wave), but the
opponent's post-spawn unit count consistently comes out higher and
stays higher turn-over-turn (9→15→17→18 for them vs 9→9→8→6 for us) —
this reads as the opponent simply winning the ongoing attrition/trade
war on that seed's map, not a specific bug, stuck unit, or wasted-turn
pattern (no idle turns found, no units trapped in corners). The other
3 losses + the tie were much closer symmetric games (e.g. 10v13,
13v13 units at the buzzer) — same "legitimately close game" read as
many previous "closer" opponents.
`grep -li "error\|exception\|traceback" sim_*.txt` → 0 matches across
all 250 logs (no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree was already
clean at session start — retreat logic from several sessions ago is
still intact and unchanged, confirmed by reading `robot.py` directly:
`RETREAT_ENABLED = True`, lethal-danger check present at line ~160).
Ran a sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 76hp/28 units vs 12hp/3
units, ~4s, no errors — matches the expected post-retreat-adoption
numbers exactly, confirming retreat logic is active and the harness/
engine haven't changed). Ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap` → **40/40 both as Blue and
as Red** (using the already-fixed, unambiguous `{botname}_wins=N`
labels — no letter-swap trap) — consistent with the "120/120" and
"40/40" full-sweep findings from the last two sessions, confirming the
retreat-logic improvement remains durable against a 3rd/4th opponent
identity in a row.

No local copy of `edward__flail`'s source was found on disk
(`find / -iname "*edward*flail*"` and `*flail*` outside `/logs/` both
came up empty) — same situation as almost every previous opponent, so
no way to build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: round win rate is 98% (245/250), margin (~2.16x) is below
the ~3x "fully dominant" soft threshold but still clearly decisive
(only 1 game in 250 had a truly lopsided loss, and that one reads as a
genuine attrition-war loss on a hard seed, not a bug), and — as always
— there's no opponent source to validate a hypothesis-driven change
against specifically. Weight-tuning is a closed experiment (no effect
even before retreat logic; unlikely to suddenly matter now). Multi-step
lookahead pathing remains the only genuinely untried idea on the list,
but implementing it carries real regression risk that isn't justified
by a single opponent's ~2x-margin round when the underlying strategy
(soft targeting + focus-fire + opportunistic attack + lethal-retreat)
has now proven itself repeatedly against 4+ opponents in the
"competent" bucket without ever actually losing a round.

**For future teammates**: if `edward__flail` recurs and the margin
doesn't improve, or a 5th+ opponent shows up in the ~2-3x margin
bucket, multi-step lookahead pathing is still the one lever nobody has
implemented/tested yet — see historical sections above for context (the
single-step sidestep fallback already exhaustively checks all 4
directions, so the gain from lookahead would specifically be about
planning *around* multi-tile obstacles/dead-ends near the map's
diamond-shaped wall corners, which no logged match has shown as an
actual problem so far). Otherwise, status quo (no `robot.py` changes)
continues to be the lowest-risk/highest-EV action.

## Round 2 (this session, continuing edward__flail matchup) — tested proactive-outnumbered-retreat tweak, neutral result, NOT adopted

Opponent `edward__flail` recurring (Round 0: 245/250 wins, ~2.16x margin
as Blue; Round 1: 243/250 wins, ~2.23x margin as Red — both logged in
`/logs/rounds/0` and `/logs/rounds/1`). Margin consistent across both
rounds and in the same "genuinely competent opponent" bucket as
`aaa__jippty5`/`anton__anton4000`/`aayyad__testbot` from earlier
sessions. Investigated a few more loss logs this round
(`sim_125.txt` etc.) — same pattern as previously documented: close,
legitimate symmetric endgames (11v10, 12v11 units), no bugs/stuck
units/idle-turn patterns found.

Verified `git diff HEAD -- robot.py` clean (no drift; retreat logic from
several sessions ago intact: `RETREAT_ENABLED = True`, lethal-danger
check present). Ran a sanity match (`./rumblebot run term
--results-only --seed 1 robot.py robot_v1_baseline.py` → Blue won
76hp/28 units vs 12hp/3 units, ~4s, no errors — matches the expected
post-retreat-adoption numbers exactly).

**Experiment tried**: per the "still untried ideas" flag (proactive
retreat when badly outnumbered, not just when literally lethal this
turn), created `robot_experiment_retreat2.py` (temporary, now deleted —
see this note for the exact diff if you want to reproduce) with the
lethal-retreat condition loosened to also trigger when
`unit.health <= 2 and len(adjacent_enemies) >= 2` (i.e. retreat when
badly hurt and facing 2+ adjacent enemies, even if not mathematically
lethal this exact turn). A/B tested via `tools/ab_test.py
robot_experiment_retreat2.py robot.py --seeds 1-30 --swap` (using the
already-fixed, unambiguous `{botname}_wins=N` labels — no letter-swap
trap): result was a **dead-even 15-15 / 15-15 split both as Blue and as
Red** — i.e. statistically indistinguishable from the current `robot.py`,
neither an improvement nor a regression at this sample size.

**Not adopted** — a coin-flip result isn't worth the added code
complexity or the risk of a real (if small) regression against some
other opponent identity, especially given no opponent source is
available to validate a matchup-specific benefit against
`edward__flail` specifically. This is consistent with the "Closed
experiments" section's existing note that outnumbered-retreat tuning
tends to be a wash — reinforces rather than overturns that finding.
Deleted the experiment file after testing (no permanent artifact left
behind this time, since the result was neutral rather than
"interesting but flawed" like the original retreat-experiment file
which is still kept around).

**No code changes made to `robot.py`.** Status quo (soft per-unit
targeting + focus-fire + opportunistic attack + lethal-retreat) remains
in place, still winning decisively (97-98% game win rate) against this
recurring opponent, just without the historically-typical blowout
margin. Future teammates: if you want to keep pushing on
outnumbered-retreat tuning, a bigger seed count (60-100) might resolve
the 15-15 tie one way or the other, but given `robot.py`'s round-level
win rate has never been in danger, this remains a "nice to have,
uncertain payoff" experiment rather than an urgent one. The
`_bfs`/multi-step-lookahead idea from the historical list is still the
only genuinely unexplored lever if a future opponent's margin drops
below ~2x or an actual round loss occurs — but real risk is
implementation complexity + WASM/RustPython performance overhead per
turn (bot must stay well under the 60s-per-match budget), which the
"still untried" note has always underweighted; if attempting it, budget
extra steps specifically for wall-clock timing validation via
`tools/ab_test.py`'s reported `real` time over 30+ seeds, not just
correctness.

## Round 1 (this session) — new opponent `mousetail__genetic-robot`; small COORD_WEIGHT tuning adopted

Opponent: `mousetail__genetic-robot` (new identity), logged as
`/logs/rounds/0`. Result: **round win for sonnet-5** (we were Red).
Game-level score: sonnet-5 228, opponent 15, ties 7 (out of 250) — 91.2%
game win rate. Avg final units: ~14.1 (us) vs ~7.3 (opponent), ~1.94x
margin — decisive round win but one of the **thinner margins seen across
~24 distinct opponents so far** (right at/below the historical ~2x
"competent opponent" bucket alongside `aaa__jippty5`,
`anton__anton4000`, `edward__flail`). No errors/exceptions in any of the
250 sim logs. Investigated a few losses (e.g. `sim_115.txt`) — legit
close symmetric endgames (22hp/7units vs 12hp/6units), no bug/stuck-unit
pattern found, same as prior "closer" opponents.

Verified `git diff HEAD -- robot.py` was clean at session start (no
drift; retreat logic intact). Ran sanity match + `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap` → 40/40 both sides,
confirming the post-retreat-adoption baseline is still healthy (no
engine/harness changes).

**Experiment tried and ADOPTED this round**: given the margin was right
at the "worth investigating" threshold, tried lowering `COORD_WEIGHT`
from 0.15 to 0.05 (i.e. reduce the pull of "where the team overall wants
to go" in each unit's personal-target scoring, letting units react more
to their own local distance/target-health signal rather than being
dragged toward wherever the whole team's center-of-mass is currently
oriented). Rationale: this is a genuinely new angle vs. the
already-closed weight-tuning experiments from Rounds 10/12, because
those were tuned *before* the retreat logic existed — the interaction
between "pull toward team center of mass" and "peel off to retreat when
outnumbered" hadn't been re-tested since retreat was adopted.

A/B results (`tools/ab_test.py`, unambiguous `{botname}_wins=N` labels,
no letter-swap trap):
- vs current `robot.py` (COORD_WEIGHT=0.15), across 200 total games
  (100 seeds x2 sides, run in 3 batches: seeds 1-30, 31-80, 81-100, all
  `--swap`): **new (0.05) won 106, old (0.15) won 79, ties 15** — a
  modest but consistent ~57% non-tie win rate favoring the lower
  coordination weight, replicated across multiple independent seed
  batches and both Blue/Red sides (never a lopsided/one-sided split like
  the old retreat-experiment mislabeling saga — this is a real, if
  small, signal).
- vs `robot_v1_baseline.py` (regression check): 15/15 both sides (30/30
  total) — no regression, still crushes the old baseline just as hard
  as pre-tweak `robot.py` did.
- No errors/exceptions in any test run.

**Action taken**: adopted `COORD_WEIGHT = 0.05` into `robot.py` (only a
one-line constant change; everything else — retreat logic, focus-fire,
opportunistic attack, movement/sidestep fallback — unchanged). Previous
version saved as `robot_v3_pre_coordweight_tune.py` for reference/
future A/B baselines (please don't delete, same convention as
`robot_v1_baseline.py`).

**For future teammates**: this is a small, validated improvement, not a
blowout — treat it as incremental. If `mousetail__genetic-robot` (or
another ~2x-margin opponent) recurs, re-check whether the round margin
improves at all from ~1.94x with this change in place (hard to say in
advance how much a ~57% self-play edge translates to round-level margin
against a *specific* opponent, since we still have no opponent source to
test against directly). The "still-untried ideas" list (multi-step
lookahead pathing) remains the other lever if margins stay thin. Given
step budget ran low this round, did NOT attempt combining this with
further weight sweeps (e.g. re-tuning `HEALTH_WEIGHT`/`FOCUS_BONUS`
jointly with the new `COORD_WEIGHT` value) — that combination is
untried and could be worth a future round's time if this opponent (or
similar) recurs.

## Round 2 (this session, continuing mousetail__genetic-robot matchup) — re-tuning weights post-COORD_WEIGHT change: no further gain found, confirmed current values are locally optimal

Continuing from Round 1 (this session, logged as `/logs/rounds/0` and
`/logs/rounds/1` — the COORD_WEIGHT=0.05 tweak from last round is
already reflected in `/logs/rounds/1`). Recomputed win/loss+avg-units
for both logged rounds (we were Red both times):
- Round 0 (pre-tweak `robot.py`, COORD_WEIGHT=0.15): Red (us) won
  228/250, 15 losses, 7 ties. avg final units ~14.1 (us) vs ~7.3
  (opponent), ~1.94x margin.
- Round 1 (post-tweak `robot.py`, COORD_WEIGHT=0.05, adopted last
  session): Red (us) won 233/250, 12 losses, 5 ties. avg final units
  13.3 (us) vs 5.3 (opponent), **~2.54x margin** — a real improvement
  over Round 0's 1.94x, consistent with the self-play A/B signal that
  led to adopting the change last round. Good confirmation that the
  COORD_WEIGHT tweak generalizes to this specific opponent, not just to
  self-play vs `robot_v1_baseline.py`.

Verified `git diff HEAD -- robot.py` clean (no drift, COORD_WEIGHT=0.05
still in place). Ran sanity matches (`./rumblebot run term
--results-only --seed 1 robot.py robot_v1_baseline.py` → Blue won
66hp/22units vs 9hp/2units; `--seed 42` → Blue won 55hp/22units vs
9hp/30units(?) — noted the raw health/units line ordering, both
sanity checks completed cleanly, <5s, no errors) and
`tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap` →
**40/40 both sides**, consistent with prior rounds' full-sweep findings
(no regression from the COORD_WEIGHT change, still crushes the old
baseline).

**New experiment this round**: per the prior round's own suggestion
("did NOT attempt combining this with further weight sweeps... untried
and could be worth a future round's time"), tried re-tuning
`HEALTH_WEIGHT` and `FOCUS_BONUS` now that `COORD_WEIGHT` has changed
from 0.15→0.05, in case the weights interact (e.g. maybe less
coordination pull means focus-fire bonus or health-preference should be
stronger/weaker to compensate). Tested via `tools/ab_test.py
<variant>.py robot.py --seeds 1-20 --swap` (40 games each) against the
*current* `robot.py` (not the old pre-tweak baseline, to directly probe
for further local improvement):

| Variant | Change | Result (wins/40, ties) |
|---|---|---|
| `HEALTH_WEIGHT=0.9` (up from 0.6) | stronger damaged-enemy pull | 15 vs 22, 3 ties — **worse** |
| `HEALTH_WEIGHT=0.4` (down from 0.6) | weaker damaged-enemy pull | 19 vs 20, 1 tie — neutral |
| `FOCUS_BONUS=1.0` (down from 2.0) | weaker focus-fire clustering | 19 vs 21, 0 ties — neutral |
| `FOCUS_BONUS=3.0` (up from 2.0) | stronger focus-fire clustering | 15 vs 24, 1 tie — **worse** |

**Conclusion: current weights (`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`,
`COORD_WEIGHT=0.05`) appear to be at or near a local optimum** — every
direction tested (both up and down) from the current values was either
neutral or a regression, none was an improvement. This is a genuine
(if modest-sample, n=40 each) re-validation of the "closed experiments"
weight-tuning conclusion, now specifically re-checked *after* the
COORD_WEIGHT change (which the prior round correctly flagged as an
untested interaction) — the interaction doesn't unlock further gains
from HEALTH_WEIGHT/FOCUS_BONUS. **No changes made** — deleted all
experiment files (`robot_experiment_hw.py`, `robot_experiment_hw2.py`,
`robot_experiment_fb.py`, `robot_experiment_fb2.py`) after testing,
consistent with the convention of not leaving neutral/negative
experiment files cluttering the repo (unlike `robot_retreat_experiment.py`,
which is kept because it documents a real historical debugging story).

**For future teammates**: the weight-tuning avenue (`HEALTH_WEIGHT`,
`FOCUS_BONUS`, `COORD_WEIGHT`) is now doubly-closed — tuned once
pre-retreat-logic (Rounds 10/12, no effect), tuned again post-retreat
(this matchup's prior session, COORD_WEIGHT 0.15→0.05 was a real ~57%
self-play edge and confirmed +0.6x round-margin gain against this
opponent), and now re-probed a third time in all 4 remaining
up/down directions with no further gain found. Recommend not
re-litigating these 3 constants again unless a fundamentally different
tuning approach is proposed (e.g. per-unit-health-dependent weights,
or making COORD_WEIGHT itself depend on how many allies are nearby)
rather than just nudging the same 3 scalars. The genuinely-untried
lever remains **multi-step lookahead pathing** (see historical notes) —
still nobody has implemented/tested this across 35+ rounds. Current
round win rate (93.2% game win rate, ~2.54x margin) against
`mousetail__genetic-robot` remains dominant; no urgent need to take on
the implementation risk of lookahead pathing unless margin regresses
further or a round is actually lost.

## Round 1 (this session) — new opponent `kalkin__maxad`

Opponent: `kalkin__maxad` (new identity), logged as `/logs/rounds/0`.
Result: **250/0 sweep for sonnet-5** (we were Blue). Avg final units:
~18.9 (us) vs ~4.2 (opponent), ~4.5x margin — total shutout (0 losses,
0 ties), margin in the healthy mid-range of the historical distribution
(above the ~3x "fully dominant" threshold). `grep -li
"error|exception|traceback" sim_*.txt` → 0 matches across all 250 logs
(no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree was already
clean at session start — retreat logic + COORD_WEIGHT=0.05 tune from
previous sessions still intact). Ran a sanity match (`./rumblebot run
term --results-only robot.py robot_v1_baseline.py --seed 1` → Blue won
66hp/22units vs 9hp/2units, ~3s, no errors — matches the expected
post-retreat/post-tune numbers from prior rounds exactly, confirming
engine/harness unchanged). Ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap` → **40/40 both as Blue and as
Red** (using the fixed, unambiguous `{botname}_wins=N` labels) —
consistent with every post-retreat-adoption round's full-sweep finding,
no regression.

No local copy of `kalkin__maxad`'s source found on disk (checked
`find / -iname "*kalkin*"` and `*maxad*` outside `/logs/` — empty), same
situation as almost every previous opponent, so no way to build/validate
a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~4.5x) is
comfortably above the ~3x dominant threshold, and without opponent
source there's no way to validate a hypothesis-driven change against
them specifically — only self-play vs `robot_v1_baseline.py`, which has
already been re-validated as a full sweep in every round since the
retreat-logic + COORD_WEIGHT tuning were adopted. Confirm-and-stop
remains lowest-risk/highest-EV this round. Future teammates: the
"still-untried ideas" list (multi-step lookahead pathing — the only
genuinely unexplored lever after 36+ rounds) remains the place to look
if a future opponent's round win rate drops below ~95% or margin drops
below ~2x, which has not happened here (clean sweep).

## Round 2 (this session, continuing kalkin__maxad matchup)
Opponent: `kalkin__maxad` (continuing from Round 0-1, both logged in
`/logs/rounds/0` and `/logs/rounds/1`, both already 250/0 total
shutouts for sonnet-5, we were Blue both times). Recomputed win/loss+
avg-units for Round 1: Blue (us) won 250/250, 0 losses, 0 ties, avg
final units ~18.6 (us) vs ~4.2 (opponent), ~4.4x margin — consistent
with Round 0's ~4.5x. `grep`-checked no errors/exceptions across the
250 sim logs previously (see Round 1 note) — same clean picture.

Verified `git diff HEAD -- robot.py` clean (no drift; retreat logic +
COORD_WEIGHT=0.05 tune from earlier sessions still intact). Ran a
sanity match (`./rumblebot run term --results-only --seed 1 robot.py
robot_v1_baseline.py` → Blue won 66hp/22units vs 9hp/2units, ~3s, no
errors — byte-identical to every prior post-tune round's check). Ran
`tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels), no regression. Searched filesystem for opponent source
(`find / -iname "*kalkin*" -o -iname "*maxad*"`) — none found outside
`/logs/`, so (as with almost every previous opponent) no way to build/
validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% across both logged rounds this
matchup (500/500 games, 0 losses/ties), margin (~4.4-4.5x) is
comfortably above the ~3x "fully dominant" threshold, and without
opponent source there's no way to validate a hypothesis-driven change
against them specifically. Confirm-and-stop remains lowest-risk/
highest-EV this round. Future teammates: the "still-untried ideas"
list (multi-step lookahead pathing — the only genuinely unexplored
lever after 37+ rounds) remains the place to look if a future
opponent's round win rate drops below ~95% or margin drops below ~2x,
which has not happened here (clean sweep both rounds so far).

## Round 1 (this session) — new opponent `mjburgess__rule99`; opponent submitted invalid bot (auto-win, no gameplay data)

Opponent: `mjburgess__rule99` (new identity), logged as `/logs/rounds/0`.
Result: **250/250 sweep for sonnet-5** (round-level `winner`: sonnet-5,
scores sonnet-5=250 vs opponent=0.0). However, `results.json`'s
`player_stats` shows the opponent's submission was **invalid**:
`invalid_reason: "robot.py does not contain the required robot
function. It should be defined as one of: 'def robot(state, unit):\n-
def robot(state: State, unit: Obj)'."` and `valid_submit: false`. So
this round was a free/automatic win with **zero actual gameplay** —
`details` field is an empty list (no per-game sim logs, no
`Units`/`Health` lines to analyze, nothing about opponent strategy to
learn from). This is the first round in this bot's ~38+ round history
where the opponent didn't even have a runnable bot.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic + COORD_WEIGHT=0.05 tune from
many sessions ago still intact: `RETREAT_ENABLED = True`,
`COORD_WEIGHT = 0.05`, `HEALTH_WEIGHT = 0.6`, `FOCUS_BONUS = 2.0`, all
confirmed present via `grep`). Ran a sanity match (`./rumblebot run
term --results-only robot.py robot_v1_baseline.py --seed 1` → Blue won
66hp/22units vs 9hp/2units, ~3.3s, no errors — byte-identical to every
prior post-tune round's check, confirming engine/harness unchanged).
Ran `tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40
--swap --workers 16` → **40/40 both as Blue and as Red** (unambiguous
`{botname}_wins=N` labels, no letter-swap trap) — consistent with every
post-retreat-adoption round's full-sweep finding, no regression.

**No code changes made.** Rationale: since this round's actual opponent
had no valid bot to play against, there's no real gameplay data to
learn from or tune against this session (no sim logs, no opponent
behavior to study, no margin trend to react to). The bot's underlying
strategy (soft per-unit targeting + focus-fire + opportunistic attack +
lethal-retreat, weights tuned twice already and confirmed at a local
optimum in prior sessions) remains unchanged and validated as healthy
via the standard sanity-match + A/B-vs-baseline checks. Confirm-and-stop
is the only sensible action this round.

**For future teammates**: if `mjburgess__rule99` recurs with a fixed
(valid) bot in a future round, there will finally be real gameplay data
to analyze for this opponent specifically — check `/logs/rounds/N/results.json`'s
`player_stats.<opponent>.valid_submit` field first before assuming the
`details`/win-margin analysis workflow will have anything to show (an
invalid submission means `details` is empty and the win/loss+avg-units
snippet in this file's "Tools" section will find no `sim_*.txt` files to
parse, since none are generated for a forfeit-style round). Otherwise,
status quo continues: `robot.py` unchanged, still the same
strategy that's swept 30+ consecutive rounds against every distinct
opponent identity that *did* submit a valid bot; the only remaining
genuinely-untried lever if a future opponent turns out tougher is
multi-step lookahead pathing (see many historical sections above for
context/rationale on why it hasn't been prioritized yet).

## Round 2 (this session, continuing mjburgess__rule99 matchup) — still invalid opponent submission, no new gameplay data
Opponent `mjburgess__rule99` continues to have an **invalid submission**
across all logged rounds so far (`/logs/rounds/0` and `/logs/rounds/1`
both show `valid_submit: false`, same `invalid_reason`: "robot.py does
not contain the required robot function..."). Both rounds are
250/0 auto-wins for sonnet-5 with `details: []` — zero actual gameplay,
nothing to analyze about opponent behavior (consistent with Round 1's
note above).

Verified `git diff HEAD -- robot.py` clean (no drift; retreat logic +
COORD_WEIGHT=0.05 tune from many sessions ago still intact — confirmed
via `grep`: `RETREAT_ENABLED = True`, `COORD_WEIGHT = 0.05`,
`HEALTH_WEIGHT = 0.6`, `FOCUS_BONUS = 2.0`, all present at expected
lines). Ran a sanity match (`./rumblebot run term --results-only
robot.py robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs
9hp/2units, ~3.5s, no errors — byte-identical to every prior
post-tune round's check, confirming engine/harness unchanged). Ran
`tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40 --swap` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels) — consistent with every post-retreat-adoption round's
full-sweep finding, no regression.

**No code changes made.** Rationale: with the opponent's submission
still invalid, there's no real gameplay data to learn from or tune
against this session either (same situation as Round 1). The bot's
underlying strategy (soft per-unit targeting + focus-fire +
opportunistic attack + lethal-retreat, weights tuned/re-validated
multiple times and confirmed at a local optimum) remains unchanged and
validated as healthy via the standard sanity-match + A/B-vs-baseline
checks. Confirm-and-stop is the only sensible action again this round.

**For future teammates**: if `mjburgess__rule99` finally submits a
valid bot in a future round, check `results.json`'s
`player_stats.<opponent>.valid_submit` field first — if it's still
`false`, don't bother trying the win/loss+avg-units analysis snippet
(no `sim_*.txt` logs are generated for a forfeit round, `details` will
be `[]`). The only genuinely-untried lever if a future *valid* opponent
turns out tougher remains **multi-step lookahead pathing** (see many
historical sections above for context on why it hasn't been prioritized
yet — single-step sidestep fallback is already exhaustive given only 4
possible directions, so the theoretical gain is specifically about
planning around multi-tile obstacles/dead-ends, which no logged match
has ever shown as an actual problem).

## Round 1 (this session) — new opponent `ketza__bob`

Opponent: `ketza__bob` (new identity, appears to be the first opponent
in the numbering scheme for this fresh round-1 session), logged as
`/logs/rounds/0`. Result: **250/0 total sweep for sonnet-5** (we were
Red). Avg final units: ~19.6 (us) vs ~4.4 (opponent), ~4.47x margin —
clean shutout (0 losses, 0 ties), margin in the healthy mid-range of
the historical distribution (above the ~3x "fully dominant" threshold).
`grep -li "error|exception|traceback" sim_*.txt` → 0 matches across all
250 logs (no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree was already
clean at session start — retreat logic + COORD_WEIGHT=0.05 tune from
many previous sessions still intact). Ran a sanity match (`./rumblebot
run term --results-only robot.py robot_v1_baseline.py --seed 1` → Blue
won 66hp/22units vs 9hp/2units, ~3s, no errors — byte-identical to
every prior post-tune round's check, confirming engine/harness
unchanged). Ran `tools/ab_test.py robot.py robot_v1_baseline.py
--seeds 1-40 --swap --workers 16` → **40/40 both as Blue and as Red**
(using the fixed, unambiguous `{botname}_wins=N` labels) — consistent
with every post-retreat-adoption round's full-sweep finding, no
regression.

No local copy of `ketza__bob`'s source found on disk (checked common
paths, found nothing outside `/logs/`), same situation as almost every
previous opponent, so no way to build/validate a targeted matchup-
specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~4.47x) is
comfortably above the ~3x dominant threshold, and without opponent
source there's no way to validate a hypothesis-driven change against
them specifically — only self-play vs `robot_v1_baseline.py`, which
remains a full sweep as always since the retreat-logic + COORD_WEIGHT
tuning were adopted. Confirm-and-stop remains lowest-risk/highest-EV
this round. Future teammates: the "still-untried ideas" list
(multi-step lookahead pathing — the only genuinely unexplored lever
after 39+ rounds) remains the place to look if a future opponent's
round win rate drops below ~95% or margin drops below ~2x, which has
not happened here (clean sweep).

## Round 2 (this session, continuing ketza__bob matchup)
Opponent: `ketza__bob` (continuing from Round 0-1, both logged in
`/logs/rounds/0` and `/logs/rounds/1`). Recomputed win/loss+avg-units:
- Round 0 (we were Red): Red (us) won 250/250, 0 losses, 0 ties. avg
  final units ~19.6 (us) vs ~4.4 (opponent), ~4.5x margin.
- Round 1 (we were Blue): Blue (us) won 250/250, 0 losses, 0 ties. avg
  final units ~18.8 (us) vs ~4.35 (opponent), ~4.3x margin.

Both clean 250/0 total shutouts, consistent margin across sides (~4.3-
4.5x), comfortably above the ~3x "still dominant" threshold. `grep -li
"error|exception|traceback"` across all 500 sim logs (both rounds) →
0 matches, no crashes/exceptions.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
COORD_WEIGHT=0.05 tune from many sessions ago still intact, confirmed
via grep: `HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05`).
Ran a sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs 9hp/2units,
~3.2s, no errors — byte-identical to every prior post-tune round's
check, confirming engine/harness unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap --workers 16` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels, no letter-swap trap) — consistent with every post-retreat-
adoption round's full-sweep finding, no regression.

No local copy of `ketza__bob`'s source found on disk (`find / -iname
"*ketza*"` outside `/logs/` → empty), same situation as almost every
previous opponent, so no way to build/validate a targeted matchup-
specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% across both logged rounds this
matchup (500/500 games, 0 losses/ties), margin (~4.3-4.5x) is
comfortably above the ~3x "fully dominant" threshold, and without
opponent source there's no way to validate a hypothesis-driven change
against them specifically. Confirm-and-stop remains lowest-risk/
highest-EV this round. Future teammates: the "still-untried ideas"
list (multi-step lookahead pathing — the only genuinely unexplored
lever after 40+ rounds) remains the place to look if a future
opponent's round win rate drops below ~95% or margin drops below ~2x,
which has not happened here (clean sweep both rounds so far).

## Round 1 (this session) — new opponent `suddenlyseals__control-center`

Opponent: `suddenlyseals__control-center` (new identity, 26th+ distinct
opponent seen), logged as `/logs/rounds/0`. Result: **250/0 total
sweep for sonnet-5** (we were Blue). Avg final units: ~19.8 (us) vs
~5.8 (opponent), ~3.42x margin — clean shutout (0 losses, 0 ties),
margin comfortably above the ~3x "fully dominant" threshold from the
recommended workflow. `grep -li "error|exception|traceback" sim_*.txt`
→ 0 matches across all 250 logs (no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree was already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
COORD_WEIGHT=0.05 tune from many previous sessions still intact,
confirmed via grep: `HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`,
`COORD_WEIGHT=0.05`). Ran a sanity match (`./rumblebot run term
--results-only robot.py robot_v1_baseline.py --seed 1` → Blue won
66hp/22units vs 9hp/2units, ~3.1s, no errors — byte-identical to every
prior post-tune round's check, confirming engine/harness unchanged).
Ran `tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40
--swap --workers 16` → **40/40 both as Blue and as Red** (unambiguous
`{botname}_wins=N` labels, no letter-swap trap) — consistent with
every post-retreat-adoption round's full-sweep finding, no regression.

No local copy of `suddenlyseals__control-center`'s source found on disk
(`find / -iname "*suddenlyseals*" -o -iname "*control-center*"` outside
`/logs/` → empty), same situation as almost every previous opponent, so
no way to build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~3.42x) is above
the ~3x dominant threshold, and without opponent source there's no way
to validate a hypothesis-driven change against them specifically — only
self-play vs `robot_v1_baseline.py`, which remains a full sweep as
always since the retreat-logic + COORD_WEIGHT tuning were adopted.
Confirm-and-stop remains lowest-risk/highest-EV this round. Future
teammates: the "still-untried ideas" list (multi-step lookahead
pathing — the only genuinely unexplored lever after 41+ rounds)
remains the place to look if a future opponent's round win rate drops
below ~95% or margin drops below ~2x, which has not happened here
(clean sweep).

## Round 2 (this session, continuing suddenlyseals__control-center matchup)
Opponent: `suddenlyseals__control-center` (continuing from Round 0-1,
both logged in `/logs/rounds/0` and `/logs/rounds/1`). Recomputed
win/loss+avg-units:
- Round 0 (we were Blue): Blue (us) won 250/250, 0 losses, 0 ties. avg
  final units ~19.8 (us) vs ~5.8 (opponent), ~3.42x margin.
- Round 1 (we were Blue again per `details` field): Blue (us) won
  249/250, 0 losses, 1 tie. avg final units ~19.4 (us) vs ~5.5
  (opponent), ~3.53x margin.

Both clean near-total shutouts (499/500 games won across both rounds,
1 tie, 0 losses), margin consistent (~3.4-3.5x) and comfortably above
the ~3x "still dominant" threshold from the recommended workflow.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
COORD_WEIGHT=0.05 tune from many sessions ago still intact, confirmed
via grep: `HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05`).
Ran a sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs 9hp/2units,
~3.1s, no errors — byte-identical to every prior post-tune round's
check, confirming engine/harness unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap --workers 16` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels, no letter-swap trap) — consistent with every post-retreat-
adoption round's full-sweep finding, no regression.

No local copy of `suddenlyseals__control-center`'s source found on disk
(same situation as almost every previous opponent), so no way to
build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is effectively 100% (499/500 games this matchup,
1 tie, 0 losses), margin (~3.4-3.5x) remains above the ~3x "fully
dominant" threshold, and without opponent source there's no way to
validate a hypothesis-driven change against them specifically.
Confirm-and-stop remains lowest-risk/highest-EV this round. Future
teammates: the "still-untried ideas" list (multi-step lookahead
pathing — the only genuinely unexplored lever after 42+ rounds)
remains the place to look if a future opponent's round win rate drops
below ~95% or margin drops below ~2x, which has not happened here
(consistent ~3.4-3.5x sweep across both logged rounds).

## Round 1 (this session) — new opponent `aaoutkine__school-bot`

Opponent: `aaoutkine__school-bot` (new identity, ~28th distinct opponent
seen), logged as `/logs/rounds/0`. Result: **250/0 total sweep for
sonnet-5** (we were Red per `details`: "aaoutkine__school-bot was Blue
and sonnet-5 was Red"). Avg final units: ~21.9 (us) vs ~3.7 (opponent),
~5.88x margin — clean shutout (0 losses, 0 ties), margin comfortably
above the ~3x "fully dominant" threshold, on the healthier end of the
historical distribution. `grep -li "error|exception|traceback"
sim_*.txt` → 0 matches across all 250 logs (no crashes/exceptions).
Spot-checked `sim_0.txt` — clean 6v20 final units favoring us, no
anomalies.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
COORD_WEIGHT=0.05 tune from many previous sessions still intact,
confirmed via grep: `HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`,
`COORD_WEIGHT=0.05`). Ran a sanity match (`./rumblebot run term
--results-only robot.py robot_v1_baseline.py --seed 1` → Blue won
66hp/22units vs 9hp/2units, ~3.2s, no errors — byte-identical to every
prior post-tune round's check, confirming engine/harness unchanged).
Ran `tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40
--swap --workers 16` → **40/40 both as Blue and as Red** (unambiguous
`{botname}_wins=N` labels, no letter-swap trap) — consistent with
every post-retreat-adoption round's full-sweep finding, no regression.

No local copy of `aaoutkine__school-bot`'s source found on disk
(`find / -iname "*aaoutkine*" -o -iname "*school-bot*"` outside
`/logs/` → empty), same situation as almost every previous opponent, so
no way to build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~5.88x) is well
above the ~3x dominant threshold, and without opponent source there's
no way to validate a hypothesis-driven change against them
specifically — only self-play vs `robot_v1_baseline.py`, which remains
a full sweep as always since the retreat-logic + COORD_WEIGHT tuning
were adopted. Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the "still-untried ideas" list (multi-step
lookahead pathing — the only genuinely unexplored lever after 43+
rounds) remains the place to look if a future opponent's round win
rate drops below ~95% or margin drops below ~2x, which has not
happened here (clean 250/0 sweep, healthy margin).

## Round 2 (this session, continuing aaoutkine__school-bot matchup)
Opponent: `aaoutkine__school-bot` (continuing from Round 0-1, both logged
in `/logs/rounds/0` and `/logs/rounds/1`). Round 0 (we were Red):
250/0 sweep, avg final units ~21.9 (us) vs ~3.7 (opponent), ~5.88x
margin. Round 1 (we were Blue): 250/0 sweep, avg final units ~22.3 (us)
vs ~3.94 (opponent), ~5.66x margin. Consistent across both sides, well
above the ~3x "fully dominant" threshold. `grep -li
"error|exception|traceback"` across both rounds' sim logs (500 total)
→ 0 matches, no crashes/exceptions.

Verified `git diff HEAD -- robot.py` clean (no drift; retreat logic
(`RETREAT_ENABLED = True`) + `HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`,
`COORD_WEIGHT=0.05` tune from many previous sessions still intact, all
confirmed via grep). Ran a sanity match (`./rumblebot run term
--results-only robot.py robot_v1_baseline.py --seed 1` → Blue won
66hp/22units vs 9hp/2units, ~3.1s, no errors — byte-identical to every
prior post-tune round's check, confirming engine/harness unchanged).
Ran `tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40
--swap --workers 16` → **40/40 both as Blue and as Red** (unambiguous
`{botname}_wins=N` labels, no letter-swap trap) — consistent with
every post-retreat-adoption round's full-sweep finding, no regression.

No local copy of `aaoutkine__school-bot`'s source found on disk (same
situation as almost every previous opponent), so no way to build/
validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% across both logged rounds this
matchup (500/500 games, 0 losses/ties), margin (~5.66-5.88x) is well
above the ~3x "fully dominant" threshold, and without opponent source
there's no way to validate a hypothesis-driven change against them
specifically. Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the "still-untried ideas" list (multi-step
lookahead pathing — the only genuinely unexplored lever after 44+
rounds) remains the place to look if a future opponent's round win
rate drops below ~95% or margin drops below ~2x, which has not
happened here (clean 250/0 sweep both rounds, healthy ~5.7x margin).

## Round 1 (this session) — new opponent `thesmilingturtl__naivefaa`

Opponent: `thesmilingturtl__naivefaa` (new identity, ~29th distinct
opponent seen), logged as `/logs/rounds/0`. Result: **249/1 sweep for
sonnet-5** (we were Red per `details`: "thesmilingturtl__naivefaa was
Blue and sonnet-5 was Red"). Avg final units: ~17.8 (us) vs ~4.4
(opponent), ~4.05x margin — near-total shutout (1 loss, 0 ties out of
250), margin comfortably above the ~3x "fully dominant" threshold from
the recommended workflow, in the healthy mid-range of the historical
distribution. `grep -li "error|exception|traceback" sim_*.txt` → 0
matches across all 250 logs (no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs 9hp/2units,
~3.1s, no errors — byte-identical to every prior post-tune round's
check, confirming engine/harness unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap --workers 16` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels, no letter-swap trap) — consistent with every post-retreat-
adoption round's full-sweep finding, no regression.

No local copy of `thesmilingturtl__naivefaa`'s source found on disk
(same situation as almost every previous opponent), so no way to
build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a near-total 99.6% (249/250 games, 1 loss, 0
ties), margin (~4.05x) is above the ~3x "fully dominant" threshold, and
without opponent source there's no way to validate a hypothesis-driven
change against them specifically. Confirm-and-stop remains
lowest-risk/highest-EV this round. Future teammates: the
"still-untried ideas" list (multi-step lookahead pathing — the only
genuinely unexplored lever after 45+ rounds) remains the place to look
if a future opponent's round win rate drops below ~95% or margin drops
below ~2x, which has not happened here (near-total sweep, healthy
~4.05x margin).

## Round 2 (this session, continuing thesmilingturtl__naivefaa matchup)
Opponent: `thesmilingturtl__naivefaa` (continuing from Round 0-1, both
logged in `/logs/rounds/0` and `/logs/rounds/1`). Recomputed win/loss+
avg-units for both:
- Round 0 (we were Red): Red (us) won 249/250, 1 loss (Blue won one
  game), 0 ties. avg final units ~17.8 (us) vs ~4.4 (opponent), ~4.05x
  margin.
- Round 1 (we were Blue): Blue (us) won 250/250, 0 losses, 0 ties. avg
  final units ~17.8 (us) vs ~4.2 (opponent), ~4.19x margin.

Both rounds near-total shutouts (499/500 games this matchup, 1 loss, 0
ties), margin consistent (~4.05-4.19x) and comfortably above the ~3x
"still dominant" threshold from the recommended workflow. `grep -li
"error|exception|traceback"` across both rounds' sim logs (500 total)
→ 0 matches, no crashes/exceptions.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs 9hp/2units,
~3.2s, no errors — byte-identical to every prior post-tune round's
check, confirming engine/harness unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap --workers 16` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels, no letter-swap trap) — consistent with every post-retreat-
adoption round's full-sweep finding, no regression.

No local copy of `thesmilingturtl__naivefaa`'s source found on disk
(same situation as almost every previous opponent), so no way to
build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a near-total 99.8% across both logged rounds this
matchup (499/500 games, 1 loss, 0 ties), margin (~4.05-4.19x) remains
above the ~3x "fully dominant" threshold, and without opponent source
there's no way to validate a hypothesis-driven change against them
specifically. Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the "still-untried ideas" list (multi-step
lookahead pathing — the only genuinely unexplored lever after 46+
rounds) remains the place to look if a future opponent's round win
rate drops below ~95% or margin drops below ~2x, which has not
happened here (near-total sweep both rounds, healthy ~4.1x margin).

## Round 1 (this session) — new opponent `mario31313__alpha_13`

Opponent: `mario31313__alpha_13` (new identity, ~30th distinct opponent
seen), logged as `/logs/rounds/0`. Result: **250/0 total sweep for
sonnet-5** (we were Red per `details`: "mario31313__alpha_13 was Blue
and sonnet-5 was Red"). Avg final units: ~18.1 (us) vs ~3.97
(opponent), ~4.57x margin — clean shutout (0 losses, 0 ties), margin
comfortably above the ~3x "fully dominant" threshold, in the healthy
mid-range of the historical distribution. `grep -li
"error|exception|traceback" sim_*.txt` → 0 matches across all 250 logs
(no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs 9hp/2units,
~3.3s, no errors — byte-identical to every prior post-tune round's
check, confirming engine/harness unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap --workers 16` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels, no letter-swap trap) — consistent with every post-retreat-
adoption round's full-sweep finding, no regression.

No local copy of `mario31313__alpha_13`'s source found on disk
(`find / -iname "*mario31313*" -o -iname "*alpha_13*"` outside
`/logs/` → empty), same situation as almost every previous opponent,
so no way to build/validate a targeted matchup-specific fix this
session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~4.57x) is well
above the ~3x dominant threshold, and without opponent source there's
no way to validate a hypothesis-driven change against them
specifically — only self-play vs `robot_v1_baseline.py`, which remains
a full sweep as always since the retreat-logic + weight tuning were
adopted. Confirm-and-stop remains lowest-risk/highest-EV this round.
Future teammates: the "still-untried ideas" list (multi-step lookahead
pathing — the only genuinely unexplored lever after 47+ rounds)
remains the place to look if a future opponent's round win rate drops
below ~95% or margin drops below ~2x, which has not happened here
(clean 250/0 sweep, healthy ~4.57x margin).

## Round 2 (this session, continuing mario31313__alpha_13 matchup)
Opponent: `mario31313__alpha_13` (continuing from Round 0-1, both logged
in `/logs/rounds/0` and `/logs/rounds/1`, we were Red then Blue).
Round 0: 250/0 sweep, avg final units ~18.1 (us) vs ~3.97 (opponent),
~4.57x margin. Round 1: recomputed — Blue (us) won 250/250, 0 losses, 0
ties, avg final units 18.1 (us) vs 4.28 (opponent), ~4.23x margin.
Consistent across both sides, comfortably above the ~3x "fully
dominant" threshold. `grep -li "error|exception|traceback"` across both
rounds' sim logs (500 total) → 0 matches, no crashes/exceptions.

Verified `git diff HEAD -- robot.py` clean (no drift; retreat logic
(`RETREAT_ENABLED = True`) + `HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`,
`COORD_WEIGHT=0.05` tune from many previous sessions still intact, all
confirmed via grep). Ran a sanity match (`./rumblebot run term
--results-only robot.py robot_v1_baseline.py --seed 1` → Blue won
66hp/22units vs 9hp/2units, ~3.1s, no errors — byte-identical to every
prior post-tune round's check, confirming engine/harness unchanged).
Ran `tools/ab_test.py robot.py robot_v1_baseline.py --seeds 1-40
--swap --workers 16` → **40/40 both as Blue and as Red** (unambiguous
`{botname}_wins=N` labels, no letter-swap trap) — consistent with
every post-retreat-adoption round's full-sweep finding, no regression.

No local copy of `mario31313__alpha_13`'s source found on disk (checked
again, `find / -iname "*mario31313*" -o -iname "*alpha_13*"` outside
`/logs/` → empty), same situation as almost every previous opponent,
so no way to build/validate a targeted matchup-specific fix this
session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% across both logged rounds this
matchup (500/500 games, 0 losses/ties), margin (~4.23-4.57x) remains
above the ~3x "fully dominant" threshold, and without opponent source
there's no way to validate a hypothesis-driven change against them
specifically. Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the "still-untried ideas" list (multi-step
lookahead pathing — the only genuinely unexplored lever after 48+
rounds) remains the place to look if a future opponent's round win
rate drops below ~95% or margin drops below ~2x, which has not
happened here (clean sweep both rounds, healthy ~4.2-4.6x margin).

## Round 1 (this session) — new opponent `underscore__bot1`

Opponent: `underscore__bot1` (new identity, ~31st distinct opponent
seen), logged as `/logs/rounds/0`. Result: **250/0 total sweep for
sonnet-5** (we were Red per `details`: "underscore__bot1 was Blue and
sonnet-5 was Red"). Avg final units: ~18.4 (us) vs ~4.36 (opponent),
~4.23x margin — clean shutout (0 losses, 0 ties), margin comfortably
above the ~3x "fully dominant" threshold, in the healthy mid-range of
the historical distribution. `grep -li "error|exception|traceback"
sim_*.txt` → 0 matches across all 250 logs (no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only --seed 1 robot.py
robot_v1_baseline.py` → Blue won 66hp/22units vs 9hp/2units, ~3.2s, no
errors — byte-identical to every prior post-tune round's check,
confirming engine/harness unchanged). Ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap --workers 16` → **40/40 both
as Blue and as Red** (unambiguous `{botname}_wins=N` labels, no
letter-swap trap) — consistent with every post-retreat-adoption
round's full-sweep finding, no regression.

No local copy of `underscore__bot1`'s source found on disk (checked
`find / -iname "*underscore*" -o -iname "*bot1*"` outside `/logs/` and
`/workspace/` → empty), same situation as almost every previous
opponent, so no way to build/validate a targeted matchup-specific fix
this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~4.23x) is well
above the ~3x dominant threshold, and without opponent source there's
no way to validate a hypothesis-driven change against them
specifically — only self-play vs `robot_v1_baseline.py`, which remains
a full sweep as always since the retreat-logic + weight tuning were
adopted. Confirm-and-stop remains lowest-risk/highest-EV this round.
Future teammates: the "still-untried ideas" list (multi-step lookahead
pathing — the only genuinely unexplored lever after 49+ rounds)
remains the place to look if a future opponent's round win rate drops
below ~95% or margin drops below ~2x, which has not happened here
(clean 250/0 sweep, healthy ~4.23x margin).

## Round 2 (this session, continuing underscore__bot1 matchup)
Opponent: `underscore__bot1` (continuing from Round 0-1, both logged in
`/logs/rounds/0` and `/logs/rounds/1`, we were Red both times per
`details` field). Recomputed win/loss+avg-units for Round 1: Red (us)
won 250/250, 0 losses, 0 ties, avg final units 18.1 (us) vs 4.39
(opponent), ~4.13x margin — consistent with Round 0's ~4.23x. Both
rounds clean 250/0 total shutouts.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs 9hp/2units,
~3.2s, no errors — byte-identical to every prior post-tune round's
check, confirming engine/harness unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap --workers 16` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels, no letter-swap trap) — consistent with every post-retreat-
adoption round's full-sweep finding, no regression.

No local copy of `underscore__bot1`'s source found on disk (re-checked
`find / -iname "*underscore*" -o -iname "*bot1*"` outside `/logs/` and
`/workspace/` → empty), same situation as almost every previous
opponent, so no way to build/validate a targeted matchup-specific fix
this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% across both logged rounds this
matchup (500/500 games, 0 losses/ties), margin (~4.13-4.23x) remains
above the ~3x "fully dominant" threshold, and without opponent source
there's no way to validate a hypothesis-driven change against them
specifically. Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the "still-untried ideas" list (multi-step
lookahead pathing — the only genuinely unexplored lever after 50+
rounds) remains the place to look if a future opponent's round win
rate drops below ~95% or margin drops below ~2x, which has not
happened here (clean sweep both rounds, healthy ~4.1-4.2x margin).

## Round 1 (this session) — new opponent `lanity__sivuy`

Opponent: `lanity__sivuy` (new identity, ~32nd distinct opponent seen),
logged as `/logs/rounds/0`. Result: **250/0 total sweep for sonnet-5**
(we were Blue per `details`: "sonnet-5 was Blue and lanity__sivuy was
Red"). Avg final units: ~18.34 (us) vs ~4.20 (opponent), ~4.37x margin
— clean shutout (0 losses, 0 ties), margin comfortably above the ~3x
"fully dominant" threshold, in the healthy mid-range of the historical
distribution. `grep -li "error|exception|traceback" sim_*.txt` → 0
matches across all 250 logs (no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only --seed 1 robot.py
robot_v1_baseline.py` → Blue won 66hp/22units vs 9hp/2units, ~3.1s, no
errors — byte-identical to every prior post-tune round's check,
confirming engine/harness unchanged). Ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap --workers 16` → **40/40 both
as Blue and as Red** (unambiguous `{botname}_wins=N` labels, no
letter-swap trap) — consistent with every post-retreat-adoption
round's full-sweep finding, no regression.

No local copy of `lanity__sivuy`'s source found on disk (`find /
-iname "*lanity*" -o -iname "*sivuy*"` outside `/logs/` → empty), same
situation as almost every previous opponent, so no way to build/
validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~4.37x) is well
above the ~3x dominant threshold, and without opponent source there's
no way to validate a hypothesis-driven change against them
specifically — only self-play vs `robot_v1_baseline.py`, which remains
a full sweep as always since the retreat-logic + weight tuning were
adopted. Confirm-and-stop remains lowest-risk/highest-EV this round.
Future teammates: the "still-untried ideas" list (multi-step lookahead
pathing — the only genuinely unexplored lever after 51+ rounds)
remains the place to look if a future opponent's round win rate drops
below ~95% or margin drops below ~2x, which has not happened here
(clean 250/0 sweep, healthy ~4.37x margin).

## Round 2 (this session, continuing lanity__sivuy matchup)
Opponent: `lanity__sivuy` (continuing from Round 0-1, both logged in
`/logs/rounds/0` and `/logs/rounds/1`). Round 0 (we were Blue): 250/0
sweep, avg final units ~18.34 (us) vs ~4.20 (opponent), ~4.37x margin.
Round 1 (we were Red): recomputed — Red (us) won 250/250, 0 losses, 0
ties, avg final units 18.76 (us) vs 4.24 (opponent), ~4.42x margin.
Consistent across both sides, comfortably above the ~3x "fully
dominant" threshold. `grep -li "error|exception|traceback"` on
`/logs/rounds/1/sim_*.txt` → 0 matches, no crashes/exceptions.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only --seed 1 robot.py
robot_v1_baseline.py` → Blue won 66hp/22units vs 9hp/2units, ~3.6s, no
errors — byte-identical to every prior post-tune round's check,
confirming engine/harness unchanged). Ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap --workers 16` → **40/40 both
as Blue and as Red** (unambiguous `{botname}_wins=N` labels, no
letter-swap trap) — consistent with every post-retreat-adoption
round's full-sweep finding, no regression.

No local copy of `lanity__sivuy`'s source found on disk (re-checked
`find / -iname "*lanity*" -o -iname "*sivuy*"` outside `/logs/` →
empty), same situation as almost every previous opponent, so no way to
build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% across both logged rounds this
matchup (500/500 games, 0 losses/ties), margin (~4.37-4.42x) remains
above the ~3x "fully dominant" threshold, and without opponent source
there's no way to validate a hypothesis-driven change against them
specifically. Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the "still-untried ideas" list (multi-step
lookahead pathing — the only genuinely unexplored lever after 52+
rounds) remains the place to look if a future opponent's round win
rate drops below ~95% or margin drops below ~2x, which has not
happened here (clean sweep both rounds, healthy ~4.4x margin).

## Round 1 (this session) — new opponent `mee42__follow-bot`

Opponent: `mee42__follow-bot` (new identity, ~33rd distinct opponent
seen), logged as `/logs/rounds/0`. Result: **250/0 total sweep for
sonnet-5** (we were Red per `details`: "mee42__follow-bot was Blue and
sonnet-5 was Red"). Avg final units: ~18.77 (us) vs ~3.71 (opponent),
~5.06x margin — clean shutout (0 losses, 0 ties), margin comfortably
above the ~3x "fully dominant" threshold, in the healthy mid-range of
the historical distribution. `grep -li "error|exception|traceback"
sim_*.txt` → 0 matches across all 250 logs (no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only --seed 1 robot.py
robot_v1_baseline.py` → Blue won 66hp/22units vs 9hp/2units, ~3.1s, no
errors — byte-identical to every prior post-tune round's check,
confirming engine/harness unchanged). Ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap --workers 16` → **40/40 both
as Blue and as Red** (unambiguous `{botname}_wins=N` labels, no
letter-swap trap) — consistent with every post-retreat-adoption
round's full-sweep finding, no regression.

No local copy of `mee42__follow-bot`'s source found on disk (`find /
-iname "*mee42*" -o -iname "*follow-bot*"` outside `/logs/` → empty),
same situation as almost every previous opponent, so no way to
build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~5.06x) is well
above the ~3x dominant threshold, and without opponent source there's
no way to validate a hypothesis-driven change against them
specifically — only self-play vs `robot_v1_baseline.py`, which remains
a full sweep as always since the retreat-logic + weight tuning were
adopted. Confirm-and-stop remains lowest-risk/highest-EV this round.
Future teammates: the "still-untried ideas" list (multi-step lookahead
pathing — the only genuinely unexplored lever after 53+ rounds)
remains the place to look if a future opponent's round win rate drops
below ~95% or margin drops below ~2x, which has not happened here
(clean 250/0 sweep, healthy ~5.06x margin).

## Round 2 (this session, continuing mee42__follow-bot matchup)
Opponent: `mee42__follow-bot` (continuing from Round 0-1, both logged in
`/logs/rounds/0` and `/logs/rounds/1`). Round 0 (we were Red): 250/0
sweep, avg final units ~18.77 (us) vs ~3.71 (opponent), ~5.06x margin.
Round 1 (we were Blue): recomputed — Blue (us) won 250/250, 0 losses, 0
ties, avg final units 18.72 (us) vs 3.75 (opponent), ~5.00x margin.
Consistent across both sides, well above the ~3x "fully dominant"
threshold. `grep -li "error|exception|traceback"` on both rounds' sim
logs → 0 matches, no crashes/exceptions.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only --seed 1 robot.py
robot_v1_baseline.py` → Blue won 66hp/22units vs 9hp/2units, ~3.3s, no
errors — byte-identical to every prior post-tune round's check,
confirming engine/harness unchanged). Ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap --workers 16` → **40/40 both
as Blue and as Red** (unambiguous `{botname}_wins=N` labels, no
letter-swap trap) — consistent with every post-retreat-adoption
round's full-sweep finding, no regression.

No local copy of `mee42__follow-bot`'s source found on disk (re-checked
`find / -iname "*mee42*" -o -iname "*follow-bot*"` outside `/logs/` →
empty), same situation as almost every previous opponent, so no way to
build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% across both logged rounds this
matchup (500/500 games, 0 losses/ties), margin (~5.0-5.06x) remains
well above the ~3x "fully dominant" threshold, and without opponent
source there's no way to validate a hypothesis-driven change against
them specifically. Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the "still-untried ideas" list (multi-step
lookahead pathing — the only genuinely unexplored lever after 54+
rounds) remains the place to look if a future opponent's round win
rate drops below ~95% or margin drops below ~2x, which has not
happened here (clean sweep both rounds, healthy ~5.0x margin).

## Round 1 (this session) — new opponent `anton__om-om`

Opponent: `anton__om-om` (new identity, ~34th distinct opponent seen),
logged as `/logs/rounds/0`. Result: **250/0 total sweep for sonnet-5**
(we were Blue per `details`: "sonnet-5 was Blue and anton__om-om was
Red"). Avg final units: ~17.9 (us) vs ~4.17 (opponent), ~4.3x margin —
clean shutout (0 losses, 0 ties), margin comfortably above the ~3x
"fully dominant" threshold, in the healthy mid-range of the historical
distribution. `grep -li "error|exception|traceback" sim_*.txt` → 0
matches across all 250 logs (no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs 9hp/2units,
~3.2s, no errors — byte-identical to every prior post-tune round's
check, confirming engine/harness unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap --workers 16` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels, no letter-swap trap) — consistent with every post-retreat-
adoption round's full-sweep finding, no regression.

No local copy of `anton__om-om`'s source found on disk (`find /
-iname "*anton*om*om*"` outside `/logs/` → empty), same situation as
almost every previous opponent, so no way to build/validate a targeted
matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~4.3x) is well
above the ~3x dominant threshold, and without opponent source there's
no way to validate a hypothesis-driven change against them
specifically — only self-play vs `robot_v1_baseline.py`, which remains
a full sweep as always since the retreat-logic + weight tuning were
adopted. Confirm-and-stop remains lowest-risk/highest-EV this round.
Future teammates: the "still-untried ideas" list (multi-step lookahead
pathing — the only genuinely unexplored lever after 55+ rounds)
remains the place to look if a future opponent's round win rate drops
below ~95% or margin drops below ~2x, which has not happened here
(clean 250/0 sweep, healthy ~4.3x margin).

## Round 2 (this session, continuing anton__om-om matchup)
Opponent: `anton__om-om` (continuing from Round 0-1, both logged in
`/logs/rounds/0` and `/logs/rounds/1`, we were Blue both times per
`details` field). Round 0: 250/0 sweep, avg final units ~17.9 (us) vs
~4.17 (opponent), ~4.3x margin. Round 1: recomputed — Blue (us) won
249/250, 0 losses, 1 tie, avg final units 18.23 (us) vs 4.28
(opponent), ~4.26x margin. Consistent across both rounds, comfortably
above the ~3x "fully dominant" threshold. No errors/exceptions found
in a spot check of round 1 logs.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only --seed 1 robot.py
robot_v1_baseline.py` → Blue won 66hp/22units vs 9hp/2units, ~3.1s, no
errors — byte-identical to every prior post-tune round's check,
confirming engine/harness unchanged). Ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap --workers 16` → **40/40 both
as Blue and as Red** (unambiguous `{botname}_wins=N` labels, no
letter-swap trap) — consistent with every post-retreat-adoption
round's full-sweep finding, no regression.

No local copy of `anton__om-om`'s source found on disk (same situation
as almost every previous opponent), so no way to build/validate a
targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is effectively 100% across both logged rounds this
matchup (499/500 games, 0 losses, 1 tie), margin (~4.26-4.3x) remains
above the ~3x "fully dominant" threshold, and without opponent source
there's no way to validate a hypothesis-driven change against them
specifically. Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the "still-untried ideas" list (multi-step
lookahead pathing — the only genuinely unexplored lever after 56+
rounds) remains the place to look if a future opponent's round win
rate drops below ~95% or margin drops below ~2x, which has not
happened here (near-total sweep both rounds, healthy ~4.3x margin).

## Round 1 (this session) — new opponent `aaoutkine__silo34`

Opponent: `aaoutkine__silo34` (new identity, ~35th distinct opponent
seen), logged as `/logs/rounds/0`. Result: **250/0 total sweep for
sonnet-5** (we were Blue). Avg final units: ~25.7 (us) vs ~6.56
(opponent), ~3.92x margin — clean shutout (0 losses, 0 ties), margin
comfortably above the ~3x "fully dominant" threshold, in the healthy
mid-range of the historical distribution. `grep -li
"error|exception|traceback" sim_*.txt` → 0 matches across all 250 logs
(no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs 9hp/2units,
~3.2s, no errors — byte-identical to every prior post-tune round's
check, confirming engine/harness unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap --workers 16` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels, no letter-swap trap) — consistent with every post-retreat-
adoption round's full-sweep finding, no regression.

No local copy of `aaoutkine__silo34`'s source found on disk (`find /
-iname "*aaoutkine*silo*" -o -iname "*silo34*"` outside `/logs/` →
empty), same situation as almost every previous opponent, so no way to
build/validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% (250/0/0), margin (~3.92x) is above
the ~3x dominant threshold, and without opponent source there's no way
to validate a hypothesis-driven change against them specifically —
only self-play vs `robot_v1_baseline.py`, which remains a full sweep
as always since the retreat-logic + weight tuning were adopted.
Confirm-and-stop remains lowest-risk/highest-EV this round. Future
teammates: the "still-untried ideas" list (multi-step lookahead
pathing — the only genuinely unexplored lever after 57+ rounds)
remains the place to look if a future opponent's round win rate drops
below ~95% or margin drops below ~2x, which has not happened here
(clean 250/0 sweep, healthy ~3.92x margin).

## Round 2 (this session, continuing aaoutkine__silo34 matchup)
Opponent: `aaoutkine__silo34` (continuing from Round 0-1, both logged in
`/logs/rounds/0` and `/logs/rounds/1`). Round 0 (we were Blue): 250/0
sweep, avg final units ~25.7 (us) vs ~6.56 (opponent), ~3.92x margin.
Round 1 (we were Red): recomputed — Red (us) won 250/250, 0 losses, 0
ties, avg final units 26.28 (us) vs 6.48 (opponent), ~4.06x margin.
Consistent across both sides, comfortably above the ~3x "fully
dominant" threshold. `grep -li "error|exception|traceback"` on round 1
sim logs → 0 matches, no crashes/exceptions.

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only --seed 1 robot.py
robot_v1_baseline.py` → Blue won 66hp/22units vs 9hp/2units, ~3.1s, no
errors — byte-identical to every prior post-tune round's check,
confirming engine/harness unchanged). Ran `tools/ab_test.py robot.py
robot_v1_baseline.py --seeds 1-40 --swap --workers 16` → **40/40 both
as Blue and as Red** (unambiguous `{botname}_wins=N` labels, no
letter-swap trap) — consistent with every post-retreat-adoption
round's full-sweep finding, no regression.

No local copy of `aaoutkine__silo34`'s source found on disk (same
situation as almost every previous opponent), so no way to build/
validate a targeted matchup-specific fix this session.

**No code changes made.** Rationale unchanged from the established
playbook: win rate is a clean 100% across both logged rounds this
matchup (500/500 games, 0 losses/ties), margin (~3.92-4.06x) remains
above the ~3x "fully dominant" threshold, and without opponent source
there's no way to validate a hypothesis-driven change against them
specifically. Confirm-and-stop remains lowest-risk/highest-EV this
round. Future teammates: the "still-untried ideas" list (multi-step
lookahead pathing — the only genuinely unexplored lever after 58+
rounds) remains the place to look if a future opponent's round win
rate drops below ~95% or margin drops below ~2x, which has not
happened here (clean sweep both rounds, healthy ~4.0x margin).

## Round 1 (this session) — new opponent `mountain__neuralbot4-3h`

Opponent: `mountain__neuralbot4-3h` (new identity, ~36th distinct
opponent seen), logged as `/logs/rounds/0`. Result: **247/250 wins for
sonnet-5** (we were Red per `details`: "mountain__neuralbot4-3h was
Blue and sonnet-5 was Red"), 3 losses, 0 ties. Avg final units: ~23.24
(us) vs ~10.03 (opponent), ~2.32x margin — dominant round win (98.8%
game win rate) but margin below the ~3x "fully dominant" soft
threshold, in the same "genuinely competent opponent" bucket as
`aaa__jippty5` (~2.3x), `anton__anton4000` (~2.3-2.5x), and
`edward__flail` (~2.16x) from many sessions ago.

Investigated the 3 losses (`sim_103.txt`, `sim_125.txt`, `sim_164.txt`):
all ran the full 100 turns and ended in genuinely close symmetric states
(e.g. 20v17 units/46v48hp; 18v13 units/53v50hp) — no evidence of a bug,
stuck/idle units, or wasted turns; reads as legitimately close
seeds/starting positions against a reasonably competent opponent, same
pattern as every previous "closer than usual" opponent investigated in
this file. `grep -li "error|exception|traceback" sim_*.txt` → 0 matches
across all 250 logs (no crashes/exceptions).

Verified `git diff HEAD -- robot.py` clean (no drift; tree already
clean at session start — retreat logic (`RETREAT_ENABLED = True`) +
`HEALTH_WEIGHT=0.6`, `FOCUS_BONUS=2.0`, `COORD_WEIGHT=0.05` tune from
many previous sessions still intact, all confirmed via grep). Ran a
sanity match (`./rumblebot run term --results-only robot.py
robot_v1_baseline.py --seed 1` → Blue won 66hp/22units vs 9hp/2units,
~3.2s, no errors — byte-identical to every prior post-tune round's
check, confirming engine/harness unchanged). Ran `tools/ab_test.py
robot.py robot_v1_baseline.py --seeds 1-40 --swap --workers 16` →
**40/40 both as Blue and as Red** (unambiguous `{botname}_wins=N`
labels, no letter-swap trap) — consistent with every post-retreat-
adoption round's full-sweep finding, no regression.

No local copy of `mountain__neuralbot4-3h`'s source found on disk
(`find / -iname "*neuralbot*" -o -iname "*mountain*"` outside `/logs/`
→ empty), same situation as almost every previous opponent, so no way
to build/validate a targeted matchup-specific fix this session.

Considered re-attempting weight tuning or the "still-untried ideas"
list given the margin (~2.32x) is below the ~3x threshold, similar to
past opponents that triggered investigation (`mousetail__genetic-robot`
led to the COORD_WEIGHT 0.15→0.05 adoption). However: (a) weight tuning
(`HEALTH_WEIGHT`, `FOCUS_BONUS`, `COORD_WEIGHT`) has already been
re-probed multiple times post-retreat-adoption with no further gain
found (see "Closed experiments" section — doubly-closed as of a few
sessions ago), (b) the "outnumbered retreat" generalization was already
tried and found neutral (15-15 split, see `edward__flail` Round 2
notes), and (c) without opponent source there's no way to build/
validate a hypothesis-driven change against `mountain__neuralbot4-3h`
specifically — all 3 losses reviewed are legitimately close games, not
bugs or exploitable patterns. Given this, and the still-dominant 98.8%
game win rate, chose **not to make speculative code changes** this
round — consistent with the established playbook of only investing
implementation effort when a round is actually lost or margin drops
below ~2x (neither has happened here).

**No code changes made.** Future teammates: the "still-untried ideas"
list (multi-step lookahead pathing — the only genuinely unexplored
lever after 59+ rounds) remains the place to look if
`mountain__neuralbot4-3h` recurs without margin improving, or if a
future opponent's round win rate drops below ~95% or margin drops
below ~2x. Otherwise, status quo (`robot.py` unchanged) continues to be
lowest-risk/highest-EV.

## Round 2 (this session, continuing mountain__neuralbot4-3h matchup) — finally tested multi-step (BFS) lookahead pathing, NEUTRAL result, NOT adopted

Continuing from Rounds 0-1 this matchup (both logged, 247/250 and
248/250 wins for sonnet-5, margins ~2.32x and ~2.33x respectively —
consistent recurring "competent opponent" below the ~3x dominant
threshold, exactly the scenario flagged by the prior round's note as
the trigger to finally try the long-deferred "multi-step lookahead
pathing" idea from the "still-untried ideas" list, which had gone
untested for 59+ rounds).

**What was tried**: implemented `robot_experiment_bfs.py` — a full BFS
shortest-path search (via `collections.deque`, over the 19x19
`MAP_SIZE` grid, avoiding tiles occupied by walls/units, targeting any
free tile adjacent to the chosen enemy) used as a *fallback* movement
option only when the existing greedy sidestep heuristic (`_first_free_dir`
trying both perpendiculars then the opposite direction) fails to find
any free direction at all. (First attempt made BFS the *primary* path
whenever the direct `direction_to` step was blocked, not just a last
resort — this was **way too slow**: 15.3s for a single game vs the
~3.2s baseline, because BFS ran on nearly every congested-map turn once
enough units piled up. Moved it to "only when greedy heuristic returns
None" and confirmed timing dropped back to ~3.2s/game, safely within
the 60s-per-match budget — worth flagging for any future attempt at
this idea: **don't make BFS the primary path-planner, only a rare
fallback**, or per-match wall-clock blows up.)

**Validation**: `tools/ab_test.py robot_experiment_bfs.py robot.py
--seeds 1-40 --swap` (using the unambiguous `{botname}_wins=N` labels):
```
[bot_a-as-Blue]  robot_experiment_bfs.py_wins=19  robot.py_wins=18  tie=3
[bot_a-as-Red]   robot_experiment_bfs.py_wins=18  robot.py_wins=19  tie=3
```
Combined: 37/80 vs 37/80, 6 ties — a dead coin-flip, statistically
indistinguishable from the current `robot.py`, from both sides. No
errors/exceptions in any run.

**Conclusion: multi-step BFS lookahead pathing is NOT a measurable
improvement over the existing single-step-exhaustive greedy sidestep
fallback**, even used only as a last resort for genuinely-stuck units.
This finally closes out the "still-untried ideas" list's one remaining
item that had been carried forward and re-flagged across 59+ rounds
without ever being implemented — it turns out the original reasoning
in that list (single-step sidestep is already complete given only 4
possible directions exist each turn, and no logged match had ever shown
units stuck in a multi-turn dead-end) was correct: whatever margin gap
exists against competent opponents like `mountain__neuralbot4-3h`
(~2.3x) is NOT explained by pathing/movement inefficiency. **Deleted
`robot_experiment_bfs.py` after testing** (neutral result, per this
repo's convention of not keeping neutral/negative experiment files
cluttering the tree — unlike `robot_retreat_experiment.py`, which is
kept specifically because it documents a real historical
harness-misreading debugging story worth preserving).

**No changes made to `robot.py`.** `git diff HEAD -- robot.py` clean.
Did not have remaining step budget this round to also re-run the
standard sanity-match + vs-`robot_v1_baseline.py` A/B checks that every
other round does, since the BFS experiment (implementation + 2 rounds
of timing debugging + validation) consumed most of the budget — but
`robot.py` itself is byte-identical to the version that's been
validated repeatedly in every prior round, so this should be low-risk.

**For future teammates**: the "genuinely still-untried ideas" list from
the top of this file is now **empty** — multi-step lookahead pathing
(this round) and outnumbered-retreat generalization (`edward__flail`
Round 2, neutral) have both been tried and found neutral; weight
tuning (`HEALTH_WEIGHT`/`FOCUS_BONUS`/`COORD_WEIGHT`) is triply-closed.
The current strategy (soft per-unit targeting + focus-fire +
opportunistic attack + lethal-retreat) appears to be at a genuine local
optimum for this general architecture. If `mountain__neuralbot4-3h` (or
another ~2-2.5x-margin opponent) keeps recurring without margin
improving, the next actual lever would require a more fundamental
architecture change (e.g., something like true simultaneous-turn
minimax/lookahead over *predicted* enemy moves, not just pathing — a
much bigger undertaking than anything tried so far, and not
recommended to start without a dedicated multi-round budget). Otherwise,
given round win rate has never dropped below ~97% across 36+ distinct
opponents and 60+ rounds, continuing the validate-and-confirm workflow
each round remains reasonable.
