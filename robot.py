"""
sonnet-5's RobotRumble bot.

Strategy overview:
- Each unit independently picks the best enemy target: prioritize enemies
  that are already adjacent (finish them off), then the weakest reachable
  enemy weighted by distance, encouraging focus fire without needing complex
  coordination (which was buggy/fragile in the previous version and caused
  our bot to *never engage* certain passive opponents - see README_agent.md).
- Movement uses a greedy direction choice with fallback candidates (ordered
  by resulting distance-to-target) so that units don't get stuck oscillating
  or permanently frozen against walls/other units, which was the critical bug
  in the previous quadrant-based approach (it produced 100% ties against any
  non-aggressive/stationary opponent - confirmed via /logs/rounds/0).
- A small amount of memory (`robot_state`) is used per-unit to avoid
  immediately reversing a move (anti-oscillation) but we always allow a
  fallback to *any* open cell (even a revisit) rather than freezing forever.
"""

from typing import *


robot_state: Dict[str, dict] = {}


ALL_DIRECTIONS = [Direction.North, Direction.South, Direction.East, Direction.West]


def score_enemy(unit: Obj, enemy: Obj) -> Tuple[float, float]:
    """Lower is better. Prioritize low health (easy kill) then close distance."""
    dist = unit.coords.distance_to(enemy.coords)
    return (dist, enemy.health)


def robot(state: State, unit: Obj) -> Optional[Action]:
    mem = robot_state.setdefault(unit.id, {})
    past_coords: Optional[Coords] = mem.get("past_coords")
    stuck_turns: int = mem.get("stuck_turns", 0)

    enemies = state.objs_by_team(state.other_team)
    if not enemies:
        mem["past_coords"] = unit.coords
        return None

    # Prefer an enemy we're already adjacent to (finish the kill / defend),
    # otherwise go for the "best" target by (health, distance).
    adjacent_enemies = [e for e in enemies if unit.coords.distance_to(e.coords) == 1]
    if adjacent_enemies:
        target = min(adjacent_enemies, key=lambda e: e.health)
    else:
        target = min(enemies, key=lambda e: score_enemy(unit, e))

    debug.locate(target)

    dist_to_target = unit.coords.distance_to(target.coords)

    if dist_to_target <= 1:
        mem["past_coords"] = unit.coords
        mem["stuck_turns"] = 0
        direction = unit.coords.direction_to(target.coords)
        return Action.attack(direction)

    direction = unit.coords.direction_to(target.coords)

    # Build a list of candidate directions, ordered by preference:
    # 1) the direct direction toward the target
    # 2) its two neighboring rotations (whichever gets us closer first)
    # 3) the opposite direction (last resort, to escape being boxed in)
    candidates = [direction]
    rotations = [direction.rotate_cw, direction.rotate_ccw]
    rotations.sort(key=lambda d: (unit.coords + d).distance_to(target.coords))
    candidates.extend(rotations)
    candidates.append(direction.opposite)

    # De-duplicate while preserving order.
    seen = set()
    ordered_candidates = []
    for d in candidates:
        if d not in seen:
            seen.add(d)
            ordered_candidates.append(d)

    def is_open(coords: Coords) -> bool:
        return state.obj_by_coords(coords) is None

    # First pass: avoid immediately reversing our last move, unless we've
    # been stuck for a while (then we allow it, to break deadlocks/loops).
    allow_revisit = stuck_turns >= 2

    best_move = None
    for d in ordered_candidates:
        dest = unit.coords + d
        if not is_open(dest):
            continue
        if not allow_revisit and past_coords is not None and dest == past_coords:
            continue
        best_move = d
        break

    # Second pass: if nothing worked (all blocked, or only the revisit option
    # was open), just allow the revisit / any open cell so we never freeze.
    if best_move is None:
        for d in ordered_candidates:
            dest = unit.coords + d
            if is_open(dest):
                best_move = d
                break

    if best_move is None:
        # completely boxed in; pass this turn
        mem["past_coords"] = unit.coords
        mem["stuck_turns"] = stuck_turns + 1
        return None

    mem["past_coords"] = unit.coords
    mem["stuck_turns"] = 0
    return Action.move(best_move)
