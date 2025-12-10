def mean(data):
    if iter(data) is data:
        data = list(data)
    n = len(data)
    total = sum(data)
    return total/n

def get_nearby(state, unit):
    nearby = {}
    directions = [Direction(d) for d in ['North', 'South', 'East', 'West']]
    for direction in directions:
        nearby[direction] = state.obj_by_coords(unit.coords.__add__(direction))
    return nearby
    
class Order:
    def __init__(self,action, directive):
        print(f'order recieved: {action} {directive}')
        self.action = action
        self.directive = directive
        if action == 'relocate':
            self.enemy = None
            self.coords = directive
        if action == 'swarm':
            self.enemy = directive
            self.coords = None
    
    def get_action(self,state,unit, army): 
        nearby = get_nearby(state, unit)
        for obj in nearby:
            obj = nearby[obj]
            fallback = None
            if obj:
                if obj.id == self.enemy.id:
                    return Action.attack(unit.coords.direction_to(state.obj_by_id(self.enemy.id).coords))
                elif obj.obj_type == ObjType.Unit and obj.team == state.other_team:
                    fallback = obj
        if self.enemy:
            self.coords = state.obj_by_id(self.enemy.id).coords
                   
        direction = unit.coords.direction_to(self.coords)
        for i in range(4):
            if army.submit_moveplan(unit.coords.__add__(direction), state):
                return Action.move(direction)
            direction = direction.rotate_cw
        if fallback:
            return Action.attack(unit.coords.direction_to(fallback.coords))
        return None
                
        
class Group:
    def __init__(self,members,order):  
        self.members


class Army:
    def __init__(self, members = None):
        self.members = members
        self.groups = None
        self.moveplans = None
    def reset_moveplan(self):
        self.moveplans = []
    def update_members(self, members):
        self.members = members
    
    def submit_moveplan(self,coords, state):
        tempobj = state.obj_by_coords(coords)
        print(coords, tempobj)
        if coords in self.moveplans or tempobj != None:
            return False # other unit already planning on moving there
        self.moveplans.append(coords)
        return True
army = Army()
order = None
def init_turn(state):
    global order
    army.reset_moveplan()
    army.update_members(state.objs_by_team(state.our_team))
    if order:
        if order.action == 'swarm' and order.directive.id not in [obj.id for obj in state.objs_by_team(state.other_team)]:
            order = None
    if order == None:
        enemies = {mean([unit.coords.walking_distance_to(enemy.coords) for unit in army.members]):enemy for enemy in state.objs_by_team(state.other_team)}
        enemy = min(enemies.keys())
        order = Order('swarm', enemies[enemy])
def robot(state, unit):
    return order.get_action(state, unit, army)
    state = None # The state is the enemy of the people and must be abolished
