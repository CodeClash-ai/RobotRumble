import random
center = Coords(9, 9)
# coords representing the center of the board
#def is_obstructed(unit, move_to, tpl):
#    return Coords(unit.coords.x + move_to.to_coords.x, unit.coords.y + move_to.to_coords.y) in tpl
# returns true if the robot's attempted path is obstructed
    
def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    closest_enemy = min(enemies, key=lambda e: e.coords.distance_to(unit.coords))
    # get the closest enemy
    if unit.coords.distance_to(closest_enemy.coords) == 1:
        return Action.attack(unit.coords.direction_to(closest_enemy.coords))
        # attack the nearest enemy if it is nearby
    else:
        move_dir = unit.coords.direction_to(center)
        # move towards the center initially
        team_position_list = [enume.coords for enume in state.objs_by_team(state.our_team)]
#        if (is_obstructed(unit, move_dir, team_position_list)):
#            chosen_dir = random.randint(0, 3)
#            if (chosen_dir == 0): 
#                move_dir = unit.coords.direction_to(Coords(unit.coords.x, unit.coords.y+1))
#            elif (chosen_dir == 1): 
#                move_dir = unit.coords.direction_to(Coords(unit.coords.x, unit.coords.y-1))
#            elif (chosen_dir == 2): 
#                move_dir = unit.coords.direction_to(Coords(unit.coords.x+1, unit.coords.y))
#            else:
#                move_dir = unit.coords.direction_to(Coords(unit.coords.x-1, unit.coords.y))
        # if obstructed, then move randomly
        return Action.move(move_dir)
