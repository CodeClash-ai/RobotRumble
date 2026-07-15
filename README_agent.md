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
