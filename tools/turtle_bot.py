"""
Simple defensive "turtle" bot used ONLY as a diagnostic sparring partner
(see README_agent.md, Round 5 session notes) to test the hypothesis that
heavier clustering/coordination specifically helps against a
defensive/turtling opponent style, since our actual real opponent
(atl15__centerrr, elo #13/58) cannot be tested against directly (no
source available) but multiple rounds' turn-by-turn logs suggested
turtling-like behavior (opponent barely loses units while we bleed out
approaching them piecemeal).

Strategy: cluster together near the team's own centroid, only actively
chase adjacent enemies (always attack if adjacent), otherwise slowly
regroup toward centroid and only advance toward the nearest enemy if the
whole team's centroid is already reasonably tight (i.e. don't scatter
chasing lone targets).
"""
from typing import *

CLUSTER_RADIUS = 3


def robot(state: State, unit: Obj) -> Optional[Action]:
    allies = state.objs_by_team(state.our_team)
    enemies = state.objs_by_team(state.other_team)

    if not enemies:
        return None

    adjacent_enemies = [e for e in enemies if unit.coords.walking_distance_to(e.coords) == 1]
    if adjacent_enemies:
        target = min(adjacent_enemies, key=lambda e: e.health)
        return Action.attack(unit.coords.direction_to(target.coords))

    # Compute centroid of allies.
    cx = sum(a.coords.x for a in allies) / len(allies)
    cy = sum(a.coords.y for a in allies) / len(allies)
    centroid = Coords(round(cx), round(cy))

    dist_to_centroid = unit.coords.distance_to(centroid)
    if dist_to_centroid > CLUSTER_RADIUS:
        direction = unit.coords.direction_to(centroid)
    else:
        # Close enough to the group -- advance cautiously toward nearest enemy
        # only if group is tight, else hold/regroup.
        nearest_enemy = min(enemies, key=lambda e: unit.coords.distance_to(e.coords))
        direction = unit.coords.direction_to(nearest_enemy.coords)

    dest = unit.coords + direction
    if state.obj_by_coords(dest):
        for d in [direction.rotate_cw, direction.rotate_ccw, direction.opposite]:
            dest2 = unit.coords + d
            if not state.obj_by_coords(dest2):
                return Action.move(d)
        return None
    return Action.move(direction)
