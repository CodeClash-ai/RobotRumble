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
    direction_to_center = unit.coords.direction_to(Coords(9,9))
    
    return ((((((((((((((Action.move(Direction.West)) if ((unit.coords.y) >= (3)) else ((Action.move(unit.coords.direction_to(closest_enemy.coords))) if ((Coords(9,9).distance_to(unit.coords)) >= (1)) else (Action.attack(unit.coords.direction_to(closest_enemy.coords))))) if ((unit.coords.x) >= (9)) else (Action.move(Direction.East))) if ((Coords(9,9).distance_to(unit.coords)) >= (2)) else (Action.attack(unit.coords.direction_to(closest_enemy.coords)))) if ((Coords(9,9).distance_to(unit.coords)) >= (4)) else (Action.move(Direction.North))) if ((closest_enemy.coords.distance_to(unit.coords)) >= (0)) else (Action.move(unit.coords.direction_to(closest_enemy.coords)))) if ((unit.health) >= (1)) else (((Action.move(unit.coords.direction_to(closest_enemy.coords))) if ((unit.coords.y) == (13)) else (Action.attack(unit.coords.direction_to(closest_enemy.coords)))) if (((unsafe_surrounding_tiles(unit.coords, state)) >= (4)) if ((Coords(9,9).distance_to(unit.coords)) >= (4)) else ((closest_ally.coords.distance_to(unit.coords)) >= (9))) else (Action.move(Direction.North)))) if ((Coords(9,9).distance_to(unit.coords)) >= (4)) else (Action.move(unit.coords.direction_to(closest_enemy.coords)))) if (((Coords(9,9).distance_to(unit.coords)) if ((closest_enemy.coords.distance_to(unit.coords)) >= (5)) else (7)) >= (1)) else ((Action.move(unit.coords.direction_to(closest_enemy.coords))) if ((closest_ally.coords.distance_to(unit.coords)) >= (2)) else (Action.move(Direction.East)))) if ((unit.health) >= (3)) else (Action.move(unit.coords.direction_to(closest_enemy.coords)))) if ((Coords(9,9).distance_to(unit.coords)) >= (9)) else (Action.move(unit.coords.direction_to(closest_enemy.coords)))) if ((Coords(9,9).distance_to(unit.coords)) >= (3)) else ((Action.move(unit.coords.direction_to(closest_enemy.coords))) if ((unit.health) >= (8)) else (Action.move(Direction.South)))) if ((unsafe_surrounding_tiles(unit.coords, state)) == (0)) else (Action.attack(unit.coords.direction_to(closest_enemy.coords)))) if ((Coords(9,9).distance_to(unit.coords)) >= (6)) else (Action.attack(unit.coords.direction_to(closest_enemy.coords)))) if ((unit.health) >= (1)) else (Action.move(unit.coords.direction_to(closest_enemy.coords)))
