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
        obj = state.obj_by_coords(coords)
        return obj is None

    # Identify the closest enemy and distance to them, taking enemy health into account
    closest_enemy = min(enemies, key=lambda e: unit.coords.distance_to(e.coords) + e.health / 10.0)
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
        # Focus on lowest health adjacent enemy to secure kills
        best_target = min(adjacent_enemies, key=lambda e: e.health)
        
        # Flee logic if we are weak and outnumbered
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

    # If we are low health and outnumbered in neighborhood, run away
    if (friends_hp + len(nearby_friends) < enemies_hp + len(nearby_enemies) or len(nearby_friends) < len(nearby_enemies)) and unit.health <= 2:
        flee_dir = unit.coords.direction_to(closest_enemy.coords).opposite
        for d in [flee_dir, flee_dir.rotate_cw, flee_dir.rotate_ccw]:
            if is_free(unit.coords + d):
                return Action.move(d)

    # Support / cluster with nearby friends when we have no adjacent enemies
    # If a nearby ally is currently engaged (has an adjacent enemy), move towards their enemy to assist them!
    fighting_allies = []
    for ally in allies:
        if ally.id != unit.id and unit.coords.distance_to(ally.coords) <= 6:
            ally_enemies = [e for e in enemies if ally.coords.distance_to(e.coords) == 1]
            if ally_enemies:
                fighting_allies.append((ally, ally_enemies))
    if fighting_allies:
        # Sort by distance to the fighting ally
        fighting_allies.sort(key=lambda x: unit.coords.distance_to(x[0].coords))
        target_ally, ally_enemies = fighting_allies[0]
        # Target the lowest health enemy of that ally
        target_enemy = min(ally_enemies, key=lambda e: e.health)
        assist_dir = unit.coords.direction_to(target_enemy.coords)
        for d in [assist_dir, assist_dir.rotate_cw, assist_dir.rotate_ccw]:
            if is_free(unit.coords + d):
                return Action.move(d)

    # If closest enemy is far (> 4), and we are far from friends, try to stay closer to other friends to group up
    if dist_to_closest > 4 and len(nearby_friends) <= 1:
        # find closest friend that actually has other friends or is closer to enemy
        active_friends = [f for f in allies if f.id != unit.id]
        if active_friends:
            closest_friend = min(active_friends, key=lambda f: unit.coords.distance_to(f.coords))
            if unit.coords.distance_to(closest_friend.coords) > 2:
                group_dir = unit.coords.direction_to(closest_friend.coords)
                for d in [group_dir, group_dir.rotate_cw, group_dir.rotate_ccw]:
                    if is_free(unit.coords + d):
                        return Action.move(d)

    # Prioritize moving towards closest enemy
    move_dir = unit.coords.direction_to(closest_enemy.coords)
    # Check if direct, rotating cw, rotating ccw moves are free.
    # To prevent being kited/stalled, if the path to the closest enemy is blocked, we can try to walk around it.
    for d in [move_dir, move_dir.rotate_cw, move_dir.rotate_ccw]:
        if is_free(unit.coords + d):
            return Action.move(d)
            
    return None
