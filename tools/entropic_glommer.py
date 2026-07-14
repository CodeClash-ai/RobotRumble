gloms = dict()
glom_lookup = dict()
target_ids = dict()
claimed_locations = set()
center = Coords(9, 9)

def nearest(team, unit):
    if team and len(team):
        return min(team, key=lambda e: e.coords.walking_distance_to(unit.coords))
    return None

# Credit to mitch84 for writing the walk_to and retreat methods for the bot retreat_walk2
def walk_to(state, from_coords, to_coords):
    x = to_coords.x - from_coords.x
    y = to_coords.y - from_coords.y

    xdir = Direction.East if x > 0 else Direction.West
    ydir = Direction.South if y > 0 else Direction.North

    blanks = []
    for direction in Direction:
        possible_location = from_coords + direction
        other = state.obj_by_coords(possible_location)
        if not other:
            blanks.append(direction)
            

    if abs(x) > abs(y) and xdir in blanks and from_coords + xdir not in claimed_locations:
        return xdir
    elif abs(y) >= abs(x) and ydir in blanks and from_coords + ydir not in claimed_locations:
        return ydir
    elif xdir in blanks and from_coords + xdir not in claimed_locations:
        return xdir
    elif ydir in blanks and from_coords + ydir not in claimed_locations:
        return ydir
    elif blanks and from_coords + blanks[0] not in claimed_locations:
        return blanks[0]
    else:
        return None

def count_adj_enemies(state, coords):
    enemies = 0
    for d in Direction:
        location = coords + d
        other = state.obj_by_coords(location)
        if other and other.team == state.other_team:
            enemies += 1
    return enemies

# Credit for this method to atl15, taken from the bot centerrr
# checking if bot is in spawn
spawn_coords = [
    (14, 2),
    (13, 2),
    (16, 4),
    (16, 5),
    (16, 13),
    (16, 14),
    (14, 16),
    (13, 16),
    (4, 16),
    (5, 16),
    (2, 14),
    (2, 13),
    (2, 4),
    (4, 2),
]


def check_spawn(unit_coord):
    if (
        unit_coord.x == 1
        or unit_coord.x == 17
        or unit_coord.y == 1
        or unit_coord.y == 17
    ):
        return True
    for coord in spawn_coords:
        if unit_coord.x == coord[0] and unit_coord.y == coord[1]:
            return True
    return False
    
def retreat(state, unit):
    return retreat_inner(state, unit, unit.coords)

def retreat_inner(state, unit, coords):
    enemies = []
    blanks = []
    walls = []
    for direction in Direction:
        new_location = coords + direction
        other = state.obj_by_coords(new_location)
        if other and other.team == state.other_team:
            enemies.append(other)
        elif (not other or new_location == unit.coords) and new_location not in claimed_locations:
            blanks.append((direction, count_adj_enemies(state, new_location)))
            
    enemies = sorted(enemies, key=lambda e: e.health * -1)
    blanks = sorted(blanks, key=lambda tup: tup[1])
    do_retreat = False
    if state.turn % 10 == 0:
        blanks = [space for space in blanks if not check_spawn(coords+space[0])]
        do_retreat = check_spawn(coords)
    
    if do_retreat and blanks:
        return blanks[0][0]
    elif not blanks or not enemies or len(enemies) < blanks[0][1]:
        return None
    # retreat if more than one enemy and there is room to retreat
    elif len(enemies) >= unit.health and blanks:
        return blanks[0][0]
    elif enemies[0].health > unit.health:
        return blanks[0][0]
    else:
        return None

def init_turn(state):
    global gloms
    global glom_lookup
    global claimed_locations
    global center
    allies = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)
    unglommed = set(allies + enemies)
    center = Coords(9, 9)
    gloms = dict()
    glom_lookup = dict()
    claimed_locations = set()
    
    def glom_neighbors(bot, glom, unglommed):
        glom['bots'].add(bot)
        glom['health'] += bot.health
        
        neighbors = [e for e in unglommed if e and e.coords.walking_distance_to(bot.coords) < 3]
        for neighbor in neighbors:
            if neighbor.team == bot.team and neighbor in unglommed:
                unglommed.remove(neighbor)
                glom_lookup[neighbor.id] = glom_lookup[bot.id]
                glom_neighbors(neighbor, glom, unglommed)
        
        return glom
     
    while len(unglommed):
        current = unglommed.pop()
        
        if not glom_lookup.get(current.id):
            glom_lookup[current.id] = len(gloms)
        
        gloms[glom_lookup[current.id]] = glom_neighbors(current, {'bots': set(), 'health': 0}, unglommed)
        if(current.team == state.our_team):
            target_ids[glom_lookup[current.id]] = nearest(enemies, current).id
    



def robot(state, unit):
    allies = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)
    glom_id = glom_lookup[unit.id]
    glom = gloms[glom_id]
    
    enemy = state.obj_by_id(target_ids[glom_id])
    enemy_glom = gloms[glom_lookup[enemy.id]]
    enemy = nearest(enemy_glom['bots'], unit)
    nearest_enemy = nearest(enemies, unit)
    if not enemy:
        enemy = nearest_enemy
    
    
    
    
    attack_direction = unit.coords.direction_to(enemy.coords)
    
    debug.inspect('glom', glom)
    debug.inspect('target', enemy)
    
    retreat_direction = retreat(state, unit)
    if retreat_direction:
        debug.inspect('action', 'retreat')
        claimed_locations.add(unit.coords + retreat_direction)
        return Action.move(retreat_direction)
    
    
    if unit.coords.walking_distance_to(nearest_enemy.coords) == 1 and nearest_enemy.health < unit.health:
        debug.inspect('action', 'finishing blow')
        return Action.attack(unit.coords.direction_to(nearest_enemy.coords))
    
    # If our gang is bigger, kill em
    elif len(enemy_glom['bots']) < len(glom['bots']) or glom['health'] > enemy_glom['health']:
        if (len(glom['bots']) > 1 and unit.coords.walking_distance_to(enemy.coords) == 1) or (len(glom['bots']) == 1 and unit.coords.walking_distance_to(enemy.coords) == 2):
            debug.inspect('action', 'attack')
            return Action.attack(attack_direction)
        debug.inspect('action', 'swarm')
        move_direction = walk_to(state, unit.coords, enemy.coords)
        if move_direction:
            would_retreat = retreat_inner(state, unit, unit.coords + move_direction)
            if not would_retreat:
                claimed_locations.add(unit.coords + move_direction)
                return Action.move(move_direction)
    ally = nearest([ally for ally in allies if ally.id != unit.id and glom_lookup[ally.id] != glom_id], unit)
    if ally:
        debug.inspect('ally', ally)
        move_direction = walk_to(state, unit.coords, ally.coords)
        if move_direction:
            would_retreat = retreat_inner(state, unit, unit.coords + move_direction)
            if not would_retreat:
                debug.inspect('action', 'glomming')
                claimed_locations.add(unit.coords + move_direction)
                return Action.move(move_direction)
    center_direction = walk_to(state, unit.coords, center)
    if center_direction:
        would_retreat = retreat_inner(state, unit, unit.coords + center_direction)
        if not would_retreat:
            debug.inspect('action', 'take the center')
            claimed_locations.add(unit.coords + center_direction)
            return Action.move(center_direction)
    location_unit = state.obj_by_coords(unit.coords.__add__(attack_direction.to_coords))
    if location_unit and not location_unit.team == unit.team:
        debug.inspect('action', 'fight to the death')
        return Action.attack(attack_direction)
    
