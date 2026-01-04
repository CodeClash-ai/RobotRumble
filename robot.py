robot_state = {}

def robot(state, unit):
    # Find all enemies
    enemies = state.objs_by_team(state.other_team)
    
    if not enemies:
        # No enemies left, just pass
        return None
    
    # Find the closest enemy to this unit
    closest_enemy = min(enemies, key=lambda e: e.coords.distance_to(unit.coords))
    
    # Get direction to the closest enemy
    direction = unit.coords.direction_to(closest_enemy.coords)
    
    # If we're adjacent to the enemy, attack
    if unit.coords.distance_to(closest_enemy.coords) == 1:
        return Action.attack(direction)
    else:
        # Otherwise, move toward the enemy
        return Action.move(direction)
