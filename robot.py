def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    closest_enemy = min(enemies,
        key=lambda e: e.coords.distance_to(unit.coords)
    )

    if unit.health > 2:
        direction = unit.coords.direction_to(closest_enemy.coords)

        if unit.coords.distance_to(closest_enemy.coords) == 1:
            # we're right next to them
            return Action.attack(direction)
    else:
        direction = closest_enemy.coords.direction_to(unit.coords)

        return Action.move(direction)

    center = Coords(10, 10)
    return Action.move(unit.coords.direction_to(center))

