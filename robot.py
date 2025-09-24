def robot(state, unit):
    """
    Improved bot:
    - If an enemy is adjacent (walking distance == 1), attack toward them.
    - Otherwise, move toward the nearest known enemy, but avoid moving into occupied tiles.
      If the direct tile is occupied, try rotating clockwise, then counter-clockwise.
    - If no enemies are known, move off spawn (North) if on spawn, else move East (or alternatives if blocked).
    """
    my_coords = unit.coords

    # Helper to check if a coords is free
    def is_free(coords):
        try:
            return state.obj_by_coords(coords) is None
        except Exception:
            # Fallback to id lookup
            try:
                return state.id_by_coords(coords) is None
            except Exception:
                return True

    # Try a list of directions and return the first valid move Action
    def try_dirs(dir_list):
        for d in dir_list:
            try:
                target = my_coords + d
            except Exception:
                # If addition with Direction not supported, use to_coords
                try:
                    tc = d.to_coords()
                    target = type(my_coords)(my_coords.x + tc[0], my_coords.y + tc[1])
                except Exception:
                    target = None
            if target is None or is_free(target):
                return Action.move(d)
        return None

    # Get enemy units
    enemies = state.objs_by_team(state.other_team)

    # Track nearest enemy
    nearest = None
    nearest_dist = None

    for e in enemies:
        try:
            dist = my_coords.walking_distance_to(e.coords)
        except Exception:
            dist = my_coords.distance_to(e.coords)

        # Attack immediately if adjacent
        if dist == 1:
            return Action.attack(my_coords.direction_to(e.coords))

        if nearest is None or dist < nearest_dist:
            nearest = e
            nearest_dist = dist

    # Move toward nearest enemy if we have one
    if nearest is not None:
        try:
            preferred = my_coords.direction_to(nearest.coords)
        except Exception:
            preferred = None

        if preferred is not None:
            # Try preferred, then rotate cw, then ccw
            dirs = [preferred]
            try:
                dirs.append(preferred.rotate_cw())
                dirs.append(preferred.rotate_ccw())
            except Exception:
                pass

            move_action = try_dirs(dirs)
            if move_action is not None:
                return move_action

            # If all blocked, fall back to cardinal tries
        # Fallback: try all cardinal directions
        all_dirs = [Direction.North, Direction.East, Direction.South, Direction.West]
        move_action = try_dirs(all_dirs)
        if move_action is not None:
            return move_action

    # No enemies known: move off spawn if on spawn, else move East
    try:
        if my_coords.is_spawn():
            # Prefer North, then East
            move_action = try_dirs([Direction.North, Direction.East])
            if move_action:
                return move_action
    except Exception:
        pass

    # Final fallbacks
    move_action = try_dirs([Direction.East, Direction.North, Direction.South, Direction.West])
    if move_action:
        return move_action

    # As a last resort, attack East (should rarely happen)
    return Action.attack(Direction.East)
