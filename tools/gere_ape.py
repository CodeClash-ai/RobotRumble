from typing import (
    Dict,
    NamedTuple,
    Sequence,
    Hashable,
    List,
    Optional,
    Tuple,
    Set,
)
from collections import namedtuple
import random


robot_actions: Dict[
    str, Action
] = {}  # Global variable to store all actions in init_turn() and to be used in robot()


Shift = namedtuple("Shift", "x y")


shift_to_direction: Dict[Tuple, Direction] = {
    (1, 0): Direction.East,
    (-1, 0): Direction.West,
    (0, 1): Direction.South,
    (0, -1): Direction.North,
}


# A plan contains an .action for an .id
# Plans are selected by *lowest* .score such that for each .target there is only one selection
Plan = namedtuple(
    "Plan",
    [
        "id",  # str: id of object
        "target",  # Hashable: only one target will be selected from all equal targets
        "score",  # float: minimum score is highest priority
        "action",  # Action: action to be executed])
    ],
)


def make_info(state: State) -> Dict:
    """
    Return anything you want to pre-calculate at the beginning of a turn
    """
    return {}


def make_obj_plan(state: State, info: Dict, obj: Obj) -> Sequence[Plan]:
    """
    Should emit a list of plans for the current object
    """
    
    result: List[Plan] = []
        
    # Attack neighbor
    enemies_around = [
        next_obj
        for shift in get_neighborhood()
        for next_obj in [state.obj_by_coords(obj.coords + shift)]
        if next_obj is not None and next_obj.team == state.other_team
    ]
    
    if len(enemies_around)>=2 or (len(enemies_around)==1 and enemies_around[0].health>obj.health):
        # run away
        escape_plans = []
        
        for shift in get_neighborhood():
            next_pos=obj.coords + shift
            if state.obj_by_coords(next_pos) is None:
                plan = Plan(
                    id=obj.id,
                    target=next_pos,
                    score=-1,
                    action=Action.move(shift_to_direction[shift]),
                )
                
                escape_plans.append(plan)
                
        result.extend(escape_plans)
        
        # attack weakest
        if not escape_plans:
            weakest_enemy=min(enemies_around, key=lambda x:x.health)
            shift=weakest_enemy.coords-obj.coords
            plan = Plan(
                id=obj.id,
                target=obj.coords,
                score=-1,
                action=Action.attack(shift_to_direction[shift]),
            )

            result.append(plan)
    elif enemies_around:
        # attack weakest
        weakest_enemy=min(enemies_around, key=lambda x:x.health)
        shift=weakest_enemy.coords-obj.coords

        plan = Plan(
            id=obj.id,
            target=obj.coords,
            score=-1,
            action=Action.attack(shift_to_direction[shift]),
        )

        result.append(plan)           
            
    if result:
        return result
       
        
    # Go center
    center=Coords(9,9)
    for shift in get_directions_to(center-obj.coords):
        next_pos = obj.coords + shift

        direction = shift_to_direction[shift]

        action = Action.move(direction)
        
        go_center = Plan(
            id=obj.id,
            target=next_pos,
            score=100,
            action=action,
        )
        
        result.append(go_center)
        
    # Chase weaker
    
    enemies = [enemy for enemy in state.objs_by_team(state.other_team) if enemy.health<obj.health]

    if enemies:
        closest_enemies, distance = find_closest(obj, enemies, get_dist)
        closest_enemy = random.choice(closest_enemies)

        shifts = get_directions_to(closest_enemy.coords - obj.coords)

        for shift in shifts:
            assert shift != (0, 0)  # should never happen

            next_pos = obj.coords + shift

            direction = shift_to_direction[shift]

            action = Action.move(direction)

            plan = Plan(
                id=obj.id,
                target=next_pos,
                score=distance,
                action=action,
            )
            result.append(plan)

    return result


##############################################################
### Following functions probably do not have to be changed ###
##############################################################


def init_turn(state: State):
    """
    run once for each turn
    use this to initialize global variables to be used by all units
    """
    global robot_actions

    info = make_info(state)
    plans = make_plans(state, info)
    selected_actions = select_plans(plans)
    robot_actions = selected_actions


def robot(state: State, unit: Obj) -> Optional[Action]:
    """
    called for each bot and needs to return an action
    """

    return robot_actions.get(unit.id)  # bots without plans will return None and be idle


def make_plans(state: State, info: Dict) -> List[Plan]:
    plans: List[Plan] = []

    for obj in state.objs_by_team(state.our_team):
        try:
            plans.extend(make_obj_plan(state, info, obj))
        except Exception as exc:
            import traceback
            print(exc)
            traceback.print_exc()

    return plans


def select_plans(plans: List[Plan]) -> Dict[str, Action]:
    # Simple greedy selection by lowest score
    targets_used: Set[Hashable] = set()
    random.shuffle(plans)  # to avoid systematic priority effects
    plans = sorted(plans, key=lambda x: x.score)

    result: Dict[str, Action] = {}

    for plan in plans:
        if plan.id in result or (
            plan.target is not None and plan.target in targets_used
        ):
            continue

        result[plan.id] = plan.action
        targets_used.add(plan.target)

    return result


def dist_from_center(coord: Coords):
    # "octagonal distance"
    dx = coord.x - 9
    dy = coord.y - 9
    return max(abs(dx), abs(dy), abs(dx) + abs(dy) - 4)


def is_spawn_turn(turn: int) -> bool:
    return turn % 10 == 0


def is_inside_field(coord: Coords):
    return dist_from_center(coord) <= 8


def is_inside_nonspawn(coord: Coords):
    return dist_from_center(coord) < 8


def is_spawn_region(coord: Coords):
    return dist_from_center(coord) == 8


def get_dist(obj1: Obj, obj2: Obj) -> int:
    return obj1.coords.walking_distance_to(obj2.coords)


def find_closest_idx(obj, others, dist_func) -> Tuple[List[int], Optional[int]]:
    """
    Return indices of position from poses2 which is closest to pos1
    Also return distance
    """
    if not others:
        return [], None

    distances = [dist_func(obj, other) for other in others]

    shortest_distance = min(distances)

    indices = [
        i for i, distance in enumerate(distances) if distance == shortest_distance
    ]

    return (
        indices,
        shortest_distance,
    )


def find_closest(obj, others, dist_func):
    closest_indices, distance = find_closest_idx(obj, others, get_dist)
    return [others[i] for i in closest_indices], distance


def get_directions_to(shift: Coords) -> Set[Coords]:
    """
    Returns all directions that would bring you closer along shift
    """
    if shift == (0, 0):
        return {Coords(0, 0)}

    result: Set[Coords] = set()

    if shift.x > 0:
        result.add(Coords(1, 0))

    if shift.x < 0:
        result.add(Coords(-1, 0))

    if shift.y > 0:
        result.add(Coords(0, 1))

    if shift.y < 0:
        result.add(Coords(0, -1))

    return result


def get_neighborhood(dists: Sequence[int] = (1,)) -> List[Coords]:
    """
    Returns shifts to neighborhood positions at distances dists
    """
    result = []

    for dist in dists:
        if dist == 0:
            result.append(Coords(0, 0))
            continue
        for d in range(dist):
            result.append(Coords(d, dist - d))
            result.append(Coords(-d, -dist + d))
            result.append(Coords(-dist + d, d))
            result.append(Coords(dist - d, -d))

    return result
