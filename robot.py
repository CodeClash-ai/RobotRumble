def surrounding_tiles(tile):
    return (
        Coords(tile.x, tile.y+1),
        Coords(tile.x, tile.y-1),
        Coords(tile.x-1, tile.y),
        Coords(tile.x+1, tile.y)
              )
    
def corner_tiles(tile):
    return (
        Coords(tile.x+1, tile.y+1),
        Coords(tile.x+1, tile.y-1),
        Coords(tile.x-1, tile.y+1),
        Coords(tile.x-1, tile.y-1)
    )
    
def allies_around_corner(tile, state):
    return sum(is_friendly(edge, state) for edge in corner_tiles(tile))
    
def unsafe_surrounding_tiles(tile, state):
    return sum(is_enemy(edge, state) for edge in surrounding_tiles(tile))

def friendly_surrounding_tiles(tile, state):
    return sum(is_friendly(edge, state) for edge in surrounding_tiles(tile))

def empty_surrounding_tiles(tile, state):
    return sum(is_terrain(edge, state) for edge in surrounding_tiles(tile))

def is_friendly(tile, state):
    return (obj:=state.obj_by_coords(tile)) is not None and obj.team == state.our_team

def is_enemy(tile, state):
    return (obj:=state.obj_by_coords(tile)) is not None and obj.team == state.other_team

def is_terrain(tile, state):
    return (obj:=state.obj_by_coords(tile)) is not None and obj.obj_type == ObjType.Terrain

def clockwise_direction_towards(tile1, tile2):
    if tile1.x == tile2.x:
        return Direction.North if tile1.y > tile2.y else Direction.South
    if tile1.y == tile2.y:
        return Direction.West if tile1.x > tile2.x else Direction.East
    if tile1.y > tile2.y and tile1.x > tile2.x:
        return Direction.West
    if tile1.y > tile2.y and tile1.x < tile2.x:
        return Direction.North
    if tile1.y < tile2.y and tile1.x < tile2.x:
        return Direction.East
    if tile1.y < tile2.y and tile1.x > tile2.x:
        return Direction.South
    return Direction.West

def find_good_evasion_tile(tile, state):
    try:
        return max(
            (i for i in surrounding_tiles(tile) if
                    not is_terrain(i, state) and
                    not is_enemy(i, state) and
                    not is_friendly(i, state) and
                    unsafe_surrounding_tiles(i, state)==0),
            key=lambda i: (
                -empty_surrounding_tiles(i, state),
                friendly_surrounding_tiles(i, state),
                -i.walking_distance_to(Coords(9,9))
            )
      )
    except ValueError:
        return None

def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    closest_enemy = min(enemies,
        key=lambda e: (
            e.coords.walking_distance_to(unit.coords),
            -allies_around_corner(e.coords, state)-friendly_surrounding_tiles(e.coords,state),
            e.health
        )
    )
    closest_ally = min((i for i in state.objs_by_team(unit.team) if i.id != unit.id),
        key=lambda e: (e.coords.walking_distance_to(unit.coords), e.health)
    )
    direction_to_center = clockwise_direction_towards(unit.coords, Coords(9,9))
    
    debug.inspect("surrounding_empty_tiles", empty_surrounding_tiles(unit.coords, state))
    debug.inspect("evasion_tile", find_good_evasion_tile(unit.coords, state))
    debug.inspect("Unsafe Surrounding tiles", unsafe_surrounding_tiles(unit.coords, state))
    debug.inspect("Closest enemy health", closest_enemy.health)
    debug.inspect("Closest enemy friendly surrounding tiles", friendly_surrounding_tiles(closest_enemy.coords, state))
    
    if unsafe_surrounding_tiles(unit.coords, state)>1 and \
        closest_enemy.health>=friendly_surrounding_tiles(closest_enemy.coords, state) and \
        (evading_tile:=find_good_evasion_tile(unit.coords, state)) is not None:
        
        # If surrounded, flee
        return Action.move(unit.coords.direction_to(evading_tile))
        
    elif empty_surrounding_tiles(unit.coords, state)>=1 and \
        ((evading_tile:=find_good_evasion_tile(unit.coords, state)) is not None or state.turn % 10 == 0):
        
        # Units near the edge are removed after 10 turns, so go away from the edge is possible
        if evading_tile is not None:
            return Action.move(unit.coords.direction_to(evading_tile))
        elif is_enemy(unit.coords + direction_to_center, state):
            return Action.attack(direction_to_center)
        else:
            return Action.move(direction_to_center)
        
    if unit.health >= closest_enemy.health:
        direction = clockwise_direction_towards(unit.coords, closest_enemy.coords)
        
        if unit.coords.walking_distance_to(closest_enemy.coords) >= 5:
            # If we are far away from any enemies, go to the center or the nearest ally
            if 2 < unit.coords.walking_distance_to(closest_ally.coords) <= 8:
                direction = unit.coords.direction_to(closest_ally.coords)
            else:
                direction = unit.coords.direction_to(Coords(9,9))
            return Action.move(direction)
        if (
                (enemy_distance := unit.coords.walking_distance_to(closest_enemy.coords)) <= 2 and
                (enemy_distance == 1
                 or (friendly_surrounding_tiles(closest_enemy.coords, state) == 0
                 and allies_around_corner(closest_enemy.coords, state) < 3)
                ) and
               
                not is_friendly(unit.coords + direction, state)
            ):
            # If we are next to a enemy, or 2 tiles away from a enemy that is not surrounded, preemptively attack
            return Action.attack(direction)
        
        elif unit.coords.walking_distance_to(closest_enemy.coords) > 1 and empty_surrounding_tiles(closest_enemy.coords, state)==0:
            if state.obj_by_coords(unit.coords + direction.to_coords) is not None and state.obj_by_coords(unit.coords + direction.to_coords).team == unit.team:
                direction = direction.rotate_ccw;
            # If we are far away from a enemy, or 1 tile away from a surrounded enemy, move towards it
            return Action.move(direction)
        else:
            # If all else fails, attack
            return Action.attack(direction)
        
    elif unit.coords.walking_distance_to(closest_enemy.coords)<=3:
        direction = closest_enemy.coords.direction_to(unit.coords)
        
        if (state.obj_by_coords(unit.coords + direction.to_coords) is not None
            and unit.coords.walking_distance_to(closest_enemy.coords)==1):
            return Action.attack(unit.coords.direction_to(closest_enemy.coords))
        
        elif unsafe_surrounding_tiles(unit.coords + direction, state) == 0:
            # If the the tile we would want to flee to is safe, flee in that direction
            return Action.move(direction)
        else:
            # If we can't safely flee, attack back
            return Action.attack(direction.opposite)
        
    else:
        direction_to_center = clockwise_direction_towards(unit.coords, closest_ally.coords or Coords(9,9))
        return Action.move(direction_to_center)

    
