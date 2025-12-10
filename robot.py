def robot(state, unit):
        enemies = state.objs_by_team(state.other_team)
        closest_enemy = min(enemies,
                key=lambda e: e.coords.distance_to(unit.coords)
        )
        direction = unit.coords.direction_to(closest_enemy.coords)
        print(direction)
        print(unit.health)
        if unit.coords.distance_to(closest_enemy.coords)==1:
            return Action.attack(direction)
        else:
            return Action.move(direction)

