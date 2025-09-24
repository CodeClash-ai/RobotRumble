# Coordinating bot: focus-fire on low-health enemies + improved micro
# Round 3 improvements:
# - Retreat when low HP and outnumbered nearby
# - Re-evaluate global target if a much weaker enemy appears
# - More robust movement/dir helpers

target_id = None


def robot(state, unit):
    """
    Team-coordinated robot with basic micro and retreat logic.
    - Global target_id chosen as the enemy with lowest health (tie-breaker: total distance).
    - If any adjacent enemies, attack the one with the lowest health.
    - If low HP and outnumbered nearby, try to retreat away from nearest enemy.
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

    # Basic stats helpers
    def hp_of(o):
        return getattr(o, "health", getattr(o, "hp", 0))

    def distance(a, b):
        try:
            return a.distance_to(b)
        except Exception:
            try:
                return a.walking_distance_to(b)
            except Exception:
                # fallback to Manhattan if coords expose x,y
                try:
                    return abs(a.x - b.x) + abs(a.y - b.y)
                except Exception:
                    return 9999

    def total_distance_for_team(enemy):
        s = 0
        for ally in allies:
            try:
                s += distance(ally.coords, enemy.coords)
            except Exception:
                s += 0
        return s

    # Validate or pick a global target
    try:
        if target_id:
            if not state.obj_by_id(target_id):
                target_id = None
    except Exception:
        target_id = None

    # Choose enemy with lowest health; tie-breaker: total distance from allies
    if enemies:
        def score_enemy(enemy):
            h = hp_of(enemy)
            td = total_distance_for_team(enemy)
            # primary: health, secondary: distance (smaller is better)
            return (h, td)

        try:
            best = min(enemies, key=score_enemy)
            # If we don't have a target, or the new best is meaningfully weaker, switch.
            if not target_id:
                target_id = best.id
            else:
                try:
                    current = state.obj_by_id(target_id)
                except Exception:
                    current = None
                if current is None:
                    target_id = best.id
                else:
                    # switch if best has much lower hp than current
                    if hp_of(best) + 2 < hp_of(current):
                        target_id = best.id
        except Exception:
            try:
                target_id = enemies[0].id
            except Exception:
                target_id = None

    # Micro: attack adjacent weakest enemy
    adjacents = []
    for e in enemies:
        d = distance(my_coords, e.coords)
        if d == 1:
            adjacents.append(e)

    # Low-HP retreat logic: if low HP and outnumbered, try to move away
    my_hp = hp_of(unit)
    # count nearby enemies/allies within 2 tiles
    nearby_enemy_count = 0
    nearby_ally_count = 0
    nearest_enemy = None
    nearest_enemy_dist = 9999
    for e in enemies:
        d = distance(my_coords, e.coords)
        if d <= 2:
            nearby_enemy_count += 1
        if d < nearest_enemy_dist:
            nearest_enemy_dist = d
            nearest_enemy = e
    for a in allies:
        if a.id == unit.id:
            continue
        try:
            if distance(my_coords, a.coords) <= 2:
                nearby_ally_count += 1
        except Exception:
            pass

    # If low HP and outnumbered (enemies nearby >= allies nearby + 1), try to retreat
    if my_hp <= 3 and nearby_enemy_count >= (nearby_ally_count + 1) and nearest_enemy is not None:
        # Try to move opposite the nearest enemy
        try:
            # compute direction from me to enemy then invert it
            dir_to_enemy = my_coords.direction_to(nearest_enemy.coords)
            away_dir = None
            try:
                away_dir = dir_to_enemy.rotate_cw().rotate_cw()
            except Exception:
                # fallback: map cardinal opposite
                try:
                    if dir_to_enemy == Direction.North:
                        away_dir = Direction.South
                    elif dir_to_enemy == Direction.South:
                        away_dir = Direction.North
                    elif dir_to_enemy == Direction.East:
                        away_dir = Direction.West
                    elif dir_to_enemy == Direction.West:
                        away_dir = Direction.East
                except Exception:
                    pass
            if away_dir is None:
                away_dir = Direction.North
            # try primary away, then other escape directions
            escape_order = [away_dir, Direction.North, Direction.East, Direction.South, Direction.West]
            move_action = try_dirs(escape_order)
            if move_action:
                return move_action
        except Exception:
            pass
        # if can't move, and there's an adjacent enemy, attack the weakest adjacent
        if adjacents:
            try:
                target = min(adjacents, key=hp_of)
                return Action.attack(my_coords.direction_to(target.coords))
            except Exception:
                try:
                    return Action.attack(Direction.East)
                except Exception:
                    return None

    if adjacents:
        # Attack weakest adjacent target (focus-fire)
        try:
            target = min(adjacents, key=hp_of)
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

