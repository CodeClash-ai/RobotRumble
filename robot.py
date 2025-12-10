def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    
    closeEnemies = list(filter(lambda e: unit.coords.walking_distance_to(e.coords) == 1, enemies))
    debug.inspect("closeEnemies", closeEnemies)
    
    closest = None
    if len(closeEnemies) > 0:
        closest = min(closeEnemies, key=lambda e: e.health)
        debug.inspect("picked element", closest)
    
    
    if closest == None:
        closest = enemies[0]
        for enemy in enemies:
            distance = enemy.coords.walking_distance_to(unit.coords)
            if distance < closest.coords.walking_distance_to(unit.coords):
                closest = enemy
                
                
                
    distance = closest.coords.walking_distance_to(unit.coords)
    debug.inspect("distance", distance)
    if distance == 1:
        return Action.attack(unit.coords.direction_to(closest.coords))
    else:
        return Action.move(unit.coords.direction_to(closest.coords))

