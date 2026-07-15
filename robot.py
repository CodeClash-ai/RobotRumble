from typing import *

# Survival-first RobotRumble bot.
# Normal mode is decided only by unit count after 100 turns.  Spawn tiles are
# wiped before reinforcements on turns 11,21,..., so the most important macro
# rule is to leave the spawn ring immediately and keep collecting new robots.
# This version keeps the strong anti-passive annulus from round 1, plus light
# combat micro: because movement resolves before attacks, a badly outnumbered
# adjacent robot can often dodge away instead of trading damage.

CENTER = Coords(9, 9)
# Avoid Coords.is_spawn(): the bundled Python stdlib stores spawn strings in a
# one-shot map iterator, so repeated membership checks can become unreliable.
SPAWN_SET = {
    Coords(1, 5), Coords(1, 6), Coords(1, 7), Coords(1, 8), Coords(1, 9), Coords(1, 10), Coords(1, 11), Coords(1, 12), Coords(1, 13),
    Coords(2, 4), Coords(2, 14), Coords(3, 3), Coords(3, 15), Coords(4, 2), Coords(4, 16),
    Coords(5, 1), Coords(5, 17), Coords(6, 1), Coords(6, 17), Coords(7, 1), Coords(7, 17), Coords(8, 1), Coords(8, 17),
    Coords(9, 1), Coords(9, 17), Coords(10, 1), Coords(10, 17), Coords(11, 1), Coords(11, 17), Coords(12, 1), Coords(12, 17), Coords(13, 1), Coords(13, 17),
    Coords(14, 2), Coords(14, 16), Coords(15, 3), Coords(15, 15), Coords(16, 4), Coords(16, 14),
    Coords(17, 5), Coords(17, 6), Coords(17, 7), Coords(17, 8), Coords(17, 9), Coords(17, 10), Coords(17, 11), Coords(17, 12), Coords(17, 13),
}
DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]
reserved_moves: Set[Coords] = set()
reserved_attack_squares: Set[Coords] = set()
our_units: List[Obj] = []
enemy_units: List[Obj] = []


def init_turn(state: State) -> None:
    global reserved_moves, reserved_attack_squares, our_units, enemy_units
    reserved_moves = set()
    reserved_attack_squares = set()
    our_units = state.objs_by_team(state.our_team)
    enemy_units = state.objs_by_team(state.other_team)


def in_bounds(c: Coords) -> bool:
    return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE


def is_free(state: State, c: Coords) -> bool:
    return (in_bounds(c) and c not in reserved_moves and
            c not in reserved_attack_squares and state.obj_by_coords(c) is None)


def is_spawn_coord(c: Coords) -> bool:
    return c in SPAWN_SET


def enemy_at(state: State, c: Coords) -> Optional[Obj]:
    obj = state.obj_by_coords(c)
    if obj and obj.team == state.other_team:
        return obj
    return None


def adjacent_enemies(state: State, unit: Obj) -> List[Tuple[Direction, Obj]]:
    out = []
    for d in DIRECTIONS:
        e = enemy_at(state, unit.coords + d)
        if e:
            out.append((d, e))
    return out


def nearest_enemy(unit: Obj) -> Optional[Obj]:
    if not enemy_units:
        return None
    return min(enemy_units, key=lambda e: (unit.coords.walking_distance_to(e.coords), e.health))


def local_count(units: List[Obj], c: Coords, r: int) -> int:
    return sum(1 for o in units if o.coords.walking_distance_to(c) <= r)


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


def retreat_from_adjacent(state: State, unit: Obj, adj: List[Tuple[Direction, Obj]]) -> Optional[Direction]:
    # Move out of current adjacent attacks when the local fight is poor.  The
    # destination must also avoid spawn tiles so dodging never sacrifices future
    # reinforcements to clear_spawn().
    enemies = [e for _, e in adj]
    current_min_dist = min(unit.coords.walking_distance_to(e.coords) for e in enemies)
    dirs = list(DIRECTIONS)

    def score(d: Direction) -> Tuple[int, int, int, int]:
        dest = unit.coords + d
        min_dist = min(dest.walking_distance_to(e.coords) for e in enemies)
        nearby = sum(1 for e in enemy_units if dest.walking_distance_to(e.coords) <= 2)
        spawn_penalty = 1 if is_spawn_coord(dest) else 0
        return (min_dist, -nearby, -spawn_penalty,
                -abs(dest.walking_distance_to(CENTER) - 7))

    dirs.sort(key=score, reverse=True)
    for d in dirs:
        dest = unit.coords + d
        if (is_free(state, dest) and not is_spawn_coord(dest) and
                min(dest.walking_distance_to(e.coords) for e in enemies) > current_min_dist):
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
        if is_free(state, dest) and not is_spawn_coord(dest):
            reserved_moves.add(dest)
            return d
    return None



def intercept_dir(state: State, unit: Obj) -> Optional[Direction]:
    # Pre-fire an adjacent empty tile when an enemy two steps away is likely to
    # move into it.  Movement is resolved before attacks, so this punishes
    # simple chase bots without changing the survival macro versus passive bots.
    best: Optional[Tuple[Tuple[int, int], Direction]] = None
    for d in DIRECTIONS:
        adj = unit.coords + d
        if state.obj_by_coords(adj) is not None or adj in reserved_moves:
            continue
        for e in enemy_units:
            if (e.coords.walking_distance_to(unit.coords) == 2 and
                    e.coords.walking_distance_to(adj) == 1 and
                    adj.walking_distance_to(unit.coords) < e.coords.walking_distance_to(unit.coords)):
                val = (local_count(our_units, adj, 1), -e.health)
                if best is None or val > best[0]:
                    best = (val, d)
    return best[1] if best else None

def robot(state: State, unit: Obj) -> Optional[Action]:
    # Highest priority: leave spawn immediately, even if an enemy is adjacent.
    # A robot left on a spawn tile is deleted before the next reinforcement wave,
    # and movement can also dodge attacks aimed at its old square.
    if is_spawn_coord(unit.coords):
        d = best_step_toward(state, unit, CENTER)
        if d:
            return Action.move(d)

    # Combat micro: focus weak adjacent enemies when we can kill/trade well;
    # otherwise dodge away from obvious adjacent attacks.
    adj = adjacent_enemies(state, unit)
    if adj:
        adj.sort(key=lambda t: t[1].health)
        attack_dir, target = adj[0]
        allies_on_target = local_count(our_units, target.coords, 1)
        enemies_near_us = local_count(enemy_units, unit.coords, 2)
        if target.health <= allies_on_target or allies_on_target >= enemies_near_us + 1:
            return Action.attack(attack_dir)
        d = retreat_from_adjacent(state, unit, adj)
        if d:
            return Action.move(d)
        return Action.attack(attack_dir)

    # If we are still too close to the wall, continue moving inward.
    if unit.coords.walking_distance_to(CENTER) > 8:
        d = best_step_toward(state, unit, CENTER)
        if d:
            return Action.move(d)

    # Movement resolves before attacks: if a nearby enemy is probably stepping
    # next to us, attack the destination square preemptively instead of walking
    # into a brawl.  Do this only after spawn/perimeter evacuation.
    d = intercept_dir(state, unit)
    if d:
        reserved_attack_squares.add(unit.coords + d)
        return Action.attack(d)

    # Take only local fights.  Do not over-chase perimeter bait or distant
    # passers; unit-count survival is usually better than damage.
    enemy = nearest_enemy(unit)
    if enemy and unit.coords.walking_distance_to(enemy.coords) <= 2 and not is_spawn_coord(enemy.coords):
        d = best_step_toward(state, unit, enemy.coords)
        if d:
            return Action.move(d)

    # If too clustered in the center, spread back out to the defensive annulus.
    if unit.coords.walking_distance_to(CENTER) < 6:
        d = step_to_annulus(state, unit)
        if d:
            return Action.move(d)

    return None
