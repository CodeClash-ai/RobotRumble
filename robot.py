# Improved RobotRumble bot with better strategy
# Strategy: Move towards center, attack enemies, coordinate with team

robot_state = {}

def robot(state, unit):
    """
    Enhanced bot strategy:
    1. Move towards center of map for better positioning
    2. Attack enemies when in range
    3. Avoid friendly fire
    4. Use terrain awareness
    """
    
    # Initialize unit state if needed
    if unit.id not in robot_state:
        robot_state[unit.id] = {'target_dir': None}
    
    # Check all 4 directions for enemies and allies
    directions = [Direction.North, Direction.South, Direction.East, Direction.West]
    
    # First priority: Attack enemies in range
    for direction in directions:
        target = state.obj_by_coords(unit.coords + direction)
        if target and hasattr(target, 'team') and target.team != state.our_team:
            return Action.attack(direction)
    
    # Second priority: Move strategically
    # Try to move towards center of map (assuming 19x19 grid)
    center_x, center_y = 9, 9
    dx = center_x - unit.coords.x
    dy = center_y - unit.coords.y
    
    # Determine best direction to move
    move_dir = None
    if abs(dx) > abs(dy):
        move_dir = Direction.East if dx > 0 else Direction.West
    else:
        move_dir = Direction.South if dy > 0 else Direction.North
    
    # Check if we can move in that direction
    target = state.obj_by_coords(unit.coords + move_dir)
    if not target:
        return Action.move(move_dir)
    elif target and hasattr(target, 'team') and target.team != state.our_team:
        return Action.attack(move_dir)
    
    # Try alternative directions if blocked
    for direction in directions:
        target = state.obj_by_coords(unit.coords + direction)
        if not target:
            return Action.move(direction)
    
    # If all else fails, stay put
    return None
