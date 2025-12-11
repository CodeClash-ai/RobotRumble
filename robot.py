import math

heat = None

def valid(coord: Coords):
    return not (coord.x < 1 or coord.x > 17 or coord.y < 1 or coord.y > 17)


def ind(coord: Coords):
    if  not valid(coord):
        return 0
    return 18 * coord.y + coord.x

def calc_heat(state):
    
    heat_enemy = 1
    heat_ally = 1
    
    detection_ally = range(-2, 3)
    detection_enemy = range(-3, 4)
    
    
    heat = [0] * (18*18)
    
    
    for o in state.objs_by_team(state.our_team):
        for i in detection_ally:
            for j in detection_ally:
                d = o.coords + Coords(i, j)
                heat[ind(d)] += heat_ally * max(0, o.health - d.walking_distance_to(o.coords))
                
    for o in state.objs_by_team(state.other_team):
        for i in detection_enemy:
            for j in detection_enemy:
                d = o.coords + Coords(i, j)
                distance = d.walking_distance_to(o.coords)
                if distance > 0:
                    heat[ind(d)] -= heat_enemy * max(0, 5 - math.log(distance))
    
    heat[ind(Coords(0,0))] = 0
    return heat
                  
def init_turn(state):
    global heat
    heat = calc_heat(state)

def fst(a):
    return a[0][0]

def d_to_center(a):
    return a[0][1].distance_to(Coords(9,9))

def robot(state, unit):
    global heat
    
    curiosity = -2
    
    c = unit.coords
    myheat = heat[ind(c)]
    
    rel = [((heat[ind(c + d)] - myheat, c + d), d) for d in Direction if valid(c + d)]
    rel.sort(key=d_to_center)
    
    debug.inspect("heat", myheat)
    
    if (myheat < 0):
        _, d = max(rel, key=fst)
        return Action.move(d)
    if (myheat >= 0):
        (h, _) , d = min(rel, key=fst)
        if (h < curiosity):
            return Action.attack(d)
        else:
            return Action.move(d)
    
        
