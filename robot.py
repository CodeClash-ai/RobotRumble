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
    fallback = None
    for d in dirs:
        dest = unit.coords + d
        if is_free(state, dest) and dest.walking_distance_to(target) < current_dist:
            # Never step onto a spawn tile if a non-spawn inward move exists.
            # Spawn is cleared before waves on turns 11,21,... and the known
            # opponent often leaves perimeter bait there.
            if not is_spawn_coord(dest):
                reserved_moves.add(dest)
                return d
            if fallback is None:
                fallback = d
    if fallback is not None:
        reserved_moves.add(unit.coords + fallback)
        return fallback
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



def kite_from_nearby(state: State, unit: Obj, radius: int = 3) -> Optional[Direction]:
    # Late-game preservation helper: when we already lead on unit count, avoid
    # letting nearby enemies force trades.  Move only if the step increases our
    # distance from the closest local threat, and never step onto spawn.
    threats = [e for e in enemy_units if unit.coords.walking_distance_to(e.coords) <= radius]
    if not threats:
        return None
    current_min = min(unit.coords.walking_distance_to(e.coords) for e in threats)
    dirs = list(DIRECTIONS)

    def score(d: Direction) -> Tuple[int, int, int, int]:
        dest = unit.coords + d
        min_dist = min(dest.walking_distance_to(e.coords) for e in threats)
        all_near = sum(1 for e in enemy_units if dest.walking_distance_to(e.coords) <= 2)
        allies_near = sum(1 for a in our_units if a is not unit and dest.walking_distance_to(a.coords) <= 2)
        return (min_dist, -all_near, allies_near,
                -abs(dest.walking_distance_to(CENTER) - 7))

    dirs.sort(key=score, reverse=True)
    for d in dirs:
        dest = unit.coords + d
        if is_free(state, dest) and not is_spawn_coord(dest):
            if min(dest.walking_distance_to(e.coords) for e in threats) > current_min:
                reserved_moves.add(dest)
                return d
    return None



def late_chase_step(state: State, unit: Obj) -> Optional[Direction]:
    # If the match is tied near the end, unit count is all that matters.
    # Take a little more initiative toward nearby non-spawn enemies, preferring
    # already-wounded targets, but do not abandon the safe interior for far bait.
    # Round-0 versus anton__anton4000 produced many final unit-count ties;
    # starting this nudge at the final spawn (turn 90) and allowing health-2
    # targets gives tied games a better chance to become +1 wins.
    candidates = [e for e in enemy_units if (e.health <= 2 and not is_spawn_coord(e.coords) and unit.coords.walking_distance_to(e.coords) <= 4)]
    if not candidates:
        return None
    target = min(candidates, key=lambda e: (e.health, unit.coords.walking_distance_to(e.coords), e.coords.walking_distance_to(CENTER)))
    return best_step_toward(state, unit, target.coords)



def late_desperation_step(state: State, unit: Obj) -> Optional[Direction]:
    # If we are behind near the end, preserving a smaller loss is worthless;
    # normal scoring is by final unit count.  Take controlled initiative toward
    # nearby wounded, non-spawn enemies to try to flip one-unit losses/ties.
    # Keep the radius modest so we do not abandon the interior for perimeter bait.
    candidates = [e for e in enemy_units if (not is_spawn_coord(e.coords) and
                                            e.health <= 3 and
                                            unit.coords.walking_distance_to(e.coords) <= 5)]
    if not candidates:
        return None
    target = min(candidates, key=lambda e: (e.health, unit.coords.walking_distance_to(e.coords), e.coords.walking_distance_to(CENTER)))
    return best_step_toward(state, unit, target.coords)

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
        # Before the final wave, spawn tiles will be wiped at the next wave and
        # must be evacuated.  After the last spawn (turn 90+) there is no turn
        # 101 clear, so perimeter robots are often safer counting as survivors
        # than marching into late trades.
        if state.turn < 90:
            d = best_step_toward(state, unit, CENTER)
            if d:
                return Action.move(d)
        else:
            adj = adjacent_enemies(state, unit)
            if adj:
                adj.sort(key=lambda t: t[1].health)
                attack_dir, target = adj[0]
                allies_on_target = local_count(our_units, target.coords, 1)
                if target.health <= allies_on_target:
                    return Action.attack(attack_dir)
                d = retreat_from_adjacent(state, unit, adj)
                if d:
                    return Action.move(d)
                return None
            d = intercept_dir(state, unit)
            if d:
                reserved_attack_squares.add(unit.coords + d)
                return Action.attack(d)
            return None

    # Combat micro: focus weak adjacent enemies when we can kill/trade well;
    # otherwise dodge away from obvious adjacent attacks.  Late in games
    # where we already have a unit-count lead, favor preserving that lead over
    # nonlethal trades; recent close logs came from bleeding leads during the
    # final reinforcement wave.  Begin a little earlier only for a 2+ unit
    # cushion, so equal/one-up positions can still seek necessary kills.
    adj = adjacent_enemies(state, unit)
    if adj:
        adj.sort(key=lambda t: t[1].health)
        attack_dir, target = adj[0]
        allies_on_target = local_count(our_units, target.coords, 1)
        enemies_near_us = local_count(enemy_units, unit.coords, 2)
        late_behind = ((state.turn >= 90 and len(our_units) < len(enemy_units)) or
                       (state.turn >= 85 and len(our_units) + 2 <= len(enemy_units)))
        if ((state.turn >= 90 and len(our_units) > len(enemy_units)) or
                (state.turn >= 85 and len(our_units) >= len(enemy_units) + 2)) and target.health > allies_on_target:
            d = retreat_from_adjacent(state, unit, adj)
            if d:
                return Action.move(d)
            return None
        if (target.health <= allies_on_target or allies_on_target >= enemies_near_us + 1 or
                (late_behind and target.health <= 3)):
            return Action.attack(attack_dir)
        d = retreat_from_adjacent(state, unit, adj)
        if d:
            return Action.move(d)
        return Action.attack(attack_dir)

    # If ahead in the final stretch, preserve the unit-count lead by kiting
    # nearby enemies instead of volunteering for trades.  With a 2+ unit
    # cushion, start after turn 85; with a one-unit lead, wait until turn 90.
    # This deliberately runs before the normal wall-to-center movement: after
    # the final wave, perimeter/non-spawn survivors often count safely if they
    # simply avoid contact, while marching inward can bleed close leads.
    if ((state.turn >= 90 and len(our_units) > len(enemy_units)) or
            (state.turn >= 85 and len(our_units) >= len(enemy_units) + 2)):
        d = kite_from_nearby(state, unit, 3)
        if d:
            return Action.move(d)
        # Once we have a late unit-count lead, do not volunteer for any extra
        # intercepts/chases/annulus shuffling.  Recent aayyad__testbot losses
        # came from bleeding a 2-4 unit post-spawn lead during turns 95-100;
        # standing still away from adjacent threats preserves the only score
        # that matters better than walking into predicted attacks.
        return None

    # If we are still too close to the wall, continue moving inward.
    if unit.coords.walking_distance_to(CENTER) > 8:
        d = best_step_toward(state, unit, CENTER)
        if d:
            return Action.move(d)

    # When tied in the final stretch, a tie is as bad as a loss.  Nudge
    # nearby units toward wounded enemies to try to gain one more kill, while the
    # existing preservation logic above still protects actual leads.
    if state.turn >= 90 and len(our_units) == len(enemy_units):
        d = late_chase_step(state, unit)
        if d:
            return Action.move(d)

    # If we are behind near the end, a cautious loss is still a loss.  Push
    # toward wounded local targets to try to recover one unit before turn 100.
    if ((state.turn >= 90 and len(our_units) < len(enemy_units)) or
            (state.turn >= 85 and len(our_units) + 2 <= len(enemy_units))):
        d = late_desperation_step(state, unit)
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
