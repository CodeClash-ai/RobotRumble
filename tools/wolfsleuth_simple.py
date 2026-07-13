target_id = None

def init_turn(state):
    global target_id

    allies = state.objs_by_team(state.our_team)

    def total_distance_for_team(enemy):
        return sum([ally.coords.distance_to(enemy.coords) for ally in allies])

    enemies = state.objs_by_team(state.other_team)
    closest_enemy_for_team = min(enemies,
        key=total_distance_for_team
    )
    target_id = closest_enemy_for_team.id

def robot(state, unit):
    close = []
    target = state.obj_by_id(target_id)
    debug.locate(target)
    direction = unit.coords.direction_to(target.coords)
    for i in state.objs_by_team(state.other_team):
        if unit.coords.distance_to(i.coords) == 1:
            close.append(i)
    if len(close) >= 1:
        min_health = 5
        for i in close:
            if i.health < min_health:
                min_health = i.health
                target = i
        return Action.attack(unit.coords.direction_to(i.coords))
    return Action.move(direction)
