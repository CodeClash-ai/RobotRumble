from typing import *

# Track previous positions to avoid oscillation
robot_state: Dict[str, dict] = {}

# Track intended moves to prevent friendly collisions
planned_moves: Dict[str, "Coords"] = {}


def init_turn(state: State) -> None:
    global planned_moves
    planned_moves = {}


def is_in_bounds(coords: "Coords") -> bool:
    # Arena is 19x19 octagonal. Walkable region excludes corner cutouts.
    # Coords are 1..MAP_SIZE-2 (1..17) walkable, with corners cut.
    x, y = coords.x, coords.y
    if x < 1 or y < 1 or x > MAP_SIZE - 2 or y > MAP_SIZE - 2:
        return False
    # Corner cutouts: 4x4 corners removed in an angled fashion
    # Based on the visual: rows 1: 9-13, row 2: 7-15, row 3: 5-17, row 4: 3-19
    # Approximate by using distance from center check on octagon
    # The map removes cells where x+y or |x-y| are too extreme.
    center = MAP_SIZE // 2  # 9
    # Cell is valid if it's within octagon
    dx = abs(x - center)
    dy = abs(y - center)
    # From arena: max dx+dy allowed is roughly 12
    if dx + dy > 12:
        return False
    return True


def is_tile_free(state: State, coords: "Coords", ignore_id: Optional[str] = None) -> bool:
    if not is_in_bounds(coords):
        return False
    obj = state.obj_by_coords(coords)
    if obj is None:
        return True
    if ignore_id and obj.id == ignore_id:
        return True
    return False


def enemy_adjacent_dir(state: State, unit: Obj) -> Optional["Direction"]:
    """Return direction of adjacent enemy (prefer low health)."""
    best = None
    best_hp = 999
    for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
        c = unit.coords + d
        obj = state.obj_by_coords(c)
        if obj and obj.obj_type == ObjType.Unit and obj.team == state.other_team:
            if obj.health < best_hp:
                best_hp = obj.health
                best = d
    return best


def friend_at(state: State, coords: "Coords") -> bool:
    obj = state.obj_by_coords(coords)
    return obj is not None and obj.obj_type == ObjType.Unit and obj.team == state.our_team


def enemy_at(state: State, coords: "Coords") -> bool:
    obj = state.obj_by_coords(coords)
    return obj is not None and obj.obj_type == ObjType.Unit and obj.team == state.other_team


def count_adjacent_enemies(state: State, coords: "Coords") -> int:
    cnt = 0
    for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
        if enemy_at(state, coords + d):
            cnt += 1
    return cnt


def count_adjacent_friends(state: State, coords: "Coords") -> int:
    cnt = 0
    for d in [Direction.North, Direction.East, Direction.South, Direction.West]:
        if friend_at(state, coords + d):
            cnt += 1
    return cnt


def try_move(state: State, unit: Obj, direction: "Direction") -> Optional["Action"]:
    """Try to move in given direction, or try rotations, avoiding walls, allies, planned collisions."""
    global planned_moves
    my_id = unit.id
    
    candidates = [direction, direction.rotate_cw, direction.rotate_ccw, direction.opposite]
    
    for i, d in enumerate(candidates):
        target = unit.coords + d
        if not is_in_bounds(target):
            continue
        obj = state.obj_by_coords(target)
        if obj is not None:
            # Blocked by unit/terrain
            continue
        # Check if another ally already planned to move here
        collision = False
        for oid, oc in planned_moves.items():
            if oid != my_id and oc.x == target.x and oc.y == target.y:
                collision = True
                break
        if collision:
            continue
        planned_moves[my_id] = target
        return Action.move(d)
    return None


def robot(state: State, unit: Obj) -> Optional["Action"]:
    global robot_state
    st = robot_state.setdefault(unit.id, {})
    past_coords = st.get("past_coords")
    st["past_coords"] = unit.coords

    enemies = [o for o in state.objs_by_team(state.other_team) if o.obj_type == ObjType.Unit]
    allies = [o for o in state.objs_by_team(state.our_team) if o.obj_type == ObjType.Unit]
    
    if not enemies:
        # Just move toward center
        center = Coords(MAP_SIZE // 2, MAP_SIZE // 2)
        if unit.coords.x == center.x and unit.coords.y == center.y:
            return None
        return try_move(state, unit, unit.coords.direction_to(center))
    
    # 1. If we're on/near a spawn tile and turn % 10 == 9, move off it! (turns spawn every 10)
    # Spawn happens every 10 turns and existing units on spawn get removed
    # Actually: "any robots still left in the spawn area are removed"
    on_spawn = unit.coords.is_spawn()
    turns_to_spawn = (10 - (state.turn % 10)) % 10
    
    if on_spawn and turns_to_spawn <= 1:
        # Get off spawn ASAP - move toward center
        center = Coords(MAP_SIZE // 2, MAP_SIZE // 2)
        d = unit.coords.direction_to(center)
        mv = try_move(state, unit, d)
        if mv:
            return mv
    
    # 2. Adjacent enemy? Attack (prefer lowest HP)
    adj = enemy_adjacent_dir(state, unit)
    
    # Count nearby situation for flee decision
    my_hp = unit.health
    
    if adj:
        # Check if we should flee first (very low HP + enemy adjacent stronger)
        adj_coords = unit.coords + adj
        adj_enemy = state.obj_by_coords(adj_coords)
        # Attack if we can kill them, or if we're healthy enough
        if my_hp <= 1 and adj_enemy.health > 1:
            # Try to flee
            flee_dir = adj.opposite
            mv = try_move(state, unit, flee_dir)
            if mv:
                return mv
            # Can't flee - attack anyway
            return Action.attack(adj)
        return Action.attack(adj)
    
    # 3. Find closest enemy, prefer weaker
    def enemy_score(e):
        return unit.coords.walking_distance_to(e.coords) * 10 + e.health
    
    target = min(enemies, key=enemy_score)
    dist = unit.coords.walking_distance_to(target.coords)
    
    # 4. Flee if very low health and no ally support
    if my_hp <= 1 and dist <= 3:
        # count nearby allies vs nearby enemies
        near_allies = sum(1 for a in allies if a.id != unit.id and unit.coords.walking_distance_to(a.coords) <= 2)
        near_enemies = sum(1 for e in enemies if unit.coords.walking_distance_to(e.coords) <= 2)
        if near_enemies > near_allies:
            flee_dir = target.coords.direction_to(unit.coords)
            mv = try_move(state, unit, flee_dir)
            if mv:
                return mv
    
    # 5. Move toward target
    direction = unit.coords.direction_to(target.coords)
    return try_move(state, unit, direction)
