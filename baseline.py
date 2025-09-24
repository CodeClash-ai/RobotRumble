def robot(state, unit):
    # Simple baseline: move East on even turns, attack South on odd turns
    if state.turn % 2 == 0:
        return Action.move(Direction.East)
    else:
        return Action.attack(Direction.South)
