import typing


class GameState():
    def __init__(self, state):
        self._state = state
        self._obstacles = []
        self._empty = []
        for i in range(0, MAP_SIZE):
            for j in range(0, MAP_SIZE):
                p = Coords(j, i)
                if not state.id_by_coords(p):
                    self._empty.append(p)
                else:
                    self._obstacles.append(p)
        self._enemies = self._state.objs_by_team(self._state.other_team)

    @property
    def enemies(self) -> typing.List[Obj]:
        return self._enemies

    def is_empty(self, pos) -> bool:
        return pos in self._empty

    def eligible_moves(self, from_pos):
        return list(filter(lambda x: self.is_empty(x), from_pos.coords_around()))

    def do_move(self, from_pos, action):
        if not action:
            return
        if action.type == ActionType.Attack:
            target = from_pos + action.direction
            idx = None
            for (i, e) in enumerate(self._enemies):
                if e.coords == target:
                    idx = i
                    break
            if not idx:
                return
            if self._enemies[idx].__data["health"] > 1:
                self._enemies[idx].__data["health"] -= 1
            else:
                del self._enemies[idx]
        elif action.type == ActionType.Move:
            to_pos = from_pos + action.direction
            self._obstacles.remove(from_pos)
            self._obstacles.append(to_pos)
            self._empty.remove(to_pos)
            self._empty.append(from_pos)


class Robot():
    def __init__(self, unit) -> None:
        self._unit = unit
        self._action = None
        self._target = None

    @property
    def pos(self) -> Coords:
        return self._unit.coords

    @property
    def id(self) -> str:
        return self._unit.id

    @property
    def hp(self) -> int:
        return self._unit.health

    @property
    def action(self) -> typing.Optional[Action]:
        if self._action:
            return self._action
        else:
            None

    @property
    def target(self) -> typing.Optional[Obj]:
        return self._target

    def __repr__(self) -> str:
        return f"<{self.pos} {self.id}, {self.hp}>"

    # micro
    def select_closest_target(self, gstate):
        closest_enemy = min(
            gstate.enemies, key=lambda enemy: self.pos.distance_to(enemy.coords))
        self._target = closest_enemy

    def is_eligible_move(self, gstate, direction) -> bool:
        new_pos = self._unit.coords + direction
        return new_pos in gstate.eligible_moves(self.pos)

    def micro_logic(self, gstate):
        if not self._target:
            self.select_closest_target(gstate)
        if not self._target:
            self._action = None
            return
        direction = self._unit.coords.direction_to(self._target.coords)
        if self.pos.distance_to(self._target.coords) == 1:
            self._action = Action.attack(direction)
        elif self.is_eligible_move(gstate, direction):
            self._action = Action.move(direction)
        else:
            self._action = None

    def do_action(self, gstate) -> typing.Optional[Action]:
        gstate.do_move(self.pos, self.action)
        return self.action


# global State
globalState = None


def init_turn(state):
    global globalState
    globalState = GameState(state)


def robot(state, unit):
    r = Robot(unit)
    r.micro_logic(globalState)
    print(f"{r.pos}:{globalState.eligible_moves(r.pos)} | target (pos: {r.target.coords}, hp: {r.target.health}) -> {r.action}")
    return r.do_action(globalState)

