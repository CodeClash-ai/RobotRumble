"""
sonnet-5's RobotRumble bot.

STRATEGY NOTES (see README_agent.md for full analysis):
- The original starter-bot's quadrant-based coordination has a critical bug:
  spawn locations are mirrored via 180-degree point reflection (not a
  left/right mirror), so a robot's quadrant frequently has ZERO allies in it.
  When that happens `target_ids[q]` is never set and the robot returns None
  forever -> robots never move or attack. Round 0 confirmed this: literally
  every single one of the 250 simulated games ended 20-20 health / 4-4 units,
  i.e. ZERO combat ever happened.
- This bot fixes that by using simple, robust, global (non-quadrant) target
  selection: pick one focused enemy target for the whole team (to concentrate
  damage and get kills faster, since it takes 5 hits to kill a unit), but
  ALWAYS opportunistically attack any adjacent enemy (not just the team's
  focus target) so we never waste a free attack.
- Movement uses direction_to plus a sidestep fallback when the direct path is
  blocked by a wall/unit, and never just gives up (falls back to trying any
  free adjacent tile) so robots don't get stuck idling.
"""

from typing import *


# ---- Global team state (persists across turns) ----
focus_target_id: Optional[str] = None
robot_state: Dict[str, dict] = {}


def total_distance_for_units(units: List[Obj], target: Obj) -> float:
    return sum(unit.coords.distance_to(target.coords) for unit in units)


def init_turn(state: State) -> None:
    """Pick (or keep) a single focus-fire target for the whole team."""
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
        best = min(enemies, key=lambda e: total_distance_for_units(allies, e))
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


def robot(state: State, unit: Obj) -> Optional[Action]:
    global focus_target_id

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
        def score(e: Obj):
            return (e.health, 0 if e.id == focus_target_id else 1)

        target = min(adjacent_enemies, key=score)
        debug.inspect("attacking", target.id)
        return Action.attack(unit.coords.direction_to(target.coords))

    # 2) Otherwise, move toward the team's focus target (fallback: nearest enemy).
    target_id = focus_target_id
    target = state.obj_by_id(target_id) if target_id else None
    if not target:
        target = min(enemies, key=lambda e: unit.coords.distance_to(e.coords))

    debug.inspect("moving_toward", target.id)
    direction = unit.coords.direction_to(target.coords)
    dest = unit.coords + direction

    blocker = state.obj_by_coords(dest)
    if not blocker:
        if dest != past_coords or True:
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
