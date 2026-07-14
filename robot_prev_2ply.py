from typing import *
import math

# RobotRumble bot - Normal mode. Black-magic-style greedy 1-ply best-response.
# Rules: UNIT_HEALTH=5, ATTACK_POWER=1, attacks stack; movement resolves
# before attacks (attacks hit a CELL). Winner = most units alive at end.

DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]
MAX_HP = 5

SPAWN_CELLS = frozenset([
    (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12), (1, 13),
    (2, 4), (2, 14), (3, 3), (3, 15), (4, 2), (4, 16), (5, 1), (5, 17),
    (6, 1), (6, 17), (7, 1), (7, 17), (8, 1), (8, 17), (9, 1), (9, 17),
    (10, 1), (10, 17), (11, 1), (11, 17), (12, 1), (12, 17), (13, 1), (13, 17),
    (14, 2), (14, 16), (15, 3), (15, 15), (16, 4), (16, 14),
    (17, 5), (17, 6), (17, 7), (17, 8), (17, 9), (17, 10), (17, 11), (17, 12), (17, 13),
])

DXY = {Direction.North: (0, -1), Direction.South: (0, 1),
       Direction.East: (1, 0), Direction.West: (-1, 0)}


def legal_xy(x, y):
    if x <= 0 or x > 17 or y <= 0 or y > 17:
        return False
    if y <= 5 - x:
        return False
    if y <= x - 13:
        return False
    if y >= x + 13:
        return False
    if y >= 31 - x:
        return False
    return True


# ---- greedy best-response scorer (mirrors black-magic) ----
# friends/enemies are dicts: (x,y) -> health

def score(friends, enemies):
    unit_score = len(friends) - len(enemies)
    health_score = 0.0
    for h in friends.values():
        health_score += math.sqrt(h)
    for h in enemies.values():
        health_score -= math.sqrt(h)
    # map score: surround + distance
    surr = {}
    dist = {}
    for k in friends:
        surr[k] = 0.0; dist[k] = 0.0
    for k in enemies:
        surr[k] = 0.0; dist[k] = 0.0
    fkeys = list(friends.keys())
    ekeys = list(enemies.keys())
    for f in fkeys:
        fx, fy = f
        for e in ekeys:
            ex, ey = e
            d = math.hypot(fx - ex, fy - ey)
            if d == 0:
                d = 0.5
            ds = 1.0 / (d * d)
            dist[e] += ds
            dist[f] -= ds
            if abs(fx - ex) + abs(fy - ey) == 1:
                surr[e] += 1
                surr[f] -= 1
    surround_score = 0.0
    distance_score = 0.0
    for k in enemies:
        # enemies surrounded by us: reward (surr[k] positive)
        surround_score += surr[k] * surr[k]
        distance_score += dist[k] * dist[k]
    for k in friends:
        # our units surrounded by enemies: penalize (surr[k] negative)
        surround_score -= surr[k] * surr[k]
        distance_score -= dist[k] * dist[k]
    # HUNT tiebreak: gently pull our units toward their nearest enemy so that
    # 'free' units (no enemy near) peel off to chase scattered fleers. Lowest
    # priority (only breaks otherwise-equal moves), so it never sacrifices trades.
    hunt_score = 0.0
    for f in fkeys:
        fx, fy = f
        md = 1e9
        for e in ekeys:
            ex, ey = e
            dd = abs(fx - ex) + abs(fy - ey)
            if dd < md:
                md = dd
        if md < 1e9:
            hunt_score -= md
    return (unit_score, surround_score, health_score, distance_score, hunt_score)


def apply_tick(friends, enemies, actions, enemy_actions):
    # actions: source(x,y) -> ('m',dx,dy) or ('a',dx,dy) or None  (our units)
    # enemy_actions: same for enemies
    f = dict(friends)
    e = dict(enemies)
    # movement phase (friends then enemies), respecting occupancy at resolution
    def do_moves(mine, other, acts):
        moved = {}
        for src, act in acts.items():
            if act is None or act[0] != 'm':
                continue
            dx, dy = act[1], act[2]
            tx, ty = src[0] + dx, src[1] + dy
            tgt = (tx, ty)
            if tgt in mine or tgt in other or tgt in moved:
                continue
            if not legal_xy(tx, ty):
                continue
            moved[src] = tgt
        for src, tgt in moved.items():
            mine[tgt] = mine.pop(src)
    do_moves(f, e, actions)
    do_moves(e, f, enemy_actions)
    # attack phase
    for src, act in list(actions.items()):
        if act is None or act[0] != 'a':
            continue
        tx, ty = src[0] + act[1], src[1] + act[2]
        t = (tx, ty)
        if t in e:
            e[t] -= 1
        elif t in f:
            f[t] -= 1
    for src, act in list(enemy_actions.items()):
        if act is None or act[0] != 'a':
            continue
        tx, ty = src[0] + act[1], src[1] + act[2]
        t = (tx, ty)
        if t in f:
            f[t] -= 1
        elif t in e:
            e[t] -= 1
    f = {k: v for k, v in f.items() if v > 0}
    e = {k: v for k, v in e.items() if v > 0}
    return f, e


ACTIONS = {}  # (x,y) -> Direction-based Action tuple


def init_turn(state):
    global ACTIONS
    ACTIONS = {}
    friends = {}
    for o in state.objs_by_team(state.our_team):
        friends[(o.coords.x, o.coords.y)] = o.health
    enemies = {}
    for o in state.objs_by_team(state.other_team):
        enemies[(o.coords.x, o.coords.y)] = o.health
    if not enemies or not friends:
        return

    clearing_next = (state.turn % 10 == 0)

    # predicted enemy actions: each enemy attacks adjacent friend with lowest hp
    enemy_actions = {}
    for e in enemies:
        best = None; lowh = 1e9
        for d, (dx, dy) in DXY.items():
            t = (e[0] + dx, e[1] + dy)
            if t in friends and friends[t] < lowh:
                lowh = friends[t]; best = ('a', dx, dy)
        enemy_actions[e] = best

    # possible actions per friend
    poss = {}
    for f in friends:
        opts = [None]
        for d, (dx, dy) in DXY.items():
            tx, ty = f[0] + dx, f[1] + dy
            t = (tx, ty)
            if not legal_xy(tx, ty):
                continue
            if t in enemies:
                opts.append(('a', dx, dy))
            elif t not in friends:
                opts.append(('m', dx, dy))
        poss[f] = opts

    # start: our units all attack lowest-hp adjacent enemy (like bm default)
    best_actions = {}
    for f in friends:
        best = None; lowh = 1e9
        for d, (dx, dy) in DXY.items():
            t = (f[0] + dx, f[1] + dy)
            if t in enemies and enemies[t] < lowh:
                lowh = enemies[t]; best = ('a', dx, dy)
        best_actions[f] = best

    def spawn_pen(actions):
        # penalty for our units ending on spawn cells before a clear
        if not clearing_next:
            return 0.0
        pen = 0.0
        for src, act in actions.items():
            if act is not None and act[0] == 'm':
                pos = (src[0] + act[1], src[1] + act[2])
            elif act is None or act[0] == 'a':
                pos = src
            else:
                pos = src
            if pos in SPAWN_CELLS:
                pen += 1.0
        return pen

    fs, es = apply_tick(friends, enemies, best_actions, enemy_actions)
    best_score = score(fs, es)
    best_pen = spawn_pen(best_actions)

    # greedy: iterate units, pick best single action given others fixed.
    # Two sweeps allow units to coordinate (2nd sweep refines given 1st).
    for _sweep in range(2):
        for f in friends:
            cur = dict(best_actions)
            for a in poss[f]:
                cur[f] = a
                fs, es = apply_tick(friends, enemies, cur, enemy_actions)
                s = score(fs, es)
                p = spawn_pen(cur)
                if (s[0], -p, s[1], s[2], s[3], s[4]) > (best_score[0], -best_pen,
                                                   best_score[1], best_score[2], best_score[3], best_score[4]):
                    best_score = s
                    best_pen = p
                    best_actions = dict(cur)

    # convert to Action objects keyed by coords
    for src, act in best_actions.items():
        if act is None:
            ACTIONS[src] = None
            continue
        dx, dy = act[1], act[2]
        for d, v in DXY.items():
            if v == (dx, dy):
                if act[0] == 'a':
                    ACTIONS[src] = Action.attack(d)
                else:
                    ACTIONS[src] = Action.move(d)
                break


def robot(state, unit):
    key = (unit.coords.x, unit.coords.y)
    return ACTIONS.get(key, None)
