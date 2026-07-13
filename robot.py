from typing import *

# RobotRumble bot.
# KEY RULE: Winner is decided by UNIT COUNT alive at the end (not health).
#   UNIT_HEALTH=5, ATTACK_POWER=1. Grid 19x19 circle map. Attack range = adjacent (dist 1).
#   Every 10 turns, 4 new units spawn per team at spawn ring (spawn tiles cleared first).
# Strategy: focus-fire to secure KILLS, gang up when advantaged, avoid getting ganged,
#   retreat near-dead units to preserve unit count.

DIRECTIONS = [Direction.North, Direction.South, Direction.East, Direction.West]


def robot_enemies(state):
    return state.objs_by_team(state.other_team)


def robot_allies(state):
    return state.objs_by_team(state.our_team)


planned: Dict[Any, bool] = {}
focus_id: Optional[str] = None
enemy_set: set = set()
ally_set: set = set()


def init_turn(state: State) -> None:
    global planned, focus_id, enemy_set, ally_set
    planned = {}
    enemies = robot_enemies(state)
    allies = robot_allies(state)
    enemy_set = set((e.coords.x, e.coords.y) for e in enemies)
    ally_set = set((a.coords.x, a.coords.y) for a in allies)
    focus_id = None
    if enemies and allies:
        def score(e):
            total = min(a.coords.walking_distance_to(e.coords) for a in allies)
            return (e.health, total)
        focus_id = min(enemies, key=score).id


def in_bounds(c):
    return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE


def coord_free(state, c):
    if not in_bounds(c):
        return False
    if state.obj_by_coords(c) is not None:
        return False
    if planned.get((c.x, c.y)):
        return False
    return True


def adjacent_enemies(state, coords):
    res = []
    for d in DIRECTIONS:
        obj = state.obj_by_coords(coords + d)
        if obj is not None and obj.obj_type == ObjType.Unit and obj.team == state.other_team:
            res.append((d, obj))
    return res


def count_enemy_adj(coords):
    """How many enemy units are orthogonally adjacent to `coords`."""
    cnt = 0
    for d in DIRECTIONS:
        nc = coords + d
        if (nc.x, nc.y) in enemy_set:
            cnt += 1
    return cnt


def count_ally_adj(coords):
    cnt = 0
    for d in DIRECTIONS:
        nc = coords + d
        if (nc.x, nc.y) in ally_set:
            cnt += 1
    return cnt


def choose_move(state, unit, target_coords, avoid_gang=True):
    """Pick a move toward target, penalising tiles where we'd be ganged up on."""
    candidates = []
    for d in DIRECTIONS:
        nc = unit.coords + d
        if not coord_free(state, nc):
            continue
        dist = nc.walking_distance_to(target_coords)
        threat = count_enemy_adj(nc)
        candidates.append((dist, threat, d, nc))
    if not candidates:
        return None
    if avoid_gang:
        # Avoid tiles where 2+ enemies could hit us, unless it's the only way
        # to close distance and no safer option reduces distance.
        safe = [c for c in candidates if c[1] <= 1]
        pool = safe if safe else candidates
    else:
        pool = candidates
    # sort by distance to target, then by threat
    pool.sort(key=lambda t: (t[0], t[1]))
    dist, threat, d, nc = pool[0]
    planned[(nc.x, nc.y)] = True
    return Action.move(d)


def robot(state: State, unit: Obj) -> Optional[Action]:
    enemies = robot_enemies(state)
    if not enemies:
        return None

    adj = adjacent_enemies(state, unit.coords)

    # Retreat if very low health and can't secure a kill this turn.
    can_kill_now = any(e.health <= 1 for d, e in adj)
    if unit.health <= 2 and adj and not can_kill_now:
        # Flee away from the nearest adjacent enemy.
        nearest_adj = min(adj, key=lambda t: t[1].health)[1]
        away = nearest_adj.coords.direction_to(unit.coords)
        # try to move to a tile far from enemies
        best = None
        for d in DIRECTIONS:
            nc = unit.coords + d
            if not coord_free(state, nc):
                continue
            score = -count_enemy_adj(nc)
            if best is None or score > best[0]:
                best = (score, d, nc)
        if best is not None:
            planned[(best[2].x, best[2].y)] = True
            return Action.move(best[1])
        # cornered: attack the weakest
        return Action.attack(min(adj, key=lambda t: t[1].health)[0])

    if adj:
        # Attack the adjacent enemy we can most likely kill (lowest health),
        # preferring our focus target on ties.
        def akey(t):
            d, e = t
            return (e.health, 0 if e.id == focus_id else 1)
        adj.sort(key=akey)
        return Action.attack(adj[0][0])

    # No adjacent enemy: advance on the focus target (or a much closer enemy).
    target = state.obj_by_id(focus_id) if focus_id else None
    nearest = min(enemies, key=lambda e: unit.coords.walking_distance_to(e.coords))
    if target is None:
        target = nearest
    elif nearest.coords.walking_distance_to(unit.coords) + 4 < target.coords.walking_distance_to(unit.coords):
        target = nearest

    mv = choose_move(state, unit, target.coords, avoid_gang=True)
    if mv is not None:
        return mv
    return None
