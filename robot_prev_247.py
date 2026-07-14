from typing import *

# RobotRumble bot - Normal mode.
# Rules: UNIT_HEALTH=5, ATTACK_POWER=1, attacks stack; movement resolves
# before attacks (attacks hit a CELL). Winner = most units alive at end.
#
# Strategy overview:
#  - Coordinated focus fire that KILLS enemy units (they have 5 hp).
#  - Predictive attacks: adjacent enemies expected to attack us usually stay;
#    attack their current cell. When ganging up we secure kills.
#  - Anti-dive: don't walk into a cell where more enemies could hit us than
#    allies can support, unless we'd immediately kill / it's worth it.
#  - Move in coordinated fashion, no friendly collisions.

DIRECTIONS = [Direction.North, Direction.South, Direction.East, Direction.West]
MAX_HP = 5

robot_state: Dict[str, dict] = {}

_planned_moves: Dict[str, Coords] = {}
_attack_plan: Dict[str, int] = {}   # enemy id -> committed damage this turn


def in_bounds(c: Coords) -> bool:
    return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE


def cell_key(c: Coords):
    return (c.x, c.y)


def init_turn(state: State) -> None:
    global _planned_moves, _attack_plan
    _planned_moves = {}
    _attack_plan = {}


def enemy_adjacent_count(c: Coords, enemies) -> int:
    return sum(1 for e in enemies if e.coords.walking_distance_to(c) == 1)


def ally_support_count(c: Coords, allies, exclude_id) -> int:
    # allies (other than exclude) that are adjacent to cell c
    return sum(1 for a in allies if a.id != exclude_id and a.coords.walking_distance_to(c) == 1)


def robot(state: State, unit: Obj) -> Optional[Action]:
    global _planned_moves, _attack_plan
    mem = robot_state.setdefault(unit.id, {})
    past = mem.get("past")
    mem["past"] = unit.coords

    enemies = state.objs_by_team(state.other_team)
    allies = state.objs_by_team(state.our_team)
    if not enemies:
        return None

    my = unit.coords

    adj_enemies = [e for e in enemies if e.coords.walking_distance_to(my) == 1]

    # ---- ATTACK DECISION ----
    if adj_enemies:
        # How many of our units are adjacent to each candidate enemy (focus).
        def focus(e):
            return sum(1 for a in allies if a.coords.walking_distance_to(e.coords) == 1)

        # Prefer: enemy that can be killed with committed damage; then lowest
        # effective health; then highest focus.
        def akey(e):
            committed = _attack_plan.get(e.id, 0)
            remaining = e.health - committed
            f = focus(e)
            killable = 1 if f >= e.health else 0
            # if already lethal committed, deprioritize (avoid overkill) unless
            # it's the only adjacent enemy
            wasted = 1 if committed >= e.health else 0
            return (-killable, wasted, remaining, -f)

        target = min(adj_enemies, key=akey)
        _attack_plan[target.id] = _attack_plan.get(target.id, 0) + 1
        return Action.attack(my.direction_to(target.coords))

    # ---- RETREAT if low health and enemy near (avoid feeding kills) ----
    nearest_enemy_dist = min(e.coords.walking_distance_to(my) for e in enemies)
    if unit.health <= 2 and nearest_enemy_dist <= 2:
        # move away from the centroid of nearby enemies toward allies
        near = [e for e in enemies if e.coords.walking_distance_to(my) <= 3]
        if near:
            ex = sum(e.coords.x for e in near) / len(near)
            ey = sum(e.coords.y for e in near) / len(near)
            best_r = None; best_rk = None
            for d in DIRECTIONS:
                dest = my + d
                if not in_bounds(dest):
                    continue
                o = state.obj_by_coords(dest)
                if o is not None:
                    continue
                if any((pd.x, pd.y) == (dest.x, dest.y) for pd in _planned_moves.values()):
                    continue
                # farther from enemy centroid is better
                away = -((dest.x - ex) ** 2 + (dest.y - ey) ** 2)
                threat = enemy_adjacent_count(dest, enemies)
                k = (threat, away)
                if best_rk is None or k < best_rk:
                    best_rk = k; best_r = (d, dest)
            if best_r is not None and best_rk[0] <= enemy_adjacent_count(my, enemies):
                d, dest = best_r
                _planned_moves[unit.id] = dest
                return Action.move(d)

    # ---- MOVEMENT DECISION ----
    # pick target enemy: nearest, tie-break lowest health
    target = min(enemies, key=lambda e: (e.coords.walking_distance_to(my), e.health))

    # ally centroid (excluding self) for grouping; helps us arrive together and
    # win trades vs clustering bots (heuristic / black-magic style).
    others = [a for a in allies if a.id != unit.id]
    if others:
        acx = sum(a.coords.x for a in others) / len(others)
        acy = sum(a.coords.y for a in others) / len(others)
    else:
        acx, acy = my.x, my.y

    def occupied_blocked(dest):
        o = state.obj_by_coords(dest)
        if o is None:
            return False
        if o.obj_type == ObjType.Terrain:
            return True
        # any unit blocks (can't move onto occupied cell)
        return True

    def reserved(dest):
        return any(cell_key(pd) == cell_key(dest) for pd in _planned_moves.values())

    # evaluate candidate moves
    best = None
    best_key = None
    for d in DIRECTIONS:
        dest = my + d
        if not in_bounds(dest):
            continue
        if occupied_blocked(dest):
            continue
        if reserved(dest):
            continue

        dist = dest.walking_distance_to(target.coords)
        # anti-dive: enemies that would be adjacent to dest next turn
        threat = enemy_adjacent_count(dest, enemies)
        support = ally_support_count(dest, allies, unit.id)
        # danger if we step into a cell where more enemies can hit us than we
        # have allied support (we'd lose the trade). Being outnumbered is bad.
        outnumbered = max(0, threat - support - 1)
        # prefer moving adjacent to target when we have support / not outnumbered
        # sorting key: primarily reduce distance, but penalize dangerous cells
        # if we'd be badly outnumbered.
        osc = 1 if (past is not None and cell_key(dest) == cell_key(past)) else 0
        # grouping: prefer cells nearer to allied centroid (Manhattan) so we
        # advance as a pack. Small weight so it does not override approach.
        group_dist = abs(dest.x - acx) + abs(dest.y - acy)
        # effective approach cost: distance to target plus danger penalty.
        eff = dist + outnumbered * 4
        key = (eff, outnumbered, osc, group_dist, -support, threat)
        if best_key is None or key < best_key:
            best_key = key
            best = (d, dest)

    if best is None:
        return None
    d, dest = best
    _planned_moves[unit.id] = dest
    return Action.move(d)
