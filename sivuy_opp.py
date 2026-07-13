import rumblelib as rbl


def robot(state: rbl.State, unit: rbl.Obj):
    enemies = state.objs_by_team(state.other_team)
    
    closestEnemy = min(enemies, key=lambda x: x.coords.distance_to(unit.coords))
    
    direction = unit.coords.direction_to(closestEnemy.coords)
    
    if unit.coords.distance_to(closestEnemy.coords) == 1 :
        return rbl.Action.attack(direction)
    else:
        return rbl.Action.move(direction)

