from typing import *

# Round-1 strategy: survival wins Normal mode.  The engine deletes units still
# on spawn tiles before reinforcements at turns 11,21,...; the default/opponent
# seen in logs never leaves spawn and therefore ties at 4-4 forever.  This bot
# immediately steps every robot off the spawn ring, then forms a loose interior
# annulus, attacks adjacent enemies, and only chases very nearby targets.

CENTER = Coords(9, 9)
DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]
reserved_moves: Set[Coords] = set()


def init_turn(state: State) -> None:
    global reserved_moves
    reserved_moves = set()


def in_bounds(c: Coords) -> bool:
    return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE


def is_free(state: State, c: Coords) -> bool:
    return in_bounds(c) and c not in reserved_moves and state.obj_by_coords(c) is None


def enemy_at(state: State, c: Coords) -> Optional[Obj]:
    obj = state.obj_by_coords(c)
    if obj and obj.team == state.other_team:
        return obj
    return None


def adjacent_enemy_direction(state: State, unit: Obj) -> Optional[Direction]:
    choices = []
    for d in DIRECTIONS:
        e = enemy_at(state, unit.coords + d)
        if e:
            choices.append((e.health, d))
    if choices:
        choices.sort(key=lambda t: t[0])
        return choices[0][1]
    return None


def nearest_enemy(state: State, unit: Obj) -> Optional[Obj]:
    enemies = state.objs_by_team(state.other_team)
    if not enemies:
        return None
    return min(enemies, key=lambda e: (unit.coords.walking_distance_to(e.coords), e.health))


def best_step_toward(state: State, unit: Obj, target: Coords) -> Optional[Direction]:
    current_dist = unit.coords.walking_distance_to(target)
    primary = unit.coords.direction_to(target)
    dirs = list(DIRECTIONS)
    dirs.sort(key=lambda d: (0 if d == primary else 1,
                             (unit.coords + d).walking_distance_to(target)))
    for d in dirs:
        dest = unit.coords + d
        if is_free(state, dest) and dest.walking_distance_to(target) < current_dist:
            reserved_moves.add(dest)
            return d
    return None


def step_to_annulus(state: State, unit: Obj) -> Optional[Direction]:
    # Stay off the spawn ring and distribute around radius ~7 from center.  This
    # prevents traffic jams and keeps most units away from perimeter spawn wipes.
    dirs = list(DIRECTIONS)
    dirs.sort(key=lambda d: (abs((unit.coords + d).walking_distance_to(CENTER) - 7),
                             (unit.coords + d).walking_distance_to(CENTER)))
    for d in dirs:
        dest = unit.coords + d
        if is_free(state, dest) and not dest.is_spawn():
            reserved_moves.add(dest)
            return d
    return None


def robot(state: State, unit: Obj) -> Optional[Action]:
    # Combat micro: focus low-health adjacent enemies.
    d = adjacent_enemy_direction(state, unit)
    if d:
        return Action.attack(d)

    # Macro priority: leave spawn immediately.  direction_to(CENTER) reliably
    # moves inward on the circular spawn ring.
    if unit.coords.is_spawn():
        d = best_step_toward(state, unit, CENTER)
        if d:
            return Action.move(d)

    # If we are still too close to the wall, continue moving inward.
    if unit.coords.walking_distance_to(CENTER) > 8:
        d = best_step_toward(state, unit, CENTER)
        if d:
            return Action.move(d)

    # Take local fights, but do not over-chase perimeter bait.
    enemy = nearest_enemy(state, unit)
    if enemy and unit.coords.walking_distance_to(enemy.coords) <= 3 and not enemy.coords.is_spawn():
        d = best_step_toward(state, unit, enemy.coords)
        if d:
            return Action.move(d)

    # If too clustered in the center, spread back out to the defensive annulus.
    if unit.coords.walking_distance_to(CENTER) < 6:
        d = step_to_annulus(state, unit)
        if d:
            return Action.move(d)

    return None
