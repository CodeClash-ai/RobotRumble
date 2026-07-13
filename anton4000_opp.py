# camper bot ️🏕️


CENTER = Coords(int(MAP_SIZE / 2), int(MAP_SIZE / 2))
camper_tiles = []
for x in range(0, MAP_SIZE):
    for y in range(0, MAP_SIZE):
        if int(Coords(x, y).distance_to(CENTER)) == 7:
            camper_tiles.append((x, y))
            

camper_tile_status = {}
available_camper_tiles = []
            
def init_turn(state):
    global available_camper_tiles
    camper_tiles_status = {}
    available_camper_tiles = []
    for coords in camper_tiles:
        obj = state.obj_by_coords(Coords(coords[0], coords[1]))
        if obj is None:
            available_camper_tiles.append((coords))
    

def robot(state, unit):
    if (unit.coords.x, unit.coords.y) in camper_tiles:
        direction = unit.coords.direction_to(CENTER)
        for i in range(4):
           target = state.obj_by_coords(unit.coords + direction.to_coords)
           if target and target.team == state.other_team:
                return Action.attack(direction)
           direction = direction.rotate_cw
        return None
        
    closest_camper_tile = min(available_camper_tiles,
        key=lambda coords: Coords(coords[0], coords[1]).distance_to(unit.coords)
    )
    
    direction = unit.coords.direction_to(Coords(closest_camper_tile[0], closest_camper_tile[1]))

    return Action.move(direction)

