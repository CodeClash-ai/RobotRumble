# Inspired by https://robotrumble.org/mitch84/crw_preempt/view-code

import random

def adjacent_to_enemy(coords, state):
    for dir in Direction:
        other = state.obj_by_coords(coords+dir)
        if other and other.team == state.other_team:
            return True
    return False

def adjacent_to_ally(coords, state, self_id):
    for dir in Direction:
        other = state.obj_by_coords(coords+dir)
        if other and other.team == state.our_team and not other.id == self_id:
            return True
    return False


def adjacent_to_robot(coords, state, self_id):
    for dir in Direction:
        if any(robot.coords == (coords+dir) for (id, robot) in robots.items()):
            return True
    return False

class Robot:
    def __init__(self, state, unit):
        self.state = state
        self.unit = unit
        self.coords = unit.coords
        
    def retreat_dirs(self):
        enemies = []
        blanks = []
        for direction in Direction:
            other = self.state.obj_by_coords(self.unit.coords + direction)
            if other and other.team == self.state.other_team:
                enemies.append(other)
            elif not other:
                blanks.append(direction)

        if not blanks:
            return []
            
        return blanks
    
    def good_retreat_dirs(self):
        return [dir for dir in self.retreat_dirs() if not adjacent_to_enemy(self.unit.coords+dir, self.state)]
    
    
    def attack_closest_enemy(self):
        enemies = self.state.objs_by_team(self.state.other_team)
        if not enemies:
            return None
        closest_enemy = min(
            enemies,
            key=lambda e: e.coords.walking_distance_to(self.unit.coords),
        )

        enemy_direction = self.unit.coords.direction_to(closest_enemy.coords)
        obj = self.state.obj_by_coords(self.unit.coords + enemy_direction)
        will_hit_ally = obj and obj.team == self.state.our_team 
        will_hit_ally = will_hit_ally or any(robot.coords == self.unit.coords + enemy_direction for (id, robot) in robots.items())
        distance_to_enemy = self.unit.coords.walking_distance_to(closest_enemy.coords)
        if not will_hit_ally:
            return Action.attack(enemy_direction)
        
        return None
    
    def act(self):
        good_retreat_dirs = self.good_retreat_dirs()
        desirable_retreat_dirs = [dir for dir in good_retreat_dirs if not adjacent_to_ally(self.unit.coords+dir, self.state, self.unit.id)]
        
        if len(desirable_retreat_dirs):
            retreat_dir = min(desirable_retreat_dirs, key=lambda dir: Coords(10, 10).walking_distance_to(self.unit.coords+dir))
            
            if random.random() < 0.85:
                self.coords = self.coords + retreat_dir
                return Action.move(retreat_dir)
            
            return self.attack_closest_enemy()
        
        return self.attack_closest_enemy()
        

robots = dict()
def init_turn(state):
    global robots
    robots = dict()
    
    for unit in state.objs_by_team(state.our_team):
        robots[unit.id] = Robot(state, unit)
        
        
def robot(state, unit):
    return Robot(state, unit).act()
