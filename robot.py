# Coordinated one-ply tactical bot, ported/adapted from the strong "black-magic"
# public bot.  init_turn chooses actions for all our robots together by assuming
# enemies make their best adjacent attacks, then greedily improving each friendly
# action under a lexicographic battle-position score.

ATTACK = 'a'
MOVE = 'm'
DIRS = [Direction.North, Direction.East, Direction.South, Direction.West]
ACTIONS = {}


def k(c):
    return (c.x, c.y)


def ck(t):
    return Coords(t[0], t[1])


def add(t, d):
    c = ck(t) + d
    return (c.x, c.y)


def legal(t):
    x, y = t
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


def dist(a, b):
    return ck(a).distance_to(ck(b))


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
        for e in enemies:
            d = dist(f, e)
            if d == 0:
                continue
            ds = 1.0 / (d * d)
            pressure[e] = pressure.get(e, 0.0) + ds
            pressure[f] = pressure.get(f, 0.0) - ds
            if d == 1:
                surround[e] = surround.get(e, 0) + 1
                surround[f] = surround.get(f, 0) - 1

    surround_score = 0
    for v in surround.values():
        surround_score += v * v
    distance_score = 0.0
    for v in pressure.values():
        distance_score += v * v

    # Small center/spawn term encourages units to leave spawn and meet the enemy instead of camping.
    center_score = 0.0
    center = (10, 10)
    for f in friends:
        center_score -= dist(f, center) * 0.03
    return (unit_score, surround_score, health_score, distance_score, center_score)


def better(a, b):
    for i in range(len(a)):
        if a[i] != b[i]:
            return a[i] > b[i]
    return False


def tick(friends, enemies, actions):
    friends = dict(friends)
    enemies = dict(enemies)
    # Approximate movement.  This intentionally ignores simultaneous move conflicts just like
    # black-magic; the heuristic remains very effective and cheap.
    for src, action in actions.items():
        if action is None:
            continue
        typ, d = action
        if typ == MOVE:
            dst = add(src, d)
            if legal(dst) and dst not in friends and dst not in enemies:
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


def init_turn(state):
    global ACTIONS
    friends = {}
    enemies = {}
    id_at = {}
    for u in state.objs_by_team(state.our_team):
        if u.health is not None:
            friends[k(u.coords)] = u.health
            id_at[k(u.coords)] = u.id
    for u in state.objs_by_team(state.other_team):
        if u.health is not None:
            enemies[k(u.coords)] = u.health

    best_actions = {}
    # Enemy model: each adjacent enemy attacks our lowest-health adjacent unit.
    for epos in enemies:
        best_actions[epos] = None
        lowest = 999
        for d in DIRS:
            target = add(epos, d)
            if target in friends and friends[target] <= lowest:
                lowest = friends[target]
                best_actions[epos] = (ATTACK, d)

    possible = {}
    for fpos in friends:
        best_actions[fpos] = None
        acts = [None]
        for d in DIRS:
            dst = add(fpos, d)
            if not legal(dst):
                continue
            if dst in enemies:
                acts.append((ATTACK, d))
            elif dst not in friends:
                acts.append((MOVE, d))
        possible[fpos] = acts

    fs, es = tick(friends, enemies, best_actions)
    best_score = score(fs, es)

    # Greedily improve one friendly action at a time.
    for fpos in friends:
        chosen = best_actions.get(fpos)
        for act in possible[fpos]:
            trial = dict(best_actions)
            trial[fpos] = act
            fs, es = tick(friends, enemies, trial)
            s = score(fs, es)
            if better(s, best_score):
                best_score = s
                chosen = act
                best_actions = trial
        best_actions[fpos] = chosen

    ACTIONS = {}
    for pos, uid in id_at.items():
        ACTIONS[uid] = best_actions.get(pos)


def robot(state, unit):
    action = ACTIONS.get(unit.id)
    if action is None:
        return None
    typ, d = action
    if typ == ATTACK:
        return Action.attack(d)
    return Action.move(d)
