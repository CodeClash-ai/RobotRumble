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

---
## Round 1 edit (opus-4-8, THIS session) - opponent = essickmango__fruity-test
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `essickmango__fruity-test`. We were
  BLUE (all 250 sims = Blue won). Opponent is aggressive-ish (deals a little
  damage: our Blue HP dips but grows via spawns; Red HP ends ~2-21) but MUCH
  weaker: we win ~16-21 units to 1-5 (sim_0: 17-2 HP 72-10; sim_100: 21-5;
  sim_200: 21-4; sim_249: 16-5). Decisive every game.
### Verification this session
- robot.py parses OK. Runtime ~1.4-4.5s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 31 units to 1 (HP 155-5).
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): 3/3 WINS as BLUE, 3/3 WINS as RED (6/6 both orientations, seeds 1-3).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot 6/6 both sides. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS essickmango__fruity-test: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 2 edit (opus-4-8, THIS session) - opponent = essickmango__fruity-test
### Result recap
- Round 0: **WON 250-0** vs essickmango__fruity-test (we were BLUE).
- Round 1: **WON 250-0** vs essickmango__fruity-test (we were BLUE, sim_0:
  24 units to 3, HP 96-12). Opponent aggressive-ish but far weaker; we crush.
### Verification this session
- robot.py parses OK. Runtime ~1.3-3.2s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 24 units to 0 (HP 120-0).
- robot BLUE vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the
  real opponent): 3/3 WINS (seeds 1-3).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 both rounds AND beats a strong aggro test bot. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS essickmango__fruity-test: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 1 edit (opus-4-8, THIS session) - opponent = tabaxi3k__charles
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `tabaxi3k__charles`. We were RED
  (all 250 sims = Red won). Opponent aggressive-ish but MUCH weaker: we win
  ~20-30 units to 1-3 (sim_0: 30-1 HP 146-5; sim_100: 21-3; sim_249: 25-2).
  Decisive every game.
### Verification this session
- robot.py parses OK. Runtime ~1.5-3.2s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 21 units to 3 (HP 105-15).
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations, seeds 1-4).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot 8/8 both sides. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS tabaxi3k__charles: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 2 edit (opus-4-8, THIS session) - opponent = tabaxi3k__charles
### Result recap
- Round 0: **WON 250-0** vs tabaxi3k__charles (we were RED).
- Round 1: **WON 250-0** vs tabaxi3k__charles (we were RED, sim_0: 30 units to 1,
  HP 146-3). Opponent aggressive-ish but far weaker; we crush every game.
### Verification this session
- robot.py parses OK. Runtime ~1.4-3.7s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 24 units to 3 (HP 120-13).
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): 3/3 WINS as BLUE, 3/3 WINS as RED (6/6 both orientations, seeds 1-3).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 both rounds AND beats a strong aggro test bot 6/6 both sides. Zero upside
to changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS tabaxi3k__charles: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 1 edit (opus-4-8, THIS session) - opponent = devchris__first_test
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `devchris__first_test`. We were
  RED (all 250 sims = Red won). Opponent is aggressive-ish (deals SOME early
  damage: HP dips to ~16-16 by turn ~10) but MUCH weaker: we win ~31 units to 3
  (sim_0: 31-3 HP 151-15). Decisive every game (verified 250/250 Red wins).
### Verification this session
- robot.py parses OK. Runtime ~1.5-3s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 24 units to 1 (HP 120-5).
- robot RED vs /tmp/marcher.py: WIN 29 units to 2 (HP 145-8).
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations, seeds 1-4).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot 8/8 both sides. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS devchris__first_test: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 2 edit (opus-4-8, THIS session) - opponent = devchris__first_test
### Result recap
- Round 0: **WON 250-0** vs devchris__first_test (we were RED).
- Round 1: **WON 250-0** vs devchris__first_test (we were RED, sim_0: 27 units
  to 2, HP 135-10). Opponent aggressive-ish but far weaker; we crush every game.
### Verification this session
- robot.py parses OK. Runtime ~1.4-1.7s/match, well under 60s.
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations, seeds 1-4).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 both rounds AND beats a strong aggro test bot 8/8 both sides. Zero upside
to changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS devchris__first_test: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 1 edit (opus-4-8, THIS session) - opponent = aaa__jippty5
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `aaa__jippty5`. We were BLUE
  (all 250 sims = Blue won). Opponent is aggressive-ish (early trading is even,
  ~1 HP/turn each side turns 1-10) but MUCH weaker: we pull ahead decisively and
  win ~15-19 units to 5-6 (sim_0: 16-5 HP 51-25; sim_50: 17-5; sim_249: 19-6).
### Verification this session
- robot.py parses OK. Runtime well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 25 units to 1 (HP 125-1).
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations, seeds 1-4).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot 8/8 both sides. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS aaa__jippty5: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 2 edit (opus-4-8, THIS session) - opponent = aaa__jippty5
### Result recap
- Round 0: **WON 250-0** vs aaa__jippty5 (we were BLUE).
- Round 1: **WON 248-0** with **2 TIES** vs aaa__jippty5 (we were BLUE, sim_0:
  14 units to 6, HP 39-22). The 2 ties (sim_163, sim_222) ended with EQUAL unit
  counts (9-9, 10-10) => tie (win is purely by unit count at turn 100; HP is
  NOT a tiebreaker - verified in logic/logic/src/lib.rs
  determine_winner_from_units_count: equal max => None/tie).
- Opponent aggressive-ish but weaker; in tie seeds it traded 1-for-1 evenly.

### What I changed (robot.py) - LATE-GAME UNIT PRESERVATION
- Added a late-game retreat rule to help convert TIES into WINS: when
  `state.turn >= 88` and a fragile unit (health <= 2) is adjacent to an enemy
  but CANNOT secure a kill this turn, it RETREATS instead of feeding an
  even/losing trade. Preserving unit count late is what wins (count-only win).
- One-block change in robot() (the `should_retreat` gate). Everything else
  (focus-fire, grouping, boxed-priority attack) unchanged.

### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- new (Blue) vs STRONG /tmp/aggro.py, seeds 1-16: **15W 1T, 0 losses**.
  baseline (Blue) vs aggro seeds 1-16: 15W 1L. => new converted a loss->tie,
  NO regressions. (aggro is STRONGER than the real opponent.)
- new vs /tmp/marcher.py (South marcher) both orientations seeds 1-4: robot
  wins ALL 8. No regression vs passive.
- new vs baseline self-play seeds 1-10 both orientations: 9W-10L-1T ~ wash
  (side bias dominates in strong-vs-strong; expected, not a concern).
- robot.py parses OK; runtime ~1.5s/match, well under 60s.

### Decision: shipped the safe late-game preservation change.
Marginal, low-risk improvement aimed at the 2 ties; no regressions found.

### Guidance for next teammate
- If opponent STAYS aaa__jippty5: robot.py wins ~248-0-2; safe to submit.
  The late-game retreat may shave a tie or two into wins.
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
- If ties persist, consider: retreat threshold turn (try 85 vs 90), or an
  explicit "preserve count when even" late strategy. Tune the late_game turn.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = jay0jayjay__naivestarter
### Result recap
- Round 0 (/logs/rounds/0/): **WON 250-0** vs `jay0jayjay__naivestarter`. We were
  BLUE (all 250 sims = Blue won). Opponent is aggressive-ish (early trading is
  roughly even, both HP drop ~1/turn turns 5-10) but MUCH weaker: we pull ahead
  decisively and win ~22-29 units to 3-7 (sim_0: 25-3 HP 77-8; sim_50: 23-4;
  sim_100: 22-7; sim_249: 29-5). Decisive every game (250/250 Blue wins).
### Verification this session
- robot.py parses OK. Runtime ~1.5-4.5s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 31 units to 3 (HP 155-15).
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations, seeds 1-4).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 AND beats a strong aggro test bot 8/8 both sides. Zero upside to changing,
real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS jay0jayjay__naivestarter: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 2 edit (opus-4-8, THIS session) - opponent = jay0jayjay__naivestarter
### Result recap
- Round 0: **WON 250-0** vs jay0jayjay__naivestarter (we were BLUE).
- Round 1: **WON 250-0** vs jay0jayjay__naivestarter (we were BLUE, sim_0:
  22 units to 6, HP 56-20). Opponent aggressive-ish (trades ~1 HP/turn early)
  but far weaker; we pull ahead and crush every game.
### Verification this session
- robot.py parses OK. Runtime ~1.3-3.2s/match, well under 60s.
- robot BLUE vs /tmp/marcher.py (South marcher): WIN 27 units to 2 (HP 135-10).
- robot vs STRONG /tmp/aggro.py (nearest-chase+attack, stronger than the real
  opponent): **4/4 WINS as BLUE, 4/4 WINS as RED** (8/8 both orientations, seeds 1-4).
### Decision: KEPT robot.py UNCHANGED (proven 250-0 baseline).
Opponent aggressive-ish but far weaker; current focus-fire + grouping bot wins
250-0 both rounds AND beats a strong aggro test bot 8/8 both sides. Zero upside
to changing, real regression risk. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS jay0jayjay__naivestarter: submit robot.py as-is (optimal).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`

---
## Round 1 edit (opus-4-8, THIS session) - opponent = luisa__luisasrobot
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 247-1** with **2 TIES** vs
  `luisa__luisasrobot` (we were RED). Opponent is COMPETITIVE (deals damage,
  trades ~1 HP/turn; mid-game unit counts even). We win almost every game
  (sim_0: 13 units to 5). The 1 loss (sim_2: Blue 8 units, us Red 6) and 2 ties
  (sim_10: 8-8; sim_202: 9-9) all ended with us AHEAD in HP but EVEN/behind in
  UNITS — HP is NOT a tiebreaker (win = most units at turn 100). Late game we
  traded units down 1-for-1 to a tie despite a HP lead.

### What I changed (robot.py) - STRONGER LATE-GAME UNIT PRESERVATION
- Broadened the existing late-game retreat: was `turn>=88 and health<=2`.
  Now `turn>=85 and health<=3 AND we are NOT behind in unit count`
  (`my_units >= enemy_units`). A fragile unit that can't secure a kill retreats
  instead of feeding an even trade -> converts ties/close losses into wins by
  preserving our numeric lead. The `my_units>=enemy_units` gate keeps us
  aggressive when BEHIND (we must trade to catch up).
- Everything else (focus-fire, grouping, boxed-priority attack, 1-HP/outnumbered
  retreat) unchanged.

### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- new vs STRONG /tmp/aggro.py (nearest-chase+attack, STRONGER than real foe):
  **12/12 WINS** (6 as Blue, 6 as Red, seeds 1-6). No regression.
- new vs /tmp/marcher.py (South marcher): WIN both sides (~3.7s runtime).
- new vs baseline self-play seeds 1-5 both orientations: wash (side bias between
  two strong bots), NO losses indicating regression.
- robot.py parses OK; runtime ~3.7s/match, well under 60s.

### Guidance for next teammate
- If opponent STAYS luisa__luisasrobot: robot.py wins ~247-1-2; the late-game
  preservation should shave the ties/close loss into wins. Safe to submit.
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
- Further ideas NOT done: predictive attack on flee tiles + retreat combined;
  tune late-game turn threshold (85) / health cap (3). This opponent is
  competitive but clearly beaten; only pursue bigger changes vs a stronger foe.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = luisa__luisasrobot
### Result recap
- Round 0: **WON 247-1** with 2 TIES vs luisa__luisasrobot (we were RED).
- Round 1: **WON 244-1** with 5 TIES vs luisa__luisasrobot (we were BLUE).
- Opponent is COMPETITIVE (trades damage; keeps HIGHER HP than us in close
  games). Analyzed /logs/rounds/1: the 5 ties all ended with EQUAL units but us
  BEHIND in HP; the 1 loss (sim_228) was 4 units to 9 - we got out-numbered
  early and the opponent snowballed via spawns. Win = most units at turn 100
  (HP is NOT a tiebreaker).

### What I changed (robot.py) - EVEN-GAME UNIT PRESERVATION (tested upgrade)
- Added an `even_game` retreat gate: `state.turn >= 50 and my_units <=
  enemy_units`. When we are NOT ahead in unit count from turn 50 on, a fragile
  unit (health <= 2) that CANNOT secure a kill this turn RETREATS instead of
  feeding an even 1-for-1 trade. Preserving fragile units when even is what
  converts TIES into WINS (count-only win condition). Kept aggressive when
  AHEAD (gate requires my_units <= enemy_units) so we still press advantages.
- One-block change in robot() (the should_retreat gate). Everything else
  (focus-fire, grouping, boxed-priority attack, late-game retreat) unchanged.

### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- vs STRONG /tmp/aggro.py (nearest-chase+attack, STRONGER than real opponent):
  * variant BLUE seeds 1-10: **10/10 WINS** (baseline 9/10 - flipped a loss).
  * variant RED  seeds 1-8:  **8/8 WINS** (baseline 7/8 - flipped a loss).
  * term seed-0 BLUE: variant WON 10-7; baseline LOST 6-10. Clear fix on the
    exact loss pattern (early out-number).
- variant vs baseline head-to-head seeds 1-10 both orientations: variant won
  ~13/20 (6-4 as Blue, 8-2 as Red) => genuine improvement, NOT just side bias.
- variant vs /tmp/marcher.py (South marcher) both orientations: wins ALL 6.
  No regression vs passive.
- robot.py parses OK; runtime ~1.5s/match, well under 60s.

### Decision: SHIPPED the even-game preservation change (low-risk, tested win).
No regressions found on any test; strictly better or equal vs strong aggro on
BOTH sides, and better head-to-head vs the prior baseline.

### Guidance for next teammate
- If opponent STAYS luisa__luisasrobot: robot.py wins ~244-247/250; this edit
  should shave more of the ties/losses. Safe to submit.
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
- Further ideas NOT done: predictive attack on flee tiles combined with retreat;
  tune even_game turn threshold (50) / health cap (2); stronger early grouping
  to avoid the early out-number snowball seen in sim_228.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = luisa__baselinegere (COMPETITIVE)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 247-1** with **2 TIES** vs
  `luisa__baselinegere` (we were RED). Opponent is COMPETITIVE - trades damage
  and keeps HIGHER unit count in close games.
- Analyzed the 3 non-wins (sim_1 tie 10-10, sim_118 loss 8-9, sim_178 loss
  10-11): in ALL of them we had a big HP LEAD but tied/lost on UNIT COUNT.
  Key finding in sim_1: at ~turn 90 we were AHEAD 12-10 units, then we TRADED
  DOWN to 10-10 while opponent lost ZERO units. i.e. we throw away a numeric
  lead late by making even/losing trades. Win = most units at turn 100 (HP is
  NOT a tiebreaker - verified in lib.rs).

### What I changed (robot.py) - PROTECT-LEAD late-game retreat (tested)
- Added `protect_lead = state.turn >= 80 and my_units > enemy_units`. When we
  are AHEAD in unit count from turn 80 on, a unit with health <= 3 that CANNOT
  secure a kill AND whose adjacent target is NOT boxed (i.e. a real trade, not
  a guaranteed free hit) RETREATS to preserve the numeric lead.
- Tuning note: I first tried health<=4 but that was slightly too passive vs a
  strong chaser (lost 1 more game vs /tmp/aggro seeds 9-16). health<=3 matches
  baseline vs aggro with NO regression and still preserves fragile units.

### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- NEW(red) vs STRONG /tmp/aggro.py: seeds 1-8 = 8/8 WINS; seeds 9-16 = 4W/3L
  (== baseline, NO regression). BLUE vs aggro seeds 1-8 = 8/8 WINS.
- NEW(red) vs baseline(blue) seeds 1-10: 5W-4L-1T (slight edge to new).
- NEW vs /tmp/marcher.py (South marcher): wins BOTH sides. No regression.
- robot.py parses OK; runtime ~2s/match, well under 60s.

### Decision: shipped the low-risk protect-lead change targeting the tie/loss
failure mode (trading down a lead). No regressions found in any test.

### Guidance for next teammate
- If opponent STAYS luisa__baselinegere: robot.py wins ~247+/250; the
  protect-lead retreat should shave the ties/close losses. Safe to submit.
- Regenerate test bots (Action/Direction/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
- Further ideas NOT done: tune protect_lead turn(80)/health(3); the retreat
  when ahead can be caught by a fast chaser - consider grouping retreats so
  units back off together toward the corner rather than scattering.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = luisa__baselinegere (COMPETITIVE)
### Result recap
- Round 0: **WON 247-2** with 1 TIE vs luisa__baselinegere (we were RED).
- Round 1: **WON 246-3** with 1 TIE vs luisa__baselinegere (we were BLUE).
- Analyzed the 4 non-wins in round 1 (sim_133 tie 10-10, sim_187 loss 7-9,
  sim_220 loss 10-11, sim_222 loss 6-11). In ALL of them we had a big HP LEAD
  but lost/tied on UNIT COUNT (win = most units at turn 100; HP NOT tiebreaker).
- FAILURE MODE (sim_222 trace): our units SCATTER across the whole map fighting
  individually. Many drop to 1 HP and feed kills while the opponent keeps its
  units at ~5 HP (preserved). At turn 40 we were AHEAD 8-3, then spawns + our
  scattered low-HP units dying let the opponent snowball to 6-11 by turn 100.

### Experiments (ALL tested, NONE shipped - each regressed on RED side)
Test bots (regenerated this session, gone next round):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py` (== current robot.py).
Variants tried:
1. /tmp/variant.py = BROAD mid-game fragile retreat: retreat any health<=2 unit
   that can't kill when target isn't boxed. vs aggro as BLUE: 8W1L1T (baseline
   10/10 - REGRESSION). Head-to-head vs baseline: BLUE 5-5 wash, RED only 3/10.
   Retreating fragile units lets a chaser pick them off. REJECTED.
2. /tmp/variant2.py = fold grouping into distance sort
   (key=(dist*3+min(ally_pen,6), ally_pen)) for TIGHTER movement. vs aggro:
   10/10 as BLUE, 7W1T as RED (baseline 8/8 RED). Head-to-head vs baseline:
   BLUE 5-4-1, but RED only 2/10 (slows aggression too much). REJECTED.

### KEY FINDING: strong RED-side map bias dominates head-to-head self-play.
Both variants win ~half as Blue but LOSE badly as Red vs baseline. Since we
play BOTH sides across rounds, a change that helps Blue but hurts Red is a net
loss. The baseline is well-balanced (8/8 or 10/10 vs strong aggro on BOTH sides).

### Decision: KEPT robot.py UNCHANGED (proven balanced baseline, 246-247/250).
No tested variant robustly beat the baseline on both orientations. Changing
risks regression with marginal upside. robot.py parses OK, runtime ~1.4-2.6s.

### Guidance for next teammate (to actually beat the close games)
The real lever for count-based wins vs this competitive foe is to STOP our
units scattering to 1 HP and feeding kills, WITHOUT becoming exploitable by a
chaser. Untried ideas that might avoid the RED-side regression:
- A retreat that moves TOWARD allies (regroup) rather than just away from the
  nearest enemy - keeps fragile units useful and in formation. Current
  retreat() only maximizes distance from nearest enemy (can scatter further).
- Reduce OVERKILL: don't send 3 units to chip 1 enemy if 2 suffice; spread the
  extra to protect flanks / kill a second enemy. Faster net kills = higher count.
- Tune the focus target to the enemy the MOST allies can reach in 1-2 moves
  (gang-kill before spawn refresh) instead of just the weakest.
- Whatever you try, TEST BOTH orientations vs /tmp/aggro.py AND head-to-head vs
  /tmp/robot_baseline.py; reject anything that drops below ~7/10 as RED.

---
## Round 0 edit (opus-4-8, THIS session) - opponent = anton__anton4000 (COMPETITIVE)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 238-3** with **9 TIES** vs
  `anton__anton4000` (we were BLUE). Opponent is COMPETITIVE — it TRADES damage
  and PRESERVES HP/units better than us in close games.
- Analyzed all 250 sims: the 9 ties ALL ended EQUAL on units but us BEHIND on HP
  (e.g. sim_0: 15-15 units, HP 47-62). The 3 losses ended slightly behind on
  units (sim_102: 13-15, sim_208: 11-13, sim_22: 12-13). Win = most units at
  turn 100 (HP is NOT a tiebreaker).
- FAILURE MODE (sim_0 turn-by-turn): at turn 40 we were AHEAD 8-5 units, but by
  turn 100 it was TIED 15-15. We build an early lead then trade it away 1-for-1
  while the opponent preserves its units; late-game spawns (4/team/10 turns)
  dominate and they catch up.

### Experiments (ALL tested vs baseline self-play, NONE shipped - all regressed)
Test bots regenerated this session (gone next round):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than the real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py` (== current robot.py).
  * /tmp/batch.sh: helper -> `/tmp/batch.sh BLUE.py RED.py NSEEDS` (uses
    `./rumblebot run batch`, prints {"winner":...} per seed). Keep NSEEDS<=8 or
    the 30s command wall-clock times out (batch is slow; ~2s/game).
Variants tried (all made us MORE passive to preserve the lead -> LOST aggression
and REGRESSED vs baseline in self-play):
1. /tmp/variant.py: protect_lead turn>=60 + big_lead(turn>=40, health<=4)
   retreat. Blue vs baseline: 4W-6L-2T. REJECTED (too passive early).
2. /tmp/variant2.py: protect_lead turn>=65. Blue vs baseline: 3W-4L-1T. REJECTED.
3. /tmp/variant3.py: when can't-kill & not-boxed & lone attacker, step_toward
   enemy instead of attacking (avoid whiff). Blue vs baseline: 3W-5L. REJECTED
   (loses damage output by chasing instead of hitting).
4. /tmp/v4.py: protect_lead turn>=70 (was 80). Blue vs baseline: 3W-2L-1T (~edge
   within noise); RED side was pure side-bias loss. NEUTRAL, not clearly better.

### KEY TAKEAWAY (consistent with all prior teammates)
- Making the bot MORE passive to "preserve leads" consistently LOSES aggression
  and regresses in self-play. The baseline is well-balanced. Self-play is noisy
  and dominated by a persistent side (map) bias, so it's a poor proxy for the
  real (unavailable) opponent.
- We ALREADY win ~95% (238-3-9) as BLUE vs anton__anton4000. No tested change
  gave a robust, clear improvement.

### Decision: KEPT robot.py UNCHANGED (proven balanced baseline).
Verified: parses OK; beats strong /tmp/aggro.py as BLUE (13-7); crushes marcher
(25-3). Runtime ~2s/game, well under 60s. Changing risks regression for marginal
upside vs an opponent we already dominate.

### Guidance for next teammate
- If opponent STAYS anton__anton4000: submit robot.py as-is (wins ~95%).
- The ONLY realistic lever to convert the 9 ties/3 losses (all EVEN/behind on
  units, ahead on HP) is to LOSE FEWER of our own units in the mid-late game
  WITHOUT going passive. Untried ideas that might avoid the passivity regression:
  * Retreat fragile units TOWARD allies (regroup) not just away from enemy, so
    they stay useful & in formation (current retreat() only maximizes distance
    from nearest enemy -> scatters).
  * Reduce OVERKILL: don't stack 3 attackers on 1 enemy if 2 suffice; redirect
    the 3rd to a second target -> more net kills per turn before spawn refresh.
  * Focus the enemy the MOST allies can reach in 1-2 moves (gang-kill fast).
  * ALWAYS test BOTH orientations vs /tmp/aggro.py AND head-to-head vs
    /tmp/robot_baseline.py; reject anything that drops below the baseline on the
    BLUE side (we are Blue vs this opponent).

---
## Round 2 edit (opus-4-8, THIS session) - opponent = anton__anton4000 (COMPETITIVE)
### Result recap
- Round 0: **WON 238-3** with 9 TIES vs anton__anton4000 (we were BLUE).
- Round 1: **WON 240-4** with 6 TIES vs anton__anton4000 (we were BLUE).
- Analyzed /logs/rounds/1 non-wins (6 ties + 4 losses): in ALL of them we ended
  EVEN-or-behind on UNITS **and** behind on HP (opponent preserves HP AND units
  better). Win = most units at turn 100 (HP NOT a tiebreaker).
- FAILURE MODE (sim_249 trace): even ~8-8 mid-game, then around spawn turns the
  opponent pulls ahead (8-10, then we trade DOWN 8->6->5 while they stay
  higher). We don't KILL fast enough before spawns refresh -> they snowball.

### What I changed (robot.py) - FASTER GANG-KILL FOCUS TARGET (tested, shipped)
- init_turn focus-target score changed from `(health, total_dist)` to
  `(-reachers, health, total_dist)` where `reachers` = # of our units within
  walking distance 3 of that enemy. => we now focus the enemy the MOST allies
  can converge on QUICKLY, securing kills faster (before the 10-turn spawn
  refresh). Pure OFFENSIVE change (not passivity - prior teammates showed
  passive/retreat changes REGRESS). One-block change; everything else unchanged.

### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- vs STRONG /tmp/aggro.py (nearest-chase+attack, STRONGER than real opponent):
  * v_focus BLUE seeds 1-16: **16/16 WINS** (baseline 15W/1T - flipped a tie).
  * v_focus RED seeds 1-6: **6/6 WINS**.
- v_focus(Blue) vs baseline(Red) head-to-head seeds 1-16: **10W-6L** => clearly
  better on OUR side (we are always BLUE vs the real opponent). As RED it was
  worse (side bias - self-play is noisy & Blue-biased; not a concern since we
  play Blue).
- v_focus vs /tmp/marcher.py both sides: wins ALL. No regression vs passive.
- CAVEAT: term seed-0 (deterministic) v_focus TIES aggro (7-7) where baseline
  WON (12-8). Single-seed edge case; aggregate seeds 1-16 v_focus is strictly
  better on Blue. Not a real-opponent concern (opponent != aggro).
- robot.py parses OK; runtime ~2.3s/match, well under 60s.

### Decision: SHIPPED the faster-gang-kill focus change (offensive, low-risk).
Clearly better on the BLUE side (our real side) vs both aggro and baseline;
addresses the root loss pattern (too-slow kills -> opponent snowballs on spawns).

### Guidance for next teammate
- If opponent STAYS anton__anton4000: robot.py wins ~240+/250; this edit should
  shave some of the close ties/losses by killing faster. Safe to submit.
- Regenerate test bots (Action/Direction/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
  * /tmp/batch.sh BLUE.py RED.py NSEEDS (keep NSEEDS<=8 to avoid 30s wall-clock).
- Untried ideas to further convert ties: reduce OVERKILL (don't stack 3
  attackers where 2 suffice; redirect extras to a 2nd target for more net
  kills/turn); tune `reachers` radius (3) or add a 2nd focus target for a
  second cluster. TEST BLUE side vs /tmp/aggro.py AND head-to-head vs baseline;
  reject anything that drops the BLUE win rate. Passive/retreat changes
  consistently REGRESS - avoid them.

---
## Round 0 edit (opus-4-8, THIS session) - opponent = aayyad__testbot (COMPETITIVE)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 220-18** with **12 TIES** vs
  `aayyad__testbot` (we were RED). Opponent is COMPETITIVE (trades damage and
  preserves units in close games). ~88% win rate.
### Failure-mode analysis (from sim logs)
- TWO loss patterns:
  1) EARLY SNOWBALL blowouts (sim_127 17-8, sim_9 13-5, sim_54 14-6): we get
     out-NUMBERED by turn ~15 (e.g. 8-5) and never recover; opponent snowballs
     via spawns to 15-19 units.
  2) LATE TRADE-DOWN of a lead/even game (sim_10 lost 9-8: at turn ~88 we were
     11-11, then dropped 11->10->9->8 in the last turns while Blue held). Many
     ties are EQUAL units, us AHEAD on HP (HP is NOT a tiebreaker - win = most
     units at turn 100).
### What I changed (robot.py) - REGROUP-AWARE RETREAT (tested, shipped)
- Rewrote retreat(): was "move to the free tile FARTHEST from nearest enemy"
  (this SCATTERS fragile units, a failure flagged by many prior teammates).
  Now: among tiles that INCREASE distance from the nearest enemy, pick the one
  that ALSO minimizes distance to allies (regroup key = (-dist_from_enemy,
  ally_penalty)). Fragile units back off TOWARD the group, staying useful and
  in formation instead of running off alone to die.
- Everything else (focus-fire, grouping, boxed-priority attack, the various
  retreat GATES) unchanged. The gates already existed; this makes the retreat
  MOVE itself smarter.
### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- Regenerated test bots: /tmp/aggro.py (nearest-chase+attack, STRONGER than
  real opponent), /tmp/marcher.py (South marcher), /tmp/robot_baseline.py.
  /tmp/batch.sh BLUE RED NSEEDS (keep NSEEDS<=6-8; batch is slow, ~2s/game,
  30s wall-clock cap per command).
- regroup(RED) vs aggro(BLUE) seeds 1-8: 7W 1T (baseline RED vs aggro 6/6).
- regroup(BLUE) vs aggro(RED) seeds 1-6: 6/6 WINS (balanced, like baseline).
- regroup(RED) vs baseline(BLUE) seeds 1-12: **7W-5L** (slight edge on OUR real
  side, RED). Seeds 1-6 3-3, seeds 7-12 4-2.
- regroup(RED) vs marcher: WIN 31-1. No regression vs passive.
- robot.py parses OK; runtime ~1.6s/match, well under 60s.
- CAVEAT: term seed-0 (deterministic) as BLUE ties aggro (baseline also close);
  single-seed edge case, we play RED vs the real opponent (win term seed-0 RED).
### Decision: SHIPPED regroup retreat (low-risk, slight edge on our RED side,
no regressions vs aggro/marcher). Targets the "scatter to death" failure mode.
### Guidance for next teammate
- If opponent STAYS aayyad__testbot: robot.py wins ~220+/250; safe to submit.
- The bigger untapped lever is the EARLY SNOWBLL (pattern 1): keep units GROUPED
  in turns 5-20 so we don't get out-numbered early. Prior teammates found broad
  grouping/passivity tweaks REGRESS on one side - test BOTH orientations vs
  /tmp/aggro.py AND head-to-head vs /tmp/robot_baseline.py; reject anything that
  drops below the baseline on the RED side (we are RED vs this opponent).
- Regenerate test bots (Action/Direction/State are globals, no logic import):
  * /tmp/aggro.py, /tmp/marcher.py, /tmp/robot_baseline.py (= git show HEAD:robot.py),
    /tmp/batch.sh (see above).

---
## Round 2 edit (opus-4-8, THIS session) - opponent = aayyad__testbot (COMPETITIVE)
### Result recap
- Round 0: **WON 220-18** w/ 12 TIES vs aayyad__testbot (we were RED).
- Round 1: **WON 225-18** w/ 7 TIES vs aayyad__testbot (we were BLUE).
- Analyzed /logs/rounds/1 non-wins (25 of them). CONSISTENT FAILURE MODE:
  we are EVEN through ~turn 40, then trade DOWN in the mid-late game while the
  opponent PRESERVES its units and snowballs on spawns (win = most units at
  turn 100; HP NOT a tiebreaker).
  * sim_110 (TIE 9-9): we were AHEAD 13-10 at turn 80, then dropped to a 9-9
    tie by turn 100 -- THREW AWAY a 3-unit lead in the last 20 turns.
  * sim_118 (LOSS 4-12): even until ~turn 40, then opponent pulled ahead and
    we bled from 7 units down to 4 in the last 15 turns.

### What I changed (robot.py) - STRONGER PROTECT-LEAD (big_lead gate)
- Added `big_lead = state.turn >= 75 and my_units >= enemy_units + 3`. When we
  hold a COMFORTABLE (>=3 unit) lead late, a unit with health <= 4 that CANNOT
  secure a kill this turn AND whose target is NOT boxed RETREATS to preserve
  the numeric lead (regroup-aware retreat backs off toward allies). One extra
  clause in the existing `should_retreat` gate; everything else unchanged.
- Tuning: first tried retreating ALL healthy units on big_lead -> term match
  showed it OVER-retreated (won 8-5 but fewer total units, 14->8). Capped at
  health <= 4 so full-HP (5) units stay aggressive; term match then 8-7 (better
  margin) while still winning. Low-risk: only fires when already ahead by 3+.

### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- vs STRONG /tmp/aggro.py (nearest-chase+attack, STRONGER than real opponent):
  * v_new BLUE seeds 1-6: 6/6 WINS (== baseline).
  * v_new RED  seeds 1-6: 5/6 WINS (== baseline). NO regression.
- v_new(BLUE) vs baseline(RED) seeds 1-6: 5-1 / 4-1 (Blue wins). Consistent
  with the known Blue-side bias; NO regression. (baseline BLUE vs v_new RED is
  also ~5-1 Blue -> head-to-head dominated by side bias, inconclusive as usual.)
- v_new BLUE vs /tmp/marcher.py: WIN. No regression vs passive.
- robot.py parses OK; runtime well under 60s.

### Decision: SHIPPED the big_lead protect-lead change (low-risk, targeted).
Only triggers when ahead by 3+ units at turn 75+ with fragile (<=4HP) units;
directly targets the "throw away a late lead -> tie" pattern (sim_110). No
regressions vs aggro/marcher on either orientation.

### Guidance for next teammate
- If opponent STAYS aayyad__testbot: robot.py wins ~90%; this edit should shave
  some late-lead ties into wins. Safe to submit.
- Regenerate test bots (Action/Direction/State globals, no logic import):
  * /tmp/aggro.py, /tmp/marcher.py, /tmp/robot_baseline.py (=git show HEAD:robot.py),
    /tmp/batch.sh BLUE RED NSEEDS (keep NSEEDS<=6, batch is slow ~2s/game, 30s cap).
- The remaining lever is the EARLY SNOWBALL (out-numbered by ~turn 40 -> lose,
  e.g. sim_118). Prior teammates found broad grouping/passivity tweaks regress
  on one side. Untried: reduce OVERKILL (redirect 3rd attacker on an enemy 2 can
  kill to a 2nd target) for more net kills/turn before spawn refresh. TEST BOTH
  orientations vs aggro AND head-to-head vs baseline; reject anything below
  baseline on either side.

---
## Round 0 edit (opus-4-8, THIS session) - opponent = edward__flail (STRONG!)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 156-87** with 7 TIES vs
  `edward__flail` (we were BLUE). ~62% win rate - by FAR the strongest opponent
  so far (87 losses!). Opponent out-fights us: in losses we're behind on BOTH
  units AND HP (e.g. 7-17, 8-14, HP 26-60).
### KEY FINDING (root cause of losses): SPAWN-TURN UNIT COUNT
- Traced sim_108 (LOSS) vs sim_0 (WIN) at the first spawn (turn 10->11):
  * WIN: after spawn we jumped 4->8 units (full 4 spawns), opp stayed 4.
  * LOSS: after spawn we only got 4->6 (lost 2!), opp got 4->8.
- Mechanic (logic/logic/src/lib.rs): on spawn turns (1,11,21,...) `clear_spawn`
  DELETES any unit still on a spawn tile, THEN `spawn_units` spawns up to 4/team
  ONLY on points where the tile AND its mirror are BOTH free. So units lingering
  in the spawn zone get WIPED **and** BLOCK our own new spawns -> we fall behind
  on unit count, which is the win condition. The strong opponent clears its
  spawn zone; our baseline sometimes didn't.
### What I changed (robot.py) - SPAWN EVACUATION (tested improvement)
- Added `spawn_turn_soon(state)` (turn%10 in {8,9,0}) and `evacuate_spawn`.
  In robot(), BEFORE combat: if a unit is on a spawn tile and a spawn/clear is
  imminent, it moves OFF the spawn zone (to a non-spawn free tile toward
  enemies/center). Exception: it will NOT abandon a GUARANTEED kill that turn.
- This ensures we (a) never get wiped on spawn turns and (b) never block our own
  spawns -> we reliably get the full +4 units each spawn.
### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- vs /tmp/campbot.py (camps near spawn + attacks adjacent; mimics a foe that
  holds its spawn zone): new BLUE won **17 units** vs baseline's **12** (same
  opponent). Direct proof evacuation captures more spawns = higher final count.
- vs STRONG /tmp/aggro.py: new BLUE 6/6 wins; new RED 5W/1T (no losses). No
  regression either side.
- vs /tmp/marcher.py (South marcher): WIN 20-3.
- Head-to-head vs baseline is dominated by the known Blue-side map bias
  (inconclusive) - the campbot unit-count test is the meaningful signal.
- robot.py parses OK; runtime <2s/match, well under 60s.
### Decision: SHIPPED spawn evacuation (targets the exact loss root cause).
### Guidance for next teammate
- If opponent STAYS edward__flail: this should raise the win rate above 62%
  by winning more spawn races. Verify in next round's sim logs at turns 10/11.
- Regenerate test bots: /tmp/aggro.py, /tmp/marcher.py, /tmp/campbot.py
  (camp+attack), /tmp/robot_baseline.py (git show HEAD:robot.py), /tmp/batch.sh.
- Further ideas: tune spawn_turn_soon window (currently {8,9,0}); ensure units
  also don't RE-ENTER spawn tiles mid-decade. Consider pushing units toward the
  spawn points' MIRROR-free areas so more spawn slots open. Test unit-count
  margin vs campbot (the real lever) AND no-regression vs aggro both sides.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = edward__flail (STRONGEST)
### Result recap
- Round 1: **WON 154-82 with 14 TIES** vs edward__flail (we were RED). Strongest
  opponent yet (~63% win rate, 82 losses). Analyzed /logs/rounds/1 sim logs:
  * In LOSSES we are behind on BOTH units AND HP - opponent out-fights us.
  * ROOT CAUSE (traced sim_137, sim_5-8): edward__flail keeps its units
    CLUSTERED near its own spawn as a defensive BALL and picks off OUR units
    one-at-a-time as they advance into it. Its casualties are instantly replaced
    by nearby spawns; our reinforcements spawn far away and arrive piecemeal.
  * Spawn analysis (/tmp/spawn.py): in WINS we get +4 units/spawn reliably; in
    LOSSES we often get only +2/+3 (units bleeding in combat near enemy spawn).
### What I changed (robot.py) - ANTI-OVEREXTENSION (tested, shipped)
- Added `local_balance()` and `regroup_toward_allies()` helpers.
- In robot() before step_toward: if a unit is exactly 2 tiles from the nearest
  enemy, we are NOT ahead in unit count, turn<80, AND locally outnumbered by
  2+ (foes within radius 2 >= my allies +2), it REGROUPS toward allies instead
  of diving alone into the enemy cluster. Prevents feeding units one-by-one
  into edward's defensive ball. Gated tightly (dist==2, deficit>=2, turn<80) so
  it does NOT make us passive vs a pure aggressor.
### Testing (baseline = /tmp/robot_baseline.py = git HEAD pre-edit)
- Built /tmp/cluster.py (defensive-rally + attack-adjacent bot mimicking
  edward__flail). NEW as RED vs cluster: won 16-7 / 9-7 (baseline 14-5) -
  bigger unit margin = the intended improvement.
- NEW BLUE vs /tmp/aggro.py: 6/6 WINS (== baseline, no regression).
- NEW RED vs /tmp/aggro.py: 5W/1T seeds 1-6 (baseline 6W; seed1 became a TIE not
  a loss - within noise, tight gate). marcher RED: crush 26-3.
- robot.py parses OK; runtime well under 60s.
### Guidance for next teammate
- If opponent STAYS edward__flail: this should convert some overextension losses.
  VERIFY in next round's sim logs: are our units still diving the enemy ball at
  turns 20-50? Check unit-count trajectory (/tmp/trace.py sim_X.txt).
- Tuning knobs: local_balance radius (2), deficit threshold (2), dist trigger
  (==2), turn gate (<80). If still losing to overextension, try radius=3 or
  deficit>=1 BUT re-test vs /tmp/aggro.py BOTH sides (too passive = regression).
- Regenerate test bots: /tmp/aggro.py, /tmp/marcher.py, /tmp/cluster.py
  (defensive rally+attack), /tmp/robot_baseline.py (git show HEAD:robot.py),
  /tmp/batch.sh, /tmp/spawn.py, /tmp/trace.py, /tmp/analyze.py.

---
## Round 0 edit (opus-4-8, THIS session) - opponent = mousetail__genetic-robot (COMPETITIVE)
### Result recap
- Round 0 (/logs/rounds/0/): **WON 218-22 with 10 TIES** vs
  `mousetail__genetic-robot` (we were RED). ~87% win. Opponent COMPETITIVE:
  in all 22 losses Blue is ahead on BOTH units AND HP.
### ROOT CAUSE of losses (traced sim_22/12/52 spawn deltas via clear_spawn):
- Spawns are SYMMETRIC (lib.rs spawn_units): each free spawn-PAIR spawns 1 blue
  + 1 red simultaneously, so per-turn spawn COUNT is EQUAL for both teams.
- The ONLY way we end a spawn turn with FEWER units is `clear_spawn`: it DELETES
  any unit (ours) sitting ON a spawn tile at the start of the spawn turn, BEFORE
  spawning. In losses RED got +0/+1 late spawns (turns 80/90) while Blue got
  +3/+4 => our units were being WIPED on spawn tiles (retreat/regroup pushed
  fragile units back into our home spawn zone late-game, then clear_spawn nuked
  them -> we lose the count race, and count is the win condition).
### What I changed (robot.py) - SPAWN-TILE AVOIDANCE (low-risk, targeted)
- Added `bad_spawn_tile(state,c)` = `spawn_turn_soon(state) and c.is_spawn()`.
- retreat(), regroup_toward_allies(), and step_toward() now SKIP any candidate
  tile that is a bad_spawn_tile => our units never END a pre-spawn turn on a
  spawn tile and get wiped. evacuate_spawn already handled units already ON
  spawn tiles; this stops them RE-ENTERING via retreat/regroup/step.
### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- NEW RED vs /tmp/aggro.py (STRONGER than real foe): all wins (term 14-11,
  batch seeds 1-4 all Red). Baseline also all wins. NO regression.
- NEW RED vs /tmp/marcher.py: WIN 25-2 (baseline 26-1, equal; marcher doesn't
  contest spawns so no wipe scenario). No regression vs passive.
- Head-to-head NEW vs baseline: dominated by the known side (map) bias (Blue
  wins seeds 1,2; Red seed 3 in BOTH orientations) - inconclusive as always.
- robot.py parses OK; runtime ~2s/match, well under 60s.
### Decision: SHIPPED spawn-tile avoidance. It removes a self-inflicted unit
loss (getting wiped by clear_spawn) that was the documented root cause of the
count-race losses. Strictly-safe constraint; no regression found.
### Guidance for next teammate
- If opponent STAYS mousetail__genetic-robot: this should convert some
  losses/ties by stopping late-game spawn-tile wipes. VERIFY in next round's
  sim logs: check spawn deltas at turns 80/90 (use the python snippet reading
  Health lines, units are re.findall(r'\d+', line)[2:4]) - RED should now get
  +3/+4 like Blue, not +0/+1.
- Regenerate test bots: /tmp/aggro.py, /tmp/marcher.py, /tmp/robot_baseline.py
  (=git show HEAD:robot.py), /tmp/batch.sh (BLUE RED N, N<=5 for 30s cap).
- Further ideas: units may occasionally get STUCK (step_toward returns None if
  its only free tile is a spawn tile pre-spawn) - acceptable (staying safe), but
  could add a non-spawn fallback. Reduce OVERKILL for more net kills/turn.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = mousetail__genetic-robot (COMPETITIVE)
### Result recap
- Round 0: **WON 218-22 w/ 10 TIES** vs mousetail__genetic-robot (we were RED).
- Round 1: **WON 209-24 w/ 17 TIES** vs mousetail (we were BLUE). ~87% win.
- Analyzed /logs/rounds/1 non-wins (24 losses + 17 ties). Most losses are
  CLOSE (1-unit: sim_106 11-12, sim_175 11-12, sim_133 9-10, etc).
### ROOT CAUSE (traced trajectories via /tmp/trace.py):
  We are AHEAD or TIED at turn ~85-96, then TRADE DOWN in the FINAL turns
  (97-100) and lose the count race. e.g. sim_175: B15 R13 at t80 -> final
  B11 R12. sim_106: B12 R11 at t85 -> final B11 R12. We throw away a late
  lead by making even 1-for-1 trades in the last ~10 turns while the opponent
  preserves units. Win = MOST units at turn 100 (HP NOT a tiebreaker).
### What I changed (robot.py) - ENDGAME LOCK-IN (tested, shipped)
- Added `count_enemy_adjacent()` helper.
- New `endgame` retreat gate in should_retreat (turn >= 90):
  * If STRICTLY AHEAD in unit count: retreat ANY unit (any HP) adjacent to an
    enemy that it cannot secure a kill on this turn AND whose target is NOT
    boxed (i.e. a real trade, not a guaranteed free hit). Locks in the lead.
  * If TIED: only retreat when the fight is NOT locally favorable
    (local_favorable = my attackers on target > enemy units adjacent to me).
    If locally favorable we still attack (a favorable trade can push us AHEAD).
  * Never fires when BEHIND (we must trade to catch up).
- One added clause `or (endgame and not boxed_here)`; everything else unchanged.
### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- vs STRONG /tmp/aggro.py (nearest-chase+attack, STRONGER than real opponent):
  * NEW BLUE batch seeds 1-5: 5/5 WINS. term seed-0: TIE 11-11
    (BASELINE seed-0 as Blue LOST 7-10 -> NEW converted loss->tie AND preserved
    more units 11 vs 7). Direct proof the endgame lock-in helps close games.
  * NEW RED batch seeds 1-5: 4W 1T (NO losses). Balanced both sides.
- NEW vs /tmp/cluster.py (defensive rally+attack, mimics competitive foe):
  BLUE won 22-2 (baseline 19-1) - more of OUR units preserved at turn 100.
  Wins on both orientations vs cluster.
- NEW vs /tmp/marcher.py (South marcher): crush both sides (32-2, 26-3). No
  regression vs passive.
- robot.py parses OK; runtime ~1.9s/match, well under 60s.
### Decision: SHIPPED the endgame lock-in (offensive-preserving, low-risk).
Targets the EXACT documented loss pattern (throw away a late lead -> tie/loss).
Only fires turn>=90 when ahead/tied, never abandons a boxed kill, never fires
when behind. No regressions vs aggro/cluster/marcher on either orientation.
### Guidance for next teammate
- If opponent STAYS mousetail__genetic-robot: robot.py wins ~87%+; this edit
  should convert several of the close late-lead ties/losses into wins. VERIFY
  in next round's sim logs: check unit trajectory turns 90-100 (/tmp/trace.py
  sim_X.txt) - we should now HOLD our lead instead of trading down.
- Tuning knobs: endgame turn threshold (90 - try 88 if still trading down late),
  the tied-game local_favorable rule. If losses shift EARLIER, the lever is the
  mid-game trade-down (protect_lead turn>=80 / big_lead turn>=75 gates).
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/cluster.py: defensive rally + attack-adjacent (mimics competitive foe).
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
  * /tmp/batch.sh BLUE RED N (N<=5 to stay under 30s wall-clock; batch ~2s/game).
  * /tmp/trace.py sim_X.txt (prints B/R unit counts per turn).
  * /tmp/analyze.py (win/loss/tie summary for a round dir - EDIT logdir + which
    team we were, Blue=first number).

---
## Round 0 edit (opus-4-8, THIS session) - opponent = kalkin__maxad (COMPETITIVE)
### Result recap
- Round 0 (/logs/rounds/0/): **WON 223-15 w/ 12 TIES** vs `kalkin__maxad` (we
  were RED). ~89% win. All 15 losses are CLOSE (1-3 units: 9-7, 10-8, 12-11...).
### ROOT CAUSE (traced sim_125 losses via 'After turn N' unit counts):
  We are AHEAD/EVEN until ~turn 50-80, then TRADE DOWN mid-late. The clearest
  loss (sim_125): at end of turn 89 we were AHEAD R8 vs B6; at the SPAWN event
  (~turn 90/91) Blue got a FULL +4 spawn (6->10) while Red got +0 AND LOST a
  unit (8->7). i.e. our units were sitting ON red spawn tiles at the spawn turn:
  clear_spawn WIPES them AND blocks our own spawn pairs (spawn needs tile+mirror
  both free), so Blue snowballs +4 while we lose ground -> lose the count race.
### What I changed (robot.py) - WIDER SPAWN-EVACUATION WINDOW (low-risk)
- `spawn_turn_soon`: window widened from turn%10 in {8,9,0} to {7,8,9,0}. Gives
  units ONE extra turn to clear off spawn tiles before the clear_spawn wipe, so
  fewer of our units get wiped/block our own spawns near spawn turns. This is
  the ONLY change; everything else (focus-fire, grouping, boxed-attack, all
  retreat/endgame gates, evacuate_spawn, bad_spawn_tile avoidance) unchanged.
### Testing (baseline = /tmp/robot_current.py = git HEAD robot.py pre-edit)
- variant RED vs /tmp/aggro.py (nearest-chase+attack, STRONGER than real foe)
  seeds 1-3: identical to baseline (null,Red,Red) - NO regression. seeds 1-6:
  5W/1T. variant BLUE vs aggro seeds 1-2: 2/2 WINS. vs /tmp/marcher.py as RED:
  WIN. robot.py parses OK; runtime ~2s/match, well under 60s.
- CAVEAT: batch is SLOW (~2s/game) - keep NSEEDS<=3 to stay under the 30s
  per-command wall-clock (I hit a timeout at 6 seeds).
### Decision: SHIPPED the wider spawn-evac window. Targets the exact documented
loss root cause (spawn-tile wipe -> asymmetric spawn snowball) with a tiny,
low-risk constraint. No regressions found.
### Guidance for next teammate
- If opponent STAYS kalkin__maxad: robot.py wins ~89%+; this should shave a few
  spawn-wipe losses. VERIFY next round: at spawn turns (11,21,...,91) do BOTH
  teams get +4? (Compare unit counts across 'After turn N' markers.) If we still
  get wiped, units may be UNABLE to evacuate (surrounded) - consider a non-spawn
  fallback in evacuate_spawn or forcing evac priority even during combat.
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_current.py: `git show HEAD:robot.py`.
- The remaining lever is the mid-game trade-down (ahead at t50-80, lose by t100).
  Prior teammates found passive/retreat tweaks regress; reduce OVERKILL (redirect
  a 3rd attacker to a 2nd target for more net kills/turn) is untried. TEST both
  orientations vs aggro AND head-to-head vs baseline; reject any regression.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = kalkin__maxad (COMPETITIVE)
### Result recap
- Round 0: **WON 223-15 w/ 12 TIES** vs kalkin__maxad (we were RED).
- Round 1: **WON 235-5 w/ 10 TIES** vs kalkin__maxad (we were BLUE). ~94% win.
- Analyzed /logs/rounds/1 non-wins (5 losses + 10 ties). All losses are CLOSE
  (1-4 units, and behind on HP): sim_199 8-9, sim_225 9-10, sim_49 11-13,
  sim_68 6-10, sim_83 11-12. TWO distinct loss patterns:
  * EARLY DEFICIT (sim_199): we were BEHIND the ENTIRE game (3-4 by t10, 2-4
    by t50, 8-10 by t90). Opponent snowballed early via spawns/combat; never
    a lead to protect - can't be fixed by late-game logic.
  * LATE TRADE-DOWN (sim_68): AHEAD 9-7 at t70, then bled to 6-10 by t100.
    (endgame lock-in gates already target this but don't always catch it.)
### Experiment tested (NOT shipped - no robust gain)
- /tmp/v_test.py: TIGHTER EARLY GROUPING in step_toward - for turn<25 weight
  ally_pen into the sort key (c[0] + min(c[1],8)*0.34) so units advance as a
  tighter pack early to avoid the early piecemeal deaths (pattern 1).
  * v_test BLUE vs /tmp/aggro.py seeds 1-3: 3/3 (== baseline).
  * v_test RED vs aggro seeds 1-3: 2W 1L (== baseline). No regression vs aggro.
  * v_test(BLUE) vs baseline(RED) seeds 1-5: only 2W-3L -> NO clear gain on our
    real (BLUE) side, possibly slight regression. REJECTED (consistent with all
    prior teammates: grouping/passivity tweaks don't robustly help; side bias
    dominates self-play).
### Decision: KEPT robot.py UNCHANGED (proven balanced baseline, ~94% win).
Verified: parses OK; BLUE vs /tmp/aggro.py 3/3 (term seed-0 20-10); RED vs aggro
2W/1T seeds 1-3; crushes /tmp/marcher.py 24-2. Runtime ~2-3s/game, well under
60s. We are BLUE vs kalkin__maxad and win 235-5; no tested change beat baseline
on the BLUE side. Changing risks regression for marginal upside.
### Guidance for next teammate
- If opponent STAYS kalkin__maxad: submit robot.py as-is (~94% win as BLUE).
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
- Batch is SLOW (~2s/game); keep NSEEDS<=3-5 to stay under the 30s per-command
  wall-clock. Run: `(for s in 1 2 3; do printf '{"blue":"A.py","red":"B.py","seed":"%s"}\n' $s; done) | ./rumblebot run batch | grep winner`
- REMAINING LEVERS (both resist safe fixes): (1) EARLY snowball - keep units
  grouped turns 5-20 WITHOUT slowing aggression (my tighter-grouping test gave
  no clear Blue-side gain). (2) reduce OVERKILL (redirect a 3rd attacker on an
  enemy 2 can kill to a 2nd target for more net kills/turn) - still UNTRIED.
  ALWAYS test the BLUE side vs /tmp/aggro.py AND head-to-head vs baseline;
  reject anything that drops the BLUE win rate below baseline.

---
## Round 0 edit (opus-4-8, THIS session) - opponent = mjburgess__rule99 (INVALID BOT!)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 250-0** vs `mjburgess__rule99`.
  The opponent's bot is **INVALID** - `invalid_reason`: "robot.py does not
  contain the required robot function." Their `valid_submit` is FALSE, score 0.
  => This is an AUTOMATIC forfeit win for us; opponent contributes NOTHING.
### Verification this session
- Our robot.py parses OK (ast.parse) and has `def robot(state, unit)` at line 195.
- Ran robot.py BLUE vs /tmp/marcher.py (South marcher): WIN 25 units to 5,
  runtime 3.7s (well under 60s). Bot is healthy and plays correctly.
### Decision: KEPT robot.py UNCHANGED (proven baseline).
Opponent forfeits (invalid bot). Any change is pure downside risk for zero
upside - the ONLY requirement is that OUR bot stays valid and doesn't crash,
which it does. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS mjburgess__rule99 (invalid): just ENSURE robot.py stays
  valid (has `def robot(state, unit)`, parses, runs <60s) and submit. We win
  250-0 by default. Do NOT risk breaking a working bot for an opponent that
  contributes zero.
- If opponent FIXES their bot: it becomes a real match. Regenerate test bots
  (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than most real foes).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
  Our aggressive focus-fire + grouping + spawn-evac + endgame-lock-in bot has
  beaten every prior opponent 90-100%; it will very likely win here too.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = mjburgess__rule99 (INVALID BOT)
### Result recap
- Round 0: **WON 250-0** vs mjburgess__rule99 (INVALID - no robot function, forfeit).
- Round 1: **WON 250-0** vs mjburgess__rule99 (STILL INVALID, forfeit again).
- results.json both rounds: opponent valid_submit=FALSE, score 0.0. Automatic
  forfeit win for us; opponent contributes nothing.
### Verification this session
- robot.py parses OK (ast.parse); has `def robot(state, unit)` at line 195.
- robot.py BLUE vs /tmp/marcher.py (South marcher): WIN 24 units to 3,
  runtime 3.7s (well under 60s). Bot healthy, plays correctly.
### Decision: KEPT robot.py UNCHANGED (proven baseline).
Opponent forfeits (invalid bot). ONLY requirement is OUR bot stays valid and
runs <60s, which it does. Any change is pure downside risk for zero upside.
### Guidance for next teammate
- If opponent STAYS mjburgess__rule99 (invalid): ensure robot.py stays valid
  (has `def robot(state, unit)`, parses, runs <60s) and submit. Win 250-0 by
  default. Do NOT risk breaking a working bot for a zero-contribution opponent.
- If opponent FIXES their bot: regenerate /tmp/aggro.py, /tmp/marcher.py,
  /tmp/robot_baseline.py (git show HEAD:robot.py). Our aggressive focus-fire +
  grouping + spawn-evac + endgame-lock-in bot has beaten every prior opponent
  90-100%; it will very likely win here too.

---
## Round 0 edit (opus-4-8, THIS session) - opponent = ketza__bob (COMPETITIVE)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 195-35 w/ 20 TIES** vs
  `ketza__bob` (we were BLUE). ~78% win - a COMPETITIVE opponent (strongest in
  a while, 35 losses). Opponent uses "TAG TEAMS": it splits its army into
  MULTIPLE 3-unit squads, each focus-firing a DIFFERENT target in parallel
  (see /logs/rounds/0/sim_0.txt "Red tag teams" logs). This kills several of
  our units per turn = efficient trades.
### ROOT CAUSE of losses (traced /tmp/trace2.py):
- NOT spawn wipes (/tmp/spawndelta.py: only 22/315 spawn events had a Blue
  deficit, 0 big wipes). Losses are COMBAT TRADE-DOWNS: we stay ~even/slightly
  behind all game then lose the count race. Our baseline used a SINGLE global
  focus target -> ALL our units dogpile ONE enemy (overkill) while the opponent
  gang-kills several of ours in PARALLEL with its multi-squad tag teams.
### What I changed (robot.py) - MULTI-TARGET SQUAD ASSIGNMENT (tested, shipped)
- init_turn now builds `_target_by_unit` (unit_id -> enemy_id) via a greedy
  nearest-pair assignment: assign ~3 allies (cap = max(2, min(4, health+1)))
  to EACH enemy, so we kill MULTIPLE enemies per turn instead of dogpiling one.
  pick_target uses this per-unit assignment first (falls back to old single
  focus / nearest-weak). Kept single `_focus_target_id` for compat. All other
  logic (attack, retreat gates, grouping, spawn-evac, endgame lock-in) unchanged.
### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- NEW(Blue) vs baseline(Red) seeds 1-11: **7W 3L 1T** - clear edge on OUR real
  (BLUE) side. NEW(Red) vs baseline(Blue) seeds 1-5: 3W 1L 1T - also better
  as Red => genuine improvement, NOT just side bias.
- NEW BLUE vs /tmp/aggro.py seeds 1-6: **6/6 WINS** (term 11-8). RED vs aggro
  seeds 1-6: 3W 3T, NO losses (slightly softer than baseline's 5W/1T as Red,
  but we play BLUE vs ketza__bob so this is fine).
- NEW vs /tmp/marcher.py both sides: crush (22-2, 21-1). No regression vs passive.
- robot.py parses OK; runtime ~1.6-1.9s/match, well under 60s.
### Decision: SHIPPED multi-target squad assignment. Directly counters the
opponent's parallel tag-team gang-kills by killing multiple enemies per turn
instead of overkilling one. Better on BOTH orientations vs baseline & aggro.
### Guidance for next teammate
- If opponent STAYS ketza__bob: this should convert some trade-down losses/ties
  by matching their parallel gang-kill efficiency. VERIFY next round: unit-count
  trajectory (/tmp/trace.py sim_X.txt) should hold even/ahead better mid-late.
- Tuning knobs: SQUAD size (3) and the per-enemy cap in init_turn. If we're
  spreading TOO thin (getting picked off), raise cap; if still overkilling,
  lower it. TEST BLUE side vs /tmp/aggro.py AND head-to-head vs baseline; reject
  regressions.
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack.
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
  * /tmp/trace.py / /tmp/trace2.py / /tmp/spawndelta.py / /tmp/analyze.py: log tools.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = ketza__bob (COMPETITIVE, tag-teams)
### Result recap
- Round 0: **WON 195-35 w/ 20 TIES** vs ketza__bob (we were BLUE).
- Round 1: **WON 225-10 w/ 15 TIES** vs ketza__bob (we were RED). ~90%+ win.
  The multi-target squad-assignment change (round 0) is holding up well.
- Analyzed /logs/rounds/1 non-wins (10 losses + 15 ties). Traced trajectories:
  * Most losses are CLOSE endgame TRADE-DOWNS: we're tied/ahead through turn
    ~80-90, then bleed units in the last 10-20 turns (sim_202 R10->R7,
    sim_66 R11->R8, sim_225 even at t40 then Blue pulls ahead). Ties are
    mostly EVEN games (equal units at turn 100). Opponent's parallel tag-team
    gang-kills out-trade us in the endgame.
### Experiment tested (NOT shipped - REGRESSED on unit margin)
- /tmp/v1.py = endgame lock-in threshold lowered 90 -> 87 (retreat non-kill
  trades earlier when ahead/tied to hold the count).
  * v1 vs cluster/aggro: still wins, BUT term seed-0 unit MARGIN dropped:
    - vs cluster: baseline 17-11, v1 only 10-8.
    - vs aggro:   baseline 15-8,  v1 only 12-7.
  * The earlier endgame retreat makes us LESS aggressive in turns 87-90, so we
    kill fewer enemies and END with a SMALLER lead. Net negative. REJECTED.
  * (v1 head-to-head vs baseline was dominated by the usual RED-side bias:
    inconclusive.)
### Decision: KEPT robot.py UNCHANGED (proven balanced baseline, ~90% win).
Verified: parses OK; `def robot(state: State, unit: Obj)` at line 225; BLUE vs
/tmp/cluster.py wins 16-6; RED vs /tmp/aggro.py wins 13-9; BLUE vs aggro 5/5,
RED vs cluster 5/5. Runtime ~2s/game, well under 60s. No tested change beat the
baseline's unit margin; changing risks regression for marginal upside.
### Guidance for next teammate
- If opponent STAYS ketza__bob: submit robot.py as-is (~90% win both sides).
- The remaining lever is the ENDGAME TRADE-DOWN (tied/ahead ~t85, lose by t100
  as the opponent's tag-teams gang-kill in parallel). LOWERING the endgame
  retreat threshold REGRESSES (kills fewer, smaller margin - tested above).
  Instead try MATCHING their kill EFFICIENCY: reduce OVERKILL (don't stack 3
  attackers where 2 finish an enemy; redirect the 3rd to a 2nd target for more
  net kills/turn) - STILL UNTRIED. Or tune the squad cap in init_turn
  (_target_by_unit greedy assignment) to spread onto more enemies.
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/cluster.py: attack-adjacent-weakest + focus-weakest move (competitive foe).
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
  * Batch (SLOW ~2s/game, keep N<=5-8 for the 30s wall-clock):
    `(for s in 1 2 3 4 5; do printf '{"blue":"A.py","red":"B.py","seed":"%s"}\n' $s; done) | ./rumblebot run batch | grep -oE '"winner":"[^"]*"'`
  * ALWAYS check unit MARGIN (term --results-only "Units B R"), not just W/L -
    a change can win but shrink the margin -> net worse across 250 games.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = suddenlyseals__control-center
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 249-0 w/ 1 TIE** vs
  `suddenlyseals__control-center` (we were RED). ~99.6% win. Verified all 250
  sims: Red(us) wins=249, losses=0, ties=1 (the 1 tie ended equal units).
  Opponent COMPETITIVE-ish but clearly far weaker; we win nearly every game
  (sim_0: 15 units to 6, HP 53-26).
### Verification this session
- robot.py parses OK (ast.parse); `def robot(state: State, unit: Obj)` at line 225.
- robot.py BLUE vs /tmp/marcher.py (South marcher): WIN 21 units to 0
  (HP 105-0), runtime 3.4s (well under 60s). Bot healthy, plays correctly.
### Decision: KEPT robot.py UNCHANGED (proven baseline, 249-0-1).
Opponent far weaker; current aggressive focus-fire + multi-target squad +
grouping + spawn-evac + endgame-lock-in bot wins ~99.6% as RED. Any change is
pure downside risk (regression) for essentially zero upside. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS suddenlyseals__control-center: submit robot.py as-is (~99.6%
  win as RED). Do NOT risk breaking a proven bot.
- If opponent gets stronger: regenerate test bots (Action/Direction/Coords/State
  globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than most real foes).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
- The 1 tie was an EVEN game (equal units at turn 100; HP is NOT a tiebreaker).
  Untried lever to shave ties: reduce OVERKILL (redirect a 3rd attacker on an
  enemy 2 can kill to a 2nd target for more net kills/turn). ALWAYS test the
  RED side vs /tmp/aggro.py AND head-to-head vs baseline; reject regressions.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = suddenlyseals__control-center
### Result recap
- Round 0: **WON 249-0 w/ 1 TIE** vs suddenlyseals__control-center (we were RED).
- Round 1: **WON 249-0 w/ 1 TIE** vs suddenlyseals__control-center (we were RED).
  ~99.6% win both rounds. Opponent competitive-ish but far weaker; we win nearly
  every game.
### Verification this session
- robot.py parses OK (ast.parse); `def robot(state: State, unit: Obj)` at line 225.
- robot.py BLUE vs /tmp/marcher.py (South marcher): WIN 25 units to 1
  (HP 125-5), runtime 3.7s (well under 60s). Bot healthy, plays correctly.
### Decision: KEPT robot.py UNCHANGED (proven baseline, 249-0-1 both rounds).
Opponent far weaker; current aggressive focus-fire + multi-target squad +
grouping + spawn-evac + endgame-lock-in bot wins ~99.6% as RED. Any change is
pure downside risk for essentially zero upside. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS suddenlyseals__control-center: submit robot.py as-is (~99.6%
  win as RED). Do NOT risk breaking a proven bot.
- If opponent gets stronger: regenerate test bots (/tmp/aggro.py nearest-chase+
  attack, /tmp/marcher.py South marcher, /tmp/robot_baseline.py = git show
  HEAD:robot.py). Untried lever to shave ties: reduce OVERKILL. Test RED side.

---
## Round 1 edit (opus-4-8, THIS session) - opponent = aaoutkine__school-bot (COMPETITIVE)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 250-0** vs `aaoutkine__school-bot`
  (we were BLUE). Analyzed all 250 sims: Blue(us) wins=250, losses=0, ties=0.
  Opponent is COMPETITIVE (games are fairly close: median unit margin +8, but
  min margin +1, and 10 games within +2). We still win EVERY game (e.g. sim_0:
  11 units to 9; sim_150: 12-10; sim_249: 13-7). Opponent trades damage and
  keeps a decent unit count but is consistently out-fought by our bot.
### Verification this session
- robot.py parses OK (ast.parse); `def robot(state: State, unit: Obj)` at line 225.
- robot.py BLUE vs /tmp/marcher.py (South marcher): WIN 18 units to 3
  (HP 90-12), runtime 3.5s (well under 60s).
- robot.py vs STRONG /tmp/aggro.py (nearest-chase+attack, STRONGER than the real
  opponent): WIN as BLUE (11-9) AND WIN as RED (11-10). Robust on both sides.
### Decision: KEPT robot.py UNCHANGED (proven baseline, 250-0).
Opponent competitive but we win 100% of games; current aggressive focus-fire +
multi-target squad + grouping + spawn-evac + endgame-lock-in bot is optimal
here. Any change is pure downside risk (regression) for zero upside vs a perfect
record. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS aaoutkine__school-bot: submit robot.py as-is (250-0, min
  margin +1). Do NOT risk breaking a proven bot for zero upside.
- If margins tighten or opponent strengthens: the untried lever is reduce
  OVERKILL (redirect a 3rd attacker on an enemy 2 can kill to a 2nd target for
  more net kills/turn -> widen margins). ALWAYS test BOTH orientations vs
  /tmp/aggro.py AND head-to-head vs /tmp/robot_baseline.py; reject regressions.
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = aaoutkine__school-bot (COMPETITIVE)
### Result recap
- Round 0: **WON 250-0** vs aaoutkine__school-bot (we were BLUE). All 250 sims
  Blue wins, avg unit margin +8.0 (min +1, max +15, 10 games within +2).
- Round 1: **WON 250-0** vs aaoutkine__school-bot (we were RED). All 250 sims
  Red wins, avg unit margin +8.0 (min +1, max +18).
- Opponent COMPETITIVE (some close games, min margin +1) but we win EVERY game
  on BOTH orientations. Perfect record so far.
### Verification this session
- robot.py parses OK (ast.parse); `def robot(state: State, unit: Obj)` at line 225.
- robot.py BLUE vs /tmp/marcher.py (South marcher): WIN 22 units to 3
  (HP 110-10), runtime 3.75s (well under 60s). Bot healthy, plays correctly.
### Decision: KEPT robot.py UNCHANGED (proven baseline, 250-0 both rounds).
Opponent competitive but we win 100% of games on both sides. Current aggressive
focus-fire + multi-target squad + grouping + spawn-evac + endgame-lock-in bot is
optimal here. Any change is pure downside risk for zero upside vs a perfect
record. Submitting as-is.
### Guidance for next teammate
- If opponent STAYS aaoutkine__school-bot: submit robot.py as-is (250-0 both
  sides, min margin +1). Do NOT risk breaking a proven bot for zero upside.
- If margins tighten: untried lever is reduce OVERKILL (redirect a 3rd attacker
  on an enemy 2 can kill to a 2nd target for more net kills/turn). ALWAYS test
  BOTH orientations vs /tmp/aggro.py AND head-to-head vs /tmp/robot_baseline.py
  (git show HEAD:robot.py); reject regressions.

---
## Round 0 edit (opus-4-8, THIS session) - opponent = thesmilingturtl__naivefaa (COMPETITIVE)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 214-12 w/ 24 TIES** vs
  `thesmilingturtl__naivefaa` (we were BLUE). ~86% win. A COMPETITIVE opponent
  (12 losses, 24 ties). In ALL 12 losses we are behind on BOTH units AND HP
  (e.g. 6-8, 6-9, 5-8; opponent HP ~30-38 vs ours ~11-23).
### ROOT CAUSE (traced sim_9): opponent OUT-TRADES us on HP.
  Turn-by-turn (sim_9): opponent maintains consistently HIGHER HP the whole game
  (mid-game HP 50 vs our 38, units R8 vs B7 by turn 31). They preserve HP while
  trading, then win the count race in the last turns as we bleed down.
### Experiment tested (NOT shipped - REGRESSED margin, REVERTED)
- OVERKILL REDIRECTION: when the chosen adjacent enemy is BOXED and has MORE
  attackers than needed to kill it, redirect the SURPLUS (higher-id) adjacent
  allies to a DIFFERENT adjacent enemy for more net kills/turn. Deterministic
  keeper set = `health` lowest-id adjacent allies stay; rest redirect.
  * Parsed OK, no crashes. NEW(Blue) vs aggro 5/5 (== baseline). NEW vs
    baseline head-to-head: dominated by strong RED-side bias (mirror
    baseline-vs-baseline: Red wins seeds 1,2,3), inconclusive; on seed 4 NEW
    won BOTH orientations (slight real edge).
  * BUT vs /tmp/cluster.py (competitive clustered foe, mimics this opponent):
    NEW term (seed 0) won only 12-9 (margin +3) vs BASELINE's 15-8 (margin +7).
    REGRESSION in unit margin. Redirecting surplus attackers to a 2nd enemy
    gives that enemy a partial hit but it SURVIVES and returns fire, costing us
    HP/units. Against a competitive/clustered foe that out-trades us, this HURTS.
    W/L unchanged (both win 4/4 vs cluster) but the SMALLER margin = closer
    games = more risk of tipping to losses over 250 games. REJECTED & REVERTED.
### KEY TAKEAWAY (consistent with ALL prior teammates)
- The "reduce OVERKILL" lever that every prior note listed as untried DOES NOT
  robustly help - it thins our attackers, letting partially-hit enemies survive
  and out-trade us. It REGRESSES the unit margin vs a competitive foe. The
  baseline's dogpile-a-boxed-enemy behavior actually SECURES kills cleanly.
  Self-play remains dominated by a strong RED-side map bias.
### Decision: KEPT robot.py UNCHANGED (proven balanced baseline, ~86% win).
Verified: parses OK; `def robot(state: State, unit: Obj)` at line 225; BLUE vs
/tmp/aggro.py 5/5 batch + term win 15-9; BLUE vs /tmp/cluster.py wins; crushes
/tmp/marcher.py 22-3. Runtime ~2s/game, well under 60s. We are BLUE vs this
opponent and win 214-12; no tested change beat baseline on the BLUE side.
### Guidance for next teammate
- If opponent STAYS thesmilingturtl__naivefaa: submit robot.py as-is (~86% win
  as BLUE). Do NOT retry the overkill-redirection lever (tested & regressed).
- The ONLY realistic lever vs this HP-out-trading foe is to LOSE FEWER of our
  own units in mid-late game WITHOUT going passive (prior teammates: passive/
  retreat tweaks regress). Untried & harder: predict enemy flee tile and only
  attack when the hit will LAND (movement resolves before attacks) so we don't
  whiff and eat return fire. Risky - test BLUE side vs /tmp/aggro.py AND
  /tmp/cluster.py MARGIN (not just W/L) and head-to-head vs baseline.
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/cluster.py: attack-adjacent-weakest + focus-weakest-nearest move
    (competitive clustered foe, best proxy for this opponent).
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
  * Batch (SLOW ~2s/game, keep N<=4-5 for the 30s wall-clock):
    `(for s in 1 2 3 4; do printf '{"blue":"A.py","red":"B.py","seed":"%s"}\n' $s; done) | ./rumblebot run batch | grep -oE '"winner":"[^"]*"'`
  * ALWAYS check unit MARGIN (term --results-only "Units B R"), not just W/L.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = thesmilingturtl__naivefaa (COMPETITIVE)
### Result recap
- Round 0: **WON 214-12 w/ 24 TIES** vs thesmilingturtl__naivefaa (we were BLUE).
- Round 1: **WON 219-13 w/ 18 TIES** vs thesmilingturtl__naivefaa (we were BLUE).
  ~87% win. Competitive foe that out-trades us on HP and preserves units late.
### Loss analysis (/logs/rounds/1, 13 losses): SPLIT ~evenly:
  * 6 = EARLY snowball (behind by turn 40, never recover; e.g. sim_234).
  * 7 = LATE trade-down (ahead/even at turn 40-90 then bleed the last 10-20
    turns; e.g. sim_106: AHEAD 12-10 at t~96 then dropped to a 10-10 TIE by
    t100 as opponent spawns replaced their losses but ours died).
### What I changed (robot.py) - ENDGAME HOLD (advance-guard, tested, shipped)
- The existing endgame lock-in only retreats units ALREADY ADJACENT to an enemy.
  Units that DIE while ADVANCING into contact in the last turns weren't caught.
- Added an ENDGAME HOLD in the move path (right before step_toward): if
  `state.turn >= 90` AND we are STRICTLY AHEAD in unit count AND the unit is
  exactly dist 2 from the nearest enemy (would step into contact next), and the
  fight ahead is NOT locally favorable (`foes_near >= mine_near`, radius 2), it
  REGROUPS toward allies instead of advancing into a fresh trade. Preserves the
  count lead (win = most units at turn 100; HP NOT a tiebreaker). Tightly gated
  (last 10 turns, only when ahead, only when not locally favorable) so it does
  NOT go passive - it still presses favorable fights.
### Testing
- vs /tmp/cluster.py (competitive clustered proxy): WIN 20-2 / 16-0 (baseline
  ~23-1; the small margin diff is noise - these weak proxies die before t90 so
  the change rarely even fires). vs /tmp/aggro.py: WIN 16-1 (term) + Blue 2/2
  batch (seeds 7,8). vs /tmp/marcher.py: WIN 23-0. No regression, all decisive.
- Head-to-head vs baseline: dominated by side bias + change only fires t90+ so
  inconclusive in self-play (batch is SLOW ~2s/game, timed out at 2-3 seeds).
- robot.py parses OK; `def robot(state: State, unit: Obj)` line 225; runtime ~3s.
### Decision: SHIPPED the endgame-hold advance-guard (low-risk, targeted at the
7 late trade-down losses). It complements the existing endgame retreat (which
only handled already-adjacent units). No regressions found on any proxy.
### Guidance for next teammate
- If opponent STAYS thesmilingturtl__naivefaa: robot.py wins ~87%; this edit
  should shave some late trade-down ties/losses. VERIFY next round: unit
  trajectory turns 90-100 (/tmp/trace.py sim_X.txt) - we should HOLD our lead
  instead of trading down to a tie (the sim_106 pattern).
- The OTHER half of losses is EARLY snowball (behind by turn 40). Prior
  teammates found tighter early grouping gives NO robust Blue-side gain and
  "reduce OVERKILL" REGRESSES the margin (partially-hit enemies survive & out-
  trade us). Those are documented dead-ends - do not retry blindly.
- If the endgame-hold HURTS (check next round's late-game trajectory - if we now
  fall BEHIND late because we held too passively while their spawns advanced),
  REVERT it (git diff shows the single added block before step_toward) or tighten
  to `foes_near >= mine_near + 1`.
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py, /tmp/marcher.py, /tmp/cluster.py, /tmp/robot_baseline.py
    (=git show HEAD:robot.py). Batch: keep N<=2-3 (SLOW, 30s wall-clock cap).
  * ALWAYS check unit MARGIN (term --results-only "Units B R"), not just W/L.

---
## Round 0 edit (opus-4-8, THIS session) - opponent = mario31313__alpha_13 (COMPETITIVE)
### Result recap
- Round 0 (/logs/rounds/0/results.json): **WON 215-14 w/ 21 TIES** vs
  `mario31313__alpha_13` (we were BLUE). ~86% win. COMPETITIVE opponent that
  OUT-TRADES us on HP (in nearly all losses/ties the opponent ends with HIGHER
  HP; they preserve HP/units while trading).
### ROOT CAUSE (traced trajectories, sim_0 & sim_113):
  We build a LEAD then THROW IT AWAY in the last ~10 turns.
  * sim_0 (TIE 8-8): AHEAD B12 R9 at turn ~90 -> traded down to 8-8 by turn 100.
  * sim_113 (LOSS 11-12): AHEAD B15 R13 at turn ~90 -> dropped to 11-12.
  Win = MOST units at turn 100 (HP NOT a tiebreaker - verified lib.rs). We were
  AHEAD on units late but traded 1-for-1 into ties/losses.
### What I changed (robot.py) - EARLIER STRICTLY-AHEAD ENDGAME LOCK-IN (shipped)
- The endgame lock-in (retreat non-kill non-boxed trades to preserve the count)
  fired only at turn>=90. Traced losses show we start bleeding the lead ~turn 86.
  Split the gate: STRICTLY-AHEAD branch now fires at **turn>=86** (protects the
  lead sooner); TIED branch stays at turn>=90 (only when not locally favorable).
  Same change applied to the ENDGAME HOLD advance-guard (move path, dist==2).
  NEVER fires when behind (we must trade to catch up). One-block change; all
  other logic unchanged.
### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- NOTE: term matches are NON-deterministic (there is randomness) - run 4-5x and
  count W/L, don't trust a single run.
- new BLUE vs /tmp/aggro.py x4: **3W 1T** (baseline 2W 2T). Wins MORE.
- new BLUE vs /tmp/cluster.py x4: **3W 1T** (baseline 2W 2T). Wins MORE.
- new(BLUE) vs baseline(RED) x5: 2W 1L 2T (favorable on our real BLUE side).
- new vs /tmp/marcher.py both sides: crush (19-3, 22-1). No regression vs passive.
- CAVEAT: RED-vs-cluster single-run margin dipped a bit (weak proxy noise); we
  are always BLUE vs mario31313 so the BLUE-side win-rate gain is what matters.
- robot.py parses OK; runtime ~2-3s/match, well under 60s.
### Decision: SHIPPED the earlier strictly-ahead endgame lock-in. Targets the
EXACT documented loss pattern (throw away a lead at turn ~86-90). Improves the
BLUE-side win rate vs both proxies AND head-to-head vs baseline; no regression.
### Guidance for next teammate
- If opponent STAYS mario31313__alpha_13: robot.py wins ~86%+; this edit should
  shave some of the late trade-down ties/losses. VERIFY next round: unit
  trajectory turns 86-100 (/tmp/trace.py) - we should HOLD the lead not trade down.
- If we now fall BEHIND late (held too passively), REVERT: git diff shows the
  single block (endgame turn 86 -> 90). Or tighten to `foes_near >= mine_near`.
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/cluster.py: attack-adjacent-weakest + focus-weakest-nearest move.
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
  * ALWAYS run term 4-5x (non-deterministic) & count W/L; batch is SLOW (~2s/game,
    timed out at 4 seeds under the 30s wall-clock).
- The other loss half is opponent OUT-TRADING on HP (they preserve HP while
  trading). Prior teammates found reduce-OVERKILL and tighter-grouping REGRESS.
  Documented dead-ends - do not retry blindly.

---
## Round 2 edit (opus-4-8, THIS session) - opponent = mario31313__alpha_13 (COMPETITIVE)
### Result recap
- Round 0: **WON 215-14 w/ 21 TIES** vs mario31313__alpha_13 (BLUE).
- Round 1: **WON 210-12 w/ 28 TIES** vs mario31313__alpha_13 (BLUE). ~84% win.
- Analyzed /logs/rounds/1 losses (12, all CLOSE 1-3 units). Traced trajectories:
  * DOMINANT loss pattern = we hold a LEAD at turn ~80-88, then LOSE it at the
    turn-91 SPAWN + final turns. sim_220: B11 R7 at t80, B10 R6 at t88, then
    at the t90/91 SPAWN it flips to B8 R9 (we LOST 2 units AND they gained 3!)
    and ends B6 R7. We threw away a 4-unit lead in the last ~12 turns - our
    units were near our spawn zone clustering (via retreat/regroup toward
    allies) and got WIPED/blocked at the spawn transition while trading down.
### What I changed (robot.py) - ENDGAME DISPERSE (run out the clock; shipped)
- Added `disperse(state, unit)`: unlike retreat()/regroup (which pull TOWARD
  allies -> cluster near spawn -> get wiped), disperse SPREADS units to safe
  tiles: maximize distance from nearest enemy, avoid spawn tiles pre-spawn, and
  MAXIMIZE min-distance to allies (anti-cluster, harder to gang-kill).
- Gated VERY TIGHTLY: fires only when `state.turn >= 94 AND my_units >=
  enemy_units + 3` (the final ~6 turns = the spawn-wipe window after the t91
  spawn, and only with a comfortable 3+ lead). Used in BOTH the adjacent-retreat
  path and the move path (replaces advancing into fights). When it fires, units
  scatter to safe corners so a 3+ lead can't be traded/wiped away by turn 100.
- NOTE: I first tried turn>=82/lead>=2 and turn>=92/lead>=2 - BOTH regressed
  (too passive, gave up kills; RED-vs-aggro dropped from 3W to losses/ties).
  turn>=94/lead>=3 has NO regression and only affects the exact loss window.
### Testing (baseline = /tmp/robot_baseline.py = git HEAD robot.py pre-edit)
- term is NON-deterministic; ran 3-4x each, counted W/L (units, first=Blue).
- NEW BLUE vs /tmp/aggro.py: 3/3 WINS. NEW RED vs aggro: 3W 1L (== baseline
  noise; baseline RED vs aggro 3/3). NO regression.
- NEW RED vs /tmp/cluster.py (competitive proxy): 3/3 WINS. NEW BLUE vs cluster:
  3/3 WINS. NEW vs /tmp/marcher.py: crush 20-3. No regression vs passive.
- Head-to-head vs baseline: dominated by side bias (inconclusive, as always).
- robot.py parses OK; runtime ~2s/match, well under 60s.
### Decision: SHIPPED endgame disperse (turn>=94, lead>=3). Directly targets the
documented spawn-wipe / late-lead trade-down loss pattern (sim_220) with a very
tight gate so it does NOT go passive or give up mid-late kills. No regressions.
### Guidance for next teammate
- If opponent STAYS mario31313__alpha_13: robot.py wins ~84%+; this edit should
  convert some final-turn lead-loss ties/losses. VERIFY next round: unit
  trajectory turns 90-100 (/tmp/trace.py sim_X.txt) - we should HOLD the lead
  through the t91 spawn instead of flipping (the sim_220 pattern).
- If it HURTS (we now fall behind late because we dispersed while their spawns
  advanced), REVERT: git diff shows the disperse() fn + 2 call sites; or raise
  the gate to turn>=96. Do NOT lower turn/lead thresholds - tested, regresses.
- Other loss half = opponent OUT-TRADES on HP / early snowball. Prior teammates
  found reduce-OVERKILL and tighter-grouping REGRESS - documented dead-ends.
- Regenerate test bots (Action/Direction/Coords/State globals, no logic import):
  * /tmp/aggro.py: nearest-enemy chase+attack (STRONGER than real opponent).
  * /tmp/marcher.py: `def robot(state,unit): return Action.move(Direction.South)`
  * /tmp/cluster.py: attack-adjacent-weakest + focus-weakest-nearest move.
  * /tmp/robot_baseline.py: `git show HEAD:robot.py`.
  * ALWAYS run term 3-4x (non-deterministic) & check unit MARGIN, not just W/L.
