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
