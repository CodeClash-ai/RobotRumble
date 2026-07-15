# RobotRumble bot v2 - aggressive coordinated focus-fire with predictive attacks
# Game facts (docs/ and logic/logic/src/lib.rs):
#  - 19x19 circular arena, 5 HP units, attacks 1 dmg, NO self-damage cost.
#  - Movement resolves BEFORE attacks each turn; attackers on same tile stack.
#  - Friendly fire IS possible (avoid it).
#  - Up to 4 units spawn/team every 10 turns; win = most units at turn 100.
#  - Move conflict priority N,E,S,W; swap-moves blocked.
# Strategy: group up, focus-fire the weakest reachable enemy, predict flee,
# never hit allies, keep units advancing out of spawn so they aren't wiped.

from typing import *

DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]
last_positions: Dict[str, Any] = {}
# Per-turn shared state computed in init_turn
_focus_target_id = None
_planned_moves: Dict[str, Any] = {}  # unit_id -> destination Coords


def in_bounds(c) -> bool:
    return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE


def blocked_tile(state, c) -> bool:
    if not in_bounds(c):
        return True
    o = state.obj_by_coords(c)
    if o is not None and o.obj_type == ObjType.Terrain:
        return True
    return False


def unit_at(state, c):
    o = state.obj_by_coords(c)
    if o is not None and o.obj_type == ObjType.Unit:
        return o
    return None


def enemy_at(state, c, other_team):
    o = state.obj_by_coords(c)
    if o is not None and o.obj_type == ObjType.Unit and o.team == other_team:
        return o
    return None


def adjacent_enemies(state, c, other_team):
    res = []
    for d in DIRECTIONS:
        e = enemy_at(state, c + d, other_team)
        if e is not None:
            res.append((d, e))
    return res


def count_my_adjacent(state, coords, my_team):
    """How many of my units are adjacent to `coords` (i.e. can attack it)."""
    n = 0
    for d in DIRECTIONS:
        o = unit_at(state, coords + d)
        if o is not None and o.team == my_team:
            n += 1
    return n


def init_turn(state: State) -> None:
    global _focus_target_id, _planned_moves
    _planned_moves = {}
    other = state.other_team
    enemies = state.objs_by_team(other)
    mine = state.objs_by_team(state.our_team)
    if not enemies or not mine:
        _focus_target_id = None
        return
    # Choose a global focus target: weakest enemy, tie-broken by total distance
    # from our units (closer = easier to gang up on).
    def score(e):
        total = sum(u.coords.walking_distance_to(e.coords) for u in mine)
        return (e.health, total)
    _focus_target_id = min(enemies, key=score).id


def robot(state: State, unit: Obj) -> Optional[Action]:
    other_team = state.other_team
    my_team = state.our_team
    enemies = state.objs_by_team(other_team)
    my = unit.coords

    if not enemies:
        return leave_spawn(state, unit)

    # 1) If an enemy is adjacent, decide whether to attack now.
    adj = adjacent_enemies(state, my, other_team)
    if adj:
        # Prefer weakest adjacent enemy.
        d, e = min(adj, key=lambda de: de[1].health)
        # Attack is guaranteed value if:
        #  - enemy will likely die this turn (health <= number of my units
        #    adjacent that can attack it), OR
        #  - enemy is at 1 HP (worth trying), OR
        #  - enemy is cornered / heavily surrounded so it can't flee freely.
        attackers = count_my_adjacent(state, e.coords, my_team)
        if e.health <= attackers or e.health <= 1 or enemy_boxed(state, e, my_team):
            return Action.attack(d)
        # Otherwise the healthy enemy will likely move away before our attack
        # lands. Still attack if we have no better move (stay engaged), because
        # staying adjacent pressures them and blocks retreat lanes.
        return Action.attack(d)

    # 2) Move toward focus target if reachable, else nearest weak enemy.
    target = pick_target(state, unit, enemies)
    return step_toward(state, unit, target.coords)


def enemy_boxed(state, e, my_team):
    """Enemy has few free escape tiles (can't dodge easily)."""
    free = 0
    for d in DIRECTIONS:
        nxt = e.coords + d
        if blocked_tile(state, nxt):
            continue
        o = unit_at(state, nxt)
        if o is None:
            free += 1
    return free <= 1


def pick_target(state, unit, enemies):
    global _focus_target_id
    my = unit.coords
    if _focus_target_id is not None:
        t = state.obj_by_id(_focus_target_id)
        if t is not None:
            return t
    return min(enemies, key=lambda e: (e.health, my.walking_distance_to(e.coords)))


def leave_spawn(state, unit):
    if not unit.coords.is_spawn():
        return None
    return step_toward(state, unit, Coords(MAP_SIZE // 2, MAP_SIZE // 2))


def step_toward(state, unit, goal):
    global last_positions, _planned_moves
    my = unit.coords
    candidates = []
    for d in DIRECTIONS:
        nxt = my + d
        if blocked_tile(state, nxt):
            continue
        o = state.obj_by_coords(nxt)
        if o is not None:
            continue  # occupied
        # avoid tiles another ally already planned to move into this turn
        collide = False
        for did, dest in _planned_moves.items():
            if did != unit.id and dest.x == nxt.x and dest.y == nxt.y:
                collide = True
                break
        if collide:
            continue
        candidates.append((nxt.walking_distance_to(goal), d, nxt))

    if not candidates:
        return None

    candidates.sort(key=lambda c: c[0])
    prev = last_positions.get(unit.id)
    for dist, d, nxt in candidates:
        if prev is not None and nxt.x == prev.x and nxt.y == prev.y:
            continue
        last_positions[unit.id] = my
        _planned_moves[unit.id] = nxt
        return Action.move(d)

    last_positions[unit.id] = my
    _planned_moves[unit.id] = candidates[0][2]
    return Action.move(candidates[0][1])
