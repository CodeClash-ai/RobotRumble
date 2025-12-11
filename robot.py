def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    allies = state.objs_by_team(state.our_team)
    
    closest_enemy = min(enemies,
        key=lambda e: e.coords.distance_to(unit.coords)
    )
    
    closest_ally_to_enemy = min(allies,
        key=lambda e: e.coords.distance_to(closest_enemy.coords)
    )
    direction = unit.coords.direction_to(closest_enemy.coords)
    
    if unit.coords.distance_to(closest_enemy.coords) > closest_ally_to_enemy.coords.distance_to(closest_enemy.coords):
        pass
    else:
        if unit.coords.distance_to(closest_enemy.coords) == 1:
            return Action.attack(direction)
        else:
            return Action.move(direction)

