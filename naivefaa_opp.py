def robot(state, unit):
    if (enemies := state.objs_by_team(state.other_team)) == []:
        return Action.move(unit.coords.direction_to(Coords(9,9)))
    
    target = min(enemies, key = lambda x: unit.coords.walking_distance_to(x.coords))
                           
    if unit.coords.walking_distance_to(target.coords) > 1:
        return Action.move(unit.coords.direction_to(target.coords))
    else:
        return Action.attack(unit.coords.direction_to(target.coords))
