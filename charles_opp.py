target_id = None

def init_turn(state):
    global target_id

    if target_id:
        if not state.obj_by_id(target_id):
            # target has died
            target_id = None

    if not target_id:
        allies = state.objs_by_team(state.our_team)

        def total_distance_for_team(enemy):
            return sum([ally.coords.distance_to(enemy.coords) for ally in allies])

        enemies = state.objs_by_team(state.other_team)
        closest_enemy_for_team = min(enemies,
            key=total_distance_for_team
        )
        target_id = closest_enemy_for_team.id

def robot(state, unit):
    target = state.obj_by_id(target_id)
    debug.locate(target)
    direction = unit.coords.direction_to(target.coords)

    if unit.coords.distance_to(target.coords) == 1:
        # we're right next to them
        return Action.attack(direction)
    else:
        return Action.move(direction)
