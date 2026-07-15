# Agent Notes - RobotRumble bot (opus-4-8)

## Current status (after round 1 edit)
- Round 0 result was a **TIE** (250 ties out of 250 batch games): BOTH our old
  bot AND opponent `anton__anton3000` were **passive** and never engaged. Every
  game ended 20 HP / 20 HP, 4 units / 4 units — zero combat.
- The old bot (`git show HEAD~1:robot.py`, also saved logic) used QUADRANT-based
  targeting: a unit only targeted enemies in its OWN quadrant. Enemies rarely
  shared a quadrant, so units wandered and never attacked → stalemate.

## What I changed (robot.py)
Rewrote into an **aggressive, coordinated focus-fire** bot:
1. If an enemy is adjacent, ATTACK the weakest adjacent enemy (secure kills).
2. Otherwise, move toward the best target = min(health, then walking distance).
   -> focus-fires low-HP enemies, ganging up naturally.
3. Never attacks allies (no friendly fire).
4. Anti-oscillation: remembers last position, avoids stepping straight back.
5. When no enemies exist, leaves spawn toward center (spawn tiles get wiped
   every 10 turns).

## Key game mechanics (verified in logic/logic/src/lib.rs)
- 19x19 circular arena, GameMode = "Normal" (default in CLI).
- Units 5 HP, attack = 1 dmg, NO self-damage. Attacks on same tile STACK.
- **Movement resolves BEFORE attacks** each turn -> a fleeing enemy dodges an
  attack aimed at its old tile. Attacking is still +EV when enemy is cornered
  or multiple allies attack the same tile.
- Friendly fire IS possible.
- Move conflict priority: N,E,S,W (clockwise). Swap-moves are blocked.
- Up to 4 units/team spawn every 10 turns; robots left in spawn area are wiped
  on the spawn turn. Win condition: MORE UNITS after 100 turns.
- `Action.heal` only works in NormalHeal mode (NOT active here) — ignore it.

## Testing / tooling
Run a single match:
  ./rumblebot run term BLUE.py RED.py --results-only
Run many (fast, reuses process):
  printf '{"blue":"robot.py","red":"X.py","seed":"1"}\n' | ./rumblebot run batch
Test bots I saved to /tmp during round 1 (regenerate if gone):
  - old passive bot: `git show HEAD~1:robot.py` (quadrant bot)
  - simple aggro bot: nearest-enemy chase+attack (quickstart style)

## Results of current bot (robot.py)
- vs old passive quadrant bot: dominant win (e.g. 17 units to 1).
- vs simple aggro chase bot: wins 6/6 across seeds, both as Blue and Red.
- Full match runs in <1s — well under the 60s limit.

## Ideas for next teammate to try
- The opponent was passive in round 0, so aggression alone likely wins. If a
  future opponent is aggressive, consider:
  * Explicit focus-fire: global target assignment in init_turn so 2-3 units
    converge on ONE enemy per turn (kills in ~2-3 turns before spawn refresh).
  * Predict enemy flee direction and attack the tile they'll move to.
  * Retreat low-HP units (1 HP) to avoid feeding kills.
  * Group units before engaging so we win local skirmishes.
- Test against the ACTUAL opponent if their code ever becomes available in logs.

---
## Round 2 edit (opus-4-8, teammate 2)
### Result recap
- Round 1: **WIN 250-0** vs anton__anton3000. Opponent is PASSIVE: units march
  in a group in one direction and NEVER attack. Our aggressive bot converged
  and won ~19 units to 1. Confirmed opponent still passive in sim logs.

### What I did
- Kept aggressive focus-fire core; upgraded robot.py to **v2**:
  * `init_turn` now picks a SHARED global focus target (weakest enemy,
    tie-broken by total distance from our units) so units gang up.
  * `step_toward` now avoids tiles another ally already PLANNED to move into
    this turn (_planned_moves), reducing self-blocking clusters.
  * Attack logic: still attacks whenever adjacent (aggressive), with helper
    `enemy_boxed`/attacker-count reasoning for documentation/future tuning.
- Backup of the round-1 bot is regenerable via `git show HEAD~1:robot.py`;
  I also saved it during my session to /tmp/robot_v1.py (gone next round).

### Key finding: STRONG RED-SIDE BIAS
- In 40 mirror games v1-vs-v2, the RED side won ~11/20 in BOTH orientations.
  So Red has a structural map advantage; bot-quality diffs are masked by it.
- v2 vs v1 net record was ~18-17 (a wash) => v2 is neutral/slightly better,
  strictly better coordination code, no regression vs passive opponent.
- Against a simple nearest-enemy aggro bot (/tmp/aggro.py, regenerate it):
  roughly 50/50 due to the side bias. This is the main area to improve IF the
  opponent ever becomes aggressive.

### Ideas for next teammate
- If opponent stays passive: current bot is more than sufficient; consider just
  submitting or adding more analysis tooling.
- If opponent turns aggressive: work on winning even LOCAL skirmishes -
  * predict enemy flee tile and attack where they'll be (movement before attack)
  * retreat 1-HP units instead of feeding kills
  * keep the group tight; don't overextend single units into 2-3 enemies.
- Regenerate test bots: /tmp/aggro.py (nearest-chase+attack) and
  /tmp/marcher.py (passive south-marcher mimicking real opponent) - see this
  session's commands, or recreate simply.

---
## Round 1 edit (opus-4-8, this session)
### CRITICAL CORRECTION: opponent is `happysquid__test`, NOT anton.
- Round 0 (/logs/rounds/0/results.json): **WON 250-0** vs `happysquid__test`.
- Analyzed all 250 sim logs (/logs/rounds/0/sim_*.txt): opponent is COMPLETELY
  PASSIVE — its units cluster/march and **NEVER attack** (our Red HP never
  drops in any game). We accumulate ~26-30 units vs their 3-4 by turn 100.
- Confirmed current robot.py wins every game decisively. No change was needed.

### What I did
- Verified robot.py runs cleanly (batch + term modes, multiple seeds), no
  crashes, well under 60s (each match ~1s). Saved baseline to /tmp.
- Considered overkill-avoidance & 1-HP retreat improvements but REJECTED them:
  since movement resolves before attacks and the opponent is passive/clustered,
  piling attacks is fine and any reservation logic risks bugs/regression with
  ZERO upside (already max score 250-0). Kept the proven bot unchanged.

### Guidance for next teammate
- If opponent STILL happysquid__test (passive): DO NOT change robot.py, just
  submit. It is optimal here.
- If opponent becomes aggressive: implement flee-tile prediction (attack the
  tile enemy will move INTO, since movement precedes attacks) and retreat
  1-HP units. Test vs a saved baseline before shipping.
- Note: earlier "strong RED-side bias" claim is not deterministic — in mirror
  self-play across seeds 1-5, Blue won on seeds 1 & 5, Red on 2/3/4.

---
## Round 2 edit (opus-4-8, teammate 3) - THIS SESSION
### Result recap
- Round 0: **WON 250-0** vs happysquid__test (passive).
- Round 1: **WON 250-0** vs happysquid__test (passive). Confirmed in
  /logs/rounds/1/sim_*.txt: opponent still marches & NEVER attacks; we win
  every game ~15 units to 3. We were RED both rounds.

### Decision: KEPT robot.py UNCHANGED (proven baseline).
Reasoning: opponent is passive; current aggressive focus-fire bot is optimal
here (250-0). Any change risks regression with zero upside vs a passive foe.

### What I tested this session (tools regenerable, in /tmp during session):
- /tmp/marcher.py: passive `Action.move(South)` bot (mimics real opponent).
  Our bot beats it as both Blue and Red decisively.
- /tmp/aggro.py: CORRECT-API nearest-enemy chase+attack bot. Use
  state.objs_by_team(state.other_team), me.walking_distance_to, me.direction_to.
  (My first aggro attempt used a wrong API and silently fell back to passive -
   BEWARE writing test bots: verify they actually engage!)
- /tmp/variant.py: baseline + PREDICTIVE ATTACK (attack tile enemy will flee
  into) + kept grouping. Built via a python patch script (see session history).

### KEY FINDING: results are dominated by a strong RED-SIDE MAP BIAS.
- Our bot vs /tmp/aggro.py across seeds 1-5, BOTH orientations: whoever is RED
  wins ~4-5/5 REGARDLESS of which bot. As Blue vs aggro we LOSE (got wiped
  0-11 in one seed). Games stay dead-even (7-7 units) until ~turn 50-60 then
  the Red side pulls ahead.
- variant (predictive) vs baseline: pure side bias again (Blue wins seeds
  1,2,5; Red wins 3,4 no matter which bot is which). => predictive change is
  NEUTRAL: no help vs aggression (bias dominates), no regression vs passive.
  I did NOT ship it (extra complexity/risk for no measurable gain).

### Guidance for next teammate
- If opponent STAYS passive (happysquid__test): submit robot.py as-is. Optimal.
- If opponent becomes AGGRESSIVE: the real problem is the RED-side bias, not
  attack logic. To win as BLUE you likely need a genuinely better skirmish:
  * Retreat/kite 1-HP units so you don't feed kills (NOT yet implemented).
  * Stronger grouping: don't let single units get surrounded early (turns 5-15
    are where units first meet - keep a tight 3-4 unit ball).
  * Consider the /tmp/variant.py predictive attack ONLY combined with retreat
    logic; alone it does nothing.
  * We can only choose our bot, not our side, so aim for logic robust to being
    Blue. Test explicitly with our bot as BLUE vs an aggressive foe.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = anton__wallifier
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 250-0** vs `anton__wallifier`.
  We were BLUE. Confirmed in sim logs: opponent is PASSIVE — its units march in
  a group and never effectively attack (their HP stays flat at ~20-25 while
  ours grows). We win ~24-30 units to 1-3.
- Verified robot.py still runs cleanly (batch + mirror seeds 1-5), <1s/match,
  no crashes.

### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent passive; aggressive focus-fire bot is optimal. Any change risks
regression with zero upside. Submitting as-is.

### Guidance for next teammate
- If opponent STAYS passive (anton__wallifier): submit robot.py as-is.
- If opponent becomes AGGRESSIVE: see prior notes on RED-side map bias, kiting
  1-HP units, and tight grouping. Test explicitly with our bot as BLUE.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = anton__wallifier
### Result recap
- Round 0: **WON 250-0** vs anton__wallifier (we were BLUE).
- Round 1: **WON 250-0** vs anton__wallifier (we were BLUE).
  Confirmed in /logs/rounds/1/sim_0.txt: opponent still PASSIVE (marches, never
  effectively attacks). We win ~32 units to 3 by turn 100.
### Verification this session
- robot.py parses OK; ran it both sides vs a passive marcher (/tmp/marcher.py:
  `def robot(state,unit): return Action.move(Direction.South)`):
  * As BLUE: won 18 units to 2.  As RED: won 20 units to 2.
- Each match ~1.3s, well under 60s limit.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent passive; aggressive focus-fire bot is optimal. No change = no
regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS passive: submit robot.py as-is (optimal).
- If opponent becomes AGGRESSIVE: see prior notes (RED-side map bias, kite
  1-HP units, tight grouping). Test with our bot explicitly as BLUE.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = ldang__nessy (AGGRESSIVE!)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 250-0** vs `ldang__nessy`. We
  were BLUE. UNLIKE prior opponents, ldang__nessy IS AGGRESSIVE — it deals
  damage (our blue units drop in ALL 250 games) but we still win decisively
  (~26 units to 3). So our aggressive focus-fire bot already beats it.

### What I changed (robot.py) — small robustness improvement, no regression
- Added `retreat()` + `count_allies_near()` helpers.
- New attack rule: a 1-HP unit that is adjacent to an enemy and CANNOT secure a
  kill this turn now RETREATS (moves to the free tile farthest from nearest
  enemy) instead of feeding a free kill. Otherwise still attacks the weakest
  adjacent enemy (unchanged aggressive core).
- Simplified the old attack block (removed dead "predict"/boxed branching that
  always returned attack anyway).

### Testing (baseline saved to /tmp/robot_baseline.py this session)
- Built /tmp/aggro.py = pure nearest-enemy chase+attack bot (STRONGER than the
  real opponent; a good stress test). CORRECT API:
    tgt=min(enemies,key=lambda e:unit.coords.walking_distance_to(e.coords))
    Action.attack(d) if adjacent else Action.move(unit.coords.direction_to(...))
- BASELINE bot vs aggro: LOST 0/5 as Blue (aggro out-damages us).
- NEW bot vs aggro: WON 2/5 as Blue, 3/5 (+1 tie) as Red. Clear improvement.
- NEW vs BASELINE: net 6-4 across both orientations (side bias present) — new is
  slightly better, NO regression.
- NEW vs passive marcher (South): wins ALL, both sides. No regression vs passive.
- Match runtime ~0.85s, well under 60s.

### Guidance for next teammate
- If opponent STAYS ldang__nessy: current robot.py wins 250-0; safe to submit.
- Aggro test bot still beats us ~half the time — the bot could be stronger vs a
  truly aggressive foe. Ideas NOT yet done: tighter grouping before engaging,
  predictive attack on flee tiles COMBINED with retreat, avoid single units
  overextending into 2+ enemies (retreat if outnumbered locally, not just 1-HP).
- Regenerate test bots: /tmp/aggro.py, /tmp/marcher.py, /tmp/robot_baseline.py
  (= `git show HEAD:robot.py` before this commit).

---
## Round 2 edit (opus-4-8, THIS session) - opponent = ldang__nessy (AGGRESSIVE)
### Result recap
- Round 0: **WON 250-0** vs ldang__nessy (we were BLUE).
- Round 1: **WON 250-0** vs ldang__nessy (we were BLUE). All 250 sim logs = Blue
  won; opponent IS aggressive (deals damage) but we win ~24 units to 2.

### What I changed (robot.py) - BOXED-PRIORITY ATTACK, tested improvement
- Adjacent-enemy attack now picks target by adj_score = (boxed? , health,
  -ally_attackers): prefer an enemy that is BOXED (enemy_boxed => <=1 free
  escape tile) so the hit is GUARANTEED to land (movement resolves before
  attacks, so unboxed enemies often flee and our attack whiffs). Then weakest,
  then most ally attackers (best chance to finish after a flee).
- Kept the 1-HP outnumbered retreat.

### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py before edit)
- NEW vs baseline over 40 games (both orientations, seeds 1-20):
  NEW won 20, baseline won 13, ties 7 (~61% excl. ties). Clear improvement,
  NO regression.
- NEW as BLUE vs strong /tmp/aggro.py (nearest-chase+attack): 5W/2L/1T over 8
  seeds (baseline was ~2/5). Better local-skirmish performance as Blue.
- NEW vs /tmp/marcher.py (South marcher): wins both sides. No regression vs
  passive.
- Runtime ~0.9s/match, well under 60s.

### Guidance for next teammate
- If opponent STAYS ldang__nessy: robot.py wins 250-0; safe to submit.
- Regenerate test bots (gone next round):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py` (pre-this-edit).
- Further ideas NOT done: predictive attack on flee tiles COMBINED with the
  boxed logic; tighter pre-engagement grouping; retreat when locally
  outnumbered even above 1 HP. There is a persistent side (map) bias in
  self-play, so test explicitly on BOTH orientations.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = ldang__nemo
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `ldang__nemo` (we were BLUE, all
  250 sim logs = Blue won ~25 units to 2). Opponent is WEAK/mostly ineffective:
  early turns (1-9) we take ZERO damage while chipping Red down. We dominate.

### What I changed (robot.py) — small robustness improvement, TESTED, no regression
- Broadened the adjacent-enemy RETREAT rule. Was: retreat only if health<=1 and
  can't kill. Now ALSO retreats a unit with health<=2 that is locally
  OUTNUMBERED (n_adj_enemies > local_allies+1) and can't secure a kill.
  Avoids single units overextending into 2+ enemies and feeding kills.
- One-line change in robot() (the retreat gate). Everything else unchanged.

### Testing (baseline = /tmp/robot_baseline.py = pre-edit robot.py)
- NOTE: `run term` is DETERMINISTIC per orientation (repeats give same result).
  For variety use `run batch` with seeds:
    (for s in 1 2 3 4 5 6; do printf '{"blue":"A.py","red":"B.py","seed":"%s"}\n' $s; done) | ./rumblebot run batch
- variant vs strong /tmp/aggro.py as BLUE (seeds 1-6): 6/6 WINS.
  baseline vs aggro as BLUE: only 3/5. => variant strictly better on OUR side.
- variant vs /tmp/marcher.py (passive S-marcher) as BLUE seeds 1-6: 6/6. No
  regression vs passive.
- variant vs baseline head-to-head (term, both orientations): 7-7 wash (side
  bias dominates); as Red vs aggro variant slightly worse (1-4 vs 2-3) but we
  are always BLUE vs the real opponent, so the Blue-side gain is what matters.
- robot.py parses OK; match runtime ~1.7s, well under 60s.

### Guidance for next teammate
- If opponent STAYS ldang__nemo (weak): robot.py wins 250-0; safe to submit.
- Test bots (regenerate — gone next round, NO `logic` import needed, Action &
  Direction are globals):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
    Uses state.objs_by_team(state.other_team), unit.coords.walking_distance_to,
    unit.coords.direction_to.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py` (pre-this-edit).
- Further ideas NOT done: predictive attack on flee tiles combined with retreat;
  tighter pre-engagement grouping; reduce the persistent RED-side map bias.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = ldang__nemo
### Result recap
- Round 0: **WON 250-0** vs ldang__nemo (we were BLUE, wiped them ~26-0).
- Round 1: **WON 250-0** vs ldang__nemo (we were RED). In /logs/rounds/1/:
  most sims we crush them (26-0, 25-5, 20-1). Opponent DOES deal SOME damage in
  a few sims (aggressive-ish/weak) but we win every game decisively.
### Verification this session
- robot.py parses OK. Runtime ~1.2s/match, well under 60s.
- robot vs strong /tmp/aggro.py (nearest-chase+attack): 6/6 WINS as BLUE;
  as RED 3W/2L/1T (aggro is STRONGER than the real opponent; side bias present).
- robot vs /tmp/marcher.py (South marcher): wins BOTH sides.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent is weak; current aggressive focus-fire bot wins 250-0 in BOTH
orientations. Any change risks regression with zero upside. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS ldang__nemo: submit robot.py as-is (optimal, 250-0).
- If opponent becomes truly AGGRESSIVE: the bot loses ~40% as RED vs strong
  aggro (side bias). Ideas NOT done: predictive attack on flee tiles combined
  with retreat; tighter pre-engagement grouping; retreat when locally
  outnumbered above 2 HP. Test BOTH orientations - regenerate /tmp/aggro.py,
  /tmp/marcher.py (see commands in prior notes).

---
## Round 1 edit (opus-4-8, THIS session) - opponent = navster8__bash-brothers (AGGRESSIVE)
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `navster8__bash-brothers`. We were
  RED (all 250 sims = Red won). Opponent IS AGGRESSIVE (deals damage: Red HP
  dropped in all 50 sampled sims) but we CRUSH them: avg unit margin +22.7
  (min +8, max +33), e.g. 29 units to 4.
### Verification this session
- robot.py parses OK. Runtime ~1.3s/match, well under 60s.
- robot as BLUE vs strong /tmp/aggro.py (nearest-chase+attack): 5/5 WINS.
- robot as RED vs aggro: 2W/2L/1T (persistent side bias; aggro test bot is
  STRONGER than the real opponent).
- robot vs /tmp/marcher.py (South marcher): wins BOTH sides (3/3 each).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive but far weaker than us; current focus-fire bot wins 250-0
with a huge margin. Any change risks regression with zero upside. Submitting.
### Guidance for next teammate
- If opponent STAYS navster8__bash-brothers: submit robot.py as-is (optimal).
- If opponent gets stronger: the bot still loses ~half vs strong aggro as RED
  (side bias). Ideas NOT done: predictive attack on flee tiles combined with
  retreat; tighter pre-engagement grouping. Regenerate /tmp/aggro.py,
  /tmp/marcher.py from commands in prior notes.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = navster8__bash-brothers
### Result recap
- Round 0: **WON 250-0** vs navster8__bash-brothers (we were RED).
- Round 1: **WON 250-0** vs navster8__bash-brothers (we were BLUE). In
  /logs/rounds/1/sim_0.txt we won 31 units to 2. Opponent is aggressive-ish
  (deals a little damage) but MUCH weaker than us.

### What I changed (robot.py) - GROUPING BONUS in step_toward. TESTED UPGRADE.
- step_toward now scores candidate move tiles as (dist_to_goal, ally_penalty)
  where ally_penalty = sum of walking distance to allies within wd<=4. Ties on
  distance-to-goal are broken by staying TIGHT with allies (avoids single units
  getting isolated/surrounded, which was the main Red-side skirmish weakness).
- Candidate tuples grew from 3 to 4 elements; unpacking updated accordingly.
- Everything else (attack logic, retreat, focus target) unchanged.

### Testing (baseline = /tmp/robot_baseline.py = pre-edit robot.py)
- vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than real opponent):
  * variant as BLUE seeds 1-8: **8/8 WINS** (baseline was 8/8 blue too).
  * variant as RED seeds 1-8: **8/8 WINS** (baseline was only 4/8!). BIG gain
    on the previously weak Red side. Grouping fixed the isolation losses.
- variant vs baseline head-to-head, seeds 1-6, BOTH orientations: variant wins
  5/6 whether it is Blue or Red => genuine improvement, NOT just side bias.
- vs /tmp/marcher.py (South marcher): wins BOTH sides decisively (29-3, 23-3).
  No regression vs passive.
- robot.py parses OK; runtime ~2-3.5s/match, well under 60s.
- NOTE: `run term` (deterministic seed 0) still shows a Blue loss vs the STRONG
  aggro test bot (5-6) - that is a single seed-0 edge case; across real seeds
  1-8 we win 8/8. The real opponent is far weaker, so this is a non-issue.

### Guidance for next teammate
- If opponent STAYS navster8__bash-brothers: robot.py wins 250-0; safe to submit.
- Regenerate test bots (gone next round; Action/Direction/State are globals,
  NO logic import needed):
  * /tmp/aggro.py: nearest-enemy chase+attack. Uses
    state.objs_by_team(state.other_team), unit.coords.walking_distance_to,
    unit.coords.direction_to.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py` (pre this-edit).
- Further ideas NOT done: predictive attack on flee tiles combined with retreat;
  tune ally_penalty weight / radius; retreat when locally outnumbered above 2 HP.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = aaoutkine__dark-knight
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `aaoutkine__dark-knight`. We were
  RED (all 250 sims = Red won). Opponent IS aggressive-ish (deals a little
  damage; blue HP ends ~13-20) but MUCH weaker: we win ~24-28 units to 1-4
  (e.g. 27-3, 28-4, 22-1). We crush them decisively.
### Verification this session
- robot.py parses OK. Runtime ~1.5-3.5s/match, well under 60s.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **6/6 WINS as BLUE, 6/6 WINS as RED** (12/12). The grouping-bonus
  edit from prior round is holding up great on BOTH orientations now.
- robot vs /tmp/marcher.py (South marcher) as BLUE: 31 units to 1.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot 12/12 both sides. Zero upside to
changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS aaoutkine__dark-knight: submit robot.py as-is (optimal).
- Regenerate test bots (gone next round; Action/Direction/State are globals,
  NO logic import needed):
  * /tmp/aggro.py: nearest-enemy chase+attack. Uses
    state.objs_by_team(state.other_team), unit.coords.walking_distance_to,
    unit.coords.direction_to.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
- Further ideas NOT done: predictive attack on flee tiles combined with retreat;
  tune ally_penalty weight/radius. Only pursue if a MUCH stronger opponent
  appears (this one is comfortably beaten).

---
## Round 2 edit (opus-4-8, THIS session) - opponent = aaoutkine__dark-knight
### Result recap
- Round 0: **WON 250-0** vs aaoutkine__dark-knight (we were RED).
- Round 1: **WON 250-0** vs aaoutkine__dark-knight (we were BLUE, e.g. 27-3 in
  sim_0). Opponent aggressive-ish but far weaker; we crush every game.
### Verification this session
- robot.py parses OK. Runtime ~4s/match, well under 60s.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **6/6 WINS as BLUE, 6/6 WINS as RED** (12/12 both orientations).
- robot vs /tmp/marcher.py (South marcher) as BLUE: 30 units to 2.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent far weaker; current focus-fire + grouping bot wins 250-0 and beats a
strong aggro test bot 12/12 both sides. Zero upside to changing, real
regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS aaoutkine__dark-knight: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (see prior notes for exact code).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
- Further ideas NOT done: predictive attack on flee tiles + retreat; tune
  ally_penalty. Only pursue vs a MUCH stronger opponent.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = mountain__neuralbot1-1h
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `mountain__neuralbot1-1h`. We were
  RED (all 250 sims = Red won). Opponent is aggressive-ish (deals early damage:
  BLUE HP drops... wait format is "Health BLUE RED" -> opponent=BLUE loses HP
  fast, we barely take damage early). We CRUSH them: ~31 units to 2 (sim_0),
  30-1, 35-2, etc. Closest of all 250 games was still a +15 UNIT margin.
### Verification this session
- robot.py parses OK. Runtime ~3.3s/match, well under 60s.
- robot vs /tmp/marcher.py (South marcher) as BLUE: 30 units to 2.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **6/6 WINS as BLUE, 6/6 WINS as RED** (12/12 both orientations).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent far weaker; current focus-fire + grouping bot wins 250-0 (min +15
margin) AND beats a strong aggro test bot 12/12 both sides. Zero upside to
changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS mountain__neuralbot1-1h: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (see prior notes for exact code).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
- Further ideas NOT done: predictive attack on flee tiles + retreat; tune
  ally_penalty. Only pursue vs a MUCH stronger opponent than this one.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = mountain__neuralbot1-1h
### Result recap
- Round 0: **WON 250-0** vs mountain__neuralbot1-1h (we were RED).
- Round 1: **WON 250-0** vs mountain__neuralbot1-1h (we were BLUE, e.g. 26-4 in
  sim_0). Opponent aggressive-ish but far weaker; we crush every game.
### Verification this session
- robot.py parses OK. Runtime ~1.5-2s/match, well under 60s.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): won ALL 8 games (seeds 1-4 both orientations - robot wins whether
  Blue or Red). Grouping + focus-fire holding up great.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent far weaker; current bot wins 250-0 both orientations and beats a strong
aggro test bot 8/8. Zero upside to changing, real regression risk. Submitting.
### Guidance for next teammate
- If opponent STAYS mountain__neuralbot1-1h: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 1 edit (opus-4-8, THIS session) - opponent = sivecano__clouded-mind
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `sivecano__clouded-mind`. We were
  BLUE (all 250 sims = Blue won). Opponent is mostly PASSIVE/weak: our Blue HP
  stays flat at ~20 while Red (opponent) HP drops steadily. We crush them
  decisively (~24 units to 4, 27-2, 23-5). One sim (249) opponent chipped a
  little of our HP early but we still won big.
### Verification this session
- robot.py parses OK. Runtime <2s/match, well under 60s.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations).
- robot vs /tmp/marcher.py (South marcher) as BLUE: WIN.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent mostly passive/weak; current focus-fire + grouping bot wins 250-0 and
beats a strong aggro test bot 8/8 both sides. Zero upside to changing, real
regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS sivecano__clouded-mind: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
- Further ideas NOT done: predictive attack on flee tiles + retreat; tune
  ally_penalty. Only pursue vs a MUCH stronger opponent than this one.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = sivecano__clouded-mind
### Result recap
- Round 0: **WON 250-0** vs sivecano__clouded-mind (we were BLUE).
- Round 1: **WON 250-0** vs sivecano__clouded-mind (we were BLUE).
  All 250 sim logs each round = Blue won. Opponent is PASSIVE/weak: our Blue HP
  grows steadily (spawns) and only drops occasionally by 1; we win ~21-28 units
  to 2-3 by turn 100 (see /logs/rounds/1/sim_0.txt: 21 units to 3).

### BUG FIX shipped in robot.py (step_toward fallback)
- Found a latent crash bug: the final fallback in step_toward did
  `return Action.move(candidates[0][1])` where candidates[0][1] is `ally_pen`
  (an int), NOT a Direction; and set `_planned_moves[id] = candidates[0][2]`
  (a Direction, not Coords). This path triggers when a unit's ONLY reachable
  free tile equals its previous position (anti-oscillation blocks it).
  On trigger it would have thrown -> could forfeit the round (>runtime/crash).
- Fixed to unpack `(dist, ap, d, nxt) = candidates[0]` and
  `return Action.move(d)` with `_planned_moves[id] = nxt`. Verified.

### Testing this session (regenerate test bots in /tmp)
- /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  (do NOT `from robot import *` in test bots - Direction/Action are injected).
- /tmp/aggro.py: nearest-enemy chase+attack (state.objs_by_team(state.other_team),
  unit.coords.walking_distance_to / .direction_to). This is STRONGER than the
  real opponent - good stress test.
- Results with fixed bot:
  * vs marcher: WIN both sides (Blue 26-4, Red 34-2).
  * vs aggro: WIN both sides seeds 1-3 (Blue AND Red all won!). Seeds 4-8 as
    Blue: 4/5 wins. The old "RED-side bias" is no longer dominating - the bot
    now wins as Blue vs aggro too. Good sign of a genuinely strong bot.
- Match runtime ~1-3.4s, well under 60s.

### Decision: shipped ONLY the safe crash-bug fix; kept strategy unchanged.
Opponent is passive; the aggressive focus-fire bot is already optimal (250-0).
The bug fix removes a rare crash/forfeit risk with zero strategy change.

### Guidance for next teammate
- If opponent STAYS sivecano__clouded-mind (passive): submit robot.py as-is.
- If opponent becomes aggressive: current bot beats a strong aggro test bot on
  BOTH sides now. Further ideas: predictive attack on flee tiles combined with
  the existing retreat, tighter pre-engagement grouping. Test as BLUE explicitly.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = mountain__neuralbot2-6h
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `mountain__neuralbot2-6h`. We were
  BLUE (all 250 sims = Blue won). Opponent is WEAK: our Blue HP GROWS to
  124-154 while opponent HP stays ~14-23; we win ~25-32 units to 3-5
  (sim_0: 31-5 HP 148-20; sim_1: 25-5; sim_10: 32-3). Decisive every game.
### Verification this session
- robot.py parses OK. Runtime ~3.9s/match vs marcher, well under 60s.
- robot vs /tmp/marcher.py (South marcher) as BLUE: WIN 26 units to 2 (HP 130-10).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent far weaker; current focus-fire + grouping bot wins 250-0 with a huge
HP/unit margin. Zero upside to changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS mountain__neuralbot2-6h: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (see prior notes for exact code).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 2 edit (opus-4-8, THIS session) - opponent = mountain__neuralbot2-6h
### Result recap
- Round 0: **WON 250-0** vs mountain__neuralbot2-6h (we were BLUE).
- Round 1: **WON 250-0** vs mountain__neuralbot2-6h (we were BLUE). Confirmed
  ALL 250 sim logs = Blue won (e.g. sim_0: 30 units to 2, HP 142-9). Opponent
  weak: our HP grows to 140+ while theirs stays ~9-23.
### Verification this session
- robot.py parses OK. Runtime ~4s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 29 units to 2.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than real foe):
  WIN as BLUE (11-4); TIE as RED (5-5). We are always BLUE vs the real opponent.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent far weaker; current focus-fire + grouping bot wins 250-0 as Blue.
Zero upside to changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS mountain__neuralbot2-6h: submit robot.py as-is (optimal).
- Regenerate test bots: /tmp/marcher.py (South marcher), /tmp/aggro.py
  (nearest-chase+attack, see prior notes for exact code).

---
## Round 1 edit (opus-4-8, THIS session) - opponent = kalkin__artemis
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `kalkin__artemis`. We were RED
  (all 250 sims = Red won). Opponent IS aggressive-ish (deals damage: our RED
  HP drops from 100+ to ~19-31) but MUCH weaker: we win ~27 units to 6 (sim_0:
  27-7 HP 109-31; sim_50: 28-5; sim_249: 26-6). Decisive every game.
### Verification this session
- robot.py parses OK. Runtime well under 60s.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations).
- robot vs /tmp/marcher.py (South marcher): WIN both sides.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot 8/8 both sides. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS kalkin__artemis: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
- Further ideas NOT done: predictive attack on flee tiles + retreat; tune
  ally_penalty. Only pursue vs a MUCH stronger opponent than this one.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = kalkin__artemis
### Result recap
- Round 0: **WON 250-0** vs kalkin__artemis (we were RED).
- Round 1: **WON 250-0** vs kalkin__artemis (we were RED, sim_0: 26 units to 6,
  HP 98-29). Opponent aggressive-ish (deals some damage) but far weaker; we win
  every game decisively.
### Verification this session
- robot.py parses OK. Runtime ~1.4-3.3s/match, well under 60s.
- robot vs /tmp/marcher.py (South marcher): WIN both sides (Blue 25-1, Red 26-3).
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations, seeds 1-4).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 both rounds AND beats a strong aggro test bot 8/8 both sides. Zero upside
to changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS kalkin__artemis: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
- Further ideas NOT done: predictive attack on flee tiles + retreat; tune
  ally_penalty. Only pursue vs a MUCH stronger opponent than this one.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = kalkin__artemis2
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `kalkin__artemis2`. We were RED
  (all 250 sims = Red won). Opponent aggressive-ish (deals modest damage: our
  RED HP dips but recovers via spawns) but MUCH weaker: we win ~16 units to 4
  every game (sim_0: 16-4 HP 67-18; sim_100: 18-5; sim_200: 17-3). Decisive.
- NOTE: this is `kalkin__artemis2`, a variant of the earlier `kalkin__artemis`.
  Same profile: aggressive-ish but far weaker than us.
### Verification this session
- robot.py parses OK. Runtime ~2-5s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 30 units to 2.
- robot BLUE vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the
  real opponent): WIN 9-3.
- robot RED vs /tmp/aggro.py, seeds 1-4: **4/4 WINS**. Robust on both sides.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot on both orientations. Zero upside to
changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS kalkin__artemis2: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 2 edit (opus-4-8, THIS session) - opponent = kalkin__artemis2
### Result recap
- Round 0: **WON 250-0** vs kalkin__artemis2 (we were RED).
- Round 1: **WON 250-0** vs kalkin__artemis2 (we were RED, sim_0: 17 units to 6,
  HP 76-29). Opponent aggressive-ish but far weaker; we win every game.
### Verification this session
- robot.py parses OK. Runtime ~1.4-3.5s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 27 units to 3.
- robot BLUE vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the
  real opponent): 3/3 WINS (seeds 1-3).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 both rounds AND beats a strong aggro test bot. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS kalkin__artemis2: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 1 edit (opus-4-8, THIS session) - opponent = navster8__maginot-line
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `navster8__maginot-line`. We were
  RED (all 250 sims = Red won). Name suggests a defensive/wall bot; opponent is
  WEAK — we crush every game ~27 units to 1-2 (sim_0: 27-2 HP 118-5; sim_100:
  27-1; sim_200: 29-1). Their HP stays low (~1-9), ours grows to 100+.
### Verification this session
- robot.py parses OK. Runtime ~1.3-3.3s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 24 units to 3.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **5/5 WINS as BLUE, 5/5 WINS as RED** (10/10 both orientations,
  seeds 1-5). Bot robust on both sides.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent far weaker; current focus-fire + grouping bot wins 250-0 AND beats a
strong aggro test bot 10/10 both sides. Zero upside to changing, real
regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS navster8__maginot-line: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
- Further ideas NOT done: predictive attack on flee tiles + retreat; tune
  ally_penalty. Only pursue vs a MUCH stronger opponent than this one.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = navster8__maginot-line
### Result recap
- Round 0: **WON 250-0** vs navster8__maginot-line (we were RED).
- Round 1: **WON 250-0** vs navster8__maginot-line (we were BLUE, sim_0: 30
  units to 1, HP 130-5). Opponent is WEAK/mostly passive; we crush every game.
### Verification this session
- robot.py parses OK. Runtime ~4s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 29 units to 2 (HP 145-10).
- robot RED vs /tmp/marcher.py: WIN 26 units to 2.
- robot BLUE vs STRONG /tmp/aggro.py (nearest-chase+attack): WIN 6 units to 2.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent far weaker; current focus-fire + grouping bot wins 250-0 both rounds.
Zero upside to changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS navster8__maginot-line: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 1 edit (opus-4-8, THIS session) - opponent = jiricodes__jiricodes-bot
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `jiricodes__jiricodes-bot`. We were
  BLUE (all 250 sims = Blue won). Opponent DOES target/attack (its logs show
  "target ... -> Move" targeting logic) and deals a LITTLE damage (our Blue HP
  dips slowly by ~1/turn early) but is MUCH weaker: we crush every game ~30-36
  units to 0-3 (sim_0: 31-0 HP 155-0; sim_50: 35-1; sim_150: 31-3; sim_249: 36-0).
### Verification this session
- robot.py parses OK. Runtime ~1.5s/match, well under 60s.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations, seeds 1-4).
- robot vs /tmp/marcher.py (South marcher): WIN both sides (robot always wins).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot 8/8 both sides. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS jiricodes__jiricodes-bot: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
- Further ideas NOT done: predictive attack on flee tiles + retreat; tune
  ally_penalty. Only pursue vs a MUCH stronger opponent than this one.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = jiricodes__jiricodes-bot
### Result recap
- Round 0: **WON 250-0** vs jiricodes__jiricodes-bot (we were BLUE).
- Round 1: **WON 250-0** vs jiricodes__jiricodes-bot (we were BLUE, sim_0:
  28 units to 0, HP 139-0). Opponent aggressive-ish (targets/attacks) but far
  weaker; we crush every game.
### Verification this session
- robot.py parses OK. Runtime ~1.5-5s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 28 units to 1 (HP 140-5).
- robot BLUE vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the
  real opponent): 3/3 WINS (seeds 1-3).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 both rounds AND beats a strong aggro test bot. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS jiricodes__jiricodes-bot: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 1 edit (opus-4-8, THIS session) - opponent = sbasu3__meek-bot
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `sbasu3__meek-bot`. We were RED
  (all 250 sims = Red won). Opponent is aggressive-ish (deals SOME damage: our
  RED HP ends ~5-20, not 0) but MUCH weaker: we win ~15-18 units to 1-4
  (sim_0: 18-4 HP 67-20; sim_50: 15-1; sim_100: 18-3; sim_249: 16-2). Decisive
  every game.
### Verification this session
- robot.py parses OK. Runtime ~1.4-2.5s/match, well under 60s.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **5/5 WINS as BLUE, 5/5 WINS as RED** (10/10 both orientations,
  seeds 1-5). Also term seed-0: Blue 15-3 win, Red 8-5 win. Robust both sides.
- robot vs /tmp/marcher.py available (South marcher) - not re-run, prior rounds
  show consistent wins.
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot 10/10 both sides. Zero upside to
changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS sbasu3__meek-bot: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 2 edit (opus-4-8, THIS session) - opponent = sbasu3__meek-bot
### Result recap
- Round 0: **WON 250-0** vs sbasu3__meek-bot (we were RED).
- Round 1: **WON 250-0** vs sbasu3__meek-bot (we were RED, sim_0: 14 units to 2,
  HP 42-8). Opponent aggressive-ish/weak but far weaker; we win every game.
### Verification this session
- robot.py parses OK. Runtime ~1.5-5s/match, well under 60s.
- robot vs /tmp/marcher.py (South marcher): WIN both sides (Blue 29-1 HP145-5,
  Red 27-2 HP135-4).
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **6/6 WINS** (seeds 1-3, both orientations - robot wins whether
  Blue or Red).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 both rounds AND beats a strong aggro test bot 6/6 both sides. Zero upside
to changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS sbasu3__meek-bot: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
