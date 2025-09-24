# Coordinating bot: focus-fire on low-health enemies + improved micro
target_id = None

def robot(state, unit):
    """
    Team-coordinated robot:
    - Global target_id chosen as the enemy with lowest health (tie-breaker: total distance).
    - If any adjacent enemies, attack the one with the lowest health.
    - Otherwise, move toward the global target (try rotate cw/ccw if blocked).
    - If no enemies known, move off spawn (North) or try East.
    """
    global target_id
    my_coords = unit.coords

    # Helpers
    def is_free(coords):
        try:
            return state.obj_by_coords(coords) is None
        except Exception:
            try:
                return state.id_by_coords(coords) is None
            except Exception:
                return True

    def try_dirs(dir_list):
        for d in dir_list:
            try:
                target = my_coords + d
            except Exception:
                try:
                    tc = d.to_coords()
                    target = type(my_coords)(my_coords.x + tc[0], my_coords.y + tc[1])
                except Exception:
                    target = None
            if target is not None and is_free(target):
                return Action.move(d)
        return None

    # Gather units
    try:
        allies = state.objs_by_team(state.our_team)
    except Exception:
        allies = []
    try:
        enemies = state.objs_by_team(state.other_team)
    except Exception:
        enemies = []

    # Validate or pick a global target
    try:
        if target_id:
            if not state.obj_by_id(target_id):
                target_id = None
    except Exception:
        target_id = None

    def total_distance_for_team(enemy):
        s = 0
        for ally in allies:
            try:
                s += ally.coords.distance_to(enemy.coords)
            except Exception:
                s += 0
        return s

    if not target_id and enemies:
        # Choose enemy with lowest health; tie-breaker: total distance from allies
        def health_then_distance(enemy):
            h = getattr(enemy, "health", getattr(enemy, "hp", 0))
            td = total_distance_for_team(enemy)
            return (h, td)
        try:
            closest_enemy_for_team = min(enemies, key=health_then_distance)
            target_id = closest_enemy_for_team.id
        except Exception:
            try:
                target_id = enemies[0].id
            except Exception:
                target_id = None

    # Micro: attack adjacent weakest enemy
    adjacents = []
    for e in enemies:
        try:
            d = my_coords.distance_to(e.coords)
        except Exception:
            try:
                d = my_coords.walking_distance_to(e.coords)
            except Exception:
                d = None
        if d == 1:
            adjacents.append(e)

    if adjacents:
        def hp_val(o):
            return getattr(o, "health", getattr(o, "hp", 0))
        target = min(adjacents, key=hp_val)
        try:
            return Action.attack(my_coords.direction_to(target.coords))
        except Exception:
            try:
                return Action.attack(Direction.East)
            except Exception:
                return None

    # Move toward global target if available
    target = None
    if target_id:
        try:
            target = state.obj_by_id(target_id)
        except Exception:
            target = None

    if target:
        try:
            preferred = my_coords.direction_to(target.coords)
        except Exception:
            preferred = None

        if preferred is not None:
            dirs = [preferred]
            try:
                dirs.append(preferred.rotate_cw())
                dirs.append(preferred.rotate_ccw())
            except Exception:
                pass
            move_action = try_dirs(dirs)
            if move_action:
                return move_action

        # fallback to cardinals
        all_dirs = [Direction.North, Direction.East, Direction.South, Direction.West]
        move_action = try_dirs(all_dirs)
        if move_action:
            return move_action

    # No target/enemies: move off spawn or head East
    try:
        is_spawn = getattr(my_coords, "is_spawn", lambda: False)
        if is_spawn():
            move_action = try_dirs([Direction.North, Direction.East])
            if move_action:
                return move_action
    except Exception:
        pass

    move_action = try_dirs([Direction.East, Direction.North, Direction.South, Direction.West])
    if move_action:
        return move_action

    try:
        return Action.attack(Direction.East)
    except Exception:
        return None
