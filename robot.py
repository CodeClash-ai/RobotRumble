from enum import Enum, auto
from typing import *

def robot(state: State, unit: Obj) -> Optional[Action]:
    our_team = state.our_team
    other_team = state.other_team
    
    # Get all live robots on both teams
    allies = state.objs_by_team(our_team)
    enemies = state.objs_by_team(other_team)
    
    if not enemies:
        return None
        
    def is_free(coords: Coords) -> bool:
        if coords.x < 0 or coords.x >= MAP_SIZE or coords.y < 0 or coords.y >= MAP_SIZE:
            return False
        # Do not use obj_by_coords if it is slow or causes issues.
        # Wait, the stdlib has state.obj_by_coords(coords) which is extremely fast.
        # But wait! Why did it timeout? Maybe MAP_SIZE is not defined or not imported?
        # Ah! MAP_SIZE is in rumblelib or standard globals, but we should verify if MAP_SIZE is imported.
        # Let's import MAP_SIZE, Coords, Action, Direction, State, Obj, etc.
        # Actually, in RobotRumble standard library, we might need to import everything or they are already pre-imported.
        # Let's check.
        obj = state.obj_by_coords(coords)
        return obj is None

    # Identify the closest enemy and distance to them
    closest_enemy = min(enemies, key=lambda e: unit.coords.distance_to(e.coords))
    dist_to_closest = unit.coords.distance_to(closest_enemy.coords)
    
    # Locate adjacent enemies specifically (distance == 1)
    adjacent_enemies = [e for e in enemies if unit.coords.distance_to(e.coords) == 1]
    
    # Local health/strength count to decide whether to fight or flee.
    # Radius of 4 is standard local micro neighborhood.
    nearby_friends = [f for f in allies if unit.coords.distance_to(f.coords) <= 4]
    nearby_enemies = [e for e in enemies if unit.coords.distance_to(e.coords) <= 4]
    
    friends_hp = sum(f.health for f in nearby_friends)
    enemies_hp = sum(e.health for e in nearby_enemies)
    
    if adjacent_enemies:
        best_target = min(adjacent_enemies, key=lambda e: e.health)
        if len(nearby_friends) * 1.5 < len(nearby_enemies) and unit.health <= 2 and best_target.health >= unit.health:
            escape_dir = unit.coords.direction_to(best_target.coords).opposite
            if is_free(unit.coords + escape_dir):
                return Action.move(escape_dir)
            elif is_free(unit.coords + escape_dir.rotate_cw):
                return Action.move(escape_dir.rotate_cw)
            elif is_free(unit.coords + escape_dir.rotate_ccw):
                return Action.move(escape_dir.rotate_ccw)
        
        attack_dir = unit.coords.direction_to(best_target.coords)
        return Action.attack(attack_dir)

    if friends_hp + len(nearby_friends) < enemies_hp + len(nearby_enemies) and unit.health <= 2:
        flee_dir = unit.coords.direction_to(closest_enemy.coords).opposite
        for d in [flee_dir, flee_dir.rotate_cw, flee_dir.rotate_ccw]:
            if is_free(unit.coords + d):
                return Action.move(d)

    move_dir = unit.coords.direction_to(closest_enemy.coords)
    for d in [move_dir, move_dir.rotate_cw, move_dir.rotate_ccw, move_dir.opposite]:
        if is_free(unit.coords + d):
            return Action.move(d)
            
    return None
