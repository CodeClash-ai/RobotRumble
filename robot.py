# Team gpt-5-5 RobotRumble bot, round 1.
# Strategy: leave spawn, converge on the most vulnerable enemy, and focus fire.
# This intentionally avoids the starter quadrant logic, which can stalemate forever
# when mirrored armies begin in different quadrants.

ALL_DIRS = [Direction.North, Direction.East, Direction.South, Direction.West]

# Per-turn shared state (reset in init_turn).
turn_cache = {
    "target_id": None,
    "reserved": set(),
    "planned_attack": {},
}

# Small persistent memory to reduce back-and-forth shuffling.
robot_memory = {}


def _key(c):
    return (c.x, c.y)


def _in_bounds(c):
    return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE


def _obj_team(obj):
    # Terrain has no team in the stdlib.
    return getattr(obj, "team", None)


def _is_empty_legal(state, c):
    return _in_bounds(c) and state.obj_by_coords(c) is None


def _adjacent_enemies(state, unit):
    out = []
    for d in ALL_DIRS:
        c = unit.coords + d
        obj = state.obj_by_coords(c)
        if obj and _obj_team(obj) == state.other_team:
            out.append((d, obj))
    return out


def _allied_neighbors(state, coords):
    n = 0
    for d in ALL_DIRS:
        obj = state.obj_by_coords(coords + d)
        if obj and _obj_team(obj) == state.our_team:
            n += 1
    return n


def init_turn(state):
    """Pick one army-wide target each turn and clear per-turn reservations."""
    global turn_cache
    turn_cache["reserved"] = set()
    turn_cache["planned_attack"] = {}

    allies = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)
    if not enemies:
        turn_cache["target_id"] = None
        return

    # Prefer enemies already in contact, low-health enemies, then enemies near our army.
    def score(enemy):
        adjacent = _allied_neighbors(state, enemy.coords)
        total_walk = 0
        for ally in allies:
            total_walk += ally.coords.walking_distance_to(enemy.coords)
        # Lower is better.  A large adjacent bonus prevents target switching mid-fight.
        return total_walk + enemy.health * 4 - adjacent * 18

    turn_cache["target_id"] = min(enemies, key=score).id


def _choose_step(state, unit, target):
    """Return a good movement direction toward target, or None if boxed in."""
    direct = unit.coords.direction_to(target.coords)

    # Consider all directions.  Sorting by resulting walking distance gives robust
    # pathing around allies/walls; slight primary-direction bias keeps advances direct.
    candidates = []
    for d in ALL_DIRS:
        dest = unit.coords + d
        dist = dest.walking_distance_to(target.coords)
        bias = 0 if d == direct else (1 if d == direct.rotate_cw or d == direct.rotate_ccw else 3)
        candidates.append((dist, bias, d, dest))
    candidates.sort(key=lambda x: (x[0], x[1]))

    mem = robot_memory.setdefault(unit.id, {})
    last = mem.get("last")

    # On turns just before respawn, do not finish the turn on a spawn square: units
    # on spawn are cleared at the beginning of turns 11,21,... before new spawns.
    avoid_spawn = (state.turn % 10 == 0)

    fallback = None
    for _, _, d, dest in candidates:
        if not _is_empty_legal(state, dest):
            continue
        if _key(dest) in turn_cache["reserved"]:
            continue
        if avoid_spawn and dest.is_spawn():
            continue
        if last is not None and _key(dest) == last:
            fallback = d
            continue
        turn_cache["reserved"].add(_key(dest))
        mem["last"] = _key(unit.coords)
        return d

    # If all good moves merely reverse the last step, take the best such move rather
    # than freeze.  Freezing on spawn/border is usually worse than oscillation.
    if fallback is not None:
        dest = unit.coords + fallback
        turn_cache["reserved"].add(_key(dest))
        mem["last"] = _key(unit.coords)
        return fallback
    mem["last"] = _key(unit.coords)
    return None


def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    if not enemies:
        return None

    # 1. If adjacent to enemies, focus the lowest-health / most-surrounded one.
    adjacent = _adjacent_enemies(state, unit)
    if adjacent:
        d, enemy = min(adjacent, key=lambda de: (de[1].health, -_allied_neighbors(state, de[1].coords)))
        return Action.attack(d)

    # 2. Otherwise advance on the army-wide target (fall back to personal nearest).
    target = state.obj_by_id(turn_cache.get("target_id"))
    if target is None:
        target = min(enemies, key=lambda e: unit.coords.walking_distance_to(e.coords) + e.health * 2)

    step = _choose_step(state, unit, target)
    if step is not None:
        return Action.move(step)

    # 3. Boxed in by allies: attack toward the target to punish enemies that step in.
    return Action.attack(unit.coords.direction_to(target.coords))
