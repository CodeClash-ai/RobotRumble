# arthur is basically the tutorial
# all of arthur's bots target the one enemy that is closest to all
# except there is someone next to them, then they just attack that one


target_id = None

def init_turn(state):
    global target_id

    if target_id:
        if not state.obj_by_id(target_id):
            # target has died
            target_id = None

    if target_id is None:
        allies = state.objs_by_team(state.our_team)

        def total_distance_for_team(enemy):
            return sum([ally.coords.distance_to(enemy.coords) for ally in allies])

        enemies = state.objs_by_team(state.other_team)
        closest_enemy = min(enemies, key=total_distance_for_team)
        target_id = closest_enemy.id

def robot(state, unit):
    global target_id
    
    # let us first check if we are next to an opponent, if so ATTACK
    enemies = state.objs_by_team(state.other_team)
    closest = min(enemies, key=lambda e: unit.coords.distance_to(e.coords))
    if unit.coords.distance_to(closest.coords) == 1:
        return Action.attack(unit.coords.direction_to(closest.coords))
    
    # else chase target
    target = state.obj_by_id(target_id)
    debug.locate(target)
    direction = unit.coords.direction_to(target.coords)

    if unit.coords.distance_to(target.coords) == 1:
        return Action.attack(direction)
    else:
        return Action.move(direction)
