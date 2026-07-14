# Matchup bot for mousetail__coward-bot.
# Fast coordinated one-ply tactical bot, adapted from the strong public
# black-magic bot. init_turn plans for all units together using an exact-ish
# enemy model and greedily keeps friendly actions that improve a lexicographic
# battle score. The key counter is pre-firing coward-bot retreat/step destinations.

ATTACK = 'a'
MOVE = 'm'
DIRS = [Direction.North, Direction.East, Direction.South, Direction.West]
DIR_DELTAS = {}
LEGAL = set()
CENTER = (10, 10)
ACTIONS = {}
TURN = 0


def k(c):
    return (c.x, c.y)


def ck(t):
    return Coords(t[0], t[1])


def init_static():
    if DIR_DELTAS:
        return
    for d in DIRS:
        c = d.to_coords
        DIR_DELTAS[d] = (c.x, c.y)
    for x in range(1, 18):
        for y in range(1, 18):
            if y <= 5 - x:
                continue
            if y <= x - 13:
                continue
            if y >= x + 13:
                continue
            if y >= 31 - x:
                continue
            LEGAL.add((x, y))


def add(t, d):
    dx, dy = DIR_DELTAS[d]
    return (t[0] + dx, t[1] + dy)


def dist(a, b):
    # Same Euclidean metric as Coords.distance_to, but without object allocation.
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx * dx + dy * dy) ** 0.5


def score(friends, enemies):
    # Lexicographic: kills matter most, then surrounding, then health, then map pressure.
    unit_score = len(friends) - len(enemies)
    health_score = 0.0
    for h in friends.values():
        health_score += h ** 0.5
    for h in enemies.values():
        health_score -= h ** 0.5

    surround = {}
    pressure = {}
    for p in friends:
        surround[p] = 0
        pressure[p] = 0.0
    for p in enemies:
        surround[p] = 0
        pressure[p] = 0.0

    for f in friends:
        fx, fy = f
        for e in enemies:
            dx = fx - e[0]
            dy = fy - e[1]
            d2 = dx * dx + dy * dy
            if d2 == 0:
                continue
            ds = 1.0 / d2
            pressure[e] = pressure.get(e, 0.0) + ds
            pressure[f] = pressure.get(f, 0.0) - ds
            if d2 == 1:
                surround[e] = surround.get(e, 0) + 1
                surround[f] = surround.get(f, 0) - 1

    surround_score = 0
    for v in surround.values():
        surround_score += v * v
    distance_score = 0.0
    for v in pressure.values():
        distance_score += v * v

    # Late in the game, make non-contact movement chase surviving enemies instead of
    # merely drifting toward center.  This is deliberately below unit/surround/health/
    # pressure in the lexicographic score, so it only breaks otherwise quiet choices;
    # the goal is to convert close 100-turn unit-count ties into wins by catching
    # isolated stragglers without disturbing proven battle micro.
    chase_score = 0.0
    if TURN >= 35 and friends and enemies:
        # Stronger cleanup pressure for evasive/runaway opponents: reduce the
        # total distance from every surviving enemy to its nearest pursuer,
        # especially when we are behind/even on unit count late.  This remains
        # below unit count and health in the score tuple, so battle trades are
        # still dominated by survival and kills; it mostly changes quiet
        # mid/late-game movement that otherwise lets stragglers survive to turn 100.
        mult = 1.0 + max(0, -unit_score) * 0.35 + max(0, TURN - 70) * 0.02
        for e, eh in enemies.items():
            best_d = 999.0
            for f in friends:
                d = dist(f, e)
                if d < best_d:
                    best_d = d
            # Low-health enemies are the most valuable to finish before turn 100.
            chase_score -= best_d * mult * (1.0 + (5 - eh) * 0.10)

    # Small center/spawn term encourages units to leave spawn and meet the enemy instead of camping.
    center_score = 0.0
    cx, cy = CENTER
    for f in friends:
        dx = f[0] - cx
        dy = f[1] - cy
        center_score -= ((dx * dx + dy * dy) ** 0.5) * 0.03
    return (unit_score, health_score, surround_score, distance_score, chase_score, center_score)


def better(a, b):
    for i in range(len(a)):
        if a[i] != b[i]:
            return a[i] > b[i]
    return False


def tick(friends, enemies, actions):
    friends = dict(friends)
    enemies = dict(enemies)
    # Approximate movement. This intentionally ignores simultaneous move conflicts just like
    # black-magic; the heuristic remains very effective and cheap.
    for src, action in actions.items():
        if action is None:
            continue
        typ, d = action
        if typ == MOVE:
            dst = add(src, d)
            if dst in LEGAL and dst not in friends and dst not in enemies:
                if src in friends:
                    friends[dst] = friends[src]
                    del friends[src]
                elif src in enemies:
                    enemies[dst] = enemies[src]
                    del enemies[src]
    for src, action in actions.items():
        if action is None:
            continue
        typ, d = action
        if typ == ATTACK:
            dst = add(src, d)
            if src in friends:
                if dst in enemies:
                    enemies[dst] -= 1
                elif dst in friends:
                    friends[dst] -= 1
            elif src in enemies:
                if dst in friends:
                    friends[dst] -= 1
                elif dst in enemies:
                    enemies[dst] -= 1
    for p in list(friends.keys()):
        if friends[p] <= 0:
            del friends[p]
    for p in list(enemies.keys()):
        if enemies[p] <= 0:
            del enemies[p]
    return friends, enemies



def bm_score_side(friends, enemies):
    # Public black-magic score from one side's perspective, without our extra
    # center/chase tie-breakers.  Used only to predict the current opponent.
    unit_score = len(friends) - len(enemies)
    health_score = 0.0
    for h in friends.values():
        health_score += h ** 0.5
    for h in enemies.values():
        health_score -= h ** 0.5

    surround = {}
    pressure = {}
    for p in friends:
        surround[p] = 0
        pressure[p] = 0.0
    for p in enemies:
        surround[p] = 0
        pressure[p] = 0.0

    for f in friends:
        for e in enemies:
            dx = f[0] - e[0]
            dy = f[1] - e[1]
            d2 = dx * dx + dy * dy
            if d2 == 0:
                continue
            ds = 1.0 / d2
            pressure[e] = pressure.get(e, 0.0) + ds
            pressure[f] = pressure.get(f, 0.0) - ds
            if d2 == 1:
                surround[e] = surround.get(e, 0) + 1
                surround[f] = surround.get(f, 0) - 1

    surround_score = 0
    for v in surround.values():
        surround_score += v * v
    distance_score = 0.0
    for v in pressure.values():
        distance_score += v * v
    return (unit_score, surround_score, health_score, distance_score)


def predict_blackmagic_actions(opp_friends, opp_enemies):
    # Predict tabaxi3k__black-magic-1/public black-magic exactly enough to avoid
    # walking into its planned moves.  The opponent plans from the current board,
    # so these actions are fixed while we evaluate our own simultaneous choices.
    actions = {}

    for epos in opp_enemies:
        actions[epos] = None
        lowest_health = 1000
        for d in DIRS:
            target = add(epos, d)
            if target not in opp_friends:
                continue
            h = opp_friends[target]
            if h > lowest_health:
                continue
            lowest_health = h
            actions[epos] = (ATTACK, d)

    possible = {}
    for fpos in opp_friends:
        actions[fpos] = None
        acts = [None]
        for d in DIRS:
            dst = add(fpos, d)
            if dst not in LEGAL:
                continue
            if dst in opp_enemies:
                acts.append((ATTACK, d))
            else:
                acts.append((MOVE, d))
        possible[fpos] = acts

    fs, es = tick(opp_friends, opp_enemies, actions)
    best_score = bm_score_side(fs, es)

    for fpos in list(opp_friends):
        chosen = actions.get(fpos)
        for act in possible[fpos]:
            old = actions.get(fpos)
            actions[fpos] = act
            fs, es = tick(opp_friends, opp_enemies, actions)
            s = bm_score_side(fs, es)
            if better(s, best_score):
                best_score = s
                chosen = act
            else:
                actions[fpos] = old
        actions[fpos] = chosen

    return {p: actions.get(p) for p in opp_friends}



def t_direction_to(a, b):
    # Match Coords.direction_to without object allocation.
    import math
    angle = math.atan2(a[1] - b[1], a[0] - b[0])
    if abs(angle) <= math.pi / 4:
        return Direction.West
    elif abs(angle + math.pi / 2) <= math.pi / 4:
        return Direction.South
    elif abs(angle - math.pi / 2) <= math.pi / 4:
        return Direction.North
    else:
        return Direction.East


def t_walking(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def mitch_walk_tuple(src, target, occupied):
    x = target[0] - src[0]
    y = target[1] - src[1]
    xd = Direction.East if x > 0 else Direction.West
    yd = Direction.South if y > 0 else Direction.North
    blanks = []
    for d in _MDIRS:
        dst = add(src, d)
        if dst in LEGAL and dst not in occupied:
            blanks.append(d)
    if abs(x) > abs(y) and xd in blanks:
        return xd
    if abs(y) >= abs(x) and yd in blanks:
        return yd
    if xd in blanks:
        return xd
    if yd in blanks:
        return yd
    return blanks[0] if blanks else None


def predict_mitch_crw_actions(enemies, friends):
    # Exact-ish model of mitch84__crw_preempt from the opponent perspective.
    # Their units pick the closest of our units by (Manhattan distance, health),
    # retreat if outnumbered/overpowered adjacent, prefire at range <=2 when not
    # blocked by their own unit, otherwise greedily walk by Direction enum order.
    actions = {}
    occupied = set(enemies) | set(friends)
    for epos, eh in enemies.items():
        if not friends:
            actions[epos] = None
            continue
        closest = min(friends, key=lambda f: (t_walking(f, epos), friends[f]))
        blanks = []
        adj = []
        for d in _MDIRS:
            dst = add(epos, d)
            if dst in friends:
                adj.append(dst)
            elif dst in LEGAL and dst not in occupied:
                blanks.append(d)
        if blanks and (len(adj) > 1 or (len(adj) == 1 and friends[adj[0]] > eh)):
            actions[epos] = (MOVE, blanks[0])
            continue
        edir = t_direction_to(epos, closest)
        step = add(epos, edir)
        if t_walking(epos, closest) <= 2 and step not in enemies:
            actions[epos] = (ATTACK, edir)
            continue
        d = mitch_walk_tuple(epos, closest, occupied)
        actions[epos] = (MOVE, d) if d else None
    return actions


def is_spawn_t(pos):
    x, y = pos
    if x == 1 or x == 17 or y == 1 or y == 17:
        return True
    return pos in {(14,2),(13,2),(16,4),(16,5),(16,13),(16,14),(14,16),(13,16),(4,16),(5,16),(2,14),(2,13),(2,4),(4,2)}


def build_gloms(units):
    # Connected components of same-side units with walking distance < 3, as in entropicdrifter__glommer.
    positions = list(units.keys())
    gid = {}
    gloms = []
    for p in positions:
        if p in gid:
            continue
        idx = len(gloms)
        stack = [p]
        gid[p] = idx
        bots = []
        hp = 0
        while stack:
            q = stack.pop()
            bots.append(q)
            hp += units[q]
            for r in positions:
                if r not in gid and t_walking(q, r) < 3:
                    gid[r] = idx
                    stack.append(r)
        gloms.append({'bots': bots, 'health': hp})
    return gid, gloms


def glommer_retreat_dir(pos, hp, friends, enemies, claimed, turn):
    # Predict glommer's retreat rule from its perspective: friends=our units, enemies=their units.
    occupied = set(friends) | set(enemies)
    adj = []
    blanks = []
    for d in _MDIRS:
        dst = add(pos, d)
        if dst in friends:
            adj.append(dst)
        elif dst in LEGAL and dst not in occupied and dst not in claimed:
            cnt = 0
            for dd in _MDIRS:
                if add(dst, dd) in friends:
                    cnt += 1
            blanks.append((cnt, d, dst))
    blanks.sort(key=lambda x: x[0])
    if turn % 10 == 0:
        blanks = [b for b in blanks if not is_spawn_t(b[2])]
        if is_spawn_t(pos) and blanks:
            return blanks[0][1]
    if not blanks or not adj or len(adj) < blanks[0][0]:
        return None
    max_adj_h = max(friends[a] for a in adj) if adj else 0
    if len(adj) >= hp or max_adj_h > hp:
        return blanks[0][1]
    return None


def glommer_walk_dir(src, target, occupied, claimed):
    x = target[0] - src[0]
    y = target[1] - src[1]
    xd = Direction.East if x > 0 else Direction.West
    yd = Direction.South if y > 0 else Direction.North
    blanks = []
    for d in _MDIRS:
        dst = add(src, d)
        if dst in LEGAL and dst not in occupied and dst not in claimed:
            blanks.append(d)
    if abs(x) > abs(y) and xd in blanks:
        return xd
    if abs(y) >= abs(x) and yd in blanks:
        return yd
    if xd in blanks:
        return xd
    if yd in blanks:
        return yd
    return blanks[0] if blanks else None


def predict_glommer_actions(enemies, friends, turn):
    # Model entropicdrifter__glommer: cluster ("glom") with nearby allies, retreat from bad adjacent fights,
    # attack/push when its glom is larger/healthier, otherwise regroup toward other gloms/center.
    actions = {}
    if not enemies:
        return actions
    egid, egloms = build_gloms(enemies)
    fgid, fgloms = build_gloms(friends)
    claimed = set()
    occupied = set(enemies) | set(friends)
    for epos in list(enemies.keys()):
        eh = enemies[epos]
        if not friends:
            actions[epos] = None
            continue
        own = egloms[egid[epos]]
        # Target the closest opposing glom, then the closest bot inside that glom.
        seed_friend = min(friends, key=lambda f: t_walking(epos, f))
        target_glom = fgloms[fgid[seed_friend]] if fgloms else {'bots': list(friends), 'health': sum(friends.values())}
        target = min(target_glom['bots'], key=lambda f: t_walking(epos, f))
        nearest_friend = min(friends, key=lambda f: t_walking(epos, f))
        attack_dir = t_direction_to(epos, target)

        rd = glommer_retreat_dir(epos, eh, friends, enemies, claimed, turn)
        if rd:
            dst = add(epos, rd)
            claimed.add(dst)
            actions[epos] = (MOVE, rd)
            continue

        if t_walking(epos, nearest_friend) == 1 and friends[nearest_friend] < eh:
            actions[epos] = (ATTACK, t_direction_to(epos, nearest_friend))
            continue

        if len(target_glom['bots']) < len(own['bots']) or own['health'] > target_glom['health']:
            w = t_walking(epos, target)
            if (len(own['bots']) > 1 and w == 1) or (len(own['bots']) == 1 and w == 2):
                actions[epos] = (ATTACK, attack_dir)
                continue
            md = glommer_walk_dir(epos, target, occupied, claimed)
            if md and not glommer_retreat_dir(add(epos, md), eh, friends, enemies, claimed | {add(epos, md)}, turn):
                claimed.add(add(epos, md))
                actions[epos] = (MOVE, md)
                continue

        other_glom_bots = [q for q in enemies if egid.get(q) != egid[epos]]
        if other_glom_bots:
            ally = min(other_glom_bots, key=lambda q: t_walking(epos, q))
            md = glommer_walk_dir(epos, ally, occupied, claimed)
            if md and not glommer_retreat_dir(add(epos, md), eh, friends, enemies, claimed | {add(epos, md)}, turn):
                claimed.add(add(epos, md))
                actions[epos] = (MOVE, md)
                continue

        md = glommer_walk_dir(epos, (9, 9), occupied, claimed)
        if md and not glommer_retreat_dir(add(epos, md), eh, friends, enemies, claimed | {add(epos, md)}, turn):
            claimed.add(add(epos, md))
            actions[epos] = (MOVE, md)
            continue
        step = add(epos, attack_dir)
        if step in friends:
            actions[epos] = (ATTACK, attack_dir)
        else:
            actions[epos] = None
    return actions


def terrain_count(pos):
    # Number of adjacent impassable/out-of-board tiles; coward_bot confusingly names this
    # empty_surrounding_tiles and uses it to evacuate wall/spawn-adjacent units.
    c = 0
    for d in _MDIRS:
        if add(pos, d) not in LEGAL:
            c += 1
    return c


def coward_clockwise_dir(src, target):
    # Exact helper from mousetail__coward-bot.
    if src[0] == target[0]:
        return Direction.North if src[1] > target[1] else Direction.South
    if src[1] == target[1]:
        return Direction.West if src[0] > target[0] else Direction.East
    if src[1] > target[1] and src[0] > target[0]:
        return Direction.West
    if src[1] > target[1] and src[0] < target[0]:
        return Direction.North
    if src[1] < target[1] and src[0] < target[0]:
        return Direction.East
    if src[1] < target[1] and src[0] > target[0]:
        return Direction.South
    return Direction.West


def c_adjacent_enemy_count(pos, enemies):
    return sum(1 for d in _COWARD_DIRS if add(pos, d) in enemies)


def c_adjacent_friend_count(pos, friends):
    return sum(1 for d in _COWARD_DIRS if add(pos, d) in friends)


def c_corner_friend_count(pos, friends):
    x, y = pos
    return sum(1 for q in ((x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1)) if q in friends)


def coward_evasion_tile(pos, friends, enemies):
    # From opponent perspective: friends are coward units, enemies are our units.
    cand = []
    occupied = set(friends) | set(enemies)
    for d in _COWARD_DIRS:
        t = add(pos, d)
        if t not in LEGAL or t in occupied:
            continue
        if c_adjacent_enemy_count(t, enemies) != 0:
            continue
        cand.append(t)
    if not cand:
        return None
    return max(cand, key=lambda t: (-terrain_count(t), c_adjacent_friend_count(t, friends), -t_walking(t, (9,9))))


def predict_coward_actions(enemies, friends, turn):
    # Exact-ish model of mousetail__coward-bot from the opponent perspective.
    # It is a wall-averse / weak-fight-averse bot with range-2 prefire against
    # unscreened targets.  Modeling its retreats and planned destinations lets
    # our one-ply planner shoot where it will step instead of chasing old squares.
    actions = {}
    enemy_positions = list(enemies.keys())
    for epos in enemy_positions:
        eh = enemies[epos]
        if not friends:
            actions[epos] = None
            continue
        closest_enemy = min(friends, key=lambda f: (t_walking(f, epos), -c_corner_friend_count(f, enemies)-c_adjacent_friend_count(f, enemies), friends[f]))
        other_allies = [q for q in enemy_positions if q != epos]
        closest_ally = min(other_allies, key=lambda q: (t_walking(q, epos), enemies[q])) if other_allies else None
        direction_to_center = coward_clockwise_dir(epos, (9,9))
        ev = coward_evasion_tile(epos, enemies, friends)

        if (c_adjacent_enemy_count(epos, friends) > 1 and
            friends[closest_enemy] >= c_adjacent_friend_count(closest_enemy, enemies) and ev is not None):
            actions[epos] = (MOVE, t_direction_to(epos, ev))
            continue

        if terrain_count(epos) >= 1 and (ev is not None or turn % 10 == 0):
            if ev is not None:
                actions[epos] = (MOVE, t_direction_to(epos, ev))
            elif add(epos, direction_to_center) in friends:
                actions[epos] = (ATTACK, direction_to_center)
            else:
                actions[epos] = (MOVE, direction_to_center)
            continue

        if eh >= friends[closest_enemy]:
            direction = coward_clockwise_dir(epos, closest_enemy)
            ed = t_walking(epos, closest_enemy)
            if ed >= 5:
                if closest_ally is not None and 2 < t_walking(epos, closest_ally) <= 8:
                    direction = t_direction_to(epos, closest_ally)
                else:
                    direction = t_direction_to(epos, (9,9))
                actions[epos] = (MOVE, direction)
                continue
            if (ed <= 2 and (ed == 1 or (c_adjacent_friend_count(closest_enemy, enemies) == 0 and c_corner_friend_count(closest_enemy, enemies) < 3))
                and add(epos, direction) not in enemies):
                actions[epos] = (ATTACK, direction)
                continue
            elif ed > 1 and terrain_count(closest_enemy) == 0:
                if add(epos, direction) in enemies:
                    direction = direction.rotate_ccw
                actions[epos] = (MOVE, direction)
                continue
            else:
                actions[epos] = (ATTACK, direction)
                continue

        elif t_walking(epos, closest_enemy) <= 3:
            direction = t_direction_to(closest_enemy, epos)  # flee away from closest enemy
            if add(epos, direction) in enemies and t_walking(epos, closest_enemy) == 1:
                actions[epos] = (ATTACK, t_direction_to(epos, closest_enemy))
            elif c_adjacent_enemy_count(add(epos, direction), friends) == 0:
                actions[epos] = (MOVE, direction)
            else:
                actions[epos] = (ATTACK, direction.opposite)
            continue
        else:
            target = closest_ally if closest_ally is not None else (9,9)
            actions[epos] = (MOVE, coward_clockwise_dir(epos, target))
    return actions

def init_turn(state):
    global ACTIONS, TURN
    TURN = state.turn
    init_static()
    friends = {}
    enemies = {}
    id_at = {}
    spawn_positions = set()
    for u in state.objs_by_team(state.our_team):
        if u.health is not None:
            pos = k(u.coords)
            friends[pos] = u.health
            id_at[pos] = u.id
            if u.coords.is_spawn():
                spawn_positions.add(pos)
    for u in state.objs_by_team(state.other_team):
        if u.health is not None:
            enemies[k(u.coords)] = u.health

    # Current opponent is mousetail__coward-bot; allow queued/chain moves,
    # but seed the simulation with its deterministic evade/prefire plan.
    allow_chain_moves = True

    enemy_plan = dict(predict_coward_actions(enemies, friends, state.turn))
    predicted_enemy_dests = set()
    for _ep, _act in enemy_plan.items():
        if _act and _act[0] == MOVE:
            predicted_enemy_dests.add(add(_ep, _act[1]))
    best_actions = dict(enemy_plan)

    possible = {}
    spawn_danger = (state.turn % 10 == 0)
    for fpos in friends:
        best_actions[fpos] = None
        acts = [None]
        evacuate = []
        for d in DIRS:
            dst = add(fpos, d)
            if dst not in LEGAL:
                continue
            if spawn_danger and fpos in spawn_positions:
                # Spawn squares are cleared every 10 turns after actions. Prefer
                # a guaranteed immediate step out of spawn over attacking/passing.
                if dst not in spawn_positions and dst not in enemies and dst not in friends:
                    evacuate.append((MOVE, d))
                continue
            if dst in enemies or dst in predicted_enemy_dests:
                # Coward-bot often retreats or pre-fires from range 2; pre-fire the
                # square it is expected to enter, not just its current square.
                acts.append((ATTACK, d))
            if dst not in enemies and (allow_chain_moves or dst not in friends):
                acts.append((MOVE, d))
        possible[fpos] = evacuate if evacuate else acts

    fs, es = tick(friends, enemies, best_actions)
    best_score = score(fs, es)

    # Greedily improve one friendly action at a time.  For this black-magic
    # mirror, use the normal public order.  A previous dual normal/reverse pass
    # optimized our imperfect one-ply score but locally lost official-bad mirror
    # seeds; the normal order is faster and performed better on sampled bads.
    for fpos in list(friends):
        chosen = best_actions.get(fpos)
        for act in possible[fpos]:
            old = best_actions.get(fpos)
            best_actions[fpos] = act
            fs, es = tick(friends, enemies, best_actions)
            s = score(fs, es)
            if better(s, best_score):
                best_score = s
                chosen = act
            else:
                best_actions[fpos] = old
        best_actions[fpos] = chosen

    ACTIONS = {}
    for pos, uid in id_at.items():
        ACTIONS[uid] = best_actions.get(pos)



def endgame_swarm_action(state, unit):
    # Matchup-specific cleanup for coward-bot: official remaining losses are
    # turn-100 unit-count losses where we trail and must kill stragglers fast.
    # From turn 70, if behind/even on units, use direct range-2 focus fire and
    # nearest-enemy chase instead of the conservative one-ply formation score.
    if state.turn < 70:
        return None
    friends = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)
    if not enemies or len(friends) > len(enemies):
        return None
    # Attack the weakest enemy in directional range 1-2, preferring true adjacent.
    shots = []
    for e in enemies:
        d = unit.coords.direction_to(e.coords)
        if d is None:
            continue
        step = unit.coords + d
        if step == e.coords or step + d == e.coords:
            block = state.obj_by_coords(step)
            if not (block is not None and block.team == state.our_team):
                shots.append((unit.coords.walking_distance_to(e.coords), e.health, d))
    if shots:
        shots.sort(key=lambda x: (x[0] > 1, x[1], x[0]))
        return Action.attack(shots[0][2])
    target = min(enemies, key=lambda e: (unit.coords.walking_distance_to(e.coords), e.health))
    d = unit.coords.direction_to(target.coords)
    if d is not None:
        dst = unit.coords + d
        if state.obj_by_coords(dst) is None:
            return Action.move(d)
    return None

def robot(state, unit):
    eg = endgame_swarm_action(state, unit)
    if eg is not None:
        return eg
    action = ACTIONS.get(unit.id)
    if action is None:
        return None
    typ, d = action
    if typ == ATTACK:
        return Action.attack(d)
    return Action.move(d)


_MDIRS=[Direction.North, Direction.South, Direction.East, Direction.West]
_COWARD_DIRS=[Direction.South, Direction.North, Direction.West, Direction.East]
def _mwalk(state, a, b):
    x=b.x-a.x; y=b.y-a.y
    xd=Direction.East if x>0 else Direction.West; yd=Direction.South if y>0 else Direction.North
    blanks=[d for d in _MDIRS if not state.obj_by_coords(a+d)]
    if abs(x)>abs(y) and xd in blanks: return xd
    if abs(y)>=abs(x) and yd in blanks: return yd
    if xd in blanks: return xd
    if yd in blanks: return yd
    return blanks[0] if blanks else None
def _pred(state,e):
    friends=state.objs_by_team(state.our_team)
    adj=[]; blanks=[]
    for d in _MDIRS:
        o=state.obj_by_coords(e.coords+d)
        if o and o.team==state.our_team: adj.append(o)
        elif not o: blanks.append(d)
    if blanks and (len(adj)>1 or (len(adj)==1 and adj[0].health>e.health)): return e.coords+blanks[0]
    if not friends: return e.coords
    c=min(friends,key=lambda f:(f.coords.walking_distance_to(e.coords),f.health))
    if e.coords.walking_distance_to(c.coords)<=2: return e.coords
    d=_mwalk(state,e.coords,c.coords)
    return e.coords+d if d else e.coords
_old_robot=robot
def robot(state, unit):
    # If no adjacent enemy, take a safe preemptive shot at a predicted adjacent destination.
    if not any((state.obj_by_coords(unit.coords+d) and state.obj_by_coords(unit.coords+d).team==state.other_team) for d in _MDIRS):
        cand=[]
        for e in state.objs_by_team(state.other_team):
            dest=_pred(state,e)
            if unit.coords.walking_distance_to(dest)==1:
                d=unit.coords.direction_to(dest); block=state.obj_by_coords(unit.coords+d) if d else None
                if d and not (block and block.team==state.our_team): cand.append((e.health,e.coords.walking_distance_to(unit.coords),d))
        if cand:
            cand.sort(key=lambda x:(x[0],x[1])); return Action.attack(cand[0][2])
    return _old_robot(state, unit)


# Final override for the coward matchup: use the coordinated plan directly, with late all-in cleanup.
def robot(state, unit):
    eg = endgame_swarm_action(state, unit)
    if eg is not None:
        return eg
    action = ACTIONS.get(unit.id)
    if action is None:
        return None
    typ, d = action
    if typ == ATTACK:
        return Action.attack(d)
    return Action.move(d)
