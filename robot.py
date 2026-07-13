from enum import Enum, auto
from typing import *


class Quadrant(Enum):
    One = auto()
    Two = auto()
    Three = auto()
    Four = auto()

    @staticmethod
    def from_coords(coords: Coords) -> "Quadrant":
        if coords.x <= MAP_SIZE // 2:
            if coords.y <= MAP_SIZE // 2:
                return Quadrant.Two
            else:
                return Quadrant.Three
        else:
            if coords.y <= MAP_SIZE // 2:
                return Quadrant.One
            else:
                return Quadrant.Four


target_ids: Dict[Quadrant, Optional[str]] = {
    Quadrant.One: None,
    Quadrant.Two: None,
    Quadrant.Three: None,
    Quadrant.Four: None,
}


def total_distance_for_units(units: List[Obj], target: Obj) -> float:
    return sum([unit.coords.distance_to(target.coords) for unit in units])


def init_turn(state: State) -> None:
    global target_ids

    for (q, id) in target_ids.items():
        if id and not state.obj_by_id(id):
            target_ids[q] = None

    allies = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)
    for q in target_ids:
        if not target_ids[q]:
            q_allies = [ally for ally in allies if Quadrant.from_coords(ally.coords) == q]
            q_enemies = [enemy for enemy in enemies if Quadrant.from_coords(enemy.coords) == q]

            if q_enemies and q_allies:
                closest_enemy = min(q_enemies, key=lambda enemy: total_distance_for_units(q_allies, enemy))
                target_ids[q] = closest_enemy.id


robot_state: Dict[str, dict] = {}


def robot(state: State, unit: Obj) -> Optional[Action]:
    past_coords: Optional[Coords] = robot_state.setdefault(unit.id, {}).get("past_coords")
    robot_state[unit.id]["past_coords"] = unit.coords
    
    id = target_ids[Quadrant.from_coords(unit.coords)]
    if id:
        target = state.obj_by_id(id)
        if target:
            
            direction = unit.coords.direction_to(target.coords)

            if unit.coords.distance_to(target.coords) == 1:
                # we're right next to them
                return Action.attack(direction)
            else:
                move_target = state.obj_by_coords(unit.coords + direction)
                if not move_target:
                    return Action.move(direction)
                else:
                    directions = [direction.rotate_cw, direction.rotate_ccw]
                    destinations = [unit.coords + direction for direction in directions]
                    if target.coords.distance_to(destinations[0]) < target.coords.distance_to(destinations[1]) \
                            and not state.obj_by_coords(destinations[0]) \
                            and past_coords != destinations[0]:
                        return Action.move(directions[0])
                    elif not state.obj_by_coords(destinations[1]) \
                            and past_coords != destinations[1]:
                        return Action.move(directions[1])
                    else:
                        return None
        else:
            raise Exception('Id points to nonexistent target')

