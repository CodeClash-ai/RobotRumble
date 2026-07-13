from typing import *

# RobotRumble bot.
# KEY RULE: Winner is decided by UNIT COUNT alive at the end (not health).
#   UNIT_HEALTH=5, ATTACK_POWER=1. Grid 19x19 circle map. Attack range = adjacent (dist 1).
#   Every 10 turns, 4 new units spawn per team at spawn ring (spawn tiles cleared first).
# Strategy: focus-fire to secure KILLS, gang up when locally advantaged, avoid getting
#   ganged, cluster to fight cohesively, retreat near-dead units to preserve unit count.

DIRECTIONS = [Direction.North, Direction.South, Direction.East, Direction.West]

planned: Dict[Any, bool] = {}
focus_id: Optional[str] = None
enemy_set: set = set()
ally_set: set = set()
ally_centroid = None
n_allies = 0
n_enemies = 0
next_turn_spawn = False


def robot_enemies(state):
    return state.objs_by_team(state.other_team)


def robot_allies(state):
    return state.objs_by_team(state.our_team)


def init_turn(state: State) -> None:
    global planned, focus_id, enemy_set, ally_set, ally_centroid, n_allies, n_enemies, next_turn_spawn
    planned = {}
    next_turn_spawn = ((state.turn + 1) % 10) == 0
    enemies = robot_enemies(state)
    allies = robot_allies(state)
    enemy_set = set((e.coords.x, e.coords.y) for e in enemies)
    ally_set = set((a.coords.x, a.coords.y) for a in allies)
    n_allies = len(allies)
    n_enemies = len(enemies)
    if allies:
        sx = sum(a.coords.x for a in allies)
        sy = sum(a.coords.y for a in allies)
        ally_centroid = Coords(sx // len(allies), sy // len(allies))
    else:
        ally_centroid = None
    focus_id = None
    if enemies and allies:
        # Focus the enemy that is lowest-health and nearest our cluster.
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
    if next_turn_spawn and c.is_spawn():
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
    """Pick a move toward target, penalising tiles where we'd be ganged up on
    (more adjacent enemies than adjacent allies)."""
    candidates = []
    for d in DIRECTIONS:
        nc = unit.coords + d
        if not coord_free(state, nc):
            continue
        dist = nc.walking_distance_to(target_coords)
        threat = count_enemy_adj(nc)
        support = count_ally_adj(nc)
        # net exposure: how outnumbered we'd be at nc
        net = threat - support
        cdist = nc.walking_distance_to(ally_centroid) if ally_centroid is not None else 0
        candidates.append((dist, net, threat, cdist, d, nc))
    if not candidates:
        return None
    if avoid_gang:
        # Prefer tiles where we won't be outnumbered by adjacent enemies.
        safe = [c for c in candidates if c[1] <= 0]
        pool = safe if safe else candidates
    else:
        pool = candidates
    pool.sort(key=lambda t: (t[0], t[3], t[1], t[2]))
    dist, net, threat, cdist, d, nc = pool[0]
    planned[(nc.x, nc.y)] = True
    return Action.move(d)


def choose_move_cautious(state, unit, target_coords):
    """Advance toward target. Never step adjacent to an enemy unless we'll have more
    adjacent allies than enemies there (net<0). Among safe tiles, get closer to target
    and stay near ally centroid (cohesion). If the only closer tiles are unsafe, prefer
    to hold near the pack instead of walking into a losing exchange."""
    candidates = []
    for d in DIRECTIONS:
        nc = unit.coords + d
        if not coord_free(state, nc):
            continue
        dist = nc.walking_distance_to(target_coords)
        threat = count_enemy_adj(nc)
        support = count_ally_adj(nc)
        net = threat - support
        cdist = nc.walking_distance_to(ally_centroid) if ally_centroid is not None else 0
        candidates.append((dist, threat, net, cdist, d, nc))
    if not candidates:
        return None
    cur_dist = unit.coords.walking_distance_to(target_coords)
    # Safe = no adjacent enemy, OR adjacent enemies but with net support (net<0).
    safe = [c for c in candidates if c[1] == 0 or c[2] < 0]
    pool = safe if safe else candidates
    # Prefer: closer to target, then near ally centroid (cluster), then less threat.
    pool.sort(key=lambda t: (t[0], t[3], t[2], t[1]))
    best = pool[0]
    # If our best safe move doesn't actually get us closer AND we're already clustered,
    # it's fine to hold (return the move anyway to keep shuffling toward cohesion).
    dist, threat, net, cdist, d, nc = best
    planned[(nc.x, nc.y)] = True
    return Action.move(d)


def robot(state: State, unit: Obj) -> Optional[Action]:
    enemies = robot_enemies(state)
    if not enemies:
        return None

    # Emergency: if we're standing on a spawn tile and next turn is a spawn tick,
    # evacuate now or we die (units on spawn tiles are cleared at spawn time).
    if next_turn_spawn and unit.coords.is_spawn():
        best = None
        for d in DIRECTIONS:
            nc = unit.coords + d
            if not in_bounds(nc):
                continue
            if nc.is_spawn():
                continue
            if state.obj_by_coords(nc) is not None or planned.get((nc.x, nc.y)):
                continue
            # Prefer safe tiles (fewer adjacent enemies, more adjacent allies)
            score = -count_enemy_adj(nc) + count_ally_adj(nc)
            if best is None or score > best[0]:
                best = (score, d, nc)
        if best is not None:
            planned[(best[2].x, best[2].y)] = True
            return Action.move(best[1])
        # Can't reach a non-spawn tile; at least attack an adjacent enemy if any.
        adj0 = adjacent_enemies(state, unit.coords)
        if adj0:
            return Action.attack(min(adj0, key=lambda t: t[1].health)[0])

    adj = adjacent_enemies(state, unit.coords)

    # Retreat if very low health and can't secure a kill this turn.
    can_kill_now = any(e.health <= 1 for d, e in adj)
    n_adj_enemy = len(adj)
    n_adj_ally = count_ally_adj(unit.coords)
    outnumbered_here = n_adj_enemy > n_adj_ally + 1
    should_retreat = (unit.health <= 2) or (unit.health <= 3 and outnumbered_here)
    if should_retreat and adj and not can_kill_now:
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
        return Action.attack(min(adj, key=lambda t: t[1].health)[0])

    if adj:
        # Attack the adjacent enemy we can most likely kill (lowest health),
        # preferring our focus target on ties.
        def akey(t):
            d, e = t
            return (e.health, 0 if e.id == focus_id else 1)
        adj.sort(key=akey)
        return Action.attack(adj[0][0])

    # No adjacent enemy. Advance toward the focus target, but ONLY move onto a tile
    # adjacent to an enemy if we'll have local support there (strict). Otherwise close
    # in cautiously while staying near the pack (cohesion), so we engage the enemy blob
    # only where we outnumber it locally.
    target = state.obj_by_id(focus_id) if focus_id else None
    nearest = min(enemies, key=lambda e: unit.coords.walking_distance_to(e.coords))
    if target is None:
        target = nearest
    elif nearest.coords.walking_distance_to(unit.coords) + 4 < target.coords.walking_distance_to(unit.coords):
        target = nearest

    mv = choose_move_cautious(state, unit, target.coords)
    if mv is not None:
        return mv
    return None
