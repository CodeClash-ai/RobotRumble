import math
from typing import Dict, List, Optional, Tuple, Set

ALL_DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]

def is_legal_coordinate(x: int, y: int) -> bool:
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

# Check if a coordinate belongs to the central Hill (3x3 grid)
def is_hill_coordinate(x: int, y: int) -> bool:
    return 8 <= x <= 10 and 8 <= y <= 10

def score(friends: Dict[Tuple[int, int], int], enemies: Dict[Tuple[int, int], int]) -> Tuple[float, float, float, float, float]:
    unit_score = len(friends) - len(enemies)

    health_score = 0.0
    for h in friends.values():
        health_score += math.pow(h, 0.5)
    for h in enemies.values():
        health_score -= math.pow(h, 0.5)

    # Control of the central 3x3 hill is highly valuable
    hill_control_score = 0.0
    for pos in friends:
        if is_hill_coordinate(pos[0], pos[1]):
            hill_control_score += 1.0
    for pos in enemies:
        if is_hill_coordinate(pos[0], pos[1]):
            hill_control_score -= 1.0

    map_score = {}
    for pos in friends:
        map_score[pos] = {"surround": 0, "distance": 0.0}
    for pos in enemies:
        map_score[pos] = {"surround": 0, "distance": 0.0}

    for f_pos in friends:
        fx, fy = f_pos
        for e_pos in enemies:
            ex, ey = e_pos
            # Use walking distance (Manhattan distance) for grid distance calculation
            d = abs(fx - ex) + abs(fy - ey)
            if d < 1:
                d = 1
            d_score = 1.0 / (d ** 2)
            map_score[e_pos]["distance"] += d_score
            map_score[f_pos]["distance"] -= d_score
            
            if d == 1:
                map_score[e_pos]["surround"] += 1
                map_score[f_pos]["surround"] -= 1

    surround_score = 0.0
    distance_score = 0.0
    for x in map_score.values():
        surround_score += math.pow(x["surround"], 2)
        distance_score += math.pow(x["distance"], 2)

    # Priority of criteria: Unit Differential > Hill Control > Surround Advantage > Health > Distance Positioning
    return (unit_score, hill_control_score, surround_score, health_score, distance_score)

def array_cmp(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
    for i in range(len(a)):
        diff = a[i] - b[i]
        if diff != 0:
            return diff
    return 0

def tick(friends: Dict[Tuple[int, int], int], enemies: Dict[Tuple[int, int], int], actions: Dict[Tuple[int, int], Optional[Tuple[str, Direction]]]):
    for source, action in list(actions.items()):
        if action is None:
            continue
        action_type, direction = action
        if action_type == "m":
            dx, dy = direction.to_coords.x, direction.to_coords.y
            target = (source[0] + dx, source[1] + dy)
            if target not in enemies and target not in friends and is_legal_coordinate(target[0], target[1]):
                if source in friends:
                    friends[target] = friends[source]
                    del friends[source]
                elif source in enemies:
                    enemies[target] = enemies[source]
                    del enemies[source]

    for source, action in list(actions.items()):
        if action is None:
            continue
        action_type, direction = action
        if action_type == "a":
            dx, dy = direction.to_coords.x, direction.to_coords.y
            target = (source[0] + dx, source[1] + dy)
            if target in enemies:
                enemies[target] -= 1
            if target in friends:
                friends[target] -= 1

    for enemy, h in list(enemies.items()):
        if h <= 0:
            del enemies[enemy]
    for friend, h in list(friends.items()):
        if h <= 0:
            del friends[friend]

ACTIONS: Dict[Tuple[int, int], Optional[Tuple[str, Direction]]] = {}

def init_turn(state: State) -> None:
    global ACTIONS
    ACTIONS = {}

    friends = {}
    for x in state.objs_by_team(state.our_team):
        friends[(x.coords.x, x.coords.y)] = x.health
    
    enemies = {}
    for x in state.objs_by_team(state.other_team):
        enemies[(x.coords.x, x.coords.y)] = x.health

    best_actions = {}

    for enemy in enemies:
        best_actions[enemy] = None
        lowest_health = 1000
        for direction in ALL_DIRECTIONS:
            dx, dy = direction.to_coords.x, direction.to_coords.y
            target = (enemy[0] + dx, enemy[1] + dy)
            if target not in friends:
                continue
            h = friends[target]
            if h > lowest_health:
                continue
            lowest_health = h
            best_actions[enemy] = ("a", direction)

    possible_actions = {}
    for friend in friends:
        best_actions[friend] = None
        possible_actions[friend] = [None]
        for direction in ALL_DIRECTIONS:
            dx, dy = direction.to_coords.x, direction.to_coords.y
            target = (friend[0] + dx, friend[1] + dy)
            if not is_legal_coordinate(target[0], target[1]):
                continue
            if target in enemies:
                possible_actions[friend].append(("a", direction))
            else:
                possible_actions[friend].append(("m", direction))

    fs = dict(friends)
    es = dict(enemies)
    tick(fs, es, best_actions)
    best_score = score(fs, es)

    for f in friends:
        actions = dict(best_actions)
        for a in possible_actions[f]:
            actions[f] = a
            fs = dict(friends)
            es = dict(enemies)
            tick(fs, es, actions)
            s = score(fs, es)
            if array_cmp(s, best_score) > 0:
                best_score = s
                best_actions = dict(actions)

    ACTIONS = best_actions

def robot(state: State, unit: Obj) -> Optional[Action]:
    pos = (unit.coords.x, unit.coords.y)
    best_action = ACTIONS.get(pos)

    if best_action is None:
        return None

    action_type, direction = best_action

    if action_type == "a":
        return Action.attack(direction)
    else:
        return Action.move(direction)
