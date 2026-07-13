from enum import Enum, auto
from typing import *

# ---------------------------------------------------------------------------
# "Black-magic style" 1-ply lookahead bot.
#
# Idea (see README_agent.md round 2/6/7 notes): builtin-bots/black-magic.js
# beats our heuristic "group brawler" bot consistently. It works by, once per
# turn, trying every possible action for every one of its own units (holding
# everyone else's action fixed), simulating the immediate result of a turn
# (assuming enemies attack whichever adjacent friend has lowest health), and
# greedily keeping whichever action improves a lexicographic score:
#   (unit_count_diff, surround_score, health_diff, distance_score)
# This file reimplements the same idea for our bot, plus a safety fallback to
# the proven "group brawler" heuristic (see robot_r6_retreat15_backup.py /
# robot.py) if unit counts get too large (compute-cost safety valve) or if
# anything goes wrong (defensive try/except, since forfeiting on a timeout
# or crash would be much worse than falling back to a known-good heuristic).
# ---------------------------------------------------------------------------

RADIUS = 6
RETREAT_RATIO = 2.5
MAX_UNITS_FOR_LOOKAHEAD = 70  # total friends+enemies; above this, use fallback heuristic (perf safety valve)

ALL_DIRS = [Direction.North, Direction.South, Direction.East, Direction.West]

_turn_cache: Dict[str, Any] = {"fallback": True}


# ---------------------------------------------------------------------------
# Fallback ("group brawler") logic -- identical to robot_r6_retreat15_backup.py
# ---------------------------------------------------------------------------

_fallback_state: Dict[str, dict] = {}


def team_centroid(units: List[Obj]) -> Optional[Coords]:
    if not units:
        return None
    xs = sum(u.coords.x for u in units)
    ys = sum(u.coords.y for u in units)
    n = len(units)
    return Coords(round(xs / n), round(ys / n))


def best_move_towards(state: State, unit: Obj, target: Coords, avoid: Optional[Coords] = None) -> Optional[Action]:
    if unit.coords == target:
        return None
    direction = unit.coords.direction_to(target)
    candidates = [direction, direction.rotate_cw, direction.rotate_ccw]
    for d in candidates:
        dest = unit.coords + d
        if state.obj_by_coords(dest):
            continue
        if avoid is not None and dest == avoid:
            continue
        return Action.move(d)
    for d in candidates:
        dest = unit.coords + d
        if not state.obj_by_coords(dest):
            return Action.move(d)
    return None


def _fallback_robot(state: State, unit: Obj) -> Optional[Action]:
    st = _fallback_state.setdefault(unit.id, {})
    past_coords: Optional[Coords] = st.get("past_coords")
    st["past_coords"] = unit.coords

    allies = [u for u in state.objs_by_team(state.our_team) if u.id != unit.id]
    enemies = state.objs_by_team(state.other_team)

    if not enemies:
        return None

    adjacent_enemies = [e for e in enemies if unit.coords.distance_to(e.coords) == 1]
    if adjacent_enemies:
        target = min(adjacent_enemies, key=lambda e: (e.health, e.coords.distance_to(unit.coords)))
        return Action.attack(unit.coords.direction_to(target.coords))

    near_allies = [a for a in allies if unit.coords.distance_to(a.coords) <= RADIUS] + [unit]
    near_enemies = [e for e in enemies if unit.coords.distance_to(e.coords) <= RADIUS]

    nearest_enemy = min(enemies, key=lambda e: unit.coords.distance_to(e.coords))

    if near_enemies:
        ally_power = sum(a.health for a in near_allies)
        enemy_power = sum(e.health for e in near_enemies)

        if enemy_power > ally_power * RETREAT_RATIO:
            other_allies = [a for a in near_allies if a.id != unit.id]
            centroid = team_centroid(other_allies) if other_allies else None

            away_dir = unit.coords.direction_to(nearest_enemy.coords).opposite
            away_target = unit.coords + away_dir

            if centroid and centroid != unit.coords:
                toward_dir = unit.coords.direction_to(centroid)
                dist_now = unit.coords.distance_to(nearest_enemy.coords)
                dist_if_toward = (unit.coords + toward_dir).distance_to(nearest_enemy.coords)
                if dist_if_toward >= dist_now:
                    action = best_move_towards(state, unit, centroid, past_coords)
                    if action:
                        return action

            dest = unit.coords + away_dir
            if not state.obj_by_coords(dest):
                return Action.move(away_dir)
            for d in [away_dir.rotate_cw, away_dir.rotate_ccw]:
                dest = unit.coords + d
                if not state.obj_by_coords(dest):
                    return Action.move(d)
            return None

    return best_move_towards(state, unit, nearest_enemy.coords, past_coords)


# ---------------------------------------------------------------------------
# Lookahead logic
# ---------------------------------------------------------------------------

def _score(friends: Dict[Coords, int], enemies: Dict[Coords, int]):
    unit_score = len(friends) - len(enemies)
    health_score = sum(h ** 0.5 for h in friends.values()) - sum(h ** 0.5 for h in enemies.values())

    surround: Dict[Coords, int] = {c: 0 for c in friends}
    for c in enemies:
        surround[c] = 0
    dist: Dict[Coords, float] = {c: 0.0 for c in friends}
    for c in enemies:
        dist[c] = 0.0

    for fc in friends:
        fx, fy = fc.x, fc.y
        for ec in enemies:
            dx = fx - ec.x
            dy = fy - ec.y
            d2 = dx * dx + dy * dy
            if d2 == 0:
                continue
            d_score = 1.0 / d2
            dist[ec] += d_score
            dist[fc] -= d_score
            if d2 == 1:
                surround[ec] += 1
                surround[fc] -= 1

    surround_score = sum(v * v for v in surround.values())
    distance_score = sum(v * v for v in dist.values())
    return (unit_score, surround_score, health_score, distance_score)


def _cmp(a, b) -> int:
    for x, y in zip(a, b):
        if x != y:
            return 1 if x > y else -1
    return 0


def _tick(friends: Dict[Coords, int], enemies: Dict[Coords, int], actions: Dict[Coords, Any],
          wall_cache: Dict[Coords, bool], state: State):
    new_friends = dict(friends)
    new_enemies = dict(enemies)

    for src, act in actions.items():
        if act is None:
            continue
        atype, d = act
        if atype != 'm':
            continue
        target = src + d
        if target in new_friends or target in new_enemies:
            continue
        if _is_wall(state, target, wall_cache):
            continue
        if src in new_friends:
            h = new_friends.pop(src)
            new_friends[target] = h
        elif src in new_enemies:
            h = new_enemies.pop(src)
            new_enemies[target] = h

    for src, act in actions.items():
        if act is None:
            continue
        atype, d = act
        if atype != 'a':
            continue
        target = src + d
        if target in new_enemies:
            new_enemies[target] -= 1
        if target in new_friends:
            new_friends[target] -= 1

    new_friends = {c: h for c, h in new_friends.items() if h > 0}
    new_enemies = {c: h for c, h in new_enemies.items() if h > 0}
    return new_friends, new_enemies


def _is_wall(state: State, coords: Coords, wall_cache: Dict[Coords, bool]) -> bool:
    cached = wall_cache.get(coords)
    if cached is not None:
        return cached
    obj = state.obj_by_coords(coords)
    res = obj is not None and obj.obj_type == ObjType.Terrain
    wall_cache[coords] = res
    return res


def _compute_lookahead(state: State) -> Dict[str, Any]:
    allies = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)

    if not enemies or not allies:
        return {"fallback": False, "actions": {}}

    if len(allies) + len(enemies) > MAX_UNITS_FOR_LOOKAHEAD:
        return {"fallback": True}

    friends: Dict[Coords, int] = {a.coords: a.health for a in allies}
    enemy_hp: Dict[Coords, int] = {e.coords: e.health for e in enemies}

    # Sanity: duplicate coords shouldn't happen (engine prevents overlap),
    # but if for some odd reason our list construction collapsed two units
    # onto the same key, bail out to fallback rather than risk bad results.
    if len(friends) != len(allies) or len(enemy_hp) != len(enemies):
        return {"fallback": True}

    wall_cache: Dict[Coords, bool] = {}

    best_actions: Dict[Coords, Any] = {}

    # Predict enemy actions: each enemy attacks whichever adjacent friend has
    # the lowest health (mirrors our own "attack lowest-health adjacent
    # enemy" logic, and is what black-magic.js / many builtin bots do too).
    for ec in enemy_hp:
        best_actions[ec] = None
        lowest = None
        best_d = None
        for d in ALL_DIRS:
            t = ec + d
            if t in friends:
                h = friends[t]
                if lowest is None or h < lowest:
                    lowest = h
                    best_d = d
        if best_d is not None:
            best_actions[ec] = ('a', best_d)

    possible_actions: Dict[Coords, List[Any]] = {}
    for fc in friends:
        best_actions[fc] = None
        opts: List[Any] = [None]
        for d in ALL_DIRS:
            t = fc + d
            if t in enemy_hp:
                opts.append(('a', d))
            elif not _is_wall(state, t, wall_cache) and t not in friends:
                opts.append(('m', d))
        possible_actions[fc] = opts

    fs, es = _tick(friends, enemy_hp, best_actions, wall_cache, state)
    best_score = _score(fs, es)

    for fc in list(friends.keys()):
        actions = dict(best_actions)
        local_best_score = best_score
        local_best_action = actions.get(fc)
        # Track the best tie-breaking "move toward nearest enemy" candidate
        # separately (only used if no action strictly improves the score --
        # see comment below).
        tie_move_action = None
        tie_move_dist = None
        nearest_e = min(enemy_hp.keys(), key=lambda ec: fc.distance_to(ec)) if enemy_hp else None
        for act in possible_actions[fc]:
            actions[fc] = act
            fs, es = _tick(friends, enemy_hp, actions, wall_cache, state)
            s = _score(fs, es)
            cmp_result = _cmp(s, local_best_score)
            if cmp_result > 0:
                local_best_score = s
                local_best_action = act
            elif cmp_result == 0 and act is not None and act[0] == 'm' and nearest_e is not None:
                new_dist = (fc + act[1]).distance_to(nearest_e)
                if tie_move_dist is None or new_dist < tie_move_dist:
                    tie_move_dist = new_dist
                    tie_move_action = act
        if local_best_action is None and tie_move_action is not None:
            # Tie-break: if standing still scores exactly the same as
            # moving (e.g. no enemy in useful range so the lexicographic
            # score doesn't change either way), prefer moving toward the
            # nearest enemy over doing nothing. Fixes the "leaves
            # stragglers alive forever" quirk noted in round 8/9 notes
            # (a unit with no local score improvement available would
            # otherwise just sit still instead of chasing down a distant
            # straggler). Only kicks in on an exact tie, so it never
            # overrides an actual best-scoring action, and only picks the
            # move that most reduces distance to the nearest enemy (not an
            # arbitrary tied direction).
            local_best_action = tie_move_action
        actions[fc] = local_best_action
        best_actions = actions
        best_score = local_best_score

    # Convert to a coords -> action mapping restricted to friend coords only
    # (that's all robot() will ever look up).
    out_actions = {fc: best_actions.get(fc) for fc in friends}
    return {"fallback": False, "actions": out_actions}


def init_turn(state: State) -> None:
    global _turn_cache
    try:
        _turn_cache = _compute_lookahead(state)
    except Exception:
        _turn_cache = {"fallback": True}


def robot(state: State, unit: Obj) -> Optional[Action]:
    try:
        if not _turn_cache.get("fallback", True):
            act = _turn_cache.get("actions", {}).get(unit.coords)
            if act is None:
                return None
            atype, d = act
            if atype == 'a':
                return Action.attack(d)
            else:
                return Action.move(d)
    except Exception:
        pass
    return _fallback_robot(state, unit)
