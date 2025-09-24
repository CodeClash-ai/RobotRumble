import random

def robot(state, unit):
    """
    Aggressive spawn-contesting bot:
    - Target weakest then nearest; attack in range.
    - When moving to engage enemies, prefer moves that get into attack range next turn,
      then lower danger, then shorter distance.
    - When no enemies visible, seek the nearest SPAWN_COORD (if available) by choosing a free
      cardinal move that reduces walking_distance to that spawn; tiebreak by lower danger.
    - Fallbacks: prefer moving East, then center, then spread out.
    """
    enemies = state.objs_by_team(state.other_team)
    allies = [a for a in state.objs_by_team(state.our_team) if a.id != unit.id]

    def in_bounds(c):
        return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE

    def is_free(c):
        return in_bounds(c) and state.obj_by_coords(c) is None

    def danger_at(coords):
        return sum(1 for e in enemies if coords.walking_distance_to(e.coords) <= 1)

    # Combat behavior
    if enemies:
        target = min(enemies, key=lambda e: ((e.health if e.health is not None else 9999),
                                              unit.coords.walking_distance_to(e.coords)))
        dist = unit.coords.walking_distance_to(target.coords)
        dir_to = unit.coords.direction_to(target.coords)

        if dist <= 1:
            return Action.attack(dir_to)

        prefs = [dir_to, dir_to.rotate_cw(), dir_to.rotate_ccw(), dir_to.opposite]
        candidates = []
        for d in prefs:
            nc = unit.coords + d
            if is_free(nc):
                candidates.append((d, nc))
        if not candidates:
            for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
                nc = unit.coords + d
                if is_free(nc):
                    candidates.append((d, nc))

        if candidates:
            low_health = (unit.health is not None and unit.health < 8)
            scored = []
            for d, nc in candidates:
                dng = danger_at(nc)
                dist_after = nc.walking_distance_to(target.coords)
                in_range_flag = 0 if dist_after <= 1 else 1
                score = (in_range_flag, dng, dist_after)
                scored.append((score, d, nc))
            scored.sort(key=lambda x: x[0])
            if low_health:
                for score, d, nc in scored:
                    if score[1] == 0:
                        return Action.move(d)
                _, best_dir, _ = scored[0]
                return Action.move(best_dir)
            _, best_dir, _ = scored[0]
            return Action.move(best_dir)
        return Action.attack(dir_to)

    # No enemies visible: try to move toward nearest spawn
    spawn_coords = []
    try:
        # SPAWN_COORDS is provided by the environment in many maps
        spawn_coords = list(SPAWN_COORDS)
    except Exception:
        spawn_coords = []

    if spawn_coords:
        # find nearest spawn
        nearest = min(spawn_coords, key=lambda s: unit.coords.walking_distance_to(s))
        # if already on spawn, try to stay / move off to contest neighbors (pick East if possible)
        # otherwise pick a free cardinal move that reduces distance to nearest
        best_moves = []
        for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
            nc = unit.coords + d
            if is_free(nc):
                dist_after = nc.walking_distance_to(nearest)
                dng = danger_at(nc)
                best_moves.append(((dist_after, dng), d))
        if best_moves:
            best_moves.sort(key=lambda x: x[0])  # minimize distance then danger
            return Action.move(best_moves[0][1])
    # If no spawn info or blocked, prefer moving East to contest expansion
    east_tile = unit.coords + Direction.East
    if is_free(east_tile):
        return Action.move(Direction.East)

    # Next preference: move toward center
    try:
        center = Coords(MAP_SIZE//2, MAP_SIZE//2)
    except Exception:
        center = None
    if center and unit.coords != center:
        dir_to = unit.coords.direction_to(center)
        nc = unit.coords + dir_to
        if is_free(nc):
            return Action.move(dir_to)
        for d in [dir_to.rotate_cw(), dir_to.rotate_ccw(), dir_to.opposite]:
            nc = unit.coords + d
            if is_free(nc):
                return Action.move(d)

    # Fallback: spread out among free tiles (least allied neighbors)
    dirs = [Direction.North, Direction.East, Direction.South, Direction.West]
    free = []
    for d in dirs:
        nc = unit.coords + d
        if is_free(nc):
            ally_neighbors = sum(1 for a in allies if nc.walking_distance_to(a.coords) <= 1)
            free.append((ally_neighbors, d))
    if free:
        free.sort(key=lambda x: x[0])
        best_count = free[0][0]
        best_choices = [d for c, d in free if c == best_count]
        return Action.move(random.choice(best_choices))

    return Action.move(Direction.North)
