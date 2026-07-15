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

    # Find the absolute closest enemy or tie-break on lowest health
    closest_enemy = min(enemies, key=lambda e: (unit.coords.walking_distance_to(e.coords), e.health))
    
    # Best direction is towards the closest enemy
    best_dir = unit.coords.direction_to(closest_enemy.coords)
    
    # Try all directions, sorted by:
    # 1. Whether they are unblocked (an unblocked path is strictly better)
    # 2. How close they bring us to the target (walking distance)
    # This automatically prefers the best direct move, then tries optimal/suboptimal rotative detours,
    # and only moves backwards if completely blocked.
    all_dirs = list(Direction)
    
    def move_priority(d: Direction) -> Tuple[int, int]:
        target_coords = unit.coords + d
        is_blocked = 1 if state.obj_by_coords(target_coords) else 0
        dist = target_coords.walking_distance_to(closest_enemy.coords)
        return (is_blocked, dist)
        
    all_dirs.sort(key=move_priority)
    
    # Move in the best prioritized direction that is not blocked
    for d in all_dirs:
        if not state.obj_by_coords(unit.coords + d):
            return Action.move(d)
            
    return None
