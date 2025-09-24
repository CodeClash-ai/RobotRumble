def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    if enemies:
        target = min(enemies, key=lambda e: unit.coords.walking_distance_to(e.coords))
        dist = unit.coords.walking_distance_to(target.coords)
        dir_to = unit.coords.direction_to(target.coords)
        if dist <= 1:
            return Action.attack(dir_to)
        # Try preferred directions toward target
        for d in (dir_to, dir_to.rotate_cw(), dir_to.rotate_ccw(), dir_to.opposite):
            next_coords = unit.coords + d
            if 0 <= next_coords.x < MAP_SIZE and 0 <= next_coords.y < MAP_SIZE:
                obj = state.obj_by_coords(next_coords)
                if obj is None:
                    return Action.move(d)
        return Action.move(dir_to)

    # No enemies visible: move toward center to encourage fights
    center = Coords(MAP_SIZE // 2, MAP_SIZE // 2)
    dir_center = unit.coords.direction_to(center)
    return Action.move(dir_center)
