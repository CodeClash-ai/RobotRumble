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



def count_allies_near(state, coords, my_team):
    """Allies within walking distance 2 (loose grouping)."""
    n = 0
    for u in state.objs_by_team(my_team):
        wd = coords.walking_distance_to(u.coords)
        if 0 < wd <= 2:
            n += 1
    return n


def retreat(state, unit):
    """Move away from the nearest enemy to a free tile."""
    other = state.other_team
    enemies = state.objs_by_team(other)
    if not enemies:
        return None
    my = unit.coords
    ne = min(enemies, key=lambda e: my.walking_distance_to(e.coords))
    best = None
    best_d = -1
    for d in DIRECTIONS:
        nxt = my + d
        if blocked_tile(state, nxt):
            continue
        if state.obj_by_coords(nxt) is not None:
            continue
        dd = nxt.walking_distance_to(ne.coords)
        if dd > best_d:
            best_d = dd
            best = d
    if best is not None and best_d > my.walking_distance_to(ne.coords):
        return Action.move(best)
    return None


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
        n_adj_enemies = len(adj)
        my_local = count_allies_near(state, my, my_team)
        # Retreat a fragile unit that is outnumbered locally (avoid feeding kills)
        # unless it can secure a kill this turn.
        # Prefer attacking an adjacent enemy that is BOXED (cannot flee this
        # turn) so the hit is guaranteed to land, then weakest, then most
        # ally-attackers (best chance to secure the kill after fleeing).
        def adj_score(de):
            dd, ee = de
            boxed = enemy_boxed(state, ee, my_team)
            attackers = count_my_adjacent(state, ee.coords, my_team)
            # lower is better: boxed first, then low health, then more attackers
            return (0 if boxed else 1, ee.health, -attackers)
        d, e = min(adj, key=adj_score)
        attackers = count_my_adjacent(state, e.coords, my_team)
        can_kill = e.health <= attackers
        # Retreat a fragile unit that is outnumbered locally and cannot kill.
        outnumbered = n_adj_enemies > my_local + 1
        # Late-game: preserve unit count (win = most units at turn 100). If a
        # fragile unit (<=2 HP) can't secure a kill this turn, retreat instead
        # of feeding an even/losing trade near the end.
        # Late-game unit preservation only when NOT behind in unit count
        # (win = most units at turn 100; if behind we must trade to catch up).
        my_units = len(state.objs_by_team(my_team))
        enemy_units = len(enemies)
        late_game = state.turn >= 85 and my_units >= enemy_units
        # Mid/late even-game: preserve fragile (<=2HP) units when NOT ahead in
        # count so even 1-for-1 trades don't leave us tied (win = most units).
        even_game = state.turn >= 50 and my_units <= enemy_units
        should_retreat = (
            unit.health <= 1
            or (outnumbered and unit.health <= 2)
            or (late_game and unit.health <= 3)
            or (even_game and unit.health <= 2)
        )
        if not can_kill and should_retreat:
            r = retreat(state, unit)
            if r is not None:
                return r
        # Attack the chosen adjacent enemy (aggressive: always trade or better).
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
        # grouping: sum walking distance to nearby allies (smaller = tighter)
        ally_pen = 0
        for u in state.objs_by_team(unit.team):
            if u.id == unit.id:
                continue
            wd = nxt.walking_distance_to(u.coords)
            if wd <= 4:
                ally_pen += wd
        candidates.append((nxt.walking_distance_to(goal), ally_pen, d, nxt))

    if not candidates:
        return None

    candidates.sort(key=lambda c: (c[0], c[1]))
    prev = last_positions.get(unit.id)
    for dist, ap, d, nxt in candidates:
        if prev is not None and nxt.x == prev.x and nxt.y == prev.y:
            continue
        last_positions[unit.id] = my
        _planned_moves[unit.id] = nxt
        return Action.move(d)

    # Fallback: all preferred tiles were the previous position; take the best.
    dist, ap, d, nxt = candidates[0]
    last_positions[unit.id] = my
    _planned_moves[unit.id] = nxt
    return Action.move(d)
