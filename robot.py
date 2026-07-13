from typing import *

# Track previous positions to avoid oscillation
robot_state: Dict[str, dict] = {}

# Track intended moves to prevent friendly collisions
planned_moves: Dict[str, "Coords"] = {}

# Track damage already committed to enemies this turn
damage_committed: Dict[str, int] = {}

# Cached enemy positions
_enemies_cache = None
_allies_cache = None
_enemy_set_cache = None
_ally_set_cache = None


def init_turn(state: State) -> None:
    global planned_moves, damage_committed, _enemies_cache, _allies_cache, _enemy_set_cache, _ally_set_cache
    planned_moves = {}
    damage_committed = {}
    _enemies_cache = [o for o in state.objs_by_team(state.other_team) if o.obj_type == ObjType.Unit]
    _allies_cache = [o for o in state.objs_by_team(state.our_team) if o.obj_type == ObjType.Unit]
    _enemy_set_cache = {(o.coords.x, o.coords.y) for o in _enemies_cache}
    _ally_set_cache = {(o.coords.x, o.coords.y) for o in _allies_cache}


def is_in_bounds(coords) -> bool:
    x, y = coords.x, coords.y
    if x < 1 or y < 1 or x > MAP_SIZE - 2 or y > MAP_SIZE - 2:
        return False
    center = MAP_SIZE // 2
    dx = abs(x - center)
    dy = abs(y - center)
    if dx + dy > 12:
        return False
    return True


def enemy_at(x, y) -> bool:
    return (x, y) in _enemy_set_cache


def friend_at(x, y) -> bool:
    return (x, y) in _ally_set_cache


def count_adj_enemies_xy(x, y) -> int:
    c = 0
    if enemy_at(x-1, y): c += 1
    if enemy_at(x+1, y): c += 1
    if enemy_at(x, y-1): c += 1
    if enemy_at(x, y+1): c += 1
    return c


def count_adj_friends_xy(x, y, ignore=None) -> int:
    c = 0
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x+dx, y+dy
        if (nx, ny) in _ally_set_cache and (nx, ny) != ignore:
            c += 1
    return c


def enemy_adjacent_dir(state, unit):
    """Return direction of adjacent enemy (prefer kill, then lowest effective HP)."""
    best = None
    best_key = None
    for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
        c = unit.coords + d
        obj = state.obj_by_coords(c)
        if obj and obj.obj_type == ObjType.Unit and obj.team == state.other_team:
            committed = damage_committed.get(obj.id, 0)
            effective_hp = obj.health - committed
            can_kill = 0 if effective_hp <= 1 else 1
            key = (can_kill, effective_hp, obj.health)
            if best_key is None or key < best_key:
                best_key = key
                best = (d, obj.id)
    if best is None:
        return None
    return best[0]


def commit_attack(direction, state, unit):
    c = unit.coords + direction
    obj = state.obj_by_coords(c)
    if obj and obj.obj_type == ObjType.Unit and obj.team == state.other_team:
        damage_committed[obj.id] = damage_committed.get(obj.id, 0) + 1
    return Action.attack(direction)


def tile_score_for_move(state, unit, target_coords, primary_dir_target):
    """Score how good a tile is to move into. Higher = better.
    Factors:
    - Distance to primary target (closer is better)
    - Number of adjacent allies (more is better - stay in formation)
    - Number of adjacent enemies (moderate - if we're strong; bad if alone)
    - Danger: if 2+ enemies adjacent and no ally support, penalty
    """
    tx, ty = target_coords.x, target_coords.y
    dist = target_coords.walking_distance_to(primary_dir_target)
    adj_e = count_adj_enemies_xy(tx, ty)
    adj_a = count_adj_friends_xy(tx, ty, ignore=(unit.coords.x, unit.coords.y))
    
    score = -dist * 10  # closer to target better
    score += adj_a * 3  # cluster with allies
    # Penalty for being surrounded by many enemies without ally support
    if adj_e >= 2 and adj_a == 0:
        score -= 25
    elif adj_e >= 3:
        score -= 15
    # If we can attack an enemy from here, that's great
    if adj_e >= 1 and adj_a >= 1:
        score += 5
    return score


def try_move_smart(state, unit, primary_target_coords):
    """Try to move, evaluating multiple candidate directions."""
    global planned_moves
    my_id = unit.id
    
    turns_to_spawn = (10 - (state.turn % 10)) % 10
    avoid_spawn = turns_to_spawn <= 1
    
    candidates = []
    for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
        target = unit.coords + d
        if not is_in_bounds(target):
            continue
        obj = state.obj_by_coords(target)
        if obj is not None:
            continue
        # Check collision with planned moves
        collision = False
        for oid, oc in planned_moves.items():
            if oid != my_id and oc.x == target.x and oc.y == target.y:
                collision = True
                break
        if collision:
            continue
        if avoid_spawn and target.is_spawn():
            continue
        s = tile_score_for_move(state, unit, target, primary_target_coords)
        candidates.append((s, d, target))
    
    if not candidates:
        # Relax spawn constraint
        for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
            target = unit.coords + d
            if not is_in_bounds(target):
                continue
            obj = state.obj_by_coords(target)
            if obj is not None:
                continue
            collision = False
            for oid, oc in planned_moves.items():
                if oid != my_id and oc.x == target.x and oc.y == target.y:
                    collision = True
                    break
            if collision:
                continue
            s = tile_score_for_move(state, unit, target, primary_target_coords)
            candidates.append((s, d, target))
    
    if not candidates:
        return None
    
    candidates.sort(key=lambda x: -x[0])
    best_s, best_d, best_target = candidates[0]
    planned_moves[my_id] = best_target
    return Action.move(best_d)


def robot_impl(state, unit):
    global robot_state
    st = robot_state.setdefault(unit.id, {})
    st["past_coords"] = unit.coords

    enemies = _enemies_cache
    allies = _allies_cache
    
    if not enemies:
        center = Coords(MAP_SIZE // 2, MAP_SIZE // 2)
        if unit.coords.x == center.x and unit.coords.y == center.y:
            return None
        return try_move_smart(state, unit, center)
    
    on_spawn = unit.coords.is_spawn()
    turns_to_spawn = (10 - (state.turn % 10)) % 10
    
    if on_spawn and turns_to_spawn <= 1:
        center = Coords(MAP_SIZE // 2, MAP_SIZE // 2)
        mv = try_move_smart(state, unit, center)
        if mv:
            return mv
    
    # Adjacent enemy check
    adj = enemy_adjacent_dir(state, unit)
    my_hp = unit.health
    
    if adj:
        adj_coords = unit.coords + adj
        adj_enemy = state.obj_by_coords(adj_coords)
        n_adj_e = count_adj_enemies_xy(unit.coords.x, unit.coords.y)
        n_adj_a = count_adj_friends_xy(unit.coords.x, unit.coords.y)
        committed = damage_committed.get(adj_enemy.id, 0)
        eff_enemy_hp = adj_enemy.health - committed
        
        # If we can kill this turn, always attack
        if eff_enemy_hp <= 1:
            return commit_attack(adj, state, unit)
        
        # Flee if very likely to die (surrounded, low hp)
        should_flee = False
        # HP <= 2 and outnumbered
        if my_hp <= 2 and n_adj_e >= 2 and n_adj_a == 0:
            should_flee = True
        # HP <= 1 and can't kill target
        elif my_hp <= 1 and eff_enemy_hp > 1:
            should_flee = True
        # HP <= 3, badly outnumbered
        elif my_hp <= 3 and n_adj_e >= 3 and n_adj_a <= 1:
            should_flee = True
        
        if should_flee:
            # Find safest retreat: away from enemies, toward allies
            best_flee = None
            best_flee_score = -1e9
            for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
                target = unit.coords + d
                if not is_in_bounds(target):
                    continue
                obj = state.obj_by_coords(target)
                if obj is not None:
                    continue
                collision = False
                for oid, oc in planned_moves.items():
                    if oid != unit.id and oc.x == target.x and oc.y == target.y:
                        collision = True
                        break
                if collision:
                    continue
                tx, ty = target.x, target.y
                e_around = count_adj_enemies_xy(tx, ty)
                a_around = count_adj_friends_xy(tx, ty, ignore=(unit.coords.x, unit.coords.y))
                s = -e_around * 20 + a_around * 5
                if s > best_flee_score:
                    best_flee_score = s
                    best_flee = (d, target)
            if best_flee:
                planned_moves[unit.id] = best_flee[1]
                return Action.move(best_flee[0])
        
        return commit_attack(adj, state, unit)
    
    # Find target - prefer weaker AND closer, avoid isolated enemies deep in formation
    def enemy_score(e):
        dist = unit.coords.walking_distance_to(e.coords)
        # Slight bias: prefer enemies with lower HP but weight distance heavily
        return dist * 10 + e.health
    
    target = min(enemies, key=enemy_score)
    dist = unit.coords.walking_distance_to(target.coords)
    
    # If HP=1 and no allies nearby, retreat toward allies
    if my_hp <= 1 and dist <= 3:
        near_allies = sum(1 for a in allies if a.id != unit.id and unit.coords.walking_distance_to(a.coords) <= 2)
        near_enemies = sum(1 for e in enemies if unit.coords.walking_distance_to(e.coords) <= 2)
        if near_enemies > near_allies:
            # Retreat toward nearest ally cluster or center
            center = Coords(MAP_SIZE // 2, MAP_SIZE // 2)
            if allies and len(allies) > 1:
                # move toward nearest ally
                other_allies = [a for a in allies if a.id != unit.id]
                if other_allies:
                    nearest_ally = min(other_allies, key=lambda a: unit.coords.walking_distance_to(a.coords))
                    return try_move_smart(state, unit, nearest_ally.coords)
            return try_move_smart(state, unit, center)
    
    return try_move_smart(state, unit, target.coords)


# Safety wrapper
def robot(state, unit):
    try:
        return robot_impl(state, unit)
    except Exception:
        try:
            for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
                c = unit.coords + d
                obj = state.obj_by_coords(c)
                if obj and obj.obj_type == ObjType.Unit and obj.team == state.other_team:
                    return Action.attack(d)
        except Exception:
            pass
        return None
