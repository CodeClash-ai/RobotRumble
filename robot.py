from rumblelib import *

# Global variables to track our strategy
FORMATION_COMPLETE = False
FORMATION_LINE_Y = 7  # The y-coordinate where we'll form our line
ASSIGNED_POSITIONS = {}  # Maps unit IDs to their assigned x positions in the line

def init_turn(state):
    global FORMATION_COMPLETE, ASSIGNED_POSITIONS
    
    # Check if our formation is complete
    our_units = state.objs_by_team(state.our_team)
    
    # If we have no units or very few, reset formation status
    if len(our_units) <= 2:
        FORMATION_COMPLETE = False
        ASSIGNED_POSITIONS = {}
    
    # Assign positions to new units that don't have assignments yet
    if not FORMATION_COMPLETE:
        existing_positions = set(ASSIGNED_POSITIONS.values())
        for unit in our_units:
            if unit.id not in ASSIGNED_POSITIONS:
                # Find an unassigned x position
                for x in range(2, 17):  # Avoid the edges of the map
                    if x not in existing_positions:
                        ASSIGNED_POSITIONS[unit.id] = x
                        existing_positions.add(x)
                        break
        
        # Check if all units are in position
        all_in_position = True
        for unit in our_units:
            if unit.id in ASSIGNED_POSITIONS:
                target_coords = Coords(ASSIGNED_POSITIONS[unit.id], FORMATION_LINE_Y)
                if unit.coords.x != target_coords.x or unit.coords.y != target_coords.y:
                    all_in_position = False
                    break
        
        FORMATION_COMPLETE = all_in_position and len(our_units) >= 4

def robot(state, unit):
    # Get out of spawn area first
    if unit.coords.is_spawn():
        # Move away from spawn
        if unit.coords.y < 5:
            return Action.move(Direction.South)
        else:
            return Action.move(Direction.East)
    
    # If we're not in formation yet, get into formation
    if not FORMATION_COMPLETE:
        if unit.id in ASSIGNED_POSITIONS:
            target_x = ASSIGNED_POSITIONS[unit.id]
            target_y = FORMATION_LINE_Y
            
            # Move to assigned position
            if unit.coords.x < target_x:
                return Action.move(Direction.East)
            elif unit.coords.x > target_x:
                return Action.move(Direction.West)
            elif unit.coords.y < target_y:
                return Action.move(Direction.South)
            elif unit.coords.y > target_y:
                return Action.move(Direction.North)
        else:
            # No assignment yet, move toward center
            return Action.move(Direction.East)
    
    # Formation is complete, start the victory march!
    # Look for enemies
    enemy_units = state.objs_by_team(state.other_team)
    
    # If there's an enemy adjacent, attack it
    for direction in [Direction.North, Direction.East, Direction.South, Direction.West]:
        target_coords = unit.coords + direction
        target_id = state.id_by_coords(target_coords)
        if target_id:
            target = state.obj_by_id(target_id)
            if target and target.team == state.other_team:
                return Action.attack(direction)
    
    # No adjacent enemies, advance toward enemy territory
    # Find closest enemy
    closest_enemy = None
    min_distance = float('inf')
    
    for enemy in enemy_units:
        distance = unit.coords.walking_distance_to(enemy.coords)
        if distance < min_distance:
            min_distance = distance
            closest_enemy = enemy
    
    # March toward closest enemy, maintaining rough formation
    if closest_enemy:
        # Try to keep the same x-position during the march
        if abs(unit.coords.x - ASSIGNED_POSITIONS[unit.id]) > 2:
            # Too far from assigned column, move back toward it
            if unit.coords.x < ASSIGNED_POSITIONS[unit.id]:
                return Action.move(Direction.East)
            else:
                return Action.move(Direction.West)
        
        # Otherwise, march forward (generally northward since enemies spawn at the top)
        if unit.coords.y > closest_enemy.coords.y:
            return Action.move(Direction.North)
        elif unit.coords.x < closest_enemy.coords.x:
            return Action.move(Direction.East)
        elif unit.coords.x > closest_enemy.coords.x:
            return Action.move(Direction.West)
        else:
            return Action.move(Direction.South)
    
    # Default: march north if no enemies found
    return Action.move(Direction.North)

