from enum import Enum, auto
from typing import *

# =========================================================================
# Strategy notes (see README_agent.md for more context, including full
# history of prior rounds' results/tuning):
#
# - Each unit has 5 HP, deals 1 damage per attack. Killing a unit therefore
#   takes 5 successful attacks. Numeric superiority in a local fight is very
#   valuable: N attackers vs 1 defender kill ~N times faster than 1v1 while
#   taking much less retaliation damage per kill.
# - New units spawn periodically (every ~10 turns) at team spawn points, so
#   games tend to snowball: keeping units alive and grouped compounds our
#   advantage turn over turn.
# - This bot (v2, round 2):
#   1. Attacks the weakest adjacent enemy (finishes kills fast).
#   2. Avoids attacking into heavily-outnumbered local fights (retreats
#      toward allies instead).
#   3. When advancing, instead of just beelining for the *nearest* enemy,
#      units bias towards a shared "focus target" -- the enemy that is
#      already weakest / most surrounded by our own units nearby. This
#      makes the group naturally converge and gang up on one victim at a
#      time (mirrors what the toughest builtin opponent, black-magic.js,
#      does to *us*: it always has each enemy attack whichever adjacent
#      ally has the lowest health, and rewards "surround" in its scoring).
#      Concentrating fire this way kills enemies faster and reduces the
#      total incoming damage we take over the course of a fight.
#   4. Movement avoids obstacles by trying the direct direction, then
#      rotate_cw/rotate_ccw, and tries not to immediately backtrack to the
#      previous tile (to reduce oscillation), falling back to allowing
#      backtrack if that's the only legal move.
# =========================================================================

RADIUS = 6            # radius (in board distance) used to judge local fights
RETREAT_RATIO = 1.5    # if enemy "power" > allies "power" * this, retreat
FOCUS_SCAN_RADIUS = 12  # how far to look for a shared focus-fire target
FOCUS_ALLY_WEIGHT = 1.2  # bonus (per nearby ally) for picking a target
FOCUS_HEALTH_WEIGHT = 0.6  # penalty per HP of the target (prefer weak ones)


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

# Per-turn cache (recomputed every call to init_turn, shared by all units
# this turn via the `robot()` calls that follow it).
_turn_cache: Dict[str, Any] = {}


def init_turn(state: State) -> None:
    """Compute a single shared "focus fire" target for the whole team this
    turn: the enemy unit that is cheapest to pile onto (weighted mix of low
    health + already having many of our units nearby). All of our units
    that aren't otherwise busy (adjacent enemy / local retreat) will bias
    their advance towards this unit, causing the team to converge and gang
    up rather than each unit just beelining for whichever enemy happens to
    be nearest to *it* individually."""
    _turn_cache.clear()

    allies = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)
    _turn_cache["allies"] = allies
    _turn_cache["enemies"] = enemies

    if not enemies:
        _turn_cache["focus_target"] = None
        return

    best_enemy = None
    best_score = None
    for e in enemies:
        nearby_allies = sum(
            1 for a in allies if a.coords.distance_to(e.coords) <= FOCUS_SCAN_RADIUS
        )
        # Lower score is better: prefer weak enemies with lots of our units
        # already converging on them.
        s = FOCUS_HEALTH_WEIGHT * e.health - FOCUS_ALLY_WEIGHT * nearby_allies
        if best_score is None or s < best_score:
            best_score = s
            best_enemy = e

    _turn_cache["focus_target"] = best_enemy


def robot(state: State, unit: Obj) -> Optional[Action]:
    st = robot_state.setdefault(unit.id, {})
    past_coords: Optional[Coords] = st.get("past_coords")
    st["past_coords"] = unit.coords

    allies = [u for u in _turn_cache.get("allies", []) if u.id != unit.id]
    enemies = _turn_cache.get("enemies", [])

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

    # --- 3) Otherwise, advance. Bias towards the shared team focus-fire
    #        target when it's not drastically further away than the
    #        nearest enemy (avoid making units travel absurd distances
    #        across the map just to pile on -- only converge when it's
    #        reasonably cheap to do so).
    focus_target = _turn_cache.get("focus_target")
    move_target = nearest_enemy
    if focus_target is not None and focus_target.id != nearest_enemy.id:
        d_nearest = unit.coords.distance_to(nearest_enemy.coords)
        d_focus = unit.coords.distance_to(focus_target.coords)
        if d_focus <= d_nearest + 3:
            move_target = focus_target

    return best_move_towards(state, unit, move_target.coords, past_coords)
