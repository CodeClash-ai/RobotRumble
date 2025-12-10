class Robot:
    def __init__(self, state, unit):
        self.state = state
        self.unit = unit

    def retreat(self):
        enemies = []
        blanks = []
        for direction in Direction:
            other = self.state.obj_by_coords(self.unit.coords + direction)
            if other and other.team == self.state.other_team:
                enemies.append(other)
            elif not other:
                blanks.append(direction)

        # retreat if more than one enemy and there is room to retreat
        if not blanks:
            return None
        elif len(enemies) > 1 or (
            len(enemies) == 1 and enemies[0].health > self.unit.health
        ):
            return blanks[0]
        else:
            return None

    def walk_to(self, from_coords, to_coords):
        x = to_coords.x - from_coords.x
        y = to_coords.y - from_coords.y

        xdir = Direction.East if x > 0 else Direction.West
        ydir = Direction.South if y > 0 else Direction.North

        blanks = []
        for direction in Direction:
            other = self.state.obj_by_coords(from_coords + direction)
            if not other:
                blanks.append(direction)

        if abs(x) > abs(y) and xdir in blanks:
            return xdir
        elif abs(y) >= abs(x) and ydir in blanks:
            return ydir
        elif xdir in blanks:
            return xdir
        elif ydir in blanks:
            return ydir
        elif blanks:
            return blanks[0]
        else:
            return None

    def main(self):
        enemies = self.state.objs_by_team(self.state.other_team)
        if not enemies:
            return None
        closest_enemy = min(
            enemies,
            key=lambda e: (e.coords.walking_distance_to(self.unit.coords), e.health),
        )
        direction = self.walk_to(self.unit.coords, closest_enemy.coords)

        retreat_dir = self.retreat()
        if retreat_dir:
            return Action.move(retreat_dir)

        enemy_direction = self.unit.coords.direction_to(closest_enemy.coords)
        obj = self.state.obj_by_coords(self.unit.coords + enemy_direction)
        if self.unit.coords.walking_distance_to(closest_enemy.coords) <= 2 and not (
            obj and obj.team == self.state.our_team
        ):
            # we're either right next to them, or suspect they will move next
            # to us
            return Action.attack(enemy_direction)
        elif direction:
            return Action.move(direction)
        else:
            return None


def robot(state, unit):
    return Robot(state, unit).main()

