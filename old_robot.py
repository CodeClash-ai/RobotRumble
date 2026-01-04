robot_state = {}

def robot(state, unit):
    target = state.obj_by_coords(unit.coords + Direction.West)
    
    if target:
        if target.team:
            if target.team == state.our_team:
                return None
            else:
                return Action.attack(Direction.East)
        else:
            # we've arrived
            return Action.attack(Direction.West)
    else:
        return Action.move(Direction.West)
