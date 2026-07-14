from rumblelib import *

def is_spawn_danger(turn: int) -> bool:
    return turn % 10 == 0

def robot(state: State, unit: Obj) -> Action:
    if is_spawn_danger(state.turn) and unit.coords.is_spawn():
        for dir in [Direction.North, Direction.East, Direction.South, Direction.West]:
            dest = unit.coords + dir
            if not dest.is_spawn() and state.obj_by_coords(dest) is None:
                return Action.move(dir)
    for dir in [Direction.North, Direction.East, Direction.South, Direction.West]:
        target = state.obj_by_coords(unit.coords + dir)
        if target and target.team == state.other_team:
            return Action.attack(dir)
    enemies = state.objs_by_team(state.other_team)
    if not enemies:
        return Action.move(Direction.North)
    target = min(enemies, key=lambda e: unit.coords.walking_distance_to(e.coords))
    direction = unit.coords.direction_to(target.coords)
    next_coords = unit.coords + direction
    occupant = state.obj_by_coords(next_coords)
    if occupant is None or occupant.team == state.other_team:
        return Action.move(direction)
    for dir in [Direction.North, Direction.East, Direction.South, Direction.West]:
        check = unit.coords + dir
        if state.obj_by_coords(check) is None:
            return Action.move(dir)
    return Action.move(Direction.North)
