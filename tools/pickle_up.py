import typing

def robot(state: State, unit: Obj):
    team = unit.team
    pos = unit.coords
    friends = state.ids_by_team(team)
    enemies = state.ids_by_team(team.opposite)
    if enemies:
        target = state.obj_by_id(min(enemies))
        enemies = order_by_distance(state.objs_by_team(team.opposite), pos)
        move_direction = pos.direction_to(target.coords)
        move_blocked = state.obj_by_coords(pos + move_direction) is not None

        if move_blocked:
            attackables = filter(lambda x: x[1] <= 2, enemies)
            directions = distinct(flat_map(lambda x: get_directions_for_target(pos, x[0].coords), attackables))
            directions = list(filter(lambda x: not is_team_at(state, pos + x, team), directions))
            try:
                min_enemy_health = min(directions, key=lambda x: o.health if (o := state.obj_by_coords(pos + x)) is not None and o.obj_type == ObjType.Unit else 10)
                return Action.attack(min_enemy_health)
            except ValueError:
                pass
        
        return Action.move(move_direction)

    else:
        return Action.move(pos.direction_to(Coords(9, 9)))

def order_by_distance(units: typing.List[Obj], pos: Coords) -> typing.List[typing.Tuple[Obj, int]]:
    distanced = [(x, x.coords.walking_distance_to(pos)) for x in units]
    filtered = filter(lambda x: x[1] > 0, distanced)
    sort = sorted(filtered, key=lambda x: x[1])
    return sort

def get_directions_for_target(pos: Coords, target: Coords):
    diff = target - pos
    res = []
    if diff.x > 0:
        res.append(Direction.East)
    elif diff.x < 0:
        res.append(Direction.West)
    if diff.y > 0:
        res.append(Direction.South)
    elif diff.y < 0:
        res.append(Direction.North)
    return res

def distinct(list):
    res = []
    for i in list:
        if i not in res:
            res.append(i)
    return res

def flat_map(f, l):
    res = []
    for i in l:
        res.extend(f(i))
    return res

def is_team_at(state: State, pos: Coords, team: Team):
    return (obj := state.obj_by_coords(pos)) is not None and \
            obj.obj_type == ObjType.Unit and \
            obj.team == team

