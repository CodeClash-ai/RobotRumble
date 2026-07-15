from enum import Enum, auto
from typing import *

def robot(state: State, unit: Obj) -> Optional[Action]:
    allies = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)
    
    # Check for adjacent enemies to attack first
    adjacent_enemies = []
    for direction in Direction:
        neighbor = state.obj_by_coords(unit.coords + direction)
        if neighbor and neighbor.team == state.other_team:
            adjacent_enemies.append((direction, neighbor))
            
    if adjacent_enemies:
        # Attack the one with the lowest health (focus fire / finish off)
        best_target_dir, best_target_obj = min(adjacent_enemies, key=lambda x: x[1].health)
        return Action.attack(best_target_dir)

    if not enemies:
        return None

    # Focus fire on the weakest reachable enemy if possible, or closest overall
    # Let's find the enemy that has the lowest health among those close to us
    closest_enemy = min(enemies, key=lambda e: (unit.coords.walking_distance_to(e.coords), e.health))
    direction = unit.coords.direction_to(closest_enemy.coords)
    
    # To avoid stepping on other allies, check if the cell is occupied
    move_target = state.obj_by_coords(unit.coords + direction)
    if not move_target:
        return Action.move(direction)
    else:
        # Instead of just rotating cw/ccw randomly, let's see which direction gets us closer to the enemy
        alt_dirs = [direction.rotate_cw, direction.rotate_ccw]
        # Sort alternative directions by how close they bring us to the enemy
        alt_dirs.sort(key=lambda d: (unit.coords + d).walking_distance_to(closest_enemy.coords))
        for alt_dir in alt_dirs:
            if not state.obj_by_coords(unit.coords + alt_dir):
                return Action.move(alt_dir)
                
    # If all primary paths are blocked, try moving anywhere
    for alt_dir in Direction:
        if not state.obj_by_coords(unit.coords + alt_dir):
            return Action.move(alt_dir)
            
    return None
