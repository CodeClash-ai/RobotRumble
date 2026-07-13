from enum import Enum, auto
from typing import *

RADIUS = 6
RETREAT_RATIO = 2.5


def team_centroid(units: List[Obj]) -> Optional[Coords]:
    if not units:
        return None
    xs = sum(u.coords.x for u in units)
    ys = sum(u.coords.y for u in units)
    n = len(units)
    return Coords(round(xs / n), round(ys / n))


def best_move_towards(state: State, unit: Obj, target: Coords, avoid: Optional[Coords] = None) -> Optional[Action]:
    if unit.coords == target:
        return None
    direction = unit.coords.direction_to(target)
    candidates = [direction, direction.rotate_cw, direction.rotate_ccw]
    for d in candidates:
        dest = unit.coords + d
        if state.obj_by_coords(dest):
            continue
        if avoid is not None and dest == avoid:
            continue
        return Action.move(d)
    for d in candidates:
        dest = unit.coords + d
        if not state.obj_by_coords(dest):
            return Action.move(d)
    return None


robot_state: Dict[str, dict] = {}


def init_turn(state: State) -> None:
    pass


def robot(state: State, unit: Obj) -> Optional[Action]:
    st = robot_state.setdefault(unit.id, {})
    past_coords: Optional[Coords] = st.get("past_coords")
    st["past_coords"] = unit.coords

    allies = [u for u in state.objs_by_team(state.our_team) if u.id != unit.id]
    enemies = state.objs_by_team(state.other_team)

    if not enemies:
        return None

    adjacent_enemies = [e for e in enemies if unit.coords.distance_to(e.coords) == 1]
    if adjacent_enemies:
        target = min(adjacent_enemies, key=lambda e: (e.health, e.coords.distance_to(unit.coords)))
        return Action.attack(unit.coords.direction_to(target.coords))

    near_allies = [a for a in allies if unit.coords.distance_to(a.coords) <= RADIUS] + [unit]
    near_enemies = [e for e in enemies if unit.coords.distance_to(e.coords) <= RADIUS]

    nearest_enemy = min(enemies, key=lambda e: unit.coords.distance_to(e.coords))

    if near_enemies:
        ally_power = sum(a.health for a in near_allies)
        enemy_power = sum(e.health for e in near_enemies)

        if enemy_power > ally_power * RETREAT_RATIO:
            # NEW: blend "toward ally centroid" and "away from nearest enemy"
            # instead of only using the centroid (which can point toward the
            # enemy if allies happen to be on the far side).
            other_allies = [a for a in near_allies if a.id != unit.id]
            centroid = team_centroid(other_allies) if other_allies else None

            away_dir = unit.coords.direction_to(nearest_enemy.coords).opposite
            away_target = unit.coords + away_dir

            if centroid and centroid != unit.coords:
                toward_dir = unit.coords.direction_to(centroid)
                # If moving toward centroid would also move away from (or
                # sideways to) the nearest enemy, use it. Otherwise prefer
                # directly retreating from the enemy.
                dist_now = unit.coords.distance_to(nearest_enemy.coords)
                dist_if_toward = (unit.coords + toward_dir).distance_to(nearest_enemy.coords)
                if dist_if_toward >= dist_now:
                    action = best_move_towards(state, unit, centroid, past_coords)
                    if action:
                        return action
                # else fall through to direct retreat below

            dest = unit.coords + away_dir
            if not state.obj_by_coords(dest):
                return Action.move(away_dir)
            # try rotate around obstacle while still increasing/maintaining distance
            for d in [away_dir.rotate_cw, away_dir.rotate_ccw]:
                dest = unit.coords + d
                if not state.obj_by_coords(dest):
                    return Action.move(d)
            return None

    return best_move_towards(state, unit, nearest_enemy.coords, past_coords)
