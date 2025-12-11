# The Perfect Battlebot
# If everything is random, there it always a chance the robot can win any match
import random

def robot(state, unit):
    if random.random() > 0.5:
        return moveRandom()
    else:
        return attackRandom(state, unit)

def moveRandom():
    randomDirection = random.random() * 4
    if randomDirection >= 2:
        if randomDirection >= 3:
            return Action.move(Direction.North)
        else:
            return Action.move(Direction.East)
    else:
        if randomDirection >= 1:
            return Action.move(Direction.South)
        else:
            return Action.move(Direction.West)

def attackRandom(state, unit):
    randomDirection = random.random() * 4
    if randomDirection >= 2:
        if randomDirection >= 3:
            target = state.obj_by_coords(unit.coords + Direction.North)
            if target:
                if target.team:
                    if target.team == state.our_team:
                            return moveRandom()
            else:
                return Action.attack(Direction.North)
        else:
            target = state.obj_by_coords(unit.coords + Direction.East)
            if target:
                if target.team:
                    if target.team == state.our_team:
                            return moveRandom()
            else:
                return Action.attack(Direction.East)
    else:
        if randomDirection >= 1:
            target = state.obj_by_coords(unit.coords + Direction.South)
            if target:
                if target.team:
                    if target.team == state.our_team:
                            return moveRandom()
            else:
                return Action.attack(Direction.South)
        else:
            target = state.obj_by_coords(unit.coords + Direction.West)
            if target:
                if target.team:
                    if target.team == state.our_team:
                            return moveRandom()
            else:
                return Action.attack(Direction.West)
