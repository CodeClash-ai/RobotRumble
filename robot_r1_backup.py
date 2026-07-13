from enum import Enum, auto
from typing import *

# =========================================================================
# Strategy notes (see README_agent.md for more context):
#
# - Each unit has 5 HP, deals 1 damage per attack. Killing a unit therefore
#   takes 5 successful attacks. Numeric superiority in a local fight is very
#   valuable: N attackers vs 1 defender kill ~N times faster than 1v1 while
#   taking much less retaliation damage per kill.
# - New units spawn periodically (every ~10 turns) at team spawn points, so
#   games tend to snowball: keeping units alive and grouped compounds our
#   advantage turn over turn.
# - This bot: attacks the weakest adjacent enemy (finishes kills fast),
#   avoids attacking into heavily-outnumbered local fights (retreats toward
#   allies instead), and otherwise advances as a group toward the enemy
#   concentration that our team can reach fastest (similar to the original
#   quadrant-targeting idea, but fixed so it can't get stuck with no target).
# =========================================================================

RADIUS = 6          # radius (in board distance) used to judge local fights
RETREAT_RATIO = 1.5  # if enemy "power" > allies "power" * this, retreat


def team_centroid(units: List[Obj]) -> Optional[Coords]:
    if not units:
        return None
    xs = sum(u.coords.x for u in units)
    ys = sum(u.coords.y for u in units)
    n = len(units)
    return Coords(round(xs / n), round(ys / n))


def best_move_towards(state: State, unit: Obj, target: Coords, avoid: Optional[Coords] = None) -> Optional[Action]:
    """Try to move one step towards `target`, avoiding occupied tiles and
    (if possible) not stepping back onto `avoid` (previous coords), to
    reduce oscillation. Falls back to rotating around obstacles."""
    if unit.coords == target:
        return None
    direction = unit.coords.direction_to(target)
    candidates = [direction, direction.rotate_cw, direction.rotate_ccw]
    # First pass: prefer moves that don't revisit our last coords.
    for d in candidates:
        dest = unit.coords + d
        if state.obj_by_coords(dest):
            continue
        if avoid is not None and dest == avoid:
            continue
        return Action.move(d)
    # Second pass: allow revisiting last coords if that's the only option.
    for d in candidates:
        dest = unit.coords + d
        if not state.obj_by_coords(dest):
            return Action.move(d)
    return None


robot_state: Dict[str, dict] = {}


def init_turn(state: State) -> None:
    # Nothing global needed right now beyond per-unit history, which is
    # tracked lazily in `robot_state`. Kept as a hook for future macro
    # strategy (e.g. team-wide focus-fire target selection).
    pass


def robot(state: State, unit: Obj) -> Optional[Action]:
    st = robot_state.setdefault(unit.id, {})
    past_coords: Optional[Coords] = st.get("past_coords")
    st["past_coords"] = unit.coords

    allies = [u for u in state.objs_by_team(state.our_team) if u.id != unit.id]
    enemies = state.objs_by_team(state.other_team)

    if not enemies:
        return None

    # --- 1) If any enemy is adjacent, always attack. Prefer finishing off
    #        the weakest one to reduce enemy unit count as fast as possible.
    adjacent_enemies = [e for e in enemies if unit.coords.distance_to(e.coords) == 1]
    if adjacent_enemies:
        target = min(adjacent_enemies, key=lambda e: (e.health, e.coords.distance_to(unit.coords)))
        return Action.attack(unit.coords.direction_to(target.coords))

    # --- 2) Judge the local fight: allies/enemies within RADIUS.
    near_allies = [a for a in allies if unit.coords.distance_to(a.coords) <= RADIUS] + [unit]
    near_enemies = [e for e in enemies if unit.coords.distance_to(e.coords) <= RADIUS]

    nearest_enemy = min(enemies, key=lambda e: unit.coords.distance_to(e.coords))

    if near_enemies:
        ally_power = sum(a.health for a in near_allies)
        enemy_power = sum(e.health for e in near_enemies)

        if enemy_power > ally_power * RETREAT_RATIO:
            # Retreat toward our own local group (regroup for a better fight)
            other_allies = [a for a in near_allies if a.id != unit.id]
            centroid = team_centroid(other_allies) if other_allies else None
            if centroid and centroid != unit.coords:
                action = best_move_towards(state, unit, centroid, past_coords)
                if action:
                    return action
            # Fall back: step directly away from the nearest enemy.
            away = unit.coords.direction_to(nearest_enemy.coords).opposite
            dest = unit.coords + away
            if not state.obj_by_coords(dest):
                return Action.move(away)
            return None

    # --- 3) Otherwise, advance as a group towards the nearest enemy.
    return best_move_towards(state, unit, nearest_enemy.coords, past_coords)
