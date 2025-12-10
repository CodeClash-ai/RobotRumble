def init_turn(board):
    global BOARD; BOARD = board 
    
    map = Map()
    score = map.army_ahead()

    if score < 0:
        print(score)

def robot(board, piece):
    global PIECE; PIECE = piece 

    robot = Robot()
    for rule in robot.get_rules():
        if (action := rule()):
            robot.debug(rule)
            return action
    else:
        robot.debug(rule, piece)
        return None

class Robot:
    def rule00_move_freespawntile(self):
        if self.escape_tile and self.at_spawn and self.turns_since_spawn() >= 6 and len(self.nearest_free_coords) >= 1:
            return self.move(self.escape_tile)

    def rule01_attack_desperate(self):
        if len(self.nearest_free_coords) == 0 and len(self.neighbor_enemies) > 0:
            return self.attack_target(self.nearest_enemy())

    def rule02_attack_suicide(self):
        if len(self.nearby_enemies) == 1 and len(self.neighbor_enemies) == 1 and (PIECE.health >= self.neighbor_enemies[0].health):
            return self.attack_target(self.nearest_enemy()) 

    def rule03_move_urgently(self):
        if self.escape_tile and (PIECE.health <= 3) and len(self.neighbor_enemies) >= 1:
            return self.move(self.escape_tile)

    def rule04_attack_strong(self):
        if (1 < len(self.neighbor_enemies) <= 2) and len(self.neighbor_friends) >= 2:
            return self.attack_target(self.nearest_enemy())

    def rule05_attack_surround(self):
        if len(self.neighbor_enemies) == 1 and len(self.friends_around(self.nearest_enemy())) >= 1:
            return self.attack_target(self.nearest_enemy())

    def rule07_move_retreat(self):
        if self.escape_tile and len(self.neighbor_enemies) >= 1 and len(self.neighbor_friends) <= 1:
            return self.move(self.escape_tile)
        
    def rule08_move_keepspawnsafe(self):
        if self.escape_tile and self.turns_since_spawn() == 9 and self.coords_near_spawn(PIECE.coords) :
            return self.move(self.escape_tile)
            
    def rule09_move_tokill(self):
        for weakest in self.nearest_weak_enemies():
            if len(self.enemies_around(weakest)) > 1 or len(self.enemies_at_aim(weakest.coords)) > 1:
                continue 
            if 1 < self.moves_between(PIECE, weakest) <= 4: 
                return self.move(weakest.coords)

    def rule10_attack_close(self):
        if len(self.nearby_enemies) >= 1:
            return self.attack_target(self.nearest_enemy())  

    def rule11_move_takecentre(self):
        attacking = Plan.global_attacks(self)

        for point in Map.CENTRAL_POINTS:
            if point not in attacking:
                return self.move(point)

    def rule99_skip_noaction(self):
        return None 

    def get_rules(self):
        return [getattr(self, f) for f in sorted(dir(self)) if f.startswith('rule')]

class Map:
    CROSS = [Coords(0,1), Coords(1,0), Coords(-1,0), Coords(0, -1)]
    SQUARE = CROSS + [Coords(1, 1), Coords(1, -1), Coords(-1, 1), Coords(-1, -1)]

    CENTRE = Coords(9, 9)
    CENTRAL_POINTS = [Coords(9,9), Coords(8, 9), Coords(7, 9), Coords(9, 7)]
    
    def turns_since_spawn(self):
        return BOARD.turn % 10

    def tile_empty(self, tile):
        return tile is None 

    def tile_piece(self, tile, team):
        return tile.obj_type == ObjType.Unit and tile.team == team

    def coords_is_spawn(self, coords):
        return (coords.x, coords.y) in [
            (14,2),(16,4),(16,14),(14,16),
            (4,16),(2,14),(2,4),(4,2),   
        ] or coords.x in (17, 1) or coords.y in (17, 1)

    def coords_near_spawn(self, coords, directions=None):
        return any([self.coords_is_spawn(coords + d) for d in (directions or Map.CROSS)])

    def coord_of_aim(self, piece, coords_aim):
        return PIECE.coords + PIECE.coords.direction_to(coords_aim)

    def nearest_pieces(self, coords, team, directions=None):
        return [ piece 
                    for piece in (BOARD.obj_by_coords(coords + d) for d in (directions or Map.CROSS)) 
                    if not self.tile_empty(piece) and PIECE.team == team 
            ]

    def nearest_free_coords(self, coords, directions=None):
        return [ coords + d 
                for d in (directions or Map.CROSS) 
                if self.tile_empty(BOARD.obj_by_coords(coords + d))
            ]

    def all_living_ids(self):
        return [p.id for p in self.all_friends() ]

    def all_friends(self):
        return BOARD.objs_by_team(BOARD.our_team)

    def all_enemies(self):
        return BOARD.objs_by_team(BOARD.other_team)
        
    def moves_between(self, piece, target):
        return PIECE.coords.walking_distance_to(target.coords) 

    def locate_pieces(self, piece, teamPIECEs, move_distance):
        return [ target for target in teamPIECEs if self.moves_between(piece, target) <= move_distance]

    def army_ahead(self):
        return len(self.all_friends()) - len(self.all_enemies())

class Plan:
    units = set()
    attacks = {}

    def global_attacks(map):
        Plan.attacks = {id: coord for id, coord in Plan.attacks.items() if id in map.all_living_ids()}
        return Plan.attacks.values()

    def global_move_safe(map, coords):
        return coords not in Plan.global_attacks(map)

    def global_attack_safe(map, piece, coords):
        tile = BOARD.obj_by_coords(coords)
        return map.tile_empty(tile) or map.tile_piece(tile, BOARD.other_team)

    def global_remember_move(piece):
        if PIECE.id in Plan.attacks:
            del Plan.attacks[PIECE.id]
        
    def global_remember_attack(piece, coords):
        Plan.attacks[PIECE.id] = coords


    def move(self, coords):
        if Plan.global_move_safe(self, coords):
            Plan.global_remember_move(PIECE)
            return Action.move(PIECE.coords.direction_to(coords))

    def attack(self, coords):
        if Plan.global_attack_safe(self, PIECE, coords):
            Plan.global_remember_attack(PIECE, coords)
            return Action.attack(PIECE.coords.direction_to(coords))

    def attack_target(self, target):
        return self.attack(self.coord_of_aim(PIECE, target.coords))

class Intelligence:
    def __init__(self):
        self.at_spawn = self.coords_is_spawn(PIECE.coords)
        self.friends = self.all_friends()
        self.enemies = self.all_enemies()
        self.neighbor_enemies = self.nearest_pieces(PIECE.coords, BOARD.other_team)
        self.neighbor_friends = self.nearest_pieces(PIECE.coords, BOARD.our_team)
        self.nearest_free_coords = self.nearest_free_coords(PIECE.coords)
        self.nearby_enemies = self.locate_pieces(PIECE, self.enemies, 2)
        self.escape_tile = self.nearest_spawnsafe()


    def enemies_at_aim(self, aim_coords):
        return self.nearest_pieces(self.coord_of_aim(PIECE, aim_coords), BOARD.other_team)

    def nearest_spawnsafe(self, tiles=None):
        if tiles is None:
            tiles = self.nearest_free_tiles()

        if self.turns_since_spawn() >= 6:
            tiles = [ t for t in tiles if not self.coords_is_spawn(t)]
        
        return tiles[0] if tiles and len(tiles) > 0 else None
        
    def weaker_enemies(self):
        return [e for e in self.enemies if e.health < PIECE.health]

    def nearest_weak_enemies(self):
        def weighted(target):
            return self.moves_between(PIECE, target)

        return sorted(self.weaker_enemies(), key=weighted)

    def nearest_enemy(self):
        def weighted(target):
            return self.moves_between(PIECE, target) + target.health/10

        return min(self.enemies, key=weighted)

    def nearest_free_tiles(self):
        if len(self.nearest_free_coords) == 0:
            return [] 

        def weighted(tile):
            return len(self.nearest_pieces(tile, BOARD.other_team, Map.SQUARE))

        return sorted(self.nearest_free_coords, key=weighted)

    def friends_around(self, target):
        return self.nearest_pieces(target.coords, BOARD.our_team)

    def enemies_around(self, target):
        return self.nearest_pieces(target.coords, BOARD.other_team)


class DebugReport:
    def debug(self, rule, highlight=None):
        if PIECE.id not in Plan.units:
            debug.locate(PIECE)
            Plan.units.add(PIECE.id)

        if highlight:
            print("HIGHLIGHT")
            debug.locate(highlight)

        debug.inspect("$rule", rule.__name__)
        debug.inspect("$score", self.army_ahead())

        for k, v in vars(self).items():
            if type(v) in [list, set, tuple]:
                debug.inspect(f"num_{k}", len(v))
            elif type(v) in [int, bool, str, float]:
                debug.inspect(k, v)

        for bot, target in Plan.attacks.items():
            debug.inspect(f"x{bot}", target)

Robot = type('Robot', (Robot, Intelligence, DebugReport, Plan, Map), {})
