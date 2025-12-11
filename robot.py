# Strong, spawn-aware, focus-firing agent

# -------------- Globals (initialized in init_turn) --------------
TURN = 0
NEXT_TURN_SPAWN = False       # True if next turn is a spawn turn (clear + spawn)
SPAWN_TURN_NOW = False        # True if this very turn is a spawn turn (for info only)
ALLIES = []
ENEMIES = []
ALLY_BY_COORD = {}
ENEMY_BY_COORD = {}
OCCUPIED = {}                 # coords -> Obj (ally or enemy)
RESERVED = set()              # coords reserved this turn by our allies
ID_PRIORITY = {}              # unit.id -> numeric priority for tie-breaking
SPAWN_RING = set()            # tiles adjacent to any spawn tile (not spawn tiles themselves)

# Tunables
INFL_ENEMY_THREAT = 3
INFL_ALLY_SUPPORT = 2
DIST_WEIGHT = 1.0
SPAWN_STEP_ON_PENALTY = 10     # mild penalty during safe windows
SPAWN_DEATH_PENALTY = 10_000   # huge penalty if stepping onto spawn the turn before a spawn tick
STAY_DANGER_WEIGHT = 2
RETREAT_IF_OUTNUMBERED = True
OUTNUMBER_RADIUS = 1           # 3x3 neighborhood
TRY_SPAWN_RING_CAMPING = True

# Helper: robust debug
def dbg(unit, key, val):
    try:
        debug.inspect(f"{unit.id}:{key}", val)
    except Exception:
        pass

def in_bounds(c: Coords) -> bool:
    return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE

def neighbors4(c: Coords):
    for d in (Direction.North, Direction.South, Direction.East, Direction.West):
        n = c + d
        if in_bounds(n):
            yield d, n

def is_free_tile(c: Coords) -> bool:
    # Free if no unit currently occupies and nobody reserved it
    return (c not in OCCUPIED) and (c not in RESERVED)

def enemy_adjacent_count(c: Coords) -> int:
    # How many enemies could attack a unit on c (i.e., enemies adjacent to c)
    cnt = 0
    for d, n in neighbors4(c):
        if n in ENEMY_BY_COORD:
            cnt += 1
    return cnt

def ally_adjacent_count(c: Coords) -> int:
    cnt = 0
    for d, n in neighbors4(c):
        if n in ALLY_BY_COORD:
            cnt += 1
    return cnt

def local_counts(center: Coords, radius: int = 1):
    # Count allies/enemies in a (2r+1)x(2r+1) box centered at center using walking distance
    # We restrict to cells within Manhattan distance <= radius
    a = 0
    e = 0
    for obj in ALLIES:
        if obj.coords.walking_distance_to(center) <= radius:
            a += 1
    for obj in ENEMIES:
        if obj.coords.walking_distance_to(center) <= radius:
            e += 1
    return a, e

def id_priority_numeric(s: str) -> int:
    # Favor numeric suffix if present (common in engines),
    # else a stable hash-ish fallback
    num = 0
    mul = 1
    for ch in reversed(s):
        if ch.isdigit():
            num += mul * int(ch)
            mul *= 10
        else:
            break
    if num != 0:
        return num
    # Fallback
    return (sum(ord(c) for c in s) * 2654435761) & 0xFFFFFFFF

def spawn_penalty_for_tile(c: Coords) -> int:
    if not c.is_spawn():
        return 0
    # Standing on a spawn tile one turn before spawn tick means death on next tick.
    if NEXT_TURN_SPAWN:
        return SPAWN_DEATH_PENALTY
    # Otherwise discourage idling on spawn tiles
    return SPAWN_STEP_ON_PENALTY

def score_tile_for_move(unit: Obj, target: Obj | None, dest: Coords) -> float:
    # Hard reject tiles that are occupied or reserved
    if dest in OCCUPIED or dest in RESERVED:
        return -1e9

    # Distance component: prefer tiles that reduce walking distance to target
    dist_score = 0.0
    if target is not None:
        # Use negative distance as "good" (lower is better)
        dist = dest.walking_distance_to(target.coords)
        dist_score = -DIST_WEIGHT * float(dist)

    # Safety via influence: fewer enemy adjacents and more ally adjacents
    enemy_threat = enemy_adjacent_count(dest)
    ally_support = ally_adjacent_count(dest)
    safety_score = -(INFL_ENEMY_THREAT * enemy_threat) + (INFL_ALLY_SUPPORT * ally_support)

    # Spawn hazard
    spawn_pen = spawn_penalty_for_tile(dest)

    return dist_score + safety_score - float(spawn_pen)

def choose_attack_direction(unit: Obj):
    # Among adjacent enemies, choose the weakest; tiebreak by being on spawn tile (so they can't safely hold it),
    # then by having fewer allies around them (easier to finish).
    best = None
    best_score = None
    best_dir = None
    for d, n in neighbors4(unit.coords):
        enemy = ENEMY_BY_COORD.get(n)
        if enemy is None:
            continue
        # Lower health -> higher priority
        h = enemy.health if enemy.health is not None else 1_000_000
        # prefer enemies on spawn tiles (we can punish their mistake) slightly
        on_spawn_bonus = 1 if n.is_spawn() else 0
        # fewer allies around enemy -> easier to isolate
        enemy_ally_support = ally_adjacent_count(n)
        score = (-10 * h) + (2 * on_spawn_bonus) - enemy_ally_support
        if best is None or score > best_score:
            best = enemy
            best_score = score
            best_dir = d
    return best_dir

def pick_target(unit: Obj) -> Obj | None:
    # Choose a target: prefer nearby enemies and those that are locally outnumbered by our side
    # Score = proximity + vulnerability + low health
    best = None
    best_score = None
    for enemy in ENEMIES:
        # closeness
        d = unit.coords.walking_distance_to(enemy.coords)
        # local outnumbering at enemy tile
        a, e = local_counts(enemy.coords, radius=1)
        # Vulnerable if we outnumber around them
        vuln = (a - e)
        # health
        h = enemy.health if enemy.health is not None else 1000
        score = (-2.0 * d) + (3.0 * vuln) + (-0.5 * h)
        # Bias: enemies on or adjacent to spawn tiles are juicy immediately after spawn
        if enemy.coords.is_spawn():
            score += 1.5
        else:
            # Adjacent to spawn ring? Slight bonus near spawns
            for _, nn in neighbors4(enemy.coords):
                if nn in SPAWN_RING:
                    score += 0.5
                    break
        if (best is None) or (score > best_score):
            best = enemy
            best_score = score
    return best

def leave_spawn_now(unit: Obj) -> Action | None:
    # If we're on a spawn tile and next turn is a spawn, we must evacuate or die.
    if not unit.coords.is_spawn():
        return None
    # Try any non-spawn free neighbor that reduces danger
    best_dir = None
    best_score = None
    for d, n in neighbors4(unit.coords):
        if not in_bounds(n) or n.is_spawn():
            continue
        if not is_free_tile(n):
            continue
        # Prefer safer tiles
        score = -5 * enemy_adjacent_count(n) + 3 * ally_adjacent_count(n)
        # Also prefer spawn ring if we want to farm next turn
        if TRY_SPAWN_RING_CAMPING and (n in SPAWN_RING):
            score += 1.0
        if best_dir is None or score > best_score:
            best_dir = d
            best_score = score
    if best_dir is not None:
        dest = unit.coords + best_dir
        RESERVED.add(dest)
        return Action.move(best_dir)
    # No way out: try to at least attack if possible
    ad = choose_attack_direction(unit)
    if ad is not None:
        return Action.attack(ad)
    # Otherwise, move anywhere that is free (even if suboptimal)
    for d, n in neighbors4(unit.coords):
        if not n.is_spawn() and is_free_tile(n):
            RESERVED.add(n)
            return Action.move(d)
    # Totally stuck
    return Action.attack(Direction.North)  # harmless fallback

def want_spawn_ring_camping(unit: Obj) -> bool:
    # On the last safe turn before a spawn (NEXT_TURN_SPAWN is True), we prepare by being adjacent to spawns.
    # We avoid stepping on spawn tiles, but prefer to be on the ring.
    if not TRY_SPAWN_RING_CAMPING:
        return False
    return NEXT_TURN_SPAWN

def best_move_toward(unit: Obj, target: Obj | None) -> Action | None:
    # Evaluate all legal moves (4 neighbors that are free) by score
    moves = []
    for d, n in neighbors4(unit.coords):
        if not is_free_tile(n):
            continue
        # Avoid stepping on spawn tile when NEXT_TURN_SPAWN
        if n.is_spawn() and NEXT_TURN_SPAWN:
            continue
        s = score_tile_for_move(unit, target, n)
        # Minor extra preference for spawn ring if we're camping
        if want_spawn_ring_camping(unit) and (n in SPAWN_RING) and not n.is_spawn():
            s += 1.0
        moves.append((s, d, n))
    if not moves:
        return None
    # Choose top-scoring move. Use unit priority to create deterministic tie-breaking.
    moves.sort(key=lambda t: (t[0], -ID_PRIORITY.get(unit.id, 0)))
    best_score, best_dir, best_dest = moves[-1]
    RESERVED.add(best_dest)
    return Action.move(best_dir)

def should_retreat(unit: Obj) -> bool:
    if not RETREAT_IF_OUTNUMBERED:
        return False
    allies, enemies = local_counts(unit.coords, radius=OUTNUMBER_RADIUS)
    # Retreat if outnumbered locally (strictly)
    return enemies > allies

def init_turn(state: State) -> None:
    global TURN, NEXT_TURN_SPAWN, SPAWN_TURN_NOW
    global ALLIES, ENEMIES, ALLY_BY_COORD, ENEMY_BY_COORD, OCCUPIED, RESERVED, ID_PRIORITY, SPAWN_RING

    TURN = state.turn
    NEXT_TURN_SPAWN = ((state.turn + 1) % 10) == 0
    # Spawn probably happens on 10, 20, 30... Treat turn%10==0 (and turn>0) as a spawn tick.
    SPAWN_TURN_NOW = (state.turn % 10 == 0) and (state.turn != 0)

    ALLIES = state.objs_by_team(state.our_team)
    ENEMIES = state.objs_by_team(state.other_team)

    ALLY_BY_COORD = {o.coords: o for o in ALLIES}
    ENEMY_BY_COORD = {o.coords: o for o in ENEMIES}
    OCCUPIED = {o.coords: o for o in ALLIES + ENEMIES}
    RESERVED = set()

    # Priority per unit: stable ID-derived number
    ID_PRIORITY = {o.id: id_priority_numeric(o.id) for o in ALLIES}

    # Precompute spawn ring (tiles adjacent to spawns but not spawns)
    ring = set()
    for s in SPAWN_COORDS:
        for d in (Direction.North, Direction.South, Direction.East, Direction.West):
            n = s + d
            if in_bounds(n) and (not n.is_spawn()):
                ring.add(n)
    SPAWN_RING = ring

def robot(state: State, unit: Obj):
    # 1) Emergency: if on spawn just before a spawn tick, evacuate immediately
    if unit.coords.is_spawn() and NEXT_TURN_SPAWN:
        act = leave_spawn_now(unit)
        if act is not None:
            dbg(unit, "evacuate_spawn", True)
            return act

    # 2) If adjacent enemy exists, decide attack vs retreat
    adj_enemy_dir = choose_attack_direction(unit)
    if adj_enemy_dir is not None:
        # Decide whether to attack or retreat based on local numbers and safety of staying
        if should_retreat(unit):
            # Try to move to a safer tile while not stepping on spawn tiles
            best = None
            best_score = None
            for d, n in neighbors4(unit.coords):
                if not is_free_tile(n):
                    continue
                if n.is_spawn() and NEXT_TURN_SPAWN:
                    continue
                # Safety heuristic: fewer enemy adjacents and more ally adjacents
                s = -STAY_DANGER_WEIGHT * enemy_adjacent_count(n) + ally_adjacent_count(n)
                # If we can move further from nearby enemies, give slight bonus
                # by measuring min distance to enemies
                mind = 1_000_000
                for e in ENEMIES:
                    dd = n.walking_distance_to(e.coords)
                    if dd < mind:
                        mind = dd
                s += 0.1 * float(mind)
                if best is None or s > best_score:
                    best = (d, n)
                    best_score = s
            if best is not None:
                chosen_d, dest = best
                RESERVED.add(dest)
                dbg(unit, "action", "retreat")
                return Action.move(chosen_d)
        # Otherwise, attack the best adjacent target
        dbg(unit, "action", "attack")
        return Action.attack(adj_enemy_dir)

    # 3) Not adjacent to enemy: pick a target and move toward it safely
    target = pick_target(unit)

    # If the next turn is a spawn tick, prefer to occupy the spawn ring (adjacent to spawn) to farm
    if want_spawn_ring_camping(unit):
        if unit.coords in SPAWN_RING:
            # Already well-positioned; move toward target if we can do so safely and remain on/near ring
            move_act = best_move_toward(unit, target)
            if move_act is not None:
                dbg(unit, "action", "camp_move")
                return move_act
            # Else hold ground by moving minimally (no "wait" action; step to safe non-spawn if possible)
            for d, n in neighbors4(unit.coords):
                if is_free_tile(n) and (not n.is_spawn()):
                    RESERVED.add(n)
                    dbg(unit, "action", "camp_hold")
                    return Action.move(d)
        else:
            # Try to step onto the ring (but not onto a spawn tile)
            best = None
            best_score = None
            best_dir = None
            for d, n in neighbors4(unit.coords):
                if not is_free_tile(n):
                    continue
                if n.is_spawn():  # never step onto spawn if a spawn tick is next
                    continue
                s = score_tile_for_move(unit, target, n)
                if n in SPAWN_RING:
                    s += 1.5  # bias toward ring
                if best is None or s > best_score:
                    best = n
                    best_score = s
                    best_dir = d
            if best_dir is not None:
                RESERVED.add(best)
                dbg(unit, "action", "move_to_ring")
                return Action.move(best_dir)

    # 4) Default pathing: safe, target-directed movement
    move_act = best_move_toward(unit, target)
    if move_act is not None:
        dbg(unit, "action", "approach")
        return move_act

    # 5) Fallbacks: if stuck, try any safe move; else harmless attack
    for d, n in neighbors4(unit.coords):
        if is_free_tile(n) and (not (n.is_spawn() and NEXT_TURN_SPAWN)):
            RESERVED.add(n)
            dbg(unit, "action", "fallback_move")
            return Action.move(d)

    dbg(unit, "action", "fallback_attack")
    return Action.attack(Direction.North)

