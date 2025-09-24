import random

def robot(state, unit):
    """
    Improved focus/retreat strategy:
    - If any enemy adjacent, attack the weakest adjacent enemy.
    - Otherwise consider all free cardinal moves and score them:
      - If low health or currently in high danger, prefer moves that reduce danger and increase distance to nearest enemy (retreat).
      - Otherwise prefer moves that reduce distance to nearest enemy and favor landing spots that let you attack low-health enemies next turn.
    - Avoid predicted dangerous tiles based on simple opponent pattern (move East on even turns, attack South on odd turns).
    - Avoid clustering with allies by adding an ally-proximity penalty.
    - Add a small random tie-breaker to reduce predictability.
    - If no enemies visible, move toward nearest spawn or East as fallback.
    """
    enemies = state.objs_by_team(state.other_team)
    allies = [a for a in state.objs_by_team(state.our_team) if a.id != unit.id]

    def in_bounds(c):
        return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE

    def is_free(c):
        return in_bounds(c) and state.obj_by_coords(c) is None

    def danger_at(coords):
        return sum(1 for e in enemies if coords.walking_distance_to(e.coords) <= 1)

    # Predict simple opponent pattern (if present)
    predicted_danger = set()
    try:
        if enemies:
            if state.turn % 2 == 0:
                for e in enemies:
                    p = e.coords + Direction.East
                    if in_bounds(p):
                        predicted_danger.add((p.x, p.y))
            else:
                for e in enemies:
                    p = e.coords + Direction.South
                    if in_bounds(p):
                        predicted_danger.add((p.x, p.y))
    except Exception:
        predicted_danger = set()

    # Combat: handle visible enemies
    if enemies:
        # Attack weakest adjacent enemy if any
        adjacent = [e for e in enemies if unit.coords.walking_distance_to(e.coords) <= 1]
        if adjacent:
            # Prefer lowest health, then lowest walking distance, then random tie-breaker
            weakest = min(adjacent, key=lambda e: ((e.health if e.health is not None else 9999),
                                                   unit.coords.walking_distance_to(e.coords),
                                                   random.random()))
            return Action.attack(unit.coords.direction_to(weakest.coords))

        # Build candidate moves (all free cardinal tiles)
        candidates = []
        for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
            nc = unit.coords + d
            if is_free(nc):
                candidates.append((d, nc))
        if not candidates:
            # Try to stay safe: look for any free adjacent spot even if diagonal-ish isn't available here,
            # otherwise fall back to a random cardinal move (may be blocked later by engine).
            for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
                nc = unit.coords + d
                if in_bounds(nc):
                    return Action.move(d)
            return Action.move(Direction.North)

        # Determine nearest enemy from current position
        def nearest_enemy_from(coords):
            return min(enemies, key=lambda e: coords.walking_distance_to(e.coords))

        current_danger = danger_at(unit.coords)
        low_health = (unit.health is not None and unit.health < 11)

        scored = []
        for d, nc in candidates:
            dng = danger_at(nc)
            nearest = nearest_enemy_from(nc)
            dist_after = nc.walking_distance_to(nearest.coords)
            # health of the nearest enemy (lower is better to focus)
            h_nearest = nearest.health if nearest.health is not None else 9999
            # how many enemies could we attack next turn from nc
            enemies_in_range = sum(1 for e in enemies if nc.walking_distance_to(e.coords) <= 1)
            # predicted danger penalty (made more severe)
            penalty = 1 if (nc.x, nc.y) in predicted_danger else 0
            penalty *= 100
            # ally proximity penalty to discourage bunching
            ally_penalty = 5 * sum(1 for a in allies if nc.walking_distance_to(a.coords) <= 1)
            # small randomness to break ties
            rnd = random.random()

            if low_health or current_danger >= 1:
                # Retreat: prefer no-penalty, lower danger, and larger distance to nearest enemy
                # Lexicographic ordering: big penalties first
                score = (penalty, ally_penalty, dng, -dist_after, -enemies_in_range, h_nearest, rnd)
            else:
                # Aggressive: prefer no-penalty, lower danger, closer to enemy, more enemies in range, lower health target
                attack_bonus = -20 if enemies_in_range > 0 else 0
                score = (penalty, ally_penalty, attack_bonus, dng, h_nearest, dist_after, -enemies_in_range, rnd)
            scored.append((score, d, nc))

        scored.sort(key=lambda x: x[0])
        _, best_dir, _ = scored[0]
        return Action.move(best_dir)

    # No enemies visible: move toward spawn if available
    spawn_coords = []
    try:
        spawn_coords = list(SPAWN_COORDS)
    except Exception:
        spawn_coords = []

    if spawn_coords:
        nearest_spawn = min(spawn_coords, key=lambda s: unit.coords.walking_distance_to(s))
        best = None
        for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
            nc = unit.coords + d
            if is_free(nc):
                penalty = 1 if (nc.x, nc.y) in predicted_danger else 0
                penalty *= 100
                dng = danger_at(nc)
                dist_after = nc.walking_distance_to(nearest_spawn)
                ally_penalty = 5 * sum(1 for a in allies if nc.walking_distance_to(a.coords) <= 1)
                rnd = random.random()
                score = (penalty, ally_penalty, dng, dist_after, rnd)
                if best is None or score < best[0]:
                    best = (score, d)
        if best:
            return Action.move(best[1])

    # Fallbacks: prefer East if safe, else center, else spread out
    east = unit.coords + Direction.East
    if is_free(east) and (east.x, east.y) not in predicted_danger:
        return Action.move(Direction.East)

    try:
        center = Coords(MAP_SIZE//2, MAP_SIZE//2)
    except Exception:
        center = None
    if center and unit.coords != center:
        dir_to = unit.coords.direction_to(center)
        nc = unit.coords + dir_to
        if is_free(nc) and (nc.x, nc.y) not in predicted_danger:
            return Action.move(dir_to)

    # Spread out
    free = []
    for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
        nc = unit.coords + d
        if is_free(nc):
            free.append((danger_at(nc), d))
    if free:
        free.sort(key=lambda x: x[0])
        return Action.move(free[0][1])

    return Action.move(Direction.North)
