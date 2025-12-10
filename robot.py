# pylint: disable=missing-function-docstring,missing-module-docstring
# pylint: disable=missing-class-docstring,invalid-name,too-few-public-methods
import random
from enum import Enum
from typing import List

if False:  # pylint: disable=using-constant-test
    try:
        from api import Coords, Direction, Obj, ObjType, State, Team
    except:  # nosec pylint: disable=bare-except
        pass

AType = Enum('AType', 'move attack wait')


class Score:
    def __init__(self, state: State, frm: Coords, coord: Coords) -> None:
        self.our_points = len(state.objs_by_team(state.our_team))
        self.other_points = len(state.objs_by_team(state.other_team))
        self.nearest_friend = -1 * min([
            x.coords.walking_distance_to(coord)
            for x in state.objs_by_team(state.our_team) if x.coords != frm
        ])

        self.our_health = sum(
            [x.health for x in state.objs_by_team(state.our_team)])
        self.other_health = sum(
            [x.health for x in state.objs_by_team(state.other_team)])

    @property
    def points(self) -> int:
        ''' Returns delta between our and other points '''
        return self.our_points - self.other_points

    @property
    def health(self) -> int:
        ''' Returns delta between our and other health '''
        return self.our_health - self.other_health

    def __eq__(self, other) -> bool:
        return (self.points, self.health,
                self.nearest_friend) == (other.points, other.health,
                                         other.nearest_friend)

    def __gt__(self, other) -> bool:
        return not self.__lt__(other)

    def __ge__(self, other) -> bool:
        return not self.__le__(other)

    def __le__(self, other) -> bool:
        return self.points <= other.points or (
            self.points == other.points and self.health <= other.health) \
                    or (self.points == other.points and self.health ==
                            other.health and self.nearest_friend <=
                            other.nearest_friend)

    def __lt__(self, other) -> bool:
        return self.points < other.points \
                or (self.points == other.points and self.health <
                        self.other_health) \
                    or (self.points == other.points and self.health ==
                            other.health and self.nearest_friend <
                            other.nearest_friend)

    def __repr__(self) -> str:
        return "Score(%dp/%dh | %d )" % (self.points, self.health,
                                         self.nearest_friend)


class ActionChoice:
    def __init__(self, _type: AType, _dir: Direction, coord):
        self.type = _type
        self.dir = _dir
        self.frm = coord
        if _type == AType.wait:
            self.coord = coord
        else:
            self.coord = coord + _dir

        self.score = None

    def __repr__(self) -> str:
        if self.type == AType.move:
            _type = "MOVE"
        elif self.type == AType.wait:
            _type = "WAIT"
        elif self.type == AType.attack:
            _type = "ATCK"

        dir_name = "Here"
        if self.dir:
            dir_name = self.dir.name
        return "%s[%s] (%s, %s)" % (_type, self.score, dir_name, self.coord)


def generate_all_actions(coord) -> List[ActionChoice]:
    return [
        ActionChoice(AType.wait, None, coord),
        ActionChoice(AType.move, Direction.North, coord),
        ActionChoice(AType.move, Direction.East, coord),
        ActionChoice(AType.move, Direction.South, coord),
        ActionChoice(AType.move, Direction.West, coord),
        ActionChoice(AType.attack, Direction.North, coord),
        ActionChoice(AType.attack, Direction.East, coord),
        ActionChoice(AType.attack, Direction.South, coord),
        ActionChoice(AType.attack, Direction.West, coord),
    ]


def enemies_coords(state: State) -> List[Coords]:
    return [x.coords for x in state.objs_by_team(state.other_team)]


def has_legal_coord(c: Coords) -> bool:
    if c.x <= 0 or c.x > 17 or c.y <= 0 or c.y > 17:
        return False
    if c.y <= 5 - c.x:
        return False
    if c.y <= c.x - 13:
        return False
    if c.y >= c.x + 13:
        return False
    if c.y >= 31 - c.x:
        return False
    return True


def legal_actions(coord) -> List[ActionChoice]:
    return [x for x in generate_all_actions(coord) if has_legal_coord(x.coord)]


def remove_stupid_actions(state: State,
                          choices: List[ActionChoice]) -> List[ActionChoice]:
    em_coords = enemies_coords(state)
    result = []
    for ac in choices:
        # do not move in to enemies
        if ac.type == AType.move and ac.coord not in em_coords:
            result.append(ac)
        # only attack if coord has an enemy
        elif ac.type == AType.attack and ac.coord in em_coords:
            result.append(ac)
        elif ac.type == AType.wait:
            result.append(ac)
    return result


def execute_choice(choice: ActionChoice):
    # pylint: disable=undefined-variable
    if choice.type == AType.move:
        return Action.move(choice.dir)
    if choice.type == AType.attack:
        return Action.attack(choice.dir)
    return None


def filter_best_action_choices(
        choices: List[ActionChoice]) -> List[ActionChoice]:
    choices.sort(key=lambda x: x.score)
    best = choices[-1]
    return [ac for ac in choices if ac.score == best.score]


def current_score(state: State) -> int:
    our_score = sum([x.health for x in state.objs_by_team(state.our_team)])
    other_score = sum([x.health for x in state.objs_by_team(state.other_team)])
    return our_score - other_score


def adjacent(coord: Coords) -> List[Coords]:
    tmp = [
        Coords(coord.x - 1, coord.y),
        Coords(coord.x + 1, coord.y),
        Coords(coord.x, coord.y - 1),
        Coords(coord.x, coord.y + 1),
    ]

    return [x for x in tmp if has_legal_coord(x)]


def count_simulated_attacks(state, coord: Coords, team: Team) -> Score:
    result = 0
    neighbours = adjacent(coord)
    enemy_coords = [x.coords for x in state.objs_by_team(team)]
    for n in neighbours:
        if n in enemy_coords:
            result += 1
    return result


def simulate_attack(state: State, score: Score, to: Coords,
                    team: Team) -> Score:
    # simulate attack by our team
    enemy_unit: Obj = state.obj_by_coords(to)
    assert enemy_unit.obj_type == ObjType.Unit  # nosec
    enemy_unit_health = enemy_unit.health
    enemy_units_coords = [x.coords for x in state.objs_by_team(team)]
    damage = 0
    for x in adjacent(to):
        if x in enemy_units_coords:
            damage += 1
            if enemy_unit_health == damage:
                break
    assert damage <= enemy_unit_health  # nosec
    score.other_health -= damage
    if damage == enemy_unit.health:
        score.other_points -= 1
    return score


def score_choices(state: State, choices: List[ActionChoice]):
    for choice in choices:
        cur_score = Score(state, choice.frm, choice.coord)
        choice.score = cur_score
        if choice.type == AType.wait:
            choice.score = simulate_attack(state, choice.score, choice.coord,
                                           state.other_team)
        elif choice.type == AType.attack:
            choice.score = simulate_attack(state, choice.score, choice.coord,
                                           state.our_team)
            choice.score = simulate_attack(state, choice.score,
                                           choice.coord + choice.dir.opposite,
                                           state.other_team)
        elif choice.type == AType.move:
            pass
        else:
            assert False, "Unknown choice.type %s" % choice.type


def robot(state: State, unit: Obj):
    choices = remove_stupid_actions(state, legal_actions(unit.coords))
    if not choices:
        return None

    score_choices(state, choices)

    best_choices = filter_best_action_choices(choices)
    # debug.inspect('ALL', generate_all_choices())
    for (i, v) in enumerate(choices):
        # pylint: disable=undefined-variable
        debug.inspect('Action %d' % i, v)
    choice = random.choice(best_choices)  # nosec
    debug.inspect("Picked ⇒ ", choice)  # pylint: disable=undefined-variable
    return execute_choice(choice)  # nosec


def init_turn(state) -> None:
    our_score = len(state.objs_by_team(state.our_team))
    other_score = len(state.objs_by_team(state.other_team))
    delta_score = our_score - other_score

    print("SCORE: %d / %d ⇒ %d" % (our_score, other_score, delta_score))

