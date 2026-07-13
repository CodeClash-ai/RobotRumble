import json
import subprocess

# Write anton4000 code to file
with open("anton4000.py", "w") as f:
    f.write('''from rumblelib import *
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
''')

def run_match(blue, red):
    cmd = ["./rumblebot", "run", "term", blue, red, "--results-only"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if "Blue won" in res.stdout:
        return "Blue"
    elif "Red won" in res.stdout:
        return "Red"
    else:
        return "Tie"

results = [run_match("robot.py", "anton4000.py") for _ in range(10)]
blue_wins = results.count("Blue")
red_wins = results.count("Red")
ties = results.count("Tie")
print(f"Vs anton4000: Blue(us): {blue_wins}, Red: {red_wins}, Ties: {ties}")
