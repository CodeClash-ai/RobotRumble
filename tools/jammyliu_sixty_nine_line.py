# created by James Liu NU'24, about to overthrow Liam with 69 lines

def robot(state, unit):
    # exit spawn region
    if in_spawn(state, unit.coords):
        for d in Direction:
            if not in_spawn(state, unit.coords+d):
                return Action.move(d)  
    
    # compute weakest nearby enemy
    enemies = closest_units(state, unit.coords, state.other_team)
    enemy = None
    min_health = 6
    for e in enemies:
        if e.health < min_health:
            min_health = e.health
            enemy = e
            
    if enemy is not None:
        # compute direction towards enemy
        enemy_dir = unit.coords.direction_to(enemy.coords)
        enemy_dist = unit.coords.walking_distance_to(enemy.coords)
        if enemy_dist <= 2:
            # attack weakest adjacent (also preemptively)
            return Action.attack(enemy_dir)
        else:
            # if unit has health, show aggression
            move_dir = enemy_dir
            if unit.health < 3:
                move_dir = move_dir.opposite
            move_coords = unit.coords+move_dir
            if not in_spawn(state, move_coords, 1):
                return Action.move(enemy_dir)
    else:
        # move toward friendly
        friend = closest_units(state, unit.coords, state.our_team)[0]
        return Action.move(unit.coords.direction_to(friend.coords))
    
# true if unit is in spawn region when (turn+turn_offset) % 10 == 0
def in_spawn(state, coords, turn_offset=0):
    if not (state.turn+turn_offset) % 10 == 0:
        return False
    for d in Direction:
        if is_terrain(state, coords+d):
            return True
    return False

def is_terrain(state, coords):
    obj = state.obj_by_coords(coords)
    if obj is None:
        return False
    if obj.obj_type == ObjType.Terrain:
        return True
    return False

def closest_units(state, coords, team):
    # find closest units on given team
    units = []
    min_dist = 100
    for obj in state.objs_by_team(team):
        dist = coords.walking_distance_to(obj.coords)
        if dist < min_dist and dist != 0:
            min_dist = dist
            units = [obj]
        elif dist == min_dist:
            units.append(obj)
    return units

# lmao nice
