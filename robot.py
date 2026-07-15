"""
sonnet-5's RobotRumble bot.

STRATEGY NOTES (see README_agent.md for full history/analysis across rounds):

Round 0 finding: the original starter-bot's quadrant-based coordination has
a critical bug (mirrored spawn points via 180-degree point reflection mean a
robot's quadrant frequently has zero allies in it, so it freezes forever).
Round 0's rewrite fixed this with global focus-fire + opportunistic adjacent
attack + direction_to movement w/ sidestep fallback, and won 250/250 games
against `happysquid__test`.

This round's change: replaced the single hard "everyone marches to the same
global target" macro strategy with a *soft* per-unit target score that still
uses the team's shared focus target as a tie-breaking/clustering signal, but
also accounts for (a) each individual unit's own distance to a candidate
target (so units don't all sprint across the map ignoring a much closer
enemy) and (b) the candidate's remaining health (so we prefer finishing off
already-damaged enemies -- a unit at 1 HP is one more hit from death no
matter which unit lands it, so it's always at least as good a target as a
fresh one at equal distance). This should help more once units get spread
out across the map (e.g. right after the periodic 10-turn respawn scatters
fresh units at random spawn points) since previously *every* unit would beeline
for the single global focus target even if a much closer, nearly-dead enemy
was sitting right next to it (mitigated in the old code only by the
opportunistic-adjacent-attack check, which doesn't help until a unit is
already adjacent).

Kept from before:
- Opportunistic attack: ALWAYS attack an adjacent enemy rather than move,
  preferring the weakest one (to secure kills), regardless of the global
  focus target.
- direction_to-based movement with a sidestep fallback (try both
  perpendiculars, preferring whichever gets closer to the target, then the
  opposite direction) when the direct path is blocked by a wall or unit, so
  robots don't get stuck idling like the original starter bot did.
"""

from typing import *


# ---- Global team state (persists across turns) ----
focus_target_id: Optional[str] = None
robot_state: Dict[str, dict] = {}

# Tunable weights for the per-unit soft targeting score (lower score = more
# attractive target). See module docstring for rationale.
HEALTH_WEIGHT = 0.6       # prefer already-damaged enemies
FOCUS_BONUS = 2.0         # bonus (score reduction) for the shared team target
COORD_WEIGHT = 0.15       # mild pull toward wherever the team overall wants to go


def total_distance_for_units(units: List[Obj], target: Obj) -> float:
    return sum(unit.coords.distance_to(target.coords) for unit in units)


def init_turn(state: State) -> None:
    """Pick (or keep) a single focus-fire target for the whole team.

    This is now used as a *soft* clustering signal in per-unit targeting
    (see `robot()`), not a hard mandate -- individual units may still peel
    off toward a much closer/weaker enemy.
    """
    global focus_target_id

    allies = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)

    if not enemies or not allies:
        focus_target_id = None
        return

    # Drop the old target if it died.
    if focus_target_id and not state.obj_by_id(focus_target_id):
        focus_target_id = None

    if not focus_target_id:
        best = min(
            enemies,
            key=lambda e: total_distance_for_units(allies, e) + e.health * HEALTH_WEIGHT,
        )
        focus_target_id = best.id


def _first_free_dir(state: State, unit: Obj, dirs: List[Direction], past_coords) -> Optional[Direction]:
    for d in dirs:
        dest = unit.coords + d
        if dest == past_coords:
            continue
        if not state.obj_by_coords(dest):
            return d
    # second pass: allow revisiting past_coords if truly nothing else works
    for d in dirs:
        dest = unit.coords + d
        if not state.obj_by_coords(dest):
            return d
    return None


def _pick_personal_target(state: State, unit: Obj, enemies: List[Obj], allies: List[Obj]) -> Obj:
    """Pick this unit's individual movement target.

    Blends: this unit's own distance to the candidate (primary factor so we
    don't ignore a nearby enemy in favor of a far-off global target),
    candidate health (prefer finishing off weakened enemies), and a mild
    bonus for the team's shared focus target (keeps some clustering/
    coordination without forcing every unit onto the same tile).
    """

    def score(e: Obj) -> float:
        s = unit.coords.distance_to(e.coords)
        s += e.health * HEALTH_WEIGHT
        s += total_distance_for_units(allies, e) * COORD_WEIGHT
        if e.id == focus_target_id:
            s -= FOCUS_BONUS
        return s

    return min(enemies, key=score)


def robot(state: State, unit: Obj) -> Optional[Action]:
    st = robot_state.setdefault(unit.id, {})
    past_coords = st.get("past_coords")
    st["past_coords"] = unit.coords

    enemies = state.objs_by_team(state.other_team)
    if not enemies:
        return None

    # 1) Opportunistic attack: if any enemy is adjacent, always attack.
    #    Prefer the weakest adjacent enemy to secure kills, tie-break toward
    #    the team's focus target.
    adjacent_enemies = [e for e in enemies if unit.coords.walking_distance_to(e.coords) == 1]
    if adjacent_enemies:
        def adj_score(e: Obj):
            return (e.health, 0 if e.id == focus_target_id else 1)

        target = min(adjacent_enemies, key=adj_score)
        debug.inspect("attacking", target.id)
        return Action.attack(unit.coords.direction_to(target.coords))

    # 2) Otherwise, move toward this unit's personal target (blend of
    #    proximity, target health, and team coordination -- see
    #    `_pick_personal_target`).
    allies = state.objs_by_team(state.our_team)
    target = _pick_personal_target(state, unit, enemies, allies)

    debug.inspect("moving_toward", target.id)
    direction = unit.coords.direction_to(target.coords)
    dest = unit.coords + direction

    blocker = state.obj_by_coords(dest)
    if not blocker:
        return Action.move(direction)

    # Path blocked (wall or unit) -- try to sidestep around it, preferring
    # whichever perpendicular direction gets us closer to the target.
    perp_dirs = [direction.rotate_cw, direction.rotate_ccw]
    perp_dests = [unit.coords + d for d in perp_dirs]
    if target.coords.distance_to(perp_dests[0]) > target.coords.distance_to(perp_dests[1]):
        perp_dirs = [perp_dirs[1], perp_dirs[0]]

    chosen = _first_free_dir(state, unit, perp_dirs + [direction.opposite], past_coords)
    if chosen:
        return Action.move(chosen)

    return None
