# RobotRumble bot - aggressive, coordinated focus-fire strategy
# Game facts (docs/ and logic/logic/src/lib.rs):
#  - 19x19 circular arena, 5 HP units, attacks 1 dmg, NO self-damage cost.
#  - Movement resolves BEFORE attacks each turn; attackers on same tile stack.
#  - Friendly fire IS possible (avoid it).
#  - Up to 4 units spawn/team every 10 turns; win = most units at turn 100.
#  - Move conflict priority N,E,S,W; swap-moves blocked.
# Strategy: hunt enemies, focus-fire the weakest reachable enemy, gang up,
# never hit allies, keep units advancing out of spawn so they aren't wiped.
# The previous stalemate (round 0 tie) happened because both bots were passive
# and never engaged; this bot always engages.

from typing import *

DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]
last_positions: Dict[str, Any] = {}


def in_bounds(c) -> bool:
    return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE


def blocked_tile(state, c) -> bool:
    if not in_bounds(c):
        return True
    o = state.obj_by_coords(c)
    if o is not None and o.obj_type == ObjType.Terrain:
        return True
    return False


def enemy_at(state, c, other_team):
    o = state.obj_by_coords(c)
    if o is not None and o.obj_type == ObjType.Unit and o.team == other_team:
        return o
    return None


def init_turn(state: State) -> None:
    pass


def robot(state: State, unit: Obj) -> Optional[Action]:
    other_team = state.other_team
    enemies = state.objs_by_team(other_team)
    my = unit.coords

    if not enemies:
        return leave_spawn(state, unit)

    # 1) Attack an adjacent enemy: pick the weakest to secure kills.
    adj = []
    for d in DIRECTIONS:
        e = enemy_at(state, my + d, other_team)
        if e is not None:
            adj.append((d, e))
    if adj:
        d, e = min(adj, key=lambda de: de[1].health)
        return Action.attack(d)

    # 2) Move toward the best target: prefer low HP, then close.
    target = min(enemies, key=lambda e: (e.health, my.walking_distance_to(e.coords)))
    return step_toward(state, unit, target.coords)


def leave_spawn(state, unit):
    if not unit.coords.is_spawn():
        return None
    return step_toward(state, unit, Coords(MAP_SIZE // 2, MAP_SIZE // 2))


def step_toward(state, unit, goal):
    global last_positions
    my = unit.coords
    candidates = []
    for d in DIRECTIONS:
        nxt = my + d
        if blocked_tile(state, nxt):
            continue
        if state.obj_by_coords(nxt) is not None:
            continue  # occupied by a unit
        candidates.append((nxt.walking_distance_to(goal), d, nxt))

    if not candidates:
        return None

    candidates.sort(key=lambda c: c[0])
    prev = last_positions.get(unit.id)
    for dist, d, nxt in candidates:
        if prev is not None and nxt.x == prev.x and nxt.y == prev.y:
            continue
        last_positions[unit.id] = my
        return Action.move(d)

    last_positions[unit.id] = my
    return Action.move(candidates[0][1])
