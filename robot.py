# Fast coordinated one-ply tactical bot, adapted from the strong public
# black-magic bot. init_turn plans for all units together using an enemy model
# (adjacent enemies attack the lowest-health adjacent friend) and greedily keeps
# friendly actions that improve a lexicographic battle score.

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
    if TURN >= 60 and unit_score <= 0 and friends and enemies:
        for e, eh in enemies.items():
            best_d = 999.0
            for f in friends:
                d = dist(f, e)
                if d < best_d:
                    best_d = d
            # Low-health enemies are the most valuable to finish before turn 100.
            chase_score -= best_d * (1.0 + (5 - eh) * 0.08)

    # Small center/spawn term encourages units to leave spawn and meet the enemy instead of camping.
    center_score = 0.0
    cx, cy = CENTER
    for f in friends:
        dx = f[0] - cx
        dy = f[1] - cy
        center_score -= ((dx * dx + dy * dy) ** 0.5) * 0.03
    return (unit_score, surround_score, health_score, distance_score, chase_score, center_score)


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


def init_turn(state):
    global ACTIONS, TURN
    TURN = state.turn
    init_static()
    friends = {}
    enemies = {}
    id_at = {}
    for u in state.objs_by_team(state.our_team):
        if u.health is not None:
            pos = k(u.coords)
            friends[pos] = u.health
            id_at[pos] = u.id
    for u in state.objs_by_team(state.other_team):
        if u.health is not None:
            enemies[k(u.coords)] = u.health

    # Permit black-magic-style queued moves into friendly squares after the
    # opening. This fixed sampled losses vs mountain__neuralbot4-3h; delaying
    # until turn 20 preserves the safer opening that avoided Red flail regressions
    # seen when queueing was enabled unconditionally.
    allow_chain_moves = (state.turn >= 20)

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
            if dst not in LEGAL:
                continue
            if dst in enemies:
                acts.append((ATTACK, d))
            elif allow_chain_moves or dst not in friends:
                acts.append((MOVE, d))
        possible[fpos] = acts

    fs, es = tick(friends, enemies, best_actions)
    best_score = score(fs, es)

    # Greedily improve one friendly action at a time.
    for fpos in friends:
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


def robot(state, unit):
    action = ACTIONS.get(unit.id)
    if action is None:
        return None
    typ, d = action
    if typ == ATTACK:
        return Action.attack(d)
    return Action.move(d)
