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
    if TURN >= 45 and friends and enemies:
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

    # Permit black-magic-style queued moves into friendly squares after the
    # opening. This fixed sampled losses vs mountain__neuralbot4-3h; delaying
    # until turn 20 preserves the safer opening that avoided Red flail regressions
    # seen when queueing was enabled unconditionally.
    allow_chain_moves = (state.turn >= 20)

    best_actions = {}

    def tuple_direction_to(src, dst):
        # Exact Coords.direction_to quadrant/tie behavior without atan2.
        vx = dst[0] - src[0]
        vy = dst[1] - src[1]
        if vx < 0 and -vx >= abs(vy):
            return Direction.West
        if vy > 0 and vy >= abs(vx):
            return Direction.South
        if vy < 0 and -vy >= abs(vx):
            return Direction.North
        if vx > 0:
            return Direction.East
        return None

    def tuple_in_spawn(pos, turn_offset=0):
        # Jammy's bot evacuates terrain-adjacent spawn squares only on clearing
        # turns. Approximate terrain with off-board/illegal adjacent cells; use the opponent's Direction iteration order when choosing an exit.
        if (state.turn + turn_offset) % 10 != 0:
            return False
        for d in DIRS:
            if add(pos, d) not in LEGAL:
                return True
        return False

    # Opponent model for current mitch84__walk_retreat matchup.  Their bot:
    #   * retreats to the first blank Direction (N,S,E,W enum order) when more
    #     than one enemy is adjacent;
    #   * otherwise attacks the closest enemy only when Euclidean distance == 1;
    #   * otherwise walks toward the closest enemy, choosing an unoccupied step
    #     on the larger axis (with first-blank fallback).
    # Modeling this simple chaser is much safer here than the older Jammy-specific
    # prefire model, which predicted attacks at range 2 and badly overestimated
    # the current opponent's tactical reach.
    def first_blank_around(pos):
        blanks = []
        for d in (Direction.North, Direction.South, Direction.East, Direction.West):
            dst = add(pos, d)
            if dst in LEGAL and dst not in friends and dst not in enemies:
                blanks.append(d)
        return blanks

    for epos, eh in enemies.items():
        best_actions[epos] = None
        if not friends:
            continue
        blanks = first_blank_around(epos)
        adjacent_friends = 0
        for d in (Direction.North, Direction.South, Direction.East, Direction.West):
            if add(epos, d) in friends:
                adjacent_friends += 1
        if adjacent_friends > 1 and blanks:
            best_actions[epos] = (MOVE, blanks[0])
            continue

        # Python min preserves state object order on ties; use tuple order as a
        # deterministic approximation.  Walking distance is Manhattan distance.
        target = min(friends, key=lambda f: abs(f[0] - epos[0]) + abs(f[1] - epos[1]))
        dx = target[0] - epos[0]
        dy = target[1] - epos[1]
        if dx * dx + dy * dy == 1:
            edir = tuple_direction_to(epos, target)
            if edir is not None:
                best_actions[epos] = (ATTACK, edir)
            continue

        xdir = Direction.East if dx > 0 else Direction.West
        ydir = Direction.South if dy > 0 else Direction.North
        if abs(dx) > abs(dy) and xdir in blanks:
            best_actions[epos] = (MOVE, xdir)
        elif abs(dy) >= abs(dx) and ydir in blanks:
            best_actions[epos] = (MOVE, ydir)
        elif xdir in blanks:
            best_actions[epos] = (MOVE, xdir)
        elif ydir in blanks:
            best_actions[epos] = (MOVE, ydir)
        elif blanks:
            best_actions[epos] = (MOVE, blanks[0])

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
            if dst in enemies:
                acts.append((ATTACK, d))
            elif allow_chain_moves or dst not in friends:
                acts.append((MOVE, d))
        possible[fpos] = evacuate if evacuate else acts

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
