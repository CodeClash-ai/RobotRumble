# RobotRumble bot v2 - aggressive coordinated focus-fire with predictive attacks
# Game facts (docs/ and logic/logic/src/lib.rs):
#  - 19x19 circular arena, 5 HP units, attacks 1 dmg, NO self-damage cost.
#  - Movement resolves BEFORE attacks each turn; attackers on same tile stack.
#  - Friendly fire IS possible (avoid it).
#  - Up to 4 units spawn/team every 10 turns; win = most units at turn 100.
#  - Move conflict priority N,E,S,W; swap-moves blocked.
# Strategy: group up, focus-fire the weakest reachable enemy, predict flee,
# never hit allies, keep units advancing out of spawn so they aren't wiped.

from typing import *

DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]
last_positions: Dict[str, Any] = {}
# Per-turn shared state computed in init_turn
_focus_target_id = None
_target_by_unit = {}  # unit_id -> enemy id (squad assignment)
_planned_moves: Dict[str, Any] = {}  # unit_id -> destination Coords


def in_bounds(c) -> bool:
    return 0 <= c.x < MAP_SIZE and 0 <= c.y < MAP_SIZE


def blocked_tile(state, c) -> bool:
    if not in_bounds(c):
        return True
    o = state.obj_by_coords(c)
    if o is not None and o.obj_type == ObjType.Terrain:
        return True
    return False


def unit_at(state, c):
    o = state.obj_by_coords(c)
    if o is not None and o.obj_type == ObjType.Unit:
        return o
    return None


def enemy_at(state, c, other_team):
    o = state.obj_by_coords(c)
    if o is not None and o.obj_type == ObjType.Unit and o.team == other_team:
        return o
    return None


def adjacent_enemies(state, c, other_team):
    res = []
    for d in DIRECTIONS:
        e = enemy_at(state, c + d, other_team)
        if e is not None:
            res.append((d, e))
    return res


def count_my_adjacent(state, coords, my_team):
    """How many of my units are adjacent to `coords` (i.e. can attack it)."""
    n = 0
    for d in DIRECTIONS:
        o = unit_at(state, coords + d)
        if o is not None and o.team == my_team:
            n += 1
    return n


def count_enemy_adjacent(state, coords, other_team):
    """How many enemy units are adjacent to `coords` (threats to this tile)."""
    n = 0
    for d in DIRECTIONS:
        o = unit_at(state, coords + d)
        if o is not None and o.team == other_team:
            n += 1
    return n


def init_turn(state: State) -> None:
    global _focus_target_id, _planned_moves, _target_by_unit
    _planned_moves = {}
    _target_by_unit = {}
    other = state.other_team
    enemies = state.objs_by_team(other)
    mine = state.objs_by_team(state.our_team)
    if not enemies or not mine:
        _focus_target_id = None
        return
    # Choose a global focus target: weakest enemy, tie-broken by total distance
    # from our units (closer = easier to gang up on).
    def score(e):
        reachers = sum(1 for u in mine if u.coords.walking_distance_to(e.coords) <= 2)
        total = sum(u.coords.walking_distance_to(e.coords) for u in mine)
        return (-reachers, e.health, total)
    _focus_target_id = min(enemies, key=score).id

    # MULTI-TARGET SQUAD ASSIGNMENT: instead of dogpiling ALL units on ONE enemy
    # (overkill while the opponent gang-kills several of ours in parallel), assign
    # ~SQUAD allies to each enemy. Greedy: repeatedly pick the (ally,enemy) pair
    # with the smallest walking distance, assign the ally, and stop adding to an
    # enemy once it has enough attackers to KILL it (health+1 attackers) or SQUAD.
    # This lets us kill MULTIPLE enemies per turn = better net trades.
    SQUAD = 2
    assigned = {}  # enemy_id -> count of allies assigned
    # cap per enemy: enough to guarantee a kill (health) but at least 2, at most SQUAD+1
    def cap(e):
        return max(2, min(SQUAD + 1, e.health + 1))
    # precompute distances
    pairs = []
    for u in mine:
        for e in enemies:
            pairs.append((u.coords.walking_distance_to(e.coords), u.id, e.id))
    pairs.sort()
    eby = {e.id: e for e in enemies}
    for dist, uid, eid in pairs:
        if uid in _target_by_unit:
            continue
        if assigned.get(eid, 0) >= cap(eby[eid]):
            continue
        _target_by_unit[uid] = eid
        assigned[eid] = assigned.get(eid, 0) + 1
    # any leftover allies (all enemies full) -> send to nearest enemy (finish/help)
    for u in mine:
        if u.id not in _target_by_unit:
            ne = min(enemies, key=lambda e: u.coords.walking_distance_to(e.coords))
            _target_by_unit[u.id] = ne.id



def count_allies_near(state, coords, my_team):
    """Allies within walking distance 2 (loose grouping)."""
    n = 0
    for u in state.objs_by_team(my_team):
        wd = coords.walking_distance_to(u.coords)
        if 0 < wd <= 2:
            n += 1
    return n


def retreat(state, unit):
    """Move away from the nearest enemy, breaking ties by moving TOWARD allies
    (regroup) so fragile units stay in formation instead of scattering."""
    other = state.other_team
    enemies = state.objs_by_team(other)
    if not enemies:
        return None
    my = unit.coords
    ne = min(enemies, key=lambda e: my.walking_distance_to(e.coords))
    cur_d = my.walking_distance_to(ne.coords)
    allies = [u for u in state.objs_by_team(unit.team) if u.id != unit.id]
    best = None
    best_key = None
    for d in DIRECTIONS:
        nxt = my + d
        if blocked_tile(state, nxt):
            continue
        if state.obj_by_coords(nxt) is not None:
            continue
        if bad_spawn_tile(state, nxt):
            continue  # don't retreat onto a spawn tile -> would be wiped
        dd = nxt.walking_distance_to(ne.coords)
        if dd <= cur_d:
            continue  # only tiles that actually increase distance from enemy
        ally_pen = sum(nxt.walking_distance_to(a.coords) for a in allies
                       if nxt.walking_distance_to(a.coords) <= 5)
        # farther from enemy is better (negate), then closer to allies
        key = (-dd, ally_pen)
        if best_key is None or key < best_key:
            best_key = key
            best = d
    if best is not None:
        return Action.move(best)
    return None




def disperse(state, unit):
    """When STRICTLY AHEAD late, spread units to safe tiles: maximize distance
    from the nearest enemy, avoid spawn tiles pre-spawn, and avoid clustering
    (so we can't be gang-killed and we don't clog our own spawn). Unlike
    retreat(), this does NOT pull toward allies (clustering near spawn late-game
    got our units wiped in traced losses, e.g. sim_220 t90)."""
    other = state.other_team
    enemies = state.objs_by_team(other)
    if not enemies:
        return None
    my = unit.coords
    ne = min(enemies, key=lambda e: my.walking_distance_to(e.coords))
    cur_d = my.walking_distance_to(ne.coords)
    best = None
    best_key = None
    for d in DIRECTIONS:
        nxt = my + d
        if blocked_tile(state, nxt):
            continue
        if state.obj_by_coords(nxt) is not None:
            continue
        if bad_spawn_tile(state, nxt):
            continue
        dd = nxt.walking_distance_to(ne.coords)
        if dd < cur_d:
            continue  # never step closer to the enemy
        # prefer farther from enemy; break ties by spreading from allies (larger
        # min-distance to any ally = less clustered = harder to gang-kill)
        allies = [u for u in state.objs_by_team(unit.team) if u.id != unit.id]
        if allies:
            spread = min(nxt.walking_distance_to(a.coords) for a in allies)
        else:
            spread = 99
        key = (-dd, -spread)
        if best_key is None or key < best_key:
            best_key = key
            best = d
    if best is not None:
        return Action.move(best)
    return None


def spawn_turn_soon(state):
    """True if a spawn/clear will occur at the start of the next turn.
    Spawn/clear happens when (turn-1) % 10 == 0 (turns 1,11,21,...). A unit
    still on a spawn tile at the END of turn T (where (T) % 10 == 0) is wiped
    at the start of turn T+1. We evacuate on turns ending in ...8,9,0."""
    t = state.turn
    # next spawn turn is the smallest turn n>t with (n-1)%10==0
    return (t % 10) in (7, 8, 9, 0)


def bad_spawn_tile(state, coords):
    """A tile we must NOT end a turn on when a spawn/clear is imminent:
    a spawn tile (we'd be WIPED by clear_spawn) is the critical case. Landing
    on a spawn tile at end of a pre-spawn turn deletes our unit -> we lose the
    count race (win = most units). Avoid it whenever a spawn is imminent."""
    return spawn_turn_soon(state) and coords.is_spawn()


def evacuate_spawn(state, unit):
    """Move a unit off a spawn tile (toward center/allies) so it is not wiped
    on the spawn turn AND does not block our own new spawns (spawn only occurs
    on points whose tile AND mirror are both free)."""
    my = unit.coords
    other = state.other_team
    enemies = state.objs_by_team(other)
    goal = Coords(MAP_SIZE // 2, MAP_SIZE // 2)
    if enemies:
        # head toward the nearest enemy direction but any non-spawn free tile is fine
        ne = min(enemies, key=lambda e: my.walking_distance_to(e.coords))
        goal = ne.coords
    best = None
    best_key = None
    for d in DIRECTIONS:
        nxt = my + d
        if blocked_tile(state, nxt):
            continue
        if state.obj_by_coords(nxt) is not None:
            continue
        if nxt.is_spawn():
            continue  # must leave the spawn zone entirely
        key = nxt.walking_distance_to(goal)
        if best_key is None or key < best_key:
            best_key = key
            best = d
    if best is not None:
        _planned_moves[unit.id] = my + best
        return Action.move(best)
    return None


def robot(state: State, unit: Obj) -> Optional[Action]:
    other_team = state.other_team
    my_team = state.our_team
    enemies = state.objs_by_team(other_team)
    my = unit.coords

    if not enemies:
        return leave_spawn(state, unit)

    # SPAWN EVACUATION (critical): if we're on a spawn tile and a spawn/clear is
    # imminent, get off it -- otherwise we're wiped AND we block our own spawns.
    if unit.coords.is_spawn() and spawn_turn_soon(state):
        # On the ACTUAL wipe turn (t%10==0), a unit left on a spawn tile is
        # deleted at the start of next turn REGARDLESS of what it does. Even a
        # guaranteed kill (enemy -1) is a 1-for-1 that ALSO costs us the spawn
        # slot, so evacuating (we keep our unit AND free the slot for +1 spawn)
        # is strictly better for the count-based win. So on the wipe turn we
        # ALWAYS evacuate if possible. On buffer turns (7,8,9) we still allow a
        # guaranteed kill first (the unit can evacuate next turn).
        is_wipe_turn = (state.turn % 10) == 0
        secured_kill = False
        if not is_wipe_turn:
            for d, e in adjacent_enemies(state, my, other_team):
                if e.health <= count_my_adjacent(state, e.coords, my_team):
                    secured_kill = True
                    break
        if not secured_kill:
            ev = evacuate_spawn(state, unit)
            if ev is not None:
                return ev

    # 1) If an enemy is adjacent, decide whether to attack now.
    adj = adjacent_enemies(state, my, other_team)
    if adj:
        n_adj_enemies = len(adj)
        my_local = count_allies_near(state, my, my_team)
        # Retreat a fragile unit that is outnumbered locally (avoid feeding kills)
        # unless it can secure a kill this turn.
        # Prefer attacking an adjacent enemy that is BOXED (cannot flee this
        # turn) so the hit is guaranteed to land, then weakest, then most
        # ally-attackers (best chance to secure the kill after fleeing).
        def adj_score(de):
            dd, ee = de
            boxed = enemy_boxed(state, ee, my_team)
            attackers = count_my_adjacent(state, ee.coords, my_team)
            # lower is better: boxed first, then low health, then more attackers
            return (0 if boxed else 1, ee.health, -attackers)
        d, e = min(adj, key=adj_score)
        attackers = count_my_adjacent(state, e.coords, my_team)
        can_kill = e.health <= attackers
        # Retreat a fragile unit that is outnumbered locally and cannot kill.
        outnumbered = n_adj_enemies > my_local + 1
        # Late-game: preserve unit count (win = most units at turn 100). If a
        # fragile unit (<=2 HP) can't secure a kill this turn, retreat instead
        # of feeding an even/losing trade near the end.
        # Late-game unit preservation only when NOT behind in unit count
        # (win = most units at turn 100; if behind we must trade to catch up).
        my_units = len(state.objs_by_team(my_team))
        enemy_units = len(enemies)
        late_game = state.turn >= 85 and my_units >= enemy_units
        # Mid/late even-game: preserve fragile (<=2HP) units when NOT ahead in
        # count so even 1-for-1 trades don't leave us tied (win = most units).
        even_game = False  # DISABLED (round 0 vs gerenuk): retreating fragile units when behind/even STRANDED them out of the fight, costing the count race. We are RED underdog here; keep units fighting.
        # Protect a LEAD: when ahead in unit count late in the game, avoid ANY
        # risky trade. A unit that can't secure a kill AND would take return
        # damage (i.e. it's a genuine trade, not a free hit on a boxed enemy)
        # should retreat to preserve the numeric lead (win = most units).
        protect_lead = state.turn >= 80 and my_units > enemy_units
        # When we hold a COMFORTABLE lead late, aggressively preserve units:
        # avoid ANY unfavorable trade (can't kill this turn) unless the target
        # is boxed (guaranteed free hit). Win = most units at turn 100, so a
        # preserved lead is worth more than a chip of damage.
        big_lead = state.turn >= 75 and my_units >= enemy_units + 3
        # MID-GAME lead protection: traced losses (sim_116) show we hold a
        # 2-unit lead at turn ~40 then trade it away in turns 40-50. Preserve
        # FRAGILE (<=2HP) units when ahead by 2+ mid-game in an unfavorable fight.
        mid_lead = 50 <= state.turn < 75 and my_units >= enemy_units + 2
        # ENDGAME LOCK-IN: in the final turns, count is decided. If we are AHEAD
        # or TIED, refuse ANY trade that isn't a guaranteed kill (attack whiffs
        # when enemy flees, but we still take return damage next turn / feed a
        # trade). Retreat healthy units too - a preserved unit at turn 100 wins
        # the count race. Losses traced: we held a 1-2 unit lead at turn ~90 then
        # traded it away 1-for-1 in the last 10 turns to a tie/loss.
        # When strictly ahead, lock in the lead (retreat non-kill trades).
        # When TIED, only retreat if this fight is NOT locally favorable (we
        # don't have more attackers on the target than it has adjacent allies) -
        # otherwise a favorable trade can push us AHEAD, which wins the count.
        local_favorable = attackers > count_enemy_adjacent(state, my, other_team)
        # Strictly-ahead endgame lock-in fires EARLIER (turn>=86): traced losses
        # (sim_0, sim_113) held a 1-3 unit lead at turn ~90 then traded it away
        # in the last turns to a tie/loss. Protecting the lead sooner converts
        # those. Tied case stays at turn>=90 (only when not locally favorable).
        endgame = (
            (state.turn >= 86 and my_units > enemy_units)
            or (state.turn >= 90 and my_units == enemy_units and not local_favorable)
        )
        boxed_here = enemy_boxed(state, e, my_team)
        should_retreat = (
            unit.health <= 1
            or (outnumbered and unit.health <= 2)
            or (late_game and unit.health <= 3)
            or (even_game and unit.health <= 2 and not local_favorable)
            or (protect_lead and unit.health <= 3 and not boxed_here)
            or (big_lead and unit.health <= 4 and not boxed_here)
            or (mid_lead and unit.health <= 2 and not boxed_here and not local_favorable)
            or (endgame and not boxed_here)
        )
        if not can_kill and should_retreat:
            # When strictly ahead by 2+ late, disperse to safe corners (don't
            # cluster toward allies/spawn where we get gang-killed/wiped).
            if state.turn >= 90 and my_units > enemy_units:
                dsp = disperse(state, unit)
                if dsp is not None:
                    return dsp
            r = retreat(state, unit)
            if r is not None:
                return r
        # Attack the chosen adjacent enemy (aggressive: always trade or better).
        return Action.attack(d)

    # 2) Move toward focus target if reachable, else nearest weak enemy.
    target = pick_target(state, unit, enemies)
    # ANTI-OVEREXTENSION: edward__flail clusters defensively near its spawn and
    # picks off our units one at a time as they arrive. If advancing would put
    # us adjacent to the enemy cluster while we are LOCALLY OUTNUMBERED, hold
    # back and regroup toward allies rather than feed a lone unit into the ball.
    # Only applies in the neutral/early-mid game when we still have units coming.
    nearest = min(enemies, key=lambda e: my.walking_distance_to(e.coords))
    dist_to_enemy = my.walking_distance_to(nearest.coords)
    my_units = len(state.objs_by_team(my_team))
    enemy_units = len(enemies)
    if dist_to_enemy == 2 and my_units <= enemy_units and state.turn < 80:
        mine_near, foes_near = local_balance(state, my, my_team, other_team, radius=2)
        # Only hold if we are clearly outnumbered locally (2+), so a lone unit
        # doesn't dive a defensive ball. A small deficit we still contest.
        if foes_near >= mine_near + 2:
            # locally outnumbered right at the front: regroup toward allies
            rg = regroup_toward_allies(state, unit)
            if rg is not None:
                return rg
    # ENDGAME HOLD: in the final turns, if we are STRICTLY AHEAD in unit count,
    # do NOT advance a healthy unit into fresh enemy contact (dist 2 -> would be
    # adjacent next turn). Movement resolves before attacks, so stepping adjacent
    # lets the enemy hit us on their turn -> a trade that can erode our lead.
    # Preserving the count (win = most units at turn 100) is worth more than a
    # chip of damage. Only fires when ahead, dist==2, so we don't go passive.
    # RUN OUT THE CLOCK: when strictly ahead by 2+ units late, stop advancing
    # into fights entirely and disperse to safe tiles. Traced losses (sim_220)
    # threw away a 4-unit lead in the last 20 turns by trading/advancing into
    # contact near spawn turns. A dispersed lead at turn 100 wins the count race.
    if state.turn >= 94 and my_units >= enemy_units + 3:
        dsp = disperse(state, unit)
        if dsp is not None:
            return dsp
    if state.turn >= 86 and my_units > enemy_units and dist_to_enemy == 2:
        mine_near, foes_near = local_balance(state, my, my_team, other_team, radius=2)
        # Only hold if the fight ahead is NOT locally favorable. If we clearly
        # outnumber them here, keep pressing (a favorable trade widens our lead).
        if foes_near >= mine_near:
            rg = regroup_toward_allies(state, unit)
            if rg is not None:
                return rg
    return step_toward(state, unit, target.coords)


def regroup_toward_allies(state, unit):
    """Move to the free adjacent tile that minimizes distance to nearby allies
    (pull the pack together) while not stepping into an enemy-adjacent tile."""
    other = state.other_team
    my = unit.coords
    allies = [u for u in state.objs_by_team(unit.team) if u.id != unit.id]
    if not allies:
        return None
    best = None
    best_key = None
    for d in DIRECTIONS:
        nxt = my + d
        if blocked_tile(state, nxt):
            continue
        if state.obj_by_coords(nxt) is not None:
            continue
        if bad_spawn_tile(state, nxt):
            continue  # don't regroup onto a spawn tile -> would be wiped
        # avoid ally-planned collisions
        collide = any(did != unit.id and dest.x == nxt.x and dest.y == nxt.y
                      for did, dest in _planned_moves.items())
        if collide:
            continue
        ally_pen = sum(nxt.walking_distance_to(a.coords) for a in allies
                       if nxt.walking_distance_to(a.coords) <= 6)
        if best_key is None or ally_pen < best_key:
            best_key = ally_pen
            best = (d, nxt)
    if best is not None:
        _planned_moves[unit.id] = best[1]
        return Action.move(best[0])
    return None


def enemy_boxed(state, e, my_team):
    """Enemy has few free escape tiles (can't dodge easily)."""
    free = 0
    for d in DIRECTIONS:
        nxt = e.coords + d
        if blocked_tile(state, nxt):
            continue
        o = unit_at(state, nxt)
        if o is None:
            free += 1
    return free <= 1


def pick_target(state, unit, enemies):
    global _focus_target_id, _target_by_unit
    my = unit.coords
    # squad assignment first (parallel gang-kills)
    eid = _target_by_unit.get(unit.id)
    if eid is not None:
        t = state.obj_by_id(eid)
        if t is not None:
            return t
    if _focus_target_id is not None:
        t = state.obj_by_id(_focus_target_id)
        if t is not None:
            return t
    return min(enemies, key=lambda e: (e.health, my.walking_distance_to(e.coords)))


def leave_spawn(state, unit):
    if not unit.coords.is_spawn():
        return None
    return step_toward(state, unit, Coords(MAP_SIZE // 2, MAP_SIZE // 2))



def local_balance(state, coords, my_team, other_team, radius=2):
    """Return (my_nearby, enemy_nearby) within `radius` walking distance of `coords`.
    Used to avoid feeding a lone unit into a clustered enemy ball."""
    mine = 0
    for u in state.objs_by_team(my_team):
        if 0 <= coords.walking_distance_to(u.coords) <= radius:
            mine += 1
    foes = 0
    for e in state.objs_by_team(other_team):
        if coords.walking_distance_to(e.coords) <= radius:
            foes += 1
    return mine, foes


def step_toward(state, unit, goal):
    global last_positions, _planned_moves
    my = unit.coords
    candidates = []
    for d in DIRECTIONS:
        nxt = my + d
        if blocked_tile(state, nxt):
            continue
        o = state.obj_by_coords(nxt)
        if o is not None:
            continue  # occupied
        if bad_spawn_tile(state, nxt):
            continue  # don't move onto a spawn tile pre-spawn -> would be wiped
        # avoid tiles another ally already planned to move into this turn
        collide = False
        for did, dest in _planned_moves.items():
            if did != unit.id and dest.x == nxt.x and dest.y == nxt.y:
                collide = True
                break
        if collide:
            continue
        # grouping: sum walking distance to nearby allies (smaller = tighter)
        ally_pen = 0
        for u in state.objs_by_team(unit.team):
            if u.id == unit.id:
                continue
            wd = nxt.walking_distance_to(u.coords)
            if wd <= 4:
                ally_pen += wd
        candidates.append((nxt.walking_distance_to(goal), ally_pen, d, nxt))

    if not candidates:
        return None

    candidates.sort(key=lambda c: (c[0], c[1]))
    prev = last_positions.get(unit.id)
    for dist, ap, d, nxt in candidates:
        if prev is not None and nxt.x == prev.x and nxt.y == prev.y:
            continue
        last_positions[unit.id] = my
        _planned_moves[unit.id] = nxt
        return Action.move(d)

    # Fallback: all preferred tiles were the previous position; take the best.
    dist, ap, d, nxt = candidates[0]
    last_positions[unit.id] = my
    _planned_moves[unit.id] = nxt
    return Action.move(d)
