import typing

def robot(state: State, unit: Obj):
    team = unit.team
    pos = unit.coords
    friends = get_team_by_distance(state, pos, team)
    close_friends = list(filter(lambda x: x[1] < 4, friends))
    enemies = get_team_by_distance(state, pos, team.opposite)
    adjacent_enemies = list(filter(lambda x: x[1] == 1, enemies))
    close_enemies = list(filter(lambda x: x[1] < 4, enemies))
    involved_close_enemies = list(filter(lambda x: friend_next_to(x[0].coords, friends), close_enemies))
    blocked = state.obj_by_coords(pos + Direction.North) is not None and \
        state.obj_by_coords(pos + Direction.East) is not None and \
        state.obj_by_coords(pos + Direction.South) is not None and \
        state.obj_by_coords(pos + Direction.West) is not None
    
    if adjacent_enemies and (unit.health >= adjacent_enemies[0][0].health or blocked):
        return Action.attack(pos.direction_to(adjacent_enemies[0][0].coords))
    if not adjacent_enemies and involved_close_enemies:
        return Action.move(pathfind_to(pos, involved_close_enemies[0][0].coords, friends, enemies))
    
    if close_friends:
        ## Healing not introduced yet...
        # wounded_friends = list(filter(lambda x: x[0].health < 5, close_friends))
        # if wounded_friends:
        #     (friend, distance) = wounded_friends[0]
        #     if distance > 1:
        #         return Action.move(pathfind_to(pos, friend.coords, friends, enemies))
        #     else:
        #         return Action.heal(pos.direction_to(friend.coords))
        if len(close_friends) >= min(len(friends) / 2, 3) and unit.health >= 5 and enemies:
            return Action.move(pathfind_to(pos, enemies[0][0].coords, friends, enemies))

    if friends:
        return Action.move(pathfind_to(pos, friends[0][0].coords, friends, enemies))
    
    if enemies:
        return Action.move(pos.direction_to(enemies[0][0].coords).opposite)
    else:
        return Action.attack(Direction.East)


def get_team_by_distance(state: State, pos: Coords, team: Team) -> typing.List[typing.Tuple[Obj, int]]:
    distanced = [(x, x.coords.walking_distance_to(pos)) for x in state.objs_by_team(team)]
    filtered = filter(lambda x: x[1] > 0, distanced)
    sort = sorted(filtered, key=lambda x: x[1])
    return sort

def pathfind_to(pos: Coords, target: Coords, friends: typing.List[typing.Tuple[Obj, int]], enemies: typing.List[typing.Tuple[Obj, int]]) -> Direction:
    return pos.direction_to(target)

def friend_next_to(pos: Coords, friends: typing.List[typing.Tuple[Obj, int]]) -> bool:
    return any([f for f in friends if f[0].coords == pos + Direction.North]) or \
        any([f for f in friends if f[0].coords == pos + Direction.East]) or \
        any([f for f in friends if f[0].coords == pos + Direction.South]) or \
        any([f for f in friends if f[0].coords == pos + Direction.West])

