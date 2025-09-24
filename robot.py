import random
def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    if enemies:
        # target weakest then nearest
        target = min(enemies, key=lambda e: ((e.health if e.health is not None else 9999), unit.coords.walking_distance_to(e.coords)))
        dist = unit.coords.walking_distance_to(target.coords)
        dir_to = unit.coords.direction_to(target.coords)
        if dist <= 1:
            return Action.attack(dir_to)
        # try preferred directions toward target
        prefs = [dir_to, dir_to.rotate_cw(), dir_to.rotate_ccw(), dir_to.opposite]
        for d in prefs:
            nc = unit.coords + d
            if 0 <= nc.x < MAP_SIZE and 0 <= nc.y < MAP_SIZE and state.obj_by_coords(nc) is None:
                return Action.move(d)
        return Action.move(dir_to)
    # No enemies: explore randomly among free cardinal moves
    dirs = [Direction.North, Direction.East, Direction.South, Direction.West]
    free = [d for d in dirs if 0 <= (unit.coords + d).x < MAP_SIZE and 0 <= (unit.coords + d).y < MAP_SIZE and state.obj_by_coords(unit.coords + d) is None]
    if free:
        return Action.move(random.choice(free))
    return Action.move(Direction.North)
