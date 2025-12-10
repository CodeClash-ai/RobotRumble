def retreat(state, unit):
    enemies = []
    blanks = []
    for direction in Direction:
        other = state.obj_by_coords(unit.coords + direction)
        if other and other.team == state.other_team:
            enemies.append(other)
        elif not other:
            blanks.append(direction)

    # retreat if more than one enemy and there is room to retreat
    if len(enemies) > 1 and blanks:
        return blanks[0]
    elif len(enemies) == 1 and blanks and enemies[0].health > unit.health:
        return blanks[0]
    else:
        return None


def walk_to(state, from_coords, to_coords):
    x = to_coords.x - from_coords.x
    y = to_coords.y - from_coords.y

    xdir = Direction.East if x > 0 else Direction.West
    ydir = Direction.South if y > 0 else Direction.North

    blanks = []
    for direction in Direction:
        other = state.obj_by_coords(from_coords + direction)
        if not other:
            blanks.append(direction)

    if abs(x) > abs(y) and xdir in blanks:
        return xdir
    elif abs(y) >= abs(x) and ydir in blanks:
        return ydir
    elif xdir in blanks:
        return xdir
    elif ydir in blanks:
        return ydir
    elif blanks:
        return blanks[0]
    else:
        return None


def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    if not enemies:
        return None
    closest_enemy = min(enemies,
        key=lambda e: e.coords.walking_distance_to(unit.coords)
    )
    direction = walk_to(state, unit.coords, closest_enemy.coords)

    retreat_dir = retreat(state, unit)
    if retreat_dir:
        return Action.move(retreat_dir)

    if unit.coords.distance_to(closest_enemy.coords) == 1:
        # we're right next to them
        direction = unit.coords.direction_to(closest_enemy.coords)
        return Action.attack(direction)
    elif direction:
        return Action.move(direction)
    else:
        return None

