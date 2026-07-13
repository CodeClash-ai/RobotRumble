# bob
# instead of targeting one enemy by all bots, bob tries to target more specifically
# he creates tag teams of 3 bots who will chase the same opponent

tag_teams = None
targets_by_unit = {}

#### UTIL ####
# all methods involving units refer to their ids, not the objs
def sum_of_distances_to_unit(unit, team, state):
    unit_obj = state.obj_by_id(unit)
    team_objs = [state.obj_by_id(t) for t in team]
    return sum([unit_obj.coords.distance_to(team_obj.coords) for team_obj in team_objs])

def closest_unit_to_team(unit_candidates, team, state):
    return min(unit_candidates, key=lambda u: sum_of_distances_to_unit(u, team, state))

def unit_alive(obj_id, state):
    alive = state.obj_by_id(obj_id) is not None
    return alive

# a tag team consists of units that share the same target
class TagTeam:
    def __init__(self, units, max_size=2):
        self.units = units
        self.max_size = max_size
        self.target = None
        
    @property
    def full(self):
        return len(self.units) >= self.max_size
    
    def update_members(self, state):
        self.units = [unit for unit in self.units if unit_alive(unit, state)]
    
    def update_targets(self, state):
        global targets_by_unit
        if (self.target is None) or (not unit_alive(self.target, state)):
            # somehow we get into this branch too often
            enemies = state.ids_by_team(state.other_team)
            self.target = closest_unit_to_team(enemies, self.units, state)
        for unit in self.units:
            targets_by_unit[unit] = self.target
            
    def __str__(self):
        return f'\tunits: {[unit for unit in self.units]}; target: {self.target}'

class TagTeams:
    def __init__(self, team_size, min_size):
        self.teams = []
        self.team_size = team_size
        self.min_size = min_size
    
    @property
    def teamed_units(self):
        if len(self.teams) > 0:
            return [unit for tag_team in self.teams for unit in tag_team.units]
        else:
            return []
    
    def delete_small_teams(self):
        if len(self.teams) > 0:
            self.teams = [team for team in self.teams if len(team.units) >= self.min_size]
            
    def update(self, state):
        # clean-up the teams and release units
        for team in self.teams:
            team.update_members(state)
        self.delete_small_teams()
        
        # determine units that are not on a team
        all_units = state.ids_by_team(state.our_team)
        covered_units = self.teamed_units
        teamless_units = [unit for unit in all_units if unit not in covered_units]
        print(f'got {len(teamless_units)} teamless units to redistribute. teamed units were: {self.teamed_units}')
        
        # grouping of teamless units to existing teams; pick first one at random, then by distance
        while len(teamless_units) > self.team_size:
            units = [teamless_units.pop()]
            for i in range(self.team_size-1):
                nearest = closest_unit_to_team(teamless_units, units, state)
                teamless_units.remove(nearest)
                units.append(nearest)
            self.teams.append(TagTeam(units, max_size=self.team_size))
            
        if len(teamless_units) > 0:
            self.teams.append(TagTeam(teamless_units, max_size=self.team_size))
            
        # and choose enemies
        for team in self.teams:
            team.update_targets(state)
            
    def __str__(self):
        return '\n'.join([str(team) for team in self.teams])

def init_turn(state):
    global tag_teams
    global targets_by_unit
    if tag_teams is None:
        tag_teams = TagTeams(team_size=3, min_size=2)
        
    tag_teams.update(state)
    print('units on our team:', state.ids_by_team(state.our_team))
    print('tag teams:')
    print(tag_teams)


def robot(state, unit):
    global targets_by_unit
    
    # let us first check if we are next to an opponent, if so ATTACK
    enemies = state.objs_by_team(state.other_team)
    closest = min(enemies, key=lambda e: unit.coords.distance_to(e.coords))
    if unit.coords.distance_to(closest.coords) == 1:
        return Action.attack(unit.coords.direction_to(closest.coords))
    
    # else chase target
    target = state.obj_by_id(targets_by_unit[unit.id])
    direction = unit.coords.direction_to(target.coords)
    if unit.coords.distance_to(target.coords) == 1:
        return Action.attack(direction)
    else:
        return Action.move(direction)
    
