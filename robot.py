# Matchup-specific counter for mitch84__retreat_walk2.
# The opponent wins unit-count endgames by retreating from bad adjacent fights and
# preserving bodies.  Use the same conservative survival policy rather than the
# black-magic contact planner, with a couple of small focus-fire improvements.

DIRS = [Direction.North, Direction.South, Direction.East, Direction.West]


def retreat(state, unit):
    enemies = []
    blanks = []
    for direction in DIRS:
        other = state.obj_by_coords(unit.coords + direction)
        if other and other.team == state.other_team:
            enemies.append(other)
        elif not other:
            blanks.append(direction)

    # Run from being dogpiled, or from a single adjacent enemy that wins the duel.
    if len(enemies) > 1 and blanks:
        return blanks[0]
    if len(enemies) == 1 and blanks and enemies[0].health > unit.health:
        return blanks[0]
    return None


def walk_to(state, from_coords, to_coords):
    x = to_coords.x - from_coords.x
    y = to_coords.y - from_coords.y
    xdir = Direction.East if x > 0 else Direction.West
    ydir = Direction.South if y > 0 else Direction.North

    blanks = []
    for direction in DIRS:
        if not state.obj_by_coords(from_coords + direction):
            blanks.append(direction)

    if abs(x) > abs(y) and xdir in blanks:
        return xdir
    if abs(y) >= abs(x) and ydir in blanks:
        return ydir
    if xdir in blanks:
        return xdir
    if ydir in blanks:
        return ydir
    if blanks:
        return blanks[0]
    return None


def robot(state, unit):
    enemies = state.objs_by_team(state.other_team)
    if not enemies:
        return None

    retreat_dir = retreat(state, unit)
    if retreat_dir:
        return Action.move(retreat_dir)

    adjacent = []
    for direction in DIRS:
        other = state.obj_by_coords(unit.coords + direction)
        if other and other.team == state.other_team:
            adjacent.append((other.health, direction, other))
    if adjacent:
        # Focus the weakest adjacent enemy when safe to stand and fight.  This is
        # slightly sharper than the opponent's closest-enemy attack in melees.
        adjacent.sort(key=lambda t: t[0])
        return Action.attack(adjacent[0][1])

    # Chase the nearest enemy by walking distance, preserving the opponent's
    # Python min/stable tie behavior from state iteration order.
    closest_enemy = min(enemies, key=lambda e: e.coords.walking_distance_to(unit.coords))
    direction = walk_to(state, unit.coords, closest_enemy.coords)
    if direction:
        return Action.move(direction)
    return None
