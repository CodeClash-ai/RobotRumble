def robot(state, unit):
    if state.turn % 2 == 0:
        return Action.move(Direction.East)
    else:
        return Action.attack(Direction.South)
def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    closest_enemy = min(enemies,
        key=lambda e: e.coords.distance_to(unit.coords)
    )
    direction = unit.coords.direction_to(closest_enemy.coords)

    if unit.coords.distance_to(closest_enemy.coords) == 1:
        # we're right next to them
        return Action.attack(direction)
    else:
        return Action.move(direction)

