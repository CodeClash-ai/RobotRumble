def robot(state, unit):
    #innate properties
    in_spawn = check_spawn(state, unit) #boolean
    enemies = state.objs_by_team(state.other_team)
    allies = state.objs_by_team(state.our_team)
    closest_enemy = min(enemies,
        key=lambda e: e.coords.walking_distance_to(unit.coords)
    )
    closest_ally = min(allies,
        key=lambda e: e.coords.walking_distance_to(unit.coords)
    )
    attack_direction = unit.coords.direction_to(closest_enemy.coords)
    
    if closest_enemy.coords.walking_distance_to(unit.coords) == 2 and not in_spawn:
        return Action.attack(attack_direction)
    elif closest_enemy.coords.walking_distance_to(unit.coords) == 2 and in_spawn:
        return Action.move(attack_direction.rotate_cw)    
    elif unit.coords.distance_to(closest_enemy.coords) == 1:
        return Action.attack(attack_direction)
    else:
        return Action.move(unit.coords.direction_to(Coords(9,9)))

#checking if bot is in spawn
spawn_coords = [(14,2),(16,4),(16,14),(14,16),(4,16),(2,14),(2,4),(4,2)]
def check_spawn(state, unit):
    if unit.coords[1] == 1 or unit.coords[1] == 17 or unit.coords[0] == 1 or       unit.coords[0] == 17:
        return True
    for coord in spawn_coords:
        if unit.coords == coord:
            return True
    return False
