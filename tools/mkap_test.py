from rumblelib import *

def is_spawn_danger(turn: int) -> bool:
    return turn % 10 == 0

def robot(state: State, unit: Obj) -> Action:
    # Don't sit in spawn tiles on danger turns
    if is_spawn_danger(state.turn) and unit.coords.is_spawn():
        for dir in [Direction.North, Direction.East, Direction.South, Direction.West]:
            dest = unit.coords + dir
            if not dest.is_spawn() and state.obj_by_coords(dest) is None:
                return Action.move(dir)

    # Attack if enemy is adjacent
    for dir in [Direction.North, Direction.East, Direction.South, Direction.West]:
        target = state.obj_by_coords(unit.coords + dir)
        if target and target.team == state.other_team:
            return Action.attack(dir)

    # Seek closest enemy
    enemies = state.objs_by_team(state.other_team)
    if not enemies:
        return Action.move(Direction.North)

    # Find the closest enemy
    target = min(enemies, key=lambda e: unit.coords.walking_distance_to(e.coords))
    direction = unit.coords.direction_to(target.coords)

    # Try to move there if it's safe
    next_coords = unit.coords + direction
    occupant = state.obj_by_coords(next_coords)
    if occupant is None or occupant.team == state.other_team:
        return Action.move(direction)

    # If blocked, try another adjacent direction
    for dir in [Direction.North, Direction.East, Direction.South, Direction.West]:
        check = unit.coords + dir
        if state.obj_by_coords(check) is None:
            return Action.move(dir)

    return Action.move(Direction.North)  # Final fallback
