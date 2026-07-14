# Team gpt-5-5 RobotRumble bot.
#
# One-ply tactical planner adapted from the strong builtin black-magic bot, with
# small spawn-wipe safety.  Each turn, init_turn builds a coordinate-based board,
# predicts obvious enemy attacks, then greedily chooses each friendly action that
# gives the best simulated lexicographic score: unit advantage, surround pattern,
# health, and army closeness.  robot() only returns the precomputed action.

ATTACK = 1
MOVE = 2
ALL_DIRS = [Direction.North, Direction.East, Direction.South, Direction.West]

DIR_DELTAS = None
ACTIONS = {}
LEGAL = None
SPAWNS = None
INV_D2 = {}


def _setup():
    global DIR_DELTAS, LEGAL, SPAWNS, INV_D2
    if DIR_DELTAS is None:
        DIR_DELTAS = {d: (d.to_coords.x, d.to_coords.y) for d in ALL_DIRS}
    if LEGAL is None:
        legal = set()
        spawns = set()
        coords = {}
        for x in range(1, 18):
            for y in range(1, 18):
                # The playable board is a 19x19 octagon with walls around it.
                if y <= 5 - x:
                    continue
                if y <= x - 13:
                    continue
                if y >= x + 13:
                    continue
                if y >= 31 - x:
                    continue
                key = (x, y)
                legal.add(key)
                c = Coords(x, y)
                coords[key] = c
                # Avoid Coords.is_spawn() here: the bundled Python stdlib stores
                # spawn strings in a one-shot map iterator, so repeated calls can
                # silently miss most spawn tiles.  Spawn points are exactly the
                # legal cells cardinally adjacent to the octagonal wall ring.
                if (x == 1 or x == 17 or y == 1 or y == 17 or
                    y == 6 - x or y == x - 12 or y == x + 12 or y == 30 - x):
                    spawns.add(key)
        LEGAL = legal
        SPAWNS = spawns

        # Precompute 1/euclidean_distance^2 between legal cells.  The tactical
        # score calls this many times; table lookup is much faster in RustPython.
        for a in coords:
            row = {}
            ax, ay = a
            for b in coords:
                if a != b:
                    dx = ax - b[0]
                    dy = ay - b[1]
                    row[b] = 1.0 / (dx * dx + dy * dy)
            INV_D2[a] = row


def _add(c, d):
    dx, dy = DIR_DELTAS[d]
    return (c[0] + dx, c[1] + dy)


CURRENT_TURN = 0

def _score(friends, enemies):
    """Return lexicographic board score from our point of view."""
    unit_score = len(friends) - len(enemies)

    friend_health_score = 0.0
    for h in friends.values():
        friend_health_score += h ** 0.5
    health_score = friend_health_score
    for h in enemies.values():
        health_score -= h ** 0.5

    surround = {c: 0 for c in friends}
    distv = {c: 0.0 for c in friends}
    for c in enemies:
        surround[c] = 0
        distv[c] = 0.0

    for f in friends:
        invrow = INV_D2[f]
        fx, fy = f
        for e in enemies:
            ds = invrow[e]
            distv[e] += ds
            distv[f] -= ds
            # Squared Euclidean distance 1 is exactly cardinal adjacency.
            if (fx - e[0]) * (fx - e[0]) + (fy - e[1]) * (fy - e[1]) == 1:
                surround[e] += 1
                surround[f] -= 1

    surround_score = 0
    for v in surround.values():
        surround_score += v * v
    distance_score = 0.0
    for v in distv.values():
        distance_score += v * v

    if CURRENT_TURN >= 60 and unit_score < 0:
        # In close late games against strong neural/scatter opponents we were
        # sometimes choosing HP-preserving moves even when the one-ply result
        # was behind on units.  Unit count is the only win condition, so in
        # those losing branches fall back to the original black-magic pressure
        # order to favor surrounding/converting damaged enemy bodies.
        return (unit_score, surround_score, health_score, distance_score)
    if CURRENT_TURN >= 95 and unit_score == 0 and health_score <= 0:
        # If the match is about to end tied on units and we are not ahead on
        # total sqrt-health, keep unit count primary but next prefer lowering
        # enemy HP so close endgames can convert before turn 100.
        # (health_score - friend_health_score) is exactly -enemy_sqrt-health.
        enemy_health_score = health_score - friend_health_score
        return (unit_score, enemy_health_score, health_score, friend_health_score, surround_score, distance_score)
    if CURRENT_TURN >= 85:
        return (unit_score, friend_health_score, health_score, surround_score, distance_score)
    if CURRENT_TURN >= 60:
        return (unit_score, health_score, surround_score, distance_score)
    return (unit_score, surround_score, health_score, distance_score)


def _tick(friends, enemies, actions):
    """Simplified one-turn simulator.  Mutates friends/enemies."""
    for source, action in actions.items():
        if action is None or action[0] != MOVE:
            continue
        target = _add(source, action[1])
        if target in LEGAL and target not in friends and target not in enemies:
            if source in friends:
                friends[target] = friends[source]
                del friends[source]
            elif source in enemies:
                enemies[target] = enemies[source]
                del enemies[source]

    for source, action in actions.items():
        if action is None or action[0] != ATTACK:
            continue
        target = _add(source, action[1])
        if target in enemies:
            enemies[target] -= 1
        if target in friends:
            friends[target] -= 1

    dead = [c for c, h in enemies.items() if h <= 0]
    for c in dead:
        del enemies[c]
    dead = [c for c, h in friends.items() if h <= 0]
    for c in dead:
        del friends[c]


def init_turn(state):
    global ACTIONS, CURRENT_TURN
    _setup()
    CURRENT_TURN = state.turn

    friends = {}
    id_at = {}
    for u in state.objs_by_team(state.our_team):
        k = (u.coords.x, u.coords.y)
        friends[k] = u.health
        id_at[k] = u.id

    enemies = {}
    for u in state.objs_by_team(state.other_team):
        enemies[(u.coords.x, u.coords.y)] = u.health

    best_actions = {}

    # Enemy model: adjacent enemies attack our lowest-health adjacent unit.
    for e in enemies:
        best = None
        lowest = 999
        for d in ALL_DIRS:
            h = friends.get(_add(e, d))
            if h is not None and h <= lowest:
                lowest = h
                best = (ATTACK, d)
        best_actions[e] = best

    possible = {}
    avoid_spawn = (state.turn % 10 == 0)
    for f in friends:
        best_actions[f] = None
        acts = [None]
        for d in ALL_DIRS:
            t = _add(f, d)
            if t not in LEGAL:
                continue
            if t in enemies:
                acts.append((ATTACK, d))
            elif not (avoid_spawn and t in SPAWNS):
                acts.append((MOVE, d))
        possible[f] = acts

    fs = dict(friends)
    es = dict(enemies)
    _tick(fs, es, best_actions)
    best_score = _score(fs, es)

    # Greedily improve one friendly action at a time against predicted enemies.
    for f in list(friends.keys()):
        chosen = best_actions.get(f)
        for a in possible[f]:
            if a == chosen:
                continue
            actions = dict(best_actions)
            actions[f] = a
            fs = dict(friends)
            es = dict(enemies)
            _tick(fs, es, actions)
            s = _score(fs, es)
            if s > best_score:
                best_score = s
                best_actions = actions
                chosen = a

    ACTIONS = {}
    for c, uid in id_at.items():
        ACTIONS[uid] = best_actions.get(c)


def robot(state, unit):
    action = ACTIONS.get(unit.id)
    if action is None:
        return None
    if action[0] == ATTACK:
        return Action.attack(action[1])
    return Action.move(action[1])
