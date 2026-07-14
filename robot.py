"""
sonnet-5's RobotRumble bot (Round 2).

Strategy overview
-----------------
Round 1's bot used pure greedy per-unit targeting/movement. It beat every
builtin bot *except* `black-magic.js`, which does a coordinate-ascent
joint-action search over all of its units each turn, scoring resulting
board states with (unit_diff, surround^2, health_diff, distance^2)
(see `builtin-bots/black-magic.js`). That structured lookahead consistently
out-plays greedy per-unit logic (it focus-fires efficiently and avoids bad
trades), so this round ports the same idea into Python via `init_turn`,
which runs once per turn (not once per unit) and lets us jointly plan
actions for our whole team before any unit's `robot()` call happens.

Algorithm (mirrors black-magic.js, adapted to the real Python API):
1. Snapshot friend/enemy coords -> health from `state`.
2. Baseline enemy behavior assumption: each enemy attacks whichever
   *adjacent* friend has the lowest health (same heuristic black-magic.js
   assumes for the *opposing* team when planning its own actions - it's a
   reasonable/aggressive worst-case-ish baseline for our friends' actions
   to react against).
3. Coordinate-ascent over our own units: for each of our units (repeated
   over a few passes for a better local optimum), try every legal action
   (move in 4 dirs, attack in 4 dirs, or pass) while holding every other
   unit's action fixed at its current best, simulate one resolved turn
   (`_tick`), score the result, and keep whichever single-unit action
   improves the joint score tuple the most. This naturally produces
   coordinated focus-fire / surround / retreat behavior without needing
   per-unit heuristics.
4. Store the resulting per-unit `Action` (or `None`) in a module-level
   dict keyed by unit id; `robot()` just looks it up (must NOT recompute
   per unit - `init_turn` already did the full-team planning once).

Movement/attack legality re: walls uses the *real* `state.obj_by_coords`
(so it works on the actual generated map, not a hardcoded diamond formula
like black-magic.js uses) - out-of-bounds or any `Terrain` object blocks
a destination; unit occupancy is tracked separately in the simulation
dicts since those change positions during the hypothetical `_tick`.

See README_agent.md for local test results / timing notes and how to
re-run analysis.
"""

from typing import *
import math

ALL_DIRECTIONS = [Direction.North, Direction.East, Direction.South, Direction.West]

_MOVE = 0
_ATTACK = 1

# Populated once per turn by init_turn(); robot() just looks up its unit id.
_PLAN: Dict[str, Optional[Action]] = {}

# Cache of wall/out-of-bounds lookups; walls never move so this is safe to
# reuse for the lifetime of a single turn (cleared at the top of init_turn).
_blocked_cache: Dict[Coords, bool] = {}


def _is_blocked(state: State, coords: Coords) -> bool:
    cached = _blocked_cache.get(coords)
    if cached is not None:
        return cached
    if not (0 <= coords.x < MAP_SIZE and 0 <= coords.y < MAP_SIZE):
        result = True
    else:
        obj = state.obj_by_coords(coords)
        result = obj is not None and obj.obj_type == ObjType.Terrain
    _blocked_cache[coords] = result
    return result


def _score(friends: Dict[Coords, int], enemies: Dict[Coords, int]) -> Tuple[float, float, float, float]:
    """Higher is better for `friends`. Mirrors black-magic.js's `score()`."""
    unit_score = float(len(friends) - len(enemies))
    health_score = sum(math.sqrt(h) for h in friends.values()) - sum(
        math.sqrt(h) for h in enemies.values()
    )

    surround: Dict[Coords, int] = {c: 0 for c in friends}
    surround.update({c: 0 for c in enemies})
    dist: Dict[Coords, float] = {c: 0.0 for c in friends}
    dist.update({c: 0.0 for c in enemies})

    for fc in friends:
        for ec in enemies:
            d = fc.distance_to(ec)
            if d == 0:
                continue
            d_score = 1.0 / (d * d)
            dist[ec] += d_score
            dist[fc] -= d_score
            if d == 1:
                surround[ec] += 1
                surround[fc] -= 1

    surround_score = sum(v * v for v in surround.values())
    distance_score = sum(v * v for v in dist.values())
    return (unit_score, float(surround_score), health_score, distance_score)


def _tick(
    fs: Dict[Coords, int],
    es: Dict[Coords, int],
    actions: Dict[Coords, Optional[Tuple[int, "Direction"]]],
    state: State,
) -> None:
    # Movement phase.
    for source, action in actions.items():
        if action is None:
            continue
        atype, direction = action
        if atype != _MOVE:
            continue
        target = source + direction
        if target in es or target in fs:
            continue
        if _is_blocked(state, target):
            continue
        obj = fs if source in fs else (es if source in es else None)
        if obj is None:
            continue
        obj[target] = obj[source]
        del obj[source]

    # Attack phase (uses original source coords, matching the real engine
    # resolving all this-turn actions off of pre-move-phase intent).
    for source, action in actions.items():
        if action is None:
            continue
        atype, direction = action
        if atype != _ATTACK:
            continue
        target = source + direction
        if target in es:
            es[target] -= 1
        if target in fs:
            fs[target] -= 1

    for c in [c for c, h in es.items() if h <= 0]:
        del es[c]
    for c in [c for c, h in fs.items() if h <= 0]:
        del fs[c]


def init_turn(state: State) -> None:
    global _PLAN
    _PLAN = {}
    _blocked_cache.clear()

    our_units = state.objs_by_team(state.our_team)
    if not our_units:
        return
    enemy_units = state.objs_by_team(state.other_team)

    friends: Dict[Coords, int] = {u.coords: u.health for u in our_units}
    enemies: Dict[Coords, int] = {u.coords: u.health for u in enemy_units}

    if not enemies:
        for u in our_units:
            _PLAN[u.id] = None
        return

    # --- Baseline enemy behavior assumption for our lookahead ---
    best_actions: Dict[Coords, Optional[Tuple[int, "Direction"]]] = {}
    for ecoord in enemies:
        best_actions[ecoord] = None
        lowest_health = 10 ** 9
        for d in ALL_DIRECTIONS:
            target = ecoord + d
            if target not in friends:
                continue
            h = friends[target]
            if h > lowest_health:
                continue
            lowest_health = h
            best_actions[ecoord] = (_ATTACK, d)

    # --- Enumerate legal actions per friend ---
    # Safety guard: simulate_score() is O(len(friends)*len(enemies)), and we
    # call it up to len(options) times per unit per pass. Round 3 investigation
    # (see README_agent.md) found the *old* threshold of 60 was WAY too low:
    # it triggered during essentially the entire mid/late game (friends and
    # enemies both routinely reach 10-15+ units by turn 30-40 thanks to
    # recurrent spawning), silently degrading our bot to "walk toward nearest
    # enemy" for most of the match - exactly when out-thinking the opponent
    # (e.g. black-magic.js, which has NO such guard and always full-searches)
    # matters most. Measured worst-case full-search runtime (self-play, the
    # scenario most likely to keep both team sizes large simultaneously) is
    # ~9s for a full 100-turn game, and ~10-13s against the builtin bots that
    # survive longest - all comfortably under the 60s forfeit limit. So the
    # guard is now effectively disabled (threshold raised far above anything
    # reachable on this map) and only kept as a pathological-case safety net.
    cheap_mode = len(friends) * len(enemies) > 4000
    possible_actions: Dict[Coords, List[Optional[Tuple[int, "Direction"]]]] = {}
    for fcoord in friends:
        best_actions[fcoord] = None
        opts: List[Optional[Tuple[int, "Direction"]]] = [None]
        if cheap_mode:
            nearest = min(enemies, key=lambda ec: fcoord.distance_to(ec))
            direction = fcoord.direction_to(nearest)
            candidate_dirs = [direction]
        else:
            candidate_dirs = ALL_DIRECTIONS
        for d in candidate_dirs:
            target = fcoord + d
            if _is_blocked(state, target):
                continue
            if target in enemies:
                opts.append((_ATTACK, d))
            else:
                opts.append((_MOVE, d))
        possible_actions[fcoord] = opts

    def simulate_score(actions):
        fs = dict(friends)
        es = dict(enemies)
        _tick(fs, es, actions, state)
        return _score(fs, es)

    best_score = simulate_score(best_actions)

    # --- Coordinate-ascent over our units' actions, a few passes for a
    # better local optimum than a single black-magic.js-style sweep. ---
    # Adaptive pass count: coordinate-ascent quality improves with more
    # passes, and extra passes are cheap when team sizes are small (which
    # is exactly when a slightly better local optimum matters most, e.g.
    # early game or once one side is nearly wiped out). Bounded by size so
    # we never risk the 60s forfeit limit in big mid-game battles.
    size = len(friends) * len(enemies)
    if size <= 100:
        PASSES = 3
    elif size <= 400:
        PASSES = 2
    else:
        PASSES = 1
    friend_coords = list(friends.keys())
    for _pass in range(PASSES):
        improved = False
        for fcoord in friend_coords:
            current = best_actions.get(fcoord)
            local_best_action = current
            local_best_score = best_score
            for opt in possible_actions[fcoord]:
                if opt == current:
                    continue
                trial = dict(best_actions)
                trial[fcoord] = opt
                s = simulate_score(trial)
                if s > local_best_score:
                    local_best_score = s
                    local_best_action = opt
            if local_best_action != current:
                improved = True
                best_actions[fcoord] = local_best_action
                best_score = local_best_score
        if not improved:
            break

    for u in our_units:
        act = best_actions.get(u.coords)
        if act is None:
            _PLAN[u.id] = None
        else:
            atype, d = act
            _PLAN[u.id] = Action.attack(d) if atype == _ATTACK else Action.move(d)


def robot(state: State, unit: Obj) -> Optional[Action]:
    return _PLAN.get(unit.id)
